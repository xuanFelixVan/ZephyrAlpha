# [BLUEPRINT] MOD-L02-022 | (pending)
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
# [A_module] module_id=MOD-L02-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

波动类技术指标（8 个，v1.0.0 全部施工完成）。

指标清单：ATR/BOLL/Keltner/Donchian/STDDEV/BandWidth/%B/HistVol

算法对齐通达信：
  - ATR 通达信用 MA（简单移动平均，非 Wilder's RMA）
  - BOLL/STDDEV 通达信 STD 用总体标准差 ddof=0（非 pandas 默认 ddof=1）
  - Keltner MID 用 EMA(adjust=False)，ATR 用 MA 对齐 ATR 指标
  - HistVol 用对数收益率样本标准差 ddof=1 × sqrt(252) 年化（金融行业标准）

设计文档：16_technical_indicator_catalog.md §2.3

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 行情OHLC数据 DataFrame
#   fields: high/low/close 列（各指标按 meta.input_columns 取用）
#   code: compute(data: pd.DataFrame)
# 层: 指标
# - id: ATR
#   name_zh: 真实波幅ATR 14
#   name_en: ATR
#   intro: 真实波幅的简单平均，度量价格波动剧烈程度
#   formula: TR=max(H-L,|H-Cp|,|L-Cp|) → ATR=MA14(TR)（通达信用 MA，非 Wilder's RMA）
#   code: volatility.py L85-93
#   registry: 指标表: 有atr_14列 但代码未读表（本模块即指标计算实现）
#   is_break: true
# - id: BOLL
#   name_zh: 布林带BOLL 20,2
#   name_en: BOLL
#   intro: 均线上下各两倍标准差形成通道，BandWidth/%B 也基于它
#   formula: MID=MA20(C)；STD=rolling20.std(ddof=0)；UPPER=MID+2STD；LOWER=MID-2STD（ddof=0 对齐通达信）
#   code: volatility.py L111-120（_boll_bands L58-67）
#   registry: 指标表: 有boll_upper/boll_middle/boll_lower列 但代码未读表（本模块即指标计算实现）
#   is_break: true
# - id: KC
#   name_zh: 肯特纳通道Keltner 20,10,2
#   name_en: Keltner
#   intro: EMA 中轨加 ATR 倍数构成通道，比布林带更平滑
#   formula: MID=EMA20(C)（复用 trend._ema adjust=False）；UPPER=MID+2×MA10(TR)；LOWER=MID-2×MA10(TR)
#   code: volatility.py L138-152
#   registry: 指标表: 有kc_upper/kc_middle/kc_lower列 但代码未读表（本模块即指标计算实现）
#   is_break: true
# - id: HV
#   name_zh: 历史波动率HistVol 20
#   name_en: HistVol
#   intro: 对数收益率的标准差年化，金融行业标准波动率
#   formula: r=log(C/C.shift1) → HV=r.rolling20.std(ddof=1)×√252×100
#   code: volatility.py L271-279
#   registry: 指标表: 有histvol_20列 但代码未读表（本模块即指标计算实现）
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
#   name_zh: ② 真实波幅TR
#   name_en: _true_range
#   intro: 三种波幅取最大，ATR 与 Keltner 通道共用
#   desc: pd.concat([H-L, |H-C.shift1|, |L-C.shift1|]).max(axis=1)，首根K线 TR=H-L
#   inputs: I1
#   outputs: TR Series
# - id: A3
#   name_zh: ③ 布林三轨
#   name_en: _boll_bands
#   intro: 中轨+上下轨一次算出，BOLL/BandWidth/%B 三指标共用，reversal 模块也 import
#   desc: MID=rolling(N).mean()；STD=rolling(N).std(ddof=0)；UPPER/LOWER=MID±nbdev×STD
#   inputs: I1
#   outputs: (upper, middle, lower) 三元组
# 层: 输出
# - id: O1
#   name_zh: 波动指标 DataFrame（8指标多列）
#   name_en: volatility indicators DataFrame
#   intro: ATR/BOLL/Keltner/Donchian/STDDEV/BandWidth/%B/HistVol 共8个波动指标的多列输出，index 与输入对齐
#   invariant: 输出列严格等于各 meta.output_columns（atr_14、boll_*、kc_*、dc_upper/dc_lower、stddev_20、boll_bw、boll_pctb、histvol_20）
#   downstream: zephyr.data.implementations.internal_compute_provider（批量计算写入 c1_market.technical_indicator）；sleeve alpha 择时；reversal.py 复用 _boll_bands
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# I1 --> A3
# A1 -.->|断点| ATR
# A1 -.->|断点| BOLL
# A1 -.->|断点| KC
# A1 -.->|断点| HV
# A2 -.->|断点| ATR
# A2 -.->|断点| KC
# A3 -.->|断点| BOLL
# ATR --> O1
# BOLL --> O1
# KC --> O1
# HV --> O1
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
