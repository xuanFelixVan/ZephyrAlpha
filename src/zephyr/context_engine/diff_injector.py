# [BLUEPRINT] MOD-INF-008 | 03_modules/_cross_layer/context-engine/blueprint.md | §

# [MODULE] zephyr.context_engine.diff_injector

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""diff_injector.py — 增量注入 (DD98, TASK-019)"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class DiffResult:
    prefix_tokens: int
    suffix_tokens: int
    diff_tokens: int
    compressed: bool


class DiffInjector:
    """Continuous session: 设定 prefix_size=1000, 后续注入 diff (DD98)."""
    def inject_diff(self, prev_context: str, new_context: str) -> DiffResult:
        return DiffResult(prefix_tokens=len(prev_context), suffix_tokens=len(new_context), diff_tokens=len(new_context) - len(prev_context), compressed=False)
