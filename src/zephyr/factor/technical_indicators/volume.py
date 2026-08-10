# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.technical_indicators.volume
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.technical_indicators.indicator_base; pandas(pip); numpy(pip)
# [CONSUMERS] zephyr.data.implementations.internal_compute_provider; sleeve alpha 择时
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 成交量类指标 7 个，纯自实现 pandas/numpy；compute→DataFrame 多列输出
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] compute 输入空 DataFrame→返回空 DataFrame 不抛；输入缺列→ValueError
# [TESTS] tests/zephyr/factor/technical_indicators/test_volume.py
# [A_module] module_id=MOD-L02-TI-VOLUME | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""成交量类技术指标（7 个，v1.0.0 全部施工完成）。

指标清单：OBV/MFI/VWAP/VR/AD/PVT/WVAD

算法对齐通达信：
  - OBV/AD/PVT 为累积量（cumsum），首值为 0
  - VR 通达信公式：VR=100×(2×up_vol+flat_vol)/(2×down_vol+flat_vol)，平盘量计入两侧
  - MFI 类似 RSI 但加入成交量加权
  - WVAD 用 (C-O)/(H-L)×V 滚动求和，H=L 时该项为 0

设计文档：16_technical_indicator_catalog.md §2.4
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from zephyr.factor.technical_indicators.indicator_base import (
    TechnicalIndicatorBase,
    TechnicalIndicatorMeta,
    TechnicalIndicatorRegistry,
)


@TechnicalIndicatorRegistry.register
class OBV(TechnicalIndicatorBase):
    """能量潮（On Balance Volume）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="obv",
        name="能量潮",
        category="volume",
        output_columns=["obv"],
        input_columns=["close", "volume"],
        params={},
        version="1.0.0",
        description="涨日加量跌日减量，累积求和，对齐通达信 VA+SUM",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        close, vol = data["close"], data["volume"]
        direction = np.sign(close.diff().fillna(0))
        obv = (direction * vol).cumsum()
        return pd.DataFrame({"obv": obv}, index=data.index)


@TechnicalIndicatorRegistry.register
class MFI(TechnicalIndicatorBase):
    """资金流量指标（Money Flow Index）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="mfi",
        name="资金流量指标",
        category="volume",
        output_columns=["mfi_14"],
        input_columns=["high", "low", "close", "volume"],
        params={"period": 14},
        version="1.0.0",
        description="TP=(H+L+C)/3; MF=TP×V; MFI=100-100/(1+正MF和/负MF和)",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        h, l, c, v = data["high"], data["low"], data["close"], data["volume"]
        tp = (h + l + c) / 3
        mf = tp * v
        tp_prev = tp.shift(1)
        pos_mf = mf.where(tp > tp_prev, 0.0)
        neg_mf = mf.where(tp < tp_prev, 0.0)
        pos_sum = pos_mf.rolling(window=n).sum()
        neg_sum = neg_mf.rolling(window=n).sum()
        mfi = 100 - 100 / (1 + pos_sum / neg_sum)
        return pd.DataFrame({f"mfi_{n}": mfi}, index=data.index)


@TechnicalIndicatorRegistry.register
class VWAP(TechnicalIndicatorBase):
    """成交量加权均价（Volume Weighted Average Price）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="vwap",
        name="成交量加权均价",
        category="volume",
        output_columns=["vwap"],
        input_columns=["close", "volume"],
        params={},
        version="1.0.0",
        description="VWAP=SUM(C×V)/SUM(V)，累积式（从首根 K 线开始）",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        close, vol = data["close"], data["volume"]
        if params.get("period"):
            # 滚动 VWAP（kwargs 传入 period 时）
            n = params["period"]
            cv = close * vol
            vwap = cv.rolling(window=n).sum() / vol.rolling(window=n).sum()
        else:
            # 累积 VWAP（默认，从首根 K 线开始）
            cv = (close * vol).cumsum()
            vwap = cv / vol.cumsum()
        return pd.DataFrame({"vwap": vwap}, index=data.index)


@TechnicalIndicatorRegistry.register
class VR(TechnicalIndicatorBase):
    """容量比率（Volume Ratio）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="vr",
        name="容量比率",
        category="volume",
        output_columns=["vr_26"],
        input_columns=["close", "volume"],
        params={"period": 26},
        version="1.0.0",
        description="VR=100×(2×up_vol+flat_vol)/(2×down_vol+flat_vol)，对齐通达信",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        close, vol = data["close"], data["volume"]
        diff = close.diff()
        up_vol = vol.where(diff > 0, 0.0)
        down_vol = vol.where(diff < 0, 0.0)
        flat_vol = vol.where(diff == 0, 0.0)
        up_sum = up_vol.rolling(window=n).sum()
        down_sum = down_vol.rolling(window=n).sum()
        flat_sum = flat_vol.rolling(window=n).sum()
        vr = 100 * (2 * up_sum + flat_sum) / (2 * down_sum + flat_sum)
        return pd.DataFrame({f"vr_{n}": vr}, index=data.index)


@TechnicalIndicatorRegistry.register
class AD(TechnicalIndicatorBase):
    """累积/派发线（Accumulation/Distribution Line）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="ad",
        name="累积/派发线",
        category="volume",
        output_columns=["ad"],
        input_columns=["high", "low", "close", "volume"],
        params={},
        version="1.0.0",
        description="CLV=(2C-H-L)/(H-L); AD=cumsum(CLV×V)，H=L时CLV=0",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        h, l, c, v = data["high"], data["low"], data["close"], data["volume"]
        hl_range = h - l
        clv = ((2 * c - h - l) / hl_range).where(hl_range != 0, 0.0)
        ad = (clv * v).cumsum()
        return pd.DataFrame({"ad": ad}, index=data.index)


@TechnicalIndicatorRegistry.register
class PVT(TechnicalIndicatorBase):
    """价量趋势（Price Volume Trend）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="pvt",
        name="价量趋势",
        category="volume",
        output_columns=["pvt"],
        input_columns=["close", "volume"],
        params={},
        version="1.0.0",
        description="PVT=cumsum(V×(C-Cp)/Cp)，累积式",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        close, vol = data["close"], data["volume"]
        pct_change = close.pct_change().fillna(0)
        pvt = (vol * pct_change).cumsum()
        return pd.DataFrame({"pvt": pvt}, index=data.index)


@TechnicalIndicatorRegistry.register
class WVAD(TechnicalIndicatorBase):
    """威廉变异离散量（William's Variable Accumulation Distribution）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="wvad",
        name="威廉变异离散量",
        category="volume",
        output_columns=["wvad_24"],
        input_columns=["open", "high", "low", "close", "volume"],
        params={"period": 24},
        version="1.0.0",
        description="WVAD=SUM(((C-O)/(H-L))×V, N)，H=L时该项为0",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        o, h, l, c, v = data["open"], data["high"], data["low"], data["close"], data["volume"]
        hl_range = h - l
        ratio = ((c - o) / hl_range).where(hl_range != 0, 0.0)
        wvad = (ratio * v).rolling(window=n).sum()
        return pd.DataFrame({f"wvad_{n}": wvad}, index=data.index)
