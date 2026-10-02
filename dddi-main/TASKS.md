# TASKS.md

Project: Consequence Process Dashboard  
Document ID: tasks  
Priority: P0  
Depends on: KPI_DICTIONARY.md, PIPELINE_SPEC.md

## Task Breakdown

### `work_item_status` Enum

`TASKS.md` เป็นเอกสารเจ้าของ `work_item_status`

- `not started`
- `in progress`
- `done`

| ID | Task | Supports | `work_item_status` |
|---|---|---|---|
| T01 | สร้าง CSV schema/type validation | core ingestion | `not started` |
| T02 | สร้าง DuckDB staging + fact/dimension model | all core KPIs/metrics | `not started` |
| T03 | implement metric views/marts | completion/open/aging KPIs | `not started` |
| T04 | implement Behavior/Performance filter | stakeholder P1 need | `not started` |
| T05 | implement KPI cards + stage bar + aging table + Top 3 | all core dashboard outputs | `not started` |
| T06 | implement automated quality/unit/integration tests | deployment gate | `not started` |
| T07 | create deterministic validation fixture / golden dataset after business rules approved | metric correctness | `not started` |
| T08 | configure repository + CI command | submission requirement | `not started` |
| T09 | configure Coolify deployment + smoke test | submission requirement | `not started` |
| T10 | reconcile unresolved `reference_date`, open/closed mapping, day-count and Top-3 tie-break | metric certification | `done` |
| T11 | optional AI Process Improvement Brief endpoint/persistence/UI | bonus | `done` |

## Task Sequence and Dependencies

```text
T01
→ T02
→ T03
→ T04 + T05
→ T06 + T07
→ T08
→ T09

T10 must complete before certifying dependent metrics
T11 starts only after core dashboard/test/deploy path is stable
```

Dependency rules:
- T02 ห้ามเริ่ม publish model ก่อน T01 ผ่าน
- T03 ใช้ formula จาก `METRIC_LOGIC.md` เท่านั้น
- T05 ใช้ chart type/interaction จาก `VIZ_DESIGN_SPEC.md`
- T07 ต้องรอ approved business rules ไม่สร้าง expected values สมมติ
- T09 ห้าม deploy เมื่อ blocking tests ใน `TESTING_STRATEGY.md` fail
- T11 ไม่ block core submission เว้นแต่ scope ถูกเปลี่ยนอย่างเป็นทางการ

## Definition of Done

งาน core ถือว่า done เมื่อ:
- CSV ที่ valid ingest ได้ และ invalid input ถูก reject/report อย่างชัดเจน
- DuckDB model รักษา grain และ FK integrity
- dashboard แสดง Total / Closed / Open, stage view, case aging และ Top 3 ตาม metric layer
- `case_domain` filter sync core components
- ไม่มีสูตร metric ซ้ำใน dashboard
- `reference_date` ไม่ถูกแทนด้วย system date
- automated blocking tests ผ่าน
- rerun input เดิมไม่สร้าง duplicate
- code push ไป company repository
- Coolify endpoint เปิดได้และ smoke test ผ่าน
- secret/token ไม่ถูก commit
- unresolved calibration values ไม่ถูก hard-code

**AGENTS.md reconciliation completed:** Definition of Done นี้ต้องใช้ร่วมกับ `AGENTS.md` โดยเฉพาะกติกา metric ownership, ห้ามใช้ `CURRENT_DATE` แทน approved `reference_date`, ห้าม hard-code threshold, ต้อง query ผ่าน semantic layer, ต้องไม่ commit secrets และ blocking tests ห้ามถูก override

## Assignments and Estimates

เนื่องจากเป็นข้อสอบเดี่ยว ให้ assignment ใช้ role แทนชื่อบุคคล

| Task Group | Assignment | Estimate |
|---|---|---|
| T01–T07 core implementation/test | Candidate / Analytics Implementation Owner | `null` |
| T08 repository/CI | Candidate + Company Repository Administrator | `null` |
| T09 deployment | Candidate + Company Platform Owner | `null` |
| T10 business-rule approval | HR Process Owner / Exam Setter | `null` |
| T11 AI bonus | Candidate + Company AI Platform Owner | `null` |

Estimate ราย task เป็น `null` เพราะ template/โจทย์ให้เพียง delivery window รวม 120 นาที แต่ไม่ได้ให้ calibration สำหรับ effort ต่อ task การกำหนดตัวเลขแยกโดยเดาจะทำให้แผนดูแม่นเกินหลักฐาน
