# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md
# [MODULE] zephyr.feedback_loop.actors.alert_router
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.alert_dispatcher
# [CONSUMERS] zephyr.feedback_loop.actors
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] route() never raises; returns AlertRoutingDecision with channel list
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] route() returns empty channel list on unknown severity
# [TESTS] tests/feedback/test_actors_init.py
# [A_module] module_id=MOD-FBL-alert_router | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""alert_router.py — Severity-based alert channel router.

Routes AlertEvent instances to appropriate channels based on severity:
  - CRITICAL/HIGH: paging + immediate_notification
  - MEDIUM: slack + email_digest
  - LOW: log_only

Decouples alert production (alert_dispatcher) from alert consumption (channels).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

__all__ = [
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
# gov_drift.alert_router.AlertRouter (drift alert routing with silencing/dedup)
# and feedback_loop._gen_inherited.AlertRouter (auto-gen stub). Different
# routing concerns; no shadowing risk (consumers import from explicit paths).
# class-name-alias: FBL severity router vs gov_drift dedup router (ARCH-034)
class AlertRouter:
    """Route alerts to channels based on severity.

    Stateless — safe to use as a singleton or per-invocation.
    """

    def route(self, alert: Any) -> AlertRoutingDecision:
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
            else str(severity_attr).upper() if severity_attr is not None
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


def route(alert: Any) -> AlertRoutingDecision:
    """Module-level convenience: route an alert using a default AlertRouter."""
    return AlertRouter().route(alert)
