# METRIC_SPEC.md

Project: Consequence Process Dashboard
Document ID: metric_spec
Priority: P0
Depends on: KPI_DICTIONARY.md, BUSINESS_GLOSSARY.md, STAKEHOLDERS.md

## Metric Profiles

### `metric_status` Enum

`METRIC_SPEC.md` เป็นเอกสารเจ้าของ `metric_status`:

- `draft` — definition หรือ business rule ที่ metric พึ่งพายังไม่ได้รับ approval ครบ
- `certified` — definition, formula, grain, filters และ business rule ที่เกี่ยวข้องได้รับ approval และผ่าน metric validation
- `deprecated` — metric ที่เลิกใช้แล้วและต้องมี replacement/deprecation path หากเคยถูกใช้งานจริง

> การเปลี่ยนนิยามของ metric ที่เป็น `certified` ถือเป็น breaking change และต้อง reconcile ไปยัง `ANALYTICS_CHANGELOG.md`

### `metric_total_cases`

- **Name:** Total Cases
- **Business Definition:** จำนวน `case` ทั้งหมดใน validated dataset snapshot ภายใต้ filter context ปัจจุบัน
- **Parent KPI:** `consequence_process_completion_rate`
- **Owner:** HR Process Owner
- **Primary Consumer:** HR / Consequence Process Owner
- **Refresh Cadence:** on-demand หลัง CSV ผ่าน validation และโหลดเข้า `DuckDB`
- **metric_status:** `certified`
- **Version:** `v1.0`
- **Action Threshold:** `null`
- **Calibration Owner:** HR Process Owner
- **Certification Basis:** certified 2026-10-02 สำหรับงานสอบนี้ — duplicate-handling policy ระบุใน `DATA_CONTRACT.md` (duplicate `case_id` ถูก reject); golden test MV-001 ผ่าน

### `metric_closed_cases`

- **Name:** Closed Cases
- **Business Definition:** จำนวน `case` ที่ผ่าน business rule ของ `closed case` ใน validated dataset snapshot ภายใต้ filter context ปัจจุบัน
- **Parent KPI:** `consequence_process_completion_rate`
- **Owner:** HR Process Owner
- **Primary Consumer:** HR / Consequence Process Owner
- **Refresh Cadence:** on-demand
- **metric_status:** `certified`
- **Version:** `v1.0`
- **Action Threshold:** `null`
- **Calibration Owner:** HR Process Owner
- **Certification Basis:** certified 2026-10-02 สำหรับงานสอบนี้ — `closed case` = `stage = 'closed'` (resolved ใน `BUSINESS_GLOSSARY.md`); golden test MV-002 ผ่าน

### `metric_open_cases`

- **Name:** Open Cases
- **Business Definition:** จำนวน `case` ที่ผ่าน business rule ของ `open case` ใน validated dataset snapshot ภายใต้ filter context ปัจจุบัน
- **Parent KPI:** `open_case_rate`
- **Owner:** HR Process Owner
- **Primary Consumer:** HR / Consequence Process Owner
- **Refresh Cadence:** on-demand
- **metric_status:** `certified`
- **Version:** `v1.0`
- **Action Threshold:** `null`
- **Calibration Owner:** HR Process Owner
- **Certification Basis:** certified 2026-10-02 สำหรับงานสอบนี้ — `open case` = `stage IN ('reviewing', 'follow_up', 'collecting_info')` (resolved ใน `BUSINESS_GLOSSARY.md`); golden test MV-003 ผ่าน

### `metric_open_cases_by_stage`

- **Name:** Open Cases by Stage
- **Business Definition:** จำนวน `open case` แยกตาม `stage` ภายใต้ filter context ปัจจุบัน
- **Parent KPI:** `open_case_rate`
- **Owner:** HR Process Owner
- **Primary Consumer:** HR / Consequence Process Owner
- **Refresh Cadence:** on-demand
- **metric_status:** `certified`
- **Version:** `v1.0`
- **Action Threshold:** `null`
- **Calibration Owner:** HR Process Owner
- **Certification Basis:** certified 2026-10-02 สำหรับงานสอบนี้ — พึ่ง `open case` rule ที่ approved; golden test MV-004 ผ่าน

### `metric_days_in_current_stage`

- **Name:** Days in Current Stage
- **Business Definition:** จำนวนวันที่ `open case` อยู่ใน `stage` ปัจจุบัน โดยคำนวณจาก `stage_entered_date` ถึง approved `reference_date`
- **Parent KPI:** `open_case_aging`
- **Owner:** HR Operations / Case Management Role
- **Primary Consumer:** HR / Consequence Process Owner
- **Refresh Cadence:** on-demand เมื่อมี approved `reference_date`
- **metric_status:** `certified`
- **Version:** `v1.0`
- **Action Threshold:** `null`
- **Calibration Owner:** HR Process Owner
- **Reference Date:** `2026-10-01` — project-specific exam assumption ที่ผู้ทำข้อสอบยืนยัน (ไม่ใช่ industry standard และไม่ใช่ค่าที่ระบุมาใน exam brief ต้นฉบับ)
- **Reference Date Owner:** Exam Setter / HR Process Owner
- **Certification Basis:** certified 2026-10-02 สำหรับงานสอบนี้ — calendar-day difference ไม่รวมวันเริ่มต้นและ `reference_date = 2026-10-01` approved; golden test MV-005 (row-level) ผ่าน

### `metric_top_3_longest_open_cases`

- **Name:** Top 3 Longest Open Cases
- **Business Definition:** รายการ 3 `open case` ที่มี `metric_days_in_current_stage` สูงสุดภายใต้ filter context เดียวกัน
- **Parent KPI:** `open_case_aging`
- **Owner:** HR Operations / Case Management Role
- **Primary Consumer:** HR / Consequence Process Owner
- **Refresh Cadence:** on-demand
- **metric_status:** `certified`
- **Version:** `v1.0`
- **Action Threshold:** not applicable as a ranking output
- **Calibration Owner:** HR Process Owner / Exam Setter for tie-break rule
- **Certification Basis:** certified 2026-10-02 สำหรับงานสอบนี้ — tie-break `case_id ASC` approved; golden test MV-006 (ids, ordering, days) ผ่าน

## Formula Reference

| Metric | Plain-Language Formula | Mathematical / Pseudocode Formula | Numerator | Denominator |
|---|---|---|---|---|
| `metric_total_cases` | นับจำนวน `case_id` ที่ valid ใน snapshot และ filter context ปัจจุบัน | `COUNT(DISTINCT case_id)` | valid distinct `case_id` | not applicable |
| `metric_closed_cases` | นับ `case_id` ที่ผ่าน approved `closed case` rule | `COUNT(DISTINCT case_id WHERE is_closed = TRUE)` | distinct closed `case_id` | not applicable |
| `metric_open_cases` | นับ `case_id` ที่ผ่าน approved `open case` rule | `COUNT(DISTINCT case_id WHERE is_open = TRUE)` | distinct open `case_id` | not applicable |
| `metric_open_cases_by_stage` | สำหรับแต่ละ `stage` ให้นับ distinct open cases | `COUNT(DISTINCT case_id) GROUP BY stage` after approved open filter | distinct open `case_id` in each `stage` | not applicable |
| `metric_days_in_current_stage` | หาผลต่างระหว่าง approved `reference_date` และ `stage_entered_date` ตาม calendar-day difference (ไม่รวมวันเริ่มต้น) ที่ approved | `DATE_DIFF('day', stage_entered_date, reference_date)` | not applicable | not applicable |
| `metric_top_3_longest_open_cases` | filter เฉพาะ open cases → เรียง `days_in_current_stage` จากมากไปน้อย → ใช้ tie-break `case_id ASC` → เลือก 3 รายการแรก | `TOP 3 ORDER BY metric_days_in_current_stage DESC, case_id ASC` | ranked open cases | not applicable |

### Derived KPI Formula Links

สูตรต่อไปนี้อยู่เพื่อเชื่อม metric กับ parent KPI; คำนวณจาก metric ที่ `certified` ข้างต้น (open/closed rule ได้รับ approval แล้ว):

- `consequence_process_completion_rate = metric_closed_cases / metric_total_cases`
- `open_case_rate = metric_open_cases / metric_total_cases`

หาก `metric_total_cases = 0` ให้ผล rate เป็น `null` และไม่หารด้วยศูนย์

## Grain and Filter Matrix

| Metric | Grain | Required Filters | Optional Filters | Segment Breakdowns |
|---|---|---|---|---|
| `metric_total_cases` | `1 validated dataset snapshot × 1 filter context` | valid record policy from future `DATA_CONTRACT.md` | `case_domain` | `case_domain`, `response_type`, `stage` |
| `metric_closed_cases` | `1 validated dataset snapshot × 1 filter context` | approved `closed case` rule | `case_domain` | `case_domain`, `response_type` |
| `metric_open_cases` | `1 validated dataset snapshot × 1 filter context` | approved `open case` rule | `case_domain` | `case_domain`, `response_type`, `stage` |
| `metric_open_cases_by_stage` | `1 stage × 1 validated dataset snapshot` | approved `open case` rule | `case_domain` | `stage`, `case_domain`, `response_type` |
| `metric_days_in_current_stage` | `1 case × 1 approved reference_date` | approved `open case` rule; valid `stage_entered_date`; approved day-count rule | `case_domain` | `case_domain`, `response_type`, `stage`, `owner` |
| `metric_top_3_longest_open_cases` | `1 ranked case × 1 approved reference_date` | approved `open case` rule; approved day-count rule; approved tie-break rule | `case_domain` | `case_domain`, `response_type`, `stage`, `owner` |

### Filter Semantics

- Dashboard requirement บังคับให้ `case_domain` เป็น user-selectable filter ระหว่าง behavior/performance
- `response_type`, `stage` และ `owner` เป็น dimensions ที่รองรับการวิเคราะห์ แต่ไม่ได้ถูกกำหนดเป็น mandatory dashboard filters ในโจทย์
- filter context เดียวกันต้องถูกใช้กับ KPI cards, stage view และ Top 3 เพื่อป้องกันการเปรียบเทียบคนละ population
- ห้ามใช้ system date เป็น implicit filter หรือ time basis แทน `reference_date`

## Action Thresholds

ยังไม่มี warning/critical threshold ที่ได้รับการ calibrate จาก HR Process Owner จึงห้ามกำหนดค่าตัวเลขขึ้นเอง

| Metric | Warning Threshold | Critical Threshold | Required Action | Responsible Team | Calibration Owner |
|---|---|---|---|---|---|
| `metric_total_cases` | `null` | `null` | ตรวจความผิดปกติของ volume เมื่อมี threshold ที่อนุมัติแล้ว | HR Process Owner / Data Owner | HR Process Owner |
| `metric_closed_cases` | `null` | `null` | ตรวจ completion trend เมื่อมี threshold ที่อนุมัติแล้ว | HR Process Owner | HR Process Owner |
| `metric_open_cases` | `null` | `null` | ตรวจ backlog และ `stage` distribution เมื่อมี threshold ที่อนุมัติแล้ว | HR Process Owner | HR Process Owner |
| `metric_open_cases_by_stage` | `null` | `null` | ตรวจ bottleneck ของขั้นตอนเมื่อมี threshold ที่อนุมัติแล้ว | HR Process Owner / HR Operations | HR Process Owner |
| `metric_days_in_current_stage` | `null` | `null` | ตรวจ case aging และ process follow-up เมื่อมี threshold ที่อนุมัติแล้ว | HR Operations / Case Management Role | HR Process Owner |
| `metric_top_3_longest_open_cases` | not applicable | not applicable | ใช้เป็น ranked review list; ไม่ใช้ threshold | HR Operations / Case Management Role | not applicable |

### Approved Business Rules (project-specific, 2026-10-02)

กติกาต่อไปนี้เป็น project-specific approved business rule สำหรับงานสอบนี้ (ไม่ใช่ industry standard); `reference_date` เป็น project-specific exam assumption ที่ไม่ได้ระบุใน exam brief ต้นฉบับ และยังต้องส่งเป็น runtime/config input (ไม่ hard-code, ไม่ใช้ system date)

- `closed case`: `stage = 'closed'`
- `open case`: `stage IN ('reviewing', 'follow_up', 'collecting_info')`
- `reference_date`: `2026-10-01`
- day count: `DATE_DIFF('day', stage_entered_date, reference_date)` (calendar-day, ไม่รวมวันเริ่มต้น)
- Top 3 ordering: `metric_days_in_current_stage DESC, case_id ASC`

### Certification Blockers

blocker ที่เคยมีทั้งหมดถูกปิดแล้ว ณ 2026-10-02:

1. ~~HR Process Owner อนุมัติ business mapping ของ `open case` และ `closed case`~~ — resolved
2. ~~Exam Setter / HR Process Owner ให้ค่า `reference_date`~~ — resolved: `2026-10-01` (project-specific exam assumption)
3. ~~อนุมัติ day-count convention~~ — resolved: calendar-day difference
4. ~~อนุมัติ deterministic tie-break สำหรับ Top 3~~ — resolved: `case_id ASC`
5. ~~`DATA_CONTRACT.md` ระบุ duplicate/required-field policy~~ — resolved (reject duplicate `case_id`, required-field rules)
6. ~~metric validation test ผ่านตาม `TESTING_STRATEGY.md`~~ — resolved: MV-001..007 ผ่าน (`tests/test_metrics_golden.py`, `tests/test_integration.py`)

Metric ที่ยัง `draft`: ไม่มี. การเปลี่ยนนิยามของ metric ที่ `certified` จากนี้ถือเป็น breaking change ตามกติกาด้านบน

ไม่มี action threshold ตัวใดถูกสร้างจาก mock dataset และไม่มีตัวเลข mock ถูกใช้เป็นมาตรฐาน
