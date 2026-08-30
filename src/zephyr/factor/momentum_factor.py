# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.momentum_factor
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.factor_base
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK-momentum_factor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: factor
# category: factor_implementation
# status: active
# created: "2026-05-05"
# ---

"""
D_FACTOR — Momentum Factor

20 日动量因子。计算过去 20 个交易日的价格变化率。

CTR 契约：
  消费者 — CTR-001 (NormalizedMarketData) ← D_DATA
  生产者 — CTR-002 (FactorSignal) -> D_SIGNAL, D_RISK, D_PORTFOLIO_CORE

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: momentum_factor.py
# 层: 算法
# - id: A1
#   name_zh: ① Momentum20d
#   name_en: Momentum20d
#   intro: class Momentum20d 源码 L69-L113
#   desc: 公共方法（定义序）: compute, incremental_compute, validate；源码 L69-L113
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: Momentum20d
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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

    def incremental_compute(
        self,
        data: pd.DataFrame,
        window: int = 20,
        cached: pd.Series | None = None,
        **kwargs,
    ) -> pd.Series:
        """增量计算20日动量——滑动窗口只重算新增数据点。

        pct_change(window) 在位置 t 需要 close[t] 和 close[t-window]，
        因此只需取最后 (window + 新增数量) 个数据点重算尾部，拼接缓存。
        """
        if cached is None or cached.empty:
            return self.compute(data, window=window)
        last_idx = cached.index[-1]
        if last_idx not in data.index:
            return self.compute(data, window=window)
        new_data = data[data.index > last_idx]
        if new_data.empty:
            return cached
        last_pos = data.index.get_loc(last_idx)
        start_pos = max(0, last_pos - window + 1)
        tail = data.iloc[start_pos:]
        tail_factor = tail["close"].pct_change(window)
        new_factor = tail_factor[tail_factor.index > last_idx]
        return pd.concat([cached, new_factor])

    def validate(self, data: pd.DataFrame) -> bool:
        if not super().validate(data):
            return False
        return "close" in data.columns and len(data) >= 22
