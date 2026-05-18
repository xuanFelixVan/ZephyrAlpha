# [BLUEPRINT] MOD-L10-001 | 03_modules/l10_compliance/compliance-core/blueprint.md | §

# [MODULE] zephyr.l10_compliance.implementations.default_security_gateway

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""L10 — Default Security Gateway

AI 安全网关具体实现。实现 SecurityGateway (OCP L10-AISG)。

CTR 契约：
  消费者 — CTR-P1-006 (StrategyLifecycleEvent) ← L05
  生产者 — CTR-P1-012 (ComplianceRule) → L04, L06

SSoT: cross-layer-contracts.yaml → CTR-P1-012
"""
from __future__ import annotations

import asyncio
import logging
import re
import uuid
from typing import Any

from zephyr.l10_compliance.security_gateway_base import (
    AuditAction,
    AuditDecision,
    SecurityGateway,
)

_logger = logging.getLogger(__name__)

_lsg_gateway = None


def _get_lsg():
    global _lsg_gateway
    if _lsg_gateway is not None:
        return _lsg_gateway
    try:
        from zephyr.llm_security.gateway import LSGSecurityGateway
        _lsg_gateway = LSGSecurityGateway()
        return _lsg_gateway
    except Exception:
        _logger.debug("LSG not available for L10 implementations gateway")
        return None


def _lsg_scan_content_sync(content: str) -> str | None:
    gw = _get_lsg()
    if gw is None:
        return None
    try:
        from zephyr.shared.contracts.security.security_decision import SecurityDecision
        result = asyncio.run(
            gw.scan_input(content, source="l10_implementations_gateway", metadata={})
        )
        if result.decision in (SecurityDecision.DENY, SecurityDecision.BLOCK):
            return result.blocked_by or "lsg_input_scan"
    except RuntimeError:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return None
            result = loop.run_until_complete(
                gw.scan_input(content, source="l10_implementations_gateway", metadata={})
            )
            from zephyr.shared.contracts.security.security_decision import SecurityDecision
            if result.decision in (SecurityDecision.DENY, SecurityDecision.BLOCK):
                return result.blocked_by or "lsg_input_scan"
        except Exception:
            pass
    except Exception:
        pass
    return None


class DefaultSecurityGateway(SecurityGateway):
    """默认 AI 安全网关——预过滤 + 规则扫描 + 审计决策"""

    _BLOCKED_PATTERNS: list[tuple[str, str]] = [
        (r"os\.system\(", "system_call"),
        (r"subprocess\.(call|Popen|run)\(", "subprocess_call"),
        (r"eval\(", "dynamic_eval"),
        (r"exec\(", "dynamic_exec"),
        (r"__import__\(", "dynamic_import"),
        (r"shutil\.rmtree", "destructive_delete"),
        (r"requests\.delete.*production", "production_api_delete"),
    ]

    _WARNING_PATTERNS: list[tuple[str, str]] = [
        (r"\.write\(\s*[\"']/etc/", "system_file_write"),
        (r"DROP\s+TABLE", "sql_drop_table"),
        (r"DELETE\s+FROM\s+(orders|trades|positions)", "sql_destructive_delete"),
        (r"rm\s+-rf\s+/", "rm_root"),
    ]

    def pre_filter(self, content: str, source: str) -> bool:
        if not content or len(content.strip()) == 0:
            return False
        if len(content) > 1_000_000:
            return True
        return True

    def security_scan(self, content: str) -> list[str]:
        risks: list[str] = []

        for pattern, risk_id in self._BLOCKED_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                risks.append(f"BLOCK:{risk_id}")

        for pattern, risk_id in self._WARNING_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                risks.append(f"WARN:{risk_id}")

        return risks

    def decide(self, risks: list[str], context: dict[str, Any]) -> AuditDecision:
        blocked = [r for r in risks if r.startswith("BLOCK:")]
        warned = [r for r in risks if r.startswith("WARN:")]

        lsg_blocked_by = _lsg_scan_content_sync(context.get("content", ""))
        if lsg_blocked_by:
            blocked.append(f"BLOCK:LSG-{lsg_blocked_by}")

        decision_id = f"audit-{uuid.uuid4().hex[:8]}"

        if blocked:
            return AuditDecision(
                decision_id=decision_id,
                action=AuditAction.BLOCK,
                rule_id="AISG-001",
                reason=f"Blocked risks: {', '.join(blocked)}",
                metadata={
                    "blocked_risks": blocked,
                    "warned_risks": warned,
                    "source": context.get("source", "unknown"),
                    "lsg_blocked_by": lsg_blocked_by,
                },
            )

        if warned:
            return AuditDecision(
                decision_id=decision_id,
                action=AuditAction.FLAG,
                rule_id="AISG-002",
                reason=f"Flagged risks: {', '.join(warned)}",
                metadata={
                    "warned_risks": warned,
                    "source": context.get("source", "unknown"),
                },
            )

        return AuditDecision(
            decision_id=decision_id,
            action=AuditAction.ALLOW,
            rule_id="AISG-000",
            reason="No risks detected",
            metadata={"source": context.get("source", "unknown")},
        )


__all__ = ["DefaultSecurityGateway"]
