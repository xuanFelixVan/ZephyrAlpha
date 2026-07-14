# [BLUEPRINT] MOD-INF-005 | scripts/governance/d1_structure/sync_index_from_manifest.py | §
# [MODULE] scripts.governance.d1_structure.sync_index_from_manifest
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
# [TTL] task_bound
"""sync_index_from_manifest.py — 从 script_manifest.yaml (SSoT) 自动同步 index.md 的脚本数量。



对标：YAML canonical SSoT + GATE-A 代码↔YAML 对齐
      index.md 的数字不再手动维护——本脚本从 manifest 读取真源并写入。

每次新脚本入库后运行一次，保证 index.md 树形图中的数字与 manifest 一致。

用法：
    python scripts/governance/d1_structure/sync_index_from_manifest.py          # 实际写入
    python scripts/governance/d1_structure/sync_index_from_manifest.py --check  # 只检查漂移（CI 模式）
"""

from __future__ import annotations

__manifest__ = """
args:
- --check
description: 从 manifest SSoT 自动同步 index.md 脚本数量（GATE-A — index.md
  数字不再手动维护）
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

from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, SCRIPTS_DIR
from _shared.encoding import ensure_utf8_stdout
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT

ensure_utf8_stdout()

INDEX_MD = SCRIPTS_DIR / "index.md"
MANIFEST = SCRIPTS_DIR / "script_manifest.yaml"

TREE_START_MARKER = "<!-- TREE-AUTO-START -->"
TREE_END_MARKER = "<!-- TREE-AUTO-END -->"
COVERAGE_START_MARKER = "<!-- COVERAGE-AUTO-START -->"
COVERAGE_END_MARKER = "<!-- COVERAGE-AUTO-END -->"

_DIR_MAP = {
    "d1_structure": ("D1", "结构完整性"),
    "d2_links": ("D2", "链接完整性"),
    "d3_metadata": ("D3", "元数据合规"),
    "d4_paths": ("D4", "路径有效性"),
    "d5_architecture": ("D5", "架构合规"),
    "d6_security": ("D6", "安全漏洞"),
    "d7_code": ("D7", "代码质量"),
    "d8_doc_sync": ("D8", "文档代码同步"),
    "d9_knowledge": ("D9", "知识覆盖"),
    "d10_performance": ("D10", "性能容量"),
    "d11_compliance": ("D11", "合规完整性"),
    "d12_ai_hallucination": ("D12", "AI 幻觉"),
}

_DIR_ORDER = [
    "d1_structure",
    "d2_links",
    "d3_metadata",
    "d4_paths",
    "d5_architecture",
    "d6_security",
    "d7_code",
    "d8_doc_sync",
    "d9_knowledge",
    "d10_performance",
    "d11_compliance",
    "d12_ai_hallucination",
]

_ROOT_SCRIPTS = [
    ("run_all.py", "全维度扫描入口"),
    ("status.py", "健康仪表盘"),
    ("check_registry_consistency.py", "跨登记表一致性校验"),
    ("script_manifest.yaml", "脚本注册表"),
    ("quality_standard.md", "审计脚本质量标准"),
]


def _load_manifest() -> list[dict]:
    """_load_manifest implementation."""
    import yaml

    with open(MANIFEST, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return list(data.get("scripts", []))


def _counts_per_dir(manifest: list[dict]) -> dict[str, int]:
    """_counts_per_dir implementation."""
    counts: dict[str, int] = {d: 0 for d in _DIR_ORDER}
    root_count = 0
    for entry in manifest:
        name: str = entry.get("name", "")
        parts = name.split("/")
        if len(parts) == 2 and parts[0] in counts:
            counts[parts[0]] += 1
        elif len(parts) == 1:
            root_count += 1
    return counts, root_count


def _generate_tree_lines(manifest: list[dict]) -> list[str]:
    """_generate_tree_lines implementation."""
    counts, _root_count = _counts_per_dir(manifest)
    total = sum(counts.values()) + _root_count

    lines = []
    lines.append(f"{TREE_START_MARKER}")
    lines.append("```")
    lines.append("scripts/governance/")
    lines.append("├── _shared/                        共用工具（5 文件）")

    for i, dim_dir in enumerate(_DIR_ORDER):
        dim_id, dim_name = _DIR_MAP[dim_dir]
        n = counts[dim_dir]
        if dim_dir == "d10_performance":
            label = "待建设"
        else:
            label = f"{n} 脚本"
        lines.append(f"├── {dim_dir:30s} {dim_id} {dim_name}（{label}）")

    for i, (path, desc) in enumerate(_ROOT_SCRIPTS):
        is_last = i == len(_ROOT_SCRIPTS) - 1
        tree_char = "└──" if is_last else "├──"
        if path == "script_manifest.yaml":
            desc_text = f"脚本注册表（SSoT — {total} 条目）"
        else:
            desc_text = desc
        lines.append(f"{tree_char} {path:30s} {desc_text}")

    lines.append("```")
    lines.append(f"{TREE_END_MARKER}")
    return lines


def _replace_tree_section(current: str, tree_lines: list[str]) -> str:
    """_replace_tree_section implementation."""
    tree_block = "\n".join(tree_lines) + "\n"

    if TREE_START_MARKER in current and TREE_END_MARKER in current:
        pattern = re.compile(
            rf"{re.escape(TREE_START_MARKER)}.*?{re.escape(TREE_END_MARKER)}\n?",
            re.DOTALL,
        )
        return pattern.sub(tree_block, current, count=1)
    else:
        old_tree_pattern = re.compile(
            r"^```\nscripts/governance/\n├──.*?^```$",
            re.DOTALL | re.MULTILINE,
        )
        match = old_tree_pattern.search(current)
        if match:
            return current[: match.start()] + tree_block + current[match.end() :]
        else:
            print("ERROR: 找不到 index.md 中的树形代码块", file=sys.stderr)
            sys.exit(EXIT_FINDINGS)


def _generate_coverage_lines(manifest: list[dict]) -> list[str]:
    """_generate_coverage_lines implementation."""
    active_dims = set()
    for entry in manifest:
        for d in entry.get("dimensions", []):
            active_dims.add(d)
    total_dims = len(_DIR_ORDER)
    covered = len(active_dims)

    bar_length = 24
    covered_bars = int(bar_length * covered / total_dims) if total_dims > 0 else 0
    bar = "█" * covered_bars + "░" * (bar_length - covered_bars)

    dim_lines = []
    for i, dim_dir in enumerate(_DIR_ORDER):
        dim_id, dim_name = _DIR_MAP[dim_dir]
        status = "✓" if dim_id in active_dims else "✗"
        dim_lines.append(f"{dim_id} {dim_name} {status}")

    line1 = dim_lines[:4]
    line2 = dim_lines[4:8]
    line3 = dim_lines[8:12]

    lines = [
        f"{COVERAGE_START_MARKER}",
        "```",
        f"已覆盖: {bar} {covered}/{total_dims} ({int(covered / total_dims * 100)}%)  [generated from manifest SSoT, auto-synced]",
        "   ".join(line1),
        "   ".join(line2),
        "   ".join(line3),
        "```",
        f"{COVERAGE_END_MARKER}",
    ]
    return lines


def _replace_coverage_section(current: str, coverage_lines: list[str]) -> str:
    """_replace_coverage_section implementation."""
    coverage_block = "\n".join(coverage_lines) + "\n"

    if COVERAGE_START_MARKER in current and COVERAGE_END_MARKER in current:
        pattern = re.compile(
            rf"{re.escape(COVERAGE_START_MARKER)}.*?{re.escape(COVERAGE_END_MARKER)}\n?",
            re.DOTALL,
        )
        return pattern.sub(coverage_block, current, count=1)
    else:
        print("ERROR: 找不到 index.md 中的 COVERAGE-AUTO 标记", file=sys.stderr)
        sys.exit(EXIT_FINDINGS)


def sync(manifest: list[dict], check_only: bool = False) -> int:
    """同步索引."""
    tree_lines = _generate_tree_lines(manifest)
    """sync."""
    coverage_lines = _generate_coverage_lines(manifest)

    with open(INDEX_MD, encoding="utf-8") as f:
        original = f.read()

    updated = _replace_tree_section(original, tree_lines)
    updated = _replace_coverage_section(updated, coverage_lines)

    if updated == original:
        print("OK: index.md 已与 manifest 一致，无漂移")
        return EXIT_PASS

    if check_only:
        print("DRIFT: index.md 与 manifest (SSoT) 不一致！")
        print("       请运行 sync_index_from_manifest.py 修复")
        return EXIT_FINDINGS

    atomic_write_safe(INDEX_MD, updated)
    print("OK: index.md 已从 manifest SSoT 同步更新")
    return EXIT_PASS
    """sync."""


def main() -> None:
    """入口函数."""
    parser = ArgumentParser(description="从 manifest SSoT 同步 index.md 脚本数量")
    parser.add_argument(
        "--check",
        action="store_true",
        help="只检查漂移（CI 模式: exit 1 = 有漂移）",
    )
    parser.add_argument("--warn-only", action="store_true", help="warn mode: exit 0 even if findings")
    args = parser.parse_args()

    try:
        manifest = _load_manifest()
    except Exception as e:
        print(f"ERROR: 无法加载 manifest: {e}", file=sys.stderr)
        sys.exit(EXIT_ERROR)

    code = sync(manifest, check_only=args.check)
    sys.exit(code)


if __name__ == "__main__":
    main()
