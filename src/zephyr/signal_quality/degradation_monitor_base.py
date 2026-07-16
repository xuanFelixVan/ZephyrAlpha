# [BLUEPRINT] MOD-SIGQC-001 | docs/03_modules/_domain_signal_quality/blueprint.md
# [MODULE] zephyr.signal_quality.degradation_monitor_base
# [DOMAIN] D_SIGQC
# [DEPENDENCIES] zephyr.trading.trading_contracts.market.signal_degradation_warning; zephyr.trading.trading_contracts.market.synthesized_signal
# [CONSUMERS] signal_fundamental; risk; pf_core
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_degradation_monitor_base | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: signal_quality
# category: degradation_monitor
# status: active
# created: "2026-07-06"
# ---

"""D_SIGQC — Signal Quality Degradation Monitor Base

信号质量降级监视器抽象基类（OCP 扩展点 D_SIGQC-DEG）。

域归属修正（2026-07-06）：本类原定义在 ``signal_fundamental/gen/aggregator_base.py``
（D_FUNDAMENTAL_SIGNAL），但按 ``functional_domain_registry.yaml`` 域边界裁定，
"信号降级"属于 D_SIGQC 域。已迁移至本文件（D_SIGQC 真源）。
``signal_fundamental`` 保留 re-export 向后兼容。

契约对齐：CTR-ERR-003（SignalDegradationWarning 出站）-> D_RISK, D_PORTFOLIO_CORE

当检测到信号质量下降时发布警告——不阻断流水线，但下游应据此降级处理。
"""

from __future__ import annotations

import abc
from typing import ClassVar

from zephyr.trading.trading_contracts.market.signal_degradation_warning import SignalDegradationWarning
from zephyr.shared.contracts.synthesized_signal import SynthesizedSignal


class DegradationMonitorBase(abc.ABC):
    """
    信号质量降级监视器（OCP 扩展点 D_SIGQC-DEG）

    契约对齐：CTR-ERR-003（SignalDegradationWarning 出站）-> D_RISK, D_PORTFOLIO_CORE

    当检测到信号质量下降时发布警告——不阻断流水线，但下游应据此降级处理。

    实现者要求：
      - evaluate(): 接收一批 SynthesizedSignal，返回 SignalDegradationWarning 列表
      - 不阻断流水线，仅发出降级通知
      - degradation_level 枚举：MILD | MODERATE | SEVERE
    """

    _registry: ClassVar[dict[str, type[DegradationMonitorBase]]] = {}

    @abc.abstractmethod
    def evaluate(self, signals: list[SynthesizedSignal]) -> list[SignalDegradationWarning]:
        """评估批量合成信号的质量，返回降级警告列表"""
        ...


__all__ = ["DegradationMonitorBase"]
