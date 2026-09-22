"""固定种子的轻量样例；只验证 P0 记录链路，不代表科研成果。"""

import json
from pathlib import Path
import random
import sys


def main() -> None:
    run_dir = Path(sys.argv[1])
    rng = random.Random(42)
    observations = [rng.random() for _ in range(8)]
    mean = sum(observations) / len(observations)
    (run_dir / "metrics.json").write_text(
        json.dumps({"mean_value": mean, "sample_count": len(observations)}), encoding="utf-8"
    )
    bars = "".join(
        f'<rect x="{10 + i * 25}" y="{110 - int(value * 100)}" width="16" height="{int(value * 100)}" fill="#1f77b4"/>'
        for i, value in enumerate(observations)
    )
    (run_dir / "artifacts" / "observations.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="220" height="120">{bars}</svg>', encoding="utf-8"
    )
    print(f"固定样例完成：mean_value={mean:.6f}")


if __name__ == "__main__":
    main()
