"""P0 实验输入和结果的最小契约。"""

from dataclasses import dataclass
from enum import Enum


class RunStatus(str, Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    TIMED_OUT = "timed_out"


@dataclass(frozen=True)
class ExperimentSpec:
    sample: str
    timeout_seconds: float = 5.0

    def __post_init__(self) -> None:
        if self.sample not in {"success", "failure", "timeout"}:
            raise ValueError("P0 仅允许 success、failure、timeout 固定样例")
        if not 0 < self.timeout_seconds <= 60:
            raise ValueError("超时时间必须大于 0 且不超过 60 秒")
