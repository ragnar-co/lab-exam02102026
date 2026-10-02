# AGENTS.md

Project: Consequence Process Dashboard  
Document ID: agents_md  
Priority: P0  
Depends on: PIPELINE_SPEC.md, DATA_GOVERNANCE.md, CONSTRAINTS.md, DATA_MODEL_SPEC.md

## Project Overview

คุณกำลังทำงานกับโปรเจกต์ `Consequence Process Dashboard` ซึ่งใช้ `ddd-data-analytics` เป็น track หลัก เป้าหมายคือรับ CSV, validate, บันทึกลง DuckDB, คำนวณ metrics จาก semantic layer และแสดง dashboard สำหรับ HR เพื่อตรวจจำนวน case, open/closed status, distribution ตาม `stage`, case aging และ Top 3 longest-open cases

ข้อกำหนดที่ต้องรักษา:
- metric meaning อยู่ใน `METRIC_SPEC.md`
- metric SQL implementation อยู่ใน `METRIC_LOGIC.md`
- schema/grain อยู่ใน `DATA_MODEL_SPEC.md`
- pipeline behavior อยู่ใน `PIPELINE_SPEC.md`
- access/PDPA policy อยู่ใน `DATA_GOVERNANCE.md`
- testing gate อยู่ใน `TESTING_STRATEGY.md`
- dashboard ต้อง consume metric layer ไม่คำนวณสูตรใหม่เอง

## Tech Stack

คัดจาก `CONSTRAINTS.md`:

- Analytics track: `ddd-data-analytics`
- Input: CSV
- Analytics store: `DuckDB`
- Coding agent: Claude Code หรือ Codex
- Token constraint: ใช้ Token ที่มีอยู่ ห้ามเติมเพิ่ม
- Deployment target: Coolify
- Source control: company repository
- Dashboard/application framework: `null` — Candidate / Implementation Owner ต้องเลือกโดยไม่ขัดข้อสอบ
- Transform tool/version: `null`
- Core external scheduler: not required; pipeline เป็น on-demand
- Optional AI endpoint: company-provided endpoint, รายละเอียด endpoint/auth/quota ยังเป็น `null`

## Query & Modeling Conventions

1. รักษา grain ของ `fact_consequence_case` เป็น `1 case × 1 validated dataset snapshot`
2. ใช้ `case_id` เป็น business key และใช้ surrogate key แยกต่างหากใน fact table
3. identifiers ต้องเก็บเป็น `VARCHAR`
4. `stage_entered_date` ต้องเป็น `DATE`
5. filter `case_domain` ต้อง propagate จาก semantic layer ไปยัง dashboard components ที่เกี่ยวข้อง
6. transformation path ใช้ `staging → intermediate → mart`
7. same input snapshot + same approved runtime inputs ต้องให้ผล deterministic
8. `reference_date` เป็น approved runtime input; ห้ามใช้ system date แทน
9. Top 3 ต้องใช้ ordering ที่ `METRIC_LOGIC.md` กำหนดและ approved tie-break
10. query ใหม่ที่คำนวณ metric ต้องอ้าง metric ID เดิมและไม่สร้าง alias definition ใหม่

## Forbidden Patterns

1. **ห้ามนิยาม metric formula ใน dashboard เพราะจะทำให้เกิด source of truth มากกว่าหนึ่งจุด ให้ใช้ output จาก `METRIC_LOGIC.md` / mart views แทน**
2. **ห้าม hard-code `reference_date` หรือใช้ `CURRENT_DATE` เพราะโจทย์ต้องใช้วันที่อ้างอิงที่กำหนด ให้รับ approved runtime/config value แทน**
3. **ห้ามเดา open/closed mapping เพราะ business definition ยังต้องได้รับ approval ให้ใช้ approved rule source ที่ pipeline/metric layer รับเข้ามาแทน**
4. **ห้ามตั้ง quality threshold, anomaly bound, retention, cost ceiling หรือ SLA number จากตัวเลข mock เพราะค่าดังกล่าวต้อง calibrate ให้ใช้ `null` + owner จนกว่าจะมี approval**
5. **ห้าม deduplicate `case_id` แบบเลือกแถวใดแถวหนึ่งเอง เพราะจะซ่อน contract violation ให้ reject/flag duplicate ตาม `DATA_QUALITY.md` แทน**
6. **ห้าม bypass semantic model แล้ว query CSV ตรงจาก dashboard เพราะจะทำให้ grain, FK และ metric governance ถูกข้าม ให้ query approved DuckDB models/marts แทน**
7. **ห้าม commit token, credential หรือ endpoint secret เพราะเสี่ยงรั่วไหล ให้ใช้ Coolify-managed environment secrets/variables แทน**
8. **ห้ามเปลี่ยน enum value ในเอกสารที่ไม่ใช่ owner เพราะจะเกิด definition drift ให้แก้เฉพาะ owner document และอ้างชื่อ enum จากที่อื่น**
9. **ห้าม publish partial run เพราะ KPI cards และ tables อาจมาจากคนละ snapshot ให้คง previous valid state จน run ใหม่ผ่าน publication gate**
10. **ห้ามใช้ AI Brief เพื่อตัดสินโทษหรือประเมินบุคคล เพราะ bonus นี้มีไว้ช่วย review process ให้จำกัด input เป็น aggregate/approved analytics output แทน**

## Data Quality & Testing Rules

- ทุก required-field, uniqueness, type, categorical, FK และ aging guard ใน `DATA_QUALITY.md` ต้องมี assertion ที่รันได้
- `rule_severity = error` fail ต้อง block publish
- warning/anomaly ที่ threshold ยังเป็น `null` ต้องแสดง `not_calibrated` ไม่ปลอมเป็น pass
- integration test ต้องมี idempotency: รัน input เดิม 2 รอบแล้วไม่เพิ่ม duplicate
- metric validation ต้องมี golden dataset หลัง business rules ได้ approval
- ต้องตรวจทั้ง row-level และ aggregate reconciliation
- filter tests ต้องพิสูจน์ว่า `behavior` กับ `performance` ไม่ปะปน
- deployment smoke test ต้องเปิด endpoint, render dashboard และ query DuckDB ได้
- failing blocking tests ห้าม override เพื่อให้ทัน 120 นาที

## PDPA Rules

ใช้ classification จาก `DATA_MODEL_SPEC.md` และ policy จาก `DATA_GOVERNANCE.md`

คอลัมน์ที่ต้องควบคุมอย่างชัดเจน:
- `fact_consequence_case.case_id`
- `fact_consequence_case.case_domain_key`
- `fact_consequence_case.response_type_key`
- `fact_consequence_case.stage_key`
- `fact_consequence_case.stage_entered_date`
- `fact_consequence_case.owner_key`
- `dim_owner.owner`

Rules:
- ห้ามเปิด `fact_consequence_case.case_id` ให้ผู้ใช้ที่ไม่ต้องใช้ identifier จริง
- ห้าม expose `dim_owner.owner` นอก authorized HR roles โดยไม่มี masking/pseudonymization policy
- row-level และ column-level access ต้องบังคับตามชั้นที่ `DATA_GOVERNANCE.md` อนุมัติ; ตอนนี้ enforcement layer ยังเป็น `null`
- legal basis และ retention ยังเป็น `null`; ห้ามเติมเองใน code/config
- logs ห้ามบันทึก secret และควรลดการบันทึก row-level HR identifiers เกินความจำเป็น
- AI bonus ต้องใช้ aggregate/minimum-necessary input และต้องไม่เปลี่ยนเป็น automated disciplinary decision
