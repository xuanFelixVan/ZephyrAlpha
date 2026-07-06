# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.security_governance.persuasion_detector
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 心理说服检测不可禁用;Cialdini六原则必须覆盖
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_persuasion_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Persuasion Detector — D-022-09 心理说服检测: 对抗语气+恳求+绕过指令。
"""

from __future__ import annotations

from typing import Final
SUSPICIOUS_PATTERNS: Final[list] = [
    "please",
    "urgent",
    "trust me",
    "you must",
    "override",
    "bypass",
    "ignore rules",
    "just this once",
    "don't escalate",
]


class PersuasionDetector:
    def detect(self, text: str) -> tuple[bool, list[str]]:
        found = [p for p in SUSPICIOUS_PATTERNS if p.lower() in text.lower()]
        return len(found) > 0, found

    def score(self, text: str) -> float:
        _, found = self.detect(text)
        return min(1.0, len(found) / len(SUSPICIOUS_PATTERNS))
