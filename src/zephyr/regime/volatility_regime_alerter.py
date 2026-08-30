# [BLUEPRINT] MOD-REGIME-011 | docs/03_modules/_domain_regime/volatility_regime_alerter/blueprint.md
# [MODULE] zephyr.regime.volatility_regime_alerter
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.risk.core.fhs_engine; numpy
# [CONSUMERS] MOD-REGIME-002(overlay_signals_builder 消费 overlay_dims 契约，运行时装配批接线)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] GARCH 自研复用 MOD-RK-26（L-BFGS-B QMLE，禁止引 arch 库）；score维度∈[0,100]/flag维度∈{0,1}/无信号=0（平时不干预）；样本不足/GARCH不收敛→降级不抛错（对齐 overlay 降级哲学）；配置非法→Fail-Closed
# [MODIFY-GUARD] tests/regime/test_volatility_regime_alerter.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] VolatilityAlerterConfigError(未登记错误码-申请中)
# [TESTS] tests/regime/test_volatility_regime_alerter.py
# [A_module] module_id=MOD-REGIME-011 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
波动率体制转换与关键时点预警（MOD-REGIME-011，模块2）。

真源：construction_backlog_dig.tsv B10-01358（A1 交易决策架构 §3 模块2，裁定=做 P0）
+ CAND-CYCLE-003。

三件套（regime 命门缺口）：
  ① GARCH(1,1) 日频波动预测——**自研复用** MOD-RK-26 fhs_engine 的 L-BFGS-B
     高斯 QMLE 拟合（项目既有裁定：不引 arch 库，AI-FHS-001 #1）；不收敛→
     vol_forecast 维度降级 0 + garch_available=False（对齐 FHS 回退哲学）；
  ② RV_5d/RV_20d 压缩标记——rv_ratio<0.8 标记波动压缩（<0.5 强压缩归模块51
     B10-01387 联动，本模块只出早标记）；
  ③ 波动突变告警——shift_ratio=sigma_forecast(年化)/RV_20d(年化)≥1.5 触发，
     输出接 overlay_signals_builder（overlay_dims 契约：score∈[0,100]/
     flag∈{0,1}/无信号=0，平时不干预纯 HMM 不退化）。

降级哲学（对齐 MOD-REGIME-002）：数据缺失/样本不足/GARCH 不收敛 → 维度=0 不抛错；
仅配置非法 Fail-Closed（VolatilityAlerterConfigError）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: volatility_regime_alerter.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① VolRegimeSignal
#   name_en: VolRegimeSignal
#   intro: 波动体制预警信号。
#   desc: 波动体制预警信号。 Attributes: rv_ratio: RV_5d/RV_20d 年化波动比（压缩判定；长窗零波动时为 inf） compression_flag: 压缩…；公共方法（定义序）: overlay…
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② VolatilityRegimeAlerter
#   name_en: VolatilityRegimeAlerter
#   intro: 波动率体制转换与关键时点预警器（GARCH 自研复用+RV 压缩+突变告警）。
#   desc: 波动率体制转换与关键时点预警器（GARCH 自研复用+RV 压缩+突变告警）。；公共方法（定义序）: config, assess；源码 L186-L256
#   inputs: config
#   outputs: 返回值
#   （注：A2 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: VolRegimeSignal, VolatilityRegimeAlerter
#   downstream: MOD-REGIME-002(overlay_signals_builder 消费 overlay_dims 契约，运行时装配批接线)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Final

import numpy as np

from zephyr.risk.core.fhs_engine import (
    ExcessiveFHSNonFiniteDataError,
    FHSConfig,
    FHSEngine,
    InsufficientFHSHistoryError,
)

__all__: Final = [
    "VolatilityAlerterConfigError",
    "VolatilityRegimeAlerter",
    "VolAlerterConfig",
    "VolRegimeSignal",
]

_log = logging.getLogger(__name__)

_ANNUALIZATION: Final[int] = 252  # A股交易日年化因子（对齐 fhs_engine）


class VolatilityAlerterConfigError(ValueError):
    """波动预警配置非法（Fail-Closed；未登记错误码-申请中）。"""


@dataclass(frozen=True)
class VolAlerterConfig:
    """波动预警配置。

    Attributes:
        rv_short_window: RV 短窗（默认 5 日）
        rv_long_window: RV 长窗基线（默认 20 日）
        compression_threshold: RV 压缩标记线 rv_ratio 上限（默认 0.8，<1）
        shift_threshold: 突变告警线 shift_ratio 下限（默认 1.5，>1）
        min_history: 最小样本数（默认 30，对齐 FHS min_history）
        fhs_simulations: FHS 残差重采样路径数（默认 100，仅取 GARCH 参数用下限）
        random_seed: FHS 模拟种子（留痕可复现）
    """

    rv_short_window: int = 5
    rv_long_window: int = 20
    compression_threshold: float = 0.8
    shift_threshold: float = 1.5
    min_history: int = 30
    fhs_simulations: int = 100
    random_seed: int = 42

    def __post_init__(self) -> None:
        if self.rv_short_window < 2:
            raise VolatilityAlerterConfigError(f"rv_short_window 须 >=2: {self.rv_short_window}")
        if self.rv_long_window <= self.rv_short_window:
            raise VolatilityAlerterConfigError(
                f"rv_long_window({self.rv_long_window}) 须 > rv_short_window({self.rv_short_window})"
            )
        if not 0.0 < self.compression_threshold < 1.0:
            raise VolatilityAlerterConfigError(f"compression_threshold 须 ∈(0,1): {self.compression_threshold}")
        if not self.shift_threshold > 1.0:
            raise VolatilityAlerterConfigError(f"shift_threshold 须 >1: {self.shift_threshold}")
        if self.min_history < self.rv_long_window:
            raise VolatilityAlerterConfigError(
                f"min_history({self.min_history}) 须 >= rv_long_window({self.rv_long_window})"
            )
        if self.fhs_simulations < 100:
            raise VolatilityAlerterConfigError(f"fhs_simulations 须 >=100: {self.fhs_simulations}")


@dataclass(frozen=True)
class VolRegimeSignal:
    """波动体制预警信号。

    Attributes:
        rv_ratio: RV_5d/RV_20d 年化波动比（压缩判定；长窗零波动时为 inf）
        compression_flag: 压缩标记（rv_ratio<阈值）
        sigma_forecast_annualized: GARCH 次日条件波动预测（年化；不可用为 None）
        shift_ratio: sigma_forecast/RV_20d（突变判定；GARCH 不可用为 None）
        garch_available: GARCH(1,1) 拟合可用（收敛）标记
        degraded: 整体降级标记（样本不足等，全维度=0）
        degrade_reason: 降级原因（未降级为 None）
        shift_threshold: 突变告警线（随信号携带，overlay_dims 消费同一真源）
    """

    rv_ratio: float
    compression_flag: int
    sigma_forecast_annualized: float | None
    shift_ratio: float | None
    garch_available: bool
    degraded: bool
    degrade_reason: str | None = field(default=None)
    shift_threshold: float = 1.5

    def overlay_dims(self) -> dict[str, float]:
        """overlay_signals_builder 消费契约：score∈[0,100]/flag∈{0,1}/无信号=0。"""
        if self.degraded:
            return {"vol_compression": 0, "vol_shift_alert": 0, "vol_forecast_score": 0.0}
        shift_alert = 0
        score = 0.0
        if self.shift_ratio is not None and np.isfinite(self.shift_ratio):
            if self.shift_ratio >= self.shift_threshold:
                shift_alert = 1
            # 1.0→0 分，阈值→100 分线性映射（超出截断）
            score = float(np.clip((self.shift_ratio - 1.0) / (self.shift_threshold - 1.0), 0.0, 1.0) * 100.0)
        return {
            "vol_compression": int(self.compression_flag),
            "vol_shift_alert": shift_alert,
            "vol_forecast_score": score,
        }


class VolatilityRegimeAlerter:
    """波动率体制转换与关键时点预警器（GARCH 自研复用+RV 压缩+突变告警）。"""

    def __init__(self, config: VolAlerterConfig | None = None) -> None:
        self._config = config or VolAlerterConfig()
        self._fhs = FHSEngine(
            FHSConfig(
                min_history=self._config.min_history,
                n_simulations=self._config.fhs_simulations,
                random_seed=self._config.random_seed,
                fallback_to_historical=True,  # GARCH 不收敛→回退并标记（回读 garch_converged）
            )
        )

    @property
    def config(self) -> VolAlerterConfig:
        return self._config

    def assess(self, returns: np.ndarray) -> VolRegimeSignal:
        """评估日频收益序列，产出波动体制预警信号（降级不抛错）。

        Args:
            returns: 日收益序列（log 或简单收益，建议 >=60 样本以激活 GARCH）。
        """
        cfg = self._config
        r = np.asarray(returns, dtype=float).ravel()
        r = r[np.isfinite(r)]  # 非有限值过滤（占比上限由 FHS 内部 Fail-Closed）
        if len(r) < cfg.min_history:
            return VolRegimeSignal(
                rv_ratio=0.0,
                compression_flag=0,
                sigma_forecast_annualized=None,
                shift_ratio=None,
                garch_available=False,
                degraded=True,
                degrade_reason=f"样本不足: {len(r)} < min_history={cfg.min_history}",
                shift_threshold=cfg.shift_threshold,
            )

        # ── ② RV_5d/RV_20d 压缩标记（不依赖 GARCH，独立可用） ──
        rv_short = float(np.std(r[-cfg.rv_short_window :], ddof=1)) * np.sqrt(_ANNUALIZATION)
        rv_long = float(np.std(r[-cfg.rv_long_window :], ddof=1)) * np.sqrt(_ANNUALIZATION)
        rv_ratio = rv_short / rv_long if rv_long > 0 else float("inf")
        compression_flag = 1 if rv_ratio < cfg.compression_threshold else 0

        # ── ① GARCH(1,1) 日频波动预测（自研复用 MOD-RK-26，不引 arch） ──
        sigma_forecast_ann: float | None = None
        shift_ratio: float | None = None
        garch_available = False
        try:
            fhs_result = self._fhs.compute(r, portfolio_value=1.0)
        except (InsufficientFHSHistoryError, ExcessiveFHSNonFiniteDataError) as exc:
            _log.warning("FHS/GARCH 不可用，vol_forecast 维度降级 0: %s", exc)
        else:
            if fhs_result.garch_converged and fhs_result.garch_params is not None:
                garch_available = True
                sigma_forecast_ann = fhs_result.garch_params.sigma_forecast * np.sqrt(_ANNUALIZATION)
                if rv_long > 0:
                    shift_ratio = sigma_forecast_ann / rv_long
            else:
                _log.warning("GARCH 不收敛（%s），vol_forecast 维度降级 0", fhs_result.fallback_reason)

        return VolRegimeSignal(
            rv_ratio=rv_ratio,
            compression_flag=compression_flag,
            sigma_forecast_annualized=sigma_forecast_ann,
            shift_ratio=shift_ratio,
            garch_available=garch_available,
            degraded=False,
            shift_threshold=cfg.shift_threshold,
        )
