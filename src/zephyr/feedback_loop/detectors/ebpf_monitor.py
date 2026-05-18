# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.detectors.ebpf_monitor

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""eBPF Monitor — v0.6.0 R64

Blindspot: Kernel-level anomalies invisible to userspace collectors.
Risk: R64 — Kernel bottleneck causes application anomaly; misdiagnosed as app bug.
"""
from dataclasses import dataclass

@dataclass
class EBPFMonitor:
    enabled: bool = False
