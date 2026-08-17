# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.governance.schema_migration
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.shared.events.event_bus_upgrade
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
# [A_module] module_id=MOD-INF-039 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""数据库 Schema 演化契约（CT-SCHEMA-MIGRATE）——向后兼容迁移+回滚脚本。"""


class SchemaMigration:
    def __init__(self):
        self._version: int = 1
        self._history: list[dict] = []

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def history(self) -> list[dict]:
        """只读：history（Stage 4 公共化）。"""
        return self._history

    @history.setter
    def history(self, value):
        """写入：history（Stage 4 公共化）。"""
        self._history = value

    def current_version(self) -> int:
        return self._version

    def migrate(self, to_version: int) -> bool:
        if to_version <= self._version:
            return False
        self._history.append({"from": self._version, "to": to_version})
        self._version = to_version
        return True

    def rollback(self, target_version: int) -> bool:
        if target_version >= self._version:
            return False
        self._version = target_version
        return True
