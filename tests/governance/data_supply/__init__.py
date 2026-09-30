# [BLUEPRINT] MOD-GOV-DS | docs/_working/total_command_closeout/wave3/supply_ledger_report.md | §4-D
# [MODULE] tests.governance.data_supply
# [DOMAIN] D_TEST
# [MATURITY] n/a
# [INVARIANTS] n/a
# [MODIFY-GUARD] none（只读校验/生成器，无状态写盘）
# [STABILITY] stable
# [SAFETY] n/a
# [AI_AUTONOMY] n/a
# [ERROR_CONTRACT] n/a
# [TESTS] n/a
# [DEPENDENCIES] scripts.governance.data_supply
# [CONSUMERS] pytest（波 3 案卷 §4-D 红证入口）
# [STARTUP] test_collected
# [TTL] task_bound
# [A_module] module_id=TST-GOV-DS-PKG | layer=test_package | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""Wave-3 data-supply ruler tests (3.2 / 3.3 / W-102 counterfactual control groups)."""
