# [BLUEPRINT] MOD-D5_ARCH_TOOLS | (auto-injected by S4 reconciler) | §
# [TTL] permanent
#!/usr/bin/env python
"""候选模块登记表查询工具。

用法:
  python scripts/governance/query_candidate_registry.py --domain D_RISK
  python scripts/governance/query_candidate_registry.py --problem "黑天鹅"
  python scripts/governance/query_candidate_registry.py --keyword "止损"
  python scripts/governance/query_candidate_registry.py --capability C-038
  python scripts/governance/query_candidate_registry.py --status deferred --priority P1
  python scripts/governance/query_candidate_registry.py --id CAND-RSK-014 --show-position
  python scripts/governance/query_candidate_registry.py --due-review
  python scripts/governance/query_candidate_registry.py --check-duplicate "黑天鹅模式库"
  python scripts/governance/query_candidate_registry.py --has-position-in dataflowgraph
"""

__manifest__ = """
args: []
description: 候选模块登记表查询工具。
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""

import argparse
import sys
from datetime import date
from pathlib import Path

import yaml

REGISTRY_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "01_policies_and_standards"
    / "_registry"
    / "catalogs"
    / "candidate_module_registry.yaml"
)


def load_registry():
    """加载候选库 YAML，返回 entries 列表。"""
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("entries", [])


def match_text(entry, query):
    """在 name/description/problem/keywords/search_terms/tags/aliases 全文匹配。"""
    fields = [
        entry.get("name", ""),
        entry.get("description", ""),
        entry.get("problem_it_solves", ""),
        " ".join(entry.get("keywords", [])),
        " ".join(entry.get("search_terms", [])),
        " ".join(entry.get("tags", [])),
        " ".join(entry.get("aliases", [])),
    ]
    return query.lower() in " ".join(fields).lower()


def print_table(entries):
    """表格输出候选列表。"""
    if not entries:
        print("无匹配候选。")
        return
    header = f"{'ID':<22} {'名称':<32} {'域':<14} {'状态':<10} {'P':<4}"
    print(header)
    print("-" * len(header))
    for e in entries:
        name = (e.get("name") or "")[:30]
        print(
            f"{e['id']:<22} {name:<32} {e.get('domain', ''):<14} {e.get('status', ''):<10} {e.get('priority', ''):<4}"
        )
    print(f"\n共 {len(entries)} 条")


def _print_depgraph(graph_data):
    """打印 depgraph 定位。"""
    print(f"  module_id: {graph_data.get('target_module_id', '')}")
    neighbors = graph_data.get("target_neighbors", {})
    print(f"  上游邻居: {neighbors.get('upstream', [])}")
    print(f"  下游邻居: {neighbors.get('downstream', [])}")
    print(f"  插入位置: {graph_data.get('insertion_description', '')}")
    for ed in graph_data.get("target_edges", []):
        print(f"  实施边: {ed.get('from', '')} → {ed.get('to', '')} ({ed.get('type', '')}) {ed.get('reason', '')}")


def _print_dataflow(graph_data):
    """打印 dataflowgraph 定位。"""
    print(f"  节点类型: {graph_data.get('target_node_type', '')}")
    print(f"  数据流: {graph_data.get('data_flow_path', '')}")
    print(f"  上游数据: {graph_data.get('upstream_data', [])}")
    print(f"  下游数据: {graph_data.get('downstream_data', [])}")


def _print_decision(graph_data):
    """打印 decisiongraph 定位。"""
    print(f"  决策层: {graph_data.get('target_layer', '')}")
    print(f"  track: {graph_data.get('target_track', '')}")
    print(f"  频率: {graph_data.get('decision_frequency', '')}")
    print(f"  决策路径: {graph_data.get('decision_path', '')}")


def _print_blueprint(graph_data):
    """打印 blueprint 定位。"""
    print(f"  文档: {graph_data.get('target_ref', '')}")
    print(f"  成熟度: {graph_data.get('design_maturity', '')}")


_GRAPH_PRINTERS = {
    "depgraph": _print_depgraph,
    "dataflowgraph": _print_dataflow,
    "decisiongraph": _print_decision,
    "blueprint": _print_blueprint,
}


def show_position(entry):
    """显示某候选的全景定位详情。"""
    pp = entry.get("panorama_position", {})
    print(f"\n{'=' * 60}")
    print(f"候选 {entry['id']}: {entry.get('name', '')}")
    print(f"{'=' * 60}")
    for graph_name in ("depgraph", "dataflowgraph", "decisiongraph", "blueprint"):
        graph_data = pp.get(graph_name, {})
        has = graph_data.get("has_position", False)
        print(f"\n[图: {graph_name}] has_position={has}")
        if has and graph_name in _GRAPH_PRINTERS:
            _GRAPH_PRINTERS[graph_name](graph_data)
        else:
            print(f"  {graph_data.get('note', '无位置')}")


def filter_entries(entries, args):
    """按 domain/status/priority/capability/problem/keyword/has-position-in 多维筛选。"""
    filtered = entries
    if args.domain:
        filtered = [e for e in filtered if e.get("domain") == args.domain]
    if args.status:
        filtered = [e for e in filtered if e.get("status") == args.status]
    if args.priority:
        filtered = [e for e in filtered if e.get("priority") == args.priority]
    if args.capability:
        filtered = [e for e in filtered if e.get("capability") == args.capability]
    if args.problem:
        filtered = [e for e in filtered if match_text(e, args.problem)]
    if args.keyword:
        filtered = [e for e in filtered if match_text(e, args.keyword)]
    if args.has_position_in:
        filtered = [
            e
            for e in filtered
            if e.get("panorama_position", {}).get(args.has_position_in, {}).get("has_position", False)
        ]
    return filtered


def cmd_by_id(entries, args):
    """按 ID 精确查找。"""
    matches = [e for e in entries if e["id"] == args.id]
    if not matches:
        print(f"未找到 ID={args.id}")
        return
    if args.show_position:
        show_position(matches[0])
    else:
        print_table(matches)


def cmd_check_duplicate(entries, args):
    """登记前查重。"""
    matches = [e for e in entries if match_text(e, args.check_duplicate)]
    if matches:
        print(f"⚠ 发现 {len(matches)} 个可能重复的候选:")
        print_table(matches)
    else:
        print("✓ 无重复，可安全登记。")


def cmd_due_review(entries):
    """查找到期需复审的候选。"""
    today = date.today()
    results = []
    for e in entries:
        nrd = e.get("next_review_date")
        if not nrd:
            continue
        try:
            review_date = date.fromisoformat(str(nrd).replace("'", ""))
            if review_date <= today:
                results.append(e)
        except (ValueError, TypeError):
            continue
    print(f"到期需复审的候选（截至 {today}）:")
    print_table(results)


def build_parser():
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(description="候选模块登记表查询工具")
    parser.add_argument("--domain", help="按域筛选 (如 D_RISK)")
    parser.add_argument("--problem", help="按痛点全文检索")
    parser.add_argument("--keyword", help="按关键词检索")
    parser.add_argument("--capability", help="按能力 C-XXX 筛选")
    parser.add_argument("--status", help="按状态筛选 (candidate/deferred/rejected/approved/promoted)")
    parser.add_argument("--priority", help="按优先级筛选 (P0/P1/P2)")
    parser.add_argument("--id", help="按 ID 精确查找 (如 CAND-RSK-014)")
    parser.add_argument("--show-position", action="store_true", help="显示全景定位详情")
    parser.add_argument("--due-review", action="store_true", help="查找到期需复审的候选")
    parser.add_argument("--check-duplicate", help="登记前查重")
    parser.add_argument("--has-position-in", help="查某图有位置的候选 (depgraph/dataflowgraph/decisiongraph/blueprint)")
    return parser


def main():
    """主入口：参数解析 + 命令分发。"""
    args = build_parser().parse_args()
    entries = load_registry()

    if args.id:
        cmd_by_id(entries, args)
    elif args.check_duplicate:
        cmd_check_duplicate(entries, args)
    elif args.due_review:
        cmd_due_review(entries)
    else:
        print_table(filter_entries(entries, args))


if __name__ == "__main__":
    main()
