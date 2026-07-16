# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] scripts.governance.d7_code.detect_forward_reference
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] _shared.constants; _shared.encoding; _shared.walk
# [CONSUMERS] gate_engine; phase_manager
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=clean, exit 1=findings, exit 2=error
# [TESTS] python scripts/governance/d7_code/detect_forward_reference.py --warn-only
# [A_module] module_id=MOD-GOV_detect_forward_ref | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""detect_forward_reference — 前向引用检测扫描器。

检测 class X 定义内部引用 X 自身的模式（前向引用 bug）。
当 class 定义体内引用了自身类名且文件缺少 `from __future__ import annotations` 时，
运行时会抛出 NameError。

根因：表头升级（TRAE-047）大规模修改文件时引入 48 个此类 bug。
治根：本扫描器作为门禁，在代码变更时自动检测前向引用风险。

用法:
    python scripts/governance/d7_code/detect_forward_reference.py [--warn-only]
    python scripts/governance/d7_code/detect_forward_reference.py --path src/zephyr/
"""
from __future__ import annotations

__manifest__ = """
args: []
description: detect_forward_reference — 前向引用检测扫描器。
dimensions:
- D7
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import ast
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

# REPO_ROOT 真源为 zephyr.shared.io.paths（project_memory 钦定唯一真源）。
# 一次性 bootstrap sys.path（此 N 值对本文件固定且仅用一次），随后从 _shared.constants 获取 REPO_ROOT。
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import REPO_ROOT
SCAN_DIRS = [REPO_ROOT / "src" / "zephyr", REPO_ROOT / "scripts"]
SCAN_EXTENSIONS = {".py"}
EXIT_PASS = 0
EXIT_FINDINGS = 1
EXIT_ERROR = 2


@dataclass
class ForwardRefViolation:
    filepath: str
    line: int
    col: int
    class_name: str
    context: str


@dataclass
class ScanResult:
    violations: list[ForwardRefViolation] = field(default_factory=list)
    files_scanned: int = 0
    files_with_future: int = 0
    errors: list[str] = field(default_factory=list)


def has_future_annotations(tree: ast.Module) -> bool:
    """检查模块是否有 `from __future__ import annotations`。"""
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            if node.module == "__future__":
                for alias in node.names:
                    if alias.name == "annotations":
                        return True
    return False


def find_self_references(class_node: ast.ClassDef) -> list[tuple[int, int, str]]:
    """在 ClassDef 中查找引用自身类名的节点，排除方法体内引用。

    前向引用 bug 发生在类定义时立即执行的代码中（类变量、基类、装饰器）。
    方法体内的引用是安全的——方法在类定义完成后才被调用。
    方法装饰器在类定义时执行，需要检测。

    返回 [(line, col, context), ...]
    """
    results: list[tuple[int, int, str]] = []
    class_name = class_node.name

    def check_node(node):
        if isinstance(node, ast.Name) and node.id == class_name:
            results.append((node.lineno, node.col_offset, class_name))

    # 检查基类列表
    for base in class_node.bases:
        for node in ast.walk(base):
            check_node(node)

    # 检查关键字参数
    for kw in class_node.keywords:
        for node in ast.walk(kw):
            check_node(node)

    # 检查类装饰器
    for decorator in class_node.decorator_list:
        for node in ast.walk(decorator):
            check_node(node)

    # 检查 body 中的非方法节点（类变量、嵌套类等）
    for stmt in class_node.body:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # 方法：只检查装饰器，不检查方法体
            for decorator in stmt.decorator_list:
                for node in ast.walk(decorator):
                    check_node(node)
            continue
        for node in ast.walk(stmt):
            check_node(node)

    return results


def scan_file(filepath: str) -> tuple[list[ForwardRefViolation], bool, str | None]:
    """扫描单个文件，返回 (violations, has_future, error)。

    violations: 前向引用违规列表（仅在缺少 from __future__ import annotations 时报告）
    has_future: 文件是否有 from __future__ import annotations
    error: 解析错误信息（None 表示无错误）
    """
    try:
        with open(filepath, encoding="utf-8") as f:
            source = f.read()
    except (OSError, UnicodeDecodeError) as e:
        return [], False, str(e)

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError as e:
        return [], False, f"SyntaxError: {e}"

    has_future = has_future_annotations(tree)
    if has_future:
        return [], True, None

    violations: list[ForwardRefViolation] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            self_refs = find_self_references(node)
            for line, col, ctx in self_refs:
                try:
                    source_lines = source.splitlines()
                    context_line = source_lines[line - 1].strip() if line <= len(source_lines) else ""
                except (IndexError, OSError):
                    context_line = ""
                violations.append(ForwardRefViolation(
                    filepath=filepath,
                    line=line,
                    col=col,
                    class_name=ctx,
                    context=context_line,
                ))

    return violations, has_future, None


def iter_py_files(scan_dirs: list[Path]) -> list[str]:
    """遍历扫描目录，返回所有 .py 文件路径。"""
    files: list[str] = []
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for root, _dirs, filenames in os.walk(scan_dir):
            if "__pycache__" in root or ".aidrafts" in root:
                continue
            for fname in filenames:
                if Path(fname).suffix in SCAN_EXTENSIONS:
                    files.append(os.path.join(root, fname))
    return files


def main() -> int:
    parser = argparse.ArgumentParser(
        description="前向引用检测扫描器——检测 class X 内部引用 X 自身的前向引用 bug"
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="仅警告，不阻断（exit 0 即使有违规）",
    )
    parser.add_argument(
        "--path",
        type=str,
        default=None,
        help="指定扫描路径（默认扫描 src/zephyr/ 和 scripts/）",
    )
    args = parser.parse_args()

    if args.path:
        scan_dirs = [Path(args.path)]
    else:
        scan_dirs = SCAN_DIRS

    py_files = iter_py_files(scan_dirs)
    result = ScanResult()

    for filepath in py_files:
        violations, has_future, error = scan_file(filepath)
        result.files_scanned += 1
        if has_future:
            result.files_with_future += 1
        if error:
            result.errors.append(f"{filepath}: {error}")
        result.violations.extend(violations)

    print(f"[SCAN] files_scanned={result.files_scanned} "
          f"files_with_future={result.files_with_future} "
          f"violations={len(result.violations)} "
          f"errors={len(result.errors)}")

    if result.errors:
        for err in result.errors[:10]:
            print(f"  [ERROR] {err}")

    if result.violations:
        print(f"\n[VIOLATION] {len(result.violations)} forward reference(s) found:")
        for v in result.violations[:50]:
            try:
                rel_path = os.path.relpath(v.filepath, REPO_ROOT)
            except ValueError:
                rel_path = v.filepath
            print(f"  {rel_path}:{v.line}:{v.col} | class {v.class_name} | {v.context}")
        if len(result.violations) > 50:
            print(f"  ... and {len(result.violations) - 50} more")
        if not args.warn_only:
            return EXIT_FINDINGS
        print("\n[WARN-ONLY] violations found but not blocking (--warn-only)")
        return EXIT_PASS

    print("[CLEAN] no forward reference violations found")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
