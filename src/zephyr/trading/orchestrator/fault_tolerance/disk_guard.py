from typing import Final

# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.trading.orchestrator.fault_tolerance.disk_guard
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.trading.orchestrator.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_disk_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""磁盘空间耗尽防护（CT-DISK-GUARD）——剩余空间<5%->告警+只读模式。"""

DISK_THRESHOLD_PCT: Final[float] = 5.0


class DiskGuard:
    def check(self, free_gb: float, total_gb: float) -> tuple[bool, str]:
        pct = (free_gb / total_gb) * 100 if total_gb > 0 else 0
        if pct < DISK_THRESHOLD_PCT:
            return False, f"磁盘剩余 {pct:.1f}% < {DISK_THRESHOLD_PCT}%"
        return True, "OK"

    def should_enter_readonly(self, free_gb: float, total_gb: float) -> bool:
        return not self.check(free_gb, total_gb)[0]
