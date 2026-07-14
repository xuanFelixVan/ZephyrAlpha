# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/validate_init_all.py | §
# [MODULE] scripts.governance.d7_code.validate_init_all
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d7_code.__init__
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
"""
validate_init_all.py — __init__.py __all__ 完整性校验



对标：PEP 8 — __all__ should be defined for public API packages
     AGENTS.md §6.4 — 显式优于隐式（AI 需要显式知道包的公开接口）

检测 src/zephyr/ 下所有 __init__.py 文件：
- 如果 __init__.py 中有 import 语句，则必须有 __all__ 定义
- 如果 __init__.py 为空（仅注释/空白），属于骨架包——跳过

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: __init__.py __all__ 完整性校验——有 import 的包必须定义 __all__
dimensions:
- D7
priority: P2
timeout_seconds: 30
warn_only: false
"""


import argparse
import ast
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

from _shared.constants import EXIT_PASS, REPO_ROOT, SRC_DIR

SKELETON_PACKAGES = {  # noqa: gate-vocab  骨架包列表业务子集
    "signal",
    "risk",
    "pf_core",
    "ex_core",
    "frontend",
    "research",
    "compliance",
    "ml_train",
    "integration",
    "hooks",
    "script_system",
    "shared/contracts",
}

EXEMPT_PACKAGES = {"shared", "data"}


def _has_imports(tree: ast.AST) -> bool:
    """_has_imports implementation."""
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            return True
    return False


def _has_all_definition(tree: ast.AST) -> bool:
    """_has_all_definition implementation."""
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    return True
    return False


def scan_init_all(init_path: Path) -> tuple[bool, bool]:
    """扫描 __init__.py 导出完整性."""
    with open(init_path, encoding="utf-8") as f:
        """扫描 __init__.py 导出完整性."""
        """扫描并返回发现列表."""
        source = f.read()
    tree = ast.parse(source, filename=str(init_path))
    has_imports = _has_imports(tree)
    has_all = _has_all_definition(tree)
    return has_imports, has_all
    """扫描 __init__.py 导出完整性."""


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="__init__.py __all__ 完整性校验")
    parser.add_argument("--warn-only", action="store_true", help="警告模式")
    args = parser.parse_args()

    findings = []
    total_inits = 0
    ok_count = 0

    for init_file in SRC_DIR.rglob("__init__.py"):
        total_inits += 1

        package_rel = str(init_file.parent.relative_to(SRC_DIR)).replace("\\", "/")
        if package_rel in SKELETON_PACKAGES:
            ok_count += 1
            continue

        has_imports, has_all = scan_init_all(init_file)

        if has_imports and not has_all:
            try:
                rel = init_file.relative_to(REPO_ROOT)
            except ValueError:
                rel = init_file
            findings.append(f"[P2] {rel}  有 import 但没有 __all__ 定义")
        else:
            ok_count += 1

    if findings:
        print(
            f"\n[INIT-ALL] {len(findings)} 个 __init__.py 缺少 __all__（扫描 {total_inits} 个包）:\n", file=sys.stderr
        )
        for f_item in findings:
            print(f_item, file=sys.stderr)
        print(file=sys.stderr)
    else:
        print(f"\n[INIT-ALL] 全部 {ok_count}/{total_inits} 个 __init__.py 符合规范 ✅\n", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
