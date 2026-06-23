# local.ch to Pipedrive V2/V3 Transformer

Deterministic Python pipeline for transforming a local.ch scraper export into the V2 and V3 Pipedrive import formats described in `docs/Prompt pour import Pipedrive.docx`.

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

## Koyeb Deployment

The repository includes a `Procfile`:

```bash
web: gunicorn --bind 0.0.0.0:$PORT src.web_app:app
```

Set these environment variables in Koyeb:

```env
PIPEDRIVE_API_TOKEN=your_pipedrive_api_token
PIPEDRIVE_BASE_URL=https://api.pipedrive.com/v1
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
