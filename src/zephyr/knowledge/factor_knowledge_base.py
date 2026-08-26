# [BLUEPRINT] MOD-KNW-005 | docs/03_modules/_domain_knowledge/factor_knowledge_base/blueprint.md
# [MODULE] zephyr.knowledge.factor_knowledge_base
# [DOMAIN] D_KNOWLEDGE
# [DEPENDENCIES] 无（纯内存三表；kb_writer/clock 全注入）
# [CONSUMERS] 运行时装配批（因子注册入库 / vector_memory knowledge 集合写入绑定 / 因子查询路由）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 关系词表闭合(same_family|orthogonal|parent_child); 状态机 DRAFT→ACTIVE→DEPRECATED 闭合不可逆; IC∈[-1,1] 越界拒绝; 因子/关系/历史三表写前校验; 查询按 factor_id 确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_knowledge/factor_knowledge_base/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] FactorKbError(占位 ZA-KNW-UNREGISTERED-FACTOR-KB)——空字段/未知因子/重复注册/非法关系/非法状态迁移/IC越界/样本不足时抛
# [TESTS] tests/knowledge/test_factor_knowledge_base.py
# [A_module] module_id=MOD-KNW-005 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""FactorKnowledgeBase — 因子知识库（MOD-KNW-005）。

B10-02181（AUD-DRAFT-001-DIGEST P2 波 P2-W03，CAND-KNW-004，A1 D-KNOWLEDGE-02）：
因子**定义/关系/历史三表**——定义表（formula/类别/假设）、关系表（同族/正交/
父子**词表闭合**）、历史表（IC 序列/IC 衰减/状态变迁留痕）+ 挂 vector_memory
knowledge 集合语义（**注入 kb_writer 回调**，因子注册与状态变迁同步写出）+
查询接口（按类别/状态/相关性，全部确定性排序）。

查重分工（蓝图 §0）：factor/casebook=因子案例簿（个案叙事，本件=结构化三表
与关系词表，不存案例叙事）；kb_engine=八 Collection 通用 CRUD 门面（本件仅经
注入 kb_writer 挂接其 knowledge 集合语义，不自建存储）；financial_knowledge_
graph=六类实体邻接图谱（本件关系仅因子间三类闭合词表，零交集）。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "FactorDefinition",
    "FactorKbError",
    "FactorKnowledgeBase",
    "FactorRelation",
    "FactorStatus",
    "IcRecord",
    "RelationType",
    "StatusTransition",
]

#: 合法状态迁移（DRAFT→ACTIVE→DEPRECATED 闭合；DRAFT 可直接废弃）
_ALLOWED_TRANSITIONS: Final[dict["FactorStatus", frozenset["FactorStatus"]]] = {}


class FactorKbError(Exception):
    """因子知识库输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-KNW-UNREGISTERED-FACTOR-KB。
    """


class FactorStatus(str, Enum):
    """因子状态机（词表闭合）。"""

    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"


_ALLOWED_TRANSITIONS.update({
    FactorStatus.DRAFT: frozenset({FactorStatus.ACTIVE, FactorStatus.DEPRECATED}),
    FactorStatus.ACTIVE: frozenset({FactorStatus.DEPRECATED}),
    FactorStatus.DEPRECATED: frozenset(),
})


class RelationType(str, Enum):
    """因子关系词表（闭合）。"""

    SAME_FAMILY = "same_family"
    ORTHOGONAL = "orthogonal"
    PARENT_CHILD = "parent_child"


@dataclass(frozen=True)
class FactorDefinition:
    """因子定义（frozen）：formula/类别/假设三要素。"""

    factor_id: str
    formula: str
    category: str
    hypothesis: str


@dataclass(frozen=True)
class FactorRelation:
    """因子关系（frozen）：src→dst + 闭合词表类型。"""

    src_factor: str
    dst_factor: str
    relation_type: RelationType


@dataclass(frozen=True)
class IcRecord:
    """IC 观测点（frozen）：IC 值 + 观测时刻 + 写入序号。"""

    factor_id: str
    ic_value: float
    observed_at: datetime.datetime
    seq: int


@dataclass(frozen=True)
class StatusTransition:
    """状态变迁留痕（frozen）。"""

    factor_id: str
    from_status: FactorStatus
    to_status: FactorStatus
    changed_at: datetime.datetime


class FactorKnowledgeBase:
    """因子知识库（定义/关系/历史三表 + kb 写入回调 + 确定性查询）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        kb_writer: Callable[[Mapping[str, object]], None] | None = None,
    ) -> None:
        self._clock = clock or datetime.datetime.now
        self._kb_writer = kb_writer
        self._definitions: dict[str, FactorDefinition] = {}
        self._status: dict[str, FactorStatus] = {}
        self._relations: set[tuple[str, str, RelationType]] = set()
        self._ic_history: dict[str, list[IcRecord]] = {}
        self._transitions: dict[str, list[StatusTransition]] = {}
        self._ic_seq = 0

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _require_factor(self, factor_id: str) -> None:
        if factor_id not in self._definitions:
            raise FactorKbError(f"未知因子: {factor_id!r}（未注册）")

    def _write_kb(self, entry: Mapping[str, object]) -> None:
        if self._kb_writer is None:
            return  # kb 写入回调可选：未注入仅内存留痕
        try:
            self._kb_writer(entry)
        except Exception:  # noqa: BLE001 — 外挂 kb 失败不阻断内存三表
            _log.exception("kb_writer 写入失败: %s", entry.get("factor_id"))

    # ── 定义表 ────────────────────────────────────────────────────────────

    def register_factor(self, definition: FactorDefinition) -> None:
        """注册因子定义（初始 DRAFT）：空字段/重复注册 → Fail-Closed。"""
        if not definition.factor_id:
            raise FactorKbError("factor_id 为空")
        if not definition.formula:
            raise FactorKbError(f"formula 为空: {definition.factor_id!r}")
        if not definition.category:
            raise FactorKbError(f"category 为空: {definition.factor_id!r}")
        if not definition.hypothesis:
            raise FactorKbError(f"hypothesis 为空: {definition.factor_id!r}")
        if definition.factor_id in self._definitions:
            raise FactorKbError(f"因子重复注册: {definition.factor_id!r}")
        self._definitions[definition.factor_id] = definition
        self._status[definition.factor_id] = FactorStatus.DRAFT
        self._write_kb({
            "kind": "factor_definition",
            "factor_id": definition.factor_id,
            "formula": definition.formula,
            "category": definition.category,
            "hypothesis": definition.hypothesis,
            "status": FactorStatus.DRAFT.value,
        })

    def get_definition(self, factor_id: str) -> FactorDefinition:
        """单因子定义查询（未知 → Fail-Closed）。"""
        self._require_factor(factor_id)
        return self._definitions[factor_id]

    def get_status(self, factor_id: str) -> FactorStatus:
        """单因子状态查询（未知 → Fail-Closed）。"""
        self._require_factor(factor_id)
        return self._status[factor_id]

    # ── 关系表（词表闭合） ────────────────────────────────────────────────

    def add_relation(
        self,
        src_factor: str,
        dst_factor: str,
        relation_type: RelationType,
    ) -> None:
        """登记因子关系：双端须已注册、类型须闭合词表、自环拒绝；重复幂等。"""
        self._require_factor(src_factor)
        self._require_factor(dst_factor)
        if src_factor == dst_factor:
            raise FactorKbError(f"自关系非法: {src_factor!r}")
        if not isinstance(relation_type, RelationType):
            raise FactorKbError(f"非法关系类型: {relation_type!r}（词表闭合）")
        self._relations.add((src_factor, dst_factor, relation_type))  # set 幂等

    def related_factors(
        self,
        factor_id: str,
        relation_type: RelationType | None = None,
    ) -> tuple[str, ...]:
        """相关性查询：双向邻居（可按关系类型过滤），factor_id 确定性排序。"""
        self._require_factor(factor_id)
        if relation_type is not None and not isinstance(relation_type, RelationType):
            raise FactorKbError(f"非法关系类型: {relation_type!r}（词表闭合）")
        neighbors = {
            dst if src == factor_id else src
            for src, dst, rtype in self._relations
            if (src == factor_id or dst == factor_id)
            and (relation_type is None or rtype is relation_type)
        }
        return tuple(sorted(neighbors))

    # ── 历史表（IC 序列/状态变迁） ────────────────────────────────────────

    def record_ic(
        self,
        factor_id: str,
        ic_value: float,
        observed_at: datetime.datetime | None = None,
    ) -> IcRecord:
        """追加 IC 观测：IC∈[-1,1] 越界 Fail-Closed；observed_at 缺省取注入时钟。"""
        self._require_factor(factor_id)
        if not -1.0 <= ic_value <= 1.0:
            raise FactorKbError(f"IC 越界 [-1,1]: {ic_value!r}")
        self._ic_seq += 1
        record = IcRecord(
            factor_id=factor_id,
            ic_value=float(ic_value),
            observed_at=observed_at or self._clock(),
            seq=self._ic_seq,
        )
        self._ic_history.setdefault(factor_id, []).append(record)
        return record

    def ic_series(self, factor_id: str) -> tuple[IcRecord, ...]:
        """IC 序列（按 (observed_at, seq) 确定性排序）。"""
        self._require_factor(factor_id)
        return tuple(sorted(
            self._ic_history.get(factor_id, ()),
            key=lambda r: (r.observed_at, r.seq),
        ))

    def ic_decay(self, factor_id: str) -> float:
        """IC 衰减斜率（对观测序号最小二乘；<2 样本 Fail-Closed）。

        返回每观测单位的 IC 变化率；负值=衰减。同输入必同输出。
        """
        series = self.ic_series(factor_id)
        if len(series) < 2:
            raise FactorKbError(f"IC 样本不足（须≥2）: {factor_id!r}")
        xs = list(range(len(series)))
        ys = [r.ic_value for r in series]
        x_bar = sum(xs) / len(xs)
        y_bar = sum(ys) / len(ys)
        denom = sum((x - x_bar) ** 2 for x in xs)
        if denom == 0:
            return 0.0
        return sum((x - x_bar) * (y - y_bar) for x, y in zip(xs, ys)) / denom

    # ── 状态机 ────────────────────────────────────────────────────────────

    def transition_status(self, factor_id: str, to_status: FactorStatus) -> StatusTransition:
        """状态迁移：非法迁移 Fail-Closed；留痕 + 同步 kb 写入回调。"""
        self._require_factor(factor_id)
        if not isinstance(to_status, FactorStatus):
            raise FactorKbError(f"非法状态: {to_status!r}（词表闭合）")
        from_status = self._status[factor_id]
        if to_status not in _ALLOWED_TRANSITIONS[from_status]:
            raise FactorKbError(
                f"非法状态迁移: {factor_id!r} {from_status.value} -> {to_status.value}"
            )
        transition = StatusTransition(
            factor_id=factor_id,
            from_status=from_status,
            to_status=to_status,
            changed_at=self._clock(),
        )
        self._status[factor_id] = to_status
        self._transitions.setdefault(factor_id, []).append(transition)
        self._write_kb({
            "kind": "factor_status",
            "factor_id": factor_id,
            "from_status": from_status.value,
            "to_status": to_status.value,
        })
        return transition

    def status_history(self, factor_id: str) -> tuple[StatusTransition, ...]:
        """状态变迁留痕（按写入序，确定性）。"""
        self._require_factor(factor_id)
        return tuple(self._transitions.get(factor_id, ()))

    # ── 查询 ─────────────────────────────────────────────────────────────

    def by_category(self, category: str) -> tuple[FactorDefinition, ...]:
        """按类别查询（factor_id 确定性排序）。"""
        if not category:
            raise FactorKbError("category 为空")
        return tuple(
            self._definitions[fid]
            for fid in sorted(self._definitions)
            if self._definitions[fid].category == category
        )

    def by_status(self, status: FactorStatus) -> tuple[FactorDefinition, ...]:
        """按状态查询（factor_id 确定性排序）。"""
        if not isinstance(status, FactorStatus):
            raise FactorKbError(f"非法状态: {status!r}（词表闭合）")
        return tuple(
            self._definitions[fid]
            for fid in sorted(self._definitions)
            if self._status[fid] is status
        )
