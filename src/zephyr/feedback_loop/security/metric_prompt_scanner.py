# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.security.metric_prompt_scanner
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SEC_metric_prompt_scanner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Metric-Prompt Scanner — v0.15.0 R215

Blindspot: Metric values injected directly into LLM prompts; prompt injection via metric poison.
Risk: R215 — Attacker poisons metric value "ignore all previous instructions"; FLE executes.

Mitigation: Pre-LLM scan of all metric values for prompt injection patterns.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ScanResult:
    metric: str
    value: str
    suspicious: bool
    pattern_matched: str = ""


@dataclass
class MetricPromptScanner:
    patterns: list[str] = field(
        default_factory=lambda: [
            "ignore previous",
            "ignore all",
            "system prompt:",
            "you are now",
            "new instructions:",
            "your new task is",
        ]
    )

    def scan(self, metric_name: str, value: str) -> ScanResult:
        value_lower = value.lower()
        for pattern in self.patterns:
            if pattern.lower() in value_lower:
                return ScanResult(metric=metric_name, value=value, suspicious=True, pattern_matched=pattern)
        return ScanResult(metric=metric_name, value=value, suspicious=False)
