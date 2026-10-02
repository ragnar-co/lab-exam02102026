"""CLI entry. `python app.py --load <csv> [--reference-date YYYY-MM-DD]` loads; plain `python app.py` serves the dashboard."""
import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.cpd import config, pipeline, publish  # noqa: E402

DEFAULT_CSV = ROOT / "data" / "looktal_consequence_mock_2-3MB.csv"


def load(csv_path, reference_date=None) -> int:
    try:
        inputs = config.load_runtime_inputs(reference_date=reference_date)
    except config.ConfigError as exc:
        print(f"CONFIG ERROR: {exc}")
        return 2
    report = pipeline.run_pipeline(csv_path, inputs, config.runs_dir())
    print(f"status={report['status']} run_id={report.get('run_id')} rows={report.get('row_count')}")
    if report["status"] == "published":
        print(f"aging={report['aging_status']} {report.get('aging_reason', '')}".strip())
        return 0
    for i in report["issues"]:
        print(f"  BLOCKED [{i['rule']}] {i['message']} (count={i['count']})")
    return 1


def serve() -> int:
    os.chdir(ROOT)  # so relative paths and .streamlit/config.toml (theme) resolve from the project root
    runs = config.runs_dir()
    if publish.read_pointer(runs) is None and DEFAULT_CSV.exists():
        load(DEFAULT_CSV)
    port = os.environ.get("PORT", "8501")
    cmd = [sys.executable, "-m", "streamlit", "run", str(ROOT / "src" / "cpd" / "dashboard.py"),
           "--server.port", port, "--server.address", "0.0.0.0", "--server.headless", "true",
           "--browser.gatherUsageStats", "false"]
    os.execv(sys.executable, cmd)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--load", metavar="CSV")
    ap.add_argument("--reference-date", metavar="YYYY-MM-DD")
    args = ap.parse_args()
    sys.exit(load(args.load, args.reference_date) if args.load else serve())
