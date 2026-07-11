# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.governance.rule_enforcement.gate_engine.__init__
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES]
# [CONSUMERS] zephyr.governance.rule_enforcement 内部模块
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 包聚合 gate_* 引擎实现 + check_type handler 函数（_handle_* 在 gate_engine.py _CHECK_DISPATCH 注册）
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
5.176.1 Phase 2/3 治本后，check_type handler 函数（_handle_*）已内联到 gate_engine.py 的 _CHECK_DISPATCH 分发表；
check_types/ 包（ct_*.py + check_type_registry.py）已删除（5.176.3 死代码清理）。
"""
