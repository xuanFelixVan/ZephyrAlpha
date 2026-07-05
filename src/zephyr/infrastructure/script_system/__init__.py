# [A_module] module_id=MOD-INF_script_system | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain-governance/governance-automation/blueprint.md
# [MODULE] zephyr.infrastructure.script_system
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
from pathlib import Path

_script_system_root = Path(__file__).parent

# 5.136.1 修复: __all__ 移除已删除的 GateBridge/KBBridge 幽灵符号
__all__ = ["finding", "gate_bridge", "kb_bridge"]
