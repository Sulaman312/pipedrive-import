"""Job storage and preview access."""

import json
from pathlib import Path
from typing import Any

import pandas as pd

from ..paths import WEB_STORAGE_DIR


def ensure_web_storage() -> None:
    WEB_STORAGE_DIR.mkdir(exist_ok=True)


def job_dir(job_id: str) -> Path:
    return WEB_STORAGE_DIR / job_id


def find_job_file(job_id: str, suffix: str) -> Path:
    matches = sorted(job_dir(job_id).glob(f"*_{suffix}"))
    if not matches:
        raise FileNotFoundError(f"No {suffix} file found for job {job_id}")
    return matches[0]


def import_status_path(job_id: str) -> Path:
    return job_dir(job_id) / "import_status.json"


def write_import_status(job_id: str, status: dict[str, Any]) -> None:
    path = import_status_path(job_id)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def read_import_status(job_id: str) -> dict[str, Any]:
    path = import_status_path(job_id)
    if not path.exists():
        raise FileNotFoundError("No import has been started for this job")
    return json.loads(path.read_text(encoding="utf-8"))


def build_preview(path: Path, limit: int | None = None) -> dict[str, Any]:
    dataframe = pd.read_excel(path, dtype=str).fillna("ND")
    visible = dataframe if limit is None else dataframe.head(limit)
    return {
        "rows": visible.to_dict(orient="records"),
        "columns": list(dataframe.columns),
        "row_count": len(dataframe),
        "column_count": len(dataframe.columns),
        "preview_count": len(visible),
    }
