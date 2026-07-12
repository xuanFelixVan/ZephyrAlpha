# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.success_validator
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/ops/test_success_validator.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GCQ_success_validator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""成功验证——判断一次去重操作是否真正消灭了克隆."""

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
