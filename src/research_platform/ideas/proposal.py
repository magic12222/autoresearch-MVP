"""结构化研究提案的读取与校验。"""

import json
from pathlib import Path
from typing import Any


REQUIRED_TEXT = ("title", "motivation", "hypothesis", "method", "expected_result")


def load_proposal(path: Path) -> dict[str, Any]:
    proposal = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(proposal, dict):
        raise ValueError("提案必须是 JSON 对象")
    for field in REQUIRED_TEXT:
        if not isinstance(proposal.get(field), str) or not proposal[field].strip():
            raise ValueError(f"提案字段 {field} 必须是非空字符串")
    for field in ("experiment_plan", "search_queries"):
        items = proposal.get(field)
        if not isinstance(items, list) or not 1 <= len(items) <= 5:
            raise ValueError(f"提案字段 {field} 必须是 1 到 5 项的列表")
        if any(not isinstance(item, str) or not item.strip() for item in items):
            raise ValueError(f"提案字段 {field} 的每一项都必须是非空字符串")
    return proposal
