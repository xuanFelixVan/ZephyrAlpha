# [BLUEPRINT] MOD-L02-019 | (pending)
# [MODULE] zephyr.factor.technical_indicators.momentum
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.technical_indicators.indicator_base; pandas(pip); numpy(pip)
# [CONSUMERS] zephyr.data.implementations.internal_compute_provider（包级 autodiscover 动态接线：internal_compute_provider L545/L1113 延迟导入本包+注册表消费）; sleeve alpha 择时
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 动量类指标 31 个，纯自实现 pandas/numpy；compute→DataFrame 多列输出
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] compute 输入空 DataFrame→返回空 DataFrame 不抛；输入缺列→ValueError
# [TESTS] tests/zephyr/factor/technical_indicators/test_momentum.py
# [A_module] module_id=MOD-L02-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

动量类技术指标（31 个；2026-09-14 A股标配批+3、批2a +1、批2b +8、批6 +9）。

指标清单：KDJ/RSI/WR/ROC/MTM/CMF/UOS/AO/CMO/StochRSI/BIAS/PSY/LWR/DPO/TSI/SMI/FISHER/KST/CONNORSRSI/QQE/STC/RVGI/STOCH/AROON/AROONOSC/BOP/PPO/APO/DX/BRAR/CR

算法对齐通达信：
  - KDJ K/D 用通达信 SMA(X,N,1)=ewm(alpha=1/N, adjust=False)（非标准 EMA alpha=2/(N+1)）
  - RSI 用通达信 SMA 平滑：RSI=SMA(up)/SMA(|Δ|)×100
  - StochRSI 依赖 RSI 计算，复用 _rsi 辅助函数
  - LWR 为威廉 %R 的 SMA 平滑版（慢速威廉），方向与 KDJ 相反（超卖=高值）
  - PSY 首行无前值记 NaN，不冒充"未上涨"

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
# - id: BIAS
#   name_zh: 乖离率BIAS 6/12/24
#   name_en: BIAS
#   intro: 收盘价偏离均线的百分比，度量短期超买超卖（A股行情软件标配）
#   formula: BIAS_N=(C−MA(C,N))/MA(C,N)×100，N=6/12/24
#   code: momentum.py 尾部 BIAS 类
#   registry: 指标表: 有bias_6/bias_12/bias_24列 但代码未读表（本模块即指标计算实现）
#   is_break: true
# - id: PSY
#   name_zh: 心理线PSY 12+MA6
#   name_en: PSY
#   intro: 近 N 日上涨天数占比，度量市场情绪偏多偏空（A股行情软件标配）
#   formula: PSY=COUNT(C>REF(C,1),12)/12×100；PSYMA=MA(PSY,6)；首行无前值=NaN
#   code: momentum.py 尾部 PSY 类
#   registry: 指标表: 有psy_12/psy_ma6列 但代码未读表（本模块即指标计算实现）
#   is_break: true
# - id: DPO
#   name_zh: 区间震荡DPO 20
#   name_en: DPO
#   intro: 收盘价减去前置均线，剔除趋势后看短期循环摆动（批2a）
#   formula: DPO=C−REF(MA(C,N),N/2+1)
#   code: momentum.py 尾部 DPO 类
#   registry: 指标表: 有dpo_20列（本模块即指标计算实现）
#   is_break: true
# - id: LWR
#   name_zh: 慢速威廉LWR 9,3,3
#   name_en: LWR
#   intro: 威廉 %R 的双重 SMA 平滑版，方向与 KDJ 相反（超卖=高值）
#   formula: RSV=(HH9−C)/(HH9−LL9)×100 → LWR1=SMA(RSV,3,1) → LWR2=SMA(LWR1,3,1)
#   code: momentum.py 尾部 LWR 类
#   registry: 指标表: 有lwr_1/lwr_2列 但代码未读表（本模块即指标计算实现）
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
#   name_zh: 动量指标 DataFrame（31指标多列）
#   name_en: momentum indicators DataFrame
#   intro: KDJ/RSI/WR/ROC/MTM/CMF/UOS/AO/CMO/StochRSI/BIAS/PSY/LWR/DPO 共31个动量指标的多列输出，index 与输入对齐
#   invariant: 输出列严格等于各 meta.output_columns（kdj_k/d/j、rsi_6/12/24、wr_14、roc_12、mtm_12/mtmma_12、cmf_20、uos、ao、cmo_14、stochrsi、bias_6/12/24、psy_12/psy_ma6、lwr_1/lwr_2、dpo_20、tsi、smi/smi_signal、fisher_9/fisher_sig9、kst/kst_signal、crsi、qqe_14/qqe_rsi_ma、stc、rvgi_10/rvgi_sig、stoch_fastk/fastd/slowk/slowd、aroon_up/down、aroonosc、bop、ppo、apo、dx_14、ar_26/br_26、cr_26）
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
# A1 -.->|断点| BIAS
# A1 -.->|断点| PSY
# A1 -.->|断点| LWR
# A1 -.->|断点| DPO
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
from zephyr.factor.technical_indicators.trend import _di  # noqa: PLC0415 — DX 复用 DMI 的 ±DI

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


@TechnicalIndicatorRegistry.register
class BIAS(TechnicalIndicatorBase):
    """乖离率（Bias Ratio，A股行情软件标配 N=6/12/24）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="bias",
        name="乖离率",
        category="momentum",
        output_columns=["bias_6", "bias_12", "bias_24"],
        input_columns=["close"],
        params={"periods": [6, 12, 24]},
        version="1.0.0",
        description="BIAS_N=(C−MA(C,N))/MA(C,N)×100，正=收盘价在均线上方（超买倾向），负=下方",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        close = data["close"]
        out = {}
        for n in params["periods"]:
            ma = close.rolling(window=n).mean()
            out[f"bias_{n}"] = (close - ma) / ma * 100
        return pd.DataFrame(out, index=data.index)


@TechnicalIndicatorRegistry.register
class PSY(TechnicalIndicatorBase):
    """心理线（Psychological Line，A股行情软件标配 12+MA6）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="psy",
        name="心理线",
        category="momentum",
        output_columns=["psy_12", "psy_ma6"],
        input_columns=["close"],
        params={"period": 12, "ma_period": 6},
        version="1.0.0",
        description="PSY=COUNT(C>REF(C,1),12)/12×100；PSYMA=MA(PSY,6)；首行无前值记 NaN",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n, ma_n = params["period"], params["ma_period"]
        delta = data["close"].diff()
        up = (delta > 0).astype(float)
        up[delta.isna()] = np.nan  # 首行无前值，不计入分母也不冒充"未上涨"
        psy = up.rolling(window=n).mean() * 100
        psy_ma = psy.rolling(window=ma_n).mean()
        return pd.DataFrame({"psy_12": psy, "psy_ma6": psy_ma}, index=data.index)


@TechnicalIndicatorRegistry.register
class LWR(TechnicalIndicatorBase):
    """慢速威廉（LW&R，威廉 %R 的双重 SMA 平滑，方向与 KDJ 相反：超卖=高值）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="lwr",
        name="慢速威廉",
        category="momentum",
        output_columns=["lwr_1", "lwr_2"],
        input_columns=["high", "low", "close"],
        params={"period": 9, "k_smooth": 3, "d_smooth": 3},
        version="1.0.0",
        description="RSV=(HH9−C)/(HH9−LL9)×100；LWR1=SMA(RSV,3,1)；LWR2=SMA(LWR1,3,1)，对齐通达信",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n, k_n, d_n = params["period"], params["k_smooth"], params["d_smooth"]
        hh = data["high"].rolling(window=n).max()
        ll = data["low"].rolling(window=n).min()
        # 威廉口径：分子为 HH−C（与 KDJ 的 C−LL 相反），高值=接近最低价=超卖
        rsv = (hh - data["close"]) / (hh - ll) * 100
        lwr1 = _sma(rsv, k_n)
        lwr2 = _sma(lwr1, d_n)
        return pd.DataFrame({"lwr_1": lwr1, "lwr_2": lwr2}, index=data.index)


@TechnicalIndicatorRegistry.register
class DPO(TechnicalIndicatorBase):
    """区间震荡（Detrended Price Oscillator，通达信口径）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="dpo",
        name="区间震荡",
        category="momentum",
        output_columns=["dpo_20"],
        input_columns=["close"],
        params={"period": 20},
        version="1.0.0",
        description="DPO=C−REF(MA(C,N),N/2+1)，剔除趋势后的短期震荡摆动指标",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        ma = data["close"].rolling(window=n).mean()
        dpo = data["close"] - ma.shift(n // 2 + 1)
        return pd.DataFrame({f"dpo_{n}": dpo}, index=data.index)


@TechnicalIndicatorRegistry.register
class TSI(TechnicalIndicatorBase):
    """真实强度指数（True Strength Index，25/13）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="tsi",
        name="真实强度指数",
        category="momentum",
        output_columns=["tsi"],
        input_columns=["close"],
        params={"long": 25, "short": 13},
        version="1.0.0",
        description="TSI=100×EMA_s(EMA_l(ΔC))/EMA_s(EMA_l(|ΔC|))，双重平滑动量，零线穿越看趋势",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        long_n, short_n = params["long"], params["short"]
        pc = data["close"].diff()
        num = pc.ewm(span=long_n, adjust=False).mean().ewm(span=short_n, adjust=False).mean()
        den = pc.abs().ewm(span=long_n, adjust=False).mean().ewm(span=short_n, adjust=False).mean()
        tsi = 100 * num / den
        return pd.DataFrame({"tsi": tsi}, index=data.index)


@TechnicalIndicatorRegistry.register
class SMI(TechnicalIndicatorBase):
    """随机动量指数（Stochastic Momentum Index，10/3/3）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="smi",
        name="随机动量指数",
        category="momentum",
        output_columns=["smi", "smi_signal"],
        input_columns=["high", "low", "close"],
        params={"period": 10, "smooth1": 3, "smooth2": 3, "signal": 3},
        version="1.0.0",
        description="SMI=100×EMAEMA(C−中点)/(0.5×EMAEMA(HH−LL))；signal=EMA(SMI,3)",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n, s1, s2, sig = params["period"], params["smooth1"], params["smooth2"], params["signal"]
        hh = data["high"].rolling(window=n).max()
        ll = data["low"].rolling(window=n).min()
        mid = 0.5 * (hh + ll)
        sh = (data["close"] - mid).ewm(span=s1, adjust=False).mean().ewm(span=s2, adjust=False).mean()
        sm = (0.5 * (hh - ll)).ewm(span=s1, adjust=False).mean().ewm(span=s2, adjust=False).mean()
        smi = 100 * sh / sm
        smi_signal = smi.ewm(span=sig, adjust=False).mean()
        return pd.DataFrame({"smi": smi, "smi_signal": smi_signal}, index=data.index)


@TechnicalIndicatorRegistry.register
class FISHER(TechnicalIndicatorBase):
    """费雪变换（Fisher Transform，9）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="fisher",
        name="费雪变换",
        category="momentum",
        output_columns=["fisher_9", "fisher_sig9"],
        input_columns=["high", "low"],
        params={"period": 9},
        version="1.0.0",
        description="norm=2(HL2−LLn)/(HHn−LLn)−1；value=0.66norm+0.67prev；F=0.5ln((1+v)/(1−v))+0.5prev，递推",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        hl2 = 0.5 * (data["high"] + data["low"])
        hh = hl2.rolling(window=n).max()
        ll = hl2.rolling(window=n).min()
        norm = (2 * (hl2 - ll) / (hh - ll) - 1).clip(-0.999, 0.999)
        norm_v = norm.to_numpy()
        m = len(norm_v)
        value = np.zeros(m)
        fisher = np.full(m, np.nan)
        for i in range(m):
            if np.isnan(norm_v[i]):
                continue
            pv = value[i - 1] if i > 0 and not np.isnan(fisher[i - 1]) else 0.0
            value[i] = 0.66 * norm_v[i] + 0.67 * pv
            v = max(-0.999, min(0.999, value[i]))
            pf = fisher[i - 1] if i > 0 and not np.isnan(fisher[i - 1]) else 0.0
            fisher[i] = 0.5 * np.log((1 + v) / (1 - v)) + 0.5 * pf
        fisher_s = pd.Series(fisher, index=data.index)
        return pd.DataFrame({"fisher_9": fisher_s, "fisher_sig9": fisher_s.shift(1)}, index=data.index)


@TechnicalIndicatorRegistry.register
class KST(TechnicalIndicatorBase):
    """确知量指标（Know Sure Thing）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="kst",
        name="确知量",
        category="momentum",
        output_columns=["kst", "kst_signal"],
        input_columns=["close"],
        params={"roc": [10, 15, 20, 30], "sma": [10, 10, 10, 15], "weights": [1, 2, 3, 4], "signal": 9},
        version="1.0.0",
        description="KST=Σwᵢ×SMA(ROC(nᵢ),sᵢ)（1/2/3/4 权重）；signal=SMA(KST,9)",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        rocs, smas, weights, sig = params["roc"], params["sma"], params["weights"], params["signal"]
        kst = pd.Series(0.0, index=data.index)
        for rc, sm, w in zip(rocs, smas, weights):
            kst = kst + w * (data["close"].pct_change(rc) * 100).rolling(window=sm).mean()
        kst_signal = kst.rolling(window=sig).mean()
        return pd.DataFrame({"kst": kst, "kst_signal": kst_signal}, index=data.index)


@TechnicalIndicatorRegistry.register
class CONNORSRSI(TechnicalIndicatorBase):
    """Connors RSI（3/2/100 三分量合成）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="connorsrsi",
        name="ConnorsRSI",
        category="momentum",
        output_columns=["crsi"],
        input_columns=["close"],
        params={"rsi_period": 3, "streak_rsi": 2, "rank_period": 100},
        version="1.0.0",
        description="CRSI=(RSI(C,3)+RSI(连涨跌天数,2)+PercentRank(1日收益,100))/3，短周期均值回归摆动",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        rsi_n, streak_n, rank_n = params["rsi_period"], params["streak_rsi"], params["rank_period"]
        close = data["close"]
        rsi_1 = _rsi(close, rsi_n)
        # 连涨/连跌天数序列（涨=+1 递增，跌=-1 递减，平/首行=0）；np 数组避免 Series 位置索引警告/标签错位
        delta = close.diff()
        sign = np.sign(delta).to_numpy(dtype=float)
        streak = np.zeros(len(close))
        for i in range(1, len(close)):
            if np.isnan(sign[i]) or sign[i] == 0:
                streak[i] = 0
            elif sign[i] == sign[i - 1] and streak[i - 1] != 0:
                streak[i] = streak[i - 1] + sign[i]
            else:
                streak[i] = sign[i]
        streak_s = pd.Series(streak, index=data.index)
        rsi_streak = _rsi(streak_s, streak_n)
        ret = close.pct_change()
        pct_rank = ret.rolling(window=rank_n).apply(
            lambda x: (x < x[-1]).sum() / (len(x) - 1) * 100, raw=True
        )
        crsi = (rsi_1 + rsi_streak + pct_rank) / 3
        return pd.DataFrame({"crsi": crsi}, index=data.index)


@TechnicalIndicatorRegistry.register
class QQE(TechnicalIndicatorBase):
    """量化质化估计（Quantitative Qualitative Estimation，14/5/27×4.236）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="qqe",
        name="QQE",
        category="momentum",
        output_columns=["qqe_14", "qqe_rsi_ma"],
        input_columns=["close"],
        params={"period": 14, "smooth": 5, "atr_period": 27, "factor": 4.236},
        version="1.0.0",
        description="RSI 双 EMA 平滑后按 DAR 跟踪带逐 bar 递推；QQE 线与 RSI_MA 交叉为信号",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n, smooth_n, atr_n, factor = params["period"], params["smooth"], params["atr_period"], params["factor"]
        rsi = _rsi(data["close"], n)
        rsi_ma = rsi.ewm(span=smooth_n, adjust=False).mean()
        dar = (
            (rsi_ma - rsi_ma.shift(1)).abs().ewm(span=atr_n, adjust=False).mean().ewm(
                span=atr_n, adjust=False
            ).mean()
            * factor
        )
        rm = rsi_ma.to_numpy()
        dv = dar.to_numpy()
        m = len(rm)
        qqe = np.full(m, np.nan)
        long_band = np.nan
        short_band = np.nan
        trend = 1.0
        for i in range(m):
            if np.isnan(rm[i]) or np.isnan(dv[i]):
                continue
            if np.isnan(long_band):
                long_band = rm[i] - dv[i]
                short_band = rm[i] + dv[i]
                qqe[i] = long_band
                continue
            new_long = rm[i] - dv[i]
            new_short = rm[i] + dv[i]
            long_band = new_long if (new_long > long_band or rm[i - 1] < long_band) else long_band
            short_band = new_short if (new_short < short_band or rm[i - 1] > short_band) else short_band
            prev_trend = trend
            if prev_trend == 1.0 and rm[i] < long_band:
                trend = -1.0
            elif prev_trend == -1.0 and rm[i] > short_band:
                trend = 1.0
            qqe[i] = long_band if trend == 1.0 else short_band
        return pd.DataFrame({"qqe_14": pd.Series(qqe, index=data.index), "qqe_rsi_ma": rsi_ma}, index=data.index)


@TechnicalIndicatorRegistry.register
class STC(TechnicalIndicatorBase):
    """Schaff 趋势周期（Schaff Trend Cycle，23/50/10/3）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="stc",
        name="Schaff趋势周期",
        category="momentum",
        output_columns=["stc"],
        input_columns=["close"],
        params={"fast": 23, "slow": 50, "cycle": 10, "smooth": 3},
        version="1.0.0",
        description="MACD(23,50)→双随机(10)→EMA(3) 平滑，0-100 循环摆动",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        fast_n, slow_n, cyc, sm = params["fast"], params["slow"], params["cycle"], params["smooth"]
        macd = data["close"].ewm(span=fast_n, adjust=False).mean() - data["close"].ewm(
            span=slow_n, adjust=False
        ).mean()
        macd_min = macd.rolling(window=cyc).min()
        macd_max = macd.rolling(window=cyc).max()
        k1 = 100 * (macd - macd_min) / (macd_max - macd_min)
        d1 = k1.ewm(span=sm, adjust=False).mean()
        d1_min = d1.rolling(window=cyc).min()
        d1_max = d1.rolling(window=cyc).max()
        k2 = 100 * (d1 - d1_min) / (d1_max - d1_min)
        stc = k2.ewm(span=sm, adjust=False).mean()
        return pd.DataFrame({"stc": stc}, index=data.index)


@TechnicalIndicatorRegistry.register
class RVGI(TechnicalIndicatorBase):
    """相对活力指数（Relative Vigor Index，10/4）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="rvgi",
        name="相对活力指数",
        category="momentum",
        output_columns=["rvgi_10", "rvgi_sig"],
        input_columns=["open", "high", "low", "close"],
        params={"period": 10, "signal": 4},
        version="1.0.0",
        description="num=C−O、den=H−L 经 1-2-2-1 加权后再 SMA(10)：RVGI=SMA(w:num)/SMA(w:den)；sig=SMA(RVGI,4)",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n, sig_n = params["period"], params["signal"]
        w = np.array([1.0, 2.0, 2.0, 1.0]) / 6.0

        def swma(series: pd.Series) -> pd.Series:
            return series.rolling(window=4).apply(lambda x: float(np.dot(x, w)), raw=True)

        num = swma(data["close"] - data["open"]).rolling(window=n).mean()
        den = swma(data["high"] - data["low"]).rolling(window=n).mean()
        rvgi = num / den
        rvgi_signal = rvgi.rolling(window=sig_n).mean()
        return pd.DataFrame({"rvgi_10": rvgi, "rvgi_sig": rvgi_signal}, index=data.index)


@TechnicalIndicatorRegistry.register
class STOCH(TechnicalIndicatorBase):
    """经典随机振荡器（TA-Lib STOCH+STOCHF 合一，5/3/3/3）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="stoch",
        name="随机振荡器",
        category="momentum",
        output_columns=["stoch_fastk", "stoch_fastd", "stoch_slowk", "stoch_slowd"],
        input_columns=["high", "low", "close"],
        params={"fastk": 5, "fastd": 3, "slowk": 3, "slowd": 3},
        version="1.0.0",
        description="FastK=100(C−LL)/(HH−LL)；fastd=SMA(fastk,3)；slowk=SMA(fastk,3)；slowd=SMA(slowk,3)（TA-Lib 口径，HH=LL 时 FastK 取 50）",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        fk_n, fd_n, sk_n, sd_n = params["fastk"], params["fastd"], params["slowk"], params["slowd"]
        hh = data["high"].rolling(window=fk_n).max()
        ll = data["low"].rolling(window=fk_n).min()
        rng = hh - ll
        # HH=LL（一字板等）时 FastK 取中性 50；预热 NaN 保持 NaN
        fastk = (100 * (data["close"] - ll) / rng).where(rng != 0, 50.0)
        fastd = fastk.rolling(window=fd_n).mean()
        slowk = fastk.rolling(window=sk_n).mean()
        slowd = slowk.rolling(window=sd_n).mean()
        return pd.DataFrame(
            {"stoch_fastk": fastk, "stoch_fastd": fastd, "stoch_slowk": slowk, "stoch_slowd": slowd},
            index=data.index,
        )


@TechnicalIndicatorRegistry.register
class AROON(TechnicalIndicatorBase):
    """阿隆指标（Aroon Up/Down，14）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="aroon",
        name="阿隆指标",
        category="momentum",
        output_columns=["aroon_up", "aroon_down"],
        input_columns=["high", "low"],
        params={"period": 14},
        version="1.0.0",
        description="AroonUp=100×(N−距最高价根数)/N；AroonDown=100×(N−距最低价根数)/N",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        # 窗口 [t−n..t]（n+1 个）内 argmax/argmin 位置 pos：距当前根数 = n−pos
        # AroonUp=100×(N−距最高根数)/N = 100×pos_argmax/N（新 High→pos=n→100）
        pos_hh = data["high"].rolling(window=n + 1).apply(np.argmax, raw=True)
        pos_ll = data["low"].rolling(window=n + 1).apply(np.argmin, raw=True)
        aroon_up = 100 * pos_hh / n
        aroon_down = 100 * pos_ll / n
        return pd.DataFrame({"aroon_up": aroon_up, "aroon_down": aroon_down}, index=data.index)


@TechnicalIndicatorRegistry.register
class AROONOSC(TechnicalIndicatorBase):
    """阿隆震荡器（Aroon Oscillator，14）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="aroonosc",
        name="阿隆震荡器",
        category="momentum",
        output_columns=["aroonosc"],
        input_columns=["high", "low"],
        params={"period": 14},
        version="1.0.0",
        description="AroonOsc=AroonUp−AroonDown，值域 [-100,100]，上穿零线看多",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        pos_hh = data["high"].rolling(window=n + 1).apply(np.argmax, raw=True)
        pos_ll = data["low"].rolling(window=n + 1).apply(np.argmin, raw=True)
        osc = 100 * (pos_hh - pos_ll) / n
        return pd.DataFrame({"aroonosc": osc}, index=data.index)


@TechnicalIndicatorRegistry.register
class BOP(TechnicalIndicatorBase):
    """力量平衡（Balance of Power，16 平滑）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="bop",
        name="力量平衡",
        category="momentum",
        output_columns=["bop"],
        input_columns=["open", "high", "low", "close"],
        params={"period": 16},
        version="1.0.0",
        description="原始值=(C−O)/(H−L)（H=L 取 0），SMA 16 平滑；值域 [-1,1] 度量买卖力量",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        o, h, l, c = data["open"], data["high"], data["low"], data["close"]
        raw = ((c - o) / (h - l)).where(h != l, 0.0)
        bop = raw.rolling(window=n).mean()
        return pd.DataFrame({"bop": bop}, index=data.index)


@TechnicalIndicatorRegistry.register
class PPO(TechnicalIndicatorBase):
    """百分比价格振荡器（Percentage Price Oscillator，12/26）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="ppo",
        name="百分比价格振荡器",
        category="momentum",
        output_columns=["ppo"],
        input_columns=["close"],
        params={"fast": 12, "slow": 26},
        version="1.0.0",
        description="PPO=(EMA12−EMA26)/EMA26×100，MACD 的百分比归一变体，跨标的可比",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        fast_n, slow_n = params["fast"], params["slow"]
        ema_fast = data["close"].ewm(span=fast_n, adjust=False).mean()
        ema_slow = data["close"].ewm(span=slow_n, adjust=False).mean()
        ppo = (ema_fast - ema_slow) / ema_slow * 100
        return pd.DataFrame({"ppo": ppo}, index=data.index)


@TechnicalIndicatorRegistry.register
class APO(TechnicalIndicatorBase):
    """绝对价格振荡器（Absolute Price Oscillator，12/26）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="apo",
        name="绝对价格振荡器",
        category="momentum",
        output_columns=["apo"],
        input_columns=["close"],
        params={"fast": 12, "slow": 26},
        version="1.0.0",
        description="APO=EMA12−EMA26（MACD DIF 同式），绝对差值口径（TA-Lib APO）",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        fast_n, slow_n = params["fast"], params["slow"]
        apo = data["close"].ewm(span=fast_n, adjust=False).mean() - data["close"].ewm(
            span=slow_n, adjust=False
        ).mean()
        return pd.DataFrame({"apo": apo}, index=data.index)


@TechnicalIndicatorRegistry.register
class DX(TechnicalIndicatorBase):
    """动向指数（Directional Movement Index，14，复用 DMI 的 ±DI）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="dx",
        name="动向指数",
        category="momentum",
        output_columns=["dx_14"],
        input_columns=["high", "low", "close"],
        params={"period": 14},
        version="1.0.0",
        description="DX=100×|+DI−−DI|/(+DI+−DI)，ADX 的未平滑原料（复用 trend._di）",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        pdi, mdi = _di(data["high"], data["low"], data["close"], n)
        dx = 100 * (pdi - mdi).abs() / (pdi + mdi).where((pdi + mdi) != 0)
        return pd.DataFrame({f"dx_{n}": dx}, index=data.index)


@TechnicalIndicatorRegistry.register
class BRAR(TechnicalIndicatorBase):
    """人气意愿指标（BRAR，通达信标配 26）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="brar",
        name="人气意愿指标",
        category="momentum",
        output_columns=["ar_26", "br_26"],
        input_columns=["open", "high", "low", "close"],
        params={"period": 26},
        version="1.0.0",
        description="AR=Σ(H−O)/Σ(O−L)×100（开盘基准人气）；BR=Σmax(0,H−Cp)/Σmax(0,Cp−L)×100（前收基准意愿）",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        o, h, l = data["open"], data["high"], data["low"]
        cp = data["close"].shift(1)
        ar = (h - o).rolling(window=n).sum() / (o - l).replace(0, np.nan).rolling(window=n).sum() * 100
        br_num = (h - cp).clip(lower=0).rolling(window=n).sum()
        br_den = (cp - l).clip(lower=0).replace(0, np.nan).rolling(window=n).sum()
        br = br_num / br_den * 100
        return pd.DataFrame({"ar_26": ar, "br_26": br}, index=data.index)


@TechnicalIndicatorRegistry.register
class CR(TechnicalIndicatorBase):
    """能量指标（CR，中间意愿，通达信标配 26）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="cr",
        name="能量指标",
        category="momentum",
        output_columns=["cr_26"],
        input_columns=["high", "low"],
        params={"period": 26},
        version="1.0.0",
        description="MID=(H+L)/2 前值基准；CR=Σmax(0,H−MIDp)/Σmax(0,MIDp−L)×100（带状能量线）",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        h, l = data["high"], data["low"]
        mid = (h + l) / 2
        mid_prev = mid.shift(1)
        up = (h - mid_prev).clip(lower=0)
        dn = (mid_prev - l).clip(lower=0)
        cr = up.rolling(window=n).sum() / dn.replace(0, np.nan).rolling(window=n).sum() * 100
        return pd.DataFrame({f"cr_{n}": cr}, index=data.index)
