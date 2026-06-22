# [A_module] module_id=MOD-GOV_script_governance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-005 | data/databases/depgraph.db | D-GOV-SCRIPT_GOVERNANCE
# [MODULE] zephyr.governance.script_governance
# [INVARIANTS] subdomain_id=D-GOV-SCRIPT_GOVERNANCE; parent_domain=governance
# [MODIFY-GUARD] domain_migration_phase2
# [CONSUMERS] domain_migration_consumers
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError_on_missing_module
# [TESTS] tests/test_domain_structure.py
"""script_governance subdomain package — D-GOV-SCRIPT_GOVERNANCE."""

__all__ = []
