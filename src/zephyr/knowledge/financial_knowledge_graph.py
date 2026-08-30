# [BLUEPRINT] MOD-KNW-003 | docs/03_modules/_domain_knowledge/financial_knowledge_graph/blueprint.md
# [MODULE] zephyr.knowledge.financial_knowledge_graph
# [DOMAIN] D_KNOWLEDGE
# [DEPENDENCIES] 无（图谱核心纯内存；sqlite连接/clock 全注入）
# [CONSUMERS] 运行时装配批（供应链推理 / 概念联动检索 / LLM抽取人工审核入图）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 六类实体词表闭合(company|industry|supply_chain|shareholder|event|concept); 关系类型词表闭合(注入校验); 权重∈(0,1]; 查询仅见approved( pending/rejected 不入图); 审核状态机pending→approved|rejected单向不可逆; 边数≥护栏即拒绝(默认≤1e6); BFS按实体id字典序访问(同输入必同输出)
# [MODIFY-GUARD] docs/03_modules/_domain_knowledge/financial_knowledge_graph/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] FinancialGraphError(占位 ZA-KNW-UNREGISTERED-FIN-GRAPH)——未知实体/非法类型/越界权重/重复边/越护栏/非法审核迁移时抛
# [TESTS] tests/knowledge/test_financial_knowledge_graph.py
# [A_module] module_id=MOD-KNW-003 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
FinancialKnowledgeGraph — 金融知识图谱（MOD-KNW-003）。

B1-00126（AUD-DRAFT-001-DIGEST P2 波 P2-W03，CAND-KNW-001，C2 D-KNOW-01）：
SQLite 邻接表轻量图谱（严禁 Neo4j）——六类实体（公司/行业/供应链/股东/
事件/概念词表闭合）+ 关系表（类型词表 + 权重 + 属性 JSON）+ 增删查 +
N 跳邻域子图抽取 + BFS 最短路径 + LLM 抽取结果人工审核入图接口
（pending_review 状态机）+ 规模护栏（≤百万边计数拒绝）。canonical 承接
KNW-010（五类/六类枚举姊妹稿）归并。

查重分工：signal_ashare/supply_chain_gnn=供应链 GNN 打分（本件=图存储与
遍历基座，不算分）；layered_memory_orchestrator=图谱层适配消费方（本件不
做编排）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: conn 参数
#   fields: 参数 conn（无注解）
#   code: financial_knowledge_graph.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: relation_types 参数
#   fields: 参数 relation_types（无注解）
#   code: financial_knowledge_graph.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: max_edges 参数
#   fields: 参数 max_edges（无注解）
#   code: financial_knowledge_graph.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: financial_knowledge_graph.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① FinancialKnowledgeGraph
#   name_en: FinancialKnowledgeGraph
#   intro: SQLite 邻接表图谱（实体/关系 + 遍历 + LLM 审核入图 + 规模护栏）。
#   desc: SQLite 邻接表图谱（实体/关系 + 遍历 + LLM 审核入图 + 规模护栏）。；公共方法（定义序）: add_entity, remove_entity, get_entity, entity_count, e…
#   inputs: conn relation_types max_edges clock
#   outputs: 返回值
#   （注：A1 之后另有 7 个公共定义未列入（含 7 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（8 定义）
#   name_en: public defs
#   intro: FinancialKnowledgeGraph
#   downstream: 运行时装配批（供应链推理 / 概念联动检索 / LLM抽取人工审核入图）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import json
import logging
import sqlite3
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Iterable, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "EdgeView",
    "EntityType",
    "EntityView",
    "ExtractionSubmission",
    "FinancialGraphError",
    "FinancialKnowledgeGraph",
    "ReviewStatus",
    "SubGraph",
]

#: 关系类型默认词表（注入则全量校验）
_DEFAULT_RELATION_TYPES: Final = (
    "belongs_to",
    "supplies_to",
    "holds",
    "competes_with",
    "triggers",
    "tagged_with",
)

#: 规模护栏：边数上限（默认 ≤ 百万边）
_MAX_EDGES_DEFAULT: Final = 1_000_000


class FinancialGraphError(Exception):
    """金融知识图谱输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-KNW-UNREGISTERED-FIN-GRAPH。
    """


class EntityType(str, Enum):
    """六类实体（词表闭合）。"""

    COMPANY = "company"
    INDUSTRY = "industry"
    SUPPLY_CHAIN = "supply_chain"
    SHAREHOLDER = "shareholder"
    EVENT = "event"
    CONCEPT = "concept"


class ReviewStatus(str, Enum):
    """LLM 抽取审核状态机（pending → approved | rejected，单向不可逆）。"""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True)
class EntityView:
    """实体视图（frozen）。"""

    entity_id: str
    entity_type: EntityType
    name: str
    attrs: dict


@dataclass(frozen=True)
class EdgeView:
    """关系边视图（frozen）。"""

    src: str
    dst: str
    rel_type: str
    weight: float
    attrs: dict


@dataclass(frozen=True)
class SubGraph:
    """N 跳邻域子图（确定性排序）。"""

    entities: tuple[EntityView, ...]
    edges: tuple[EdgeView, ...]


@dataclass(frozen=True)
class ExtractionSubmission:
    """LLM 抽取审核批次（FIFO 队列条目，frozen）。"""

    submission_id: str
    status: ReviewStatus
    entity_ids: tuple[str, ...]
    edge_keys: tuple[tuple[str, str, str], ...]
    submitted_at: datetime.datetime


class FinancialKnowledgeGraph:
    """SQLite 邻接表图谱（实体/关系 + 遍历 + LLM 审核入图 + 规模护栏）。"""

    def __init__(
        self,
        *,
        conn: sqlite3.Connection,
        relation_types: Iterable[str] | None = None,
        max_edges: int = _MAX_EDGES_DEFAULT,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if conn is None:
            raise FinancialGraphError("sqlite 连接未注入（邻接表强制依赖）")
        vocab = tuple(relation_types) if relation_types is not None else _DEFAULT_RELATION_TYPES
        if not vocab:
            raise FinancialGraphError("关系类型词表为空")
        seen: set[str] = set()
        for rel in vocab:
            if not rel or not isinstance(rel, str):
                raise FinancialGraphError(f"非法关系类型: {rel!r}")
            if rel in seen:
                raise FinancialGraphError(f"关系类型词表重复: {rel!r}")
            seen.add(rel)
        if max_edges < 1:
            raise FinancialGraphError(f"非法边数护栏: {max_edges}")
        self._relation_types: frozenset[str] = frozenset(vocab)
        self._max_edges = max_edges
        self._clock = clock or datetime.datetime.now
        self._conn = conn
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS fkg_entities ("
            "entity_id TEXT PRIMARY KEY, type TEXT NOT NULL, name TEXT NOT NULL, "
            "attrs TEXT NOT NULL, review_status TEXT NOT NULL)"
        )
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS fkg_edges ("
            "src TEXT NOT NULL, dst TEXT NOT NULL, rel_type TEXT NOT NULL, "
            "weight REAL NOT NULL, attrs TEXT NOT NULL, review_status TEXT NOT NULL, "
            "PRIMARY KEY (src, dst, rel_type))"
        )
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS fkg_submissions ("
            "submission_id TEXT PRIMARY KEY, status TEXT NOT NULL, "
            "entity_ids TEXT NOT NULL, edge_keys TEXT NOT NULL, "
            "submitted_at TEXT NOT NULL)"
        )
        self._submission_seq = 0

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _require_rel_type(self, rel_type: str) -> None:
        if rel_type not in self._relation_types:
            raise FinancialGraphError(f"未知关系类型: {rel_type!r}（词表闭合）")

    @staticmethod
    def _require_weight(weight: float) -> None:
        if not 0.0 < weight <= 1.0:
            raise FinancialGraphError(f"权重越界: {weight}（须 ∈ (0,1]）")

    @staticmethod
    def _entity_type_of(raw: object) -> EntityType:
        try:
            return raw if isinstance(raw, EntityType) else EntityType(str(raw))
        except ValueError as exc:
            raise FinancialGraphError(f"非法实体类型: {raw!r}（六类词表闭合）") from exc

    def _edge_count(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) FROM fkg_edges").fetchone()
        return int(row[0])

    def _guard_edge_capacity(self) -> None:
        if self._edge_count() >= self._max_edges:
            raise FinancialGraphError(f"规模护栏触发: 边数已达 {self._max_edges}（≤百万边计数拒绝）")

    def _live_entity_ids(self, entity_ids: Iterable[str]) -> dict[str, tuple]:
        out: dict[str, tuple] = {}
        for entity_id in entity_ids:
            row = self._conn.execute(
                "SELECT type, name, attrs FROM fkg_entities WHERE entity_id = ? AND review_status = ?",
                (entity_id, ReviewStatus.APPROVED.value),
            ).fetchone()
            if row is None:
                raise FinancialGraphError(f"未知实体: {entity_id!r}（未入图或待审核）")
            out[entity_id] = row
        return out

    def _insert_entity(
        self,
        entity_id: str,
        entity_type: EntityType,
        name: str,
        attrs: Mapping | None,
        status: ReviewStatus,
    ) -> None:
        self._conn.execute(
            "INSERT INTO fkg_entities (entity_id, type, name, attrs, review_status) VALUES (?, ?, ?, ?, ?)",
            (entity_id, entity_type.value, name, json.dumps(dict(attrs or {}), sort_keys=True), status.value),
        )

    def _insert_edge(
        self,
        src: str,
        dst: str,
        rel_type: str,
        weight: float,
        attrs: Mapping | None,
        status: ReviewStatus,
    ) -> None:
        self._conn.execute(
            "INSERT INTO fkg_edges (src, dst, rel_type, weight, attrs, review_status) VALUES (?, ?, ?, ?, ?, ?)",
            (src, dst, rel_type, weight, json.dumps(dict(attrs or {}), sort_keys=True), status.value),
        )

    # ── 实体增删查 ────────────────────────────────────────────────────────

    def add_entity(
        self,
        entity_id: str,
        entity_type: EntityType,
        name: str,
        *,
        attrs: Mapping | None = None,
    ) -> EntityView:
        """登记实体（人工直登即 approved；重复/非法类型 Fail-Closed）。"""
        if not entity_id:
            raise FinancialGraphError("entity_id 为空")
        etype = self._entity_type_of(entity_type)
        if not name:
            raise FinancialGraphError("实体名为空")
        row = self._conn.execute("SELECT review_status FROM fkg_entities WHERE entity_id = ?", (entity_id,)).fetchone()
        if row is not None:
            raise FinancialGraphError(f"实体已存在: {entity_id!r}（重复登记拒绝）")
        self._insert_entity(entity_id, etype, name, attrs, ReviewStatus.APPROVED)
        return EntityView(entity_id=entity_id, entity_type=etype, name=name, attrs=dict(attrs or {}))

    def remove_entity(self, entity_id: str) -> None:
        """删除实体并级联删除其全部边（未知 → Fail-Closed）。"""
        self._live_entity_ids([entity_id])
        self._conn.execute("DELETE FROM fkg_edges WHERE src = ? OR dst = ?", (entity_id, entity_id))
        self._conn.execute("DELETE FROM fkg_entities WHERE entity_id = ?", (entity_id,))

    def get_entity(self, entity_id: str) -> EntityView:
        """单实体查询（仅 approved 可见）。"""
        row = self._live_entity_ids([entity_id])[entity_id]
        return EntityView(
            entity_id=entity_id,
            entity_type=self._entity_type_of(row[0]),
            name=row[1],
            attrs=json.loads(row[2]),
        )

    def entity_count(self) -> int:
        """approved 实体计数。"""
        row = self._conn.execute(
            "SELECT COUNT(*) FROM fkg_entities WHERE review_status = ?",
            (ReviewStatus.APPROVED.value,),
        ).fetchone()
        return int(row[0])

    def edge_count(self) -> int:
        """approved 边计数。"""
        row = self._conn.execute(
            "SELECT COUNT(*) FROM fkg_edges WHERE review_status = ?",
            (ReviewStatus.APPROVED.value,),
        ).fetchone()
        return int(row[0])

    # ── 关系增删查 ────────────────────────────────────────────────────────

    def add_edge(
        self,
        src: str,
        dst: str,
        rel_type: str,
        weight: float,
        *,
        attrs: Mapping | None = None,
    ) -> EdgeView:
        """登记关系边（两端实体须已 approved；护栏计数拒绝；重复边 Fail-Closed）。"""
        self._require_rel_type(rel_type)
        self._require_weight(weight)
        self._live_entity_ids([src, dst])
        row = self._conn.execute(
            "SELECT review_status FROM fkg_edges WHERE src = ? AND dst = ? AND rel_type = ?",
            (src, dst, rel_type),
        ).fetchone()
        if row is not None:
            raise FinancialGraphError(f"边已存在: {src}->{dst}({rel_type})（重复登记拒绝）")
        self._guard_edge_capacity()
        self._insert_edge(src, dst, rel_type, weight, attrs, ReviewStatus.APPROVED)
        return EdgeView(src=src, dst=dst, rel_type=rel_type, weight=weight, attrs=dict(attrs or {}))

    def remove_edge(self, src: str, dst: str, rel_type: str) -> None:
        """删除指定边（未知 → Fail-Closed）。"""
        self._require_rel_type(rel_type)
        cur = self._conn.execute(
            "DELETE FROM fkg_edges WHERE src = ? AND dst = ? AND rel_type = ? AND review_status = ?",
            (src, dst, rel_type, ReviewStatus.APPROVED.value),
        )
        if cur.rowcount == 0:
            raise FinancialGraphError(f"未知边: {src}->{dst}({rel_type})")

    def neighbors(self, entity_id: str) -> tuple[EdgeView, ...]:
        """出向邻居（仅 approved；按 (dst, rel_type) 确定性排序）。"""
        self._live_entity_ids([entity_id])
        rows = self._conn.execute(
            "SELECT dst, rel_type, weight, attrs FROM fkg_edges "
            "WHERE src = ? AND review_status = ? ORDER BY dst, rel_type",
            (entity_id, ReviewStatus.APPROVED.value),
        ).fetchall()
        return tuple(
            EdgeView(src=entity_id, dst=r[0], rel_type=r[1], weight=r[2], attrs=json.loads(r[3])) for r in rows
        )

    # ── 遍历 ─────────────────────────────────────────────────────────────

    def subgraph(self, entity_id: str, hops: int) -> SubGraph:
        """N 跳邻域子图抽取（出向 BFS；实体/边均确定性排序）。"""
        if hops < 1:
            raise FinancialGraphError(f"非法跳数: {hops}（须 ≥ 1）")
        self._live_entity_ids([entity_id])
        visited: set[str] = {entity_id}
        frontier = [entity_id]
        for _ in range(hops):
            next_frontier: list[str] = []
            for edge in self._edges_from(frontier):
                if edge.dst not in visited:
                    visited.add(edge.dst)
                    next_frontier.append(edge.dst)
            frontier = sorted(next_frontier)
            if not frontier:
                break
        entity_rows = self._conn.execute(
            "SELECT entity_id, type, name, attrs FROM fkg_entities "
            "WHERE review_status = ? AND entity_id IN (%s) ORDER BY entity_id" % ",".join("?" * len(visited)),
            (ReviewStatus.APPROVED.value, *sorted(visited)),
        ).fetchall()
        edge_rows = self._conn.execute(
            "SELECT src, dst, rel_type, weight, attrs FROM fkg_edges "
            "WHERE review_status = ? AND src IN (%s) ORDER BY src, dst, rel_type" % ",".join("?" * len(visited)),
            (ReviewStatus.APPROVED.value, *sorted(visited)),
        ).fetchall()
        entities = tuple(
            EntityView(
                entity_id=r[0],
                entity_type=self._entity_type_of(r[1]),
                name=r[2],
                attrs=json.loads(r[3]),
            )
            for r in entity_rows
        )
        edges = tuple(
            EdgeView(src=r[0], dst=r[1], rel_type=r[2], weight=r[3], attrs=json.loads(r[4])) for r in edge_rows
        )
        return SubGraph(entities=entities, edges=edges)

    def _edges_from(self, src_ids: Iterable[str]) -> list[EdgeView]:
        ids = sorted(set(src_ids))
        if not ids:
            return []
        rows = self._conn.execute(
            "SELECT src, dst, rel_type, weight, attrs FROM fkg_edges "
            "WHERE review_status = ? AND src IN (%s) ORDER BY src, dst, rel_type" % ",".join("?" * len(ids)),
            (ReviewStatus.APPROVED.value, *ids),
        ).fetchall()
        return [EdgeView(src=r[0], dst=r[1], rel_type=r[2], weight=r[3], attrs=json.loads(r[4])) for r in rows]

    def shortest_path(self, src: str, dst: str) -> tuple[str, ...] | None:
        """BFS 最短路径（出向；邻居按实体 id 字典序访问保证确定性；不可达 → None）。"""
        self._live_entity_ids([src, dst])
        if src == dst:
            return (src,)
        prev: dict[str, str] = {}
        visited = {src}
        queue: deque[str] = deque([src])
        while queue:
            node = queue.popleft()
            for edge in self._edges_from([node]):
                nxt = edge.dst
                if nxt in visited:
                    continue
                visited.add(nxt)
                prev[nxt] = node
                if nxt == dst:
                    path = [dst]
                    while path[-1] != src:
                        path.append(prev[path[-1]])
                    return tuple(reversed(path))
                queue.append(nxt)
        return None

    # ── LLM 抽取人工审核入图（pending_review 状态机） ─────────────────────

    def submit_extraction(
        self,
        *,
        entities: Iterable[Mapping] = (),
        edges: Iterable[Mapping] = (),
    ) -> str:
        """LLM 抽取批次登记为 pending（校验同人工登记；不入图可见集）。"""
        entity_list = list(entities)
        edge_list = list(edges)
        if not entity_list and not edge_list:
            raise FinancialGraphError("抽取批次为空（实体与边不可同时为空）")
        entity_ids: list[str] = []
        for item in entity_list:
            entity_id = str(item.get("entity_id") or "")
            if not entity_id:
                raise FinancialGraphError("抽取实体缺 entity_id")
            etype = self._entity_type_of(item.get("entity_type"))
            name = str(item.get("name") or "")
            if not name:
                raise FinancialGraphError(f"抽取实体缺名称: {entity_id!r}")
            row = self._conn.execute(
                "SELECT review_status FROM fkg_entities WHERE entity_id = ?", (entity_id,)
            ).fetchone()
            if row is not None:
                raise FinancialGraphError(f"实体已存在: {entity_id!r}（抽取重复拒绝）")
            self._insert_entity(entity_id, etype, name, item.get("attrs"), ReviewStatus.PENDING)
            entity_ids.append(entity_id)
        edge_keys: list[tuple[str, str, str]] = []
        known = set(entity_ids)
        for item in edge_list:
            src = str(item.get("src") or "")
            dst = str(item.get("dst") or "")
            rel_type = str(item.get("rel_type") or "")
            weight = float(item.get("weight", 0.0))
            self._require_rel_type(rel_type)
            self._require_weight(weight)
            for endpoint in (src, dst):
                if endpoint in known:
                    continue
                row = self._conn.execute(
                    "SELECT review_status FROM fkg_entities WHERE entity_id = ?", (endpoint,)
                ).fetchone()
                if row is None:
                    raise FinancialGraphError(f"抽取边端点未知: {endpoint!r}")
            row = self._conn.execute(
                "SELECT review_status FROM fkg_edges WHERE src = ? AND dst = ? AND rel_type = ?",
                (src, dst, rel_type),
            ).fetchone()
            if row is not None:
                raise FinancialGraphError(f"边已存在: {src}->{dst}({rel_type})（抽取重复拒绝）")
            self._guard_edge_capacity()
            self._insert_edge(src, dst, rel_type, weight, item.get("attrs"), ReviewStatus.PENDING)
            edge_keys.append((src, dst, rel_type))
        self._submission_seq += 1
        submission_id = f"sub-{self._submission_seq:06d}"
        self._conn.execute(
            "INSERT INTO fkg_submissions "
            "(submission_id, status, entity_ids, edge_keys, submitted_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                submission_id,
                ReviewStatus.PENDING.value,
                json.dumps(entity_ids),
                json.dumps([list(k) for k in edge_keys]),
                self._clock().isoformat(),
            ),
        )
        _log.info("LLM抽取入队: %s (实体%d 边%d)", submission_id, len(entity_ids), len(edge_keys))
        return submission_id

    def _submission(self, submission_id: str) -> tuple:
        row = self._conn.execute(
            "SELECT status, entity_ids, edge_keys FROM fkg_submissions WHERE submission_id = ?",
            (submission_id,),
        ).fetchone()
        if row is None:
            raise FinancialGraphError(f"未知审核批次: {submission_id!r}")
        return row

    def _transition(self, submission_id: str, target: ReviewStatus) -> None:
        status, entity_ids, edge_keys = self._submission(submission_id)
        if status != ReviewStatus.PENDING.value:
            raise FinancialGraphError(f"非法审核迁移: {submission_id!r} 当前 {status}（仅 pending 可迁移，单向不可逆）")
        for entity_id in json.loads(entity_ids):
            self._conn.execute(
                "UPDATE fkg_entities SET review_status = ? WHERE entity_id = ?",
                (target.value, entity_id),
            )
        for src, dst, rel_type in json.loads(edge_keys):
            self._conn.execute(
                "UPDATE fkg_edges SET review_status = ? WHERE src = ? AND dst = ? AND rel_type = ?",
                (target.value, src, dst, rel_type),
            )
        self._conn.execute(
            "UPDATE fkg_submissions SET status = ? WHERE submission_id = ?",
            (target.value, submission_id),
        )
        _log.info("审核迁移: %s -> %s", submission_id, target.value)

    def approve_extraction(self, submission_id: str) -> None:
        """人工审核通过：批次实体/边转 approved 入图。"""
        self._transition(submission_id, ReviewStatus.APPROVED)

    def reject_extraction(self, submission_id: str) -> None:
        """人工审核拒绝：批次实体/边转 rejected 留痕不入图。"""
        self._transition(submission_id, ReviewStatus.REJECTED)

    def pending_submissions(self) -> tuple[ExtractionSubmission, ...]:
        """待审核批次（按 submission_id 即 FIFO 序，确定性）。"""
        rows = self._conn.execute(
            "SELECT submission_id, entity_ids, edge_keys, submitted_at FROM fkg_submissions "
            "WHERE status = ? ORDER BY submission_id",
            (ReviewStatus.PENDING.value,),
        ).fetchall()
        return tuple(
            ExtractionSubmission(
                submission_id=r[0],
                status=ReviewStatus.PENDING,
                entity_ids=tuple(json.loads(r[1])),
                edge_keys=tuple(tuple(k) for k in json.loads(r[2])),
                submitted_at=datetime.datetime.fromisoformat(r[3]),
            )
            for r in rows
        )
