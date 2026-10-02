# BUSINESS_GLOSSARY.md

Project: Consequence Process Dashboard  
Document ID: business_glossary  
Priority: P0  
Depends on: none

## Term Definitions

| Term | Official Definition | Common Misunderstanding | Authoritative Source |
|---|---|---|---|
| `case` | หนึ่งกรณีใน Consequence Process ที่ระบุด้วย `case_id` หนึ่งค่าใน dataset | อาจสับสนกับจำนวนเหตุการณ์ย่อยหรือจำนวนครั้งที่มีการติดตามภายในกรณีเดียว | Exam brief + mock CSV schema |
| `case_domain` | มิติที่ใช้เลือกดูกรณีระหว่างด้าน `behavior` และ `performance` ตามโจทย์ | อาจสับสนกับ `response_type` ซึ่งบอกลักษณะการตอบสนอง ไม่ใช่ด้านของกรณี | Exam brief + mock CSV column `case_domain` |
| `response_type` | ลักษณะการตอบสนองใน Consequence Process ซึ่งข้อมูล mockup ใช้แยกกรณีเชิงการยอมรับและการปรับปรุง | อาจสับสนกับสถานะของกรณีหรือ `stage` | Exam brief + mock CSV column `response_type` |
| `stage` | ขั้นตอนปัจจุบันที่ record ระบุว่ากรณีนั้นอยู่ ณ dataset snapshot | อาจถูกตีความเป็นประวัติทุกขั้นตอน ทั้งที่ mock CSV มีเพียงค่าขั้นตอนปัจจุบันต่อกรณี | Mock CSV column `stage` |
| `stage_entered_date` | วันที่ที่กรณีเข้าสู่ `stage` ปัจจุบันตาม record | อาจสับสนกับวันที่เปิดกรณีครั้งแรกหรือวันที่สร้าง record | Mock CSV column `stage_entered_date` |
| `owner` | ผู้รับผิดชอบที่ระบุอยู่ใน record ของกรณี ณ dataset snapshot | ไม่ควรตีความโดยอัตโนมัติว่าเป็นผู้ตัดสินใจทางวินัยหรือ KPI owner | Mock CSV column `owner` |
| `reference_date` | วันที่อ้างอิงคงที่ที่โจทย์กำหนดเพื่อใช้คำนวณอายุของกรณีในขั้นตอนปัจจุบัน และต้องใช้ค่าเดียวกันทุกการตรวจผล | อาจถูกแทนด้วย system date หรือวันที่เปิด dashboard ซึ่งจะทำให้ผลตรวจเปลี่ยนไป | Exam brief กำหนดให้ใช้วันที่อ้างอิงคงที่ แต่ไม่ได้ระบุค่า; ค่าที่ใช้ = `2026-10-01` — project-specific exam assumption ที่ผู้ทำข้อสอบยืนยัน (ไม่ใช่ industry standard และไม่ใช่ค่าที่ระบุมาใน exam brief ต้นฉบับ) |
| `days_in_current_stage` | จำนวนวันระหว่าง `stage_entered_date` กับ approved `reference_date` สำหรับกรณีที่ถูกจัดว่าเปิด ตาม business rule ที่ได้รับอนุมัติ | อาจสับสนกับอายุรวมตั้งแต่เริ่มกรณี หรือคำนวณด้วย system date | Exam brief; approved rule: calendar-day difference `DATE_DIFF('day', stage_entered_date, reference_date)` (ไม่รวมวันเริ่มต้น) — formula ใน `METRIC_SPEC.md` / `METRIC_LOGIC.md` |
| `open case` | คำธุรกิจสำหรับกรณีที่ยังต้องดำเนินการต่อใน Consequence Process | ไม่ใช่ทุก record ที่ `stage` ไม่ใช่ `closed` ต้องตีความเอง — ใช้ mapping ที่อนุมัติ: `stage IN ('reviewing', 'follow_up', 'collecting_info')` | Exam brief + approved rule (2026-10-02); project-specific approved business rule สำหรับงานสอบนี้ (ไม่ใช่ industry standard) |
| `closed case` | คำธุรกิจสำหรับกรณีที่กระบวนการถือว่าปิดแล้ว | ใช้ mapping ที่อนุมัติ: `stage = 'closed'` เป็นเกณฑ์เดียว | Exam brief + mock CSV + approved rule (2026-10-02); project-specific approved business rule สำหรับงานสอบนี้ (ไม่ใช่ industry standard) |
| `Top 3 longest-open cases` | รายการสามกรณีที่ผ่านเกณฑ์ `open case` และมี `days_in_current_stage` สูงสุดภายใต้ filter เดียวกัน | deterministic ด้วย ordering `days_in_current_stage DESC, case_id ASC` | Exam brief + approved tie-break (2026-10-02); project-specific approved business rule สำหรับงานสอบนี้ (ไม่ใช่ industry standard) |
| `Process Improvement Brief` | ร่างข้อสังเกตและข้อเสนอเพื่อช่วย HR ตรวจสอบและปรับปรุงกระบวนการจากข้อมูลภาพรวม โดยเป็น optional AI bonus | ไม่ใช่คำตัดสินทาง HR ไม่ใช่การประเมินบุคคล และไม่ใช่ automated disciplinary decision | Exam brief |

## Disputed Terms

คำต่อไปนี้เคยเป็น disputed term และได้รับ resolution แล้วเมื่อ 2026-10-02 โดยเป็น project-specific approved business rule สำหรับงานสอบนี้ (ไม่ใช่ industry standard) ที่ผู้รับผิดชอบงานสอบยืนยัน ไม่ใช่ industry standard และไม่ใช่ค่าที่ระบุใน exam brief ต้นฉบับ ห้ามนำไปใช้กับ production โดยไม่ผ่านการยืนยันจาก HR Process Owner จริง

| Disputed Term | Competing Definitions / Ambiguity | Official Resolution | Approval Date | Decision Owner |
|---|---|---|---|---|
| `open case` | (1) ทุก record ที่ `stage` ไม่ใช่ขั้นตอนปิด หรือ (2) ใช้สถานะ business แยกต่างหากซึ่งยังไม่มีใน CSV | resolved: `stage IN ('reviewing', 'follow_up', 'collecting_info')` | 2026-10-02 | HR Process Owner (project decision for exam) |
| `closed case` | (1) `stage` ที่มีชื่อสื่อว่าปิด หรือ (2) ต้องมีเงื่อนไขอื่นประกอบก่อนถือว่าปิด | resolved: `stage = 'closed'` | 2026-10-02 | HR Process Owner (project decision for exam) |
| `days_in_current_stage` | (1) date difference แบบ calendar-day หรือ (2) business-day; รวม/ไม่รวมวันเริ่มต้น | resolved: calendar-day difference ไม่รวมวันเริ่มต้น `DATE_DIFF('day', stage_entered_date, reference_date)` โดย `reference_date = 2026-10-01` (project-specific exam assumption ที่ส่งเป็น runtime/config input) | 2026-10-02 | HR Process Owner / Exam Setter (project decision for exam) |
| `Top 3 longest-open cases` tie-break | เมื่อหลายกรณีมีอายุเท่ากัน อาจเรียงตาม `case_id`, `stage_entered_date`, หรือกติกาอื่น | resolved: `days_in_current_stage DESC, case_id ASC` | 2026-10-02 | HR Process Owner / Exam Setter (project decision for exam) |

### Resolution Gate

ก่อน certify metrics ที่ใช้ `open case`, `closed case`, `days_in_current_stage` หรือ Top 3 ต้องมี:
- นิยามที่อนุมัติแล้ว — ครบ (2026-10-02)
- `approval_date` จริง — ครบ (2026-10-02)
- decision owner ที่ยืนยัน — ครบ (project decision for exam)
- การอัปเดต Change Log ด้านล่าง — ครบ

## Change Log

บันทึกการอนุมัติ definition สำหรับงานสอบนี้ (ไม่ใช่การแก้ไขสูตร metric)

| Changed Term | Change Date | Old Definition | New Definition | Reason |
|---|---|---|---|---|
| `open case` | 2026-10-02 | unresolved (`null`) | `stage IN ('reviewing', 'follow_up', 'collecting_info')` | project-specific approved business rule for exam |
| `closed case` | 2026-10-02 | unresolved (`null`) | `stage = 'closed'` | project-specific approved business rule for exam |
| `days_in_current_stage` | 2026-10-02 | unresolved (`null`) | calendar-day difference, `reference_date = 2026-10-01` | project-specific approved business rule / assumption for exam |
| `Top 3 longest-open cases` tie-break | 2026-10-02 | unresolved (`null`) | `days_in_current_stage DESC, case_id ASC` | project-specific approved business rule for exam |

การเปลี่ยน resolution ในอนาคตต้องเพิ่มรายการเปลี่ยนแปลงพร้อมวันที่มีผลจริง และห้ามย้อนแก้ประวัติโดยไม่มีหลักฐานการอนุมัติ

## Enumeration Registry

Registry นี้เป็น **index เท่านั้น**: แสดงชื่อ enum และเอกสารเจ้าของเพียงหนึ่งเดียว ห้ามประกาศค่า enum ในตารางนี้

| Enum | Owner Document |
|---|---|
| `data_literacy_level` | `STAKEHOLDERS.md` |
| `data_need_priority` | `STAKEHOLDERS.md` |
| `scd_type` | `DATA_MODEL_SPEC.md` |
| `pdpa_classification` | `DATA_MODEL_SPEC.md` |
| `rule_severity` | `DATA_QUALITY.md` |
| `dataset_criticality` | `SLA_FRESHNESS.md` |
| `chart_type` | `VIZ_DESIGN_SPEC.md` |
| `complexity_level` | `VIZ_DESIGN_SPEC.md` |
| `metric_status` | `METRIC_SPEC.md` |
| `model_status` | `AI_MODEL_SPEC.md` |
| `work_item_status` | `TASKS.md` |
| `incident_severity` | `RUNBOOK.md` |
| `change_type` | `ANALYTICS_CHANGELOG.md` |

### Registry Rules

- enum ทุกตัวมี owner document เพียงหนึ่งเดียว
- เอกสารที่ไม่ใช่ owner อ้างอิง enum ด้วยชื่อเท่านั้น และไม่ประกาศค่าซ้ำ
- Registry นี้ต้องถูก reconcile อีกครั้งเมื่อ owner documents ถูกสร้างครบ
- `data_need_priority`, `dataset_criticality` และ `incident_severity` เป็นคนละแกนและห้ามนำมารวมเป็น scale เดียว
