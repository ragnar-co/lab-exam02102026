# RUNBOOK.md

Project: Consequence Process Dashboard  
Document ID: runbook  
Priority: P0  
Depends on: PIPELINE_SPEC.md, SLA_FRESHNESS.md, DATA_QUALITY.md

## Common Failure Scenarios

### `incident_severity` Enum

`RUNBOOK.md` เป็นเอกสารเจ้าของ `incident_severity`

- `SEV1`
- `SEV2`
- `SEV3`

> ห้ามใช้ `P0/P1/P2` แทน `incident_severity`

| Scenario | Trigger | Severity | First Response |
|---|---|---|---|
| CSV schema contract violation | DQ schema check fail | `SEV2` | stop ingestion; preserve previous valid state |
| Duplicate `case_id` | DQ duplicate assertion returns rows | `SEV2` | block semantic build; inspect source duplicate |
| Invalid `stage_entered_date` | parse/range validation fail | `SEV2` | block aging path; identify invalid rows |
| DuckDB load/write failure | pipeline write/build error | `SEV1` if production unavailable, otherwise `SEV2` | stop publish; preserve last valid database/state |
| Required metric runtime input missing | `reference_date`/approved mapping missing | `SEV3` | mark dependent metrics unavailable; do not default |
| Dashboard displays mismatched/partial run | run IDs/timestamps do not align | `SEV1` | revert to previous valid published run |
| Optional AI endpoint failure | auth/rate/network error in bonus path | `SEV3` if core unaffected | disable AI action; keep core dashboard available |

Threshold-based triggers that depend on uncalibrated SLA/anomaly values remain `null` and must not be invented

## Triage Checklist

1. identify failing run / commit / deployed revision
2. check whether failure domain is contract, quality, pipeline, freshness, correctness, dashboard, or optional AI
3. confirm last known valid published state
4. inspect blocking quality rules from `DATA_QUALITY.md`
5. inspect pipeline stage from `PIPELINE_SPEC.md`
6. check whether required runtime inputs are approved
7. verify no secret/token is present in logs
8. decide whether rollback is required before attempting repair

## Recovery Procedures

### Schema Contract Violation
- stop ingestion
- compare input headers/types with `DATA_CONTRACT.md`
- do not auto-accept breaking drift
- correct source or approve/version contract change
- rerun validation

Verification:
```sql
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'stg_consequence_case'
ORDER BY column_name;
```

Rollback: keep previous valid published state

### Duplicate `case_id`
- isolate duplicates
- confirm source snapshot grain
- correct input; do not arbitrarily deduplicate unless business rule exists
- rerun ingestion

Verification:
```sql
SELECT case_id, COUNT(*)
FROM stg_consequence_case
GROUP BY case_id
HAVING COUNT(*) > 1;
```

Expected: 0 rows

### Invalid Date / Negative Aging
- inspect invalid dates
- validate approved `reference_date`
- correct source/runtime input
- rebuild aging mart

Verification:
```sql
SELECT *
FROM mart_consequence_case_aging
WHERE metric_days_in_current_stage < 0;
```

Expected: 0 rows

### DuckDB Failure
- stop partial publish
- verify filesystem/path availability
- inspect last successful database artifact/run
- rebuild from validated staging snapshot
- run integration tests before switching publish pointer/state

Rollback: restore previous known-valid DuckDB artifact or deployment revision; if no validated artifact exists, do not fabricate recovery data

### Mismatched Dashboard Run
- disable publication of partial run
- select previous run where semantic + metrics are complete
- verify KPI cards and tables share same run identifier
- rerun smoke tests

### Optional AI Failure
- keep core dashboard operational
- verify endpoint/config/credential via secret store
- retry only transient errors according to pipeline policy
- do not expose token in logs
- if unresolved, mark AI Brief unavailable

## Escalation Contacts

| Failure Domain | First Contact | Escalation Contact |
|---|---|---|
| source/contract | HR Data Owner | HR Process Owner |
| data quality/model | Analytics Implementation Owner | Data Governance Owner |
| pipeline/DuckDB | Analytics Implementation Owner | Platform Owner |
| freshness | Analytics Implementation Owner | HR Process Owner / Product Owner |
| dashboard publication | Product Owner / Analytics Implementation Owner | HR Process Owner |
| PDPA/access | Data Protection Owner | Company Security/Compliance Owner |
| AI bonus | Company AI Platform Owner | Product Owner |

ชื่อบุคคลจริง = `null`; owner สำหรับเติม contact roster คือ Project Sponsor / Company Operations Owner

## Post-Incident Review

ทุก `SEV1` และ incident ที่กระทบ metric correctness ต้องมี review หลังเหตุการณ์ โดยบันทึก:
- incident date/time
- affected run/revision
- trigger
- user/business impact
- root cause
- detection gap
- recovery action
- verification evidence
- rollback used or not used
- preventive action
- owner and due date
- changelog/contract/metric docs ที่ต้อง update

ห้ามเปลี่ยน metric definition เพื่อ “แก้ incident” แบบเงียบ ๆ; ถ้านิยามเปลี่ยนต้องไป `ANALYTICS_CHANGELOG.md`

## Retention Enforcement & Archival

Retention periods ใน `DATA_GOVERNANCE.md` ยังเป็น `null` จึงยังห้ามเปิด purge schedule จริง

เมื่อ retention ได้รับ approval ต้องสร้าง procedure ต่อ dataset ที่ครอบคลุม:
- identify eligible rows/artifacts by approved retention rule
- preview delete/archive set
- approval/checkpoint ก่อน destructive action
- purge/archive source/staging/semantic/extract/cache ตาม policy
- AI persisted output/training data ถ้ามี
- archives/backups ตาม legal procedure
- record audit evidence

**Purge schedule:** `null`  
**Calibration Owner:** Data Protection Owner / Platform Owner

**Restore test cadence:** คู่มือระบุให้ restore test ทุก 6 เดือน เมื่อ archival mechanism ถูกเปิดใช้
- restore ไป isolated schema/location
- ห้าม overwrite production
- validate row count/content
- record evidence

**Volume anomaly guard:** คู่มือยก guard >50% จากค่าเฉลี่ยสำหรับ retention job; ให้ใช้เมื่อมี baseline ที่รองรับและ reconcile กับ governance implementation ก่อน enable destructive purge

PDPA erasure request ต้องครอบคลุม archive layer ด้วย ไม่ถือ archive เป็นข้อยกเว้น
