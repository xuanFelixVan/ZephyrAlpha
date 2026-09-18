# [A_module] module_id=MOD-INF-script_system | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md
# [MODULE] zephyr.infrastructure.script_system
# [DOMAIN] D_INFRA_RUNTIME
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""


# [ALGO_FLOW] external: docs/03_modules/_domain_infrastructure/algo_flow/script_system/script_system__init__.yaml
"""

from pathlib import Path

_script_system_root = Path(__file__).parent

# 5.136.1 修复: __all__ 移除已删除的 GateBridge/KBBridge 幽灵符号
__all__ = ["finding", "gate_bridge"]
