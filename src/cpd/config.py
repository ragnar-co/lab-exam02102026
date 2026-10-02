"""Runtime inputs. reference_date is a required approved input: never defaulted, never system date."""
import json
import os
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SQL_DIR = ROOT / "sql"
DEFAULT_CONFIG = ROOT / "config" / "runtime_config.json"
SUPPORTED_DAY_COUNT = "calendar_day_difference"
SUPPORTED_TIE_BREAK = "case_id ASC"


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class RuntimeInputs:
    reference_date: date | None
    open_stages: tuple[str, ...]
    closed_stages: tuple[str, ...]
    day_count_mode: str
    top3_tie_break: str


def parse_reference_date(value) -> date | None:
    if value is None or str(value).strip() == "":
        return None
    text = str(value).strip()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        raise ConfigError(f"reference_date must be YYYY-MM-DD, got {text!r}")
    try:
        return date.fromisoformat(text)
    except ValueError as exc:
        raise ConfigError(f"reference_date invalid: {text!r}") from exc


def load_runtime_inputs(config_path=None, env=None, reference_date=None) -> RuntimeInputs:
    env = os.environ if env is None else env
    path = Path(config_path or env.get("CPD_CONFIG") or DEFAULT_CONFIG)
    cfg = json.loads(path.read_text(encoding="utf-8"))
    ref = reference_date if reference_date not in (None, "") else env.get("CPD_REFERENCE_DATE") or cfg.get("reference_date")
    open_s, closed_s = tuple(cfg.get("open_stages") or ()), tuple(cfg.get("closed_stages") or ())
    if set(open_s) & set(closed_s):
        raise ConfigError("a stage cannot be both open and closed")
    if cfg.get("day_count_mode") != SUPPORTED_DAY_COUNT:
        raise ConfigError(f"unsupported day_count_mode {cfg.get('day_count_mode')!r}")
    if cfg.get("top3_tie_break") != SUPPORTED_TIE_BREAK:
        raise ConfigError(f"unsupported top3_tie_break {cfg.get('top3_tie_break')!r}")
    return RuntimeInputs(parse_reference_date(ref), open_s, closed_s, cfg["day_count_mode"], cfg["top3_tie_break"])


def runs_dir(env=None) -> Path:
    env = os.environ if env is None else env
    return Path(env.get("CPD_RUNS_DIR") or ROOT / "runs")


def mask_identifiers(env=None) -> bool:
    env = os.environ if env is None else env
    return str(env.get("CPD_MASK_IDENTIFIERS", "false")).lower() in ("1", "true", "yes")
