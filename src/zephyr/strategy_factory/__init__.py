# [BLUEPRINT] MOD-SOWNER-001 | docs/03_modules/_domain_ashare_signal/blueprint.md
# [MODULE] zephyr.strategy_factory
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] none
# [CONSUMERS] zephyr.strategy_factory.owner_band_t（策略卡考试模块族）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 本包只收纳策略卡转译的 Owner mandate 策略模块；每张卡一个子包；禁在本包放置通用回测基建（那是 zephyr.backtest 的职责）
# [MODIFY-GUARD] schema-change
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import-error 直抛
# [TESTS] tests/strategy_factory/
# [A_module] module_id=MOD-SOWNER-001 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""策略工厂策略卡模块包（S-OWNER 系列卡转译实现）。

每张 Owner mandate 策略卡对应一个子包，实现卡面规则 + E4 考试器。
通用回测/成本/数据设施一律复用 zephyr.backtest / zephyr.infrastructure，
本包零复制（RULE-CLONEGUARD）。
"""
