# [BLUEPRINT] MOD-INF-005 | scripts/governance/d1_structure/detect_orphan_py.py | §
# [MODULE] scripts.governance.d1_structure.detect_orphan_py
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d1_structure.__init__
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
detect_orphan_py.py — 全库孤儿 .py 文件检测


对标：AGENTS.md §6.5（脚本自创入库强制约定）：
    .py 文件只允许放在 scripts/**、src/zephyr/**、tests/** 三个根域的任意子目录中。
    本脚本递归扫描全库，检测未放入合法位置的 .py 孤儿文件——
    这是 AI session 最常见的"留下的垃圾"。

检测逻辑（Gap-3 修复 2026-07-28：非递归→递归全库）：
    - 递归扫描 REPO_ROOT 下所有 .py 文件（排除 .git/__pycache__/node_modules 等）
    - 合法目录前缀: scripts/、src/zephyr/、tests/——不在这些前缀下的 .py 即为孤儿
    - 根目录级 Python 约定文件（__init__.py/conftest.py/setup.py/sitecustomize.py）豁免
    - --fix 模式：自动删除检测到的孤儿文件

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args:
- --fix
description: 全库孤儿.py文件检测（AGENTS.md §6.5 — .py只允许在scripts/** / src/zephyr/**
  / tests/** 任意子目录）
dimensions:
- D1
priority: P0
timeout_seconds: 30
warn_only: false
"""


import os
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
import argparse

from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT

LEGAL_DIRS: tuple[str, ...] = ("scripts/", "src/zephyr/", "tests/", "schemas/")
# repo root 合法 .py 白名单（Python/打包约定的根级文件，必须在 repo root 才能生效）：
#   __init__.py / conftest.py / setup.py — 历史豁免
#   sitecustomize.py — Python 解释器启动自动加载（GATE-20 运行时 Gate 引导入口，
#       必须 repo root；详见 AGENTS.md §4.2.1 + runtime_interceptor.py）
EXCLUDE_NAMES: frozenset[str] = frozenset({"__init__.py", "conftest.py", "setup.py", "sitecustomize.py"})


def find_orphan_py_files() -> list[Path]:
    """递归扫描全库，查找不在合法目录内的 .py 孤儿文件。

    合法目录前缀: scripts/、src/zephyr/、tests/（任意子目录）。
    根目录级 Python 约定文件（__init__.py/conftest.py/setup.py/sitecustomize.py）豁免。
    """
    findings: list[Path] = []
    skip_dirs = {".git", "__pycache__", "node_modules", ".trae", ".runtime", "models", "tmp", ".pytest_tmp"}
    try:
        for root, dirs, files in os.walk(REPO_ROOT):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for f in files:
                if not f.endswith(".py"):
                    continue
                abspath = Path(root) / f
                rel = str(abspath.relative_to(REPO_ROOT)).replace("\\", "/")
                # 根目录级 Python 约定文件豁免（必须在 repo root 才能生效）
                if "/" not in rel and f in EXCLUDE_NAMES:
                    continue
                # 合法目录前缀内的 .py 文件放行
                if any(rel.startswith(ld) for ld in LEGAL_DIRS):
                    continue
                findings.append(abspath)
    except OSError as exc:
        print(f"ERROR: Cannot scan {REPO_ROOT}: {exc}", file=sys.stderr)
        raise
    return findings


def fix_orphans(files: list[Path]) -> int:
    """fix orphans."""
    removed = 0
    "fix_orphans."
    for f in files:
        try:
            f.unlink()
            print(f"  DELETED: {f.relative_to(REPO_ROOT)}")
            removed += 1
        except OSError as exc:
            print(f"  ERROR deleting {f.relative_to(REPO_ROOT)}: {exc}", file=sys.stderr)
    return removed
    "fix orphans."


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="检测并修复项目根目录下的孤儿 .py 文件（对标 AGENTS.md §6.5）")
    parser.add_argument(
        "--warn-only", action="store_true", default=False, help="仅警告不阻断（exit 0，即使发现孤儿文件）"
    )
    parser.add_argument("--fix", action="store_true", default=False, help="自动删除检测到的孤儿 .py 文件")
    args = parser.parse_args()
    try:
        orphans = find_orphan_py_files()
    except OSError:
        sys.exit(EXIT_ERROR)
    if not orphans:
        print("OK: 全库零孤儿 .py 文件（所有 .py 均在合法目录 scripts/、src/zephyr/、tests/ 内）")
        sys.exit(EXIT_PASS)
    print(f"FOUND {len(orphans)} orphan .py file(s) outside legal directories:")
    for f in orphans:
        print(f"  {f.relative_to(REPO_ROOT)}")
    if args.fix:
        removed = fix_orphans(orphans)
        print(f"FIXED: {removed} file(s) deleted")
        sys.exit(0 if removed == len(orphans) else 1)
    print()
    print("AGENTS.md §6.5 规定: .py 文件只允许放在以下根域的任意子目录中:")
    for d in LEGAL_DIRS:
        print(f"  - {REPO_ROOT / d}")
    print("请删除上述孤儿文件，或移动至合法目录。")
    print("提示: 使用 --fix 自动删除。")
    if args.warn_only:
        print("WARN-ONLY: 不阻断，exit 0")
        sys.exit(EXIT_PASS)
    sys.exit(EXIT_FINDINGS)


if __name__ == "__main__":
    main()
