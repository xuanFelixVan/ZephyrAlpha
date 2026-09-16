# [A_module] module_id=MOD-INF-040 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-040 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_quality
# [DOMAIN] D_SIGQC
# [TTL] permanent
"""

D_SIGQC — Signal Quality Domain

信号质量域。负责信号质量评估/信号过滤/信号降级/信号冲突检测。

子模块:
  degradation_monitor_base — 信号质量降级监视器抽象基类（OCP D_SIGQC-DEG）
  degradation_detector — 多维滑窗基线对比降级检测器（MOD-SIGQC-001，包级导出）
  signal_dedup / signal_degradation_monitor / signal_explainability_guarantor / signal_quality_benchmark — 域内待装配模块（各自独立蓝图 MOD-SIGQC-003~006）

# [ALGO_FLOW] external: docs/03_modules/_domain_signal_quality/algo_flow/signal_quality__init__.yaml
"""

from __future__ import annotations

from zephyr.signal_quality.degradation_monitor_base import DegradationMonitorBase
from zephyr.signal_quality.degradation_detector import DegradationDetector

__all__ = [
    "DegradationMonitorBase",
]

__all__.append("DegradationDetector")
