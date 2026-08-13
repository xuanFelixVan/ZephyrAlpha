# [BLUEPRINT] MOD-L02-019 | (pending)
# [MODULE] zephyr.factor.technical_indicators.momentum
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.technical_indicators.indicator_base; pandas(pip); numpy(pip)
# [CONSUMERS] zephyr.data.implementations.internal_compute_provider; sleeve alpha 择时
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 动量类指标 10 个，纯自实现 pandas/numpy；compute→DataFrame 多列输出
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] compute 输入空 DataFrame→返回空 DataFrame 不抛；输入缺列→ValueError
# [TESTS] tests/zephyr/factor/technical_indicators/test_momentum.py
# [A_module] module_id=MOD-L02-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

动量类技术指标（10 个，v1.0.0 全部施工完成）。

指标清单：KDJ/RSI/WR/ROC/MTM/CMF/UOS/AO/CMO/StochRSI

算法对齐通达信：
  - KDJ K/D 用通达信 SMA(X,N,1)=ewm(alpha=1/N, adjust=False)（非标准 EMA alpha=2/(N+1)）
  - RSI 用通达信 SMA 平滑：RSI=SMA(up)/SMA(|Δ|)×100
  - StochRSI 依赖 RSI 计算，复用 _rsi 辅助函数

设计文档：16_technical_indicator_catalog.md §2.2

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 行情OHLCV数据 DataFrame
#   fields: high/low/close/volume 列（各指标按 meta.input_columns 取用）
#   code: compute(data: pd.DataFrame)
# 层: 指标
# - id: KDJ
#   name_zh: 随机指标KDJ 9,3,3
#   name_en: KDJ
#   intro: 用最高最低价衡量收盘价所处位置，判断超买超卖
#   formula: RSV=(C-LL9)/(HH9-LL9)×100 → K=SMA(RSV,3,1) → D=SMA(K,3,1) → J=3K-2D（SMA=ewm alpha=1/N 对齐通达信）
#   code: momentum.py L84-96
#   registry: 指标表: 有kdj_k/kdj_d/kdj_j列 但代码未读表（本模块即指标计算实现）
#   is_break: true
# - id: RSI
#   name_zh: 相对强弱RSI 6/12/24 + 随机RSI
#   name_en: RSI/StochRSI
#   intro: 涨跌幅平滑比值衡量多空力量，StochRSI 再对 RSI 做归一化
#   formula: RSI=100×SMA(up,N)/(SMA(up,N)+SMA(down,N))；StochRSI=(RSI-min14(RSI))/(max14(RSI)-min14(RSI))
#   code: momentum.py L114-121 + L337-347
#   registry: 指标表: 有rsi_6/rsi_12/rsi_24/stochrsi列 但代码未读表（本模块即指标计算实现）
#   is_break: true
# - id: CMF
#   name_zh: 蔡金资金流CMF 20
#   name_en: CMF
#   intro: 收盘价在当日振幅中的位置乘以成交量，度量资金流入流出
#   formula: CLV=(2C-H-L)/(H-L)（H=L时取0）→ CMF=Σ20(CLV×V)/Σ20(V)
#   code: momentum.py L217-229
#   registry: 指标表: 有cmf_20列 但代码未读表（本模块即指标计算实现）
#   is_break: true
# - id: UOS
#   name_zh: 终极指标UOS 7/14/28
#   name_en: UOS
#   intro: 三个周期买卖压力加权合成，减少单一周期假信号
#   formula: BP=C-min(L,Cp)；TR=max(H,Cp)-min(L,Cp)；AvgN=ΣN(BP)/ΣN(TR)；UOS=(4Avg7+2Avg14+Avg28)/7×100
#   code: momentum.py L247-263
#   registry: 指标表: 有uos列 但代码未读表（本模块即指标计算实现）
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
#   name_zh: ② 通达信SMA平滑
#   name_en: _sma
#   intro: 通达信 SMA(X,N,1)，alpha=1/N 的指数平滑，KDJ的K/D和RSI都靠它
#   desc: series.ewm(alpha=1/N, adjust=False).mean()，与标准 EMA(alpha=2/(N+1)) 不同
#   inputs: I1
#   outputs: 平滑后 Series
# - id: A3
#   name_zh: ③ RSI核心计算
#   name_en: _rsi
#   intro: 涨跌幅裁剪后双向 SMA 平滑求比值，RSI 与 StochRSI 复用
#   desc: delta=close.diff() → up/down clip(0) → 100×_sma(up)/(_sma(up)+_sma(down))
#   inputs: I1 A2
#   outputs: RSI Series
# 层: 输出
# - id: O1
#   name_zh: 动量指标 DataFrame（10指标多列）
#   name_en: momentum indicators DataFrame
#   intro: KDJ/RSI/WR/ROC/MTM/CMF/UOS/AO/CMO/StochRSI 共10个动量指标的多列输出，index 与输入对齐
#   invariant: 输出列严格等于各 meta.output_columns（kdj_k/d/j、rsi_6/12/24、wr_14、roc_12、mtm_12/mtmma_12、cmf_20、uos、ao、cmo_14、stochrsi）
#   downstream: zephyr.data.implementations.internal_compute_provider（批量计算写入 c1_market.technical_indicator）；sleeve alpha 择时
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# I1 --> A3
# A2 --> A3
# A1 -.->|断点| KDJ
# A1 -.->|断点| RSI
# A1 -.->|断点| CMF
# A1 -.->|断点| UOS
# A2 -.->|断点| KDJ
# A2 -.->|断点| RSI
# A3 -.->|断点| RSI
# KDJ --> O1
# RSI --> O1
# CMF --> O1
# UOS --> O1
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from zephyr.factor.technical_indicators.indicator_base import (
    TechnicalIndicatorBase,
    TechnicalIndicatorMeta,
    TechnicalIndicatorRegistry,
)

# ---------------------------------------------------------------------------
# 模块级辅助函数
# ---------------------------------------------------------------------------


def _sma(series: pd.Series, n: int) -> pd.Series:
    """通达信 SMA(X,N,1) = (X + (N-1)×prev) / N。

    等价于 ewm(alpha=1/N, adjust=False)。
    注意：与标准 EMA(span=N) 的 alpha=2/(N+1) 不同——通达信 SMA 的 alpha=1/N。
    用于 KDJ 的 K/D 平滑和 RSI 的涨跌平滑。
    """
    return series.ewm(alpha=1 / n, adjust=False).mean()


def _rsi(close: pd.Series, n: int) -> pd.Series:
    """RSI 相对强弱指标，对齐通达信 SMA 平滑。

    通达信: RSI = SMA(MAX(C-LC,0),N,1) / SMA(ABS(C-LC),N,1) × 100
    等价于: RSI = avg_up / (avg_up + avg_down) × 100
    """
    delta = close.diff()
    up = delta.clip(lower=0)
    down = (-delta).clip(lower=0)
    avg_up = _sma(up, n)
    avg_down = _sma(down, n)
    return 100 * avg_up / (avg_up + avg_down)


@TechnicalIndicatorRegistry.register
class KDJ(TechnicalIndicatorBase):
    """随机指标（Stochastic Oscillator KDJ）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="kdj",
        name="随机指标",
        category="momentum",
        output_columns=["kdj_k", "kdj_d", "kdj_j"],
        input_columns=["high", "low", "close"],
        params={"period": 9, "k_smooth": 3, "d_smooth": 3},
        version="1.0.0",
        description="RSV=(C-Ln)/(Hn-Ln)×100; K=SMA(RSV); D=SMA(K); J=3K-2D，SMA 对齐通达信",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n, k_n, d_n = params["period"], params["k_smooth"], params["d_smooth"]
        hh = data["high"].rolling(window=n).max()
        ll = data["low"].rolling(window=n).min()
        rsv = (data["close"] - ll) / (hh - ll) * 100
        k = _sma(rsv, k_n)
        d = _sma(k, d_n)
        j = 3 * k - 2 * d
        return pd.DataFrame({"kdj_k": k, "kdj_d": d, "kdj_j": j}, index=data.index)


@TechnicalIndicatorRegistry.register
class RSI(TechnicalIndicatorBase):
    """相对强弱指标（Relative Strength Index）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="rsi",
        name="相对强弱指标",
        category="momentum",
        output_columns=["rsi_6", "rsi_12", "rsi_24"],
        input_columns=["close"],
        params={"periods": [6, 12, 24]},
        version="1.0.0",
        description="RSI=SMA(up)/SMA(|Δ|)×100，SMA 平滑对齐通达信，periods=[6,12,24]",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        close = data["close"]
        result = {f"rsi_{n}": _rsi(close, n) for n in params["periods"]}
        return pd.DataFrame(result, index=data.index)


@TechnicalIndicatorRegistry.register
class WR(TechnicalIndicatorBase):
    """威廉指标（Williams %R）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="wr",
        name="威廉指标",
        category="momentum",
        output_columns=["wr_14"],
        input_columns=["high", "low", "close"],
        params={"period": 14},
        version="1.0.0",
        description="WR=(Hn-C)/(Hn-Ln)×100，0=超买 100=超卖",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        hh = data["high"].rolling(window=n).max()
        ll = data["low"].rolling(window=n).min()
        wr = (hh - data["close"]) / (hh - ll) * 100
        return pd.DataFrame({f"wr_{n}": wr}, index=data.index)


@TechnicalIndicatorRegistry.register
class ROC(TechnicalIndicatorBase):
    """变动率（Rate of Change）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="roc",
        name="变动率",
        category="momentum",
        output_columns=["roc_12"],
        input_columns=["close"],
        params={"period": 12},
        version="1.0.0",
        description="ROC=(C-Cn)/Cn×100，百分比变动率",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        roc = (data["close"] / data["close"].shift(n) - 1) * 100
        return pd.DataFrame({f"roc_{n}": roc}, index=data.index)


@TechnicalIndicatorRegistry.register
class MTM(TechnicalIndicatorBase):
    """动量指标（Momentum）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="mtm",
        name="动量指标",
        category="momentum",
        output_columns=["mtm_12", "mtmma_12"],
        input_columns=["close"],
        params={"period": 12, "ma_period": 6},
        version="1.0.0",
        description="MTM=C-Cn; MTMMA=MA(MTM,ma_period)，绝对差值非百分比",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n, ma_n = params["period"], params["ma_period"]
        mtm = data["close"] - data["close"].shift(n)
        mtmma = mtm.rolling(window=ma_n).mean()
        return pd.DataFrame({f"mtm_{n}": mtm, f"mtmma_{n}": mtmma}, index=data.index)


@TechnicalIndicatorRegistry.register
class CMF(TechnicalIndicatorBase):
    """蔡金资金流（Chaikin Money Flow）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="cmf",
        name="蔡金资金流",
        category="momentum",
        output_columns=["cmf_20"],
        input_columns=["high", "low", "close", "volume"],
        params={"period": 20},
        version="1.0.0",
        description="CLV=(2C-H-L)/(H-L); CMF=SUM(CLV×Vol)/SUM(Vol)，H=L时CLV=0",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        h, l, c, v = data["high"], data["low"], data["close"], data["volume"]
        hl_range = h - l
        # H=L 时 CLV=0（避免除零）
        clv = ((2 * c - h - l) / hl_range).where(hl_range != 0, 0.0)
        mfv = clv * v
        cmf = mfv.rolling(window=n).sum() / v.rolling(window=n).sum()
        return pd.DataFrame({f"cmf_{n}": cmf}, index=data.index)


@TechnicalIndicatorRegistry.register
class UOS(TechnicalIndicatorBase):
    """终极指标（Ultimate Oscillator）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="uos",
        name="终极指标",
        category="momentum",
        output_columns=["uos"],
        input_columns=["high", "low", "close"],
        params={"p1": 7, "p2": 14, "p3": 28},
        version="1.0.0",
        description="UOS=(4×Avg7+2×Avg14+1×Avg28)/7×100，Avg=SUM(BP)/SUM(TR)",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        p1, p2, p3 = params["p1"], params["p2"], params["p3"]
        h, l, c = data["high"], data["low"], data["close"]
        cp = c.shift(1)
        # BP = Close - min(Low, PrevClose)
        bp = c - pd.concat([l, cp], axis=1).min(axis=1)
        # TR = max(High, PrevClose) - min(Low, PrevClose)
        tr = pd.concat([h, cp], axis=1).max(axis=1) - pd.concat([l, cp], axis=1).min(axis=1)
        avg1 = bp.rolling(window=p1).sum() / tr.rolling(window=p1).sum()
        avg2 = bp.rolling(window=p2).sum() / tr.rolling(window=p2).sum()
        avg3 = bp.rolling(window=p3).sum() / tr.rolling(window=p3).sum()
        uos = (4 * avg1 + 2 * avg2 + 1 * avg3) / 7 * 100
        return pd.DataFrame({"uos": uos}, index=data.index)


@TechnicalIndicatorRegistry.register
class AO(TechnicalIndicatorBase):
    """震荡指标（Awesome Oscillator）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="ao",
        name="震荡指标",
        category="momentum",
        output_columns=["ao"],
        input_columns=["high", "low"],
        params={"fast": 5, "slow": 34},
        version="1.0.0",
        description="AO=MA(median,fast)-MA(median,slow)，median=(H+L)/2",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        fast, slow = params["fast"], params["slow"]
        median = (data["high"] + data["low"]) / 2
        ao = median.rolling(window=fast).mean() - median.rolling(window=slow).mean()
        return pd.DataFrame({"ao": ao}, index=data.index)


@TechnicalIndicatorRegistry.register
class CMO(TechnicalIndicatorBase):
    """钱德动量摆动（Chande Momentum Oscillator）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="cmo",
        name="钱德动量摆动",
        category="momentum",
        output_columns=["cmo_14"],
        input_columns=["close"],
        params={"period": 14},
        version="1.0.0",
        description="CMO=(Su-Sd)/(Su+Sd)×100，Su=SUM(涨),Sd=SUM(|跌|)",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        delta = data["close"].diff()
        up = delta.clip(lower=0)
        down = (-delta).clip(lower=0)
        su = up.rolling(window=n).sum()
        sd = down.rolling(window=n).sum()
        cmo = (su - sd) / (su + sd) * 100
        return pd.DataFrame({f"cmo_{n}": cmo}, index=data.index)


@TechnicalIndicatorRegistry.register
class StochRSI(TechnicalIndicatorBase):
    """随机RSI（Stochastic RSI）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="stochrsi",
        name="随机RSI",
        category="momentum",
        output_columns=["stochrsi"],
        input_columns=["close"],
        params={"rsi_period": 14, "stoch_period": 14},
        version="1.0.0",
        description="StochRSI=(RSI-min(RSI,n))/(max(RSI,n)-min(RSI,n))，复用 _rsi 辅助函数",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        rsi_n, stoch_n = params["rsi_period"], params["stoch_period"]
        rsi = _rsi(data["close"], rsi_n)
        rsi_min = rsi.rolling(window=stoch_n).min()
        rsi_max = rsi.rolling(window=stoch_n).max()
        stochrsi = (rsi - rsi_min) / (rsi_max - rsi_min)
        return pd.DataFrame({"stochrsi": stochrsi}, index=data.index)
