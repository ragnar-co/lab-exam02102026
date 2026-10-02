import duckdb
import pytest

from src.cpd import metrics, pipeline, publish
from tests.conftest import GOLDEN_REF, REAL_CSV, make_inputs


def snapshot(runs):
    con = publish.connect_published(runs)
    try:
        out = {t: con.execute(f"SELECT * FROM {t} ORDER BY ALL").fetchall()
               for t in ("stg_consequence_case", "fact_consequence_case", "dim_case_domain", "dim_response_type", "dim_stage", "dim_owner")}
        out["metrics"] = [metrics.scalar(con, n, d) for n in ("metric_total_cases", "metric_open_cases", "metric_closed_cases") for d in (None, "behavior")]
        out["top3"] = metrics.top3(con).values.tolist()
        return out
    finally:
        con.close()


def test_it004_idempotent_rerun(golden_csv, runs):
    r1 = pipeline.run_pipeline(golden_csv, make_inputs(GOLDEN_REF), runs)
    s1 = snapshot(runs)
    r2 = pipeline.run_pipeline(golden_csv, make_inputs(GOLDEN_REF), runs)
    s2 = snapshot(runs)
    assert r1["run_id"] == r2["run_id"] and r2["status"] == "published"
    assert s1 == s2
    assert len(s2["fact_consequence_case"]) == 10 and len(s2["dim_owner"]) == 3  # no duplicates
    assert len(list(runs.glob("*.duckdb"))) == 1  # same snapshot replaced, not appended


@pytest.mark.skipif(not REAL_CSV.exists(), reason="mock CSV not present")
def test_it001_end_to_end_real_mock_csv(tmp_path):
    runs = tmp_path / "runs"
    rep = pipeline.run_pipeline(REAL_CSV, make_inputs(GOLDEN_REF), runs)
    assert rep["status"] == "published" and rep["row_count"] == 40000
    con = publish.connect_published(runs)
    total, closed, open_ = (metrics.scalar(con, n) for n in ("metric_total_cases", "metric_closed_cases", "metric_open_cases"))
    assert total == 40000 and closed + open_ == total
    # reconcile against raw CSV via independent query
    raw = duckdb.connect()
    exp = raw.execute("SELECT COUNT(*) FILTER (WHERE stage='closed'), COUNT(*) FROM read_csv(?, header=true, all_varchar=true)", [str(REAL_CSV)]).fetchone()
    assert (closed, total) == exp
    for d in ("behavior", "performance"):
        assert metrics.scalar(con, "metric_total_cases", d) == raw.execute("SELECT COUNT(*) FROM read_csv(?, header=true, all_varchar=true) WHERE case_domain=?", [str(REAL_CSV), d]).fetchone()[0]
    # aging / Top 3 with reference_date 2026-10-01, reconciled against an independent query
    assert metrics.run_status(con)["aging_status"] == "available"
    exp_top = raw.execute("""SELECT case_id, DATE_DIFF('day', CAST(stage_entered_date AS DATE), DATE '2026-10-01') d
        FROM read_csv(?, header=true, all_varchar=true) WHERE stage <> 'closed' ORDER BY d DESC, case_id ASC LIMIT 3""", [str(REAL_CSV)]).fetchall()
    top = metrics.top3(con)
    assert list(zip(top.case_id, top.metric_days_in_current_stage)) == exp_top
    assert len(metrics.case_aging(con)) == open_
    con.close()
