# [BLUEPRINT] MOD-RK-28 | docs/03_modules/_domain_risk/adaptive_risk_forecast/blueprint.md
# [MODULE] zephyr.risk.core.adaptive_risk_forecast
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.signal_ashare.conditional_density_predictor(MOD-SIG-043); zephyr.signal_ashare.conformal_predictor(MOD-SIG-044); zephyr.shared.foundation.errors; numpy
# [CONSUMERS] MOD-RK-30(Adaptive Risk Coordinator, C-004 三层联动盘前预判); MOD-RK-05D(var_intraday_recalc 盘前基线, 设计契约)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] var_pct/cvar_pct/conformal_var_pct 非负(损失幅度口径); cvar_pct>=var_pct; conformal_var_pct=var_pct+margin; limit_scale∈(0,1]; 无校准集→margin=0+degraded=True(无覆盖率保证保守方向); 纯函数无IO无未来函数
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidForwardVarConfigError
# [TESTS] tests/risk/test_adaptive_risk_forecast.py
# [TTL] permanent

# [ALGO_FLOW]
# I1: 历史收益序列 + 平行条件标签(可空) + 目标条件桶(可空)
# I2: 共形校准 (预测, 实际) 对(可空)
# I3: ForwardVarConfig(var_level/conformal_alpha/var_limit_pct/sit_out_var_pct/密度窗口)
# A1: 条件PDF密度预测(复用MOD-SIG-043)→var_pct/cvar_pct(负值口径取正)
# A2: 共形校准(复用MOD-SIG-044 SplitConformalPredictor)→margin q̂; 无校准→margin=0+degraded
# A3: 限额对照(limit_scale=min(1,limit/conformal_var), breached, sit_out)
# O1: ForwardVarForecast(frozen) → C-004 盘前裁决 / var_intraday_recalc 盘前基线
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A2
# I3 --> A1
# I3 --> A3
# A1 --> A3
# A2 --> A3
# A3 --> O1
"""

Adaptive Risk Forecast — 前瞻 VaR 共形预判层 (MOD-RK-28, C-004 ①预判层 MVP)

C-004 自适应风控三层体系（预判+监控+熔断）的预判层能力底座：
盘前用条件 PDF（MOD-SIG-043 条件经验分布）产出前瞻 VaR/CVaR，外裹共形安全缓冲
（MOD-SIG-044 split-conformal，分布无关有限样本边际覆盖率数学保证），对照风险
限额产出 limit_scale / sit_out 盘前建议；输出可作 MOD-RK-05D var_intraday_recalc
的盘前基线（premarket_baseline）。

底座复用裁定（W1c 同族整合）：本模块不重复实现 VaR/密度/共形算法，仅做装配与
限额对照；裁决与三层联动属 MOD-RK-30 编排层，本模块只产数据契约。

SSoT: docs/03_modules/_domain_risk/adaptive_risk_forecast/blueprint.md
Version: 0.1.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Final, Iterable, Sequence

from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.signal_ashare.conditional_density_predictor import (
    ConditionalDensityConfig,
    conditional_density,
)
from zephyr.signal_ashare.conformal_predictor import SplitConformalPredictor

_logger = logging.getLogger(__name__)

__all__: Final = [
    "ForwardVarConfig",
    "ForwardVarForecast",
    "InvalidForwardVarConfigError",
    "forecast_forward_var",
]


class InvalidForwardVarConfigError(ZephyrBaseError):
    """前瞻预判层配置/输入非法（Fail-Closed）。"""


@dataclass(frozen=True)
class ForwardVarConfig:
    """前瞻 VaR 预判配置（C 类可调参数）。

    Attributes:
        var_level: VaR/CVaR 置信水平（透传条件密度 var_level）
        conformal_alpha: 共形显著性水平（目标覆盖率 1-alpha）
        var_limit_pct: 日前瞻 VaR 限额（NAV 占比，正数）
        sit_out_var_pct: 共形 VaR 达此占比 → sit_out 盘前坐出建议
        density_window: 条件密度 trailing 窗口
        density_min_samples: 条件桶最小样本数（不足回退全样本 degraded）
    """

    var_level: float = 0.95
    conformal_alpha: float = 0.05
    var_limit_pct: float = 0.02
    sit_out_var_pct: float = 0.04
    density_window: int = 250
    density_min_samples: int = 60

    def __post_init__(self) -> None:
        if not 0.0 < self.var_level < 1.0:
            raise InvalidForwardVarConfigError(f"var_level 必须 ∈ (0,1): {self.var_level}")
        if not 0.0 < self.conformal_alpha < 1.0:
            raise InvalidForwardVarConfigError(f"conformal_alpha 必须 ∈ (0,1): {self.conformal_alpha}")
        if self.var_limit_pct <= 0.0:
            raise InvalidForwardVarConfigError(f"var_limit_pct 必须 >0: {self.var_limit_pct}")
        if self.sit_out_var_pct <= 0.0:
            raise InvalidForwardVarConfigError(f"sit_out_var_pct 必须 >0: {self.sit_out_var_pct}")
        if self.density_window < 1:
            raise InvalidForwardVarConfigError(f"density_window 必须 ≥1: {self.density_window}")
        if self.density_min_samples < 1:
            raise InvalidForwardVarConfigError(f"density_min_samples 必须 ≥1: {self.density_min_samples}")


@dataclass(frozen=True)
class ForwardVarForecast:
    """前瞻 VaR 盘前预判结果（损失幅度口径，正数=亏损占 NAV 比例）。"""

    var_pct: float  # 条件PDF VaR（正数=损失幅度）
    cvar_pct: float  # 条件PDF CVaR/ES（>= var_pct）
    conformal_margin_pct: float  # 共形安全缓冲 q̂（0=无校准）
    conformal_var_pct: float  # 共形VaR = var_pct + margin（覆盖率保证口径）
    limit_scale: float  # 限额缩放建议 ∈ (0,1]（超限收紧）
    limit_breached: bool  # conformal_var_pct > var_limit_pct
    sit_out: bool  # 盘前坐出建议（conformal_var_pct >= sit_out_var_pct）
    degraded: bool  # 条件桶回退或校准缺失（无完整覆盖率保证）
    n_samples: int  # 密度样本数
    n_calibration: int  # 共形校准样本数


def forecast_forward_var(
    returns: Iterable[float],
    *,
    conditions: Sequence[str] | None = None,
    condition: str | None = None,
    calibration_predictions: Iterable[float] | None = None,
    calibration_actuals: Iterable[float] | None = None,
    config: ForwardVarConfig | None = None,
) -> ForwardVarForecast:
    """盘前前瞻 VaR/CVaR + 共形 VaR 预判主入口。

    Args:
        returns: 历史收益序列（trailing 使用，无未来函数）
        conditions: 与 returns 平行的条件标签（波动率桶/regime，可空）
        condition: 目标条件桶（conditions 提供时必填）
        calibration_predictions: 共形校准集历史点预测（可空）
        calibration_actuals: 共形校准集实际值（与 predictions 等长）
        config: 配置（None → 默认）

    Returns:
        ForwardVarForecast

    Raises:
        InvalidForwardVarConfigError: 配置非法 / 校准集只给单侧
        ValueError: 收益样本不足 / 校准集长度不一致（透传底层校验）
    """
    cfg = config or ForwardVarConfig()

    density = conditional_density(
        list(returns),
        conditions,
        condition=condition,
        config=ConditionalDensityConfig(
            window=cfg.density_window,
            min_samples=cfg.density_min_samples,
            var_level=cfg.var_level,
        ),
    )
    var_pct = max(0.0, -float(density.var_95))
    cvar_pct = max(var_pct, -float(density.cvar_95))

    margin = 0.0
    n_cal = 0
    cal_degraded = True
    if (calibration_predictions is None) != (calibration_actuals is None):
        raise InvalidForwardVarConfigError("共形校准集 predictions/actuals 必须成对提供")
    if calibration_predictions is not None and calibration_actuals is not None:
        predictor = SplitConformalPredictor(alpha=cfg.conformal_alpha)
        predictor.fit(list(calibration_predictions), list(calibration_actuals))
        margin = float(predictor.margin or 0.0)
        n_cal = predictor.predict_interval(0.0).n_calibration
        cal_degraded = False

    conformal_var = var_pct + margin
    if conformal_var > 0.0:
        limit_scale = min(1.0, cfg.var_limit_pct / conformal_var)
    else:
        limit_scale = 1.0
    limit_breached = conformal_var > cfg.var_limit_pct
    sit_out = conformal_var >= cfg.sit_out_var_pct

    if sit_out:
        _logger.warning(
            "前瞻VaR预判 sit_out: conformal_var=%.4f >= 阈值 %.4f", conformal_var, cfg.sit_out_var_pct
        )

    return ForwardVarForecast(
        var_pct=var_pct,
        cvar_pct=cvar_pct,
        conformal_margin_pct=margin,
        conformal_var_pct=conformal_var,
        limit_scale=limit_scale,
        limit_breached=limit_breached,
        sit_out=sit_out,
        degraded=bool(density.degraded) or cal_degraded,
        n_samples=int(density.n_samples),
        n_calibration=n_cal,
    )
