# [BLUEPRINT] MOD-INF-020 | 03_modules/l01_infrastructure/audit-trail/blueprint.md | §

# [MODULE] zephyr.audit_trail.drift_bridge

# [INVARIANTS] see blueprint MOD-INF-020

# [MODIFY-GUARD] __init__.py

# [CONSUMERS] zephyr.audit_trail

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] AuditTrailError

# [TESTS]

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


    """审计追踪链 <-> 漂移检测器双向桥接.





    使用方式:


        bridge = DriftBridge()


        result = bridge.sync()


        if result.critical_gaps > 0:


            print(f"⚠ {result.critical_gaps} 处关键缺口")


    """





    def __init__(


        self,


        audit_events_path: Path | str = Path("data/audit_trail/events.jsonl"),


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


            from zephyr.audit_trail.anomaly import AnomalyDetector





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


            logger.info("[drift-bridge] AnomalyDetector not available--跳过审计异常扫描")


            return []


        except Exception:


            logger.exception("[drift-bridge] 审计异常扫描失败")


            return []





    def _scan_drift_events(self) -> list[dict[str, Any]]:


        try:


            from zephyr.behavioral_auditor.drift_engine import scan as drift_scan
            from zephyr.behavioral_auditor.drift_models import DriftEvent
            import asyncio

            result = asyncio.get_event_loop().run_until_complete(drift_scan(level="LIGHT"))
            events = result.events if hasattr(result, "events") else []


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


            logger.info("[drift-bridge] drift scan not available--跳过漂移扫描")


            return []


        except Exception:


            logger.exception("[drift-bridge] 漂移事件扫描失败")


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


