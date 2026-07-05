# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §4.2
# [MODULE] zephyr.infrastructure.auto_fix_engine.models
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.auto_fix_engine.__init__
# [CONSUMERS] MOD-INF-027(audit-orchestrator);MOD-INF-023(drift-detector);MOD-INF-029(orphan-judge);MOD-INF-028(semantic-auditor)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] FixAction.fingerprint MUST be deterministic; FixStatus transitions MUST be legal
# [MODIFY-GUARD] blueprint.md §4.2; __init__.py __all__; _fixer-registry.yaml
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FixActionValidationError;FixBudgetExceededError
# [TESTS] tests/auto-fix-engine/test_models.py
# [A_module] module_id=MOD-INF_models | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FixLevel(str, Enum):
    L1_RULE = "l1_rule"
    L2_LLM = "l2_llm"
    L3_AGENT = "l3_agent"


class FixConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FixStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"
    APPROVAL_PENDING = "approval_pending"
    CANCELLED = "cancelled"


class BlastRadius(BaseModel):
    files: int = 0
    modules: int = 0
    lines_estimate: int = 0
    risk: str = "low"


class ValidationResult(BaseModel):
    valid: bool
    check_name: str
    evidence: str = ""
    error: str = ""


class BudgetInfo(BaseModel):
    daily_remaining: int = 50
    monthly_remaining: int = 500
    llm_tokens_remaining: int = 500000


class SafetyDecision(BaseModel):
    approved: bool
    confidence: FixConfidence = FixConfidence.HIGH
    reason: str = ""


class BudgetDecision(BaseModel):
    allowed: bool
    reason: str = ""
    remaining_daily: int = 0
    remaining_monthly: int = 0


class FixAction(BaseModel):
    action_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    action_type: str
    level: FixLevel = FixLevel.L1_RULE
    status: FixStatus = FixStatus.PENDING
    target: str
    before: str = ""
    after: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    validation: ValidationResult | None = None
    audit_trail_id: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    confidence: FixConfidence = FixConfidence.HIGH
    attempts: int = 1
    retry_count: int = 0
    model: str = ""
    context_sources: list[str] = Field(default_factory=list)
    token_cost: int = 0
    verified: bool = False
    escalated: bool = False
    sandbox_verified: bool = False
    fingerprint: str = ""
    blast_radius: BlastRadius | None = None

    @model_validator(mode="after")
    def _compute_fingerprint(self) -> FixAction:
        if not self.fingerprint:
            raw = f"{self.action_type}:{self.target}:{self.before}"
            self.fingerprint = hashlib.sha256(raw.encode()).hexdigest()[:16]
        return self


class FixHistory(BaseModel):
    fix_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    action_type: str
    target: str
    before_hash: str = ""
    after_hash: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    success: bool = False
    verifier: str = ""
    revert_possible: bool = True


class FixDeadLetter(BaseModel):
    dead_letter_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    original_fix: FixAction
    failure_reason: str = ""
    retry_count: int = 0
    last_retry: datetime = Field(default_factory=lambda: datetime.now(UTC))
    escalated: bool = False


class FixReport(BaseModel):
    total_attempted: int = 0
    succeeded: int = 0
    failed: int = 0
    escalated: int = 0
    dead_lettered: int = 0
    budget_remaining: BudgetInfo = Field(default_factory=BudgetInfo)
    actions: list[FixAction] = Field(default_factory=list)
    cascade_alerts: list[str] = Field(default_factory=list)


class FixHealthReport(BaseModel):
    healthy: bool = True
    fixers: dict[str, str] = Field(default_factory=dict)
    budget_ok: bool = True
    cascade_active: bool = False
    dead_letter_count: int = 0
    approval_queue_size: int = 0
    db_accessible: bool = True
    config_loaded: bool = True


class ShadowResult(BaseModel):
    safe_to_apply: bool = False
    test_result: Any | None = None
    type_result: Any | None = None
    lint_result: Any | None = None
    error: str = ""
    shadow_dir: str = ""


class ComplianceEvidence(BaseModel):
    fix_id: str
    action_type: str
    target: str
    before_hash: str = ""
    after_hash: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    actor: str = "auto-fix-engine"
    confidence: str = ""
    rbac_decision: str = ""
    validation_result: str = ""
    audit_trail_id: str = ""
    tamper_proof_hash: str = ""

    @model_validator(mode="after")
    def _compute_hash(self) -> ComplianceEvidence:
        if not self.tamper_proof_hash:
            raw = (
                f"{self.fix_id}:{self.action_type}:{self.target}:{self.before_hash}:{self.after_hash}:{self.timestamp}"
            )
            self.tamper_proof_hash = hashlib.sha256(raw.encode()).hexdigest()[:32]
        return self


class BaseFixer(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    fixer_id: str
    action_type: str
    level: FixLevel = FixLevel.L1_RULE
    dimension: str = ""
    description: str = ""

    def scan(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    def fix(self, target: str, dry_run: bool = False) -> FixAction:
        raise NotImplementedError

    def validate(self, target: str) -> ValidationResult:
        raise NotImplementedError

    def rollback(self, target: str) -> bool:
        raise NotImplementedError


_STABILITY_FROZEN = True
_FROZEN_PUBLIC_API = frozenset(
    {
        "FixLevel",
        "FixConfidence",
        "FixStatus",
        "BlastRadius",
        "ValidationResult",
        "BudgetInfo",
        "SafetyDecision",
        "BudgetDecision",
        "FixAction",
        "FixHistory",
        "FixDeadLetter",
        "FixReport",
        "FixHealthReport",
        "ShadowResult",
        "ComplianceEvidence",
        "BaseFixer",
    }
)
