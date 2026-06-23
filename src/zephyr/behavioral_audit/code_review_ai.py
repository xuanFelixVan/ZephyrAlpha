# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain-governance/drift-detector/blueprint.md
# [MODULE] zephyr.behavioral_audit.code_review_ai
# [DOMAIN] D-BEHAVIORAL_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] MOD-INF-007;MOD-INF-021;MOD-INF-020
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Git-native漂移检测;自动对账;漂移预算
# [MODIFY-GUARD] docs/03_modules/_domain-governance/drift-detector/blueprint.md;src/zephyr/behavioral-auditor/__init__.py
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/test_behavioral_auditor/
# [A_module] module_id=MOD-SEC_code_review_ai | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

from __future__ import annotations

from enum import Enum


class ReviewLevel(str, Enum):
    L0_RUFF = "L0_ruff"
    L1_SECURITY = "L1_security"
    L2_LOGIC = "L2_logic"
    L3_ARCH = "L3_arch"
    L4_STRATEGY = "L4_strategy"
    L5_DUAL_AI = "L5_dual_ai"


REVIEW_TIMEOUTS: dict[ReviewLevel, int] = {
    ReviewLevel.L0_RUFF: 1,
    ReviewLevel.L1_SECURITY: 5,
    ReviewLevel.L2_LOGIC: 5,
    ReviewLevel.L3_ARCH: 30,
    ReviewLevel.L4_STRATEGY: 60,
    ReviewLevel.L5_DUAL_AI: 120,
}

REVIEW_RULES: list[str] = [
    "所有AI产出MUST通过L3",
    "模块部署前L3+L4完整审查",
    "黄金路径: AI自L2→AI同伴L3→Owner L4标志→终",
]
