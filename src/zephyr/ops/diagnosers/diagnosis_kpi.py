# [A_module] module_id=MOD-UNK_diagnosis_kpi | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-010 | docs/03_modules/_cross_layer/feedback-loop/blueprint.md

# [MODULE] zephyr.observability.feedback_loop.diagnosers.diagnosis_kpi

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Diagnosis KPI — v0.9.0 R116

Blindspot: No metrics on how often diagnoses lead to effective repairs.
Risk: R116 — Broken diagnosis pipeline invisible — repair feedback loop severed.
"""

from dataclasses import dataclass


@dataclass
class DiagnosisKPI:
    total: int = 0
    effective: int = 0

    @property
    def effectiveness_rate(self) -> float:
        return self.effective / max(self.total, 1)
