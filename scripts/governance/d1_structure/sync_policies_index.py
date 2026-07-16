# [BLUEPRINT] MOD-INF-005 | scripts/governance/d1_structure/sync_policies_index.py | §
# [MODULE] scripts.governance.d1_structure.sync_policies_index
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d1_structure.__init__
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
"""sync_policies_index.py — 从磁盘实际扫描，自动同步 PS-IDX-001 §二 文件数量表格。



对标：AGENTS.md §6.11 索引-实际同步强制约定（PS-IDX-001 文件数表格不得漂移）
      每次在 01_policies_and_standards/ 下新增/删除文件后运行一次。

用法：
    python sync_policies_index.py              # 实际同步
    python sync_policies_index.py --check      # CI 模式：只检查漂移
"""

from __future__ import annotations

__manifest__ = """
args:
- --check
description: 从磁盘扫描同步 PS-IDX-001 §二 文件数量表格（AGENTS.md §6.11——防止手动维护数字漂移）
dimensions:
- D1
priority: P2
timeout_seconds: 10
warn_only: true
"""


import os
import re
import sys
from argparse import ArgumentParser
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, GOV_DOCS_DIR
from _shared.encoding import ensure_utf8_stdout
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT

ensure_utf8_stdout()

PS_IDX_PATH = GOV_DOCS_DIR / "index.md"

TABLE_START_MARKER = "<!-- TABLE-AUTO-START -->"
TABLE_END_MARKER = "<!-- TABLE-AUTO-END -->"

EXCLUDE_NAMES = {
    ".git",
    "__pycache__",
    ".obsidian",
    "index.md",
    "README.md",
    "drafts_zone",
    ".DS_Store",
    "Thumbs.db",
}

_SUBDIRS = [
    (
        "meta/",
        '元规则——定义"规则怎么写、怎么管"',
        "meta/index.md",
        "[_registry/catalogs/_index.yaml](_registry/catalogs/_index.yaml)",
    ),
    (
        "governance/",
        "声明式全局规则——8 个治理域",
        "governance/index.md",
        "[rule_catalog_registry.yaml](_registry/catalogs/rule_catalog_registry.yaml)",
    ),
    ("operational/", "过程式操作手册——3 个操作域", "operational/index.md", "同上"),
    ("domains/", "层域特定规则——4 个架构层", "domains/index.md", "同上"),
    ("_registry/", "注册表+契约——4 个子目录", "不需要（机器可读）", "自身即注册表"),
    (
        "templates/",
        "文档模板",
        "不需要（文件名自描述）",
        "[rule_catalog_registry.yaml](_registry/catalogs/rule_catalog_registry.yaml)",
    ),
]


def _count_files(root: Path) -> int:
    """_count_files implementation."""
    count = 0
    for entry in sorted(root.iterdir()):
        if entry.name in EXCLUDE_NAMES:
            continue
        if entry.name.startswith("."):
            continue
        if (
            entry.name.endswith(".md")
            or entry.name.endswith(".yaml")
            or entry.name.endswith(".yml")
            or entry.name.endswith(".json")
        ):
            count += 1
    return count


def _count_recursive(root: Path) -> int:
    """_count_recursive implementation."""
    total = 0
    for entry in sorted(root.rglob("*")):
        if entry.name in EXCLUDE_NAMES:
            continue
        if any(part.startswith(".") and part != "_registry" for part in entry.parts):
            continue
        if entry.is_file() and entry.suffix in (".md", ".yaml", ".yml", ".json"):
            total += 1
    return total


def _generate_table() -> list[str]:
    """_generate_table implementation."""
    lines = [TABLE_START_MARKER]
    lines.append("| 子目录 | 职责 | 管辖文件数 | 索引入口 | 注册表 |")
    lines.append("|--------|------|:---------:|---------|--------|")

    grand_total = 0
    for dir_name, duty, entry_point, registry in _SUBDIRS:
        full_path = GOV_DOCS_DIR / dir_name
        if dir_name == "_registry/":
            n = _count_recursive(full_path)
        else:
            n = _count_recursive(full_path)
        grand_total += n
        lines.append(f"| `{dir_name}` | {duty} | {n} | [{entry_point}]({entry_point}) | {registry} |")

    lines.append("")
    lines.append(
        f"> **合计**：6 个子目录，{grand_total} 个文件，全部注册在 [rule_catalog_registry.yaml](_registry/catalogs/rule_catalog_registry.yaml)（auto-generated，取代旧的 governance-rules-master-registry.yaml 和 master-document-inventory-registry.md）。"
    )
    lines.append(TABLE_END_MARKER)
    return lines


def _find_table_range(content: str) -> tuple[int, int] | None:
    """Find the old table block: starts with '| 子目录' and ends with 'master-document-inventory-registry.md）。'"""
    start = content.find("| 子目录 ")
    if start == -1:
        return None

    end_pattern = re.compile(
        r"master-document-inventory\.yaml）\.\s*$",
        re.MULTILINE,
    )
    end_match = end_pattern.search(content, pos=start)
    if not end_match:
        return None
    end = end_match.end()

    prev_nl = content.rfind("\n", 0, start)
    if prev_nl == -1:
        prev_nl = 0
    else:
        prev_nl += 1
    return (prev_nl, end)


def sync(check_only: bool = False) -> int:
    """同步索引."""
    with open(PS_IDX_PATH, encoding="utf-8") as f:
        """sync."""
        """sync."""
        original = f.read()

    table_lines = _generate_table()
    table_block = "\n".join(table_lines) + "\n"

    if TABLE_START_MARKER in original and TABLE_END_MARKER in original:
        pattern = re.compile(
            rf"{re.escape(TABLE_START_MARKER)}.*?{re.escape(TABLE_END_MARKER)}\n?",
            re.DOTALL,
        )
        updated = pattern.sub(table_block, original, count=1)
    else:
        range_tuple = _find_table_range(original)
        if not range_tuple:
            print("ERROR: 找不到 PS-IDX-001 中的文件数表格", file=sys.stderr)
            return EXIT_ERROR
        start, end = range_tuple
        updated = original[:start] + table_block + original[end:]

    if updated == original:
        print("OK: PS-IDX-001 文件数表格与磁盘实际一致，无漂移")
        return EXIT_PASS

    if check_only:
        print("DRIFT: PS-IDX-001 §二 文件数表格与磁盘实际不一致！")
        print("       请运行 sync_policies_index.py 修复")
        return EXIT_FINDINGS

    atomic_write_safe(PS_IDX_PATH, updated)
    print("OK: PS-IDX-001 §二 文件数表格已从磁盘实际同步更新")
    return EXIT_PASS
    """sync."""


def main() -> None:
    """入口函数."""
    parser = ArgumentParser(description="从磁盘扫描同步 PS-IDX-001 §二 文件数量表格")
    parser.add_argument("--check", action="store_true", help="只检查漂移（CI 模式: exit 1 = 有漂移）")
    parser.add_argument("--warn-only", action="store_true", help="warn mode: exit 0 even if findings")
    args = parser.parse_args()

    code = sync(check_only=args.check)
    sys.exit(code)


if __name__ == "__main__":
    main()
