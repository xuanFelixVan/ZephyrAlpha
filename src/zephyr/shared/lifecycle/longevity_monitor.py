# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.lifecycle.longevity_monitor
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: longevity_monitor.py
# 层: 算法
# - id: A1
#   name_zh: ① LongevityMonitor
#   name_en: LongevityMonitor
#   intro: class LongevityMonitor 源码 L63-L78
#   desc: 公共方法（定义序）: register, report；源码 L63-L78
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: LongevityMonitor
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class LongevityReport:
    component_id: str
    uptime_seconds: float
    memory_growth_mb: float
    degradation_score: float


class LongevityMonitor:
    def __init__(self):
        self._start_times: dict[str, float] = {}
        self._baselines: dict[str, float] = {}

    def register(self, component_id: str, baseline_memory_mb: float = 0.0) -> None:
        self._start_times[component_id] = time.time()
        self._baselines[component_id] = baseline_memory_mb

    def report(self, component_id: str, current_memory_mb: float) -> LongevityReport:
        start = self._start_times.get(component_id, time.time())
        baseline = self._baselines.get(component_id, 0.0)
        uptime = time.time() - start
        growth = current_memory_mb - baseline
        degradation = min(1.0, max(0.0, growth / max(baseline, 1.0)))
        return LongevityReport(component_id, uptime, growth, degradation)
