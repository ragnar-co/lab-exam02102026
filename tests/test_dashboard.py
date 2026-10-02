import pytest
from streamlit.testing.v1 import AppTest

from src.cpd import pipeline
from tests.conftest import GOLDEN_REF, make_inputs

from pathlib import Path
APP = str(Path(__file__).resolve().parents[1] / "src/cpd/dashboard.py")


def app(monkeypatch, runs):
    monkeypatch.setenv("CPD_RUNS_DIR", str(runs))
    return AppTest.from_file(APP, default_timeout=30)


def card(at, label):
    return next(m.value for m in at.metric if m.label == label)


def test_da001_cards_and_da003_filter(monkeypatch, published):
    at = app(monkeypatch, published).run()
    assert not at.exception
    assert (card(at, "Total Cases"), card(at, "Closed Cases"), card(at, "Open Cases")) == ("10", "2", "8")
    assert all("certified" in m.help and "draft" not in m.help for m in at.metric)
    at.selectbox(key="case_domain").select("behavior").run()
    assert (card(at, "Total Cases"), card(at, "Closed Cases"), card(at, "Open Cases")) == ("5", "1", "4")
    at.selectbox(key="case_domain").select("performance").run()
    assert card(at, "Total Cases") == "5"
    at.selectbox(key="case_domain").select("all").run()  # reset
    assert card(at, "Total Cases") == "10"


def test_da004_005_aging_and_top3(monkeypatch, published):
    at = app(monkeypatch, published).run()
    dfs = [d.value for d in at.dataframe]
    top = next(d for d in dfs if "rank" in d.columns)
    assert list(top.case_id) == ["G07", "G02", "G03"]
    at.selectbox(key="case_domain").select("behavior").run()
    top = next(d.value for d in at.dataframe if "rank" in d.value.columns)
    assert list(top.case_id) == ["G02", "G01", "G10"]


def test_da004_pending_without_reference_date(monkeypatch, golden_csv, runs):
    pipeline.run_pipeline(golden_csv, make_inputs(None), runs)
    at = app(monkeypatch, runs).run()
    assert not at.exception
    assert card(at, "Total Cases") == "10"
    assert any("Pending / unavailable" in i.value for i in at.info)
    assert not any("rank" in d.value.columns for d in at.dataframe)


def test_drill_down(monkeypatch, published):
    at = app(monkeypatch, published).run()
    at.selectbox(key="drill_status").select("closed").run()
    drill = next(d.value for d in at.dataframe if "case_status" in d.value.columns)
    assert set(drill.case_id) == {"G05", "G06"}


def test_da006_validation_failure_ux_keeps_previous_state(monkeypatch, published, tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("case_id,case_domain\nG1,behavior\n")
    pipeline.run_pipeline(bad, make_inputs(GOLDEN_REF), published)
    at = app(monkeypatch, published).run()
    assert any("rejected" in e.value for e in at.error)
    assert card(at, "Total Cases") == "10"  # previous valid state still shown


def test_no_published_run(monkeypatch, runs):
    at = app(monkeypatch, runs).run()
    assert not at.exception and any("No published run" in w.value for w in at.warning)


def test_masking_flag(monkeypatch, published):
    monkeypatch.setenv("CPD_MASK_IDENTIFIERS", "true")
    at = app(monkeypatch, published).run()
    top = next(d.value for d in at.dataframe if "rank" in d.value.columns)
    assert all(v.startswith("id-") for v in top.case_id) and all(v.startswith("id-") for v in top.owner)
