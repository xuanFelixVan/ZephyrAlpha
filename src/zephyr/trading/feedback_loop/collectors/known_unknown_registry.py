# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.collectors.known_unknown_registry
# [DOMAIN] D_OPS
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
# [A_module] module_id=MOD-UNK_known_unknown_registry | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""Known-Unknown Registry — v0.16.0 R229

Blindspot: FLE unconscious of its own blindspots; "unknown unknowns" accumulate silently.
Risk: R229 — FLE overconfident in domains it has never been validated against.

Mitigation: "I know what I don't know" registry—explicit blindspot catalog with confidence calibration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class KnownUnknownState(str, Enum):
    OPEN = "OPEN"
    MITIGATED = "MITIGATED"
    ACCEPTED = "ACCEPTED"


@dataclass
class KnownUnknown:
    id: str
    domain: str
    description: str
    state: KnownUnknownState = KnownUnknownState.OPEN
    last_reviewed: str = ""


@dataclass
class KnownUnknownRegistry:
    items: list[KnownUnknown] = field(default_factory=list)

    def register(self, id: str, domain: str, description: str) -> KnownUnknown:
        item = KnownUnknown(id=id, domain=domain, description=description)
        self.items.append(item)
        return item

    def open_count(self) -> int:
        return sum(1 for i in self.items if i.state is KnownUnknownState.OPEN)

    def by_domain(self, domain: str) -> list[KnownUnknown]:
        return [i for i in self.items if i.domain == domain]
