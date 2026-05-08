"""Notification Feedback — v0.9.0 R118

Blindspot: Owner response to notifications not tracked.
Risk: R118 — No feedback loop from notification to diagnosis quality.
"""
from dataclasses import dataclass, field

@dataclass
class NotificationFeedback:
    responses: list[dict] = field(default_factory=list)

    def record(self, notification_id: str, owner_action: str) -> None:
        self.responses.append({"id": notification_id, "action": owner_action})
