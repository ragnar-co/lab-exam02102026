# VIZ_DESIGN_SPEC.md

Project: Consequence Process Dashboard  
Document ID: viz_design_spec  
Priority: P1  
Depends on: STAKEHOLDERS.md, METRIC_SPEC.md

## Chart Type Matrix

### `chart_type` Enum

`VIZ_DESIGN_SPEC.md` เป็นเอกสารเจ้าของ `chart_type`

ค่าที่ใช้ในโปรเจกต์นี้:

- `kpi_card`
- `bar`
- `table`

### `complexity_level` Enum

`VIZ_DESIGN_SPEC.md` เป็นเอกสารเจ้าของ `complexity_level`

- `basic`
- `intermediate`
- `advanced`

### Matrix

| Metric / Output | Metric Type | Recommended `chart_type` | `complexity_level` | Grain Consideration | Anti-pattern Reference |
|---|---|---|---|---|---|
| `metric_total_cases` | single-value count | `kpi_card` | `basic` | 1 validated dataset snapshot × filter context | `pending source` — required `references/data-to-viz/*` corpus not present in current pack |
| `metric_closed_cases` | single-value count | `kpi_card` | `basic` | same snapshot/filter context as Total Cases | `pending source` |
| `metric_open_cases` | single-value count | `kpi_card` | `basic` | same snapshot/filter context as Total Cases | `pending source` |
| `metric_open_cases_by_stage` | categorical count | `bar` | `basic` | 1 bar per `stage`; sort consistently | `pending source` — expected source `references/data-to-viz/data-to-viz-barplot.md` |
| `metric_days_in_current_stage` | row-level numeric measure | `table` | `basic` | 1 case × approved `reference_date`; show exact days with case context | `pending source` |
| `metric_top_3_longest_open_cases` | ranking | `table` | `basic` | at most 3 ranked cases under same filter context | `pending source` |

### Chart Selection Rationale

- KPI cards ใช้กับ metric ที่โจทย์ต้องการเห็นเป็นจำนวนรวมทันที
- bar ใช้กับ `metric_open_cases_by_stage` เพราะเป็น categorical count ตาม `stage`
- table ใช้กับ case-aging และ Top 3 เพราะผู้ใช้ต้องเห็น exact case context เช่น `case_id`, `stage`, `owner`, `days_in_current_stage`
- ไม่มี time-series metric ใน `METRIC_SPEC.md` ปัจจุบัน จึงไม่ใช้ line chart
- ไม่มี heatmap/scatter/multi-axis/animation ใน core dashboard

### Reference Limitation

Template กำหนดว่า anti-pattern ต้องอ้างจาก `references/data-to-viz/data-to-viz-*.md` จริง
แต่ reference corpus ดังกล่าวไม่ได้อยู่ใน source pack ที่ได้รับในโปรเจกต์นี้

ดังนั้น:
- chart recommendation ด้านบนอิง metric shape และข้อกำหนดจาก template
- anti-pattern เฉพาะ chart จะยังไม่ถือว่า verified
- ก่อน production sign-off ต้องเติม source reference จาก corpus ที่ template ระบุ
- ห้ามแต่ง anti-pattern จากความจำเพื่อให้ช่องดูครบ

## Color & Theme Spec

เป้าหมายของ theme คือให้ dashboard อ่านง่ายในบริบท HR และไม่ใช้สีเพียงอย่างเดียวเพื่อสื่อสถานะ

### Palette

ธีมปัจจุบัน (2026-10-02): Ragnar red + white + warm cream — เปลี่ยนเฉพาะ presentation ไม่เปลี่ยน metric/logic

Primary palette:
- `#8F1D2C` — primary red (accent, active state, primary series)
- `#6F1420` — dark red (headings, hover)
- `#F7F1E8` — warm cream (page background)
- `#FFF9F2` — soft cream (cards / highlighted sections)
- `#FFFFFF` — white (cards, table surface)
- `#222222` — text
- `#666666` — secondary text
- `#E6DDD2` — border

Semantic intent:
- positive / completed: `#3F7D4E`
- caution / attention: `#A15A1C`
- neutral / unavailable: `#8A8178`
- primary analytic series: `#8F1D2C`
- secondary analytic series: `#B5495B`

Semantic colors ต้องใช้พร้อม text label/icon/status wording ไม่ใช้สีเป็นสัญญาณเดียว
Contrast: text `#222222` และ `#666666` บน `#F7F1E8`/`#FFFFFF`, และข้อความขาวบน `#8F1D2C` ผ่าน WCAG 2.1 AA

### Font Rules

- ใช้ system sans-serif stack เพื่อให้ deploy ง่าย และมี fallback ที่รองรับภาษาไทย (Tahoma, Leelawadee UI, Noto Sans Thai, Sarabun, Thonburi) สำหรับ UI สองภาษา TH/EN
- title ต้องเด่นกว่าค่า metric แต่ไม่ใช้ decorative font
- table body ต้องอ่านได้ชัดบน desktop
- ตัวเลข KPI ใช้ font weight สูงกว่า label
- ห้ามลด font size เพื่อบีบข้อมูลจำนวนมากลง chart; ให้ใช้ scroll/table แทน

### `viz_theme` Python Module

```python
COLOR_PALETTE = {
    "primary": "#8F1D2C",
    "dark": "#6F1420",
    "secondary": "#B5495B",
    "positive": "#3F7D4E",
    "warning": "#A15A1C",
    "neutral": "#8A8178",
    "accent": "#C9A27A",
    "cream": "#F7F1E8",
    "card": "#FFF9F2",
    "white": "#FFFFFF",
    "text": "#222222",
    "text_secondary": "#666666",
    "border": "#E6DDD2",
}

FONT_RULES = {
    "family": "Arial, Helvetica, Tahoma, 'Leelawadee UI', 'Noto Sans Thai', Sarabun, Thonburi, sans-serif",
    "title_size": 32,
    "subtitle_size": 14,
    "body_size": 14,
    "kpi_value_size": 30,
    "kpi_label_size": 14,
}

CHART_DEFAULTS = {
    "show_legend": False,
    "show_grid": True,
    "animation": False,
    "responsive": True,
    "empty_state_text": "No data available for the current filter.",
}
```

Dashboard code สามารถคัดลอก fenced block นี้ไปเป็น `viz_theme.py`
โดยต้องคง exports `COLOR_PALETTE`, `FONT_RULES`, `CHART_DEFAULTS` ครบ

## Interaction Spec

### Global Filter

**Control:** `case_domain`

User ต้องเลือกดู:
- `behavior`
- `performance`

และสามารถกลับสู่ unfiltered/all state ได้

Filter ต้อง sync พร้อมกันกับ:
- Total Cases card
- Closed Cases card
- Open Cases card
- Open Cases by Stage chart
- case-aging table
- Top 3 table

ห้ามมี component ใดใช้ population คนละ filter context โดยไม่มี label ชัดเจน

### `kpi_card`

**Tooltip**
- metric name
- filter context ปัจจุบัน
- dataset/run identifier เมื่อ available
- metric status เมื่อยัง `draft`

**Click / Drill-down**
- Total Cases → case-level table ภายใต้ filter ปัจจุบัน
- Closed Cases → closed-case table เมื่อ closed rule approved
- Open Cases → open-case table เมื่อ open rule approved

**Animation**
- disabled

### `bar`

**Tooltip**
- `stage`
- exact case count
- active `case_domain` filter

**Click / Drill-down**
- click bar → filter case table ให้เหลือ `stage` ที่เลือก
- drill-down target = case-level table

**Cross-chart Sync**
- selected `stage` ต้อง apply กับ case-level table
- KPI cards ไม่ต้องถูก recalculate จาก click-on-bar เว้นแต่ Dashboard Spec กำหนด explicit cross-filter ภายหลัง

**Animation**
- disabled

### `table`

**Displayed case-aging fields**
- `case_id`
- `case_domain`
- `response_type`
- `stage`
- `stage_entered_date`
- `owner`
- `metric_days_in_current_stage`

**Interaction**
- sortable by `metric_days_in_current_stage`
- Top 3 table ใช้ ordering จาก `METRIC_LOGIC.md` เท่านั้น
- ห้ามให้ client-side sort เปลี่ยน business definition ของ Top 3
- exact row drill-down beyond current dataset = not available in core scope

**Tooltip**
- ใช้ column header helper text เมื่อชื่อ field ต้องอธิบาย
- ไม่ซ่อนค่าหลักไว้เฉพาะ tooltip

**Animation**
- disabled

### Pending / Unavailable State

เมื่อ `reference_date` หรือ approved open/closed rule ยังไม่พร้อม:
- component ที่พึ่ง input นั้นต้องแสดง unavailable/pending state
- ห้ามแสดง `0` เพื่อแทน “ยังคำนวณไม่ได้”
- ห้ามใช้ current system date แทน

## Accessibility Guidelines

### WCAG Target

Target: WCAG 2.1 AA

### Color and Contrast

- text/background ต้องผ่าน AA contrast ก่อน release
- semantic status ต้องมี text/icon ร่วมกับสี
- ห้ามใช้ red/green อย่างเดียวเพื่อแยกความหมาย
- chart labels ต้องยังอ่านความหมายได้เมื่อพิมพ์ grayscale

### Colorblind-Safe Behavior

สำหรับ protanopia / deuteranopia / tritanopia:
- category identification ใช้ label โดยตรง
- bar chart ใช้ axis/category label ชัดเจน
- KPI status มี text status
- Top 3 ใช้ rank number และ exact days ไม่ใช้สีลำดับเพียงอย่างเดียว

### Screen Reader

ทุก chart/container ต้องมี:
- descriptive title
- `aria-label` หรือ equivalent
- concise alt-text ที่สรุปว่ากราฟแสดง metric ใดและ filter ใด

ตัวอย่างแนวทาง:
`Open cases by current stage for case_domain=behavior`

table ต้องมี:
- semantic column headers
- accessible sort-state indication

### Keyboard Navigation

ผู้ใช้ต้องสามารถ:
- focus `case_domain` control
- เลือก/เปลี่ยน filter
- focus chart/table container
- เข้าถึง Top 3 rows
- reset filter

ได้โดยไม่พึ่ง mouse

### Motion

core dashboard ไม่มี animated chart
หากมี feature motion ภายหลัง ต้องรองรับ reduced-motion preference

## Data Literacy Guard Rails

Stakeholder หลักจาก `STAKEHOLDERS.md` คือ `HR / Consequence Process Owner`
ซึ่งเวอร์ชันข้อสอบนี้กำหนด `data_literacy_level = basic`

### Literacy Mapping

| Audience `data_literacy_level` | Maximum `complexity_level` | Examples Allowed by Template |
|---|---|---|
| `basic` | `basic` | KPI card, bar, line, table |
| `intermediate` | `intermediate` | basic + heatmap, scatter, grouped bar, crosshair |
| `advanced` | `advanced` | intermediate + multi-axis, animated, custom visualization, Sankey |

### Gate for This Dashboard

Core Consequence Process Dashboard ใช้เฉพาะ:
- `kpi_card`
- `bar`
- `table`

ทั้งหมดเป็น `basic` และไม่เกิน literacy level ของ target audience

### Animation Rule

animation เป็น `advanced` เสมอ

ดังนั้น:
- ห้ามใช้ animation สำหรับ audience `basic`
- ห้ามเขียนว่า animation ใช้ได้ที่ `intermediate`
- core dashboard นี้ปิด animation

### Override Process

หากต้องใช้ visualization ที่มี complexity สูงกว่า audience literacy:
1. ต้องมี stakeholder sign-off
2. ต้องมี training plan
3. ต้องบันทึกการเปลี่ยนแปลงใน `ANALYTICS_CHANGELOG.md`
4. ต้อง update `VIZ_DESIGN_SPEC.md` ก่อน dashboard code

### Current Design Decision

สำหรับข้อสอบ 120 นาที ไม่มีเหตุผลเชิงข้อมูลที่ต้องใช้ visualization ระดับ intermediate/advanced
การใช้ basic charts ลด interpretation risk และทำให้ acceptance test ตรงกับ metric output ได้ง่ายกว่า
