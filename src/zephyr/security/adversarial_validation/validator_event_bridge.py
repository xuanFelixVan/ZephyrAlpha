# [BLUEPRINT] MOD-SEC-030 | docs/03_modules/_domain_security/red_blue_validator/blueprint.md | §
# [MODULE] zephyr.security.adversarial_validation.validator_event_bridge
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.shared.event_bus; zephyr.security.adversarial_validation.validator
# [CONSUMERS] zephyr.trading.boot_hooks
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] subscribe is idempotent; handler never raises; validator failure logged not propagated
# [MODIFY-GUARD] event topic names must be "fix_completed"
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] handler swallows all exceptions and logs; never raises during event dispatch
# [TESTS] tests/red_blue/test_validator_event_bridge.py
# [A_module] module_id=MOD-SEC_validator_event_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
ValidatorEventBridge — 红蓝验证器事件桥接 (MOD-SEC-030).

将 fix_completed 事件桥接到 RedBlueValidator，触发修复后的对抗验证会话。

职责:
  1. 订阅 EventBusBackpressure 的 fix_completed 事件
  2. 事件到达时调用 RedBlueValidator.run_adversarial_session() 验证修复
  3. 验证结果记录日志（不发布事件，避免循环）

用法:
    from zephyr.security.adversarial_validation.validator_event_bridge import (
        subscribe_eventbus,
    )
    subscribe_eventbus()  # 在 boot_hooks 中统一调用
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


# ── EventBusBackpressure 订阅 (DM-2507-G) ──────────────────────────────

_subscribed = False
_validator_instance: Any = None


def subscribe_eventbus() -> None:
    """订阅 EventBusBackpressure 的 fix_completed 事件。

    幂等：重复调用安全。Backpressure 总线不可用时静默跳过。
    供 boot_hooks 统一调用。
    """
    global _subscribed
    if _subscribed:
        return
    try:
        from zephyr.shared.events.event_bus import EventBusBackpressure

        bus = EventBusBackpressure()
        bus.subscribe("fix_completed", _on_fix_completed)
        _subscribed = True
        logger.info("ValidatorEventBridge: subscribed to fix_completed event")
    except Exception as e:
        logger.warning("ValidatorEventBridge: subscribe_eventbus failed: %s", e, exc_info=True)


def _get_validator() -> Any:
    """懒加载 RedBlueValidator 单例。"""
    global _validator_instance
    if _validator_instance is None:
        try:
            from zephyr.security.adversarial_validation.validator import RedBlueValidator

            _validator_instance = RedBlueValidator()
        except Exception as e:
            logger.warning("ValidatorEventBridge: failed to instantiate validator: %s", e, exc_info=True)
            return None
    return _validator_instance


def _on_fix_completed(payload: object) -> None:
    """fix_completed 事件：修复完成触发对抗验证。轻量handler。

    payload 期望字段: {timestamp, source_function, severity, detail}
    调用 RedBlueValidator.run_adversarial_session() 验证修复有效性。
    验证结果仅记录日志，不发布事件（避免循环）。
    """
    try:
        data = payload if isinstance(payload, dict) else {}
        detail = data.get("detail", str(payload))
        source = data.get("source_function", "unknown")
        logger.info(
            "ValidatorEventBridge: fix_completed event received "
            "(source=%s, detail=%s) — triggering adversarial validation",
            source,
            detail,
        )

        validator = _get_validator()
        if validator is None:
            logger.warning(
                "ValidatorEventBridge: validator unavailable, skip validation for '%s'",
                detail,
            )
            return

        session_name = f"fix_validation_{source}"
        report = validator.run_adversarial_session(session_name=session_name)
        logger.info(
            "ValidatorEventBridge: adversarial session completed "
            "(session_id=%s, scenarios=%s, blocked=%s, bypassed=%s)",
            getattr(report, "session_id", None),
            getattr(report, "total_scenarios", None),
            getattr(report, "blocked", None),
            getattr(report, "bypassed", None),
        )
    except Exception as e:
        logger.error("ValidatorEventBridge: _on_fix_completed failed: %s", e, exc_info=True)