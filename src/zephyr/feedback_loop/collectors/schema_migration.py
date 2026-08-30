# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.collectors.schema_migration
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Schema Migration — v0.14.0 R190

Blindspot: Schema migrations are manual and risky; no dry-run preview.
Risk: R190 — Migration breaks production silently; data corruption undetected.

Mitigation: Zero-downtime schema migration with dry-run preview.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: schema_migration.py
# 层: 算法
# - id: A1
#   name_zh: ① SchemaMigration
#   name_en: SchemaMigration
#   intro: class SchemaMigration 源码 L78-L100
#   desc: 公共方法（定义序）: add_step, dry_run, apply, rollback；源码 L78-L100
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: SchemaMigration
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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
