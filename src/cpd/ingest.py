"""pl_ingest_consequence_csv: validate source shape/content, stage into stg_consequence_case."""
import csv
from dataclasses import dataclass

import duckdb

from . import contract as C


@dataclass
class Issue:
    rule: str
    message: str
    count: int = 1
    severity: str = "error"


def _read_header(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return next(csv.reader(fh), None)


def _count(con, sql):
    return con.execute(sql).fetchone()[0]


def validate_and_stage(con: duckdb.DuckDBPyConnection, csv_path) -> list[Issue]:
    """Return blocking issues. stg_consequence_case exists only when the list is empty."""
    issues: list[Issue] = []
    try:
        header = _read_header(csv_path)
    except (OSError, UnicodeDecodeError) as exc:
        return [Issue("DQ-007", f"unreadable file: {type(exc).__name__}")]
    if not header:
        return [Issue("DQ-007", "empty file / missing header")]
    header = [h.strip() for h in header]
    missing = [c for c in C.REQUIRED_COLUMNS if c not in header]
    extra = [c for c in header if c not in C.REQUIRED_COLUMNS]
    if missing:
        issues.append(Issue("DQ-007", f"missing required columns: {', '.join(missing)}", len(missing)))
    if extra:
        issues.append(Issue("DQ-007", f"unexpected extra columns need contract review: {', '.join(extra)}", len(extra)))
    if len(set(header)) != len(header):
        issues.append(Issue("DQ-007", "duplicate column names in header"))
    if issues:
        return issues

    try:
        con.execute("CREATE OR REPLACE TABLE raw_csv AS SELECT * FROM read_csv(?, header=true, all_varchar=true)", [str(csv_path)])
    except duckdb.Error as exc:
        return [Issue("DQ-007", f"CSV cannot be parsed: {type(exc).__name__}")]

    blank = " OR ".join(f"{c} IS NULL OR TRIM({c}) = ''" for c in C.REQUIRED_COLUMNS)
    n = _count(con, f"SELECT COUNT(*) FROM raw_csv WHERE {blank}")
    if n:
        issues.append(Issue("DQ-006", "rows with null/blank required values", n))
    n = _count(con, "SELECT COUNT(*) FROM (SELECT case_id FROM raw_csv WHERE case_id IS NOT NULL GROUP BY case_id HAVING COUNT(*) > 1)")
    if n:
        issues.append(Issue("DQ-003", "duplicate case_id groups (not deduplicated automatically)", n))
    for col, vals in (("case_domain", C.CASE_DOMAINS), ("response_type", C.RESPONSE_TYPES), ("stage", C.STAGES)):
        n = _count(con, f"SELECT COUNT(*) FROM raw_csv WHERE {col} IS NOT NULL AND TRIM({col}) <> '' AND {col} NOT IN ({C.sql_list(vals)})")
        if n:
            issues.append(Issue("DQ-005", f"{col} values outside contract", n))
    n = _count(con, "SELECT COUNT(*) FROM raw_csv WHERE stage_entered_date IS NOT NULL AND TRIM(stage_entered_date) <> '' AND TRY_CAST(stage_entered_date AS DATE) IS NULL")
    if n:
        issues.append(Issue("DQ-DATE", "stage_entered_date cannot be parsed as DATE", n))
    if issues:
        return issues

    con.execute(
        """CREATE OR REPLACE TABLE stg_consequence_case AS
           SELECT case_id::VARCHAR AS case_id, case_domain::VARCHAR AS case_domain,
                  response_type::VARCHAR AS response_type, stage::VARCHAR AS stage,
                  CAST(stage_entered_date AS DATE) AS stage_entered_date, owner::VARCHAR AS owner
           FROM raw_csv ORDER BY case_id"""
    )
    con.execute("DROP TABLE raw_csv")
    return []
