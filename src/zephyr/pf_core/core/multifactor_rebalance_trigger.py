# [BLUEPRINT] MOD-PF-002 | docs/03_modules/_domain_portfolio_core/portfolio_optimizer/blueprint.md
# [MODULE] zephyr.pf_core.core.multifactor_rebalance_trigger
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] 无（纯函数）; 触发后调用 §3.5 七约束链重优化 + §3.7#2 仲裁
# [CONSUMERS] multifactor_pit_backtest; multifactor_holding_drift_monitor(critical强制换仓)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 最短间隔3天硬保护; TIME保底换仓不受成本门控; Inaction>Action才换仓(Perold 1988 IS框架)
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 漂移/排名变化为None->视为0不触发
# [TESTS] tests/pf_core/test_multifactor_rebalance_trigger.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: days_since_last(距上次换仓交易日数) + weight_drift(组合权重漂移) + top30_rank_change(top-30因子排名变化)
# I2: RebalanceTriggerParams(window 3-5/drift 0.15/rank 10×30归一化/cost 0.004/daily_alpha 0.0005)
# F1: should_rebalance(①<3天→WAIT ②≥5天→TIME保底(不受成本门控) ③漂移>15%且成本门控通过→DRIFT ④排名变化>10且成本门控通过→SIGNAL ⑤→HOLD)
# F2: _is_rebalance_worthwhile(Inaction Cost=drift×daily_alpha×expected_days vs Action Cost=0.4%×drift, break-even 8天, window_max=5<8安全垫)
# O1: RebalanceDecision(trigger/action/inaction_cost/action_cost/worthwhile)
# [/ALGO_FLOW]
"""25号memo §3.7#6 换仓触发决策（RebalanceTrigger 含 Inaction Cost，MVP 即做）。

§3.4 裁定 convergence_window = 3-5 天，本模块形式化"何时在窗口内触发换仓"——
过早换仓增成本，过晚换仓 alpha 流失。三触发器 + Inaction Cost 成本门控
（Perold 1988 Implementation Shortfall 框架）：

  Inaction Cost = drift × daily_alpha × expected_days（expected_days=5-days_since_last）
  Action Cost   = 0.4% × drift（A 股往返：印花税+佣金+滑点）
  Inaction > Action 才换仓。化简 break-even：0.05%×days > 0.4% → 8 天；
  convergence_window_max=5 < 8 提供安全垫——窗口内漂移/信号触发时若距保底
  仅剩 1-2 天，等保底触发省交易成本。

触发后调用 §3.5 七约束链重优化 + §3.7#2 约束仲裁。
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

__all__ = [
    "RebalanceTriggerParams",
    "RebalanceTriggerType",
    "RebalanceDecision",
    "should_rebalance",
]


@dataclass(frozen=True)
class RebalanceTriggerParams:
    """换仓触发参数（25号memo §3.7#6 参数表）。"""

    convergence_window_max: int = 5       # 保底换仓周期
    convergence_window_min: int = 3       # 最短换仓间隔（防过度换仓）
    drift_threshold: float = 0.15         # 组合权重漂移>15%→触发
    rank_change_threshold: float = 10.0   # top-30 因子排名变化>10 位→触发
    rank_normalization: float = 30.0      # 排名变化 ×30 归一化
    cost_aware: bool = True               # 换仓成本感知
    transaction_cost_rate: float = 0.004  # A 股往返交易成本 0.4%
    daily_alpha_estimate: float = 0.0005  # 日均因子 alpha 估计 0.05%（IC~0.03 保守）


class RebalanceTriggerType(str, Enum):
    WAIT = "WAIT"      # 最短间隔保护
    TIME = "TIME"      # 保底换仓（不受成本门控）
    DRIFT = "DRIFT"    # 漂移触发
    SIGNAL = "SIGNAL"  # 排名变化触发
    HOLD = "HOLD"      # 不换仓


@dataclass(frozen=True)
class RebalanceDecision:
    """换仓决策结果。"""

    trigger: RebalanceTriggerType
    should_rebalance: bool
    reason: str
    inaction_cost: float = 0.0
    action_cost: float = 0.0
    cost_gate_applied: bool = False
    rank_change_score: float = 0.0  # 排名变化 ×30 归一化得分


def _is_rebalance_worthwhile(
    drift: float,
    days_since_last: int,
    p: RebalanceTriggerParams,
) -> tuple[bool, float, float]:
    """Inaction Cost 成本门控（Perold 1988 IS 框架）。

    Returns:
        (worthwhile, inaction_cost, action_cost)
    """
    expected_days = max(p.convergence_window_max - days_since_last, 0)
    inaction_cost = drift * p.daily_alpha_estimate * expected_days
    action_cost = p.transaction_cost_rate * drift
    return inaction_cost > action_cost, inaction_cost, action_cost


def should_rebalance(
    days_since_last: int,
    weight_drift: float | None = 0.0,
    top30_rank_change: float | None = 0.0,
    params: RebalanceTriggerParams | None = None,
) -> RebalanceDecision:
    """换仓触发决策——三触发器 + Inaction Cost 成本门控。

    Args:
        days_since_last: 距上次换仓交易日数
        weight_drift: 组合权重漂移（Σ|Δw|/2 口径）
        top30_rank_change: top-30 因子平均排名变化（位）
        params: 触发参数

    Returns:
        RebalanceDecision
    """
    p = params or RebalanceTriggerParams()
    drift = float(weight_drift or 0.0)
    rank_change = float(top30_rank_change or 0.0)
    rank_score = rank_change * p.rank_normalization

    # ① 最短间隔保护
    if days_since_last < p.convergence_window_min:
        return RebalanceDecision(
            RebalanceTriggerType.WAIT, False,
            f"距上次换仓 {days_since_last}<{p.convergence_window_min} 天（最短间隔保护）",
            rank_change_score=rank_score,
        )
    # ② TIME 保底换仓（不受成本门控）
    if days_since_last >= p.convergence_window_max:
        return RebalanceDecision(
            RebalanceTriggerType.TIME, True,
            f"距上次换仓 {days_since_last}≥{p.convergence_window_max} 天→保底换仓",
            rank_change_score=rank_score,
        )

    def _gate() -> tuple[bool, float, float]:
        if not p.cost_aware:
            return True, 0.0, 0.0
        return _is_rebalance_worthwhile(drift, days_since_last, p)

    # ③ 漂移触发（成本门控）
    if drift > p.drift_threshold:
        ok, ina, act = _gate()
        if ok:
            return RebalanceDecision(
                RebalanceTriggerType.DRIFT, True,
                f"权重漂移 {drift:.1%}>{p.drift_threshold:.0%} 且 Inaction Cost 通过",
                ina, act, p.cost_aware, rank_score,
            )
        return RebalanceDecision(
            RebalanceTriggerType.HOLD, False,
            f"漂移 {drift:.1%} 超阈但 Inaction {ina:.5f}≤Action {act:.5f}→等保底省成本",
            ina, act, p.cost_aware, rank_score,
        )
    # ④ 信号触发（成本门控）
    if rank_change > p.rank_change_threshold:
        ok, ina, act = _gate()
        if ok:
            return RebalanceDecision(
                RebalanceTriggerType.SIGNAL, True,
                f"top-30 排名变化 {rank_change:.1f}>{p.rank_change_threshold:.0f} 位且成本门控通过",
                ina, act, p.cost_aware, rank_score,
            )
        return RebalanceDecision(
            RebalanceTriggerType.HOLD, False,
            f"排名变化 {rank_change:.1f} 超阈但成本门控未通过→等保底",
            ina, act, p.cost_aware, rank_score,
        )
    # ⑤ 均未达
    return RebalanceDecision(
        RebalanceTriggerType.HOLD, False, "未达触发条件",
        rank_change_score=rank_score,
    )
