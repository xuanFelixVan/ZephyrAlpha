# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.mock_duplicate_generator
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/governance_misc/test_mock_duplicate_generator.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-017 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
可控克隆生产器——零假阳性可期待引擎分子离散

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: mock_duplicate_generator.py
# 层: 算法
# - id: A1
#   name_zh: ① MockDuplicateGenerator
#   name_en: MockDuplicateGenerator
#   intro: class MockDuplicateGenerator 源码 L73-L131
#   desc: 公共方法（定义序）: generate；源码 L73-L131
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: MockDuplicateGenerator
#   downstream: tests/governance/governance_misc/test_mock_duplicate_generator.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

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
