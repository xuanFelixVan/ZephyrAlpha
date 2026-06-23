# [BLUEPRINT] MOD-INF-027 | docs/03_modules/_cross_layer/audit-orchestrator/blueprint.md | §8
# [MODULE] zephyr.governance.audit_trail.delegation_auditor
# [DOMAIN] D-GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit_trail.delegation_bridge
# [CONSUMERS] audit-orchestrator.integrity(完整性校验子流程)
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 审计委托事件链完整性; 检测循环委托/深度溢出/死锁
# [MODIFY-GUARD] DelegationEngine API变更时同步此审计器
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 审计失败返回空结果
# [TESTS] tests/audit-orchestrator/test_delegation_auditor.py
# [A_module] module_id=MOD-GOV_delegation_auditor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
import logging
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["DelegationAuditor"]

MAX_DELEGATION_DEPTH = 5


class DelegationAuditor:
    def __init__(self) -> None:
        self._bridge = None
        self._available = False
        try:
            from zephyr.governance.audit_trail.delegation_bridge import DelegationBridge

            self._bridge = DelegationBridge()
            self._available = self._bridge.is_available()
        except ImportError:
            logger.warning("DelegationBridge not available")
        except Exception as exc:
            logger.warning("DelegationBridge init failed: %s", exc)

    def audit_delegation_chain(self, events: list[dict[str, Any]]) -> dict[str, Any]:
        if not self._available:
            return {"status": "skipped", "reason": "DelegationBridge unavailable", "findings": []}

        findings: list[dict[str, Any]] = []
        visited: set[str] = set()
        chain: list[str] = []

        for event in events:
            chain.append(event.get("target", ""))
            target = event.get("target", "")

            if target in visited:
                findings.append(
                    {
                        "severity": "RED",
                        "type": "circular_delegation",
                        "target": target,
                        "detail": f"Circular delegation detected: {' -> '.join(chain)}",
                    }
                )

            visited.add(target)

            depth = event.get("depth", 0)
            if depth > MAX_DELEGATION_DEPTH:
                findings.append(
                    {
                        "severity": "YELLOW",
                        "type": "depth_overflow",
                        "target": target,
                        "depth": depth,
                        "detail": f"Delegation depth {depth} exceeds max {MAX_DELEGATION_DEPTH}",
                    }
                )

            if event.get("deadlock", False):
                findings.append(
                    {
                        "severity": "RED",
                        "type": "deadlock",
                        "target": target,
                        "detail": "Potential deadlock detected in delegation chain",
                    }
                )
                if self._bridge:
                    self._bridge.report_delegation_failure(target, "deadlock detected")

        return {
            "status": "completed",
            "events_scanned": len(events),
            "findings": findings,
            "pass": len([f for f in findings if f["severity"] == "RED"]) == 0,
        }

    def is_available(self) -> bool:
        return self._available
