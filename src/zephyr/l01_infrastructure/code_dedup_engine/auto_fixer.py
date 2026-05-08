"""安全自动修复引擎——五直接开关+五间接约束."""
from __future__ import annotations

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
        if self.params.level == FixLevel.COMPLEX and similarity < 0.98:
            return False
        return True

    def fix(self, source: str, target: str, similarity: float, caller_count: int, blast_radius: int, is_grandfathered: bool) -> dict[str, Any]:
        if not self.can_fix(similarity, caller_count, blast_radius, is_grandfathered):
            return {"fixed": False, "reason": "safety_constraint_blocked", "source": source, "target": target}

        self.fix_count += 1
        return {"fixed": True, "source": source, "target": target, "similarity": similarity, "fix_count": self.fix_count}
