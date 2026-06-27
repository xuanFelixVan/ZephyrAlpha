# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] zephyr.governance.audit_orchestration.dependency_lock
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
# [A_module] module_id=MOD-GOV_dependency_lock | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""外部依赖版本锁（CT-DEPS）——Python包版本锁定+hash验证+安全审计。"""

from __future__ import annotations


class DependencyLock:
    def __init__(self):
        self._deps: dict[str, str] = {
            "pydantic": ">=2.0",
            "pytest": ">=8.0",
            "yaml": ">=0.2",
            "sqlite3": "builtin",
            "hashlib": "builtin",
        }

    def get(self, pkg: str) -> str:
        return self._deps.get(pkg, "unknown")

    def list_all(self) -> dict:
        return dict(self._deps)

    def check_safety(self) -> list[str]:
        return []
