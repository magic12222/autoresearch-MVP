"""以独立 manifest 和追加式索引保存实验历史。"""

import json
import os
from pathlib import Path
from typing import Any


def save_record(root: Path, record: dict[str, Any]) -> None:
    run_dir = root / "experiments" / record["experiment_id"]
    manifest = run_dir / "manifest.json"
    temporary = run_dir / "manifest.json.tmp"
    temporary.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(manifest)

    journal = root / "journal.jsonl"
    with journal.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def list_records(root: Path) -> list[dict[str, Any]]:
    journal = root / "journal.jsonl"
    if not journal.exists():
        return []
    return [json.loads(line) for line in journal.read_text(encoding="utf-8").splitlines() if line.strip()]
