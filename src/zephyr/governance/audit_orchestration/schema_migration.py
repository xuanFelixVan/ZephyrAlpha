# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] zephyr.governance.audit_orchestration.schema_migration
# [DOMAIN] D-GOV_AUDIT
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
# [A_module] module_id=MOD-GOV_schema_migration | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""数据库 Schema 演化契约（CT-SCHEMA-MIGRATE）——向后兼容迁移+回滚脚本。"""

from __future__ import annotations


class SchemaMigration:
    def __init__(self):
        self._version: int = 1
        self._history: list[dict] = []

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
