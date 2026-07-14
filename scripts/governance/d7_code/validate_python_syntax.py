# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/validate_python_syntax.py | §
# [MODULE] scripts.governance.d7_code.validate_python_syntax
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
"""validate_python_syntax.py — Python 语法完整性校验

对标：AUDIT-09 病根分析（连字符损坏 / 语法错误）

检测内容：
- 扫描 src/zephyr/ 和 tests/ 下所有 .py 文件
- 使用 py_compile 编译校验语法正确性
- 捕获连字符损坏、括号不匹配、缩进错误等语法问题

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: >
  Python 语法完整性校验 —— 扫描 src/zephyr/ + tests/ 全部 .py 文件，
  使用 py_compile 编译验证。预防连字符损坏、批量替换副作用等语法破坏。
dimensions:
- D7
priority: P1
timeout_seconds: 60
warn_only: false
"""

import argparse
import multiprocessing
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

_TARGET_DIRS = ["src/zephyr", "tests"]
_EXCLUDE_DIRS = ["__pycache__", ".git", ".ailocks", ".trae", "session_logs"]


def _find_py_files() -> list[Path]:
    """_find_py_files implementation."""
    files: list[Path] = []
    for target in _TARGET_DIRS:
        target_path = REPO_ROOT / target
        if not target_path.exists():
            print(f"WARNING: 目录不存在，跳过: {target_path}")
            continue
        for py_file in target_path.rglob("*.py"):
            parts = py_file.parts
            if any(excl in parts for excl in _EXCLUDE_DIRS):
                continue
            files.append(py_file)
    return files


def _check_syntax(py_file: Path) -> str | None:
    """_check_syntax implementation."""
    try:
        with open(py_file, encoding="utf-8") as f:
            source = f.read()
        compile(source, str(py_file), "exec")
        return None
    except SyntaxError as exc:
        return f"SYNTAX-ERROR: {py_file} [line {exc.lineno}]: {exc.msg}"
    except Exception as exc:
        return f"COMPILE-ERROR: {py_file}: {exc}"


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="Python 语法完整性校验")
    parser.parse_args()

    py_files = _find_py_files()
    total = len(py_files)
    print(f"扫描 {total} 个 Python 文件...")

    findings: list[str] = []
    with multiprocessing.Pool() as pool:
        results = pool.map(_check_syntax, py_files)

    for result in results:
        if result is not None:
            findings.append(result)
            print(result)

    ok = total - len(findings)
    print(f"\n结果: {ok}/{total} 通过, {len(findings)} 语法错误")

    if findings:
        return EXIT_FINDINGS
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
