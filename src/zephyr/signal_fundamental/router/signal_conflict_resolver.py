# [BLUEPRINT] MOD-SIG-010 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/21_stock_selection_engine.md §3.3
# [MODULE] zephyr.signal_fundamental.router.signal_conflict_resolver
# [DOMAIN] D_FUNDAMENTAL_SIGNAL
# [DEPENDENCIES] none
# [CONSUMERS] (待 sleeve 编排层 / StrategyBook 接线)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 同 symbol 方向矛盾才构成冲突；风险否决绝对优先；不能做空——利空方向输出 REJECT 非 SHORT；规则链首命中即终局；纯函数无副作用
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] confidence∉[0,1] → ValueError；空输入 → 空结果
# [TESTS] tests/signal_fundamental/router/test_signal_conflict_resolver.py
# [A_module] module_id=MOD-SIG-010 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: ConflictSignal（signal_id/symbol/方向 LONG·EXIT/类别/置信度/到达序号/来源）
# A1: 按 symbol 分组——单方向组直通 ADOPT（no_conflict）
# A2: 规则链裁定——R1 风险否决(风险类高置信→REJECT) → R2 置信度差(≥margin 高者胜) → R3 时效(新者胜) → R4 来源优先级 → R5 平局 DEFER
# O1: list[ConflictResolution]（symbol/action/winner/losers/rule_applied 留痕）
# [/ALGO_FLOW]
"""信号冲突消解器（MOD-SIG-010）。

多个信号互相矛盾（一个说买一个说卖）时裁定听谁的，避免信号打架系统无所适从。
A 股不能做空（宪章 §2 约束三）：方向空间 = LONG（买入/持有）vs EXIT（卖出/回避），
利空方向输出 REJECT（不动作/退出候选），绝无 SHORT。

规则链（首命中即终局，全程留痕 rule_applied）：
  R1 风险否决——任一 RISK 类信号置信度 ≥ veto_confidence → REJECT（风控绝对优先，
     与 21 号 BM-SEL-02-L"风险信号 > 机会信号，硬约束优先"一致）；
  R2 置信度差——双方最高置信度差 ≥ margin → 高置信方胜；
  R3 时效——平局取最新到达方（created_seq 大者）；
  R4 来源优先级——按 source_priority 表（未登记来源=0）；
  R5 仍平局 → DEFER（挂起不动作，等下一信号或人工）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Final, Mapping

__all__: Final = [
    "ConflictResolution",
    "ConflictResolverConfig",
    "ConflictSignal",
    "ResolutionAction",
    "resolve_conflicts",
]


class ResolutionAction(str, Enum):
    """裁定动作。"""

    ADOPT = "ADOPT"  # 采纳 LONG 方（无冲突直通或 LONG 胜出）
    REJECT = "REJECT"  # 否决（风险否决或 EXIT 方胜出——剔除/不买入）
    DEFER = "DEFER"  # 平局挂起（规则链穷尽仍无法裁定）


@dataclass(frozen=True)
class ConflictResolverConfig:
    """消解参数。

    Attributes:
        veto_confidence: R1 风险否决置信度门槛（风险类 ≥ 此值即否决）
        margin: R2 置信度差门槛（差值 ≥ 此值高者胜）
        source_priority: R4 来源优先级表（分高者胜，未登记=0）
    """

    veto_confidence: float = 0.8
    margin: float = 0.15
    source_priority: Mapping[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class ConflictSignal:
    """待裁定信号记录。"""

    signal_id: str
    symbol: str
    direction: str = "LONG"  # LONG / EXIT（A 股无做空，方向空间二元）
    kind: str = "OPPORTUNITY"  # RISK / OPPORTUNITY（R1 输入）
    confidence: float = 0.5  # [0,1]
    created_seq: int = 0  # 到达序号（R3 时效输入）
    source: str = ""  # 来源模块（R4 输入）


@dataclass(frozen=True)
class ConflictResolution:
    """单 symbol 裁定输出（留痕件）。"""

    symbol: str
    action: ResolutionAction
    rule_applied: str  # no_conflict / R1_risk_veto / R2_confidence / R3_recency / R4_source / R5_defer
    winner_id: str = ""  # 胜出信号（DEFER/空组为 ""）
    loser_ids: tuple[str, ...] = ()


def _best(signals: list[ConflictSignal], key) -> ConflictSignal:
    """取 key 最大者（同分按 created_seq 降序、signal_id 升序保证确定性）。"""
    return sorted(signals, key=lambda s: (-key(s), -s.created_seq, s.signal_id))[0]


def _resolve_group(group: list[ConflictSignal], cfg: ConflictResolverConfig) -> ConflictResolution:
    """单 symbol 组裁定（规则链 R1→R5）。"""
    symbol = group[0].symbol
    longs = [s for s in group if s.direction == "LONG"]
    exits = [s for s in group if s.direction == "EXIT"]
    ids = tuple(s.signal_id for s in group)
    if not exits:
        winner = _best(longs, lambda s: s.confidence)
        return ConflictResolution(symbol, ResolutionAction.ADOPT, "no_conflict", winner.signal_id, tuple(i for i in ids if i != winner.signal_id))
    if not longs:
        winner = _best(exits, lambda s: s.confidence)
        return ConflictResolution(symbol, ResolutionAction.REJECT, "no_conflict", winner.signal_id, tuple(i for i in ids if i != winner.signal_id))
    # R1 风险否决：任一 RISK 类高置信 → REJECT（赢家=该风险信号）
    risk_signals = [s for s in group if s.kind == "RISK" and s.confidence >= cfg.veto_confidence]
    if risk_signals:
        winner = _best(risk_signals, lambda s: s.confidence)
        return ConflictResolution(symbol, ResolutionAction.REJECT, "R1_risk_veto", winner.signal_id, tuple(i for i in ids if i != winner.signal_id))
    best_long = _best(longs, lambda s: s.confidence)
    best_exit = _best(exits, lambda s: s.confidence)
    # R2 置信度差
    diff = best_long.confidence - best_exit.confidence
    if abs(diff) >= cfg.margin:
        winner = best_long if diff > 0 else best_exit
        action = ResolutionAction.ADOPT if diff > 0 else ResolutionAction.REJECT
        return ConflictResolution(symbol, action, "R2_confidence", winner.signal_id, tuple(i for i in ids if i != winner.signal_id))
    # R3 时效（最新到达方）
    if best_long.created_seq != best_exit.created_seq:
        winner = best_long if best_long.created_seq > best_exit.created_seq else best_exit
        action = ResolutionAction.ADOPT if winner is best_long else ResolutionAction.REJECT
        return ConflictResolution(symbol, action, "R3_recency", winner.signal_id, tuple(i for i in ids if i != winner.signal_id))
    # R4 来源优先级
    pl = cfg.source_priority.get(best_long.source, 0)
    pe = cfg.source_priority.get(best_exit.source, 0)
    if pl != pe:
        winner = best_long if pl > pe else best_exit
        action = ResolutionAction.ADOPT if winner is best_long else ResolutionAction.REJECT
        return ConflictResolution(symbol, action, "R4_source", winner.signal_id, tuple(i for i in ids if i != winner.signal_id))
    # R5 平局挂起
    return ConflictResolution(symbol, ResolutionAction.DEFER, "R5_defer", "", ids)


def resolve_conflicts(
    signals: list[ConflictSignal],
    *,
    config: ConflictResolverConfig | None = None,
) -> list[ConflictResolution]:
    """冲突消解主入口：按 symbol 分组逐组走规则链。confidence 非法 → ValueError。"""
    cfg = config or ConflictResolverConfig()
    groups: dict[str, list[ConflictSignal]] = {}
    for s in signals:
        if not 0.0 <= s.confidence <= 1.0:
            raise ValueError(f"confidence 必须 ∈ [0,1]: {s.confidence}")
        if s.direction not in ("LONG", "EXIT"):
            raise ValueError(f"direction 必须 ∈ LONG/EXIT（A 股无做空）: {s.direction}")
        groups.setdefault(s.symbol, []).append(s)
    return [_resolve_group(groups[symbol], cfg) for symbol in sorted(groups)]
