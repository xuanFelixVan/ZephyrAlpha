"""Capacity Forecast — v0.13.0 R186b

Blindspot: Resource exhaustion predicted days in advance; no proactive alert.
"""
from dataclasses import dataclass

@dataclass
class CapacityForecast:
    days_until_full: float = float("inf")
