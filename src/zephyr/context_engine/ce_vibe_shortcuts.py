# [BLUEPRINT] MOD-INF-008 | 03_modules/_cross_layer/context-engine/blueprint.md | §

# [MODULE] zephyr.context_engine.ce_vibe_shortcuts

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""ce_vibe_shortcuts.py — Vibe/Strict 模式切换 (TASK-016)"""
from __future__ import annotations
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
