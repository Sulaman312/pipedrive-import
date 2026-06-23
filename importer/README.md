# Pipedrive XLSX Importer

Python automation for importing `.xlsx` files into Pipedrive organizations, persons, and deals.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set:

```env
PIPEDRIVE_API_TOKEN=your_token_here
PIPEDRIVE_BASE_URL=https://api.pipedrive.com/v1
```

The API token is never hardcoded in the script.

## Folders

- `input/`: place `.xlsx` files here before running the importer.
- `processed/`: successfully processed files are moved here in normal mode.
- `failed/`: unreadable files, or files where every row fails, are moved here in normal mode.
- `logs/`: each run writes a timestamped log file here.

Dry-run mode does not move files.

## Run a Dry Run

```bash
python importer.py --dry-run
```

Dry-run mode reads each `.xlsx` file, prints detected columns, logs unmapped columns, maps row data, and shows what would be created or updated. It does not call the Pipedrive API and does not move files.

## Run a Real Import

```bash
python importer.py
```

Normal mode:

1. Loads Pipedrive field metadata from `/dealFields`, `/organizationFields`, and `/personFields`.
2. Builds a visible field name to API field key lookup.
3. Reads `.xlsx` files from `input/`.
4. Ignores extra unmapped columns while logging them.
5. Searches organizations by name, updating when found and creating when missing.
6. Searches persons by email first, then by name, updating when found and creating when missing.
7. Creates deals linked to the organization and person when IDs are available.
8. Moves completed files to `processed/` or fully failed files to `failed/`.

For fields that use Pipedrive internal IDs, the importer resolves values dynamically:

- Deal stage: spreadsheet text such as `Prospects` is matched to a Pipedrive stage and sent as `stage_id`.
- Deal label: spreadsheet text such as `TOP` is matched to a Pipedrive label option and sent as `label`.
- Organization owner: spreadsheet text such as `Fabien` is matched to a Pipedrive user and sent as `owner_id`.

## List Pipedrive Fields

```bash
python importer.py --list-fields
```

This exports the current deal, organization, and person field metadata to CSV files in `logs/`, including option labels where Pipedrive exposes them.

## Mapping

The source of truth for column mapping is `FIELD_MAPPING` in `mapping.py`.

Standard Pipedrive fields are handled explicitly:

- Deal title maps to `title`.
- Organization name maps to `name`.
- Organization address fields map to standard address keys where applicable.
- Person name maps to `name`.
- Person email maps to `email`.
- Person phone maps to `phone`.

All other mapped fields are resolved dynamically from Pipedrive field metadata before upload.
