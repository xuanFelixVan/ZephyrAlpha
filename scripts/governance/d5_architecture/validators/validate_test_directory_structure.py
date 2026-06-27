# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/validate_test_directory_structure.py | §
# [MODULE] scripts.governance.d5_architecture.validators.validate_test_directory_structure
# [DOMAIN] D-GOVERNANCE
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
validate_test_directory_structure.py — 测试目录结构校验器
=========================================================
依据：GOV-DOC-002 §三 + blueprint-template.md §6（测试代码路径）

检查项
------
1. tests/unit/ 下是否有模块子目录分组（非平铺）
2. tests/unit/ 根级 .py 文件数是否超过阈值
3. tests/ 下的子目录是否与 src/zephyr/ 模块一一对应

Usage:
    python scripts/governance/d5_architecture/validate_test_directory_structure.py
    python scripts/governance/d5_architecture/validate_test_directory_structure.py --warn-only
"""

__manifest__ = {
    "args": ["--warn-only", "--jsonl"],
    "description": "测试目录结构校验（tests/unit/ 模块分组 + 平铺检测）",
    "dimensions": ["D5"],
    "priority": "P1",
    "timeout_seconds": 30,
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

TESTS_DIR = REPO_ROOT / "tests"
UNIT_DIR = TESTS_DIR / "unit"
SRC_ZEPHYR = REPO_ROOT / "src" / "zephyr"

FLAT_THRESHOLD_WARN = 20
FLAT_THRESHOLD_ERROR = 50


def _get_src_modules() -> set[str]:
    """_get_src_modules implementation."""
    if not SRC_ZEPHYR.exists():
        return set()
    return {d.name for d in SRC_ZEPHYR.iterdir() if d.is_dir() and not d.name.startswith("_")}


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="测试目录结构校验")
    parser.add_argument("--warn-only", action="store_true")
    parser.add_argument("--jsonl", action="store_true")
    args = parser.parse_args()

    warn_threshold = get("directory_scalability.src_py_warn", FLAT_THRESHOLD_WARN)
    error_threshold = get("directory_scalability.src_py_error", FLAT_THRESHOLD_ERROR)

    violations = []

    if UNIT_DIR.exists():
        root_py_files = [f for f in UNIT_DIR.iterdir() if f.is_file() and f.suffix == ".py" and f.name != "__init__.py"]
        if len(root_py_files) >= error_threshold:
            violations.append(
                {
                    "severity": "ERROR",
                    "path": "tests/unit/",
                    "count": len(root_py_files),
                    "message": f"tests/unit/ has {len(root_py_files)} flat .py files (error>{error_threshold}) — should use module subdirectories (e.g., tests/unit/db/, tests/unit/shared/)",
                }
            )
        elif len(root_py_files) >= warn_threshold:
            violations.append(
                {
                    "severity": "WARN",
                    "path": "tests/unit/",
                    "count": len(root_py_files),
                    "message": f"tests/unit/ has {len(root_py_files)} flat .py files (warn>{warn_threshold}) — consider module subdirectories",
                }
            )

        subdirs = {d.name for d in UNIT_DIR.iterdir() if d.is_dir() and not d.name.startswith("_")}
        src_modules = _get_src_modules()
        missing_test_dirs = src_modules - subdirs - {"__pycache__"}
        significant_missing = {
            m
            for m in missing_test_dirs
            if any(
                (SRC_ZEPHYR / m / f).is_file() and f.suffix == ".py" and f.name != "__init__.py"
                for f in (SRC_ZEPHYR / m).iterdir()
            )
            if (SRC_ZEPHYR / m).is_dir()
        }
        if significant_missing:
            violations.append(
                {
                    "severity": "WARN",
                    "path": "tests/unit/",
                    "count": len(significant_missing),
                    "message": f"Missing test subdirectories for src modules: {sorted(significant_missing)[:10]}",
                }
            )

    if not violations:
        print("\u2705 测试目录结构校验通过", file=sys.stderr)
        if args.jsonl:
            print(
                json.dumps({"severity": "INFO", "check_id": "TEST-DIR-STRUCTURE", "violations": 0}, ensure_ascii=False)
            )
        return EXIT_PASS
    print(f"\u274c 测试目录结构问题: {len(violations)} 项", file=sys.stderr)
    for v in violations:
        icon = "\u274c" if v["severity"] == "ERROR" else "\u26a0\ufe0f"
        print(f"  {icon} {v['path']} — {v['message']}", file=sys.stderr)

    if args.jsonl:
        for v in violations:
            print(json.dumps({"check_id": "TEST-DIR-STRUCTURE", **v}, ensure_ascii=False))

    if args.warn_only:
        print("\n\u26a0\ufe0f  --warn-only 模式: 仅报告，不阻断", file=sys.stderr)
        return EXIT_PASS
    errors = [v for v in violations if v["severity"] == "ERROR"]
    if errors:
        print("\n\u274c 阻断: 测试目录存在严重平铺问题。", file=sys.stderr)
        return EXIT_FINDINGS
    return EXIT_PASS


if __name__ == "__main__":
    raise SystemExit(main())
