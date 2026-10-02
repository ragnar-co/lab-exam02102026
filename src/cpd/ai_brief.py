"""Optional AI bonus: Process Improvement Brief (AI_MODEL_SPEC.md). Experimental; not a core dependency.

Only approved aggregate outputs are sent (no case_id, owner, dates). Endpoint, key and model come from
environment variables / Coolify secrets. Wire format is an ASSUMPTION (OpenAI-compatible chat completions)
because the DDD leaves endpoint/auth method as null. No retry/timeout/latency numbers are invented.
"""
import json
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import pandas as pd

from . import metrics

ENV_URL, ENV_KEY, ENV_MODEL = "CPD_AI_ENDPOINT_URL", "CPD_AI_API_KEY", "CPD_AI_MODEL"
ENV_TIMEOUT, ENV_AUTH_HEADER = "CPD_AI_TIMEOUT_SECONDS", "CPD_AI_AUTH_HEADER"
STORE_NAME = "ai_briefs.duckdb"

AGG_KEYS = {"case_domain_filter", "reference_date", "run_id", "total_cases", "open_cases", "closed_cases",
            "open_cases_by_stage", "top_3_longest_open_cases"}
TOP3_KEYS = {"rank", "stage", "days_in_current_stage"}  # no case_id / owner / dates
UNAVAILABLE = "unavailable"

SYSTEM_PROMPT = """You help an HR Process Owner review the Consequence Process. You receive ONLY aggregate analytics
from one dashboard run. Write a short draft Process Improvement Brief in Thai with exactly three sections:
1. จุดที่ควรตรวจสอบ (process areas that may need review)
2. ข้อสังเกตคอขวด (observable bottlenecks in this snapshot)
3. ข้อเสนอปรับปรุงขั้นตอน (process-improvement ideas)
Rules: describe only what the numbers show, using wording such as "ควรตรวจสอบ" or "พบการกระจุกตัว/ค้างใน snapshot นี้".
Do not label values good/bad against any threshold and do not propose automatic escalation. If a field is
"unavailable", say it is unavailable and do not guess. You MUST NOT make or suggest disciplinary decisions, score or
rank any employee, infer intent, personality or mental state, identify individuals, or replace HR approval.
The brief is a draft for human review only."""


class MalformedResponse(Exception):
    pass


@dataclass(frozen=True)
class AIConfig:
    url: str | None
    api_key: str | None
    model: str | None
    timeout: float | None
    auth_header: str

    @property
    def configured(self) -> bool:
        return bool(self.url and self.api_key)


def load_ai_config(env) -> AIConfig:
    t = (env.get(ENV_TIMEOUT) or "").strip()
    return AIConfig(env.get(ENV_URL) or None, env.get(ENV_KEY) or None, env.get(ENV_MODEL) or None,
                    float(t) if t else None, env.get(ENV_AUTH_HEADER) or "Authorization")


def store_path(runs: Path) -> Path:
    return Path(runs) / STORE_NAME


# ---------- input (approved aggregates only) ----------
def build_aggregate(con, case_domain=None) -> dict:
    st = metrics.run_status(con)
    ref = st["reference_date"]
    agg = {
        "case_domain_filter": case_domain or "all",
        "reference_date": ref.isoformat() if ref else UNAVAILABLE,
        "run_id": st["run_id"],
        "total_cases": int(metrics.scalar(con, "metric_total_cases", case_domain)),
        "open_cases": int(metrics.scalar(con, "metric_open_cases", case_domain)),
        "closed_cases": int(metrics.scalar(con, "metric_closed_cases", case_domain)),
        "open_cases_by_stage": {r.stage: int(r.metric_open_cases_by_stage) for r in metrics.open_by_stage(con, case_domain).itertuples()},
    }
    top = metrics.top3(con, case_domain)
    agg["top_3_longest_open_cases"] = UNAVAILABLE if top is None else [
        {"rank": i, "stage": r.stage, "days_in_current_stage": int(r.metric_days_in_current_stage)}
        for i, r in enumerate(top.itertuples(), 1)]
    validate_aggregate(agg)
    return agg


def validate_aggregate(agg: dict) -> None:
    if set(agg) != AGG_KEYS:
        raise ValueError(f"unexpected aggregate fields: {sorted(set(agg) ^ AGG_KEYS)}")
    top = agg["top_3_longest_open_cases"]
    if top != UNAVAILABLE:
        for row in top:
            if set(row) != TOP3_KEYS:
                raise ValueError("top-3 context must use minimum necessary fields only")


def build_payload(agg: dict, model: str | None) -> dict:
    validate_aggregate(agg)
    body = {"messages": [{"role": "system", "content": SYSTEM_PROMPT},
                         {"role": "user", "content": json.dumps(agg, ensure_ascii=False, sort_keys=True)}]}
    if model:
        body["model"] = model
    return body


# ---------- endpoint ----------
def _http_post(url, headers, body: bytes, timeout):
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")


def parse_response(raw: str):
    try:
        data = json.loads(raw)
        text = data["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise MalformedResponse("response is not the expected chat-completion shape") from exc
    if not isinstance(text, str) or not text.strip():
        raise MalformedResponse("empty or non-text brief")
    model = data.get("model") if isinstance(data.get("model"), str) else None
    return text.strip(), model


def _category(status: int) -> str:
    if status in (401, 403):
        return "auth_failure"
    if status == 429:
        return "rate_limited"
    return "endpoint_error"


# ---------- persistence (separate DB so briefs survive pipeline reruns) ----------
def _store(path: Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(path))
    con.execute("""CREATE TABLE IF NOT EXISTS ai_brief(
        brief_id VARCHAR PRIMARY KEY, generated_at TIMESTAMP, run_id VARCHAR, case_domain_filter VARCHAR,
        reference_date DATE, model_identifier VARCHAR, brief_text VARCHAR, generation_status VARCHAR,
        error_category VARCHAR, error_message VARCHAR)""")
    return con


def persist(path: Path, rec: dict) -> None:
    con = _store(path)
    try:
        con.execute("INSERT INTO ai_brief VALUES (?,?,?,?,?,?,?,?,?,?)",
                    [rec["brief_id"], rec["generated_at"], rec["run_id"], rec["case_domain_filter"], rec["reference_date"],
                     rec["model_identifier"], rec["brief_text"], rec["generation_status"], rec["error_category"], rec["error_message"]])
    finally:
        con.close()


def latest_brief(path: Path):
    """Most recent attempt (success or failed); None if nothing stored or store unreadable."""
    if not Path(path).exists():
        return None
    try:
        con = _store(path)
        try:
            df = con.execute("SELECT * FROM ai_brief ORDER BY generated_at DESC, rowid DESC LIMIT 1").df()
        finally:
            con.close()
    except duckdb.Error:
        return None
    if df.empty:
        return None
    rec = df.iloc[0].to_dict()
    ref = rec["reference_date"]
    rec["reference_date"] = None if pd.isna(ref) else ref.date()
    return {k: (None if (not isinstance(v, (list, dict)) and pd.isna(v)) else v) for k, v in rec.items()}


# ---------- orchestration ----------
def generate_brief(con, case_domain, cfg: AIConfig, path: Path) -> dict:
    """Build aggregate -> call endpoint -> persist. Never raises for AI/endpoint problems."""
    if not cfg.configured:
        return {"generation_status": "not_configured", "error_category": "not_configured",
                "error_message": f"set {ENV_URL} and {ENV_KEY}", "brief_text": ""}
    agg = build_aggregate(con, case_domain)
    ref = metrics.run_status(con)["reference_date"]
    rec = {"brief_id": str(uuid.uuid4()), "generated_at": datetime.now(timezone.utc).replace(tzinfo=None),
           "run_id": agg["run_id"], "case_domain_filter": agg["case_domain_filter"], "reference_date": ref,
           "model_identifier": cfg.model, "brief_text": "", "generation_status": "failed",
           "error_category": None, "error_message": None}
    try:
        body = json.dumps(build_payload(agg, cfg.model)).encode("utf-8")
        headers = {"Content-Type": "application/json", cfg.auth_header: f"Bearer {cfg.api_key}"}
        status, raw = _http_post(cfg.url, headers, body, cfg.timeout)
        if status < 200 or status >= 300:
            rec.update(error_category=_category(status), error_message=f"endpoint returned HTTP {status}")
        else:
            text, model = parse_response(raw)
            rec.update(brief_text=text, generation_status="success", model_identifier=model or cfg.model)
    except MalformedResponse as exc:
        rec.update(error_category="malformed_response", error_message=str(exc))
    except Exception as exc:  # network/DNS/timeout etc.; never echo exception text (may contain URL)
        rec.update(error_category="endpoint_unavailable", error_message=f"endpoint request failed ({type(exc).__name__})")
    try:
        persist(path, rec)
    except Exception as exc:
        rec.update(generation_status="failed", error_category="persistence_failure",
                   error_message=f"could not persist brief ({type(exc).__name__})")
    return rec
