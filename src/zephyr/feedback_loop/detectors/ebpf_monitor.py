"""eBPF Monitor — v0.6.0 R64

Blindspot: Kernel-level anomalies invisible to userspace collectors.
Risk: R64 — Kernel bottleneck causes application anomaly; misdiagnosed as app bug.
"""
from dataclasses import dataclass

@dataclass
class EBPFMonitor:
    enabled: bool = False
