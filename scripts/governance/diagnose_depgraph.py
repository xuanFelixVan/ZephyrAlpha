#!/usr/bin/env python3
"""
# [BLUEPRINT] MOD-INF-005 | scripts/governance/diagnose_depgraph.py | §7
# [MODULE] scripts.governance.diagnose_depgraph
# [INVARIANTS] --dry-run MUST NOT modify any file; output MUST be valid YAML
# [MODIFY-GUARD] system-dependency-map.md
# [CONSUMERS] governance automation; structural optimization planning
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ScanError; ParseError
# [TESTS] tests/test_diagnose_depgraph.py
"""

import argparse
import os
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEPGRAPH_PATH = PROJECT_ROOT / "data" / "asset_index" / "project-entity-depgraph.yaml"

LAYER_MAP = {
    "L00": 0, "L01": 1, "L02": 2, "L03": 3, "L04": 4,
    "L05": 5, "L06": 6, "L07": 7, "L08": 8, "L09": 9,
    "L10": 10, "L11": 11, "L12": 12, "L13": 13,
}

LAYER_KEYS_SORTED = sorted(LAYER_MAP.keys(), key=lambda x: -len(x))

ORPHAN_EXEMPT_TYPES = {"doc", "diagram", "infra", "policy", "standard", "template", "schema", "data", "config"}


def load_depgraph():
    import yaml
    with open(DEPGRAPH_PATH, "r", encoding="utf-8") as f:
        return yaml.unsafe_load(f)


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
            for neighbor_info in adjacency.get(node, []):
                nb = neighbor_info["to"]
                if nb in path_set:
                    idx = path.index(nb)
                    cycle = path[idx:]
                    cycle_key = tuple(sorted(cycle))
                    if cycle_key not in seen_cycle_keys:
                        seen_cycle_keys.add(cycle_key)
                        cycles.append(cycle)
                elif len(path) < max_depth:
                    stack.append((nb, path + [nb], path_set | {nb}))

    for node in adjacency:
        dfs(node)

    return cycles


def verify_cycles(cycles, edges, nodes):
    verified = []
    edge_type_map = defaultdict(lambda: defaultdict(set))
    for e in edges:
        edge_type_map[e["from"]][e["to"]].add(e.get("type", "unknown"))

    for cycle in cycles:
        if len(cycle) != 2:
            verified.append({
                "nodes": cycle,
                "classification": "multi_node_cycle",
                "needs_manual_review": True,
                "reason": "Multi-node cycle; verify each edge type before acting",
            })
            continue

        a, b = cycle[0], cycle[1]
        a_to_b_types = edge_type_map[a][b]
        b_to_a_types = edge_type_map[b][a]

        if a_to_b_types == {"imports"} and b_to_a_types == {"imports"}:
            classification = "true_cycle"
            reason = "Both directions are hard imports"
        elif a_to_b_types & {"imports"} and b_to_a_types & {"imports"}:
            classification = "bidirectional_import"
            reason = "Both import each other but may have additional edge types"
        elif a_to_b_types & {"imports"} and b_to_a_types & {"produces", "consumes", "events", "data_flow"}:
            classification = "event_driven"
            reason = "One direction is import, other is event/data flow — NOT a circular dependency"
        elif a_to_b_types & {"produces", "consumes", "events", "data_flow"} and b_to_a_types & {"produces", "consumes", "events", "data_flow"}:
            classification = "event_driven"
            reason = "Both directions are event/data flow — NOT a circular dependency"
        elif a_to_b_types & {"imports"} and not b_to_a_types & {"imports"}:
            classification = "false_positive"
            reason = "Only one direction is import; reverse is %s — NOT a circular dependency" % (",".join(b_to_a_types) or "none")
        else:
            classification = "needs_review"
            reason = "Edge types: A→B=%s, B→A=%s" % (",".join(a_to_b_types), ",".join(b_to_a_types))

        verified.append({
            "nodes": cycle,
            "classification": classification,
            "needs_manual_review": classification not in ("true_cycle", "event_driven", "false_positive"),
            "reason": reason,
            "a_to_b_types": sorted(a_to_b_types),
            "b_to_a_types": sorted(b_to_a_types),
        })

    return verified


def find_cross_layer_refs(nodes, edges, node_layers):
    refs = []
    for edge in edges:
        if edge["type"] != "imports":
            continue
        from_id = edge["from"]
        to_id = edge["to"]
        from_layer = node_layers.get(from_id)
        to_layer = node_layers.get(to_id)
        if from_layer is not None and to_layer is not None:
            if from_layer > to_layer + 1:
                from_path = nodes.get(from_id, {}).get("path", from_id)
                to_path = nodes.get(to_id, {}).get("path", to_id)
                refs.append({
                    "from": from_path,
                    "to": to_path,
                    "from_layer": from_layer,
                    "to_layer": to_layer,
                    "gap": from_layer - to_layer,
                })
    return sorted(refs, key=lambda x: -x["gap"])


def find_deep_chains(adjacency, max_depth=20):
    chains = []
    stack = []
    for start in adjacency:
        stack.append((start, [start], {start}))
    while stack:
        node, path, visited = stack.pop()
        neighbors = [e["to"] for e in adjacency.get(node, []) if e["type"] == "imports"]
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


def find_god_modules(nodes, adjacency_forward, adjacency_reverse, threshold=15):
    fan_out = defaultdict(int)
    fan_in = defaultdict(int)
    for nid, neighbors in adjacency_forward.items():
        for e in neighbors:
            if e["type"] == "imports":
                fan_out[nid] += 1
    for nid, neighbors in adjacency_reverse.items():
        for e in neighbors:
            if e["type"] == "imports":
                fan_in[nid] += 1

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
        if edge["type"] != "imports":
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
            violations.append({
                "from": from_path,
                "to": to_path,
                "from_pkg": from_pkg,
                "to_pkg": to_pkg,
            })
    return violations


def find_empty_blueprint_nodes(nodes):
    empty = []
    for nid, node in nodes.items():
        bid = node.get("blueprint_id", "")
        ntype = node.get("type", "")
        if not bid and ntype not in ORPHAN_EXEMPT_TYPES and ntype != "blueprint":
            empty.append({"path": node.get("path", nid), "type": ntype})
    return empty


def find_orphan_nodes(nodes, adjacency_forward, adjacency_reverse):
    orphans = []
    for nid in nodes:
        ntype = nodes[nid].get("type", "")
        if ntype in ORPHAN_EXEMPT_TYPES:
            continue
        has_out = any(e.get("type") == "imports" for e in adjacency_forward.get(nid, []))
        has_in = any(e.get("type") == "imports" for e in adjacency_reverse.get(nid, []))
        has_owned = any(e.get("type") == "owned_by" for e in adjacency_forward.get(nid, []))
        has_ref = any(e.get("type") == "references" for e in adjacency_forward.get(nid, []))
        if not has_out and not has_in and not has_owned and not has_ref:
            node = nodes[nid]
            orphans.append({"path": node.get("path", nid), "type": ntype, "blueprint_id": node.get("blueprint_id", "")})
    return orphans


STABILITY_ORDER = {"frozen": 0, "stable": 1, "evolving": 2, "volatile": 3}
SAFETY_ORDER = {"H": 0, "M": 1, "L": 2}
AUTONOMY_ORDER = {"immutable_core": 0, "human_gated": 1, "ai_modifiable": 2}


def find_test_coverage_gaps(nodes, edges):
    modules_with_tests = set()
    test_files = set()
    for nid, node in nodes.items():
        if node.get("type") == "test":
            test_files.add(nid)
    for edge in edges:
        if edge["type"] == "imports":
            from_id = edge["from"]
            to_id = edge["to"]
            from_type = nodes.get(from_id, {}).get("type", "")
            to_type = nodes.get(to_id, {}).get("type", "")
            if from_type == "test" and to_type == "module":
                modules_with_tests.add(to_id)
    untested = []
    for nid, node in nodes.items():
        if node.get("type") == "module" and nid not in modules_with_tests:
            untested.append({"path": node.get("path", nid), "type": "module"})
    return untested


def find_stability_violations(nodes, edges):
    violations = []
    for edge in edges:
        if edge["type"] != "imports":
            continue
        from_id = edge["from"]
        to_id = edge["to"]
        from_stability = nodes.get(from_id, {}).get("stability", "")
        to_stability = nodes.get(to_id, {}).get("stability", "")
        if from_stability and to_stability:
            from_rank = STABILITY_ORDER.get(from_stability)
            to_rank = STABILITY_ORDER.get(to_stability)
            if from_rank is not None and to_rank is not None:
                if from_rank < to_rank:
                    violations.append({
                        "from": nodes.get(from_id, {}).get("path", from_id),
                        "to": nodes.get(to_id, {}).get("path", to_id),
                        "from_stability": from_stability,
                        "to_stability": to_stability,
                        "violation": "%s depends on %s" % (from_stability, to_stability),
                    })
    return violations


def find_autonomy_violations(nodes, edges):
    violations = []
    for edge in edges:
        if edge["type"] != "imports":
            continue
        from_id = edge["from"]
        to_id = edge["to"]
        from_autonomy = nodes.get(from_id, {}).get("ai_autonomy", "")
        to_autonomy = nodes.get(to_id, {}).get("ai_autonomy", "")
        if from_autonomy and to_autonomy:
            from_rank = AUTONOMY_ORDER.get(from_autonomy)
            to_rank = AUTONOMY_ORDER.get(to_autonomy)
            if from_rank is not None and to_rank is not None:
                if from_rank < to_rank:
                    violations.append({
                        "from": nodes.get(from_id, {}).get("path", from_id),
                        "to": nodes.get(to_id, {}).get("path", to_id),
                        "from_autonomy": from_autonomy,
                        "to_autonomy": to_autonomy,
                        "violation": "%s depends on %s" % (from_autonomy, to_autonomy),
                    })
    return violations


def main():
    parser = argparse.ArgumentParser(description="Diagnose structural issues in project dependency graph")
    parser.add_argument("--output", type=str, default="", help="Output YAML report path")
    args = parser.parse_args()

    print("[DIAG] Loading dependency graph...")
    dg = load_depgraph()
    nodes = dg["nodes"]
    edges = dg["edges"]
    adj_fwd = dg.get("adjacency_forward", {})
    adj_rev = dg.get("adjacency_reverse", {})

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
    orphans = find_orphan_nodes(nodes, adj_fwd, adj_rev)
    print("[DIAG]   Found %d orphan nodes" % len(orphans))

    print("[DIAG] 3/10 Finding circular dependencies...")
    import_edges_fwd = defaultdict(list)
    for e in edges:
        if e["type"] == "imports":
            import_edges_fwd[e["from"]].append({"to": e["to"], "type": "imports"})
    cycles = find_cycles(import_edges_fwd, max_depth=8)
    print("[DIAG]   Found %d circular dependency chains" % len(cycles))

    print("[DIAG] 3b/10 Verifying cycles (diagnosis inversion check)...")
    verified_cycles = verify_cycles(cycles, edges, nodes)
    true_cycles = [v for v in verified_cycles if v["classification"] == "true_cycle"]
    event_driven = [v for v in verified_cycles if v["classification"] == "event_driven"]
    false_positives = [v for v in verified_cycles if v["classification"] == "false_positive"]
    bidirectional = [v for v in verified_cycles if v["classification"] == "bidirectional_import"]
    needs_review = [v for v in verified_cycles if v["needs_manual_review"]]
    print("[DIAG]   True cycles: %d | Event-driven (NOT cycle): %d | False positives: %d | Bidirectional: %d | Needs review: %d" % (
        len(true_cycles), len(event_driven), len(false_positives), len(bidirectional), len(needs_review)))

    print("[DIAG] 4/10 Finding cross-layer references (gap >= 2)...")
    cross_layer = find_cross_layer_refs(nodes, edges, node_layers)
    print("[DIAG]   Found %d cross-layer import references" % len(cross_layer))

    print("[DIAG] 5/10 Finding deep dependency chains...")
    deep_chains = find_deep_chains(import_edges_fwd, max_depth=20)
    print("[DIAG]   Found %d deep chains (depth>=4)" % len(deep_chains))

    print("[DIAG] 6/10 Finding God modules...")
    god_out, god_in = find_god_modules(nodes, adj_fwd, adj_rev, threshold=15)
    print("[DIAG]   God modules (fan_out>=15): %d" % len(god_out))
    print("[DIAG]   God modules (fan_in>=15): %d" % len(god_in))

    print("[DIAG] 7/10 Finding cross-package boundary violations...")
    boundary_violations = find_boundary_violations(nodes, edges)
    pkg_pairs = defaultdict(int)
    for v in boundary_violations:
        key = "%s -> %s" % (v["from_pkg"], v["to_pkg"])
        pkg_pairs[key] += 1
    print("[DIAG]   Found %d cross-package imports across %d package pairs" % (len(boundary_violations), len(pkg_pairs)))

    print("[DIAG] 8/10 Finding test coverage gaps...")
    test_gaps = find_test_coverage_gaps(nodes, edges)
    print("[DIAG]   Found %d modules without test imports" % len(test_gaps))

    print("[DIAG] 9/10 Finding stability violations...")
    stability_violations = find_stability_violations(nodes, edges)
    print("[DIAG]   Found %d stability violations" % len(stability_violations))

    print("[DIAG] 10/10 Finding AI_AUTONOMY violations...")
    autonomy_violations = find_autonomy_violations(nodes, edges)
    print("[DIAG]   Found %d AI_AUTONOMY violations" % len(autonomy_violations))

    report = {
        "metadata": {
            "diagnosis_version": "2.1.0",
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
                "by_gap": dict(defaultdict(int, {gap: sum(1 for r in cross_layer if r["gap"] == gap) for gap in set(r["gap"] for r in cross_layer)})),
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
            "stability_violations": {"count": len(stability_violations), "sample": stability_violations[:30]},
            "autonomy_violations": {"count": len(autonomy_violations), "sample": autonomy_violations[:30]},
        },
    }

    if args.output:
        import yaml
        out_path = PROJECT_ROOT / args.output
        tmp_path = str(out_path) + ".%d.tmp" % os.getpid()
        with open(tmp_path, "w", encoding="utf-8") as f:
            yaml.dump(report, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        os.replace(tmp_path, str(out_path))
        print("[DIAG] Report written to %s" % args.output)

    print()
    print("=" * 60)
    print("DIAGNOSIS SUMMARY (v2.2.0)")
    print("=" * 60)
    print("  Empty blueprint_id:     %d" % len(empty_bp))
    print("  Orphan nodes:           %d" % len(orphans))
    print("  Circular dependencies:  %d (true: %d | event-driven: %d | false+: %d | bidir: %d)" % (
        len(cycles), len(true_cycles), len(event_driven), len(false_positives), len(bidirectional)))
    print("  Cross-layer refs:       %d" % len(cross_layer))
    print("  Deep chains (>=4):      %d" % len(deep_chains))
    print("  God modules (out>=15):  %d" % len(god_out))
    print("  God modules (in>=15):   %d" % len(god_in))
    print("  Cross-pkg violations:   %d" % len(boundary_violations))
    print("  Package pairs:          %d" % len(pkg_pairs))
    print("  Test coverage gaps:     %d" % len(test_gaps))
    print("  Stability violations:   %d" % len(stability_violations))
    print("  Autonomy violations:    %d" % len(autonomy_violations))
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
