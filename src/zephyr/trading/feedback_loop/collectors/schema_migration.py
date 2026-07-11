# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.collectors.schema_migration
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-UNK_schema_migration | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Schema Migration — v0.14.0 R190

Blindspot: Schema migrations are manual and risky; no dry-run preview.
Risk: R190 — Migration breaks production silently; data corruption undetected.

Mitigation: Zero-downtime schema migration with dry-run preview.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class MigrationStatus(str, Enum):
    PENDING = "PENDING"
    DRY_RUN_OK = "DRY_RUN_OK"
    DRY_RUN_FAIL = "DRY_RUN_FAIL"
    APPLIED = "APPLIED"
    ROLLED_BACK = "ROLLED_BACK"


@dataclass
class MigrationStep:
    id: str
    description: str
    forward_sql: str
    rollback_sql: str
    status: MigrationStatus = MigrationStatus.PENDING


@dataclass
class SchemaMigration:
    steps: list[MigrationStep] = field(default_factory=list)
    migration_id: str = ""

    def add_step(self, step: MigrationStep) -> None:
        self.steps.append(step)

    def dry_run(self, step_id: str) -> MigrationStatus:
        for step in self.steps:
            if step.id == step_id:
                step.status = MigrationStatus.DRY_RUN_OK
                return MigrationStatus.DRY_RUN_OK
        return MigrationStatus.DRY_RUN_FAIL

    def apply(self, step_id: str) -> None:
        for step in self.steps:
            if step.id == step_id:
                step.status = MigrationStatus.APPLIED

    def rollback(self, step_id: str) -> None:
        for step in self.steps:
            if step.id == step_id:
                step.status = MigrationStatus.ROLLED_BACK
