# KPI_DICTIONARY.md

Project: Consequence Process Dashboard
Document ID: kpi_dictionary
Priority: P0
Depends on: none

## KPI Catalog

### KPI-01 — Consequence Process Completion Rate

- **Identifier:** `consequence_process_completion_rate`
- **Level:** Company
- **Definition:** สัดส่วนกรณี Consequence Process ที่อยู่ในสถานะปิดเมื่อเทียบกับกรณีทั้งหมดใน dataset snapshot เดียวกัน
- **Business Impact:** ใช้สะท้อนความสามารถโดยรวมของกระบวนการในการพากรณีไปสู่การปิด หากค่าลดลงควรตรวจว่ามี backlog เพิ่มขึ้นในขั้นตอนใด
- **Owner:** HR Process Owner
- **Target:** `null`
- **Calibration Owner:** HR Process Owner / Project Sponsor
- **Measurement Frequency:** on-demand per validated dataset snapshot
- **OKR / iKPI Mapping:** `null`
- **Calibration Owner for OKR / iKPI Mapping:** HR Process Owner / Project Sponsor
- **Notes:** ไม่ใช้ KPI นี้เพื่อประเมินบุคคลหรือสรุปผลทางวินัยโดยอัตโนมัติ

### KPI-02 — Open Case Rate

- **Identifier:** `open_case_rate`
- **Level:** Department
- **Definition:** สัดส่วนกรณีที่ยังเปิดอยู่เมื่อเทียบกับกรณีทั้งหมดใน dataset snapshot เดียวกัน
- **Business Impact:** ช่วย HR เห็นขนาดของ workload ที่ยังต้องติดตาม และใช้ drill-down ไปยัง `stage` เพื่อหาจุดที่มีกรณีค้างอยู่
- **Owner:** HR Process Owner
- **Target:** `null`
- **Calibration Owner:** HR Process Owner
- **Measurement Frequency:** on-demand per validated dataset snapshot
- **OKR / iKPI Mapping:** `null`
- **Calibration Owner for OKR / iKPI Mapping:** HR Process Owner / Project Sponsor
- **Parent KPI:** `consequence_process_completion_rate`

### KPI-03 — Open Case Aging

- **Identifier:** `open_case_aging`
- **Level:** Team
- **Definition:** ระยะเวลาที่กรณีเปิดอยู่ใน `current_stage` เมื่อเทียบกับ `reference_date` ที่โจทย์กำหนด ใช้เพื่อตรวจกรณีที่ค้างนานและจัดลำดับการติดตาม process
- **Business Impact:** ช่วยระบุกรณีที่อาจติดค้างในขั้นตอนปัจจุบันและทำให้ HR เห็นว่าควรตรวจสอบ process ตรงไหนก่อน
- **Owner:** HR Operations / Case Management Role
- **Target:** `null`
- **Calibration Owner:** HR Process Owner
- **Measurement Frequency:** on-demand per validated dataset snapshot using the approved `reference_date`
- **OKR / iKPI Mapping:** `null`
- **Calibration Owner for OKR / iKPI Mapping:** HR Process Owner / Project Sponsor
- **Parent KPI:** `open_case_rate`
- **Reference Date:** `2026-10-01` — project-specific exam assumption ที่ผู้ทำข้อสอบยืนยัน (ไม่ใช่ industry standard และไม่ใช่ค่าที่ระบุมาใน exam brief ต้นฉบับ)
- **Reference Date Owner:** Exam Setter / HR Process Owner

## KPI Hierarchy (CEO to Team Level)

| Level | KPI | Parent KPI | Accountability |
|---|---|---|---|
| Company | `consequence_process_completion_rate` | none | HR Process Owner |
| Department | `open_case_rate` | `consequence_process_completion_rate` | HR Process Owner |
| Team | `open_case_aging` | `open_case_rate` | HR Operations / Case Management Role |

### Parent-Child Logic

- `consequence_process_completion_rate` เป็น outcome ระดับบนที่สะท้อนสัดส่วนกรณีซึ่งปิดแล้ว
- `open_case_rate` เป็น driver ที่แสดงสัดส่วนกรณีซึ่งยังต้องดำเนินการต่อ และเป็นส่วนเติมเต็มของภาพรวม completion
- `open_case_aging` เป็น operational KPI ที่ช่วยตรวจว่ากรณีเปิดค้างอยู่ใน `current_stage` นานเพียงใด
- จำนวนกรณีทั้งหมด, จำนวนกรณีเปิด/ปิด, จำนวนกรณีแยกตาม `stage`, และ Top 3 longest-open cases จะถูกนิยามเป็น metrics ใน `METRIC_SPEC.md`; เอกสารนี้ไม่ประกาศสูตร metric ซ้ำ

## Measurement Frequency

| KPI | Frequency | Measurement Trigger | Time Basis |
|---|---|---|---|
| `consequence_process_completion_rate` | on-demand | หลัง CSV ผ่าน validation และโหลดเข้า `DuckDB` สำเร็จ | dataset snapshot |
| `open_case_rate` | on-demand | หลัง CSV ผ่าน validation และโหลดเข้า `DuckDB` สำเร็จ | dataset snapshot |
| `open_case_aging` | on-demand | หลัง CSV ผ่าน validation และมี `reference_date` ที่ยืนยันแล้ว | `stage_entered_date` ถึง approved `reference_date` |

### Frequency Constraint

โจทย์ไม่ได้ระบุ daily, weekly หรือ monthly operating cadence สำหรับข้อมูลจริง จึงไม่กำหนด cadence เหล่านั้นขึ้นมาเอง งานสอบนี้ใช้การคำนวณแบบ on-demand ต่อ dataset snapshot เพื่อให้ผลตรวจ deterministic

## KPI Owners

| KPI | Owner Role | Target Status | Calibration Owner |
|---|---|---|---|
| `consequence_process_completion_rate` | HR Process Owner | `null` — not calibrated | HR Process Owner / Project Sponsor |
| `open_case_rate` | HR Process Owner | `null` — not calibrated | HR Process Owner |
| `open_case_aging` | HR Operations / Case Management Role | `null` — not calibrated | HR Process Owner |

### Ownership Rules

- Owner ต้องเป็น role ไม่ใช่ชื่อบุคคล
- KPI target ทุกตัวต้องเป็น numeric เมื่อได้รับการอนุมัติแล้ว
- ณ เวอร์ชันข้อสอบนี้ไม่มี target ที่ได้รับการยืนยัน จึงใช้ `null` พร้อม calibration owner ตาม governance rule
- ห้ามใช้ตัวเลขจาก mock dataset เป็น KPI target หรือมาตรฐาน
- ค่า `reference_date` ไม่ใช่ KPI target; ใช้ `2026-10-01` เป็น project-specific exam assumption (ไม่ใช่ industry standard)
- KPI definition ในไฟล์นี้เป็น parent ของ metrics ที่จะสร้างใน `METRIC_SPEC.md`

## Readiness Note

เอกสารนี้พร้อมใช้เป็น upstream สำหรับการออกแบบ metric structure แต่ **ยังไม่ผ่าน KPI target readiness** เพราะ target และ OKR / iKPI mapping ยังไม่มีข้อมูลที่ได้รับการยืนยันจาก business owner การทำข้อสอบ core dashboard สามารถเดินหน้าต่อได้โดยไม่ใช้ target เพื่อคำนวณจำนวนกรณีและ case aging แต่ห้ามสร้าง action threshold หรือ performance judgement จาก target ที่ยังเป็น `null`
