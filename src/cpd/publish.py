"""Publication gate: previous valid state stays until a new run passes; pointer swap is atomic."""
import json
import os
from pathlib import Path

import duckdb


def _atomic_write(path: Path, payload: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    os.replace(tmp, path)


def publish(runs: Path, build_db: Path, run_id: str, report: dict) -> Path:
    final = runs / f"{run_id}.duckdb"
    os.replace(build_db, final)
    _atomic_write(runs / "published.json", {"run_id": run_id, "db": final.name, "report": report})
    return final


def write_last_report(runs: Path, report: dict) -> None:
    _atomic_write(runs / "last_run.json", report)


def _read(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def read_pointer(runs: Path):
    ptr = _read(runs / "published.json")
    if ptr and (runs / ptr["db"]).exists():
        return ptr
    return None


def read_last_report(runs: Path):
    return _read(runs / "last_run.json")


def connect_published(runs: Path):
    ptr = read_pointer(runs)
    if not ptr:
        return None
    return duckdb.connect(str(runs / ptr["db"]), read_only=True)
