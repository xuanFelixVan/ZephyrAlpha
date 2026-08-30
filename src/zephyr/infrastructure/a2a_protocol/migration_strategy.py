# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.migration_strategy
# [DOMAIN] D_INFRA_A2A
# [DEPENDENCIES] zephyr.infrastructure.a2a_protocol.__init__
# [CONSUMERS] MOD-INF-027;MOD-INF-018;MOD-INF-022
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Agent间通信;冲突解决;四级委托约束
# [MODIFY-GUARD] docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md;src/zephyr/infrastructure/runtime_integration/a2a_protocol/__init__.py
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CommunicationError;ConflictError;DelegationError
# [TESTS] tests/test_a2a_protocol/
# [A_module] module_id=MOD-INF-025 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: phase 参数
#   fields: 参数 phase，类型注解 MigrationPhase
#   code: migration_strategy.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① get_phase_def
#   name_en: get_phase_def
#   intro: get_phase_def(phase) 源码 L133-L134
#   desc: 源码 L133-L134
#   inputs: phase
#   outputs: PhaseDef | None
# - id: A2
#   name_zh: ② get_next_phase
#   name_en: get_next_phase
#   intro: get_next_phase(phase) 源码 L137-L139
#   desc: 源码 L137-L139
#   inputs: phase
#   outputs: MigrationPhase | None
#   （注：A2 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: PhaseDef | None
#   name_en: PhaseDef | None
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-INF-027;MOD-INF-018;MOD-INF-022
# - id: O2
#   name_zh: MigrationPhase | None
#   name_en: MigrationPhase | None
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-INF-027;MOD-INF-018;MOD-INF-022
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

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


MIGRATION_PIPELINE: dict[MigrationPhase, PhaseDef] = {
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
