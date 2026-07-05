# [BLUEPRINT] SRC-184 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md
# [MODULE] zephyr.shared.contracts.rollback_types
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES]
# [CONSUMERS] zephyr.governance.escalation.result_types;zephyr.governance.escalation.contracts
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] RollbackResult 字段不可删;status/validation_result 枚举不可改值
# [MODIFY-GUARD] contracts_blueprint.md §4; contracts/__init__.py __all__
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RollbackError;TypeError
# [TESTS] tests/governance/
# [A_module] module_id=MOD-INT_rollback_types | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-INF-016-CONTRACTS | 03_modules/_cross_layer/shared-core/contracts_blueprint.md

G-CT-003 — RollbackResult Pydantic V2 BaseModel 回滚结果数据结构.
Canonical home for rollback result types.
"""

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
