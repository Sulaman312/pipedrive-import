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
    success = stats.failed_rows == 0
    return {
        "success": success,
        "message": (
            "Test completed" if dry_run and success
            else "Test completed with issues" if dry_run
            else "Upload completed" if success
            else "Upload completed with issues"
        ),
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
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #f5f7f8;
      --panel: #ffffff;
      --ink: #1f2933;
      --muted: #667085;
      --line: #d9dee7;
      --accent: #0f766e;
      --accent-strong: #115e59;
      --accent-soft: #e6f4f2;
      --warn: #b45309;
      --danger: #b42318;
      --soft: #eef6f5;
      --shadow: 0 18px 44px rgba(31, 41, 51, .07);
      --radius: 18px;
      --radius-sm: 14px;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Poppins, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: var(--bg);
    }
    .shell { width: min(1560px, calc(100vw - 32px)); margin: 0 auto; padding: 24px 0 40px; }
    .topbar {
      display: flex; justify-content: space-between; align-items: center;
      gap: 18px; padding-bottom: 22px; border-bottom: 1px solid var(--line);
    }
    .brand { display: flex; gap: 12px; align-items: center; }
    .brand-mark {
      width: 38px; height: 38px; border-radius: 14px; background: #e8f3f1;
      color: var(--accent); display: grid; place-items: center; border: 1px solid #c8e3df;
    }
    h1 { font-size: 22px; line-height: 1.2; margin: 0; letter-spacing: 0; }
    .subtitle { color: var(--muted); margin: 4px 0 0; font-size: 14px; }
    .header-actions { display: flex; align-items: center; gap: 10px; }
    .flow-tabs {
      display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px;
      margin-top: 20px; padding: 6px; border: 1px solid var(--line); border-radius: var(--radius); background: #eef2f5;
    }
    .flow-tab {
      display: flex; align-items: center; justify-content: center; gap: 8px;
      min-height: 42px; border-radius: var(--radius-sm); color: #52606d; text-decoration: none; font-size: 14px; font-weight: 700;
      border: 1px solid transparent;
    }
    .flow-tab.active { background: #fff; color: var(--accent-strong); border-color: #c8e3df; box-shadow: 0 6px 18px rgba(31, 41, 51, .07); }
    .flow-tab.disabled { opacity: .48; pointer-events: none; }
    .grid { display: grid; grid-template-columns: 360px minmax(0, 1fr); gap: 20px; margin-top: 22px; align-items: start; }
    .full-width { margin-top: 22px; }
    .single { max-width: 760px; margin: 22px auto 0; }
    .panel {
      background: var(--panel); border: 1px solid var(--line); border-radius: var(--radius); box-shadow: var(--shadow);
    }
    .panel-header { padding: 18px 18px 0; }
    .panel-title { font-size: 15px; font-weight: 700; margin: 0; }
    .panel-body { padding: 18px; }
    .steps { display: grid; gap: 10px; }
    .step {
      display: grid; grid-template-columns: 30px 1fr; gap: 10px; padding: 10px;
      border: 1px solid var(--line); border-radius: var(--radius-sm); background: #fbfcfd;
    }
    .step-icon { width: 30px; height: 30px; display: grid; place-items: center; color: var(--accent); background: var(--soft); border-radius: 12px; }
    .step strong { display: block; font-size: 13px; }
    .step span { color: var(--muted); font-size: 12px; line-height: 1.35; }
    .upload-box { display: grid; gap: 16px; }
    .dropzone {
      border: 1.5px dashed #8da3b3; border-radius: var(--radius); padding: 34px 28px; background: linear-gradient(180deg, #ffffff, #f9fbfb);
      display: grid; gap: 16px; min-height: 258px; place-items: center; text-align: center; cursor: pointer;
      transition: border-color .16s ease, background .16s ease, box-shadow .16s ease, transform .16s ease;
    }
    .dropzone:hover, .dropzone.dragover { border-color: var(--accent); background: #f2fbf9; box-shadow: 0 18px 38px rgba(15, 118, 110, .11); transform: translateY(-1px); }
    .file-prompt { display: grid; gap: 12px; justify-items: center; }
    .file-prompt-icon { width: 54px; height: 54px; display: grid; place-items: center; color: var(--accent); background: var(--soft); border-radius: 16px; border: 1px solid #c8e3df; }
    .file-prompt-icon svg { width: 24px; height: 24px; }
    .file-prompt strong { display: block; font-size: 16px; }
    .file-prompt span { color: var(--muted); font-size: 13px; }
    .file-empty { display: grid; gap: 12px; justify-items: center; }
    .file-selected { display: none; gap: 12px; justify-items: center; }
    .dropzone.has-file .file-empty { display: none; }
    .dropzone.has-file .file-selected { display: grid; }
    .selected-file-icon { width: 88px; height: 88px; border-radius: 22px; display: grid; place-items: center; color: var(--accent); background: var(--accent-soft); border: 1px solid #c8e3df; }
    .selected-file-icon svg { width: 38px; height: 38px; }
    .file-input { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
    .file-name {
      display: block; max-width: min(420px, 100%); color: var(--accent-strong); font-size: 14px; font-weight: 700; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    }
    input[type=text], input[type=password] {
      width: 100%; border: 1px solid var(--line); border-radius: var(--radius-sm); background: #fff;
      padding: 11px 12px; font-size: 14px; color: var(--ink); outline: none;
    }
    input[type=text]:focus, input[type=password]:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(15, 118, 110, .12); }
    label { display: grid; gap: 7px; color: #344054; font-size: 13px; font-weight: 650; }
    .form-stack { display: grid; gap: 14px; }
    .login-shell { min-height: calc(100vh - 56px); display: grid; place-items: center; }
    .login-panel { width: min(420px, 100%); }
    .actions { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; }
    .button {
      appearance: none; border: 1px solid var(--line); border-radius: 999px; padding: 10px 15px;
      background: var(--panel); color: var(--ink); font-weight: 650; font-size: 14px;
      display: inline-flex; align-items: center; gap: 8px; text-decoration: none; cursor: pointer;
      min-height: 40px;
    }
    .button.primary { background: var(--accent); border-color: var(--accent); color: #fff; }
    .button.primary:hover { background: var(--accent-strong); }
    .button.danger { color: var(--danger); border-color: #f0b9b5; }
    .button:disabled { opacity: .55; cursor: not-allowed; }
    .flash { margin-top: 14px; padding: 11px 12px; border-radius: var(--radius-sm); border: 1px solid #f1d7a8; color: #7c4a03; background: #fff8eb; font-size: 13px; }
    .metrics { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; margin-bottom: 16px; }
    .metric { border: 1px solid var(--line); border-radius: var(--radius-sm); padding: 12px; background: #fbfcfd; }
    .metric span { color: var(--muted); font-size: 12px; }
    .metric strong { display: block; margin-top: 4px; font-size: 20px; }
    .table-wrap { overflow: auto; max-height: calc(100vh - 292px); min-height: 380px; scroll-behavior: smooth; }
    .table-panel { transition: border-radius .22s ease, box-shadow .22s ease, transform .22s ease, opacity .18s ease; }
    .table-panel.entering-fullscreen { opacity: .92; transform: scale(.992); }
    .table-panel:fullscreen { border-radius: 0; border: 0; box-shadow: none; height: 100vh; display: flex; flex-direction: column; animation: fullscreenIn .18s ease-out; }
    .table-panel:fullscreen .table-wrap { flex: 1; max-height: none; min-height: 0; }
    .table-panel:fullscreen .table-actions,
    .table-panel:fullscreen .result-summary,
    .table-panel:fullscreen .mini-stats { flex: 0 0 auto; }
    .table-panel.fullscreen-fallback {
      position: fixed; inset: 0; z-index: 80; border-radius: 0; border: 0; box-shadow: none;
      height: 100vh; display: flex; flex-direction: column; animation: fullscreenIn .18s ease-out;
    }
    .table-panel.fullscreen-fallback .table-wrap { flex: 1; max-height: none; min-height: 0; }
    table { border-collapse: separate; border-spacing: 0; width: max-content; min-width: 100%; font-size: 12px; }
    th, td { border-bottom: 1px solid var(--line); padding: 10px 12px; text-align: left; vertical-align: top; white-space: nowrap; }
    th { position: sticky; top: 0; background: #eef3f6; z-index: 2; color: #344054; font-weight: 700; }
    td { color: #384250; background: #fff; }
    tbody tr:nth-child(even) td { background: #fbfcfd; }
    .empty { padding: 52px 18px; text-align: center; color: var(--muted); }
    .result-list { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }
    .result-list .metric strong { font-size: 18px; }
    .result-hero { display: flex; justify-content: space-between; gap: 18px; align-items: center; margin-bottom: 16px; padding: 16px; border: 1px solid #c8e3df; border-radius: var(--radius-sm); background: var(--soft); }
    .result-hero strong { display: block; font-size: 18px; }
    .result-hero span { color: var(--muted); font-size: 13px; }
    .table-actions { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 10px; padding: 14px; border-top: 1px solid var(--line); background: #fbfcfd; }
    .table-actions form { margin: 0; display: inline-flex; }
    .inline-error { margin: 14px; padding: 11px 12px; border-radius: var(--radius-sm); border: 1px solid #f0b9b5; color: var(--danger); background: #fff4f2; font-size: 13px; }
    .result-summary {
      display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px;
      padding: 14px; border-top: 1px solid var(--line); background: #fbfcfd;
    }
    .result-status { display: flex; align-items: center; gap: 10px; }
    .result-dot { width: 10px; height: 10px; border-radius: 99px; background: var(--accent); }
    .result-dot.failed { background: var(--danger); }
    .result-status strong { display: block; font-size: 14px; }
    .result-status span, .result-detail { color: var(--muted); font-size: 13px; }
    .mini-stats {
      display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px;
      padding: 14px; border-top: 1px solid var(--line); background: #fff;
    }
    .mini-stat { border: 1px solid var(--line); border-radius: var(--radius-sm); padding: 12px; background: #fbfcfd; }
    .mini-stat span { color: var(--muted); font-size: 12px; }
    .mini-stat strong { display: block; margin-top: 4px; font-size: 20px; }
    .mini-stat small { display: block; margin-top: 4px; color: var(--muted); font-size: 12px; }
    .notice { color: var(--muted); font-size: 13px; line-height: 1.5; margin-top: 12px; }
    .loading-overlay {
      position: fixed; inset: 0; display: none; place-items: center; background: rgba(245, 247, 248, .78);
      backdrop-filter: blur(5px); z-index: 50;
    }
    .loading-overlay.visible { display: grid; }
    .loading-card {
      width: min(360px, calc(100vw - 32px)); border: 1px solid var(--line); border-radius: 16px; background: #fff;
      box-shadow: 0 24px 70px rgba(31, 41, 51, .16); padding: 24px; text-align: center;
    }
    .loader-ring {
      width: 42px; height: 42px; margin: 0 auto 14px; border-radius: 999px; border: 4px solid #dbe7e5;
      border-top-color: var(--accent); animation: spin .8s linear infinite;
    }
    .loading-card strong { display: block; font-size: 16px; }
    .loading-card span { display: block; margin-top: 6px; color: var(--muted); font-size: 13px; }
    .completion-toast {
      position: fixed; right: 20px; bottom: 20px; display: flex; align-items: center; gap: 10px; padding: 12px 14px;
      border: 1px solid #c8e3df; border-radius: 14px; color: var(--accent-strong); background: #fff; box-shadow: var(--shadow);
      animation: fadeAway 3.8s ease forwards; z-index: 60; font-size: 13px; font-weight: 700;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    @keyframes fullscreenIn {
      from { opacity: .88; transform: scale(.985); }
      to { opacity: 1; transform: scale(1); }
    }
    @keyframes fadeAway {
      0%, 72% { opacity: 1; transform: translateY(0); }
      100% { opacity: 0; transform: translateY(8px); pointer-events: none; }
    }
    svg { width: 18px; height: 18px; stroke-width: 2; }
    svg * { stroke-linecap: round; stroke-linejoin: round; }
    @media (max-width: 900px) {
      .grid { grid-template-columns: 1fr; }
      .topbar { align-items: flex-start; flex-direction: column; }
      .metrics, .result-list, .flow-tabs, .mini-stats { grid-template-columns: 1fr; }
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
  <div class="loading-overlay" data-loading-overlay>
    <div class="loading-card">
      <div class="loader-ring"></div>
      <strong data-loading-title>Processing</strong>
      <span>This can take a moment for large files.</span>
    </div>
  </div>
  {% if completion_message %}
    <div class="completion-toast">{{ icon("workflow")|safe }} {{ completion_message }}</div>
  {% endif %}
  <script>
    document.querySelectorAll("[data-dropzone]").forEach((dropzone) => {
      const input = dropzone.querySelector("input[type='file']");
      const nameTarget = dropzone.querySelector("[data-file-name]");
      const setFileName = () => {
        if (!input || !nameTarget) return;
        const file = input.files && input.files[0];
        nameTarget.textContent = file ? file.name : "";
        dropzone.classList.toggle("has-file", Boolean(file));
      };
      dropzone.addEventListener("click", (event) => {
        if (event.target === input) return;
        input && input.click();
      });
      dropzone.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          input && input.click();
        }
      });
      ["dragenter", "dragover"].forEach((eventName) => {
        dropzone.addEventListener(eventName, (event) => {
          event.preventDefault();
          dropzone.classList.add("dragover");
        });
      });
      ["dragleave", "drop"].forEach((eventName) => {
        dropzone.addEventListener(eventName, (event) => {
          event.preventDefault();
          dropzone.classList.remove("dragover");
        });
      });
      dropzone.addEventListener("drop", (event) => {
        if (!input || !event.dataTransfer || !event.dataTransfer.files.length) return;
        input.files = event.dataTransfer.files;
        setFileName();
      });
      input && input.addEventListener("change", setFileName);
    });
    document.querySelectorAll("form[data-loading-message]").forEach((form) => {
      form.addEventListener("submit", () => {
        const overlay = document.querySelector("[data-loading-overlay]");
        const title = document.querySelector("[data-loading-title]");
        if (title) title.textContent = form.getAttribute("data-loading-message") || "Processing";
        if (overlay) overlay.classList.add("visible");
      });
    });
    document.querySelectorAll("[data-fullscreen-toggle]").forEach((button) => {
      const panel = button.closest("[data-table-panel]");
      if (!panel) return;
      const setLabel = () => {
        const isFull = document.fullscreenElement === panel || panel.classList.contains("fullscreen-fallback");
        button.innerHTML = isFull
          ? '{{ icon("expand")|safe }} Exit full screen'
          : '{{ icon("expand")|safe }} Full screen';
      };
      button.addEventListener("click", async () => {
        if (document.fullscreenElement === panel) {
          await document.exitFullscreen();
        } else if (panel.classList.contains("fullscreen-fallback")) {
          panel.classList.remove("fullscreen-fallback");
        } else if (panel.requestFullscreen) {
          panel.classList.add("entering-fullscreen");
          await new Promise((resolve) => setTimeout(resolve, 90));
          await panel.requestFullscreen();
          panel.classList.remove("entering-fullscreen");
        } else {
          panel.classList.add("entering-fullscreen");
          await new Promise((resolve) => setTimeout(resolve, 90));
          panel.classList.remove("entering-fullscreen");
          panel.classList.add("fullscreen-fallback");
        }
        setLabel();
      });
      document.addEventListener("fullscreenchange", () => {
        panel.classList.remove("entering-fullscreen");
        setLabel();
      });
      document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && panel.classList.contains("fullscreen-fallback")) {
          panel.classList.remove("fullscreen-fallback");
          setLabel();
        }
      });
      setLabel();
    });
  </script>
</body>
</html>
"""


def icon(name: str) -> str:
    icons = {
        "workflow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M6 3v6"/><path d="M18 15v6"/><rect x="3" y="9" width="6" height="6" rx="1"/><rect x="15" y="3" width="6" height="6" rx="1"/><rect x="15" y="9" width="6" height="6" rx="1"/><path d="M9 12h6"/><path d="M18 15v0"/></svg>',
        "upload": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M12 16V4"/><path d="m7 9 5-5 5 5"/><path d="M20 16v4H4v-4"/></svg>',
        "table": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><rect x="3.5" y="5" width="17" height="14" rx="3"/><path d="M3.5 10h17"/><path d="M8.5 5v14"/></svg>',
        "send": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M20.2 4.4 14.4 19c-.4 1.1-1.9 1.2-2.5.2l-2.7-4.5-4.5-2.7c-1-.6-.9-2.1.2-2.5l14.6-5.8c.5-.2 1 .2.7.7Z"/><path d="m9.3 14.6 4.2-4.2"/></svg>',
        "download": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M12 3v12"/><path d="m7 10 5 5 5-5"/><path d="M5 21h14"/></svg>',
        "play": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M9 7.8c0-1.3 1.4-2.1 2.5-1.4l5.8 3.8c1 .7 1 2.1 0 2.8l-5.8 3.8C10.4 17.5 9 16.7 9 15.4Z"/></svg>',
        "key": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="7.5" cy="15.5" r="3.5"/><path d="m10 13 9-9"/><path d="m15 4 2 2"/><path d="m13 6 2 2"/></svg>',
        "file": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M14 2H6v20h12V8z"/><path d="M14 2v6h6"/></svg>',
        "lock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>',
        "expand": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><rect x="4" y="4" width="16" height="16" rx="4"/><path d="M9 9h-1a1 1 0 0 0-1 1v1"/><path d="M15 9h1a1 1 0 0 1 1 1v1"/><path d="M9 15h-1a1 1 0 0 1-1-1v-1"/><path d="M15 15h1a1 1 0 0 0 1-1v-1"/></svg>',
    }
    return icons[name]


app.jinja_env.globals["icon"] = icon


def render_page(
    body: str,
    *,
    active_step: str | None = None,
    current_job: str | None = None,
    show_header: bool = True,
    completion_message: str | None = None,
) -> str:
    return render_template_string(
        BASE_TEMPLATE,
        body=body,
        authenticated=is_authenticated(),
        active_step=active_step,
        current_job=current_job,
        show_header=show_header,
        completion_message=completion_message,
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
              <form class="upload-box" action="{{ url_for('upload') }}" method="post" enctype="multipart/form-data" data-loading-message="Preparing your file">
                <div class="dropzone" data-dropzone role="button" tabindex="0">
                  <input class="file-input" type="file" name="source_file" accept=".xlsx,.xls,.csv" required>
                  <div class="file-prompt">
                    <div class="file-empty">
                      <div class="file-prompt-icon">{{ icon("file")|safe }}</div>
                      <div>
                        <strong>Drag and drop your file here</strong>
                        <span>or click to choose an Excel or CSV file</span>
                      </div>
                    </div>
                    <div class="file-selected">
                      <div class="selected-file-icon">{{ icon("file")|safe }}</div>
                      <span class="file-name" data-file-name></span>
                    </div>
                  </div>
                </div>
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

    return redirect(url_for("preview", job_id=current_job, completed="upload"))


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
          <section class="panel table-panel" data-table-panel>
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
              <button class="button" type="button" data-fullscreen-toggle>{{ icon("expand")|safe }} Full screen</button>
              <a class="button" href="{{ url_for('download', job_id=job_id, version='V2', extension='xlsx') }}">{{ icon("download")|safe }} Download V2</a>
              <a class="button" href="{{ url_for('download', job_id=job_id, version='V3', extension='xlsx') }}">{{ icon("download")|safe }} Download V3</a>
              <form action="{{ url_for('run_import', job_id=job_id) }}" method="post" data-loading-message="Testing the import">
                <button class="button" type="submit" name="mode" value="dry-run">{{ icon("play")|safe }} Test import</button>
              </form>
              <form action="{{ url_for('run_import', job_id=job_id) }}" method="post" data-loading-message="Uploading to Pipedrive">
                <button class="button primary" type="submit" name="mode" value="upload">{{ icon("send")|safe }} Upload to Pipedrive</button>
              </form>
            </div>
          </section>
        </main>
        """,
        preview=preview_data,
        job_id=job_id,
    )
    completion_message = "File ready" if request.args.get("completed") == "upload" else None
    return render_page(body, active_step="preview", current_job=job_id, completion_message=completion_message)


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
        preview_data = build_preview(v3_xlsx)
        result = import_v3(v3_xlsx, dry_run=dry_run)
    except Exception as exc:
        try:
            v3_xlsx = find_job_file(job_id, "V3.xlsx")
            preview_data = build_preview(v3_xlsx)
        except Exception:
            flash(f"Import failed: {exc}")
            return redirect(url_for("preview", job_id=job_id))
        result = {
            "success": False,
            "message": "Test failed" if dry_run else "Upload failed",
            "dry_run": dry_run,
            "rows": preview_data["row_count"],
            "organizations_created": 0,
            "organizations_updated": 0,
            "persons_created": 0,
            "persons_updated": 0,
            "deals_created": 0,
            "failed_rows": preview_data["row_count"],
            "row_errors": [str(exc)],
            "skipped_fields": [],
            "unmapped_columns": [],
        }

    body = render_template_string(
        """
        <main class="full-width">
          <section class="panel table-panel" data-table-panel>
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
            <div class="result-summary">
              <div class="result-status">
                <span class="result-dot {{ '' if result.success else 'failed' }}"></span>
                <div>
                  <strong>{{ result.message }}</strong>
                  <span>{{ "No data was sent to Pipedrive." if result.dry_run else "Pipedrive upload was attempted." }}</span>
                </div>
              </div>
              <div class="result-detail">
                {{ result.rows }} rows checked · {{ result.failed_rows }} rows with issues
              </div>
            </div>
            <div class="mini-stats">
              <div class="mini-stat"><span>Organizations</span><strong>{{ result.organizations_created }}</strong><small>{{ result.organizations_updated }} updated</small></div>
              <div class="mini-stat"><span>Persons</span><strong>{{ result.persons_created }}</strong><small>{{ result.persons_updated }} updated</small></div>
              <div class="mini-stat"><span>Deals</span><strong>{{ result.deals_created }}</strong><small>created</small></div>
            </div>
            <div class="table-actions">
              <button class="button" type="button" data-fullscreen-toggle>{{ icon("expand")|safe }} Full screen</button>
              <a class="button" href="{{ url_for('download', job_id=job_id, version='V2', extension='xlsx') }}">{{ icon("download")|safe }} Download V2</a>
              <a class="button" href="{{ url_for('download', job_id=job_id, version='V3', extension='xlsx') }}">{{ icon("download")|safe }} Download V3</a>
              <a class="button" href="{{ url_for('preview', job_id=job_id) }}">{{ icon("table")|safe }} Back to preview</a>
              {% if result.dry_run %}
                <form action="{{ url_for('run_import', job_id=job_id) }}" method="post" data-loading-message="Uploading to Pipedrive">
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
    completion_message = result["message"]
    return render_page(body, active_step="import", current_job=job_id, completion_message=completion_message)


if __name__ == "__main__":
    ensure_web_storage()
    port = int(os.getenv("PORT") or os.getenv("FLASK_RUN_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    app.run(host=os.getenv("FLASK_RUN_HOST", "127.0.0.1"), port=port, debug=debug)
