# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context-engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.ce_vibe_shortcuts
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-CONTEXT_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""ce_vibe_shortcuts.py — Vibe/Strict 模式切换 (TASK-016)"""

from dataclasses import dataclass
from enum import Enum


class CEMode(Enum):
    VIBE = "vibe"
    STRICT = "strict"


@dataclass
class ModeConfig:
    mode: CEMode
    top_k: int
    similarity_threshold: float


_MODE_CONFIGS: dict[CEMode, ModeConfig] = {
    CEMode.VIBE: ModeConfig(mode=CEMode.VIBE, top_k=8, similarity_threshold=0.6),
    CEMode.STRICT: ModeConfig(mode=CEMode.STRICT, top_k=3, similarity_threshold=0.8),
}


def ce_vibe() -> ModeConfig:
    """Switch to vibe mode: expand top_k + lower threshold."""
    return _MODE_CONFIGS[CEMode.VIBE]


def ce_strict() -> ModeConfig:
    """Switch to strict mode: restore conservative params."""
    return _MODE_CONFIGS[CEMode.STRICT]
