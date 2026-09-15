# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §3.1
# [MODULE] zephyr.factor.core.ctr001_consumer
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.shared.contracts.market_data
# [CONSUMERS] zephyr.factor.factor_base（契约级消费 CTR-001 数据形态，无 import 依赖——经 2026-09-05 AI-08 审计实证）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-004: PIT铁律——仅使用timestamp做截面对齐
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/factor/test_ctr001_consumer.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
CTR-001 NormalizedMarketData 消费者包入口。

导出公共 API:
- to_dataframe: NormalizedMarketData 列表 → pd.DataFrame
- filter_quality: 质量过滤

# [ALGO_FLOW] external: docs/03_modules/_domain_factor/algo_flow/ctr001_consumer__init__.yaml
"""

from zephyr.factor.core.ctr001_consumer.converter import filter_quality, to_dataframe

__all__ = ["to_dataframe", "filter_quality"]
