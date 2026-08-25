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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 子模块 degradation_monitor_base
#   fields: DegradationMonitorBase 信号质量降级监视器抽象基类（OCP扩展点D_SIGQC-DEG）
#   code: zephyr.signal_quality.degradation_monitor_base
# 层: 算法
# - id: A1
#   name_zh: ① 包级再导出
#   name_en: signal_quality.__init__
#   intro: 把子模块的降级监视器基类提升为包公共API
#   desc: from degradation_monitor_base import DegradationMonitorBase → __all__=["DegradationMonitorBase"] 对外暴露
#   inputs: I1
#   outputs: 包公共API __all__
# 层: 输出
# - id: O1
#   name_zh: 信号质量域包公共接口
#   name_en: zephyr.signal_quality __all__
#   intro: 对外暴露DegradationMonitorBase，承担信号质量评估/过滤/降级/冲突检测域入口
#   downstream: 无下游/内部使用（无[CONSUMERS]头；由import方使用）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from zephyr.signal_quality.degradation_monitor_base import DegradationMonitorBase
from zephyr.signal_quality.degradation_detector import DegradationDetector

__all__ = [
    "DegradationMonitorBase",
]

__all__.append("DegradationDetector")
