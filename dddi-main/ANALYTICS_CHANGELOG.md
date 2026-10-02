# ANALYTICS_CHANGELOG.md

Project: Consequence Process Dashboard  
Document ID: analytics_changelog  
Priority: P1  
Depends on: METRIC_SPEC.md, KPI_DICTIONARY.md, PIPELINE_SPEC.md, DATA_CONTRACT.md

## Metric Definition Changes

### `change_type` Enum

`ANALYTICS_CHANGELOG.md` เป็นเอกสารเจ้าของ `change_type`

- `metric_definition`
- `kpi_target`
- `pipeline_logic`
- `dashboard`
- `data_contract`

2026-10-02: บันทึกการอนุมัติ business rule (open/closed, day-count, Top 3 tie-break) และ certify metric ทั้ง 6 ตัว — เป็น **การอนุมัติ business rule ที่เคย unresolved ไม่ใช่การเปลี่ยนสูตร metric** (SQL ใน `METRIC_LOGIC.md` ไม่ถูกแก้)

| date | change_type | changed_item | before_value | after_value | reason | approved_by | breaking_change |
|---|---|---|---|---|---|---|---|
| 2026-10-02 | metric_definition | `open case` / `closed case` (BUSINESS_GLOSSARY.md) | `null` — unresolved | open = `stage IN ('reviewing','follow_up','collecting_info')`; closed = `stage = 'closed'` | project-specific approved business rule for exam; ไม่ใช่ industry standard; สูตร metric ไม่เปลี่ยน | Exam candidate / implementation owner (project decision) | false |
| 2026-10-02 | metric_definition | `days_in_current_stage` day-count (BUSINESS_GLOSSARY.md) | `null` — unresolved | calendar-day difference `DATE_DIFF('day', stage_entered_date, reference_date)` | project-specific approved business rule for exam; สูตรใน METRIC_LOGIC.md ไม่เปลี่ยน | Exam candidate / implementation owner (project decision) | false |
| 2026-10-02 | metric_definition | Top 3 tie-break (BUSINESS_GLOSSARY.md) | `null` — unresolved | `days_in_current_stage DESC, case_id ASC` | project-specific approved business rule for exam; สูตรใน METRIC_LOGIC.md ไม่เปลี่ยน | Exam candidate / implementation owner (project decision) | false |
| 2026-10-02 | metric_definition | `metric_status` ของ `metric_total_cases`, `metric_closed_cases`, `metric_open_cases`, `metric_open_cases_by_stage`, `metric_days_in_current_stage`, `metric_top_3_longest_open_cases` | `draft` (v0.1) | `certified` (v1.0) | blocker ปิดครบ และ MV-001..007 ผ่าน (44 tests passed) | Exam candidate / implementation owner (project decision) | false |

เมื่อ certified metric เปลี่ยนนิยาม ต้องบันทึก:
- effective date
- before/after definition หรือ formula
- historical treatment: restate history หรือเก็บ old/new definition คู่กัน
- downstream consumers ที่ได้รับผล
- approval
- breaking-change handling

## KPI Target Changes

KPI targets ปัจจุบันใน `KPI_DICTIONARY.md` ยังเป็น `null` เพราะยังไม่ calibrate ดังนั้นไม่มี target change ที่เกิดขึ้นจริง

| date | change_type | changed_item | before_value | after_value | reason | approved_by | breaking_change |
|---|---|---|---|---|---|---|---|
| none | none | none | none | none | No approved KPI target change yet | none | false |

การตั้ง target ครั้งแรกเมื่อได้รับ approval ต้องบันทึกเป็น governance event และห้ามอ้างตัวเลข mock dataset เป็นมาตรฐาน

## Pipeline Changes

Baseline pipeline ปัจจุบัน:
- `pl_ingest_consequence_csv`
- `pl_build_consequence_model`
- `pl_build_consequence_metrics`
- full snapshot load strategy
- DuckDB semantic/mart layer

ยังไม่มี approved pipeline change หลัง baseline

| date | change_type | changed_item | before_value | after_value | reason | approved_by | breaking_change |
|---|---|---|---|---|---|---|---|
| none | none | none | none | none | Initial pipeline baseline | none | false |
| 2026-10-02 | dashboard | optional AI Process Improvement Brief (T11, bonus, `Experimental`) | ไม่มี | ปุ่ม Generate + แสดง brief ล่าสุด; persist ใน `runs/ai_briefs.duckdb`; endpoint/key/model จาก env vars; ส่งเฉพาะ aggregate (ไม่มี case_id/owner) | AI_MODEL_SPEC.md bonus scope; ไม่เปลี่ยนสูตร metric; endpoint/auth/quota/threshold ยังเป็น `null` | Exam candidate / implementation owner | false |
| 2026-10-02 | dashboard | dashboard theme (VIZ_DESIGN_SPEC.md Color & Theme) | blue/green/orange palette | Ragnar red `#8F1D2C` + white + warm cream; presentation only | ปรับ visual theme ตามคำขอ; ไม่เปลี่ยน metric, logic, SQL หรือ `reference_date` | Exam candidate / implementation owner | false |
| 2026-10-02 | pipeline_logic | runtime input `reference_date` | `null` (ไม่ได้ระบุใน exam brief) | `2026-10-01` ผ่าน `config/runtime_config.json` / `CPD_REFERENCE_DATE` | project-specific exam assumption ที่ผู้ทำข้อสอบยืนยัน ไม่ใช่ industry standard; ยังเป็น runtime/config input, ไม่ใช้ `CURRENT_DATE`/system date | Exam candidate / implementation owner (project decision) | false |
| 2026-10-02 | pipeline_logic | run-level tables (`run_metadata`, `runtime_inputs`, `approved_*_stage_values`, `quality_results`) | ไม่มี | เพิ่มต่อ run นอก fact/dim grain | implement publication gate และ pending state ของ runtime input; ไม่เปลี่ยน grain/column ของ fact | Exam candidate / implementation owner | false |

เมื่อเปลี่ยน source schema, grain, load strategy, business key, metric transformation หรือ runtime-rule mapping ต้องประเมิน breaking impact ก่อน deploy

## Breaking Changes Log

Breaking change ต้องอ้าง policy ใน `DATA_CONTRACT.md` และใช้ notice period ตาม contract

| effective_date | change_type | changed_item | downstream_impact | migration_plan | historical_treatment | approved_by | notice_completed |
|---|---|---|---|---|---|---|---|
| none | none | none | none | none | none | none | none |

### Breaking Change Procedure

1. identify proposed change
2. compare before/after
3. assess downstream metrics, dashboard, tests and consumers
4. apply `DATA_CONTRACT.md` breaking-change policy and notice period
5. decide historical treatment
6. obtain approval
7. update canonical owner document first
8. update this changelog
9. run validation/CI
10. deploy with rollback plan

ห้ามเปลี่ยนสูตร metric, KPI target หรือ contract silently เพราะจะทำให้ historical comparison และความเชื่อมั่นของผู้ใช้เสียหาย
