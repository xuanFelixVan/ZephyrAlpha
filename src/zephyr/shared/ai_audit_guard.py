"""
AI Audit Guard — AI 修改审计守卫规则引擎 (M-17)
职责：拦截未授权的 AI 高风险操作，记录 Provenance Chain。
同时写入核心 zephyr.audit_trail.writer.AuditWriter 不可变审计链。

设计：
  - 规则从 YAML 加载（config/audit/audit_rules.yaml）
  - 每项 AI 修改提交前经过规则引擎校验
  - 高风险操作默认拦截，需 Human override
"""
import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from zephyr.audit_trail.bridge import write_to_core


class AuditAction(Enum):
    MODIFY = "modify"
    CREATE = "create"
    DELETE = "delete"
    RENAME = "rename"
    EXECUTE = "execute"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditVerdict(Enum):
    ALLOW = "allow"
    BLOCK = "block"
    REQUIRE_HUMAN = "require_human"
    FLAG = "flag"


@dataclass
class AuditRule:
    rule_id: str
    action: AuditAction
    target_pattern: str
    risk_level: RiskLevel
    verdict: AuditVerdict
    description: str = ""


@dataclass
class AuditRequest:
    agent_id: str
    action: AuditAction
    target: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class AuditResult:
    request: AuditRequest
    verdict: AuditVerdict
    matched_rules: list[str] = field(default_factory=list)
    provenance_hash: Optional[str] = None
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))


class AuditGuardEngine:
    """
    AI 审计守卫规则引擎 (M-17)
    规则匹配逻辑：按 target_pattern 进行 glob 匹配
    """

    DEFAULT_BLOCKED_PATTERNS = [
        "docs/01_policies_and_standards/**",
        "src/zephyr/shared/schemas.py",
        ".trae/rules/project_rules.md",
        "config/**/*.yaml",
    ]

    def __init__(self, rules_path: Optional[str] = None):
        self.rules: list[AuditRule] = []
        self._audit_log: list[AuditResult] = []
        self._load_rules(rules_path)

    def _load_rules(self, rules_path: Optional[str] = None):
        if rules_path and os.path.exists(rules_path):
            import yaml
            with open(rules_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                for r in data.get("rules", []):
                    self.rules.append(AuditRule(
                        rule_id=r["rule_id"],
                        action=AuditAction(r["action"]),
                        target_pattern=r["target_pattern"],
                        risk_level=RiskLevel(r["risk_level"]),
                        verdict=AuditVerdict(r["verdict"]),
                        description=r.get("description", ""),
                    ))

        for pattern in self.DEFAULT_BLOCKED_PATTERNS:
            self.rules.append(AuditRule(
                rule_id=f"blocked-{hashlib.md5(pattern.encode()).hexdigest()[:8]}",
                action=AuditAction.MODIFY,
                target_pattern=pattern,
                risk_level=RiskLevel.CRITICAL,
                verdict=AuditVerdict.BLOCK,
                description=f"Default blocked: {pattern}",
            ))

    def evaluate(self, request: AuditRequest) -> AuditResult:
        import fnmatch

        matched_rules = []
        highest_verdict = AuditVerdict.ALLOW

        for rule in self.rules:
            if rule.action != request.action:
                continue
            if fnmatch.fnmatch(request.target, rule.target_pattern):
                matched_rules.append(rule.rule_id)
                if self._verdict_severity(rule.verdict) > self._verdict_severity(highest_verdict):
                    highest_verdict = rule.verdict

        provenance_hash = self._compute_provenance_hash(request)

        result = AuditResult(
            request=request,
            verdict=highest_verdict,
            matched_rules=matched_rules,
            provenance_hash=provenance_hash,
        )
        self._audit_log.append(result)
        write_to_core("ai_audit_guard", {
            "agent_id": request.agent_id,
            "action": request.action.value,
            "target": request.target,
            "verdict": highest_verdict.value,
            "matched_rules": matched_rules,
            "provenance_hash": provenance_hash,
        })
        return result

    def _verdict_severity(self, verdict: AuditVerdict) -> int:
        return {
            AuditVerdict.ALLOW: 0,
            AuditVerdict.FLAG: 1,
            AuditVerdict.REQUIRE_HUMAN: 2,
            AuditVerdict.BLOCK: 3,
        }.get(verdict, 0)

    def _compute_provenance_hash(self, request: AuditRequest) -> str:
        payload = json.dumps({
            "agent_id": request.agent_id,
            "action": request.action.value,
            "target": request.target,
            "old_value": request.old_value,
            "new_value": request.new_value,
            "timestamp": time.time(),
        }, sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def get_audit_log(self, limit: int = 100) -> list[AuditResult]:
        return self._audit_log[-limit:]

    def clear_log(self):
        self._audit_log.clear()


_guard: Optional[AuditGuardEngine] = None


def get_guard() -> AuditGuardEngine:
    global _guard
    if _guard is None:
        _guard = AuditGuardEngine()
    return _guard
