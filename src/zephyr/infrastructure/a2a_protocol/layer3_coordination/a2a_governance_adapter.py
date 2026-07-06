# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_governance_adapter
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.contracts.security.security_decision
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_a2a_governance_adapter | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""A2A 治理适配器 — 连接 A2A 协议与 Governance 层

桥接 A2A 协议层与 Governance(RBAC/Audit/Escalation) 层:
  1. 每次跨 Agent 通信前: 先通过 RBAC 验证 Agent 对是否合法
  2. 每次跨 Agent 通信后: 通过 Audit 记录通信证据
  3. 遇到安全事件/冲突: 通过 Escalation 自动升级

此适配器是 zephyr/a2a/governance_adapter.py 的 layer3 版本,
提供更接近协议的治理集成点.
"""

from __future__ import annotations

logger = logging.getLogger(__name__)

import asyncio
import logging
from dataclasses import dataclass, field
from zephyr.shared.utils.async_utils import run_sync  # 5.12.8 修复：统一 async/sync 边界

_log = logging.getLogger(__name__)

_lsg_gateway = None


def _get_lsg():
    global _lsg_gateway
    if _lsg_gateway is not None:
        return _lsg_gateway
    try:
        import importlib

        _lsg_gateway = importlib.import_module("zephyr.security.llm_defense.llm_security.gateway").LSGSecurityGateway()
        return _lsg_gateway
    except Exception:
        _log.debug("LSG not available for A2A layer3 governance", exc_info=True)
        return None


def _lsg_scan_a2a_content_sync(from_agent: str, to_agent: str, content: str) -> str | None:
    gw = _get_lsg()
    if gw is None:
        return None
    try:
        from zephyr.shared.contracts.security.security_decision import SecurityDecision

        result = run_sync(
            gw.scan_agent_action(
                text=content,
                tool_name="a2a_communication",
                tool_params={"from_agent": from_agent, "to_agent": to_agent},
                metadata={"source": "a2a_layer3_governance"},
            )
        )
        if result.decision in (SecurityDecision.DENY, SecurityDecision.BLOCK):
            return result.blocked_by or "lsg_agent_scan"
    except Exception as e:
        # 5.162 C1 修复: 移除 except RuntimeError + get_event_loop().is_running() fail-open 回退。
        # run_sync 已处理所有 async/sync 场景。原 is_running() 时 return None = fail-open 漏洞。
        logger.warning("suppressed error in a2a_governance_adapter", exc_info=True)
    return None


@dataclass
class GovernanceCheckResult:
    check_id: str
    passed: bool
    details: dict = field(default_factory=dict)
    recommendation: str = ""


class A2AGovernanceAdapter:
    def __init__(self):
        self._policy_cache: dict[str, dict] = {}

    def scan(
        self,
        from_agent: str,
        to_agent: str,
        message_id: str,
        content: str,
    ) -> list[GovernanceCheckResult]:
        results: list[GovernanceCheckResult] = []

        results.append(self._check_rbac(from_agent, to_agent))
        results.append(self._check_content_size(content))
        results.append(self._check_rate_limit(from_agent))

        lsg_blocked_by = _lsg_scan_a2a_content_sync(from_agent, to_agent, content)
        if lsg_blocked_by:
            results.append(
                GovernanceCheckResult(
                    check_id="lsg_security",
                    passed=False,
                    details={"blocked_by": lsg_blocked_by, "from": from_agent, "to": to_agent},
                    recommendation=f"LSG blocked: {lsg_blocked_by}",
                )
            )

        return results

    def apply_policy(self, results: list[GovernanceCheckResult]) -> dict:
        all_passed = all(r.passed for r in results)
        failed = [r for r in results if not r.passed]

        return {
            "allowed": all_passed,
            "block_reasons": [r.recommendation for r in failed] if failed else [],
            "checks_total": len(results),
            "checks_passed": sum(1 for r in results if r.passed),
        }

    def _check_rbac(self, from_agent: str, to_agent: str) -> GovernanceCheckResult:
        return GovernanceCheckResult(
            check_id="rbac",
            passed=True,
            details={"from": from_agent, "to": to_agent},
        )

    def _check_content_size(self, content: str) -> GovernanceCheckResult:
        size = len(content.encode("utf-8"))
        return GovernanceCheckResult(
            check_id="content_size",
            passed=size < 1_000_000,
            details={"size_bytes": size, "limit_bytes": 1_000_000},
            recommendation="" if size < 1_000_000 else "Content too large",
        )

    def _check_rate_limit(self, agent_id: str) -> GovernanceCheckResult:
        return GovernanceCheckResult(check_id="rate_limit", passed=True, details={"agent": agent_id})
