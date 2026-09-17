# [BLUEPRINT] MOD-SOWNER-001 | docs/03_modules/_domain_ashare_signal/blueprint.md
# [MODULE] zephyr.strategy_factory.owner_band_t.signals
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] pandas; numpy
# [CONSUMERS] zephyr.strategy_factory.owner_band_t.engine; tests/strategy_factory/test_s_owner_001_engine.py
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 全部 rolling/shift 只用 ≤i 期数据（PIT）；纯函数无 I/O
# [MODIFY-GUARD] 语义变更=考试冻结口径变更，冻结期禁改
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(窗口参数非法)
# [TESTS] tests/strategy_factory/test_s_owner_001_engine.py
# [A_module] module_id=MOD-SOWNER-001 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""波段信号面（信号=000300 指数日线）——布林上轨/前高/涨幅分位/波动率分位。

与 E4 冻结文档 §3 一致：
  * 布林上轨: close >= SMA20 + 2*std20
  * 前高:     close >= max(high[t-60 .. t-10])
  * 涨幅分位: 20 日收益 >= 其 250 日滚动 90 分位
  * 波动率分位: 20 日收益 std 在其 250 日滚动分布中的分位（P1 阈比较用）
"""

from __future__ import annotations

import numpy as np
import pandas as pd

BB_WINDOW = 20
BB_K = 2.0
PRIOR_HIGH_FROM = 60
PRIOR_HIGH_TO = 10  # 不含当日：high[t-60..t-10]
RET_WINDOW = 20
RET_QUANTILE_LOOKBACK = 250
RET_QUANTILE = 0.90
VOL_WINDOW = 20
VOL_QUANTILE_LOOKBACK = 250


def bb_upper_flag(close: pd.Series) -> pd.Series:
    """布林上轨触发（close>=SMA20+2σ）。"""
    sma = close.rolling(BB_WINDOW).mean()
    std = close.rolling(BB_WINDOW).std(ddof=0)
    return close >= (sma + BB_K * std)


def prior_high_ref(high: pd.Series) -> pd.Series:
    """前高参考线: max(high[t-60..t-10])（不含近 10 日，避免与当前价惯性重叠）。

    触发判定（close>=ref）由 engine 在收盘数据上执行。
    """
    return high.shift(PRIOR_HIGH_TO).rolling(PRIOR_HIGH_FROM - PRIOR_HIGH_TO + 1).max()


def return_quantile_flag(close: pd.Series) -> pd.Series:
    """涨幅分位触发：20 日收益 >= 其 250 日滚动 90 分位。"""
    ret = close.pct_change(RET_WINDOW)
    q = ret.rolling(RET_QUANTILE_LOOKBACK, min_periods=RET_QUANTILE_LOOKBACK // 2).quantile(RET_QUANTILE)
    return ret >= q


def volatility_percentile(close: pd.Series) -> pd.Series:
    """20 日波动率的 250 日滚动分位（0..1；TD 极值联动 P1 阈用）。"""
    vol = close.pct_change().rolling(VOL_WINDOW).std(ddof=0)
    pct = vol.rolling(VOL_QUANTILE_LOOKBACK, min_periods=VOL_QUANTILE_LOOKBACK // 2).rank(pct=True)
    return pct


def build_signal_panel(close: pd.Series, high: pd.Series) -> pd.DataFrame:
    """一次性构建全部信号列（engine 网格复用，避免逐组合重算）。"""
    return pd.DataFrame(
        {
            "bb_upper": bb_upper_flag(close),
            "prior_high_ref": prior_high_ref(high),
            "ret_quantile": return_quantile_flag(close),
            "vol_pct": volatility_percentile(close),
        },
        index=close.index,
    )
