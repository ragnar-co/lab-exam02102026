# DATA_GOVERNANCE.md

Project: Consequence Process Dashboard  
Document ID: data_governance  
Priority: P0  
Depends on: DATA_MODEL_SPEC.md, DATA_CONTRACT.md, KPI_DICTIONARY.md

## Data Ownership Matrix

Template ต้องการ Data Owner และ Data Steward ที่เป็นชื่อบุคคลจริง แต่โจทย์ไม่ได้ให้รายชื่อ จึงไม่สมมติชื่อ

| Dataset | Data Owner | Data Steward | Calibration Owner |
|---|---|---|---|
| `stg_consequence_case` | `null` | `null` | HR Process Owner / Company Data Governance Owner |
| `fact_consequence_case` | `null` | `null` | HR Process Owner / Company Data Governance Owner |
| `dim_case_domain` | `null` | `null` | HR Process Owner / Company Data Governance Owner |
| `dim_response_type` | `null` | `null` | HR Process Owner / Company Data Governance Owner |
| `dim_stage` | `null` | `null` | HR Process Owner / Company Data Governance Owner |
| `dim_owner` | `null` | `null` | HR Process Owner / Company Data Governance Owner |
| metric marts/views | `null` | `null` | HR Process Owner / Analytics Governance Owner |

**Governance blocker:** production readiness ยังไม่ผ่านจนกว่าจะระบุชื่อจริงของ Data Owner และ Data Steward

## Access Control Policy

Access control ต้องบังคับมากกว่าชั้น dashboard เพียงอย่างเดียว

| Role | Row Scope | Column Access | Write Access |
|---|---|---|---|
| HR Process Owner | HR consequence-process rows ตาม scope ที่องค์กรอนุมัติ | business metrics + case-level fields ตาม policy | no direct source-table write |
| HR Operations / Case Management | rows ที่อยู่ใน operational scope ของตน | fields ที่จำเป็นต่อ follow-up | no direct semantic-model write |
| Analytics Implementation Owner | technical access ที่จำเป็นต่อ pipeline/test | masked/minimum necessary when inspecting HR case data | pipeline-managed only |
| Dashboard Viewer | aggregated/authorized dashboard scope | aggregate + approved row-level drill-down | none |

- **Row-level security enforcement layer:** `null`
- **Calibration Owner:** Company Data Platform / Security Owner
- **Column masking enforcement layer:** `null`
- **Calibration Owner:** Company Data Platform / Security Owner
- direct DuckDB/file access ใน production ต้องไม่ bypass policy
- secrets/credentials ไม่ใช่ mechanism สำหรับอนุญาต business data access

## PDPA and PII Classification

Classification อ้าง `pdpa_classification` จาก `DATA_MODEL_SPEC.md`; เอกสารนี้ไม่ประกาศ enum values ซ้ำ

| Column | Classification Reference | Masking Rule | Legal Basis |
|---|---|---|---|
| `fact_consequence_case.case_id` | `DATA_MODEL_SPEC.md` | mask/pseudonymize สำหรับผู้ใช้ที่ไม่ต้องเห็น identifier จริง | `null` — owner: HR Data Owner / Data Protection Owner |
| `fact_consequence_case.case_domain_key` | `DATA_MODEL_SPEC.md` | role-based access | `null` — owner: HR Data Owner / Data Protection Owner |
| `fact_consequence_case.response_type_key` | `DATA_MODEL_SPEC.md` | role-based access | `null` — owner: HR Data Owner / Data Protection Owner |
| `fact_consequence_case.stage_key` | `DATA_MODEL_SPEC.md` | role-based access | `null` — owner: HR Data Owner / Data Protection Owner |
| `fact_consequence_case.stage_entered_date` | `DATA_MODEL_SPEC.md` | role-based access | `null` — owner: HR Data Owner / Data Protection Owner |
| `fact_consequence_case.owner_key` | `DATA_MODEL_SPEC.md` | mask where viewer does not require owner identity | `null` — owner: HR Data Owner / Data Protection Owner |
| `dim_owner.owner` | `DATA_MODEL_SPEC.md` | mask/pseudonymize outside authorized HR roles | `null` — owner: HR Data Owner / Data Protection Owner |

ทุก column ที่ classified confidential/restricted ต้องมี legal basis และ masking/access rule ก่อน production approval

## Data Retention Policy

Retention period เป็นค่าที่ต้อง calibrate และโจทย์ไม่ได้ให้ จึงไม่สร้างตัวเลข

| Dataset | Retention Period (months) | Justification | Calibration Owner |
|---|---:|---|---|
| staging snapshot | `null` | pending legal/business requirement | HR Data Owner / Data Protection Owner |
| semantic fact/dim | `null` | pending legal/business requirement | HR Data Owner / Data Protection Owner |
| dashboard extracts/cache | `null` | pending platform/business requirement | Product Owner / Data Protection Owner |
| AI brief persistence if bonus enabled | `null` | pending legal/business requirement | HR Process Owner / Data Protection Owner |
| archive/backups | `null` | pending legal/security requirement | Data Protection Owner / Platform Owner |

Erasure mechanics เมื่อมี policy ที่อนุมัติแล้วต้องครอบคลุมอย่างน้อย:
`source/ingested data → semantic tables → extracts/cache → AI persisted output/training set if any → archives/backups according to lawful procedure`

ห้ามถือว่าการลบเฉพาะ source table คือ erasure ที่เสร็จสมบูรณ์

## Audit Requirements

ต้องบันทึก audit evidence สำหรับ:
- CSV ingestion run identifier
- validation result
- schema/contract violation
- pipeline publish status
- access to restricted/confidential row-level data
- export/download ถ้ามี
- governance policy change
- PDPA erasure action
- AI Brief generation/persistence ถ้าเปิด bonus

**Audit retention:** `null`  
**Calibration Owner:** Company Security / Data Protection Owner

Audit log ต้องไม่บันทึก secret/token และควรเก็บ actor/role, action, object, timestamp, result และ run/change identifier

## Cost Governance

หัวข้อนี้เป็น ongoing operational cost ไม่ใช่ project delivery budget ใน `CONSTRAINTS.md`

- **Monthly cost ceiling:** `null`
- **Budget Owner (named person required):** `null`
- **Calibration Owner:** Project Sponsor / Finance Owner
- **Warning threshold:** `null`
- **Critical threshold:** `null`
- **Calibration Owner:** Finance Owner / Platform Owner
- **Cost dashboard:** required when cost-bearing infrastructure is used; implementation = `null`
- **Per-query bytes limit by role:** `null`
- **Auto-kill runaway query rule:** `null`
- **Calibration Owner:** Platform Owner
- **Cost attribution labels:** `team`, `dashboard_id`, `pipeline_name`

ใน exam implementation ที่ใช้ embedded DuckDB อาจไม่มี warehouse query charge โดยตรง แต่ค่า operational hosting/API ยังต้องถูก governance หากเกิดค่าใช้จ่ายจริง
