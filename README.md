# local.ch to Pipedrive Application

Flask application and deterministic Python tooling for transforming local.ch exports, importing them into Pipedrive, and migrating Pipedrive configuration. The transformation formats are defined by `docs/Prompt pour import Pipedrive.docx`.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a local environment file:

```bash
cp .env.example .env
```

Set these values in `.env`:

```env
PIPEDRIVE_API_TOKEN=your_pipedrive_api_token
PIPEDRIVE_BASE_URL=https://api.pipedrive.com/v1
PIPEDRIVE_PIPELINE_NAME=CAMILLE - PME-KMU
PIPEDRIVE_FORCE_IPV4=1
FLASK_SECRET_KEY=any-local-random-string
APP_USERNAME=admin
APP_PASSWORD=choose-a-strong-password
FLASK_RUN_HOST=127.0.0.1
FLASK_RUN_PORT=5000
```

The app also loads `importer/.env`, so keeping the existing importer token there works too.

## Web App

```bash
source .venv/bin/activate
python src/web_app.py
```

Open `http://127.0.0.1:5000`.

The web flow is:

1. Upload a raw local.ch scraper `.xlsx`, `.xls`, or `.csv`.
2. The app generates V2 and V3 files under `web_storage/`.
3. Preview the generated V3 table in the browser.
4. Download V2/V3 outputs, run a Pipedrive dry-run, or upload the V3 XLSX to Pipedrive.

Real imports run in the background. The upload overlay shows processed and remaining rows, and the final result is persisted in the job directory. Deals are restricted to the pipeline named by `PIPEDRIVE_PIPELINE_NAME`; startup validation stops the import if that pipeline does not exist. Existing deals with the same title and linked organization/person are skipped.

## Project structure

The Flask application uses an application factory and feature blueprints:

- `src/web/blueprints/`: authentication, transformation/job, and import routes.
- `src/web/services/`: business orchestration used by routes.
- `src/web/presentation.py` and `src/web/views.py`: HTML rendering and browser behavior.
- `src/configuration/`: Pipedrive configuration migration implementations.
- `src/automations/`: boundary for future application-owned automations.
- `src/web_app.py`: backward-compatible local and Gunicorn entry point.
- `importer/`: importer domain logic and mapping.

All historical URL paths and Flask endpoint names remain available. See [context.md](context.md) for the detailed architecture and current automation status.

## Pipedrive preparation

Before importing, configure the target company in Pipedrive:

1. Open any deal's detail view, click **Label** in its left-side summary, then choose **+ Add new label** and create `TOP`. You can also add it from the Deals list view through the label pencil icon.
2. Open the upper-right account menu, choose **Manage users**, then **+ User**. Invite or activate a user whose displayed name is exactly `Fabien` (use `Fabian` instead only if the workbook is changed to that spelling).
3. Open **Deals**, select the `CAMILLE - PME-KMU` pipeline, and use the pencil icon beside the pipeline selector to verify its exact name and stages. Stage values in the workbook are matched only inside this pipeline. An unknown stage is placed in the pipeline's first stage.

Completed job results include `created_organization_ids`, `created_person_ids`, and `created_deal_ids` for audit and cleanup. Deal duplicate detection makes retrying a partially completed file safe for deals.

## Configuration migration

The existing CLI commands remain unchanged:

```bash
python src/export_pipedrive_config.py --output-dir pipedrive_config_exports
python src/import_pipedrive_config.py --export pipedrive_config_exports/<snapshot>.json
python src/import_pipedrive_config.py --export pipedrive_config_exports/<snapshot>.json --apply
```

The command wrappers delegate to `src/configuration/`.

## Automations

AUT-02 is complete using five native Pipedrive automations. Moving a deal to Call 1–5 creates its corresponding Appel 1–5 activity with the predefined due date and weekend-skipping behavior.

AUT-03 is not implemented. Slack and the Pipedrive Deal/Updated webhook are configured externally. The planned application flow is HTTP Basic Auth validation, payload parsing, an exact `R1 PRIS` stage check, and a Slack notification to `#appointments`. The `src/automations/` package documents the intended boundary; no webhook route or Slack code has been added yet.

## Koyeb Deployment

The repository includes a `Procfile`:

```bash
web: gunicorn --bind 0.0.0.0:$PORT src.web_app:app
```

Set these environment variables in Koyeb:

```env
PIPEDRIVE_API_TOKEN=your_pipedrive_api_token
PIPEDRIVE_BASE_URL=https://api.pipedrive.com/v1
PIPEDRIVE_PIPELINE_NAME=CAMILLE - PME-KMU
PIPEDRIVE_FORCE_IPV4=1
FLASK_SECRET_KEY=generate-a-long-random-secret
APP_USERNAME=admin
APP_PASSWORD=choose-a-strong-password
```

Koyeb provides `PORT` automatically. Do not set `FLASK_RUN_HOST` for production.

Important deployment note: generated files are stored on the app filesystem under `web_storage/`. That is fine for short-lived upload/import sessions, but the files are not permanent if the service restarts or scales across instances.

## Transform

```bash
python src/transform.py --input "docs/localch_export_serrurerie à romandie_20260427_215114.xlsx" --output-dir output
```

This writes:

- `[source_filename]_V2.xlsx`
- `[source_filename]_V2.csv`
- `[source_filename]_V3.xlsx`
- `[source_filename]_V3.csv`

CSV files are UTF-8 encoded and use `;` as separator.

## Compare Against Reference V3

```bash
python src/compare_outputs.py \
  --generated "output/localch_export_serrurerie à romandie_20260427_215114_V3.csv" \
  --reference "docs/localch_export_Serrurerie_a_Region_lemanique_20260416_231720_V3.csv"
```

The comparison report includes row/column count differences, missing and extra columns, column order differences, per-column mismatch counts, sample mismatching cells, and exact match percentage.

## Notes

- The implementation uses pandas/openpyxl/python-docx only. It does not use the OpenAI SDK.
- Missing, empty, null-like, `N/A`, and `NaN` values are normalized to `ND`.
- Booleans are normalized to `oui`, `non`, or `ND`.
- `persons` is parsed with deterministic priority: president first, director second, remaining people after that, capped at four.
- `phone_numbers` is split into up to four deduplicated phone columns.
