"""DATA_QUALITY.md DQ-001..015 as runnable assertions. Uncalibrated rules report not_calibrated."""
from . import contract as C

FAIL, PASS, NOT_CAL, PENDING = "fail", "pass", "not_calibrated", "pending"


def _rows(con, sql, params=None):
    return con.execute(sql, params or []).fetchall()


def _assert_zero(rule_id, name, severity, con, sql, scope="core", params=None):
    n = len(_rows(con, sql, params))
    return dict(rule_id=rule_id, name=name, severity=severity, scope=scope,
                status=PASS if n == 0 else FAIL, failing_rows=n, detail="")


def _info(rule_id, name, con, sql, scope="core"):
    detail = "; ".join(f"{r[0]}={r[1]}" for r in _rows(con, sql))
    return dict(rule_id=rule_id, name=name, severity="warning", scope=scope,
                status=NOT_CAL, failing_rows=0, detail=f"threshold null (not calibrated); observed {detail}")


def run_core(con, inputs) -> list[dict]:
    r = []
    r.append(_assert_zero("DQ-001", "required fields non-null", "error", con,
        "SELECT 1 FROM fact_consequence_case WHERE case_id IS NULL OR case_domain_key IS NULL OR response_type_key IS NULL OR stage_key IS NULL OR stage_entered_date IS NULL OR owner_key IS NULL"))
    r.append(_info("DQ-002", "snapshot completeness", con,
        "SELECT 'total_rows', COUNT(*) FROM stg_consequence_case"))
    r.append(_assert_zero("DQ-003", "no duplicate case_id (staging)", "error", con,
        "SELECT case_id FROM stg_consequence_case GROUP BY case_id HAVING COUNT(*) > 1"))
    r.append(_assert_zero("UT-006", "fact grain: 1 row per case_id", "error", con,
        "SELECT case_id FROM fact_consequence_case GROUP BY case_id HAVING COUNT(*) > 1"))
    if inputs.reference_date is None:
        r.append(dict(rule_id="DQ-004", name="stage_entered_date <= reference_date", severity="error", scope="aging",
                      status=PENDING, failing_rows=0, detail="reference_date not provided"))
    else:
        r.append(_assert_zero("DQ-004", "stage_entered_date <= reference_date", "error", con,
            "SELECT case_id FROM fact_consequence_case WHERE stage_entered_date > CAST(? AS DATE)", scope="aging",
            params=[inputs.reference_date]))
    r.append(_assert_zero("DQ-005", "categorical values within contract", "error", con,
        f"""SELECT * FROM stg_consequence_case WHERE case_domain NOT IN ({C.sql_list(C.CASE_DOMAINS)})
            OR response_type NOT IN ({C.sql_list(C.RESPONSE_TYPES)}) OR stage NOT IN ({C.sql_list(C.STAGES)})"""))
    r.append(_assert_zero("DQ-006", "case_id/owner non-empty", "error", con,
        "SELECT * FROM stg_consequence_case WHERE TRIM(case_id) = '' OR TRIM(owner) = ''"))
    cols = [x[0] for x in _rows(con, "SELECT column_name FROM information_schema.columns WHERE table_name='stg_consequence_case' ORDER BY column_name")]
    ok = cols == sorted(C.REQUIRED_COLUMNS)
    r.append(dict(rule_id="DQ-007", name="schema matches contract", severity="error", scope="core",
                  status=PASS if ok else FAIL, failing_rows=0 if ok else 1, detail=""))
    for rid, dim, key in (("DQ-008", "dim_case_domain", "case_domain_key"), ("DQ-009", "dim_response_type", "response_type_key"),
                          ("DQ-010", "dim_stage", "stage_key"), ("DQ-011", "dim_owner", "owner_key")):
        r.append(_assert_zero(rid, f"{key} resolves", "error", con,
            f"SELECT f.case_id FROM fact_consequence_case f LEFT JOIN {dim} d ON f.{key} = d.{key} WHERE d.{key} IS NULL"))
    r.append(_info("DQ-012", "row volume anomaly", con, "SELECT 'current_row_count', COUNT(*) FROM stg_consequence_case"))
    r.append(_info("DQ-013", "stage distribution shift", con, "SELECT stage, COUNT(*) FROM stg_consequence_case GROUP BY stage ORDER BY stage"))
    r.append(_info("DQ-014", "case_domain mix shift", con, "SELECT case_domain, COUNT(*) FROM stg_consequence_case GROUP BY case_domain ORDER BY case_domain"))
    # every stage must map to exactly one of open/closed (approved rule coverage)
    r.append(_assert_zero("MAP-001", "every stage maps to exactly one of open/closed", "error", con,
        "SELECT stage FROM mart_consequence_case_metrics WHERE case_status = 'unmapped' GROUP BY stage"))
    return r


def run_aging(con, available: bool) -> dict:
    if not available:
        return dict(rule_id="DQ-015", name="no negative aging", severity="error", scope="aging",
                    status=PENDING, failing_rows=0, detail="aging mart not built")
    return _assert_zero("DQ-015", "no negative aging", "error", con,
        "SELECT * FROM mart_consequence_case_aging WHERE metric_days_in_current_stage < 0", scope="aging")


def core_blocked(results) -> bool:
    return any(x["severity"] == "error" and x["scope"] == "core" and x["status"] == FAIL for x in results)


def store(con, results, run_id) -> None:
    con.execute("CREATE OR REPLACE TABLE quality_results(run_id VARCHAR, rule_id VARCHAR, name VARCHAR, severity VARCHAR, scope VARCHAR, status VARCHAR, failing_rows BIGINT, detail VARCHAR)")
    for x in results:
        con.execute("INSERT INTO quality_results VALUES (?,?,?,?,?,?,?,?)",
                    [run_id, x["rule_id"], x["name"], x["severity"], x["scope"], x["status"], x["failing_rows"], x["detail"]])
