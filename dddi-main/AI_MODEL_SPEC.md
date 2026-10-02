# AI_MODEL_SPEC.md

Project: Consequence Process Dashboard  
Document ID: ai_model_spec  
Priority: P2  
Depends on: DATA_MODEL_SPEC.md, METRIC_SPEC.md, DATA_QUALITY.md, LINEAGE.md

## Model Inventory

### `model_status` Enum

`AI_MODEL_SPEC.md` เป็นเอกสารเจ้าของ `model_status`

- `Production`
- `Staging`
- `Experimental`
- `Deprecated`

### Inventory

| Model / Workflow | Purpose | Type | `model_status` | Business Owner |
|---|---|---|---|---|
| `process_improvement_brief_generator` | สร้างร่าง Process Improvement Brief จาก aggregate analytics เพื่อช่วย HR ตรวจสอบ bottleneck และจุดที่ควรปรับขั้นตอน | external generative AI endpoint / LLM workflow | `Experimental` | HR Process Owner |

AI workflow นี้เป็น **bonus scope** และไม่ใช่ dependency ของ core dashboard

## Model Profiles

### `process_improvement_brief_generator`

- **Purpose:** สร้างร่างข้อความสรุปจุดที่ควรตรวจสอบและข้อเสนอปรับ process จากข้อมูลภาพรวม
- **Business Action:** human review โดย HR Process Owner ก่อนนำข้อเสนอไปใช้
- **Automated Decision:** prohibited
- **HR Disciplinary Decision:** prohibited
- **Input Scope:** aggregate metrics และ minimal case-ranking context ที่ได้รับอนุมัติ
- **Endpoint:** `null`
- **Model Identifier:** `null`
- **Authentication Method:** `null`
- **Quota:** `null`
- **Owner:** Company AI Platform Owner
- **`model_status`:** `Experimental`
- **Output:** Process Improvement Brief text + generation metadata
- **Persistence:** ต้องบันทึกและเรียกกลับมาแสดงใน application ได้หากเปิดใช้ bonus

### Action-Threshold Link

`METRIC_SPEC.md` ยังไม่มี action threshold ที่ calibrate แล้ว ดังนั้น workflow นี้:
- ห้ามแปลง metric value เป็น “good/bad” โดยใช้ threshold ที่แต่งขึ้นเอง
- ห้ามสร้าง automatic escalation จาก metric value
- ใช้ wording เช่น “ควรตรวจสอบ” หรือ “พบการกระจุกตัว/ค้างในข้อมูล snapshot นี้” ตามข้อมูลจริง
- เมื่อ action threshold ถูกอนุมัติในอนาคต ต้อง link กลับ `METRIC_SPEC.md` ก่อนใช้ในการ prompt/action logic

## Feature Definitions

Workflow นี้ไม่ train predictive model แต่ prompt inputs ต้อง trace กลับ source ได้เหมือน feature

| Feature / Prompt Input | Definition | Source Column Reference | Lineage |
|---|---|---|---|
| `total_cases` | จำนวน distinct cases ใน filter context | `fact_consequence_case.case_id` | CSV `case_id` → staging → fact → metric mart |
| `open_cases` | จำนวน cases ที่ผ่าน approved open rule | `fact_consequence_case.case_id`, `dim_stage.stage` | CSV `case_id`,`stage` → fact/dim → approved rule → metric mart |
| `closed_cases` | จำนวน cases ที่ผ่าน approved closed rule | `fact_consequence_case.case_id`, `dim_stage.stage` | CSV `case_id`,`stage` → fact/dim → approved rule → metric mart |
| `open_cases_by_stage` | จำนวน open cases ต่อ stage | `fact_consequence_case.case_id`, `dim_stage.stage` | source → semantic → grouped metric |
| `top_3_longest_open_cases` | ranked cases by approved aging logic | `fact_consequence_case.case_id`, `fact_consequence_case.stage_entered_date`, `dim_stage.stage`, `dim_owner.owner` | source → semantic → aging mart → top3 mart |
| `case_domain_filter` | filter context ของ brief | `dim_case_domain.case_domain` | CSV `case_domain` → dimension → dashboard/AI filter context |
| `reference_date` | approved runtime date ที่ใช้คำนวณ aging | not a source column; approved runtime input | runtime input → aging metric → brief metadata |

### Feature Rules

- ใช้ metric outputs จาก semantic layer ไม่คำนวณสูตรซ้ำใน AI workflow
- ห้ามส่ง row-level HR identifiers ไป endpoint ถ้า aggregate summary เพียงพอ
- หากต้องส่ง Top 3 context ต้องใช้ minimum necessary fields และ policy จาก `DATA_GOVERNANCE.md`
- missing/unapproved runtime input ต้องทำให้ dependent prompt fields unavailable ไม่ใช้ค่า default

## Training Data Spec

### Training Strategy

Not applicable สำหรับ core bonus implementation:
- ไม่มีการ fine-tune หรือ train model ในโปรเจกต์นี้
- ใช้ company-provided external endpoint ตาม quota ที่บริษัทจัดให้
- ไม่มี train/validation/test split สำหรับ model training

### Prompt/Evaluation Fixture

สำหรับทดสอบ workflow ให้ใช้ synthetic/approved fixture ที่ไม่เปิดเผย HR personal data โดยครอบคลุม:
- aggregate with one dominant stage
- balanced stage distribution
- zero/open unavailable cases
- missing approved `reference_date`
- endpoint failure
- malformed model response

**Fixture values:** `null`  
**Calibration / Approval Owner:** HR Process Owner / Company AI Platform Owner

### Data Exclusion

ห้ามใช้ข้อมูลต่อไปนี้เป็น training/fine-tuning set โดยอัตโนมัติ:
- raw HR case records
- identifiable `case_id`
- identifiable `owner`
- persisted briefs

การนำข้อมูลใดไป train ต้องมี legal basis, governance approval และเอกสารใหม่/ฉบับแก้ไขที่รองรับ

## Evaluation Metrics

Acceptance threshold เป็นค่าที่ต้อง calibrate; โจทย์ไม่ได้ให้ จึงไม่สร้างตัวเลข

| Evaluation Metric | Definition | Acceptance Threshold | Calibration Owner |
|---|---|---|---|
| factual consistency | brief ไม่ขัดกับ aggregate inputs ที่ส่งเข้า model | `null` | HR Process Owner / Company AI Platform Owner |
| unsupported-claim rate | จำนวน claim ที่ไม่มีข้อมูล input รองรับ | `null` | HR Process Owner |
| required-section completeness | มีจุดที่ควรตรวจสอบ + ข้อเสนอปรับขั้นตอนตาม prompt contract | `null` | HR Process Owner |
| persistence success | generation ที่สำเร็จถูกบันทึกและอ่านกลับได้ | `null` | Analytics Implementation Owner |
| latency | เวลาตั้งแต่ request ถึง response | `null` | Company AI Platform Owner |

### Evaluation Rule

- ห้าม promote จาก `Experimental` ไป `Staging`/`Production` จน acceptance thresholds ได้รับ approval และ evaluation ผ่าน
- evaluation ต้องใช้ known input → reviewed expected constraints
- human reviewer ต้องสามารถ trace ข้อสรุปกลับ metric/run ที่ใช้ generate

## Deployment and Monitoring

### Deployment

- AI feature เปิดหลัง core dashboard/test/deployment path ทำงานแล้ว
- endpoint URL / auth / model identifier / quota = `null`
- secrets ต้องอยู่ใน Coolify-managed environment secret/variable
- AI failure ต้องไม่ทำให้ core dashboard unavailable
- persisted brief ต้องบันทึกอย่างน้อย:
  - `brief_id`
  - `generated_at`
  - `run_id`
  - `case_domain_filter`
  - `reference_date` ถ้ามี
  - model identifier เมื่อ endpoint ให้ข้อมูลนี้
  - brief text
  - generation status

### Monitoring

Monitoring items:
- endpoint availability
- authentication failure
- rate/quota errors
- response parse failure
- persistence failure
- factual-consistency review result
- unsupported-claim review result

### Drift Detection

สำหรับ external generative endpoint ไม่มี feature-distribution drift model ที่ calibrate แล้วในโปรเจกต์นี้

- **Drift / behavior-change threshold:** `null`
- **Alert Route:** `null`
- **Calibration Owner:** Company AI Platform Owner / HR Process Owner
- **Retraining Trigger:** not applicable unless company introduces a trainable/fine-tuned model
- **Model-version change trigger:** เมื่อ provider/model identifier เปลี่ยน ต้อง rerun evaluation suite และบันทึก change

### Alerting

- auth failure → alert Company AI Platform Owner
- repeated endpoint failure → mark AI feature unavailable; core dashboard remains available
- evaluation regression หลัง model/version change → stop promotion/use of new version until reviewed
- no threshold-based automated HR action is permitted

### Governance Boundary

AI-generated brief เป็น draft เพื่อสนับสนุน human review เท่านั้น
ต้องไม่:
- ตัดสินความผิด/โทษ
- score บุคคล
- rank พนักงาน
- infer intent/mental state
- replace HR approval

ทุกข้อเสนอใน brief ต้องถูกตีความเป็น process-review suggestion ไม่ใช่คำตัดสินต่อบุคคล
