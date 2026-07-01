"""Import a portable Pipedrive configuration export."""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv
from requests import RequestException


ROOT_DIR = Path(__file__).resolve().parents[2]
IMPORTER_DIR = ROOT_DIR / "importer"
DEFAULT_EXPORT_PATH = ROOT_DIR / "pipedrive_config_exports" / "pipedrive_config_export_20260625_165205.json"

FIELD_ENDPOINTS = {
    "deal": "dealFields",
    "organization": "organizationFields",
    "person": "personFields",
    "activity": "activityFields",
    "product": "productFields",
    "lead": "leadFields",
}

CUSTOM_FIELD_KEY_RE = re.compile(r"^[a-f0-9]{40}$", re.IGNORECASE)


class PipedriveImportError(Exception):
    pass


@dataclass
class ImportStats:
    created: Counter[str] = field(default_factory=Counter)
    skipped: Counter[str] = field(default_factory=Counter)
    failed: list[str] = field(default_factory=list)

    def record_created(self, kind: str) -> None:
        self.created[kind] += 1

    def record_skipped(self, kind: str) -> None:
        self.skipped[kind] += 1

    def record_failed(self, message: str) -> None:
        self.failed.append(message)


class PipedriveClient:
    def __init__(self, api_token: str, base_url: str, dry_run: bool) -> None:
        self.api_token = api_token
        self.base_url = base_url.rstrip("/")
        self.dry_run = dry_run
        self.session = requests.Session()

    def request(self, method: str, endpoint: str, payload: dict[str, Any] | None = None) -> Any:
        if self.dry_run and method.upper() != "GET":
            return {"dry_run": True, "payload": payload or {}}

        try:
            response = self.session.request(
                method,
                f"{self.base_url}/{endpoint.lstrip('/')}",
                params={"api_token": self.api_token},
                json=payload,
                timeout=45,
            )
        except RequestException as exc:
            raise PipedriveImportError(f"{method} {endpoint}: request failed ({exc.__class__.__name__})") from None

        try:
            body = response.json()
        except ValueError:
            body = {"success": False, "error": response.text}

        if not response.ok or body.get("success") is False:
            error = body.get("error") or body.get("error_info") or response.text
            raise PipedriveImportError(f"{method} {endpoint}: {error}")
        return body.get("data")

    def get_all(self, endpoint: str) -> list[dict[str, Any]]:
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
                raise PipedriveImportError(f"GET {endpoint}: request failed ({exc.__class__.__name__})") from None

            try:
                body = response.json()
            except ValueError:
                body = {"success": False, "error": response.text}
            if not response.ok or body.get("success") is False:
                error = body.get("error") or body.get("error_info") or response.text
                raise PipedriveImportError(f"GET {endpoint}: {error}")

            data = body.get("data") or []
            if isinstance(data, dict):
                data = [data]
            if isinstance(data, list):
                items.extend(item for item in data if isinstance(item, dict))

            pagination = (body.get("additional_data") or {}).get("pagination") or {}
            if not pagination.get("more_items_in_collection"):
                break
            start = int(pagination.get("next_start", start + limit))
        return items

    def post_with_fallback(self, endpoint: str, payload: dict[str, Any], fallback_payload: dict[str, Any]) -> Any:
        try:
            return self.request("POST", endpoint, payload)
        except PipedriveImportError:
            if payload == fallback_payload:
                raise
            return self.request("POST", endpoint, fallback_payload)


def load_env() -> tuple[str, str]:
    load_dotenv(ROOT_DIR / ".env")
    load_dotenv(IMPORTER_DIR / ".env")
    api_token = os.getenv("PIPEDRIVE_API_TOKEN")
    base_url = os.getenv("PIPEDRIVE_BASE_URL", "https://api.pipedrive.com/v1")
    if not api_token:
        raise PipedriveImportError("PIPEDRIVE_API_TOKEN is missing from .env or importer/.env")
    return api_token, base_url


def normalize(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip()).casefold()


def is_custom_field(field: dict[str, Any]) -> bool:
    return bool(CUSTOM_FIELD_KEY_RE.match(str(field.get("key") or "")))


def field_signature(field: dict[str, Any]) -> tuple[str, str, tuple[str, ...]]:
    options = field.get("options") or []
    labels = tuple(normalize(option.get("label")) for option in options if isinstance(option, dict) and option.get("label"))
    return normalize(field.get("name")), normalize(field.get("field_type")), labels


def create_field_payload(field: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "name": field.get("name"),
        "field_type": field.get("field_type"),
    }
    options = field.get("options") or []
    option_labels = [option.get("label") for option in options if isinstance(option, dict) and option.get("label")]
    if option_labels:
        payload["options"] = [{"label": label} for label in option_labels]
    for optional_key in ("add_visible_flag", "important_flag"):
        if optional_key in field and field[optional_key] is not None:
            payload[optional_key] = field[optional_key]
    return payload


def minimal_field_payload(field: dict[str, Any]) -> dict[str, Any]:
    payload = {"name": field.get("name"), "field_type": field.get("field_type")}
    options = field.get("options") or []
    option_labels = [option.get("label") for option in options if isinstance(option, dict) and option.get("label")]
    if option_labels:
        payload["options"] = [{"label": label} for label in option_labels]
    return payload


def import_custom_fields(client: PipedriveClient, export: dict[str, Any], stats: ImportStats) -> None:
    exported_by_entity = dict(export.get("field_endpoints", {}))
    lead_fields = export.get("config_endpoints", {}).get("lead_fields")
    if lead_fields:
        exported_by_entity["lead"] = {"fields": lead_fields.get("items", [])}

    for entity, payload in exported_by_entity.items():
        endpoint = FIELD_ENDPOINTS.get(entity)
        if not endpoint:
            continue
        try:
            existing_fields = client.get_all(endpoint)
        except PipedriveImportError as exc:
            stats.record_failed(str(exc))
            continue

        existing_counts = Counter(field_signature(field) for field in existing_fields if is_custom_field(field))
        source_fields = [field for field in payload.get("fields", []) if is_custom_field(field) and field.get("name") and field.get("field_type")]
        source_seen: Counter[tuple[str, str, tuple[str, ...]]] = Counter()

        for field in source_fields:
            signature = field_signature(field)
            source_seen[signature] += 1
            if existing_counts[signature] >= source_seen[signature]:
                stats.record_skipped(f"{entity}_field")
                continue

            try:
                client.post_with_fallback(endpoint, create_field_payload(field), minimal_field_payload(field))
                stats.record_created(f"{entity}_field")
                existing_counts[signature] += 1
            except PipedriveImportError as exc:
                stats.record_failed(f"{entity} field {field.get('name')}: {exc}")


def import_pipelines_and_stages(client: PipedriveClient, export: dict[str, Any], stats: ImportStats) -> None:
    source_pipelines = export.get("config_endpoints", {}).get("pipelines", {}).get("items", [])
    source_stages = export.get("config_endpoints", {}).get("stages", {}).get("items", [])

    try:
        existing_pipelines = client.get_all("pipelines")
    except PipedriveImportError as exc:
        stats.record_failed(str(exc))
        return

    pipeline_by_name = {normalize(item.get("name")): item for item in existing_pipelines}
    pipeline_id_by_source_id: dict[Any, Any] = {}

    for pipeline in source_pipelines:
        name = pipeline.get("name")
        if not name:
            continue
        existing = pipeline_by_name.get(normalize(name))
        if existing:
            pipeline_id_by_source_id[pipeline.get("id")] = existing.get("id")
            stats.record_skipped("pipeline")
            continue
        payload = {
            "name": name,
            "deal_probability": bool(pipeline.get("deal_probability")),
            "order_nr": pipeline.get("order_nr"),
        }
        try:
            created = client.request("POST", "pipelines", payload)
            stats.record_created("pipeline")
            pipeline_id_by_source_id[pipeline.get("id")] = (created or {}).get("id") or pipeline.get("id")
            if not client.dry_run and created:
                pipeline_by_name[normalize(name)] = created
        except PipedriveImportError as exc:
            stats.record_failed(f"pipeline {name}: {exc}")

    try:
        existing_stages = client.get_all("stages")
    except PipedriveImportError as exc:
        stats.record_failed(str(exc))
        return

    existing_stage_keys = {(normalize(stage.get("name")), stage.get("pipeline_id")) for stage in existing_stages}
    for stage in source_stages:
        target_pipeline_id = pipeline_id_by_source_id.get(stage.get("pipeline_id"))
        if not target_pipeline_id:
            stats.record_failed(f"stage {stage.get('name')}: target pipeline missing")
            continue
        key = (normalize(stage.get("name")), target_pipeline_id)
        if key in existing_stage_keys:
            stats.record_skipped("stage")
            continue
        payload = {
            "name": stage.get("name"),
            "pipeline_id": target_pipeline_id,
            "deal_probability": stage.get("deal_probability"),
            "rotten_flag": bool(stage.get("rotten_flag")),
            "rotten_days": stage.get("rotten_days"),
        }
        try:
            client.request("POST", "stages", payload)
            stats.record_created("stage")
            existing_stage_keys.add(key)
        except PipedriveImportError as exc:
            stats.record_failed(f"stage {stage.get('name')}: {exc}")


def import_activity_types(client: PipedriveClient, export: dict[str, Any], stats: ImportStats) -> None:
    source_items = export.get("config_endpoints", {}).get("activity_types", {}).get("items", [])
    try:
        existing = client.get_all("activityTypes")
    except PipedriveImportError as exc:
        stats.record_failed(str(exc))
        return
    existing_names = {normalize(item.get("name")) for item in existing}
    for item in source_items:
        name = item.get("name")
        if not name:
            continue
        if normalize(name) in existing_names:
            stats.record_skipped("activity_type")
            continue
        payload = {
            "name": name,
            "icon_key": item.get("icon_key") or "task",
            "color": item.get("color"),
        }
        try:
            client.post_with_fallback("activityTypes", payload, {"name": name, "icon_key": payload["icon_key"]})
            stats.record_created("activity_type")
            existing_names.add(normalize(name))
        except PipedriveImportError as exc:
            stats.record_failed(f"activity type {name}: {exc}")


def import_lead_labels(client: PipedriveClient, export: dict[str, Any], stats: ImportStats) -> None:
    source_items = export.get("config_endpoints", {}).get("lead_labels", {}).get("items", [])
    try:
        existing = client.get_all("leadLabels")
    except PipedriveImportError as exc:
        stats.record_failed(str(exc))
        return
    existing_names = {normalize(item.get("name")) for item in existing}
    for item in source_items:
        name = item.get("name")
        if not name:
            continue
        if normalize(name) in existing_names:
            stats.record_skipped("lead_label")
            continue
        payload = {"name": name, "color": item.get("color")}
        try:
            client.post_with_fallback("leadLabels", payload, {"name": name})
            stats.record_created("lead_label")
            existing_names.add(normalize(name))
        except PipedriveImportError as exc:
            stats.record_failed(f"lead label {name}: {exc}")


def import_config(export_path: Path, apply: bool) -> ImportStats:
    api_token, base_url = load_env()
    export = json.loads(export_path.read_text(encoding="utf-8"))
    client = PipedriveClient(api_token=api_token, base_url=base_url, dry_run=not apply)
    stats = ImportStats()

    import_custom_fields(client, export, stats)
    import_pipelines_and_stages(client, export, stats)
    import_activity_types(client, export, stats)
    import_lead_labels(client, export, stats)
    return stats


def print_summary(stats: ImportStats, apply: bool) -> None:
    mode = "APPLY" if apply else "DRY RUN"
    print(f"Mode: {mode}")
    print("Created:")
    for key, value in sorted(stats.created.items()):
        print(f"  {key}: {value}")
    print("Skipped:")
    for key, value in sorted(stats.skipped.items()):
        print(f"  {key}: {value}")
    print(f"Failures: {len(stats.failed)}")
    for failure in stats.failed[:50]:
        print(f"  - {failure}")
    if len(stats.failed) > 50:
        print(f"  ...and {len(stats.failed) - 50} more")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import exported Pipedrive configuration into the current target account.")
    parser.add_argument("--export", type=Path, default=DEFAULT_EXPORT_PATH)
    parser.add_argument("--apply", action="store_true", help="Actually create missing config. Omit for dry-run.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    stats = import_config(args.export, args.apply)
    print_summary(stats, args.apply)
    return 1 if stats.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
