# Consequence Process Dashboard

Core app per `dddi-main/` (DDD docs): CSV → validation → DuckDB staging → fact/dim → metric views → Streamlit.

```bash
pip install -r requirements.txt
python app.py --load data/looktal_consequence_mock_2-3MB.csv            # validate + load (reference_date from config = 2026-10-01)
python app.py --load data/looktal_consequence_mock_2-3MB.csv --reference-date YYYY-MM-DD   # override (e.g. for tests); normally comes from config
python -m pytest -q                                                      # blocking tests
python app.py                                                            # dashboard (loads default CSV if nothing published)
```

Runtime inputs: `CPD_REFERENCE_DATE` (or `--reference-date`; system date is never used), `CPD_RUNS_DIR`, `CPD_CONFIG`, `CPD_MASK_IDENTIFIERS`, `PORT`.
`reference_date = 2026-10-01` lives in `config/runtime_config.json` as a **project-specific exam assumption** (not an industry standard, not supplied by the original exam brief).
`config/runtime_config.json` also holds the project-specific open/closed mapping, calendar-day count and Top-3 tie-break (`days DESC, case_id ASC`).

Each run builds `runs/<run_id>.duckdb`; `runs/published.json` switches atomically only after DQ error rules pass, so an invalid CSV keeps the previous valid state.
Tested with Python 3.12.3, duckdb 1.5.5, streamlit 1.63.0, pandas 3.0.5, pytest 9.1.1.
Without a reference_date (empty config and env) aging/Top 3 show pending. Not yet done: repository push, Coolify deploy (credentials/URLs are `null` in the DDD docs), production PDPA enforcement layer.

## Optional AI bonus (Process Improvement Brief)
Dashboard section "Process Improvement Brief" generates an AI draft from approved aggregates only (totals, open by stage, Top 3 as rank/stage/days, domain filter, reference_date) — no `case_id`/`owner`/dates are sent. Briefs are stored in `runs/ai_briefs.duckdb` (survives pipeline reruns). AI failure never affects the core dashboard.
Env vars (values from Coolify secrets, never committed): `CPD_AI_ENDPOINT_URL`, `CPD_AI_API_KEY` (both required to enable), `CPD_AI_MODEL`, `CPD_AI_TIMEOUT_SECONDS`, `CPD_AI_AUTH_HEADER` (optional; default header `Authorization: Bearer <key>`).
Assumption: the DDD leaves endpoint/auth/format `null`; the client speaks OpenAI-compatible chat-completions JSON. No retry, timeout, latency or quality thresholds are configured unless set by env.
