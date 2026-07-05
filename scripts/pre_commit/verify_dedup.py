# [BLUEPRINT] MOD-INF-005 | scripts/pre_commit/verify_dedup.py | §
# [MODULE] scripts.pre_commit.verify_dedup
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""pre_commit 验证脚本 — 委托给 code-dedup-engine CLI verify 子命令.

在 pre_commit hook 中调用：
  python scripts/pre_commit/verify_dedup.py [--staged]

退出码：
  0 = GATE_PASSED（引擎正常）
  1 = GATE_WARN（引擎降级——需人工判断）
  2 = GATE_ERROR（引擎故障——需人工判断）

所有重复检测逻辑由 cli.py verify 统一执行，本文件仅作为 pre_commit 入口委托。
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# bootstrap: 定位 scripts/governance/ 以 import _shared.constants（REPO_ROOT SSoT 真源）
_GOV_DIR = str(Path(__file__).resolve().parent.parent / "governance")
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import REPO_ROOT  # noqa: E402

SRC_DIR = REPO_ROOT / "src"


def main() -> int:
    result = subprocess.run(
        [sys.executable, "-m", "zephyr.governance.code_dedup.cli", "verify"],
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
