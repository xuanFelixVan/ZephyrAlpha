# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.value_factor
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.factor_base
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
# [A_module] module_id=MOD-UNK_value_factor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: factor
# category: factor_implementation
# status: active
# created: "2026-05-05"
# ---

"""D_FACTOR — Value Factor

估值因子。使用简易 PE proxy（价格/年化盈利估算）。

CTR 契约：
  消费者 — CTR-001 (NormalizedMarketData) ← D_DATA
  生产者 — CTR-002 (FactorSignal) -> D_SIGNAL, D_RISK, D_PORTFOLIO_CORE
"""

from __future__ import annotations

import pandas as pd

from zephyr.factor.factor_base import FactorBase, FactorMeta, FactorRegistry


@FactorRegistry.register
class ValueFactor(FactorBase):
    meta = FactorMeta(
        factor_id="value_factor",
        name="估值因子",
        domain="fundamental",
        version="1.0.0",
        description="简易 PE proxy = 1 / (price/avg_earnings_estimate)",
        tags=["value", "pe"],
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.Series:
        avg_price = data["close"].rolling(60).mean()
        earnings_estimate = kwargs.get("earnings_per_share", 5.0)
        pe_ratio = avg_price / earnings_estimate

        pe_ratio = pe_ratio.replace([float("inf"), float("-inf")], float("nan"))
        value_signal = 1.0 / pe_ratio.replace(0, float("nan"))

        return value_signal.fillna(0)

    def validate(self, data: pd.DataFrame) -> bool:
        if not super().validate(data):
            return False
        return "close" in data.columns and len(data) >= 60
