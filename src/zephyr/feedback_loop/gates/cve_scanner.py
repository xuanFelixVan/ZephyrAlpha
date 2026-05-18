# [BLUEPRINT] MOD-INF-007 | 03_modules/_cross_layer/gate-engine/blueprint.md | §

# [MODULE] zephyr.feedback_loop.gates.cve_scanner

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""CVE Scanner — v0.8.0 R106

Blindspot: FLE dependencies accumulate CVEs without detection.
Risk: R106 — Known vulnerability exploited; FLE unaware.
"""
from dataclasses import dataclass, field

@dataclass
class CVEScanner:
    known_cves: list[str] = field(default_factory=list)

    def scan(self, dependency: str) -> list[str]:
        return [c for c in self.known_cves if dependency in c]
