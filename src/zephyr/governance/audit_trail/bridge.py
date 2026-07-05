# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §12
# [MODULE] zephyr.governance.audit_trail.bridge
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit_trail.drift_bridge; zephyr.governance.audit_trail.feedback_bridge; zephyr.governance.audit_trail.delegation_bridge; zephyr.governance.merkle_hourly; zephyr.governance.audit_trail.trust_bridge; zephyr.governance.audit_trail.tiered_storage_bridge
# [CONSUMERS] audit-orchestrator.*; pipeline_runner
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 统一桥接入口; 所有外部依赖通过此桥接访问
# [MODIFY-GUARD] 新增外部依赖必须在此注册
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 桥接失败返回None或空结果
# [TESTS] tests/audit-orchestrator/test_bridge.py
# [A_module] module_id=MOD-GOV_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import logging
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["OrchestratorBridge", "write_to_core"]


def write_to_core(channel: str, payload: dict[str, Any]) -> None:
    logger.info("write_to_core channel=%s payload_keys=%s", channel, list(payload.keys()))


class OrchestratorBridge:
    def __init__(self) -> None:
        self._drift_bridge = None
        self._feedback_bridge = None
        self._delegation_bridge = None
        self._merkle_bridge = None
        self._trust_bridge = None
        self._storage_bridge = None
        self._init_bridges()

    def _init_bridges(self) -> None:
        try:
            from zephyr.governance.audit_trail.drift_bridge import DriftBridge

            self._drift_bridge = DriftBridge()
        except Exception as exc:
            logger.warning("DriftBridge init failed: %s", exc)

        try:
            from zephyr.governance.audit_trail.feedback_bridge import FeedbackBridge

            self._feedback_bridge = FeedbackBridge()
        except Exception as exc:
            logger.warning("FeedbackBridge init failed: %s", exc)

        try:
            from zephyr.governance.audit_trail.delegation_bridge import DelegationBridge

            self._delegation_bridge = DelegationBridge()
        except Exception as exc:
            logger.warning("DelegationBridge init failed: %s", exc)

        try:
            from zephyr.governance.merkle_hourly import MerkleHourlyBridge

            self._merkle_bridge = MerkleHourlyBridge()
        except Exception as exc:
            logger.warning("MerkleHourlyBridge init failed: %s", exc)

        try:
            from zephyr.governance.audit_trail.trust_bridge import TrustBridge

            self._trust_bridge = TrustBridge()
        except Exception as exc:
            logger.warning("TrustBridge init failed: %s", exc)

        try:
            from zephyr.governance.audit_trail.tiered_storage_bridge import TieredStorageBridge

            self._storage_bridge = TieredStorageBridge()
        except Exception as exc:
            logger.warning("TieredStorageBridge init failed: %s", exc)

    def check_drift(self, metrics: dict[str, float]) -> dict[str, Any]:
        if self._drift_bridge and self._drift_bridge.is_available():
            return self._drift_bridge.check_drift(metrics)
        return {"is_drifting": False, "drift_score": 0.0, "available": False}

    def analyze_findings(self, findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if self._feedback_bridge and self._feedback_bridge.is_available():
            return self._feedback_bridge.analyze_audit_findings(findings)
        return []

    def report_delegation_failure(self, target: str, reason: str) -> dict[str, Any] | None:
        if self._delegation_bridge and self._delegation_bridge.is_available():
            return self._delegation_bridge.report_delegation_failure(target, reason)
        return None

    def verify_merkle(self, hour_key: str, expected_root: str) -> bool:
        if self._merkle_bridge and self._merkle_bridge.is_available():
            return self._merkle_bridge.verify(hour_key, expected_root)
        return False

    def health_check(self) -> dict[str, bool]:
        return {
            "drift": self._drift_bridge is not None and self._drift_bridge.is_available(),
            "feedback": self._feedback_bridge is not None and self._feedback_bridge.is_available(),
            "delegation": self._delegation_bridge is not None and self._delegation_bridge.is_available(),
            "merkle": self._merkle_bridge is not None and self._merkle_bridge.is_available(),
            "trust": self._trust_bridge is not None and self._trust_bridge.is_available(),
            "storage": self._storage_bridge is not None and self._storage_bridge.is_available(),
        }


def _get_writer(backend: str | None = None) -> None:
    return None


_AVAILABLE = ["writer", "query", "replay", "integrity"]
