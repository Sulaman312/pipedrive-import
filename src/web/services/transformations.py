"""Orchestration for uploaded source-file transformations."""

import shutil
import sys
import uuid
from pathlib import Path

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from ..paths import SRC_DIR

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
from transform import transform  # noqa: E402

from .storage import ensure_web_storage, job_dir


ALLOWED_EXTENSIONS = {".xlsx", ".xls", ".csv"}


def validate_source_file(file: FileStorage | None) -> str | None:
    if not file or not file.filename:
        return "Choose a source XLSX, XLS, or CSV file."
    if Path(file.filename).suffix.lower() not in ALLOWED_EXTENSIONS:
        return "Unsupported file type. Upload XLSX, XLS, or CSV."
    return None


def transform_upload(file: FileStorage) -> str:
    ensure_web_storage()
    job_id = uuid.uuid4().hex
    directory = job_dir(job_id)
    directory.mkdir(parents=True, exist_ok=True)
    source_path = directory / secure_filename(file.filename or "upload")
    file.save(source_path)
    try:
        transform(source_path, directory)
    except Exception:
        shutil.rmtree(directory, ignore_errors=True)
        raise
    return job_id
