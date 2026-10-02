"""Centralised UI translations (presentation text only). UTF-8. Data values/identifiers stay untouched.

Internal values (behavior, performance, closed, reviewing, follow_up, collecting_info, case_id, owner, ...) are
never changed in the data layer; this module only maps them to display labels.
"""
import os

LANGS = ("TH", "EN")
DEFAULT_LANG = "TH"
ENV_DEFAULT_LANG = "CPD_DEFAULT_LANG"


def default_lang(env=None) -> str:
    env = os.environ if env is None else env
    v = str(env.get(ENV_DEFAULT_LANG, DEFAULT_LANG)).upper()
    return v if v in LANGS else DEFAULT_LANG


TEXT = {
    "EN": {
        "page_title": "Consequence Process Dashboard",
        "app_title": "Consequence Process Dashboard",
        "eyebrow": "HR Analytics",
        "language": "Language / ภาษา",
        "reference_date": "Reference date",
        "filter": "Filter",
        "all_cases": "All cases",
        "ref_unavailable": "not available",
        "ref_pending": "not provided (pending)",
        "run_info": "Run `{run_id}` · snapshot `{snapshot}` · rows {rows} · reference date: {ref}",
        "kpi_total": "Total Cases",
        "kpi_closed": "Closed Cases",
        "kpi_open": "Open Cases",
        "kpi_help": "{metric} · {ctx} · metric_status: certified",
        "rates": "Completion rate: {c} · Open case rate: {o} · derived from certified metrics",
        "filter_label": "Case domain filter",
        "filter_help": "Applies to all components. Choose 'All' to reset.",
        "all": "All",
        "ctx": "Filter: {label}",
        "stage_title": "Open Cases by Stage",
        "stage_caption": "Open cases by current stage · {ctx}",
        "axis_stage": "Stage",
        "axis_open": "Open cases",
        "chart_table": "Data table for chart",
        "drill_title": "Case drill-down",
        "status": "Status",
        "stage": "Stage",
        "drill_caption": "{n} cases · {ctx}",
        "aging_title": "Open Case Aging",
        "aging_caption": "Days in current stage = calendar-day difference to reference date {ref} · {n} open cases · longest first; the bar shows relative age and the number is the exact value · {ctx}",
        "pending_aging": "Pending / unavailable: {reason}. Set reference_date in config/runtime_config.json (or `CPD_REFERENCE_DATE=YYYY-MM-DD`) and reload the CSV. System date is never used.",
        "top3_title": "Top 3 Longest Open Cases",
        "pending_top3": "Pending / unavailable: requires approved reference_date.",
        "top3_caption": "Ranked by days in current stage (longest first); ties by case_id ascending.",
        "days_unit": "{n} days",
        "empty": "No data available for the current filter.",
        "dq_title": "Data quality status (this run)",
        "no_run": "No published run yet. Load a CSV: `python app.py --load data/<file>.csv`",
        "rejected": "Latest CSV run was rejected; showing the previous valid published state (if any).",
        "ai_title": "Process Improvement Brief (AI bonus · experimental)",
        "ai_caption": "AI-generated draft from aggregate analytics only (no case_id/owner sent). For human review by HR; not a disciplinary decision, employee score or ranking.",
        "ai_not_configured": "AI endpoint not configured (set {url} and {api_key}). Core dashboard is unaffected.",
        "ai_button": "Generate Process Improvement Brief",
        "ai_spinner": "Generating brief...",
        "ai_none": "No brief generated yet.",
        "ai_success": "Generation status: success",
        "ai_failed": "Generation status: failed ({cat}): {msg}",
        "ai_meta": "generated_at {at} · run `{run_id}` · filter: {flt} · reference date {ref} · model {model} · brief_id `{bid}`",
        "ai_prev_run": "Note: this brief was generated from a different (previous) run.",
        "ai_crash": "AI brief section unavailable ({exc}). Core dashboard is unaffected.",
        "col_rank": "Rank",
        "col_case_id": "Case ID",
        "col_case_domain": "Case domain",
        "col_response_type": "Response type",
        "col_stage": "Stage",
        "col_stage_entered_date": "Stage entered date",
        "col_owner": "Owner",
        "col_case_status": "Status",
        "col_days": "Days in current stage",
        "col_days_help": "Calendar days from stage entered date to reference date",
        "lbl_case_id": "case_id",
        "lbl_stage": "stage",
        "lbl_owner": "owner",
        "pending": "Pending",
        "failed": "Failed",
        "success": "Success",
    },
    "TH": {
        "page_title": "แดชบอร์ดติดตามกระบวนการ Consequence",
        "app_title": "แดชบอร์ดติดตามกระบวนการ Consequence",
        "eyebrow": "การวิเคราะห์ข้อมูล HR",
        "language": "Language / ภาษา",
        "reference_date": "วันที่อ้างอิง",
        "filter": "ตัวกรอง",
        "all_cases": "ทุกกรณี",
        "ref_unavailable": "ไม่มีข้อมูล",
        "ref_pending": "ยังไม่ได้ระบุ (รอข้อมูล)",
        "run_info": "รอบข้อมูล `{run_id}` · snapshot `{snapshot}` · จำนวนแถว {rows} · วันที่อ้างอิง: {ref}",
        "kpi_total": "จำนวนกรณีทั้งหมด",
        "kpi_closed": "กรณีปิดแล้ว",
        "kpi_open": "กรณีเปิด",
        "kpi_help": "{metric} · {ctx} · สถานะ metric: certified (รับรองแล้ว)",
        "rates": "อัตราการปิดกรณี: {c} · อัตรากรณีเปิด: {o} · คำนวณจาก metric ที่ certified แล้ว",
        "filter_label": "ตัวกรองด้านของกรณี (case_domain)",
        "filter_help": "มีผลกับทุกส่วนของแดชบอร์ด เลือก 'ทั้งหมด' เพื่อล้างตัวกรอง",
        "all": "ทั้งหมด",
        "ctx": "ตัวกรอง: {label}",
        "stage_title": "กรณีเปิดแยกตามขั้นตอน",
        "stage_caption": "จำนวนกรณีเปิดแยกตามขั้นตอนปัจจุบัน · {ctx}",
        "axis_stage": "ขั้นตอน",
        "axis_open": "จำนวนกรณีเปิด",
        "chart_table": "ตารางข้อมูลของกราฟ",
        "drill_title": "รายละเอียดรายกรณี",
        "status": "สถานะ",
        "stage": "ขั้นตอน",
        "drill_caption": "{n} กรณี · {ctx}",
        "aging_title": "ระยะเวลาที่กรณีเปิดค้างในขั้นตอนปัจจุบัน",
        "aging_caption": "จำนวนวันที่อยู่ในขั้นตอนปัจจุบัน = ผลต่างวันตามปฏิทินถึงวันที่อ้างอิง {ref} · {n} กรณีเปิด · เรียงจากนานที่สุด แถบแสดงอายุเชิงเปรียบเทียบ และตัวเลขคือค่าจริง · {ctx}",
        "pending_aging": "รอข้อมูล / ยังไม่พร้อมใช้งาน: {reason} กำหนด reference_date ใน config/runtime_config.json (หรือ `CPD_REFERENCE_DATE=YYYY-MM-DD`) แล้วโหลด CSV ใหม่ ระบบไม่ใช้วันที่ของเครื่อง",
        "top3_title": "3 กรณีที่อยู่ในขั้นตอนนานที่สุด",
        "pending_top3": "รอข้อมูล / ยังไม่พร้อมใช้งาน: ต้องมี reference_date ที่อนุมัติแล้ว",
        "top3_caption": "เรียงตามจำนวนวันที่อยู่ในขั้นตอนปัจจุบัน (มากไปน้อย) หากเท่ากันเรียงตาม case_id จากน้อยไปมาก",
        "days_unit": "{n} วัน",
        "empty": "ไม่มีข้อมูลสำหรับเงื่อนไขที่เลือก",
        "dq_title": "สถานะคุณภาพข้อมูล (รอบนี้)",
        "no_run": "ยังไม่มีข้อมูลที่เผยแพร่ โหลด CSV ด้วย: `python app.py --load data/<file>.csv`",
        "rejected": "การโหลด CSV รอบล่าสุดถูกปฏิเสธ จึงแสดงข้อมูลรอบที่ถูกต้องก่อนหน้า (ถ้ามี)",
        "ai_title": "ร่างข้อเสนอปรับปรุงกระบวนการ (AI โบนัส · ทดลอง)",
        "ai_caption": "ร่างที่ AI สร้างจากข้อมูลสรุปเท่านั้น (ไม่ส่ง case_id/owner) ใช้เพื่อให้ HR พิจารณา ไม่ใช่การตัดสินโทษ การให้คะแนน หรือจัดอันดับพนักงาน",
        "ai_not_configured": "ยังไม่ได้ตั้งค่า AI endpoint (กำหนด {url} และ {api_key}) แดชบอร์ดหลักไม่ได้รับผลกระทบ",
        "ai_button": "สร้างร่างข้อเสนอปรับปรุงกระบวนการ",
        "ai_spinner": "กำลังสร้างร่างข้อเสนอ...",
        "ai_none": "ยังไม่มีการสร้างร่างข้อเสนอ",
        "ai_success": "สถานะการสร้าง: สำเร็จ",
        "ai_failed": "สถานะการสร้าง: ไม่สำเร็จ ({cat}): {msg}",
        "ai_meta": "สร้างเมื่อ {at} · รอบข้อมูล `{run_id}` · ตัวกรอง: {flt} · วันที่อ้างอิง {ref} · โมเดล {model} · brief_id `{bid}`",
        "ai_prev_run": "หมายเหตุ: ร่างนี้สร้างจากข้อมูลคนละรอบ (รอบก่อนหน้า)",
        "ai_crash": "ส่วนร่างข้อเสนอ AI ใช้งานไม่ได้ ({exc}) แดชบอร์ดหลักไม่ได้รับผลกระทบ",
        "col_rank": "อันดับ",
        "col_case_id": "case_id",
        "col_case_domain": "ด้านของกรณี (case_domain)",
        "col_response_type": "ประเภทการตอบสนอง (response_type)",
        "col_stage": "ขั้นตอน (stage)",
        "col_stage_entered_date": "วันที่เข้าขั้นตอน",
        "col_owner": "ผู้รับผิดชอบ (owner)",
        "col_case_status": "สถานะ",
        "col_days": "จำนวนวันที่อยู่ในขั้นตอนปัจจุบัน",
        "col_days_help": "จำนวนวันตามปฏิทินจากวันที่เข้าขั้นตอนถึงวันที่อ้างอิง",
        "lbl_case_id": "case_id",
        "lbl_stage": "ขั้นตอน",
        "lbl_owner": "ผู้รับผิดชอบ",
        "pending": "รอข้อมูล",
        "failed": "ไม่สำเร็จ",
        "success": "สำเร็จ",
    },
}

# value labels (display only)
VALUE_LABELS = {
    "EN": {
        "case_domain": {"behavior": "Behavior", "performance": "Performance"},
        "stage": {"closed": "Closed", "reviewing": "Reviewing", "follow_up": "Follow-up", "collecting_info": "Collecting info"},
        "response_type": {"recognition": "Recognition", "improvement": "Improvement"},
        "case_status": {"open": "Open", "closed": "Closed"},
    },
    "TH": {
        "case_domain": {"behavior": "พฤติกรรม", "performance": "ผลงาน"},
        "stage": {"closed": "ปิดแล้ว", "reviewing": "กำลังตรวจสอบ", "follow_up": "ติดตามผล", "collecting_info": "รวบรวมข้อมูล"},
        "response_type": {"recognition": "การยอมรับ/ชื่นชม", "improvement": "การปรับปรุง"},
        "case_status": {"open": "เปิด", "closed": "ปิด"},
    },
}

# display-only column labels; the dataframe columns themselves keep their internal names
COLUMN_KEYS = {"rank": "col_rank", "case_id": "col_case_id", "case_domain": "col_case_domain", "response_type": "col_response_type",
               "stage": "col_stage", "stage_entered_date": "col_stage_entered_date", "owner": "col_owner",
               "case_status": "col_case_status", "metric_days_in_current_stage": "col_days"}


def norm(lang) -> str:
    return lang if lang in LANGS else DEFAULT_LANG


def t(lang: str, key: str, **kw) -> str:
    s = TEXT[norm(lang)][key]
    return s.format(**kw) if kw else s


def label(lang: str, kind: str, value) -> str:
    """Display label for an internal value (kind: case_domain/stage/response_type/case_status); unknown -> raw."""
    return VALUE_LABELS[norm(lang)].get(kind, {}).get(value, str(value))


def localize_df(df, lang: str):
    """Copy of df with categorical VALUES mapped to display labels (column names untouched)."""
    if df is None:
        return None
    df = df.copy()
    for kind in VALUE_LABELS["EN"]:
        if kind in df.columns:
            df[kind] = df[kind].map(lambda v, k=kind: label(lang, k, v))
    return df
