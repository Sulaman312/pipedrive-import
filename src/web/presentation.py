"""HTML presentation helpers for the web application."""

from __future__ import annotations

from flask import render_template_string, session


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
    .loading-card.failed .loader-ring { animation: none; border-color: #f2c7c3; border-top-color: var(--danger); }
    .loading-card.failed .progress-fill { background: var(--danger); }
    .loading-card.failed [data-loading-title] { color: var(--danger); }
    .loading-card strong { display: block; font-size: 16px; }
    .loading-card span { display: block; margin-top: 6px; color: var(--muted); font-size: 13px; }
    .loading-progress { display: none; margin-top: 18px; text-align: left; }
    .loading-progress.visible { display: block; }
    .progress-track { height: 10px; overflow: hidden; border-radius: 999px; background: #e6ecef; }
    .progress-fill { width: 0; height: 100%; border-radius: inherit; background: var(--accent); transition: width .25s ease; }
    .progress-counts { display: flex; justify-content: space-between; gap: 12px; margin-top: 8px; color: var(--muted); font-size: 12px; }
    .loading-dismiss { display: none; margin: 18px auto 0; }
    .loading-card.failed .loading-dismiss { display: inline-flex; }
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
          <a class="button" href="{{ url_for('auth.logout') }}">{{ icon("lock")|safe }} Sign out</a>
        {% endif %}
      </div>
    </header>
    {% endif %}
    {% with messages = get_flashed_messages() %}
      {% for message in messages %}<div class="flash">{{ message }}</div>{% endfor %}
    {% endwith %}
    {% if active_step %}
      <nav class="flow-tabs" aria-label="Progress">
        <a class="flow-tab {{ 'active' if active_step == 'upload' else '' }}" href="{{ url_for('transformations.index') }}">{{ icon("upload")|safe }} Upload</a>
        <a class="flow-tab {{ 'active' if active_step == 'preview' else '' }} {{ 'disabled' if not current_job else '' }}" href="{{ url_for('transformations.preview', job_id=current_job) if current_job else '#' }}">{{ icon("table")|safe }} Preview V3</a>
        <a class="flow-tab {{ 'active' if active_step == 'import' else '' }} {{ 'disabled' if not current_job else '' }}" href="{{ url_for('transformations.preview', job_id=current_job) if current_job else '#' }}">{{ icon("send")|safe }} Import</a>
      </nav>
    {% endif %}
    {{ body|safe }}
  </div>
  <div class="loading-overlay" data-loading-overlay>
    <div class="loading-card">
      <div class="loader-ring"></div>
      <strong data-loading-title>Processing</strong>
      <span data-loading-detail>This can take a moment for large files.</span>
      <div class="loading-progress" data-loading-progress>
        <div class="progress-track"><div class="progress-fill" data-progress-fill></div></div>
        <div class="progress-counts"><span data-progress-imported>0 imported</span><span data-progress-left>Calculating…</span></div>
      </div>
      <button class="button loading-dismiss" type="button" data-loading-dismiss>Close</button>
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
    const pollImport = async (statusUrl, resultUrl) => {
      const progress = document.querySelector("[data-loading-progress]");
      const fill = document.querySelector("[data-progress-fill]");
      const imported = document.querySelector("[data-progress-imported]");
      const left = document.querySelector("[data-progress-left]");
      const detail = document.querySelector("[data-loading-detail]");
      progress && progress.classList.add("visible");
      while (true) {
        const response = await fetch(statusUrl, {headers: {"Accept": "application/json"}});
        const status = await response.json();
        if (!response.ok) throw new Error(status.error || "Could not read import progress");
        const percent = Number(status.percent || 0);
        if (fill) fill.style.width = `${percent}%`;
        if (imported) imported.textContent = `${status.processed || 0} imported`;
        if (left) left.textContent = `${status.remaining || 0} left`;
        if (detail) detail.textContent = `${percent}% complete`;
        if (status.state === "completed") {
          window.location.assign(resultUrl);
          return;
        }
        if (status.state === "failed") throw new Error(status.error || "Import failed");
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }
    };
    const showImportError = (message) => {
      const card = document.querySelector(".loading-card");
      const title = document.querySelector("[data-loading-title]");
      const detail = document.querySelector("[data-loading-detail]");
      card && card.classList.add("failed");
      if (title) title.textContent = "Import failed";
      if (detail) detail.textContent = message;
    };
    document.querySelector("[data-loading-dismiss]")?.addEventListener("click", () => {
      document.querySelector("[data-loading-overlay]")?.classList.remove("visible");
    });
    document.querySelectorAll("form[data-loading-message]").forEach((form) => {
      form.addEventListener("submit", async (event) => {
        const overlay = document.querySelector("[data-loading-overlay]");
        const card = document.querySelector(".loading-card");
        const title = document.querySelector("[data-loading-title]");
        card && card.classList.remove("failed");
        if (title) title.textContent = form.getAttribute("data-loading-message") || "Processing";
        if (overlay) overlay.classList.add("visible");
        if (!form.action.endsWith("/import")) return;
        event.preventDefault();
        try {
          const formData = new FormData(form);
          if (event.submitter && event.submitter.name) {
            formData.set(event.submitter.name, event.submitter.value);
          }
          const response = await fetch(form.action, {method: "POST", body: formData, headers: {"Accept": "application/json"}});
          const payload = await response.json();
          if (!response.ok) throw new Error(payload.error || "Could not start import");
          await pollImport(payload.status_url, payload.result_url);
        } catch (error) {
          showImportError(error.message);
        }
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
        authenticated=bool(session.get("authenticated")),
        active_step=active_step,
        current_job=current_job,
        show_header=show_header,
        completion_message=completion_message,
    )
