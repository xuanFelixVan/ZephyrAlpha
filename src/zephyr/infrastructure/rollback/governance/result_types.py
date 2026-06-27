# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.governance.result_types
# [DOMAIN] D-INFRA_OPS
# [DEPENDENCIES] zephyr.infrastructure.rollback.governance.__init__
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
# [A_module] module_id=MOD-GOV_result_types | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""G-CT-003 — RollbackResult Pydantic V2 BaseModel 回滚结果数据结构."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field


class RollbackStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"


class ValidationResult(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    PENDING = "PENDING"


class RollbackResult(BaseModel):
    rollback_id: str
    target: str
    status: RollbackStatus = RollbackStatus.SUCCESS
    validation_result: ValidationResult = ValidationResult.PENDING
    error_detail: str = ""
    detected_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    agent_id: str = ""
    resource_path: str = ""

    @property
    def needs_escalation(self) -> bool:
        return self.status == RollbackStatus.FAILED or self.validation_result == ValidationResult.FAIL
