# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.implementations.shrinkage_engine
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.implementations.vectorized_engine; zephyr.backtest.core.engine_base
# [CONSUMERS] zephyr.backtest.regime_validation.c1_comparator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Shrinkage只减不增(value∈[0,1.0]); 权重和≤1.0(剩余留现金); shrinkage=1.0时与DefaultBacktestEngine等价; 不改归一化前的信号
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ShrinkageEngineError(ZA-BT-0014)
# [TESTS] tests/backtest/test_shrinkage_engine.py
# [A_module] module_id=MOD-BT-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #11_regime_backtest_validation_plan #MOD-REGIME-001 #C1-shrinkage-comparator

"""L_BACKTEST — Shrinkage Backtest Engine (B: Shrinkage 接入点)

继承 DefaultBacktestEngine，在目标权重归一化后按 Shrinkage 因子缩放仓位，
剩余资金保留为现金，实现 regime 风险节流（只减不增）。

接入点设计（11_regime_backtest_validation_plan §2.2 "Shrinkage 接入点"）:
  DefaultBacktestEngine._get_day_signals 把当日信号归一化为 Σ=1.0 的权重 dict。
  MatchingEngine._build_target_orders 用 target_value = NAV × weight 计算目标持仓——
  若权重和 < 1.0，差额自然留作现金。故 Shrinkage 接入只需在归一化后把每个权重
  乘以 Shrinkage 因子（value ∈ (0, 1.0]），无需改撮合引擎。

  shrinkage = 1.0  → 权重不变，满部署，与 DefaultBacktestEngine 完全等价（C1 基准组）
  shrinkage = 0.6  → 每个权重 × 0.6，权重和 = 0.6，40% 留现金（C1 实验组）
  shrinkage = 0.0  → 全空仓（极端收缩）

Shrinkage 因子来源（ShrinkageProvider，B2 实现）:
  - ConstShrinkageProvider(1.0)       → C1 基准组（关）
  - ScheduleShrinkageProvider(查表)   → 回放 RegimeDetector 预计算序列（开）
  - MockShrinkageProvider(规则mock)   → HMM 未就绪时占位
  - RegimeDetectorShrinkageAdapter    → 适配真实 RegimeDetector 输出

约束:
  - Shrinkage 只减不增：value 钳制到 [0.0, 1.0]，>1.0 视为 1.0
  - 不修改归一化前的原始信号（PIT 铁律不变）
  - shrinkage=1.0 时行为与 DefaultBacktestEngine 完全一致（C1 对比可溯源）

依据: 11_regime_backtest_validation_plan §2.2/§4.3 C1 + 30_multi_strategy_concurrency §2.2（Shrinkage=Confidence×Risk）
SSoT: cross_layer_contracts.yaml -> CTR-P1-016
Version: 0.1.0
"""

from __future__ import annotations

import logging
from datetime import date as _date_class
from datetime import datetime
from typing import TYPE_CHECKING, Protocol, runtime_checkable

import pandas as pd

from zephyr.backtest.implementations.vectorized_engine import (
    BacktestConfig,
    DefaultBacktestEngine,
)

try:  # 治理基类缺失时降级为 Exception，保证模块可独立 import
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # pragma: no cover
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

if TYPE_CHECKING:
    from zephyr.backtest.core.engine_base import BacktestResult

_logger = logging.getLogger(__name__)

__backtest_id__ = "shrinkage-backtest-engine"


class ShrinkageEngineError(ZephyrBaseError):
    """ZA-BT-0014: Shrinkage 引擎错误（provider 缺失/返回值非法）。

    改号留痕：原 ZA-BT-0009 与 decision_gate.DecisionGateError 重码，
    #ARCH-ERRCODE-001 裁定 git 首引入者保留 canonical，本类后引入（2026-08-06）改号。
    """

    error_code = "ZA-BT-0014"


@runtime_checkable
class ShrinkageProvider(Protocol):
    """Shrinkage 因子供给协议（B2 实现，引擎消费）。

    实现方按日期返回当日 Shrinkage 因子，value ∈ [0.0, 1.0]：
      - 1.0 = 满部署（无节流，C1 基准组）
      - <1.0 = 部分留现金（节流，C1 实验组）
    引擎会再次钳制到 [0,1]，故实现方轻微越界不会破坏不变量。
    """

    def get_shrinkage(self, date: datetime) -> float:
        """返回指定日期的 Shrinkage 因子（[0.0, 1.0]）。"""
        ...


def _clamp_shrinkage(value: float) -> float:
    """钳制 Shrinkage 到 [0.0, 1.0]（只减不增不变量）。"""
    if value != value:  # NaN
        return 1.0
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


class ShrinkageBacktestEngine(DefaultBacktestEngine):
    """Shrinkage 回测引擎——regime 风险节流接入点（B）。

    在 DefaultBacktestEngine 基础上 override _get_day_signals：归一化后按当日
    Shrinkage 因子缩放权重，剩余资金留现金。撮合/绩效/过拟合检测全部复用父类。

    Usage（C1 基准组——关）:
        from zephyr.backtest.regime_validation.shrinkage_provider import ConstShrinkageProvider
        engine_off = ShrinkageBacktestEngine(
            config=BacktestConfig(...),
            shrinkage_provider=ConstShrinkageProvider(1.0),
        )
        result_off = engine_off.run(data=data_df, signals=signals_df)

    Usage（C1 实验组——开）:
        engine_on = ShrinkageBacktestEngine(
            config=BacktestConfig(...),
            shrinkage_provider=schedule_provider,  # 回放 regime 预计算序列
        )
        result_on = engine_on.run(data=data_df, signals=signals_df)

    不变量:
      - shrinkage=1.0 时与 DefaultBacktestEngine.run 完全等价（C1 可溯源对比）
      - 权重和 ≤ 1.0（剩余留现金，MatchingEngine 天然支持）
      - Shrinkage 只减不增（value 钳制 [0,1]）
    """

    __backtest_id__ = __backtest_id__

    def __init__(
        self,
        config: BacktestConfig | None = None,
        shrinkage_provider: ShrinkageProvider | None = None,
    ) -> None:
        """初始化 Shrinkage 引擎。

        Args:
            config: 回测配置（同 DefaultBacktestEngine）。
            shrinkage_provider: Shrinkage 因子供给方。None 等价于 ConstShrinkageProvider(1.0)
                （满部署，退化为 DefaultBacktestEngine，便于 C1 基准组复用同一类）。
        """
        super().__init__(config=config)
        if shrinkage_provider is None:
            shrinkage_provider = _ConstOneProvider()
        self._shrinkage_provider: ShrinkageProvider = shrinkage_provider
        # 每日 Shrinkage 应用记录（归因用：date -> 实际生效的 shrinkage）
        self._shrinkage_log: list[tuple[datetime, float]] = []

    @property
    def shrinkage_provider(self) -> ShrinkageProvider:
        """当前 Shrinkage 供给方（只读）。"""
        return self._shrinkage_provider

    @property
    def shrinkage_log(self) -> list[tuple[datetime, float]]:
        """每日实际生效的 Shrinkage 因子序列（归因用，(date, value)）。"""
        return list(self._shrinkage_log)

    def _get_day_signals(
        self, signals: pd.DataFrame, date: object
    ) -> dict[str, float]:
        """归一化后按当日 Shrinkage 缩放权重（剩余留现金）。

        流程:
          1. 调用父类 _get_day_signals 取归一化权重（Σ=1.0）
          2. 把 date 转为 datetime，向 provider 取当日 Shrinkage 因子
          3. 钳制 Shrinkage 到 [0,1]（只减不增）
          4. 每个权重 × Shrinkage → 权重和 = Shrinkage，差额留现金
          5. 记录 (date, shrinkage) 到 shrinkage_log（归因）

        Args:
            signals: 信号 DataFrame（date × symbol）。
            date: 当前日期（date/datetime/str/timestamp 等，_to_datetime 统一处理）。

        Returns:
            {symbol: weight} 缩放后的权重 dict（仅含 weight>0 的，权重和 ≤ 1.0）。
            无信号时返回空 dict（同父类）。
        """
        weights = super()._get_day_signals(signals, date)
        if not weights:
            # 无信号不记录 shrinkage（与父类早返回语义一致）
            return weights

        dt = self._to_datetime(date)
        try:
            raw = self._shrinkage_provider.get_shrinkage(dt)
        except Exception as exc:  # provider 异常不应阻断回测
            _logger.warning(
                "Shrinkage provider 异常，当日退化为满部署 (date=%s): %s", dt, exc
            )
            raw = 1.0
        shrinkage = _clamp_shrinkage(raw if isinstance(raw, (int, float)) else 1.0)

        self._shrinkage_log.append((dt, shrinkage))

        if shrinkage >= 1.0:
            # 满部署，权重不变（避免无意义浮点乘引入误差）
            return weights
        if shrinkage <= 0.0:
            # 极端收缩：全空仓
            return {}

        return {symbol: w * shrinkage for symbol, w in weights.items()}


class _ConstOneProvider:
    """内部默认 provider——恒返回 1.0（满部署，等价于无 Shrinkage）。"""

    def get_shrinkage(self, date: datetime) -> float:  # noqa: ARG002
        return 1.0


__all__ = [
    "ShrinkageProvider",
    "ShrinkageBacktestEngine",
    "ShrinkageEngineError",
]
