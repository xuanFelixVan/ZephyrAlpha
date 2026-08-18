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
# [A_module] module_id=MOD-SEC-030 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: fix_completed事件 payload字典
#   fields: timestamp + source_function + severity + detail, 来自EventBusBackpressure总线
#   code: _on_fix_completed() payload L82
# 层: 算法
# - id: A1
#   name_zh: ① 幂等事件订阅
#   name_en: subscribe_eventbus
#   intro: 把fix_completed事件挂到背压事件总线上且重复调用安全
#   desc: _subscribed全局标志保证幂等; bus.subscribe("fix_completed", _on_fix_completed); 总线不可用静默跳过只记warning
#   inputs: I1
#   outputs: 事件订阅关系
#   invariant: subscribe is idempotent
# - id: A2
#   name_zh: ② 验证器懒加载单例
#   name_en: _get_validator
#   intro: 第一次用时才实例化RedBlueValidator并缓存
#   desc: _validator_instance全局缓存; 实例化失败记warning返回None不抛异常
#   inputs: I1
#   outputs: RedBlueValidator实例或None
# - id: A3
#   name_zh: ③ 修复完成事件处理
#   name_en: _on_fix_completed
#   intro: 收到修复完成事件就触发一轮对抗验证会话只记日志不回发事件
#   desc: 解析payload取source/detail; session_name=fix_validation_{source}; validator.run_adversarial_session(); 结果(session_id/scenarios/blocked/bypassed)记info日志; 全程吞异常不外抛
#   inputs: I1 A1 A2
#   outputs: 验证会话日志记录
#   invariant: handler never raises; 验证结果不发布事件避免循环
# 层: 输出
# - id: O1
#   name_zh: 对抗验证触发与日志
#   name_en: adversarial session log
#   intro: 修复后对抗验证会话的执行记录(session_id/场景数/拦截数/绕过数)
#   downstream: zephyr.trading.boot_hooks(启动时统一调用订阅); RedBlueValidator(执行验证)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A3
# A1 --> A3
# A2 --> A3
# I1 --> A1
# I1 --> A2
# A3 --> O1
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
        from zephyr.shared.event_bus import EventBusBackpressure

        bus = EventBusBackpressure()
        bus.subscribe("fix_completed", _on_fix_completed)
        _subscribed = True
        logger.info("ValidatorEventBridge: subscribed to fix_completed event")
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("ValidatorEventBridge: subscribe_eventbus failed: %s", e, exc_info=True)


def _get_validator() -> object:
    """懒加载 RedBlueValidator 单例。"""
    global _validator_instance
    if _validator_instance is None:
        try:
            from zephyr.security.adversarial_validation.validator import RedBlueValidator

            _validator_instance = RedBlueValidator()
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
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
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.error("ValidatorEventBridge: _on_fix_completed failed: %s", e, exc_info=True)
