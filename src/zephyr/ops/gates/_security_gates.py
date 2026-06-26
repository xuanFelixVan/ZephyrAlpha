# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.observability.feedback_loop.gates._security_gates
# [DOMAIN] D-OPS
# [DEPENDENCIES] zephyr.ops.gates.__init__
# [CONSUMERS] zephyr.observability.feedback_loop.gates.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] backward_compat: all exports must remain available from feedback-loop.gates
# [MODIFY-GUARD] zephyr.observability.feedback_loop.gates.__init__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "import zephyr.ops.gates"
# [A_module] module_id=MOD-UNK__security_gates | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

SUBMODULES = [
    "adversarial_validation",
    "ci_cd_pre_scanner",
    "concurrent_change_deconfliction",
    "cve_scanner",
    "deployment_suppression",
    "emergency_takeover",
    "federated_security",
    "license_compliance",
    "merkle_audit_root",
]
