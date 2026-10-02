# STAKEHOLDERS.md

Project: Consequence Process Dashboard  
Document ID: stakeholders  
Priority: P1  
Depends on: none

## Stakeholder Profiles

### HR / Consequence Process Owner

- **Name / Role:** HR / Consequence Process Owner
- **Team:** Human Resources
- **data_literacy_level:** basic
- **Critical Questions:**
  - ขณะนี้มีกรณีทั้งหมดกี่กรณี และแบ่งเป็นกรณีเปิดกับกรณีปิดเท่าใด
  - กรณีเปิดกำลังค้างอยู่ที่ `stage` ใดบ้าง
  - กรณีเปิดแต่ละกรณีอยู่ใน `current_stage` มาแล้วกี่วันเมื่อเทียบกับ `reference_date` ของโจทย์
  - 3 กรณีใดอยู่ใน `current_stage` นานที่สุดและควรถูกนำมาตรวจสอบก่อน
  - เมื่อเลือก `case_domain = behavior` หรือ `case_domain = performance` ภาพรวมและรายการค้างเปลี่ยนไปอย่างไร
  - ภาพรวมของ `response_type = recognition` และ `response_type = improvement` สะท้อนจุดใดของกระบวนการที่ควรตรวจสอบเพิ่มเติม
- **Current Pain Points:**
  - ต้องตรวจหลายกรณีจากข้อมูลรายการโดยตรง ทำให้เห็น bottleneck ของกระบวนการได้ยาก
  - ยังไม่มีมุมมองรวมที่แสดงจำนวนกรณีตาม `stage` พร้อมอายุของกรณีเปิดในขั้นตอนปัจจุบัน
  - การหากรณีที่ค้างนานที่สุดต้องอาศัยการคำนวณและเรียงข้อมูล
  - หากใช้วันที่ปัจจุบันของเครื่องแทน `reference_date` ผลการตรวจอาจไม่ตรงกับโจทย์
- **Preferred Format:** dashboard
- **Decision Cadence:** ใช้งานแบบ on-demand ก่อนการทบทวนหรือปรับปรุง Consequence Process โดยผลคำนวณต้องอ้างอิง `reference_date` ที่โจทย์กำหนด
- **Decision Scope:** ใช้เพื่อระบุจุดที่ควรตรวจสอบและจัดลำดับการติดตาม process ไม่ใช้ dashboard เพื่อตัดสินโทษ ประเมินบุคคล หรือสรุปผลทางวินัยโดยอัตโนมัติ

### Enum Ownership

`STAKEHOLDERS.md` เป็นเอกสารเจ้าของ enum ต่อไปนี้

#### `data_literacy_level`

- `basic` — ผู้ใช้ต้องการ visualization และคำอธิบายที่ตรงไปตรงมา
- `intermediate` — ผู้ใช้สามารถอ่าน visualization เชิงวิเคราะห์และใช้ filter/drill-down ได้
- `advanced` — ผู้ใช้สามารถตีความ visualization และ analytical interaction ที่ซับซ้อนได้

#### `data_need_priority`

- `P0` — cannot operate without
- `P1` — important
- `P2` — nice to have

> หมายเหตุ: `data_need_priority` เป็นคนละแนวคิดกับ `dataset_criticality` และ `incident_severity`

## Data Needs Matrix

| Stakeholder | Data Need | Related KPI / Metric Intent | `data_need_priority` | Freshness Requirement |
|---|---|---|---|---|
| HR / Consequence Process Owner | จำนวนกรณีทั้งหมด พร้อมจำนวน `open` และ `closed` | Process case overview | P0 | คำนวณจาก dataset ที่โหลดสำเร็จ โดยใช้ `reference_date` ของโจทย์; `reference_date` = `2026-10-01` — project-specific exam assumption ที่ผู้ทำข้อสอบยืนยัน (ไม่ใช่ industry standard และไม่ใช่ค่าที่ระบุมาใน exam brief ต้นฉบับ) |
| HR / Consequence Process Owner | จำนวนกรณีแยกตาม `stage` | Stage distribution / process bottleneck view | P0 | snapshot เดียวกับ dashboard run และ `reference_date` เดียวกัน |
| HR / Consequence Process Owner | จำนวนวันของกรณีเปิดใน `current_stage` และ Top 3 longest-open cases | Case aging / follow-up prioritization | P0 | คำนวณแบบ deterministic จาก `stage_entered_date` ถึง `reference_date`; `reference_date` = `2026-10-01` — project-specific exam assumption ที่ผู้ทำข้อสอบยืนยัน (ไม่ใช่ industry standard และไม่ใช่ค่าที่ระบุมาใน exam brief ต้นฉบับ) |
| HR / Consequence Process Owner | Filter ตาม `case_domain` | Behavior vs Performance analysis | P1 | ใช้ dataset snapshot เดียวกับ metric หลัก |
| HR / Consequence Process Owner | ภาพรวม `response_type` | Recognition vs Improvement context | P2 | ใช้ dataset snapshot เดียวกับ metric หลัก |
| HR / Consequence Process Owner | AI-generated Process Improvement Brief | จุดที่ควรตรวจสอบและข้อเสนอการปรับขั้นตอนจากข้อมูลภาพรวม | P2 | สร้างหลัง metric หลักคำนวณสำเร็จ และต้องอ้างอิง aggregate ที่แสดงบน dashboard รอบเดียวกัน |

### Assumptions to Validate

1. `data_literacy_level = basic` เป็น assumption สำหรับผู้ใช้ HR ในงานสอบนี้ และต้องยืนยันกับผู้ใช้จริงหากนำระบบไปใช้จริง
2. `reference_date` = `2026-10-01` — project-specific exam assumption ที่ผู้ทำข้อสอบยืนยัน (ไม่ใช่ industry standard และไม่ใช่ค่าที่ระบุมาใน exam brief ต้นฉบับ); ถ้านำไปใช้จริงต้องให้ Exam Setter / HR Process Owner ยืนยันใหม่
3. ความหมายอย่างเป็นทางการของ `open` และ `closed` จะต้องถูกนิยามใน `BUSINESS_GLOSSARY.md`; ยังไม่ประกาศนิยามในเอกสารนี้
4. AI Process Improvement Brief เป็นข้อมูลช่วยตรวจสอบ process เท่านั้น ไม่ใช่ automated HR decision

