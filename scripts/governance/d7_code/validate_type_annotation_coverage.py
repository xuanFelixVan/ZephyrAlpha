# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/validate_type_annotation_coverage.py | §
# [MODULE] scripts.governance.d7_code.validate_type_annotation_coverage
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
# [TTL] permanent
"""
validate_type_annotation_coverage.py — 类型注解覆盖率校验



对标：PEP 484 — type hints improve code readability and enable static analysis
     AGENTS.md §5.1 — 零记忆重启标准（类型注解 = AI 可读的"迷你合约"）

检测 src/zephyr/ 下所有 .py 文件中：
- 公共函数的参数缺少类型注解
- 公共函数缺少返回值类型注解

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 类型注解覆盖率校验——公共函数参数和返回值必须有类型注解
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

SKIP_MODULES = {  # noqa: gate-vocab  跳过类型注解检查的业务子集
    "signal",
    "risk",
    "pf_core",
    "ex_core",
    "frontend",
    "research",
    "compliance",
    "ml_train",
    "integration",
}


def _is_public(name: str) -> bool:
    """_is_public implementation."""
    if name.startswith("__") and name.endswith("__"):
        return False
    return not name.startswith("_")


def _has_return_annotation(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """_has_return_annotation implementation."""
    return node.returns is not None


def _missing_param_annotations(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    """_missing_param_annotations implementation."""
    missing = []
    for arg in node.args.args:
        if arg.arg == "self":
            continue
        if arg.arg == "cls":
            continue
        if arg.annotation is None:
            missing.append(arg.arg)
    return missing


def scan_type_annotations(source_path: Path) -> list[str]:
    """扫描类型注解覆盖率."""
    with open(source_path, encoding="utf-8") as f:
        """扫描类型注解覆盖率."""
        """扫描并返回发现列表."""
        source = f.read()
    tree = ast.parse(source, filename=str(source_path))

    issues = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not _is_public(node.name):
                continue

            missing_params = _missing_param_annotations(node)
            if missing_params:
                params_str = ", ".join(missing_params)
                issues.append(f"[函数] {node.name}({params_str}) 参数缺少类型注解")

            if not _has_return_annotation(node):
                issues.append(f"[函数] {node.name}() 缺少返回值类型注解")

        elif isinstance(node, ast.ClassDef):
            if not _is_public(node.name):
                continue
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not _is_public(sub.name):
                        continue
                    missing_params = _missing_param_annotations(sub)
                    if missing_params:
                        params_str = ", ".join(missing_params)
                        issues.append(f"[方法] {node.name}.{sub.name}({params_str}) 参数缺少类型注解")
                    if not _has_return_annotation(sub):
                        if sub.name != "__init__":
                            issues.append(f"[方法] {node.name}.{sub.name}() 缺少返回值类型注解")

    return issues
    """扫描类型注解覆盖率."""


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="类型注解覆盖率校验")
    parser.add_argument("--warn-only", action="store_true", help="警告模式")
    args = parser.parse_args()

    findings = []
    total_files = 0
    ok_files = 0

    for py_file in SRC_DIR.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue

        parts = set(py_file.parts)
        if parts & SKIP_MODULES:
            continue

        total_files += 1
        issues = scan_type_annotations(py_file)

        if issues:
            try:
                rel = py_file.relative_to(REPO_ROOT)
            except ValueError:
                rel = py_file
            for i_item in issues:
                findings.append(f"[P2] {rel}  {i_item}")
        else:
            ok_files += 1

    if findings:
        print(
            f"\n[TYPE-ANNOT] {len(findings)} 个类型注解缺失（扫描 {total_files} 文件，{ok_files} 合格）:\n",
            file=sys.stderr,
        )
        for f_item in findings:
            print(f_item, file=sys.stderr)
        print(file=sys.stderr)
    else:
        print(f"\n[TYPE-ANNOT] 全部 {total_files} 文件类型注解完整 ✅\n", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
