"""保存检索证据；不从少量搜索结果推断新颖性。"""

import hashlib
import json
from pathlib import Path
from typing import Any, Callable
from datetime import datetime, timezone
from uuid import uuid4

from research_platform.literature.sources import (
    SearchError,
    normalize_papers,
    search_openalex,
    search_semantic_scholar,
)


SearchFunction = Callable[[str, int], tuple[str, dict[str, Any]]]
SOURCES: dict[str, SearchFunction] = {
    "semantic_scholar": search_semantic_scholar,
    "openalex": search_openalex,
}


def check_novelty(
    proposal: dict[str, Any],
    root: Path,
    sources: dict[str, SearchFunction] | None = None,
) -> dict[str, Any]:
    """逐源逐查询检索，任何失败都留痕且总体结论保持未判定。"""
    active_sources = sources if sources is not None else SOURCES
    if not active_sources:
        raise ValueError("至少需要一个检索源")
    check_id = uuid4().hex
    directory = root / "novelty_checks" / check_id
    directory.mkdir(parents=True, exist_ok=False)
    proposal_bytes = json.dumps(proposal, ensure_ascii=False, sort_keys=True).encode("utf-8")
    (directory / "proposal.json").write_bytes(proposal_bytes)
    observations = []
    all_papers = []
    rate_limited: set[str] = set()
    for query in proposal["search_queries"]:
        for source_name, search in active_sources.items():
            observation: dict[str, Any] = {
                "source": source_name,
                "query": query,
                "searched_at": datetime.now(timezone.utc).isoformat(),
            }
            if source_name in rate_limited:
                observation.update({"status": "skipped", "error": "该来源此前返回 HTTP 429，本次不重复请求"})
                observations.append(observation)
                continue
            try:
                url, raw = search(query, 5)
                papers = normalize_papers(source_name, raw)
                raw_name = f"response_{len(observations):02d}.json"
                (directory / raw_name).write_text(
                    json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                )
                observation.update({"status": "ok", "request_url": url, "raw_path": raw_name, "paper_count": len(papers)})
                all_papers.extend(papers)
            except SearchError as exc:
                observation.update({"status": "error", "error": str(exc), "http_status": exc.status_code})
                if exc.status_code == 429:
                    rate_limited.add(source_name)
            observations.append(observation)
    result = {
        "check_id": check_id,
        "proposal_sha256": hashlib.sha256(proposal_bytes).hexdigest(),
        "status": "needs_review" if all(item["status"] == "ok" for item in observations) else "insufficient_evidence",
        "novelty_verdict": None,
        "observations": observations,
        "candidate_papers": all_papers,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    temporary = directory / "report.json.tmp"
    temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(directory / "report.json")
    return result
