# [BLUEPRINT] MOD-GOV-SCRIPTS-ARCH | scripts/governance/generate_project_depgraph_artifact.py | §cqrs-read-model
# [MODULE] scripts.governance.generate_project_depgraph_artifact
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] scripts.governance._shared.constants
# [CONSUMERS] .pre_commit-config.yaml; src/zephyr/governance/audit_trail/pipeline_runner.py; src/zephyr/security/access_control/orphan_judge/registration_checker.py
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读DB(零DELETE/UPDATE/INSERT);CQRS读模型;制品是DB的派生投影
# [MODIFY-GUARD] 裁定#207 R2——职责分离治本，禁止添加任何DB写操作
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=成功; exit 1=文件写入失败; exit 2=DB错误/参数错误
# [TESTS] tests/unit/test_generate_project_depgraph_artifact.py
"""generate_project_depgraph_artifact.py — 只读制品生成器（裁定#207 R2 CQRS 职责分离）。

将 depgraph.db 的数据导出为 project_entity_depgraph.yaml 制品。
**只读 DB**：零 DELETE/UPDATE/INSERT，纯 SELECT 投影。
制品是 DB 的派生读模型（CQRS），重生制品不应破坏写模型（DB）。

对标 generate_target_path_tree.py 的只读范式：
  - 默认 stdout 打印（安全，可随时跑）
  - --write 原子写入 data/asset_index/
  - --check 只读校验现有文件与 DB 对齐

裁定#207 R2 治本：
  - R2-1 职责分离：本脚本只读 DB 生成 yaml，不碰 write_depgraph_to_db
  - R2-2 制品安全重生：阶段B/C/D后用本脚本重生制品，不触发DB重建
  - 原 generate_project_depgraph.py 的破坏性重建逻辑需 --force（见 rebuild 门禁）

用法::

    # 默认：stdout 打印（安全预览）
    python scripts/governance/generate_project_depgraph_artifact.py

    # 写入制品文件
    python scripts/governance/generate_project_depgraph_artifact.py --write

    # 校验现有制品与 DB 对齐
    python scripts/governance/generate_project_depgraph_artifact.py --check

exit codes: 0=成功, 1=文件写入失败, 2=DB错误/参数错误
"""

from __future__ import annotations

import argparse
import datetime
import os
import sqlite3
import sys
from pathlib import Path

import yaml

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import DEPGRAPH_DB_PATH  # noqa: E402

_PROJECT_ROOT = _THIS_FILE.parents[2]
OUTPUT_PATH = _PROJECT_ROOT / "data" / "asset_index" / "project_entity_depgraph.yaml"


# ---------------------------------------------------------------------------
# 只读 DB 加载（零写操作）
# ---------------------------------------------------------------------------

def load_nodes_from_db(conn: sqlite3.Connection) -> dict[str, dict]:
    """从 nodes 表加载，返回 {node_id: {type, path, ...}}。

    字段重命名：node_type → type（兼容 YAML 制品格式）。
    """
    conn.row_factory = sqlite3.Row
    nodes: dict[str, dict] = {}
    for row in conn.execute("SELECT * FROM nodes"):
        node = dict(row)
        nid = str(node.pop("node_id"))
        # node_type → type（YAML 制品兼容）
        node["type"] = node.pop("node_type", "")
        nodes[nid] = node
    return nodes


def load_edges_from_db(conn: sqlite3.Connection) -> list[dict]:
    """从 edges 表加载，返回 [{from, to, dep_type, ...}]。

    字段重命名：from_node_id → from, to_node_id → to（兼容 YAML 制品格式）。
    """
    conn.row_factory = sqlite3.Row
    edges: list[dict] = []
    for row in conn.execute("SELECT * FROM edges"):
        edge = dict(row)
        edge["from"] = str(edge.pop("from_node_id", ""))
        edge["to"] = str(edge.pop("to_node_id", ""))
        edge.pop("edge_id", None)
        edges.append(edge)
    return edges


def load_domains_from_db(conn: sqlite3.Connection) -> list[dict]:
    """从 domains 表加载功能域列表。"""
    conn.row_factory = sqlite3.Row
    return [dict(row) for row in conn.execute("SELECT * FROM domains ORDER BY domain_id")]


def load_hard_boundaries_from_db(conn: sqlite3.Connection) -> list[dict]:
    """从 hard_boundaries 表加载硬边界列表。"""
    conn.row_factory = sqlite3.Row
    return [dict(row) for row in conn.execute("SELECT * FROM hard_boundaries ORDER BY boundary_id")]


def load_arch_constraints_from_db(conn: sqlite3.Connection) -> dict:
    """从 arch_constraints 表加载架构约束，按 constraint_type 分组。"""
    conn.row_factory = sqlite3.Row
    result: dict[str, list[dict]] = {}
    for row in conn.execute("SELECT * FROM arch_constraints ORDER BY constraint_id"):
        entry = dict(row)
        cat = entry.get("constraint_type", "general")
        result.setdefault(cat, []).append(entry)
    return result


def load_path_mappings_from_db(conn: sqlite3.Connection) -> list[dict]:
    """从 arch_path_mappings 表加载路径映射（active 条目）。"""
    conn.row_factory = sqlite3.Row
    return [
        dict(row)
        for row in conn.execute(
            "SELECT * FROM arch_path_mappings WHERE state='active' ORDER BY domain_id"
        )
    ]


# ---------------------------------------------------------------------------
# 派生计算（纯计算，不碰 DB）
# ---------------------------------------------------------------------------

def build_adjacency_lists(edges: list[dict]) -> dict[str, list]:
    """从 edges 构建邻接表 {outgoing: {from_id: [to_id, ...]}, incoming: {to_id: [from_id, ...]}}。"""
    outgoing: dict[str, list[str]] = {}
    incoming: dict[str, list[str]] = {}
    for edge in edges:
        f = str(edge.get("from", ""))
        t = str(edge.get("to", ""))
        if f and t:
            outgoing.setdefault(f, []).append(t)
            incoming.setdefault(t, []).append(f)
    return {"outgoing": outgoing, "incoming": incoming}


def build_blueprint_file_map(nodes: dict[str, dict]) -> dict[str, list[str]]:
    """从 nodes 构建 {blueprint_id: [file_paths]} 映射。"""
    result: dict[str, list[str]] = {}
    for node_data in nodes.values():
        bp = node_data.get("blueprint_id", "")
        path = node_data.get("path", "")
        if bp and path:
            result.setdefault(bp, []).append(path)
    return result


def find_orphan_nodes(nodes: dict[str, dict], edges: list[dict]) -> list[str]:
    """找出无任何边的孤立节点 ID 列表。"""
    connected = set()
    for edge in edges:
        f = str(edge.get("from", ""))
        t = str(edge.get("to", ""))
        if f:
            connected.add(f)
        if t:
            connected.add(t)
    return sorted(nid for nid in nodes if nid not in connected)


def compute_graph_metrics(nodes: dict[str, dict], edges: list[dict]) -> dict:
    """计算图度量。"""
    by_type: dict[str, int] = {}
    by_maturity: dict[str, int] = {}
    for node_data in nodes.values():
        t = node_data.get("type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
        m = node_data.get("design_maturity", "unknown")
        by_maturity[m] = by_maturity.get(m, 0) + 1
    return {
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "nodes_by_type": by_type,
        "nodes_by_maturity": by_maturity,
        "orphan_count": len(find_orphan_nodes(nodes, edges)),
    }


def build_metadata(nodes: dict, edges: list, domains: list) -> dict:
    """构建制品元数据。"""
    now = datetime.datetime.now().isoformat()
    by_type: dict[str, int] = {}
    for nd in nodes.values():
        t = nd.get("type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
    design_count = sum(1 for nd in nodes.values() if nd.get("design_maturity") == "design")
    prod_count = sum(1 for nd in nodes.values() if nd.get("design_maturity") == "production")
    return {
        "graph_id": "PROJECT-ENTITY-DEPGRAPH-001",
        "version": "4.0.0",
        "granularity": "system",
        "generated_at": now,
        "generated_by": "generate_project_depgraph_artifact.py",
        "source": "depgraph.db (read-only CQRS projection, 裁定#207 R2)",
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "total_functional_domains": len(domains),
        "design_state_nodes": design_count,
        "operational_state_nodes": prod_count,
        "scope": "Project entity dependency graph (CQRS read model, DB projection)",
        "nodes_by_type": by_type,
    }


def build_completeness_declaration(nodes: dict, edges: list) -> dict:
    """构建完整性声明。"""
    return {
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "orphan_nodes": len(find_orphan_nodes(nodes, edges)),
        "source": "depgraph.db",
        "method": "read-only CQRS projection (裁定#207 R2)",
    }


# ---------------------------------------------------------------------------
# 制品组装 + 输出
# ---------------------------------------------------------------------------

def build_artifact(db_path: Path) -> dict:
    """从 DB 构建完整制品 dict（只读，零副作用）。"""
    conn = sqlite3.connect(str(db_path))
    try:
        nodes = load_nodes_from_db(conn)
        edges = load_edges_from_db(conn)
        domains = load_domains_from_db(conn)
        hard_boundaries = load_hard_boundaries_from_db(conn)
        arch_constraints = load_arch_constraints_from_db(conn)
        path_mappings = load_path_mappings_from_db(conn)
    finally:
        conn.close()

    return {
        "metadata": build_metadata(nodes, edges, domains),
        "hard_boundaries": hard_boundaries,
        "nodes": nodes,
        "edges": edges,
        "adjacency_lists": build_adjacency_lists(edges),
        "functional_domains": domains,
        "blueprint_file_map": build_blueprint_file_map(nodes),
        "orphan_nodes": find_orphan_nodes(nodes, edges),
        "completeness_declaration": build_completeness_declaration(nodes, edges),
        "graph_metrics": compute_graph_metrics(nodes, edges),
        "architecture_constraints": arch_constraints,
        "path_mappings": path_mappings,
    }


def cmd_write(db_path: Path, out_path: Path) -> int:
    """原子写入制品文件。"""
    artifact = build_artifact(db_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_suffix(f".{os.getpid()}.tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            yaml.dump(
                artifact,
                f,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False,
                width=120,
            )
        os.replace(tmp_path, str(out_path))
    except Exception as e:
        if tmp_path.exists():
            tmp_path.unlink()
        print(f"ERROR: 写入失败: {e}", file=sys.stderr)
        return 1
    print(f"OK: 制品已写入 {out_path}", file=sys.stderr)
    print(f"  nodes: {len(artifact['nodes'])}", file=sys.stderr)
    print(f"  edges: {len(artifact['edges'])}", file=sys.stderr)
    print(f"  domains: {len(artifact['functional_domains'])}", file=sys.stderr)
    return 0


def cmd_check(db_path: Path, out_path: Path) -> int:
    """校验现有制品与 DB 对齐（只读）。"""
    if not out_path.is_file():
        print(f"[FAIL] 制品文件不存在: {out_path}", file=sys.stderr)
        return 1
    # 加载现有制品
    with open(out_path, encoding="utf-8") as f:
        existing = yaml.safe_load(f)
    if not isinstance(existing, dict):
        print(f"[FAIL] 制品格式无效", file=sys.stderr)
        return 1
    # 从 DB 构建当前状态
    db_artifact = build_artifact(db_path)
    # 对比关键计数
    mismatches = []
    ex_nodes = len(existing.get("nodes", {}))
    db_nodes = len(db_artifact["nodes"])
    if ex_nodes != db_nodes:
        mismatches.append(f"nodes: 制品={ex_nodes} DB={db_nodes}")
    ex_edges = len(existing.get("edges", []))
    db_edges = len(db_artifact["edges"])
    if ex_edges != db_edges:
        mismatches.append(f"edges: 制品={ex_edges} DB={db_edges}")
    ex_domains = len(existing.get("functional_domains", []))
    db_domains = len(db_artifact["functional_domains"])
    if ex_domains != db_domains:
        mismatches.append(f"domains: 制品={ex_domains} DB={db_domains}")

    if mismatches:
        print(f"[FAIL] 制品与 DB 不一致:", file=sys.stderr)
        for m in mismatches:
            print(f"  {m}", file=sys.stderr)
        return 1
    print(f"[PASS] 制品与 DB 对齐 (nodes={db_nodes}, edges={db_edges}, domains={db_domains})")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="generate_project_depgraph_artifact.py",
        description="只读制品生成器（裁定#207 R2 CQRS）——depgraph.db → project_entity_depgraph.yaml",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--write",
        action="store_true",
        help="原子写入制品文件到 data/asset_index/project_entity_depgraph.yaml",
    )
    group.add_argument(
        "--check",
        action="store_true",
        help="只读校验现有制品与 DB 对齐情况",
    )
    parser.add_argument(
        "--db-path",
        default=str(DEPGRAPH_DB_PATH),
        help="depgraph.db 路径",
    )
    parser.add_argument(
        "--output",
        default=str(OUTPUT_PATH),
        help="制品输出路径（默认: data/asset_index/project_entity_depgraph.yaml）",
    )
    args = parser.parse_args()

    db_path = Path(args.db_path)
    if not db_path.exists():
        print(f"ERROR: DB not found: {db_path}", file=sys.stderr)
        return 2

    out_path = Path(args.output)

    if args.write:
        return cmd_write(db_path, out_path)
    elif args.check:
        return cmd_check(db_path, out_path)
    else:
        # 默认：stdout 打印（安全预览）
        artifact = build_artifact(db_path)
        yaml.dump(
            artifact,
            sys.stdout,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            width=120,
        )
        return 0


if __name__ == "__main__":
    sys.exit(main())
