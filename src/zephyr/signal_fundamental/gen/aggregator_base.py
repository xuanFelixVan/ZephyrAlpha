# [BLUEPRINT] MOD-L03-001 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_fundamental.gen.aggregator_base
# [DOMAIN] D_FUNDAMENTAL_SIGNAL
# [DEPENDENCIES] zephyr.trading.trading_contracts.execution.capital_allocation_result; zephyr.trading.trading_contracts.market.signal_degradation_warning; zephyr.trading.trading_contracts.market.factor_signal; zephyr.trading.trading_contracts.market.synthesized_signal
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_aggregator_base | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: signal
# category: signal_interface
# status: active
# created: "2026-05-05"
# ---

"""
D_SIGNAL — Signal Generation Layer

信号生成层。负责将 D_FACTOR 的因子信号（FactorSignal）合成为可交易的合成信号（SynthesizedSignal）。

核心职责：
  - 多因子信号聚合（Alpha / Macro / Sentiment / Flow 多域信号融合）
  - 信号合成（-> SynthesizedSignal）传递给 D_RISK/D_PORTFOLIO_CORE
  - 资本配置（-> CapitalAllocationResult）传递给 D_PORTFOLIO_CORE
  - 信号质量降级检测（-> SignalDegradationWarning）通知 D_RISK/D_PORTFOLIO_CORE

扩展点：
  - SignalAggregatorBase : OCP D_SIGNAL-AGG — 因子信号 -> 合成信号
  - CapitalAllocatorBase  : OCP D_SIGNAL-ALC — 合成信号 -> 资本配置
  - DegradationMonitorBase: OCP D_SIGQC-DEG — 信号质量降级检测（真源已迁移至
    zephyr.signal_quality.degradation_monitor_base，D_SIGQC 域；本模块 re-export 向后兼容）

依赖方向：D_FACTOR -> D_SIGNAL -> D_RISK/D_PORTFOLIO_CORE
"""

from __future__ import annotations

import abc
from typing import ClassVar

from zephyr.trading.trading_contracts.execution.capital_allocation_result import CapitalAllocationResult
from zephyr.shared.contracts.factor_signal import FactorSignal
from zephyr.trading.trading_contracts.market.signal_degradation_warning import SignalDegradationWarning
from zephyr.shared.contracts.synthesized_signal import SynthesizedSignal


class SignalAggregatorBase(abc.ABC):
    """
    信号聚合器抽象基类（OCP 扩展点 D_SIGNAL-AGG）

    契约对齐：CTR-002（FactorSignal 入站）-> CTR-P1-015（SynthesizedSignal 出站）

    实现者要求：
      - aggregate(): 接收一批 FactorSignal，聚合为单个标的的合成信号
      - 必须使用 idempotency_key 保证幂等性（INV-007）
      - 返回的 SynthesizedSignal.signal_value 必须在 [-3.0, 3.0] 范围内
      - contributing_factors 必须记录每个因子的权重，用于下游归因分析
    """

    _registry: ClassVar[dict[str, type[SignalAggregatorBase]]] = {}

    @abc.abstractmethod
    def aggregate(self, factor_signals: list[FactorSignal], symbol: str, idempotency_key: str) -> SynthesizedSignal:
        """聚合多个 FactorSignal 为单个标的的 SynthesizedSignal"""
        ...

    @staticmethod
    def normalize_signal(raw: float, clip_range: tuple[float, float] = (-3.0, 3.0)) -> float:
        return max(clip_range[0], min(clip_range[1], raw))


class CapitalAllocatorBase(abc.ABC):
    """
    资本配置器抽象基类（OCP 扩展点 D_SIGNAL-ALC）

    契约对齐：CTR-P1-003（CapitalAllocationResult 出站）-> D_PORTFOLIO_CORE

    实现者要求：
      - allocate(): 接收多策略合成信号，产出各策略的资本权重
      - allocation_method 枚举：equal_weight | sharpe_weight | risk_parity
      - total_allocated_weight 通常 = 1.0
    """

    _registry: ClassVar[dict[str, type[CapitalAllocatorBase]]] = {}

    @abc.abstractmethod
    def allocate(self, signals: list[SynthesizedSignal], idempotency_key: str) -> CapitalAllocationResult:
        """多策略信号 -> 资本配置权重"""
        ...


# DegradationMonitorBase 已迁移至 zephyr.signal_quality.degradation_monitor_base
# （D_SIGQC 域，2026-07-06 域边界修正）。本模块不再定义，通过 gen/__init__.py
# 和 signal_fundamental/__init__.py 的 __getattr__ re-export 向后兼容。


__all__ = [
    "CapitalAllocatorBase",
    "SignalAggregatorBase",
]
