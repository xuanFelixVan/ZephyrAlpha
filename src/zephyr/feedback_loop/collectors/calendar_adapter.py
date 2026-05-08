"""Calendar Adapter — v0.8.0 R102b

Blindspot: FLE operates same way during weekends as weekdays.
Risk: R102b — Weekend low-urgency repairs escalate unnecessarily.
"""
from dataclasses import dataclass

@dataclass
class CalendarAdapter:
    is_weekend: bool = False
