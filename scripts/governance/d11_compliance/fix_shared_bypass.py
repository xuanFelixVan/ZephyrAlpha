"""
fix_shared_bypass.py — D-D-07 自动修复工具（validate_script_quality.py 的 --fix 搭档）

对标：AGENTS.md §6.5（脚本自创入库强制约定）
      SCRIPT-QUALITY-001 D-D-07（禁止绕过 _shared 工具）
      ESLint --fix 模式（检测 + 自动修复）

功能：
  默认模式：扫描 scripts/governance/ 下所有 .py 文件，报告本地重定义 _shared API 的违规
  --fix 模式：自动修复——删除本地定义 + 添加 SSoT import + 替换调用点

修复规则：
  ┌─────────────────┬──────────────────────────────────────────────┐
  │ 本地定义         │ 替换为                                       │
  ├─────────────────┼──────────────────────────────────────────────┤
  │ REPO_ROOT       │ from _shared.constants import REPO_ROOT      │
  │ _REPO_ROOT      │ from _shared.constants import REPO_ROOT      │
  │ EXCLUDE_DIRS    │ from _shared.constants import EXCLUDE_DIRS   │
  │ SRC_DIR         │ from _shared.constants import SRC_DIR        │
  │ CONFIG_DIR      │ from _shared.constants import CONFIG_DIR     │
  │ SCRIPTS_DIR     │ from _shared.constants import SCRIPTS_DIR    │
  │ MANIFEST_PATH   │ from _shared.constants import MANIFEST_PATH  │
  │ SCAN_EXTENSIONS │ from _shared.constants import SCAN_EXTENSIONS_CODE │
  │ parse_frontmatter │ from _shared.frontmatter import parse_frontmatter │
  │ load_yaml       │ from _shared.yaml_utils import load_yaml     │
  │ ensure_utf8_stdout │ from _shared.encoding import ensure_utf8_stdout │
  └─────────────────┴──────────────────────────────────────────────┘

安全措施：
  - 修复前自动备份原文件为 .bak（--no-backup 可关闭）
  - 仅处理 _shared API 白名单中的符号，不碰未知符号
  - --dry-run 模式只报告不修改

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

import ast
import re
import shutil
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import REPO_ROOT, SCAN_EXTENSIONS_CODE, SCRIPTS_DIR
from _shared.encoding import ensure_utf8_stdout
from _shared.walk import iter_files

ensure_utf8_stdout()
import argparse

_EXCLUDE_NAMES = {"__init__.py"}
_SELF_REL = "scripts/governance/d11_compliance/fix_shared_bypass.py"
_SHARED_SYMBOL_MAP: dict[str, tuple[str, str]] = {
    "REPO_ROOT": ("_shared.constants", "REPO_ROOT"),
    "_REPO_ROOT": ("_shared.constants", "REPO_ROOT"),
    "EXCLUDE_DIRS": ("_shared.constants", "EXCLUDE_DIRS"),
    "SRC_DIR": ("_shared.constants", "SRC_DIR"),
    "CONFIG_DIR": ("_shared.constants", "CONFIG_DIR"),
    "SCRIPTS_DIR": ("_shared.constants", "SCRIPTS_DIR"),
    "MANIFEST_PATH": ("_shared.constants", "MANIFEST_PATH"),
    "SCAN_EXTENSIONS": ("_shared.constants", "SCAN_EXTENSIONS_CODE"),
    "_SCAN_EXTENSIONS": ("_shared.constants", "SCAN_EXTENSIONS_CODE"),
    "parse_frontmatter": ("_shared.frontmatter", "parse_frontmatter"),
    "parse_frontmatter_from_file": ("_shared.frontmatter", "parse_frontmatter_from_file"),
    "parse_yaml_header": ("_shared.frontmatter", "parse_yaml_header"),
    "load_yaml": ("_shared.yaml_utils", "load_yaml"),
    "ensure_utf8_stdout": ("_shared.encoding", "ensure_utf8_stdout"),
    "iter_files": ("_shared.walk", "iter_files"),
}

class FixResult:
    def __init__(self, filepath: Path) -> None:
        self.filepath = filepath
        self.violations: list[str] = []
        self.fixes: list[str] = []
        self.imports_added: list[str] = []
        self.lines_removed: list[int] = []

    @property
    def has_violations(self) -> bool:
        """判断是否存在违规"""
        return len(self.violations) > 0
        "判断是否存在违规."

    @property
    def has_fixes(self) -> bool:
        """判断是否存在修复"""
        return len(self.fixes) > 0
        "判断是否存在修复."

def _is_shared_file(filepath: Path) -> bool:
    rel = str(filepath).replace("\\", "/")
    return "_shared/" in rel

def _detect_violations(content: str, filepath: Path) -> list[tuple[str, str, str]]:
    """检测本地重定义 _shared API 的违规。

    Returns:
        list of (symbol_name, local_name, shared_module)
    """
    if _is_shared_file(filepath):
        return []
    try:
        tree = ast.parse(content, filename=str(filepath))
    except SyntaxError:
        return []
    imported_from_shared: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module.startswith("_shared"):
                for a in node.names:
                    imported_from_shared.add(a.name)
                    if a.asname:
                        imported_from_shared.add(a.asname)
    local_defs: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            local_defs.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    local_defs.add(target.id)
    violations = []
    overlaps = (local_defs & set(_SHARED_SYMBOL_MAP.keys())) - imported_from_shared
    for local_name in sorted(overlaps):
        module, canonical = _SHARED_SYMBOL_MAP[local_name]
        violations.append((local_name, canonical, module))
    return violations

def _remove_local_definition(content: str, symbol_name: str) -> tuple[str, list[int]]:
    """从源码中删除本地定义（函数或常量赋值）。

    Returns:
        (modified_content, removed_line_numbers)
    """
    lines = content.split("\n")
    removed: list[int] = []
    result_lines: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if re.match(f"^{re.escape(symbol_name)}\\s*=", stripped):
            removed.append(i + 1)
            i += 1
            continue
        if re.match(f"^{re.escape(symbol_name)}\\s*=\\s*\\w+$", stripped):
            removed.append(i + 1)
            i += 1
            continue
        func_match = re.match(f"^def\\s+{re.escape(symbol_name)}\\s*\\(", stripped)
        method_match = re.match(f"^\\s+def\\s+{re.escape(symbol_name)}\\s*\\(", line)
        if func_match or method_match:
            removed.append(i + 1)
            indent = len(line) - len(line.lstrip())
            i += 1
            while i < len(lines):
                next_line = lines[i]
                next_stripped = next_line.strip()
                if not next_stripped:
                    if i + 1 < len(lines) and (not lines[i + 1].strip()):
                        removed.append(i + 1)
                        i += 1
                        break
                    removed.append(i + 1)
                    i += 1
                    continue
                next_indent = len(next_line) - len(next_line.lstrip())
                if next_indent <= indent and next_stripped:
                    break
                removed.append(i + 1)
                i += 1
            continue
        result_lines.append(line)
        i += 1
    return ("\n".join(result_lines), removed)

def _add_import(content: str, module: str, symbol: str) -> str:
    """在源码中添加 from module import symbol 语句。"""
    import_line = f"from {module} import {symbol}"
    existing_imports = [l for l in content.split("\n") if l.startswith("from _shared.")]
    for existing in existing_imports:
        if import_line in existing or existing.startswith(import_line.rstrip()):
            return content
    lines = content.split("\n")
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.startswith("from _shared."):
            insert_idx = i + 1
        elif line.startswith("from ") and insert_idx > 0:
            break
    if insert_idx == 0:
        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                insert_idx = i + 1
    lines.insert(insert_idx, import_line)
    return "\n".join(lines)

def _replace_calls(content: str, local_name: str, canonical_name: str) -> str:
    """替换调用点：local_name → canonical_name。"""
    if local_name == canonical_name:
        return content
    content = content.replace(f"self.{local_name}()", f"{canonical_name}()")
    content = content.replace(f"{local_name}(", f"{canonical_name}(")
    content = content.replace(f"{local_name} =", f"{canonical_name} =")
    content = content.replace(f"= {local_name}", f"= {canonical_name}")
    content = re.sub(f"\\b{re.escape(local_name)}\\b", canonical_name, content)
    return content

def fix_file(filepath: Path, dry_run: bool = False, backup: bool = True) -> FixResult:
    """扫描并修复单个文件。

    Args:
        filepath: 目标文件路径
        dry_run: 只报告不修改
        backup: 修复前创建 .bak 备份

    Returns:
        FixResult 包含违规和修复信息
    """
    result = FixResult(filepath)
    try:
        content = filepath.read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError) as e:
        result.violations.append(f"无法读取: {e}")
        return result
    violations = _detect_violations(content, filepath)
    if not violations:
        return result
    for local_name, canonical, module in violations:
        result.violations.append(f"本地重定义: {local_name} → 应为 from {module} import {canonical}")
    if dry_run:
        return result
    modified = content
    for local_name, canonical, module in violations:
        modified, removed = _remove_local_definition(modified, local_name)
        if removed:
            result.lines_removed.extend(removed)
            result.fixes.append(f"删除 {local_name} 本地定义（行 {removed}）")
        modified = _add_import(modified, module, canonical)
        result.imports_added.append(f"from {module} import {canonical}")
        result.fixes.append(f"添加 from {module} import {canonical}")
        modified = _replace_calls(modified, local_name, canonical)
        if local_name != canonical:
            result.fixes.append(f"替换 {local_name} → {canonical}")
    if modified != content:
        if backup:
            shutil.copy2(filepath, str(filepath) + ".bak")
        filepath.write_text(modified, encoding="utf-8")
    return result

def scan_and_fix(scan_dir: Path, fix: bool = False, dry_run: bool = False, backup: bool = True) -> tuple[int, int, int]:
    """扫描目录下所有 .py 文件并报告/修复违规。

    Returns:
        (total_files, violation_count, fix_count)
    """
    total = 0
    violations = 0
    fixes = 0
    py_files = iter_files(scan_dir, SCAN_EXTENSIONS_CODE)
    py_files = [f for f in py_files if f.name not in _EXCLUDE_NAMES and str(f).replace("\\", "/") != _SELF_REL]
    for filepath in sorted(py_files):
        total += 1
        result = fix_file(filepath, dry_run=not fix and (not dry_run), backup=backup)
        if result.has_violations:
            violations += 1
            rel = filepath.relative_to(REPO_ROOT)
            for v in result.violations:
                print(f"  {rel}: {v}")
            if result.has_fixes:
                fixes += 1
                for fx in result.fixes:
                    print(f"    FIX: {fx}")
    return (total, violations, fixes)

def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="D-D-07 自动修复：检测并修复本地重定义 _shared API 的违规")
    parser.add_argument("--fix", action="store_true", help="执行修复（默认只检测不修复）")
    parser.add_argument("--dry-run", action="store_true", help="模拟修复，不写入文件")
    parser.add_argument("--no-backup", action="store_true", help="修复时不创建 .bak 备份")
    parser.add_argument("--scan-dir", type=Path, default=SCRIPTS_DIR, help="扫描目录（默认 scripts/governance/）")
    parser.add_argument("--warn-only", action="store_true", help="非阻断模式（exit 0 even with findings）")
    args = parser.parse_args()
    print("=" * 72)
    print("D-D-07 fix_shared_bypass: _shared API 本地重定义自动修复")
    print(f'模式: {('FIX' if args.fix else 'DRY-RUN' if args.dry_run else 'SCAN-ONLY')}')
    print(f"扫描目录: {args.scan_dir}")
    print("=" * 72)
    total, violation_count, fix_count = scan_and_fix(
        args.scan_dir, fix=args.fix, dry_run=args.dry_run, backup=not args.no_backup
    )
    print()
    print(f"扫描文件: {total}")
    print(f"违规文件: {violation_count}")
    if args.fix or args.dry_run:
        print(f"修复文件: {fix_count}")
    if violation_count > 0 and (not args.warn_only) and (not args.fix):
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
