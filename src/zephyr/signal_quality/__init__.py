# [A_module] module_id=MOD-INF-040 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-040 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_quality
# [DOMAIN] D_SIGQC
# [TTL] permanent
"""D_SIGQC — Signal Quality Domain

信号质量域。负责信号质量评估/信号过滤/信号降级/信号冲突检测。

子模块:
  degradation_monitor_base — 信号质量降级监视器抽象基类（OCP D_SIGQC-DEG）
"""
from __future__ import annotations

from zephyr.signal_quality.degradation_monitor_base import DegradationMonitorBase

__all__ = [
    "DegradationMonitorBase",
]
