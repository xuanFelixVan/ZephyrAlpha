"""Log Anomaly Detector — v0.6.0 R61

Blindspot: Structured log anomalies invisible to metric-only detection.
Risk: R61 — Error log spikes undetected while CPU/memory look normal.
"""
from dataclasses import dataclass

@dataclass
class LogAnomaly:
    error_rate_threshold: float = 0.05

    def check(self, error_rate: float) -> bool:
        return error_rate > self.error_rate_threshold
