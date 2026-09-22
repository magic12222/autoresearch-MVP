"""P0 命令行入口。"""

import argparse
import json
from pathlib import Path

from research_platform.experiments.contracts import ExperimentSpec
from research_platform.experiments.runner import PROJECT_ROOT, run_experiment
from research_platform.journal.store import list_records


def main() -> int:
    parser = argparse.ArgumentParser(description="P0 受控实验执行器")
    sub = parser.add_subparsers(dest="action", required=True)
    run_parser = sub.add_parser("run", help="运行固定样例")
    run_parser.add_argument("sample", choices=("success", "failure", "timeout"))
    run_parser.add_argument("--timeout", type=float, default=5.0)
    sub.add_parser("list", help="列出实验历史")
    args = parser.parse_args()
    root = Path(PROJECT_ROOT / "workspace")
    if args.action == "list":
        for record in list_records(root):
            print(f"{record['experiment_id']}  {record['sample']}  {record['status']}")
        return 0
    try:
        record = run_experiment(ExperimentSpec(args.sample, args.timeout), root)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps({"experiment_id": record["experiment_id"], "status": record["status"], "run_dir": record["cwd"]}, ensure_ascii=False))
    return 0 if record["status"] == "succeeded" else 1
