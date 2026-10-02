from datetime import date
from pathlib import Path

import pytest

from src.cpd import config, pipeline

HEADER = "case_id,case_domain,response_type,stage,stage_entered_date,owner\n"
# Hand-computed golden fixture. Reference date 2026-10-01 = approved project-specific exam assumption.
GOLDEN_ROWS = """G01,behavior,improvement,reviewing,2026-09-01,HR-01
G02,behavior,recognition,follow_up,2026-08-02,HR-02
G03,performance,improvement,collecting_info,2026-08-02,HR-01
G04,performance,improvement,reviewing,2026-09-21,HR-03
G05,behavior,improvement,closed,2026-07-01,HR-02
G06,performance,recognition,closed,2026-06-01,HR-03
G07,performance,improvement,follow_up,2026-07-03,HR-02
G08,behavior,recognition,collecting_info,2026-10-01,HR-01
G09,performance,recognition,reviewing,2026-08-02,HR-01
G10,behavior,improvement,follow_up,2026-09-30,HR-03
"""
GOLDEN_REF = date(2026, 10, 1)
REAL_CSV = Path(__file__).resolve().parents[1] / "data" / "looktal_consequence_mock_2-3MB.csv"


def write_csv(path, body, header=HEADER):
    path.write_text(header + body, encoding="utf-8")
    return path


@pytest.fixture
def golden_csv(tmp_path):
    return write_csv(tmp_path / "golden.csv", GOLDEN_ROWS)


@pytest.fixture
def runs(tmp_path):
    return tmp_path / "runs"


def make_inputs(ref=None):
    """ref=None simulates a missing reference_date (overrides the configured one)."""
    import dataclasses
    return dataclasses.replace(config.load_runtime_inputs(env={}), reference_date=ref)


@pytest.fixture
def published(golden_csv, runs):
    """Golden run published with test reference date."""
    rep = pipeline.run_pipeline(golden_csv, make_inputs(GOLDEN_REF), runs)
    assert rep["status"] == "published", rep
    return runs


@pytest.fixture(autouse=True)
def _english_ui_by_default(monkeypatch):
    """Existing dashboard tests assert English UI text; the app default is Thai (see tests/test_i18n.py)."""
    monkeypatch.setenv("CPD_DEFAULT_LANG", "EN")
