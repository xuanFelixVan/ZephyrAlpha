# [A_module] module_id=MOD-GOV_disk_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md | §

# [MODULE] zephyr.governance.audit_orchestration.disk_guard

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""磁盘空间耗尽防护（CT-DISK-GUARD）——剩余空间<5%→告警+只读模式。"""

from __future__ import annotations

DISK_THRESHOLD_PCT: float = 5.0


class DiskGuard:
    def check(self, free_gb: float, total_gb: float) -> tuple[bool, str]:
        pct = (free_gb / total_gb) * 100 if total_gb > 0 else 0
        if pct < DISK_THRESHOLD_PCT:
            return False, f"磁盘剩余 {pct:.1f}% < {DISK_THRESHOLD_PCT}%"
        return True, "OK"

    def should_enter_readonly(self, free_gb: float, total_gb: float) -> bool:
        return not self.check(free_gb, total_gb)[0]
