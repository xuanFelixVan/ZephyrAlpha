"""Agent Skill Guard — v0.14.0 R201

Blindspot: Agent Skills downloaded from internet without security validation.
Risk: R201 — Malicious skill compromises FLE; unauthorized autonomous actions.

Mitigation: Agent Skill supply chain security with hash validation and sandbox execution.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum


class SkillStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    VERIFIED = "VERIFIED"
    BLOCKED = "BLOCKED"
    SANDBOX_ONLY = "SANDBOX_ONLY"


@dataclass
class SkillRecord:
    skill_name: str
    source_url: str
    sha256_hash: str
    status: SkillStatus = SkillStatus.UNKNOWN
    verified_by: str = ""


@dataclass
class AgentSkillGuard:
    skills: dict[str, SkillRecord] = field(default_factory=dict)
    trusted_sources: set[str] = field(default_factory=lambda: {"github.com/zephyr"})
    blocked_patterns: set[str] = field(default_factory=lambda: {"eval(", "exec(", "subprocess", "os.system"})

    def register(self, name: str, source: str, content: str) -> SkillStatus:
        sha = hashlib.sha256(content.encode()).hexdigest()
        source_domain = source.split("/")[2] if "/" in source else ""
        if source_domain in self.trusted_sources:
            status = SkillStatus.VERIFIED
        else:
            status = SkillStatus.SANDBOX_ONLY
        for pattern in self.blocked_patterns:
            if pattern in content:
                status = SkillStatus.BLOCKED
                break
        self.skills[name] = SkillRecord(skill_name=name, source_url=source, sha256_hash=sha, status=status)
        return status

    def verify_existing(self, name: str, current_hash: str) -> SkillStatus:
        record = self.skills.get(name)
        if record is None:
            return SkillStatus.UNKNOWN
        if record.sha256_hash != current_hash:
            return SkillStatus.BLOCKED
        return record.status
