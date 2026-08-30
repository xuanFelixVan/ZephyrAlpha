# [BLUEPRINT] MOD-INT-EVENT-CHAIN | docs/03_modules/_domain_intelligence/event_chain_causal_graph/blueprint.md
# [MODULE] zephyr.intelligence.event_chain_causal_graph
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] 无（因果图核心纯内存；granger 检验器/时钟全注入）
# [CONSUMERS] 运行时装配批（granger 检验器接 causal_inference_engine / 事件注册接事件采集 / 概率查询接信号层）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 事件类型四类词表闭合(policy|industry_data|announcement|overseas)；event_id 唯一；因果边仅连已注册节点且无自环；滞后阶数 1..max_lag；p 值须 < p_threshold 否则拒绝注册边；P(B|A) 频次估计+拉普拉斯平滑恒落 [0,1]；同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_intelligence/event_chain_causal_graph/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] EventChainError(占位 ZA-IT-UNREGISTERED-EVENT-CHAIN)——非法事件类型/未知节点/自环/非法滞后/序列非法/p 值越界或不显著/重复边/未知边查询时抛
# [TESTS] tests/intelligence/test_event_chain_causal_graph.py
# [A_module] module_id=MOD-INT-EVENT-CHAIN | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
EventChainCausalGraph — 事件链推理因果图（MOD-INT-EVENT-CHAIN）。

B10-01448（AUD-DRAFT-001-DIGEST P2 波 P2-W04，CAND-AISA-011，A1 模块41）：
事件节点表（政策/行业数据/公告/海外**四类词表闭合**）+ **Granger 因果边**
（滞后阶数 + p 值阈值注册，granger 检验器注入）+ **贝叶斯网络条件概率表**
（P(B|A) 频次估计 + 拉普拉斯平滑）+ 概率查询接口。pgmpy 思想轻量内存版。
与 D-ALT-22 传导模板分工：本件=统计因果，彼=规则传导。

查重分工（蓝图 §0）：causal_inference_engine=信号侧因果推断实现（本件经
注入 granger_tester 消费其语义，不重建检验算法）；event_* 族=事件打分/地
图（本件=事件间统计因果边与条件概率，零交集）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: granger_tester 参数
#   fields: 参数 granger_tester（无注解）
#   code: event_chain_causal_graph.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: p_threshold 参数
#   fields: 参数 p_threshold（无注解）
#   code: event_chain_causal_graph.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: max_lag 参数
#   fields: 参数 max_lag（无注解）
#   code: event_chain_causal_graph.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: laplace_alpha 参数
#   fields: 参数 laplace_alpha（无注解）
#   code: event_chain_causal_graph.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① EventChainCausalGraph
#   name_en: EventChainCausalGraph
#   intro: 事件链因果图件（节点表 + Granger 边 + 贝叶斯 CPT + 概率查询）。
#   desc: 事件链因果图件（节点表 + Granger 边 + 贝叶斯 CPT + 概率查询）。；公共方法（定义序）: register_event, event, node_count, add_granger_edge, ed…
#   inputs: granger_tester p_threshold max_lag laplace_alpha
#   outputs: 返回值
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: EventChainCausalGraph
#   downstream: 运行时装配批（granger 检验器接 causal_inference_engine / 事件注册接事件采集 / 概率查询接信号层）
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
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "EventChainCausalGraph",
    "EventChainError",
    "EventNode",
    "EventType",
    "GrangerEdge",
]


class EventChainError(Exception):
    """事件链因果图输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-IT-UNREGISTERED-EVENT-CHAIN。
    """


class EventType(str, Enum):
    """事件节点类型（四类词表闭合）。"""

    POLICY = "policy"
    INDUSTRY_DATA = "industry_data"
    ANNOUNCEMENT = "announcement"
    OVERSEAS = "overseas"


@dataclass(frozen=True)
class EventNode:
    """事件节点（frozen）。"""

    event_id: str
    event_type: EventType
    name: str
    occurred_at: datetime.datetime


@dataclass(frozen=True)
class GrangerEdge:
    """Granger 因果边（cause → effect，frozen）。"""

    cause_id: str
    effect_id: str
    lag: int
    p_value: float


@dataclass
class _EdgeStats:
    """单边观测计数（内部可变）：windows=cause 发生窗口数，hits=effect 跟随数。"""

    edge: GrangerEdge
    windows: int = 0
    hits: int = 0


class EventChainCausalGraph:
    """事件链因果图件（节点表 + Granger 边 + 贝叶斯 CPT + 概率查询）。"""

    def __init__(
        self,
        *,
        granger_tester: Callable[[Sequence[float], Sequence[float], int], float],
        p_threshold: float = 0.05,
        max_lag: int = 5,
        laplace_alpha: float = 1.0,
    ) -> None:
        if not callable(granger_tester):
            raise EventChainError("granger_tester 未注入（禁止内置实现）")
        if not (0.0 < p_threshold < 1.0):
            raise EventChainError(f"p_threshold 越界 (0,1): {p_threshold!r}")
        if max_lag < 1:
            raise EventChainError(f"max_lag 非正: {max_lag!r}")
        if laplace_alpha <= 0.0:
            raise EventChainError(f"laplace_alpha 非正: {laplace_alpha!r}")
        self._tester = granger_tester
        self._p_threshold = p_threshold
        self._max_lag = max_lag
        self._alpha = laplace_alpha
        self._nodes: dict[str, EventNode] = {}
        self._edges: dict[tuple[str, str], _EdgeStats] = {}

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _require_node(self, event_id: str) -> EventNode:
        node = self._nodes.get(event_id)
        if node is None:
            raise EventChainError(f"未知事件节点: {event_id!r}（未注册）")
        return node

    def _require_edge(self, cause_id: str, effect_id: str) -> _EdgeStats:
        stats = self._edges.get((cause_id, effect_id))
        if stats is None:
            raise EventChainError(f"未知因果边: {cause_id!r} -> {effect_id!r}")
        return stats

    # ── 事件节点表 ────────────────────────────────────────────────────────

    def register_event(self, node: EventNode) -> None:
        """注册事件节点：类型词表闭合；event_id 唯一。"""
        if not node.event_id:
            raise EventChainError("event_id 为空")
        if not isinstance(node.event_type, EventType):
            raise EventChainError(f"非法事件类型: {node.event_type!r}")
        if not node.name:
            raise EventChainError("事件名为空")
        if node.event_id in self._nodes:
            raise EventChainError(f"event_id 重复: {node.event_id!r}")
        self._nodes[node.event_id] = node

    def event(self, event_id: str) -> EventNode:
        """单节点查询（未知 → Fail-Closed）。"""
        return self._require_node(event_id)

    def node_count(self) -> int:
        """已注册节点数。"""
        return len(self._nodes)

    # ── Granger 因果边 ────────────────────────────────────────────────────

    def add_granger_edge(
        self,
        cause_id: str,
        effect_id: str,
        *,
        lag: int,
        cause_series: Sequence[float],
        effect_series: Sequence[float],
    ) -> GrangerEdge:
        """注册因果边：注入检验器算 p 值，p < p_threshold 方可注册（否则拒绝）。

        滞后阶数须 1..max_lag；两序列等长且长度 > lag；自环/重复边拒绝。
        """
        self._require_node(cause_id)
        self._require_node(effect_id)
        if cause_id == effect_id:
            raise EventChainError(f"自环非法: {cause_id!r}")
        if not (1 <= lag <= self._max_lag):
            raise EventChainError(f"滞后阶数越界 1..{self._max_lag}: {lag!r}")
        if (cause_id, effect_id) in self._edges:
            raise EventChainError(f"因果边重复: {cause_id!r} -> {effect_id!r}")
        if not cause_series or not effect_series or len(cause_series) != len(effect_series):
            raise EventChainError("因果序列为空或长度不等")
        if len(cause_series) <= lag:
            raise EventChainError(f"序列长度 {len(cause_series)} 不足覆盖滞后 {lag}")
        p_value = float(self._tester(cause_series, effect_series, lag))
        if not (0.0 <= p_value <= 1.0):
            raise EventChainError(f"granger p 值越界 [0,1]: {p_value!r}")
        if p_value >= self._p_threshold:
            _log.warning(
                "Granger 边拒绝: %s -> %s lag=%d p=%.4f >= 阈值 %.4f（不显著）",
                cause_id,
                effect_id,
                lag,
                p_value,
                self._p_threshold,
            )
            raise EventChainError(
                f"Granger 因果不显著: {cause_id} -> {effect_id} p={p_value:.4f} >= p_threshold={self._p_threshold}"
            )
        edge = GrangerEdge(cause_id=cause_id, effect_id=effect_id, lag=lag, p_value=p_value)
        self._edges[(cause_id, effect_id)] = _EdgeStats(edge=edge)
        return edge

    def edges_of(self, event_id: str) -> tuple[GrangerEdge, ...]:
        """以该节点为因的出边（按 effect_id 确定性排序）。"""
        self._require_node(event_id)
        out = [s.edge for (c, _), s in self._edges.items() if c == event_id]
        out.sort(key=lambda e: e.effect_id)
        return tuple(out)

    # ── 贝叶斯条件概率表（频次估计 + 拉普拉斯平滑） ───────────────────────

    def record_outcome(self, cause_id: str, effect_id: str, *, effect_occurred: bool) -> None:
        """记录一次观测窗口：cause 已发生，effect 是否在滞后窗口内跟随。"""
        stats = self._require_edge(cause_id, effect_id)
        stats.windows += 1
        if effect_occurred:
            stats.hits += 1

    def probability(self, effect_id: str, *, given_cause_id: str) -> float:
        """P(B|A) = (hits + α) / (windows + 2α)（拉普拉斯平滑，恒落 [0,1]）。"""
        stats = self._require_edge(given_cause_id, effect_id)
        return (stats.hits + self._alpha) / (stats.windows + 2.0 * self._alpha)

    def cpt(self, cause_id: str) -> tuple[tuple[str, float], ...]:
        """单因节点条件概率表视图（按 effect_id 确定性排序）。"""
        self._require_node(cause_id)
        rows = [(e, self.probability(e, given_cause_id=cause_id)) for (c, e) in self._edges if c == cause_id]
        rows.sort(key=lambda kv: kv[0])
        return tuple(rows)
