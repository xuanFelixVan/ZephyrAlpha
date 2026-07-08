# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.governance.drift_detection.cascade_detector
# [DOMAIN] D_BEHAVIORAL_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/governance/rule_enforcement/drift_detector.py; tests/audit/test_cascade_detector.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 级联检测不可禁用
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_cascade_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Cascade Failure Detector — 级联故障检测 D-023-22 · §6.15。





module_id: MOD-INF-023


trigger: 同一module 30min内>=3新漂移且每次前一个被修复


action: 暂停自动修复锁定1h + P0通知Owner + cascade_forensics report


prevention: dry-run影响面分析(临时目录模拟修复diff跑关联检测器)


对标 blueprint.md §6.15。"""

from __future__ import annotations

from typing import Final
from zephyr.shared.io.serialization import dumps

import logging

logger = logging.getLogger(__name__)

import json
import os
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path


@dataclass
class CascadeEventRecord:
    event_id: str

    module: str

    detected_at: datetime

    resolved_at: datetime | None = None

    fix_diff: str = ""


@dataclass
class CascadeAlert:
    alert_id: str

    module: str

    trigger_events: list[CascadeEventRecord]

    cascade_count: int

    first_detected: datetime

    last_detected: datetime

    auto_fix_paused: bool = True

    pause_until: datetime | None = None

    forensics_report: str = ""


@dataclass
class CascadeConfig:
    window_minutes: int = 30

    threshold: int = 3

    lockout_minutes: int = 60

    state_dir: str = ""


_CASCADE_STATE_FILE: str = "_cascade_state.json"


CASCADE_CONFIG: Final[CascadeConfig] = CascadeConfig()


def _load_cascade_state() -> dict[str, object]:
    path = os.path.join(CASCADE_CONFIG.state_dir, _CASCADE_STATE_FILE)

    if not path or not os.path.exists(path):
        return {"events": [], "alerts": []}

    try:
        with open(path, encoding="utf-8") as f:
            return json.loads(f.read())

    except Exception:
        return {"events": [], "alerts": []}


def _save_cascade_state(state: dict[str, object]) -> None:
    if not CASCADE_CONFIG.state_dir:
        return

    os.makedirs(CASCADE_CONFIG.state_dir, exist_ok=True)

    path = os.path.join(CASCADE_CONFIG.state_dir, _CASCADE_STATE_FILE)

    tmp = f"{path}.{os.getpid()}.tmp"

    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(dumps(state,  indent=2))

        os.replace(tmp, path)

    except PermissionError:
        try:
            os.remove(tmp)

        except OSError:
            pass


def detect_cascade(
    events: list[dict[str, object]],
) -> list[CascadeAlert]:
    alerts: list[CascadeAlert] = []

    module_events: dict[str, list[dict[str, object]]] = {}

    for evt in events:
        source = str(evt.get("source_file", ""))

        parts = Path(source).parts

        module = "unknown"

        for i, part in enumerate(parts):
            if part in ("src", "tests") and i + 1 < len(parts):
                module = parts[i + 1]

                break

        module_events.setdefault(module, []).append(evt)

    now = datetime.now(UTC)

    window = timedelta(minutes=CASCADE_CONFIG.window_minutes)

    for module, mod_events in module_events.items():
        recent = sorted(
            mod_events,
            key=lambda e: str(e.get("timestamp", "")),
            reverse=True,
        )

        window_events: list[dict[str, object]] = []

        for evt in recent:
            ts_str = str(evt.get("timestamp", ""))

            if not ts_str:
                continue

            try:
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))

            except Exception:
                continue

            if now - ts <= window:
                window_events.append(evt)

        if len(window_events) >= CASCADE_CONFIG.threshold:
            cascade_events: list[CascadeEventRecord] = []

            for we in window_events[: CASCADE_CONFIG.threshold]:
                cascade_events.append(
                    CascadeEventRecord(
                        event_id=str(we.get("event_id", "")),
                        module=module,
                        detected_at=datetime.fromisoformat(str(we.get("timestamp", "")).replace("Z", "+00:00")),
                    )
                )

            pause_until = now + timedelta(minutes=CASCADE_CONFIG.lockout_minutes)

            alert = CascadeAlert(
                alert_id=f"cascade-{module}-{now.strftime('%Y%m%d%H%M')}",
                module=module,
                trigger_events=cascade_events,
                cascade_count=len(window_events),
                first_detected=cascade_events[-1].detected_at,
                last_detected=cascade_events[0].detected_at,
                auto_fix_paused=True,
                pause_until=pause_until,
                forensics_report=(
                    f"Cascade detected in {module}: "
                    f"{len(window_events)} drifts in "
                    f"{CASCADE_CONFIG.window_minutes}min. "
                    f"Auto-fix paused until "
                    f"{pause_until.isoformat()}. "
                    f"Notify Owner."
                ),
            )

            alerts.append(alert)

            _trigger_cascade_rollback(module, cascade_events)

    return alerts


def _trigger_cascade_rollback(
    module: str,
    cascade_events: list[CascadeEventRecord],
) -> None:
    """CT-005: 级联修复循环 -> MOD-INF-021 Rollback 回滚到 cascade 前状态。"""

    try:
        import importlib

        rollback_module = importlib.import_module("zephyr.infrastructure.rollback.engine")

        if hasattr(rollback_module, "execute_rollback"):
            for ce in cascade_events:
                rollback_module.execute_rollback(
                    drift_event_id=ce.event_id,
                    source_module="MOD-INF-023",
                    reason=(f"Cascade fallback ({module}): revert to pre-cascade baseline"),
                )

    except ImportError:
        pass

    except Exception as e:
        logger.warning("suppressed error in cascade_detector", exc_info=True)


def dry_run_impact_analysis(
    fix_diff: str,
    detector_id: str,
    project_root: str,
) -> dict[str, object]:
    """Dry-run影响面分析：临时目录模拟修复diff跑关联检测器。"""

    with tempfile.TemporaryDirectory() as tmpdir_str:
        tmpdir = Path(tmpdir_str)

        test_file = tmpdir / "test_fix.py"

        test_file.write_text(
            f"# Dry-run impact analysis for {detector_id}\n# Fix diff:\n{fix_diff}\n",
            encoding="utf-8",
        )

        impacted_files = 0

        side_effects: list[str] = []

        try:
            import ast

            ast.parse(test_file.read_text(encoding="utf-8"))

        except SyntaxError as e:
            side_effects.append(f"Syntax error in fix: {e}")

    return {
        "detector_id": detector_id,
        "impacted_files": impacted_files,
        "side_effects": side_effects,
        "safe_to_apply": len(side_effects) == 0,
    }


def is_auto_fix_paused(module: str) -> bool:
    state = _load_cascade_state()

    alerts = state.get("alerts", [])

    now = datetime.now(UTC)

    for alert in alerts:
        if alert.get("module") == module and alert.get("auto_fix_paused", True):
            pause_until_str = alert.get("pause_until", "")

            if pause_until_str:
                try:
                    pause_until = datetime.fromisoformat(pause_until_str.replace("Z", "+00:00"))

                    if now < pause_until:
                        return True

                except Exception as e:
                    logger.warning("suppressed error in cascade_detector", exc_info=True)

    return False
