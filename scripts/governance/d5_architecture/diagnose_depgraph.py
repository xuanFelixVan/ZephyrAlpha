#!/usr/bin/env python3
"""
# [BLUEPRINT] MOD-INF-005 | scripts/governance/diagnose_depgraph.py | §7
# [MODULE] scripts.governance.diagnose_depgraph
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
# [CONSUMERS] governance automation; structural optimization planning
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] --dry-run MUST NOT modify any file; output MUST be valid YAML
# [MODIFY-GUARD] PostgreSQL depgraph
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ScanError; ParseError
# [TESTS] tests/test_diagnose_depgraph.py
# [TTL] permanent
"""

__manifest__ = """
args: []
description: '# [BLUEPRINT] MOD-INF-005 | scripts/governance/diagnose_depgraph.py
  | §7'
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import os
import sys
from collections import defaultdict
from pathlib import Path

# 治本（2026-06-27）：删除 DEPGRAPH_PATH = .../depgraph.db 常量（路径污染源，未使用）。
# P2 迁移后 depgraph 已迁至 PostgreSQL，连接入口 get_depgraph_pg_connection()。

# P2迁移后：depgraph.db 已迁移到 PostgreSQL，通过 _shared.constants 获取 PG 连接。
_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import get_depgraph_pg_connection, REPO_ROOT  # noqa: E402
from _shared.file_utils import atomic_write  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT
from zephyr.shared.io.yaml_utils import load_vocabulary_values  # noqa: E402  SSoT 词表加载（治本 2026-06-30）

PROJECT_ROOT = REPO_ROOT

LAYER_MAP = {
    "L00": 0,
    "L01": 1,
    "L02": 2,
    "L03": 3,
    "L04": 4,
    "L05": 5,
    "L06": 6,
    "L07": 7,
    "L08": 8,
    "L09": 9,
    "L10": 10,
    "L11": 11,
    "L12": 12,
    "L13": 13,
}

LAYER_KEYS_SORTED = sorted(LAYER_MAP.keys(), key=lambda x: -len(x))

ORPHAN_EXEMPT_TYPES = {"doc", "diagram", "infra", "policy", "template", "schema", "data", "config"}  # noqa: gate-vocab  孤儿节点豁免类型业务子集


def load_depgraph():
    conn = get_depgraph_pg_connection(autocommit=True)
    data = {"nodes": {}, "edges": [], "adjacency_lists": {"forward": {}, "reverse": {}}, "metadata": {}}
    for row in conn.execute("SELECT * FROM nodes"):
        node = dict(row)
        nid = node.pop("node_id")
        node["type"] = node.pop("node_type", "")
        data["nodes"][nid] = node
    for row in conn.execute("SELECT * FROM edges"):
        edge = dict(row)
        edge["from"] = edge.pop("from_node_id", "")
        edge["to"] = edge.pop("to_node_id", "")
        data["edges"].append(edge)
    # Build adjacency lists from edges
    fwd = defaultdict(list)
    rev = defaultdict(list)
    for e in data["edges"]:
        fwd[e["from"]].append(e["to"])
        rev[e["to"]].append(e["from"])
    data["adjacency_lists"]["forward"] = dict(fwd)
    data["adjacency_lists"]["reverse"] = dict(rev)
    conn.close()
    return data


def extract_layer(path, blueprint_id):
    if path:
        pl = path.lower().replace("\\", "/")
        for key in LAYER_KEYS_SORTED:
            lk = key.lower()
            if f"/{lk}_" in pl or f"/{lk}/" in pl:
                return LAYER_MAP[key]
    if blueprint_id:
        bid = blueprint_id.strip('"').strip("'")
        if bid.startswith("MOD-L"):
            for key in LAYER_KEYS_SORTED:
                if key in bid:
                    return LAYER_MAP[key]
    return None


def build_node_layers(nodes):
    node_layers = {}
    for nid, node in nodes.items():
        path = node.get("path", "")
        bid = node.get("blueprint_id", "")
        layer = extract_layer(path, bid)
        node_layers[nid] = layer
    return node_layers


def find_cycles(adjacency, max_depth=10):
    cycles = []
    seen_cycle_keys = set()

    def dfs(start):
        stack = [(start, [start], {start})]
        while stack:
            node, path, path_set = stack.pop()
            for neighbor in adjacency.get(node, []):
                if neighbor in path_set:
                    idx = path.index(neighbor)
                    cycle = path[idx:]
                    cycle_key = tuple(sorted(cycle))
                    if cycle_key not in seen_cycle_keys:
                        seen_cycle_keys.add(cycle_key)
                        cycles.append(cycle)
                elif len(path) < max_depth:
                    stack.append((neighbor, path + [neighbor], path_set | {neighbor}))

    for node in adjacency:
        dfs(node)

    return cycles


def verify_cycles(cycles, edges, nodes):
    verified = []
    edge_type_map = defaultdict(lambda: defaultdict(set))
    for e in edges:
        edge_type_map[e["from"]][e["to"]].add(e.get("dep_type", "unknown"))

    for cycle in cycles:
        if len(cycle) != 2:
            verified.append(
                {
                    "nodes": cycle,
                    "classification": "multi_node_cycle",
                    "needs_manual_review": True,
                    "reason": "Multi-node cycle; verify each edge type before acting",
                }
            )
            continue

        a, b = cycle[0], cycle[1]
        a_to_b_types = edge_type_map[a][b]
        b_to_a_types = edge_type_map[b][a]

        if a_to_b_types == {"import_depends"} and b_to_a_types == {"import_depends"}:
            classification = "true_cycle"
            reason = "Both directions are hard imports"
        elif a_to_b_types & {"import_depends"} and b_to_a_types & {"import_depends"}:
            classification = "bidirectional_import"
            reason = "Both import each other but may have additional edge types"
        elif a_to_b_types & {"import_depends"} and b_to_a_types & {"produces", "consumes", "events", "data_flow"}:
            classification = "event_driven"
            reason = "One direction is import, other is event/data flow — NOT a circular dependency"
        elif a_to_b_types & {"produces", "consumes", "events", "data_flow"} and b_to_a_types & {
            "produces",
            "consumes",
            "events",
            "data_flow",
        }:
            classification = "event_driven"
            reason = "Both directions are event/data flow — NOT a circular dependency"
        elif a_to_b_types & {"import_depends"} and not b_to_a_types & {"import_depends"}:
            classification = "false_positive"
            reason = "Only one direction is import; reverse is %s — NOT a circular dependency" % (
                ",".join(b_to_a_types) or "none"
            )
        else:
            classification = "needs_review"
            reason = "Edge types: A→B=%s, B→A=%s" % (",".join(a_to_b_types), ",".join(b_to_a_types))

        verified.append(
            {
                "nodes": cycle,
                "classification": classification,
                "needs_manual_review": classification not in ("true_cycle", "event_driven", "false_positive"),
                "reason": reason,
                "a_to_b_types": sorted(a_to_b_types),
                "b_to_a_types": sorted(b_to_a_types),
            }
        )

    return verified


def find_cross_layer_refs(nodes, edges, node_layers):
    refs = []
    for edge in edges:
        if edge["dep_type"] != "import_depends":
            continue
        from_id = edge["from"]
        to_id = edge["to"]
        from_layer = node_layers.get(from_id)
        to_layer = node_layers.get(to_id)
        if from_layer is not None and to_layer is not None:
            if from_layer > to_layer + 1:
                from_path = nodes.get(from_id, {}).get("path", from_id)
                to_path = nodes.get(to_id, {}).get("path", to_id)
                refs.append(
                    {
                        "from": from_path,
                        "to": to_path,
                        "from_layer": from_layer,
                        "to_layer": to_layer,
                        "gap": from_layer - to_layer,
                    }
                )
    return sorted(refs, key=lambda x: -x["gap"])


def find_deep_chains(adjacency, max_depth=20):
    chains = []
    stack = []
    for start in adjacency:
        stack.append((start, [start], {start}))
    while stack:
        node, path, visited = stack.pop()
        neighbors = adjacency.get(node, [])
        if not neighbors:
            if len(path) >= 4:
                chains.append(path[:])
            continue
        if len(path) >= max_depth:
            chains.append(path[:])
            continue
        for neighbor in neighbors:
            if neighbor in visited:
                continue
            stack.append((neighbor, path + [neighbor], visited | {neighbor}))
    return sorted(chains, key=lambda x: -len(x))[:30]


def find_god_modules(nodes, edges, threshold=15):
    fan_out = defaultdict(int)
    fan_in = defaultdict(int)
    for e in edges:
        if e["dep_type"] == "import_depends":
            fan_out[e["from"]] += 1
            fan_in[e["to"]] += 1

    god_out = []
    for nid, count in sorted(fan_out.items(), key=lambda x: -x[1]):
        if count >= threshold:
            node = nodes.get(nid, {})
            god_out.append({"path": node.get("path", nid), "type": node.get("type", ""), "fan_out": count})

    god_in = []
    for nid, count in sorted(fan_in.items(), key=lambda x: -x[1]):
        if count >= threshold:
            node = nodes.get(nid, {})
            god_in.append({"path": node.get("path", nid), "type": node.get("type", ""), "fan_in": count})

    return god_out, god_in


def find_boundary_violations(nodes, edges):
    violations = []
    for edge in edges:
        if edge["dep_type"] != "import_depends":
            continue
        from_id = edge["from"]
        to_id = edge["to"]
        from_path = nodes.get(from_id, {}).get("path", "")
        to_path = nodes.get(to_id, {}).get("path", "")
        if not from_path.startswith("src/zephyr/") or not to_path.startswith("src/zephyr/"):
            continue
        if to_path.endswith("/__init__.py"):
            continue
        from_pkg = from_path.replace("src/zephyr/", "").split("/")[0]
        to_pkg = to_path.replace("src/zephyr/", "").split("/")[0]
        if from_pkg != to_pkg:
            violations.append(
                {
                    "from": from_path,
                    "to": to_path,
                    "from_pkg": from_pkg,
                    "to_pkg": to_pkg,
                }
            )
    return violations


def find_empty_blueprint_nodes(nodes):
    empty = []
    for nid, node in nodes.items():
        bid = node.get("blueprint_id", "")
        ntype = node.get("type", "")
        if not bid and ntype not in ORPHAN_EXEMPT_TYPES and ntype != "blueprint":
            empty.append({"path": node.get("path", nid), "type": ntype})
    return empty


def find_orphan_nodes(nodes, adjacency_forward, adjacency_reverse, project_root=None):
    """找出图拓扑孤儿节点（无入边无出边）。

    P1-DEP 扩展：当 project_root 提供时，额外检查 node.path 是否在磁盘存在。
    若不存在则标记 ghost=True（对称漂移：磁盘已删除但 depgraph 仍保留）。

    Args:
        nodes: {node_id: {path, type, blueprint_id, ...}}
        adjacency_forward: {node_id: [to_node_id, ...]}
        adjacency_reverse: {node_id: [from_node_id, ...]}
        project_root: 可选，项目根目录 Path；提供时启用 ghost 检测

    Returns:
        list[dict]: 每个 dict 含 path/type/blueprint_id，project_root 提供时额外含 ghost 键
    """
    orphans = []
    for nid in nodes:
        ntype = nodes[nid].get("type", "")
        if ntype in ORPHAN_EXEMPT_TYPES:
            continue
        fwd_neighbors = adjacency_forward.get(nid, [])
        rev_neighbors = adjacency_reverse.get(nid, [])
        has_out = len(fwd_neighbors) > 0
        has_in = len(rev_neighbors) > 0
        if not has_out and not has_in:
            node = nodes[nid]
            # 治本（2026-06-29）：跳过已 deprecated 的孤儿节点。
            # deprecate_node 专用于孤儿清理（文件已删除的残留节点），
            # deprecated 节点是"已知废弃"，不应再报告为 ghost/orphan，
            # 避免 commit 噪音，让 ghost_count 聚焦未处理的漂移。
            if node.get("build_status") == "deprecated":
                continue
            path = node.get("path", nid)
            entry = {"path": path, "type": ntype, "blueprint_id": node.get("blueprint_id", "")}
            # P1-DEP: 对称漂移检测——磁盘不存在的 node 标记为 ghost
            if project_root is not None:
                full_path = Path(project_root) / path
                entry["ghost"] = not full_path.exists()
            orphans.append(entry)
    return orphans


STABILITY_ORDER = {"frozen": 0, "stable": 1, "evolving": 2, "volatile": 3}
SAFETY_ORDER = {"H": 0, "M": 1, "L": 2}
AUTONOMY_ORDER = {"immutable_core": 0, "human_gated": 1, "ai_modifiable": 2}


def find_test_coverage_gaps(nodes, edges):
    modules_with_tests = set()
    test_files = set()
    for nid, node in nodes.items():
        if node.get("dep_type") == "test":
            test_files.add(nid)
    for edge in edges:
        if edge["dep_type"] == "import_depends":
            from_id = edge["from"]
            to_id = edge["to"]
            from_type = nodes.get(from_id, {}).get("type", "")
            to_type = nodes.get(to_id, {}).get("type", "")
            if from_type == "test" and to_type == "module":
                modules_with_tests.add(to_id)
    untested = []
    for nid, node in nodes.items():
        if node.get("dep_type") == "module" and nid not in modules_with_tests:
            untested.append({"path": node.get("path", nid), "type": "module"})
    return untested


def find_stability_violations(nodes, edges):
    violations = []
    for edge in edges:
        if edge["dep_type"] != "import_depends":
            continue
        from_id = edge["from"]
        to_id = edge["to"]
        from_stability = nodes.get(from_id, {}).get("change_policy", "") or nodes.get(from_id, {}).get("stability", "")
        to_stability = nodes.get(to_id, {}).get("change_policy", "") or nodes.get(to_id, {}).get("stability", "")
        if from_stability and to_stability:
            from_rank = STABILITY_ORDER.get(from_stability)
            to_rank = STABILITY_ORDER.get(to_stability)
            if from_rank is not None and to_rank is not None:
                if from_rank < to_rank:
                    violations.append(
                        {
                            "from": nodes.get(from_id, {}).get("path", from_id),
                            "to": nodes.get(to_id, {}).get("path", to_id),
                            "from_change_policy": from_stability,
                            "to_change_policy": to_stability,
                            "violation": "%s depends on %s" % (from_stability, to_stability),
                        }
                    )
    return violations


def find_autonomy_violations(nodes, edges):
    violations = []
    for edge in edges:
        if edge["dep_type"] != "import_depends":
            continue
        from_id = edge["from"]
        to_id = edge["to"]
        from_autonomy = nodes.get(from_id, {}).get("modification_permission", "")
        to_autonomy = nodes.get(to_id, {}).get("modification_permission", "")
        if from_autonomy and to_autonomy:
            from_rank = AUTONOMY_ORDER.get(from_autonomy)
            to_rank = AUTONOMY_ORDER.get(to_autonomy)
            if from_rank is not None and to_rank is not None:
                if from_rank < to_rank:
                    violations.append(
                        {
                            "from": nodes.get(from_id, {}).get("path", from_id),
                            "to": nodes.get(to_id, {}).get("path", to_id),
                            "from_modification_permission": from_autonomy,
                            "to_modification_permission": to_autonomy,
                            "violation": "%s depends on %s" % (from_autonomy, to_autonomy),
                        }
                    )
    return violations


def find_semantic_field_gaps(nodes, edges):
    """Check for missing or invalid semantic fields on edges and nodes (v3.1.0)."""
    # 治本（2026-06-30）：从 semantic_vocabulary.yaml 动态加载（SSoT，PS-VOC-025），
    # 消除与 generate_project_depgraph.py 的复制粘贴多真源。
    VALID_SEMANTIC_TYPES = load_vocabulary_values("semantic_vocabulary.yaml")
    VALID_SEMANTIC_DIRECTIONS = {"upstream", "downstream", "peer"}
    VALID_DECISIONS = {"NEW", "MODIFY", "KEEP", "DEPRECATE"}

    edge_gaps = []
    for edge in edges:
        issues = []
        st = edge.get("semantic_type", "")
        sd = edge.get("semantic_direction", "")
        if not st:
            issues.append("missing semantic_type")
        elif st not in VALID_SEMANTIC_TYPES:
            issues.append("invalid semantic_type: %s" % st)
        if not sd:
            issues.append("missing semantic_direction")
        elif sd not in VALID_SEMANTIC_DIRECTIONS:
            issues.append("invalid semantic_direction: %s" % sd)
        if issues:
            edge_gaps.append({"from": edge.get("from", ""), "to": edge.get("to", ""), "issues": issues})

    node_gaps = []
    for nid, node in nodes.items():
        dec = node.get("decision", "")
        if not dec:
            node_gaps.append({"node": nid, "issue": "missing decision"})
        elif dec not in VALID_DECISIONS:
            node_gaps.append({"node": nid, "issue": "invalid decision: %s" % dec})

    # Critical edges without contract_anchor or failure_mode
    critical_no_ca = sum(1 for e in edges if e.get("coupling_strength") == "critical" and not e.get("contract_anchor"))
    critical_no_fm = sum(1 for e in edges if e.get("coupling_strength") == "critical" and not e.get("failure_mode"))

    return {
        "edge_field_gaps": len(edge_gaps),
        "node_field_gaps": len(node_gaps),
        "critical_no_contract_anchor": critical_no_ca,
        "critical_no_failure_mode": critical_no_fm,
        "edge_sample": edge_gaps[:10],
        "node_sample": node_gaps[:10],
    }


def main():
    parser = argparse.ArgumentParser(description="Diagnose structural issues in project dependency graph")
    parser.add_argument("--output", type=str, default="", help="Output YAML report path")
    args = parser.parse_args()

    print("[DIAG] Loading dependency graph...")
    dg = load_depgraph()
    nodes = dg["nodes"]
    edges = dg["edges"]
    adj_lists = dg.get("adjacency_lists", {})
    adj_fwd = adj_lists.get("forward", dg.get("adjacency_forward", {}))
    adj_rev = adj_lists.get("reverse", dg.get("adjacency_reverse", {}))

    print("[DIAG] Nodes: %d | Edges: %d" % (len(nodes), len(edges)))

    print("[DIAG] 0/10 Building node layer map...")
    node_layers = build_node_layers(nodes)
    layer_dist = defaultdict(int)
    for nid, layer in node_layers.items():
        if layer is not None:
            layer_dist[layer] += 1
    for layer in sorted(layer_dist.keys()):
        print("[DIAG]   Layer %s: %d nodes" % (layer, layer_dist[layer]))

    print("[DIAG] 1/10 Finding empty blueprint_id nodes...")
    empty_bp = find_empty_blueprint_nodes(nodes)
    print("[DIAG]   Found %d nodes with empty blueprint_id" % len(empty_bp))

    print("[DIAG] 2/10 Finding orphan nodes (excluding doc/policy/config types)...")
    orphans = find_orphan_nodes(nodes, adj_fwd, adj_rev, project_root=PROJECT_ROOT)
    ghost_count = sum(1 for o in orphans if o.get("ghost"))
    print("[DIAG]   Found %d orphan nodes (%d ghost: disk-deleted but depgraph retains)" % (len(orphans), ghost_count))

    print("[DIAG] 3/10 Finding circular dependencies...")
    import_edges_fwd = defaultdict(list)
    for e in edges:
        if e["dep_type"] == "import_depends":
            import_edges_fwd[e["from"]].append(e["to"])
    cycles = find_cycles(import_edges_fwd, max_depth=8)
    print("[DIAG]   Found %d circular dependency chains" % len(cycles))

    print("[DIAG] 3b/10 Verifying cycles (diagnosis inversion check)...")
    verified_cycles = verify_cycles(cycles, edges, nodes)
    true_cycles = [v for v in verified_cycles if v["classification"] == "true_cycle"]
    event_driven = [v for v in verified_cycles if v["classification"] == "event_driven"]
    false_positives = [v for v in verified_cycles if v["classification"] == "false_positive"]
    bidirectional = [v for v in verified_cycles if v["classification"] == "bidirectional_import"]
    needs_review = [v for v in verified_cycles if v["needs_manual_review"]]
    print(
        "[DIAG]   True cycles: %d | Event-driven (NOT cycle): %d | False positives: %d | Bidirectional: %d | Needs review: %d"
        % (len(true_cycles), len(event_driven), len(false_positives), len(bidirectional), len(needs_review))
    )

    print("[DIAG] 4/10 Finding cross-layer references (gap >= 2)...")
    cross_layer = find_cross_layer_refs(nodes, edges, node_layers)
    print("[DIAG]   Found %d cross-layer import references" % len(cross_layer))

    print("[DIAG] 5/10 Finding deep dependency chains...")
    deep_chains = find_deep_chains(import_edges_fwd, max_depth=20)
    print("[DIAG]   Found %d deep chains (depth>=4)" % len(deep_chains))

    print("[DIAG] 6/10 Finding God modules...")
    god_out, god_in = find_god_modules(nodes, edges, threshold=15)
    print("[DIAG]   God modules (fan_out>=15): %d" % len(god_out))
    print("[DIAG]   God modules (fan_in>=15): %d" % len(god_in))

    print("[DIAG] 7/10 Finding cross-package boundary violations...")
    boundary_violations = find_boundary_violations(nodes, edges)
    pkg_pairs = defaultdict(int)
    for v in boundary_violations:
        key = "%s -> %s" % (v["from_pkg"], v["to_pkg"])
        pkg_pairs[key] += 1
    print(
        "[DIAG]   Found %d cross-package imports across %d package pairs" % (len(boundary_violations), len(pkg_pairs))
    )

    print("[DIAG] 8/10 Finding test coverage gaps...")
    test_gaps = find_test_coverage_gaps(nodes, edges)
    print("[DIAG]   Found %d modules without test imports" % len(test_gaps))

    print("[DIAG] 9/10 Finding stability violations...")
    stability_violations = find_stability_violations(nodes, edges)
    print("[DIAG]   Found %d stability violations" % len(stability_violations))

    print("[DIAG] 10/11 Finding AI_AUTONOMY violations...")
    autonomy_violations = find_autonomy_violations(nodes, edges)
    print("[DIAG]   Found %d AI_AUTONOMY violations" % len(autonomy_violations))

    print("[DIAG] 11/11 Checking semantic field gaps (v3.1.0)...")
    semantic_gaps = find_semantic_field_gaps(nodes, edges)
    print(
        "[DIAG]   Edge field gaps: %d | Node field gaps: %d"
        % (semantic_gaps["edge_field_gaps"], semantic_gaps["node_field_gaps"])
    )
    print(
        "[DIAG]   Critical edges without contract_anchor: %d | without failure_mode: %d"
        % (semantic_gaps["critical_no_contract_anchor"], semantic_gaps["critical_no_failure_mode"])
    )

    report = {
        "metadata": {
            "diagnosis_version": "3.1.0",
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "layer_distribution": dict(sorted(layer_dist.items())),
        },
        "descriptive_errors": {
            "empty_blueprint_id": {"count": len(empty_bp), "sample": empty_bp[:30]},
            "orphan_nodes": {"count": len(orphans), "sample": orphans[:30]},
        },
        "structural_issues": {
            "circular_dependencies": {
                "count": len(cycles),
                "verified": {
                    "true_cycles": len(true_cycles),
                    "event_driven_not_cycle": len(event_driven),
                    "false_positives": len(false_positives),
                    "bidirectional_import": len(bidirectional),
                    "needs_manual_review": len(needs_review),
                },
                "chains": [
                    {"nodes": [nodes.get(nid, {}).get("path", nid) for nid in cycle], "length": len(cycle)}
                    for cycle in cycles[:30]
                ],
                "verified_details": verified_cycles[:30],
            },
            "cross_layer_references": {
                "count": len(cross_layer),
                "by_gap": dict(
                    defaultdict(
                        int,
                        {
                            gap: sum(1 for r in cross_layer if r["gap"] == gap)
                            for gap in set(r["gap"] for r in cross_layer)
                        },
                    )
                ),
                "sample": cross_layer[:30],
            },
            "deep_dependency_chains": {
                "count": len(deep_chains),
                "chains": [
                    {"nodes": [nodes.get(nid, {}).get("path", nid) for nid in chain], "length": len(chain)}
                    for chain in deep_chains[:20]
                ],
            },
            "god_modules": {
                "high_fan_out": god_out[:20],
                "high_fan_in": god_in[:20],
            },
            "cross_package_violations": {
                "total_imports": len(boundary_violations),
                "package_pairs": dict(sorted(pkg_pairs.items(), key=lambda x: -x[1])[:30]),
            },
        },
        "quality_gates": {
            "test_coverage_gaps": {"count": len(test_gaps), "sample": test_gaps[:30]},
            "change_policy_violations": {"count": len(stability_violations), "sample": stability_violations[:30]},
            "modification_permission_violations": {
                "count": len(autonomy_violations),
                "sample": autonomy_violations[:30],
            },
            "semantic_field_gaps": semantic_gaps,
        },
    }

    if args.output:
        import yaml

        out_path = PROJECT_ROOT / args.output
        content = yaml.dump(report, allow_unicode=True, default_flow_style=False, sort_keys=False)
        atomic_write(out_path, content)
        print("[DIAG] Report written to %s" % args.output)

    print()
    print("=" * 60)
    print("DIAGNOSIS SUMMARY (v3.1.0)")
    print("=" * 60)
    print("  Empty blueprint_id:     %d" % len(empty_bp))
    print("  Orphan nodes:           %d" % len(orphans))
    print(
        "  Circular dependencies:  %d (true: %d | event-driven: %d | false+: %d | bidir: %d)"
        % (len(cycles), len(true_cycles), len(event_driven), len(false_positives), len(bidirectional))
    )
    print("  Cross-layer refs:       %d" % len(cross_layer))
    print("  Deep chains (>=4):      %d" % len(deep_chains))
    print("  God modules (out>=15):  %d" % len(god_out))
    print("  God modules (in>=15):   %d" % len(god_in))
    print("  Cross-pkg violations:   %d" % len(boundary_violations))
    print("  Package pairs:          %d" % len(pkg_pairs))
    print("  Test coverage gaps:     %d" % len(test_gaps))
    print("  Stability violations:   %d" % len(stability_violations))
    print("  Autonomy violations:    %d" % len(autonomy_violations))
    print(
        "  Semantic field gaps:    %d edges / %d nodes"
        % (semantic_gaps["edge_field_gaps"], semantic_gaps["node_field_gaps"])
    )
    print(
        "  Critical no contract:   %d | Critical no failure_mode: %d"
        % (semantic_gaps["critical_no_contract_anchor"], semantic_gaps["critical_no_failure_mode"])
    )
    print()
    print("TOP 10 CROSS-PACKAGE PAIRS:")
    for pair, count in sorted(pkg_pairs.items(), key=lambda x: -x[1])[:10]:
        print("  %s: %d imports" % (pair, count))
    print()
    print("CIRCULAR DEPENDENCIES:")
    for i, cycle in enumerate(cycles[:12], 1):
        paths = [nodes.get(nid, {}).get("path", nid) for nid in cycle]
        short = " -> ".join("/".join(p.split("/")[-2:]) if "/" in p else p for p in paths)
        vc = verified_cycles[i - 1] if i - 1 < len(verified_cycles) else {}
        cls = vc.get("classification", "unknown")
        reason = vc.get("reason", "")
        print("  Cycle %d (len=%d) [%s]: %s" % (i, len(cycle), cls, short))
        if reason:
            print("    Reason: %s" % reason)

    sys.exit(0)


if __name__ == "__main__":
    main()
