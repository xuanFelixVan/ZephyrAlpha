# [BLUEPRINT] MOD-INF-005 | scripts/pre-commit/verify_dedup.py | §
"""pre-commit 验证脚本 — 委托给 code-dedup-engine CLI verify 子命令.

在 pre-commit hook 中调用：
  python scripts/pre-commit/verify_dedup.py [--staged]

退出码：
  0 = GATE_PASSED（引擎正常）
  1 = GATE_WARN（引擎降级——需人工判断）
  2 = GATE_ERROR（引擎故障——需人工判断）

所有重复检测逻辑由 cli.py verify 统一执行，本文件仅作为 pre-commit 入口委托。
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[2] / "src"


def main() -> int:
    result = subprocess.run(
        [sys.executable, "-m", "zephyr.l01_infrastructure.code_dedup_engine.cli", "verify"],
        cwd=str(SRC_DIR.parent),
        capture_output=True,
        text=True,
    )
    sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
