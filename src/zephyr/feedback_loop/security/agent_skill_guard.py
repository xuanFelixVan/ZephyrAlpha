# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.security.agent_skill_guard
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Agent Skill Guard — v0.14.0 R201

Blindspot: Agent Skills downloaded from internet without security validation.
Risk: R201 — Malicious skill compromises FLE; unauthorized autonomous actions.

Mitigation: Agent Skill supply chain security with hash validation and sandbox execution.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: agent_skill_guard.py
# 层: 算法
# - id: A1
#   name_zh: ① AgentSkillGuard
#   name_en: AgentSkillGuard
#   intro: class AgentSkillGuard 源码 L81-L106
#   desc: 公共方法（定义序）: register, verify_existing；源码 L81-L106
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: AgentSkillGuard
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum


class SkillSecurityStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    VERIFIED = "VERIFIED"
    BLOCKED = "BLOCKED"
    SANDBOX_ONLY = "SANDBOX_ONLY"


SkillStatus = SkillSecurityStatus


@dataclass
class SkillRecord:
    skill_name: str
    source_url: str
    sha256_hash: str
    status: SkillSecurityStatus = SkillSecurityStatus.UNKNOWN
    verified_by: str = ""


@dataclass
class AgentSkillGuard:
    skills: dict[str, SkillRecord] = field(default_factory=dict)
    trusted_sources: set[str] = field(default_factory=lambda: {"github.com/zephyr"})
    blocked_patterns: set[str] = field(default_factory=lambda: {"eval(", "exec(", "subprocess", "os.system"})

    def register(self, name: str, source: str, content: str) -> SkillSecurityStatus:
        sha = hashlib.sha256(content.encode()).hexdigest()
        source_domain = source.split("/")[2] if "/" in source else ""
        if source_domain in self.trusted_sources:
            status = SkillSecurityStatus.VERIFIED
        else:
            status = SkillSecurityStatus.SANDBOX_ONLY
        for pattern in self.blocked_patterns:
            if pattern in content:
                status = SkillSecurityStatus.BLOCKED
                break
        self.skills[name] = SkillRecord(skill_name=name, source_url=source, sha256_hash=sha, status=status)
        return status

    def verify_existing(self, name: str, current_hash: str) -> SkillSecurityStatus:
        record = self.skills.get(name)
        if record is None:
            return SkillSecurityStatus.UNKNOWN
        if record.sha256_hash != current_hash:
            return SkillSecurityStatus.BLOCKED
        return record.status
