# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.governance.rule_enforcement.gate_engine.gate_engine.__init__
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES]
# [CONSUMERS] zephyr.governance.rule_enforcement 内部模块
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 包仅聚合 gate_* 引擎实现；handler 仍在 check_types/（ct_* 前缀）
# [MODIFY-GUARD] blueprint.md; _registry.yaml
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] —
# [TESTS] tests/governance/rule_enforcement/
# [A_module] module_id=MOD-GOV_gate_engine | layer=package | stability=stable | safety=L | ai_autonomy=human_gated
# [TTL] permanent
"""gate_engine package — 门禁引擎模块集合（ARCH-042 阶段1 拆分产物）。

归并 gate_* 系列 + adversarial_validation 实现，从 rule_enforcement/ 根迁入。
本包仅含引擎实现；check type handler 仍在 check_types/（ct_* 前缀）。
"""
