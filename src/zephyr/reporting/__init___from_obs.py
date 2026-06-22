# [A_module] module_id=MOD-UNK_asset_inventory | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-026 | data/databases/depgraph.db | D-OBS-ASSET_INVENTORY
# [MODULE] zephyr.observability.asset_inventory
# [INVARIANTS] subdomain_id=D-OBS-ASSET_INVENTORY; parent_domain=observability
# [MODIFY-GUARD] domain_migration_phase2
# [CONSUMERS] domain_migration_consumers
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError_on_missing_module
# [TESTS] tests/test_domain_structure.py
"""asset-inventory subdomain package — D-OBS-ASSET_INVENTORY."""

__all__ = []
