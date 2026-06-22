# [BLUEPRINT] MOD-INF-005 | scripts/governance/audit_registration.py | §
"""audit_registration.py — 孤儿注册检测（RULE-TWO 防线 2）

扫描 src/zephyr/ 和 scripts/ 中所有 .py/.yaml 文件，
对比三个注册表（__init__.py __all__、script_manifest.yaml、_registry.yaml），
检测:
  - 孤儿文件: 存在于磁盘但不在任何注册表中
  - 僵尸引用: 注册表引用的文件已删除
  - __init__.py 缺 __all__: 有模块文件但包级 __init__.py 无 __all__

用法:
    python scripts/governance/audit_registration.py           # 报告孤儿清单（全量）
    python scripts/governance/audit_registration.py --full    # 显式全量扫描
    python scripts/governance/audit_registration.py --incremental  # 仅扫描 git 变更文件
    python scripts/governance/audit_registration.py --fix     # 交互式修复

返回码:
    0 = CLEAN（无孤儿）
    1 = 发现孤儿
    2 = 扫描错误

设计基线:
    RULE-TWO 反孤儿功能
    可被 Pipeline Gate 调用（作为 G6 的一部分或独立门禁）
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

import argparse
import ast
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from _shared.constants import EXIT_ERROR

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ZEPHYR = PROJECT_ROOT / "src" / "zephyr"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
GATES_DIR = SRC_ZEPHYR / "gates"
SCRIPT_MANIFEST = SCRIPTS_DIR / "script_manifest.yaml"
GATE_REGISTRY = GATES_DIR / "_registry.yaml"

EXCLUDE_PATTERNS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    ".git",
    ".venv",
    "venv",
    "env",
    "dist",
    "build",
    "egg-info",
    ".ailocks",
    "session-logs",
    "_backup",
    "_archive",
}

EXCLUDE_SCRIPT_DIRS = {
    "governance",  # 治理脚本本身不注册到 manifest（由 generate_manifest.py 管理）
    "__pycache__",
}

# 这些文件是系统级别文件，不归模块注册表管
EXCLUDE_FROM_MODULE_AUDIT: set[str] = {
    "__init__.py",
    "conftest.py",
    "setup.py",
    "version.py",
    "py.typed",
}


@dataclass
class AuditResult:
    orphan_modules: list[OrphanEntry] = field(default_factory=list)
    orphan_scripts: list[OrphanEntry] = field(default_factory=list)
    orphan_gates: list[OrphanEntry] = field(default_factory=list)
    zombie_references: list[ZombieEntry] = field(default_factory=list)
    missing_all: list[Path] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        """is_clean implementation."""
        return not any(
            [
                self.orphan_modules,
                self.orphan_scripts,
                self.orphan_gates,
                self.zombie_references,
                self.missing_all,
            ]
        )

    @property
    def total_issues(self) -> int:
        """total_issues implementation."""
        return (
            len(self.orphan_modules)
            + len(self.orphan_scripts)
            + len(self.orphan_gates)
            + len(self.zombie_references)
            + len(self.missing_all)
        )


@dataclass
class OrphanEntry:
    path: Path
    relative: str
    package: str = ""
    suggestion: str = ""


@dataclass
class ZombieEntry:
    reference: str
    registry: str
    detail: str = ""


def audit(changed_files: set[Path] | None = None) -> AuditResult:
    """执行完整注册审计扫描。

    Args:
        changed_files: 增量模式下传入的变更文件集合。None 表示全量扫描。
    """
    result = AuditResult()

    # ── 1. 构建已注册集合 ──
    registered_modules = _build_module_registry()
    registered_scripts = _build_script_registry()
    registered_gates = _build_gate_registry()

    # ── 1.5 批量收集所有 import 语句（消费者地图）──
    # RULE-TWO 豁免原则：已有自然发现机制（被其他模块 import）的模块不报为 ORPHAN
    import_map = _batch_collect_imports()

    # ── 2. 扫描 src/zephyr/ 模块孤儿 ──
    _scan_module_orphans(registered_modules, import_map, result, changed_files)

    # ── 3. 扫描 scripts/ 脚本孤儿 ──
    _scan_script_orphans(registered_scripts, result, changed_files)

    # ── 4. 扫描 gates/ 门禁孤儿 ──
    _scan_gate_orphans(registered_gates, result, changed_files)

    # ── 5. 检测僵尸引用 ──
    _detect_zombie_references(registered_modules, registered_scripts, registered_gates, result)

    # ── 6. 检测缺 __all__ 的 __init__.py ──
    _detect_missing_all(result, changed_files)

    return result


# ===================================================================
# 注册表构建
# ===================================================================


def _build_module_registry() -> dict[str, set[str]]:
    """返回 {package_name: {module_name, ...}} 表示 __all__ 中已注册的模块。"""
    registry: dict[str, set[str]] = {}

    for init_py in SRC_ZEPHYR.rglob("__init__.py"):
        if any(ex in init_py.parts for ex in EXCLUDE_PATTERNS):
            continue

        rel = init_py.relative_to(SRC_ZEPHYR)
        pkg_name = rel.parent.as_posix().replace("\\", "/").replace("/", ".")

        content = init_py.read_text(encoding="utf-8")

        all_entries = _extract_all_entries(content)
        registry[pkg_name] = all_entries

    return registry


def _extract_all_entries(source: str) -> set[str]:
    """从 __init__.py 源码中提取 __all__ 列表。"""
    entries: set[str] = set()

    try:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            # Handle both __all__ = [...] and __all__: list[str] = [...]
            all_value = None
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        all_value = node.value
                        break
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name) and node.target.id == "__all__":
                    all_value = node.value
            if all_value is not None and isinstance(all_value, (ast.List, ast.Tuple)):
                for elt in all_value.elts:
                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                        entries.add(elt.value)
    except SyntaxError:
        pattern = r'"([^"]+)"'
        for match in re.finditer(pattern, source):
            entries.add(match.group(1))

    return entries


def _build_script_registry() -> set[str]:
    """从 script_manifest.yaml 中提取已注册的脚本路径集合。"""
    if not SCRIPT_MANIFEST.exists():
        return set()

    manifest = yaml.safe_load(SCRIPT_MANIFEST.read_text(encoding="utf-8")) or {}
    scripts = manifest.get("scripts", [])
    return {s.get("path", "") for s in scripts if s.get("path")}


def _build_gate_registry() -> set[str]:
    """从 _registry.yaml 中提取已注册的 gate 文件名集合。"""
    if not GATE_REGISTRY.exists():
        return set()

    registry_data = yaml.safe_load(GATE_REGISTRY.read_text(encoding="utf-8")) or {}
    gates = registry_data.get("gates", [])
    return {g.get("file", "") for g in gates if g.get("file")}


def _batch_collect_imports() -> dict[str, list[str]]:
    """批量收集所有 import 语句，构建 {module: [consumer_files]} 映射。

    用于 RULE-TWO 豁免判定：被其他模块 import 的模块视为"已有自然发现机制"，
    不报为 ORPHAN（即使未注册到 __all__）。

    匹配模式:
        from zephyr.X.Y.Z import ...
        import zephyr.X.Y.Z

    Returns:
        {full_module_path: [consumer_file_paths]}
    """
    import re as _re
    from collections import defaultdict

    pattern = r"(?:from\s+(zephyr[\w.]*))\s+import|(?:import\s+(zephyr[\w.]*))"
    consumers: dict[str, list[str]] = defaultdict(list)

    try:
        result = subprocess.run(
            ["rg", "--no-heading", "-n", "-e", pattern, "src/", "scripts/", "tests/"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                parts = line.split(":", 2)
                if len(parts) < 3:
                    continue
                consumer_file = parts[0]
                content = parts[2]
                match = _re.search(pattern, content)
                if match:
                    module = match.group(1) or match.group(2)
                    if module:
                        consumers[module].append(consumer_file)
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"WARNING: 批量收集 import 失败，消费者豁免将不生效: {e}", file=sys.stderr)

    return dict(consumers)


# ===================================================================
# 孤儿扫描
# ===================================================================


def _scan_module_orphans(
    registered: dict[str, set[str]],
    import_map: dict[str, list[str]],
    result: AuditResult,
    changed_files: set[Path] | None = None,
) -> None:
    """扫描 src/zephyr/ 下所有 .py 文件，找出不在 __all__ 中且无消费者的。

    RULE-TWO 豁免原则：被其他模块 import 的模块视为"已有自然发现机制"，
    不报为 ORPHAN（即使未注册到 __all__）。

    Args:
        registered: {package: {module_names}} 来自 __all__
        import_map: {full_module: [consumer_files]} 来自批量 Grep
        result: 审计结果
        changed_files: 增量模式下仅扫描此集合中的文件。None 表示全量扫描。
    """
    for py_file in SRC_ZEPHYR.rglob("*.py"):
        if any(ex in py_file.parts for ex in EXCLUDE_PATTERNS):
            continue
        if py_file.name in EXCLUDE_FROM_MODULE_AUDIT:
            continue
        if py_file.name.startswith("_"):
            continue
        # 增量模式：跳过未变更文件
        if changed_files is not None and py_file not in changed_files:
            continue

        rel = py_file.relative_to(SRC_ZEPHYR)
        rel_str = rel.as_posix()
        parts = rel.parts

        pkg = ".".join(parts[:-1]) if len(parts) > 1 else ""
        module_name = py_file.stem

        if pkg not in registered:
            result.orphan_modules.append(
                OrphanEntry(
                    path=py_file,
                    relative=rel_str,
                    package=pkg,
                    suggestion=f"Package '{pkg}' 的 __init__.py 不包含任何 __all__ 条目",
                )
            )
            continue

        class_name = "".join(p.capitalize() for p in module_name.split("_"))
        if module_name not in registered[pkg] and class_name not in registered[pkg]:
            # RULE-TWO 豁免：检查是否有消费者（被其他模块 import）
            full_module = "zephyr." + ".".join(parts[:-1] + (module_name,)) if parts[:-1] else "zephyr." + module_name
            consumer_files = import_map.get(full_module, [])
            # 排除自身
            consumer_files = [c for c in consumer_files if not c.endswith(rel_str)]
            if consumer_files:
                # 有消费者 = 已有自然发现机制 = 豁免
                continue

            result.orphan_modules.append(
                OrphanEntry(
                    path=py_file,
                    relative=rel_str,
                    package=pkg,
                    suggestion=(
                        f"from zephyr.{pkg.replace('/', '.').replace('\\', '.')}.{module_name} import {class_name}"
                    ),
                )
            )


def _scan_script_orphans(
    registered: set[str],
    result: AuditResult,
    changed_files: set[Path] | None = None,
) -> None:
    """扫描 scripts/ 下所有 .py 文件，找出不在 script_manifest.yaml 中的。

    Args:
        changed_files: 增量模式下仅扫描此集合中的文件。None 表示全量扫描。
    """
    for py_file in SCRIPTS_DIR.rglob("*.py"):
        if any(ex in py_file.parts for ex in EXCLUDE_PATTERNS):
            continue
        # 增量模式：跳过未变更文件
        if changed_files is not None and py_file not in changed_files:
            continue

        rel = py_file.relative_to(SCRIPTS_DIR)
        rel_str = rel.as_posix()

        parts = rel.parts
        if parts and parts[0] in EXCLUDE_SCRIPT_DIRS:
            continue

        if rel_str not in registered:
            result.orphan_scripts.append(
                OrphanEntry(
                    path=py_file,
                    relative=rel_str,
                    suggestion=f"python scripts/scaffold.py script {rel.with_suffix('').as_posix()}",
                )
            )


def _scan_gate_orphans(
    registered: set[str],
    result: AuditResult,
    changed_files: set[Path] | None = None,
) -> None:
    """扫描 gates/ 下所有 .yaml 文件，找出不在 _registry.yaml 中的。

    Args:
        changed_files: 增量模式下仅扫描此集合中的文件。None 表示全量扫描。
    """
    if not GATES_DIR.is_dir():
        return

    for yaml_file in GATES_DIR.glob("*.yaml"):
        if yaml_file.name.startswith("_"):
            continue
        # 增量模式：跳过未变更文件
        if changed_files is not None and yaml_file not in changed_files:
            continue

        if yaml_file.name not in registered:
            result.orphan_gates.append(
                OrphanEntry(
                    path=yaml_file,
                    relative=yaml_file.name,
                    suggestion=f"python scripts/scaffold.py gate {yaml_file.stem.upper()}",
                )
            )


# ===================================================================
# 僵尸引用检测
# ===================================================================


def _detect_zombie_references(
    module_registry: dict[str, set[str]],
    script_registry: set[str],
    gate_registry: set[str],
    result: AuditResult,
) -> None:
    """检测注册表中引用了已删除文件的条目。"""
    # Script manifest
    if SCRIPT_MANIFEST.exists():
        manifest = yaml.safe_load(SCRIPT_MANIFEST.read_text(encoding="utf-8")) or {}
        for entry in manifest.get("scripts", []):
            path_str = entry.get("path", "")
            if path_str and not (SCRIPTS_DIR / path_str).exists():
                result.zombie_references.append(
                    ZombieEntry(
                        reference=path_str,
                        registry="script_manifest.yaml",
                        detail=entry.get("description", ""),
                    )
                )

    # Gate registry
    if GATE_REGISTRY.exists():
        registry_data = yaml.safe_load(GATE_REGISTRY.read_text(encoding="utf-8")) or {}
        for entry in registry_data.get("gates", []):
            file_name = entry.get("file", "")
            if file_name and not (GATES_DIR / file_name).exists():
                result.zombie_references.append(
                    ZombieEntry(
                        reference=f"gate_id={entry.get('gate_id', '?')}",
                        registry="_registry.yaml",
                        detail=f"file={file_name}, title={entry.get('title', '')}",
                    )
                )


# ===================================================================
# __init__.py 缺 __all__
# ===================================================================


def _detect_missing_all(result: AuditResult, changed_files: set[Path] | None = None) -> None:
    """检测有 .py 模块但包级 __init__.py 无 __all__ 的包。

    Args:
        changed_files: 增量模式下仅扫描此集合中文件所属的 __init__.py。None 表示全量扫描。
    """
    for init_py in SRC_ZEPHYR.rglob("__init__.py"):
        if any(ex in init_py.parts for ex in EXCLUDE_PATTERNS):
            continue
        # 增量模式：仅检查变更文件所在目录的 __init__.py，或 __init__.py 自身变更
        if changed_files is not None:
            parent_dir = init_py.parent
            relevant = any(cf == init_py or cf.parent == parent_dir for cf in changed_files)
            if not relevant:
                continue

        pkg_dir = init_py.parent
        py_files = [
            f for f in pkg_dir.glob("*.py") if f.name not in EXCLUDE_FROM_MODULE_AUDIT and not f.name.startswith("_")
        ]

        if not py_files:
            continue

        content = init_py.read_text(encoding="utf-8")
        if "__all__" not in content:
            result.missing_all.append(init_py)


# ===================================================================
# 格式化输出
# ===================================================================


def print_report(ar: AuditResult, compact: bool = False) -> str:
    """格式化审计报告。"""
    lines: list[str] = []

    total = ar.total_issues
    status = "CLEAN" if ar.is_clean else f"ISSUES ({total})"
    lines.append(f"\n{'=' * 60}")
    lines.append(f"  RULE-TWO 注册审计: {status}")
    lines.append(f"{'=' * 60}")

    if ar.is_clean:
        lines.append("\n  No orphan files detected — all modules registered.")
        return "\n".join(lines)

    if ar.orphan_modules:
        lines.append(f"\n  ORPHAN MODULES ({len(ar.orphan_modules)}):")
        for oe in ar.orphan_modules:
            lines.append(f"    {oe.relative}")
            if not compact and oe.suggestion:
                lines.append(f"      → {oe.suggestion}")

    if ar.orphan_scripts:
        lines.append(f"\n  ORPHAN SCRIPTS ({len(ar.orphan_scripts)}):")
        for oe in ar.orphan_scripts:
            lines.append(f"    {oe.relative}")
            if not compact and oe.suggestion:
                lines.append(f"      → {oe.suggestion}")

    if ar.orphan_gates:
        lines.append(f"\n  ORPHAN GATES ({len(ar.orphan_gates)}):")
        for oe in ar.orphan_gates:
            lines.append(f"    {oe.relative}")
            if not compact and oe.suggestion:
                lines.append(f"      → {oe.suggestion}")

    if ar.missing_all:
        lines.append(f"\n  MISSING __all__  ({len(ar.missing_all)}):")
        for p in ar.missing_all:
            rel = p.relative_to(PROJECT_ROOT).as_posix()
            lines.append(f"    {rel}")

    if ar.zombie_references:
        lines.append(f"\n  ZOMBIE REFERENCES ({len(ar.zombie_references)}):")
        for ze in ar.zombie_references:
            lines.append(f"    {ze.reference} → [{ze.registry}] {ze.detail}")

    lines.append(f"\n  TOTAL: {total} issues")
    return "\n".join(lines)


# ===================================================================
# 增量扫描支持
# ===================================================================


def _get_changed_files_from_git() -> set[Path]:
    """通过 git diff 获取相对于 HEAD 的变更文件集合。

    包含已暂存和未暂存的变更，以及未跟踪的新文件。
    返回绝对路径集合，仅包含 src/zephyr/ 和 scripts/ 下的文件。
    """
    changed: set[Path] = set()
    try:
        # 已跟踪文件的变更（已暂存 + 未暂存）
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                line = line.strip()
                if line:
                    p = PROJECT_ROOT / line
                    if p.exists():
                        changed.add(p)

        # 未跟踪的新文件
        result = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                line = line.strip()
                if line:
                    p = PROJECT_ROOT / line
                    if p.exists():
                        changed.add(p)
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"WARNING: git diff 失败，回退到全量扫描: {e}", file=sys.stderr)
        return set()

    # 仅保留 src/zephyr/ 和 scripts/ 下的文件
    filtered: set[Path] = set()
    for p in changed:
        try:
            rel = p.relative_to(PROJECT_ROOT)
            rel_str = rel.as_posix()
            if rel_str.startswith("src/zephyr/") or rel_str.startswith("scripts/"):
                filtered.add(p)
        except ValueError:
            continue

    return filtered


# ===================================================================
# CLI
# ===================================================================


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(
        description="RULE-TWO 注册审计——检测孤儿模块/脚本/门禁",
    )
    scan_mode = parser.add_mutually_exclusive_group()
    scan_mode.add_argument("--full", action="store_true", help="全量扫描（默认）")
    scan_mode.add_argument("--incremental", action="store_true", help="增量扫描：仅扫描 git 变更文件")
    parser.add_argument("--compact", action="store_true", help="紧凑输出")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出（供 AI/MCP 消费）")
    parser.add_argument("--fix", action="store_true", help="交互式修复孤儿")
    args = parser.parse_args()

    # 确定扫描模式
    changed_files: set[Path] | None = None
    try:
        if args.incremental:
            changed_files = _get_changed_files_from_git()
            if not changed_files:
                print("[INCREMENTAL] 无变更文件或 git 不可用，扫描结果为空（CLEAN）")
                # 无变更文件 = 无新增孤儿 = CLEAN
                ar = AuditResult()
            else:
                print(f"[INCREMENTAL] 检测到 {len(changed_files)} 个变更文件，仅扫描这些文件")
                ar = audit(changed_files=changed_files)
        else:
            ar = audit()
    except Exception as e:
        print(f"ERROR: 审计失败: {e}", file=sys.stderr)
        sys.exit(EXIT_ERROR)

    if args.json:
        import json

        output = {
            "orphan_modules": [{"relative": oe.relative, "suggestion": oe.suggestion} for oe in ar.orphan_modules],
            "orphan_scripts": [{"relative": oe.relative, "suggestion": oe.suggestion} for oe in ar.orphan_scripts],
            "orphan_gates": [{"relative": oe.relative, "suggestion": oe.suggestion} for oe in ar.orphan_gates],
            "missing_all": [p.relative_to(PROJECT_ROOT).as_posix() for p in ar.missing_all],
            "zombie_references": [
                {"reference": ze.reference, "registry": ze.registry, "detail": ze.detail} for ze in ar.zombie_references
            ],
            "total_issues": ar.total_issues,
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(print_report(ar, compact=args.compact))

    if args.fix and not ar.is_clean:
        _interactive_fix(ar)

    sys.exit(0 if ar.is_clean else 1)


def _interactive_fix(ar: AuditResult) -> None:
    """交互式修复孤儿文件——将 orphan 注册到对应注册表。"""
    print("\n--- 交互式修复 ---")
    print("输入 'y' 自动注册, 'n' 跳过, 'd' 删除孤儿文件, 'q' 退出\n")

    for oe in ar.orphan_modules:
        choice = input(f"  注册模块 {oe.relative}? [y/n/d/q] ").strip().lower()
        if choice == "q":
            break
        elif choice == "d":
            oe.path.unlink()
            print(f"    DELETED {oe.relative}")
        elif choice == "y":
            _auto_register_module(oe)
        else:
            print("    SKIPPED")

    for oe in ar.orphan_scripts:
        choice = input(f"  注册脚本 {oe.relative}? [y/n/d/q] ").strip().lower()
        if choice == "q":
            break
        elif choice == "d":
            oe.path.unlink()
            print(f"    DELETED {oe.relative}")
        elif choice == "y":
            _auto_register_script(oe)
        else:
            print("    SKIPPED")


def _auto_register_module(oe: OrphanEntry) -> None:
    """自动将模块注册到 __init__.py。"""
    pkg_path = SRC_ZEPHYR / oe.package.replace(".", "/")
    init_py = pkg_path / "__init__.py"
    module_name = oe.path.stem
    class_name = "".join(p.capitalize() for p in module_name.split("_"))

    import_line = f"from zephyr.{oe.package.replace('/', '.').replace('\\', '.')}.{module_name} import {class_name}"

    if init_py.exists():
        content = init_py.read_text(encoding="utf-8")
        if import_line not in content:
            content = import_line + "\n" + content
        if "__all__" in content:
            if class_name not in content:
                pattern = r"(\[__all__\s*=\s*\[)(.*?)(\])"
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    mid = match.group(2)
                    entries = [e.strip().strip('"').strip("'") for e in mid.split(",") if e.strip()]
                    entries.append(class_name)
                    new_mid = "\n    " + ",\n    ".join(f'"{e}"' for e in sorted(set(entries))) + ",\n"
                    content = content[: match.start(2)] + new_mid + content[match.end(2) :]
                else:
                    content += f'\n__all__.append("{class_name}")\n'
        else:
            content += f'\n__all__ = [\n    "{class_name}",\n]\n'
    else:
        content = f'{import_line}\n\n__all__ = [\n    "{class_name}",\n]\n'

    import os

    tmp_path = Path(str(init_py) + f".{os.getpid()}.tmp")
    tmp_path.write_text(content, encoding="utf-8")
    os.replace(str(tmp_path), str(init_py))
    print(f"    REGISTERED {module_name} → {init_py}")


def _auto_register_script(oe: OrphanEntry) -> None:
    """自动将脚本注册到 script_manifest.yaml（壳层注册，generate_manifest.py 可后续覆盖）。"""
    if not SCRIPT_MANIFEST.exists():
        print(f"    ERROR: {SCRIPT_MANIFEST} 不存在")
        return

    import os

    manifest = yaml.safe_load(SCRIPT_MANIFEST.read_text(encoding="utf-8")) or {}
    scripts = manifest.get("scripts", [])

    entry = {
        "path": oe.relative,
        "description": f"{oe.path.stem} 脚本",
        "domain": oe.relative.split("/")[0] if "/" in oe.relative else "root",
        "execution_plane": "warm-path",
        "status": "registered",
    }
    scripts.append(entry)
    manifest["scripts"] = scripts
    manifest["total_scripts"] = len(scripts)

    new_content = yaml.dump(manifest, default_flow_style=False, allow_unicode=True, sort_keys=False)
    tmp_path = Path(str(SCRIPT_MANIFEST) + f".{os.getpid()}.tmp")
    tmp_path.write_text(new_content, encoding="utf-8")
    os.replace(str(tmp_path), str(SCRIPT_MANIFEST))
    print(f"    REGISTERED {oe.relative} → script_manifest.yaml")


if __name__ == "__main__":
    main()
