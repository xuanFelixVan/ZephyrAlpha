"""Autoscale Remediation — v0.13.0 R174

Blindspot: Static resource allocation causes capacity-related anomalies.
Risk: R174 — Load spike; FLE diagnoses instead of autoscaling.
"""
from dataclasses import dataclass

@dataclass
class AutoscaleRemediation:
    scale_up_threshold: float = 0.8
