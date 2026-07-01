# Project Context

This project is a Python-based automation for importing XLSX rows into Pipedrive through the REST API. It replaces manual spreadsheet uploads in the Pipedrive import UI.

## Main Files

- `importer.py`: CLI entry point and main importer logic.
- `mapping.py`: source-of-truth mapping from XLSX column names to Pipedrive entities/fields.
- `.env`: local runtime secrets, not committed. Must contain `PIPEDRIVE_API_TOKEN`.
- `.env.example`: template environment file.
- `requirements.txt`: Python dependencies.
- `README.md`: setup and usage instructions.

## Runtime Folders

- `input/`: `.xlsx` files waiting to be imported.
- `processed/`: files moved here after a successful normal import.
- `failed/`: files moved here if the whole file fails.
- `logs/`: timestamped run logs and field metadata CSV exports.

Dry-run mode does not move files.

## Commands

Install dependencies:

```bash
pip install -r requirements.txt
```

Create local env file:

```bash
cp .env.example .env
```

Dry-run import:

```bash
python importer.py --dry-run
```

Real import:

```bash
python importer.py
```

Export Pipedrive field metadata:

```bash
python importer.py --list-fields
```

Use `python3` instead of `python` if the local environment does not provide `python`.

## Import Flow

For each `.xlsx` file in `input/`:

1. Read the workbook with `pandas`/`openpyxl`.
2. Print and log detected columns.
3. Normalize column names so small XLSX differences still match, including:
   - curly apostrophes vs straight apostrophes
   - en dash/em dash vs hyphen
   - spacing around `-` and `_`
4. Map each row into three payloads:
   - organization
   - person
   - deal
5. In real mode, fetch Pipedrive metadata:
   - deal fields
   - organization fields
   - person fields
   - stages
   - users
   - field options such as deal labels
6. Upsert organization by name.
7. Upsert person by email first, then name.
8. Create a deal linked to the organization/person IDs when available, restricted to `PIPEDRIVE_PIPELINE_NAME`.
9. The CLI continues after row-level errors; the web service stops on systemic Pipedrive API/transport errors.
10. Move the file to `processed/` unless every row failed, in which case move it to `failed/`.

## Duplicate Behavior

The current behavior mimics Pipedrive's "merge data" behavior only partially:

- Organizations are deduplicated by exact organization name search.
- Persons are deduplicated by email first, then name.
- Deals are deduplicated by exact normalized title plus linked organization/person.

This means re-importing the same file updates the existing organization/person and skips the existing deal.

## Important Field Handling

`mapping.py` contains `FIELD_MAPPING` for XLSX column to Pipedrive visible field names.

`STANDARD_FIELD_ALIASES` maps selected visible field names to API keys directly. Important examples:

- deal title: `title`
- deal label: `label`
- deal stage: `stage_id`
- organization owner: `owner_id`
- organization name: `name`
- organization address fields: `address`, `address_route`, `address_postal_code`, `address_locality`
- person name: `name`
- person email: `email`
- person phone: `phone`

Some Pipedrive fields require IDs rather than display text:

- Deal stage values such as `Prospects` are resolved to `stage_id`.
- Deal labels such as `TOP` are resolved to Pipedrive label option IDs.
- Organization owner values such as `Fabien` are resolved to a Pipedrive user ID.

Resolution is handled in `resolve_pipedrive_value()` in `importer.py`.

## Pipedrive Dashboard Verification

API imports do not appear in Pipedrive's spreadsheet import history page. That page only tracks imports done through the Pipedrive UI.

To verify API imports:

- Search organizations under `Contacts > Organizations`.
- Search persons under `Contacts > People`.
- Search deals under `Deals`.
- Check the local logs under `logs/`.
- Check whether the file moved from `input/` to `processed/`.

For the generated test workbook, useful search values were:

- Organization: `TEST API ORGANISATION 2026-06-23 UNIQUE`
- Person email: `person-test-api-20260623@example.com`
- Deal: `TEST API DEAL 2026-06-23 UNIQUE`

## Known Limitations

- Row-level audit CSVs with entity IDs are not implemented yet.
- The importer skips a mapped custom field if the Pipedrive account does not expose a matching field name/key.
- Stage matching is restricted to the configured pipeline. Users and label options use normalized matching with containment fallback.
- `ND` is currently imported as a normal value because the user indicated it should be preserved.

## Useful Next Improvements

- Add an import audit CSV with row number, organization ID/action, person ID/action, deal ID/action, and error.
- Add configurable matching rules for users, stages, and labels.
- Add tests for column normalization and value resolution.
