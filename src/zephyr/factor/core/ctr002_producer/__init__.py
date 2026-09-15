# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §3.1
# [MODULE] zephyr.factor.core.ctr002_producer
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.shared.contracts.factor_signal
# [CONSUMERS] zephyr.signal_fundamental.pipeline（契约级消费 CTR-002 产物，无 import 依赖——经 2026-09-05 AI-08 审计实证）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-004: PIT铁律——as_of_date必须对齐因子计算的数据截面日期
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/factor/test_ctr002_producer.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
CTR-002 FactorSignal 生产者包入口。

导出公共 API:
- to_signals: pd.Series → list[FactorSignal]

# [ALGO_FLOW] external: docs/03_modules/_domain_factor/algo_flow/ctr002_producer__init__.yaml
"""

from zephyr.factor.core.ctr002_producer.converter import to_signals

__all__ = ["to_signals"]
