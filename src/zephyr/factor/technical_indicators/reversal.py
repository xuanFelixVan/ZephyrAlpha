# [BLUEPRINT] MOD-L02-020 | (pending)
# [MODULE] zephyr.factor.technical_indicators.reversal
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.technical_indicators.indicator_base; zephyr.factor.technical_indicators.trend; zephyr.factor.technical_indicators.momentum; zephyr.factor.technical_indicators.volatility; pandas(pip); numpy(pip)
# [CONSUMERS] zephyr.data.implementations.internal_compute_provider; sleeve alpha 择时
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 反转类指标 5 个，纯自实现 pandas/numpy；compute→DataFrame 多列输出（信号列 0/1/-1）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] compute 输入空 DataFrame→返回空 DataFrame 不抛；输入缺列→ValueError
# [TESTS] tests/zephyr/factor/technical_indicators/test_reversal.py
# [A_module] module_id=MOD-L02-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

反转类技术指标（5 个，v1.0.0 全部施工完成）。

指标清单：CandlestickPattern/RSIDivergence/MACDDivergence/BOLLBreakout/VolumePriceDivergence

输出约定：
  - 信号列 Float64: 0.0=无信号, 1.0=正信号(看涨), -1.0=负信号(看跌)
  - K线形态编码: 0=无, 1=锤子, 2=看涨吞没, -2=看跌吞没, 3=启明星, 4=黄昏星, 5=十字星

算法说明：
  - 背离检测用简化方案（lookback 窗口内价格趋势 vs 指标趋势对比），可后续升级为峰谷分析
  - K线形态识别覆盖 6 种基础形态，可扩展

设计文档：16_technical_indicator_catalog.md §2.5

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 行情OHLCV数据 DataFrame
#   fields: open/high/low/close/volume 列（各指标按 meta.input_columns 取用）
#   code: compute(data: pd.DataFrame)
# 层: 指标
# - id: CANDLE
#   name_zh: K线形态识别
#   name_en: CandlestickPattern
#   intro: 按实体/影线比例识别锤子、吞没、启明星、黄昏星、十字星并编码
#   formula: body=|C-O|；doji: body/(H-L)<0.1→5；hammer: 下影/实体>2 且上影<0.3实体→1；吞没±2（2bar）；启明/黄昏星 3/4（3bar）
#   code: reversal.py L62-107
#   registry: 指标表: 有candle_pattern列 但代码未读表（本模块即指标计算实现）
#   is_break: true
# - id: RSIDIV
#   name_zh: RSI背离 12,20
#   name_en: RSIDivergence
#   intro: 价格趋势与 RSI 趋势反向即背离信号，复用 momentum._rsi
#   formula: rsi=_rsi(C,12) → 顶背离: Δ20C>0 且 Δ20rsi<0 → 1；底背离: Δ20C<0 且 Δ20rsi>0 → -1
#   code: reversal.py L125-140
#   registry: 指标表: 有rsi_divergence列 但代码未读表（本模块即指标计算实现）
#   is_break: true
# - id: BOLLBRK
#   name_zh: 布林带突破 20,2
#   name_en: BOLLBreakout
#   intro: 收盘价突破布林上轨发正信号、破下轨发负信号，复用 volatility._boll_bands
#   formula: (upper,_,lower)=_boll_bands(C,20,2) → C>upper→1；C<lower→-1；否则0
#   code: reversal.py L192-202
#   registry: 指标表: 有boll_breakout列 但代码未读表（本模块即指标计算实现）
#   is_break: true
# - id: VPDIV
#   name_zh: 量价背离 10
#   name_en: VolumePriceDivergence
#   intro: 价升量缩为顶背离、价跌量增为底背离
#   formula: 顶背离: Δ10C>0 且 Δ10V<0 → 1；底背离: Δ10C<0 且 Δ10V>0 → -1；否则0
#   code: reversal.py L220-234
#   registry: 指标表: 有vol_price_div列 但代码未读表（本模块即指标计算实现）
#   is_break: true
# 层: 算法
# - id: A1
#   name_zh: ① 校验+参数合并+空表短路 compute统一契约
#   name_en: TechnicalIndicatorBase.compute
#   intro: 每个指标入口先校验列、空表直接返回空 DataFrame、再合并默认参数
#   desc: validate(data) 缺列抛 ValueError → data.empty 返回空表 → get_params(**kwargs) 合并默认参数
#   inputs: I1
#   outputs: 校验通过的 data 与 params
#   invariant: 空 DataFrame 输入→空 DataFrame 输出不抛异常
# - id: A2
#   name_zh: ② 复用三库基础指标函数
#   name_en: _rsi/_ema/_boll_bands
#   intro: 从 momentum/trend/volatility import 现成平滑与轨道函数，不重复造轮子
#   desc: reversal.py L42-44：momentum._rsi（RSI背离用）、trend._ema（MACD背离的 DIF/DEA/HIST 用）、volatility._boll_bands（布林突破用）
#   inputs: I1
#   outputs: RSI/EMA/布林三轨等中间序列
# - id: A3
#   name_zh: ③ 简化背离检测
#   name_en: lookback divergence
#   intro: lookback 窗口内价格变化与指标变化符号对比，输出 0/1/-1 信号
#   desc: price_change=x-x.shift(lookback) 与 ind_change 符号相反 → 置 ±1；RSI/MACD/量价三背离共用此简化方案（docstring 注明可升级为峰谷分析）
#   inputs: I1 A2
#   outputs: 信号 Series（0=无 1=顶背离 -1=底背离）
# 层: 输出
# - id: O1
#   name_zh: 反转信号 DataFrame（5指标）
#   name_en: reversal indicators DataFrame
#   intro: K线形态编码 + 4个背离/突破信号列，识别趋势反转点
#   invariant: 信号列取值 ∈{0.0,1.0,-1.0}；candle_pattern 编码 ∈{0,1,2,-2,3,4,5}
#   downstream: zephyr.data.implementations.internal_compute_provider（批量计算写入 c1_market.technical_indicator）；sleeve alpha 择时
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# I1 --> A3
# A2 --> A3
# A1 -.->|断点| CANDLE
# A1 -.->|断点| RSIDIV
# A1 -.->|断点| BOLLBRK
# A1 -.->|断点| VPDIV
# A2 -.->|断点| RSIDIV
# A2 -.->|断点| BOLLBRK
# A3 -.->|断点| RSIDIV
# A3 -.->|断点| VPDIV
# CANDLE --> O1
# RSIDIV --> O1
# BOLLBRK --> O1
# VPDIV --> O1
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from zephyr.factor.technical_indicators.indicator_base import (
    TechnicalIndicatorBase,
    TechnicalIndicatorMeta,
    TechnicalIndicatorRegistry,
)
from zephyr.factor.technical_indicators.momentum import _rsi
from zephyr.factor.technical_indicators.trend import _ema
from zephyr.factor.technical_indicators.volatility import _boll_bands


@TechnicalIndicatorRegistry.register
class CandlestickPattern(TechnicalIndicatorBase):
    """K线形态识别（Candlestick Pattern Recognition）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="candlestick_pattern",
        name="K线形态",
        category="reversal",
        output_columns=["candle_pattern"],
        input_columns=["open", "high", "low", "close"],
        params={"patterns": "all"},
        version="1.0.0",
        description="识别锤子/吞没/启明星/黄昏星/十字星，编码(0=无,1=锤子,2=看涨吞没,-2=看跌吞没,3=启明星,4=黄昏星,5=十字星)",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        o, h, l, c = data["open"], data["high"], data["low"], data["close"]
        body = (c - o).abs()
        hl_range = h - l
        upper_shadow = h - pd.concat([o, c], axis=1).max(axis=1)
        lower_shadow = pd.concat([o, c], axis=1).min(axis=1) - l
        # 避免除零
        body_safe = body.where(body > 0, np.nan)
        ratio = lower_shadow / body_safe

        pattern = pd.Series(0.0, index=data.index, dtype=float)

        # 5=十字星：实体极小（<10% 振幅）
        doji = (body / hl_range.where(hl_range > 0, np.nan) < 0.1) & (hl_range > 0)
        pattern[doji] = 5.0

        # 1=锤子线：下影线 > 2×实体，上影线小，实体在上方
        hammer = (ratio > 2) & (upper_shadow < body_safe * 0.3) & (body > 0)
        pattern[hammer] = 1.0

        # 2=看涨吞没 / -2=看跌吞没（2 bar）
        prev_bearish = c.shift(1) < o.shift(1)
        curr_bullish = c > o
        prev_bullish = c.shift(1) > o.shift(1)
        curr_bearish = c < o
        bull_engulf = prev_bearish & curr_bullish & (o <= c.shift(1)) & (c >= o.shift(1))
        bear_engulf = prev_bullish & curr_bearish & (o >= c.shift(1)) & (c <= o.shift(1))
        pattern[bull_engulf] = 2.0
        pattern[bear_engulf] = -2.0

        # 3=启明星 / 4=黄昏星（3 bar）
        bar1_bear = c.shift(2) < o.shift(2)
        bar1_bull = c.shift(2) > o.shift(2)
        bar2_small = (c.shift(1) - o.shift(1)).abs() < body.shift(2) * 0.5
        bar3_bull = c > o
        bar3_bear = c < o
        bar1_mid = (o.shift(2) + c.shift(2)) / 2
        morning_star = bar1_bear & bar2_small & bar3_bull & (c > bar1_mid)
        evening_star = bar1_bull & bar2_small & bar3_bear & (c < bar1_mid)
        pattern[morning_star] = 3.0
        pattern[evening_star] = 4.0

        return pd.DataFrame({"candle_pattern": pattern}, index=data.index)


@TechnicalIndicatorRegistry.register
class RSIDivergence(TechnicalIndicatorBase):
    """RSI背离（RSI Divergence）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="rsi_divergence",
        name="RSI背离",
        category="reversal",
        output_columns=["rsi_divergence"],
        input_columns=["close"],
        params={"rsi_period": 12, "lookback": 20},
        version="1.0.0",
        description="价格趋势 vs RSI 趋势对比，输出(0=无,1=顶背离,-1=底背离)",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        rsi_n, lookback = params["rsi_period"], params["lookback"]
        close = data["close"]
        rsi = _rsi(close, rsi_n)
        price_change = close - close.shift(lookback)
        rsi_change = rsi - rsi.shift(lookback)
        signal = pd.Series(0.0, index=data.index, dtype=float)
        # 顶背离：价升 RSI 降
        signal[(price_change > 0) & (rsi_change < 0)] = 1.0
        # 底背离：价跌 RSI 升
        signal[(price_change < 0) & (rsi_change > 0)] = -1.0
        return pd.DataFrame({"rsi_divergence": signal}, index=data.index)


@TechnicalIndicatorRegistry.register
class MACDDivergence(TechnicalIndicatorBase):
    """MACD背离（MACD Divergence）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="macd_divergence",
        name="MACD背离",
        category="reversal",
        output_columns=["macd_divergence"],
        input_columns=["close"],
        params={"lookback": 20, "fast": 12, "slow": 26, "signal": 9},
        version="1.0.0",
        description="价格趋势 vs MACD HIST 趋势对比，输出(0=无,1=顶背离,-1=底背离)",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        lookback = params["lookback"]
        fast, slow, signal_n = params["fast"], params["slow"], params["signal"]
        close = data["close"]
        dif = _ema(close, fast) - _ema(close, slow)
        dea = _ema(dif, signal_n)
        hist = 2 * (dif - dea)
        price_change = close - close.shift(lookback)
        hist_change = hist - hist.shift(lookback)
        signal_out = pd.Series(0.0, index=data.index, dtype=float)
        signal_out[(price_change > 0) & (hist_change < 0)] = 1.0
        signal_out[(price_change < 0) & (hist_change > 0)] = -1.0
        return pd.DataFrame({"macd_divergence": signal_out}, index=data.index)


@TechnicalIndicatorRegistry.register
class BOLLBreakout(TechnicalIndicatorBase):
    """布林带突破（Bollinger Band Breakout）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="boll_breakout",
        name="布林带突破",
        category="reversal",
        output_columns=["boll_breakout"],
        input_columns=["close"],
        params={"period": 20, "nbdev": 2},
        version="1.0.0",
        description="收盘价突破上轨→1, 突破下轨→-1, 否则0",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        upper, _, lower = _boll_bands(data["close"], params["period"], params["nbdev"])
        close = data["close"]
        signal = pd.Series(0.0, index=data.index, dtype=float)
        signal[close > upper] = 1.0
        signal[close < lower] = -1.0
        return pd.DataFrame({"boll_breakout": signal}, index=data.index)


@TechnicalIndicatorRegistry.register
class VolumePriceDivergence(TechnicalIndicatorBase):
    """量价背离（Volume-Price Divergence）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="vol_price_divergence",
        name="量价背离",
        category="reversal",
        output_columns=["vol_price_div"],
        input_columns=["close", "volume"],
        params={"lookback": 10},
        version="1.0.0",
        description="价升量缩→顶背离(1), 价跌量增→底背离(-1), 否则0",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        lookback = params["lookback"]
        close, vol = data["close"], data["volume"]
        price_change = close - close.shift(lookback)
        vol_change = vol - vol.shift(lookback)
        signal = pd.Series(0.0, index=data.index, dtype=float)
        # 顶背离：价升量缩
        signal[(price_change > 0) & (vol_change < 0)] = 1.0
        # 底背离：价跌量增
        signal[(price_change < 0) & (vol_change > 0)] = -1.0
        return pd.DataFrame({"vol_price_div": signal}, index=data.index)
