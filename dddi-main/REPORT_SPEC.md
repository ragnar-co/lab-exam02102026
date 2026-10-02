# REPORT_SPEC.md

Project: Consequence Process Dashboard  
Document ID: report_spec  
Priority: P1  
Depends on: DASHBOARD_SPEC.md, KPI_DICTIONARY.md, METRIC_SPEC.md, STAKEHOLDERS.md, SLA_FRESHNESS.md

## Report Profiles

### `consequence_process_summary_report`

- **Purpose:** สรุปภาพรวม Consequence Process แบบ static snapshot สำหรับ HR review
- **Audience:** HR / Consequence Process Owner
- **Format:** PDF หรือ HTML export จาก metric snapshot เดียวกับ dashboard
- **Source:** `mart_consequence_case_metrics`, `mart_consequence_case_aging`, `mart_top3_longest_open_cases`
- **Contents:**
  - Total Cases
  - Closed Cases
  - Open Cases
  - Open Cases by Stage
  - Top 3 Longest Open Cases
  - active `case_domain` filter context
  - `reference_date` ที่ใช้คำนวณ aging
  - run identifier / data timestamp
- **Static Snapshot Rule:** report ต้อง freeze metric values จาก run เดียวกันทั้งหมด
- **Late/Unavailable Rule:** หาก data run ใหม่ยังไม่พร้อม ให้ส่ง previous valid report พร้อมระบุว่าเป็น previous valid snapshot หรือไม่ส่ง report ใหม่ตาม policy ที่ owner อนุมัติ; ห้ามผสมค่าจากหลาย run
- **AI Bonus:** Process Improvement Brief สามารถแนบเป็น optional section เมื่อ feature เปิดใช้งานและ generation สำเร็จ

## KPI Coverage

| KPI | Covered By Report | Report Section | Status |
|---|---|---|---|
| `consequence_process_completion_rate` | `consequence_process_summary_report` | Total / Closed summary | covered |
| `open_case_rate` | `consequence_process_summary_report` | Open summary + stage distribution | covered |
| `open_case_aging` | `consequence_process_summary_report` | Top 3 longest-open cases | covered |

ทุก KPI ใน `KPI_DICTIONARY.md` ถูกครอบคลุมอย่างน้อยหนึ่งครั้งใน report

Metric labels ต้องอ้างชื่อจาก `METRIC_SPEC.md` และห้ามสร้างสูตร metric ใน report layer

## Distribution Schedule

### Current Schedule Status

โจทย์ไม่ได้กำหนด recurring report cadence จริง จึงไม่สร้าง daily/weekly/monthly schedule ขึ้นมาเอง

- **Cadence:** `null`
- **Distribution Time:** `null`
- **Deadline:** `null`
- **Calibration Owner:** HR Process Owner / Product Owner
- **Distribution Channel:** `null`
- **Calibration Owner:** HR Process Owner / Company Platform Owner

### Scheduling Rule

เมื่อ owner กำหนด schedule จริง:
1. deadline ต้องอยู่ **หลัง** data availability ตาม `SLA_FRESHNESS.md`
2. report ต้องใช้ successful metric run เดียวกัน
3. หากพลาด deadline ต้องมี consequence ที่ชัดเจน เช่น alert owner, delay distribution หรือใช้ previous valid snapshot ตาม approved policy
4. ห้ามส่ง partial report ที่บาง metric มาจาก run ใหม่และบาง metric มาจาก run เก่า

### Exam Use

สำหรับข้อสอบ สามารถ generate report แบบ on-demand เพื่อใช้ตรวจผลได้ โดยไม่ถือเป็น recurring operational distribution schedule

## Template Definitions

### Standard Report Template

```text
Consequence Process Summary
Run ID: <run_id>
Reference Date: <reference_date>
Filter: <case_domain/all>

1. Executive Summary
   - Total Cases
   - Closed Cases
   - Open Cases

2. Open Cases by Stage
   - stage
   - case count

3. Case Aging
   - Top 3 Longest Open Cases
   - case_id
   - stage
   - owner
   - days_in_current_stage

4. Data Status
   - validation status
   - metric status
   - data timestamp
   - pending runtime inputs if any (none expected: approved values are in config)

5. Optional AI Process Improvement Brief
   - generated_at
   - input run_id
   - brief text
```

### Template Rules

- report ต้องระบุ `reference_date` อย่างชัดเจนเมื่อมี aging metric (งานสอบนี้ใช้ `2026-10-01` เป็น project-specific exam assumption)
- unavailable metric ต้องแสดงว่า unavailable/pending ไม่แทนด้วย `0`
- static export ต้องรักษา filter context ของ report
- Top 3 ordering ต้องตรง `METRIC_LOGIC.md`
- report styling อ้างหลัก readability จาก `VIZ_DESIGN_SPEC.md`
- report ไม่ใช่ dashboard และไม่มี requirement เรื่อง interactive drill-down
