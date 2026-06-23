# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain-infra_ops/capacity-assurance/blueprint.md
# [MODULE] zephyr.infrastructure.capacity_assurance.trace_capacity_injector
# [DOMAIN] D-INFRA_RUNTIME
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
# [A_module] module_id=MOD-INF_trace_capacity_injector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""
Trace Capacity Injector — W3C TraceContext 容量元数据注入 (盲点 #25)
特性：
  - tracestate: cap_error_budget_tier, cap_module_count, cap_queue_depth
  - ContractBus 调用自动注入 tracestate
"""


class TraceCapacityInjector:
    """
    Trace 容量元数据注入器 (盲点 #25)
    注入字段到 tracestate：
      - cap_eb_tier: Error Budget tier (L0~L4)
      - cap_mod_cnt: 当前活跃模块数
      - cap_qd: EventBus queue depth
    """

    def __init__(self):
        self._error_budget_tier = "L0"
        self._module_count = 0
        self._queue_depth = 0

    def set_state(self, error_budget_tier: str, module_count: int, queue_depth: int):
        self._error_budget_tier = error_budget_tier
        self._module_count = module_count
        self._queue_depth = queue_depth

    def inject_tracestate(self) -> str:
        return (
            f"zephyr=1,"
            f"cap_eb_tier:{self._error_budget_tier},"
            f"cap_mod_cnt:{self._module_count},"
            f"cap_qd:{self._queue_depth}"
        )

    def get_capacity_headers(self) -> dict:
        return {
            "tracestate": self.inject_tracestate(),
            "cap-error-budget-tier": self._error_budget_tier,
            "cap-module-count": str(self._module_count),
            "cap-queue-depth": str(self._queue_depth),
        }
