# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.gates.cve_scanner
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.trading.feedback_loop.gates.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_cve_scanner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

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
