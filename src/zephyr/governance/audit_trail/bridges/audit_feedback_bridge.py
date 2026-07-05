# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] zephyr.governance.audit_trail.bridges.audit_feedback_bridge
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit_trail.query; zephyr.governance.audit_trail.anomaly
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_feedback_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Audit ↔ Feedback Loop 三角闭环桥接.

蓝图 §5 Evolve 支柱 — 审计异常数据驱动 FLE 策略演进。
双向数据流:
  Audit → FLE: 异常事件作为 FLE 输入信号
  FLE → Audit: 进化提案写入审计日志
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

_logger = logging.getLogger(__name__)


class AuditFeedbackBridge:
    """审计↔反馈闭环桥接器.

    将审计异常事件转化为 FLE EvolutionEngine 可消费的信号，
    并将 FLE 进化提案写回审计日志形成闭环。
    """

    def __init__(self) -> None:
        self._anomaly_to_signal = {
            "ANM-001": "UNAUTHORIZED_ACCESS",
            "ANM-002": "BULK_DELETE",
            "ANM-003": "GATE_BYPASS",
            "ANM-004": "CONFIG_CHANGE",
            "ANM-005": "PRIVILEGE_ESCALATION",
            "ANM-006": "TIME_ANOMALY",
            "ANM-007": "LOG_ANOMALY",
            "ANM-008": "AGENT_IMPERSONATION",
            "ANM-009": "SUPPLY_CHAIN_RISK",
            "ANM-010": "INDIRECT_OPERATION",
            "ANM-011": "DATA_EXFILTRATION",
            "ANM-012": "SESSION_HIJACK",
            "ANM-013": "BLUEPRINT_DRIFT",
        }

    def anomaly_to_fle_signal(self, anomaly: dict[str, Any]) -> dict[str, Any] | None:
        """将审计异常事件转化为 FLE EvolutionSignal.

        Args:
            anomaly: AnomalyEvent 字典 (signature_id, severity, agent_id, ...)

        Returns:
            FLE 可消费的信号字典，或 None 如果无法映射
        """
        sig_id = anomaly.get("signature_id", "")
        signal_name = self._anomaly_to_signal.get(sig_id)
        if not signal_name:
            return None

        severity = anomaly.get("severity", "MEDIUM")
        layer = self._classify_layer(severity)

        fle_signal = {
            "source": "audit-trail",
            "signal_type": signal_name,
            "layer": layer,
            "severity": severity,
            "agent_id": anomaly.get("agent_id", "unknown"),
            "timestamp": anomaly.get("timestamp", datetime.now(UTC).isoformat()),
            "details": anomaly.get("details", {}),
        }

        _logger.info(
            "Audit→FLE: %s → %s (layer=%s, severity=%s)",
            sig_id,
            signal_name,
            layer,
            severity,
        )
        return fle_signal

    def evolution_to_audit_record(self, proposal: dict[str, Any]) -> dict[str, Any]:
        """将 FLE 进化提案转化为审计记录.

        Args:
            proposal: EvolutionProposal 字典 (signal, layer, recommended_action, ...)

        Returns:
            可写入 AuditWriter 的审计事件字典
        """
        return {
            "event_type": "feedback_loop_evolution",
            "source": "fle_evolution_engine",
            "signal": proposal.get("signal", ""),
            "layer": proposal.get("layer", ""),
            "severity": proposal.get("severity", ""),
            "recommended_action": proposal.get("recommended_action", ""),
            "timestamp": datetime.now(UTC).isoformat(),
            "provenance": "feedback-loop",
        }

    def scan_and_bridge(self) -> list[dict[str, Any]]:
        """扫描审计异常 → 转化为 FLE 信号列表."""
        try:
            from zephyr.governance.audit_trail.anomaly import AnomalyDetector
            from zephyr.governance.audit_trail.query import AuditQuery

            query = AuditQuery()
            events = query._load_events()
            if not events:
                return []

            detector = AnomalyDetector()
            anomalies = detector.scan(events)

            signals: list[dict[str, Any]] = []
            for a in anomalies:
                sig = self.anomaly_to_fle_signal(
                    {
                        "signature_id": a.signature_id,
                        "severity": a.severity.value if hasattr(a.severity, "value") else str(a.severity),
                        "agent_id": a.agent_id,
                        "timestamp": a.timestamp,
                        "details": a.details if hasattr(a, "details") else {},
                    }
                )
                if sig:
                    signals.append(sig)

            _logger.info("Audit→FLE: bridged %d/%d anomalies", len(signals), len(anomalies))
            return signals
        except Exception:
            _logger.exception("Audit→FLE: bridge scan failed")
            return []

    @staticmethod
    def _classify_layer(severity: str) -> str:
        if severity in ("CRITICAL", "HIGH"):
            return "L3_ARCHITECTURE"
        if severity == "MEDIUM":
            return "L2_PATTERN"
        return "L1_TASK"
