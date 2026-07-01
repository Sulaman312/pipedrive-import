"""Page-specific renderers kept separate from HTTP and service logic."""

from typing import Any

from flask import render_template_string

from .presentation import render_page


def login_page() -> str:
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


def upload_page() -> str:
    body = render_template_string(
        """
        <main class="single">
          <section class="panel">
            <div class="panel-header"><h2 class="panel-title">Upload source file</h2></div>
            <div class="panel-body">
              <form class="upload-box" action="{{ url_for('transformations.upload') }}" method="post" enctype="multipart/form-data" data-loading-message="Preparing your file">
                <div class="dropzone" data-dropzone role="button" tabindex="0">
                  <input class="file-input" type="file" name="source_file" accept=".xlsx,.xls,.csv" required>
                  <div class="file-prompt">
                    <div class="file-empty">
                      <div class="file-prompt-icon">{{ icon("file")|safe }}</div>
                      <div><strong>Drag and drop your file here</strong><span>or click to choose an Excel or CSV file</span></div>
                    </div>
                    <div class="file-selected">
                      <div class="selected-file-icon">{{ icon("file")|safe }}</div>
                      <span class="file-name" data-file-name></span>
                    </div>
                  </div>
                </div>
                <div class="actions"><button class="button primary" type="submit">{{ icon("play")|safe }} Continue to preview</button></div>
              </form>
            </div>
          </section>
        </main>
        """
    )
    return render_page(body, active_step="upload")


def preview_page(preview: dict[str, Any], job_id: str, completed: bool) -> str:
    body = render_template_string(
        """
        <main class="full-width">
          <section class="panel table-panel" data-table-panel>
            <div class="table-wrap">
              <table>
                <thead><tr>{% for column in preview.columns %}<th>{{ column }}</th>{% endfor %}</tr></thead>
                <tbody>{% for row in preview.rows %}<tr>{% for column in preview.columns %}<td>{{ row[column] }}</td>{% endfor %}</tr>{% endfor %}</tbody>
              </table>
            </div>
            <div class="table-actions">
              <button class="button" type="button" data-fullscreen-toggle>{{ icon("expand")|safe }} Full screen</button>
              <a class="button" href="{{ url_for('transformations.download', job_id=job_id, version='V2', extension='xlsx') }}">{{ icon("download")|safe }} Download V2</a>
              <a class="button" href="{{ url_for('transformations.download', job_id=job_id, version='V3', extension='xlsx') }}">{{ icon("download")|safe }} Download V3</a>
              <form action="{{ url_for('imports.run_import', job_id=job_id) }}" method="post" data-loading-message="Testing the import">
                <button class="button" type="submit" name="mode" value="dry-run">{{ icon("play")|safe }} Test import</button>
              </form>
              <form action="{{ url_for('imports.run_import', job_id=job_id) }}" method="post" data-loading-message="Uploading to Pipedrive">
                <button class="button primary" type="submit" name="mode" value="upload">{{ icon("send")|safe }} Upload to Pipedrive</button>
              </form>
            </div>
          </section>
        </main>
        """,
        preview=preview,
        job_id=job_id,
    )
    return render_page(
        body,
        active_step="preview",
        current_job=job_id,
        completion_message="File ready" if completed else None,
    )


def import_result_page(preview: dict[str, Any], result: dict[str, Any], job_id: str) -> str:
    body = render_template_string(
        """
        <main class="full-width">
          <section class="panel table-panel" data-table-panel>
            {% if result.failed_rows or result.row_errors %}
              <div class="inline-error">Some rows could not be processed. {{ result.row_errors|join(" | ") }}</div>
            {% endif %}
            <div class="table-wrap">
              <table>
                <thead><tr>{% for column in preview.columns %}<th>{{ column }}</th>{% endfor %}</tr></thead>
                <tbody>{% for row in preview.rows %}<tr>{% for column in preview.columns %}<td>{{ row[column] }}</td>{% endfor %}</tr>{% endfor %}</tbody>
              </table>
            </div>
            <div class="result-summary">
              <div class="result-status">
                <span class="result-dot {{ '' if result.success else 'failed' }}"></span>
                <div><strong>{{ result.message }}</strong><span>{{ "No data was sent to Pipedrive." if result.dry_run else "Pipedrive upload was attempted." }}</span></div>
              </div>
              <div class="result-detail">{{ result.rows }} rows checked · {{ result.failed_rows }} rows with issues</div>
            </div>
            <div class="mini-stats">
              <div class="mini-stat"><span>Organizations</span><strong>{{ result.organizations_created }}</strong><small>{{ result.organizations_updated }} updated</small></div>
              <div class="mini-stat"><span>Persons</span><strong>{{ result.persons_created }}</strong><small>{{ result.persons_updated }} updated</small></div>
              <div class="mini-stat"><span>Deals</span><strong>{{ result.deals_created }}</strong><small>{{ result.deals_skipped }} existing/skipped</small></div>
            </div>
            <div class="table-actions">
              <button class="button" type="button" data-fullscreen-toggle>{{ icon("expand")|safe }} Full screen</button>
              <a class="button" href="{{ url_for('transformations.download', job_id=job_id, version='V2', extension='xlsx') }}">{{ icon("download")|safe }} Download V2</a>
              <a class="button" href="{{ url_for('transformations.download', job_id=job_id, version='V3', extension='xlsx') }}">{{ icon("download")|safe }} Download V3</a>
              <a class="button" href="{{ url_for('transformations.preview', job_id=job_id) }}">{{ icon("table")|safe }} Back to preview</a>
              {% if result.dry_run %}
                <form action="{{ url_for('imports.run_import', job_id=job_id) }}" method="post" data-loading-message="Uploading to Pipedrive">
                  <button class="button primary" type="submit" name="mode" value="upload">{{ icon("send")|safe }} Upload to Pipedrive</button>
                </form>
              {% endif %}
            </div>
          </section>
        </main>
        """,
        result=result,
        preview=preview,
        job_id=job_id,
    )
    return render_page(
        body, active_step="import", current_job=job_id, completion_message=result["message"]
    )
