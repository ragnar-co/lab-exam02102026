# DATA_CONTRACT.md

Project: Consequence Process Dashboard  
Document ID: data_contract  
Priority: P1  
Depends on: DATA_MODEL_SPEC.md  
Contract Version: v0.1-draft  
Effective Date: null  
Effective Date Owner: Exam Setter / HR Process Owner

## Contract Overview

### Contract Parties

- **Producer:** Mock CSV / HR source-data producer
- **Consumer:** Consequence Process analytics pipeline and dashboard
- **Business Owner:** HR Process Owner
- **Technical Consumer Owner:** Candidate / Analytics Implementation Owner

### Contract Scope

Contract นี้ครอบคลุม source CSV ที่ถูก ingest เข้าสู่ `stg_consequence_case`
และข้อมูลที่ materialize ต่อเป็น `fact_consequence_case` ตาม `DATA_MODEL_SPEC.md`

Source columns ภายใต้ contract:

- `case_id`
- `case_domain`
- `response_type`
- `stage`
- `stage_entered_date`
- `owner`

Contract นี้ไม่กำหนดสูตร metric; สูตรเป็นของ `METRIC_SPEC.md` และ `METRIC_LOGIC.md`

### Contract Status

`v0.1-draft` ยังไม่ถือเป็น production-approved contract จนกว่า:

1. ~~HR Process Owner อนุมัติ business meaning ของ `open case` / `closed case`~~ — resolved 2026-10-02 (project-specific approved rule; ดู `BUSINESS_GLOSSARY.md`)
2. ~~Exam Setter / HR Process Owner ให้ค่า `reference_date`~~ — resolved สำหรับงานสอบ: `2026-10-01` (project-specific exam assumption)
3. Producer และ consumer ยืนยัน SLA
4. Pipeline schema-drift check ถูก implement และ reconcile ใน `PIPELINE_SPEC.md`
5. Data-quality reactions ถูก reconcile ใน `DATA_QUALITY.md`

## Schema Definitions

### Source Contract — `consequence_case_csv`

| Field | Data Type | Allowed Values / Constraint | Nullable | Description |
|---|---|---|---|---|
| `case_id` | VARCHAR | non-empty; unique within validated snapshot | no | business identifier ของ case |
| `case_domain` | VARCHAR | `behavior`, `performance` | no | ด้านของ case ที่ใช้เป็น dashboard filter |
| `response_type` | VARCHAR | `recognition`, `improvement` | no | ลักษณะ response ของ consequence process |
| `stage` | VARCHAR | `closed`, `reviewing`, `follow_up`, `collecting_info` สำหรับ mock contract version นี้ | no | stage ปัจจุบันใน snapshot |
| `stage_entered_date` | DATE | valid ISO-like date parseable to DuckDB DATE | no | วันที่เข้าสู่ stage ปัจจุบัน |
| `owner` | VARCHAR | non-empty source identifier | no | coded/current case owner จาก source |

> Allowed values ของ `stage` ด้านบนเป็น **source-shape contract** เท่านั้น ไม่ใช่ business rule ว่า
> ค่าใดต้องนับเป็น `open` หรือ `closed`; mapping ทางธุรกิจถูกกำหนดใน `BUSINESS_GLOSSARY.md` (approved 2026-10-02)

### Analytics Table Contract — `fact_consequence_case`

| Field | Data Type | Nullable | Contract Role |
|---|---|---|---|
| `consequence_case_sk` | BIGINT | no | generated surrogate primary key |
| `case_id` | VARCHAR | no | source business key |
| `case_domain_key` | VARCHAR | no | FK → `dim_case_domain` |
| `response_type_key` | VARCHAR | no | FK → `dim_response_type` |
| `stage_key` | VARCHAR | no | FK → `dim_stage` |
| `stage_entered_date` | DATE | no | case-aging date input |
| `owner_key` | VARCHAR | no | FK → `dim_owner` |

### Dimension Contract

| Table | Primary Key | Required Business Attribute |
|---|---|---|
| `dim_case_domain` | `case_domain_key` | `case_domain` |
| `dim_response_type` | `response_type_key` | `response_type` |
| `dim_stage` | `stage_key` | `stage` |
| `dim_owner` | `owner_key` | `owner` |

## SLA Commitments

ยังไม่มี SLA ตัวเลขที่ได้รับการ calibrate จาก producer/HR owner จึงไม่สร้างค่าเอง

| Contract Object | Latency SLA | Availability SLA | Completeness SLA | Calibration Owner |
|---|---|---|---|---|
| `consequence_case_csv` | `null` | `null` | `null` | HR Data Owner / Exam Setter |
| `fact_consequence_case` | `null` | `null` | `null` | Analytics Implementation Owner / HR Data Owner |
| dimension tables | `null` | `null` | `null` | Analytics Implementation Owner / HR Data Owner |

### Exam Execution Expectation

สำหรับข้อสอบ มีข้อกำหนดที่ยืนยันแล้วว่า core solution ต้อง ingest, validate, persist, test และ deploy
ภายใน 120 นาที แต่เงื่อนไขนี้เป็น **project delivery constraint** ไม่ใช่ operational data SLA
จึงไม่แปลงเป็น latency/availability/completeness SLA ใน contract นี้

## Breaking Change Policy

### Breaking vs Additive

**Additive change**
- เพิ่ม field ใหม่ที่ optional / nullable และ consumer เดิมยังทำงานได้
- เพิ่ม metadata ที่ consumer ไม่จำเป็นต้องใช้

**Breaking change**
- rename field
- drop field
- เปลี่ยน data type
- เปลี่ยนความหมายของ field หรือ value เดิม
- เปลี่ยน required field ให้ consumer เดิมรับไม่ได้
- เพิ่ม allowed value ใหม่ใน categorical field ที่ consumer ใช้ exhaustive branching/switch
- เปลี่ยน grain หรือ uniqueness guarantee
- เปลี่ยน business key semantics

### Notice Period

Breaking change ต้องแจ้ง consumer ล่วงหน้า **ไม่น้อยกว่า 14 วัน**

### Versioning Strategy

- non-breaking additive change: increment minor version เช่น `v0.1` → `v0.2`
- breaking change: increment major version เช่น `v1` → `v2`
- old/new contract อาจ coexist ระหว่าง migration window
- `v0.1-draft` ยังไม่ใช่ certified production contract

### Migration Procedure

1. Producer แจ้ง proposed change พร้อม schema diff
2. Consumer ทำ impact analysis ต่อ staging, fact/dim, metrics, tests และ dashboard
3. สร้าง contract version ใหม่
4. เพิ่ม/แก้ validation test ก่อน ingest version ใหม่
5. รัน compatibility test กับ sample input
6. deploy consumer ที่รองรับ version ใหม่
7. switch producer หลัง validation ผ่าน
8. retire old version หลัง migration deadline และ evidence ครบ

ห้ามแก้ shape ของ source แล้วปล่อยให้ pipeline infer silently

## Required Fields

### Source CSV Required Fields

ทุก record ต้องมี fields ต่อไปนี้:

- `case_id`
- `case_domain`
- `response_type`
- `stage`
- `stage_entered_date`
- `owner`

### Required-Field Rules

- header ต้องมีครบทั้ง 6 fields
- `case_id` ต้อง non-null, non-empty และ unique ภายใน snapshot
- categorical fields ต้อง non-null และผ่าน allowed-value check
- `stage_entered_date` ต้อง parse เป็น `DATE`
- `owner` ต้อง non-null และ non-empty
- extra optional column สามารถรับได้เฉพาะเมื่อ schema-drift policy ระบุว่า additive และ pipeline
  ไม่พังจาก column ดังกล่าว

### Reject / Quarantine Expectation

record ที่ผิด required-field contract ต้องไม่เข้า `fact_consequence_case` แบบเงียบ ๆ
reaction ที่แน่นอน (reject ทั้ง file หรือ quarantine row) จะถูกประกาศใน `DATA_QUALITY.md`
หลัง `PIPELINE_SPEC.md` พร้อม

## Data Type Constraints

| Field | Expected Type | Type Constraint |
|---|---|---|
| `case_id` | VARCHAR | ห้าม cast เป็น numeric เพราะเป็น identifier |
| `case_domain` | VARCHAR | exact categorical match ตาม contract version |
| `response_type` | VARCHAR | exact categorical match ตาม contract version |
| `stage` | VARCHAR | exact categorical match ตาม contract version |
| `stage_entered_date` | DATE | parse failure = contract violation |
| `owner` | VARCHAR | preserve source identifier; ห้าม infer personal name |

### General Type Rules

- identifiers ต้องเก็บเป็น `VARCHAR`
- dates ต้อง materialize เป็น DuckDB `DATE`
- boolean/rate fields ที่เพิ่มภายหลังต้องกำหนด type ชัดเจนก่อน ingest
- monetary field หากถูกเพิ่มในอนาคตต้องใช้ `DECIMAL` ไม่ใช้ `FLOAT`
- ห้ามเปลี่ยน type อัตโนมัติจากการเดา sample rows หากขัดกับ contract
- schema validation ต้องเกิดก่อน transformation logic ที่คำนวณ metrics

## Upstream Event Contract (Product Events)

**Not applicable สำหรับ core scope ปัจจุบัน**

โปรเจกต์นี้เลือก `ddd-data-analytics` เพียง track เดียวและ source ที่ได้รับคือ CSV snapshot
ไม่ได้ consume web-app product events และไม่มี upstream `TRACKING_PLAN.md`

ดังนั้น:

- ไม่มี `event_name` ที่ DATA_CONTRACT.md ต้องอ้าง
- ไม่มี `event_schema_version` ที่ต้อง assign ใน core scope
- ไม่มี first-consumed event run
- ห้ามสร้าง product event contract สมมติขึ้นมา

### Schema Drift Detection Expectation

แม้ไม่มี product event stream, CSV source ยังต้องตรวจ shape drift ก่อน ingest โดยอย่างน้อยตรวจ:

1. required header presence
2. unexpected missing fields
3. data-type parseability
4. categorical values นอก contract
5. duplicate `case_id`
6. unexpected extra columns และ classify ว่า additive หรือ breaking

กลไก implementation จริงจะอยู่ใน `PIPELINE_SPEC.md` และ reaction/rule severity จะอยู่ใน
`DATA_QUALITY.md`; เอกสารนี้ประกาศเพียง contract ที่ทั้งสองเอกสารต้อง enforce
