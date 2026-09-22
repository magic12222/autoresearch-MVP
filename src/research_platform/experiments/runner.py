"""仅执行仓库内预审样例的 P0 实验执行器。"""

import hashlib
import json
import math
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from uuid import uuid4

from research_platform.experiments.contracts import ExperimentSpec, RunStatus
from research_platform.journal.store import save_record


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SAMPLES = {
    "success": PROJECT_ROOT / "examples" / "tiny_success.py",
    "failure": PROJECT_ROOT / "examples" / "tiny_failure.py",
    "timeout": PROJECT_ROOT / "examples" / "tiny_timeout.py",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _output_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value


def _read_metrics(path: Path) -> dict[str, float]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not data:
        raise ValueError("metrics.json 必须是非空对象")
    metrics: dict[str, float] = {}
    for name, value in data.items():
        if not isinstance(name, str) or not name or isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("指标必须是名称和数值的映射")
        if not math.isfinite(value):
            raise ValueError("指标不能是 NaN 或无穷大")
        metrics[name] = float(value)
    return metrics


def run_experiment(spec: ExperimentSpec, root: Path | None = None) -> dict:
    root = (root or PROJECT_ROOT / "workspace").resolve()
    root.mkdir(parents=True, exist_ok=True)
    experiment_id = uuid4().hex
    run_dir = root / "experiments" / experiment_id
    snapshot_dir = run_dir / "snapshot"
    artifact_dir = run_dir / "artifacts"
    snapshot_dir.mkdir(parents=True)
    artifact_dir.mkdir()

    source = SAMPLES[spec.sample]
    snapshot = snapshot_dir / source.name
    shutil.copy2(source, snapshot)
    command = [sys.executable, str(snapshot), str(run_dir)]
    started_at = _utc_now()
    status = RunStatus.FAILED
    error: str | None = None
    exit_code: int | None = None
    stdout = ""
    stderr = ""
    metrics: dict[str, float] = {}

    # 仅传递 Python 运行所需的基础环境变量，避免把 LLM 或 SSH 凭据带入样例进程。
    allowed = {"PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "HOME", "LANG", "LC_ALL"}
    child_env = {key: value for key, value in os.environ.items() if key.upper() in allowed}
    child_env["PYTHONIOENCODING"] = "utf-8"
    child_env["PYTHONUNBUFFERED"] = "1"

    try:
        completed = subprocess.run(
            command,
            cwd=run_dir,
            env=child_env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=spec.timeout_seconds,
            check=False,
        )
        exit_code = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
        if exit_code == 0:
            metrics = _read_metrics(run_dir / "metrics.json")
            status = RunStatus.SUCCEEDED
        else:
            error = f"进程退出码为 {exit_code}"
    except subprocess.TimeoutExpired as exc:
        status = RunStatus.TIMED_OUT
        error = f"运行超过 {spec.timeout_seconds} 秒"
        stdout = _output_text(exc.stdout)
        stderr = _output_text(exc.stderr)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        error = f"结果校验失败：{exc}"

    (run_dir / "stdout.log").write_text(stdout, encoding="utf-8")
    (run_dir / "stderr.log").write_text(stderr, encoding="utf-8")
    artifacts = [
        {"path": path.relative_to(run_dir).as_posix(), "size": path.stat().st_size, "sha256": _sha256(path)}
        for path in sorted(artifact_dir.rglob("*"))
        if path.is_file()
    ]
    record = {
        "experiment_id": experiment_id,
        "parent_id": None,
        "sample": spec.sample,
        "hypothesis": "固定 CPU 样例验证实验执行与记录契约",
        "plan": "运行已审核的 Python 样例并收集结果",
        "code_change": None,
        "code_snapshot": snapshot.relative_to(run_dir).as_posix(),
        "code_sha256": _sha256(snapshot),
        "command": command,
        "cwd": str(run_dir),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "timeout_seconds": spec.timeout_seconds,
        "metrics": metrics,
        "result": "样例执行并通过指标校验" if status == RunStatus.SUCCEEDED else None,
        "error": error,
        "analysis": None,
        "status": status.value,
        "exit_code": exit_code,
        "stdout_path": "stdout.log",
        "stderr_path": "stderr.log",
        "metrics_path": "metrics.json" if (run_dir / "metrics.json").exists() else None,
        "artifacts": artifacts,
        "started_at": started_at,
        "finished_at": _utc_now(),
    }
    save_record(root, record)
    return record
