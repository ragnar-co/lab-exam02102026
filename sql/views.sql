CREATE OR REPLACE VIEW int_consequence_case_current AS
SELECT
    f.case_id,
    dcd.case_domain,
    drt.response_type,
    ds.stage,
    f.stage_entered_date,
    o.owner
FROM fact_consequence_case AS f
JOIN dim_case_domain AS dcd ON f.case_domain_key = dcd.case_domain_key
JOIN dim_response_type AS drt ON f.response_type_key = drt.response_type_key
JOIN dim_stage AS ds ON f.stage_key = ds.stage_key
JOIN dim_owner AS o ON f.owner_key = o.owner_key;

CREATE OR REPLACE VIEW mart_consequence_case_metrics AS
SELECT
    c.*,
    CASE
        WHEN ro.stage IS NOT NULL AND rc.stage IS NULL THEN 'open'
        WHEN rc.stage IS NOT NULL AND ro.stage IS NULL THEN 'closed'
        ELSE 'unmapped'
    END AS case_status
FROM int_consequence_case_current AS c
LEFT JOIN approved_open_stage_values AS ro ON c.stage = ro.stage
LEFT JOIN approved_closed_stage_values AS rc ON c.stage = rc.stage;
