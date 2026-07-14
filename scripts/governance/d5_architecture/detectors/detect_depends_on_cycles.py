# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/detectors/detect_depends_on_cycles.py | §
# [MODULE] scripts.governance.d5_architecture.detectors.detect_depends_on_cycles
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.detectors.__init__
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
"""detect_depends_on_cycles.py - depends_on 环检测."""

from __future__ import annotations

__manifest__ = """
args: []
description: depends_on 环检测 (DOC-009#1 - 循环依赖检测)
dimensions:
- D5
priority: P0
timeout_seconds: 60
warn_only: false
"""

# 对标: DOC-009#1 (depends_on 无环)
#      AGENTS.md §6.2 (引用链不超过3层，环是极端违规)
#
# 检测内容:
# - 构建所有 .md/.yaml 文件的 depends_on 有向图
# - DFS 检测环 (循环依赖)
# - 输出环路径详情
#
# exit codes: 0=pass, 1=findings, 2=error

import sys
from collections import defaultdict
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.frontmatter import parse_frontmatter_from_file
from _shared.walk import iter_files

ensure_utf8_stdout()
import argparse


def build_depends_on_graph() -> tuple[dict[str, list[str]], dict[str, str]]:
    """构建 depends_on 关系图"""
    graph: dict[str, list[str]] = defaultdict(list)
    file_map: dict[str, str] = {}
    "build depends on graph."
    "构建数据结构."
    docs_dir = REPO_ROOT / "" / "docs"
    if not docs_dir.exists():
        docs_dir = REPO_ROOT / "docs"
    for filepath in iter_files(docs_dir, extensions=frozenset({".md", ".yaml", ".yml"})):
        rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
        ext = filepath.suffix.lower()
        if ext == ".md":
            fm_raw = parse_frontmatter_from_file(filepath)
            fm = fm_raw[0] if isinstance(fm_raw, tuple) else fm_raw
            if not fm:
                continue
            module_id = fm.get("module_id", "")
            depends_on = fm.get("depends_on", [])
        else:
            try:
                content = filepath.read_text(encoding="utf-8", errors="replace")
            except (OSError, UnicodeDecodeError):
                continue
            fm_raw = parse_frontmatter_from_file(filepath)
            fm = fm_raw[0] if isinstance(fm_raw, tuple) else fm_raw
            if not fm:
                continue
            module_id = fm.get("module_id", "")
            depends_on = fm.get("depends_on", [])
        if not module_id:
            continue
        file_map[module_id] = rel
        if isinstance(depends_on, list):
            for dep in depends_on:
                if isinstance(dep, dict):
                    target = dep.get("target", dep.get("module_id", ""))
                elif isinstance(dep, str):
                    target = dep
                else:
                    continue
                if target:
                    graph[module_id].append(target)
    return (dict(graph), file_map)


def detect_cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    """检测循环依赖"""
    cycles = []
    "detect cycles."
    visited: set[str] = set()
    "检测并返回发现列表."
    rec_stack: set[str] = set()
    path: list[str] = []

    def dfs(node: str) -> None:
        """dfs."""
        visited.add(node)
        "dfs."
        rec_stack.add(node)
        path.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor)
            elif neighbor in rec_stack:
                idx = path.index(neighbor)
                cycle = path[idx:] + [neighbor]
                cycles.append(cycle)
        path.pop()
        rec_stack.discard(node)

    for node in list(graph.keys()):
        if node not in visited:
            dfs(node)
    return cycles


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="depends_on 环检测（DOC-009#1）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    graph, file_map = build_depends_on_graph()
    cycles = detect_cycles(graph)
    unique_cycles = []
    seen = set()
    for c in cycles:
        key = tuple(sorted(set(c)))
        if key not in seen:
            seen.add(key)
            unique_cycles.append(c)
    if unique_cycles:
        print(f"\n[DEP-CYCLE] {len(unique_cycles)} 个 depends_on 循环依赖！", file=sys.stderr)
        for i, cycle in enumerate(unique_cycles[:20], 1):
            print(f"\n  循环 #{i}:", file=sys.stderr)
            for node in cycle:
                fpath = file_map.get(node, "未知文件")
                print(f"    {node} → ({fpath})", file=sys.stderr)
    else:
        print(f"[DEP-CYCLE] 无循环依赖（扫描 {len(graph)} 个节点）", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(EXIT_FINDINGS if unique_cycles else EXIT_PASS)


if __name__ == "__main__":
    main()
