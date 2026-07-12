# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] zephyr.gov_audit.bridges.audit_drift_bridge
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.shared.schema.schemas; zephyr.gov_audit.anomaly; zephyr.governance.drift_detection.drift_engine; zephyr.governance.drift_detection.drift_models
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
# [A_module] module_id=MOD-GOV_drift_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
G-CT-007 Audit ↔ Drift 双向桥接 — MOD-INF-020 ↔ MOD-INF-023
=============================================================
蓝图 §2.6 · 审计异常 ↔ 漂移检测双向联动

SRC-0038: 副本文件 — 保持独立实现，待后续审核。
  此文件是 drift-detector 真源 (src/zephyr/drift-detector/) 的**桥接层消费者**，
  包含专属的 DriftBridge.sync() 审计↔漂移交叉对账逻辑，不可简化为纯 shim。
  已从真源导入: drift_engine.DriftEngine, drift_models.DriftEvent.

桥接功能
--------
  DriftBridge.sync():
    1. 从 audit-trail 拉取最近异常事件
    2. 从 drift-detector 拉取最近 DriftEvent
    3. 交叉对账——漂移事件中未匹配审计记录的 = 潜在审计规避
    4. 审计异常中未匹配漂移的 = 潜在漂移盲区

契约锚定: DOM-GOV-001 G-CT-007
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from zephyr.shared.schema.schemas import BASE_CONFIG

logger = logging.getLogger(__name__)


class BridgeResult(BaseModel):
    model_config = BASE_CONFIG

    synced_at: str = ""
    audit_anomalies: int = 0
    drift_events: int = 0
    matched: int = 0
    unmatched_audit: int = 0
    unmatched_drift: int = 0
    critical_gaps: int = 0


class DriftBridge:
    """审计追踪链 ↔ 漂移检测器双向桥接。

    使用方式:
        bridge = DriftBridge()
        result = bridge.sync()
        if result.critical_gaps > 0:
            print(f"⚠ {result.critical_gaps} 处关键缺口")
    """

    def __init__(
        self,
        audit_events_path: Path | str = Path("data/audit-trail/events.jsonl"),
    ) -> None:
        self._audit_events_path = Path(audit_events_path)

    def sync(self) -> BridgeResult:
        audit_anomalies = self._scan_audit_anomalies()
        drift_events = self._scan_drift_events()

        matched = 0
        drift_targets = {d.get("target_path", "") for d in drift_events}

        for a in audit_anomalies:
            a_target = a.get("target_path", a.get("resource_path", ""))
            if a_target in drift_targets:
                matched += 1

        result = BridgeResult(
            synced_at=datetime.now(UTC).isoformat(),
            audit_anomalies=len(audit_anomalies),
            drift_events=len(drift_events),
            matched=matched,
            unmatched_audit=len(audit_anomalies) - matched,
            unmatched_drift=len(drift_events) - matched,
            critical_gaps=sum(
                1
                for a in audit_anomalies
                if a.get("severity", "") in ("HIGH", "CRITICAL") and a.get("target_path", "") not in drift_targets
            ),
        )

        if result.critical_gaps > 0:
            logger.warning(
                "[drift-bridge] %d critical gaps: audit anomalies without drift confirmation",
                result.critical_gaps,
            )

        return result

    def _scan_audit_anomalies(self) -> list[dict[str, Any]]:
        try:
            from zephyr.gov_audit.anomaly import AnomalyDetector

            events = self._load_events()
            detector = AnomalyDetector()
            anomalies = detector.scan(events)

            return [
                {
                    "signature_id": a.signature_id,
                    "signature_name": a.signature_name,
                    "severity": a.severity,
                    "agent_id": a.agent_id,
                    "session_id": a.session_id,
                    "target_path": a.details.get("target_path", ""),
                }
                for a in anomalies
            ]
        except ImportError:
            logger.info("[drift-bridge] AnomalyDetector not available—跳过审计异常扫描")
            return []
        except Exception:
            logger.exception("[drift-bridge] 审计异常扫描失败", exc_info=True)
            return []

    def _scan_drift_events(self) -> list[dict[str, Any]]:
        try:
            from zephyr.governance.drift_detection.drift_engine import DriftEngine
            from zephyr.governance.drift_detection.drift_models import DriftEvent

            engine = DriftEngine()
            events = engine.recent_events(limit=50)
            return [
                {
                    "drift_id": getattr(e, "drift_id", ""),
                    "target_path": getattr(e, "target_path", ""),
                    "severity": getattr(e, "severity", ""),
                    "detected_at": getattr(e, "detected_at", ""),
                }
                for e in events
            ]
        except ImportError:
            logger.info("[drift-bridge] DriftEngine not available—跳过漂移扫描")
            return []
        except Exception:
            logger.exception("[drift-bridge] 漂移事件扫描失败", exc_info=True)
            return []

    def _load_events(self) -> list[dict[str, Any]]:
        import json

        if not self._audit_events_path.exists():
            return []

        events: list[dict[str, Any]] = []
        with open(self._audit_events_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
        return events