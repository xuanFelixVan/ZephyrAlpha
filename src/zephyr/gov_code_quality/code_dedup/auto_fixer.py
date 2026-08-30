# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.auto_fixer
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.gov_code_quality.code_dedup.cli; tests/automation/test_auto_fixer.py; tests/governance/code_quality/test_code_dedup_engine.py
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
安全自动修复引擎——五直接开关+五间接约束.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: auto_fixer.py
# 层: 算法
# - id: A1
#   name_zh: ① AutoFixer
#   name_en: AutoFixer
#   intro: class AutoFixer 源码 L77-L105
#   desc: 公共方法（定义序）: can_fix, fix；源码 L77-L105
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: AutoFixer
#   downstream: zephyr.gov_code_quality.code_dedup.cli; tests/automation/test_auto_fixer.py; te…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

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
