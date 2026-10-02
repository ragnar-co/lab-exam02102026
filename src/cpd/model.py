"""pl_build_consequence_model: dimensions + fact (grain 1 case x 1 snapshot), deterministic keys."""

_DIMS = [
    ("dim_case_domain", "case_domain", "case_domain_key", "CD"),
    ("dim_response_type", "response_type", "response_type_key", "RT"),
    ("dim_stage", "stage", "stage_key", "ST"),
    ("dim_owner", "owner", "owner_key", "OW"),
]


def build(con) -> None:
    for table, col, key, prefix in _DIMS:
        con.execute(
            f"""CREATE OR REPLACE TABLE {table} AS
                SELECT '{prefix}' || LPAD(ROW_NUMBER() OVER (ORDER BY {col})::VARCHAR, 3, '0') AS {key}, {col}
                FROM (SELECT DISTINCT {col} FROM stg_consequence_case)"""
        )
    con.execute(
        """CREATE OR REPLACE TABLE fact_consequence_case AS
           SELECT ROW_NUMBER() OVER (ORDER BY s.case_id)::BIGINT AS consequence_case_sk,
                  s.case_id, d1.case_domain_key, d2.response_type_key, d3.stage_key,
                  s.stage_entered_date, d4.owner_key
           FROM stg_consequence_case s
           LEFT JOIN dim_case_domain d1 USING (case_domain)
           LEFT JOIN dim_response_type d2 USING (response_type)
           LEFT JOIN dim_stage d3 USING (stage)
           LEFT JOIN dim_owner d4 USING (owner)
           ORDER BY s.case_id"""
    )
