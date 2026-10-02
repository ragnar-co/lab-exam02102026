# SLA_FRESHNESS.md

Project: Consequence Process Dashboard  
Document ID: sla_freshness  
Priority: P1  
Depends on: PIPELINE_SPEC.md

## Freshness Requirements per Dataset

### `dataset_criticality` Enum

`SLA_FRESHNESS.md` เป็นเอกสารเจ้าของ `dataset_criticality`

- `P0` — business-critical
- `P1` — informational
- `P2` — informational

> `dataset_criticality` เป็นคนละแกนจาก `data_need_priority` ใน `STAKEHOLDERS.md`
> และคนละแกนจาก `incident_severity` ใน `RUNBOOK.md`

### Freshness Doctrine

- **Freshness** = ข้อมูลมาถึงและพร้อมใช้ตามเวลาที่ตกลงหรือไม่
- **Completeness** = แถว/field ที่ควรมีอยู่ครบหรือไม่ — เป็นความรับผิดชอบหลักของ `DATA_QUALITY.md`
- **Correctness** = metric ที่คำนวณได้ถูกต้องตาม known truth หรือไม่ — เป็นความรับผิดชอบหลักของ `TESTING_STRATEGY.md`
- dashboard สามารถ fresh และ complete แต่ยังคำนวณผิดได้ จึงห้ามใช้ freshness status แทน quality/correctness status

### Dataset / Pipeline Freshness Entries

Pipeline ใน `PIPELINE_SPEC.md` เป็นแบบ on-demand และไม่มี cron ที่ได้รับการยืนยัน
ดังนั้นเอกสารนี้ไม่กำหนด hourly/daily SLA ขึ้นมาเอง

| Dataset / Pipeline | Refresh Frequency | `dataset_criticality` | Delay Tolerance | Measurement Window | Calibration Owner |
|---|---|---|---|---|---|
| `pl_ingest_consequence_csv` / `stg_consequence_case` | on-demand เมื่อ user submit/load CSV | `null` | `null` | จาก accepted ingestion trigger จน staging snapshot พร้อมใช้ | HR Process Owner / Analytics Implementation Owner |
| `pl_build_consequence_model` / semantic fact-dim layer | triggered หลัง ingestion สำเร็จ | `null` | `null` | จาก validated staging snapshot จน fact/dimension publish สำเร็จ | HR Process Owner / Analytics Implementation Owner |
| `pl_build_consequence_metrics` / metric marts | triggered หลัง semantic model สำเร็จ | `null` | `null` | จาก semantic model publish จน metric marts/views พร้อมใช้ | HR Process Owner / Analytics Implementation Owner |
| Consequence Process Dashboard | refresh หลัง metric marts/views ของ run เดียวกันพร้อม | `null` | `null` | จาก metric publish จน dashboard แสดง run เดียวกันได้ | HR Process Owner / Product Owner |

### Calibration Status

ค่าต่อไปนี้ยังไม่มีข้อมูลที่ยืนยันจากโจทย์หรือ operational history:

- recurring refresh frequency
- `dataset_criticality` assignment ต่อ dataset
- numeric delay tolerance
- freshness warning threshold
- freshness critical threshold

จึงกำหนดเป็น `null` และต้องให้ owner ด้านบน calibrate ก่อน production operation

### Exam-Scope Constraint

ข้อกำหนด “ทำให้เสร็จภายใน 120 นาที” เป็น **project delivery timeline**
ใน `CONSTRAINTS.md` ไม่ใช่ recurring freshness SLA

จึงห้ามนำ 120 นาทีไปใช้เป็น:
- dataset delay tolerance
- freshness warning threshold
- freshness critical threshold

โดยไม่มี operational calibration เพิ่มเติม

## Delay Tolerance Matrix

### Rule

- ถ้า pipeline มี recurring refresh schedule ในอนาคต `delay_tolerance`
  ต้อง **มากกว่า refresh frequency**
- ห้ามกำหนด freshness SLA เร็วกว่าที่ pipeline schedule สามารถผลิตข้อมูลได้
- สำหรับ on-demand pipeline ไม่มี fixed interval จึงต้อง calibrate delay จาก observed execution time
  และ business expectation ก่อน

| Dataset / Output | Refresh Basis | Delay Tolerance | Warning Threshold | Critical Threshold | Business Impact of Delay | Calibration Owner |
|---|---|---|---|---|---|---|
| `stg_consequence_case` | ingestion trigger | `null` | `null` | `null` | dashboard run ใหม่เริ่มไม่ได้จน source snapshot validated | Analytics Implementation Owner / HR Data Owner |
| semantic fact/dim layer | successful staging load | `null` | `null` | `null` | metrics สำหรับ run ใหม่ยังสร้างไม่ได้ | Analytics Implementation Owner |
| metric marts | successful semantic model | `null` | `null` | `null` | KPI cards, stage view และ aging outputs ของ run ใหม่ยังไม่พร้อม | Analytics Implementation Owner / HR Process Owner |
| dashboard | successful metric publish | `null` | `null` | `null` | HR ยังเห็น run ก่อนหน้าหรือไม่สามารถใช้ run ใหม่ได้ | HR Process Owner / Product Owner |

### Measurement Method

เมื่อ calibrate แล้ว freshness timing ต้องบันทึก timestamps อย่างน้อย:

- `triggered_at`
- `staging_ready_at`
- `semantic_ready_at`
- `metrics_ready_at`
- `dashboard_ready_at`

และคำนวณ delay จาก milestone ที่ระบุใน Measurement Window ของแต่ละ entry
ไม่ใช้ file `stage_entered_date` เป็น freshness clock เพราะ field นั้นเป็น business date ของ case ไม่ใช่ pipeline arrival time

### Relationship to `reference_date`

`reference_date` ใช้คำนวณ `metric_days_in_current_stage`
แต่ไม่ใช่ตัวชี้ freshness ของ pipeline

ดังนั้น:
- data freshness breach ไม่ได้หมายความว่า `reference_date` ผิด
- `reference_date` ที่ missing เป็น metric runtime-input blocker ไม่ใช่ freshness breach

## Alert Rules

ยังไม่มี numeric freshness threshold ที่ calibrate แล้ว
ทุก threshold จึงเป็น `null` ตาม NB1

### FR-001 — Staging Freshness Warning

- **Target:** `pl_ingest_consequence_csv`
- **Condition:** elapsed time ตั้งแต่ accepted ingestion trigger ถึง `staging_ready_at`
- **Warning Threshold:** `null`
- **Critical Threshold:** `null`
- **Calibration Owner:** Analytics Implementation Owner / HR Data Owner
- **Alert Contact:** Analytics Implementation Owner

### FR-002 — Semantic Model Freshness Warning

- **Target:** `pl_build_consequence_model`
- **Condition:** elapsed time ตั้งแต่ validated staging พร้อม จน semantic model publish
- **Warning Threshold:** `null`
- **Critical Threshold:** `null`
- **Calibration Owner:** Analytics Implementation Owner
- **Alert Contact:** Analytics Implementation Owner

### FR-003 — Metric Mart Freshness Warning

- **Target:** `pl_build_consequence_metrics`
- **Condition:** elapsed time ตั้งแต่ semantic model พร้อม จน metric marts พร้อม
- **Warning Threshold:** `null`
- **Critical Threshold:** `null`
- **Calibration Owner:** Analytics Implementation Owner / HR Process Owner
- **Alert Contact:** Analytics Implementation Owner

### FR-004 — Dashboard Freshness Warning

- **Target:** Consequence Process Dashboard
- **Condition:** dashboard ยังไม่แสดง metric run ล่าสุดที่ publish สำเร็จ
- **Warning Threshold:** `null`
- **Critical Threshold:** `null`
- **Calibration Owner:** Product Owner / HR Process Owner
- **Alert Contact:** Product Owner / Analytics Implementation Owner

### Alert Separation

Freshness alert ห้ามถูกใช้แทน:
- completeness alert จาก `DATA_QUALITY.md`
- correctness/metric-validation failure จาก `TESTING_STRATEGY.md`
- authentication/configuration failure จาก pipeline error handling

เมื่อเกิดหลาย failure พร้อมกัน ต้องแสดง failure domain แยกกันเพื่อให้ owner ที่ถูกต้องรับผิดชอบ

## Escalation Procedures

### Escalation Principles

- escalation ระบุเป็น **role** ไม่ใช้ชื่อบุคคล
- `SLA_FRESHNESS.md` กำหนดว่าเมื่อไร/ส่งต่อให้ใคร
- ขั้นตอน recovery แบบลงมือจริงต้องอยู่ใน `RUNBOOK.md`
- ห้ามกำหนด `incident_severity` ในไฟล์นี้ เพราะ owner ของ enum นั้นคือ `RUNBOOK.md`

### Freshness Escalation Flow

1. ตรวจว่า freshness measurement มี `triggered_at` และ milestone timestamps ครบ
2. ตรวจว่า failure เป็น freshness จริง ไม่ใช่ completeness หรือ correctness issue
3. แจ้ง pipeline owner ของ stage ที่ล่าช้า
4. หากเกิน critical threshold ที่ calibrate แล้ว ให้ escalate ไปยัง operational owner ที่กำหนด
5. หยุดการ publish run ใหม่ หาก dashboard อาจแสดงข้อมูลบางส่วนจากคนละ run
6. คง previous valid/published state ไว้จน run ใหม่ครบทุก publication gate
7. เมื่อ `RUNBOOK.md` ถูกสร้าง ให้ link ไป recovery procedure ที่ตรงกับ pipeline stage นั้น

### Escalation Matrix

| Freshness Area | First Contact | Escalation Contact | Recovery Owner | Current Threshold Status |
|---|---|---|---|---|
| CSV ingestion / staging | Analytics Implementation Owner | HR Data Owner | Analytics Implementation Owner | `null` — not calibrated |
| semantic fact/dim build | Analytics Implementation Owner | Product Owner | Analytics Implementation Owner | `null` — not calibrated |
| metric marts | Analytics Implementation Owner | HR Process Owner | Analytics Implementation Owner | `null` — not calibrated |
| dashboard publication | Product Owner / Analytics Implementation Owner | HR Process Owner | Product Owner / Analytics Implementation Owner | `null` — not calibrated |

### RUNBOOK Reconciliation

เมื่อ `RUNBOOK.md` ถูกสร้างภายหลัง ต้อง reconcile freshness scenarios อย่างน้อย:
- staging run delayed
- semantic build delayed
- metric marts delayed
- dashboard displaying previous run
- partial publication / mismatched run IDs

เอกสารนี้ไม่เขียน recovery command ซ้ำ เพื่อคงขอบเขตว่า SLA ระบุ “เมื่อไรถือว่าล่าช้าและใครรับเรื่อง”
ส่วน RUNBOOK ระบุ “ต้องทำอะไรเพื่อกู้ระบบ”
