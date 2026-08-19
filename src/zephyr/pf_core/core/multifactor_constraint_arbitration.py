# [BLUEPRINT] MOD-PF-002 | docs/03_modules/_domain_portfolio_core/portfolio_optimizer/blueprint.md
# [MODULE] zephyr.pf_core.core.multifactor_constraint_arbitration
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.shared.contracts.risk_limits(CTR-003)
# [CONSUMERS] multifactor_pit_backtest; PortfolioOptimizer 后处理层
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬约束(C1/C5/C7)违反=不可行; 软约束违反仅记录接受; universe不可缩时总仓位降80%保硬约束
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空违规清单->FEASIBLE/ACCEPT
# [TESTS] tests/pf_core/test_multifactor_constraint_arbitration.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: violations(list[ConstraintViolation] 求解器违规清单) + universe_size(当前股票池大小)
# I2: C1-C7策略级约束参数(STRATEGY_CONSTRAINTS, 25号memo §3.5裁定目标态, CTR-003注入对齐MOD-PF-006)
# F1: arbitrate(①无违反→FEASIBLE/ACCEPT ②仅软违反→SOFT_VIOLATION/ACCEPT_WITH_PENALTY ③硬违反且可缩→SHRINK_UNIVERSE剔5只 ④硬违反不可缩→REDUCE_GROSS降至80%)
# F2: build_multifactor_risk_limits(C1-C7策略参数→CTR-003 RiskLimits注入, max_single_position=0.02/max_sector_concentration=0.05)
# O1: ArbitrationResult(status/action/target_universe_size/gross_leverage_cap)
# [/ALGO_FLOW]
"""25号memo §3.7#2 七约束链冲突仲裁（ConstraintArbitration）+ C1-C7↔CTR-003 对齐。

§3.5 的 7 约束链缺硬/软分级与冲突仲裁——本模块在组合优化器求解后增加
arbitrate() 后处理层，避免 cvxpy 返回不可行解或静默放宽。

硬约束（违反=不可行，必须满足）：C1 单票≤2% NAV / C5 单票≤日成交5% / C7 ≥20只
软约束（违反=次优，记录但接受，cvxpy 加松弛变量）：C2 行业≤±5% / C3 波动率≤25%
  / C4 换手≤30% / C6 因子暴露≤±10%

C1-C7 策略级约束链 ↔ MOD-PF-006 对齐（memo §6 待裁定项，CTR-003 注入，配置级）：
  STRATEGY_CONSTRAINTS 登记 §3.5 裁定目标态参数（严于 constraint_solver.py
  基础设施默认：行业绝对≤30%/相对±10% 等），build_multifactor_risk_limits()
  把可映射项注入 CTR-003 RiskLimits（C1→max_single_position=0.02，
  C2→max_sector_concentration=0.05）；C3/C4/C5/C6/C7 为策略侧运行时检查项，
  不在 CTR-003 schema 内，由策略层（本模块违规检测/RebalanceTrigger）消费。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from zephyr.shared.contracts.risk_limits import RiskLimits

__all__ = [
    "C1_SINGLE_POSITION_MAX",
    "STRATEGY_CONSTRAINTS",
    "HARD_CONSTRAINTS",
    "SOFT_CONSTRAINTS",
    "ConstraintViolation",
    "ArbitrationStatus",
    "ArbitrationAction",
    "ArbitrationResult",
    "arbitrate",
    "build_multifactor_risk_limits",
]

# ── C1-C7 策略级约束链参数（25号memo §3.5 裁定目标态，CTR-003 注入对齐）──
C1_SINGLE_POSITION_MAX = 0.02   # C1 单票 ≤ 2% NAV
C2_INDUSTRY_EXPOSURE_MAX = 0.05  # C2 单行业 ≤ ±5%（申万一级，相对基准）
C3_PORTFOLIO_VOL_MAX = 0.25     # C3 组合年化波动 ≤ 25%（滚动 60 日）
C4_DAILY_TURNOVER_MAX = 0.30    # C4 日均换手 ≤ 30%
C5_ADV_PARTICIPATION_MAX = 0.05  # C5 单票 ≤ 日成交 5%
C6_FACTOR_EXPOSURE_MAX = 0.10   # C6 合成因子暴露 ≤ 指数 ±10%
C7_MIN_HOLDINGS = 20            # C7 最小持仓 ≥ 20 只

STRATEGY_CONSTRAINTS: dict[str, float] = {
    "C1_single_position_max": C1_SINGLE_POSITION_MAX,
    "C2_industry_exposure_max": C2_INDUSTRY_EXPOSURE_MAX,
    "C3_portfolio_vol_max": C3_PORTFOLIO_VOL_MAX,
    "C4_daily_turnover_max": C4_DAILY_TURNOVER_MAX,
    "C5_adv_participation_max": C5_ADV_PARTICIPATION_MAX,
    "C6_factor_exposure_max": C6_FACTOR_EXPOSURE_MAX,
    "C7_min_holdings": float(C7_MIN_HOLDINGS),
}

HARD_CONSTRAINTS: frozenset[str] = frozenset({"C1", "C5", "C7"})
SOFT_CONSTRAINTS: frozenset[str] = frozenset({"C2", "C3", "C4", "C6"})

SOFT_PENALTY_WEIGHT = 100.0   # 软约束松弛惩罚权重（cvxpy 松弛变量系数）
MAX_UNIVERSE_SHRINK = 5       # 硬约束不可行时最多剔 5 只标的重解
REDUCED_GROSS_CAP = 0.80      # universe 不可缩时总仓位降至 80% 保硬约束


@dataclass(frozen=True)
class ConstraintViolation:
    """单条约束违规记录。

    Attributes:
        constraint_id: "C1".."C7"
        magnitude: 违反幅度（如超出上限的绝对值）
        detail: 人类可读说明
    """

    constraint_id: str
    magnitude: float
    detail: str = ""

    @property
    def is_hard(self) -> bool:
        return self.constraint_id in HARD_CONSTRAINTS


class ArbitrationStatus(str, Enum):
    FEASIBLE = "FEASIBLE"
    SOFT_VIOLATION = "SOFT_VIOLATION"
    HARD_INFEASIBLE = "HARD_INFEASIBLE"


class ArbitrationAction(str, Enum):
    ACCEPT = "ACCEPT"
    ACCEPT_WITH_PENALTY = "ACCEPT_WITH_PENALTY"
    SHRINK_UNIVERSE = "SHRINK_UNIVERSE"
    REDUCE_GROSS = "REDUCE_GROSS"


@dataclass(frozen=True)
class ArbitrationResult:
    """仲裁结果。

    Attributes:
        status: 可行性判定
        action: 处置动作
        soft_violations: 软约束违规清单（记录但接受）
        hard_violations: 硬约束违规清单
        target_universe_size: SHRINK_UNIVERSE 时的目标池大小（其余为 None）
        gross_leverage_cap: REDUCE_GROSS 时的总仓位上限 0.80（其余为 1.0）
        penalty_weight: 软约束松弛惩罚权重
    """

    status: ArbitrationStatus
    action: ArbitrationAction
    soft_violations: tuple[ConstraintViolation, ...] = ()
    hard_violations: tuple[ConstraintViolation, ...] = ()
    target_universe_size: int | None = None
    gross_leverage_cap: float = 1.0
    penalty_weight: float = SOFT_PENALTY_WEIGHT


def arbitrate(
    violations: list[ConstraintViolation],
    universe_size: int,
) -> ArbitrationResult:
    """7 约束链冲突仲裁——优化器求解后处理层。

    决策逻辑（25号memo §3.7#2）：
      ① 无违反 → FEASIBLE / ACCEPT
      ② 仅软约束违反 → SOFT_VIOLATION / ACCEPT_WITH_PENALTY（加松弛接受次优）
      ③ 硬约束违反且 universe_size-5 ≥ 20（C7 下限）→ HARD_INFEASIBLE /
         SHRINK_UNIVERSE 剔 5 只重解
      ④ 硬约束违反且 universe 不可缩 → REDUCE_GROSS 总仓位降至 80% 保硬约束
    """
    soft = tuple(v for v in violations if not v.is_hard)
    hard = tuple(v for v in violations if v.is_hard)
    if not violations:
        return ArbitrationResult(ArbitrationStatus.FEASIBLE, ArbitrationAction.ACCEPT)
    if not hard:
        return ArbitrationResult(
            ArbitrationStatus.SOFT_VIOLATION,
            ArbitrationAction.ACCEPT_WITH_PENALTY,
            soft_violations=soft,
        )
    shrunk = universe_size - MAX_UNIVERSE_SHRINK
    if shrunk >= C7_MIN_HOLDINGS:
        return ArbitrationResult(
            ArbitrationStatus.HARD_INFEASIBLE,
            ArbitrationAction.SHRINK_UNIVERSE,
            soft_violations=soft,
            hard_violations=hard,
            target_universe_size=shrunk,
        )
    return ArbitrationResult(
        ArbitrationStatus.HARD_INFEASIBLE,
        ArbitrationAction.REDUCE_GROSS,
        soft_violations=soft,
        hard_violations=hard,
        gross_leverage_cap=REDUCED_GROSS_CAP,
    )


def build_multifactor_risk_limits(
    as_of_date: datetime,
    idempotency_key: str,
    **overrides,
) -> RiskLimits:
    """C1-C7 策略级约束 → CTR-003 RiskLimits 注入（多因子 sleeve 上线前对齐）。

    可映射项：C1 单票≤2% → max_single_position；C2 行业≤±5% →
    max_sector_concentration（严于基础设施默认 0.30）；总仓位 1.0 不加杠杆。
    C3/C4/C5/C6/C7 非 CTR-003 schema 字段，由策略层运行时检查消费。
    """
    return RiskLimits(
        as_of_date=as_of_date,
        idempotency_key=idempotency_key,
        max_single_position=C1_SINGLE_POSITION_MAX,
        max_sector_concentration=C2_INDUSTRY_EXPOSURE_MAX,
        max_gross_leverage=1.0,
        **overrides,
    )
