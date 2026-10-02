# รายงานหลักฐานการทำงานสอบ Practical — Consequence Process Dashboard

> ไฟล์นี้ **สร้างหลังสอบ** (AFTER_EXAM) เมื่อ 2026-10-02 12:14 +07 จากการอ่านอย่างเดียว ไม่ใช่ส่วนหนึ่งของงานที่ส่งสอบ
> รายงานนี้ไม่ให้คะแนน ไม่ตัดสินผ่าน–ตก และไม่เสนอการแก้ไข

**คำอธิบายสถานะ:** VERIFIED = มีหลักฐานตรวจพบโดยตรง · REPORTED = มีผู้กล่าวไว้แต่ไม่มีหลักฐานโดยตรง · INFERRED = อนุมาน (ระบุเหตุผล) · UNKNOWN = ข้อมูลไม่พอ/เข้าถึงไม่ได้
**ช่วงเวลา:** DURING_EXAM / AFTER_EXAM / TIME_UNKNOWN — เนื่องจาก **ไม่ทราบเวลาเริ่ม–หมดเวลาสอบ** จึงใช้ `TIME_UNKNOWN*` กับหลักฐานทั้งหมดที่เกิดก่อนข้อความ 12:12:16 ที่ผู้สอบระบุว่า "งานสอบสิ้นสุดแล้ว" (เครื่องหมาย * = เกิดก่อนข้อความนั้น แต่ไม่ยืนยันว่าอยู่ในกรอบเวลาสอบ) และ `AFTER_EXAM` กับการรวบรวมรายงานนี้

---

## A. ข้อมูลผู้สอบและขอบเขตหลักฐาน

| รายการ | ข้อมูล | สถานะ |
|---|---|---|
| ชื่อผู้สอบ | **UNKNOWN** — บริบท session ไม่ระบุชื่อไว้อย่างชัดเจน (ไม่ใช้การเดาจากข้อมูลบัญชี) | UNKNOWN |
| ตำแหน่ง | ไม่ทราบ — ไม่มีหลักฐาน | UNKNOWN |
| โจทย์/DDD ที่เลือก | โปรเจกต์ `Consequence Process Dashboard` ใช้ track `ddd-data-analytics` เป็น blueprint หลัก (ข้อความของผู้สอบ [E002] และเอกสาร `dddi-main/CONSTRAINTS.md` [E036]) | VERIFIED (ว่าระบุไว้) |
| เครื่องมือ AI ที่ใช้พัฒนา | Claude Code; โมเดล `Sonnet 5.5`, effort `medium` (ผลคำสั่ง `/model` และ `/effort` ใน session [E001]) | VERIFIED |
| DB / Framework | DuckDB (ระบุใน `CONSTRAINTS.md`) และ Streamlit (ผู้สอบสั่งให้ใช้ใน [E003]) | VERIFIED |
| Repo path (local) | `/home/looktal/lab-exam02102026` | VERIFIED [E029] |
| Repo URL / branch / commit | **ไม่ทราบ — ไม่มี Git repo** (`fatal: not a git repository`) | VERIFIED ว่าไม่มี [E029] |
| URL แอป (local) | `http://localhost:8501` (รันในเครื่องระหว่าง session) | VERIFIED [E020, E024] |
| URL Coolify / deployment | ไม่พบหลักฐาน; `CONSTRAINTS.md` ระบุค่า repository URL และ Coolify project/domain เป็น `null` | UNKNOWN [E036] |
| เวลาเริ่ม–หมดเวลาสอบ | **ไม่ทราบ** (ไม่มีหลักฐาน); เอกสาร `CONSTRAINTS.md` ระบุกรอบ "120 นาที" ของโจทย์ แต่ไม่ระบุเวลาจริงของผู้สอบ | UNKNOWN |
| ช่วงเวลาที่ session มีบันทึก | 2026-10-02 11:09:11 – 12:12:57 (+07) = ราว 63 นาที ระหว่างระเบียนแรกและสุดท้ายของ transcript — **เป็นช่วงของ session ไม่ใช่ระยะเวลาสอบที่ยืนยัน** | VERIFIED [E001] |
| เวลาที่ผู้สอบแจ้งว่าสอบสิ้นสุด | ข้อความ 12:12:16 (+07) | REPORTED [E013] |
| เวลาเริ่มรวบรวมหลักฐาน / timezone | 2026-10-02 12:12:42 (+07, ICT) | VERIFIED [E029] |

**แหล่งที่เข้าถึงได้:** บริบท session ปัจจุบันครบทุกข้อความ (ไม่พบว่าถูกย่อ), ไฟล์ transcript ของ session (ใช้อ่านเฉพาะ timestamp ข้อความผู้ใช้และรายการ tool calls), ไฟล์ใน repo, สถานะ Git
**แหล่งที่ขาด:** Git history, remote repo, ผล push, Coolify (ไม่มีเลย), เวลาสอบจริง, ข้อมูล token/quota, หลักฐานการเรียก AI endpoint จริง, ผลรัน test ที่เชื่อมกับ commit

---

## B. สภาพงานที่พบ (ก่อนสร้างรายงาน)

| รายการ | ข้อมูล | สถานะ |
|---|---|---|
| Git | ไม่มี `.git`; `git rev-parse/status/log` ล้มเหลวด้วย `fatal: not a git repository` → **ไม่มี branch, HEAD, commit ที่ส่งสอบ, staged/unstaged/untracked** ให้บันทึก | VERIFIED [E029] |
| กรณีนี้หมายความว่า | แยก "งานใน commit" กับ "ไม่ commit" **ไม่ได้**; ทุกไฟล์ถือเป็นสภาพที่พบตอนรวบรวม | INFERRED |
| working directory ก่อนสร้างรายงาน | 12 รายการระดับบน: `.dockerignore .env.example .gitignore .pytest_cache .streamlit Dockerfile README.md __MACOSX app.py config data dddi-main looktal_consequence_mock_2-3MB.csv(+Zone.Identifier) pytest.ini requirements.txt runs sql src tests` | VERIFIED [E029] |
| ไฟล์ที่ **มีมาก่อน/ไม่ได้สร้างใน session** | CSV ต้นฉบับที่ root (mtime 10:19), `__MACOSX/` และไฟล์ `*:Zone.Identifier` (mtime 11:08), เอกสาร DDD 23 ไฟล์ใน `dddi-main/` (ฉบับเดิมที่ไม่ถูกแก้มี mtime 10:52–11:03 เช่น `SLA_FRESHNESS.md`, `RUNBOOK.md`, `DATA_GOVERNANCE.md`, `AI_MODEL_SPEC.md`, `LINEAGE.md`, `AGENTS.md`) — อนุมานว่าเป็นชุดที่ได้รับ/แตกไฟล์ก่อน session; mtime **ไม่ใช่หลักฐานเด็ดขาด** | INFERRED [E030] |
| ไฟล์ที่สร้างโดยคำสั่งใน session | `requirements.txt, pytest.ini, Dockerfile, .dockerignore, .gitignore, .env.example, .streamlit/config.toml, app.py, config/runtime_config.json, data/ (สำเนา CSV), sql/*.sql, src/cpd/*.py, tests/*.py, README.md` และ `runs/` (ไฟล์ที่ pipeline สร้าง) | VERIFIED [E016, E021, E023, E025, E027] |
| เอกสาร DDD ที่ถูกแก้ใน session | `STAKEHOLDERS, CONSTRAINTS, BUSINESS_GLOSSARY, KPI_DICTIONARY, METRIC_SPEC, DATA_MODEL_SPEC, METRIC_LOGIC, DATA_QUALITY, TESTING_STRATEGY, DASHBOARD_SPEC, REPORT_SPEC, README, DATA_CONTRACT, PIPELINE_SPEC, TASKS, ANALYTICS_CHANGELOG, VIZ_DESIGN_SPEC` (.md) ตามคำสั่ง [E004, E005, E012] | VERIFIED [E018, E019, E025, E027] |
| ผลกระทบนอก repo จาก session | ติดตั้ง `pytest` และ `playwright` (user site, `--break-system-packages`), ดาวน์โหลด Chromium ของ playwright, แตกไลบรารี/ฟอนต์ไทยใน `/tmp/claude-1000/` และ `~/.fonts`, สร้าง snapshot เอกสารที่ `/tmp/claude-1000/ddd_before`, ภาพหน้าจอ 22 ไฟล์ใน scratchpad ของ session | VERIFIED [E015, E026, E027] |
| ไม่มี `.venv`/`venv` | ผู้สอบสั่งให้ activate virtual environment ที่มี แต่ไม่พบ; `python3 -m venv` ล้มเหลวใน session | VERIFIED [E009, E015] |

---

## C. ลำดับการทำงาน

เวลาเป็น +07 จาก timestamp ใน transcript (UTC+7). ผู้ดำเนินการ "ผู้สอบ" = ข้อความที่ผู้สอบพิมพ์; "Claude Code" = tool calls ที่ AI เรียกใช้ตามคำสั่ง

| ลำดับ | เวลา | สิ่งที่ทำ | ผู้ดำเนินการที่ยืนยันได้ | ผลที่พบ | Evidence |
|---|---|---|---|---|---|
| 1 | 11:09:11–11:09:39 | ตั้ง effort=medium และเลือกโมเดล Sonnet 5.5 | ผู้สอบ (คำสั่ง `/effort`, `/model`) | บันทึกค่าเป็นค่าเริ่มต้น | E001 |
| 2 | 11:10:35 | รับโจทย์: ให้ใช้ AGENTS.md + เอกสาร DDD ตามลำดับ, ตรวจ CSV/repo, ห้ามเดา `null`/`CURRENT_DATE`, **ยังไม่ implement** ให้เสนอ architecture/โครงสร้าง/mapping TASKS/blockers/ลำดับงาน | ผู้สอบ | — | E002 |
| 3 | 11:10:37–11:11:02 | อ่านเอกสาร DDD ทั้งชุด, ตรวจ CSV (40,000 แถว) และ repo (ยังไม่มี code/Git) | Claude Code | CSV ตรง contract: 40,000 แถว, ไม่มี `case_id` ซ้ำ/ค่าว่าง, `stage` 4 ค่า, `owner` 8 ค่า | E014 |
| 4 | ก่อน 11:14:08 | ส่งแผน architecture/โครงสร้าง/blockers (ข้อความคำตอบของ AI) | Claude Code | ระบุ blocker: `reference_date`, open/closed, day-count, tie-break, Coolify/repo; เสนอ Streamlit | REPORTED (คำตอบของ AI ไม่มีเวลาที่ตรวจแยก) |
| 5 | 11:14:08 | ผู้สอบกำหนด business rules (open/closed, day-count, tie-break), เลือก Streamlit, สั่ง implement core ครบพร้อม test และ idempotent rerun, ยังไม่ทำ AI bonus; `reference_date` ยังไม่มีค่า | ผู้สอบ | — | E003 |
| 6 | 11:15:42–11:19:18 | สร้างโครงสร้าง/โค้ด/test/Dockerfile/README; ติดตั้ง pytest; เจอปัญหา venv | Claude Code | test ครั้งแรก 7 failed/37 passed → แก้ → **44 passed** (11:18:30) | E015–E017 |
| 7 | 11:24:45 | ผู้สอบยืนยัน `reference_date = 2026-10-01` (เป็น project-specific assumption) และสั่งอัปเดตเอกสาร/config/test | ผู้สอบ | — | E004 |
| 8 | 11:24:48–11:29:40 | อัปเดตเอกสาร DDD + config + test ให้ใช้ 2026-10-01; โหลด CSV จริงด้วยวันที่นี้ | Claude Code | **44 passed** (11:25:38, 11:29:13); โหลดจริง `run_id=43ed417f4b4f-2026-10-01` | E018 |
| 9 | 11:27:16 | ผู้สอบยืนยัน business rules ทั้งหมดและสั่ง reconcile เอกสาร → certify metric, อัปเดต ANALYTICS_CHANGELOG, TASKS T10 | ผู้สอบ | — | E005 |
| 10 | 11:27:24–11:29:40 | แก้เอกสาร 13 ไฟล์ (เทียบ snapshot ก่อนแก้), metric 6 ตัว → `certified`, T10 → `done` | Claude Code | **44 passed** (11:29:13); ไม่มี Git จึงสรุป diff เทียบ snapshot | E019 |
| 11 | 11:34:27 | ผู้สอบสั่งรันแอปและขอ URL | ผู้สอบ | — | E006 |
| 12 | 11:34:30–11:34:33 | รัน `app.py` | Claude Code | health=200, page=200, URL `http://localhost:8501` | E020 |
| 13 | 11:38:54 | ผู้สอบสั่ง implement AI bonus (อ่าน AI_MODEL_SPEC ฯลฯ ก่อน) | ผู้สอบ | — | E007 |
| 14 | 11:38:56–11:43:39 | อ่านเอกสาร, สร้าง `ai_brief.py` + 27 tests (endpoint จำลอง); รันแอปโดยให้ AI endpoint ชี้ไปที่ที่เชื่อมต่อไม่ได้ | Claude Code | 2 failed/69 passed → แก้ → **71 passed** (11:42:03); แอป health=200 | E021, E022 |
| 15 | 11:45:51 | ผู้สอบสั่งสร้าง `.gitignore` และตรวจ secret | ผู้สอบ | — | E008 |
| 16 | 11:45:56–11:46:08 | ตรวจต้นไม้ไฟล์ + สแกน secret; เขียน `.gitignore` | Claude Code | ไม่พบ secret จริง; ไม่มีไฟล์ `.env` | E023 |
| 17 | 11:47:54 | ผู้สอบสั่งรันแอปด้วย `reference_date` และโหลด CSV | ผู้สอบ | — | E009 |
| 18 | 11:47:59–11:48:xx | โหลด CSV + รันแอป | Claude Code | `status=published run_id=43ed417f4b4f-2026-10-01 rows=40000`; health=200, page=200; Total 40,000 / Closed 17,706 / Open 22,294 | E024, E031 |
| 19 | 11:50:47 | ผู้สอบสั่งปรับธีม Ragnar แดง/ขาว/ครีม (ห้ามแตะ logic) | ผู้สอบ | — | E010 |
| 20 | 11:51:32–11:53:51 | แก้ presentation + VIZ_DESIGN_SPEC | Claude Code | **71 passed** (11:52:28, 11:53:20, 11:53:51); ตรวจ contrast ด้วยการคำนวณ | E025 |
| 21 | 11:55:03 | ผู้สอบ: "ขอดูหน้าจอจริงก่อน แล้วค่อยปรับ" | ผู้สอบ | — | E011 |
| 22 | 11:55:06–11:56:28 | ติดตั้ง playwright/Chromium, แก้ไลบรารีที่ขาด, ถ่ายภาพหน้าจอ | Claude Code | ได้ภาพจริง; ระบุปัญหา 10 ข้อและ **ยังไม่แก้** รอผู้สอบ | E026 |
| 23 | 11:57:13 | ผู้สอบสั่งเพิ่มสองภาษา TH/EN | ผู้สอบ | — | E012 |
| 24 | 11:57:23–12:10:31 | สร้าง `i18n.py`, ปรับ dashboard/CSS/test; พบ/แก้บั๊ก selectbox ค้างภาษา | Claude Code | 1 failed/70 passed → 71 → **81 passed** (12:00:54) → **82 passed** (12:09:11, 12:10:31) | E027 |
| 25 | 12:12:16 | ผู้สอบแจ้งว่างานสอบสิ้นสุดและสั่งรวบรวมหลักฐาน | ผู้สอบ | — | E013 |
| 26 | 12:12:35–12:14 | รวบรวมหลักฐาน (อ่านอย่างเดียว) และสร้างรายงานนี้ | Claude Code | AFTER_EXAM | E029–E035 |

**ไม่พบหลักฐาน:** การ `git init`/commit/push, การ build Docker, การ deploy Coolify, การเรียก AI endpoint จริง
**หมายเหตุ:** มีข้อความของผู้สอบที่แทรกกลางงาน (เรื่องปรับ test/เอกสารหาก `reference_date` ทำให้ผลเปลี่ยน) ปรากฏใน context ของ session แต่ **ไม่ปรากฏเป็นระเบียนข้อความผู้ใช้แยกในไฟล์ transcript ที่ตรวจ** (REPORTED) [E037]

---

## D. คำสั่งและเครื่องมือที่ใช้

จากรายการ tool calls ใน transcript: **Bash 80 ครั้ง, Read 12 ครั้ง** (ไม่พบ tool Write/Edit; การสร้างและแก้ไฟล์ทำผ่านคำสั่ง Bash เช่น heredoc และสคริปต์ python) — ตารางต่อไปนี้ **เป็นการสรุปกลุ่มคำสั่ง** (ไม่ใช่รายการครบทุกตัวอักษร) `ERR` = tool รายงาน error/exit code ไม่เป็นศูนย์

### D1. คำสั่งที่มีหลักฐานว่า execute แล้ว

| ลำดับ (tool call #) | คำสั่ง/tool ที่พบ (สรุป) | จุดประสงค์ที่มีหลักฐาน | ผล/exit code ที่พบ | ช่วงเวลา | Evidence |
|---|---|---|---|---|---|
| 001–008 | `find`, `cat dddi-main/*.md`, `head`/`wc` CSV, `grep` | อ่านเอกสาร DDD และตรวจ CSV/repo | พบเอกสารครบ, CSV 40,000 แถว | 11:10:37–11:11:02 | E014 |
| 009–011 | `mkdir …; cp CSV data/; pip install pytest`; `python3 -m venv …` | เตรียมโฟลเดอร์และ environment | **ERR** pip (PEP 668), **ERR** venv; แก้ด้วย `pip install --user --break-system-packages pytest` → `Successfully installed … pytest-9.1.1` | 11:15:42–11:15:49 | E015 |
| 012–014 | เขียน `requirements.txt`, `ingest.py`, `model.py`, `metrics.py`, `quality.py`, `publish.py`, `pipeline.py`, `sql/*.sql` ฯลฯ; `python3 app.py --load data/…csv` | สร้าง core pipeline | `status=published run_id=43ed417f4b4f-noref rows=40000` | 11:16:15–11:17:18 | E016 |
| 015–016 | เขียน `tests/*`; `python3 -m pytest -q` | ทดสอบ core | `7 failed, 37 passed` → แก้ path ของ AppTest → `44 passed in 19.58s` | 11:18:08–11:18:30 | E017 |
| 017–018 | เขียน `Dockerfile`, `README.md` | เตรียม deploy/เอกสาร | ไม่มีผลรัน | 11:18:57–11:19:18 | E016 |
| 019–024 | `grep` หา `reference_date`, แก้ doc/config/test ด้วย python, `python3 -m pytest -q`, `python3 app.py --load … --reference-date 2026-10-01` | ปรับให้ใช้ 2026-10-01 | `44 passed in 19.65s`; `run_id=43ed417f4b4f-2026-10-01` | 11:24:48–11:26:06 | E018 |
| 025–030 | snapshot เอกสาร, แก้ doc ด้วย python, `python3 -m pytest -q`, เทียบ snapshot, `git rev-parse` | reconcile DDD | `44 passed in 20.40s`; `fatal: not a git repository` | 11:27:24–11:29:40 | E019 |
| 031–032 | `PORT=8501 nohup python3 app.py`; `curl` health/page | รันแอป | `health=200`, `page=200` | 11:34:30–11:34:33 | E020 |
| 033–037 | อ่าน AI/Governance docs, สร้าง `ai_brief.py`, `tests/test_ai_brief.py`; `python3 -m pytest -q` | AI bonus | `2 failed, 69 passed` → `71 passed in 37.56s` | 11:38:56–11:42:03 | E021 |
| 038 | python แก้เอกสาร + `pkill -f "streamlit run"` | ปิดแอปเดิม | **ERR** exit 144 (คำสั่ง pkill ฆ่า shell ตัวเอง) แก้ด้วย `fuser -k 8501/tcp` ในคำสั่งถัดไป | 11:42:55 | E021 |
| 039 | รัน `app.py` โดยตั้ง `CPD_AI_ENDPOINT_URL=http://127.0.0.1:9/none` และคีย์ปลอม | ตรวจว่า core ทำงานเมื่อ AI ใช้ไม่ได้ | `health=200` | 11:43:39 | E022 |
| 040–041 | `find` ต้นไม้ไฟล์, สแกน secret ด้วย `grep`, เขียน `.gitignore` | เตรียม commit | ไม่พบ secret จริง | 11:45:56–11:46:08 | E023 |
| 042 | `ls -d .venv venv`; `fuser -k`; โหลด CSV + `--reference-date 2026-10-01`; รันแอป; query สถานะ | ยืนยันว่ารันได้ | ไม่มี `.venv`; `run_id=…-2026-10-01`; `health=200, page=200`; Total/Closed/Open = 40000/17706/22294 | 11:47:59–11:48:xx | E024 |
| 043–050 | แก้ presentation (`viz_theme.py`, `dashboard.py`, `.streamlit/config.toml`, `app.py`, `Dockerfile`, `VIZ_DESIGN_SPEC.md`); `python3 -m pytest -q`; AppTest ตรวจ | ปรับธีม | `71 passed in 25.32s`, `23.86s`, `24.28s`; (ERR exit 2 ที่ 048 = health/page ได้ 200 แต่คำสั่งท้ายสคริปต์คืน exit 2) | 11:51:32–11:53:51 | E025 |
| 051–058 | `pip install --user --break-system-packages playwright`; `playwright install chromium`; `apt-get download` ไลบรารี; ถ่ายภาพ; `streamlit config show` | ดูหน้าจอจริง | ภาพหน้าจอได้ (หลังแก้ libnspr4/libnss3/libasound); ERR ช่วงแรกจากไลบรารีขาด | 11:55:06–11:57:52 | E026 |
| 059–062 | สร้าง `i18n.py`, แก้ `dashboard.py`; `python3 -m pytest -q` | สองภาษา | `1 failed, 70 passed` → `71 passed` → `81 passed in 28.90s` | 11:58:46–12:00:54 | E027 |
| 063–073 | ดาวน์โหลดฟอนต์ไทย, ถ่ายภาพ TH/EN, ทดลองสลับภาษา, แก้ CSS/selectbox | ตรวจ UI สองภาษา | พบว่า selectbox แสดงข้อความค้างภาษาเดิม; ERR หลายครั้งจาก locator timeout ระหว่างทดลอง | 12:01:30–12:08:09 | E027 |
| 074–075 | แก้ label + เพิ่ม test + changelog/README; `python3 -m pytest -q` | ปิดงานสองภาษา | `82 passed in 31.07s`; `82 passed in 29.23s` | 12:09:11–12:10:31 | E027 |

### D2. คำสั่งที่เพียงเสนอหรือกล่าวถึง (ไม่มีหลักฐานว่า execute)

| คำสั่ง | บริบท |
|---|---|
| `pip install -r requirements.txt`, `pytest -q`, `python app.py --load …`, `python app.py` | ลำดับใน README (ทั้งของ DDD และ README ที่เขียนใน session) — README ของ DDD ระบุเป็น "target command interface" |
| `pkill -f "streamlit run"` | AI แนะนำให้ผู้สอบใช้หยุดแอป (ไม่ได้รันโดยผู้สอบตามหลักฐาน; ตัวที่รันจริงคือ `fuser -k 8501/tcp`) |
| `git init` / commit / push | AI กล่าวถึงว่ารอ URL ของบริษัท; ผู้สอบกล่าวว่าจะ commit/push ผ่าน SourceTree เอง (REPORTED) |
| `docker build` / Coolify deploy | มีเพียง `Dockerfile`; **ไม่พบการ build/deploy** |

### D3. คำสั่งอ่านอย่างเดียวที่ใช้รวบรวมรายงานนี้ (AFTER_EXAM)

`date`, `pwd`, `git rev-parse/status/log`, `ls -la`, `find … -printf`, `stat`-ผ่าน `find`, `cat runs/*.json` (เฉพาะ metadata), `sha256sum`, `wc -l`, `rg -c/-n` (นับ test/หาตำแหน่ง/สแกน secret และ system date), `ls` รายการโฟลเดอร์โปรเจกต์ของ session, สคริปต์ python อ่าน transcript (พิมพ์เฉพาะ timestamp+ข้อความผู้ใช้ย่อ+รายการ tool calls) และ `ls` โฟลเดอร์แม่เพื่อเลือกที่วางรายงาน (**ผลของ `ls` โฟลเดอร์แม่แสดงรายการนอกขอบเขตโดยไม่ตั้งใจ ไม่ได้ใช้และไม่ได้บันทึกในรายงาน**) — ไม่ได้รัน test/app/scripts ของ repo [E029–E035]

---

## E. การตัดสินใจและการใช้ AI

| หัวข้อ | สิ่งที่พบ | ที่มา/เหตุผลที่ปรากฏ | สถานะ |
|---|---|---|---|
| Track | `ddd-data-analytics` | ผู้สอบระบุ [E002]; `CONSTRAINTS.md` | VERIFIED |
| Analytics store | DuckDB | `CONSTRAINTS.md`: โจทย์อนุญาต SQLite3/DuckDB เลือก DuckDB ภายในเวลาจำกัด | VERIFIED [E036] |
| Framework | Streamlit | `CONSTRAINTS.md` ระบุ `null`; AI เสนอ; ผู้สอบสั่งใช้ [E003] | VERIFIED |
| กติกาธุรกิจ | closed=`stage='closed'`; open=`reviewing/follow_up/collecting_info`; day-count=calendar-day; tie-break=`days DESC, case_id ASC` | ผู้สอบกำหนดเอง ระบุว่าเป็นกติกาเฉพาะงานสอบ ไม่ใช่มาตรฐานอุตสาหกรรม [E003, E005] | VERIFIED |
| `reference_date` | `2026-10-01` | ผู้สอบยืนยันเป็น project-specific assumption [E004]; ก่อนหน้านั้นผู้สอบสั่งไม่ให้เดา [E003] | VERIFIED |
| ขอบเขตที่ตัดออก/เลื่อน | AI bonus เลื่อนจนกว่า core เสร็จ [E003]; ภายหลังผู้สอบสั่งทำ [E007]; ไม่ได้ทำ push/deploy ใน session | VERIFIED |
| ข้อจำกัดที่ผู้สอบกำหนด | ห้ามแก้ metric formula/SQL/reference_date/เทสต์ เมื่อปรับธีมและสองภาษา [E010, E012] | VERIFIED |
| การตรวจ/ปรับ output ของ AI โดยผู้สอบ | ผู้สอบสั่งให้อ่านเอกสารก่อนเขียน code [E002]; กำหนดและแก้ business rules [E003–E005]; สั่งให้ "ขอดูหน้าจอจริงก่อน แล้วค่อยปรับ" [E011]; ตรวจผลได้ด้วยการสั่งรันแอป [E006, E009]. **ไม่มีหลักฐานเพิ่มเติมเรื่องการอ่านโค้ด** และไม่สรุปว่าผู้สอบเข้าใจโค้ดหรือไม่ | VERIFIED (ว่ามีข้อความเหล่านี้) |
| การตรวจ output ของ AI เองใน session | AI รัน test, ตรวจ contrast ด้วยการคำนวณ, ถ่ายภาพหน้าจอ และแก้บั๊กที่เจอ (ดู F) | VERIFIED [E017, E025–E027] |
| Token/quota ที่ใช้ | **ไม่ทราบ** — ไม่ได้ดึงข้อมูลการใช้จาก session และไม่ประมาณ; เอกสารระบุข้อจำกัด "ใช้ Token ที่มีอยู่ ห้ามเติมเพิ่ม" (`CONSTRAINTS.md`) | UNKNOWN |

---

## F. ปัญหาและสิ่งที่ติด

| ปัญหา | อาการ/error ที่พบ | วิธีที่ลอง | ผลที่ยืนยันได้ | ยังไม่ทราบ/ยังค้าง | Evidence |
|---|---|---|---|---|---|
| ติดตั้ง pytest ไม่ได้ตามปกติ | pip ถูกปฏิเสธ (PEP 668 hint) | `pip install --user --break-system-packages pytest` | ติดตั้งสำเร็จ pytest 9.1.1 | ติดตั้งนอก virtualenv | E015 |
| สร้าง virtualenv ไม่ได้ | `python3 -m venv` → `Failing command: …/.venv/bin/python3` | ลบ `.venv` แล้วใช้ Python ระบบ | ไม่มี `.venv` ใน repo | สาเหตุ venv ล้มเหลว (ไม่ปรากฏใน output) | E015, E024 |
| AppTest หาไฟล์ไม่เจอ | `7 failed, 37 passed` (`FileNotFoundError` path ของ dashboard) | แก้ path ให้เป็น absolute | `44 passed` | — | E017 |
| AI tests ล้มเหลว | `2 failed, 69 passed` (ตรวจวันที่ใน payload และชนิด reference_date) | แก้ test/โค้ด | `71 passed` | — | E021 |
| ปิดแอปด้วย pkill | exit 144 | ใช้ `fuser -k 8501/tcp` | แอปรันใหม่ได้ | — | E021 |
| สคริปต์แก้เอกสารหยุดกลางคัน | `AssertionError` ที่ `../README.md` (ผิด path ของ README) | แก้ path เป็น `dddi-main/README.md` | แก้ครบ | — | E018 |
| Chromium ขาดไลบรารี | `libnspr4.so: cannot open shared object file` | `apt-get download` + `dpkg -x` ไปที่ `/tmp` | ถ่ายภาพหน้าจอได้ | — | E026 |
| selectbox ค้างข้อความภาษาเดิม | หลังสลับ TH→EN กล่องยังแสดงข้อความไทย (พบจากภาพ/การอ่านค่า) | ลองเปลี่ยน key container (ไม่ได้ผล) → ใช้ label สองภาษาที่เหมือนกัน | หลังแก้ กล่องแสดง `ผลงาน / Performance` ทั้งสองภาษา; `82 passed` | สาเหตุภายใน Streamlit ไม่ได้ตรวจลึก | E027 |
| ฟอนต์ไทยในเครื่องทดสอบ | เครื่องไม่มีฟอนต์ไทย | ดาวน์โหลดฟอนต์ไว้ใน `~/.fonts` เพื่อถ่ายภาพ | ภาพแสดงไทยได้ | การแสดงผลบนเครื่องผู้สอบ/Coolify ไม่ได้ตรวจ | E027 |
| **Push repo / deploy Coolify** | ไม่มี Git repo; ค่า URL/Coolify เป็น `null` ใน `CONSTRAINTS.md` | — | ไม่พบการดำเนินการ | **ยังไม่มีหลักฐาน push/deploy** | E029, E036 |
| สถานะงานใน TASKS.md | T01–T09 ยัง `not started`, T10/T11 = `done` | ไม่ได้แก้ (ผู้สอบสั่งเฉพาะ T10 และ T11) | ตามไฟล์ | ไม่สอดคล้องกับงานที่ทำแล้ว | E035 |

---

## G. งานที่ส่งมอบ

### G1. ฟังก์ชันหลักและเส้นทางข้อมูล (พบ implementation)

```
CSV → ingest.validate_and_stage → stg_consequence_case → model.build (dim_* + fact_consequence_case)
    → views (sql/views.sql, aging_views.sql) → quality DQ rules → publish (runs/<run_id>.duckdb + published.json)
    → Streamlit dashboard (อ่านจากไฟล์ที่ publish แบบ read-only) [+ AI brief ใน runs/ai_briefs.duckdb]
```

| ส่วน | ตำแหน่ง | สถานะ |
|---|---|---|
| Validation + staging | `src/cpd/ingest.py:27` | พบ implementation; รันสำเร็จใน session (E016, E024) |
| Dim/Fact model | `src/cpd/model.py:11` | พบ; รันสำเร็จ |
| Metric SQL (9 queries) | `sql/metrics.sql` | พบ; ตรวจด้วย golden test (E017, E027) |
| DQ rules | `src/cpd/quality.py:23` | พบ; รันสำเร็จ (ผลในไฟล์ DB) |
| Publication gate | `src/cpd/publish.py:15`, `src/cpd/pipeline.py:20` | พบ; test ตรวจ invalid run ไม่ทับ state เดิม |
| Dashboard (KPI, stage bar, aging, Top 3, filter, drill-down) | `src/cpd/dashboard.py:131` | พบ; รันจริงในเครื่อง (E020, E024, E026) |
| AI brief | `src/cpd/ai_brief.py:181` (`generate_brief`) | พบ; ดู J |
| สองภาษา/ธีม | `src/cpd/i18n.py`, `src/cpd/viz_theme.py`, `.streamlit/config.toml` | พบ; ตรวจด้วยภาพ+test |
| ผลจริงที่ session แสดง | Total 40,000 / Closed 17,706 / Open 22,294 และ Top 3 = H000001–H000003 (120 วัน) บน CSV จริง | VERIFIED จาก output ใน session (E024, E018); **ไม่ได้ตรวจซ้ำตอนรวบรวม** |

### G2. ฐานข้อมูลและ persistence

- DuckDB ไฟล์ต่อ run: `runs/43ed417f4b4f-2026-10-01.duckdb` (3,682,304 ไบต์), ชี้ด้วย `runs/published.json` (`row_count=40000`, `reference_date=2026-10-01`, `aging_status=available`, `started_at=2026-10-02T04:48:01+00:00` = 11:48:01 +07) — VERIFIED ว่าไฟล์อยู่จริง (E031); ไม่ได้ query เนื้อใน DB ตอนรวบรวม
- SHA-256 ของ CSV (data/ และ root เหมือนกัน) ขึ้นต้น `43ed417f4b4f…` ตรงกับ `snapshot_id` ใน run (VERIFIED, E031–E032)
- ไม่พบไฟล์ `runs/ai_briefs.duckdb` ตอนรวบรวม → **ไม่มี AI brief ที่ถูกบันทึกจริงใน runtime ของ repo นี้** (VERIFIED จากรายการ `runs/`, E031)
- `Dockerfile` ตั้ง `CPD_RUNS_DIR=/app/runs` แต่ไม่พบการตั้ง volume/persistence ในไฟล์ที่ตรวจ → การคงอยู่ของข้อมูลหลัง deploy **ไม่ทราบ** (UNKNOWN; ไม่เคย build หรือ deploy)

### G3. ข้อจำกัดที่พบโดยไม่ทดลองใหม่

- ไม่มี Git/remote/CI, ไม่มีหลักฐาน deploy (ดู I)
- ไม่มี `.venv`; dependencies ติดตั้งในระบบ/user site
- AI endpoint ไม่เคยถูกเรียกจริง
- เอกสาร DDD บางส่วนยังมี `null` ตามเดิมโดยตั้งใจ (SLA, retention, threshold ฯลฯ) และ `TASKS.md` สถานะ T01–T09 ไม่ได้อัปเดต
- ค่า CSV เป็น mock มี `case_id`/`owner` รหัส (อยู่ใน repo ที่ `data/` และ root)

---

## H. หลักฐาน Test / Validation

**ผลรันจริงที่พบใน session** (คำสั่ง `python3 -m pytest -q` ที่ `/home/looktal/lab-exam02102026`; ไม่มี commit ให้อ้างอิง — ไม่ทราบความสัมพันธ์กับ commit):

| เวลา (+07) | ผล | บริบท | Evidence |
|---|---|---|---|
| 11:18:08 | 7 failed, 37 passed | เขียน test ครั้งแรก (path ของ AppTest ผิด) | E017 |
| 11:18:30 | **44 passed in 19.58s** | หลังแก้ | E017 |
| 11:25:38 / 11:29:13 | 44 passed (19.65s / 20.40s) | หลังอัปเดต reference_date / เอกสาร | E018, E019 |
| 11:40:30→11:42:03 | 2 failed/69 passed → **71 passed in 37.56s** | หลังเพิ่ม AI tests | E021 |
| 11:52:28–11:53:51 | 71 passed (25.32s, 23.86s, 24.28s) | หลังปรับธีม | E025 |
| 11:59:13→12:00:54 | 1 failed/70 → 71 → **81 passed in 28.90s** | หลังเพิ่มสองภาษา | E027 |
| 12:09:11 / 12:10:31 | **82 passed** (31.07s / 29.23s) | หลังแก้ selectbox + changelog (ผลรันครั้งสุดท้าย) | E027 |

**Test code (นับแบบ static ตอนรวบรวม ไม่ได้รัน):** 64 ฟังก์ชัน test ใน 8 ไฟล์ (`test_ai_brief` 17, `test_i18n` 11, `test_ingest_contract` 9, `test_dashboard` 7, `test_runtime_guard` 7, `test_model_quality` 6, `test_metrics_golden` 5, `test_integration` 2); จำนวน 82 ที่รันมาจาก parametrize (VERIFIED เฉพาะตัวเลข 82 จากผลรันใน session; E033)

**กรณีทดสอบสำคัญ (ชื่อ test อ้างรหัสตาม `TESTING_STRATEGY.md`) — คาดหวัง/ผลจริง:**

| กลุ่ม | สิ่งที่ตรวจ | Expected (ในโค้ด test) | Actual |
|---|---|---|---|
| Validation (UT-001–005, 012; IT-002/003) | header ขาด/เกิน, ซ้ำ, ว่าง, enum, วันที่ผิด, ไฟล์อ่านไม่ได้, run ผิดไม่ทับของเดิม | block + รายงาน, state เดิมคงอยู่ | ผ่าน (รวมใน 82) |
| Model/DQ (UT-006–011) | grain, FK ไม่ orphan, dim grain, DQ error ผ่าน, uncalibrated=`not_calibrated` | ตามสเปก | ผ่าน |
| Golden metrics (MV-001–007) | fixture 10 แถวคำนวณมือ ref=2026-10-01: total 10/closed 2/open 8; by stage; Top 3 = G07(90), G02(60), G03(60); behavior/performance แยกกัน | ตรงค่ามือ | ผ่าน |
| Integration (IT-001, IT-004, IT-005, IT-006) | CSV จริง 40,000 แถว, rerun ซ้ำไม่เพิ่ม, filter ไม่ปะปน, ไม่มี reference_date → pending | ตรงที่ระบุ | ผ่าน |
| Runtime guard | ไม่มี `CURRENT_DATE`/system date ใน src/sql, ไม่มี secret ใน source | 0 match | ผ่าน |
| Dashboard (DA-001–006) | KPI, filter, Top 3, pending, drill-down, ข้อผิดพลาดของ CSV, masking | ตามสเปก | ผ่าน (AppTest) |
| AI | สำเร็จ/ล้มเหลว/malformed/persist/ไม่ส่ง field อ่อนไหว (endpoint จำลอง) | ตามสเปก | ผ่าน |
| i18n | TH/EN, สลับภาษาคง filter, ป้ายไทยตามที่กำหนด | ตามสเปก | ผ่าน |

**ข้อสังเกตสำหรับกรรมการ:** ไม่มีผลรัน CI/pipeline, ไม่มี smoke test บน deployment (DA-007 ไม่มีหลักฐาน), และ **ไม่ได้รัน test ซ้ำตอนรวบรวม** ตามข้อกำหนด

---

## I. หลักฐาน Repo และ Coolify

| รายการ | พบ | สถานะ |
|---|---|---|
| URL repo / remote | ไม่พบ (ไม่มี Git; `CONSTRAINTS.md`: `null`) | UNKNOWN |
| commit SHA ที่ส่งสอบ | ไม่พบ | UNKNOWN |
| หลักฐาน push (ทันเวลา/ไม่ทันเวลา) | ไม่พบ; ผู้สอบกล่าวว่าจะ commit/push เองผ่าน SourceTree [E008] | REPORTED / UNKNOWN |
| Deployment ID / URL / commit ที่ deploy | ไม่พบ | UNKNOWN |
| ผลเปิดใช้งานบน Coolify | ไม่พบ | UNKNOWN |
| ไฟล์เตรียม deploy | `Dockerfile`, `.dockerignore`, `.streamlit/config.toml`, `.env.example` (ไม่มีค่า secret) — **ไม่เคย build/ทดสอบ** | VERIFIED ว่ามีไฟล์; UNKNOWN ว่าใช้งานได้ |
| URL ที่ใช้งานได้ | เฉพาะ `http://localhost:8501` | VERIFIED [E020, E024] |

---

## J. หลักฐาน AI workflow โบนัส

**(1) Runtime AI workflow ในแอป** — พบ implementation, **ไม่พบหลักฐานเรียก endpoint จริง**
- Trigger: ปุ่ม "Generate Process Improvement Brief" (`gen_brief`) ใน `src/cpd/dashboard.py` (`render_ai_section`, บรรทัด 100)
- Input จาก DB: `build_aggregate` (`ai_brief.py:69`) ใช้ metric layer ส่งเฉพาะ total/open/closed, open by stage, Top 3 เป็น rank/stage/days, filter, reference_date, run_id — ไม่ส่ง `case_id`/`owner`/วันที่รายแถว; มี validator ปฏิเสธ field เกิน (VERIFIED จากโค้ดและ test)
- AI call: `_http_post` (`ai_brief.py:109`) รับ URL/key/model จาก env (`CPD_AI_ENDPOINT_URL`, `CPD_AI_API_KEY`, `CPD_AI_MODEL`, `CPD_AI_TIMEOUT_SECONDS`, `CPD_AI_AUTH_HEADER`); รูปแบบ API เป็น**ข้อสมมติ** (OpenAI-compatible) เพราะ DDD ระบุ `null`
- การตรวจ output: parse ผล (`MalformedResponse` เมื่อรูปแบบผิด/ข้อความว่าง); จัดหมวด error (auth/rate/endpoint/malformed); ไม่เก็บ URL/key ใน error
- บันทึก/แสดง: ตาราง `ai_brief` ใน `runs/ai_briefs.duckdb` (field: brief_id, generated_at, run_id, case_domain_filter, reference_date, model_identifier, brief_text, generation_status, error_*) และส่วนแสดงบน dashboard
- หลักฐานการทำงาน: **เฉพาะ endpoint จำลองใน test** (17 test ผ่านรวมใน 71/82 passed [E021]); รันแอปจริงหนึ่งครั้งโดยชี้ endpoint ไปที่ที่เชื่อมต่อไม่ได้เพื่อดู core ทำงาน: health=200 [E022] (ไม่ได้กดปุ่มสร้าง)
- Logs/ข้อมูลที่บันทึกจริง: ไม่พบไฟล์ `runs/ai_briefs.duckdb`; ไม่มี log การเรียก endpoint จริง
- ไม่มีค่า threshold/latency/quota ถูกตั้ง (ตรงตาม DDD ที่เป็น `null`)

**(2) การใช้ Claude Code ช่วยเขียนโค้ด:** ใช้ตลอด session (ดู A, E) — แยกจาก runtime AI workflow ข้างต้น

---

## K. ตารางหลักฐานตามเกณฑ์สอบ

| หัวข้อ | หลักฐานที่รองรับ | Evidence | สถานะหลักฐาน | สิ่งที่ยังยืนยันไม่ได้ |
|---|---|---|---|---|
| ประโยชน์และฟังก์ชันหลัก | Dashboard แสดง Total/Closed/Open, stage, aging, Top 3, filter domain; รันจริงในเครื่อง; ตัวเลขบน CSV จริงใน output ของ session | E018, E020, E024, E026 | VERIFIED (local) | การใช้งานบน deployment; การตรวจหน้าจอโดยกรรมการ |
| การใช้ DDD | อ่านเอกสาร DDD ก่อนเริ่ม; โครงสร้าง pipeline/metric/DQ/test อ้างเอกสาร; แก้เอกสารให้ตรง implementation และบันทึก changelog | E014, E016, E019, E027, E035 | VERIFIED (ว่าทำ) / INFERRED (ว่าตรงเจตนา) | คุณภาพการ reconcile ฉบับเต็ม; T01–T09 สถานะไม่อัปเดต |
| ฐานข้อมูลและ persistence | DuckDB ไฟล์ต่อ run + pointer; idempotent rerun (test); หลักฐานไฟล์ใน `runs/` | E031, E032 | VERIFIED (local) | persistence บน Coolify; เนื้อใน DB ตอนรวบรวมไม่ได้ query |
| Test / Validation | ผลรัน 44 → 71 → 82 passed ใน session ตามตารางข้อ H | E017–E027 | VERIFIED (ผลรันใน session) | ความสัมพันธ์กับ commit; CI; smoke test deploy |
| Push repo และ Coolify deployment | ไม่พบ Git/remote/deploy | E029, E036 | UNKNOWN | ทุกอย่าง |
| การใช้งานและส่งมอบ | README (วิธีรัน/env), `.env.example`, `Dockerfile`, `.gitignore`, สคริปต์ `app.py` | E016, E023, E025 | VERIFIED (ว่ามีไฟล์) | ใช้งานได้บนเครื่องอื่น/ใน container |
| AI workflow โบนัส | implementation + tests ด้วย endpoint จำลอง | E021, E022 | VERIFIED (implementation/test); UNKNOWN (เรียกจริง) | การเรียก endpoint ของบริษัท, brief ที่บันทึกจริง, quota |

**เงื่อนไขบังคับแยกรายการ**

| เงื่อนไข | สถานะ | หมายเหตุ |
|---|---|---|
| ฟังก์ชันหลักใช้ได้ | VERIFIED (local, TIME_UNKNOWN*) | จาก output ใน session [E024]; deployment ไม่ทราบ |
| ใช้ DB จริง | VERIFIED (local) | DuckDB ไฟล์ + คิวรีใน session [E024, E031] |
| มี Test/Validation ผ่าน | VERIFIED (ผลรันใน session, TIME_UNKNOWN*) | 82 passed (ครั้งสุดท้ายก่อนสิ้นสุด) [E027]; ไม่ทราบ commit |
| push ทันเวลา | UNKNOWN | ไม่มีหลักฐาน push และไม่ทราบเวลาสอบ |
| deploy เปิดใช้ทันเวลา | UNKNOWN | ไม่มีหลักฐาน deploy และไม่ทราบเวลาสอบ |

---

## L. Evidence Index

> ข้อความผู้สอบเป็นส่วนย่อ (Thai/EN) ตัดเฉพาะที่จำเป็น; ไม่มี secret/ข้อมูลส่วนบุคคล (ข้อมูลบัญชีผู้ใช้ไม่ถูกนำมาใช้หรือบันทึก) ช่วงเวลา: `TIME_UNKNOWN*` ตามนิยามด้านบน

| ID | แหล่งและตำแหน่ง | Excerpt (ย่อ) | ช่วงเวลา | ข้อเท็จจริงที่รองรับ |
|---|---|---|---|---|
| E001 | transcript ของ session (ไฟล์ `.jsonl` ใน `~/.claude/projects/-home-looktal-lab-exam02102026/`) ระเบียนแรก–สุดท้าย | first `2026-10-02T04:09:11Z`, last `…05:12:57Z`; `/effort`→medium, `/model`→`Sonnet 5.5`; tool calls: Bash 80, Read 12 | AFTER_EXAM (อ่านตอนรวบรวม) | ช่วงเวลา session, โมเดล, จำนวน tool calls |
| E002 | ข้อความผู้สอบ 11:10:35 | "โปรเจกต์นี้คือ `Consequence Process Dashboard` และใช้ `ddd-data-analytics` เป็น blueprint หลัก … จากนั้นยังไม่ต้อง implement" | TIME_UNKNOWN* | โจทย์/track/ข้อห้าม |
| E003 | ข้อความ 11:14:08 | "ให้ใช้ business rules … `reference_date`: ตอนนี้ยังไม่มีค่า … เลือกใช้ Streamlit … ยังไม่ต้องทำ AI bonus" | TIME_UNKNOWN* | กติกาธุรกิจ + เลือก Streamlit + สั่ง implement core |
| E004 | ข้อความ 11:24:45 | "Confirm project assumption: reference_date = 2026-10-01 … project-specific" | TIME_UNKNOWN* | ค่า reference_date |
| E005 | ข้อความ 11:27:16 | "The implementation and blocking tests are now passing. I am confirming … business decisions … reconcile the DDD documentation" | TIME_UNKNOWN* | ยืนยัน rules; สั่ง certify/changelog/T10 |
| E006 | ข้อความ 11:34:27 | "Please run this Streamlit app locally using app.py and tell me the localhost URL." | TIME_UNKNOWN* | สั่งรันแอป |
| E007 | ข้อความ 11:38:54 | "Now implement the optional AI bonus described in AI_MODEL_SPEC.md." | TIME_UNKNOWN* | สั่งทำ AI bonus |
| E008 | ข้อความ 11:45:51 | "Create a .gitignore … Do not run git commands. I will commit and push manually using SourceTree." | TIME_UNKNOWN* | ผู้สอบจะ commit/push เอง (REPORTED) |
| E009 | ข้อความ 11:47:54 | "Please run the Consequence Process Dashboard locally and verify it is usable. 1. Activate the existing project virtual environment…" | TIME_UNKNOWN* | สั่งรัน/ตรวจ |
| E010 | ข้อความ 11:50:47 | "restyle … Ragnar red, white, and warm cream. Do not change any business logic…" | TIME_UNKNOWN* | สั่งปรับธีม |
| E011 | ข้อความ 11:55:03 | "ขอดูหน้าจอจริงก่อน แล้วค่อยปรับ" | TIME_UNKNOWN* | ผู้สอบขอดูผลก่อนปรับ |
| E012 | ข้อความ 11:57:13 | "add bilingual UI support … TH / EN … Translate presentation text only." | TIME_UNKNOWN* | สั่งสองภาษา |
| E013 | ข้อความ 12:12:16 | "งานสอบ Practical สิ้นสุดแล้ว ให้รวบรวมหลักฐาน…" | AFTER_EXAM (ข้อความที่ระบุว่าสอบสิ้นสุด) | ผู้สอบแจ้งสิ้นสุด (REPORTED) |
| E014 | tool calls #001–008 (11:10:37–11:11:02) | `cat dddi-main/*.md`; CSV: `['case_id','case_domain','response_type','stage','stage_entered_date','owner'] 40000`; stage: closed 17706, reviewing 9022, follow_up 8812, collecting_info 4460; dups 0; blank 0; owners 8; date 2026-04-04..2026-10-01 | TIME_UNKNOWN* | อ่าน DDD; ข้อมูล CSV |
| E015 | tool calls #009–011 | pip: `externally-managed` hint; venv: `Failing command: …/.venv/bin/python3`; `pip install --user --break-system-packages pytest` → `Successfully installed … pytest-9.1.1` | TIME_UNKNOWN* | ข้อจำกัด environment |
| E016 | tool calls #012–014, #017–018; ไฟล์ใน repo | `status=published run_id=43ed417f4b4f-noref rows=40000`; `Dockerfile`, `README.md` สร้าง | TIME_UNKNOWN* | สร้าง core pipeline; รันจริงครั้งแรก |
| E017 | tool calls #015–016 | `7 failed, 37 passed` → `44 passed in 19.58s` | TIME_UNKNOWN* | test ครั้งแรกและหลังแก้ |
| E018 | tool calls #019–024 | `44 passed in 19.65s`; `status=published run_id=43ed417f4b4f-2026-10-01 rows=40000`; grep CURRENT_DATE ใน code = 0 | TIME_UNKNOWN* | ใช้ 2026-10-01; ไม่มี system date |
| E019 | tool calls #025–030 | `44 passed in 20.40s`; "13 ไฟล์ (+121/−78 บรรทัด)" เทียบ snapshot; `fatal: not a git repository` | TIME_UNKNOWN* | reconcile เอกสาร; metric certified |
| E020 | tool calls #031–032 | `health=200`, `page=200`, "Local URL: http://localhost:8501" | TIME_UNKNOWN* | แอปรันได้ในเครื่อง |
| E021 | tool calls #033–038; `src/cpd/ai_brief.py`; `tests/test_ai_brief.py` | `2 failed, 69 passed` → `71 passed in 37.56s`; `pkill` exit 144 | TIME_UNKNOWN* | AI bonus + tests |
| E022 | tool call #039 | รันด้วย `CPD_AI_ENDPOINT_URL=http://127.0.0.1:9/none CPD_AI_API_KEY=[REDACTED]` → `health=200` | TIME_UNKNOWN* | core ใช้ได้เมื่อ AI ไม่พร้อม (ไม่ได้กดสร้าง) |
| E023 | tool calls #040–041; `.gitignore` | สแกน secret ไม่พบค่า; มีเฉพาะ `.env.example` (ค่าว่าง) | TIME_UNKNOWN* | เตรียม commit; ไม่มี secret ที่พบ |
| E024 | tool call #042 | `ls -d .venv venv` → `cannot access`; `status=published run_id=43ed417f4b4f-2026-10-01 rows=40000`; `health=200 page=200`; `[40000, 17706, 22294]` | TIME_UNKNOWN* | รันตามขั้นตอนผู้สอบ; ไม่มี venv |
| E025 | tool calls #043–050 | `71 passed in 25.32s` / `23.86s` / `24.28s`; contrast ที่คำนวณ เช่น text/cream 14.2:1 | TIME_UNKNOWN* | ปรับธีมโดยไม่กระทบ test |
| E026 | tool calls #051–058 + ภาพใน scratchpad (22 ไฟล์ `.png`) | `libnspr4.so … cannot open` → ได้ภาพ; รายการปัญหา 10 ข้อที่เสนอและยังไม่แก้ | TIME_UNKNOWN* | ตรวจหน้าจอจริง |
| E027 | tool calls #059–075; `src/cpd/i18n.py`; `tests/test_i18n.py` | `81 passed in 28.90s` → `82 passed in 31.07s` → `82 passed in 29.23s`; บั๊ก selectbox ค้างภาษา | TIME_UNKNOWN* | สองภาษา + ผลรันครั้งสุดท้าย |
| E028 | `src/cpd/ingest.py:27`, `model.py:11`, `quality.py:23`, `publish.py:15`, `pipeline.py:20`, `ai_brief.py:69/109/181`, `dashboard.py:100/131`; `sql/metrics.sql` (9 `-- name:`) | (ผลจาก `rg -n`) | AFTER_EXAM (อ่านตอนรวบรวม) | ตำแหน่ง implementation |
| E029 | คำสั่งรวบรวม #076 | `2026-10-02 12:12:42 +07`; `/home/looktal/lab-exam02102026`; `fatal: not a git repository (or any of the parent directories): .git` | AFTER_EXAM | เวลาเริ่มรวบรวม; ไม่มี Git |
| E030 | คำสั่งรวบรวม #077 | รายการไฟล์พร้อม mtime (เช่น CSV root 10:19; `dddi-main/SLA_FRESHNESS.md` 10:52; src/tests 11:16–12:09) | AFTER_EXAM | mtime ของไฟล์ — **ไม่ใช่หลักฐานเวลาทำเสร็จ** |
| E031 | `runs/published.json`, `runs/last_run.json`, `ls runs` | `{"run_id": "43ed417f4b4f-2026-10-01", "status": "published", "row_count": 40000, "aging_status": "available", "reference_date": "2026-10-01", "started_at": "2026-10-02T04:48:01+00:00"}`; DB 3,682,304 ไบต์; ไม่มี `ai_briefs.duckdb` | AFTER_EXAM (ไฟล์ที่สร้างตอน 11:48) | ผล run ที่ publish |
| E032 | `sha256sum` CSV (data/ และ root) | `43ed417f4b4f1d81…` เหมือนกันทั้งสองไฟล์ | AFTER_EXAM | snapshot_id ตรงกับ CSV |
| E033 | `rg -c "^def test_" tests` | รวม 64 ฟังก์ชันใน 8 ไฟล์ | AFTER_EXAM | จำนวน test (static) |
| E034 | `rg` สแกนที่ `sql src app.py config` และ source | ไม่พบ `CURRENT_DATE/CURRENT_TIMESTAMP/date.today/now()`; ไม่พบ pattern secret | AFTER_EXAM | ไม่มี system date/secret ใน code ที่สแกน |
| E035 | `dddi-main/METRIC_SPEC.md` (บรรทัด 28,42,56,70,84,100), `dddi-main/TASKS.md` (บรรทัด 20–30) | `metric_status: certified` ×6; T10/T11 `done`; T01–T09 `not started` | AFTER_EXAM | สถานะเอกสาร |
| E036 | `dddi-main/CONSTRAINTS.md` (หัวข้อ Project Budget & Timeline, Integration Constraints) | "Delivery time limit: 120 นาที…"; "Company repository: repository URL … = `null`"; "Coolify … = `null`"; "Reference date value: `2026-10-01` — project-specific exam assumption" | AFTER_EXAM (เนื้อหาเอกสารที่มีใน session) | กรอบเวลา; repo/Coolify ยังเป็น `null` |
| E037 | บริบท session (ข้อความผู้สอบแทรกกลางงาน) | "If changing reference_date changes expected metric outputs or Top 3 results, update the tests and documentation … but do not alter the metric formulas" | TIME_UNKNOWN* | REPORTED: ไม่ปรากฏเป็นระเบียนแยกใน transcript ที่ตรวจ |

---

## รายการที่กรรมการควรตรวจเพิ่มเติม

1. เวลาเริ่ม–หมดเวลาสอบจริง และเวลาที่ผู้สอบ commit/push (ไม่มีใน session/repo)
2. Git repository ของบริษัท: commit SHA ที่ส่งสอบ และเวลา push จริง
3. Coolify: deployment ID/URL, commit ที่ deploy, ผลเปิดใช้งานและ smoke test
4. ผลรัน test ที่เชื่อมกับ commit ที่ส่ง (ผลใน session ไม่มี commit อ้างอิง) หรือ CI ถ้ามี
5. ผู้สอบชื่ออะไร/ตำแหน่งใด และบทสนทนาก่อนเริ่ม session นี้ (ถ้ามี) — ไม่มีใน session
6. การตรวจ/ปรับ output ของ AI โดยผู้สอบนอกเหนือจากข้อความในข้อ E
7. การเรียก AI endpoint จริงของบริษัท (ถ้ามี) และ brief ที่บันทึก
8. ข้อมูลการใช้ token/quota ของ session
9. ตรวจหน้าจอ dashboard ด้วยตนเอง (ภาพใน scratchpad: `/tmp/claude-1000/-home-looktal-lab-exam02102026/0efb67e5-aa7e-424c-a967-1bad178d0fdf/scratchpad/`) และความสอดคล้องกับ `VIZ_DESIGN_SPEC.md`

---

### การตรวจรายงานก่อนส่ง (บันทึก)
- ข้อสรุปสำคัญอ้าง Evidence ID E001–E037 ที่มีใน Evidence Index
- แยกคำกล่าว (REPORTED) ออกจากผลที่ยืนยัน (VERIFIED) และแยกช่วงสอบ/หลังสอบด้วย `TIME_UNKNOWN*`/`AFTER_EXAM`
- ไม่มี secret/ข้อมูลส่วนบุคคลในรายงาน (API key ที่ตั้งในคำสั่งทดลองถูกแทนด้วย `[REDACTED]`)
- การสร้างรายงานนี้สร้างไฟล์เดียวในโฟลเดอร์ `lab-exam02102026-evidence/`; ไม่แก้ไฟล์/Git state อื่น และไม่รัน test/app ซ้ำ
