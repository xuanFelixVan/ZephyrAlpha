# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.technical_indicators.trend
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.technical_indicators.indicator_base; pandas(pip); numpy(pip)
# [CONSUMERS] zephyr.data.implementations.internal_compute_provider; sleeve alpha 择时
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 趋势类指标 10 个，纯自实现 pandas/numpy；compute→DataFrame 多列输出
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] compute 输入空 DataFrame→返回空 DataFrame 不抛；输入缺列→ValueError
# [TESTS] tests/zephyr/factor/technical_indicators/test_trend.py
# [A_module] module_id=MOD-L02-TI-TREND | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""趋势类技术指标（10 个，v1.0.0 全部施工完成）。

指标清单：MA/EMA/WMA/DEMA/MACD/ADX/DMI/CCI/SAR/TRIX

算法对齐通达信：
  - EMA 系列（EMA/DEMA/MACD/TRIX）统一 adjust=False，种子=首值，无预热 NaN
  - DMI/ADX 使用 SUM 平滑（非 EMA），对齐通达信 DMI 函数
  - CCI 使用 AVEDEV（平均绝对偏差），对齐通达信 AVEDEV 函数
  - SAR 逐 bar 迭推，AF 从 step 递增至 max，趋势翻转时重置
  - MACD HIST = 2×(DIF-DEA)，对齐通达信 MACD 柱

设计文档：docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/16_technical_indicator_catalog.md §2.1
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
