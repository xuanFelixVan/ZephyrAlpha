# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §12
# [MODULE] zephyr.gov_audit.feedback_bridge
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.trading.__init__
# [CONSUMERS] audit-orchestrator.feedback_policy(策略引擎消费反馈)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 不实现反馈逻辑; 仅桥接FeedbackLoop.analyze_pending()+generate_proposals()+apply_proposal()
# [MODIFY-GUARD] FeedbackLoop API变更时同步此桥接
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 桥接失败返回空结果
# [TESTS] tests/feedback/test_feedback_bridge.py
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from zephyr.shared.io.paths import get_tmp_dir

logger = logging.getLogger(__name__)

__all__ = ["AuditFeedbackBridge", "FeedbackBridge"]


# ---------------------------------------------------------------------------
# Anomaly signature → FLE signal type mapping (ANM-001 through ANM-013).
# Each anomaly signature detected by audit-trail maps to a canonical signal
# type consumed by the Feedback Loop Engine.
# ---------------------------------------------------------------------------

_ANOMALY_SIGNAL_MAP: dict[str, str] = {
    "ANM-001": "UNAUTHORIZED_ACCESS",
    "ANM-002": "PRIVILEGE_ESCALATION",
    "ANM-003": "DATA_EXFILTRATION",
    "ANM-004": "RESOURCE_ABUSE",
    "ANM-005": "CONFIGURATION_DRIFT",
    "ANM-006": "AUDIT_TAMPERING",
    "ANM-007": "RATE_LIMIT_VIOLATION",
    "ANM-008": "BOUNDARY_VIOLATION",
    "ANM-009": "STALE_CREDENTIAL_USE",
    "ANM-010": "UNUSUAL_ACCESS_PATTERN",
    "ANM-011": "DEPENDENCY_CONFUSION",
    "ANM-012": "SECRET_LEAK",
    "ANM-013": "SUPPLY_CHAIN_ANOMALY",
}


# Severity → architecture layer mapping (used by _classify_layer).
_SEVERITY_LAYER_MAP: dict[str, str] = {
    "CRITICAL": "L3_ARCHITECTURE",
    "HIGH": "L3_ARCHITECTURE",
    "MEDIUM": "L2_PATTERN",
    "LOW": "L1_TASK",
    "INFO": "L1_TASK",
}


class FeedbackBridge:
    """Bridge between audit-trail anomaly findings and the Feedback Loop Engine.

    Two parallel APIs coexist:
      1. Legacy FeedbackLoop delegation (analyze_audit_findings/generate_rules/apply)
         — used by `FeedbackPolicy` to translate audit findings into evolution
         proposals.
      2. Anomaly-to-signal bridging (anomaly_to_fle_signal/evolution_to_audit_record/
         scan_and_bridge) — used by audit-orchestrator to translate raw anomaly
         events into FLE signals and back-port FLE evolution decisions into
         audit records.
    """

    def __init__(self, storage_path: Path | None = None) -> None:
        self._loop = None
        self._available = False
        # Anomaly signature → signal type mapping (instance attribute for test access).
        self._anomaly_to_signal: dict[str, str] = dict(_ANOMALY_SIGNAL_MAP)
        try:
            from zephyr.feedback_loop import FeedbackLoop

            # 5.133.6 修复：mkdtemp 创建系统临时目录从不清理，改为项目托管临时目录；
            # 同时开放 storage_path 参数支持依赖注入（测试可 mock）
            self._loop = FeedbackLoop(storage_path or get_tmp_dir() / "feedback_audit_trail")
            self._available = True
        except ImportError:
            logger.warning("FeedbackLoop not available")
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("FeedbackLoop init failed: %s", exc, exc_info=True)

    @property
    def anomaly_to_signal(self) -> dict[str, str]:
        """只读：anomaly_to_signal 映射表（R5 公共化）。"""
        return self._anomaly_to_signal

    @staticmethod
    def classify_layer(severity) -> str:
        """公共接口：classify_layer（Stage 4 公共化）。"""
        return __class__._classify_layer(severity)

    # ------------------------------------------------------------------
    # Legacy FeedbackLoop delegation API
    # ------------------------------------------------------------------

    def analyze_audit_findings(self, findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not self._available or self._loop is None:
            return []
        try:
            entries = [
                {
                    "id": f.get("issue_id", str(i)),
                    "module": "audit-orchestrator",
                    "context": f.get("detail", f.get("type", "unknown finding")),
                }
                for i, f in enumerate(findings)
            ]
            proposals = self._loop.analyze_pending(entries)
            return [
                {
                    "proposal_id": p.proposal_id,
                    "source": p.source,
                    "pattern": p.pattern,
                    "change": p.suggested_rule_change,
                    "confidence": p.confidence,
                }
                for p in proposals
            ]
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.error("FeedbackBridge.analyze_audit_findings failed: %s", exc, exc_info=True)
            return []

    def generate_rules(self, pending: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not self._available or self._loop is None:
            return []
        try:
            proposals = self._loop.generate_proposals(pending)
            return [
                {
                    "proposal_id": p.proposal_id,
                    "source": p.source,
                    "pattern": p.pattern,
                    "change": p.suggested_rule_change,
                    "confidence": p.confidence,
                    "status": p.status,
                }
                for p in proposals
            ]
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.error("FeedbackBridge.generate_rules failed: %s", exc, exc_info=True)
            return []

    def apply(self, proposal: dict[str, Any]) -> bool:
        if not self._available or self._loop is None:
            return False
        try:
            from zephyr.feedback_loop import EvolutionProposal

            p = EvolutionProposal(
                source=proposal.get("source", "unknown"),
                pattern=proposal.get("pattern", ""),
                suggested_rule_change=proposal.get("change", ""),
                confidence=proposal.get("confidence", 0.5),
            )
            return self._loop.apply_proposal(p)
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.error("FeedbackBridge.apply failed: %s", exc, exc_info=True)
            return False

    def is_available(self) -> bool:
        return self._available

    # ------------------------------------------------------------------
    # Anomaly-to-signal bridging API
    # ------------------------------------------------------------------

    def anomaly_to_fle_signal(self, anomaly: dict[str, Any]) -> dict[str, Any] | None:
        """Convert an audit-trail anomaly dict to an FLE signal dict.

        Returns None if the anomaly's `signature_id` is missing or unknown.
        Default severity is MEDIUM; default agent_id is "unknown".
        """
        signature_id = anomaly.get("signature_id")
        if not signature_id:
            return None
        signal_type = self._anomaly_to_signal.get(signature_id)
        if signal_type is None:
            return None
        severity = str(anomaly.get("severity", "MEDIUM")).upper()
        if severity not in _SEVERITY_LAYER_MAP:
            severity = "MEDIUM"
        return {
            "source": "audit-trail",
            "signal_type": signal_type,
            "severity": severity,
            "agent_id": anomaly.get("agent_id", "unknown") or "unknown",
            "timestamp": anomaly.get("timestamp", ""),
            "layer": self._classify_layer(severity),
            "details": anomaly.get("details", {}),
        }

    def evolution_to_audit_record(self, proposal: dict[str, Any]) -> dict[str, Any]:
        """Convert an FLE evolution proposal dict to an audit-trail record dict.

        Empty/missing fields default to empty strings (not None) so downstream
        audit consumers can uniformly use `.get(key, "")` patterns.
        """
        return {
            "event_type": "feedback_loop_evolution",
            "source": "fle_evolution_engine",
            "signal": proposal.get("signal", ""),
            "layer": proposal.get("layer", ""),
            "severity": proposal.get("severity", ""),
            "recommended_action": proposal.get("recommended_action", ""),
            "provenance": "feedback-loop",
        }

    @staticmethod
    def _classify_layer(severity: str) -> str:
        """Map a severity string to an architecture layer.

        Mapping:
          - CRITICAL, HIGH → L3_ARCHITECTURE
          - MEDIUM        → L2_PATTERN
          - LOW, INFO     → L1_TASK
        Unknown severities default to L1_TASK (conservative).
        """
        sev = str(severity).upper()
        return _SEVERITY_LAYER_MAP.get(sev, "L1_TASK")

    def scan_and_bridge(self) -> list[dict[str, Any]]:
        """Scan pending audit anomalies and bridge each to an FLE signal.

        Returns a list of FLE signal dicts (one per bridgable anomaly).
        Empty list if no pending anomalies or FeedbackLoop unavailable.

        Does NOT catch exceptions — callers (and tests) rely on propagating
        RuntimeError/etc. for diagnostic purposes.
        """
        if not self._available or self._loop is None:
            return []
        # Delegate to FeedbackLoop to fetch pending anomalies; bridge each.
        pending = self._loop.fetch_pending_anomalies() if hasattr(self._loop, "fetch_pending_anomalies") else []
        signals: list[dict[str, Any]] = []
        for anomaly in pending:
            signal = self.anomaly_to_fle_signal(anomaly)
            if signal is not None:
                signals.append(signal)
        return signals


# Alias for consumers/tests that import `AuditFeedbackBridge` directly.
# Semantically identical to `FeedbackBridge` — kept as a module-level name
# so `from zephyr.gov_audit.feedback_bridge import AuditFeedbackBridge` works.
AuditFeedbackBridge = FeedbackBridge
