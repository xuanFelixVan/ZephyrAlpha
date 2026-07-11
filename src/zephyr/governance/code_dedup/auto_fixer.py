# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.auto_fixer
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.governance.code_dedup.cli; tests/automation/test_auto_fixer.py; tests/governance/code_quality/test_code_dedup_engine.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_auto_fixer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""安全自动修复引擎——五直接开关+五间接约束."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SafetyTier(str, Enum):
    ALWAYS = "always"
    REVIEW = "review"
    NEVER = "never"


class FixLevel(str, Enum):
    TRIVIAL = "trivial"
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


@dataclass
class FixParams:
    safety_tier: SafetyTier = SafetyTier.ALWAYS
    level: FixLevel = FixLevel.SIMPLE
    caller_count: int = 7
    blast_radius: int = 50
    grandfather: bool = False


@dataclass
class AutoFixer:
    params: FixParams = field(default_factory=FixParams)
    fix_count: int = 0

    def can_fix(self, similarity: float, caller_count: int, blast_radius: int, is_grandfathered: bool) -> bool:
        if self.params.grandfather and is_grandfathered:
            return False
        if caller_count > self.params.caller_count:
            return False
        if blast_radius > self.params.blast_radius:
            return False
        if self.params.level is FixLevel.COMPLEX and similarity < 0.98:
            return False
        return True

    def fix(
        self, source: str, target: str, similarity: float, caller_count: int, blast_radius: int, is_grandfathered: bool
    ) -> dict[str, Any]:
        if not self.can_fix(similarity, caller_count, blast_radius, is_grandfathered):
            return {"fixed": False, "reason": "safety_constraint_blocked", "source": source, "target": target}

        self.fix_count += 1
        return {
            "fixed": True,
            "source": source,
            "target": target,
            "similarity": similarity,
            "fix_count": self.fix_count,
        }
