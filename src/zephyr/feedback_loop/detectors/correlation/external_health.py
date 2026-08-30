# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.correlation.external_health
# [DOMAIN] D_FBL_DETECTORS
# [DEPENDENCIES] zephyr.feedback_loop.detectors.__init__
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
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
External Health Monitor — v0.14.0 R193

Blindspot: External dependency health unmonitored; cascading failure misdiagnosed.
Risk: R193 — External API returns 500; FLE diagnoses as internal pipeline failure.

Mitigation: External dependency health scoring with cascading failure suppression.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: external_health.py
# 层: 算法
# - id: A1
#   name_zh: ① ExternalHealth
#   name_en: ExternalHealth
#   intro: class ExternalHealth 源码 L77-L102
#   desc: 公共方法（定义序）: register, report_success, report_failure, suppress_internal_alerts；源码 L77-L102
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: ExternalHealth
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class DependencyStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    DOWN = "DOWN"


@dataclass
class DependencyHealth:
    service: str
    status: DependencyStatus = DependencyStatus.HEALTHY
    last_success: float = field(default_factory=time.time)
    consecutive_failures: int = 0
    health_score: float = 100.0


@dataclass
class ExternalHealth:
    dependencies: dict[str, DependencyHealth] = field(default_factory=dict)

    def register(self, service: str) -> DependencyHealth:
        dep = DependencyHealth(service=service)
        self.dependencies[service] = dep
        return dep

    def report_success(self, service: str) -> None:
        if service in self.dependencies:
            dep = self.dependencies[service]
            dep.status = DependencyStatus.HEALTHY
            dep.consecutive_failures = 0
            dep.last_success = time.time()
            dep.health_score = min(100.0, dep.health_score + 10.0)

    def report_failure(self, service: str) -> None:
        if service in self.dependencies:
            dep = self.dependencies[service]
            dep.consecutive_failures += 1
            dep.health_score = max(0.0, dep.health_score - 20.0)
            if dep.consecutive_failures >= 3:
                dep.status = DependencyStatus.DOWN

    def suppress_internal_alerts(self) -> set[str]:
        return {s for s, d in self.dependencies.items() if d.status is DependencyStatus.DOWN}
