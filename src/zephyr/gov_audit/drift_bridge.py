# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §12
# [MODULE] zephyr.gov_audit.drift_bridge
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] audit-orchestrator.self_monitor(自监控漂移检测)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 不实现漂移检测逻辑; 仅桥接DriftDetector.establish_baseline()+detect()+is_drifting()
# [MODIFY-GUARD] DriftDetector API变更时同步此桥接
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 桥接失败返回无漂移(false)
# [TESTS] tests/bridges/test_bridges_drift_bridge.py
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

__all__ = ["BridgeResult", "DriftBridge"]


class BridgeResult(BaseModel):
    """drift bridge sync result -- 对齐 test_bridges_drift_bridge.py."""

    audit_anomalies: int = 0
    drift_events: int = 0
    matched: int = 0
    unmatched_audit: int = 0
    unmatched_drift: int = 0
    critical_gaps: int = 0
    synced_at: str = ""


class DriftBridge:
    """Audit <-> Drift bridge -- 对齐 test_bridges_drift_bridge.py.

    New API: DriftBridge(audit_events_path=...) + sync() -> BridgeResult
    Old API: establish_baseline/check_drift/is_available (backward compat)
    """

    def __init__(self, audit_events_path: Path | str | None = None) -> None:
        # 治本（AI-AUDIT12 路径SSoT收敛）：默认锚定 AUDIT_DATA_DIR 真源
        # （原 None 默认使桥接默认构造即静默空读，test_default_path 契约
        # 要求 audit_events_path 非 None）。
        if audit_events_path is None:
            from zephyr.shared.io.paths import AUDIT_DATA_DIR

            audit_events_path = AUDIT_DATA_DIR / "events.jsonl"
        self._audit_events_path: Path | None = Path(audit_events_path)
        self._detector = None
        self._available = False
        try:
            from zephyr.gov_drift.drift_detector import DriftDetector

            self._detector = DriftDetector()
            self._available = True
        except ImportError:
            logger.warning("DriftDetector not available")
        except Exception as exc:  # noqa: BLE001
            logger.warning("DriftDetector init failed: %s", exc, exc_info=True)

    def scan_drift_events(self) -> list[dict[str, Any]]:
        """公共接口：scan_drift_events（Stage 4 公共化）。"""
        return self._scan_drift_events()


    def scan_audit_anomalies(self) -> list[dict[str, Any]]:
        """公共接口：scan_audit_anomalies（Stage 4 公共化）。"""
        return self._scan_audit_anomalies()


    def load_events(self) -> list[dict[str, Any]]:
        """公共接口：load_events（Stage 4 公共化）。"""
        return self._load_events()


    @property
    def audit_events_path(self) -> Path | None:
        """只读：audit_events_path（Stage 4 公共化）。"""
        return self._audit_events_path

    @audit_events_path.setter
    def audit_events_path(self, value):
        """写入：audit_events_path（Stage 4 公共化）。"""
        self._audit_events_path = value


    # --- new API ---

    def _load_events(self) -> list[dict[str, Any]]:
        if self._audit_events_path is None or not self._audit_events_path.exists():
            return []
        try:
            content = self._audit_events_path.read_text(encoding="utf-8")
        except OSError:
            return []
        events: list[dict[str, Any]] = []
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return events

    def _scan_audit_anomalies(self) -> list[dict[str, Any]]:
        try:
            from zephyr.gov_audit.anomaly import AnomalyDetector
        except ImportError:
            return []
        try:
            detector = AnomalyDetector()
            events = self._load_events()
            results: list[dict[str, Any]] = []
            for ev in events:
                if ev.get("event_type") == "anomaly_detected":
                    results.append(ev)
            return results
        except Exception:  # noqa: BLE001
            return []

    def _scan_drift_events(self) -> list[dict[str, Any]]:
        try:
            from zephyr.gov_drift.drift_detector import DriftDetector
        except ImportError:
            return []
        try:
            detector = DriftDetector()
            return []
        except Exception:  # noqa: BLE001
            return []

    def sync(self) -> BridgeResult:
        audit_anomalies = self._scan_audit_anomalies()
        drift_events = self._scan_drift_events()

        audit_paths = {a.get("target_path") for a in audit_anomalies if a.get("target_path")}
        drift_paths = {d.get("target_path") for d in drift_events if d.get("target_path")}

        matched_paths = audit_paths & drift_paths
        unmatched_audit = audit_paths - drift_paths
        unmatched_drift = drift_paths - audit_paths

        critical_gaps = sum(
            1
            for a in audit_anomalies
            if a.get("severity") == "CRITICAL"
            and a.get("target_path")
            and a.get("target_path") not in drift_paths
        )

        return BridgeResult(
            audit_anomalies=len(audit_anomalies),
            drift_events=len(drift_events),
            matched=len(matched_paths),
            unmatched_audit=len(unmatched_audit),
            unmatched_drift=len(unmatched_drift),
            critical_gaps=critical_gaps,
            synced_at=datetime.now(UTC).isoformat(),
        )

    # --- old API (backward compat) ---

    def establish_baseline(self, metrics: dict[str, float]) -> bool:
        if not self._available or self._detector is None:
            return False
        try:
            self._detector.establish_baseline(metrics)
            return True
        except Exception as exc:  # noqa: BLE001
            logger.error("DriftBridge.establish_baseline failed: %s", exc, exc_info=True)
            return False

    def check_drift(self, current: dict[str, float], threshold: float = 0.3) -> dict[str, Any]:
        if not self._available or self._detector is None:
            return {"is_drifting": False, "drift_score": 0.0, "available": False}
        try:
            score = self._detector.detect(current)
            return {
                "is_drifting": self._detector.is_drifting(current, threshold),
                "drift_score": round(score, 4),
                "available": True,
            }
        except Exception as exc:  # noqa: BLE001
            logger.error("DriftBridge.check_drift failed: %s", exc, exc_info=True)
            return {"is_drifting": False, "drift_score": 0.0, "available": False}

    def is_available(self) -> bool:
        return self._available
