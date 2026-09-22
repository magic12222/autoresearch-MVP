"""验证 P0 成功、失败、超时及历史记录。"""

import json
from pathlib import Path
import sys
import tempfile
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from research_platform.experiments.contracts import ExperimentSpec
from research_platform.experiments.runner import run_experiment
from research_platform.journal.store import list_records


class RunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        (PROJECT_ROOT / "workspace").mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=PROJECT_ROOT / "workspace")
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_success_records_metrics_snapshot_and_artifact(self) -> None:
        record = run_experiment(ExperimentSpec("success"), self.root)
        run_dir = Path(record["cwd"])
        self.assertEqual(record["status"], "succeeded")
        self.assertEqual(record["exit_code"], 0)
        self.assertEqual(record["metrics"]["sample_count"], 8.0)
        self.assertEqual(len(record["artifacts"]), 1)
        self.assertTrue((run_dir / record["code_snapshot"]).exists())
        self.assertTrue((run_dir / record["artifacts"][0]["path"]).exists())
        self.assertEqual(json.loads((run_dir / "manifest.json").read_text(encoding="utf-8")), record)
        self.assertEqual(list_records(self.root), [record])

    def test_failure_keeps_stdout_stderr_and_history(self) -> None:
        record = run_experiment(ExperimentSpec("failure"), self.root)
        run_dir = Path(record["cwd"])
        self.assertEqual(record["status"], "failed")
        self.assertNotEqual(record["exit_code"], 0)
        self.assertIn("失败样例已启动", (run_dir / "stdout.log").read_text(encoding="utf-8"))
        self.assertIn("受控失败", (run_dir / "stderr.log").read_text(encoding="utf-8"))
        self.assertEqual(list_records(self.root), [record])

    def test_timeout_is_recorded(self) -> None:
        record = run_experiment(ExperimentSpec("timeout", 0.3), self.root)
        self.assertEqual(record["status"], "timed_out")
        self.assertIsNone(record["exit_code"])
        self.assertIn("运行超过", record["error"])
        self.assertEqual(list_records(self.root), [record])


if __name__ == "__main__":
    unittest.main()
