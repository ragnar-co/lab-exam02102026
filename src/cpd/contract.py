"""Source contract v0.1-draft (DATA_CONTRACT.md)."""
REQUIRED_COLUMNS = ["case_id", "case_domain", "response_type", "stage", "stage_entered_date", "owner"]
CASE_DOMAINS = ("behavior", "performance")
RESPONSE_TYPES = ("recognition", "improvement")
STAGES = ("closed", "reviewing", "follow_up", "collecting_info")


def sql_list(values) -> str:
    return ", ".join("'" + v.replace("'", "''") + "'" for v in values)
