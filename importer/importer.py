"""Import XLSX files into Pipedrive organizations, persons, and deals."""

from __future__ import annotations

import argparse
import csv
import logging
import os
import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from requests import RequestException
from dotenv import load_dotenv

from mapping import FIELD_MAPPING, STANDARD_FIELD_ALIASES


BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "input"
PROCESSED_DIR = BASE_DIR / "processed"
FAILED_DIR = BASE_DIR / "failed"
LOG_DIR = BASE_DIR / "logs"

ENTITY_ENDPOINTS = {
    "deal": "deals",
    "organization": "organizations",
    "person": "persons",
}

FIELD_ENDPOINTS = {
    "deal": "dealFields",
    "organization": "organizationFields",
    "person": "personFields",
}

OPTION_DELIMITER_RE = re.compile(r"\s*[,;|]\s*")


class ImporterError(Exception):
    """Base exception for importer failures."""


@dataclass
class ImportStats:
    rows: int = 0
    organizations_created: int = 0
    organizations_updated: int = 0
    persons_created: int = 0
    persons_updated: int = 0
    deals_created: int = 0
    failed_rows: int = 0
    row_errors: list[str] = field(default_factory=list)
    unmapped_columns: list[str] = field(default_factory=list)
    skipped_fields: set[str] = field(default_factory=set)


@dataclass
class PipedriveMetadata:
    field_lookup: dict[str, dict[str, str]]
    field_options: dict[str, dict[str, dict[str, Any]]]
    stages: dict[str, int]
    users: dict[str, int]


def ensure_directories() -> None:
    for directory in (INPUT_DIR, PROCESSED_DIR, FAILED_DIR, LOG_DIR):
        directory.mkdir(exist_ok=True)


def setup_logging() -> logging.Logger:
    ensure_directories()
    log_path = LOG_DIR / f"import_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    logger = logging.getLogger("pipedrive_importer")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger


def clean_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def normalize_name(value: str) -> str:
    value = str(value)
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u00a0": " ",
    }
    for source, target in replacements.items():
        value = value.replace(source, target)

    value = re.sub(r"\s*-\s*", "-", value)
    value = re.sub(r"\s*_\s*", "_", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip().casefold()


NORMALIZED_FIELD_MAPPING = {
    normalize_name(column): (column, config) for column, config in FIELD_MAPPING.items()
}


NORMALIZED_STANDARD_FIELD_ALIASES = {
    entity: {normalize_name(name): key for name, key in aliases.items()}
    for entity, aliases in STANDARD_FIELD_ALIASES.items()
}


def load_xlsx_file(path: Path) -> pd.DataFrame:
    return pd.read_excel(path, engine="openpyxl")


def list_input_files() -> list[Path]:
    return sorted(INPUT_DIR.glob("*.xlsx"))


def unique_destination(directory: Path, source_name: str) -> Path:
    destination = directory / source_name
    if not destination.exists():
        return destination

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return directory / f"{destination.stem}_{timestamp}{destination.suffix}"


def move_file(path: Path, destination_dir: Path) -> Path:
    destination = unique_destination(destination_dir, path.name)
    return Path(shutil.move(str(path), str(destination)))


class PipedriveClient:
    def __init__(self, api_token: str, base_url: str, logger: logging.Logger) -> None:
        self.api_token = api_token
        self.base_url = base_url.rstrip("/")
        self.logger = logger
        self.session = requests.Session()

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Any:
        request_params = dict(params or {})
        request_params["api_token"] = self.api_token
        try:
            response = self.session.request(
                method,
                f"{self.base_url}/{path.lstrip('/')}",
                params=request_params,
                json=json,
                timeout=30,
            )
        except RequestException:
            raise ImporterError(f"Pipedrive request failed on {method} {path}") from None
        try:
            payload = response.json()
        except ValueError:
            payload = {"success": False, "error": response.text}

        if not response.ok or payload.get("success") is False:
            error = payload.get("error") or payload.get("error_info") or response.text
            raise ImporterError(f"Pipedrive API error on {method} {path}: {error}")

        return payload.get("data")

    def load_field_lookup(self) -> dict[str, dict[str, str]]:
        lookup: dict[str, dict[str, str]] = {}
        for entity, endpoint in FIELD_ENDPOINTS.items():
            fields = self.load_fields(entity)
            lookup[entity] = {}
            for item in fields:
                name = item.get("name")
                key = item.get("key")
                if name and key:
                    lookup[entity][name] = key
                    lookup[entity][normalize_name(name)] = key
            self.logger.info("Loaded %s %s fields from Pipedrive", len(fields), entity)
        return lookup

    def load_fields(self, entity: str) -> list[dict[str, Any]]:
        fields = self.request("GET", FIELD_ENDPOINTS[entity]) or []
        return fields if isinstance(fields, list) else []

    def load_stages(self) -> list[dict[str, Any]]:
        stages = self.request("GET", "stages") or []
        return stages if isinstance(stages, list) else []

    def load_users(self) -> list[dict[str, Any]]:
        users = self.request("GET", "users") or []
        return users if isinstance(users, list) else []

    def load_metadata(self) -> PipedriveMetadata:
        field_lookup: dict[str, dict[str, str]] = {}
        field_options: dict[str, dict[str, dict[str, Any]]] = {}

        for entity in FIELD_ENDPOINTS:
            fields = self.load_fields(entity)
            field_lookup[entity] = {}
            field_options[entity] = {}
            for item in fields:
                name = item.get("name")
                key = item.get("key")
                if name and key:
                    field_lookup[entity][name] = key
                    field_lookup[entity][normalize_name(name)] = key

                options = item.get("options") or []
                if key and isinstance(options, list):
                    field_options[entity][key] = {}
                    for option in options:
                        label = option.get("label")
                        option_id = option.get("id")
                        if label is not None and option_id is not None:
                            field_options[entity][key][normalize_name(str(label))] = option_id

            self.logger.info("Loaded %s %s fields from Pipedrive", len(fields), entity)

        stages = {}
        for stage in self.load_stages():
            name = stage.get("name")
            stage_id = stage.get("id")
            if name and stage_id is not None:
                stages[normalize_name(name)] = int(stage_id)

        users = {}
        for user in self.load_users():
            user_id = user.get("id")
            if user_id is None:
                continue
            for key in ("name", "email"):
                value = user.get(key)
                if value:
                    users[normalize_name(str(value))] = int(user_id)
            first_name = user.get("first_name")
            last_name = user.get("last_name")
            if first_name and last_name:
                users[normalize_name(f"{first_name} {last_name}")] = int(user_id)

        self.logger.info("Loaded %s stages and %s user lookup entries", len(stages), len(users))
        return PipedriveMetadata(
            field_lookup=field_lookup,
            field_options=field_options,
            stages=stages,
            users=users,
        )

    def search_organization_by_name(self, name: str) -> dict[str, Any] | None:
        data = self.request(
            "GET",
            "organizations/search",
            params={"term": name, "fields": "name", "exact_match": 1},
        )
        return first_search_item(data)

    def search_person_by_email(self, email: str) -> dict[str, Any] | None:
        data = self.request(
            "GET",
            "persons/search",
            params={"term": email, "fields": "email", "exact_match": 1},
        )
        return first_search_item(data)

    def search_person_by_name(self, name: str) -> dict[str, Any] | None:
        data = self.request(
            "GET",
            "persons/search",
            params={"term": name, "fields": "name", "exact_match": 1},
        )
        return first_search_item(data)

    def create_entity(self, entity: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self.request("POST", ENTITY_ENDPOINTS[entity], json=payload)

    def update_entity(self, entity: str, entity_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        return self.request("PUT", f"{ENTITY_ENDPOINTS[entity]}/{entity_id}", json=payload)


def first_search_item(data: Any) -> dict[str, Any] | None:
    items = (data or {}).get("items") or []
    if not items:
        return None
    item = items[0].get("item") or items[0]
    return item if isinstance(item, dict) else None


def extract_entity_id(entity: dict[str, Any] | None) -> int | None:
    if not entity:
        return None
    value = entity.get("id")
    if isinstance(value, dict):
        value = value.get("value")
    return int(value) if value is not None else None


def dry_run_field_lookup() -> dict[str, dict[str, str]]:
    lookup: dict[str, dict[str, str]] = {"deal": {}, "organization": {}, "person": {}}
    for source in FIELD_MAPPING.values():
        entity = source["entity"]
        visible_name = source["pipedrive_field_name"]
        if visible_name not in STANDARD_FIELD_ALIASES.get(entity, {}):
            lookup[entity][visible_name] = f"DRY_RUN_FIELD::{visible_name}"
            lookup[entity][normalize_name(visible_name)] = f"DRY_RUN_FIELD::{visible_name}"
    return lookup


def find_lookup_value(lookup: dict[str, Any], raw_value: Any) -> Any | None:
    normalized_value = normalize_name(str(raw_value))
    if normalized_value in lookup:
        return lookup[normalized_value]

    matches = [
        (name, value)
        for name, value in lookup.items()
        if normalized_value in name or name in normalized_value
    ]
    if not matches:
        return None

    matches.sort(key=lambda item: len(item[0]))
    return matches[0][1]


def split_option_values(value: Any) -> list[Any]:
    if isinstance(value, str):
        return [item for item in OPTION_DELIMITER_RE.split(value) if item]
    if isinstance(value, (list, tuple, set)):
        return list(value)
    return [value]


def resolve_pipedrive_value(
    entity: str,
    field_key: str,
    field_name: str,
    value: Any,
    metadata: PipedriveMetadata | None,
    stats: ImportStats,
    logger: logging.Logger,
) -> Any | None:
    if metadata is None:
        return value

    if field_key == "stage_id":
        stage_id = find_lookup_value(metadata.stages, value)
        if stage_id is None:
            stats.skipped_fields.add(f"{entity}: {field_name} value {value}")
            logger.warning("Skipping stage value %r because no matching Pipedrive stage was found", value)
            return None
        return stage_id

    if field_key == "owner_id":
        user_id = find_lookup_value(metadata.users, value)
        if user_id is None:
            stats.skipped_fields.add(f"{entity}: {field_name} value {value}")
            logger.warning("Skipping owner value %r because no matching Pipedrive user was found", value)
            return None
        return user_id

    if entity == "deal" and field_key == "label":
        option_lookup = metadata.field_options.get(entity, {}).get(field_key, {})
        resolved_values = []
        missing_values = []
        for option_value in split_option_values(value):
            option_id = find_lookup_value(option_lookup, option_value)
            if option_id is None:
                missing_values.append(option_value)
            else:
                resolved_values.append(option_id)

        if missing_values:
            stats.skipped_fields.add(f"{entity}: {field_name} values {missing_values}")
            logger.warning(
                "Skipping deal label value(s) %r because no matching Pipedrive label option was found",
                missing_values,
            )
            return None
        if len(resolved_values) == 1:
            return resolved_values[0]
        return resolved_values

    return value


def map_row(
    row: pd.Series,
    field_lookup: dict[str, dict[str, str]],
    metadata: PipedriveMetadata | None,
    stats: ImportStats,
    logger: logging.Logger,
) -> dict[str, dict[str, Any]]:
    mapped = {"organization": {}, "person": {}, "deal": {}}
    columns_by_normalized_name = {normalize_name(column): column for column in row.index}

    for normalized_column, (_configured_column, config) in NORMALIZED_FIELD_MAPPING.items():
        actual_column = columns_by_normalized_name.get(normalized_column)
        if actual_column is None:
            continue

        value = clean_value(row[actual_column])
        if value is None:
            continue

        entity = config["entity"]
        field_name = config["pipedrive_field_name"]
        standard_key = NORMALIZED_STANDARD_FIELD_ALIASES.get(entity, {}).get(
            normalize_name(field_name)
        )
        field_key = (
            standard_key
            or field_lookup.get(entity, {}).get(field_name)
            or field_lookup.get(entity, {}).get(normalize_name(field_name))
        )

        if not field_key:
            skipped = f"{entity}: {field_name}"
            stats.skipped_fields.add(skipped)
            logger.warning(
                "Skipping mapped column '%s' because Pipedrive field '%s' was not found for %s",
                actual_column,
                field_name,
                entity,
            )
            continue
        resolved_value = resolve_pipedrive_value(
            entity,
            field_key,
            field_name,
            value,
            metadata,
            stats,
            logger,
        )
        if resolved_value is None:
            continue
        mapped[entity][field_key] = resolved_value
    return mapped


def detected_unmapped_columns(columns: list[str]) -> list[str]:
    return [
        column
        for column in columns
        if normalize_name(column) not in NORMALIZED_FIELD_MAPPING
    ]


def print_column_summary(path: Path, columns: list[str], unmapped: list[str], logger: logging.Logger) -> None:
    logger.info("Detected columns in %s: %s", path.name, ", ".join(columns) or "(none)")
    if unmapped:
        logger.warning("Unmapped columns in %s: %s", path.name, ", ".join(unmapped))
    else:
        logger.info("No unmapped columns in %s", path.name)


def export_pipedrive_fields(client: PipedriveClient, logger: logging.Logger) -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for entity in FIELD_ENDPOINTS:
        fields = client.load_fields(entity)
        csv_path = LOG_DIR / f"pipedrive_{entity}_fields_{timestamp}.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=[
                    "entity",
                    "name",
                    "key",
                    "field_type",
                    "edit_flag",
                    "add_visible_flag",
                    "options",
                ],
            )
            writer.writeheader()
            for item in fields:
                writer.writerow(
                    {
                        "entity": entity,
                        "name": item.get("name", ""),
                        "key": item.get("key", ""),
                        "field_type": item.get("field_type", ""),
                        "edit_flag": item.get("edit_flag", ""),
                        "add_visible_flag": item.get("add_visible_flag", ""),
                        "options": "; ".join(
                            str(option.get("label", ""))
                            for option in item.get("options", []) or []
                        ),
                    }
                )

        logger.info("Exported %s %s fields to %s", len(fields), entity, csv_path)
        logger.info("%s fields:", entity.capitalize())
        for item in fields:
            logger.info(
                "  name=%r key=%r type=%r",
                item.get("name", ""),
                item.get("key", ""),
                item.get("field_type", ""),
            )


def upsert_organization(
    client: PipedriveClient | None,
    payload: dict[str, Any],
    dry_run: bool,
    logger: logging.Logger,
) -> tuple[int | None, str]:
    name = payload.get("name")
    if not name:
        return None, "skipped"

    if dry_run:
        logger.info("[dry-run] Would search/create/update organization: %s", payload)
        return None, "created"

    assert client is not None
    existing = client.search_organization_by_name(str(name))
    existing_id = extract_entity_id(existing)
    if existing_id:
        client.update_entity("organization", existing_id, payload)
        return existing_id, "updated"

    created = client.create_entity("organization", payload)
    return extract_entity_id(created), "created"


def upsert_person(
    client: PipedriveClient | None,
    payload: dict[str, Any],
    org_id: int | None,
    dry_run: bool,
    logger: logging.Logger,
) -> tuple[int | None, str]:
    if org_id:
        payload = {**payload, "org_id": org_id}

    email = payload.get("email")
    name = payload.get("name")
    if not email and not name:
        return None, "skipped"

    if dry_run:
        logger.info("[dry-run] Would search/create/update person: %s", payload)
        return None, "created"

    assert client is not None
    existing = client.search_person_by_email(str(email)) if email else None
    if not existing and name:
        existing = client.search_person_by_name(str(name))

    existing_id = extract_entity_id(existing)
    if existing_id:
        client.update_entity("person", existing_id, payload)
        return existing_id, "updated"

    created = client.create_entity("person", payload)
    return extract_entity_id(created), "created"


def create_deal(
    client: PipedriveClient | None,
    payload: dict[str, Any],
    org_id: int | None,
    person_id: int | None,
    dry_run: bool,
    logger: logging.Logger,
) -> bool:
    if org_id:
        payload = {**payload, "org_id": org_id}
    if person_id:
        payload = {**payload, "person_id": person_id}

    if not payload.get("title"):
        logger.info("Skipping deal because no title was mapped")
        return False

    if dry_run:
        logger.info("[dry-run] Would create deal: %s", payload)
        return True

    assert client is not None
    client.create_entity("deal", payload)
    return True


def process_row(
    row_number: int,
    row: pd.Series,
    client: PipedriveClient | None,
    field_lookup: dict[str, dict[str, str]],
    metadata: PipedriveMetadata | None,
    stats: ImportStats,
    dry_run: bool,
    logger: logging.Logger,
) -> None:
    mapped = map_row(row, field_lookup, metadata, stats, logger)
    org_id, org_action = upsert_organization(client, mapped["organization"], dry_run, logger)
    if org_action == "created":
        stats.organizations_created += 1
    elif org_action == "updated":
        stats.organizations_updated += 1

    person_id, person_action = upsert_person(client, mapped["person"], org_id, dry_run, logger)
    if person_action == "created":
        stats.persons_created += 1
    elif person_action == "updated":
        stats.persons_updated += 1

    if create_deal(client, mapped["deal"], org_id, person_id, dry_run, logger):
        stats.deals_created += 1

    logger.info("Processed row %s", row_number)


def log_summary(path: Path, stats: ImportStats, logger: logging.Logger) -> None:
    logger.info(
        "Summary for %s: rows=%s, organizations created=%s, organizations updated=%s, "
        "persons created=%s, persons updated=%s, deals created=%s, failed rows=%s",
        path.name,
        stats.rows,
        stats.organizations_created,
        stats.organizations_updated,
        stats.persons_created,
        stats.persons_updated,
        stats.deals_created,
        stats.failed_rows,
    )
    for error in stats.row_errors:
        logger.error(error)
    if stats.skipped_fields:
        logger.warning(
            "Skipped mapped fields missing in Pipedrive: %s",
            ", ".join(sorted(stats.skipped_fields)),
        )


def process_file(
    path: Path,
    client: PipedriveClient | None,
    field_lookup: dict[str, dict[str, str]],
    metadata: PipedriveMetadata | None,
    dry_run: bool,
    logger: logging.Logger,
) -> bool:
    logger.info("Processing file: %s", path.name)
    try:
        dataframe = load_xlsx_file(path)
    except Exception as exc:
        logger.exception("Failed to read %s", path.name)
        if not dry_run:
            moved_to = move_file(path, FAILED_DIR)
            logger.error("Moved %s to %s", path.name, moved_to)
        return False

    stats = ImportStats(rows=len(dataframe))
    stats.unmapped_columns = detected_unmapped_columns(list(dataframe.columns))
    print_column_summary(path, list(dataframe.columns), stats.unmapped_columns, logger)

    for index, row in dataframe.iterrows():
        row_number = int(index) + 2
        try:
            process_row(row_number, row, client, field_lookup, metadata, stats, dry_run, logger)
        except Exception as exc:
            stats.failed_rows += 1
            message = f"Row {row_number} failed in {path.name}: {exc}"
            stats.row_errors.append(message)
            logger.exception(message)

    log_summary(path, stats, logger)
    file_failed = stats.rows > 0 and stats.failed_rows == stats.rows

    if dry_run:
        logger.info("[dry-run] Leaving %s in input folder", path.name)
        return not file_failed

    destination = FAILED_DIR if file_failed else PROCESSED_DIR
    moved_to = move_file(path, destination)
    logger.info("Moved %s to %s", path.name, moved_to)
    return not file_failed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import XLSX files into Pipedrive.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Read and map files without calling Pipedrive or moving files.",
    )
    parser.add_argument(
        "--list-fields",
        action="store_true",
        help="Export Pipedrive deal, organization, and person field metadata to logs/.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logger = setup_logging()
    load_dotenv()

    ensure_directories()

    client: PipedriveClient | None = None
    if args.list_fields:
        if args.dry_run:
            logger.error("--list-fields requires real mode. Run without --dry-run.")
            return 1
        api_token = os.getenv("PIPEDRIVE_API_TOKEN")
        base_url = os.getenv("PIPEDRIVE_BASE_URL", "https://api.pipedrive.com/v1")
        if not api_token:
            logger.error("PIPEDRIVE_API_TOKEN is required in .env or the environment")
            return 1
        client = PipedriveClient(api_token=api_token, base_url=base_url, logger=logger)
        export_pipedrive_fields(client, logger)
        return 0

    files = list_input_files()
    if not files:
        logger.info("No .xlsx files found in %s", INPUT_DIR)
        return 0

    if args.dry_run:
        field_lookup = dry_run_field_lookup()
        metadata = None
        logger.info("Running in dry-run mode. No API calls or file moves will be made.")
    else:
        api_token = os.getenv("PIPEDRIVE_API_TOKEN")
        base_url = os.getenv("PIPEDRIVE_BASE_URL", "https://api.pipedrive.com/v1")
        if not api_token:
            logger.error("PIPEDRIVE_API_TOKEN is required in .env or the environment")
            return 1
        client = PipedriveClient(api_token=api_token, base_url=base_url, logger=logger)
        metadata = client.load_metadata()
        field_lookup = metadata.field_lookup

    successes = 0
    failures = 0
    for path in files:
        if process_file(path, client, field_lookup, metadata, args.dry_run, logger):
            successes += 1
        else:
            failures += 1

    logger.info("Import finished: successful files=%s, failed files=%s", successes, failures)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
