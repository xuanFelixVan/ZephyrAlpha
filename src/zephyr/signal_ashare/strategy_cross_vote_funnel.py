# [BLUEPRINT] MOD-SIG-109 | docs/03_modules/_domain_signal/strategy_cross_vote_funnel/blueprint.md
# [MODULE] zephyr.signal_ashare.strategy_cross_vote_funnel
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] none（纯函数核，不 import zephyr 内部件）
# [CONSUMERS] （候选：第六层组合优化 B10-01505 W-P1-21）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 三席+额外投票方权重封闭；加权投票 score>0 approved；弃权不计入分母；全弃权→score=0 不通过；allow_buy=False 一票否决；kept ⊆ 输入（漏斗单调收敛）
# [MODIFY-GUARD] AUD-DRAFT-001 深挖批 B10-01504 行 + 候选注册表 CAND-TESTB-026
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未知 voter/重复 voter/非法 vote 值/权重越界/capacity≤0/空 symbol → ValueError（fail-closed）
# [TESTS] tests/signal_ashare/test_strategy_cross_vote_funnel.py
# [A_module] module_id=MOD-SIG-109 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""筛选漏斗第五层多策略交叉投票（MOD-SIG-109，B10-01504）。

在线信号层：策略A价值30%/B动量25%/C事件20% + C-034/C-036 额外投票方
+ 市场状态否决门；60 秒级→~30。
与 strategy_cpcv_matrix（MOD-BT-028，离线验证层）双视图分工。

依据: AUD-DRAFT-001 深挖批 B10-01504（裁定=做 P1）；蓝图 §0 边界
SSoT: depgraph blueprint_id=MOD-SIG-109
Version: 0.1.0
"""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Final

logger = logging.getLogger(__name__)

__all__: Final = [
    "CORE_SEAT_WEIGHTS",
    "EXTRA_VOTER_WEIGHTS",
    "CrossVoteConfig",
    "CrossVoteEntryResult",
    "CrossVoteFunnelResult",
    "MarketStateClearance",
    "StrategyCrossVoteFunnel",
    "StrategyVote",
]

# ------------------------------------------------------------------
# 封闭集
# ------------------------------------------------------------------
CORE_SEAT_WEIGHTS: Final[dict[str, float]] = {
    "value": 0.30,
    "momentum": 0.25,
    "event": 0.20,
}
EXTRA_VOTER_WEIGHTS: Final[dict[str, float]] = {
    "c034_inference": 0.10,
    "c036_synergy": 0.10,
}
_VOTER_REGISTRY: Final[set[str]] = set(CORE_SEAT_WEIGHTS) | set(EXTRA_VOTER_WEIGHTS)


# ------------------------------------------------------------------
# 契约
# ------------------------------------------------------------------
@dataclass(frozen=True)
class StrategyVote:
    voter: str
    vote: int  # 1=YES, 0=ABSTAIN, -1=NO

    def __post_init__(self):
        if self.voter not in _VOTER_REGISTRY:
            raise ValueError(f"未知 voter: {self.voter}")
        if self.vote not in (-1, 0, 1):
            raise ValueError("vote 必须为 -1/0/1")


@dataclass(frozen=True)
class MarketStateClearance:
    allow_buy: bool
    state_label: str = ""


@dataclass(frozen=True)
class CrossVoteConfig:
    pass_threshold: float = 0.0
    capacity_target: int = 30
    veto_enabled: bool = True

    def __post_init__(self):
        if self.capacity_target <= 0:
            raise ValueError("capacity_target 必须 >0")


@dataclass(frozen=True)
class CrossVoteEntryResult:
    symbol: str
    approved: bool
    vote_score: float
    vetoed: bool
    degraded: bool
    reason: str


@dataclass(frozen=True)
class CrossVoteFunnelResult:
    kept: list[str]
    excluded: dict[str, str]
    degraded: bool
    notes: str


# ------------------------------------------------------------------
# 实现
# ------------------------------------------------------------------
class StrategyCrossVoteFunnel:
    """多策略交叉投票漏斗（第五层在线信号层）。"""

    def __init__(self, config: CrossVoteConfig | None = None) -> None:
        self.config = config or CrossVoteConfig()

    def evaluate_symbol(
        self,
        symbol: str,
        votes: list[StrategyVote],
        market_state: MarketStateClearance | None = None,
    ) -> CrossVoteEntryResult:
        if not symbol:
            raise ValueError("symbol 不可为空")
        seen = set()
        for v in votes:
            if v.voter in seen:
                raise ValueError(f"重复 voter: {v.voter}")
            seen.add(v.voter)

        # 加权投票（弃权不计入分母）
        weights = {**CORE_SEAT_WEIGHTS, **EXTRA_VOTER_WEIGHTS}
        weighted_sum = 0.0
        weight_denom = 0.0
        for v in votes:
            if v.vote == 0:
                continue
            w = weights.get(v.voter, 0.0)
            weighted_sum += w * v.vote
            weight_denom += w

        if weight_denom <= 0:
            score = 0.0
        else:
            score = weighted_sum / weight_denom

        approved = score > self.config.pass_threshold
        vetoed = False
        degraded = False
        reasons: list[str] = []

        if self.config.veto_enabled and market_state is not None and not market_state.allow_buy:
            vetoed = True
            approved = False
            reasons.append("market_state_veto")
        elif market_state is None and self.config.veto_enabled:
            degraded = True
            reasons.append("market_state_none_degraded")

        if not approved and not vetoed:
            reasons.append(f"score={score:.4f}<=threshold={self.config.pass_threshold}")

        return CrossVoteEntryResult(
            symbol=symbol,
            approved=approved,
            vote_score=score,
            vetoed=vetoed,
            degraded=degraded,
            reason="; ".join(reasons) if reasons else "approved",
        )

    def run(
        self,
        candidates: list[str],
        votes_by_symbol: dict[str, list[StrategyVote]],
        market_state: MarketStateClearance | None = None,
    ) -> CrossVoteFunnelResult:
        entries: list[tuple[str, float, bool]] = []
        excluded: dict[str, str] = {}
        degraded = False
        for sym in candidates:
            vote_list = votes_by_symbol.get(sym)
            if vote_list is None:
                excluded[sym] = "no_votes"
                continue
            r = self.evaluate_symbol(sym, vote_list, market_state)
            if r.degraded:
                degraded = True
            if r.approved:
                entries.append((sym, r.vote_score, True))
            else:
                excluded[sym] = r.reason

        entries.sort(key=lambda x: (-x[1], x[0]))
        kept = [sym for sym, _, _ in entries[:self.config.capacity_target]]
        notes = "degraded" if degraded else ""
        return CrossVoteFunnelResult(
            kept=kept, excluded=excluded, degraded=degraded, notes=notes
        )
