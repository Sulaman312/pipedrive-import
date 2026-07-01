"""Backward-compatible Flask entry point.

Koyeb and existing local commands continue importing ``src.web_app:app``.
New code should use the factory in :mod:`src.web.app`.
"""

import os

from flask import session

if __package__:
    from .web import create_app
else:
    from web import create_app


app = create_app()

# Compatibility exports for code that imported helpers or route callables from
# the former monolithic module. New code should import from ``src.web``.
if __package__:
    from .web.paths import IMPORTER_DIR, ROOT_DIR, WEB_STORAGE_DIR
    from .web.services.auth import credentials_match, is_configured as auth_configured
    from .web.services.imports import import_v3
    from .web.services.storage import (
        build_preview,
        ensure_web_storage,
        find_job_file,
        import_status_path,
        job_dir,
        read_import_status,
        write_import_status,
    )
else:
    from web.paths import IMPORTER_DIR, ROOT_DIR, WEB_STORAGE_DIR
    from web.services.auth import credentials_match, is_configured as auth_configured
    from web.services.imports import import_v3
    from web.services.storage import (
        build_preview,
        ensure_web_storage,
        find_job_file,
        import_status_path,
        job_dir,
        read_import_status,
        write_import_status,
    )

login = app.view_functions["login"]
logout = app.view_functions["logout"]
index = app.view_functions["index"]
upload = app.view_functions["upload"]
preview = app.view_functions["preview"]
download = app.view_functions["download"]
run_import = app.view_functions["run_import"]
import_status = app.view_functions["import_status"]
import_result = app.view_functions["import_result"]


def is_authenticated() -> bool:
    return bool(session.get("authenticated"))


if __name__ == "__main__":
    port = int(os.getenv("PORT") or os.getenv("FLASK_RUN_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    app.run(host=os.getenv("FLASK_RUN_HOST", "127.0.0.1"), port=port, debug=debug)
