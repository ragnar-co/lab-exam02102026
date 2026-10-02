-- Implementations from METRIC_LOGIC.md (named params: $case_domain, NULL = unfiltered)
-- name: metric_total_cases
SELECT COUNT(DISTINCT case_id) AS metric_total_cases
FROM int_consequence_case_current
WHERE ($case_domain::VARCHAR IS NULL OR case_domain = $case_domain);

-- name: metric_closed_cases
SELECT COUNT(DISTINCT c.case_id) AS metric_closed_cases
FROM int_consequence_case_current AS c
JOIN approved_closed_stage_values AS r ON c.stage = r.stage
WHERE ($case_domain::VARCHAR IS NULL OR c.case_domain = $case_domain);

-- name: metric_open_cases
SELECT COUNT(DISTINCT c.case_id) AS metric_open_cases
FROM int_consequence_case_current AS c
JOIN approved_open_stage_values AS r ON c.stage = r.stage
WHERE ($case_domain::VARCHAR IS NULL OR c.case_domain = $case_domain);

-- name: metric_open_cases_by_stage
SELECT c.stage, COUNT(DISTINCT c.case_id) AS metric_open_cases_by_stage
FROM int_consequence_case_current AS c
JOIN approved_open_stage_values AS r ON c.stage = r.stage
WHERE ($case_domain::VARCHAR IS NULL OR c.case_domain = $case_domain)
GROUP BY c.stage
ORDER BY c.stage;

-- name: metric_days_in_current_stage
SELECT case_id, case_domain, response_type, stage, stage_entered_date, owner, metric_days_in_current_stage
FROM mart_consequence_case_aging
WHERE ($case_domain::VARCHAR IS NULL OR case_domain = $case_domain)
ORDER BY metric_days_in_current_stage DESC, case_id ASC;

-- name: metric_top_3_longest_open_cases
SELECT case_id, case_domain, response_type, stage, stage_entered_date, owner, metric_days_in_current_stage
FROM mart_consequence_case_aging
WHERE ($case_domain::VARCHAR IS NULL OR case_domain = $case_domain)
ORDER BY metric_days_in_current_stage DESC, case_id ASC
LIMIT 3;

-- name: consequence_process_completion_rate
SELECT CASE WHEN total_cases = 0 THEN NULL ELSE closed_cases::DOUBLE / total_cases END AS consequence_process_completion_rate
FROM (
    SELECT COUNT(DISTINCT c.case_id) AS total_cases,
           COUNT(DISTINCT CASE WHEN r.stage IS NOT NULL THEN c.case_id END) AS closed_cases
    FROM int_consequence_case_current AS c
    LEFT JOIN approved_closed_stage_values AS r ON c.stage = r.stage
    WHERE ($case_domain::VARCHAR IS NULL OR c.case_domain = $case_domain)
);

-- name: open_case_rate
SELECT CASE WHEN total_cases = 0 THEN NULL ELSE open_cases::DOUBLE / total_cases END AS open_case_rate
FROM (
    SELECT COUNT(DISTINCT c.case_id) AS total_cases,
           COUNT(DISTINCT CASE WHEN r.stage IS NOT NULL THEN c.case_id END) AS open_cases
    FROM int_consequence_case_current AS c
    LEFT JOIN approved_open_stage_values AS r ON c.stage = r.stage
    WHERE ($case_domain::VARCHAR IS NULL OR c.case_domain = $case_domain)
);

-- name: case_list
-- drill-down listing from the mart (no metric formula)
SELECT case_id, case_domain, response_type, stage, stage_entered_date, owner, case_status
FROM mart_consequence_case_metrics
WHERE ($case_domain::VARCHAR IS NULL OR case_domain = $case_domain)
  AND ($case_status::VARCHAR IS NULL OR case_status = $case_status)
  AND ($stage::VARCHAR IS NULL OR stage = $stage)
ORDER BY case_id;
