# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.security.security_decision
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] l10-compliance ; llm-security.protocol
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] enum members are frozen; no additions without ADR
# [MODIFY-GUARD] member changes require cross-package impact review
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] none
# [TESTS] tests/llm_security/test_fail_closed.py; tests/llm_security/test_gateway_e2e.py; tests/llm_security/test_l0_supply_chain.py; tests/llm_security/test_l1_input_defense.py; tests/llm_security/test_l2_prompt_protection.py  # 2026-09-05 STEWARD B20 重锚：AI-00 修复脚本 src. 前缀 bug 漏网（AST/patch 直查 10 个测试）
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
# [ALGO_FLOW] external: docs/03_modules/_domain_shared/algo_flow/contracts/security/security_decision.yaml
"""

from enum import Enum


class SecurityDecision(Enum):
    BLOCK = "block"
    ALLOW = "allow"
    DENY = "deny"
    FLAG = "flag"
