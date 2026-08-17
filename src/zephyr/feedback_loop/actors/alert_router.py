# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md
# [MODULE] zephyr.feedback_loop.actors.alert_router
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.alert_dispatcher
# [CONSUMERS] zephyr.feedback_loop.actors
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] route() never raises; returns AlertRoutingDecision with channel list
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] route() returns empty channel list on unknown severity
# [TESTS] tests/feedback/test_actors_init.py
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

alert_router.py — Severity-based alert channel router.

Routes AlertEvent instances to appropriate channels based on severity:
  - CRITICAL/HIGH: paging + immediate_notification
  - MEDIUM: slack + email_digest
  - LOW: log_only

Decouples alert production (alert_dispatcher) from alert consumption (channels).

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 告警事件 AlertEvent
#   fields: event_id + severity（枚举或字符串均可，duck-typing 读取）
#   code: alert_router.py L85 route(alert) 参数
# 层: 算法
# - id: A1
#   name_zh: ① 严重度归一化
#   name_en: severity normalize（AlertRouter.route 内联）
#   intro: 不管severity是枚举还是字符串，统一掰成全大写字符串，缺了算UNKNOWN
#   desc: 有.value取枚举值；否则str().upper()；None→"UNKNOWN"（alert_router.py L91-99）
#   inputs: I1
#   outputs: severity 大写字符串
# - id: A2
#   name_zh: ② 严重度渠道映射路由
#   name_en: AlertRouter.route
#   intro: 按严重度查表分渠道：危重呼叫+即推，中档slack+邮件，低档只记日志
#   desc: _SEVERITY_CHANNELS 查表：CRITICAL/HIGH→paging+immediate_notification；MEDIUM→slack+email_digest；LOW/INFO→log_only；未知→空渠道+routed=False+warning日志（L54-60, L100-115）
#   inputs: A1
#   outputs: AlertRoutingDecision（channels/routed/reason）
#   invariant: route() never raises；未知severity返回空渠道列表 routed=False
# 层: 输出
# - id: O1
#   name_zh: 告警路由决策 AlertRoutingDecision
#   name_en: alert routing decision
#   intro: 一条告警该发往哪些渠道的结论，带没路由上的原因
#   downstream: alert_dispatcher.route_alert 同模块 MOD-FEEDBACK_LOOP 内部；终端渠道 paging/slack/email_digest/log_only
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

__all__ = [  # noqa: n114-final  n114-final豁免: __all__是Python导出约定且本文件运行时动态append，Final标注不适用
    "AlertChannel",
    "AlertRoutingDecision",
    "AlertRouter",
    "route",
]


class AlertChannel:
    """Named channel constants for alert routing."""

    PAGING = "paging"
    IMMEDIATE_NOTIFICATION = "immediate_notification"
    SLACK = "slack"
    EMAIL_DIGEST = "email_digest"
    LOG_ONLY = "log_only"


# Severity → channels mapping. CRITICAL/HIGH get paging+immediate;
# MEDIUM gets slack+email; LOW gets log only.
_SEVERITY_CHANNELS: dict[str, list[str]] = {
    "CRITICAL": [AlertChannel.PAGING, AlertChannel.IMMEDIATE_NOTIFICATION],
    "HIGH": [AlertChannel.PAGING, AlertChannel.IMMEDIATE_NOTIFICATION],
    "MEDIUM": [AlertChannel.SLACK, AlertChannel.EMAIL_DIGEST],
    "LOW": [AlertChannel.LOG_ONLY],
    "INFO": [AlertChannel.LOG_ONLY],
}


@dataclass
class AlertRoutingDecision:
    """Result of routing an alert — which channels should receive it."""

    event_id: str
    severity: str
    channels: list[str] = field(default_factory=list)
    routed: bool = False
    reason: str = ""


# severity-based alert channel router (feedback_loop.actors), distinct from
# gov_drift.alert_router.AlertRouter (drift alert routing with silencing/dedup).
# Different routing concerns; no shadowing risk (consumers import from explicit paths).
# class-name-alias: FBL severity router vs gov_drift dedup router (ARCH-034)
class AlertRouter:
    """Route alerts to channels based on severity.

    Stateless — safe to use as a singleton or per-invocation.
    """

    def route(self, alert: object) -> AlertRoutingDecision:
        """Route an alert to channels based on its severity.

        Never raises; unknown severity returns empty channel list with
        `routed=False` and a reason string.
        """
        event_id = getattr(alert, "event_id", "unknown")
        severity_attr = getattr(alert, "severity", None)
        # Handle both enum and string severities
        severity = (
            severity_attr.value
            if hasattr(severity_attr, "value")
            else str(severity_attr).upper()
            if severity_attr is not None
            else "UNKNOWN"
        )
        channels = _SEVERITY_CHANNELS.get(severity)
        if channels is None:
            logger.warning("AlertRouter: unknown severity %r for event %s", severity, event_id)
            return AlertRoutingDecision(
                event_id=event_id,
                severity=severity,
                channels=[],
                routed=False,
                reason=f"unknown severity: {severity}",
            )
        return AlertRoutingDecision(
            event_id=event_id,
            severity=severity,
            channels=list(channels),
            routed=True,
        )


def route(alert: object) -> AlertRoutingDecision:
    """Module-level convenience: route an alert using a default AlertRouter."""
    return AlertRouter().route(alert)
