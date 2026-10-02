# TESTING_STRATEGY.md

Project: Consequence Process Dashboard  
Document ID: testing_strategy  
Priority: P1  
Depends on: PIPELINE_SPEC.md, DATA_QUALITY.md, METRIC_LOGIC.md

## Unit Tests (dbt / SQL)

เป้าหมายของ unit tests คือพิสูจน์ว่า SQL transformation และ model constraints ทำงานตามที่เขียน
ไม่ใช่พิสูจน์ว่าตัวเลข business metric ถูกต้องตามความจริงทั้งหมด ซึ่งเป็นหน้าที่ของ Metric Validation Tests

### Unit Test Coverage

ทุก fact/dimension/model ที่ core pipeline ใช้ต้องมีอย่างน้อยหนึ่ง test และทุก rule ใน `DATA_QUALITY.md`
ต้องมี test counterpart หรือ assertion ที่รันได้ใน CI

| Test ID | Target | Assertion | Expected Result | Deployment Effect |
|---|---|---|---|---|
| UT-001 | `stg_consequence_case` | required columns exist | all required columns present | block |
| UT-002 | `stg_consequence_case.case_id` | no duplicate `case_id` | 0 duplicate groups | block |
| UT-003 | required source fields | no null / blank required values | 0 failing rows | block |
| UT-004 | categorical source fields | values conform to active contract | 0 failing rows | block |
| UT-005 | `stage_entered_date` | parses as DATE | 0 parse failures | block |
| UT-006 | `fact_consequence_case` | business grain preserved | 1 row per `case_id` per snapshot | block |
| UT-007 | `fact_consequence_case → dim_case_domain` | FK resolves | 0 orphan rows | block |
| UT-008 | `fact_consequence_case → dim_response_type` | FK resolves | 0 orphan rows | block |
| UT-009 | `fact_consequence_case → dim_stage` | FK resolves | 0 orphan rows | block |
| UT-010 | `fact_consequence_case → dim_owner` | FK resolves | 0 orphan rows | block |
| UT-011 | `mart_consequence_case_aging` | no negative aging | 0 rows | block |
| UT-012 | schema drift | actual schema matches active contract | no breaking drift | block |

### Example SQL Assertions

#### Duplicate `case_id`

```sql
SELECT case_id
FROM stg_consequence_case
GROUP BY case_id
HAVING COUNT(*) > 1;
```

Expected result: `0 rows`

#### Fact grain

```sql
SELECT case_id
FROM fact_consequence_case
GROUP BY case_id
HAVING COUNT(*) > 1;
```

Expected result: `0 rows`

#### Orphan `stage_key`

```sql
SELECT f.case_id
FROM fact_consequence_case AS f
LEFT JOIN dim_stage AS d
  ON f.stage_key = d.stage_key
WHERE d.stage_key IS NULL;
```

Expected result: `0 rows`

### Coverage Target

- **Numeric coverage target:** `null`
- **Calibration Owner:** Analytics Implementation Owner / Exam Setter
- **Rationale:** template กำหนดให้ coverage expectation ต้องเป็นตัวเลขพร้อมเหตุผล หรือ `null` พร้อม owner;
  โจทย์ไม่ได้กำหนด coverage percentage จึงไม่สร้างค่าเอง
- **Minimum structural expectation:** ทุก quality rule ใน `DATA_QUALITY.md`, ทุก fact table และทุก metric SQL
  path ที่ deploy ต้องมี automated test อย่างน้อยหนึ่งรายการ

## Integration Tests

Integration tests ต้องพิสูจน์ว่า pipeline ทั้ง flow ทำงานร่วมกันจริงตั้งแต่ CSV ถึง semantic/mart outputs

### IT-001 — End-to-End Valid CSV Run

**Input:** validated mock CSV  
**Steps:**
1. run `pl_ingest_consequence_csv`
2. build staging
3. run `pl_build_consequence_model`
4. build fact/dim tables
5. run `pl_build_consequence_metrics` สำหรับ metric ที่มี approved runtime inputs

**Expected:**
- pipeline ไม่ error
- row count ที่ semantic fact สอดคล้องกับ validated source grain
- dimensions resolve ครบ
- metric marts ที่ dependency พร้อมถูกสร้างสำเร็จ

### IT-002 — Invalid Schema Must Stop Pipeline

**Input:** fixture ที่ลบ required column หนึ่งตัวออก  
**Expected:**
- ingestion fails
- semantic model ไม่ถูก rebuild จาก invalid input
- previous valid published state ยังคงใช้งานได้

### IT-003 — Invalid Date Must Stop Aging Path

**Input:** fixture ที่ `stage_entered_date` parse ไม่ได้  
**Expected:**
- quality validation fail
- aging mart และ Top 3 ไม่ publish
- error reason ถูก surface ชัดเจน

### IT-004 — Idempotency

รัน validated input เดิม **2 ครั้งติดกัน**

Expected:
- `stg_consequence_case` content สำหรับ snapshot เดิมไม่เพิ่ม duplicate
- `fact_consequence_case` row count ไม่เพิ่มจาก rerun
- dimension rows ไม่เพิ่มซ้ำจาก business key เดิม
- metric outputs สำหรับ input + runtime inputs ชุดเดียวกันต้องเท่ากันทั้งสอง run

### IT-005 — Filter Propagation

รัน metric layer โดย:
- no `case_domain` filter
- `case_domain = behavior`
- `case_domain = performance`

Expected:
- filtered population เป็น subset ของ unfiltered population
- metric cards, stage aggregation และ Top 3 ใช้ filter context เดียวกัน
- filter หนึ่ง domain ต้องไม่ปะปนอีก domain

### IT-006 — Runtime Input Guard

กรณี `approved_reference_date = null` หรือ open/closed business mapping ยังไม่ approved

Expected:
- metric ที่ไม่ต้องพึ่ง runtime input เช่น `metric_total_cases` ยังรันได้
- aging/open/closed dependent metrics ต้องไม่ substitute default เอง
- ต้องไม่ใช้ `CURRENT_DATE`
- status/output ต้องบอกว่า dependency ยังไม่พร้อม

## Metric Validation Tests

Metric validation tests พิสูจน์ว่า “ตัวเลขถูกต้อง” โดยเทียบ output จาก `METRIC_LOGIC.md`
กับ known expected result ไม่ใช่แค่พิสูจน์ว่า SQL execute สำเร็จ

### Golden Dataset Requirement

ต้องสร้าง fixture ขนาดเล็กที่คำนวณผลด้วยมือได้แน่นอน

**Golden dataset:** `tests/conftest.py` (`GOLDEN_ROWS`, 10 cases) คำนวณมือด้วย `reference_date = 2026-10-01`; expected outputs อยู่ใน `tests/test_metrics_golden.py`
(total 10 / closed 2 / open 8; open by stage collecting_info 2, follow_up 3, reviewing 3; Top 3 = G07 (90), G02 (60), G03 (60); behavior Top 3 = G02, G01, G10; performance Top 3 = G07, G03, G09)
**Calibration / Approval Owner:** HR Process Owner / Exam Setter (approved 2026-10-02, project-specific)

metrics ที่พึ่ง `open/closed` หรือ aging ถูก certify เมื่อมี (ครบแล้ว):
- approved open/closed mapping (`closed` = `stage = 'closed'`; `open` = `reviewing`/`follow_up`/`collecting_info`)
- approved `reference_date` = `2026-10-01` (project-specific exam assumption; golden tests ใช้ค่านี้)
- approved day-count convention (calendar-day difference)
- approved Top 3 tie-break (`case_id ASC`)

จึงจะสามารถบันทึก expected outputs แบบ authoritative ได้

### Required Metric Validation Cases

| Test ID | Metric | Validation |
|---|---|---|
| MV-001 | `metric_total_cases` | เทียบ `COUNT(DISTINCT case_id)` กับ manual expected value |
| MV-002 | `metric_closed_cases` | เทียบกับ manual classification หลัง closed rule approved |
| MV-003 | `metric_open_cases` | เทียบกับ manual classification หลัง open rule approved |
| MV-004 | `metric_open_cases_by_stage` | เทียบ stage-by-stage counts กับ manual expected table |
| MV-005 | `metric_days_in_current_stage` | เทียบ row-level date difference กับ manual expected days |
| MV-006 | `metric_top_3_longest_open_cases` | เทียบทั้ง case IDs, ordering และ day values กับ manual ranking |
| MV-007 | KPI rate derivations | `closed / total` และ `open / total`; total=0 ต้องได้ `null` |

### Row-Level vs Aggregate Reconciliation

ต้องตรวจทั้งสองระดับ:

1. **Row-level reconciliation**  
   เลือก sample cases จาก golden dataset แล้วเทียบ:
   - `stage`
   - `stage_entered_date`
   - `case_domain`
   - expected open/closed classification
   - expected `days_in_current_stage`

2. **Aggregate reconciliation**  
   รวม row-level expected values แล้วเทียบกับ:
   - total
   - open
   - closed
   - stage counts

ห้ามยอมรับ aggregate อย่างเดียว เพราะความผิดพลาดคนละทิศทางอาจหักล้างกันแล้วทำให้ยอดรวมดูถูก

### Reconciliation Invariant

เมื่อ approved business rule กำหนดให้ทุก case อยู่ใน open หรือ closed เพียงสถานะเดียว:

```text
metric_total_cases = metric_open_cases + metric_closed_cases
```

Invariant นี้เป็น certified requirement เพราะ open/closed mapping ได้รับ approval (2026-10-02) และถูกตรวจใน MV-007

## Dashboard Acceptance Tests

`DASHBOARD_SPEC.md` ยังไม่ถูกสร้าง ณ เวอร์ชันนี้
ดังนั้น acceptance tests ชุดนี้อ้างจาก stakeholder needs + `METRIC_SPEC.md`
และต้อง reconcile อีกครั้งหลังสร้าง `DASHBOARD_SPEC.md`

### DA-001 — Core KPI Cards Render

Dashboard ต้องแสดง:
- Total Cases
- Closed Cases
- Open Cases

Acceptance:
- component render สำเร็จ
- ค่าที่แสดงตรงกับ metric mart/query output ของ filter context เดียวกัน

### DA-002 — Cases by Stage Renders

Acceptance:
- stage visualization render สำเร็จ
- counts ตรงกับ `metric_open_cases_by_stage`
- ไม่คำนวณ metric ซ้ำใน dashboard code

### DA-003 — Behavior / Performance Filter

Acceptance:
- user เลือก `behavior` หรือ `performance` ได้
- KPI cards, stage view, open-case table และ Top 3 เปลี่ยนพร้อมกัน
- clear/reset filter กลับสู่ unfiltered state ได้

### DA-004 — Open Case Aging Display

เมื่อ approved `reference_date` พร้อม:
- open-case rows แสดง `days_in_current_stage`
- day values ตรงกับ metric layer
- กรณี runtime input ยังไม่พร้อม ต้องแสดง unavailable/pending state ไม่ใช้ system date แทน

### DA-005 — Top 3 Longest Cases

Acceptance:
- แสดงไม่เกิน 3 cases
- ordering ตรงกับ `METRIC_LOGIC.md`
- tie-break ต้องตรง approved rule
- ค่า case ID / stage / owner / days ตรงกับ mart output

### DA-006 — Validation Failure UX

เมื่อ upload CSV ที่ผิด contract:
- user เห็น validation failure
- business dashboard ไม่ publish output จาก invalid run
- previous valid state ไม่ถูก overwrite แบบ partial

### DA-007 — Deployment Smoke Test

หลัง Coolify deploy:
- application endpoint เปิดได้
- dashboard page render ได้
- DuckDB data path อ่านได้
- core query หนึ่งชุดรันสำเร็จ
- ไม่มี secret แสดงใน UI/log output ที่ใช้ตรวจ smoke test

## Test Automation and CI

### Test Execution Order

```text
schema / contract checks
→ SQL unit tests
→ data-quality assertions
→ pipeline integration tests
→ metric validation tests
→ dashboard acceptance / smoke tests
→ deployment
```

### Blocking Gates

ต่อไปนี้ **block deployment**:
- required schema/unit test fail
- `rule_severity = error` quality rule fail
- fact/dimension referential integrity fail
- idempotency test fail
- metric validation fail สำหรับ metric ที่จะ publish
- dashboard core acceptance fail
- deployment smoke test fail
- secret exposed in committed source or test output

### Warn-Only Gates

ต่อไปนี้เป็น **warn-only** จนกว่าจะ calibrate:
- anomaly rules ที่ threshold = `null`
- freshness thresholds ที่ยังไม่ calibrate
- optional AI bonus tests เมื่อ core deployment ไม่พึ่ง AI feature

Warn-only ต้องไม่ถูกแสดงเป็น `pass`; ควรแสดงสถานะ `not_calibrated` หรือ equivalent

### CI Trigger

เมื่อ repository/CI platform ถูกยืนยันแล้ว ให้รัน test suite อย่างน้อยเมื่อ:
- push/merge request ที่กระทบ pipeline/model/metric/dashboard code
- ก่อน production deployment
- manual release validation สำหรับ exam submission

**Exact CI platform / workflow syntax:** `null`  
**Calibration Owner:** Company Repository Administrator / Candidate

### Deployment Rule

```text
if blocking_tests_pass:
    allow_deploy
else:
    block_deploy
```

ห้าม deploy โดย override failing blocking tests เพื่อให้ทันเวลา 120 นาที

### Evidence for Exam Submission

เก็บหลักฐานอย่างน้อย:
- test command ที่ใช้
- pass/fail summary
- row counts ที่สำคัญ
- metric validation result
- deployment smoke-test result
- deployed endpoint reference
- commit/revision identifier

หลักฐานเหล่านี้ช่วยพิสูจน์เงื่อนไขโจทย์ว่า “มี Test หรือ Validation ผ่าน”
แทนการอ้างเพียงว่า application เปิดได้

### Optional AI Bonus Test Boundary

ถ้าทำ AI Process Improvement Brief เพิ่มภายหลัง ต้องมี test แยกสำหรับ:
- API failure handling
- response persistence
- retrieval/display บน app
- aggregate-only input contract
- no automated HR disciplinary decision

AI bonus failure ต้องไม่ทำให้ core analytics dashboard fail เว้นแต่ product owner เปลี่ยน scope ให้ AI เป็น mandatory feature
