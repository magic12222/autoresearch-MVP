"""提案契约和检索证据的离线验证。"""

import json
from pathlib import Path
import sys
import tempfile
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from research_platform.ideas.proposal import load_proposal
from research_platform.literature.novelty import check_novelty
from research_platform.literature.sources import SearchError


class NoveltyTests(unittest.TestCase):
    def setUp(self) -> None:
        (PROJECT_ROOT / "workspace").mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=PROJECT_ROOT / "workspace")
        self.root = Path(self.temp.name)
        self.proposal = load_proposal(PROJECT_ROOT / "examples" / "proposal_2d_diffusion.json")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_proposal_rejects_missing_hypothesis(self) -> None:
        path = self.root / "bad.json"
        path.write_text(json.dumps({**self.proposal, "hypothesis": ""}), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "hypothesis"):
            load_proposal(path)

    def test_success_saves_raw_evidence_without_novelty_claim(self) -> None:
        def fake_search(query: str, limit: int):
            self.assertEqual(limit, 5)
            return "https://example.org/search", {"data": [{
                "paperId": "paper-1", "title": "Relevant prior work", "year": 2024,
                "url": "https://example.org/paper-1", "abstract": "Comparison",
                "externalIds": {"DOI": "10.1/example"},
            }]}

        report = check_novelty(self.proposal, self.root, {"semantic_scholar": fake_search})
        directory = self.root / "novelty_checks" / report["check_id"]
        self.assertEqual(report["status"], "needs_review")
        self.assertIsNone(report["novelty_verdict"])
        self.assertEqual(len(report["candidate_papers"]), 2)
        self.assertTrue((directory / "response_00.json").exists())
        self.assertEqual(json.loads((directory / "report.json").read_text(encoding="utf-8")), report)

    def test_rate_limit_remains_insufficient_evidence(self) -> None:
        def limited_search(query: str, limit: int):
            raise SearchError("HTTP 429", 429)

        report = check_novelty(self.proposal, self.root, {"semantic_scholar": limited_search})
        self.assertEqual(report["status"], "insufficient_evidence")
        self.assertIsNone(report["novelty_verdict"])
        self.assertEqual(report["observations"][0]["http_status"], 429)
        self.assertEqual(report["observations"][1]["status"], "skipped")
        self.assertEqual(report["candidate_papers"], [])


if __name__ == "__main__":
    unittest.main()
