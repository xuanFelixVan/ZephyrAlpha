# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.integration.shared_08.contracts.sys_master_compliance
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES] zephyr.governance.rule_enforcement.sys_master_compliance
# [CONSUMERS] zephyr.governance.rule_enforcement;zephyr.infrastructure.rollback.phase_check_registry
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] SysMasterCompliance 真源在 zephyr.governance.rule_enforcement.sys_master_compliance;本文件仅作向后兼容re-export
# [MODIFY-GUARD] src/zephyr/gates/sys_master_compliance.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError on missing gates module
# [TESTS] tests/test_gates/
# [A_module] module_id=MOD-INT_sys_master_compliance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

from __future__ import annotations

from zephyr.governance.rule_enforcement.sys_master_compliance import SysMasterCompliance

__all__ = ["SysMasterCompliance"]
