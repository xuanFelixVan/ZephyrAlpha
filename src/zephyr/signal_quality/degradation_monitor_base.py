# [BLUEPRINT] MOD-SIGQC-001 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_quality.degradation_monitor_base
# [DOMAIN] D_SIGQC
# [DEPENDENCIES] zephyr.trading.trading_contracts.market.signal_degradation_warning; zephyr.shared.contracts.synthesized_signal
# [CONSUMERS] signal_fundamental; risk; pf_core
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SIGQC-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: signal_quality
# category: degradation_monitor
# status: active
# created: "2026-07-06"
# ---

"""

D_SIGQC — Signal Quality Degradation Monitor Base

信号质量降级监视器抽象基类（OCP 扩展点 D_SIGQC-DEG）。

域归属修正（2026-07-06）：本类原定义在 ``signal_fundamental/gen/aggregator_base.py``
（D_FUNDAMENTAL_SIGNAL），但按 ``functional_domain_registry.yaml`` 域边界裁定，
"信号降级"属于 D_SIGQC 域。已迁移至本文件（D_SIGQC 真源）。
``signal_fundamental`` 保留 re-export 向后兼容。

契约对齐：CTR-ERR-003（SignalDegradationWarning 出站）-> D_RISK, D_PORTFOLIO_CORE

当检测到信号质量下降时发布警告——不阻断流水线，但下游应据此降级处理。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 批量合成信号 list[SynthesizedSignal]
#   fields: 合成信号列表（信号质量降级评估对象）
#   code: zephyr.shared.contracts.synthesized_signal.SynthesizedSignal
# 层: 算法
# - id: A1
#   name_zh: ① 信号质量降级评估（抽象扩展点）
#   name_en: DegradationMonitorBase.evaluate
#   intro: 接收一批合成信号评估质量，返回降级警告——基类仅定义契约，子类实现
#   desc: 抽象方法（OCP扩展点D_SIGQC-DEG），函数体为...占位；实现者要求不阻断流水线仅发降级通知，degradation_level分MILD/MODERATE/SEVERE
#   inputs: I1
#   outputs: SignalDegradationWarning列表
#   is_break: true
# 层: 输出
# - id: O1
#   name_zh: 信号降级警告列表
#   name_en: list[SignalDegradationWarning]
#   intro: 出站降级警告（契约CTR-ERR-003），下游据此降级处理但不阻断流水线
#   downstream: signal_fundamental / risk / pf_core（[CONSUMERS]；契约CTR-ERR-003 → D_RISK, D_PORTFOLIO_CORE）
# [/ALGO_FLOW]
#
# 边:
# I1 -.->|断点| A1
# A1 --> O1
"""

from __future__ import annotations

import abc
from typing import ClassVar

from zephyr.shared.contracts.synthesized_signal import SynthesizedSignal
from zephyr.trading.trading_contracts.market.signal_degradation_warning import SignalDegradationWarning


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
