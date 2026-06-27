# [A_module] module_id=MOD-INT_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/contracts_blueprint.md
# [MODULE] zephyr.integration.shared_08.contracts.gate
# [INVARIANTS] re-export shim package; truth source is zephyr.governance.rule_enforcement.gate_types
# [MODIFY-GUARD] truth source MUST NOT be modified here; changes go to zephyr.governance.rule_enforcement.gate_types
# [CONSUMERS] legacy imports via integration.shared_08.contracts
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "import zephyr.integration.shared_08.contracts.gate"
# [TTL] task_bound

__all__ = [
    "gate_result",
]
