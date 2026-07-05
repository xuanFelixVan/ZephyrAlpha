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

__all__ = ["GateBridge", "KBBridge", "finding", "gate_bridge", "kb_bridge"]

# MIGRATED: from zephyr.infrastructure.script_system.gate_bridge import GateBridge, submit_to_gate  # removed by TC-7-2
# MIGRATED: from zephyr.infrastructure.script_system.kb_bridge import KBBridge, publish_to_kb  # removed by TC-7-2
