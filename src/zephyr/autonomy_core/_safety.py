# [A_module] module_id=MOD-ORC__safety | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-008 | docs/03_modules/_cross_layer/context-engine/blueprint.md
# [MODULE] zephyr.autonomy_core._safety
# [INVARIANTS] _SUBMODULES列表不变
# [MODIFY-GUARD] 新增子模块须同步更新__init__.py的__all__
# [CONSUMERS] zephyr.autonomy_core.__init__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_context_engine_imports.py

_SUBMODULES = [
    "adversarial_robustness",
    "alignment_scorer",
    "config_safety_guard",
    "integrity_check",
    "kill_switch",
    "poisoning_monitor",
    "sensitivity_classifier",
    "solo_dev_safety_net",
    "lsg_pattern_tracker",
    "diversity_constraint",
    "self_diagnosis",
    "verify_paths",
]
