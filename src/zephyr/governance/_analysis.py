# [A_module] module_id=MOD-UNK__analysis | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain-governance/code-dedup-engine/blueprint.md
# [MODULE] zephyr.testing.code_dedup._analysis
# [INVARIANTS] backward_compat: all exports must remain available from code_dedup_engine
# [MODIFY-GUARD] zephyr.testing.code_dedup.__init__
# [CONSUMERS] zephyr.testing.code_dedup.__init__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "import zephyr.testing.code_dedup"

SUBMODULES = [
    'behavioral_trust_checker',
    'blind_spot_tracker',
    'consequence_tracker',
    'contract_consistency_checker',
    'cross_boundary_detector',
    'doom_loop_guard',
    'extraction_safety',
    'fifteen_dimension_auditor',
    'hotspot_tracker',
    'import_surface_tracker',
    'observation_window_guard',
    'policy_tree_validator',
    'pre_apply_integrity_gate',
    'question_tracker',
    'risk_mitigation_tracker',
    'risk_mitigator',
    'shadow_trust_validator',
    'shadow_verifier',
    'stale_shared_detector',
    'temporal_drift_tracker',
    'thematic_clusterer',
    'verifier',
]
