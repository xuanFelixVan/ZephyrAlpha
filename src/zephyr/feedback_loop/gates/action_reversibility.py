# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.feedback_loop.gates.action_reversibility
# [DOMAIN] D_FBL_VERIFICATION
# [DEPENDENCIES] zephyr.feedback_loop.gates.__init__
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
# [A_module] module_id=MOD-UNK_action_reversibility | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Action Reversibility — v0.15.0 R208

Blindspot: Some repairs irreversible; FLE executes without reversible-path verification.
Risk: R208 — "DELETE FROM production" executed; no undo possible because irreversibility un-checked.

Mitigation: Action reversibility gate—all destructive actions require verified rollback path.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Reversibility(str, Enum):
    FULLY_REVERSIBLE = "FULLY_REVERSIBLE"
    PARTIALLY_REVERSIBLE = "PARTIALLY_REVERSIBLE"
    IRREVERSIBLE = "IRREVERSIBLE"
    UNKNOWN = "UNKNOWN"


@dataclass
class ActionReversibility:
    blocked_actions: list[str] = field(default_factory=list)

    def classify(self, action: str, has_rollback: bool, has_snapshot: bool) -> Reversibility:
        if has_snapshot and has_rollback:
            return Reversibility.FULLY_REVERSIBLE
        if has_snapshot or has_rollback:
            return Reversibility.PARTIALLY_REVERSIBLE
        return Reversibility.IRREVERSIBLE

    def gate(self, action: str, reversibility: Reversibility, autonomy_level: int) -> bool:
        if reversibility is Reversibility.IRREVERSIBLE and autonomy_level < 3:
            self.blocked_actions.append(action)
            return False
        return True
