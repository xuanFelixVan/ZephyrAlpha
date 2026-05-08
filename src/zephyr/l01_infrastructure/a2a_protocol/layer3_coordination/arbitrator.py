"""A2A 三级仲裁引擎 — priority → rule → escalation

当 ConflictDetector 检测到冲突后，Arbitrator 按三级策略仲裁:
  Tier 1 (priority):    按 Agent 优先级 — site:safety operator:superadmin > role:reviewer > role:builder
  Tier 2 (rule):        按文件归属规则 — 每个文件最多一个 owner Agent
  Tier 3 (escalation):  不可自动解决 → 生成 ESC-A2A 升级 ticket

输入: ConflictDetector 输出的冲突列表 + 两个 Agent 的 metadata
输出: 仲裁结果 — winner + reason + 失败方补偿建议
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum


class AgentRole(IntEnum):
    SUPERADMIN = 100
    SAFETY_OPERATOR = 90
    GOVERNANCE = 80
    REVIEWER = 70
    SITE_OWNER = 60
    BUILDER = 50
    OBSERVER = 10

    @classmethod
    def from_string(cls, s: str) -> "AgentRole":
        s_lower = s.lower().replace("-", "_").replace(" ", "_")
        mapping = {
            "superadmin": cls.SUPERADMIN,
            "site_superadmin": cls.SUPERADMIN,
            "safety_operator": cls.SAFETY_OPERATOR,
            "governance": cls.GOVERNANCE,
            "reviewer": cls.REVIEWER,
            "site_owner": cls.SITE_OWNER,
            "builder": cls.BUILDER,
            "observer": cls.OBSERVER,
        }
        return mapping.get(s_lower, cls.BUILDER)


@dataclass
class FileOwnership:
    file_pattern: str
    owner_role: AgentRole
    description: str = ""


_DEFAULT_OWNERSHIP = [
    FileOwnership(".trae/rules/project_rules.md", AgentRole.SUPERADMIN, "系统规则"),
    FileOwnership("docs/registry-of-registries.yaml", AgentRole.SUPERADMIN, "中央注册表"),
    FileOwnership("docs/03_modules/", AgentRole.GOVERNANCE, "蓝图"),
    FileOwnership("src/zephyr/governance/", AgentRole.GOVERNANCE, "治理模块"),
    FileOwnership("src/zephyr/gates/", AgentRole.REVIEWER, "门禁"),
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


class Arbitrator:
    """A2A 三级仲裁引擎.

    Tier 1: 角色优先级 — SUPERADMIN > SAFETY_OPERATOR > ... > BUILDER
    Tier 2: 文件归属 — 检查 file_ownership 规则
    Tier 3: 升级 — 无法自动解决 → 生成 ESC-A2A
    """

    def __init__(
        self,
        ownership_rules: list[FileOwnership] | None = None,
    ):
        self._ownership = ownership_rules or _DEFAULT_OWNERSHIP

    def arbitrate(
        self,
        agent_a: AgentMeta,
        agent_b: AgentMeta,
        conflicted_files: list[str],
    ) -> ArbitrationResult:

        result = self._tier1_priority(agent_a, agent_b)
        if result is not None:
            return result

        result = self._tier2_ownership(agent_a, agent_b, conflicted_files)
        if result is not None:
            return result

        return self._tier3_escalation(agent_a, agent_b, conflicted_files)

    def _tier1_priority(self, a: AgentMeta, b: AgentMeta) -> ArbitrationResult | None:
        role_diff = a.role.value - b.role.value

        if role_diff > 20:
            return ArbitrationResult(
                winner=a.agent_id, loser=b.agent_id, tier=1,
                reason=f"Role priority: {a.role.name}({a.role.value}) > {b.role.name}({b.role.value})",
            )
        if role_diff < -20:
            return ArbitrationResult(
                winner=b.agent_id, loser=a.agent_id, tier=1,
                reason=f"Role priority: {b.role.name}({b.role.value}) > {a.role.name}({a.role.value})",
            )

        if role_diff == 0:
            return self._tier1_session_age(a, b)
        return None

    def _tier1_session_age(self, a: AgentMeta, b: AgentMeta) -> ArbitrationResult | None:
        if a.tasks_completed > b.tasks_completed + 5:
            return ArbitrationResult(
                winner=a.agent_id, loser=b.agent_id, tier=1,
                reason=f"Seniority: {a.tasks_completed} tasks > {b.tasks_completed} tasks",
            )
        if b.tasks_completed > a.tasks_completed + 5:
            return ArbitrationResult(
                winner=b.agent_id, loser=a.agent_id, tier=1,
                reason=f"Seniority: {b.tasks_completed} tasks > {a.tasks_completed} tasks",
            )
        return None

    def _tier2_ownership(
        self, a: AgentMeta, b: AgentMeta, conflicted_files: list[str],
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
                winner=a.agent_id, loser=b.agent_id, tier=2,
                reason=f"File ownership: A={a_score} > B={b_score} on {conflicted_files}",
            )
        if b_score > a_score and b_score > 0:
            return ArbitrationResult(
                winner=b.agent_id, loser=a.agent_id, tier=2,
                reason=f"File ownership: B={b_score} > A={a_score} on {conflicted_files}",
            )
        return None

    def _tier3_escalation(
        self, a: AgentMeta, b: AgentMeta, conflicted_files: list[str],
    ) -> ArbitrationResult:
        return ArbitrationResult(
            winner=None, loser=None, tier=3, escalation=True,
            reason=f"Cannot auto-resolve: {a.agent_id}({a.role.name}) vs "
                   f"{b.agent_id}({b.role.name}) on {conflicted_files}",
            escalation_message=f"ESC-A2A: conflict on {conflicted_files} between {a.agent_id} and {b.agent_id}",
            compensation="Both agents: pause conflicting files → escalate → await human or superadmin",
        )
