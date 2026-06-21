# [A_module] module_id=MOD-ORC_diff_injector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-008 | docs/03_modules/_cross_layer/context-engine/blueprint.md

# [MODULE] zephyr.autonomy_core.diff_injector

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""diff_injector.py — 增量注入 (DD98, TASK-019)"""

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
