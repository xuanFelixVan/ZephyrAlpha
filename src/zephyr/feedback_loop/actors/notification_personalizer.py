"""Notification Personalizer — v0.6.0 R67

Blindspot: One-size-fits-all notifications; owner ignores irrelevant alerts.
Risk: R67 — Alert fatigue causes owner to miss critical notification.
"""
from dataclasses import dataclass

@dataclass
class NotificationPersonalizer:
    owner_preferences: dict = {}

    def personalize(self, alert: dict) -> dict:
        return {**alert, "personalized": True}
