import duckdb
import pytest

from src.cpd import publish


@pytest.fixture
def con(published):
    c = publish.connect_published(published)
    yield c
    c.close()


def test_ut006_grain_and_surrogate(con):
    assert con.execute("SELECT COUNT(*), COUNT(DISTINCT case_id), COUNT(DISTINCT consequence_case_sk) FROM fact_consequence_case").fetchone() == (10, 10, 10)


@pytest.mark.parametrize("dim,key", [("dim_case_domain", "case_domain_key"), ("dim_response_type", "response_type_key"),
                                     ("dim_stage", "stage_key"), ("dim_owner", "owner_key")])
def test_ut007_010_no_orphans(con, dim, key):
    assert con.execute(f"SELECT COUNT(*) FROM fact_consequence_case f LEFT JOIN {dim} d USING ({key}) WHERE d.{key} IS NULL").fetchone()[0] == 0


def test_dimension_grain(con):
    assert con.execute("SELECT COUNT(*) FROM dim_case_domain").fetchone()[0] == 2
    assert con.execute("SELECT COUNT(*) FROM dim_stage").fetchone()[0] == 4
    assert con.execute("SELECT COUNT(*) FROM dim_owner").fetchone()[0] == 3


def test_all_error_rules_pass_and_uncalibrated_not_faked(con):
    rows = con.execute("SELECT rule_id, severity, status FROM quality_results").fetchall()
    assert all(s == "pass" for _, sev, s in rows if sev == "error")
    by = {r: s for r, _, s in rows}
    assert {by[k] for k in ("DQ-002", "DQ-012", "DQ-013", "DQ-014")} == {"not_calibrated"}
    assert {"DQ-0%02d" % i for i in range(1, 16)} <= set(by)


def test_ut011_no_negative_aging(con):
    assert con.execute("SELECT COUNT(*) FROM mart_consequence_case_aging WHERE metric_days_in_current_stage < 0").fetchone()[0] == 0


def test_forbidden_schema_fields(con):
    n = con.execute("SELECT COUNT(*) FROM information_schema.columns WHERE table_name='fact_consequence_case' AND lower(column_name) IN ('churn_date','mrr','subscription_id','plan_id','price','billing_period','proration_amount')").fetchone()[0]
    assert n == 0
