"""Shared filesystem locations used by the web layer."""

from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
IMPORTER_DIR = ROOT_DIR / "importer"
WEB_STORAGE_DIR = ROOT_DIR / "web_storage"
