# [BLUEPRINT] MOD-L02-022 | (pending)
# [MODULE] zephyr.factor.technical_indicators.volatility
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.technical_indicators.indicator_base; zephyr.factor.technical_indicators.trend; pandas(pip); numpy(pip)
# [CONSUMERS] zephyr.data.implementations.internal_compute_provider（包级 autodiscover 动态接线：internal_compute_provider L545/L1113 延迟导入本包+注册表消费）; sleeve alpha 择时
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 波动类指标 18 个，纯自实现 pandas/numpy；compute→DataFrame 多列输出；复用 trend._ema
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] compute 输入空 DataFrame→返回空 DataFrame 不抛；输入缺列→ValueError
# [TESTS] tests/zephyr/factor/technical_indicators/test_volatility.py
# [A_module] module_id=MOD-L02-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

波动类技术指标（18 个，v1.0.0 全部施工完成）。

指标清单：ATR/BOLL/Keltner/Donchian/STDDEV/BandWidth/%B/HistVol/NATR/TRANGE/MASSI（批2a+2b）/PARKINSON/GARMAN_KLASS/ROGERS_SATCHELL/YANG_ZHANG（批6 学术 RV 族）/
CHOP/CVI/ULCER（2026-09-20 清欠班波2-A +3）

算法对齐通达信：
  - ATR 通达信用 MA（简单移动平均，非 Wilder's RMA）
  - BOLL/STDDEV 通达信 STD 用总体标准差 ddof=0（非 pandas 默认 ddof=1）
  - Keltner MID 用 EMA(adjust=False)，ATR 用 MA 对齐 ATR 指标
  - HistVol 用对数收益率样本标准差 ddof=1 × sqrt(252) 年化（金融行业标准）

设计文档：16_technical_indicator_catalog.md §2.3

# [ALGO_FLOW] external: docs/03_modules/_domain_factor/algo_flow/volatility.yaml
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


@TechnicalIndicatorRegistry.register
class NATR(TechnicalIndicatorBase):
    """归一化真实波幅（Normalized ATR，TA-Lib 口径）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="natr",
        name="归一化真实波幅",
        category="volatility",
        output_columns=["natr_14"],
        input_columns=["high", "low", "close"],
        params={"period": 14},
        version="1.0.0",
        description="NATR=TR/Close×100，消除价格量纲便于跨标的比较波动率（TA-Lib NATR）",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        tr = _true_range(data["high"], data["low"], data["close"])
        natr = tr / data["close"] * 100
        # MA 平滑对齐 ATR 同族口径
        natr_ma = natr.rolling(window=n).mean()
        return pd.DataFrame({f"natr_{n}": natr_ma}, index=data.index)


@TechnicalIndicatorRegistry.register
class TRANGE(TechnicalIndicatorBase):
    """真实波幅原始值（True Range，TA-Lib 口径）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="trange",
        name="真实波幅",
        category="volatility",
        output_columns=["trange"],
        input_columns=["high", "low", "close"],
        params={},
        version="1.0.0",
        description="TR=max(H-L,|H-Cp|,|L-Cp|)，首行=H-L（无前收盘）；ATR/NATR 的底层原料",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        tr = _true_range(data["high"], data["low"], data["close"])
        return pd.DataFrame({"trange": tr}, index=data.index)


@TechnicalIndicatorRegistry.register
class MASSI(TechnicalIndicatorBase):
    """质量指数（Mass Index，9/25，Donald Dorsey）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="massi",
        name="质量指数",
        category="volatility",
        output_columns=["massi_25"],
        input_columns=["high", "low"],
        params={"ema": 9, "period": 25},
        version="1.0.0",
        description="MI=Σ25[EMA9(H−L)/EMA9(EMA9(H−L))]，度量区间膨胀速率；>27 预警趋势反转",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        ema_n, n = params["ema"], params["period"]
        rng = data["high"] - data["low"]
        ema1 = rng.ewm(span=ema_n, adjust=False).mean()
        ema2 = ema1.ewm(span=ema_n, adjust=False).mean()
        ratio = ema1 / ema2
        massi = ratio.rolling(window=n).sum()
        return pd.DataFrame({f"massi_{n}": massi}, index=data.index)


@TechnicalIndicatorRegistry.register
class PARKINSON(TechnicalIndicatorBase):
    """Parkinson 波动率（1980，高低价极差估计）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="parkinson",
        name="Parkinson波动率",
        category="volatility",
        output_columns=["parkinson_20"],
        input_columns=["high", "low"],
        params={"period": 20},
        version="1.0.0",
        description="σ²=Σ[ln(H/L)]²/(4ln2·N) 开方×100；只用高低极差（Parkinson 1980, J. Bus.）",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        hl2 = np.log(data["high"] / data["low"]) ** 2
        est = hl2.rolling(window=n).sum() / (4 * np.log(2) * n)
        return pd.DataFrame({f"parkinson_{n}": np.sqrt(est) * 100}, index=data.index)


@TechnicalIndicatorRegistry.register
class GARMAN_KLASS(TechnicalIndicatorBase):
    """Garman-Klass 波动率（1980，OHLC 全用，效率≈7.4× close-to-close）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="garman_klass",
        name="Garman-Klass波动率",
        category="volatility",
        output_columns=["garman_klass_20"],
        input_columns=["open", "high", "low", "close"],
        params={"period": 20},
        version="1.0.0",
        description="σ²=mean{0.5ln²(H/L)−(2ln2−1)ln²(C/O)} 开方×100（零漂移假设，忽略隔夜跳空）",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        hl = np.log(data["high"] / data["low"])
        co = np.log(data["close"] / data["open"])
        term = 0.5 * hl**2 - (2 * np.log(2) - 1) * co**2
        est = term.rolling(window=n).mean()
        return pd.DataFrame({f"garman_klass_{n}": np.sqrt(est.clip(lower=0)) * 100}, index=data.index)


@TechnicalIndicatorRegistry.register
class ROGERS_SATCHELL(TechnicalIndicatorBase):
    """Rogers-Satchell 波动率（1991，漂移无关）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="rogers_satchell",
        name="Rogers-Satchell波动率",
        category="volatility",
        output_columns=["rogers_satchell_20"],
        input_columns=["open", "high", "low", "close"],
        params={"period": 20},
        version="1.0.0",
        description="σ²=mean{ln(H/O)ln(C/O)+ln(L/O)ln(C/O)} 开方×100（漂移独立估计）",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        ho = np.log(data["high"] / data["open"])
        lo = np.log(data["low"] / data["open"])
        co = np.log(data["close"] / data["open"])
        term = ho * co + lo * co
        est = term.rolling(window=n).mean()
        return pd.DataFrame({f"rogers_satchell_{n}": np.sqrt(est.clip(lower=0)) * 100}, index=data.index)


@TechnicalIndicatorRegistry.register
class YANG_ZHANG(TechnicalIndicatorBase):
    """Yang-Zhang 波动率（2000，处理隔夜跳空+漂移）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="yang_zhang",
        name="Yang-Zhang波动率",
        category="volatility",
        output_columns=["yang_zhang_20"],
        input_columns=["open", "high", "low", "close"],
        params={"period": 20},
        version="1.0.0",
        description="σ²=σ_o²+kσ_c²+(1−k)σ_rs²，k=0.34/(1.34+(N+1)/(N−1))；唯一同时处理隔夜跳空与漂移（YZ 2000, J. Bus.）",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        o, h, l, c = data["open"], data["high"], data["low"], data["close"]
        sigma_o2 = (np.log(o / o.shift(1)) ** 2).rolling(window=n).mean()
        sigma_c2 = (np.log(c / o) ** 2).rolling(window=n).mean()
        ho = np.log(h / o)
        lo = np.log(l / o)
        co = np.log(c / o)
        sigma_rs2 = (ho * co + lo * co).rolling(window=n).mean()
        k = 0.34 / (1.34 + (n + 1) / (n - 1))
        est = sigma_o2 + k * sigma_c2 + (1 - k) * sigma_rs2
        return pd.DataFrame({f"yang_zhang_{n}": np.sqrt(est.clip(lower=0)) * 100}, index=data.index)


# ---------------------------------------------------------------------------
# 2026-09-20 简单指标清欠班波2-A：CHOP/CVI/ULCER
# （CHOP 复用 _true_range；CVI 就地 ewm(span, adjust=False)——trend.py 本车道只读）
# ---------------------------------------------------------------------------


@TechnicalIndicatorRegistry.register
class CHOP(TechnicalIndicatorBase):
    """盘整指数（Choppiness Index，14，E.W. Dreiss）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="chop",
        name="盘整指数",
        category="volatility",
        output_columns=["chop_14"],
        input_columns=["high", "low", "close"],
        params={"period": 14},
        version="1.0.0",
        description=(
            "CHOP=100×log10(ΣTR(N)/(HH(N)−LL(N)))/log10(N)，TR=真实波幅（复用 _true_range）；"
            ">61.8 盘整市/<38.3 趋势市；恒定区间（HH=LL）0/0 保护为 NaN"
        ),
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = int(params["period"])
        tr_sum = _true_range(data["high"], data["low"], data["close"]).rolling(window=n).sum()
        hh = data["high"].rolling(window=n).max()
        ll = data["low"].rolling(window=n).min()
        range_ = (hh - ll).where(hh - ll > 0)  # 分母 ≤0（恒定区间）→ NaN，禁 inf
        chop = 100 * np.log10(tr_sum / range_) / np.log10(n)
        return pd.DataFrame({f"chop_{n}": chop}, index=data.index)


@TechnicalIndicatorRegistry.register
class CVI(TechnicalIndicatorBase):
    """Chaikin 波动率（Chaikin Volatility，EMA3/ROC10）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="cvi",
        name="Chaikin波动率",
        category="volatility",
        output_columns=["cvi"],
        input_columns=["high", "low"],
        params={"ema_period": 3, "roc_period": 10},
        version="1.0.0",
        description=(
            "CVI=100×(EMA(H−L,3)/EMA(H−L,3).shift(10)−1)；EMA adjust=False（本库口径，"
            "首值种子无预热 NaN，首有效=第 roc_period 根）；度量高低价区间膨胀速率变化"
        ),
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        ema_n, roc_n = int(params["ema_period"]), int(params["roc_period"])
        rng = data["high"] - data["low"]
        ema_rng = rng.ewm(span=ema_n, adjust=False).mean()
        cvi = 100 * (ema_rng / ema_rng.shift(roc_n) - 1)
        return pd.DataFrame({"cvi": cvi}, index=data.index)


@TechnicalIndicatorRegistry.register
class ULCER(TechnicalIndicatorBase):
    """溃疡指数（Ulcer Index，Martin 1987，14）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="ulcer",
        name="溃疡指数",
        category="volatility",
        output_columns=["ulcer_14"],
        input_columns=["close"],
        params={"period": 14},
        version="1.0.0",
        description=(
            "ULCER=100×√(mean((C/max(C,N)−1)²))，等价 √(mean(((C/max−1)×100)²))——单一滚动窗口含当根，"
            "窗口内各收盘对窗口峰值回撤的 RMS（Martin 溃疡指数，只罚下行波动）"
        ),
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = int(params["period"])
        ulcer = (
            data["close"]
            .rolling(window=n)
            .apply(lambda w: 100.0 * np.sqrt(np.mean(np.square(w / w.max() - 1.0))), raw=True)
        )
        return pd.DataFrame({f"ulcer_{n}": ulcer}, index=data.index)
