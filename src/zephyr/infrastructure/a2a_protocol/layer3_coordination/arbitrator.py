# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.arbitrator
# [DOMAIN] D_INFRA_A2A
# [DEPENDENCIES] zephyr.shared.foundation.constants
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-025 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# P1-3: 本地 AgentRole(IntEnum) 已删除，改 import shared 版 ArbitrationRole as AgentRole（兼容层）

"""
A2A 三级仲裁引擎 — priority -> rule -> escalation

当 ConflictDetector 检测到冲突后，Arbitrator 按三级策略仲裁:
  Tier 1 (priority):    按 Agent 优先级 — site:safety operator:superadmin > role:reviewer > role:builder
  Tier 2 (rule):        按文件归属规则 — 每个文件最多一个 owner Agent
  Tier 3 (escalation):  不可自动解决 -> 生成 ESC-A2A 升级 ticket

输入: ConflictDetector 输出的冲突列表 + 两个 Agent 的 metadata
输出: 仲裁结果 — winner + reason + 失败方补偿建议

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: ownership_rules 参数
#   fields: 参数 ownership_rules（无注解）
#   code: arbitrator.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: escalation_engine 参数
#   fields: 参数 escalation_engine（无注解）
#   code: arbitrator.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: deadlock_detector 参数
#   fields: 参数 deadlock_detector（无注解）
#   code: arbitrator.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① Arbitrator
#   name_en: Arbitrator
#   intro: A2A 三级仲裁引擎.
#   desc: A2A 三级仲裁引擎. Tier 1: 角色优先级 — SUPERADMIN > SAFETY_OPERATOR > ... > BUILDER Tier 2: 文件归属 — 检…；公共方法（定义序）: escalat…
#   inputs: ownership_rules escalation_engine deadlock_detector
#   outputs: 返回值
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: Arbitrator
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import IntEnum

# P1-3: 删除本地 AgentRole(IntEnum) 定义，改 import shared 版 ArbitrationRole
# 真源 = zephyr.shared.protocols.a2a.a2a_coordination.ArbitrationRole
# P1-3 Batch 2: import ArbitrationRole（新名）+ AgentRole = ArbitrationRole 兼容层
# （与其他3模块 RbacRole/RoutingRole/MultiAgentRole 一致），让 _core_coordination 可同时 re-export 两名
from zephyr.shared.protocols.a2a.a2a_coordination import ArbitrationRole

# P1-3 兼容层：旧名 AgentRole 保留为 ArbitrationRole 别名（body 内 AgentRole.SUPERADMIN 等引用无缝工作）
AgentRole = ArbitrationRole  # noqa: F811  # [DEPRECATED] [TTL] task_bound — P1-3 兼容层


class ArbitrationVerdict(IntEnum):
    AUTONOMOUS = 0
    AUTO_GUARD = 1
    BLOCKED = 2


@dataclass
class FileOwnership:
    file_pattern: str
    owner_role: AgentRole
    description: str = ""


_DEFAULT_OWNERSHIP = [
    FileOwnership(".trae/rules/project_rules.md", AgentRole.SUPERADMIN, "系统规则"),
    FileOwnership("docs/registry_of_registries.yaml", AgentRole.SUPERADMIN, "中央注册表"),
    FileOwnership("docs/03_modules/", AgentRole.GOVERNANCE, "蓝图"),
    FileOwnership("src/zephyr/governance/", AgentRole.GOVERNANCE, "治理模块"),
    FileOwnership("src/zephyr/gov_enforcement/rule_enforcement/", AgentRole.REVIEWER, "门禁"),
    FileOwnership("tests/", AgentRole.REVIEWER, "测试"),
    FileOwnership("scripts/", AgentRole.SITE_OWNER, "脚本"),
]


@dataclass
class AgentMeta:
    agent_id: str
    role: AgentRole = AgentRole.BUILDER
    session_age_minutes: float = 0.0
    tasks_completed: int = 0
    owned_files: list[str] = field(default_factory=list)


@dataclass
class ArbitrationResult:
    winner: str | None
    loser: str | None
    tier: int
    reason: str
    escalation: bool = False
    escalation_message: str = ""
    compensation: str = ""
    verdict: ArbitrationVerdict = ArbitrationVerdict.AUTONOMOUS


class Arbitrator:
    """A2A 三级仲裁引擎.

    Tier 1: 角色优先级 — SUPERADMIN > SAFETY_OPERATOR > ... > BUILDER
    Tier 2: 文件归属 — 检查 file_ownership 规则
    Tier 3: 升级 — 无法自动解决 -> 生成 ESC-A2A

    扩展: 集成 EscalationEngine + DeadlockDetector + 审计日志
    """

    def __init__(
        self,
        ownership_rules: list[FileOwnership] | None = None,
        escalation_engine: object = None,
        deadlock_detector: object = None,
    ):
        self._ownership = ownership_rules or _DEFAULT_OWNERSHIP
        self._escalation_engine = escalation_engine
        self._deadlock_detector = deadlock_detector
        self._audit_log: list[dict] = []

    @property
    def escalation_engine(self):
        """公共只读属性 (reverse hierarchy: _escalation_engine 仍为存储)。"""
        return self._escalation_engine

    @property
    def deadlock_detector(self):
        """公共只读属性 (reverse hierarchy: _deadlock_detector 仍为存储)。"""
        return self._deadlock_detector

    def _record_audit(
        self,
        agent_a: str,
        agent_b: str,
        result: ArbitrationResult,
        conflicted_files: list[str],
    ) -> None:
        self._audit_log.append(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "agent_a": agent_a,
                "agent_b": agent_b,
                "winner": result.winner,
                "loser": result.loser,
                "tier": result.tier,
                "verdict": result.verdict.name,
                "reason": result.reason,
                "conflicted_files": list(conflicted_files),
            }
        )

    def get_audit_log(self) -> list[dict]:
        return list(self._audit_log)

    def clear_audit_log(self) -> None:
        self._audit_log.clear()

    def arbitrate(
        self,
        agent_a: AgentMeta,
        agent_b: AgentMeta,
        conflicted_files: list[str],
    ) -> ArbitrationResult:
        result = self._tier1_priority(agent_a, agent_b)
        if result is not None:
            result.verdict = ArbitrationVerdict.AUTONOMOUS
            self._record_audit(agent_a.agent_id, agent_b.agent_id, result, conflicted_files)
            return result

        result = self._tier2_ownership(agent_a, agent_b, conflicted_files)
        if result is not None:
            result.verdict = ArbitrationVerdict.AUTONOMOUS
            self._record_audit(agent_a.agent_id, agent_b.agent_id, result, conflicted_files)
            return result

        result = self._tier3_escalation(agent_a, agent_b, conflicted_files)
        result.verdict = self._compute_verdict(agent_a, agent_b, conflicted_files)
        self._record_audit(agent_a.agent_id, agent_b.agent_id, result, conflicted_files)
        return result

    def _compute_verdict(
        self,
        agent_a: AgentMeta,
        agent_b: AgentMeta,
        conflicted_files: list[str],
    ) -> ArbitrationVerdict:
        if self.deadlock_detector is not None:
            try:
                cycle = self.deadlock_detector.detect_cycle(agent_a.agent_id, agent_b.agent_id)
                if cycle:
                    return ArbitrationVerdict.BLOCKED
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.warning("suppressed error in arbitrator", exc_info=True)
        if self.escalation_engine is not None:
            try:
                from zephyr.governance.escalation.escalation_models import RuleCategory

                self.escalation_engine.evaluate(
                    category=RuleCategory.DEADLOCK,
                    description=f"A2A conflict: {agent_a.agent_id} vs {agent_b.agent_id} on {conflicted_files}",
                    owner_id=agent_a.agent_id,
                )
                return ArbitrationVerdict.AUTO_GUARD
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.warning("suppressed error in arbitrator", exc_info=True)
        return ArbitrationVerdict.AUTO_GUARD

    def _tier1_priority(self, a: AgentMeta, b: AgentMeta) -> ArbitrationResult | None:
        role_diff = a.role.value - b.role.value

        if role_diff > 20:
            return ArbitrationResult(
                winner=a.agent_id,
                loser=b.agent_id,
                tier=1,
                reason=f"Role priority: {a.role.name}({a.role.value}) > {b.role.name}({b.role.value})",
            )
        if role_diff < -20:
            return ArbitrationResult(
                winner=b.agent_id,
                loser=a.agent_id,
                tier=1,
                reason=f"Role priority: {b.role.name}({b.role.value}) > {a.role.name}({a.role.value})",
            )

        if role_diff == 0:
            return self._tier1_session_age(a, b)
        return None

    def _tier1_session_age(self, a: AgentMeta, b: AgentMeta) -> ArbitrationResult | None:
        if a.tasks_completed > b.tasks_completed + 5:
            return ArbitrationResult(
                winner=a.agent_id,
                loser=b.agent_id,
                tier=1,
                reason=f"Seniority: {a.tasks_completed} tasks > {b.tasks_completed} tasks",
            )
        if b.tasks_completed > a.tasks_completed + 5:
            return ArbitrationResult(
                winner=b.agent_id,
                loser=a.agent_id,
                tier=1,
                reason=f"Seniority: {b.tasks_completed} tasks > {a.tasks_completed} tasks",
            )
        return None

    def _tier2_ownership(
        self,
        a: AgentMeta,
        b: AgentMeta,
        conflicted_files: list[str],
    ) -> ArbitrationResult | None:
        a_score = 0
        b_score = 0

        for file_path in conflicted_files:
            for rule in self._ownership:
                if file_path.startswith(rule.file_pattern):
                    if a.role.value >= rule.owner_role.value:
                        a_score += 1
                    if b.role.value >= rule.owner_role.value:
                        b_score += 1

            if file_path in a.owned_files:
                a_score += 2
            if file_path in b.owned_files:
                b_score += 2

        if a_score > b_score and a_score > 0:
            return ArbitrationResult(
                winner=a.agent_id,
                loser=b.agent_id,
                tier=2,
                reason=f"File ownership: A={a_score} > B={b_score} on {conflicted_files}",
            )
        if b_score > a_score and b_score > 0:
            return ArbitrationResult(
                winner=b.agent_id,
                loser=a.agent_id,
                tier=2,
                reason=f"File ownership: B={b_score} > A={a_score} on {conflicted_files}",
            )
        return None

    def _tier3_escalation(
        self,
        a: AgentMeta,
        b: AgentMeta,
        conflicted_files: list[str],
    ) -> ArbitrationResult:
        return ArbitrationResult(
            winner=None,
            loser=None,
            tier=3,
            escalation=True,
            reason=f"Cannot auto-resolve: {a.agent_id}({a.role.name}) vs "
            f"{b.agent_id}({b.role.name}) on {conflicted_files}",
            escalation_message=f"ESC-A2A: conflict on {conflicted_files} between {a.agent_id} and {b.agent_id}",
            compensation="Both agents: pause conflicting files -> escalate -> await human or superadmin",
        )
