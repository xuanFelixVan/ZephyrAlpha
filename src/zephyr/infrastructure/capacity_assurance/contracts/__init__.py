# [A_module] module_id=MOD-INF-contracts | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infrastructure_operations/capacity_assurance/blueprint.md
# [MODULE] zephyr.infrastructure.capacity_assurance.contracts
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
capacity-assurance contracts — ContractBus 44条契约 Pydantic v2 Schema Enforcement.

# [ALGO_FLOW] external: docs/03_modules/_domain_infrastructure/algo_flow/capacity_assurance/contracts/contracts__init__.yaml
"""

from zephyr.infrastructure.capacity_assurance.contracts.contract_bus import ContractBusLoader

__all__ = ["ContractBusLoader", "batch1_infra", "batch2_governance", "batch3_integration", "contract_bus"]
