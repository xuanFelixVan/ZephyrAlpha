# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md
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
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
[BLUEPRINT] MOD-INF-016-CONTRACTS | 03_modules/_cross_layer/shared-core/contracts_blueprint.md

G-CT-003 — RollbackResult Pydantic V2 BaseModel 回滚结果数据结构.
Canonical home for rollback result types.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: rollback_types.py
# 层: 算法
# - id: A1
#   name_zh: ① 数据契约声明
#   name_en: data class declarations
#   intro: 纯声明类（无公共方法，AST 事实）: RollbackStatus, ValidationResult, RollbackResult
#   desc: 数据契约/异常/枚举声明共 3 类；无算法流程（AST 事实）
#   inputs: I1
#   outputs: 数据契约类集合
# 层: 输出
# - id: O1
#   name_zh: 数据契约声明（3 类）
#   name_en: data classes
#   intro: RollbackStatus, ValidationResult, RollbackResult
#   downstream: zephyr.governance.escalation.result_types;zephyr.governance.escalation.contracts
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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
        return self.status is RollbackStatus.FAILED or self.validation_result is ValidationResult.FAIL
