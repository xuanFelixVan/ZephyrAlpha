# [BLUEPRINT] MOD-L02-023 | (pending)
# [MODULE] zephyr.factor.technical_indicators.volume
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.technical_indicators.indicator_base; pandas(pip); numpy(pip)
# [CONSUMERS] zephyr.data.implementations.internal_compute_provider（包级 autodiscover 动态接线：internal_compute_provider L545/L1113 延迟导入本包+注册表消费）; sleeve alpha 择时
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 成交量类指标 13 个，纯自实现 pandas/numpy；compute→DataFrame 多列输出
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] compute 输入空 DataFrame→返回空 DataFrame 不抛；输入缺列→ValueError
# [TESTS] tests/zephyr/factor/technical_indicators/test_volume.py
# [A_module] module_id=MOD-L02-023 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

成交量类技术指标（7 个，v1.0.0 全部施工完成）。

指标清单：OBV/MFI/VWAP/VR/AD/PVT/WVAD/VWMA/ADOSC/EOM/KVO/NVI/PVI（批2b +6）

算法对齐通达信：
  - OBV/AD/PVT 为累积量（cumsum），首值为 0
  - VR 通达信公式：VR=100×(2×up_vol+flat_vol)/(2×down_vol+flat_vol)，平盘量计入两侧
  - MFI 类似 RSI 但加入成交量加权
  - WVAD 用 (C-O)/(H-L)×V 滚动求和，H=L 时该项为 0

设计文档：16_technical_indicator_catalog.md §2.4

# [ALGO_FLOW] external: docs/03_modules/_domain_factor/algo_flow/volume.yaml
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


@TechnicalIndicatorRegistry.register
class VWMA(TechnicalIndicatorBase):
    """成交量加权均线（Volume Weighted Moving Average，20）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="vwma",
        name="成交量加权均线",
        category="volume",
        output_columns=["vwma_20"],
        input_columns=["close", "volume"],
        params={"period": 20},
        version="1.0.0",
        description="VWMA=Σ(C×V,N)/Σ(V,N)（滚动窗口；区别于累积口径的 vwap）",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        cv = (data["close"] * data["volume"]).rolling(window=n).sum()
        v_sum = data["volume"].rolling(window=n).sum()
        vwma = cv / v_sum
        return pd.DataFrame({f"vwma_{n}": vwma}, index=data.index)


@TechnicalIndicatorRegistry.register
class ADOSC(TechnicalIndicatorBase):
    """蔡金震荡器（Chaikin A/D Oscillator，3/10）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="adosc",
        name="蔡金震荡器",
        category="volume",
        output_columns=["adosc"],
        input_columns=["high", "low", "close", "volume"],
        params={"fast": 3, "slow": 10},
        version="1.0.0",
        description="ADOSC=EMA3(AD)−EMA10(AD)，AD 线短期与长期平滑之差（TA-Lib ADOSC）",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        fast_n, slow_n = params["fast"], params["slow"]
        h, l, c, v = data["high"], data["low"], data["close"], data["volume"]
        clv = ((c - l) - (c - h)).where(h != l, 0.0)
        ad_line = (clv * v).cumsum()
        adosc = ad_line.ewm(span=fast_n, adjust=False).mean() - ad_line.ewm(
            span=slow_n, adjust=False
        ).mean()
        return pd.DataFrame({"adosc": adosc}, index=data.index)


@TechnicalIndicatorRegistry.register
class EOM(TechnicalIndicatorBase):
    """简易波动量（Ease of Movement，14）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="eom",
        name="简易波动量",
        category="volume",
        output_columns=["eom_14"],
        input_columns=["high", "low", "volume"],
        params={"period": 14, "divisor": 100000000.0},
        version="1.0.0",
        description="EMV=中价差/(量/1e8/(H−L))；EOM=SMA(EMV,14)，价格上涨轻松度（H=L 时该项取 0）",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n, divisor = params["period"], params["divisor"]
        h, l, v = data["high"], data["low"], data["volume"]
        mid = 0.5 * (h + l)
        mid_shift = 0.5 * (h.shift(1) + l.shift(1))
        dm = mid - mid_shift
        br = (v / divisor) / (h - l)
        emv = (dm / br).where((h - l) != 0, 0.0)
        eom = emv.rolling(window=n).mean()
        return pd.DataFrame({f"eom_{n}": eom}, index=data.index)


@TechnicalIndicatorRegistry.register
class KVO(TechnicalIndicatorBase):
    """Klinger 量震荡器（Klinger Volume Oscillator，34/55，signal 13）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="kvo",
        name="Klinger量震荡器",
        category="volume",
        output_columns=["kvo", "kvo_signal"],
        input_columns=["high", "low", "close", "volume"],
        params={"fast": 34, "slow": 55, "signal": 13},
        version="1.0.0",
        description="VF=V×trend×|2×DM/CM−1|（CM 随趋势翻转重置）；KVO=EMA34(VF)−EMA55(VF)；sig=EMA13",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        fast_n, slow_n, sig_n = params["fast"], params["slow"], params["signal"]
        h, l, v = data["high"], data["low"], data["volume"]
        dm = (h - l).to_numpy()
        hl2_prev = (h + l).shift(1).to_numpy()
        sv = np.sign((h + l).to_numpy() - hl2_prev)
        m = len(dm)
        vol = v.to_numpy()
        vf = np.zeros(m)
        cm = 0.0
        prev_sv = 0.0
        for i in range(1, m):
            if sv[i] != prev_sv:
                cm = abs(dm[i - 1]) + dm[i]
            else:
                cm = cm + dm[i]
            prev_sv = sv[i]
            if cm != 0:
                vf[i] = vol[i] * sv[i] * abs(2 * dm[i] / cm - 1)
        vf_s = pd.Series(vf, index=data.index)
        kvo = vf_s.ewm(span=fast_n, adjust=False).mean() - vf_s.ewm(span=slow_n, adjust=False).mean()
        kvo_signal = kvo.ewm(span=sig_n, adjust=False).mean()
        return pd.DataFrame({"kvo": kvo, "kvo_signal": kvo_signal}, index=data.index)


@TechnicalIndicatorRegistry.register
class NVI(TechnicalIndicatorBase):
    """负成交量指标（Negative Volume Index）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="nvi",
        name="负成交量指标",
        category="volume",
        output_columns=["nvi"],
        input_columns=["close", "volume"],
        params={},
        version="1.0.0",
        description="缩量日累乘 (1+收益率)，放量日不动；种子=100。度量'聪明钱'行为",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        ret = data["close"].pct_change()
        factor = (1 + ret).where(data["volume"] < data["volume"].shift(1), 1.0).fillna(1.0)
        nvi = 100.0 * factor.cumprod()
        return pd.DataFrame({"nvi": nvi}, index=data.index)


@TechnicalIndicatorRegistry.register
class PVI(TechnicalIndicatorBase):
    """正成交量指标（Positive Volume Index）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="pvi",
        name="正成交量指标",
        category="volume",
        output_columns=["pvi"],
        input_columns=["close", "volume"],
        params={},
        version="1.0.0",
        description="放量日累乘 (1+收益率)，缩量日不动；种子=100。度量'散户钱'行为",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        ret = data["close"].pct_change()
        factor = (1 + ret).where(data["volume"] > data["volume"].shift(1), 1.0).fillna(1.0)
        pvi = 100.0 * factor.cumprod()
        return pd.DataFrame({"pvi": pvi}, index=data.index)


@TechnicalIndicatorRegistry.register
class FORCE_INDEX(TechnicalIndicatorBase):
    """强力指数（Alexander Elder Force Index，13）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="force_index",
        name="强力指数",
        category="volume",
        output_columns=["fi_13"],
        input_columns=["close", "volume"],
        params={"period": 13},
        version="1.0.0",
        description="FI=EMA13[ΔC×V]，价格变动×成交量合成买卖力量（Alexander Elder）",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        raw = data["close"].diff() * data["volume"]
        fi = raw.ewm(span=n, adjust=False).mean()
        return pd.DataFrame({f"fi_{n}": fi}, index=data.index)
