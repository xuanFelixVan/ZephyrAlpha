# [BLUEPRINT] MOD-RK-046 | docs/03_modules/_domain_risk/risk_contagion_modeler/blueprint.md
# [MODULE] zephyr.risk.risk_contagion_modeler
# [DOMAIN] D_RISK
# [DEPENDENCIES] 无（协议核心纯内存；边权/会话/评分回调/时钟 全注入）
# [CONSUMERS] 运行时装配批（盘后风险传播建模装配：相关性+产业链边注入 / 评分入风控参考输出）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 节点集闭合(边端点须在节点集内); 边权∈(0,1]Decimal; 衰减∈(0,1); 冲击沿边衰减传播(逐轮δ×边权×衰减,|δ|<ε终止); 传染评分=节点暴露度归一∈[0,1]; 盘后运行语义(会话非post_close Fail-Closed); 邻接视图按(target,kind)确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_risk/risk_contagion_modeler/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] RiskContagionError(占位 ZA-RK-UNREGISTERED-RISK-CONTAGION)——空节点集/未知节点/非法边权衰减/零冲击/会话缺失或非盘后时抛
# [TESTS] tests/risk/test_risk_contagion_modeler.py
# [A_module] module_id=MOD-RK-046 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""RiskContagionModeler — 风险传播建模器（MOD-RK-046）。

B14-04692（AUD-DRAFT-001-DIGEST P2 波 P2-W09，CAND-RSK-050，A9 M15-S01）：
风险传播网络——板块/个股相关性 + 产业链边建图（边权注入）+ 冲击传导路径
模拟（初始冲击沿边衰减传播）+ 传染评分（节点暴露度）+ 评分入风控参考输出
+ 盘后运行语义。Diebold-Yilmaz 思想轻量版（确定性衰减传播，不做方差分解）。

查重分工（蓝图 §0）：ashare_systemic_risk_detector=系统性风险检测（本件=传
播路径模拟与暴露评分，不做检测判定）；correlation/copula 族=相关性估计（本
件边权全注入，不估计相关性）；stress_test_engine=情景压测（本件=网络传导，
不跑情景库）。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Callable, Final, Iterable

_log = logging.getLogger(__name__)

__all__: Final = [
    "ContagionEdge",
    "ContagionReport",
    "EdgeKind",
    "RiskContagionError",
    "RiskContagionModeler",
    "ShockEvent",
]

_ZERO: Final = Decimal("0")
_ONE: Final = Decimal("1")
_POST_CLOSE: Final = "post_close"


class RiskContagionError(Exception):
    """风险传播建模输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-RK-UNREGISTERED-RISK-CONTAGION。
    """


class EdgeKind(str, Enum):
    """传播边类型（词表闭合）。"""

    CORRELATION = "correlation"
    INDUSTRY_CHAIN = "industry_chain"


@dataclass(frozen=True)
class ContagionEdge:
    """传播边（边权注入，frozen）。"""

    source: str
    target: str
    weight: Decimal
    kind: EdgeKind


@dataclass(frozen=True)
class ShockEvent:
    """初始冲击事件（节点 + 冲击幅度，负值=损失冲击，frozen）。"""

    node: str
    shock: Decimal


@dataclass(frozen=True)
class ContagionReport:
    """传播模拟报告（暴露度 + 归一传染评分，frozen）。"""

    impacts: tuple[tuple[str, Decimal], ...]  # (node, 累计暴露) 按 node 排序
    scores: tuple[tuple[str, Decimal], ...]  # (node, 归一评分∈[0,1]) 按 node 排序
    rounds_used: int
    evaluated_at: datetime.datetime

    def impact_of(self, node: str) -> Decimal:
        """单节点暴露度查询。"""
        return dict(self.impacts).get(node, _ZERO)

    def score_of(self, node: str) -> Decimal:
        """单节点传染评分查询。"""
        return dict(self.scores).get(node, _ZERO)


class RiskContagionModeler:
    """风险传播建模器（建图 + 衰减传导模拟 + 传染评分，盘后语义）。"""

    def __init__(
        self,
        *,
        nodes: Iterable[str],
        edges: Iterable[ContagionEdge] = (),
        decay: Decimal = Decimal("0.5"),
        epsilon: Decimal = Decimal("0.000001"),
        max_rounds: int = 16,
        session_provider: Callable[[], str] | None = None,
        score_sink: Callable[[ContagionReport], None] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        node_set = {n for n in nodes if n}
        if not node_set:
            raise RiskContagionError("节点集为空")
        if not (_ZERO < decay < _ONE):
            raise RiskContagionError(f"衰减系数越界(0,1): {decay!r}")
        if epsilon <= _ZERO:
            raise RiskContagionError(f"终止阈值非正: {epsilon!r}")
        if max_rounds < 1:
            raise RiskContagionError(f"最大轮次非法: {max_rounds!r}")
        self._nodes: set[str] = set(node_set)
        self._adj: dict[str, list[ContagionEdge]] = {n: [] for n in node_set}
        self._decay = decay
        self._epsilon = epsilon
        self._max_rounds = max_rounds
        self._session = session_provider
        self._score_sink = score_sink
        self._clock = clock or datetime.datetime.now
        for edge in edges:
            self.add_edge(edge)

    # ── 建图（相关性 + 产业链边，边权注入） ──────────────────────────────

    def add_edge(self, edge: ContagionEdge) -> None:
        """登记传播边：端点须在节点集内，边权 ∈ (0,1]，自环拒绝。"""
        if not isinstance(edge, ContagionEdge):
            raise RiskContagionError(f"非法传播边: {edge!r}")
        if not isinstance(edge.kind, EdgeKind):
            raise RiskContagionError(f"非法边类型: {edge.kind!r}")
        if edge.source not in self._nodes:
            raise RiskContagionError(f"边源节点未知: {edge.source!r}")
        if edge.target not in self._nodes:
            raise RiskContagionError(f"边目标节点未知: {edge.target!r}")
        if edge.source == edge.target:
            raise RiskContagionError(f"自环边非法: {edge.source!r}")
        if not (_ZERO < edge.weight <= _ONE):
            raise RiskContagionError(f"边权越界(0,1]: {edge.weight!r}")
        self._adj[edge.source].append(edge)

    def graph_nodes(self) -> tuple[str, ...]:
        """节点视图（排序确定性）。"""
        return tuple(sorted(self._nodes))

    def neighbors_of(self, node: str) -> tuple[ContagionEdge, ...]:
        """邻接视图（按 (target, kind) 确定性排序）。"""
        if node not in self._nodes:
            raise RiskContagionError(f"未知节点: {node!r}")
        return tuple(
            sorted(self._adj[node], key=lambda e: (e.target, e.kind.value))
        )

    # ── 冲击传导模拟（沿边衰减传播） ──────────────────────────────────────

    def simulate(self, shocks: Iterable[ShockEvent]) -> ContagionReport:
        """初始冲击沿边衰减传播 → 暴露度 + 归一传染评分（盘后运行语义）。"""
        if self._session is None:
            raise RiskContagionError("session_provider 未注入（盘后语义无法确认）")
        session = self._session()
        if session != _POST_CLOSE:
            raise RiskContagionError(f"盘后运行语义违反: 当前会话 {session!r}")

        totals: dict[str, Decimal] = {n: _ZERO for n in self._nodes}
        pending: dict[str, Decimal] = {}
        seen_shock = False
        for shock in shocks:
            if not isinstance(shock, ShockEvent):
                raise RiskContagionError(f"非法冲击事件: {shock!r}")
            if shock.node not in self._nodes:
                raise RiskContagionError(f"冲击节点未知: {shock.node!r}")
            if shock.shock == _ZERO:
                raise RiskContagionError(f"零冲击非法: {shock.node!r}")
            pending[shock.node] = pending.get(shock.node, _ZERO) + shock.shock
            seen_shock = True
        if not seen_shock:
            raise RiskContagionError("冲击集为空")

        rounds_used = 0
        for node, delta in pending.items():
            totals[node] += delta
        while pending and rounds_used < self._max_rounds:
            nxt: dict[str, Decimal] = {}
            for node in sorted(pending):
                delta = pending[node]
                for edge in self._adj[node]:
                    propagated = delta * edge.weight * self._decay
                    if propagated != _ZERO:
                        nxt[edge.target] = nxt.get(edge.target, _ZERO) + propagated
            if not nxt or max(abs(d) for d in nxt.values()) < self._epsilon:
                break
            rounds_used += 1
            for node, delta in nxt.items():
                totals[node] += delta
            pending = nxt

        max_abs = max(abs(d) for d in totals.values())
        impacts = tuple(sorted(totals.items()))
        scores = tuple(
            (node, (abs(delta) / max_abs if max_abs else _ZERO))
            for node, delta in impacts
        )
        report = ContagionReport(
            impacts=impacts,
            scores=scores,
            rounds_used=rounds_used,
            evaluated_at=self._clock(),
        )
        if self._score_sink is not None:
            try:
                self._score_sink(report)  # 评分入风控参考输出
            except Exception:  # noqa: BLE001 — 回调失败不阻断（蓝图 §1）
                _log.exception("score_sink 回调失败")
        return report
