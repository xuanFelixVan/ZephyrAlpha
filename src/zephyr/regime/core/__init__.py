# [BLUEPRINT] MOD-REGIME-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_module] module_id=PKG-regime-core | layer=package | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D_REGIME 域核心包 — regime 检测器核心实现。"""

from zephyr.regime.core.regime_detector import (
    RegimeDetector,
    RegimeProbabilities,
    RegimeSnapshot,
    ShrinkageResult,
    TransitionTriggered,
)

__all__ = [
    "RegimeDetector",
    "RegimeProbabilities",
    "ShrinkageResult",
    "TransitionTriggered",
    "RegimeSnapshot",
]
