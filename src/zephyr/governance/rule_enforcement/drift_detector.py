# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.governance.rule_enforcement.drift_detector
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] zephyr.shared.contracts.protocols; zephyr.governance.drift_detection.drift_hotfix_bypass; zephyr.governance.drift_detection.drift_engine; zephyr.governance.drift_detection.cascade_detector; zephyr.governance.drift_detection.reconciler; zephyr.governance.__init__; zephyr.governance.drift_detection.events
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
# [A_module] module_id=MOD-GOV_drift_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Gate-side Drift Detector Recovery — zephyr.governance.rule_enforcement.drift_detector

module_id: GCT-023 (gate integration)
trigger_router 消费端：drift_detected 事件 → 扫描确认 → 自动修复 → 回滚兜底。

SRC-0038: 副本文件 — 保持独立实现，待后续审核。
  此文件是 drift-detector 真源 (src/zephyr/drift-detector/) 的**消费者/编排层**，
  包含专属的 trigger_recovery() 恢复流程编排逻辑，不可简化为纯 shim。
  已从真源导入: drift_engine, drift_hotfix_bypass, cascade_detector, reconciler.

完整恢复流程：
  1. 从 payload 提取漂移上下文（module_id / changed_files / commit_message）
  2. 调用 drift_engine.scan() 确认漂移
  3. 级联检测（cascade_detector.detect_cascade）
  4. 对可自动修复事件执行 AutoFixer.auto_fix()
  5. 修复失败 → DriftFixHandler.on_drift_fix() 兜底回滚
  6. Hotfix 旁路检查（[HOTFIX]/[EMERGENCY] commit 72h 抑制）
  7. 返回结构化恢复结果

对标: MOD-INF-023 blueprint.md §2.5（自动对账策略）+ trigger_router.yaml drift_detected
"""

from __future__ import annotations

import asyncio
import logging
import os
import uuid
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def trigger_recovery(payload: dict[str, Any]) -> dict[str, Any]:
    """``drift_detected`` 触发器恢复入口。

    Parameters
    ----------
    payload : dict
        trigger_router.dispatch() 透传的负载，预期包含：
        - module_id (str): 漂移发生的模块 ID
        - changed_files (list[str]): 变更文件列表（可选）
        - commit_message (str): 触发 commit 消息（可选，用于 hotfix 旁路判断）
        - scan_level (str): 扫描级别 LIGHT/STANDARD/DEEP（可选，默认 STANDARD）

    Returns
    -------
    dict
        恢复结果，包含 recovery_status / scan_result / fix_results / cascade_alerts
    """
    module_id = payload.get("module_id", "MOD-INF-023")
    changed_files = payload.get("changed_files", [])
    commit_message = payload.get("commit_message", "")
    scan_level_str = payload.get("scan_level", "STANDARD")

    result: dict[str, Any] = {
        "recovery_id": str(uuid.uuid4()),
        "module_id": module_id,
        "triggered_at": datetime.now(UTC).isoformat(),
        "recovery_status": "INITIATED",
        "scan_result": None,
        "fix_results": [],
        "cascade_alerts": [],
        "hotfix_bypass": False,
        "errors": [],
    }

    try:
        from zephyr.governance.drift_detection.drift_hotfix_bypass import HotfixBypass

        bypass = HotfixBypass(project_root=_PROJECT_ROOT)
        if commit_message and bypass.is_hotfix_commit(commit_message):
            result["hotfix_bypass"] = True
            result["recovery_status"] = "HOTFIX_BYPASSED"
            logger.info("Drift recovery bypassed: hotfix commit detected for %s", module_id)
            return result
    except Exception as exc:
        logger.debug("Hotfix bypass check failed (non-fatal): %s", exc)

    try:
        from zephyr.governance.drift_detection.drift_engine import (
            ScanLevel,
            build_report,
            scan,
        )

        level = ScanLevel[scan_level_str]
    except (KeyError, ImportError) as exc:
        level = ScanLevel.STANDARD
        if isinstance(exc, ImportError):
            result["errors"].append(f"drift_engine import failed: {exc}")
            result["recovery_status"] = "SCAN_FAILED"
            return result

    try:
        scan_result = asyncio.get_event_loop().run_until_complete(scan(level=level, scope=changed_files or None))
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            scan_result = loop.run_until_complete(scan(level=level, scope=changed_files or None))
        finally:
            loop.close()
    except Exception as exc:
        result["errors"].append(f"scan failed: {exc}")
        result["recovery_status"] = "SCAN_FAILED"
        return result

    result["scan_result"] = {
        "scan_id": str(scan_result.scan_id),
        "detectors_run": scan_result.detectors_run,
        "total_drift_events": scan_result.total_drift_events,
        "storm_mode_triggered": scan_result.storm_mode_triggered,
    }

    if scan_result.total_drift_events == 0:
        result["recovery_status"] = "NO_DRIFT_FOUND"
        return result

    try:
        from zephyr.governance.drift_detection.cascade_detector import detect_cascade, is_auto_fix_paused

        event_dicts = []
        for evt in scan_result.events:
            event_dicts.append(
                {
                    "event_id": str(evt.event_id),
                    "source_file": evt.drift_dimension,
                    "timestamp": evt.created_at.isoformat() if evt.created_at else "",
                }
            )

        cascade_alerts = detect_cascade(event_dicts)
        result["cascade_alerts"] = [
            {
                "alert_id": a.alert_id,
                "module": a.module,
                "cascade_count": a.cascade_count,
                "auto_fix_paused": a.auto_fix_paused,
                "pause_until": a.pause_until.isoformat() if a.pause_until else None,
                "forensics_report": a.forensics_report,
            }
            for a in cascade_alerts
        ]

        if is_auto_fix_paused(module_id):
            result["recovery_status"] = "CASCADE_LOCKOUT"
            logger.warning("Auto-fix paused for %s due to cascade detection", module_id)
            return result
    except Exception as exc:
        logger.debug("Cascade detection failed (non-fatal): %s", exc)

    try:
        from zephyr.governance.drift_detection.reconciler import AutoFixer

        fixer = AutoFixer(project_root=_PROJECT_ROOT)
    except ImportError as exc:
        result["errors"].append(f"AutoFixer import failed: {exc}")
        result["recovery_status"] = "FIXER_UNAVAILABLE"
        return result

    fix_results: list[dict[str, Any]] = []
    fixed_count = 0
    failed_count = 0

    for event in scan_result.events:
        try:
            fixer.pre_fix_snapshot(event, changed_files)
            success = fixer.auto_fix(event)

            if success:
                fixed_count += 1
                fix_results.append(
                    {
                        "event_id": str(event.event_id),
                        "dimension": event.drift_dimension,
                        "status": "AUTO_FIXED",
                    }
                )
            else:
                failed_count += 1
                fallback = _fallback_to_rollback_handler(event)
                fix_results.append(
                    {
                        "event_id": str(event.event_id),
                        "dimension": event.drift_dimension,
                        "status": fallback["action"],
                        "detail": fallback.get("reason", "auto_fix returned False"),
                    }
                )
        except Exception as exc:
            failed_count += 1
            fix_results.append(
                {
                    "event_id": str(event.event_id),
                    "dimension": event.drift_dimension,
                    "status": "FIX_ERROR",
                    "detail": str(exc),
                }
            )

    result["fix_results"] = fix_results

    if failed_count == 0:
        result["recovery_status"] = "FULLY_RECOVERED"
    elif fixed_count > 0:
        result["recovery_status"] = "PARTIALLY_RECOVERED"
    else:
        result["recovery_status"] = "RECOVERY_FAILED"

    logger.info(
        "Drift recovery completed for %s: %d fixed, %d failed, status=%s",
        module_id,
        fixed_count,
        failed_count,
        result["recovery_status"],
    )
    return result


def _fallback_to_rollback_handler(event: Any) -> dict[str, Any]:
    """AutoFixer 修复失败时，尝试通过 DriftFixHandler 兜底回滚。"""
    try:
        from zephyr.infrastructure.rollback.drift_fix import DriftFixHandler

        handler = DriftFixHandler()
        return handler.on_drift_fix(event)
    except ImportError:
        try:
            from zephyr.governance.drift_detection.events import (
                ManagedDriftEvent as GovDriftEvent,
            )
            from zephyr.governance.drift_detection.events import (
                ManagedDriftState as GovDriftState,
            )
            from zephyr.governance.drift_detection.events import (
                DriftType,
            )

            gov_event = GovDriftEvent(
                drift_id=str(event.event_id),
                drift_type=DriftType.CODE_DIVERGENCE,
                state=GovDriftState.DETECTED,
                target=event.drift_dimension,
                auto_fixable=False,
            )
            gov_event.mark_manual_required()
            return {
                "drift_id": gov_event.drift_id,
                "action": "MANUAL_REQUIRED",
                "reason": "AutoFixer failed + DriftFixHandler unavailable",
            }
        except ImportError:
            return {
                "drift_id": str(event.event_id),
                "action": "MANUAL_REQUIRED",
                "reason": "AutoFixer failed + all fallback handlers unavailable",
            }
    except Exception as exc:
        return {
            "drift_id": str(event.event_id),
            "action": "FALLBACK_ERROR",
            "reason": str(exc),
        }
