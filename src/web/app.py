"""Flask application factory and cross-cutting web configuration."""

import os

from dotenv import load_dotenv
from flask import Flask, flash, redirect, request, session, url_for

from .blueprints.auth import blueprint as auth_blueprint
from .blueprints.imports import blueprint as imports_blueprint
from .blueprints.transformations import blueprint as transformations_blueprint
from .blueprints.webhooks import webhooks_blueprint
from .paths import IMPORTER_DIR, ROOT_DIR
from .presentation import icon
from .services import auth as auth_service
from .services.storage import ensure_web_storage


def create_app() -> Flask:
    load_dotenv(ROOT_DIR / ".env")
    load_dotenv(IMPORTER_DIR / ".env")

    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "local-dev-secret-change-me")
    app.jinja_env.globals["icon"] = icon
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(transformations_blueprint)
    app.register_blueprint(imports_blueprint)
    app.register_blueprint(webhooks_blueprint)
    _register_legacy_endpoint_names(app)
    app.before_request(_require_login)
    ensure_web_storage()
    return app


def _require_login():
    if request.endpoint in {"auth.login", "login"}:
        return None
    if not auth_service.is_configured():
        if request.endpoint not in {"transformations.index", "index"}:
            flash("Sign-in is not set up yet.")
            return redirect(url_for("transformations.index"))
        return None
    if not session.get("authenticated"):
        return redirect(
            url_for("auth.login", next=request.full_path if request.query_string else request.path)
        )
    return None


def _register_legacy_endpoint_names(app: Flask) -> None:
    """Keep historical `url_for()` endpoint names available during migration."""
    aliases = {
        "login": ("/login", ["GET", "POST"], "auth.login"),
        "logout": ("/logout", ["GET"], "auth.logout"),
        "index": ("/", ["GET"], "transformations.index"),
        "upload": ("/upload", ["POST"], "transformations.upload"),
        "preview": ("/jobs/<job_id>", ["GET"], "transformations.preview"),
        "download": (
            "/jobs/<job_id>/download/<version>.<extension>", ["GET"], "transformations.download"
        ),
        "run_import": ("/jobs/<job_id>/import", ["POST"], "imports.run_import"),
        "import_status": ("/jobs/<job_id>/import/status", ["GET"], "imports.import_status"),
        "import_result": ("/jobs/<job_id>/import/result", ["GET"], "imports.import_result"),
    }
    for endpoint, (rule, methods, target) in aliases.items():
        app.add_url_rule(rule, endpoint, app.view_functions[target], methods=methods)
