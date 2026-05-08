"""Trend-Cycle Separator — v0.9.0 R113

Blindspot: Long-term trends conflated with short-term anomalies.
Risk: R113 — Gradual trend growth triggers anomaly on otherwise healthy metric.
"""
from dataclasses import dataclass

@dataclass
class TrendCycleSeparator:

    def separate(self, time_series: list[float]) -> tuple[list[float], list[float]]:
        return ([], [])
