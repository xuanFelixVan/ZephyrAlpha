# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain-infra_ops/capacity-assurance/blueprint.md
# [MODULE] zephyr.infrastructure.capacity_assurance.startup_guard
# [DOMAIN] D-INFRA_RUNTIME
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_startup_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
Startup Guard — 启动序列保护窗口 (盲点 #26, M-31)
特性：
  - 启动后 30s 内仅被动监控，不触发降级
  - load_order.yaml 定义加载顺序
  - boot_SLO: 启动成功率 > 95%
"""

import time


class StartupGuard:
    """
    启动保护窗 (M-31, 盲点 #26)
    """

    GRACE_PERIOD = 30.0
    BOOT_SLO_TARGET = 0.95

    def __init__(self):
        self._start_time = time.time()
        self._load_order: list[str] = []
        self._loaded: set[str] = set()
        self._boot_success = True

    def is_grace_period(self) -> bool:
        return (time.time() - self._start_time) < self.GRACE_PERIOD

    def register_load(self, module: str):
        self._loaded.add(module)

    def load_order_ok(self, expected_order: list[str]) -> bool:
        loaded_list = sorted(self._loaded)
        expected_list = sorted(expected_order)
        return set(expected_list) == set(loaded_list)

    def get_boot_status(self) -> dict:
        elapsed = time.time() - self._start_time
        grace_ended = elapsed >= self.GRACE_PERIOD
        return {
            "grace_period_active": not grace_ended,
            "boot_elapsed_seconds": round(elapsed, 1),
            "modules_loaded": len(self._loaded),
            "boot_slo_target": self.BOOT_SLO_TARGET,
        }
