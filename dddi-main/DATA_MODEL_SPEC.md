# DATA_MODEL_SPEC.md

Project: Consequence Process Dashboard  
Document ID: data_model_spec  
Priority: P0  
Depends on: METRIC_SPEC.md

## Fact Tables

### `fact_consequence_case`

**Purpose:** ตารางหลักสำหรับวิเคราะห์สถานะ Consequence Process จาก validated CSV snapshot

**Grain:** 1 row ต่อ 1 `case_id` ณ dataset snapshot ที่โหลดสำเร็จ

| Column | Type | Role | Source | Nullable | Notes |
|---|---|---|---|---|---|
| `case_id` | VARCHAR | business key | CSV `case_id` | no | รหัสกรณี; mock CSV ปัจจุบัน unique 40,000 ค่า |
| `case_domain_key` | VARCHAR | FK | derived from CSV `case_domain` | no | join ไป `dim_case_domain` |
| `response_type_key` | VARCHAR | FK | derived from CSV `response_type` | no | join ไป `dim_response_type` |
| `stage_key` | VARCHAR | FK | derived from CSV `stage` | no | join ไป `dim_stage` |
| `stage_entered_date` | DATE | event/date attribute | CSV `stage_entered_date` | no | วันที่เข้าสู่ stage ปัจจุบัน |
| `owner_key` | VARCHAR | FK | derived from CSV `owner` | no | join ไป `dim_owner` |

### Primary Key Strategy

สำหรับ implementation ของข้อสอบ ให้ใช้ surrogate key ชื่อ `consequence_case_sk` เมื่อ materialize ตารางจริง และคง `case_id` เป็น business key

- `consequence_case_sk`: generated surrogate primary key
- `case_id`: source business key
- ห้ามใช้ `case_id` เป็น surrogate key แม้ mock CSV ปัจจุบันจะ unique

### Supported Metric References

ตารางนี้รองรับ metrics ที่ประกาศไว้ใน `METRIC_SPEC.md`:

- `metric_total_cases`
- `metric_closed_cases`
- `metric_open_cases`
- `metric_open_cases_by_stage`
- `metric_days_in_current_stage`
- `metric_top_3_longest_open_cases`

สูตรของ metrics ยังคงเป็นเจ้าของโดย `METRIC_SPEC.md` และไม่ประกาศสูตรซ้ำในเอกสารนี้

## Dimension Tables

### `scd_type` Enum

`DATA_MODEL_SPEC.md` เป็นเอกสารเจ้าของ `scd_type`:

- `1` — overwrite current value
- `2` — keep history ด้วย `valid_from` / `valid_to`
- `none` — dimension ไม่ต้องจัดการประวัติการเปลี่ยนแปลงแบบ SCD

### `dim_case_domain`

**Purpose:** dimension สำหรับแยกด้านของกรณีที่ dashboard ใช้เป็น mandatory filter  
**Business Key:** `case_domain`  
**Primary Key:** `case_domain_key`  
**scd_type:** `none`

| Column | Type | Notes |
|---|---|---|
| `case_domain_key` | VARCHAR | surrogate/dimension key |
| `case_domain` | VARCHAR | source value จาก CSV |

เหตุผลที่ใช้ `none`: ในขอบเขตข้อสอบค่าถูกใช้เป็น category code จาก snapshot และยังไม่มี requirement ให้ track history ของ code list

### `dim_response_type`

**Purpose:** dimension สำหรับลักษณะการตอบสนองใน Consequence Process  
**Business Key:** `response_type`  
**Primary Key:** `response_type_key`  
**scd_type:** `none`

| Column | Type | Notes |
|---|---|---|
| `response_type_key` | VARCHAR | surrogate/dimension key |
| `response_type` | VARCHAR | source value จาก CSV |

### `dim_stage`

**Purpose:** dimension สำหรับขั้นตอนปัจจุบันของกรณี  
**Business Key:** `stage`  
**Primary Key:** `stage_key`  
**scd_type:** `none`

| Column | Type | Notes |
|---|---|---|
| `stage_key` | VARCHAR | surrogate/dimension key |
| `stage` | VARCHAR | source value จาก CSV |

> `dim_stage` ไม่ประกาศว่า stage ใดคือ open หรือ closed; mapping อยู่ใน `BUSINESS_GLOSSARY.md` (approved) และถูกส่งเป็น runtime relation (`approved_open_stage_values` / `approved_closed_stage_values`)

### `dim_owner`

**Purpose:** dimension สำหรับผู้รับผิดชอบกรณีที่ปรากฏใน dataset  
**Business Key:** `owner`  
**Primary Key:** `owner_key`  
**scd_type:** `1`

| Column | Type | Notes |
|---|---|---|
| `owner_key` | VARCHAR | surrogate/dimension key |
| `owner` | VARCHAR | source identifier เช่น coded HR owner |

เหตุผลที่ใช้ Type 1: mock source มีเพียง current owner identifier และไม่มี effective-date history สำหรับ owner dimension; หาก production requirement ต้องเก็บประวัติการเปลี่ยน owner ต้องเปลี่ยน model ผ่าน change process ก่อน

## Relationships

| From | Cardinality | To | Join Key | Integrity Rule |
|---|---|---|---|---|
| `fact_consequence_case` | many-to-one | `dim_case_domain` | `case_domain_key` | fact ทุก row ต้อง resolve dimension ได้ |
| `fact_consequence_case` | many-to-one | `dim_response_type` | `response_type_key` | fact ทุก row ต้อง resolve dimension ได้ |
| `fact_consequence_case` | many-to-one | `dim_stage` | `stage_key` | fact ทุก row ต้อง resolve dimension ได้ |
| `fact_consequence_case` | many-to-one | `dim_owner` | `owner_key` | fact ทุก row ต้อง resolve dimension ได้ |

### Relationship Rules

- ห้ามเกิด orphan foreign key ใน fact table
- dimension key ต้อง deterministic ภายใน dataset load
- filter `case_domain` ต้องไหลจาก `dim_case_domain` ไปยัง `fact_consequence_case`
- stage aggregation ต้องอ้าง `dim_stage`
- Top 3 และ case aging ใช้ row-level fact โดยอ้าง metric definition จาก `METRIC_SPEC.md`
- ไม่มี many-to-many relationship ใน core model ของข้อสอบนี้

## Grain Definitions

### `fact_consequence_case`

**Declared grain:**  
`1 case × 1 validated dataset snapshot`

**Uniqueness expectation:**  
`case_id` ต้องมีไม่เกิน 1 row ต่อ validated snapshot

**Current mock observation:**  
mock CSV ที่ได้รับมี 40,000 rows และ `case_id` unique 40,000 ค่า

**Not represented by this grain:**

- ประวัติการเปลี่ยน `stage`
- ประวัติการเปลี่ยน `owner`
- event-level case activity
- case comments / notes
- effective-from / effective-to history

ดังนั้น model นี้ตอบคำถามว่า “กรณีอยู่ที่ไหนใน snapshot ปัจจุบัน” ไม่ใช่ “กรณีเดินผ่านทุกขั้นตอนอย่างไรตลอดเวลา”

### Dimension Grains

| Dimension | Grain |
|---|---|
| `dim_case_domain` | 1 row ต่อ distinct `case_domain` |
| `dim_response_type` | 1 row ต่อ distinct `response_type` |
| `dim_stage` | 1 row ต่อ distinct `stage` |
| `dim_owner` | 1 row ต่อ distinct current `owner` identifier |

### Reference Date

`reference_date` ไม่ใช่ field ที่มีอยู่ใน source CSV ปัจจุบัน; ค่าที่ใช้ = `2026-10-01` — project-specific exam assumption ที่ผู้ทำข้อสอบยืนยัน (ไม่ใช่ industry standard และไม่ใช่ค่าที่ระบุมาใน exam brief ต้นฉบับ) (ส่งเข้ามาเป็น runtime input)

- **Owner:** Exam Setter / HR Process Owner
- **Use:** runtime/configuration input สำหรับ metrics ที่พึ่ง reference date
- **Constraint:** ห้ามใช้ system date แทนโดยอัตโนมัติ
- หากต้อง persist `reference_date` ต่อ run ให้เพิ่ม run metadata table ผ่าน model change ที่มี approval แทนการแทรก field เข้า fact โดยไม่มี source
- Implementation (2026-10-02) เพิ่ม run-level tables นอก fact/dim grain: `run_metadata` (run_id, snapshot_id, csv_sha256, row_count, reference_date, aging_status), `runtime_inputs`, `approved_open_stage_values`, `approved_closed_stage_values`, `quality_results`; ไม่เปลี่ยน grain หรือ column ของ `fact_consequence_case`

## PDPA Data Classification

### `pdpa_classification` Enum

`DATA_MODEL_SPEC.md` เป็นเอกสารเจ้าของ `pdpa_classification`:

- `public` — ข้อมูลที่อนุญาตให้เปิดเผยสาธารณะ
- `internal` — ข้อมูลสำหรับใช้งานภายในองค์กร
- `confidential` — ข้อมูลที่ต้องจำกัดการเข้าถึงตามบทบาทหรือหน้าที่
- `restricted` — ข้อมูลที่มีความอ่อนไหวสูงและต้องใช้การควบคุมเข้าถึงที่เข้มงวดที่สุดในระดับโปรเจกต์

### Column Classification

การจัดชั้นต่อไปนี้เป็น **project classification assumption สำหรับงานสอบ** โดยใช้แนวทาง conservative เนื่องจากข้อมูลอยู่ในบริบท HR; ต้องให้ HR Data Owner / Data Protection Owner ยืนยันก่อน production use

| Table | Column | `pdpa_classification` | Rationale / Handling |
|---|---|---|---|
| `fact_consequence_case` | `consequence_case_sk` | `internal` | technical identifier |
| `fact_consequence_case` | `case_id` | `restricted` | identifier ที่เชื่อมโยงกับกรณี HR |
| `fact_consequence_case` | `case_domain_key` | `confidential` | เป็น attribute ของกรณี HR เมื่อเชื่อมกับ case |
| `fact_consequence_case` | `response_type_key` | `confidential` | เป็น attribute ของกรณี HR |
| `fact_consequence_case` | `stage_key` | `confidential` | สะท้อนสถานะกระบวนการ HR |
| `fact_consequence_case` | `stage_entered_date` | `confidential` | วันที่เกี่ยวข้องกับกรณี HR |
| `fact_consequence_case` | `owner_key` | `confidential` | เชื่อมกับผู้รับผิดชอบภายใน |
| `dim_case_domain` | `case_domain_key` | `internal` | technical key |
| `dim_case_domain` | `case_domain` | `internal` | code list เมื่ออยู่นอก context ของ case |
| `dim_response_type` | `response_type_key` | `internal` | technical key |
| `dim_response_type` | `response_type` | `internal` | code list เมื่ออยู่นอก context ของ case |
| `dim_stage` | `stage_key` | `internal` | technical key |
| `dim_stage` | `stage` | `internal` | process code list |
| `dim_owner` | `owner_key` | `confidential` | identifier mapping key |
| `dim_owner` | `owner` | `confidential` | coded HR owner identifier |

### Classification Constraints

- mock CSV ไม่มีชื่อบุคคลโดยตรง แต่ `case_id` และ `owner` ยังสามารถเป็น identifiers ภายในบริบท HR ได้ จึงไม่ถือว่าเป็น public
- classification นี้ไม่ใช่การยืนยัน legal basis, retention period หรือ access policy
- legal basis และ residency ยังเป็น `null` ตาม `CONSTRAINTS.md`
- access control และ retention ต้องไปกำหนดใน `DATA_GOVERNANCE.md` หลัง dependencies พร้อม
- ก่อน ship pipeline ต้องไม่มี personal-data column ที่ไม่ได้รับ `pdpa_classification`
