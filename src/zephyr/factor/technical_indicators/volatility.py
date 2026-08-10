# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.technical_indicators.volatility
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.technical_indicators.indicator_base; zephyr.factor.technical_indicators.trend; pandas(pip); numpy(pip)
# [CONSUMERS] zephyr.data.implementations.internal_compute_provider; sleeve alpha 择时
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 波动类指标 8 个，纯自实现 pandas/numpy；compute→DataFrame 多列输出；复用 trend._ema
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] compute 输入空 DataFrame→返回空 DataFrame 不抛；输入缺列→ValueError
# [TESTS] tests/zephyr/factor/technical_indicators/test_volatility.py
# [A_module] module_id=MOD-L02-TI-VOLATILITY | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""波动类技术指标（8 个，v1.0.0 全部施工完成）。

指标清单：ATR/BOLL/Keltner/Donchian/STDDEV/BandWidth/%B/HistVol

算法对齐通达信：
  - ATR 通达信用 MA（简单移动平均，非 Wilder's RMA）
  - BOLL/STDDEV 通达信 STD 用总体标准差 ddof=0（非 pandas 默认 ddof=1）
  - Keltner MID 用 EMA(adjust=False)，ATR 用 MA 对齐 ATR 指标
  - HistVol 用对数收益率样本标准差 ddof=1 × sqrt(252) 年化（金融行业标准）

设计文档：16_technical_indicator_catalog.md §2.3
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from zephyr.factor.technical_indicators.indicator_base import (
    TechnicalIndicatorBase,
    TechnicalIndicatorMeta,
    TechnicalIndicatorRegistry,
)
from zephyr.factor.technical_indicators.trend import _ema

# ---------------------------------------------------------------------------
# 模块级辅助函数
# ---------------------------------------------------------------------------


def _true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    """真实波幅 TR = max(H-L, |H-Cp|, |L-Cp|)。

    Cp 为前一日收盘价。首根 K 线 TR = H-L（无前收）。
    """
    return pd.concat(
        [high - low, (high - close.shift(1)).abs(), (low - close.shift(1)).abs()],
        axis=1,
    ).max(axis=1)


def _boll_bands(close: pd.Series, n: int, nbdev: float) -> tuple[pd.Series, pd.Series, pd.Series]:
    """布林带三轨，对齐通达信 STD（ddof=0 总体标准差）。

    Returns: (upper, middle, lower)
    """
    mid = close.rolling(window=n).mean()
    std = close.rolling(window=n).std(ddof=0)
    upper = mid + nbdev * std
    lower = mid - nbdev * std
    return upper, mid, lower


@TechnicalIndicatorRegistry.register
class ATR(TechnicalIndicatorBase):
    """真实波幅（Average True Range）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="atr",
        name="真实波幅",
        category="volatility",
        output_columns=["atr_14"],
        input_columns=["high", "low", "close"],
        params={"period": 14},
        version="1.0.0",
        description="TR=max(H-L,|H-Cp|,|L-Cp|); ATR=MA(TR,N)，对齐通达信（非 Wilder's RMA）",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        tr = _true_range(data["high"], data["low"], data["close"])
        atr = tr.rolling(window=n).mean()
        return pd.DataFrame({f"atr_{n}": atr}, index=data.index)


@TechnicalIndicatorRegistry.register
class BOLL(TechnicalIndicatorBase):
    """布林带（Bollinger Bands）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="boll",
        name="布林带",
        category="volatility",
        output_columns=["boll_upper", "boll_middle", "boll_lower"],
        input_columns=["close"],
        params={"period": 20, "nbdev": 2},
        version="1.0.0",
        description="MID=MA(C); UPPER=MID+nbdev×STD; LOWER=MID-nbdev×STD，STD 用 ddof=0 对齐通达信",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        upper, mid, lower = _boll_bands(data["close"], params["period"], params["nbdev"])
        return pd.DataFrame(
            {"boll_upper": upper, "boll_middle": mid, "boll_lower": lower},
            index=data.index,
        )


@TechnicalIndicatorRegistry.register
class Keltner(TechnicalIndicatorBase):
    """肯特纳通道（Keltner Channel）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="keltner",
        name="肯特纳通道",
        category="volatility",
        output_columns=["kc_upper", "kc_middle", "kc_lower"],
        input_columns=["high", "low", "close"],
        params={"period": 20, "atr_period": 10, "mult": 2},
        version="1.0.0",
        description="MID=EMA(C,N); UPPER=MID+mult×ATR(M); LOWER=MID-mult×ATR(M)，EMA adjust=False",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n, atr_n, mult = params["period"], params["atr_period"], params["mult"]
        mid = _ema(data["close"], n)
        tr = _true_range(data["high"], data["low"], data["close"])
        atr = tr.rolling(window=atr_n).mean()
        upper = mid + mult * atr
        lower = mid - mult * atr
        return pd.DataFrame(
            {"kc_upper": upper, "kc_middle": mid, "kc_lower": lower},
            index=data.index,
        )


@TechnicalIndicatorRegistry.register
class Donchian(TechnicalIndicatorBase):
    """唐奇安通道（Donchian Channel）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="donchian",
        name="唐奇安通道",
        category="volatility",
        output_columns=["dc_upper", "dc_lower"],
        input_columns=["high", "low"],
        params={"period": 20},
        version="1.0.0",
        description="UPPER=max(H,N); LOWER=min(L,N)，含当前 bar",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        upper = data["high"].rolling(window=n).max()
        lower = data["low"].rolling(window=n).min()
        return pd.DataFrame({"dc_upper": upper, "dc_lower": lower}, index=data.index)


@TechnicalIndicatorRegistry.register
class STDDEV(TechnicalIndicatorBase):
    """标准差（Standard Deviation）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="stddev",
        name="标准差",
        category="volatility",
        output_columns=["stddev_20"],
        input_columns=["close"],
        params={"period": 20},
        version="1.0.0",
        description="N 日收盘价标准差，ddof=0 对齐通达信 STD 函数",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        std = data["close"].rolling(window=n).std(ddof=0)
        return pd.DataFrame({f"stddev_{n}": std}, index=data.index)


@TechnicalIndicatorRegistry.register
class BandWidth(TechnicalIndicatorBase):
    """布林带宽度（Bollinger Band Width）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="bandwidth",
        name="布林带宽度",
        category="volatility",
        output_columns=["boll_bw"],
        input_columns=["close"],
        params={"period": 20, "nbdev": 2},
        version="1.0.0",
        description="BW=(UPPER-LOWER)/MID，基于 BOLL 三轨",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        upper, mid, lower = _boll_bands(data["close"], params["period"], params["nbdev"])
        bw = (upper - lower) / mid
        return pd.DataFrame({"boll_bw": bw}, index=data.index)


@TechnicalIndicatorRegistry.register
class PercentB(TechnicalIndicatorBase):
    """布林带%B（Bollinger %B）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="percent_b",
        name="布林带%B",
        category="volatility",
        output_columns=["boll_pctb"],
        input_columns=["close"],
        params={"period": 20, "nbdev": 2},
        version="1.0.0",
        description="%B=(C-LOWER)/(UPPER-LOWER)，基于 BOLL 三轨",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        upper, _, lower = _boll_bands(data["close"], params["period"], params["nbdev"])
        pctb = (data["close"] - lower) / (upper - lower)
        return pd.DataFrame({"boll_pctb": pctb}, index=data.index)


@TechnicalIndicatorRegistry.register
class HistVol(TechnicalIndicatorBase):
    """历史波动率（Historical Volatility）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="histvol",
        name="历史波动率",
        category="volatility",
        output_columns=["histvol_20"],
        input_columns=["close"],
        params={"period": 20},
        version="1.0.0",
        description="HV=STD(log(C/Cp),N,ddof=1)×sqrt(252)×100，年化波动率",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        log_ret = np.log(data["close"] / data["close"].shift(1))
        hv = log_ret.rolling(window=n).std(ddof=1) * np.sqrt(252) * 100
        return pd.DataFrame({f"histvol_{n}": hv}, index=data.index)
