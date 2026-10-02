import json
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from src.cpd import ai_brief, metrics, pipeline, publish
from tests.conftest import GOLDEN_REF, GOLDEN_ROWS, make_inputs

APP = str(Path(__file__).resolve().parents[1] / "src/cpd/dashboard.py")
KEY = "test-secret-key-123"
URL = "https://ai.example.invalid/v1/chat"
BRIEF = "1. จุดที่ควรตรวจสอบ ... 2. ข้อสังเกตคอขวด ... 3. ข้อเสนอปรับปรุงขั้นตอน ..."


def ok_response(text=BRIEF, model="company-model-x"):
    return 200, json.dumps({"model": model, "choices": [{"message": {"content": text}}]})


class FakeEndpoint:
    def __init__(self, result=None, exc=None):
        self.result, self.exc, self.calls = result or ok_response(), exc, []

    def __call__(self, url, headers, body, timeout):
        self.calls.append(dict(url=url, headers=headers, body=body.decode("utf-8"), timeout=timeout))
        if self.exc:
            raise self.exc
        return self.result


@pytest.fixture
def cfg():
    return ai_brief.load_ai_config({ai_brief.ENV_URL: URL, ai_brief.ENV_KEY: KEY, ai_brief.ENV_MODEL: "configured-model"})


@pytest.fixture
def con(published):
    c = publish.connect_published(published)
    yield c
    c.close()


@pytest.fixture
def store(tmp_path):
    return tmp_path / "briefs" / "ai_briefs.duckdb"


def fake(monkeypatch, **kw):
    f = FakeEndpoint(**kw)
    monkeypatch.setattr(ai_brief, "_http_post", f)
    return f


def test_success_generation_and_persistence(monkeypatch, con, cfg, store):
    f = fake(monkeypatch)
    rec = ai_brief.generate_brief(con, None, cfg, store)
    assert rec["generation_status"] == "success" and rec["brief_text"] == BRIEF
    assert len(f.calls) == 1 and f.calls[0]["url"] == URL
    assert f.calls[0]["headers"]["Authorization"] == f"Bearer {KEY}"
    stored = ai_brief.latest_brief(store)
    assert stored["brief_id"] == rec["brief_id"] and stored["brief_text"] == BRIEF
    assert stored["generation_status"] == "success" and stored["model_identifier"] == "company-model-x"
    assert stored["run_id"] == metrics.run_status(con)["run_id"]
    assert stored["case_domain_filter"] == "all" and str(stored["reference_date"]) == "2026-10-01"
    assert stored["generated_at"] is not None


def test_payload_contains_only_approved_aggregates(monkeypatch, con, cfg, store):
    f = fake(monkeypatch)
    ai_brief.generate_brief(con, "behavior", cfg, store)
    body = json.loads(f.calls[0]["body"])
    assert body["model"] == "configured-model"
    agg = json.loads(body["messages"][1]["content"])
    assert agg["case_domain_filter"] == "behavior" and agg["reference_date"] == "2026-10-01"
    assert (agg["total_cases"], agg["open_cases"], agg["closed_cases"]) == (5, 4, 1)
    assert agg["open_cases_by_stage"] == {"collecting_info": 1, "follow_up": 2, "reviewing": 1}
    assert agg["top_3_longest_open_cases"] == [{"rank": 1, "stage": "follow_up", "days_in_current_stage": 60},
                                               {"rank": 2, "stage": "reviewing", "days_in_current_stage": 30},
                                               {"rank": 3, "stage": "follow_up", "days_in_current_stage": 1}]


def test_no_raw_sensitive_fields_in_request(monkeypatch, con, cfg, store):
    f = fake(monkeypatch)
    ai_brief.generate_brief(con, None, cfg, store)
    sent = f.calls[0]["body"]
    for row in GOLDEN_ROWS.splitlines():
        case_id, _, _, _, entered, owner = row.split(",")
        assert case_id not in sent and owner not in sent
        if entered != "2026-10-01":  # reference_date itself is an approved input
            assert entered not in sent
    for field in ("case_id", "owner", "stage_entered_date"):
        assert field not in sent.replace("Do not", "")
    assert KEY not in sent  # secret only in header, never in body


def test_aggregate_validator_rejects_extra_fields(con):
    agg = ai_brief.build_aggregate(con)
    bad = dict(agg, case_id="G01")
    with pytest.raises(ValueError):
        ai_brief.validate_aggregate(bad)
    bad2 = dict(agg, top_3_longest_open_cases=[{"rank": 1, "stage": "x", "days_in_current_stage": 1, "owner": "HR-01"}])
    with pytest.raises(ValueError):
        ai_brief.validate_aggregate(bad2)


def test_prompt_contains_governance_boundaries():
    p = ai_brief.SYSTEM_PROMPT.lower()
    for phrase in ("disciplinary", "score or", "rank any employee", "intent, personality or mental state", "replace hr approval"):
        assert phrase in p


@pytest.mark.parametrize("kind,result,exc,category", [
    ("network", None, OSError("boom https://secret-host"), "endpoint_unavailable"),
    ("500", (500, "oops"), None, "endpoint_error"),
    ("401", (401, "no"), None, "auth_failure"),
    ("429", (429, "slow"), None, "rate_limited"),
])
def test_endpoint_failures_persisted_without_leaking(monkeypatch, con, cfg, store, kind, result, exc, category):
    fake(monkeypatch, result=result, exc=exc)
    rec = ai_brief.generate_brief(con, None, cfg, store)
    assert rec["generation_status"] == "failed" and rec["error_category"] == category and rec["brief_text"] == ""
    stored = ai_brief.latest_brief(store)
    assert stored["generation_status"] == "failed" and stored["error_category"] == category
    for secret in (KEY, URL, "secret-host"):
        assert secret not in str(stored["error_message"])


@pytest.mark.parametrize("raw", ["not json", "{}", json.dumps({"choices": []}), json.dumps({"choices": [{"message": {}}]}),
                                 json.dumps({"choices": [{"message": {"content": "   "}}]}),
                                 json.dumps({"choices": [{"message": {"content": 42}}]})])
def test_malformed_response(monkeypatch, con, cfg, store, raw):
    fake(monkeypatch, result=(200, raw))
    rec = ai_brief.generate_brief(con, None, cfg, store)
    assert rec["generation_status"] == "failed" and rec["error_category"] == "malformed_response"
    assert ai_brief.latest_brief(store)["error_category"] == "malformed_response"


def test_not_configured_makes_no_call_and_persists_nothing(monkeypatch, con, store):
    f = fake(monkeypatch)
    rec = ai_brief.generate_brief(con, None, ai_brief.load_ai_config({}), store)
    assert rec["generation_status"] == "not_configured" and f.calls == []
    assert ai_brief.latest_brief(store) is None


def test_missing_reference_date_marks_fields_unavailable(monkeypatch, golden_csv, runs, cfg, store):
    pipeline.run_pipeline(golden_csv, make_inputs(None), runs)
    c = publish.connect_published(runs)
    f = fake(monkeypatch)
    ai_brief.generate_brief(c, None, cfg, store)
    agg = json.loads(json.loads(f.calls[0]["body"])["messages"][1]["content"])
    assert agg["reference_date"] == "unavailable" and agg["top_3_longest_open_cases"] == "unavailable"
    assert ai_brief.latest_brief(store)["reference_date"] is None
    c.close()


def test_latest_retrieval_and_persistence_survives_pipeline_rerun(monkeypatch, con, cfg, golden_csv, published, tmp_path):
    store = ai_brief.store_path(published)
    fake(monkeypatch, result=ok_response("first brief"))
    ai_brief.generate_brief(con, None, cfg, store)
    fake(monkeypatch, result=ok_response("second brief"))
    ai_brief.generate_brief(con, "performance", cfg, store)
    latest = ai_brief.latest_brief(store)
    assert latest["brief_text"] == "second brief" and latest["case_domain_filter"] == "performance"
    pipeline.run_pipeline(golden_csv, make_inputs(GOLDEN_REF), published)  # replaces run db, not the brief store
    assert ai_brief.latest_brief(store)["brief_text"] == "second brief"


def test_persistence_failure_reported_not_raised(monkeypatch, con, cfg, tmp_path):
    fake(monkeypatch)
    bad_store = tmp_path / "is_a_dir.duckdb"
    bad_store.mkdir()
    rec = ai_brief.generate_brief(con, None, cfg, bad_store)
    assert rec["error_category"] == "persistence_failure" and rec["generation_status"] == "failed"


def test_no_hardcoded_endpoint_or_secret_in_source():
    src = Path(ai_brief.__file__).read_text(encoding="utf-8")
    assert "http://" not in src and "https://" not in src.replace("https://ai.example", "")
    assert KEY not in src


# ---------------- dashboard ----------------
def app(monkeypatch, runs, configured=True):
    monkeypatch.setenv("CPD_RUNS_DIR", str(runs))
    for k in (ai_brief.ENV_URL, ai_brief.ENV_KEY, ai_brief.ENV_MODEL):
        monkeypatch.delenv(k, raising=False)
    if configured:
        monkeypatch.setenv(ai_brief.ENV_URL, URL)
        monkeypatch.setenv(ai_brief.ENV_KEY, KEY)
    return AppTest.from_file(APP, default_timeout=30)


def card(at, label):
    return next(m.value for m in at.metric if m.label == label)


def test_dashboard_generate_and_display(monkeypatch, published):
    f = fake(monkeypatch)
    at = app(monkeypatch, published).run()
    assert not at.exception and any("No brief generated yet" in c.value for c in at.caption)
    at.button(key="gen_brief").click().run()
    assert not at.exception and len(f.calls) == 1
    assert any(BRIEF in m.value for m in at.markdown)
    assert any("Generation status: success" in s.value for s in at.success)
    at2 = app(monkeypatch, published).run()  # retrieval on a fresh session
    assert any(BRIEF in m.value for m in at2.markdown)


def test_dashboard_filter_used_for_brief(monkeypatch, published):
    f = fake(monkeypatch)
    at = app(monkeypatch, published).run()
    at.selectbox(key="case_domain").select("performance").run()
    at.button(key="gen_brief").click().run()
    agg = json.loads(json.loads(f.calls[0]["body"])["messages"][1]["content"])
    assert agg["case_domain_filter"] == "performance" and agg["total_cases"] == 5


@pytest.mark.parametrize("kw", [dict(exc=OSError("down")), dict(result=(500, "err")), dict(result=(200, "garbage"))])
def test_core_dashboard_works_when_ai_endpoint_unavailable(monkeypatch, published, kw):
    fake(monkeypatch, **kw)
    at = app(monkeypatch, published).run()
    at.button(key="gen_brief").click().run()
    assert not at.exception
    assert any("Generation status: failed" in e.value for e in at.error)
    assert (card(at, "Total Cases"), card(at, "Closed Cases"), card(at, "Open Cases")) == ("10", "2", "8")
    top = next(d.value for d in at.dataframe if "rank" in d.value.columns)
    assert list(top.case_id) == ["G07", "G02", "G03"]


def test_dashboard_ai_not_configured_core_unaffected(monkeypatch, published):
    f = fake(monkeypatch)
    at = app(monkeypatch, published, configured=False).run()
    assert not at.exception and at.button(key="gen_brief").disabled
    assert any("AI endpoint not configured" in i.value for i in at.info)
    assert card(at, "Total Cases") == "10" and f.calls == []


def test_dashboard_ai_section_crash_is_contained(monkeypatch, published):
    def boom(*a, **k):
        raise RuntimeError("unexpected")
    monkeypatch.setattr(ai_brief, "latest_brief", boom)
    at = app(monkeypatch, published).run()
    assert not at.exception and any("AI brief section unavailable" in w.value for w in at.warning)
    assert card(at, "Total Cases") == "10"
