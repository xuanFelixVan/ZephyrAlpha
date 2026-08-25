# [BLUEPRINT] MOD-RK-38 | docs/03_modules/_domain_risk/factor_exposure_manager/blueprint.md
# [MODULE] zephyr.risk.core.factor_exposure_manager
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-RK-02(Pre-Trade 预警消费候选); MOD-RK-03(实时监控消费候选); 盘前检查装配批
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] exposure[f]=Σ(w_s×loading[s][f])(权重归一化Σw=1); 缺载荷按0计并列uncovered披露; |exposure|>limit→BREACH, ≥limit×warn_ratio→WARNING; limits外因子只计量不预警; breaches按|exposure/limit|降序; 报告frozen; 非法输入Fail-Closed
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidFactorExposureInputError
# [TESTS] tests/risk/core/test_factor_exposure_manager.py
# [A_module] module_id=MOD-RK-38 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Factor Exposure Manager — 因子敞口管理器 (MOD-RK-38, CAND-RSK-041, B10-02083 PC-14)

Barra 式组合因子敞口计量（A1 §30.1.3）：组合在某因子上的敞口 =
Σ(个股权重 × 个股因子载荷)。输出全因子敞口矩阵 + 逐因子超限判定
（|exposure| > limit → BREACH；≥ limit×warn_ratio → WARNING），供风控预警
与盘前/实时监控消费。

与既有件分工（蓝图 §0 查重裁定）：MOD-RK-16 为因子/残差风险方差分解（需协方差
矩阵，事后归因）；MOD-RK-07 为行业权重集中度（HHI，无载荷维度）；MOD-RK-13 为
跨策略拥挤度（策略级单值敞口）；D_PF_CORE performance_attribution_engine 为
绩效归因（事后）。本模块为"持仓×因子载荷→组合敞口矩阵+超限预警"判定核心，
口径互不重复。

纪律：纯函数无 IO；持仓权重与因子载荷由调用方注入（D_POSITION/D_FACTOR，
三维解耦，不越域取数）；超限仅产预警信号并经 audit_sink 回调留痕（处置委托
MOD-RK-02/MOD-RK-03 等既有执行面，审计落账委托 D_GOV_AUDIT）。

依据: blueprint.md（MOD-RK-38）§3 核心规则；Barra USE3/CNE5 风险模型口径
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 持仓权重
#   fields: positions {symbol: weight}（long-only 非负，Σw>0 自动归一）
#   code: compute_exposures() positions 参数
# - id: I2
#   name: 因子载荷
#   fields: factor_loadings {symbol: {factor: loading}}（缺失→uncovered 披露按 0 计）
#   code: compute_exposures() factor_loadings 参数
# - id: I3
#   name: 配置 FactorExposureConfig
#   fields: limits {factor: 上限>0} + warn_ratio∈(0,1)（默认 0.8）
#   code: FactorExposureConfig
# 层: 算法
# - id: A1
#   name_zh: ① 校验与权重归一化
#   name_en: _validate_and_normalize
#   intro: 非空持仓/非负有限权重/有限载荷校验；w/=Σw
# - id: A2
#   name_zh: ② 敞口矩阵计算
#   name_en: compute_exposures
#   intro: exposure[f]=Σ w_s×loading[s][f]；因子全集=limits∪载荷键
# - id: A3
#   name_zh: ③ 超限分级
#   name_en: _grade
#   intro: |e|>limit→BREACH; |e|≥limit×warn_ratio→WARNING; 按|e/limit|降序
# 层: 输出
# - id: O1
#   name: FactorExposureReport
#   fields: exposures/breaches/uncovered_symbols/weight_sum（frozen）
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A3
# A1 --> A2
# A2 --> A3
# A3 --> O1
# [/ALGO_FLOW]
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Final

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "ExposureBreach",
    "ExposureSeverity",
    "FactorExposureConfig",
    "FactorExposureManager",
    "FactorExposureReport",
    "InvalidFactorExposureInputError",
]

_DEFAULT_WARN_RATIO: Final = 0.8


class InvalidFactorExposureInputError(ZephyrBaseError):
    """因子敞口管理器输入/配置非法（Fail-Closed）。"""


class ExposureSeverity(str, Enum):
    """敞口超限分级（OK 不入 breaches）。"""

    WARNING = "WARNING"  # |exposure| ≥ limit×warn_ratio
    BREACH = "BREACH"  # |exposure| > limit


@dataclass(frozen=True)
class FactorExposureConfig:
    """因子敞口配置（C 类可调）。"""

    limits: Mapping[str, float]  # 因子敞口上限（绝对值对称，>0）
    warn_ratio: float = _DEFAULT_WARN_RATIO  # 预警线 = limit × warn_ratio，∈(0,1)

    def __post_init__(self) -> None:
        if not self.limits:
            raise InvalidFactorExposureInputError("limits 不能为空（至少一个受控因子）")
        for factor, limit in self.limits.items():
            if not factor:
                raise InvalidFactorExposureInputError("limits 因子名不能为空")
            lv = float(limit)
            if not math.isfinite(lv) or lv <= 0:
                raise InvalidFactorExposureInputError(f"limit 必须为正有限值: {factor}={limit}")
        wr = float(self.warn_ratio)
        if not math.isfinite(wr) or not 0.0 < wr < 1.0:
            raise InvalidFactorExposureInputError(f"warn_ratio 必须 ∈(0,1): {self.warn_ratio}")


@dataclass(frozen=True)
class ExposureBreach:
    """单因子超限事件（frozen）。"""

    factor: str
    exposure: float
    limit: float
    severity: ExposureSeverity


@dataclass(frozen=True)
class FactorExposureReport:
    """组合因子敞口报告（frozen）。"""

    exposures: Mapping[str, float]  # 全因子敞口矩阵（limits ∪ 载荷键）
    breaches: tuple[ExposureBreach, ...]  # 按 |exposure/limit| 降序
    uncovered_symbols: tuple[str, ...]  # 缺载荷标的（载荷按 0 计，如实披露）
    weight_sum: float  # 归一化后权重和（恒=1，校验用）


def _require_finite(name: str, value: float) -> float:
    v = float(value)
    if not math.isfinite(v):
        raise InvalidFactorExposureInputError(f"{name} 必须为有限值: {value}")
    return v


class FactorExposureManager:
    """因子敞口管理器（载荷加权敞口矩阵 + 超限预警）。

    Args:
        config: FactorExposureConfig（limits + warn_ratio）
        audit_sink: 超限事件回调（委托 D_GOV_AUDIT 落账；None=仅返回报告）
    """

    def __init__(
        self,
        config: FactorExposureConfig,
        audit_sink: Callable[[ExposureBreach], None] | None = None,
    ) -> None:
        if not isinstance(config, FactorExposureConfig):
            raise InvalidFactorExposureInputError(f"config 类型非法: {type(config).__name__}")
        self._config = config
        self._audit_sink = audit_sink

    @property
    def config(self) -> FactorExposureConfig:
        return self._config

    def compute_exposures(
        self,
        *,
        positions: Mapping[str, float],
        factor_loadings: Mapping[str, Mapping[str, float]],
    ) -> FactorExposureReport:
        """计算组合因子敞口矩阵 + 超限分级。

        Args:
            positions: {symbol: weight}（long-only 非负；Σw>0 自动归一化）
            factor_loadings: {symbol: {factor: loading}}（缺失标的列 uncovered）

        Returns:
            FactorExposureReport（frozen）

        Raises:
            InvalidFactorExposureInputError: 输入非法（Fail-Closed）
        """
        if not positions:
            raise InvalidFactorExposureInputError("positions 不能为空")
        weights: dict[str, float] = {}
        for symbol, weight in positions.items():
            if not symbol:
                raise InvalidFactorExposureInputError("持仓标的名不能为空")
            w = _require_finite(f"positions[{symbol}]", weight)
            if w < 0:
                raise InvalidFactorExposureInputError(f"负权重拒绝（long-only）: {symbol}={weight}")
            weights[symbol] = w
        total = sum(weights.values())
        if total <= 0:
            raise InvalidFactorExposureInputError("权重和必须 >0（全零持仓拒绝）")
        weights = {s: w / total for s, w in weights.items()}

        uncovered: list[str] = []
        exposures: dict[str, float] = dict.fromkeys(self._config.limits, 0.0)
        for symbol, w in weights.items():
            loadings = factor_loadings.get(symbol)
            if loadings is None:
                uncovered.append(symbol)
                continue
            for factor, loading in loadings.items():
                lv = _require_finite(f"factor_loadings[{symbol}][{factor}]", loading)
                exposures[factor] = exposures.get(factor, 0.0) + w * lv

        breaches: list[ExposureBreach] = []
        for factor, limit in self._config.limits.items():
            exposure = exposures.get(factor, 0.0)
            abs_e = abs(exposure)
            if abs_e > limit:
                breaches.append(ExposureBreach(factor, exposure, limit, ExposureSeverity.BREACH))
            elif abs_e >= limit * self._config.warn_ratio:
                breaches.append(ExposureBreach(factor, exposure, limit, ExposureSeverity.WARNING))
        breaches.sort(key=lambda b: abs(b.exposure / b.limit), reverse=True)

        if self._audit_sink is not None:
            for breach in breaches:
                self._audit_sink(breach)

        return FactorExposureReport(
            exposures=exposures,
            breaches=tuple(breaches),
            uncovered_symbols=tuple(sorted(uncovered)),
            weight_sum=sum(weights.values()),
        )
