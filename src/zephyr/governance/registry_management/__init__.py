# [A_module] module_id=MOD-GOV_registry_management | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-037 | src/zephyr/governance/registry_management/__init__.py | D_GOV_REGISTRY_MANAGEMENT
# [MODULE] zephyr.governance.registry_management
# [INVARIANTS] subdomain_id=D_GOV_REGISTRY_MANAGEMENT; parent_domain=governance
# [MODIFY-GUARD] domain_migration_phase2
# [CONSUMERS] domain_migration_consumers
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ImportError_on_missing_module
# [TESTS] tests/test_domain_structure.py
# [TTL] task_bound
"""registry_management subdomain package — D_GOV_REGISTRY_MANAGEMENT."""

__all__ = []
