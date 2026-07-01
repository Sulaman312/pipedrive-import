"""Upload, transformation, preview, and download routes."""

from flask import Blueprint, flash, redirect, request, send_file, url_for

from ..services.storage import build_preview, find_job_file
from ..services.transformations import transform_upload, validate_source_file
from ..views import preview_page, upload_page


blueprint = Blueprint("transformations", __name__)


@blueprint.get("/")
def index() -> str:
    return upload_page()


@blueprint.post("/upload")
def upload():
    file = request.files.get("source_file")
    validation_error = validate_source_file(file)
    if validation_error:
        flash(validation_error)
        return redirect(url_for("transformations.index"))
    assert file is not None
    try:
        job_id = transform_upload(file)
    except Exception as exc:
        flash(f"Transformation failed: {exc}")
        return redirect(url_for("transformations.index"))
    return redirect(url_for("transformations.preview", job_id=job_id, completed="upload"))


@blueprint.get("/jobs/<job_id>")
def preview(job_id: str) -> str:
    try:
        preview_data = build_preview(find_job_file(job_id, "V3.xlsx"))
    except Exception as exc:
        flash(f"Could not load job preview: {exc}")
        return redirect(url_for("transformations.index"))
    return preview_page(preview_data, job_id, request.args.get("completed") == "upload")


@blueprint.get("/jobs/<job_id>/download/<version>.<extension>")
def download(job_id: str, version: str, extension: str):
    if version not in {"V2", "V3"} or extension not in {"xlsx", "csv"}:
        flash("Invalid download request.")
        return redirect(url_for("transformations.preview", job_id=job_id))
    path = find_job_file(job_id, f"{version}.{extension}")
    return send_file(path, as_attachment=True, download_name=path.name)
