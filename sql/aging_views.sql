CREATE OR REPLACE VIEW mart_consequence_case_aging AS
SELECT
    c.case_id,
    c.case_domain,
    c.response_type,
    c.stage,
    c.stage_entered_date,
    c.owner,
    DATE_DIFF('day', c.stage_entered_date, (SELECT reference_date FROM runtime_inputs)) AS metric_days_in_current_stage
FROM int_consequence_case_current AS c
JOIN approved_open_stage_values AS r ON c.stage = r.stage
WHERE c.stage_entered_date IS NOT NULL;

CREATE OR REPLACE VIEW mart_top3_longest_open_cases AS
SELECT *
FROM mart_consequence_case_aging
ORDER BY metric_days_in_current_stage DESC, case_id ASC
LIMIT 3;
