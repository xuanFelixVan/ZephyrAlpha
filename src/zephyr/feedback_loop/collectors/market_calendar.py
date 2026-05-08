"""Market Calendar — v0.5.0 R48

Blindspot: FLE unaware of market holidays; diagnoses no-data as pipeline failure.
Risk: R48 — Holiday false alarms erode trust in FLE.
"""
from dataclasses import dataclass, field

@dataclass
class MarketCalendar:
    holidays: set[str] = field(default_factory=set)

    def is_trading_day(self, date_str: str) -> bool:
        return date_str not in self.holidays
