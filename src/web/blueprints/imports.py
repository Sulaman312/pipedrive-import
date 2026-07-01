"""Pipedrive import lifecycle routes."""

import json

from flask import Blueprint, flash, jsonify, redirect, request, url_for

from ..services.imports import ImportAlreadyRunningError, start_import
from ..services.storage import build_preview, find_job_file, read_import_status
from ..views import import_result_page


blueprint = Blueprint("imports", __name__)


@blueprint.post("/jobs/<job_id>/import")
def run_import(job_id: str):
    mode = request.form.get("mode")
    if mode not in {"dry-run", "upload"}:
        return jsonify({"error": "Import mode is missing or invalid"}), 400
    try:
        start_import(job_id, dry_run=mode == "dry-run")
    except ImportAlreadyRunningError as exc:
        return jsonify({"error": str(exc)}), 409
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({
        "status_url": url_for("imports.import_status", job_id=job_id),
        "result_url": url_for("imports.import_result", job_id=job_id),
    }), 202


@blueprint.get("/jobs/<job_id>/import/status")
def import_status(job_id: str):
    try:
        return jsonify(read_import_status(job_id))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        return jsonify({"error": str(exc)}), 404


@blueprint.get("/jobs/<job_id>/import/result")
def import_result(job_id: str) -> str:
    try:
        preview = build_preview(find_job_file(job_id, "V3.xlsx"))
        status = read_import_status(job_id)
    except Exception as exc:
        flash(f"Could not load import result: {exc}")
        return redirect(url_for("transformations.preview", job_id=job_id))
    if status.get("state") in {"queued", "running"}:
        flash("The import is still running.")
        return redirect(url_for("transformations.preview", job_id=job_id))
    result = status["result"] if status.get("state") == "completed" else _failed_result(status, preview)
    return import_result_page(preview, result, job_id)


def _failed_result(status: dict, preview: dict) -> dict:
    return {
        "success": False,
        "message": "Test failed" if status.get("dry_run") else "Upload failed",
        "dry_run": status.get("dry_run", False),
        "rows": preview["row_count"],
        "organizations_created": 0,
        "organizations_updated": 0,
        "persons_created": 0,
        "persons_updated": 0,
        "deals_created": 0,
        "deals_skipped": 0,
        "failed_rows": preview["row_count"],
        "row_errors": [status.get("error", "Import failed")],
        "skipped_fields": [],
        "unmapped_columns": [],
    }
