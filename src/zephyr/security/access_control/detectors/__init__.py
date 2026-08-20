# [BLUEPRINT] MOD-INF-018 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_module] module_id=MOD-SEC-detectors | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# Package marker for *_detector.py modules (ARCH-035 suffix-based grouping)

from typing import Final

__all__: Final = [
    "anomaly_detector",
    "context_drift_detector",
    "cross_session_detector",
    "false_completion_detector",
    "multi_agent_collusion_detector",
    "shell_dialect_detector",
]
