# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.market_data.market_data
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] factor; _cross_layer
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DAT_market_data | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
# 归一(2026-07-02): 删除手工复制的codegen产物(CTR-001 NormalizedMarketData)，
# 改为从shared/contracts re-export。真源唯一：shared/contracts/market_data.py（codegen生成）。
# 原问题：market_data.py有codegen标记但不在生成范围，trace_context引用TraceContext未import，
# from __future__ import annotations掩盖了运行时NameError。
from zephyr.shared.contracts.market_data import NormalizedMarketData

__all__ = ["NormalizedMarketData"]
