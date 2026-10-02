import pytest

from src.cpd import metrics, publish
from tests.conftest import GOLDEN_REF


@pytest.fixture
def con(published):
    c = publish.connect_published(published)
    yield c
    c.close()


EXPECT = {  # hand-calculated from GOLDEN_ROWS
    None: dict(total=10, closed=2, open=8, stage={"collecting_info": 2, "follow_up": 3, "reviewing": 3}, top=[("G07", 90), ("G02", 60), ("G03", 60)]),
    "behavior": dict(total=5, closed=1, open=4, stage={"collecting_info": 1, "follow_up": 2, "reviewing": 1}, top=[("G02", 60), ("G01", 30), ("G10", 1)]),
    "performance": dict(total=5, closed=1, open=4, stage={"collecting_info": 1, "follow_up": 1, "reviewing": 2}, top=[("G07", 90), ("G03", 60), ("G09", 60)]),
}


@pytest.mark.parametrize("dom", EXPECT)
def test_mv001_to_006(con, dom):
    e = EXPECT[dom]
    assert metrics.scalar(con, "metric_total_cases", dom) == e["total"]
    assert metrics.scalar(con, "metric_closed_cases", dom) == e["closed"]
    assert metrics.scalar(con, "metric_open_cases", dom) == e["open"]
    assert dict(metrics.open_by_stage(con, dom).itertuples(index=False)) == e["stage"]
    top = metrics.top3(con, dom)
    assert list(zip(top.case_id, top.metric_days_in_current_stage)) == e["top"]  # ids, order, days (tie-break case_id ASC)


@pytest.mark.parametrize("dom", EXPECT)
def test_mv007_rates_and_reconciliation(con, dom):
    e = EXPECT[dom]
    assert metrics.scalar(con, "consequence_process_completion_rate", dom) == pytest.approx(e["closed"] / e["total"])
    assert metrics.scalar(con, "open_case_rate", dom) == pytest.approx(e["open"] / e["total"])
    assert e["total"] == metrics.scalar(con, "metric_open_cases", dom) + metrics.scalar(con, "metric_closed_cases", dom)
    assert sum(metrics.open_by_stage(con, dom).iloc[:, 1]) == e["open"]


def test_row_level_days(con):
    aging = metrics.case_aging(con).set_index("case_id")["metric_days_in_current_stage"].to_dict()
    assert aging == {"G01": 30, "G02": 60, "G03": 60, "G04": 10, "G07": 90, "G08": 0, "G09": 60, "G10": 1}
    assert set(aging) == set(metrics.case_list(con, None, "open").case_id)  # closed cases excluded


def test_it005_filter_does_not_mix_domains(con):
    for dom in ("behavior", "performance"):
        assert set(metrics.case_aging(con, dom).case_domain) == {dom}
        assert set(metrics.top3(con, dom).case_domain) == {dom}
        assert set(metrics.case_list(con, dom).case_domain) == {dom}
    all_ids = set(metrics.case_list(con).case_id)
    assert set(metrics.case_list(con, "behavior").case_id) | set(metrics.case_list(con, "performance").case_id) == all_ids
    assert not set(metrics.case_list(con, "behavior").case_id) & set(metrics.case_list(con, "performance").case_id)


def test_reference_date_recorded_not_system(con):
    assert metrics.run_status(con)["reference_date"] == GOLDEN_REF
