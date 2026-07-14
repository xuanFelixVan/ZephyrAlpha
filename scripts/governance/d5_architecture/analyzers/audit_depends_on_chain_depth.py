# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/analyzers/audit_depends_on_chain_depth.py | §
# [MODULE] scripts.governance.d5_architecture.analyzers.audit_depends_on_chain_depth
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.analyzers.__init__
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
"""audit_depends_on_chain_depth.py — depends_on 依赖链路深度审计



对标：GOV-DOC-009 DOC-009 — 文档控制原则
检测：扫描 docs/ 下所有 .md 文件的 depends_on 字段，构建依赖图，标记超过阈值（3 层）的链路

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: depends_on 依赖链路深度审计（AGENTS.md §6.2 — 引用链不超过3层）
dimensions:
- D5
priority: P1
timeout_seconds: 60
warn_only: false
"""

import argparse
import sys
from collections import defaultdict
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXCLUDE_DIRS, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_MD
from _shared.encoding import ensure_utf8_stdout
from _shared.frontmatter import parse_frontmatter_from_file
from _shared.walk import iter_files

ensure_utf8_stdout()
DOCS_DIR = REPO_ROOT / "docs"
_EXTRA_EXCLUDE = EXCLUDE_DIRS | {"scripts"}
DEFAULT_MAX_DEPTH = 3


def resolve_target_to_file(target: str, module_id_to_file: dict[str, Path], docs_dir: Path) -> Path | None:
    """解析 depends_on 目标为实际文件路径。"""
    clean_target = target.rsplit("#", maxsplit=1)[0].rstrip("/").rstrip(".md")
    if clean_target in module_id_to_file:
        return module_id_to_file[clean_target]
    candidate = docs_dir / f"{clean_target}.md"
    if candidate.exists() and candidate.is_file():
        return candidate
    candidate_rel = docs_dir / clean_target
    if candidate_rel.exists() and candidate_rel.is_file():
        return candidate_rel.resolve()
    for filepath in iter_files(docs_dir, extensions=SCAN_EXTENSIONS_MD, exclude_dirs=_EXTRA_EXCLUDE):
        if filepath.name == Path(clean_target).name:
            return filepath
    return None


def build_dependency_graph() -> tuple[dict[str, set[str]], dict[str, set[str]], dict[str, str], set[str], int]:
    """构建有向依赖图。"""
    adjacency: dict[str, set[str]] = defaultdict(set)
    reverse_adj: dict[str, set[str]] = defaultdict(set)
    module_id_to_file: dict[str, Path] = {}
    file_to_module_id: dict[str, str] = {}
    files_with_deps: set[str] = set()
    total_files = 0
    for filepath in iter_files(DOCS_DIR, extensions=SCAN_EXTENSIONS_MD, exclude_dirs=_EXTRA_EXCLUDE):
        total_files += 1
        fm = parse_frontmatter_from_file(filepath)
        if not fm:
            continue
        module_id = fm.get("module_id", fm.get("doc_id", ""))
        if module_id:
            module_id_to_file[str(module_id)] = filepath
        try:
            rel = str(filepath.relative_to(REPO_ROOT))
        except ValueError:
            rel = str(filepath)
        if module_id:
            file_to_module_id[rel] = str(module_id)
        depends_on = fm.get("depends_on", [])
        if not isinstance(depends_on, list) or not depends_on:
            continue
        files_with_deps.add(rel)
        for dep in depends_on:
            if isinstance(dep, dict):
                dep_target = dep.get("target", dep.get("module_id", ""))
            elif isinstance(dep, str):
                dep_target = dep
            else:
                continue
            if not dep_target:
                continue
            resolved = resolve_target_to_file(dep_target, module_id_to_file, DOCS_DIR)
            if resolved is None:
                continue
            try:
                resolved_rel = str(resolved.relative_to(REPO_ROOT))
            except ValueError:
                resolved_rel = str(resolved)
            adjacency[rel].add(resolved_rel)
            reverse_adj[resolved_rel].add(rel)
    return (adjacency, reverse_adj, file_to_module_id, files_with_deps, total_files)


def compute_chain_depths(adjacency: dict[str, set[str]], files_with_deps: set[str]) -> dict[str, int]:
    """计算每个节点的最长依赖深度。"""
    depths: dict[str, int] = {}

    def dfs(node: str, visited: set[str]) -> int:
        """深度优先搜索"""
        if node in depths:
            return depths[node]
        "dfs."
        if node in visited:
            return EXIT_FINDINGS
        visited.add(node)
        max_dep = 0
        for neighbor in adjacency.get(node, set()):
            sub_depth = dfs(neighbor, visited | {node})
            max_dep = max(max_dep, sub_depth)
        depth = max_dep + 1
        depths[node] = depth
        return depth
        "dfs."

    for file_path in files_with_deps:
        if file_path not in depths:
            dfs(file_path, set())
    return depths


def analyze_chains(
    adjacency: dict[str, set[str]],
    reverse_adj: dict[str, set[str]],
    depths: dict[str, int],
    files_with_deps: set[str],
    file_to_module_id: dict[str, str],
    max_depth: int,
) -> list[dict]:
    """分析超标链路。"""
    findings = []
    root_files = {f for f in files_with_deps if f not in reverse_adj or not reverse_adj[f]}

    def trace_chain(node: str, visited: frozenset[str]) -> list[str]:
        """追踪依赖链"""
        if node in visited or node not in adjacency or (not adjacency[node]):
            "trace_chain."
            return [node]
        deepest: list[str] = []
        for neighbor in adjacency[node]:
            sub = trace_chain(neighbor, visited | {node})
            if len(sub) > len(deepest):
                deepest = sub
        return [node] + deepest
        "trace chain."

    chain_id = 0
    for root in sorted(root_files):
        chain_id += 1
        chain = trace_chain(root, frozenset())
        depth = len(chain)
        depth_val = depths.get(root, depth)
        node_labels = []
        for node in chain:
            mid = file_to_module_id.get(node, "")
            label = mid if mid else Path(node).stem
            node_labels.append(label)
        if depth_val > max_depth:
            findings.append(
                {
                    "type": "chain_violation",
                    "chain_id": chain_id,
                    "root_file": root,
                    "root_module_id": file_to_module_id.get(root, ""),
                    "depth": depth_val,
                    "max_allowed": max_depth,
                    "chain": " → ".join(node_labels),
                    "chain_files": chain,
                    "severity": "MEDIUM" if depth_val == max_depth + 1 else "HIGH",
                }
            )
    return findings


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="depends_on 依赖链路深度审计")
    parser.add_argument("--max-depth", type=int, default=DEFAULT_MAX_DEPTH)
    parser.add_argument("--warn-only", action="store_true")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()
    print("\n[DEP-CHAIN] 开始扫描...", file=sys.stderr)
    adjacency, reverse_adj, file_to_module_id, files_with_deps, total_files = build_dependency_graph()
    print(f"  扫描文件: {total_files}", file=sys.stderr)
    print(f"  有 depends_on 的文件: {len(files_with_deps)}", file=sys.stderr)
    if not files_with_deps:
        print("[DEP-CHAIN] OK", file=sys.stderr)
        sys.exit(EXIT_PASS)
    depths = compute_chain_depths(adjacency, files_with_deps)
    findings = analyze_chains(adjacency, reverse_adj, depths, files_with_deps, file_to_module_id, args.max_depth)
    root_files = {f for f in files_with_deps if f not in reverse_adj or not reverse_adj[f]}
    mid_chain_files = files_with_deps - root_files
    print(f"  链路总数: {len(root_files)}", file=sys.stderr)
    print(f"  中间节点: {len(mid_chain_files)}", file=sys.stderr)
    depth_distribution: dict[int, int] = defaultdict(int)
    for root in sorted(root_files):
        d = depths.get(root, 1)
        depth_distribution[d] += 1
    for d in sorted(depth_distribution):
        marker = " ⚠" if d > args.max_depth else ""
        print(f"    {d} 层: {depth_distribution[d]}{marker}", file=sys.stderr)
    violations = [f for f in findings if f["type"] == "chain_violation"]
    print(f"\n  超标链路: {len(violations)} (阈值={args.max_depth})", file=sys.stderr)
    if args.verbose:
        for vl in violations:
            print(
                f"\n  [{vl['severity']}] 链路#{vl['chain_id']} — {vl['depth']}层 (上限{vl['max_allowed']})",
                file=sys.stderr,
            )
            print(f"    根文件: {vl['root_file']}", file=sys.stderr)
            print(f"    链路: {vl['chain']}", file=sys.stderr)
    if violations:
        print(f"\n[DEP-CHAIN] FAIL {len(violations)} 条超标", file=sys.stderr)
    else:
        print("\n[DEP-CHAIN] PASS", file=sys.stderr)
    sys.exit(EXIT_FINDINGS if violations and (not args.warn_only) else EXIT_PASS)


if __name__ == "__main__":
    main()
