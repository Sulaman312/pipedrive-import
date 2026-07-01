"""Background Pipedrive import orchestration for the web application."""

import logging
import os
import sys
import threading
from pathlib import Path
from typing import Any, Callable

from ..paths import IMPORTER_DIR
from .storage import find_job_file, read_import_status, write_import_status


if str(IMPORTER_DIR) not in sys.path:
    sys.path.insert(0, str(IMPORTER_DIR))
import importer as pipedrive_importer  # noqa: E402


ProgressCallback = Callable[[int, int, Any], None]
_threads: dict[str, threading.Thread] = {}
_threads_lock = threading.Lock()


def import_v3(path: Path, dry_run: bool, progress_callback: ProgressCallback | None = None) -> dict[str, Any]:
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
                row_number, row, client, field_lookup, metadata, stats, dry_run, logger
            )
        except Exception as exc:
            stats.failed_rows += 1
            message = f"Row {row_number} failed in {path.name}: {exc}"
            stats.row_errors.append(message)
            logger.exception(message)
            if isinstance(exc, pipedrive_importer.ImporterError):
                raise
        finally:
            if progress_callback:
                progress_callback(int(index) + 1, len(dataframe), stats)

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
        "deals_skipped": stats.deals_skipped,
        "created_organization_ids": stats.created_organization_ids,
        "created_person_ids": stats.created_person_ids,
        "created_deal_ids": stats.created_deal_ids,
        "failed_rows": stats.failed_rows,
        "unmapped_columns": stats.unmapped_columns,
        "skipped_fields": sorted(stats.skipped_fields),
        "row_errors": stats.row_errors[:20],
    }


def _run_import_background(job_id: str, dry_run: bool) -> None:
    try:
        v3_xlsx = find_job_file(job_id, "V3.xlsx")

        def update_progress(processed: int, total: int, stats: Any) -> None:
            write_import_status(job_id, {
                "state": "running", "dry_run": dry_run, "processed": processed,
                "total": total, "remaining": max(total - processed, 0),
                "percent": round((processed / total) * 100) if total else 100,
                "organizations_created": stats.organizations_created,
                "organizations_updated": stats.organizations_updated,
                "persons_created": stats.persons_created,
                "persons_updated": stats.persons_updated,
                "deals_created": stats.deals_created,
                "deals_skipped": stats.deals_skipped,
                "failed_rows": stats.failed_rows,
            })

        result = import_v3(v3_xlsx, dry_run=dry_run, progress_callback=update_progress)
        write_import_status(job_id, {
            "state": "completed", "processed": result["rows"], "total": result["rows"],
            "remaining": 0, "percent": 100, "result": result,
        })
    except Exception as exc:
        try:
            current = read_import_status(job_id)
        except Exception:
            current = {}
        write_import_status(job_id, {
            "state": "failed", "dry_run": dry_run,
            "processed": current.get("processed", 0), "total": current.get("total", 0),
            "remaining": current.get("remaining", 0), "percent": current.get("percent", 0),
            "error": str(exc),
        })
    finally:
        with _threads_lock:
            _threads.pop(job_id, None)


def start_import(job_id: str, dry_run: bool) -> int:
    v3_xlsx = find_job_file(job_id, "V3.xlsx")
    total = len(pipedrive_importer.load_xlsx_file(v3_xlsx))
    with _threads_lock:
        active = _threads.get(job_id)
        if active and active.is_alive():
            raise ImportAlreadyRunningError("An import is already running for this job")
        write_import_status(job_id, {
            "state": "queued", "dry_run": dry_run, "processed": 0,
            "total": total, "remaining": total, "percent": 0,
        })
        thread = threading.Thread(
            target=_run_import_background, args=(job_id, dry_run),
            name=f"pipedrive-import-{job_id[:8]}", daemon=True,
        )
        _threads[job_id] = thread
        thread.start()
    return total


class ImportAlreadyRunningError(RuntimeError):
    """Raised when the same job already has a live import thread."""
