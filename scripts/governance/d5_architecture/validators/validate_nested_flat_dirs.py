# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/validate_nested_flat_dirs.py | §
# [MODULE] scripts.governance.d5_architecture.validators.validate_nested_flat_dirs
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.__init__
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
"""Module docstring — see module-level docstring for details."""

from __future__ import annotations

#!/usr/bin/env python3
"""
validate_nested_flat_dirs.py — 递归嵌套目录平铺检测器
=====================================================
依据：GOV-DOC-018 文件夹平铺容量阈值协议（T_hard=60/T_soft=120）

检查项
------
1. 递归扫描 src/zephyr/、tests/、scripts/governance/ 下所有目录
2. 每个目录的 .py 文件数超过 warn/error 阈值即报警
3. 阈值来自 thresholds.yaml directory_scalability 节（src_py_warn=60, src_py_error=120）
4. --check-prefix 模式（ARCH-043 Risk 2-B）：对 >T_hard(60) 的目录验证 __init__.py
   是否文档化了命名前缀约定（T_soft=120 资格）。无约定的目录 T_hard=60 适用，需拆分。

Usage:
    python scripts/governance/d5_architecture/validators/validate_nested_flat_dirs.py
    python scripts/governance/d5_architecture/validators/validate_nested_flat_dirs.py --warn-only
    python scripts/governance/d5_architecture/validators/validate_nested_flat_dirs.py --check-prefix
"""

__manifest__ = {
    "args": ["--warn-only", "--jsonl", "--max-depth", "--check-prefix"],
    "description": "递归嵌套目录平铺检测（GOV-DOC-018 T_hard=60/T_soft=120 + 前缀簇合规）",
    "dimensions": ["D5"],
    "priority": "P0",
    "timeout_seconds": 60,
    "warn_only": False,
}

import argparse
import json
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.thresholds import get

ensure_utf8_stdout()

SCAN_ROOTS = [
    REPO_ROOT / "src" / "zephyr",
    REPO_ROOT / "tests",
    REPO_ROOT / "scripts" / "governance",
]

SKIP_DIRS = {"__pycache__", ".git", "node_modules", ".mypy_cache", ".pytest_cache"}

# 前缀约定文档检测标记（__init__.py 注释块中任一存在即视为已文档化 T_soft 资格）
_PREFIX_CONVENTION_MARKERS = (
    "命名规则",
    "前缀簇",
    "T_soft",
    "GOV-DOC-018",
    "模块地图",
)


def _has_prefix_convention(init_path: Path) -> bool:
    """检查 __init__.py 是否文档化了命名前缀约定（T_soft=120 资格）。

    ARCH-043 Risk 2-B：>T_hard(60) 的目录必须有文档化的前缀约定才能享 T_soft=120。
    检测 __init__.py 注释块中的关键标记（命名规则/前缀簇/T_soft/GOV-DOC-018/模块地图）。
    """
    if not init_path.exists():
        return False
    try:
        content = init_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False
    return any(m in content for m in _PREFIX_CONVENTION_MARKERS)


def _scan_prefix_compliance(root: Path, t_hard: int, t_soft: int) -> list[dict]:
    """检查 T_soft 前缀簇合规（ARCH-043 Risk 2-B）。

    - count <= t_hard: PASS（无需前缀约定）
    - t_hard < count <= t_soft 且有前缀约定: PASS（T_soft=120 适用）
    - t_hard < count <= t_soft 且无前缀约定: ERROR（T_hard=60 适用，需拆分或补文档）
    - count > t_soft: ERROR（必须拆分，无论有无前缀约定）
    """
    violations = []
    for d in root.rglob("*"):
        if not d.is_dir():
            continue
        if d.name in SKIP_DIRS or d.name.startswith("."):
            continue
        py_files = [f for f in d.iterdir() if f.is_file() and f.suffix == ".py" and f.name != "__init__.py"]
        count = len(py_files)
        if count <= t_hard:
            continue
        has_conv = _has_prefix_convention(d / "__init__.py")
        rel = str(d.relative_to(REPO_ROOT)).replace("\\", "/")
        if count > t_soft:
            violations.append({
                "severity": "ERROR",
                "path": rel,
                "py_count": count,
                "threshold": t_soft,
                "has_prefix_convention": has_conv,
                "message": f"{count} .py files (>T_soft={t_soft}) — 必须拆分，无论有无前缀约定",
            })
        elif not has_conv:
            violations.append({
                "severity": "ERROR",
                "path": rel,
                "py_count": count,
                "threshold": t_hard,
                "has_prefix_convention": False,
                "message": (
                    f"{count} .py files (>T_hard={t_hard}) 但 __init__.py 未文档化命名前缀约定 — "
                    f"需拆分或补充前缀约定文档（GOV-DOC-018 T_soft 资格）"
                ),
            })
    return violations


def _scan_recursive(root: Path, max_depth: int, warn: int, error: int) -> list[dict]:
    """_scan_recursive implementation."""
    violations = []
    for d in root.rglob("*"):
        if not d.is_dir():
            continue
        if d.name in SKIP_DIRS or d.name.startswith("."):
            continue
        depth = len(d.relative_to(root).parts)
        if max_depth > 0 and depth > max_depth:
            continue
        py_files = [f for f in d.iterdir() if f.is_file() and f.suffix == ".py" and f.name != "__init__.py"]
        all_files = [f for f in d.iterdir() if f.is_file() and not f.name.startswith(".")]
        if len(py_files) >= error:
            violations.append(
                {
                    "severity": "ERROR",
                    "path": str(d.relative_to(REPO_ROOT)).replace("\\", "/"),
                    "py_count": len(py_files),
                    "total_count": len(all_files),
                    "threshold": error,
                    "message": f"{len(py_files)} .py files (error>{error}) — should use subdirectory isolation",
                }
            )
        elif len(py_files) >= warn:
            violations.append(
                {
                    "severity": "WARN",
                    "path": str(d.relative_to(REPO_ROOT)).replace("\\", "/"),
                    "py_count": len(py_files),
                    "total_count": len(all_files),
                    "threshold": warn,
                    "message": f"{len(py_files)} .py files (warn>{warn}) — consider subdirectory isolation",
                }
            )
    return violations


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="递归嵌套目录平铺检测")
    parser.add_argument("--warn-only", action="store_true")
    parser.add_argument("--jsonl", action="store_true")
    parser.add_argument("--max-depth", type=int, default=0, help="Max directory depth to scan (0=unlimited)")
    parser.add_argument(
        "--check-prefix",
        action="store_true",
        help="ARCH-043 Risk 2-B: 对 >T_hard(60) 的目录验证 __init__.py 是否文档化命名前缀约定（T_soft=120 资格）",
    )
    args = parser.parse_args()

    warn = get("directory_scalability.src_py_warn", 10)
    error = get("directory_scalability.src_py_error", 30)

    all_violations = []
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        violations = _scan_recursive(root, args.max_depth, warn, error)
        all_violations.extend(violations)
        if args.check_prefix:
            all_violations.extend(_scan_prefix_compliance(root, warn, error))

    errors = [v for v in all_violations if v["severity"] == "ERROR"]
    warns = [v for v in all_violations if v["severity"] == "WARN"]

    if not all_violations:
        mode = " + --check-prefix" if args.check_prefix else ""
        print(
            f"\u2705 嵌套目录平铺检测通过{mode}: 所有目录 .py 文件数在阈值内 (T_hard={warn}, T_soft={error})",
            file=sys.stderr,
        )
        if args.jsonl:
            print(json.dumps({"severity": "INFO", "check_id": "NESTED-FLAT", "violations": 0}, ensure_ascii=False))
        return EXIT_PASS
    print(f"\u274c 嵌套目录平铺检测: {len(errors)} errors, {len(warns)} warnings", file=sys.stderr)
    for v in sorted(all_violations, key=lambda x: (-x["py_count"], x["path"])):
        icon = "\u274c" if v["severity"] == "ERROR" else "\u26a0\ufe0f"
        print(f"  {icon} [{v['py_count']} .py] {v['path']} — {v['message']}", file=sys.stderr)

    if args.jsonl:
        for v in all_violations:
            print(json.dumps({"check_id": "NESTED-FLAT", **v}, ensure_ascii=False))

    if args.warn_only:
        print("\n\u26a0\ufe0f  --warn-only 模式: 仅报告，不阻断", file=sys.stderr)
        return EXIT_PASS
    if errors:
        print(
            "\n\u274c 阻断: 存在超过 error 阈值的平铺目录。参考 GOV-DOC-018 \u6587\u4ef6\u5939\u5e73\u94fa\u5bb9\u91cf\u9608\u503c\u534f\u8bae\u3002", file=sys.stderr
        )
        return EXIT_FINDINGS
    return EXIT_PASS


if __name__ == "__main__":
    raise SystemExit(main())
