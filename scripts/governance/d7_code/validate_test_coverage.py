# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/validate_test_coverage.py | §
# [MODULE] scripts.governance.d7_code.validate_test_coverage
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
validate_test_coverage.py — 测试覆盖率治理校验器



对标：AGENTS.md §7.2（根源分析优先 — 测试缺口是系统性风险，非个案）
     PS-STD-003 COND-43（代码质量维度补全）

检测内容：
- 扫描 src/zephyr/**/*.py（排除 __init__.py 和骨架/占位文件）
- 对每个源文件检查 tests/ 下是否存在对应的 test_*.py
- 输出未覆盖模块清单

映射规则（ARCH-029 后 tests/ 按功能域归类，无 unit/ 目录）：
  src/zephyr/{module}/{filename}.py  →  tests/{domain}/test_{filename}.py
  src/zephyr/{filename}.py           →  tests/{domain}/test_{filename}.py
  （domain 由模块功能域决定，递归搜索 tests/ 下所有 test_*.py）

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 测试覆盖率校验——每个 src/zephyr/ 下 .py 文件必须有对应 test_*.py
dimensions:
- D7
priority: P1
timeout_seconds: 30
warn_only: false
"""


import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

from _shared.constants import EXIT_PASS, REPO_ROOT, SRC_DIR

TESTS_DIR = REPO_ROOT / "tests"

SKIP_MODULES = {  # noqa: gate-vocab  跳过测试覆盖的目录名，非 domain 值
    "data",
    "infrastructure_runtime_integration",
    "factor",
    "signal",
    "risk",
    "pf_core",
    "ex_core",
    "frontend",
    "research",
    "compliance",
    "ml_train",
    "observability",
    "integration",
}


def _is_skeleton_module(filepath: Path) -> bool:
    """_is_skeleton_module implementation."""
    parts = filepath.parts
    if "__init__.py" in parts:
        return False
    for part in parts:
        if part in SKIP_MODULES:
            return True
    return False


def _find_test_file(source_file: Path) -> Path | None:
    """_find_test_file implementation."""
    stem = source_file.stem
    try:
        rel = source_file.relative_to(SRC_DIR)
    except ValueError:
        return None

    # ARCH-029: tests/ 按功能域归类，递归搜索所有子目录
    candidates = list(TESTS_DIR.rglob(f"test_{stem}.py"))
    candidates = [c for c in candidates if "__pycache__" not in str(c)]

    if rel.parent != Path("."):
        module_prefix = rel.parent.name
        candidates.extend(
            c for c in TESTS_DIR.rglob(f"test_{module_prefix}_{stem}.py")
            if "__pycache__" not in str(c)
        )

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def scan_coverage() -> tuple[list[dict], int, int]:
    """扫描测试覆盖率."""
    untested: list[dict] = []
    """扫描并返回发现列表."""
    total_sources = 0
    tested_count = 0

    for py_file in SRC_DIR.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
        if _is_skeleton_module(py_file):
            continue

        total_sources += 1
        test_file = _find_test_file(py_file)

        try:
            rel_src = py_file.relative_to(REPO_ROOT)
        except ValueError:
            rel_src = py_file

        if test_file is None:
            untested.append(
                {
                    "source": str(rel_src),
                    "test_expected": f"tests/{{domain}}/test_{py_file.stem}.py",
                    "module": py_file.parent.name,
                }
            )
        else:
            tested_count += 1

    return untested, total_sources, tested_count
    """扫描测试覆盖率."""


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="测试覆盖率治理校验器")
    parser.add_argument("--warn-only", action="store_true", help="警告模式")
    args = parser.parse_args()

    untested, total_sources, tested_count = scan_coverage()
    coverage_pct = (tested_count / total_sources * 100) if total_sources > 0 else 100

    if untested:
        print(
            f"\n[TEST-COV] {len(untested)} 源文件缺少单元测试（共 {total_sources} 源文件，覆盖率 {coverage_pct:.0f}%）:\n",
            file=sys.stderr,
        )
        for f in untested:
            source = f["source"]
            test_expected = f["test_expected"]
            module = f["module"]
            print(f"[P1] {source}  缺少单元测试（期望: {test_expected}, 模块: {module}）", file=sys.stderr)
        print(file=sys.stderr)
    else:
        print(f"\n[TEST-COV] 全部 {total_sources} 源文件已有对应单元测试 ✅\n", file=sys.stderr)

    print(
        f"Scanned {total_sources} source files, {tested_count} tested ({coverage_pct:.0f}%), {len(untested)} untested",
        file=sys.stderr,
    )

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if untested else 0)


if __name__ == "__main__":
    main()
