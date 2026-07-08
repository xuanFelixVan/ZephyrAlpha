# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.momentum_factor
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_momentum_factor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: factor
# category: factor_implementation
# status: active
# created: "2026-05-05"
# ---

"""D_FACTOR — Momentum Factor

20 日动量因子。计算过去 20 个交易日的价格变化率。

CTR 契约：
  消费者 — CTR-001 (NormalizedMarketData) ← D_DATA
  生产者 — CTR-002 (FactorSignal) -> D_SIGNAL, D_RISK, D_PORTFOLIO_CORE
"""

from __future__ import annotations

import pandas as pd

from zephyr.factor.factor_base import FactorBase, FactorMeta, FactorRegistry


@FactorRegistry.register
class Momentum20d(FactorBase):
    meta = FactorMeta(
        factor_id="momentum_20d",
        name="20日动量因子",
        domain="technical",
        version="1.0.0",
        description="过去 20 个交易日收盘价变化率",
        tags=["momentum", "trend"],
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.Series:
        window = kwargs.get("window", 20)
        return data["close"].pct_change(window)

    def validate(self, data: pd.DataFrame) -> bool:
        if not super().validate(data):
            return False
        return "close" in data.columns and len(data) >= 22
