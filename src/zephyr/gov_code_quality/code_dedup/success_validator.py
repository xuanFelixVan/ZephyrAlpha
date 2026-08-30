# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.success_validator
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/ops/test_success_validator.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-017 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
成功验证——判断一次去重操作是否真正消灭了克隆.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: success_validator.py
# 层: 算法
# - id: A1
#   name_zh: ① SuccessValidator
#   name_en: SuccessValidator
#   intro: class SuccessValidator 源码 L66-L96
#   desc: 公共方法（定义序）: validate, summary；源码 L66-L96
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: SuccessValidator
#   downstream: tests/governance/ops/test_success_validator.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValidationResult:
    fix_id: str
    timestamp: str
    clone_before_count: int
    clone_after_count: int
    success: bool
    new_clones_introduced: int = 0
    metrics_improved: bool = False
    detail: str = ""


@dataclass
class SuccessValidator:
    results: list[ValidationResult] = field(default_factory=list)
    min_reduction_pct: float = 100.0

    def validate(self, fix_id: str, before_count: int, after_count: int) -> ValidationResult:
        success = after_count < before_count
        new_clones = max(0, after_count - before_count)
        improved = after_count == 0 and before_count > 0

        result = ValidationResult(
            fix_id=fix_id,
            timestamp=__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
            clone_before_count=before_count,
            clone_after_count=after_count,
            success=success,
            new_clones_introduced=new_clones,
            metrics_improved=improved,
            detail=f"{before_count}->{after_count} clones" if success else "clone count increased or unchanged",
        )
        self.results.append(result)
        return result

    def summary(self) -> dict[str, Any]:
        total = len(self.results)
        success_count = sum(1 for r in self.results if r.success)
        return {
            "total_fixes": total,
            "successful": success_count,
            "failed": total - success_count,
            "success_rate": success_count / max(total, 1),
        }
