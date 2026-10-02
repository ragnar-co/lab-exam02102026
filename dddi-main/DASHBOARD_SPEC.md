# DASHBOARD_SPEC.md

Project: Consequence Process Dashboard  
Document ID: dashboard_spec  
Priority: P0  
Depends on: METRIC_SPEC.md, KPI_DICTIONARY.md, DATA_MODEL_SPEC.md, STAKEHOLDERS.md, TESTING_STRATEGY.md, VIZ_DESIGN_SPEC.md

## Dashboard Inventory

| Dashboard | Purpose | Target User | Data Source |
|---|---|---|---|
| `consequence_process_dashboard` | ติดตามจำนวน case, สถานะเปิด/ปิด, bottleneck ตาม `stage`, case aging และ Top 3 longest-open cases | HR / Consequence Process Owner | `mart_consequence_case_metrics`, `mart_consequence_case_aging`, `mart_top3_longest_open_cases` |

Core dashboard นี้เป็น dashboard หลักเพียงหนึ่งตัวในขอบเขตข้อสอบ เพื่อให้ทุก metric ใช้ filter context และ semantic layer เดียวกัน

## Dashboard Profiles

### `consequence_process_dashboard`

- **Name:** Consequence Process Dashboard
- **Purpose:** ช่วย HR ตรวจภาพรวมของ Consequence Process และระบุกรณีที่ควรติดตาม process ก่อน
- **Target User:** HR / Consequence Process Owner
- **Data Literacy:** อ้าง `data_literacy_level` จาก `STAKEHOLDERS.md`
- **Data Source:** DuckDB semantic/mart views ที่นิยามใน `METRIC_LOGIC.md`
- **Chart Inventory:**
  - Total Cases → `kpi_card`
  - Closed Cases → `kpi_card`
  - Open Cases → `kpi_card`
  - Open Cases by Stage → `bar`
  - Open Case Aging → `table`
  - Top 3 Longest Open Cases → `table`
- **Acceptance Criteria:**
  - component ทุกตัว render ได้
  - metric values ตรงกับ semantic/mart output
  - `case_domain` filter sync ทุก core component
  - หาก runtime input ที่จำเป็นยังไม่พร้อม ให้แสดง pending/unavailable state ไม่ใช้ค่า default สมมติ
  - Top 3 ใช้ ordering จาก `METRIC_LOGIC.md`
  - invalid CSV run ต้องไม่ overwrite previous valid published state
  - deployment smoke test ผ่านตาม `TESTING_STRATEGY.md`

## Metric Coverage Matrix

| KPI | Metric | Dashboard Component | Covered |
|---|---|---|---|
| `consequence_process_completion_rate` | `metric_total_cases` | Total Cases KPI card | yes |
| `consequence_process_completion_rate` | `metric_closed_cases` | Closed Cases KPI card | yes |
| `open_case_rate` | `metric_open_cases` | Open Cases KPI card | yes |
| `open_case_rate` | `metric_open_cases_by_stage` | Open Cases by Stage bar chart | yes |
| `open_case_aging` | `metric_days_in_current_stage` | Open Case Aging table | yes |
| `open_case_aging` | `metric_top_3_longest_open_cases` | Top 3 table | yes |

ทุก KPI ใน `KPI_DICTIONARY.md` มี representation อย่างน้อยหนึ่งจุดใน dashboard นี้

Dashboard ห้ามคำนวณสูตร metric ซ้ำเอง ต้อง consume output จาก metric layer เท่านั้น

## Drill-down Logic

### Global Filter

- mandatory user filter: `case_domain`
- supported selections มาจาก source contract
- ต้องมี state สำหรับ all/unfiltered
- KPI cards, stage chart, aging table และ Top 3 ต้องใช้ filter context เดียวกัน

### Drill-down Paths

| From | Interaction | To |
|---|---|---|
| Total Cases card | click | case-level table ภายใต้ filter ปัจจุบัน |
| Closed Cases card | click | closed-case table (business rule approved) |
| Open Cases card | click | open-case table (business rule approved) |
| Open Cases by Stage bar | click stage | case-level table filtered by selected `stage` |
| Aging table | sort | sort by `metric_days_in_current_stage` |
| Top 3 table | read-only ranking | exact ranked rows from metric mart |

### Guard Rails

- chart types และ interaction ต้องตรง `VIZ_DESIGN_SPEC.md`
- animation disabled
- client-side sorting ห้ามเปลี่ยน business definition ของ Top 3
- `reference_date` ที่ใช้ = `2026-10-01` (project-specific exam assumption) ผ่าน runtime/config input
- หาก `reference_date` เป็น `null` ให้ aging components แสดง pending/unavailable
- ห้ามใช้ `CURRENT_DATE`
- optional filter ที่เพิ่มภายหลังต้องไม่สร้าง metric formula ใหม่ใน dashboard code

## Refresh Schedule

Dashboard refresh ผูกกับ successful metric publication ของ pipeline run เดียวกัน

| Layer | Trigger | Dashboard Behavior |
|---|---|---|
| CSV ingestion | on-demand | ยังไม่ publish dashboard run ใหม่ |
| semantic model ready | after valid ingestion | รอ metric marts |
| metric marts ready | after semantic model | dashboard สามารถ refresh ไป run ใหม่ |
| invalid/partial run | any failure | คง previous valid published state |

- **Fixed cron:** `null`
- **Calibration Owner:** Product Owner / HR Process Owner
- **Freshness tolerance:** อ้าง `SLA_FRESHNESS.md`; ค่าที่ยังไม่ calibrate ไม่ถูกตั้งในเอกสารนี้
- dashboard ต้องแสดง run identifier / data timestamp เมื่อ implementation รองรับ
