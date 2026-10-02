"""Orchestrates ingest -> model -> metrics -> quality -> publish. Failure never touches published state."""
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import duckdb

from . import ingest, metrics, model, publish, quality
from .config import RuntimeInputs


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run_pipeline(csv_path, inputs: RuntimeInputs, runs: Path) -> dict:
    runs = Path(runs)
    runs.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    report = {"status": "failed", "started_at": started, "csv": Path(csv_path).name, "issues": [], "quality": []}
    tmp = runs / ".build.duckdb"
    for p in (tmp, Path(str(tmp) + ".wal")):
        p.unlink(missing_ok=True)
    try:
        sha = sha256_file(csv_path)
    except OSError as exc:
        report["issues"] = [dict(rule="DQ-007", message=f"unreadable file: {type(exc).__name__}", count=1)]
        publish.write_last_report(runs, report)
        return report
    run_id = f"{sha[:12]}-{inputs.reference_date.isoformat() if inputs.reference_date else 'noref'}"
    report.update(run_id=run_id, snapshot_id=sha[:12])
    con = duckdb.connect(str(tmp))
    try:
        issues = ingest.validate_and_stage(con, csv_path)
        if issues:
            report["issues"] = [vars(i) for i in issues]
            return report
        model.build(con)
        metrics.setup_runtime_inputs(con, inputs)
        metrics.build_core_views(con)
        results = quality.run_core(con, inputs)
        aging_status, reason = "pending_reference_date", "reference_date not provided"
        if inputs.reference_date is not None:
            dq4 = next(x for x in results if x["rule_id"] == "DQ-004")
            if dq4["status"] == quality.FAIL:
                aging_status, reason = "blocked", f"DQ-004: {dq4['failing_rows']} stage_entered_date after reference_date"
            else:
                metrics.build_aging_views(con)
                dq15 = quality.run_aging(con, True)
                results.append(dq15)
                if dq15["status"] == quality.PASS:
                    aging_status, reason = "available", ""
                else:
                    metrics.drop_aging_views(con)
                    aging_status, reason = "blocked", "DQ-015 negative aging"
        if not any(x["rule_id"] == "DQ-015" for x in results):
            results.append(quality.run_aging(con, False))
        report["quality"] = results
        if quality.core_blocked(results):
            report["issues"] = [dict(rule=x["rule_id"], message=x["name"], count=x["failing_rows"])
                                for x in results if x["status"] == quality.FAIL and x["scope"] == "core"]
            return report
        rows = con.execute("SELECT COUNT(*) FROM fact_consequence_case").fetchone()[0]
        con.execute("CREATE OR REPLACE TABLE run_metadata AS SELECT ?::VARCHAR run_id, ?::VARCHAR snapshot_id, ?::VARCHAR csv_sha256, ?::BIGINT row_count, ?::DATE reference_date, ?::VARCHAR aging_status, ?::VARCHAR aging_reason",
                    [run_id, sha[:12], sha, rows, inputs.reference_date, aging_status, reason])
        quality.store(con, results, run_id)
        con.close()
        report.update(status="published", row_count=rows, aging_status=aging_status, aging_reason=reason,
                      reference_date=inputs.reference_date.isoformat() if inputs.reference_date else None)
        publish.publish(runs, tmp, run_id, report)
        return report
    except Exception as exc:  # DuckDB/IO failure: keep previous valid state
        report["issues"] = [dict(rule="PIPELINE", message=f"{type(exc).__name__}: {exc}", count=1)]
        return report
    finally:
        try:
            con.close()
        except Exception:
            pass
        for p in (tmp, Path(str(tmp) + ".wal")):
            p.unlink(missing_ok=True)
        publish.write_last_report(runs, report)
