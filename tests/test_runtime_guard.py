import re
from pathlib import Path

import pytest

from src.cpd import config, metrics, pipeline, publish
from tests.conftest import GOLDEN_REF, make_inputs


def open_run(csv, runs, ref):
    rep = pipeline.run_pipeline(csv, make_inputs(ref), runs)
    return rep, publish.connect_published(runs)


def test_it006_no_reference_date_pending_not_defaulted(golden_csv, runs):
    rep, con = open_run(golden_csv, runs, None)
    assert rep["status"] == "published" and rep["aging_status"] == "pending_reference_date"
    assert metrics.scalar(con, "metric_total_cases") == 10  # not dependent on runtime input
    assert metrics.scalar(con, "metric_open_cases") == 8
    assert metrics.case_aging(con) is None and metrics.top3(con) is None
    assert con.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name='mart_consequence_case_aging'").fetchone()[0] == 0
    assert dict(con.execute("SELECT rule_id, status FROM quality_results").fetchall())["DQ-004"] == "pending"


def test_stage_date_after_reference_date_blocks_aging_only(golden_csv, runs):  # DQ-004
    from datetime import date
    rep, con = open_run(golden_csv, runs, date(2026, 9, 1))  # G08 (2026-10-01) is after this
    assert rep["status"] == "published" and rep["aging_status"] == "blocked"
    assert metrics.top3(con) is None and metrics.scalar(con, "metric_total_cases") == 10


def test_reference_date_parsing_strict():
    assert config.parse_reference_date(None) is None and config.parse_reference_date("") is None
    for bad in ("2026/10/01", "01-10-2026", "2026-13-01", "yesterday"):
        with pytest.raises(config.ConfigError):
            config.parse_reference_date(bad)


def test_default_config_reference_date_is_approved_exam_assumption_and_rules():
    inp = config.load_runtime_inputs(env={})
    assert inp.reference_date == GOLDEN_REF  # 2026-10-01
    assert inp.closed_stages == ("closed",) and set(inp.open_stages) == {"reviewing", "follow_up", "collecting_info"}


def test_env_reference_date_override():
    assert config.load_runtime_inputs(env={"CPD_REFERENCE_DATE": "2026-10-05"}).reference_date.isoformat() == "2026-10-05"


def test_no_system_date_or_hardcoded_reference_in_code():
    root = Path(__file__).resolve().parents[1]
    for f in list((root / "src").rglob("*.py")) + list((root / "sql").glob("*.sql")) + [root / "app.py"]:
        text = f.read_text(encoding="utf-8")
        assert not re.search(r"CURRENT_DATE|CURRENT_TIMESTAMP|now\(\)|date\.today|datetime\.now\(\)\.date", text, re.I) or f.name == "pipeline.py", f
    # pipeline.py may use wall-clock only for run timestamps, never for dates in metrics
    assert "date.today" not in (root / "src/cpd/pipeline.py").read_text()
    assert "CURRENT_DATE" not in (root / "src/cpd/pipeline.py").read_text()


def test_no_committed_secrets():
    root = Path(__file__).resolve().parents[1]
    for f in list((root / "src").rglob("*.py")) + [root / "app.py", root / "config/runtime_config.json"]:
        assert not re.search(r"(api[_-]?key|secret|token|password)\s*[=:]\s*['\"][^'\"]+", f.read_text(), re.I), f
