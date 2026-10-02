# DATA_QUALITY.md

Project: Consequence Process Dashboard  
Document ID: data_quality  
Priority: P0  
Depends on: DATA_MODEL_SPEC.md, PIPELINE_SPEC.md

## Null and Completeness Checks

### `rule_severity` Enum

`DATA_QUALITY.md` เป็นเอกสารเจ้าของ `rule_severity`

- `error` — block pipeline และห้าม publish downstream output
- `warning` — แจ้งเตือนแต่ pipeline สามารถรันต่อได้

### DQ-001 — Required Fields Must Be Non-null

- **Applies to:** `fact_consequence_case`
- **Rule Type:** null check
- **Expected Behavior:** fields ที่จำเป็นต่อ grain และ metrics ต้องไม่เป็น null
- **rule_severity:** `error`
- **Action on Failure:** block `pl_build_consequence_metrics`, เก็บ validation evidence และแจ้ง Analytics Implementation Owner

```sql
SELECT COUNT(*) AS failing_rows
FROM fact_consequence_case
WHERE case_id IS NULL
   OR case_domain_key IS NULL
   OR response_type_key IS NULL
   OR stage_key IS NULL
   OR stage_entered_date IS NULL
   OR owner_key IS NULL;
```

**Pass condition:** `failing_rows = 0`

### DQ-002 — Source Snapshot Completeness

- **Applies to:** `stg_consequence_case`
- **Rule Type:** completeness
- **Expected Behavior:** completeness target ต้องอิงค่าที่ calibrate จากข้อมูลจริง
- **Completeness Threshold:** `null`
- **Calibration Owner:** HR Data Owner / Exam Setter
- **rule_severity:** `warning` จนกว่าจะมี threshold ที่อนุมัติ
- **Action on Failure:** เมื่อมี threshold จริง ให้ alert owner และห้ามยกระดับเป็น blocking rule โดยไม่มี approval

```sql
SELECT
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (
        WHERE case_id IS NOT NULL
          AND case_domain IS NOT NULL
          AND response_type IS NOT NULL
          AND stage IS NOT NULL
          AND stage_entered_date IS NOT NULL
          AND owner IS NOT NULL
    ) AS complete_rows
FROM stg_consequence_case;
```

### DQ-003 — Duplicate `case_id` Must Not Exist

- **Applies to:** `stg_consequence_case.case_id`
- **Rule Type:** uniqueness / completeness protection
- **Expected Behavior:** grain `1 case × 1 validated dataset snapshot` ต้องไม่ถูกทำลายด้วย duplicate business key
- **rule_severity:** `error`
- **Action on Failure:** block semantic-model build และให้ producer แก้ source snapshot

```sql
SELECT case_id, COUNT(*) AS row_count
FROM stg_consequence_case
GROUP BY case_id
HAVING COUNT(*) > 1;
```

**Pass condition:** `0 rows`

## Range and Validity Checks

### DQ-004 — `stage_entered_date` Must Be Valid for Approved `reference_date`

- **Applies to:** `fact_consequence_case.stage_entered_date`
- **Rule Type:** range / validity
- **Expected Behavior:** เมื่อมี approved `reference_date`, วันที่เข้า stage ต้องไม่อยู่หลังวันอ้างอิง
- **Approved `reference_date`:** `2026-10-01` (project-specific exam assumption)
- **rule_severity:** `error`
- **Action on Failure:** block aging metrics และ Top 3 output; ห้ามแทนค่าด้วย zero

```sql
SELECT
    case_id,
    stage_entered_date
FROM fact_consequence_case
WHERE :approved_reference_date IS NOT NULL
  AND stage_entered_date > CAST(:approved_reference_date AS DATE);
```

**Pass condition:** `0 rows`

### DQ-005 — Contracted Categorical Values Must Be Recognized

- **Applies to:** `stg_consequence_case.case_domain`, `response_type`, `stage`
- **Rule Type:** validity
- **Expected Behavior:** source values ต้องอยู่ใน source-shape contract version ปัจจุบัน
- **rule_severity:** `error`
- **Action on Failure:** classify เป็น schema/contract drift, block ingestion และแจ้ง HR Data Owner / Contract Owner

```sql
SELECT *
FROM stg_consequence_case
WHERE case_domain NOT IN ('behavior', 'performance')
   OR response_type NOT IN ('recognition', 'improvement')
   OR stage NOT IN ('closed', 'reviewing', 'follow_up', 'collecting_info');
```

**Pass condition:** `0 rows`

> ค่าเหล่านี้เป็น source contract values จาก `DATA_CONTRACT.md` ไม่ใช่ enum registry ของ template

### DQ-006 — `case_id` and `owner` Must Be Non-empty Strings

- **Applies to:** `stg_consequence_case.case_id`, `owner`
- **Rule Type:** validity
- **Expected Behavior:** identifier ห้ามเป็น blank หลัง trim
- **rule_severity:** `error`
- **Action on Failure:** reject affected source rows and block downstream publish until corrected

```sql
SELECT *
FROM stg_consequence_case
WHERE TRIM(case_id) = ''
   OR TRIM(owner) = '';
```

**Pass condition:** `0 rows`

### DQ-007 — Upstream Schema Drift Detection

- **Applies to:** incoming CSV schema
- **Rule Type:** schema validity
- **Expected Behavior:** required fields ต้องครบ และ unexpected change ต้องถูก classify ตาม `DATA_CONTRACT.md`
- **rule_severity:** `error` สำหรับ missing/renamed/type-breaking field; additive extra field ต้องผ่าน contract review ก่อนใช้
- **Action on Failure:** stop ingestion, กันข้อมูลไม่ให้เข้า semantic model และแจ้ง Contract Owner

DuckDB/Python implementation ต้องเปรียบเทียบ actual header set กับ:

```text
case_id
case_domain
response_type
stage
stage_entered_date
owner
```

SQL assertion หลัง staging:

```sql
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'stg_consequence_case'
ORDER BY column_name;
```

Pipeline ต้อง compare ผลลัพธ์กับ expected contract fields ก่อน publish downstream

## Referential Integrity Checks

ทุก FK จาก `fact_consequence_case` ต้องมี SQL assertion แยกตามคู่ relationship

### DQ-008 — `case_domain_key` Must Resolve

- **rule_severity:** `error`
- **Action on Failure:** block pipeline และ rebuild/reconcile dimension mapping

```sql
SELECT f.case_id
FROM fact_consequence_case AS f
LEFT JOIN dim_case_domain AS d
  ON f.case_domain_key = d.case_domain_key
WHERE d.case_domain_key IS NULL;
```

### DQ-009 — `response_type_key` Must Resolve

- **rule_severity:** `error`
- **Action on Failure:** block pipeline และ rebuild/reconcile dimension mapping

```sql
SELECT f.case_id
FROM fact_consequence_case AS f
LEFT JOIN dim_response_type AS d
  ON f.response_type_key = d.response_type_key
WHERE d.response_type_key IS NULL;
```

### DQ-010 — `stage_key` Must Resolve

- **rule_severity:** `error`
- **Action on Failure:** block pipeline และ rebuild/reconcile dimension mapping

```sql
SELECT f.case_id
FROM fact_consequence_case AS f
LEFT JOIN dim_stage AS d
  ON f.stage_key = d.stage_key
WHERE d.stage_key IS NULL;
```

### DQ-011 — `owner_key` Must Resolve

- **rule_severity:** `error`
- **Action on Failure:** block pipeline และ rebuild/reconcile dimension mapping

```sql
SELECT f.case_id
FROM fact_consequence_case AS f
LEFT JOIN dim_owner AS d
  ON f.owner_key = d.owner_key
WHERE d.owner_key IS NULL;
```

**Pass condition ของ DQ-008 ถึง DQ-011:** ทุก query คืน `0 rows`

## Anomaly Detection Rules

Anomaly threshold ต้องมาจาก observed history ที่มี source หรือเป็น `null` พร้อม calibration owner ห้ามใช้ตัวเลขกลม ๆ จากการคาดเดา

### DQ-012 — Unexpected Total Row Volume

- **Applies to:** `stg_consequence_case`
- **Rule Type:** anomaly
- **Observed History Source:** ยังไม่มี historical run series; มีเพียง mock snapshot ปัจจุบัน
- **Lower Bound:** `null`
- **Upper Bound:** `null`
- **Calibration Owner:** HR Data Owner / Analytics Implementation Owner
- **rule_severity:** `warning`
- **Action on Failure:** เมื่อ calibrate แล้วให้ alert owner และตรวจ source delivery ก่อน publish; การยกระดับเป็น `error` ต้องมี approval

```sql
SELECT COUNT(*) AS current_row_count
FROM stg_consequence_case;
```

### DQ-013 — Unexpected Stage Distribution Shift

- **Applies to:** `stg_consequence_case.stage`
- **Rule Type:** anomaly
- **Threshold:** `null`
- **Calibration Owner:** HR Process Owner / Analytics Implementation Owner
- **Historical Source Required:** validated historical snapshots หลายรอบ
- **rule_severity:** `warning`
- **Action on Failure:** alert ให้ HR Process Owner ตรวจว่าการเปลี่ยน distribution เป็น process change จริงหรือ data issue

```sql
SELECT
    stage,
    COUNT(*) AS row_count,
    COUNT(*)::DOUBLE / NULLIF(SUM(COUNT(*)) OVER (), 0) AS stage_share
FROM stg_consequence_case
GROUP BY stage
ORDER BY stage;
```

### DQ-014 — Unexpected `case_domain` Mix Shift

- **Applies to:** `stg_consequence_case.case_domain`
- **Rule Type:** anomaly
- **Threshold:** `null`
- **Calibration Owner:** HR Process Owner
- **Historical Source Required:** validated historical snapshots
- **rule_severity:** `warning`
- **Action on Failure:** alert only; ห้ามตีความว่าเป็น process deterioration โดยอัตโนมัติ

```sql
SELECT
    case_domain,
    COUNT(*) AS row_count,
    COUNT(*)::DOUBLE / NULLIF(SUM(COUNT(*)) OVER (), 0) AS domain_share
FROM stg_consequence_case
GROUP BY case_domain
ORDER BY case_domain;
```

### DQ-015 — Negative Aging Must Never Occur After Approval Inputs Exist

- **Applies to:** `mart_consequence_case_aging`
- **Rule Type:** anomaly / correctness guard
- **Expected Behavior:** `metric_days_in_current_stage >= 0`
- **rule_severity:** `error`
- **Action on Failure:** block aging mart และ dashboard sections that consume it

```sql
SELECT *
FROM mart_consequence_case_aging
WHERE metric_days_in_current_stage < 0;
```

**Pass condition:** `0 rows`

## Quality Dashboards

### Quality Monitoring Scope

Quality dashboard สำหรับงานนี้ต้องแสดงสถานะของ rules โดยไม่ปนกับ business dashboard หลัก

| Monitor | Source | Display | Owner |
|---|---|---|---|
| latest pipeline quality status | results of DQ-001..DQ-015 | pass / fail per rule | Analytics Implementation Owner |
| failing row count | quality-rule outputs | count by rule | Analytics Implementation Owner |
| duplicate `case_id` count | DQ-003 | count | HR Data Owner |
| invalid categorical rows | DQ-005 | count by field | HR Data Owner |
| referential-integrity failures | DQ-008..DQ-011 | count by relationship | Analytics Implementation Owner |
| row volume history | DQ-012 | trend | HR Data Owner |
| stage distribution history | DQ-013 | trend | HR Process Owner |
| domain mix history | DQ-014 | trend | HR Process Owner |

### Quality Status Logic

- rule ที่มี `rule_severity = error` และ fail → pipeline status = blocked
- rule ที่มี `rule_severity = warning` และ fail → pipeline status = warning; pipeline อาจรันต่อ
- anomaly rule ที่ threshold ยังเป็น `null` → แสดง `not_calibrated`, ไม่แสดง pass/fail ปลอม
- dashboard ต้องแสดง timestamp/run identifier ของ validation result
- quality status ไม่เท่ากับ metric correctness; metric correctness จะถูกพิสูจน์ต่อใน `TESTING_STRATEGY.md`

### Publication Gate

Core business dashboard publish ได้เมื่อ:
1. DQ rules ที่เป็น `error` ผ่านทั้งหมด
2. source schema ตรงกับ active `DATA_CONTRACT.md`
3. fact/dimension model ไม่มี orphan FK
4. aging-related output ใช้ approved `reference_date` (`2026-10-01`) และ business rules ที่อนุมัติแล้ว; หาก runtime input ขาดหรือ DQ-004/DQ-015 fail ให้ block เฉพาะ aging/Top 3 และแสดง pending/unavailable
5. warning/anomaly ที่ยังไม่ calibrate ต้องถูกแสดงเป็น `not_calibrated` ไม่ใช่ silently pass
