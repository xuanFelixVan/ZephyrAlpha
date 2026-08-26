# [BLUEPRINT] MOD-SIG-125 | docs/03_modules/_domain_signal/industry_chain_graph/blueprint.md
# [MODULE] zephyr.signal_ashare.industry_chain_graph
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] sqlite3（标准库；连接全注入，禁Neo4j/禁网络）
# [CONSUMERS] 运行时装配批（产业链传导路径信号装配 / 上下游冲击分析消费方）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 节点词表闭合(company|segment); 边类型词表闭合(supply|material|demand|byproduct); 边权 ∈ (0,1]; 禁止自环/悬空边/重复边; 路径强度=decay^跳数×边权连乘(乘积衰减); BFS邻接按node_id排序展开; 路径输出按(-strength,steps)确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_signal/industry_chain_graph/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] IndustryChainError(占位 ZA-SIG-UNREGISTERED-INDUSTRY-CHAIN)——非法连接/空id/重复节点/未知节点/非法边类型/边权越界/自环/悬空边/重复边/非法跳数时抛
# [TESTS] tests/signal_ashare/test_industry_chain_graph.py
# [A_module] module_id=MOD-SIG-125 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""IndustryChainGraph — 产业链知识图谱（MOD-SIG-125）。

B10-02202（AUD-DRAFT-001-DIGEST P2 波 P2-W06，CAND-TESTB-053，A1 D-ALT-DATA-29）：
产业链**节点/边 SQLite 表**（连接全注入：节点=公司/环节，边=投入产出关系+权重
+来源）+ **传导路径查询**（上游/下游 N 跳 BFS + 路径强度乘积衰减）+ 增删查。

查重分工（蓝图 §0）：KNW-003=通用金融 KG（本件=产业链传导专用，边类型词表闭
合，不重建通用 KG）；supply_chain_gnn=GNN 风险传播占位（本件=关系存储与路径
查询，不做图神经网络推理）；禁 Neo4j，存储仅经注入的 sqlite3 连接。
"""

from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from enum import Enum
from typing import Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "ChainEdge",
    "ChainNode",
    "ChainPath",
    "EdgeKind",
    "IndustryChainError",
    "IndustryChainGraph",
    "NodeKind",
]

#: 节点建表语句（节点=公司/环节）
_DDL_NODES: Final = (
    "CREATE TABLE IF NOT EXISTS ic_nodes ("
    "node_id TEXT PRIMARY KEY, "
    "name TEXT NOT NULL, "
    "kind TEXT NOT NULL, "
    "meta TEXT NOT NULL DEFAULT '')"
)

#: 边建表语句（投入产出关系+权重+来源；主键 (src,dst,edge_kind)）
_DDL_EDGES: Final = (
    "CREATE TABLE IF NOT EXISTS ic_edges ("
    "src TEXT NOT NULL, "
    "dst TEXT NOT NULL, "
    "edge_kind TEXT NOT NULL, "
    "weight REAL NOT NULL, "
    "source TEXT NOT NULL DEFAULT '', "
    "PRIMARY KEY (src, dst, edge_kind))"
)


class IndustryChainError(Exception):
    """产业链图谱输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SIG-UNREGISTERED-INDUSTRY-CHAIN。
    """


class NodeKind(str, Enum):
    """节点类型（词表闭合）。"""

    COMPANY = "company"
    SEGMENT = "segment"


class EdgeKind(str, Enum):
    """边类型（投入产出关系词表闭合）。

    方向语义：src → dst 表示 src 的产出作为 dst 的投入（src 是 dst 的上游）。
    """

    SUPPLY = "supply"  # 供给投入（上游供货）
    MATERIAL = "material"  # 原材料投入
    DEMAND = "demand"  # 下游需求产出
    BYPRODUCT = "byproduct"  # 副产品关联


@dataclass(frozen=True)
class ChainNode:
    """产业链节点（公司/环节，frozen）。"""

    node_id: str
    name: str
    kind: NodeKind
    meta: str = ""


@dataclass(frozen=True)
class ChainEdge:
    """产业链边（投入产出关系+权重+来源，frozen）。"""

    src: str
    dst: str
    edge_kind: EdgeKind
    weight: float
    source: str = ""


@dataclass(frozen=True)
class ChainPath:
    """传导路径（steps 含起点终点；strength=decay^跳数×边权连乘，frozen）。"""

    steps: tuple[str, ...]
    strength: float

    @property
    def hops(self) -> int:
        """跳数（边数）。"""
        return len(self.steps) - 1


class IndustryChainGraph:
    """产业链图谱件（注入 SQLite 连接 + 增删查 + 上/下游传导路径 BFS）。"""

    def __init__(self, *, conn: sqlite3.Connection, decay: float = 1.0) -> None:
        if not isinstance(conn, sqlite3.Connection):
            raise IndustryChainError("conn 须为已注入的 sqlite3.Connection（禁自建/禁Neo4j）")
        if not 0.0 < decay <= 1.0:
            raise IndustryChainError(f"decay 必须 ∈ (0,1]: {decay}")
        self._conn = conn
        self._decay = float(decay)
        self._conn.execute(_DDL_NODES)
        self._conn.execute(_DDL_EDGES)
        self._conn.commit()

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _has_node(self, node_id: str) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM ic_nodes WHERE node_id = ?", (node_id,)
        ).fetchone()
        return row is not None

    def _require_node(self, node_id: str) -> None:
        if not self._has_node(node_id):
            raise IndustryChainError(f"未知节点: {node_id!r}（未登记）")

    # ── 节点增删查 ────────────────────────────────────────────────────────

    def add_node(self, node: ChainNode) -> None:
        """登记节点：空 id/空名/非法类型/重复 → Fail-Closed。"""
        if not node.node_id:
            raise IndustryChainError("node_id 为空")
        if not node.name:
            raise IndustryChainError("name 为空")
        if not isinstance(node.kind, NodeKind):
            raise IndustryChainError(f"非法节点类型: {node.kind!r}")
        if self._has_node(node.node_id):
            raise IndustryChainError(f"节点重复: {node.node_id!r}")
        self._conn.execute(
            "INSERT INTO ic_nodes (node_id, name, kind, meta) VALUES (?, ?, ?, ?)",
            (node.node_id, node.name, node.kind.value, node.meta),
        )
        self._conn.commit()

    def remove_node(self, node_id: str) -> None:
        """删除节点：未知 → Fail-Closed；级联删除关联边。"""
        self._require_node(node_id)
        self._conn.execute(
            "DELETE FROM ic_edges WHERE src = ? OR dst = ?", (node_id, node_id)
        )
        self._conn.execute("DELETE FROM ic_nodes WHERE node_id = ?", (node_id,))
        self._conn.commit()

    def get_node(self, node_id: str) -> ChainNode:
        """单节点查询（未知 → Fail-Closed）。"""
        row = self._conn.execute(
            "SELECT node_id, name, kind, meta FROM ic_nodes WHERE node_id = ?",
            (node_id,),
        ).fetchone()
        if row is None:
            raise IndustryChainError(f"未知节点: {node_id!r}（未登记）")
        return ChainNode(node_id=row[0], name=row[1], kind=NodeKind(row[2]), meta=row[3])

    def list_nodes(self) -> tuple[ChainNode, ...]:
        """全量节点（按 node_id 确定性排序）。"""
        rows = self._conn.execute(
            "SELECT node_id, name, kind, meta FROM ic_nodes ORDER BY node_id"
        ).fetchall()
        return tuple(
            ChainNode(node_id=r[0], name=r[1], kind=NodeKind(r[2]), meta=r[3])
            for r in rows
        )

    # ── 边增删查 ──────────────────────────────────────────────────────────

    def add_edge(self, edge: ChainEdge) -> None:
        """登记边：非法类型/悬空/自环/边权越界/重复 → Fail-Closed。"""
        if not isinstance(edge.edge_kind, EdgeKind):
            raise IndustryChainError(f"非法边类型: {edge.edge_kind!r}")
        if edge.src == edge.dst:
            raise IndustryChainError(f"自环非法: {edge.src!r}")
        self._require_node(edge.src)
        self._require_node(edge.dst)
        weight = float(edge.weight)
        if not 0.0 < weight <= 1.0:
            raise IndustryChainError(
                f"边权必须 ∈ (0,1]: {edge.src!r} -> {edge.dst!r} = {edge.weight}"
            )
        dup = self._conn.execute(
            "SELECT 1 FROM ic_edges WHERE src = ? AND dst = ? AND edge_kind = ?",
            (edge.src, edge.dst, edge.edge_kind.value),
        ).fetchone()
        if dup is not None:
            raise IndustryChainError(
                f"边重复: {edge.src!r} -> {edge.dst!r} ({edge.edge_kind.value})"
            )
        self._conn.execute(
            "INSERT INTO ic_edges (src, dst, edge_kind, weight, source) VALUES (?, ?, ?, ?, ?)",
            (edge.src, edge.dst, edge.edge_kind.value, weight, edge.source),
        )
        self._conn.commit()

    def remove_edge(self, src: str, dst: str, edge_kind: EdgeKind) -> None:
        """删除边：未知 → Fail-Closed。"""
        if not isinstance(edge_kind, EdgeKind):
            raise IndustryChainError(f"非法边类型: {edge_kind!r}")
        cur = self._conn.execute(
            "DELETE FROM ic_edges WHERE src = ? AND dst = ? AND edge_kind = ?",
            (src, dst, edge_kind.value),
        )
        self._conn.commit()
        if cur.rowcount == 0:
            raise IndustryChainError(
                f"未知边: {src!r} -> {dst!r} ({edge_kind.value})（未登记）"
            )

    def list_edges(self, node_id: str | None = None) -> tuple[ChainEdge, ...]:
        """边查询（可选按节点过滤；按 (src,dst,edge_kind) 确定性排序）。"""
        if node_id is None:
            rows = self._conn.execute(
                "SELECT src, dst, edge_kind, weight, source FROM ic_edges "
                "ORDER BY src, dst, edge_kind"
            ).fetchall()
        else:
            self._require_node(node_id)
            rows = self._conn.execute(
                "SELECT src, dst, edge_kind, weight, source FROM ic_edges "
                "WHERE src = ? OR dst = ? ORDER BY src, dst, edge_kind",
                (node_id, node_id),
            ).fetchall()
        return tuple(
            ChainEdge(src=r[0], dst=r[1], edge_kind=EdgeKind(r[2]), weight=r[3], source=r[4])
            for r in rows
        )

    # ── 传导路径查询（上/下游 N 跳 BFS + 乘积衰减） ────────────────────────

    def _neighbors(self, node_id: str, *, upstream: bool) -> list[tuple[str, float]]:
        """邻接（上游=前驱/下游=后继；按 node_id 排序保证确定性）。"""
        if upstream:
            rows = self._conn.execute(
                "SELECT src, weight FROM ic_edges WHERE dst = ? ORDER BY src",
                (node_id,),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT dst, weight FROM ic_edges WHERE src = ? ORDER BY dst",
                (node_id,),
            ).fetchall()
        return [(r[0], float(r[1])) for r in rows]

    def _paths(self, start: str, max_hops: int, *, upstream: bool) -> tuple[ChainPath, ...]:
        """N 跳简单路径 BFS：strength=decay^跳数×边权连乘；输出按(-strength,steps)排序。"""
        self._require_node(start)
        if not isinstance(max_hops, int) or max_hops < 1:
            raise IndustryChainError(f"max_hops 须为 ≥1 整数: {max_hops!r}")
        direction = "上游" if upstream else "下游"
        _log.debug("传导路径查询: %s %s max_hops=%d", direction, start, max_hops)

        out: list[ChainPath] = []
        queue: list[tuple[str, tuple[str, ...], float]] = [(start, (start,), 1.0)]
        while queue:
            current, path, strength = queue.pop(0)
            if len(path) - 1 >= max_hops:
                continue
            for nxt, weight in self._neighbors(current, upstream=upstream):
                if nxt in path:  # 简单路径：防环
                    continue
                new_path = path + (nxt,)
                new_strength = strength * weight * self._decay
                out.append(ChainPath(steps=new_path, strength=new_strength))
                queue.append((nxt, new_path, new_strength))
        out.sort(key=lambda p: (-p.strength, p.steps))
        return tuple(out)

    def upstream_paths(self, start: str, max_hops: int) -> tuple[ChainPath, ...]:
        """上游传导路径（前驱方向 N 跳 BFS，乘积衰减）。"""
        return self._paths(start, max_hops, upstream=True)

    def downstream_paths(self, start: str, max_hops: int) -> tuple[ChainPath, ...]:
        """下游传导路径（后继方向 N 跳 BFS，乘积衰减）。"""
        return self._paths(start, max_hops, upstream=False)
