# [BLUEPRINT] MOD-INF-005 | scripts/governance/d11_compliance/validate_script_quality.py | §
# [MODULE] scripts.governance.d11_compliance.validate_script_quality
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d11_compliance.__init__
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
validate_script_quality.py — 治理脚本质量合规检查


对标：SCRIPT-QUALITY-001 §10 自检清单（38 项条款：22 MUST + 16 SHOULD）
      AGENTS.md §6.5（脚本自创入库强制约定）

检测内容（15 项可自动化的条款）：
- D-A-01: UTF-8 输出强制声明（ensure_utf8_stdout 或 sys.stdout.reconfigure）
- D-A-02: 禁止裸 except
- D-A-03: 禁止 shell=True
- D-A-04: I/O 操作必须显式指定 encoding='utf-8'（SCRIPT-QUALITY-001 D-A-04）
- D-A-05: 禁止重复 import（同一模块被 import 多次）
- D-B-01: 公共函数必须有返回类型注解
- D-B-02: main() 必须有返回类型标注
- D-C-01: 必须有模块级 docstring
- D-C-02: 公共函数必须有 docstring
- D-D-06: 必须有 if __name__ == "__main__" 守卫
- D-D-07: 禁止绕过 _shared 工具——本地重定义等价函数/常量（SCRIPT-QUALITY-001 D-D-07）
- D-D-08: 禁止 os.walk() + 手动 EXCLUDE_DIRS 过滤——应使用 iter_files()（SCRIPT-QUALITY-001 D-D-08）
- D-F-01: 必须支持 --warn-only 参数
- D-F-02: 必须使用 sys.exit() 返回 POSIX 退出码
- D-G-06: 禁止 ast.unparse() 重写文件——必须使用 LibCST 等无损工具（SCRIPT-QUALITY-001 D-G-06）

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 治理脚本质量合规检查（SCRIPT-QUALITY-001 §10 — 10项可自动化MUST条款扫描）
dimensions:
- D11
priority: P1
timeout_seconds: 60
warn_only: false
"""

import ast
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_ERROR, EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_CODE
from _shared.encoding import ensure_utf8_stdout
from _shared.walk import iter_files

ensure_utf8_stdout()
import argparse

EXCLUDE_NAMES = {"__init__.py"}
_SELF_REL = "scripts/governance/d11_compliance/validate_script_quality.py"


class ClauseCheck:
    def __init__(self, clause_id: str, description: str, severity: str = "MUST"):
        """__init__ implementation."""
        self.clause_id = clause_id
        self.description = description
        self.severity = severity
        self.failures: list[str] = []

    def add_failure(self, filepath: Path, detail: str = "") -> None:
        """add failure"""
        self.failures.append(
            f"{filepath.relative_to(REPO_ROOT)}: {detail}" if detail else str(filepath.relative_to(REPO_ROOT))
        )


def check_utf8(content: str, filepath: Path, result: ClauseCheck) -> None:
    """check utf8"""
    if "ensure_utf8_stdout" not in content and "sys.stdout.reconfigure" not in content:
        result.add_failure(filepath, "缺少 UTF-8 输出强制声明")


def check_bare_except(content: str, filepath: Path, result: ClauseCheck) -> None:
    """check bare except"""
    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if re.match("^except\\s*:", stripped):
            result.add_failure(filepath, f"L{i}: 裸 except")


def _is_code_line(line: str, in_docstring: bool) -> bool:
    """_is_code_line implementation."""
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return False
    if stripped.startswith('"""') or stripped.startswith("'''"):
        return False
    if in_docstring:
        if '"""' in stripped or "'''" in stripped:
            return False
        return False
    return True


def _strip_string_literals(line: str) -> str:
    """_strip_string_literals implementation."""
    result = []
    in_single = False
    in_double = False
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == '"' and (not in_single):
            in_double = not in_double
            result.append('"')
            i += 1
            continue
        if ch == "'" and (not in_double):
            in_single = not in_single
            result.append("'")
            i += 1
            continue
        if not in_single and (not in_double):
            result.append(ch)
        i += 1
    return "".join(result)


def check_io_encoding(content: str, filepath: Path, result: ClauseCheck) -> None:
    """check io encoding"""
    lines = content.split("\n")
    in_docstring = False
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            in_docstring = not in_docstring
            continue
        if in_docstring or stripped.startswith("#"):
            continue
        code_only = _strip_string_literals(line)
        for pattern in ["open(", ".read_text(", ".write_text("]:
            if pattern in code_only:
                if "encoding=" not in code_only and "encoding =" not in code_only:
                    result.add_failure(filepath, f"L{i}: I/O 操作缺少 encoding='utf-8' ({pattern})")
                    break


def check_shell_true(content: str, filepath: Path, result: ClauseCheck) -> None:
    """check shell true"""
    lines = content.split("\n")
    in_docstring = False
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            in_docstring = not in_docstring
            continue
        if in_docstring:
            if '"""' in stripped or "'''" in stripped:
                in_docstring = False
            continue
        if stripped.startswith("#"):
            continue
        if "shell=True" in line:
            code_only = _strip_string_literals(line)
            if "shell=True" in code_only:
                result.add_failure(filepath, f"L{i}: shell=True")


def check_main_return_type(content: str, filepath: Path, result: ClauseCheck) -> None:
    """check main return type"""
    if "def main" not in content:
        return
    for m in re.finditer("def main\\([^)]*\\)(\\s*->\\s*\\S+)?\\s*:", content):
        if "->" not in m.group(0):
            result.add_failure(filepath, "main() 缺少返回类型标注")


def check_docstring(content: str, filepath: Path, result: ClauseCheck) -> None:
    """check docstring"""
    if filepath.name == "__init__.py":
        return
    if filepath.suffix != ".py":
        return
    try:
        tree = ast.parse(content, filename=str(filepath))
        if ast.get_docstring(tree) is None:
            result.add_failure(filepath, "缺少模块级 docstring")
    except SyntaxError:
        result.add_failure(filepath, "语法错误，无法解析 docstring")


def check_public_func_annotations(content: str, filepath: Path, result: ClauseCheck) -> None:
    """check public func annotations"""
    try:
        tree = ast.parse(content, filename=str(filepath))
    except SyntaxError:
        return
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and (not node.name.startswith("_")):
            if node.returns is None:
                result.add_failure(filepath, f"D-B-01: 公共函数 '{node.name}' 缺少返回类型注解（L{node.lineno}）")


def check_public_func_docstring(content: str, filepath: Path, result: ClauseCheck) -> None:
    """check public func docstring"""
    try:
        tree = ast.parse(content, filename=str(filepath))
    except SyntaxError:
        return
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and (not node.name.startswith("_")):
            if ast.get_docstring(node) is None:
                result.add_failure(filepath, f"D-C-02: 公共函数 '{node.name}' 缺少 docstring（L{node.lineno}）")


def check_main_guard(content: str, filepath: Path, result: ClauseCheck) -> None:
    """check main guard"""
    if 'if __name__ == "__main__"' not in content and "if __name__ == '__main__'" not in content:
        result.add_failure(filepath, "缺少 if __name__ == '__main__' 守卫")


def check_warn_only(content: str, filepath: Path, result: ClauseCheck) -> None:
    """check warn only"""
    if "--warn-only" not in content and "--warn_only" not in content:
        result.add_failure(filepath, "不支持 --warn-only")


def check_exit_codes(content: str, filepath: Path, result: ClauseCheck) -> None:
    """check exit codes"""
    if "sys.exit(" not in content and "SystemExit" not in content:
        result.add_failure(filepath, "缺少 sys.exit() 显式退出码")


_SHARED_API_NAMES: frozenset[str] = frozenset(
    {
        "REPO_ROOT",
        "EXCLUDE_DIRS",
        "SCAN_EXTENSIONS_MD_YAML",
        "SCAN_EXTENSIONS_CODE",
        "SCAN_EXTENSIONS_DOCS",
        "SCAN_EXTENSIONS_PY",
        "SCAN_EXTENSIONS_MD",
        "SCAN_EXTENSIONS_DATA",
        "GOV_DOCS_DIR",
        "SRC_DIR",
        "CONFIG_DIR",
        "SCRIPTS_DIR",
        "MANIFEST_PATH",
        "find_repo_root",
        "parse_frontmatter",
        "parse_frontmatter_from_file",
        "parse_frontmatter_raw_from_file",
        "parse_yaml_header",
        "ensure_utf8_stdout",
        "iter_files",
        "load_yaml",
    }
)


def check_duplicate_imports(content: str, filepath: Path, result: ClauseCheck) -> None:
    """check duplicate imports"""
    try:
        tree = ast.parse(content, filename=str(filepath))
    except SyntaxError:
        return
    seen: dict[str, int] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                seen[alias.name] = seen.get(alias.name, 0) + 1
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                seen[node.module] = seen.get(node.module, 0) + 1
    for name, count in seen.items():
        if count > 1:
            result.add_failure(filepath, f"重复 import: '{name}' 被导入 {count} 次")


def check_shared_bypass(content: str, filepath: Path, result: ClauseCheck) -> None:
    """D-D-07: 逐符号检测——仅豁免已从 _shared import 的符号。

    与 v1 的区别：v1 发现任何 from _shared import 就跳过整个文件。
    v2 改为逐符号豁免——脚本可以从 _shared.constants import REPO_ROOT
    但仍然会因为定义了 parse_frontmatter 而被告警。"""
    rel = str(filepath).replace("\\", "/")
    if "_shared/" in rel:
        return
    try:
        tree = ast.parse(content, filename=str(filepath))
    except SyntaxError:
        return
    imported_from_shared: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module.startswith("_shared"):
                imported_from_shared |= {a.name for a in node.names}
        elif isinstance(node, ast.Import):
            for a in node.names:
                if a.name.startswith("_shared"):
                    imported_from_shared.add(a.asname or a.name.split(".")[-1])
    local_defs: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            local_defs.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    local_defs.add(target.id)
    overlaps = (local_defs & _SHARED_API_NAMES) - imported_from_shared
    if overlaps:
        result.add_failure(
            filepath, f"本地重定义了 _shared 工具: {', '.join(sorted(overlaps))} — 请改为 from _shared.xxx import ..."
        )


def check_oswalk_bypass(content: str, filepath: Path, result: ClauseCheck) -> None:
    """D-D-08: 检测 os.walk() + 手动 EXCLUDE_DIRS 过滤模式。

    该模式已由 _shared/walk.py 的 iter_files() 统一封装。
    脚本应优先使用 iter_files()，仅在特殊需求时使用 os.walk()。"""
    if "_shared/" in str(filepath).replace("\\", "/"):
        return
    has_oswalk = "os.walk(" in content or "os.walk (" in content
    has_exclude = "EXCLUDE_DIRS" in content or "exclude" in content.lower()
    uses_iter_files = "iter_files(" in content
    if has_oswalk and has_exclude and (not uses_iter_files):
        result.add_failure(
            filepath, "使用 os.walk() + 手动 EXCLUDE_DIRS 过滤 — 请改为 from _shared.walk import iter_files"
        )


def check_lossy_transform(content: str, filepath: Path, result: ClauseCheck) -> None:
    """D-G-06: 检测 ast.unparse() 重写文件——有损代码变换。

    ast.unparse() 丢失行内注释、自定义格式。代码变换必须使用
    LibCST (libcst.parse_module → CSTTransformer → tree.code) 等无损工具。
    对标：Instagram/Meta LibCST + ruff safe/unsafe 修复分类。"""
    has_unparse = False
    has_write = False
    in_docstring = False
    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            in_docstring = not in_docstring
            continue
        if in_docstring or stripped.startswith("#"):
            continue
        code_only = _strip_string_literals(line)
        if "ast.unparse(" in code_only:
            has_unparse = True
        if ".write_text(" in code_only or ".write(" in code_only:
            has_write = True
    if has_unparse and has_write:
        result.add_failure(
            filepath,
            "使用 ast.unparse() + 文件写入——有损代码变换，丢失行内注释/格式。请改用 LibCST (libcst.parse_module → CSTTransformer → tree.code)",
        )


CLAUSE_CHECKS: list[tuple[str, str, callable, bool]] = [
    ("D-A-01", "UTF-8 输出强制声明", check_utf8, False),
    ("D-A-02", "禁止裸 except", check_bare_except, False),
    ("D-A-03", "禁止 shell=True", check_shell_true, False),
    ("D-A-04", "I/O 操作显式 encoding='utf-8'", check_io_encoding, True),
    ("D-A-05", "禁止重复 import", check_duplicate_imports, False),
    ("D-B-01", "公共函数返回类型注解", check_public_func_annotations, True),
    ("D-B-02", "main() 返回类型标注", check_main_return_type, True),
    ("D-C-01", "模块级 docstring", check_docstring, False),
    ("D-C-02", "公共函数 docstring", check_public_func_docstring, True),
    ("D-D-06", "if __name__ 守卫", check_main_guard, True),
    ("D-D-07", "禁止绕过 _shared 工具", check_shared_bypass, False),
    ("D-D-08", "禁止 os.walk + EXCLUDE_DIRS 手动过滤", check_oswalk_bypass, False),
    ("D-F-01", "--warn-only 支持", check_warn_only, True),
    ("D-F-02", "POSIX 退出码", check_exit_codes, True),
    ("D-G-06", "禁止 ast.unparse 重写文件", check_lossy_transform, False),
]


def _is_library_module(content: str) -> bool:
    """_is_library_module implementation."""
    return "def main" not in content and "if __name__" not in content


def scan_scripts(scan_dir: Path, warn_only: bool = False) -> tuple[list[ClauseCheck], int]:
    """scan scripts"""
    results: list[ClauseCheck] = []
    total_scripts = 0
    is_lib: dict[str, bool] = {}
    for clause_id, desc, _checker, _exec_only in CLAUSE_CHECKS:
        results.append(ClauseCheck(clause_id, desc))
    for filepath in sorted(iter_files(scan_dir, SCAN_EXTENSIONS_CODE, EXCLUDE_NAMES)):
        total_scripts += 1
        try:
            content = filepath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
        if rel == _SELF_REL:
            continue
        is_lib[rel] = _is_library_module(content)
        for clause_id, desc, checker, exec_only in CLAUSE_CHECKS:
            if exec_only and is_lib.get(rel, False):
                continue
            for result in results:
                if result.clause_id == clause_id:
                    checker(content, filepath, result)
                    break
    return (results, total_scripts)


def _fix_dc02(scan_dir: Path) -> int:
    """Auto-fix D-C-02 violations using LibCST (lossless)."""
    try:
        from _shared.libcst_docstring_adder import add_docstrings_lossless
    except ImportError:
        print("[FIX] 无法导入 libcst_docstring_adder，请确认 libcst 已安装", file=sys.stderr)
        return EXIT_PASS
    targets = [
        f
        for f in iter_files(scan_dir, SCAN_EXTENSIONS_CODE, EXCLUDE_NAMES)
        if f.name != "__init__.py" and "_shared" not in f.parts
    ]
    total_fixed = 0
    for fp in targets:
        try:
            content = fp.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        try:
            tree = ast.parse(content)
        except SyntaxError:
            continue
        needs_fix = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and (not node.name.startswith("_")):
                if ast.get_docstring(node) is None:
                    needs_fix = True
                    break
        if not needs_fix:
            continue
        m, f = add_docstrings_lossless(fp)
        total_fixed += f
    return total_fixed


def main() -> None:
    """入口函数"""
    parser = argparse.ArgumentParser(description="治理脚本质量合规检查 — 对照 SCRIPT-QUALITY-001 38 项条款")
    parser.add_argument("--warn-only", action="store_true", help="警告模式：发现违规不阻塞（exit 0）")
    parser.add_argument("--fix", action="store_true", help="自动修复 D-C-02 违规（使用 LibCST 无损添加 docstring）")
    parser.add_argument(
        "--scripts-dir", type=str, default=str(REPO_ROOT / "scripts" / "governance"), help="治理脚本目录路径"
    )
    args = parser.parse_args()
    scan_dir = Path(args.scripts_dir).resolve()
    if not scan_dir.exists():
        print(f"[ERROR] 脚本目录不存在: {scan_dir}", file=sys.stderr)
        sys.exit(EXIT_ERROR)
    if args.fix:
        print("[FIX] 使用 LibCST 无损修复 D-C-02 违规...\n")
        fixed = _fix_dc02(scan_dir)
        print(f"\n[FIX] 修复完成：添加了 {fixed} 个函数 docstring\n")
    results, total = scan_scripts(scan_dir, warn_only=args.warn_only)
    print(f"\n[SCRIPT-QUALITY] 扫描 {total} 个治理脚本，{len(CLAUSE_CHECKS)} 项条款：\n")
    total_failures = 0
    for result in results:
        if result.failures:
            total_failures += len(result.failures)
            print(f"  [{result.clause_id}] {result.description} — {len(result.failures)} 违规：")
            for f in result.failures:
                print(f"    - {f}")
        else:
            print(f"  [{result.clause_id}] {result.description} — ✅ 通过")
    print(f"\n  总计: {total} 脚本, {total_failures} 项违规\n")
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if total_failures > 0 else 0)


if __name__ == "__main__":
    main()
