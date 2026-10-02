from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from src.cpd import i18n, pipeline, publish
from tests.conftest import GOLDEN_REF, make_inputs

APP = str(Path(__file__).resolve().parents[1] / "src/cpd/dashboard.py")


def app(monkeypatch, runs, default="TH"):
    monkeypatch.setenv("CPD_RUNS_DIR", str(runs))
    monkeypatch.setenv("CPD_DEFAULT_LANG", default)
    return AppTest.from_file(APP, default_timeout=30)


def card(at, label):
    return next(m.value for m in at.metric if m.label == label)


def texts(at):
    parts = [m.value for m in at.markdown] + [c.value for c in at.caption] + [s.value for s in at.subheader] + [i.value for i in at.info]
    return " ".join(parts)


def test_translation_tables_have_identical_keys_and_utf8():
    assert set(i18n.TEXT["EN"]) == set(i18n.TEXT["TH"])
    for lang in i18n.LANGS:
        for key, val in i18n.TEXT[lang].items():
            assert val.strip(), (lang, key)
    assert set(i18n.VALUE_LABELS["EN"]) == set(i18n.VALUE_LABELS["TH"])
    for kind in i18n.VALUE_LABELS["EN"]:
        assert set(i18n.VALUE_LABELS["EN"][kind]) == set(i18n.VALUE_LABELS["TH"][kind])


def test_requested_thai_labels():
    th = lambda k: i18n.t("TH", k)
    assert th("app_title") == "แดชบอร์ดติดตามกระบวนการ Consequence"
    assert (th("kpi_total"), th("kpi_closed"), th("kpi_open")) == ("จำนวนกรณีทั้งหมด", "กรณีปิดแล้ว", "กรณีเปิด")
    assert th("stage_title") == "กรณีเปิดแยกตามขั้นตอน"
    assert th("aging_title") == "ระยะเวลาที่กรณีเปิดค้างในขั้นตอนปัจจุบัน"
    assert th("top3_title") == "3 กรณีที่อยู่ในขั้นตอนนานที่สุด"
    assert th("ai_button") == "สร้างร่างข้อเสนอปรับปรุงกระบวนการ"
    assert (th("pending"), th("failed"), th("success")) == ("รอข้อมูล", "ไม่สำเร็จ", "สำเร็จ")
    assert th("empty") == "ไม่มีข้อมูลสำหรับเงื่อนไขที่เลือก"
    assert i18n.label("TH", "case_domain", "behavior") == "พฤติกรรม" and i18n.label("TH", "case_domain", "performance") == "ผลงาน"
    assert i18n.label("EN", "case_domain", "behavior") == "Behavior"
    assert i18n.label("TH", "stage", "unknown_value") == "unknown_value"  # unknown values pass through


def test_localize_df_changes_values_not_columns():
    import pandas as pd
    df = pd.DataFrame({"case_id": ["A"], "stage": ["follow_up"], "case_domain": ["behavior"], "owner": ["HR-01"]})
    out = i18n.localize_df(df, "TH")
    assert list(out.columns) == list(df.columns) and out.loc[0, "stage"] == "ติดตามผล" and out.loc[0, "case_id"] == "A"
    assert df.loc[0, "stage"] == "follow_up"  # original untouched


def test_default_language_is_thai(monkeypatch, published):
    monkeypatch.delenv("CPD_DEFAULT_LANG", raising=False)
    monkeypatch.setenv("CPD_RUNS_DIR", str(published))
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception and at.radio(key="lang").value == "TH"
    assert [m.label for m in at.metric] == ["จำนวนกรณีทั้งหมด", "กรณีปิดแล้ว", "กรณีเปิด"]
    assert "แดชบอร์ดติดตามกระบวนการ Consequence" in texts(at) and "วันที่อ้างอิง" in texts(at) and "2026-10-01" in texts(at)


def test_thai_and_english_views_show_same_numbers(monkeypatch, published):
    th = app(monkeypatch, published, "TH").run()
    en = app(monkeypatch, published, "EN").run()
    assert not th.exception and not en.exception
    assert [m.value for m in th.metric] == [m.value for m in en.metric] == ["10", "2", "8"]
    top_th = next(d.value for d in th.dataframe if "rank" in d.value.columns)
    top_en = next(d.value for d in en.dataframe if "rank" in d.value.columns)
    assert list(top_th.case_id) == list(top_en.case_id) == ["G07", "G02", "G03"]
    assert list(top_th.metric_days_in_current_stage) == list(top_en.metric_days_in_current_stage) == [90, 60, 60]
    assert list(top_th.columns) == list(top_en.columns)  # internal column names never translated
    assert "ติดตามผล" in set(top_th.stage) and "Follow-up" in set(top_en.stage)


def test_switch_language_preserves_filters_and_state(monkeypatch, published):
    at = app(monkeypatch, published, "TH").run()
    at.selectbox(key="case_domain").select("behavior").run()
    at.selectbox(key="drill_status").select("open").run()
    at.selectbox(key="drill_stage").select("follow_up").run()
    before = [m.value for m in at.metric]
    assert before == ["5", "1", "4"]
    at.radio(key="lang").set_value("EN").run()
    assert not at.exception and at.radio(key="lang").value == "EN"
    assert (at.selectbox(key="case_domain").value, at.selectbox(key="drill_status").value, at.selectbox(key="drill_stage").value) == ("behavior", "open", "follow_up")
    assert [m.label for m in at.metric] == ["Total Cases", "Closed Cases", "Open Cases"] and [m.value for m in at.metric] == before
    assert "Behavior" in texts(at)
    at.radio(key="lang").set_value("TH").run()
    assert at.selectbox(key="case_domain").value == "behavior" and [m.value for m in at.metric] == before
    assert "พฤติกรรม" in texts(at)


def test_switch_language_does_not_touch_data(monkeypatch, published):
    ptr = publish.read_pointer(published)
    at = app(monkeypatch, published, "TH").run()
    at.radio(key="lang").set_value("EN").run()
    assert publish.read_pointer(published) == ptr  # no new run, nothing republished


def test_thai_pending_state_without_reference_date(monkeypatch, golden_csv, runs):
    pipeline.run_pipeline(golden_csv, make_inputs(None), runs)
    at = app(monkeypatch, runs, "TH").run()
    assert not at.exception and any("รอข้อมูล" in i.value for i in at.info)
    assert not any("rank" in d.value.columns for d in at.dataframe)


def test_thai_ai_section(monkeypatch, published):
    for k in ("CPD_AI_ENDPOINT_URL", "CPD_AI_API_KEY"):
        monkeypatch.delenv(k, raising=False)
    at = app(monkeypatch, published, "TH").run()
    assert not at.exception and at.button(key="gen_brief").label == "สร้างร่างข้อเสนอปรับปรุงกระบวนการ"
    assert any("ยังไม่ได้ตั้งค่า AI endpoint" in i.value for i in at.info)


def test_thai_ai_success_and_failure_labels(monkeypatch, published):
    from src.cpd import ai_brief
    import json
    monkeypatch.setenv("CPD_AI_ENDPOINT_URL", "https://ai.example.invalid/x")
    monkeypatch.setenv("CPD_AI_API_KEY", "dummy-test-value")
    monkeypatch.setattr(ai_brief, "_http_post", lambda *a, **k: (200, json.dumps({"choices": [{"message": {"content": "ร่างข้อเสนอ"}}]})))
    at = app(monkeypatch, published, "TH").run()
    at.button(key="gen_brief").click().run()
    assert any("สถานะการสร้าง: สำเร็จ" in s.value for s in at.success)
    monkeypatch.setattr(ai_brief, "_http_post", lambda *a, **k: (500, "x"))
    at.button(key="gen_brief").click().run()
    assert any("สถานะการสร้าง: ไม่สำเร็จ" in e.value for e in at.error)
    assert [m.value for m in at.metric] == ["10", "2", "8"]  # core unaffected
