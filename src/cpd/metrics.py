"""pl_build_consequence_metrics + parametrised metric queries. SQL lives in sql/ (METRIC_LOGIC.md)."""
import re

import pandas as pd

from .config import SQL_DIR, RuntimeInputs


def _load_named_queries() -> dict[str, str]:
    text = (SQL_DIR / "metrics.sql").read_text(encoding="utf-8")
    parts = re.split(r"^-- name: (\w+)\s*$", text, flags=re.M)
    return {parts[i]: parts[i + 1].strip() for i in range(1, len(parts), 2)}


QUERIES = _load_named_queries()


def setup_runtime_inputs(con, inputs: RuntimeInputs) -> None:
    con.execute("CREATE OR REPLACE TABLE runtime_inputs(reference_date DATE, day_count_mode VARCHAR, top3_tie_break VARCHAR)")
    con.execute("INSERT INTO runtime_inputs VALUES (?, ?, ?)", [inputs.reference_date, inputs.day_count_mode, inputs.top3_tie_break])
    for table, stages in (("approved_open_stage_values", inputs.open_stages), ("approved_closed_stage_values", inputs.closed_stages)):
        con.execute(f"CREATE OR REPLACE TABLE {table}(stage VARCHAR)")
        for s in stages:
            con.execute(f"INSERT INTO {table} VALUES (?)", [s])


def build_core_views(con) -> None:
    con.execute((SQL_DIR / "views.sql").read_text(encoding="utf-8"))


def build_aging_views(con) -> None:
    con.execute((SQL_DIR / "aging_views.sql").read_text(encoding="utf-8"))


def drop_aging_views(con) -> None:
    con.execute("DROP VIEW IF EXISTS mart_top3_longest_open_cases")
    con.execute("DROP VIEW IF EXISTS mart_consequence_case_aging")


def run_status(con) -> dict:
    row = con.execute("SELECT run_id, snapshot_id, row_count, reference_date, aging_status, aging_reason FROM run_metadata").fetchone()
    return dict(zip(("run_id", "snapshot_id", "row_count", "reference_date", "aging_status", "aging_reason"), row))


def aging_available(con) -> bool:
    return run_status(con)["aging_status"] == "available"


def _q(con, name, **params) -> pd.DataFrame:
    full = {"case_domain": None, "case_status": None, "stage": None}
    full.update(params)
    needed = set(re.findall(r"\$(\w+)", QUERIES[name]))
    return con.execute(QUERIES[name], {k: v for k, v in full.items() if k in needed}).df()


def scalar(con, name, case_domain=None):
    return _q(con, name, case_domain=case_domain).iloc[0, 0]


def open_by_stage(con, case_domain=None) -> pd.DataFrame:
    return _q(con, "metric_open_cases_by_stage", case_domain=case_domain)


def case_aging(con, case_domain=None):
    """None means pending/unavailable (never 0, never system date)."""
    return _q(con, "metric_days_in_current_stage", case_domain=case_domain) if aging_available(con) else None


def top3(con, case_domain=None):
    return _q(con, "metric_top_3_longest_open_cases", case_domain=case_domain) if aging_available(con) else None


def case_list(con, case_domain=None, case_status=None, stage=None) -> pd.DataFrame:
    return _q(con, "case_list", case_domain=case_domain, case_status=case_status, stage=stage)


def case_domains(con) -> list[str]:
    return [r[0] for r in con.execute("SELECT case_domain FROM dim_case_domain ORDER BY 1").fetchall()]


def stages(con) -> list[str]:
    return [r[0] for r in con.execute("SELECT stage FROM dim_stage ORDER BY 1").fetchall()]
