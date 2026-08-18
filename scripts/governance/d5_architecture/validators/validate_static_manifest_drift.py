# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/validate_static_manifest_drift.py | §
# [MODULE] scripts.governance.d5_architecture.validators.validate_static_manifest_drift
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
validate_static_manifest_drift.py — GATE-21 静态清单漂移阻断

顺序运行所有静态清单生成器的 --check 模式。自动生成版与磁盘版任何不一致
均触发硬失败（exit 1）。

权威依据：AGENTS.md §6.3 静态清单自动生成铁律——任何"条目列表 + 计数"清单
必须由生成器产出（Type A：从代码/配置派生）或以 schema 为输入（Type B），
禁止手工维护条目（手工维护必然与真源漂移）。

检查清单：
  1. script_manifest.yaml — via generate_script_manifest.py --check
  2. gate_registry.yaml   — via generate_gate_registry.py --check

治本（2026-07-17）：
  - 清理代码退化结构（双 docstring / 重复 import / 游离 shebang / __manifest__ 块）
  - CHECKS 补齐 gate_registry.yaml（原仅 script_manifest.yaml，漏检门禁登记表漂移）
  - 输出消息 GATE-19 → GATE-21（2026-06-30 簇3合并重命名后消息未同步）
  - §6.16 断头引用 → §6.2 → §6.3（AGENTS.md 原无 §6.16，2026-07-17 治本补建 §6.2，2026-07-20 因新增临时文件分类存放铁律顺延为 §6.3）
  - 自举 sys.path 含 src/ + 子进程注入 PYTHONPATH=src，消除对调用方环境的依赖
    （原 validator 在未设 PYTHONPATH=src 的环境下崩溃 ModuleNotFoundError: No module named 'zephyr'）

Usage:
    python validate_static_manifest_drift.py --check
"""

from __future__ import annotations

__manifest__ = """
args:
- {flag: --check, type: bool, description: "检测漂移，不一致时 exit 1"}
description: GATE-21 静态清单漂移阻断——顺序运行所有静态清单生成器的 --check 模式，自动生成版与磁盘版不一致即硬失败
dimensions:
- D1
- D5
priority: P1
timeout_seconds: 120
warn_only: false
"""

import os
import subprocess
import sys
from pathlib import Path

# 自举 sys.path（顺序敏感）：
#   1. scripts/governance/ —— import _shared.*
#   2. <repo_root>/src      —— _shared.constants 内部 import zephyr.*（治本：原缺此行）
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists())
_REPO_ROOT = _GOV_DIR.parent.parent  # scripts/governance -> scripts -> <repo_root>
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))
_SRC_DIR = _REPO_ROOT / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from _shared.constants import EXIT_FINDINGS, EXIT_PASS  # noqa: E402
from _shared.encoding import ensure_utf8_stdout  # noqa: E402

ensure_utf8_stdout()

# 子进程环境：生成器 import _shared.constants → import zephyr，需 src/ 在 PYTHONPATH。
# 治本：原 subprocess.run 未传 env，子进程在未设 PYTHONPATH=src 的环境下崩溃。
_pp_parts = [str(_SRC_DIR)]
if os.environ.get("PYTHONPATH"):
    _pp_parts.append(os.environ["PYTHONPATH"])
_SUBPROCESS_ENV = {**os.environ, "PYTHONPATH": os.pathsep.join(_pp_parts)}

GENERATORS_DIR = _GOV_DIR / "generators"
SYNCERS_DIR = _GOV_DIR / "d5_architecture" / "syncers"

CHECKS = [
    {
        "name": "script_manifest.yaml",
        "cmd": [sys.executable, str(GENERATORS_DIR / "generate_script_manifest.py"), "--check"],
    },
    {
        "name": "gate_registry.yaml",
        "cmd": [sys.executable, str(GENERATORS_DIR / "generate_gate_registry.py"), "--check"],
    },
    # 注（2026-08-19 退库终态跟进）：原 blueprint_registry.yaml 检查已摘除——
    # 该文件经 #ARCH-BP-REGISTRY-DELETION-001 后续裁定正式派生退库（commit 03df6215e8：
    # 100% 可由 frontmatter 重生成=派生物，盘文件删除+.gitignore 入列+
    # check_no_commit_derived 扩列防重新跟踪）。文件缺失从"事故"翻转为"决策终态"，
    # dry-run 缺文件即 exit 2 的防删检测已过时（防重新跟踪由 check_no_commit_derived 承接）；
    # triple_alignment 消费侧已改 frontmatter 现算回退（同批治本）。
    {
        "name": ".importlinter forbidden_modules",
        "cmd": [sys.executable, str(GENERATORS_DIR / "generate_importlinter.py"), "--check"],
    },
]


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    # --check 是唯一模式（pre-commit / 手动调用均传 --check）；忽略其他参数。
    failures = []
    for check in CHECKS:
        result = subprocess.run(
            check["cmd"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=_SUBPROCESS_ENV,
            cwd=str(_REPO_ROOT),
        )
        if result.returncode != 0:
            msg = (result.stdout + result.stderr).strip()
            failures.append(f"FAIL [{check['name']}]: {msg}")
        else:
            print(f"PASS [{check['name']}]: {result.stdout.strip()}")

    if not failures:
        print("\nGATE-21 PASS: all static manifests are consistent with their sources.")
        sys.exit(EXIT_PASS)

    print(f"\nGATE-21 FAIL: {len(failures)} static manifest(s) have drifted:\n")
    for f in failures:
        print(f"  - {f}")
    print("\nFix: 运行对应生成器（不带 --check）重新生成，例如：")
    print("  python scripts/governance/generators/generate_script_manifest.py")
    print("  python scripts/governance/generators/generate_gate_registry.py")
    print("  python scripts/governance/d5_architecture/syncers/sync_registry_from_blueprints.py --write")
    sys.exit(EXIT_FINDINGS)


if __name__ == "__main__":
    main()
