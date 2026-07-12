# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.lifecycle.housekeeping
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.orchestrator.__init__
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
# [A_module] module_id=MOD-ORC_housekeeping | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""文件卫生保洁管理器（CT-HOUSEKEEPING）——临时文件扫描+日志轮转+废弃目录清理。"""


class HousekeepingManager:
    TEMP_PATTERNS: list[str] = ["_temp*", "_check*", "_phase_*", "*.tmp", "*.bak"]

    def scan_temp_files(self) -> list[str]:
        return []

    def should_clean(self, filename: str) -> bool:
        return any(filename.startswith(p.replace("*", "").rstrip("*")) for p in self.TEMP_PATTERNS)
