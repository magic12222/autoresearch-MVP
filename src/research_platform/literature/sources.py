"""公开论文检索源；凭据只读取环境变量，不写入结果。"""

import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class SearchError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def _get_json(url: str, headers: dict[str, str]) -> dict[str, Any]:
    request = Request(url, headers=headers)
    try:
        with urlopen(request, timeout=12) as response:
            payload = response.read(2_000_001)
    except HTTPError as exc:
        raise SearchError(f"HTTP {exc.code}", exc.code) from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise SearchError(f"网络请求失败：{type(exc).__name__}") from exc
    if len(payload) > 2_000_000:
        raise SearchError("响应超过 2 MB 限制")
    try:
        data = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SearchError("响应不是有效 JSON") from exc
    if not isinstance(data, dict):
        raise SearchError("响应不是 JSON 对象")
    return data


def search_semantic_scholar(query: str, limit: int = 5) -> tuple[str, dict[str, Any]]:
    params = urlencode({"query": query, "limit": limit, "fields": "title,year,url,abstract,externalIds"})
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?{params}"
    headers = {"User-Agent": "AIResearchPlatform/0.1"}
    api_key = os.getenv("S2_API_KEY")
    if api_key:
        headers["x-api-key"] = api_key
    return url, _get_json(url, headers)


def search_openalex(query: str, limit: int = 5) -> tuple[str, dict[str, Any]]:
    params = urlencode({"search": query, "per-page": limit})
    url = f"https://api.openalex.org/works?{params}"
    return url, _get_json(url, {"User-Agent": "AIResearchPlatform/0.1"})


def normalize_papers(source: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
    items = payload.get("data") if source == "semantic_scholar" else payload.get("results")
    if not isinstance(items, list):
        raise SearchError("论文列表字段缺失或类型错误")
    papers = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if source == "semantic_scholar":
            external_ids = item.get("externalIds") or {}
            paper = {
                "source": source,
                "source_id": item.get("paperId"),
                "title": item.get("title"),
                "year": item.get("year"),
                "doi": external_ids.get("DOI") if isinstance(external_ids, dict) else None,
                "url": item.get("url"),
                "abstract": item.get("abstract"),
            }
        else:
            location = item.get("primary_location") or {}
            paper = {
                "source": source,
                "source_id": item.get("id"),
                "title": item.get("display_name"),
                "year": item.get("publication_year"),
                "doi": item.get("doi"),
                "url": location.get("landing_page_url") if isinstance(location, dict) else None,
                "abstract": None,
            }
        if paper["title"]:
            papers.append(paper)
    return papers
