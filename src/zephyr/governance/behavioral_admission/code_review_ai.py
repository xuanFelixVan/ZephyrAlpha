# [BLUEPRINT] SRC-021 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.behavioral_admission.code_review_ai
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-GOV_code_review_ai | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
from enum import Enum


class ReviewLevel(str, Enum):
    L0_RUFF = "L0_ruff"
    L1_SECURITY = "L1_security"
    L2_LOGIC = "L2_logic"
    L3_ARCH = "L3_arch"
    L4_STRATEGY = "L4_strategy"
    L5_DUAL_AI = "L5_dual_ai"


REVIEW_TIMEOUTS: Final[dict[ReviewLevel, int]] = {
    ReviewLevel.L0_RUFF: 1,
    ReviewLevel.L1_SECURITY: 5,
    ReviewLevel.L2_LOGIC: 5,
    ReviewLevel.L3_ARCH: 30,
    ReviewLevel.L4_STRATEGY: 60,
    ReviewLevel.L5_DUAL_AI: 120,
}

REVIEW_RULES: Final[list[str]] = [
    "所有AI产出MUST通过L3",
    "模块部署前L3+L4完整审查",
    "黄金路径: AI自L2->AI同伴L3->Owner L4标志->终",
]
