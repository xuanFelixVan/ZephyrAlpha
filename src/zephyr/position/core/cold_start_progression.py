# [BLUEPRINT] MOD-POS-020 | docs/03_modules/_domain_position/blueprint.md | §
# [MODULE] zephyr.position.core.cold_start_progression
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.position.core.strategy_book (COLD_START_RATIO_* 常量只读消费，不改动); zephyr.shared.foundation.errors
# [CONSUMERS] 调用方（新策略上线冷启动编排；53 号迁移路径 PARALLEL→SHADOW→GRAY_RAMP 承载时装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 晋升须正面证据（数据缺失→HOLD 不晋升）; 回退须正面失败证据（缺失→HOLD 至窗满才回退）; 连续 2 次回退→ESCALATE_RETIREMENT（61 号 §3.9）; 非 T2 恒 retrain_paused=True; 比例口径与 StrategyBook 冷启动常量一致（0.30/0.60/1.00）
# [MODIFY-GUARD] 61_lifecycle_multi_ai.md §3.1
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ColdStartProgressionError(ZA-POS-0018)
# [TESTS] tests/position/test_cold_start_progression.py
# [A_module] module_id=MOD-POS-020 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: ColdStartEvalInput(stage/days_in_stage/divergence/risk_downgraded/rolling_sharpe/oos_sharpe/loss/decay_alert/consecutive_rollbacks)
# I2: ColdStartProgressionConfig(T0 5-10 日/T1 10-20 日/divergence 阈值 0.30/Sharpe 系数 0.7/0.85/回退上限 2)
# F1: T0 门控（divergence<阈值 且未风控降级 → PROMOTE T1；失败证据 → ROLLBACK SIMULATION）
# F2: T1 门控（Rolling Sharpe≥OOS×0.7 且无连续 3 日亏损超限 → PROMOTE T2；否则 ROLLBACK T0）
# F3: T2 门控（Rolling Sharpe≥OOS×0.85 且 Decay 无告警 → HOLD；否则 ROLLBACK T1）
# F4: 回退计数（连续 2 次 → ESCALATE_RETIREMENT）；retrain_paused=stage≠T2
# O1: ColdStartEvalResult(stage/action/position_ratio/retrain_paused/consecutive_rollbacks/detail)
# [/ALGO_FLOW]
"""D_POSITION — 冷启动 T0/T1/T2 渐进建仓评估（61 号 §3.1，函数级）。

时间+表现双门控阶梯放量：T0 观察 ×30%（5-10 交易日）→ T1 小仓 ×60%（10-20 交易日）
→ T2 常规 ×100%。任一阶段门控未达标 → 回退上一阶段（T0 回退到模拟阶段）；连续 2 次
回退 → 进入 61 号 §3.9 退役评估。冷启动期间（非 T2）暂停重训练。

与 StrategyBook 冷启动（30 号 §6.7，按上线天数三段式）**只读兼容**：比例常量直接复用
``COLD_START_RATIO_COLD/HALF``（0.30/0.60），本模块不改动 strategy_book.py——
StrategyBook 按天数自动晋升（MVP 基线），本模块是 61 号双门控细化版（晋升须表现证据），
两口径比例一致可叠加消费（RegimeMetaAllocator cold_start_ratios 取最紧）。

依据: 61_lifecycle_multi_ai §3.1（渐进建仓节奏细化表 + 回退/暂停重训练纪律）
Version: 0.1.0
"""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from enum import Enum
from typing import Final

from zephyr.position.core.strategy_book import (
    COLD_START_RATIO_COLD,
    COLD_START_RATIO_HALF,
)
from zephyr.shared.foundation.errors import ZephyrBaseError

logger = logging.getLogger(__name__)


class ColdStartProgressionError(ZephyrBaseError):
    """冷启动评估输入非法（负天数 / NaN 指标 / 负偏离）。"""

    error_code = "ZA-POS-0018"


class ColdStartStage(str, Enum):
    """冷启动阶段（SIMULATION=T0 回退终点，61 号 §3.1）。"""

    SIMULATION = "SIMULATION"
    T0_OBSERVE = "T0"
    T1_SMALL = "T1"
    T2_FULL = "T2"


class ColdStartAction(str, Enum):
    HOLD = "hold"
    PROMOTE = "promote"
    ROLLBACK = "rollback"
    ESCALATE_RETIREMENT = "escalate_retirement"


_STAGE_RATIO: Final[dict[ColdStartStage, float]] = {
    ColdStartStage.SIMULATION: 0.0,
    ColdStartStage.T0_OBSERVE: COLD_START_RATIO_COLD,   # 0.30（与 StrategyBook 口径一致）
    ColdStartStage.T1_SMALL: COLD_START_RATIO_HALF,     # 0.60
    ColdStartStage.T2_FULL: 1.0,
}
_ROLLBACK_TARGET: Final[dict[ColdStartStage, ColdStartStage]] = {
    ColdStartStage.T0_OBSERVE: ColdStartStage.SIMULATION,
    ColdStartStage.T1_SMALL: ColdStartStage.T0_OBSERVE,
    ColdStartStage.T2_FULL: ColdStartStage.T1_SMALL,
}


@dataclass(frozen=True)
class ColdStartProgressionConfig:
    """双门控参数（61 号 §3.1 表）。"""

    divergence_threshold: float = 0.30   # T0：实盘 vs 模拟 divergence 阈值（对齐 30 号 §6.7 PnL 偏离 ≤30% 质量门）
    sharpe_factor_t1: float = 0.70       # T1 晋升：Rolling Sharpe ≥ OOS × 0.7
    sharpe_factor_t2: float = 0.85       # T2 维持：Rolling Sharpe ≥ OOS × 0.85
    t0_min_days: int = 5
    t0_max_days: int = 10
    t1_min_days: int = 10
    t1_max_days: int = 20
    loss_day_limit: int = 3              # 连续亏损日超限阈值
    max_consecutive_rollbacks: int = 2   # 连续回退上限 → 退役评估


@dataclass(frozen=True)
class ColdStartEvalInput:
    """冷启动评估输入（门控数据由调用方供给，None=缺失）。"""

    stage: ColdStartStage
    days_in_stage: int
    sim_live_divergence: float | None = None  # T0 门控：实盘 vs 模拟偏离
    risk_downgraded: bool = False             # T0 门控：风控触发降级
    rolling_sharpe: float | None = None       # T1/T2 门控：阶段内滚动 Sharpe
    oos_sharpe: float | None = None           # 回测 OOS Sharpe 基准
    consecutive_loss_days: int = 0            # T1 门控：连续亏损日
    decay_alert_active: bool = False          # T2 门控：Decay Detection 5 监控点告警
    consecutive_rollbacks: int = 0            # 已累计连续回退次数


@dataclass(frozen=True)
class ColdStartEvalResult:
    """冷启动评估产物。"""

    stage: ColdStartStage
    action: ColdStartAction
    position_ratio: float
    retrain_paused: bool
    consecutive_rollbacks: int
    detail: str


def _result(
    stage: ColdStartStage, action: ColdStartAction, rollbacks: int, detail: str,
) -> ColdStartEvalResult:
    return ColdStartEvalResult(
        stage=stage,
        action=action,
        position_ratio=_STAGE_RATIO[stage],
        retrain_paused=stage is not ColdStartStage.T2_FULL,
        consecutive_rollbacks=rollbacks,
        detail=detail,
    )


def _rollback(stage: ColdStartStage, rollbacks: int, cfg: ColdStartProgressionConfig, why: str) -> ColdStartEvalResult:
    new_rollbacks = rollbacks + 1
    if new_rollbacks >= cfg.max_consecutive_rollbacks:
        logger.warning("冷启动 %s: 连续 %d 次回退 → 进入退役评估（61 号 §3.9）", stage.value, new_rollbacks)
        return _result(
            stage, ColdStartAction.ESCALATE_RETIREMENT, new_rollbacks,
            f"{why}；连续 {new_rollbacks} 次回退达上限 → 退役评估",
        )
    target = _ROLLBACK_TARGET[stage]
    logger.warning("冷启动 %s → %s 回退（%s）", stage.value, target.value, why)
    return _result(target, ColdStartAction.ROLLBACK, new_rollbacks, f"{why} → 回退 {target.value}")


def evaluate_cold_start(
    inp: ColdStartEvalInput,
    cfg: ColdStartProgressionConfig | None = None,
) -> ColdStartEvalResult:
    """评估冷启动阶段流转（纯函数，61 号 §3.1 双门控）。

    门控口径：晋升须正面证据（数据缺失 → HOLD 至阶段窗满才回退）；
    回退须正面失败证据（divergence 超标 / 风控降级 / Sharpe 不达标 / 连续亏损超限 /
    Decay 告警）；T2 常规阶段数据缺失 → HOLD 不回退。
    """
    cfg = cfg or ColdStartProgressionConfig()
    if inp.days_in_stage < 0 or inp.consecutive_loss_days < 0 or inp.consecutive_rollbacks < 0:
        raise ColdStartProgressionError(
            f"天数/计数须 >= 0: {inp.days_in_stage}/{inp.consecutive_loss_days}/{inp.consecutive_rollbacks}"
        )
    for name, v in (("sim_live_divergence", inp.sim_live_divergence),
                    ("rolling_sharpe", inp.rolling_sharpe), ("oos_sharpe", inp.oos_sharpe)):
        if v is not None and (math.isnan(v) or math.isinf(v)):
            raise ColdStartProgressionError(f"{name} 非法: {v}")
    if inp.sim_live_divergence is not None and inp.sim_live_divergence < 0:
        raise ColdStartProgressionError(f"sim_live_divergence 须 >= 0: {inp.sim_live_divergence}")

    if inp.stage is ColdStartStage.SIMULATION:
        return _result(inp.stage, ColdStartAction.HOLD, 0, "模拟阶段（T0 回退终点）")
    if inp.stage is ColdStartStage.T0_OBSERVE:
        return _eval_t0(inp, cfg)
    if inp.stage is ColdStartStage.T1_SMALL:
        return _eval_t1(inp, cfg)
    return _eval_t2(inp, cfg)


def _eval_t0(inp: ColdStartEvalInput, cfg: ColdStartProgressionConfig) -> ColdStartEvalResult:
    if inp.days_in_stage < cfg.t0_min_days:
        return _result(inp.stage, ColdStartAction.HOLD, inp.consecutive_rollbacks,
                       f"T0 观察期第 {inp.days_in_stage}/{cfg.t0_min_days} 天，未达评估窗")
    if inp.risk_downgraded:
        return _rollback(inp.stage, inp.consecutive_rollbacks, cfg, "T0 风控触发降级")
    if inp.sim_live_divergence is not None:
        if inp.sim_live_divergence < cfg.divergence_threshold:
            return _result(ColdStartStage.T1_SMALL, ColdStartAction.PROMOTE, 0,
                           f"T0 门控通过（divergence {inp.sim_live_divergence:.2%} < {cfg.divergence_threshold:.0%}）→ 晋升 T1")
        return _rollback(inp.stage, inp.consecutive_rollbacks, cfg,
                         f"T0 divergence {inp.sim_live_divergence:.2%} ≥ {cfg.divergence_threshold:.0%}")
    # 数据缺失：窗内 HOLD，窗满回退
    if inp.days_in_stage < cfg.t0_max_days:
        return _result(inp.stage, ColdStartAction.HOLD, inp.consecutive_rollbacks,
                       "T0 门控数据缺失（divergence 未供给），观察至窗满")
    return _rollback(inp.stage, inp.consecutive_rollbacks, cfg, "T0 窗满门控数据仍缺失")


def _eval_t1(inp: ColdStartEvalInput, cfg: ColdStartProgressionConfig) -> ColdStartEvalResult:
    if inp.days_in_stage < cfg.t1_min_days:
        return _result(inp.stage, ColdStartAction.HOLD, inp.consecutive_rollbacks,
                       f"T1 小仓期第 {inp.days_in_stage}/{cfg.t1_min_days} 天，未达评估窗")
    if inp.consecutive_loss_days >= cfg.loss_day_limit:
        return _rollback(inp.stage, inp.consecutive_rollbacks, cfg,
                         f"T1 连续 {inp.consecutive_loss_days} 日亏损超限（≥{cfg.loss_day_limit}）")
    if inp.rolling_sharpe is not None and inp.oos_sharpe is not None:
        floor = inp.oos_sharpe * cfg.sharpe_factor_t1
        if inp.rolling_sharpe >= floor:
            return _result(ColdStartStage.T2_FULL, ColdStartAction.PROMOTE, 0,
                           f"T1 门控通过（Rolling Sharpe {inp.rolling_sharpe:.2f} ≥ OOS×{cfg.sharpe_factor_t1}={floor:.2f}）→ 晋升 T2")
        return _rollback(inp.stage, inp.consecutive_rollbacks, cfg,
                         f"T1 Rolling Sharpe {inp.rolling_sharpe:.2f} < {floor:.2f}")
    if inp.days_in_stage < cfg.t1_max_days:
        return _result(inp.stage, ColdStartAction.HOLD, inp.consecutive_rollbacks,
                       "T1 门控数据缺失（Sharpe 未供给），观察至窗满")
    return _rollback(inp.stage, inp.consecutive_rollbacks, cfg, "T1 窗满门控数据仍缺失")


def _eval_t2(inp: ColdStartEvalInput, cfg: ColdStartProgressionConfig) -> ColdStartEvalResult:
    if inp.decay_alert_active:
        return _rollback(inp.stage, inp.consecutive_rollbacks, cfg, "T2 Decay Detection 告警")
    if inp.rolling_sharpe is not None and inp.oos_sharpe is not None:
        floor = inp.oos_sharpe * cfg.sharpe_factor_t2
        if inp.rolling_sharpe < floor:
            return _rollback(inp.stage, inp.consecutive_rollbacks, cfg,
                             f"T2 Rolling Sharpe {inp.rolling_sharpe:.2f} < OOS×{cfg.sharpe_factor_t2}={floor:.2f}")
    return _result(inp.stage, ColdStartAction.HOLD, 0, "T2 常规阶段（门控维持）")


__all__: Final = [
    "ColdStartAction",
    "ColdStartEvalInput",
    "ColdStartEvalResult",
    "ColdStartProgressionConfig",
    "ColdStartProgressionError",
    "ColdStartStage",
    "evaluate_cold_start",
]
