# [BLUEPRINT] MOD-INF-035 | 03_modules/_cross_layer/auto-runtime-core/blueprint.md | §

# [MODULE] zephyr.orchestrator.stability_guard

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""API 稳定性守护（CT-STABILITY）——public API签名锁+breaking change检测。"""

from __future__ import annotations

class StabilityGuard:
    def lock_api(self, module: str, exports: list[str]) -> dict:
        return {"module": module, "exports": exports, "locked": True}

    def check_breaking(self, old_exports: list[str], new_exports: list[str]) -> list[str]:
        removed = set(old_exports) - set(new_exports)
        return [f"BREAKING: {e} removed" for e in removed]
