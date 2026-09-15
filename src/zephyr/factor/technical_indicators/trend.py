# [BLUEPRINT] MOD-L02-021 | (pending)
# [MODULE] zephyr.factor.technical_indicators.trend
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.technical_indicators.indicator_base; pandas(pip); numpy(pip)
# [CONSUMERS] zephyr.data.implementations.internal_compute_provider（包级 autodiscover 动态接线：internal_compute_provider L545/L1113 延迟导入本包+注册表消费）; sleeve alpha 择时
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 趋势类文件指标 19 个（18 趋势类 + 1 复合类 Ichimoku），纯自实现 pandas/numpy；compute→DataFrame 多列输出
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] compute 输入空 DataFrame→返回空 DataFrame 不抛；输入缺列→ValueError
# [TESTS] tests/zephyr/factor/technical_indicators/test_trend.py
# [A_module] module_id=MOD-L02-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

趋势类技术指标（17 个；2026-09-14 A股标配批+1、批2a +5、批2b +1、批3 +1 Ichimoku[复合类]、批6 +1 BBI）。

指标清单：MA/EMA/WMA/DEMA/MACD/ADX/DMI/CCI/SAR/TRIX/DKX/HMA/ZLEMA/KAMA/VORTEX/SUPERTREND/MCGINLEY/BBI/ICHIMOKU(复合类)

算法对齐通达信：
  - EMA 系列（EMA/DEMA/MACD/TRIX）统一 adjust=False，种子=首值，无预热 NaN
  - DMI/ADX 使用 SUM 平滑（非 EMA），对齐通达信 DMI 函数
  - CCI 使用 AVEDEV（平均绝对偏差），对齐通达信 AVEDEV 函数
  - SAR 逐 bar 迭推，AF 从 step 递增至 max，趋势翻转时重置
  - MACD HIST = 2×(DIF-DEA)，对齐通达信 MACD 柱
  - DKX 多空线：MID 线性加权 20..1/210，对齐通达信
  - HMA/ZLEMA 为低滞后均线（WMA 差值再造 / 误差修正 EMA）；KAMA/VORTEX/SUPERTREND 逐 bar 或滚动矩实现（TA-Lib/pandas-ta 口径） DKX 函数

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
        return pd.DataFrame(
            {f"supertrend_{n}": st, "supertrend_dir": direction}, index=data.index
        )


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
            "gmma_s3", "gmma_s5", "gmma_s8", "gmma_s10", "gmma_s12", "gmma_s15",
            "gmma_l30", "gmma_l35", "gmma_l40", "gmma_l45", "gmma_l50", "gmma_l60",
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
