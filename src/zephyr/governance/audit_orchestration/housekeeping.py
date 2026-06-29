# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] zephyr.governance.audit_orchestration.housekeeping
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit_orchestration.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_housekeeping | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""文件卫生保洁管理器（CT-HOUSEKEEPING）——临时文件扫描+日志轮转+废弃目录清理。"""

from __future__ import annotations


class HousekeepingManager:
    TEMP_PATTERNS: list[str] = ["_temp*", "_check*", "_phase_*", "*.tmp", "*.bak"]

    def scan_temp_files(self) -> list[str]:
        return []

    def should_clean(self, filename: str) -> bool:
        return any(filename.startswith(p.replace("*", "").rstrip("*")) for p in self.TEMP_PATTERNS)
