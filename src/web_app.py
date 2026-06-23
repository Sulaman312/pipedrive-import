from __future__ import annotations

import hmac
import logging
import os
import shutil
import sys
import uuid
from pathlib import Path
from typing import Any

import pandas as pd
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template_string, request, send_file, session, url_for
from werkzeug.utils import secure_filename

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = Path(__file__).resolve().parent
IMPORTER_DIR = ROOT_DIR / "importer"
WEB_STORAGE_DIR = ROOT_DIR / "web_storage"
ALLOWED_EXTENSIONS = {".xlsx", ".xls", ".csv"}

sys.path.insert(0, str(SRC_DIR))
from transform import transform


sys.path.insert(0, str(IMPORTER_DIR))
import importer as pipedrive_importer  # noqa: E402

load_dotenv(ROOT_DIR / ".env")
load_dotenv(IMPORTER_DIR / ".env")

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "local-dev-secret-change-me")


def ensure_web_storage() -> None:
    WEB_STORAGE_DIR.mkdir(exist_ok=True)


def auth_configured() -> bool:
    return bool(os.getenv("APP_USERNAME") and os.getenv("APP_PASSWORD"))


def is_authenticated() -> bool:
    return bool(session.get("authenticated"))


def credentials_match(username: str, password: str) -> bool:
    expected_username = os.getenv("APP_USERNAME", "")
    expected_password = os.getenv("APP_PASSWORD", "")
    return hmac.compare_digest(username, expected_username) and hmac.compare_digest(password, expected_password)


def job_dir(job_id: str) -> Path:
    return WEB_STORAGE_DIR / job_id


def find_job_file(job_id: str, suffix: str) -> Path:
    matches = sorted(job_dir(job_id).glob(f"*_{suffix}"))
    if not matches:
        raise FileNotFoundError(f"No {suffix} file found for job {job_id}")
    return matches[0]


def build_preview(path: Path, limit: int | None = None) -> dict[str, Any]:
    df = pd.read_excel(path, dtype=str).fillna("ND")
    visible_df = df if limit is None else df.head(limit)
    return {
        "rows": visible_df.to_dict(orient="records"),
        "columns": list(df.columns),
        "row_count": len(df),
        "column_count": len(df.columns),
        "preview_count": len(visible_df),
    }


def import_v3(path: Path, dry_run: bool) -> dict[str, Any]:
    logger = pipedrive_importer.setup_logging()
    for handler in list(logger.handlers):
        if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
            logger.removeHandler(handler)
    if dry_run:
        logger.setLevel(logging.WARNING)
    pipedrive_importer.ensure_directories()

    client = None
    metadata = None
    if dry_run:
        field_lookup = pipedrive_importer.dry_run_field_lookup()
        logger.info("Web import dry-run for %s", path.name)
    else:
        api_token = os.getenv("PIPEDRIVE_API_TOKEN")
        base_url = os.getenv("PIPEDRIVE_BASE_URL", "https://api.pipedrive.com/v1")
        if not api_token:
            raise RuntimeError("PIPEDRIVE_API_TOKEN is missing. Add it to .env or importer/.env.")
        client = pipedrive_importer.PipedriveClient(api_token=api_token, base_url=base_url, logger=logger)
        metadata = client.load_metadata()
        field_lookup = metadata.field_lookup
        logger.info("Web real import for %s", path.name)

    dataframe = pipedrive_importer.load_xlsx_file(path)
    stats = pipedrive_importer.ImportStats(rows=len(dataframe))
    stats.unmapped_columns = pipedrive_importer.detected_unmapped_columns(list(dataframe.columns))
    pipedrive_importer.print_column_summary(path, list(dataframe.columns), stats.unmapped_columns, logger)

    for index, row in dataframe.iterrows():
        row_number = int(index) + 2
        try:
            pipedrive_importer.process_row(
                row_number,
                row,
                client,
                field_lookup,
                metadata,
                stats,
                dry_run,
                logger,
            )
        except Exception as exc:
            stats.failed_rows += 1
            message = f"Row {row_number} failed in {path.name}: {exc}"
            stats.row_errors.append(message)
            logger.exception(message)

    pipedrive_importer.log_summary(path, stats, logger)
    return {
        "dry_run": dry_run,
        "rows": stats.rows,
        "organizations_created": stats.organizations_created,
        "organizations_updated": stats.organizations_updated,
        "persons_created": stats.persons_created,
        "persons_updated": stats.persons_updated,
        "deals_created": stats.deals_created,
        "failed_rows": stats.failed_rows,
        "unmapped_columns": stats.unmapped_columns,
        "skipped_fields": sorted(stats.skipped_fields),
        "row_errors": stats.row_errors[:20],
    }


BASE_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>local.ch to Pipedrive</title>
  <style>
    :root {
      --bg: #f7f8fa;
      --panel: #ffffff;
      --ink: #1f2933;
      --muted: #667085;
      --line: #d9dee7;
      --accent: #0f766e;
      --accent-strong: #115e59;
      --warn: #b45309;
      --danger: #b42318;
      --soft: #eef6f5;
      --shadow: 0 18px 40px rgba(31, 41, 51, .08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: var(--bg);
    }
    .shell { max-width: 1180px; margin: 0 auto; padding: 28px 22px 48px; }
    .topbar {
      display: flex; justify-content: space-between; align-items: center;
      gap: 18px; padding-bottom: 22px; border-bottom: 1px solid var(--line);
    }
    .brand { display: flex; gap: 12px; align-items: center; }
    .brand-mark {
      width: 38px; height: 38px; border-radius: 8px; background: #e8f3f1;
      color: var(--accent); display: grid; place-items: center; border: 1px solid #c8e3df;
    }
    h1 { font-size: 22px; line-height: 1.2; margin: 0; letter-spacing: 0; }
    .subtitle { color: var(--muted); margin: 4px 0 0; font-size: 14px; }
    .header-actions { display: flex; align-items: center; gap: 10px; }
    .flow-tabs {
      display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px;
      margin-top: 20px; padding: 6px; border: 1px solid var(--line); border-radius: 8px; background: #eef2f5;
    }
    .flow-tab {
      display: flex; align-items: center; justify-content: center; gap: 8px;
      min-height: 42px; border-radius: 7px; color: #52606d; text-decoration: none; font-size: 14px; font-weight: 700;
      border: 1px solid transparent;
    }
    .flow-tab.active { background: #fff; color: var(--accent-strong); border-color: #c8e3df; box-shadow: 0 6px 18px rgba(31, 41, 51, .07); }
    .flow-tab.disabled { opacity: .48; pointer-events: none; }
    .grid { display: grid; grid-template-columns: 360px minmax(0, 1fr); gap: 20px; margin-top: 22px; align-items: start; }
    .full-width { margin-top: 22px; }
    .single { max-width: 860px; margin: 22px auto 0; }
    .panel {
      background: var(--panel); border: 1px solid var(--line); border-radius: 8px; box-shadow: var(--shadow);
    }
    .panel-header { padding: 18px 18px 0; }
    .panel-title { font-size: 15px; font-weight: 700; margin: 0; }
    .panel-body { padding: 18px; }
    .steps { display: grid; gap: 10px; }
    .step {
      display: grid; grid-template-columns: 30px 1fr; gap: 10px; padding: 10px;
      border: 1px solid var(--line); border-radius: 8px; background: #fbfcfd;
    }
    .step-icon { width: 30px; height: 30px; display: grid; place-items: center; color: var(--accent); background: var(--soft); border-radius: 7px; }
    .step strong { display: block; font-size: 13px; }
    .step span { color: var(--muted); font-size: 12px; line-height: 1.35; }
    .upload-box {
      border: 1px dashed #9aa8b8; border-radius: 8px; padding: 28px; background: #fbfcfd;
      display: grid; gap: 18px; min-height: 210px; align-content: center;
    }
    .file-prompt { display: flex; gap: 14px; align-items: center; }
    .file-prompt-icon { width: 44px; height: 44px; display: grid; place-items: center; color: var(--accent); background: var(--soft); border-radius: 8px; border: 1px solid #c8e3df; }
    .file-prompt strong { display: block; font-size: 16px; }
    .file-prompt span { color: var(--muted); font-size: 13px; }
    input[type=file] { width: 100%; font-size: 14px; color: var(--muted); padding: 10px; border: 1px solid var(--line); border-radius: 8px; background: #fff; }
    input[type=text], input[type=password] {
      width: 100%; border: 1px solid var(--line); border-radius: 8px; background: #fff;
      padding: 11px 12px; font-size: 14px; color: var(--ink); outline: none;
    }
    input[type=text]:focus, input[type=password]:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(15, 118, 110, .12); }
    label { display: grid; gap: 7px; color: #344054; font-size: 13px; font-weight: 650; }
    .form-stack { display: grid; gap: 14px; }
    .login-shell { min-height: calc(100vh - 56px); display: grid; place-items: center; }
    .login-panel { width: min(420px, 100%); }
    .actions { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; }
    .button {
      appearance: none; border: 1px solid var(--line); border-radius: 8px; padding: 10px 13px;
      background: var(--panel); color: var(--ink); font-weight: 650; font-size: 14px;
      display: inline-flex; align-items: center; gap: 8px; text-decoration: none; cursor: pointer;
      min-height: 40px;
    }
    .button.primary { background: var(--accent); border-color: var(--accent); color: #fff; }
    .button.primary:hover { background: var(--accent-strong); }
    .button.danger { color: var(--danger); border-color: #f0b9b5; }
    .button:disabled { opacity: .55; cursor: not-allowed; }
    .flash { margin-top: 14px; padding: 11px 12px; border-radius: 8px; border: 1px solid #f1d7a8; color: #7c4a03; background: #fff8eb; font-size: 13px; }
    .metrics { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; margin-bottom: 16px; }
    .metric { border: 1px solid var(--line); border-radius: 8px; padding: 12px; background: #fbfcfd; }
    .metric span { color: var(--muted); font-size: 12px; }
    .metric strong { display: block; margin-top: 4px; font-size: 20px; }
    .table-wrap { overflow: auto; max-height: 640px; }
    table { border-collapse: collapse; width: 100%; min-width: 1320px; font-size: 12px; }
    th, td { border-bottom: 1px solid var(--line); padding: 9px 10px; text-align: left; vertical-align: top; white-space: nowrap; }
    th { position: sticky; top: 0; background: #f2f5f8; z-index: 1; color: #344054; font-weight: 700; }
    td { color: #384250; }
    .empty { padding: 52px 18px; text-align: center; color: var(--muted); }
    .result-list { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }
    .result-list .metric strong { font-size: 18px; }
    .result-hero { display: flex; justify-content: space-between; gap: 18px; align-items: center; margin-bottom: 16px; padding: 16px; border: 1px solid #c8e3df; border-radius: 8px; background: var(--soft); }
    .result-hero strong { display: block; font-size: 18px; }
    .result-hero span { color: var(--muted); font-size: 13px; }
    .table-actions { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 10px; padding: 14px; border-top: 1px solid var(--line); background: #fbfcfd; }
    .table-actions form { margin: 0; display: inline-flex; }
    .inline-error { margin: 14px; padding: 11px 12px; border-radius: 8px; border: 1px solid #f0b9b5; color: var(--danger); background: #fff4f2; font-size: 13px; }
    .notice { color: var(--muted); font-size: 13px; line-height: 1.5; margin-top: 12px; }
    svg { width: 18px; height: 18px; stroke-width: 2; }
    @media (max-width: 900px) {
      .grid { grid-template-columns: 1fr; }
      .topbar { align-items: flex-start; flex-direction: column; }
      .metrics, .result-list, .flow-tabs { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="shell">
    {% if show_header %}
    <header class="topbar">
      <div class="brand">
        <div class="brand-mark">{{ icon("workflow")|safe }}</div>
        <div>
          <h1>local.ch to Pipedrive</h1>
          <p class="subtitle">Upload, review, and send cleaned leads to Pipedrive.</p>
        </div>
      </div>
      <div class="header-actions">
        {% if authenticated %}
          <a class="button" href="{{ url_for('logout') }}">{{ icon("lock")|safe }} Sign out</a>
        {% endif %}
      </div>
    </header>
    {% endif %}
    {% with messages = get_flashed_messages() %}
      {% for message in messages %}<div class="flash">{{ message }}</div>{% endfor %}
    {% endwith %}
    {% if active_step %}
      <nav class="flow-tabs" aria-label="Progress">
        <a class="flow-tab {{ 'active' if active_step == 'upload' else '' }}" href="{{ url_for('index') }}">{{ icon("upload")|safe }} Upload</a>
        <a class="flow-tab {{ 'active' if active_step == 'preview' else '' }} {{ 'disabled' if not current_job else '' }}" href="{{ url_for('preview', job_id=current_job) if current_job else '#' }}">{{ icon("table")|safe }} Preview V3</a>
        <a class="flow-tab {{ 'active' if active_step == 'import' else '' }} {{ 'disabled' if not current_job else '' }}" href="{{ url_for('preview', job_id=current_job) if current_job else '#' }}">{{ icon("send")|safe }} Import</a>
      </nav>
    {% endif %}
    {{ body|safe }}
  </div>
</body>
</html>
"""


def icon(name: str) -> str:
    icons = {
        "workflow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M6 3v6"/><path d="M18 15v6"/><rect x="3" y="9" width="6" height="6" rx="1"/><rect x="15" y="3" width="6" height="6" rx="1"/><rect x="15" y="9" width="6" height="6" rx="1"/><path d="M9 12h6"/><path d="M18 15v0"/></svg>',
        "upload": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M12 16V4"/><path d="m7 9 5-5 5 5"/><path d="M20 16v4H4v-4"/></svg>',
        "table": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M3 5h18v14H3z"/><path d="M3 10h18"/><path d="M8 5v14"/></svg>',
        "send": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>',
        "download": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M12 3v12"/><path d="m7 10 5 5 5-5"/><path d="M5 21h14"/></svg>',
        "play": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M5 3v18l15-9Z"/></svg>',
        "key": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="7.5" cy="15.5" r="3.5"/><path d="m10 13 9-9"/><path d="m15 4 2 2"/><path d="m13 6 2 2"/></svg>',
        "file": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M14 2H6v20h12V8z"/><path d="M14 2v6h6"/></svg>',
        "lock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>',
    }
    return icons[name]


app.jinja_env.globals["icon"] = icon


def render_page(body: str, *, active_step: str | None = None, current_job: str | None = None, show_header: bool = True) -> str:
    return render_template_string(
        BASE_TEMPLATE,
        body=body,
        authenticated=is_authenticated(),
        active_step=active_step,
        current_job=current_job,
        show_header=show_header,
    )


@app.before_request
def require_login():
    if request.endpoint in {"login"}:
        return None
    if not auth_configured():
        if request.endpoint not in {"index"}:
            flash("Sign-in is not set up yet.")
            return redirect(url_for("index"))
        return None
    if not is_authenticated():
        return redirect(url_for("login", next=request.full_path if request.query_string else request.path))
    return None


@app.route("/login", methods=["GET", "POST"])
def login():
    if not auth_configured():
        flash("Sign-in is not set up yet.")
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if credentials_match(username, password):
            session.clear()
            session["authenticated"] = True
            return redirect(request.args.get("next") or url_for("index"))
        flash("Invalid username or password.")

    body = render_template_string(
        """
        <main class="login-shell">
          <section class="panel login-panel">
            <div class="panel-header"><h2 class="panel-title">Welcome back</h2></div>
            <div class="panel-body">
              <form class="form-stack" method="post">
                <label>Username<input type="text" name="username" autocomplete="username" required autofocus></label>
                <label>Password<input type="password" name="password" autocomplete="current-password" required></label>
                <button class="button primary" type="submit">{{ icon("lock")|safe }} Sign in</button>
              </form>
            </div>
          </section>
        </main>
        """
    )
    return render_page(body, show_header=False)


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.get("/")
def index() -> str:
    body = render_template_string(
        """
        <main class="single">
          <section class="panel">
            <div class="panel-header"><h2 class="panel-title">Upload source file</h2></div>
            <div class="panel-body">
              <form class="upload-box" action="{{ url_for('upload') }}" method="post" enctype="multipart/form-data">
                <div class="file-prompt">
                  <div class="file-prompt-icon">{{ icon("file")|safe }}</div>
                  <div>
                    <strong>Select the local.ch export</strong>
                    <span>Use the raw XLSX or CSV file. The app will prepare the V3 preview automatically.</span>
                  </div>
                </div>
                <input type="file" name="source_file" accept=".xlsx,.xls,.csv" required>
                <div class="actions">
                  <button class="button primary" type="submit">{{ icon("play")|safe }} Continue to preview</button>
                </div>
              </form>
            </div>
          </section>
        </main>
        """
    )
    return render_page(body, active_step="upload")


@app.post("/upload")
def upload():
    ensure_web_storage()
    file = request.files.get("source_file")
    if not file or not file.filename:
        flash("Choose a source XLSX, XLS, or CSV file.")
        return redirect(url_for("index"))

    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        flash("Unsupported file type. Upload XLSX, XLS, or CSV.")
        return redirect(url_for("index"))

    current_job = uuid.uuid4().hex
    directory = job_dir(current_job)
    directory.mkdir(parents=True, exist_ok=True)
    source_path = directory / secure_filename(file.filename)
    file.save(source_path)

    try:
        transform(source_path, directory)
    except Exception as exc:
        shutil.rmtree(directory, ignore_errors=True)
        flash(f"Transformation failed: {exc}")
        return redirect(url_for("index"))

    return redirect(url_for("preview", job_id=current_job))


@app.get("/jobs/<job_id>")
def preview(job_id: str) -> str:
    try:
        v3_xlsx = find_job_file(job_id, "V3.xlsx")
        preview_data = build_preview(v3_xlsx)
    except Exception as exc:
        flash(f"Could not load job preview: {exc}")
        return redirect(url_for("index"))

    body = render_template_string(
        """
        <main class="full-width">
          <section class="panel">
            <div class="table-wrap">
              <table>
                <thead><tr>{% for column in preview.columns %}<th>{{ column }}</th>{% endfor %}</tr></thead>
                <tbody>
                  {% for row in preview.rows %}
                    <tr>{% for column in preview.columns %}<td>{{ row[column] }}</td>{% endfor %}</tr>
                  {% endfor %}
                </tbody>
              </table>
            </div>
            <div class="table-actions">
              <a class="button" href="{{ url_for('download', job_id=job_id, version='V2', extension='xlsx') }}">{{ icon("download")|safe }} Download V2</a>
              <a class="button" href="{{ url_for('download', job_id=job_id, version='V3', extension='xlsx') }}">{{ icon("download")|safe }} Download V3</a>
              <form action="{{ url_for('run_import', job_id=job_id) }}" method="post">
                <button class="button" type="submit" name="mode" value="dry-run">{{ icon("play")|safe }} Test import</button>
              </form>
              <form action="{{ url_for('run_import', job_id=job_id) }}" method="post">
                <button class="button primary" type="submit" name="mode" value="upload">{{ icon("send")|safe }} Upload to Pipedrive</button>
              </form>
            </div>
          </section>
        </main>
        """,
        preview=preview_data,
        job_id=job_id,
    )
    return render_page(body, active_step="preview", current_job=job_id)


@app.get("/jobs/<job_id>/download/<version>.<extension>")
def download(job_id: str, version: str, extension: str):
    if version not in {"V2", "V3"} or extension not in {"xlsx", "csv"}:
        flash("Invalid download request.")
        return redirect(url_for("preview", job_id=job_id))
    path = find_job_file(job_id, f"{version}.{extension}")
    return send_file(path, as_attachment=True, download_name=path.name)


@app.post("/jobs/<job_id>/import")
def run_import(job_id: str) -> str:
    mode = request.form.get("mode")
    dry_run = mode != "upload"
    try:
        v3_xlsx = find_job_file(job_id, "V3.xlsx")
        result = import_v3(v3_xlsx, dry_run=dry_run)
        preview_data = build_preview(v3_xlsx)
    except Exception as exc:
        flash(f"Import failed: {exc}")
        return redirect(url_for("preview", job_id=job_id))

    body = render_template_string(
        """
        <main class="full-width">
          <section class="panel">
            {% if result.failed_rows or result.row_errors %}
              <div class="inline-error">
                Some rows could not be processed. {{ result.row_errors|join(" | ") }}
              </div>
            {% endif %}
            <div class="table-wrap">
              <table>
                <thead><tr>{% for column in preview.columns %}<th>{{ column }}</th>{% endfor %}</tr></thead>
                <tbody>
                  {% for row in preview.rows %}
                    <tr>{% for column in preview.columns %}<td>{{ row[column] }}</td>{% endfor %}</tr>
                  {% endfor %}
                </tbody>
              </table>
            </div>
            <div class="table-actions">
              <a class="button" href="{{ url_for('download', job_id=job_id, version='V2', extension='xlsx') }}">{{ icon("download")|safe }} Download V2</a>
              <a class="button" href="{{ url_for('download', job_id=job_id, version='V3', extension='xlsx') }}">{{ icon("download")|safe }} Download V3</a>
              <a class="button" href="{{ url_for('preview', job_id=job_id) }}">{{ icon("table")|safe }} Back to preview</a>
              {% if result.dry_run %}
                <form action="{{ url_for('run_import', job_id=job_id) }}" method="post">
                  <button class="button primary" type="submit" name="mode" value="upload">{{ icon("send")|safe }} Upload to Pipedrive</button>
                </form>
              {% endif %}
            </div>
          </section>
        </main>
        """,
        result=result,
        preview=preview_data,
        job_id=job_id,
    )
    return render_page(body, active_step="import", current_job=job_id)


if __name__ == "__main__":
    ensure_web_storage()
    port = int(os.getenv("PORT") or os.getenv("FLASK_RUN_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    app.run(host=os.getenv("FLASK_RUN_HOST", "127.0.0.1"), port=port, debug=debug)
