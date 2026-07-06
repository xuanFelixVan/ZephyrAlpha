# [BLUEPRINT] SRC-048 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.lifecycle_governance.migration_strategy
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.lifecycle_governance.__init__
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
# [A_module] module_id=MOD-GOV_migration_strategy | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
from enum import Enum

from pydantic import BaseModel


class MigrationPhase(str, Enum):
    ISSUE_TRACKING = "ISSUE_TRACKING"
    RISK_ASSESSMENT = "RISK_ASSESSMENT"
    ROLLBACK_PLAN = "ROLLBACK_PLAN"
    STAGING = "STAGING"
    PILOT = "PILOT"
    FULL_ROLLOUT = "FULL_ROLLOUT"
    POSTMORTEM = "POSTMORTEM"


class PhaseDef(BaseModel):
    phase: MigrationPhase
    label: str
    predecessor: MigrationPhase | None = None
    successor: MigrationPhase | None = None
    confidence_threshold: float = 0.95


MIGRATION_PIPELINE: Final[dict[MigrationPhase, PhaseDef]] = {
    MigrationPhase.ISSUE_TRACKING: PhaseDef(
        phase=MigrationPhase.ISSUE_TRACKING,
        label="问题追踪",
        successor=MigrationPhase.RISK_ASSESSMENT,
    ),
    MigrationPhase.RISK_ASSESSMENT: PhaseDef(
        phase=MigrationPhase.RISK_ASSESSMENT,
        label="风险评估(7维度)",
        predecessor=MigrationPhase.ISSUE_TRACKING,
        successor=MigrationPhase.ROLLBACK_PLAN,
        confidence_threshold=0.90,
    ),
    MigrationPhase.ROLLBACK_PLAN: PhaseDef(
        phase=MigrationPhase.ROLLBACK_PLAN,
        label="回滚计划",
        predecessor=MigrationPhase.RISK_ASSESSMENT,
        successor=MigrationPhase.STAGING,
    ),
    MigrationPhase.STAGING: PhaseDef(
        phase=MigrationPhase.STAGING,
        label="预发布环境",
        predecessor=MigrationPhase.ROLLBACK_PLAN,
        successor=MigrationPhase.PILOT,
        confidence_threshold=0.95,
    ),
    MigrationPhase.PILOT: PhaseDef(
        phase=MigrationPhase.PILOT,
        label="灰度试点",
        predecessor=MigrationPhase.STAGING,
        successor=MigrationPhase.FULL_ROLLOUT,
    ),
    MigrationPhase.FULL_ROLLOUT: PhaseDef(
        phase=MigrationPhase.FULL_ROLLOUT,
        label="全量发布",
        predecessor=MigrationPhase.PILOT,
        successor=MigrationPhase.POSTMORTEM,
    ),
    MigrationPhase.POSTMORTEM: PhaseDef(
        phase=MigrationPhase.POSTMORTEM,
        label="复盘",
        predecessor=MigrationPhase.FULL_ROLLOUT,
    ),
}


def get_phase_def(phase: MigrationPhase) -> PhaseDef | None:
    return MIGRATION_PIPELINE.get(phase)


def get_next_phase(phase: MigrationPhase) -> MigrationPhase | None:
    d = MIGRATION_PIPELINE.get(phase)
    return d.successor if d else None
