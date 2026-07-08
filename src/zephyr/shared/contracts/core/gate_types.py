# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §
# [MODULE] zephyr.shared.contracts.core.gate_types
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] backward-compat shim — canonical location is zephyr.governance.rule_enforcement.gate_types
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_gate_types | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# Lazy import to avoid circular dependency deadlock:
# shared.contracts -> governance.rule_enforcement -> governance.__init__ -> ... -> governance (cycle)
# At module load time, governance may not be fully initialized yet.
def __getattr__(name):
    _mod = __import__("zephyr.governance.rule_enforcement.gate_types", fromlist=[name])
    return getattr(_mod, name)
