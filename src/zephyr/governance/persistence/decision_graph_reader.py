# [BLUEPRINT] SH-DB-002 | docs/03_modules/_cross_layer/database/blueprint.md | §decisiongraph
# [MODULE] zephyr.governance.persistence.decision_graph_reader
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.persistence.decisiongraph_schema (get_decisiongraph_pg_connection); psycopg2
# [CONSUMERS] scripts/governance/extract_decisiongraph.py; scripts/governance/apply_decisiongraph.py; scripts/governance/generate_decision_graph.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 只读查询; 参数化防注入; 懒加载连接; 与 depgraph 共享 PG 实例（不同表）
# [MODIFY-GUARD] 修改需同步更新 tests/test_decision_graph_reader.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 连接失败抛 RuntimeError; 查询失败抛 psycopg2.Error
# [TESTS] tests/test_decision_graph_reader.py
# [TTL] permanent
"""
decision_graph_reader.py — 决策流图数据库只读查询工具模块

[BLUEPRINT] SH-DB-002 | src/zephyr/governance/persistence/decision_graph_reader.py | §decisiongraph
[MODULE] zephyr.governance.persistence.decision_graph_reader
[INVARIANTS] 只读查询; 参数化防注入; 懒加载连接; JSONB 字段自动解析
[MODIFY-GUARD] 修改需同步更新 tests/test_decision_graph_reader.py
[CONSUMERS] scripts/governance/extract_decisiongraph.py; scripts/governance/apply_decisiongraph.py
[STABILITY] evolving
[SAFETY] M
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] 连接失败抛 RuntimeError; 查询失败抛 psycopg2.Error
[TESTS] tests/test_decision_graph_reader.py

提供从 decisiongraph (PostgreSQL) 读取决策流图数据的统一接口，
替代直接查询 4 张 decision_* 表的方式。

4 张表：
  - decision_layers   — 决策层（L0-L6，10列）
  - decision_nodes    — 决策节点（16列，JSONB inputs/outputs/conditions/facets）
  - decision_edges    — 决策边（9列，4种 edge_type）
  - decision_tracks   — 四轨（战略/战役/战术/操作）

与 DepgraphReader 的关系：
  - 复用同一 PostgreSQL 实例（不同表前缀 decision_*）
  - 连接由 decisiongraph_schema.get_decisiongraph_pg_connection() 派生
  - 设计模式与 DepgraphReader 完全一致（_PgConnExecuteWrapper + 懒加载）

使用方式：
    from zephyr.governance.persistence.decision_graph_reader import DecisionGraphReader
    reader = DecisionGraphReader()
    layers = reader.get_layers_by_track('model_driven')
    nodes = reader.get_nodes_by_layer('L0')
    edges = reader.get_edges_from_node(42)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor

from zephyr.governance.persistence.decisiongraph_schema import (
    get_decisiongraph_pg_connection,
)


# class-name-alias: 复用 depgraph_reader.py 的 psycopg2 execute() 兼容包装器模式（同库不同表，设计同源）
class _PgConnExecuteWrapper:
    """兼容 sqlite3.Connection.execute() 接口的 psycopg2 connection 包装器。

    与 DepgraphReader._PgConnExecuteWrapper 同源设计：
    psycopg2 connection 没有 execute() 方法，此包装器使查询代码无需修改。
    每次调用 execute() 创建一个新的 RealDictCursor（与 sqlite3.Row 的 dict(row) 用法等价）。
    """

    def __init__(self, pg_conn: psycopg2.extensions.connection) -> None:
        self._pg_conn = pg_conn

    def execute(self, sql: str, params: tuple = ()) -> Any:
        cur = self._pg_conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql, params)
        return cur

    def close(self) -> None:
        self._pg_conn.close()


# JSONB 字段名（自动解析为 dict/list）
_JSONB_NODE_FIELDS = ("inputs", "outputs", "conditions", "facets")
_JSONB_EDGE_FIELDS = ("evidence_bundle",)


def _parse_jsonb(row: dict, fields: tuple[str, ...]) -> dict:
    """将 JSONB 字段从字符串解析为 Python 对象（原地修改 row）。"""
    for f in fields:
        v = row.get(f)
        if isinstance(v, str) and v:
            try:
                row[f] = json.loads(v)
            except (json.JSONDecodeError, TypeError):
                pass  # 保留原字符串
    return row


class DecisionGraphReader:
    """决策流图数据库只读读取器。

    懒加载连接，可作 context manager 使用：
        with DecisionGraphReader() as reader:
            layers = reader.get_all_layers()
    """

    def __init__(self, db_path: str | Path | None = None) -> None:
        # db_path 保留向后兼容（PG 模式下由 decisiongraph_schema 管理连接配置）
        self._conn: _PgConnExecuteWrapper | None = None

    def _get_conn(self) -> _PgConnExecuteWrapper:
        if self._conn is None:
            self._conn = _PgConnExecuteWrapper(
                get_decisiongraph_pg_connection(autocommit=True)
            )
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> DecisionGraphReader:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    # ── 层查询 ────────────────────────────────────────────────

    def get_all_layers(self) -> list[dict[str, Any]]:
        """获取所有决策层（按 layer_id 排序）。"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM decision_layers ORDER BY layer_id")
        return [dict(row) for row in cursor.fetchall()]

    def get_layer_by_id(self, layer_id: str) -> dict[str, Any] | None:
        """按 layer_id 精确查询决策层。"""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM decision_layers WHERE layer_id = %s", (layer_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_layers_by_track(self, track: str) -> list[dict[str, Any]]:
        """按 track（model_driven/data_driven/human_override/emergency）查询层。"""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM decision_layers WHERE track = %s ORDER BY layer_id",
            (track,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_layers_by_build_status(self, build_status: str) -> list[dict[str, Any]]:
        """按 build_status（planned/generated/testing/stable/deprecated）查询层。"""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM decision_layers WHERE build_status = %s ORDER BY layer_id",
            (build_status,),
        )
        return [dict(row) for row in cursor.fetchall()]

    # ── 节点查询 ──────────────────────────────────────────────

    def get_all_nodes(self) -> list[dict[str, Any]]:
        """获取所有决策节点（自动解析 JSONB 字段）。"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM decision_nodes ORDER BY node_id")
        return [
            _parse_jsonb(dict(row), _JSONB_NODE_FIELDS) for row in cursor.fetchall()
        ]

    def get_node_by_id(self, node_id: int) -> dict[str, Any] | None:
        """按 node_id（BIGINT）精确查询节点（自动解析 JSONB）。"""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM decision_nodes WHERE node_id = %s", (node_id,)
        )
        row = cursor.fetchone()
        return _parse_jsonb(dict(row), _JSONB_NODE_FIELDS) if row else None

    def get_node_by_path(self, path: str) -> dict[str, Any] | None:
        """按 path（UNIQUE）精确查询节点（自动解析 JSONB）。"""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM decision_nodes WHERE path = %s", (path,)
        )
        row = cursor.fetchone()
        return _parse_jsonb(dict(row), _JSONB_NODE_FIELDS) if row else None

    def get_nodes_by_layer(self, layer_id: str) -> list[dict[str, Any]]:
        """按 layer_id 查询节点（自动解析 JSONB）。"""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM decision_nodes WHERE layer_id = %s ORDER BY node_id",
            (layer_id,),
        )
        return [
            _parse_jsonb(dict(row), _JSONB_NODE_FIELDS) for row in cursor.fetchall()
        ]

    def get_nodes_by_type(self, node_type: str) -> list[dict[str, Any]]:
        """按 node_type（signal/portfolio_target/risk_check/order/...）查询节点。"""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM decision_nodes WHERE node_type = %s ORDER BY node_id",
            (node_type,),
        )
        return [
            _parse_jsonb(dict(row), _JSONB_NODE_FIELDS) for row in cursor.fetchall()
        ]

    def get_nodes_by_module_id(self, module_id: str) -> list[dict[str, Any]]:
        """按 module_id 查询节点（与 depgraph.nodes.blueprint_id 关联）。

        三张图正交关联点：decision_nodes.module_id ↔ depgraph.nodes.blueprint_id
        """
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM decision_nodes WHERE module_id = %s ORDER BY node_id",
            (module_id,),
        )
        return [
            _parse_jsonb(dict(row), _JSONB_NODE_FIELDS) for row in cursor.fetchall()
        ]

    def get_nodes_by_build_status(self, build_status: str) -> list[dict[str, Any]]:
        """按 build_status 查询节点。"""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM decision_nodes WHERE build_status = %s ORDER BY node_id",
            (build_status,),
        )
        return [
            _parse_jsonb(dict(row), _JSONB_NODE_FIELDS) for row in cursor.fetchall()
        ]

    # ── 边查询 ────────────────────────────────────────────────

    def get_all_edges(self) -> list[dict[str, Any]]:
        """获取所有决策边（自动解析 JSONB evidence_bundle）。"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM decision_edges ORDER BY edge_id")
        return [
            _parse_jsonb(dict(row), _JSONB_EDGE_FIELDS) for row in cursor.fetchall()
        ]

    def get_edge_by_id(self, edge_id: int) -> dict[str, Any] | None:
        """按 edge_id 精确查询边。"""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM decision_edges WHERE edge_id = %s", (edge_id,)
        )
        row = cursor.fetchone()
        return _parse_jsonb(dict(row), _JSONB_EDGE_FIELDS) if row else None

    def get_edges_from_node(self, from_node_id: int) -> list[dict[str, Any]]:
        """查询从指定节点出发的所有边。"""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM decision_edges WHERE from_node_id = %s ORDER BY edge_id",
            (from_node_id,),
        )
        return [
            _parse_jsonb(dict(row), _JSONB_EDGE_FIELDS) for row in cursor.fetchall()
        ]

    def get_edges_to_node(self, to_node_id: int) -> list[dict[str, Any]]:
        """查询指向指定节点的所有边。"""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM decision_edges WHERE to_node_id = %s ORDER BY edge_id",
            (to_node_id,),
        )
        return [
            _parse_jsonb(dict(row), _JSONB_EDGE_FIELDS) for row in cursor.fetchall()
        ]

    def get_edges_by_type(self, edge_type: str) -> list[dict[str, Any]]:
        """按 edge_type（triggering/informing/constraining/approving）查询边。"""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM decision_edges WHERE edge_type = %s ORDER BY edge_id",
            (edge_type,),
        )
        return [
            _parse_jsonb(dict(row), _JSONB_EDGE_FIELDS) for row in cursor.fetchall()
        ]

    def get_edges_by_track(self, track: str) -> list[dict[str, Any]]:
        """按 track 查询边（与 decision_tracks.track_id 关联）。"""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM decision_edges WHERE track = %s ORDER BY edge_id",
            (track,),
        )
        return [
            _parse_jsonb(dict(row), _JSONB_EDGE_FIELDS) for row in cursor.fetchall()
        ]

    # ── 轨查询 ────────────────────────────────────────────────

    def get_all_tracks(self) -> list[dict[str, Any]]:
        """获取所有决策轨（按 priority 排序）。"""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM decision_tracks ORDER BY priority"
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_track_by_id(self, track_id: str) -> dict[str, Any] | None:
        """按 track_id 精确查询轨。"""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM decision_tracks WHERE track_id = %s", (track_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    # ── 图拓扑查询 ──────────────────────────────────────────────

    def get_adjacency_forward(self) -> dict[int, list[int]]:
        """构建前向邻接表 {from_node_id: [to_node_id, ...]}。"""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT from_node_id, to_node_id FROM decision_edges ORDER BY from_node_id"
        )
        adj: dict[int, list[int]] = {}
        for row in cursor.fetchall():
            r = dict(row)
            adj.setdefault(r["from_node_id"], []).append(r["to_node_id"])
        return adj

    def get_adjacency_reverse(self) -> dict[int, list[int]]:
        """构建反向邻接表 {to_node_id: [from_node_id, ...]}。"""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT from_node_id, to_node_id FROM decision_edges ORDER BY to_node_id"
        )
        adj: dict[int, list[int]] = {}
        for row in cursor.fetchall():
            r = dict(row)
            adj.setdefault(r["to_node_id"], []).append(r["from_node_id"])
        return adj

    def get_approving_edges_to_node(self, to_node_id: int) -> list[dict[str, Any]]:
        """查询指向指定节点的 approving 边（DEC-INV-001 风控一票否决校验用）。

        order 节点必须有至少一条 approving 入边来自 risk_check。
        """
        conn = self._get_conn()
        cursor = conn.execute(
            """
            SELECT de.*, dn_from.node_type AS from_node_type
            FROM decision_edges de
            JOIN decision_nodes dn_from ON de.from_node_id = dn_from.node_id
            WHERE de.to_node_id = %s AND de.edge_type = 'approving'
            ORDER BY de.edge_id
            """,
            (to_node_id,),
        )
        return [
            _parse_jsonb(dict(row), _JSONB_EDGE_FIELDS) for row in cursor.fetchall()
        ]

    def get_full_graph(self) -> dict[str, Any]:
        """导出完整决策流图（layers + nodes + edges + tracks）。

        用于 generate_decision_graph.py 的 YAML→DB 同步对比，或外部可视化工具。
        """
        return {
            "layers": self.get_all_layers(),
            "nodes": self.get_all_nodes(),
            "edges": self.get_all_edges(),
            "tracks": self.get_all_tracks(),
        }

    # ── 统计查询 ──────────────────────────────────────────────

    def get_layer_count(self) -> int:
        """获取决策层总数。"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT COUNT(*) AS cnt FROM decision_layers")
        return cursor.fetchone()["cnt"]

    def get_node_count(self) -> int:
        """获取决策节点总数。"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT COUNT(*) AS cnt FROM decision_nodes")
        return cursor.fetchone()["cnt"]

    def get_edge_count(self) -> int:
        """获取决策边总数。"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT COUNT(*) AS cnt FROM decision_edges")
        return cursor.fetchone()["cnt"]

    def get_track_count(self) -> int:
        """获取决策轨总数。"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT COUNT(*) AS cnt FROM decision_tracks")
        return cursor.fetchone()["cnt"]

    def get_node_count_by_layer(self) -> dict[str, int]:
        """按 layer_id 分组统计节点数。"""
        conn = self._get_conn()
        cursor = conn.execute(
            """
            SELECT layer_id, COUNT(*) AS cnt
            FROM decision_nodes
            GROUP BY layer_id
            ORDER BY layer_id
            """
        )
        return {row["layer_id"]: row["cnt"] for row in cursor.fetchall()}

    def get_edge_count_by_type(self) -> dict[str, int]:
        """按 edge_type 分组统计边数。"""
        conn = self._get_conn()
        cursor = conn.execute(
            """
            SELECT edge_type, COUNT(*) AS cnt
            FROM decision_edges
            GROUP BY edge_type
            ORDER BY edge_type
            """
        )
        return {row["edge_type"]: row["cnt"] for row in cursor.fetchall()}

    # ── 不变量校验查询（DEC-INV-001~005）────────────────────────

    def find_order_nodes_without_risk_approving(self) -> list[dict[str, Any]]:
        """查找违反 DEC-INV-001（风控一票否决）的 order 节点。

        order 节点必须有至少一条 approving 入边来自 risk_check 节点。
        返回缺失 approving 边的 order 节点列表（违反不变量）。
        """
        conn = self._get_conn()
        cursor = conn.execute(
            """
            SELECT dn.*
            FROM decision_nodes dn
            WHERE dn.node_type = 'order'
              AND NOT EXISTS (
                  SELECT 1 FROM decision_edges de
                  JOIN decision_nodes dn_from ON de.from_node_id = dn_from.node_id
                  WHERE de.to_node_id = dn.node_id
                    AND de.edge_type = 'approving'
                    AND dn_from.node_type = 'risk_check'
              )
            ORDER BY dn.node_id
            """
        )
        return [
            _parse_jsonb(dict(row), _JSONB_NODE_FIELDS) for row in cursor.fetchall()
        ]

    def find_signal_to_order_direct_edges(self) -> list[dict[str, Any]]:
        """查找违反 DEC-INV-002（信号仓位分离）的边。

        signal 节点不能直接连 order 节点，必须经 portfolio_target 中转。
        返回违反不变量的边列表。
        """
        conn = self._get_conn()
        cursor = conn.execute(
            """
            SELECT de.*, dn_from.node_type AS from_node_type, dn_to.node_type AS to_node_type
            FROM decision_edges de
            JOIN decision_nodes dn_from ON de.from_node_id = dn_from.node_id
            JOIN decision_nodes dn_to   ON de.to_node_id   = dn_to.node_id
            WHERE dn_from.node_type = 'signal' AND dn_to.node_type = 'order'
            ORDER BY de.edge_id
            """
        )
        return [
            _parse_jsonb(dict(row), _JSONB_EDGE_FIELDS) for row in cursor.fetchall()
        ]

    def find_nodes_missing_evidence_hash(self) -> list[dict[str, Any]]:
        """查找违反 DEC-INV-005（evidence_hash 必填）的节点。

        每个决策节点必须有 evidence_hash（决策时数据+模型版本哈希）。
        返回缺失 evidence_hash 的节点列表。
        """
        conn = self._get_conn()
        cursor = conn.execute(
            """
            SELECT * FROM decision_nodes
            WHERE evidence_hash IS NULL OR evidence_hash = ''
            ORDER BY node_id
            """
        )
        return [
            _parse_jsonb(dict(row), _JSONB_NODE_FIELDS) for row in cursor.fetchall()
        ]


if __name__ == "__main__":
    # CLI 入口：python -m zephyr.governance.persistence.decision_graph_reader
    # 打印决策流图摘要（用于快速健康检查）
    reader = DecisionGraphReader()
    try:
        print(f"layers: {reader.get_layer_count()}")
        print(f"nodes:  {reader.get_node_count()}")
        print(f"edges:  {reader.get_edge_count()}")
        print(f"tracks: {reader.get_track_count()}")
        by_layer = reader.get_node_count_by_layer()
        if by_layer:
            print("nodes per layer:")
            for layer_id, cnt in by_layer.items():
                print(f"  {layer_id}: {cnt}")
        by_type = reader.get_edge_count_by_type()
        if by_type:
            print("edges per type:")
            for edge_type, cnt in by_type.items():
                print(f"  {edge_type}: {cnt}")
    finally:
        reader.close()
