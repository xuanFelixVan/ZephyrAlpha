# [BLUEPRINT] MOD-INF-005 | scripts/governance/rewrite_imports.py | §
# [MODULE] scripts.governance.rewrite_imports
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
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
"""rewrite_imports.py — 批量重写 Python import 路径（AST-based）

当文件从 old_path 移到 new_path 时，扫描所有 .py 文件的 import 语句，
将引用旧路径的 import 更新为新路径。

策略：
  - 用 ast 解析找到 Import/ImportFrom 节点（准确，不误匹配字符串/注释）
  - 用行号定位 + 正则替换修改（保留原始格式）
  - 支持 dry-run 模式预览改动
  - 支持 YAML 映射文件批量重写

支持的 import 模式：
  1. from zephyr.autonomy_core.xxx import yyy      → from zephyr.autonomy_core.<sub>.xxx import yyy
  2. import zephyr.autonomy_core.xxx               → import zephyr.autonomy_core.<sub>.xxx
  3. from zephyr.autonomy_core import xxx          → from zephyr.autonomy_core.<sub> import xxx

用法：
    # 从 YAML 映射文件重写（dry-run）
    python scripts/governance/rewrite_imports.py --mapping move_map.yaml --dry-run
    # 实际写入
    python scripts/governance/rewrite_imports.py --mapping move_map.yaml --apply
    # 单文件移动
    python scripts/governance/rewrite_imports.py --old src/zephyr/autonomy_core/xxx.py --new src/zephyr/autonomy_core/context/xxx.py --dry-run
    # 指定扫描目录
    python scripts/governance/rewrite_imports.py --mapping move_map.yaml --dry-run --scan-dirs src tests

YAML 映射格式：
    move_map:
      - old: src/zephyr/autonomy_core/atomic_injector.py
        new: src/zephyr/autonomy_core/context/atomic_injector.py
      - old: src/zephyr/autonomy_core/budget_forecaster.py
        new: src/zephyr/governance/capacity/budget_forecaster.py

返回码：
    0 = CLEAN（无 import 需要重写）
    1 = 重写完成（有 import 被重写）
    2 = 错误（映射文件解析失败等）
"""

from __future__ import annotations

__manifest__ = """
args: ["--mapping", "--old", "--new", "--dry-run", "--apply", "--scan-dirs"]
description: rewrite_imports.py — 批量重写 Python import 路径（AST-based）
dimensions:
- D1
- D5
priority: P2
timeout_seconds: 120
warn_only: false
"""

import argparse
import ast
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_PASS, REPO_ROOT  # noqa: E402
from _shared.file_utils import atomic_write  # noqa: E402

PROJECT_ROOT = REPO_ROOT
EXCLUDE_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".git", ".venv", ".aidrafts"}


# ────────────────────────── 数据结构 ──────────────────────────


@dataclass
class MoveEntry:
    """单个文件的移动映射"""

    old_path: str  # 相对路径，如 src/zephyr/autonomy_core/xxx.py
    new_path: str


@dataclass
class ImportRewrite:
    """单个 import 的重写指令"""

    line: int  # 1-based 行号
    old_text: str  # 旧模块路径
    new_text: str  # 新模块路径


@dataclass
class RewriteResult:
    """单文件的重写结果"""

    file_path: Path
    rewrites: list[ImportRewrite] = field(default_factory=list)
    applied: bool = False


# ────────────────────────── 核心逻辑 ──────────────────────────


def path_to_module(file_path: str) -> str:
    """文件路径转模块路径。

    src/zephyr/autonomy_core/xxx.py → zephyr.autonomy_core.xxx
    src/zephyr/autonomy_core/context/xxx.py → zephyr.autonomy_core.context.xxx
    """
    p = file_path.replace("\\", "/")
    if p.startswith("src/"):
        p = p[4:]
    if p.endswith(".py"):
        p = p[:-3]
    if p.endswith("/__init__"):
        p = p[:-9]
    return p.replace("/", ".")


def build_module_mapping(moves: list[MoveEntry]) -> dict[str, str]:
    """构建旧→新模块路径映射。"""
    mapping: dict[str, str] = {}
    for m in moves:
        old_mod = path_to_module(m.old_path)
        new_mod = path_to_module(m.new_path)
        if old_mod != new_mod:
            mapping[old_mod] = new_mod
    return mapping


def match_module(module: str, mapping: dict[str, str]) -> str | None:
    """匹配模块路径。支持完全匹配。"""
    return mapping.get(module)


def find_import_rewrites(source: str, mapping: dict[str, str]) -> list[ImportRewrite]:
    """用 ast 找到需要重写的 import 节点。

    处理三种 import 模式：
    1. from zephyr.autonomy_core.xxx import yyy  → 替换 module
    2. import zephyr.autonomy_core.xxx           → 替换 name
    3. from zephyr.autonomy_core import xxx       → 检查 module+"."+name 是否在映射中
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    rewrites: list[ImportRewrite] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            # import zephyr.autonomy_core.xxx [as yyy]
            for alias in node.names:
                new_name = match_module(alias.name, mapping)
                if new_name:
                    rewrites.append(
                        ImportRewrite(line=node.lineno, old_text=alias.name, new_text=new_name)
                    )

        elif isinstance(node, ast.ImportFrom):
            if not node.module:
                continue
            # from zephyr.autonomy_core.xxx import yyy
            new_module = match_module(node.module, mapping)
            if new_module:
                rewrites.append(
                    ImportRewrite(line=node.lineno, old_text=node.module, new_text=new_module)
                )
            else:
                # from zephyr.autonomy_core import xxx
                # 检查 module + "." + name 是否在映射中
                for alias in node.names:
                    combined = f"{node.module}.{alias.name}"
                    new_full = match_module(combined, mapping)
                    if new_full:
                        # 新的 module 路径 = new_full 去掉最后一层
                        new_mod = new_full.rsplit(".", 1)[0]
                        rewrites.append(
                            ImportRewrite(
                                line=node.lineno, old_text=node.module, new_text=new_mod
                            )
                        )
                        break  # 一行只处理一次 module 替换

    return rewrites


def apply_rewrites_to_source(source: str, rewrites: list[ImportRewrite]) -> str:
    """应用重写到源代码（保留原始格式）。

    用正则确保不误匹配部分路径（如 xxx 不会匹配 xxx_helper）。
    """
    if not rewrites:
        return source

    lines = source.split("\n")
    # 按行分组，同一行可能有多个重写
    line_rewrites: dict[int, list[ImportRewrite]] = {}
    for rw in rewrites:
        line_rewrites.setdefault(rw.line, []).append(rw)

    for line_no, rws in line_rewrites.items():
        idx = line_no - 1  # 0-based
        if idx >= len(lines):
            continue
        old_line = lines[idx]
        new_line = old_line
        for rw in rws:
            # (?![\w]) 确保模块路径后面不是字母/数字/下划线
            # 避免 zephyr.autonomy_core.xxx 匹配 zephyr.autonomy_core.xxx_helper
            pattern = re.escape(rw.old_text) + r"(?![\w])"
            new_line = re.sub(pattern, rw.new_text, new_line, count=1)
        lines[idx] = new_line

    return "\n".join(lines)


def scan_file(py_file: Path, mapping: dict[str, str]) -> list[ImportRewrite]:
    """扫描单个文件，返回需要重写的 import 列表。"""
    try:
        source = py_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    return find_import_rewrites(source, mapping)


def scan_and_rewrite(
    mapping: dict[str, str],
    scan_dirs: list[Path],
    apply: bool = False,
) -> list[RewriteResult]:
    """扫描所有 .py 文件并重写 import。

    Args:
        mapping: 旧→新模块路径映射
        scan_dirs: 要扫描的目录列表
        apply: True=实际写入文件，False=只返回结果

    Returns:
        所有有重写的文件列表
    """
    if not mapping:
        return []

    results: list[RewriteResult] = []

    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for py_file in sorted(scan_dir.rglob("*.py")):
            # 排除缓存/虚拟环境等
            if any(part in EXCLUDE_PARTS for part in py_file.parts):
                continue

            rewrites = scan_file(py_file, mapping)
            if not rewrites:
                continue

            result = RewriteResult(file_path=py_file, rewrites=rewrites)

            if apply:
                try:
                    source = py_file.read_text(encoding="utf-8")
                    new_source = apply_rewrites_to_source(source, rewrites)
                    if new_source != source:
                        atomic_write(py_file, new_source)
                        result.applied = True
                except Exception as e:
                    print(f"  ERROR writing {py_file}: {e}", file=sys.stderr)

            results.append(result)

    return results


# ────────────────────────── 映射加载 ──────────────────────────


def load_mapping_from_yaml(yaml_path: Path) -> list[MoveEntry]:
    """从 YAML 文件加载移动映射。"""
    import yaml

    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    if not data or "move_map" not in data:
        print(f"ERROR: YAML 文件 {yaml_path} 缺少 move_map 键", file=sys.stderr)
        return []

    moves: list[MoveEntry] = []
    for entry in data["move_map"]:
        old = entry.get("old", "")
        new = entry.get("new", "")
        if old and new:
            moves.append(MoveEntry(old_path=old, new_path=new))
    return moves


def load_mapping_from_args(old_path: str, new_path: str) -> list[MoveEntry]:
    """从命令行参数构建单文件移动映射。"""
    return [MoveEntry(old_path=old_path, new_path=new_path)]


# ────────────────────────── 报告输出 ──────────────────────────


def print_dry_run_report(results: list[RewriteResult]) -> None:
    """打印 dry-run 报告（预览改动）。"""
    total_rewrites = sum(len(r.rewrites) for r in results)
    print(f"\n{'=' * 70}")
    print(f"DRY-RUN: {total_rewrites} import(s) would be rewritten in {len(results)} file(s)")
    print(f"{'=' * 70}\n")

    for result in sorted(results, key=lambda r: str(r.file_path)):
        rel = result.file_path.relative_to(PROJECT_ROOT) if result.file_path.is_absolute() else result.file_path
        print(f"  {rel}:")
        for rw in result.rewrites:
            print(f"    L{rw.line}: {rw.old_text} → {rw.new_text}")

    print(f"\n共 {total_rewrites} 处重写。使用 --apply 实际写入。")


def print_apply_report(results: list[RewriteResult]) -> None:
    """打印实际写入报告。"""
    total_rewrites = sum(len(r.rewrites) for r in results)
    applied_count = sum(1 for r in results if r.applied)
    print(f"\n{'=' * 70}")
    print(f"APPLIED: {total_rewrites} import(s) rewritten in {applied_count} file(s)")
    print(f"{'=' * 70}\n")

    for result in sorted(results, key=lambda r: str(r.file_path)):
        rel = result.file_path.relative_to(PROJECT_ROOT) if result.file_path.is_absolute() else result.file_path
        status = "OK" if result.applied else "SKIP"
        print(f"  [{status}] {rel}: {len(result.rewrites)} rewrite(s)")


# ────────────────────────── CLI ──────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(
        description="批量重写 Python import 路径（AST-based）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--mapping", type=Path, help="YAML 映射文件路径")
    group.add_argument("--old", type=str, help="旧文件路径（单文件模式）")
    parser.add_argument("--new", type=str, help="新文件路径（与 --old 配合）")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="只预览，不写入")
    mode.add_argument("--apply", action="store_true", help="实际写入文件")
    parser.add_argument(
        "--scan-dirs",
        nargs="+",
        type=Path,
        default=[PROJECT_ROOT / "src", PROJECT_ROOT / "tests"],
        help="要扫描的目录列表（默认: src tests）",
    )
    args = parser.parse_args()

    # 加载映射
    if args.mapping:
        if not args.mapping.exists():
            print(f"ERROR: 映射文件不存在: {args.mapping}", file=sys.stderr)
            return 2
        moves = load_mapping_from_yaml(args.mapping)
    else:
        if not args.new:
            print("ERROR: --old 需要配合 --new", file=sys.stderr)
            return 2
        moves = load_mapping_from_args(args.old, args.new)

    if not moves:
        print("ERROR: 未加载到任何移动映射", file=sys.stderr)
        return 2

    # 构建模块映射
    mapping = build_module_mapping(moves)
    if not mapping:
        print("INFO: 无 import 需要重写（所有文件路径未变化或映射为空）")
        return EXIT_PASS

    print(f"模块映射 ({len(mapping)} 条):")
    for old, new in sorted(mapping.items()):
        print(f"  {old} → {new}")

    # 扫描并重写
    results = scan_and_rewrite(mapping, args.scan_dirs, apply=args.apply)

    if not results:
        print("\nINFO: 未找到需要重写的 import。")
        return EXIT_PASS

    # 输出报告
    if args.apply:
        print_apply_report(results)
    else:
        print_dry_run_report(results)

    return 1 if results else EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
