# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md | §
# [MODULE] zephyr.governance.drift_detection.bridges.drift_bridge
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.event_bus; zephyr.governance.drift_detection.drift_engine
# [CONSUMERS] zephyr.trading.boot_hooks
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] subscribe is idempotent; handler never raises; drift_engine failure logged not propagated
# [MODIFY-GUARD] event topic names must be "gate_blocked" / "task_completed"
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] handler swallows all exceptions and logs; never raises during event dispatch
# [TESTS] tests/test_drift_bridge.py
# [A_module] module_id=MOD-GOV_drift_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
DriftBridge — 漂移检测器事件桥接 (MOD-INF-023).

将 gate_blocked / task_completed 事件桥接到 DriftEngine。
由于 drift_detector 模块本身是 frozen，在 bridge 层挂载订阅。

职责:
  1. 订阅 EventBusBackpressure 的 gate_blocked / task_completed 事件
  2. gate_blocked 事件到达时记录日志（可能触发手动漂移扫描）
  3. task_completed 事件到达时记录日志（用于漂移趋势分析）

用法:
    from zephyr.governance.drift_detection.bridges.drift_bridge import (
        subscribe_eventbus,
    )
    subscribe_eventbus()  # 在 boot_hooks 中统一调用
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


# ── EventBusBackpressure 订阅 (DM-2507-I) ──────────────────────────────

_subscribed = False


def subscribe_eventbus() -> None:
    """订阅 EventBusBackpressure 的 gate_blocked / task_completed 事件。

    幂等：重复调用安全。Backpressure 总线不可用时静默跳过。
    供 boot_hooks 统一调用。
    """
    global _subscribed
    if _subscribed:
        return
    try:
        from zephyr.shared.events.event_bus import EventBusBackpressure

        bus = EventBusBackpressure()
        bus.subscribe("gate_blocked", _on_gate_blocked)
        bus.subscribe("task_completed", _on_task_completed)
        _subscribed = True
        logger.info(
            "DriftBridge: subscribed to 2 events (gate_blocked/task_completed)"
        )
    except Exception as e:
        logger.warning("DriftBridge: subscribe_eventbus failed: %s", e, exc_info=True)


def _on_gate_blocked(payload: object) -> None:
    """gate_blocked 事件：门禁被阻断。轻量handler——仅日志记录。

    payload 期望字段: {timestamp, source_function, severity, detail}
    门禁阻断可能指示漂移，记录日志供后续手动触发漂移扫描。
    drift_engine 的 scan 需要 ScanResult 参数，无法从 payload 构造，
    因此不自动触发扫描（避免幻觉）。
    """
    try:
        data = payload if isinstance(payload, dict) else {}
        detail = data.get("detail", str(payload))
        source = data.get("source_function", "unknown")
        logger.warning(
            "DriftBridge: gate_blocked event (source=%s, detail=%s) — "
            "manual drift scan recommended",
            source,
            detail,
        )
    except Exception as e:
        logger.error("DriftBridge: _on_gate_blocked failed: %s", e, exc_info=True)


def _on_task_completed(payload: object) -> None:
    """task_completed 事件：任务完成。轻量handler——仅日志记录。

    payload 期望字段: {timestamp, source_function, severity, detail}
    任务完成事件用于漂移趋势分析，记录日志供后续审计。
    """
    try:
        data = payload if isinstance(payload, dict) else {}
        detail = data.get("detail", str(payload))
        source = data.get("source_function", "unknown")
        logger.info(
            "DriftBridge: task_completed event (source=%s, detail=%s) — "
            "recorded for drift trend analysis",
            source,
            detail,
        )
    except Exception as e:
        logger.error("DriftBridge: _on_task_completed failed: %s", e, exc_info=True)