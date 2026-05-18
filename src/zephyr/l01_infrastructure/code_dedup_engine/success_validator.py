# [BLUEPRINT] MOD-INF-017 | 03_modules/l01_infrastructure/code-dedup-engine/blueprint.md | §

# [MODULE] zephyr.l01_infrastructure.code_dedup_engine.success_validator

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""成功验证——判断一次去重操作是否真正消灭了克隆."""
from __future__ import annotations

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
            detail=f"{before_count}→{after_count} clones" if success else "clone count increased or unchanged",
        )
        self.results.append(result)
        return result

    def summary(self) -> dict[str, Any]:
        total = len(self.results)
        success_count = sum(1 for r in self.results if r.success)
        return {"total_fixes": total, "successful": success_count, "failed": total - success_count, "success_rate": success_count / max(total, 1)}
