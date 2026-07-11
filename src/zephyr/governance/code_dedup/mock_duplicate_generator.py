# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.mock_duplicate_generator
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/governance_misc/test_mock_duplicate_generator.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_mock_duplicate_generator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""可控克隆生产器——零假阳性可期待引擎分子离散"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DuplicateType(str, Enum):
    EXACT = "exact"
    RENAMED = "renamed"
    REORDERED = "reordered"
    WRAPPED = "wrapped"
    NEAR_MISS = "near_miss"
    MODERATE = "moderate"


@dataclass
class GeneratedDuplicate:
    original: str
    duplicate: str
    dup_type: DuplicateType
    path_a: str = ""
    path_b: str = ""


@dataclass
class MockDuplicateGenerator:
    output: list[GeneratedDuplicate] = field(default_factory=list)

    SEED = "def calculate(x: int) -> int:\n    return x * 2 + 1\n"

    def generate(self, dup_type: DuplicateType) -> GeneratedDuplicate:
        generators: dict[DuplicateType, Any] = {
            DuplicateType.EXACT: self._exact,
            DuplicateType.RENAMED: self._renamed,
            DuplicateType.REORDERED: self._reordered,
            DuplicateType.WRAPPED: self._wrapped,
            DuplicateType.NEAR_MISS: self._near_miss,
            DuplicateType.MODERATE: self._moderate,
        }
        gd = generators[dup_type]()
        self.output.append(gd)
        return gd

    def _exact(self) -> GeneratedDuplicate:
        return GeneratedDuplicate(original=self.SEED, duplicate=self.SEED, dup_type=DuplicateType.EXACT)

    def _renamed(self) -> GeneratedDuplicate:
        return GeneratedDuplicate(
            original=self.SEED,
            duplicate="def compute(val: int) -> int:\n    return val * 2 + 1\n",
            dup_type=DuplicateType.RENAMED,
        )

    def _reordered(self) -> GeneratedDuplicate:
        return GeneratedDuplicate(
            original="def foo():\n    a = 1\n    b = 2\n    return a + b\n",
            duplicate="def bar():\n    b = 2\n    a = 1\n    return a + b\n",
            dup_type=DuplicateType.REORDERED,
        )

    def _wrapped(self) -> GeneratedDuplicate:
        return GeneratedDuplicate(
            original=self.SEED,
            duplicate=f"def wrapper():\n{self._indent(self.SEED)}\n    return result\n",
            dup_type=DuplicateType.WRAPPED,
        )

    def _near_miss(self) -> GeneratedDuplicate:
        return GeneratedDuplicate(
            original=self.SEED,
            duplicate="def calculate(x: int) -> int:\n    return x * 2 + 2\n",
            dup_type=DuplicateType.NEAR_MISS,
        )

    def _moderate(self) -> GeneratedDuplicate:
        return GeneratedDuplicate(
            original="def is_even(n): return n % 2 == 0",
            duplicate="def is_odd(n): return not (n % 2 == 0)",
            dup_type=DuplicateType.MODERATE,
        )

    @staticmethod
    def _indent(text: str) -> str:
        return "\n".join(f"    {line}" for line in text.splitlines())
