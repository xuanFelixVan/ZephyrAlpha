# [BLUEPRINT] MOD-RULE_ENGINE | docs/03_modules/_cross_layer/rule-engine/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.rule_engine.__init__
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES]
# [CONSUMERS] zephyr.gov_enforcement.rule_enforcement 内部模块
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 包仅聚合 rule_* 引擎实现（rule_engine/rule_canary_manager/rule_debt_auditor/rule_shadow_runner/rule_watcher）
# [MODIFY-GUARD] blueprint.md; _registry.yaml
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] —
# [TESTS] tests/governance/rule_enforcement/
# [A_module] module_id=MOD-GOV_rule_engine | layer=package | stability=stable | safety=L | ai_autonomy=human_gated
# [TTL] permanent
"""rule_engine package — 规则引擎模块集合（ARCH-042 阶段1 拆分产物）。

归并 rule_* 系列，从 rule_enforcement/ 根迁入。
"""
