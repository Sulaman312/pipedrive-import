# Repository Context

## Purpose and current status

This repository transforms local.ch exports into Pipedrive V2/V3 files, imports them through the Pipedrive API, migrates Pipedrive account configuration, and provides the hosted Flask interface used to operate those workflows.

Completed:

- Deterministic transformation pipeline.
- Pipedrive organization/person/deal importer.
- Web upload, preview, download, dry-run, background import, progress, and result flow.
- Pipedrive configuration export/import tooling.
- Test Pipedrive account configuration and data import.
- AUT-02 native Pipedrive automations.

AUT-03 is the next automation. Its webhook and Slack integration are intentionally not implemented yet.

## Application architecture

```text
src/
├── web_app.py                    # Existing local/Koyeb compatibility entry point
├── web/
│   ├── app.py                    # Flask application factory and auth guard
│   ├── blueprints/
│   │   ├── auth.py               # Login/logout routes
│   │   ├── transformations.py    # Upload, preview, and download routes
│   │   ├── imports.py            # Import start, status, and result routes
│   │   └── webhooks.py           # Empty AUT-03 boundary; no endpoint yet
│   ├── services/
│   │   ├── auth.py               # Credential policy
│   │   ├── transformations.py    # Upload/transformation orchestration
│   │   ├── imports.py            # Background import orchestration
│   │   └── storage.py            # Job files, previews, and status persistence
│   ├── presentation.py           # Shared page shell, CSS, and browser behavior
│   ├── views.py                  # Page-specific rendering
│   └── paths.py                  # Shared repository paths
├── configuration/
│   ├── exporter.py               # Configuration export implementation
│   └── importer.py               # Configuration import implementation
├── automations/
│   └── README.md                 # Boundary and plan for application automations
├── transform.py                  # Transformation behavior and CLI
├── utils.py                      # Parsing/normalization helpers
└── compare_outputs.py            # Comparison CLI

importer/
├── importer.py                   # Pipedrive import domain implementation and CLI
├── mapping.py                    # V3-to-Pipedrive field mapping
└── context.md                    # Importer-specific behavior
```

Business logic does not belong in Flask route handlers. Blueprints validate HTTP input and delegate to services. The transformer and importer remain independent domain modules and retain their CLI behavior.

`src/web_app.py` still exports `app`, so the existing Procfile and local command remain valid. Historical Flask endpoint names are registered as aliases; existing URL paths and `url_for()` names remain compatible.

## Existing HTTP endpoints

- `GET /` – upload page.
- `POST /upload` – transform an uploaded source file.
- `GET /jobs/<job_id>` – preview a transformed V3 file.
- `GET /jobs/<job_id>/download/<version>.<extension>` – download generated output.
- `POST /jobs/<job_id>/import` – start dry-run or real Pipedrive import.
- `GET /jobs/<job_id>/import/status` – read background import progress.
- `GET /jobs/<job_id>/import/result` – display the persisted result.
- `GET|POST /login` and `GET /logout` – internal session authentication.

No AUT-03 webhook endpoint exists yet.

## Main user flow

1. Sign in to the internal web app.
2. Upload a raw local.ch CSV or Excel export.
3. Generate V2 and V3 outputs.
4. Preview or download generated data.
5. Run a dry-run.
6. Start a real background import.
7. Follow persisted progress and review the result.

## Setup and deployment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python src/web_app.py
```

Koyeb continues to use:

```text
web: gunicorn --bind 0.0.0.0:$PORT src.web_app:app
```

`web_storage/` is ephemeral and the current background worker is in-process. This is appropriate for the current single-instance deployment but is not a durable distributed queue.

## Environment

- `FLASK_SECRET_KEY`, `APP_USERNAME`, `APP_PASSWORD` – internal web session authentication.
- `PIPEDRIVE_API_TOKEN`, `PIPEDRIVE_BASE_URL` – target Pipedrive account.
- `PIPEDRIVE_PIPELINE_NAME` – required deal pipeline; currently `CAMILLE - PME-KMU`.
- `PIPEDRIVE_FORCE_IPV4` – defaults to `1` for the current host's broken IPv6 route.
- `FLASK_RUN_HOST`, `FLASK_RUN_PORT` – optional local settings; Koyeb supplies `PORT`.

Never commit `.env` files or expose credentials in logs or documentation.

## Transformation and import behavior

Transformation is deterministic and does not use OpenAI. V2 cleans and normalizes scraper data; V3 has the fixed Pipedrive mapping/order requested by the original prompt.

The importer:

- Matches organizations by exact normalized name.
- Matches people by valid email and then name.
- Updates existing organizations/people.
- Deduplicates deals by title plus linked organization/person.
- Restricts deals and stage lookup to `PIPEDRIVE_PIPELINE_NAME`.
- Resolves Pipedrive stage, label, and owner IDs dynamically.
- Persists background progress and created entity IDs in each web job.
- Stops a web import on systemic Pipedrive API/transport failures.

See `importer/context.md` for CLI-specific details.

## Configuration migration

The implementations live under `src/configuration/`. Existing commands remain compatible through wrappers:

```bash
python src/export_pipedrive_config.py --output-dir pipedrive_config_exports
python src/import_pipedrive_config.py --export <snapshot.json>
python src/import_pipedrive_config.py --export <snapshot.json> --apply
```

The retained production snapshot is `pipedrive_config_exports/pipedrive_config_export_20260625_165205.json`. Configuration migration does not copy business records or account users.

## AUT-02 – complete

AUT-02 is implemented entirely with five separate native Pipedrive automations. Each triggers when a deal's stage changes to its corresponding call stage and creates a linked activity with predefined due date behavior and weekend skipping:

- Call 1 → activity type/subject `Appel 1`.
- Call 2 → activity type/subject `Appel 2`.
- Call 3 → activity type/subject `Appel 3`.
- Call 4 → activity type/subject `Appel 4`.
- Call 5 → activity type/subject `Appel 5`.

No AUT-02 application code should be added unless the architecture decision changes explicitly.

## AUT-03 – prepared, not implemented

External setup already completed:

- Slack workspace, `#appointments` channel, Slack App, `chat:write`, installation, bot token, incoming webhook, and bot channel invitation.
- Pipedrive Deal/Updated webhook targeting the existing Koyeb Flask application with HTTP Basic Authentication enabled.

Planned flow:

```text
Pipedrive Deal Updated webhook
    → dedicated webhook blueprint
    → validate HTTP Basic Authentication
    → parse payload
    → automation service checks Deal Stage == "R1 PRIS"
        → false: return HTTP 200
        → true: collect deal data → build message → Slack client → #appointments
```

When implemented, keep HTTP concerns in a new webhook blueprint and keep stage decisions and Slack delivery in separate automation modules. Define webhook authentication as an explicit public-route exception to the current session-login guard. Do not place AUT-03 logic in import or transformation services.

Open AUT-03 decisions include message fields, appointment date/time source, duplicate-event policy, retry behavior, secret variable names, and failure reporting.

## Safety

- Verify the target account before real imports or configuration `--apply` runs.
- Test automations only against the test account.
- Preserve the retained configuration snapshot.
- Do not implement AUT-03 until its remaining behavior and secret contract are confirmed.
