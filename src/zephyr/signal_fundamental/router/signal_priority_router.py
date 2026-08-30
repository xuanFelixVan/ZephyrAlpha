# [BLUEPRINT] MOD-SIG-009 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/21_stock_selection_engine.md §3.3
# [MODULE] zephyr.signal_fundamental.router.signal_priority_router
# [DOMAIN] D_FUNDAMENTAL_SIGNAL
# [DEPENDENCIES] none
# [CONSUMERS] zephyr.signal_fundamental.router.signal_conflict_resolver
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 排序确定性（同分按 created_seq 升序 FIFO）；风险类恒先于机会类（同置信度口径）；纯函数无副作用
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] confidence∉[0,1] → ValueError；空输入 → 空结果
# [TESTS] tests/signal_fundamental/router/test_signal_priority_router.py
# [A_module] module_id=MOD-SIG-009 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: RoutableSignal（signal_id/symbol/类别/置信度/到达序号/来源）
# A1: 优先级分 = kind_base(风险1000/机会100/元0) + confidence×100
# A2: 排序——优先级分降序，同分按 created_seq 升序（FIFO 公平），再按 signal_id 字典序兜底确定性
# O1: RouteResult(ordered signal_ids + scores + 首信号 = 当前应处理信号)
# [/ALGO_FLOW]
"""
信号优先级路由器（MOD-SIG-009）。

多个信号同时到达时按优先级决定处理顺序，避免重要信号被淹没。优先级仲裁原则
（21 号 memo BM-SEL-02-L 契约）：**风险信号 > 机会信号，硬约束优先**——同类内
按置信度降序，同置信度按到达先后（FIFO）。

路由分 = kind_base + confidence×100：类别差（1000/100/0）恒大于置信度差
（0-100），保证风险类在任何置信度下都先于机会类被处理。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: sig 参数
#   fields: 参数 sig，类型注解 RoutableSignal
#   code: signal_priority_router.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: cfg 参数
#   fields: 参数 cfg（无注解）
#   code: signal_priority_router.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: signals 参数
#   fields: 参数 signals，类型注解 list[RoutableSignal]
#   code: signal_priority_router.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: signal_priority_router.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① priority_score
#   name_en: priority_score
#   intro: 优先级分 = kind_base + confidence×scale。
#   desc: 优先级分 = kind_base + confidence×scale。confidence∉[0,1] → ValueError。；源码 L151-L155
#   inputs: sig cfg
#   outputs: float
# - id: A2
#   name_zh: ② route_signals
#   name_en: route_signals
#   intro: 按优先级排序信号：风险>机会>元；同类置信度降序；同分 FIFO（created_seq 升序）。
#   desc: 按优先级排序信号：风险>机会>元；同类置信度降序；同分 FIFO（created_seq 升序）。；源码 L158-L167
#   inputs: signals config
#   outputs: RouteResult
#   （注：A2 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: float
#   name_en: float
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.signal_fundamental.router.signal_conflict_resolver
# - id: O2
#   name_zh: RouteResult
#   name_en: RouteResult
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.signal_fundamental.router.signal_conflict_resolver
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Final

__all__: Final = [
    "PriorityRouterConfig",
    "RoutableSignal",
    "RouteResult",
    "SignalKind",
    "route_signals",
]


class SignalKind(str, Enum):
    """信号类别（决定基础优先级）。"""

    RISK = "RISK"  # 风险信号（止损/风控否决/系统性风险）
    OPPORTUNITY = "OPPORTUNITY"  # 机会信号（买入/加仓）
    META = "META"  # 元信号（状态通知/留痕，不直接触发动作）


#: 类别基础优先级（风险 ≫ 机会 ≫ 元；间隔 10× 于置信度量程保证类别绝对优先）
_KIND_BASE: Final = {
    SignalKind.RISK: 1000.0,
    SignalKind.OPPORTUNITY: 100.0,
    SignalKind.META: 0.0,
}


@dataclass(frozen=True)
class PriorityRouterConfig:
    """路由器参数。

    Attributes:
        confidence_scale: 置信度量程（×confidence 加进基础分，默认 100 ≪ 类别间隔）
    """

    confidence_scale: float = 100.0


@dataclass(frozen=True)
class RoutableSignal:
    """待路由信号记录。"""

    signal_id: str
    symbol: str
    kind: str = "OPPORTUNITY"  # SignalKind 值
    confidence: float = 0.5  # [0,1]
    created_seq: int = 0  # 到达序号（单调递增，FIFO tiebreak 输入）
    source: str = ""  # 来源模块（留痕）


@dataclass(frozen=True)
class RouteResult:
    """路由输出。"""

    ordered: tuple[str, ...]  # signal_id 处理顺序（首元素=当前应处理）
    scores: dict[str, float] = field(default_factory=dict)  # {signal_id: 优先级分}


def priority_score(sig: RoutableSignal, *, cfg: PriorityRouterConfig) -> float:
    """优先级分 = kind_base + confidence×scale。confidence∉[0,1] → ValueError。"""
    if not 0.0 <= sig.confidence <= 1.0:
        raise ValueError(f"confidence 必须 ∈ [0,1]: {sig.confidence}")
    return _KIND_BASE[SignalKind(sig.kind)] + sig.confidence * cfg.confidence_scale


def route_signals(
    signals: list[RoutableSignal],
    *,
    config: PriorityRouterConfig | None = None,
) -> RouteResult:
    """按优先级排序信号：风险>机会>元；同类置信度降序；同分 FIFO（created_seq 升序）。"""
    cfg = config or PriorityRouterConfig()
    scores = {s.signal_id: priority_score(s, cfg=cfg) for s in signals}
    ordered = sorted(signals, key=lambda s: (-scores[s.signal_id], s.created_seq, s.signal_id))
    return RouteResult(ordered=tuple(s.signal_id for s in ordered), scores=scores)
