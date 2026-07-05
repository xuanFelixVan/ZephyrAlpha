# [BLUEPRINT] MOD-L10-001 | docs/03_modules/_domain_compliance/blueprint.md
# [MODULE] zephyr.governance.security_governance.default_security_gateway
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.security_governance.security_gateway_base; zephyr.security.llm_defense.llm_security.input_sanitizer; zephyr.governance.intelligence_governance.aisg_sandbox; zephyr.security.llm_defense.llm_security.gateway; zephyr.shared.contracts.security.security_decision
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_default_security_gateway | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ==== BEGIN CODEGEN:OCP-004 ====
"""
DefaultSecurityGateway — SecurityGateway 三层防御 OCP-004 实现

三层防御架构：
  L1 — Prompt Injection 检测（InputSanitizer 集成）
  L2 — 危险代码模式扫描（AISGSandbox 集成）
  L3 — 审计追踪（AuditDecision 生成 + behavior_audit_logger）

SSoT: cross_layer_contracts.yaml v3.0 — CTR-P1-012 (ComplianceRule)
架构决策:  (LPC 双轨),  (沙箱)

Phase F — LLM 安全门禁落地
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, ClassVar
from uuid import uuid4

from zephyr.governance.intelligence_governance.aisg_sandbox import AISGSandbox
from zephyr.shared.utils.async_utils import run_sync  # 5.12.8 修复：统一 async/sync 边界
from zephyr.governance.security_governance.security_gateway_base import (
    AuditAction,
    AuditDecision,
    SecurityGateway,
)
from zephyr.security.llm_defense.llm_security.input_sanitizer import InputSanitizer

_lsg_gateway = None


def _get_lsg():
    global _lsg_gateway
    if _lsg_gateway is not None:
        return _lsg_gateway
    try:
        from zephyr.security.llm_defense.llm_security.gateway import LSGSecurityGateway

        _lsg_gateway = LSGSecurityGateway()
        return _lsg_gateway
    except Exception:
        return None


@dataclass(frozen=True)
class ScanFinding:
    rule_id: str
    severity: str
    message: str
    snippet: str = ""
    line_number: int = 0


@dataclass
class SecurityContext:
    user_id: str = "system"
    session_id: str = ""
    source_module: str = ""
    execution_environment: str = "development"
    allowed_patterns: list[str] = field(default_factory=list)
    blocked_patterns: list[str] = field(default_factory=list)


class DefaultSecurityGateway(SecurityGateway):
    """SecurityGateway 三层防御默认实现（OCP-004）

    OCP 扩展点：
      - 子类可覆盖 _custom_pre_filter() 添加自定义 L1 规则
      - 子类可覆盖 _custom_scan_rules() 添加自定义 L2 规则
      - 子类可覆盖 _custom_audit_hook() 添加自定义 L3 审计回调
    """

    _L1_PATTERNS: ClassVar[list[tuple[str, re.Pattern[str], str]]] = [
        (
            "PROMPT-INJECT-001",
            re.compile(
                r"(ignore\s+(all\s+)?(previous|above|prior)\s+(instructions?|directives?|prompts?)"
                r"|system\s*prompt\s*:?\s*you\s+are\s+now"
                r"|\[INST\].*\[/INST\]"
                r"|<<SYS>>.*<</SYS>>)",
                re.IGNORECASE,
            ),
            "Prompt injection pattern detected — override/system prompt manipulation",
        ),
        (
            "PROMPT-INJECT-002",
            re.compile(
                r"(execute\s+(this\s+)?(code|command|script)"
                r"|eval\s*\(|exec\s*\("
                r"|subprocess\.(run|Popen|call)"
                r"|os\.system\s*\()",
                re.IGNORECASE,
            ),
            "Dangerous code execution pattern in LLM input",
        ),
        (
            "PROMPT-INJECT-003",
            re.compile(
                r"(reveal\s+(your\s+)?(system\s+)?prompt|show\s+(your\s+)?instructions?"
                r"|what\s+(is|are)\s+(your\s+)?(system\s+)?(prompt|instructions?)"
                r"|DAN\s*mode|jailbreak)",
                re.IGNORECASE,
            ),
            "Jailbreak / prompt extraction attempt detected",
        ),
    ]

    _L2_PATTERNS: ClassVar[list[tuple[str, re.Pattern[str], str]]] = [
        (
            "CODE-DANGER-001",
            re.compile(
                r"(rm\s+-rf\s+/|del\s+/[fs]/q" r"|Format-\w+\s+-Force" r"|DROP\s+(TABLE|DATABASE)\s+\w+)",
                re.IGNORECASE,
            ),
            "Destructive system command detected",
        ),
        (
            "CODE-DANGER-002",
            re.compile(
                r"((?:api[_-]?key|secret|password|token|credential)\s*[:=]\s*[\"'][^\"']{8,}[\"'])",
                re.IGNORECASE,
            ),
            "Hardcoded credential detected",
        ),
        (
            "CODE-DANGER-003",
            re.compile(
                r"(http[s]?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
                r"|http[s]?://localhost"
                r"|\.\./\.\./(?:etc|var|root|Windows))",
                re.IGNORECASE,
            ),
            "SSRF / path traversal URL pattern detected",
        ),
    ]

    def __init__(self, context: SecurityContext | None = None, project_root: str = "."):
        self._context = context or SecurityContext()
        self._sanitizer = InputSanitizer(root=project_root)
        self._aisg = AISGSandbox()
        self._findings: list[ScanFinding] = []
        self._l1_clean = True

    # ─── Layer 1: Prompt Injection ───

    def pre_filter(self, content: str, metadata: dict[str, Any] | None = None) -> str:
        """L1 — 预过滤：Prompt Injection + 输入净化"""
        findings: list[ScanFinding] = []

        for rule_id, pattern, message in self._L1_PATTERNS:
            matches = list(pattern.finditer(content))
            for m in matches:
                findings.append(
                    ScanFinding(
                        rule_id=rule_id,
                        severity="error",
                        message=message,
                        snippet=m.group(0)[:120],
                    )
                )

        self._findings.extend(findings)

        try:
            self._sanitizer.validate_llm_context(content)
            self._l1_clean = True
        except Exception:
            self._l1_clean = False
            self._findings.append(
                ScanFinding(
                    rule_id="LLM-CTX-001",
                    severity="error",
                    message="InputSanitizer context validation failed — potential injection",
                )
            )

        sanitized = self._filter_backtick_escape(content)
        return sanitized

    # ─── Layer 2: Dangerous Pattern Scan ───

    def security_scan(self, content: str, metadata: dict[str, Any] | None = None) -> list[ScanFinding]:
        """L2 — 安全扫描：危险代码 + SSRF + Credential"""
        findings: list[ScanFinding] = []

        for rule_id, pattern, message in self._L2_PATTERNS:
            for m in pattern.finditer(content):
                findings.append(
                    ScanFinding(
                        rule_id=rule_id,
                        severity="error",
                        message=message,
                        snippet=m.group(0)[:120],
                    )
                )

        aisg_findings = self._aisg.scan_content(content)
        for af in aisg_findings:
            findings.append(
                ScanFinding(
                    rule_id="AISG-DANGER-001",
                    severity="warning",
                    message=f"AISG sandbox: {af}",
                    snippet="",
                )
            )

        self._findings.extend(findings)
        return findings

    # ─── Layer 3: Decide ───

    def decide(self, content: str, metadata: dict[str, Any] | None = None) -> AuditDecision:
        """L3 — 决策：基于 L1+L2+LSG 发现生成审计决策"""
        errors = [f for f in self._findings if f.severity == "error"]
        warnings_list = [f for f in self._findings if f.severity == "warning"]

        lsg_blocked_by = self._lsg_full_scan(content, metadata)

        if errors or lsg_blocked_by:
            action = AuditAction.BLOCK
        elif warnings_list or not self._l1_clean:
            action = AuditAction.FLAG
        else:
            action = AuditAction.ALLOW

        lsg_info = {"lsg_blocked_by": lsg_blocked_by} if lsg_blocked_by else {}
        return AuditDecision(
            decision_id=f"sgw-{uuid4().hex[:12]}",
            action=action,
            rule_id="L10-SGW-001",
            reason=f"L1+L2+LSG scan: {len(errors)} errors, {len(warnings_list)} warnings, l1_clean={self._l1_clean}, lsg_blocked={bool(lsg_blocked_by)}",
            timestamp=datetime.now(UTC),
            metadata={
                "findings": [
                    {"rule_id": f.rule_id, "severity": f.severity, "message": f.message} for f in self._findings
                ],
                "content_safe": action is not AuditAction.BLOCK,
                "sanction_enabled": len(errors) > 0 or bool(lsg_blocked_by),
                **lsg_info,
            },
        )

    def _lsg_full_scan(self, content: str, metadata: dict[str, Any] | None = None) -> str | None:
        gw = _get_lsg()
        if gw is None:
            return None
        try:
            import asyncio

            from zephyr.shared.contracts.security.security_decision import SecurityDecision

            result = run_sync(gw.scan_input(content, source="l10-compliance", metadata=metadata or {}))
            if result.decision in (SecurityDecision.DENY, SecurityDecision.BLOCK):
                return result.blocked_by or "lsg_input_scan"
        except Exception:
            # 5.16.9 修复：移除废弃的 get_event_loop fallback，run_sync 已处理所有场景
            pass
        return None

    def reset(self) -> None:
        self._findings.clear()
        self._l1_clean = True

    # ─── Helpers ───

    @staticmethod
    def _filter_backtick_escape(content: str) -> str:
        return re.sub(r"```[\s\S]*?```", "[CODE_BLOCK_REDACTED]", content)


__all__ = [
    "DefaultSecurityGateway",
    "ScanFinding",
    "SecurityContext",
]

# ==== END CODEGEN:OCP-004 ====
