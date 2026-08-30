# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.resilience.resource_starvation_aware
# [DOMAIN] D_FEEDBACK_LOOP
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
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Resource Starvation Aware — v0.15.0 R209

Blindspot: FLE repair actions consume resources; resource exhaustion during repair invisible.
Risk: R209 — FLE repair triggers OOM; FLE itself killed before repair completes.

Mitigation: Pre-repair resource check; refuse to start if resources below safety margin.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: resource_starvation_aware.py
# 层: 算法
# - id: A1
#   name_zh: ① ResourceStarvationAware
#   name_en: ResourceStarvationAware
#   intro: class ResourceStarvationAware 源码 L67-L77
#   desc: 公共方法（定义序）: can_proceed；源码 L67-L77
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: ResourceStarvationAware
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ResourceBudget:
    cpu_available_pct: float = 100.0
    mem_available_mb: float = 8192.0
    disk_available_mb: float = 102400.0


@dataclass
class ResourceStarvationAware:
    cpu_min_pct: float = 10.0
    mem_min_mb: float = 512.0
    disk_min_mb: float = 1024.0

    def can_proceed(self, budget: ResourceBudget) -> bool:
        return (
            budget.cpu_available_pct >= self.cpu_min_pct
            and budget.mem_available_mb >= self.mem_min_mb
            and budget.disk_available_mb >= self.disk_min_mb
        )
