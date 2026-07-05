# [BLUEPRINT] MOD-GOV-SCRIPTS | docs/03_modules/_domain_governance/blueprint.md | §decisiongraph
# [MODULE] scripts.governance.extract_decisiongraph
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.__init__; zephyr.governance.persistence.decision_graph_reader (DecisionGraphReader); zephyr.governance.persistence.decisiongraph_schema (get_decisiongraph_pg_connection)
# [CONSUMERS] 所有需要读取 decisiongraph 的 AI session
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 只读查询; 禁止 AI 直接 Read 大表; 提取输出必须可被 AI 安全消费
# [MODIFY-GUARD] 对标 scripts/governance/extract_depgraph.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 连接失败->exit 1; 参数无效->exit 3
# [TESTS] tests/test_extract_decisiongraph.py
# [TTL] task_bound
"""
extract_decisiongraph - decisiongraph on-demand extraction tool

Usage:
  python scripts/governance/extract_decisiongraph.py --summary
  python scripts/governance/extract_decisiongraph.py --layers
  python scripts/governance/extract_decisiongraph.py --layers L0,L1 --track model_driven
  python scripts/governance/extract_decisiongraph.py --nodes
  python scripts/governance/extract_decisiongraph.py --nodes 1,2,3 --layer L0 --type signal
  python scripts/governance/extract_decisiongraph.py --edges --type approving
  python scripts/governance/extract_decisiongraph.py --tracks
  python scripts/governance/extract_decisiongraph.py --invariants
  python scripts/governance/extract_decisiongraph.py --stats
  python scripts/governance/extract_decisiongraph.py --summary --output result.json
"""

from __future__ import annotations

__manifest__ = """
args: []
description: decisiongraph on-demand extraction tool
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""

import argparse
import datetime
import decimal
import json
import sys
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))
from _shared.file_utils import atomic_write_safe  # noqa: E402

from zephyr.governance.persistence.decision_graph_reader import DecisionGraphReader  # noqa: E402
from zephyr.governance.persistence.decisiongraph_schema import (  # noqa: E402
    get_decisiongraph_pg_connection,
)


class _CustomEncoder(json.JSONEncoder):
    """Handle non-JSON-serializable types found in decisiongraph."""

    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super().default(obj)


def _write_decision_output(data, output_path):
    """Atomically write output (RULE-ONE) - decisiongraph-specific name to avoid FUNCTION-DUP."""
    content = json.dumps(data, ensure_ascii=False, indent=2, cls=_CustomEncoder)
    if output_path:
        if atomic_write_safe(output_path, content):
            print(f"Output written to: {output_path}", file=sys.stderr)
    else:
        print(content)


def cmd_summary(reader, output):
    """Decision graph summary: layers + nodes + edges + tracks + invariant violations."""
    layer_count = reader.get_layer_count()
    node_count = reader.get_node_count()
    edge_count = reader.get_edge_count()
    track_count = reader.get_track_count()

    nodes_by_layer = reader.get_node_count_by_layer()
    edges_by_type = reader.get_edge_count_by_type()

    order_violations = len(reader.find_order_nodes_without_risk_approving())
    signal_order_violations = len(reader.find_signal_to_order_direct_edges())
    missing_evidence = len(reader.find_nodes_missing_evidence_hash())

    result = {
        "total_layers": layer_count,
        "total_nodes": node_count,
        "total_edges": edge_count,
        "total_tracks": track_count,
        "nodes_by_layer": nodes_by_layer,
        "edges_by_type": edges_by_type,
        "invariant_violations": {
            "DEC-INV-001_risk_veto": order_violations,
            "DEC-INV-002_signal_order_separation": signal_order_violations,
            "DEC-INV-005_evidence_hash_required": missing_evidence,
            "total": order_violations + signal_order_violations + missing_evidence,
        },
    }
    _write_decision_output(result, output)


def cmd_layers(reader, layer_ids, track, output):
    """Query decision layers."""
    if layer_ids:
        result = []
        for lid in layer_ids:
            row = reader.get_layer_by_id(lid)
            if row is None:
                print(f"WARNING: Layer '{lid}' not found", file=sys.stderr)
            else:
                result.append(row)
    elif track:
        result = reader.get_layers_by_track(track)
    else:
        result = reader.get_all_layers()
    _write_decision_output(result, output)


def cmd_nodes(reader, node_ids, layer_id, node_type, module_id, build_status, output):
    """Query decision nodes."""
    if node_ids:
        result = []
        for nid in node_ids:
            row = reader.get_node_by_id(nid)
            if row is None:
                print(f"WARNING: Node {nid} not found", file=sys.stderr)
            else:
                result.append(row)
    elif layer_id:
        result = reader.get_nodes_by_layer(layer_id)
    elif node_type:
        result = reader.get_nodes_by_type(node_type)
    elif module_id:
        result = reader.get_nodes_by_module_id(module_id)
    elif build_status:
        result = reader.get_nodes_by_build_status(build_status)
    else:
        result = reader.get_all_nodes()
    _write_decision_output(result, output)


def cmd_edges(reader, edge_ids, edge_type, track, from_node, to_node, output):
    """Query decision edges."""
    if edge_ids:
        result = []
        for eid in edge_ids:
            row = reader.get_edge_by_id(eid)
            if row is None:
                print(f"WARNING: Edge {eid} not found", file=sys.stderr)
            else:
                result.append(row)
    elif edge_type:
        result = reader.get_edges_by_type(edge_type)
    elif track:
        result = reader.get_edges_by_track(track)
    elif from_node is not None:
        result = reader.get_edges_from_node(from_node)
    elif to_node is not None:
        result = reader.get_edges_to_node(to_node)
    else:
        result = reader.get_all_edges()
    _write_decision_output(result, output)


def cmd_tracks(reader, output):
    """Query four tracks."""
    result = reader.get_all_tracks()
    _write_decision_output(result, output)


def cmd_invariants(reader, output):
    """Five invariant check report (DEC-INV-001~005)."""
    order_violations = reader.find_order_nodes_without_risk_approving()
    signal_order_edges = reader.find_signal_to_order_direct_edges()
    missing_evidence = reader.find_nodes_missing_evidence_hash()

    result = {
        "DEC-INV-001_risk_veto": {
            "description": "order nodes must have at least one approving edge from risk_check",
            "violations": len(order_violations),
            "violating_nodes": order_violations,
        },
        "DEC-INV-002_signal_order_separation": {
            "description": "signal nodes cannot directly connect to order nodes",
            "violations": len(signal_order_edges),
            "violating_edges": signal_order_edges,
        },
        "DEC-INV-003_dag_no_cycle": {
            "description": "No cycles in graph (Tarjan SCC, checked by apply_decisiongraph.py)",
            "violations": None,
            "note": "Checked at write time by apply_decisiongraph.py",
        },
        "DEC-INV-004_time_monotonicity": {
            "description": "forall (u,v) in E, tau(u) <= tau(v)",
            "violations": None,
            "note": "Enforced by DB CHECK constraint",
        },
        "DEC-INV-005_evidence_hash_required": {
            "description": "Every node must have evidence_hash",
            "violations": len(missing_evidence),
            "violating_nodes": missing_evidence,
        },
    }
    total = sum(v["violations"] for v in result.values() if isinstance(v["violations"], int))
    result["_total_violations"] = total
    _write_decision_output(result, output)


def cmd_stats(output):
    """Database statistics."""
    conn = get_decisiongraph_pg_connection(autocommit=True)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT pg_database_size(current_database()) AS sz")
            size_bytes = cur.fetchone()["sz"]
            cur.execute("SELECT COUNT(*) AS cnt FROM decision_layers")
            layer_count = cur.fetchone()["cnt"]
            cur.execute("SELECT COUNT(*) AS cnt FROM decision_nodes")
            node_count = cur.fetchone()["cnt"]
            cur.execute("SELECT COUNT(*) AS cnt FROM decision_edges")
            edge_count = cur.fetchone()["cnt"]
            cur.execute("SELECT COUNT(*) AS cnt FROM decision_tracks")
            track_count = cur.fetchone()["cnt"]
    finally:
        conn.close()

    result = {
        "database": "PostgreSQL (shared with depgraph)",
        "size_mb": round(size_bytes / 1024 / 1024, 1),
        "size_bytes": size_bytes,
        "layer_count": layer_count,
        "node_count": node_count,
        "edge_count": edge_count,
        "track_count": track_count,
        "estimated_tokens": size_bytes // 3,
    }
    _write_decision_output(result, output)


def main():
    parser = argparse.ArgumentParser(
        description="decisiongraph on-demand extraction tool",
    )
    parser.add_argument("--summary", action="store_true", help="Decision graph summary")
    parser.add_argument("--layers", type=str, nargs="?", const="ALL",
                        help="Query layers (no arg=all, or comma-separated layer_id)")
    parser.add_argument("--track", type=str,
                        help="Filter by track (model_driven/data_driven/human_override/emergency)")
    parser.add_argument("--nodes", type=str, nargs="?", const="ALL",
                        help="Query nodes (no arg=all, or comma-separated node_id)")
    parser.add_argument("--layer", type=str, help="Filter nodes by layer_id")
    parser.add_argument("--type", type=str, help="Filter by node_type or edge_type")
    parser.add_argument("--module_id", type=str, help="Filter nodes by module_id")
    parser.add_argument("--build_status", type=str,
                        help="Filter by build_status (planned/generated/testing/stable/deprecated)")
    parser.add_argument("--edges", type=str, nargs="?", const="ALL",
                        help="Query edges (no arg=all, or comma-separated edge_id)")
    parser.add_argument("--from", dest="from_node", type=int, help="Filter edges by from_node_id")
    parser.add_argument("--to", dest="to_node", type=int, help="Filter edges by to_node_id")
    parser.add_argument("--tracks", action="store_true", help="Query four tracks")
    parser.add_argument("--invariants", action="store_true", help="Invariant check report")
    parser.add_argument("--stats", action="store_true", help="Database statistics")
    parser.add_argument("--output", type=str, help="Output to JSON file (default stdout)")
    args = parser.parse_args()

    if not any([
        args.summary, args.layers, args.nodes, args.edges, args.tracks,
        args.invariants, args.stats,
    ]):
        parser.print_help()
        print("\nERROR: Must specify at least one extraction mode.", file=sys.stderr)
        sys.exit(3)

    if args.stats:
        cmd_stats(args.output)
        return

    reader = DecisionGraphReader()
    try:
        if args.summary:
            cmd_summary(reader, args.output)

        if args.layers is not None:
            if args.layers == "ALL":
                cmd_layers(reader, None, args.track, args.output)
            else:
                layer_ids = [lid.strip() for lid in args.layers.split(",")]
                cmd_layers(reader, layer_ids, args.track, args.output)

        if args.nodes is not None:
            if args.nodes == "ALL":
                cmd_nodes(reader, None, args.layer, args.type,
                          args.module_id, args.build_status, args.output)
            else:
                try:
                    node_ids = [int(n.strip()) for n in args.nodes.split(",")]
                except ValueError:
                    print("ERROR: --nodes requires integer node_id list", file=sys.stderr)
                    sys.exit(3)
                cmd_nodes(reader, node_ids, None, None, None, None, args.output)

        if args.edges is not None:
            if args.edges == "ALL":
                cmd_edges(reader, None, args.type, args.track,
                          args.from_node, args.to_node, args.output)
            else:
                try:
                    edge_ids = [int(e.strip()) for e in args.edges.split(",")]
                except ValueError:
                    print("ERROR: --edges requires integer edge_id list", file=sys.stderr)
                    sys.exit(3)
                cmd_edges(reader, edge_ids, None, None, None, None, args.output)

        if args.tracks:
            cmd_tracks(reader, args.output)

        if args.invariants:
            cmd_invariants(reader, args.output)
    finally:
        reader.close()


if __name__ == "__main__":
    main()
