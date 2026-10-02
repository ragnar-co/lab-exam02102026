import pytest

from src.cpd import pipeline, publish
from tests.conftest import GOLDEN_ROWS, HEADER, make_inputs, write_csv


def run(path, runs):
    return pipeline.run_pipeline(path, make_inputs(), runs)


def rules(rep):
    return {i["rule"] for i in rep["issues"]}


def test_ut001_missing_column_blocks(tmp_path, runs):  # IT-002 / UT-001 / UT-012
    p = write_csv(tmp_path / "a.csv", "G1,behavior,improvement,reviewing,2026-09-01\n", "case_id,case_domain,response_type,stage,stage_entered_date\n")
    rep = run(p, runs)
    assert rep["status"] == "failed" and "DQ-007" in rules(rep)
    assert publish.read_pointer(runs) is None


def test_extra_column_needs_contract_review(tmp_path, runs):
    p = write_csv(tmp_path / "a.csv", "G1,behavior,improvement,reviewing,2026-09-01,HR-01,x\n", HEADER.strip() + ",extra\n")
    assert "DQ-007" in rules(run(p, runs))


def test_ut002_duplicate_case_id_rejected_not_deduped(tmp_path, runs):
    p = write_csv(tmp_path / "a.csv", GOLDEN_ROWS + "G01,behavior,improvement,reviewing,2026-09-01,HR-01\n")
    rep = run(p, runs)
    assert rep["status"] == "failed" and "DQ-003" in rules(rep)


@pytest.mark.parametrize("row", [",behavior,improvement,reviewing,2026-09-01,HR-01", "G1,behavior,improvement,reviewing,2026-09-01,  "])
def test_ut003_blank_required(tmp_path, runs, row):
    assert "DQ-006" in rules(run(write_csv(tmp_path / "a.csv", row + "\n"), runs))


def test_ut004_enum_outside_contract(tmp_path, runs):
    p = write_csv(tmp_path / "a.csv", "G1,Behavior,improvement,reviewing,2026-09-01,HR-01\nG2,behavior,improvement,archived,2026-09-01,HR-01\n")
    rep = run(p, runs)
    assert "DQ-005" in rules(rep)
    assert sum(i["count"] for i in rep["issues"]) == 2


def test_ut005_invalid_date_blocks_before_aging(tmp_path, runs):  # IT-003
    p = write_csv(tmp_path / "a.csv", "G1,behavior,improvement,reviewing,not-a-date,HR-01\n")
    rep = run(p, runs)
    assert rep["status"] == "failed" and "DQ-DATE" in rules(rep)


def test_unreadable_file(tmp_path, runs):
    rep = run(tmp_path / "missing.csv", runs)
    assert rep["status"] == "failed"


def test_identifiers_stay_varchar(published):
    import duckdb
    c = duckdb.connect(str(published / publish.read_pointer(published)["db"]), read_only=True)
    types = dict(c.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='fact_consequence_case'").fetchall())
    assert types["case_id"] == "VARCHAR" and types["stage_entered_date"] == "DATE"


def test_it002_invalid_run_keeps_previous_valid_state(published, tmp_path):
    before = publish.read_pointer(published)
    bad = write_csv(tmp_path / "bad.csv", "G1,behavior,improvement,reviewing,nope,HR-01\n")
    rep = pipeline.run_pipeline(bad, make_inputs(), published)
    assert rep["status"] == "failed"
    assert publish.read_pointer(published) == before
    assert publish.read_last_report(published)["status"] == "failed"
    assert publish.connect_published(published) is not None
