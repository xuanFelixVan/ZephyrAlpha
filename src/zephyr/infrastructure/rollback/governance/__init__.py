# [A_module] module_id=MOD-GOV_governance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [TTL] task_bound
"""
Rollback — MOD-INF-021

回滚系统：WAL式原子操作 + 自动/手动回滚。
"""

from zephyr.infrastructure.rollback.governance.auditor import RollbackAuditor
from zephyr.infrastructure.rollback.governance.budget_tracker import RollbackBudgetTracker
from zephyr.infrastructure.rollback.governance.contracts import RollbackHandler
# ARCH-034 P3 / SRC-038 合并：drift_fix 冗余副本已删除，改为从 canonical 真源 re-export
from zephyr.infrastructure.rollback.drift_fix import DriftFixHandler
from zephyr.infrastructure.rollback.governance.result_types import RollbackResult, RollbackStatus, ValidationResult

__all__ = [
    "DriftFixHandler",
    "RollbackAuditor",
    "RollbackBudgetTracker",
    "RollbackHandler",
    "RollbackResult",
    "RollbackStatus",
    "ValidationResult",
    "auditor",
    "budget_tracker",
    "contracts",
    "drift_fix",
    "result_types",
]

__version__ = "0.1.0"
__module_id__ = "MOD-INF-021"
