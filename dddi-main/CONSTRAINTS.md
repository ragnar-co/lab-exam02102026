# CONSTRAINTS.md

Project: Consequence Process Dashboard
Document ID: constraints
Priority: P0
Depends on: none

## Platform & Tooling Constraints

- **Analytics track:** ต้องใช้ `ddd-data-analytics` เพียงหนึ่ง track สำหรับงานนี้
- **Input format:** ระบบต้องรับข้อมูลจาก CSV mockup ที่ผู้ใช้ให้มา
- **Analytics store:** เลือกใช้ `DuckDB` สำหรับงานสอบนี้ เนื่องจากโจทย์อนุญาต `SQLite3` หรือ `DuckDB` และต้องเลือก implementation ที่ทำงานได้ภายในเวลาจำกัด
- **Dashboard / application framework:** `null`
  - **Calibration owner:** Candidate / Implementation Owner
  - **Reason:** โจทย์ไม่ได้ระบุ framework บังคับ
- **BI licensing tier / seat limit:** `null`
  - **Calibration owner:** Company Platform Owner
  - **Reason:** ไม่มีข้อมูล licensing ในโจทย์
- **Transform tool / version:** `null`
  - **Calibration owner:** Candidate / Implementation Owner
  - **Reason:** โจทย์ไม่ได้บังคับ dbt หรือ transformation framework ใด
- **Coding agent:** ต้องใช้ Claude Code หรือ Codex ตามทรัพยากรที่บริษัทให้
- **Token constraint:** ใช้ Token ที่มีอยู่เท่านั้น ห้ามเติมเพิ่ม
- **Deployment target:** ต้อง deploy ผ่าน Coolify และเปิดใช้งานได้จริง
- **Source-control target:** ต้อง push งานไป repository ของบริษัท
- **Required connectors:** ไม่มี connector ภายนอกที่ยืนยันสำหรับ core dashboard; AI endpoint เป็น optional integration สำหรับ bonus

## Scale Constraints

- **Observed mock dataset:** CSV mockup มีข้อมูลระดับหลายหมื่น records และต้อง ingest ได้สำเร็จใน local analytics store
- **Largest fact table row count at 1 year:** `null`
  - **Calibration owner:** HR Process Owner / Data Owner
- **Largest fact table row count at 3 years:** `null`
  - **Calibration owner:** HR Process Owner / Data Owner
- **Source API rate limit for core dashboard:** not applicable — core source เป็น CSV
- **AI endpoint rate limit / quota:** `null`
  - **Calibration owner:** Company AI Platform Owner
  - **Scope:** ใช้เฉพาะ bonus AI workflow
- **Warehouse concurrent-query quota:** not applicable to external warehouse tier in the exam implementation because the selected analytics store is embedded `DuckDB`
- **Application concurrency expectation:** `null`
  - **Calibration owner:** Company Platform Owner
- **Scale rule:** ห้ามออกแบบ threshold, partition strategy, storage forecast หรือ cost projection จากการเดาปริมาณอนาคต จนกว่าจะมีค่าที่ calibrate แล้ว

## Compliance & Residency Constraints

- **Data residency region:** `null`
  - **Calibration owner:** Company Security / Compliance Owner
- **Legal basis for collection under PDPA:** `null`
  - **Calibration owner:** HR Data Owner / Data Protection Owner
- **Industry standard required before launch:** `null`
  - **Calibration owner:** Company Security / Compliance Owner
- **HR data sensitivity:** ข้อมูล Consequence Process ต้องถือเป็นข้อมูลธุรกิจด้าน HR ที่ต้องตรวจสอบ classification อย่างเป็นทางการใน `DATA_MODEL_SPEC.md` และข้อกำหนด access control ภายหลังใน `DATA_GOVERNANCE.md`
- **Scope boundary:** เอกสารนี้ไม่กำหนด retention period, access-control policy หรือ ongoing monthly cost ceiling เพราะหัวข้อเหล่านั้นเป็นความรับผิดชอบของ `DATA_GOVERNANCE.md`
- **AI boundary:** Bonus AI workflow ต้องใช้ข้อมูลภาพรวมหรือ aggregate ที่จำเป็นต่อ Process Improvement Brief และไม่ควรถูกใช้เพื่อตัดสินโทษหรือประเมินบุคคลโดยอัตโนมัติ

## Project Budget & Timeline

- **Delivery time limit:** 120 นาทีสำหรับสร้าง ตรวจสอบ push และ deploy งานให้เปิดใช้งานได้
- **Delivery budget ceiling:** `null`
  - **Calibration owner:** Exam Setter / Project Sponsor
  - **Constraint:** ห้ามตีความข้อจำกัด Token เป็นงบการเงินของโปรเจกต์
- **Go-live condition:** ภายในกรอบ 120 นาที ระบบ core ต้องเปิดใช้งานผ่าน Coolify ได้
- **Exact go-live timestamp:** `null`
  - **Calibration owner:** Exam Setter
- **Mandatory core scope before go-live:**
  - รับและ validate CSV
  - บันทึกข้อมูลลง `DuckDB`
  - แสดงจำนวนกรณีทั้งหมด
  - แสดงจำนวนกรณีปิดและกรณีเปิด
  - แสดงจำนวนกรณีแยกตาม `stage`
  - คำนวณจำนวนวันที่กรณีเปิดอยู่ในขั้นตอนปัจจุบันโดยใช้ `reference_date` จากโจทย์
  - แสดง 3 กรณีที่อยู่ในขั้นตอนนานที่สุด
  - filter ตาม `case_domain` ระหว่าง `behavior` และ `performance`
  - มี Test หรือ Validation ที่ผ่าน
  - push ไป company repository
  - deploy ผ่าน Coolify
- **Phased rollout:** Bonus AI Process Improvement Brief ทำหลัง core scope, validation และ deployment requirements พร้อมแล้ว
- **Reference date value:** `2026-10-01` — project-specific exam assumption ที่ผู้ทำข้อสอบยืนยัน (ไม่ใช่ industry standard และไม่ใช่ค่าที่ระบุมาใน exam brief ต้นฉบับ)
  - **Calibration owner:** Exam Setter / HR Process Owner (ยืนยันใหม่หากนำไปใช้จริง)
  - **Provided via:** runtime/config input (`config/runtime_config.json` หรือ `CPD_REFERENCE_DATE`) ไม่ hard-code ใน code
  - **Constraint:** ห้ามใช้ system date แทนโดยอัตโนมัติ

## Integration Constraints

- **Core source integration:** CSV upload / CSV file ingestion
- **Core database integration:** embedded `DuckDB`
- **Company repository:** repository URL / authentication details = `null`
  - **Calibration owner:** Company Repository Administrator / Exam Setter
- **Coolify:** target project, environment, domain และ deployment credentials = `null`
  - **Calibration owner:** Company Platform Owner / Exam Setter
- **AI endpoint for bonus:** endpoint URL, authentication method, model identifier และ quota = `null`
  - **Calibration owner:** Company AI Platform Owner
- **AI output persistence:** หากทำ bonus ต้องบันทึก Process Improvement Brief และเรียกกลับมาแสดงในแอปได้จริง
- **Contract stability:** CSV schema ที่ได้รับเป็น input contract เบื้องต้นสำหรับข้อสอบ แต่ schema validation และ breaking-change policy ต้องระบุใน `DATA_CONTRACT.md` เมื่อ dependency พร้อม
- **API compatibility:** ไม่มี external API ที่จำเป็นต่อ core dashboard; AI API เป็น optional bonus และต้องใช้เฉพาะ endpoint/โควตาที่บริษัทจัดให้
