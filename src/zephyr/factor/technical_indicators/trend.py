# [BLUEPRINT] MOD-L02-021 | (pending)
# [MODULE] zephyr.factor.technical_indicators.trend
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.technical_indicators.indicator_base; pandas(pip); numpy(pip)
# [CONSUMERS] zephyr.data.implementations.internal_compute_provider（包级 autodiscover 动态接线：internal_compute_provider L545/L1113 延迟导入本包+注册表消费）; sleeve alpha 择时
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 趋势类文件指标 38 个（37 趋势类 + 1 复合类 Ichimoku），纯自实现 pandas/numpy；compute→DataFrame 多列输出
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] compute 输入空 DataFrame→返回空 DataFrame 不抛；输入缺列→ValueError
# [TESTS] tests/zephyr/factor/technical_indicators/test_trend.py
# [A_module] module_id=MOD-L02-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

趋势类技术指标（38 个；2026-09-14 A股标配批+1、批2a +5、批2b +1、批3 +1 Ichimoku[复合类]、批6 +1 BBI、
鳄鱼/顾比/GannHiLo 批 +3、2026-09-20 自适应均线批 +3、2026-09-20 简单指标清欠批1-L3 +8、
2026-09-20 简单指标清欠班波2-A +2 INERTIA/QSTICK、2026-09-20 Ehlers 滤波器族班波3-B +3
SUPERSMOOTHER/HIGHPASS/PTREND）。

指标清单：MA/EMA/WMA/DEMA/MACD/ADX/DMI/CCI/SAR/TRIX/DKX/HMA/ZLEMA/KAMA/VORTEX/SUPERTREND/MCGINLEY/
BBI/ALLIGATOR/GMMA/GANN_HILO/MAMA+FAMA/FRAMA/JMA/TEMA/TRIMA/T3/VIDYA/AVGPRICE/MEDPRICE/TYPPRICE/WCPRICE/
INERTIA/QSTICK/SUPERSMOOTHER/HIGHPASS/PTREND/ICHIMOKU(复合类)

算法对齐通达信：
  - EMA 系列（EMA/DEMA/MACD/TRIX）统一 adjust=False，种子=首值，无预热 NaN
  - DMI/ADX 使用 SUM 平滑（非 EMA），对齐通达信 DMI 函数
  - CCI 使用 AVEDEV（平均绝对偏差），对齐通达信 AVEDEV 函数
  - SAR 逐 bar 迭推，AF 从 step 递增至 max，趋势翻转时重置
  - MACD HIST = 2×(DIF-DEA)，对齐通达信 MACD 柱
  - DKX 多空线：MID 线性加权 20..1/210，对齐通达信
  - HMA/ZLEMA 为低滞后均线（WMA 差值再造 / 误差修正 EMA）；KAMA/VORTEX/SUPERTREND 逐 bar 或滚动矩实现（TA-Lib/pandas-ta 口径） DKX 函数
  - TEMA/T3 复用 _ema 链式（adjust=False 种子=首值，无预热 NaN）；TRIMA 偶窗 SMA(N/2)×SMA(N/2+1) 对齐 TA-Lib；
    VIDYA alpha=|CMO|/100×2/(N+1)（CMO 对齐 momentum.py CMO 类）；AVGPRICE/MEDPRICE/TYPPRICE/WCPRICE 为 OHLC 线性变换
  - Ehlers 滤波器族（班波3-B）：SUPERSMOOTHER 二极低通（首两根种子，无预热 NaN）；HIGHPASS 三阶高通
    （首两根零种子非 NaN，financial-hacker C 转译）；PTREND=HighPass3(250)−HighPass3(40) 谱带差分 + TROC 确认项

设计文档：docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/16_technical_indicator_catalog.md §2.1

# [ALGO_FLOW] external: docs/03_modules/_domain_factor/algo_flow/trend.yaml
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


def _ema(series: pd.Series, span: int) -> pd.Series:
    """指数移动平均，对齐通达信算法。

    通达信 EMA(C,N) = (2×C + (N-1)×EMA_prev) / (N+1)，等价于
    pandas ewm(span=N, adjust=False)——种子=首值，从第 0 根 K 线开始递推，无预热 NaN。

    与 adjust=True（pandas 默认）的区别：adjust=True 会对前期值做加权修正，
    与通达信/东方财富输出不一致，故禁用。
    """
    return series.ewm(span=span, adjust=False).mean()


def _wma(series: pd.Series, n: int) -> pd.Series:
    """加权移动平均，对齐通达信 WMA。

    通达信 WMA(C,N) = (1×C_{t-N+1} + 2×C_{t-N+2} + ... + N×C_t) / (1+2+...+N)
    近期权重高（最新值权重=N，最旧值权重=1），权重和 = N×(N+1)/2。
    """
    weights = np.arange(1, n + 1, dtype=float)
    return series.rolling(window=n).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)


def _true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    """真实波幅 TR = max(H-L, |H-Cp|, |L-Cp|)，首行=H-L。

    与 volatility._true_range 同式——volatility 单向依赖本模块（_ema），
    此处独立定义避免循环导入（VORTEX/SUPERTREND 使用）。
    """
    prev_close = close.shift(1)
    tr = pd.concat(
        [high - low, (high - prev_close).abs(), (low - prev_close).abs()],
        axis=1,
    ).max(axis=1)
    return tr


def _di(high: pd.Series, low: pd.Series, close: pd.Series, n: int) -> tuple[pd.Series, pd.Series]:
    """计算 +DI / -DI，对齐通达信 DMI 算法（SUM 平滑，非 EMA）。

    通达信 DMI:
      MTR = SUM(MAX(MAX(H-L, |H-Cp|), |L-Cp|), N)   — True Range 滚动求和
      DMP = SUM(IF(HD>0 AND HD>LD, HD, 0), N)        — +DM 滚动求和
      DMM = SUM(IF(LD>0 AND LD>HD, LD, 0), N)        — -DM 滚动求和
      +DI = DMP × 100 / MTR
      -DI = DMM × 100 / MTR

    其中 HD=H-Hp（上移），LD=Lp-L（下移）。
    """
    # True Range
    tr = pd.concat(
        [high - low, (high - close.shift(1)).abs(), (low - close.shift(1)).abs()],
        axis=1,
    ).max(axis=1)
    # Directional Movement
    hd = high - high.shift(1)  # 上移
    ld = low.shift(1) - low  # 下移
    dmp = hd.where((hd > 0) & (hd > ld), 0.0)  # +DM
    dmm = ld.where((ld > 0) & (ld > hd), 0.0)  # -DM
    # SUM 平滑（通达信标准）
    tr_sum = tr.rolling(window=n).sum()
    dmp_sum = dmp.rolling(window=n).sum()
    dmm_sum = dmm.rolling(window=n).sum()
    pdi = dmp_sum * 100 / tr_sum
    mdi = dmm_sum * 100 / tr_sum
    return pdi, mdi


@TechnicalIndicatorRegistry.register
class MA(TechnicalIndicatorBase):
    """简单移动平均（Simple Moving Average）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="ma",
        name="简单移动平均",
        category="trend",
        output_columns=["ma_5", "ma_10", "ma_20", "ma_60"],
        input_columns=["close"],
        params={"periods": [5, 10, 20, 60]},
        version="1.0.0",
        description="N 日收盘价算术平均，periods=[5,10,20,60] 四条均线",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        close = data["close"]
        result = {f"ma_{n}": close.rolling(window=n).mean() for n in params["periods"]}
        return pd.DataFrame(result, index=data.index)


@TechnicalIndicatorRegistry.register
class EMA(TechnicalIndicatorBase):
    """指数移动平均（Exponential Moving Average）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="ema",
        name="指数移动平均",
        category="trend",
        output_columns=["ema_12", "ema_26"],
        input_columns=["close"],
        params={"periods": [12, 26]},
        version="1.0.0",
        description="N 日收盘价指数加权平均，periods=[12,26]，adjust=False 对齐通达信",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        close = data["close"]
        result = {f"ema_{n}": _ema(close, n) for n in params["periods"]}
        return pd.DataFrame(result, index=data.index)


@TechnicalIndicatorRegistry.register
class WMA(TechnicalIndicatorBase):
    """加权移动平均（Weighted Moving Average）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="wma",
        name="加权移动平均",
        category="trend",
        output_columns=["wma_10"],
        input_columns=["close"],
        params={"period": 10},
        version="1.0.0",
        description="N 日收盘价线性加权平均（近期权重高），权重=1..N",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        return pd.DataFrame({f"wma_{n}": _wma(data["close"], n)}, index=data.index)


@TechnicalIndicatorRegistry.register
class DEMA(TechnicalIndicatorBase):
    """双指数移动平均（Double Exponential Moving Average）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="dema",
        name="双指数移动平均",
        category="trend",
        output_columns=["dema_12"],
        input_columns=["close"],
        params={"period": 12},
        version="1.0.0",
        description="DEMA = 2×EMA - EMA(EMA)，减少 EMA 滞后，adjust=False 对齐通达信",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        ema1 = _ema(data["close"], n)
        ema2 = _ema(ema1, n)
        dema = 2 * ema1 - ema2
        return pd.DataFrame({f"dema_{n}": dema}, index=data.index)


@TechnicalIndicatorRegistry.register
class MACD(TechnicalIndicatorBase):
    """异同移动平均（Moving Average Convergence Divergence）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="macd",
        name="异同移动平均",
        category="trend",
        output_columns=["macd_dif", "macd_dea", "macd_hist"],
        input_columns=["close"],
        params={"fast": 12, "slow": 26, "signal": 9},
        version="1.0.0",
        description="DIF=EMA12-EMA26; DEA=EMA9(DIF); HIST=2×(DIF-DEA)，全 EMA adjust=False 对齐通达信",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        fast, slow, signal = params["fast"], params["slow"], params["signal"]
        close = data["close"]
        dif = _ema(close, fast) - _ema(close, slow)
        dea = _ema(dif, signal)
        hist = 2 * (dif - dea)
        return pd.DataFrame({"macd_dif": dif, "macd_dea": dea, "macd_hist": hist}, index=data.index)


@TechnicalIndicatorRegistry.register
class ADX(TechnicalIndicatorBase):
    """平均趋向指数（Average Directional Index）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="adx",
        name="平均趋向指数",
        category="trend",
        output_columns=["adx_14"],
        input_columns=["high", "low", "close"],
        params={"period": 14},
        version="1.0.0",
        description="DX=|+DI--DI|/(+DI+-DI)×100; ADX=MA(DX)，DI 用 SUM 平滑对齐通达信",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        pdi, mdi = _di(data["high"], data["low"], data["close"], n)
        dx = (pdi - mdi).abs() / (pdi + mdi) * 100
        adx = dx.rolling(window=n).mean()
        return pd.DataFrame({f"adx_{n}": adx}, index=data.index)


@TechnicalIndicatorRegistry.register
class DMI(TechnicalIndicatorBase):
    """趋向指标（Directional Movement Index）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="dmi",
        name="趋向指标",
        category="trend",
        output_columns=["pdi_14", "mdi_14"],
        input_columns=["high", "low", "close"],
        params={"period": 14},
        version="1.0.0",
        description="+DM/-DM → +DI/-DI，SUM 平滑对齐通达信（非 EMA）",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        pdi, mdi = _di(data["high"], data["low"], data["close"], n)
        return pd.DataFrame({f"pdi_{n}": pdi, f"mdi_{n}": mdi}, index=data.index)


@TechnicalIndicatorRegistry.register
class CCI(TechnicalIndicatorBase):
    """顺势指标（Commodity Channel Index）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="cci",
        name="顺势指标",
        category="trend",
        output_columns=["cci_14"],
        input_columns=["high", "low", "close"],
        params={"period": 14},
        version="1.0.0",
        description="TP=(H+L+C)/3; CCI=(TP-MA(TP))/(0.015×AVEDEV(TP))，AVEDEV=平均绝对偏差",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        tp = (data["high"] + data["low"] + data["close"]) / 3
        ma_tp = tp.rolling(window=n).mean()
        # AVEDEV = 平均绝对偏差（对齐通达信 AVEDEV 函数）
        avedev = tp.rolling(window=n).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True)
        cci = (tp - ma_tp) / (0.015 * avedev)
        return pd.DataFrame({f"cci_{n}": cci}, index=data.index)


@TechnicalIndicatorRegistry.register
class SAR(TechnicalIndicatorBase):
    """抛物线指标（Stop and Reverse）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="sar",
        name="抛物线指标",
        category="trend",
        output_columns=["sar"],
        input_columns=["high", "low"],
        params={"af_step": 0.02, "af_max": 0.2},
        version="1.0.0",
        description="SAR(t+1)=SAR(t)+AF×(EP-SAR(t))，AF 从 step 递增至 max，趋势翻转时重置",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        af_step = params["af_step"]
        af_max = params["af_max"]
        high = data["high"].values
        low = data["low"].values
        n = len(high)
        sar = np.empty(n)
        sar[:] = np.nan
        if n == 0:
            return pd.DataFrame({"sar": sar}, index=data.index)
        # 初始假设上升趋势
        is_long = True
        sar[0] = low[0]
        ep = high[0]
        af = af_step
        for i in range(1, n):
            sar[i] = sar[i - 1] + af * (ep - sar[i - 1])
            if is_long:
                # 上升期 SAR 不能高于近两根 K 线的最低价
                sar[i] = min(sar[i], low[i - 1])
                if i >= 2:
                    sar[i] = min(sar[i], low[i - 2])
                if low[i] < sar[i]:
                    # 翻转为下降趋势
                    is_long = False
                    sar[i] = ep
                    ep = low[i]
                    af = af_step
                elif high[i] > ep:
                    ep = high[i]
                    af = min(af + af_step, af_max)
            else:
                # 下降期 SAR 不能低于近两根 K 线的最高价
                sar[i] = max(sar[i], high[i - 1])
                if i >= 2:
                    sar[i] = max(sar[i], high[i - 2])
                if high[i] > sar[i]:
                    # 翻转为上升趋势
                    is_long = True
                    sar[i] = ep
                    ep = high[i]
                    af = af_step
                elif low[i] < ep:
                    ep = low[i]
                    af = min(af + af_step, af_max)
        return pd.DataFrame({"sar": sar}, index=data.index)


@TechnicalIndicatorRegistry.register
class TRIX(TechnicalIndicatorBase):
    """三重指数平滑平均（Triple Exponential Average）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="trix",
        name="三重指数平滑平均",
        category="trend",
        output_columns=["trix", "trma"],
        input_columns=["close"],
        params={"period": 12},
        version="1.0.0",
        description="TR=EMA(EMA(EMA(C,N))); TRIX=100×(TR-REF(TR,1))/REF(TR,1); TRMA=MA(TRIX,N)",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        close = data["close"]
        # TR = 三重 EMA（通达信标准，非 TEMA 公式）
        tr = _ema(_ema(_ema(close, n), n), n)
        # TRIX = 100 × TR 变化率
        trix = 100 * tr.pct_change()
        # TRMA = MA(TRIX)
        trma = trix.rolling(window=n).mean()
        return pd.DataFrame({"trix": trix, "trma": trma}, index=data.index)


@TechnicalIndicatorRegistry.register
class DKX(TechnicalIndicatorBase):
    """多空线（DKX，A股行情软件标配 20+MA10）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="dkx",
        name="多空线",
        category="trend",
        output_columns=["dkx_20", "dkx_ma10"],
        input_columns=["open", "high", "low", "close"],
        params={"period": 20, "ma_period": 10},
        version="1.0.0",
        description="MID=(3C+L+O+H)/6；DKX=(20·MID+19·REF(MID,1)+…+1·REF(MID,19))/210；MADKX=MA(DKX,10)",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n, ma_n = params["period"], params["ma_period"]
        mid = (3 * data["close"] + data["low"] + data["open"] + data["high"]) / 6
        # 线性加权 20..1，分母 210=Σ20..1（对齐通达信 DKX）
        weighted = pd.Series(0.0, index=data.index)
        for i in range(n):
            weighted = weighted + (n - i) * mid.shift(i)
        dkx = weighted / (n * (n + 1) / 2)
        dkx_ma = dkx.rolling(window=ma_n).mean()
        return pd.DataFrame({f"dkx_{n}": dkx, f"dkx_ma{ma_n}": dkx_ma}, index=data.index)


@TechnicalIndicatorRegistry.register
class HMA(TechnicalIndicatorBase):
    """Hull 均线（Hull Moving Average）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="hma",
        name="Hull均线",
        category="trend",
        output_columns=["hma_16"],
        input_columns=["close"],
        params={"period": 16},
        version="1.0.0",
        description="HMA=WMA(2×WMA(C,N/2)−WMA(C,N), ⌊√N⌋)，低滞后高平滑",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        half = _wma(data["close"], max(2, n // 2))
        full = _wma(data["close"], n)
        raw = 2 * half - full
        hma = _wma(raw, max(1, int(np.sqrt(n))))
        return pd.DataFrame({f"hma_{n}": hma}, index=data.index)


@TechnicalIndicatorRegistry.register
class ZLEMA(TechnicalIndicatorBase):
    """零滞后 EMA（Zero-Lag EMA）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="zlema",
        name="零滞后EMA",
        category="trend",
        output_columns=["zlema_21"],
        input_columns=["close"],
        params={"period": 21},
        version="1.0.0",
        description="lag=(N−1)/2；ZLEMA=EMA(2C−REF(C,lag))，误差修正项抵消 EMA 滞后",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        lag = (n - 1) // 2
        de_lagged = 2 * data["close"] - data["close"].shift(lag)
        zlema = _ema(de_lagged, n)
        return pd.DataFrame({f"zlema_{n}": zlema}, index=data.index)


@TechnicalIndicatorRegistry.register
class KAMA(TechnicalIndicatorBase):
    """Kaufman 自适应均线（Kaufman's Adaptive Moving Average）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="kama",
        name="Kaufman自适应均线",
        category="trend",
        output_columns=["kama_10"],
        input_columns=["close"],
        params={"period": 10, "fast": 2, "slow": 30},
        version="1.0.0",
        description="ER=|C−C_N|/Σ|ΔC|；SC=(ER×(2/(f+1)−2/(s+1))+2/(s+1))²；KAMA 逐 bar 递推",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n, fast, slow = params["period"], params["fast"], params["slow"]
        close = data["close"]
        change = (close - close.shift(n)).abs()
        volatility = close.diff().abs().rolling(window=n).sum()
        er = change / volatility
        fast_sc = 2.0 / (fast + 1)
        slow_sc = 2.0 / (slow + 1)
        sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2
        # 逐 bar 递推（ER 逐日变化，无闭式滚动解；SAR 同族实现）
        kama_values = np.full(len(close), np.nan)
        closes = close.to_numpy(dtype=float)
        sc_vals = sc.to_numpy()
        prev = np.nan
        # 种子=第 N 根收盘价（预热窗口结束点）
        for i in range(len(closes)):
            if i < n or np.isnan(sc_vals[i]):
                if i == n - 1:
                    prev = closes[i]
                    kama_values[i] = prev
                continue
            prev = prev + sc_vals[i] * (closes[i] - prev)
            kama_values[i] = prev
        kama = pd.Series(kama_values, index=data.index)
        return pd.DataFrame({f"kama_{n}": kama}, index=data.index)


@TechnicalIndicatorRegistry.register
class VORTEX(TechnicalIndicatorBase):
    """涡旋指标（Vortex Indicator）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="vortex",
        name="涡旋指标",
        category="trend",
        output_columns=["vip_14", "vim_14"],
        input_columns=["high", "low", "close"],
        params={"period": 14},
        version="1.0.0",
        description="VI+=Σ|H−L_prev|/ΣTR；VI−=Σ|L−H_prev|/ΣTR；VIP 上穿 VIM 看涨",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        prev_close = data["close"].shift(1)
        vmp = (data["high"] - data["low"].shift(1)).abs()
        vmn = (data["low"] - data["high"].shift(1)).abs()
        tr = _true_range(data["high"], data["low"], data["close"])
        tr_sum = tr.rolling(window=n).sum()
        vip = vmp.rolling(window=n).sum() / tr_sum
        vim = vmn.rolling(window=n).sum() / tr_sum
        return pd.DataFrame({f"vip_{n}": vip, f"vim_{n}": vim}, index=data.index)


@TechnicalIndicatorRegistry.register
class SUPERTREND(TechnicalIndicatorBase):
    """超级趋势（Supertrend，10/3 通通行情口径）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="supertrend",
        name="超级趋势",
        category="trend",
        output_columns=["supertrend_10", "supertrend_dir"],
        input_columns=["high", "low", "close"],
        params={"period": 10, "multiplier": 3.0},
        version="1.0.0",
        description="基础带=(H+L)/2±mul×ATR；带随趋势单向收紧；收盘穿越带→翻转；dir=1 多/−1 空",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n, mult = params["period"], params["multiplier"]
        high, low, close = data["high"], data["low"], data["close"]
        atr = _true_range(high, low, close).rolling(window=n).mean()
        mid = (high + low) / 2
        upper_basic = mid + mult * atr
        lower_basic = mid - mult * atr
        # 逐 bar 递推：final 带只随趋势单向收紧；收盘穿越带→翻转（canonical close 口径）
        ub = upper_basic.to_numpy()
        lb = lower_basic.to_numpy()
        c = close.to_numpy()
        m = len(c)
        st = np.full(m, np.nan)
        direction = np.full(m, np.nan)  # 预热期 NaN，不冒充方向信号
        final_ub = np.nan
        final_lb = np.nan
        prev_close = np.nan
        trend = 0.0
        for i in range(m):
            if np.isnan(ub[i]) or np.isnan(lb[i]):
                continue
            # final 带收紧规则：带宽只能朝趋势方向收，除非前收越带解锁反向放宽
            if np.isnan(final_ub):
                final_ub, final_lb = ub[i], lb[i]
                trend = 1.0 if c[i] >= mid.to_numpy()[i] else -1.0
            else:
                final_ub = ub[i] if (ub[i] < final_ub or prev_close > final_ub) else final_ub
                final_lb = lb[i] if (lb[i] > final_lb or prev_close < final_lb) else final_lb
                if trend == 1.0 and c[i] < final_lb:
                    trend = -1.0
                elif trend == -1.0 and c[i] > final_ub:
                    trend = 1.0
            prev_close = c[i]
            direction[i] = trend
            st[i] = final_lb if trend == 1.0 else final_ub
        return pd.DataFrame({f"supertrend_{n}": st, "supertrend_dir": direction}, index=data.index)


@TechnicalIndicatorRegistry.register
class MCGINLEY(TechnicalIndicatorBase):
    """McGinley 动态均线（McGinley Dynamic，14）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="mcginley",
        name="McGinley动态均线",
        category="trend",
        output_columns=["md_14"],
        input_columns=["close"],
        params={"period": 14, "k": 0.6},
        version="1.0.0",
        description="MD=prev+(C−prev)/(k×N×(C/prev)⁴)，追踪速度随偏离自动调节，分离度低于 EMA",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n, k = params["period"], params["k"]
        c = data["close"].to_numpy()
        m = len(c)
        md = np.full(m, np.nan)
        prev = np.nan
        for i in range(m):
            if np.isnan(prev):
                prev = c[i]
                md[i] = prev
                continue
            ratio = c[i] / prev if prev != 0 else 1.0
            denom = k * n * max(ratio**4, 1e-12)
            prev = prev + (c[i] - prev) / denom
            md[i] = prev
        return pd.DataFrame({f"md_{n}": pd.Series(md, index=data.index)}, index=data.index)


@TechnicalIndicatorRegistry.register
class ICHIMOKU(TechnicalIndicatorBase):
    """一目均衡表（Ichimoku Kinko Hyo，9/26/52，位移 26）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="ichimoku",
        name="一目均衡表",
        category="composite",
        output_columns=["tenkan_sen", "kijun_sen", "senkou_span_a", "senkou_span_b", "chikou_span"],
        input_columns=["high", "low", "close"],
        params={"tenkan": 9, "kijun": 26, "senkou_b": 52, "displacement": 26},
        version="1.0.0",
        description=(
            "转折=(HH9+LL9)/2；基准=(HH26+LL26)/2；先行A=(转折+基准)/2 先移26；"
            "先行B=(HH52+LL52)/2 先移26；迟行=收盘（后移26 为显示位移，存储取计算时点值）。"
            "存储口径 PIT 安全：先行跨度存显示位（值来自 26 根之前，无前视）；迟行存现值"
        ),
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        t_n, k_n, b_n, disp = params["tenkan"], params["kijun"], params["senkou_b"], params["displacement"]
        hh = lambda n: data["high"].rolling(window=n).max()  # noqa: E731
        ll = lambda n: data["low"].rolling(window=n).min()  # noqa: E731
        tenkan = (hh(t_n) + ll(t_n)) / 2
        kijun = (hh(k_n) + ll(k_n)) / 2
        senkou_a = ((tenkan + kijun) / 2).shift(disp)
        senkou_b = ((hh(b_n) + ll(b_n)) / 2).shift(disp)
        chikou = data["close"]
        return pd.DataFrame(
            {
                "tenkan_sen": tenkan,
                "kijun_sen": kijun,
                "senkou_span_a": senkou_a,
                "senkou_span_b": senkou_b,
                "chikou_span": chikou,
            },
            index=data.index,
        )


@TechnicalIndicatorRegistry.register
class BBI(TechnicalIndicatorBase):
    """多空指数（Bull and Bear Index，通达信/同花顺标配 3/6/12/24）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="bbi",
        name="多空指数",
        category="trend",
        output_columns=["bbi"],
        input_columns=["close"],
        params={"periods": [3, 6, 12, 24]},
        version="1.0.0",
        description="BBI=(MA3+MA6+MA12+MA24)/4，四周期均线合成，收盘上穿看多",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        bbi = pd.Series(0.0, index=data.index)
        for n in params["periods"]:
            bbi = bbi + data["close"].rolling(window=n).mean()
        bbi = bbi / len(params["periods"])
        return pd.DataFrame({"bbi": bbi}, index=data.index)


@TechnicalIndicatorRegistry.register
class ALLIGATOR(TechnicalIndicatorBase):
    """鳄鱼线（Bill Williams Alligator，13/8/5 均衡移动平均 SMMA+前移位移）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="alligator",
        name="鳄鱼线",
        category="trend",
        output_columns=["alligator_jaw", "alligator_teeth", "alligator_lips"],
        input_columns=["high", "low"],
        params={"jaw": 13, "teeth": 8, "lips": 5, "jaw_shift": 8, "teeth_shift": 5, "lips_shift": 3},
        version="1.0.0",
        description="SMMA(中价 HL/2)：颚 13 前移 8 / 齿 8 前移 5 / 唇 5 前移 3；存储=显示位（值来自过去，PIT 无前视）",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        mid = (data["high"] + data["low"]) / 2

        def smma(series: pd.Series, n: int) -> pd.Series:
            return series.ewm(alpha=1 / n, adjust=False).mean()

        jaw = smma(mid, params["jaw"]).shift(params["jaw_shift"])
        teeth = smma(mid, params["teeth"]).shift(params["teeth_shift"])
        lips = smma(mid, params["lips"]).shift(params["lips_shift"])
        return pd.DataFrame(
            {"alligator_jaw": jaw, "alligator_teeth": teeth, "alligator_lips": lips},
            index=data.index,
        )


@TechnicalIndicatorRegistry.register
class GMMA(TechnicalIndicatorBase):
    """顾比复合均线（Guppy Multiple Moving Average，短期 3-15 + 长期 30-60 共 12 条 EMA）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="gmma",
        name="顾比复合均线",
        category="trend",
        output_columns=[
            "gmma_s3",
            "gmma_s5",
            "gmma_s8",
            "gmma_s10",
            "gmma_s12",
            "gmma_s15",
            "gmma_l30",
            "gmma_l35",
            "gmma_l40",
            "gmma_l45",
            "gmma_l50",
            "gmma_l60",
        ],
        input_columns=["close"],
        params={"short": [3, 5, 8, 10, 12, 15], "long": [30, 35, 40, 45, 50, 60]},
        version="1.0.0",
        description="短期组/长期组各 6 条 EMA：组收敛=趋势共识，发散=趋势运行（StockCharts ChartSchool 口径）",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        out = {}
        for n in params["short"]:
            out[f"gmma_s{n}"] = data["close"].ewm(span=n, adjust=False).mean()
        for n in params["long"]:
            out[f"gmma_l{n}"] = data["close"].ewm(span=n, adjust=False).mean()
        return pd.DataFrame(out, index=data.index)


@TechnicalIndicatorRegistry.register
class GANN_HILO(TechnicalIndicatorBase):
    """Gann HiLo Activator（10）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="gann_hilo",
        name="Gann HiLo Activator",
        category="trend",
        output_columns=["gann_hilo", "gann_hilo_dir"],
        input_columns=["high", "low", "close"],
        params={"period": 10},
        version="1.0.0",
        description="HiLo=SMA(HL/2,10)；收盘在 HiLo 上方=多头(1)/下方=空头(-1)，逐 bar 翻转",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        mid = (data["high"] + data["low"]) / 2
        hilo = mid.rolling(window=n).mean()
        close = data["close"]
        dir_col = pd.Series(np.nan, index=data.index)
        trend = np.nan
        for i in range(n - 1, len(close)):
            if np.isnan(trend):
                trend = 1.0 if close.iloc[i] >= hilo.iloc[i] else -1.0
            elif close.iloc[i] > hilo.iloc[i]:
                trend = 1.0
            elif close.iloc[i] < hilo.iloc[i]:
                trend = -1.0
            dir_col.iloc[i] = trend
        return pd.DataFrame({"gann_hilo": hilo, "gann_hilo_dir": dir_col}, index=data.index)


# ---------------------------------------------------------------------------
# 2026-09-20 自适应均线批：MAMA / FRAMA / JMA（递推类，逐 bar 移植，KAMA/SAR 同族实现）
# ---------------------------------------------------------------------------

_MAMA_HILB_A = 0.0962
_MAMA_HILB_B = 0.5769


def _hilbert_stage(
    buf: list, idx: int, prev: float, prev_input: float, src: float, adj: float
) -> tuple[float, float, float]:
    """Hilbert 四抽头差分单级（TA-Lib ta_MAMA.c 同式，_MAMA_HILB_A=0.0962 / _MAMA_HILB_B=0.5769）。

    v = ((a·src − buf[idx]) + a·src − b·旧prev_input) + b·旧prev_input，再乘 adj；
    buf[idx] / prev / prev_input 就地更新，返回 (本级输出, 新 prev, 新 prev_input)。
    """
    h = _MAMA_HILB_A * src
    v = 0.0 - buf[idx]
    buf[idx] = h
    v += h
    v -= prev
    prev = _MAMA_HILB_B * prev_input
    v += prev
    prev_input = src
    v *= adj
    return v, prev, prev_input


def _mama_wma_seed(price: np.ndarray) -> tuple[int, float, float, float, int]:
    """尾随 WMA 预热种子（C 源 3 根展开 + 9 根滚动，today 走到 12）。

    返回 (today, wma_sub, wma_sum, trailing, trailing_idx) 供主递推循环续用。
    """
    today = 0
    t = price[today]
    today += 1
    wma_sub = t
    wma_sum = t
    t = price[today]
    today += 1
    wma_sub += t
    wma_sum += t * 2.0
    t = price[today]
    today += 1
    wma_sub += t
    wma_sum += t * 3.0
    trailing = 0.0
    trailing_idx = 0
    for _ in range(9):
        t = price[today]
        today += 1
        wma_sub += t
        wma_sub -= trailing
        wma_sum += t * 4.0
        trailing = price[trailing_idx]
        trailing_idx += 1
        wma_sum -= wma_sub
    return today, wma_sub, wma_sum, trailing, trailing_idx


def _mama_period_update(
    i2: float,
    q2: float,
    prev_i2: float,
    prev_q2: float,
    re_acc: float,
    im_acc: float,
    period: float,
) -> tuple[float, float, float]:
    """homodyne 同相正交积分解瞬时周期（atan 分母零保护）。

    周期钳位 [0.67p,1.5p]∩[6,50] 后按 0.2/0.8 平滑；返回 (re_acc, im_acc, period)。
    """
    re_acc = 0.8 * re_acc + 0.2 * (i2 * prev_i2 + q2 * prev_q2)
    im_acc = 0.8 * im_acc + 0.2 * (i2 * prev_q2 - q2 * prev_i2)
    rad2deg = 180.0 / (4.0 * np.arctan(1.0))
    period_prev = period
    if im_acc != 0.0 and re_acc != 0.0:
        period = 360.0 / (np.arctan(im_acc / re_acc) * rad2deg)
    cap = 1.5 * period_prev
    if period > cap:
        period = cap
    cap = 0.67 * period_prev
    if period < cap:
        period = cap
    if period < 6.0:
        period = 6.0
    elif period > 50.0:
        period = 50.0
    period = 0.2 * period + 0.8 * period_prev
    return re_acc, im_acc, period


def _mama_recursion(price: np.ndarray, fast_limit: float, slow_limit: float) -> tuple[np.ndarray, np.ndarray]:
    """Ehlers homodyne 递推主体，逐 bar 移植 TA-Lib ta_MAMA.c（BSD 风格许可）。

    公式权威源：https://github.com/ta-lib/ta-lib/blob/main/src/ta_func/ta_MAMA.c
    结构对应：
      - 前 12 根为尾随 WMA 预热种子（3 根展开 + 9 根滚动，C 源 TradeStation 兼容窗）；
      - detrender/Q1/jI/jQ 四组 3 槽圈缓冲按奇偶 bar 分相推进（hilbertIdx 仅偶数 bar 前进）；
      - I1 链延迟 3 bar；atan 求瞬时相位（分母零保护置 0），DeltaPhase 钳位 [1,180]；
      - alpha=fast_limit/DeltaPhase 钳位 [slow_limit, fast_limit]；
      - 瞬时周期：Re/Im 同相正交积分解算，钳位 [0.67p,1.5p]∩[6,50] 再 0.2/0.8 平滑。
    输出自第 12 根起（预热后首根递推位）；TA-Lib 全量 lookback=32 属 unstable period
    语义（前段差异豁免），第 32 根起与 talib.MAMA 逐位一致。
    """
    n = len(price)
    mama_arr = np.full(n, np.nan)
    fama_arr = np.full(n, np.nan)
    if n <= 12:
        return mama_arr, fama_arr
    rad2deg = 180.0 / (4.0 * np.arctan(1.0))
    # --- 尾随 WMA 种子（C 源 3 根展开 + 9 根 do-while，today 走到 12） ---
    _, wma_sub, wma_sum, trailing, trailing_idx = _mama_wma_seed(price)
    # --- Hilbert 圈缓冲（各奇偶 3 槽）与递推状态（零种子，对齐 C 源） ---
    det_e = [0.0, 0.0, 0.0]
    det_o = [0.0, 0.0, 0.0]
    q1_e = [0.0, 0.0, 0.0]
    q1_o = [0.0, 0.0, 0.0]
    ji_e = [0.0, 0.0, 0.0]
    ji_o = [0.0, 0.0, 0.0]
    jq_e = [0.0, 0.0, 0.0]
    jq_o = [0.0, 0.0, 0.0]
    pd_e = pd_o = 0.0  # prev detrender（偶/奇）
    pdi_e = pdi_o = 0.0  # prev detrender input
    pq_e = pq_o = 0.0  # prev Q1
    pqi_e = pqi_o = 0.0  # prev Q1 input
    pj_e = pj_o = 0.0  # prev jI
    pji_e = pji_o = 0.0  # prev jI input
    pjg_e = pjg_o = 0.0  # prev jQ
    pjgi_e = pjgi_o = 0.0  # prev jQ input
    hilbert_idx = 0
    period = 0.0
    prev_q2 = prev_i2 = 0.0
    re_acc = im_acc = 0.0
    mama = fama = 0.0
    i1_e2 = i1_e3 = i1_o2 = i1_o3 = 0.0  # I1 链延迟 3 bar（偶/奇各 2 级）
    prev_phase = 0.0
    for i in range(12, n):
        today_value = price[i]
        adj = 0.075 * period + 0.54
        wma_sub += today_value
        wma_sub -= trailing
        wma_sum += today_value * 4.0
        trailing = price[trailing_idx]
        trailing_idx += 1
        smoothed = wma_sum * 0.1
        wma_sum -= wma_sub
        if i % 2 == 0:
            detrender, pd_e, pdi_e = _hilbert_stage(det_e, hilbert_idx, pd_e, pdi_e, smoothed, adj)
            q1, pq_e, pqi_e = _hilbert_stage(q1_e, hilbert_idx, pq_e, pqi_e, detrender, adj)
            ji, pj_e, pji_e = _hilbert_stage(ji_e, hilbert_idx, pj_e, pji_e, i1_e3, adj)
            jq, pjg_e, pjgi_e = _hilbert_stage(jq_e, hilbert_idx, pjg_e, pjgi_e, q1, adj)
            hilbert_idx = 0 if hilbert_idx == 2 else hilbert_idx + 1
            q2 = 0.2 * (q1 + ji) + 0.8 * prev_q2
            i2 = 0.2 * (i1_e3 - jq) + 0.8 * prev_i2
            i1_o3 = i1_o2
            i1_o2 = detrender
            i1_phase = i1_e3
        else:
            detrender, pd_o, pdi_o = _hilbert_stage(det_o, hilbert_idx, pd_o, pdi_o, smoothed, adj)
            q1, pq_o, pqi_o = _hilbert_stage(q1_o, hilbert_idx, pq_o, pqi_o, detrender, adj)
            ji, pj_o, pji_o = _hilbert_stage(ji_o, hilbert_idx, pj_o, pji_o, i1_o3, adj)
            jq, pjg_o, pjgi_o = _hilbert_stage(jq_o, hilbert_idx, pjg_o, pjgi_o, q1, adj)
            q2 = 0.2 * (q1 + ji) + 0.8 * prev_q2
            i2 = 0.2 * (i1_o3 - jq) + 0.8 * prev_i2
            i1_e3 = i1_e2
            i1_e2 = detrender
            i1_phase = i1_o3
        # 相位差 → alpha（DeltaPhase 钳位下界 1°，上界由 atan 值域天然兜底）
        phase = np.arctan(q1 / i1_phase) * rad2deg if i1_phase != 0.0 else 0.0
        delta_phase = prev_phase - phase
        prev_phase = phase
        if delta_phase < 1.0:
            delta_phase = 1.0
        if delta_phase > 1.0:
            alpha = fast_limit / delta_phase
            if alpha < slow_limit:
                alpha = slow_limit
        else:
            alpha = fast_limit
        # MAMA/FAMA 双速递推（FAMA 取半速 alpha）
        mama = (1.0 - alpha) * mama + alpha * today_value
        alpha *= 0.5
        fama = (1.0 - alpha) * fama + alpha * mama
        mama_arr[i] = mama
        fama_arr[i] = fama
        # homodyne 同相正交积分解瞬时周期（atan 分母零保护，抽出独立函数）
        re_acc, im_acc, period = _mama_period_update(i2, q2, prev_i2, prev_q2, re_acc, im_acc, period)
        prev_q2 = q2
        prev_i2 = i2
    return mama_arr, fama_arr


@TechnicalIndicatorRegistry.register
class MAMA(TechnicalIndicatorBase):
    """MESA 自适应均线（Ehlers MESA Adaptive Moving Average，homodyne 口径对齐 TA-Lib MAMA）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="mama",
        name="MESA自适应均线",
        category="trend",
        output_columns=["mama", "fama"],
        input_columns=["high", "low"],
        params={"fast_limit": 0.5, "slow_limit": 0.05},
        version="1.0.0",
        description=(
            "Price=(H+L)/2 经 Hilbert 变换解瞬时周期：alpha=fast_limit/DeltaPhase 钳位"
            " [slow_limit,fast_limit]；MAMA=αP+(1−α)MAMA'，FAMA 半速慢线（TA-Lib MAMA 口径）"
        ),
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        mama_arr, fama_arr = _mama_recursion(
            ((data["high"] + data["low"]) / 2.0).to_numpy(dtype=float),
            float(params["fast_limit"]),
            float(params["slow_limit"]),
        )
        return pd.DataFrame({"mama": mama_arr, "fama": fama_arr}, index=data.index)


@TechnicalIndicatorRegistry.register
class FRAMA(TechnicalIndicatorBase):
    """分形自适应均线（Ehlers Fractal Adaptive Moving Average，TASC 2005）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="frama",
        name="分形自适应均线",
        category="trend",
        output_columns=["frama_16"],
        input_columns=["high", "low"],
        params={"period": 16},
        version="1.0.0",
        description=(
            "窗口对半分求分维 D=log2(2(HL1+HL2)/HL3)（两半/整窗各自 max(H)−min(L)）："
            "alpha=exp(−4.6(D−1)) 钳位 [0.01,1]；FRAMA=α×(H+L)/2+(1−α)×FRAMA'，窗口自动取偶"
        ),
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n_win = int(params["period"])
        if n_win % 2 == 1:
            n_win += 1  # Ehlers 分形窗要求偶数（对半分）
        high, low = data["high"], data["low"]
        half = n_win // 2
        price = (high + low) / 2.0
        hl1 = high.rolling(window=half).max().shift(half) - low.rolling(window=half).min().shift(half)
        hl2 = high.rolling(window=half).max() - low.rolling(window=half).min()
        hl3 = high.rolling(window=n_win).max() - low.rolling(window=n_win).min()
        # 分维 D = log2((HL1+HL2)/half ÷ HL3/N) = log2(2(HL1+HL2)/HL3)，理论值域 [1,2]
        sum_halves = hl1 + hl2
        with np.errstate(divide="ignore", invalid="ignore"):
            dim = np.log(2.0 * sum_halves / hl3) / np.log(2.0)
            alpha = np.exp(-4.6 * (dim - 1.0))
        # HL 全零/非正（常数窗）→ 负对数无定义 → alpha 取钳位上界 1
        valid = (sum_halves > 0) & (hl3 > 0)
        alpha = alpha.where(valid, 1.0).clip(lower=0.01, upper=1.0)
        # 先 rolling 窗口算 alpha 序列，再单遍递推：首有效=第 N−1 根，种子=当根中价
        alphas = alpha.to_numpy(dtype=float)
        prices = price.to_numpy(dtype=float)
        m = len(prices)
        out = np.full(m, np.nan)
        prev = np.nan
        for i in range(n_win - 1, m):
            a = alphas[i]
            if np.isnan(prev):
                prev = prices[i]
            else:
                prev = a * prices[i] + (1.0 - a) * prev
            out[i] = prev
        return pd.DataFrame({f"frama_{n_win}": pd.Series(out, index=data.index)}, index=data.index)


@TechnicalIndicatorRegistry.register
class JMA(TechnicalIndicatorBase):
    """Jurik 自适应均线（Jurik Moving Average，pandas-ta 开源移植口径）。

    公式权威源（逐行移植）：
    https://github.com/twopirllc/pandas-ta/blob/main/pandas_ta/overlap/jma.py
    （原仓已下架，存续镜像 pandas_ta_classic/overlap/jma.py 同源同式）
    """

    meta = TechnicalIndicatorMeta(
        indicator_id="jma",
        name="Jurik自适应均线",
        category="trend",
        output_columns=["jma_7"],
        input_columns=["close"],
        params={"period": 7, "phase": 50, "power": 2},
        version="1.0.0",
        description=(
            "Jurik 波动率自适应三段滤波：自适应 EMA 预平滑+Kalman 修正+Jurik 终滤波"
            "（beta/phaseRatio/alpha/det0/det1 递推链）；power 为 API 保留位，"
            "pandas-ta 口径中压缩链指数由 period 内生决定；前 period−1 根 NaN"
        ),
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        length = int(params["period"])
        phase = float(params["phase"])
        c = data["close"].to_numpy(dtype=float)
        m = len(c)
        # --- 静态系数（pandas-ta jma.py 逐行对应） ---
        sum_length = 10
        half_len = 0.5 * (length - 1)
        pr = 0.5 if phase < -100 else (2.5 if phase > 100 else 1.5 + phase * 0.01)
        length1 = max((np.log(np.sqrt(half_len)) / np.log(2.0)) + 2.0, 0.0)
        pow1 = max(length1 - 2.0, 0.5)
        length2 = length1 * np.sqrt(half_len)
        bet = length2 / (length2 + 1.0)
        beta = 0.45 * (length - 1) / (0.45 * (length - 1) + 2.0)
        min_r_volty = np.power(length1, 1.0 / pow1)
        # --- 逐 bar 递推（波动率带 + 三段滤波压缩链） ---
        volty = np.zeros(m)
        v_sum = np.zeros(m)
        jma = np.zeros(m)
        det0 = det1 = ma2 = 0.0
        ma1 = u_band = l_band = jma[0] = c[0]
        for i in range(1, m):
            price = c[i]
            del1 = price - u_band
            del2 = price - l_band
            volty[i] = max(abs(del1), abs(del2)) if abs(del1) != abs(del2) else 0.0
            v_sum[i] = v_sum[i - 1] + (volty[i] - volty[max(i - sum_length, 0)]) / sum_length
            avg_volty = np.mean(v_sum[max(i - 65, 0) : i + 1])
            d_volty = 0.0 if avg_volty == 0 else volty[i] / avg_volty
            r_volty = max(1.0, min(min_r_volty, d_volty))
            pow2 = np.power(r_volty, pow1)
            kv = np.power(bet, np.sqrt(pow2))
            u_band = price if del1 > 0 else price - kv * del1
            l_band = price if del2 < 0 else price - kv * del2
            alpha = np.power(beta, pow2)
            # 第一段：自适应 EMA 预平滑
            ma1 = (1.0 - alpha) * price + alpha * ma1
            # 第二段：Kalman 修正
            det0 = (price - ma1) * (1.0 - beta) + beta * det0
            ma2 = ma1 + pr * det0
            # 第三段：Jurik 终滤波
            det1 = (ma2 - jma[i - 1]) * (1.0 - alpha) * (1.0 - alpha) + alpha * alpha * det1
            jma[i] = jma[i - 1] + det1
        jma[: length - 1] = np.nan  # pandas-ta 口径：预热位掩 NaN（种子=首值）
        return pd.DataFrame({f"jma_{length}": pd.Series(jma, index=data.index)}, index=data.index)


# ---------------------------------------------------------------------------
# 2026-09-20 简单指标清欠批1-L3：TEMA/TRIMA/T3/VIDYA + 四价格变换
# （TEMA/T3 复用 _ema 链式，KAMA/FRAMA 同族递推约定：种子当根即首有效）
# ---------------------------------------------------------------------------


@TechnicalIndicatorRegistry.register
class TEMA(TechnicalIndicatorBase):
    """三重指数移动平均（Triple Exponential Moving Average）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="tema",
        name="三重指数移动平均",
        category="trend",
        output_columns=["tema_10"],
        input_columns=["close"],
        params={"period": 10},
        version="1.0.0",
        description=(
            "TEMA=3×EMA1−3×EMA2+EMA3，EMA1/2/3 为 _ema(close,N) 三重链式，"
            "全链 adjust=False 种子=首值，无预热 NaN（warmup 语义记 1）"
        ),
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        close = data["close"]
        e1 = _ema(close, n)
        e2 = _ema(e1, n)
        e3 = _ema(e2, n)
        return pd.DataFrame({f"tema_{n}": 3 * e1 - 3 * e2 + e3}, index=data.index)


@TechnicalIndicatorRegistry.register
class TRIMA(TechnicalIndicatorBase):
    """三角移动平均（Triangular Moving Average，TA-Lib 偶窗/奇窗双口径）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="trima",
        name="三角移动平均",
        category="trend",
        output_columns=["trima_10"],
        input_columns=["close"],
        params={"period": 10},
        version="1.0.0",
        description=(
            "偶 N：SMA(SMA(C,N/2),N/2+1) 双窗级联；奇 N：两窗均 (N+1)/2，对齐 TA-Lib TRIMA；首有效=第 N 根（index N−1）"
        ),
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        if n % 2 == 0:
            w1, w2 = n // 2, n // 2 + 1
        else:
            w1 = w2 = (n + 1) // 2
        trima = data["close"].rolling(window=w1).mean().rolling(window=w2).mean()
        return pd.DataFrame({f"trima_{n}": trima}, index=data.index)


@TechnicalIndicatorRegistry.register
class T3(TechnicalIndicatorBase):
    """Tillson T3 均线（六重 EMA 链，v 因子 0.7）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="t3",
        name="Tillson T3均线",
        category="trend",
        output_columns=["t3_10"],
        input_columns=["close"],
        params={"period": 10, "vfactor": 0.7},
        version="1.0.0",
        description=(
            "e1..e6=_ema(close,N) 六重链；c1=−a³ c2=3a²+3a³ c3=−6a²−3a−3a³ c4=1+3a+a³+3a²；"
            "T3=c1·e6+c2·e5+c3·e4+c4·e3（系数和恒为 1），adjust=False 无预热 NaN"
        ),
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        a = params["vfactor"]
        close = data["close"]
        e1 = _ema(close, n)
        e2 = _ema(e1, n)
        e3 = _ema(e2, n)
        e4 = _ema(e3, n)
        e5 = _ema(e4, n)
        e6 = _ema(e5, n)
        c1 = -(a**3)
        c2 = 3 * a**2 + 3 * a**3
        c3 = -6 * a**2 - 3 * a - 3 * a**3
        c4 = 1 + 3 * a + a**3 + 3 * a**2
        t3 = c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3
        return pd.DataFrame({f"t3_{n}": t3}, index=data.index)


@TechnicalIndicatorRegistry.register
class VIDYA(TechnicalIndicatorBase):
    """可变指数动态均线（Chande Variable Index Dynamic Average）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="vidya",
        name="可变指数动态均线",
        category="trend",
        output_columns=["vidya_14"],
        input_columns=["close"],
        params={"period": 14, "cmo_period": 9},
        version="1.0.0",
        description=(
            "alpha=|CMO(C,cmo_period)|/100×2/(N+1)（CMO 滚动涨跌和，对齐 momentum.py CMO 类）；"
            "VIDYA=α·C+(1−α)·VIDYA'，种子=CMO 首有效当根 close（种子当根即首有效，KAMA/FRAMA 同族约定）"
        ),
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        cmo_n = params["cmo_period"]
        close = data["close"]
        # CMO 对齐 momentum.py CMO 类：滚动 9 窗涨跌和（diff 首位 NaN → 首有效=cmo_period）
        delta = close.diff()
        su = delta.clip(lower=0).rolling(window=cmo_n).sum()
        sd = (-delta).clip(lower=0).rolling(window=cmo_n).sum()
        cmo = (su - sd) / (su + sd) * 100
        alpha = cmo.abs() / 100.0 * (2.0 / (n + 1))
        # 逐 bar 递推：种子=首个 alpha 有效当根 close（种子当根即输出，与 KAMA/FRAMA 一致）
        a_vals = alpha.to_numpy()
        c_vals = close.to_numpy(dtype=float)
        m = len(c_vals)
        out = np.full(m, np.nan)
        prev = np.nan
        for i in range(m):
            if np.isnan(a_vals[i]):
                continue
            if np.isnan(prev):
                prev = c_vals[i]
            else:
                prev = a_vals[i] * c_vals[i] + (1.0 - a_vals[i]) * prev
            out[i] = prev
        return pd.DataFrame({f"vidya_{n}": pd.Series(out, index=data.index)}, index=data.index)


@TechnicalIndicatorRegistry.register
class AVGPRICE(TechnicalIndicatorBase):
    """平均价格（Average Price，OHLC4）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="avgprice",
        name="平均价格",
        category="trend",
        output_columns=["avgprice"],
        input_columns=["open", "high", "low", "close"],
        params={},
        version="1.0.0",
        description="AVGPRICE=(O+H+L+C)/4，逐 bar 线性变换，首行即有效",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        avgprice = (data["open"] + data["high"] + data["low"] + data["close"]) / 4
        return pd.DataFrame({"avgprice": avgprice}, index=data.index)


@TechnicalIndicatorRegistry.register
class MEDPRICE(TechnicalIndicatorBase):
    """中位价格（Median Price，HL2）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="medprice",
        name="中位价格",
        category="trend",
        output_columns=["medprice"],
        input_columns=["high", "low"],
        params={},
        version="1.0.0",
        description="MEDPRICE=(H+L)/2，逐 bar 线性变换，首行即有效",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        medprice = (data["high"] + data["low"]) / 2
        return pd.DataFrame({"medprice": medprice}, index=data.index)


@TechnicalIndicatorRegistry.register
class TYPPRICE(TechnicalIndicatorBase):
    """典型价格（Typical Price，HLC3）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="typprice",
        name="典型价格",
        category="trend",
        output_columns=["typprice"],
        input_columns=["high", "low", "close"],
        params={},
        version="1.0.0",
        description="TYPPRICE=(H+L+C)/3，逐 bar 线性变换，首行即有效",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        typprice = (data["high"] + data["low"] + data["close"]) / 3
        return pd.DataFrame({"typprice": typprice}, index=data.index)


@TechnicalIndicatorRegistry.register
class WCPRICE(TechnicalIndicatorBase):
    """加权收盘价（Weighted Close Price，TA-Lib 名 WCLPRICE 的别名关系）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="wcprice",
        name="加权收盘价",
        category="trend",
        output_columns=["wcprice"],
        input_columns=["high", "low", "close"],
        params={},
        version="1.0.0",
        description="WCPRICE=(H+L+2×C)/4（收盘双倍权重）；本库 id=wcprice，TA-Lib 函数名 WCLPRICE（别名关系）",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        wcprice = (data["high"] + data["low"] + 2 * data["close"]) / 4
        return pd.DataFrame({"wcprice": wcprice}, index=data.index)


# ---------------------------------------------------------------------------
# 2026-09-20 简单指标清欠班波2-A：INERTIA/QSTICK
# INERTIA 逐行移植：https://github.com/xgboosted/pandas-ta-classic/blob/main/pandas_ta_classic/momentum/inertia.py
# （依赖链 volatility/rvi.py + overlap/linreg.py + overlap/ema.py 基础口径随迁）
# QSTICK 移植源：https://github.com/xgboosted/pandas-ta-classic/blob/main/pandas_ta_classic/trend/qstick.py
# ---------------------------------------------------------------------------


def _seeded_ema(series: pd.Series, length: int) -> pd.Series:
    """pandas-ta 口径 EMA（pandas_ta_classic/overlap/ema.py，sma=True 默认）。

    首段 length 个有效值取 SMA 作种子（对应位置前置值置 NaN），再 ewm(span, adjust=False)
    递推——区别于本库 _ema（首值种子）：种子前整段为预热 NaN。
    """
    first_valid = series.first_valid_index()
    if first_valid is None:
        return series
    fv_pos = series.index.get_loc(first_valid)
    seeded = series.copy()
    if fv_pos + length <= len(seeded):
        sma_nth = seeded.iloc[fv_pos : fv_pos + length].mean()
        seeded.iloc[: fv_pos + length - 1] = np.nan
        seeded.iloc[fv_pos + length - 1] = sma_nth
    else:
        seeded.iloc[:] = np.nan  # 有效值不足一个窗口：EMA 全程无定义（源码同口径）
    return seeded.ewm(span=length, adjust=False).mean()


def _rvi_basic(source: pd.Series, length: int, scalar: float, mamode: str) -> pd.Series:
    """相对波动指数 RVI 基础模式（pandas_ta_classic/volatility/rvi.py 口径）。

    UP=STD×1{Δsrc>0}，DOWN=STD×1{Δsrc≤0}（diff 首位 NaN 记 0，与源 unsigned_differences
    一致）；STD 为 ddof=0 滚动总体标准差；UP/DOWN 经 mamode 平滑后
    RVI=scalar×UP_avg/(UP_avg+DOWN_avg)。src 恒定 → STD=0 → 0/0=NaN（源码忠实行为）。
    """
    std = source.rolling(window=length).std(ddof=0)
    diff = source.diff().fillna(0.0)
    pos = (diff > 0).astype(float)
    neg = (diff < 0).astype(float)
    if mamode == "ema":
        pos_avg = _seeded_ema(pos * std, length)
        neg_avg = _seeded_ema(neg * std, length)
    else:  # "sma"
        pos_avg = (pos * std).rolling(window=length).mean()
        neg_avg = (neg * std).rolling(window=length).mean()
    return scalar * pos_avg / (pos_avg + neg_avg)


def _linreg_endpoint(series: pd.Series, length: int) -> pd.Series:
    """滚动最小二乘回归端点拟合值（pandas_ta_classic/overlap/linreg.py 默认输出）。

    对窗口 x=[0..length−1], y=窗口值做 OLS，取 x=length−1 处拟合值
    = slope×(length−1)+intercept（端点值对 x 平移不变）。
    """
    x = np.arange(length, dtype=float)
    x_sum = x.sum()
    x2_sum = np.square(x).sum()
    divisor = length * x2_sum - x_sum**2

    def endpoint(window: np.ndarray) -> float:
        y_sum = window.sum()
        xy_sum = float(np.dot(window, x))
        slope = (length * xy_sum - x_sum * y_sum) / divisor
        intercept = (y_sum * x2_sum - x_sum * xy_sum) / divisor
        return slope * (length - 1) + intercept

    return series.rolling(window=length).apply(endpoint, raw=True)


@TechnicalIndicatorRegistry.register
class INERTIA(TechnicalIndicatorBase):
    """惯性指标（Inertia，Donald Dorsey 1995，RVI 经最小二乘均线平滑）。

    公式权威源（逐行移植）：
    https://github.com/xgboosted/pandas-ta-classic/blob/main/pandas_ta_classic/momentum/inertia.py
    （Dorsey, "The Relative Vigor Index / Inertia"，1995-09）
    """

    meta = TechnicalIndicatorMeta(
        indicator_id="inertia",
        name="惯性指标",
        category="trend",
        output_columns=["inertia_20_14"],
        input_columns=["high", "low"],
        params={"length": 20, "rvi_length": 14, "scalar": 100, "mamode": "ema"},
        version="1.0.0",
        description=(
            "INERTIA=LINREG(RVI(src,rvi_length),length)（滚动 OLS 端点拟合）；RVI=scalar×"
            "EMA(pos·STD)/(EMA(pos·STD)+EMA(neg·STD))，EMA 用 pandas-ta SMA 种子口径（种子前 NaN）；"
            "src=(H+L)/2——移植源基础模式用 close，按车道规格 inputs=[high,low] 取 HL2（MAMA 同款约定）；"
            ">50 正惯性/<50 负惯性；列名 inertia_{length}_{rvi_length}（源命名 INERTIA_{length}_{rvi_length} 小写化）"
        ),
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        length = int(params["length"])
        rvi_length = int(params["rvi_length"])
        scalar = float(params["scalar"])
        mamode = str(params["mamode"])
        if mamode not in ("ema", "sma"):
            raise ValueError(f"INERTIA 基础移植仅支持 mamode='ema'/'sma'，收到: {mamode}")
        src = (data["high"] + data["low"]) / 2
        rvi = _rvi_basic(src, rvi_length, scalar, mamode)
        inertia = _linreg_endpoint(rvi, length)
        return pd.DataFrame({f"inertia_{length}_{rvi_length}": inertia}, index=data.index)


@TechnicalIndicatorRegistry.register
class QSTICK(TechnicalIndicatorBase):
    """Q 棒指标（QStick，Tushar Chande，SMA(C−O,N)）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="qstick",
        name="QStick指标",
        category="trend",
        output_columns=["qstick_10"],
        input_columns=["open", "close"],
        params={"length": 10},
        version="1.0.0",
        description=(
            "QS=SMA(C−O,N)（Chande QStick，源默认 ma='sma'，本移植固定 sma 口径）；"
            ">0 阳线动能占优/<0 阴线动能占优；十字星 C=O 按数学定义记 0"
            "（未移植源 non_zero_range 的 0.001 epsilon 修补——加密盘零极差数据专用）"
        ),
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = int(params["length"])
        diff = data["close"] - data["open"]
        qstick = diff.rolling(window=n).mean()
        return pd.DataFrame({f"qstick_{n}": qstick}, index=data.index)


# ---------------------------------------------------------------------------
# 2026-09-20 Ehlers 滤波器族班波3-B：SUPERSMOOTHER/HIGHPASS/PTREND
# 公式权威源：Ehlers "Rocket Science for Traders"（SuperSmoother 二极低通）+
# TASC 2024-09 "Precision Trend Analysis"（HighPass3/PTrend，financial-hacker
# C 转译逐行核对）。递推类逐 bar 移植（KAMA/SAR/MAMA 同族实现）。
# ---------------------------------------------------------------------------


def _supersmoother_coeffs(n: int) -> tuple[float, float, float]:
    """Ehlers SuperSmoother 二极低通滤波系数 (c1, c2, c3)。

    a1 = exp(-1.414π/N)；c2 = 2a1·cos(1.414π/N)；c3 = -a1²；c1 = 1 - c2 - c3
    （三系数和恒为 1，常数输入恒等该常数）。注意 HighPass3 系数（cos(f/2)、
    c1=(1+c2-c3)/4）与本式不同，见 _highpass3——两套系数各自独立成块，禁混用。
    """
    a1 = np.exp(-1.414 * np.pi / n)
    c2 = 2.0 * a1 * np.cos(1.414 * np.pi / n)
    c3 = -(a1 * a1)
    c1 = 1.0 - c2 - c3
    return c1, c2, c3


def _highpass3(series: pd.Series, n: int) -> pd.Series:
    """Ehlers HighPass3 三阶高通滤波（TASC 2024-09 Precision Trend 原生组件）。

    financial-hacker C 转译逐行核对：f = 1.414π/N；a1 = exp(-f)；
    c2 = 2a1·cos(f/2)；c3 = -a1²；c1 = (1 + c2 - c3)/4；
    hp[0] = hp[1] = 0（C 源零种子，非 NaN）；t>=2:
    hp[t] = c1·(p[t] - 2p[t-1] + p[t-2]) + c2·hp[t-1] + c3·hp[t-2]。
    HIGHPASS/PTREND 三处调用共用本助手；warmup 语义记 3（首两根零种子非缺数据）。
    """
    f = 1.414 * np.pi / n
    a1 = np.exp(-f)
    c2 = 2.0 * a1 * np.cos(f / 2.0)
    c3 = -(a1 * a1)
    c1 = (1.0 + c2 - c3) / 4.0
    p = series.to_numpy(dtype=float)
    hp = np.zeros(len(p))
    for t in range(2, len(p)):
        hp[t] = c1 * (p[t] - 2.0 * p[t - 1] + p[t - 2]) + c2 * hp[t - 1] + c3 * hp[t - 2]
    return pd.Series(hp, index=series.index)


@TechnicalIndicatorRegistry.register
class SUPERSMOOTHER(TechnicalIndicatorBase):
    """超级平滑器（Ehlers SuperSmoother，二极低通滤波）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="supersmoother",
        name="超级平滑器",
        category="trend",
        output_columns=["supersmoother_10"],
        input_columns=["close"],
        params={"period": 10},
        version="1.0.0",
        description=(
            "Ehlers SuperSmoother：ss[t]=c1·(p[t]+p[t-1])/2 + c2·ss[t-1] + c3·ss[t-2]"
            "（a1=exp(-1.414π/N) 生成 c1/c2/c3，系数和恒为 1）；首两根种子 ss[0]=p[0]、"
            "ss[1]=(p[0]+p[1])/2，无预热 NaN（warmup 语义记 1），逐 bar 递推（KAMA/SAR 同族）"
        ),
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = int(params["period"])
        c1, c2, c3 = _supersmoother_coeffs(n)
        p = data["close"].to_numpy(dtype=float)
        ss = np.empty(len(p))
        ss[0] = p[0]
        if len(p) > 1:
            ss[1] = (p[0] + p[1]) / 2.0
        for t in range(2, len(p)):
            ss[t] = c1 * (p[t] + p[t - 1]) / 2.0 + c2 * ss[t - 1] + c3 * ss[t - 2]
        return pd.DataFrame({f"supersmoother_{n}": pd.Series(ss, index=data.index)}, index=data.index)


@TechnicalIndicatorRegistry.register
class HIGHPASS(TechnicalIndicatorBase):
    """三阶高通滤波（Ehlers HighPass3，TASC 2024-09 Precision Trend 原生组件）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="highpass",
        name="三阶高通滤波",
        category="trend",
        output_columns=["highpass_40"],
        input_columns=["close"],
        params={"period": 40},
        version="1.0.0",
        description=(
            "Ehlers HighPass3：hp[t]=c1·(p[t]-2p[t-1]+p[t-2]) + c2·hp[t-1] + c3·hp[t-2]"
            "（f=1.414π/N，c2=2a1·cos(f/2)，c1=(1+c2-c3)/4，financial-hacker C 转译）；"
            "首两根记 0 值非 NaN（与 C 源一致，warmup 语义记 3）；滤除 N 周期以下的趋势分量"
        ),
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = int(params["period"])
        hp = _highpass3(data["close"], n)
        return pd.DataFrame({f"highpass_{n}": hp}, index=data.index)


@TechnicalIndicatorRegistry.register
class PTREND(TechnicalIndicatorBase):
    """精调趋势（Ehlers Precision Trend，TASC 2024-09，谱带差分趋势线）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="ptrend",
        name="精调趋势",
        category="trend",
        output_columns=["ptrend_250_40", "ptrend_roc"],
        input_columns=["close"],
        params={"period_long": 250, "period_short": 40},
        version="1.0.0",
        description=(
            "PTrend=HighPass3(C,250)−HighPass3(C,40)（40..250 带通带谱带差分趋势线）；"
            "TROC=(period_short/2π)×ΔPTrend 确认项（首位无前值记 NaN）；"
            "列名固定 ptrend_250_40/ptrend_roc（双参语义，kwargs 覆盖周期时列名不变，mama/fama 固定列先例）"
        ),
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n_long = int(params["period_long"])
        n_short = int(params["period_short"])
        close = data["close"]
        hp_long = _highpass3(close, n_long)
        hp_short = _highpass3(close, n_short)
        ptrend = hp_long - hp_short
        troc = (n_short / (2.0 * np.pi)) * ptrend.diff()
        return pd.DataFrame({"ptrend_250_40": ptrend, "ptrend_roc": troc}, index=data.index)
