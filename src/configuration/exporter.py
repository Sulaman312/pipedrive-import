"""Export Pipedrive configuration into portable JSON and Markdown files."""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv
from requests import RequestException


ROOT_DIR = Path(__file__).resolve().parents[2]
IMPORTER_DIR = ROOT_DIR / "importer"
DEFAULT_OUTPUT_DIR = ROOT_DIR / "pipedrive_config_exports"

FIELD_ENDPOINTS = {
    "deal": "dealFields",
    "organization": "organizationFields",
    "person": "personFields",
    "activity": "activityFields",
    "product": "productFields",
}

CONFIG_ENDPOINTS = {
    "pipelines": "pipelines",
    "stages": "stages",
    "activity_types": "activityTypes",
    "users": "users",
    "teams": "teams",
    "roles": "roles",
    "permission_sets": "permissionSets",
    "filters": "filters",
    "currencies": "currencies",
    "webhooks": "webhooks",
    "lead_labels": "leadLabels",
    "lead_sources": "leadSources",
    "lead_fields": "leadFields",
    "deal_labels": "dealLabels",
    "organization_relationships": "organizationRelationships",
}

CUSTOM_FIELD_KEY_RE = re.compile(r"^[a-f0-9]{40}$", re.IGNORECASE)


class PipedriveExportError(Exception):
    pass


class PipedriveClient:
    def __init__(self, api_token: str, base_url: str) -> None:
        self.api_token = api_token
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def get(self, endpoint: str) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        start = 0
        limit = 500

        while True:
            try:
                response = self.session.get(
                    f"{self.base_url}/{endpoint}",
                    params={"api_token": self.api_token, "start": start, "limit": limit},
                    timeout=45,
                )
            except RequestException as exc:
                raise PipedriveExportError(f"{endpoint}: request failed ({exc.__class__.__name__})") from None
            try:
                payload = response.json()
            except ValueError:
                payload = {"success": False, "error": response.text}

            if not response.ok or payload.get("success") is False:
                error = payload.get("error") or payload.get("error_info") or response.text
                raise PipedriveExportError(f"{endpoint}: {error}")

            data = payload.get("data") or []
            if isinstance(data, dict):
                data = [data]
            if not isinstance(data, list):
                data = []
            items.extend(item for item in data if isinstance(item, dict))

            pagination = (payload.get("additional_data") or {}).get("pagination") or {}
            if not pagination.get("more_items_in_collection"):
                break
            start = int(pagination.get("next_start", start + limit))

        return items


def load_env() -> tuple[str, str]:
    load_dotenv(ROOT_DIR / ".env")
    load_dotenv(IMPORTER_DIR / ".env")
    api_token = os.getenv("PIPEDRIVE_API_TOKEN")
    base_url = os.getenv("PIPEDRIVE_BASE_URL", "https://api.pipedrive.com/v1")
    if not api_token:
        raise PipedriveExportError("PIPEDRIVE_API_TOKEN is missing from .env or importer/.env")
    return api_token, base_url


def is_custom_like_field(field: dict[str, Any]) -> bool:
    key = str(field.get("key") or "")
    return bool(CUSTOM_FIELD_KEY_RE.match(key))


def summarize_field(field: dict[str, Any]) -> dict[str, Any]:
    options = field.get("options") or []
    if not isinstance(options, list):
        options = []
    return {
        "id": field.get("id"),
        "key": field.get("key"),
        "name": field.get("name"),
        "field_type": field.get("field_type"),
        "is_custom_like": is_custom_like_field(field),
        "edit_flag": field.get("edit_flag"),
        "add_visible_flag": field.get("add_visible_flag"),
        "options": [
            {
                "id": option.get("id"),
                "label": option.get("label"),
            }
            for option in options
            if isinstance(option, dict)
        ],
    }


def export_config(output_dir: Path) -> tuple[Path, Path]:
    api_token, base_url = load_env()
    client = PipedriveClient(api_token=api_token, base_url=base_url)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir.mkdir(parents=True, exist_ok=True)

    export: dict[str, Any] = {
        "exported_at": datetime.now().isoformat(timespec="seconds"),
        "base_url": base_url,
        "field_endpoints": {},
        "config_endpoints": {},
        "errors": {},
    }

    for entity, endpoint in FIELD_ENDPOINTS.items():
        try:
            fields = client.get(endpoint)
            export["field_endpoints"][entity] = {
                "endpoint": endpoint,
                "fields": fields,
                "summary": [summarize_field(field) for field in fields],
            }
        except PipedriveExportError as exc:
            export["errors"][endpoint] = str(exc)

    for name, endpoint in CONFIG_ENDPOINTS.items():
        try:
            export["config_endpoints"][name] = {
                "endpoint": endpoint,
                "items": client.get(endpoint),
            }
        except PipedriveExportError as exc:
            export["errors"][endpoint] = str(exc)

    json_path = output_dir / f"pipedrive_config_export_{timestamp}.json"
    md_path = output_dir / f"pipedrive_config_export_{timestamp}.md"

    json_path.write_text(json.dumps(export, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(export), encoding="utf-8")
    return json_path, md_path


def render_markdown(export: dict[str, Any]) -> str:
    lines: list[str] = [
        "# Pipedrive Configuration Export",
        "",
        f"Exported at: `{export['exported_at']}`",
        f"Base URL: `{export['base_url']}`",
        "",
        "This file summarizes fields and account configuration needed to recreate custom setup in another Pipedrive environment.",
        "",
    ]

    lines.extend(["## Fields", ""])
    for entity, payload in export["field_endpoints"].items():
        summary = payload.get("summary", [])
        custom_count = sum(1 for field in summary if field.get("is_custom_like"))
        lines.extend(
            [
                f"### {entity.title()} Fields",
                "",
                f"Endpoint: `{payload.get('endpoint')}`",
                f"Total fields: `{len(summary)}`",
                f"Likely custom fields: `{custom_count}`",
                "",
                "| Custom | Name | Key | Type | Options |",
                "|---|---|---|---|---|",
            ]
        )
        for field in summary:
            options = ", ".join(str(option.get("label")) for option in field.get("options", []) if option.get("label"))
            lines.append(
                "| {custom} | {name} | `{key}` | {field_type} | {options} |".format(
                    custom="yes" if field.get("is_custom_like") else "no",
                    name=escape_md(field.get("name")),
                    key=field.get("key") or "",
                    field_type=escape_md(field.get("field_type")),
                    options=escape_md(options),
                )
            )
        lines.append("")

    lines.extend(["## Pipelines And Stages", ""])
    pipelines = export["config_endpoints"].get("pipelines", {}).get("items", [])
    stages = export["config_endpoints"].get("stages", {}).get("items", [])
    lines.append(f"Pipelines: `{len(pipelines)}`")
    for pipeline in pipelines:
        lines.append(f"- {pipeline.get('name')} (`id={pipeline.get('id')}`)")
        for stage in stages:
            if stage.get("pipeline_id") == pipeline.get("id"):
                lines.append(f"  - {stage.get('name')} (`id={stage.get('id')}`, order={stage.get('order_nr')})")
    lines.append("")

    lines.extend(["## Activity Types", ""])
    activity_types = export["config_endpoints"].get("activity_types", {}).get("items", [])
    lines.append(f"Activity types: `{len(activity_types)}`")
    for activity_type in activity_types:
        lines.append(
            f"- {activity_type.get('name')} (`key_string={activity_type.get('key_string')}`, active={activity_type.get('active_flag')})"
        )
    lines.append("")

    lines.extend(["## Other Configuration Endpoints", ""])
    for name, payload in export["config_endpoints"].items():
        if name in {"pipelines", "stages", "activity_types"}:
            continue
        items = payload.get("items", [])
        lines.extend(
            [
                f"### {name.replace('_', ' ').title()}",
                "",
                f"Endpoint: `{payload.get('endpoint')}`",
                f"Items: `{len(items)}`",
                "",
            ]
        )
        for item in items[:50]:
            label = item.get("name") or item.get("label") or item.get("key_string") or item.get("id")
            lines.append(f"- {escape_md(label)} (`id={item.get('id', '')}`)")
        if len(items) > 50:
            lines.append(f"- ...and {len(items) - 50} more")
        lines.append("")

    if export.get("errors"):
        lines.extend(["## Export Errors", ""])
        for endpoint, error in export["errors"].items():
            lines.append(f"- `{endpoint}`: {error}")
        lines.append("")

    return "\n".join(lines)


def escape_md(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("|", "\\|").replace("\n", " ")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export Pipedrive field and account configuration metadata.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    json_path, md_path = export_config(args.output_dir)
    print(f"Wrote JSON export: {json_path}")
    print(f"Wrote Markdown summary: {md_path}")


if __name__ == "__main__":
    main()
