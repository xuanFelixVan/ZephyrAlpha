# [BLUEPRINT] MOD-L02-029 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.technical_indicators.cycle
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.technical_indicators.indicator_base; numpy(pip); pandas(pip)
# [CONSUMERS] zephyr.data.implementations.internal_compute_provider（包级 autodiscover 动态接线：internal_compute_provider L545/L1113 延迟导入本包+注册表消费）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 循环族指标 8 个/11 输出列，纯自实现 numpy；compute→DataFrame 多列输出；HT 五指标共享 _ht_core 单遍递推；EBSW 逐行移植 pandas-ta-classic；CONTINUATION/GPRED 逐行移植 Ehlers TASC 论文（HighPass3/SuperSmoother 系数复用 trend 单源）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] compute 输入空 DataFrame→返回空 DataFrame 不抛；输入缺列→ValueError
# [TESTS] tests/zephyr/factor/technical_indicators/test_cycle.py
# [A_module] module_id=MOD-L02-029 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

循环族技术指标（8 个指标/11 输出列；HT 五件套 2026-09-14 批 3 新建，
EBSW 2026-09-20 清欠班波2-A +1，CONTINUATION/GPRED 2026-09-20 清欠班波5 +2）。

指标清单：HT_DCPERIOD/HT_DCPHASE/HT_PHASOR/HT_SINE/HT_TRENDMODE/EBSW/CONTINUATION/GPRED

对齐 TA-Lib Hilbert Transform 循环组理论源（Ehlers, Rocket Science for Traders），
实现采用 **相位累积（Phase Accumulation）** 口径：
  - 4 项 WMA 平滑 → EMA 降噪 → Ehlers 4-tap Hilbert 滤波器取正交分量
  - 逐根相位差 unwrap（限幅防跳变）→ 瞬时周期 = 2π/Δφ → 平滑
  - 相位累积 mod 360 → 正弦/超前正弦；主导周期窗口内交叉计数 → 趋势/循环模式
  - 瞬时周期钳位 [6, 50]（TA-Lib 同款）；输出预热 63 根（TA-Lib 同款）

设计文档：16_technical_indicator_catalog.md §2.8

# [ALGO_FLOW] external: docs/03_modules/_domain_factor/algo_flow/cycle.yaml
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from zephyr.factor.technical_indicators.indicator_base import (
    TechnicalIndicatorBase,
    TechnicalIndicatorMeta,
    TechnicalIndicatorRegistry,
)
from zephyr.factor.technical_indicators.trend import _highpass3, _supersmoother_coeffs

_WARMUP = 63  # TA-Lib 同款稳定预热期
_PERIOD_MIN, _PERIOD_MAX = 6.0, 50.0


def _ht_core(real: np.ndarray) -> dict[str, np.ndarray]:
    """Ehlers 相位累积 Hilbert 变换核，单遍递推。

    返回 dict：dcperiod/dcphase/ip/qp/sine/leadsine/trendmode（预热期 NaN）。
    """
    n = len(real)
    out = {
        k: np.full(n, np.nan)
        for k in (
            "dcperiod",
            "dcphase",
            "ip",
            "qp",
            "sine",
            "leadsine",
            "trendmode",
        )
    }
    if n < _WARMUP:
        return out

    # ① 4 项 WMA 平滑 + EMA 降噪
    smooth = np.full(n, np.nan)
    for i in range(3, n):
        smooth[i] = (4 * real[i] + 3 * real[i - 1] + 2 * real[i - 2] + real[i - 3]) / 10
    s = pd.Series(smooth, index=np.arange(n))
    filt = s.ewm(span=10, adjust=False).mean().to_numpy()

    # ② Ehlers 4-tap Hilbert 滤波器取正交分量；同相分量取延迟 3 根
    q = np.zeros(n)
    for i in range(7, n):
        q[i] = 0.0962 * filt[i] + 0.5769 * filt[i - 2] - 0.5769 * filt[i - 4] - 0.0962 * filt[i - 6]
    ip = np.full(n, np.nan)
    ip[3:] = filt[:-3]

    # ③ 逐根相位差 unwrap → 瞬时周期 → 平滑；相位累积
    dcp_out = out["dcperiod"]
    dcphase_out = out["dcphase"]
    prev_phase = np.nan
    prev_period = 20.0
    period_s = 20.0
    accum = 0.0
    cross_count = 0
    prev_above = False
    for i in range(7, n):
        if q[i] == 0 and ip[i] == 0:
            continue
        phase = np.arctan2(q[i], ip[i])
        if np.isnan(prev_phase):
            prev_phase = phase
            continue
        dphase = phase - prev_phase
        if dphase < 0:
            dphase += 2 * np.pi
        # 限幅：单根相位增量不超过最快周期(6)对应值
        if dphase > 2 * np.pi / _PERIOD_MIN:
            dphase = 2 * np.pi / _PERIOD_MIN
        prev_phase = phase
        if dphase <= 0:
            continue
        inst = 2 * np.pi / dphase
        inst = min(max(inst, _PERIOD_MIN), _PERIOD_MAX)
        period_s = 0.2 * inst + 0.8 * period_s
        prev_period = period_s
        accum = (accum + dphase) % (2 * np.pi)
        if i < _WARMUP:
            continue
        dc_deg = np.degrees(accum)
        sine = np.sin(accum)
        lead = np.sin(accum + np.pi / 4)
        above = sine > lead
        if i > _WARMUP and above != prev_above:
            cross_count += 1
        prev_above = above
        win = int(round(period_s)) or 1
        out["dcperiod"][i] = win
        out["dcphase"][i] = dc_deg
        out["ip"][i] = ip[i]
        out["qp"][i] = q[i]
        out["sine"][i] = sine
        out["leadsine"][i] = lead
        # 趋势模式：主导周期窗口内正弦交叉少→趋势态(1)，多→循环态(0)
        out["trendmode"][i] = 1.0 if cross_count <= 2 else 0.0
        if cross_count >= 4:
            cross_count = 2  # 计数衰减，防历史交叉永久压制
    _ = prev_period
    return out


class _HTBase(TechnicalIndicatorBase):
    """HT 家族公共基类：单遍 _ht_core 后按 output_columns 切片。"""

    _keys: tuple[str, ...] = ()

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        core = _ht_core(data["close"].to_numpy(dtype=float))
        cols = dict(zip(self._keys, self.meta.output_columns, strict=False))
        return pd.DataFrame(
            {col: pd.Series(core[key], index=data.index) for key, col in cols.items()},
            index=data.index,
        )


@TechnicalIndicatorRegistry.register
class HT_DCPERIOD(_HTBase):
    """主导周期（Hilbert Transform Dominant Cycle Period）。"""

    _keys = ("dcperiod",)

    meta = TechnicalIndicatorMeta(
        indicator_id="ht_dcperiod",
        name="主导周期",
        category="cycle",
        output_columns=["ht_dcperiod"],
        input_columns=["close"],
        params={},
        version="1.0.0",
        description="Ehlers 相位累积 Hilbert 主导周期（钳位 [6,50]），循环族共用核（TA-Lib HT_DCPERIOD 同源）",
    )


@TechnicalIndicatorRegistry.register
class HT_DCPHASE(_HTBase):
    """主导周期相位（Hilbert Transform Dominant Cycle Phase）。"""

    _keys = ("dcphase",)

    meta = TechnicalIndicatorMeta(
        indicator_id="ht_dcphase",
        name="主导周期相位",
        category="cycle",
        output_columns=["ht_dcphase"],
        input_columns=["close"],
        params={},
        version="1.0.0",
        description="累积相位角（度，0-360 循环），TA-Lib HT_DCPHASE 同源理论",
    )


@TechnicalIndicatorRegistry.register
class HT_PHASOR(_HTBase):
    """同相/正交分量（Hilbert Transform Phasor）。"""

    _keys = ("ip", "qp")

    meta = TechnicalIndicatorMeta(
        indicator_id="ht_phasor",
        name="同相正交分量",
        category="cycle",
        output_columns=["ht_ip", "ht_qp"],
        input_columns=["close"],
        params={},
        version="1.0.0",
        description="同相分量（延迟 3 根平滑价）与正交分量（4-tap Hilbert 滤波），TA-Lib HT_PHASOR 同源",
    )


@TechnicalIndicatorRegistry.register
class HT_SINE(_HTBase):
    """正弦波（Hilbert Transform Sine Wave）。"""

    _keys = ("sine", "leadsine")

    meta = TechnicalIndicatorMeta(
        indicator_id="ht_sine",
        name="正弦波",
        category="cycle",
        output_columns=["ht_sine", "ht_leadsine"],
        input_columns=["close"],
        params={},
        version="1.0.0",
        description="主正弦与超前 45° 正弦；两线交叉标记周期转折日，TA-Lib HT_SINE 同源",
    )


@TechnicalIndicatorRegistry.register
class HT_TRENDMODE(_HTBase):
    """趋势/循环模式（Hilbert Transform Trend vs Cycle Mode）。"""

    _keys = ("trendmode",)

    meta = TechnicalIndicatorMeta(
        indicator_id="ht_trendmode",
        name="趋势循环模式",
        category="cycle",
        output_columns=["ht_trendmode"],
        input_columns=["close"],
        params={},
        version="1.0.0",
        description="1=趋势态（正弦交叉少）/0=循环态（交叉频繁），穿越计数口径；TA-Lib HT_TRENDMODE 同源",
    )


# ---------------------------------------------------------------------------
# 2026-09-20 简单指标清欠班波2-A：EBSW（Ehlers Even Better Sine Wave）
# 逐行移植：https://github.com/xgboosted/pandas-ta-classic/blob/main/pandas_ta_classic/cycles/ebsw.py
# ---------------------------------------------------------------------------


def _ebsw_core(close: np.ndarray, length: int, bars: int) -> np.ndarray:
    """EBSW 带通滤波核，逐行移植 pandas_ta_classic/cycles/ebsw.py::_ebsw_nb。

    HighPass（alpha1，通达信式 360/length 写法原样保留——源码 sin/cos 即按弧度取值）
    + SuperSmoother（a1/b1/c1..c3 三极递推）→ 3 根平均 Wave 对均方根 Pwr 归一化，
    输出由 Cauchy–Schwarz 界钳位在 [-1,1]。种子：第 length−1 根置 0.0。
    """
    m = close.size
    result = np.full(m, np.nan)
    if length - 1 < m:
        result[length - 1] = 0.0

    # HighPass 与 SuperSmoother 系数逐 bar 恒定
    alpha1 = (1 - np.sin(360 / length)) / np.cos(360 / length)
    a1 = np.exp(-np.sqrt(2) * np.pi / bars)
    b1 = 2 * a1 * np.cos(np.sqrt(2) * 180 / bars)
    c2 = b1
    c3 = -a1 * a1
    c1 = 1 - c2 - c3

    last_close = 0.0
    last_hp = 0.0
    fh0 = 0.0  # FilterHist[0]（更旧）
    fh1 = 0.0  # FilterHist[1]（更新）

    for i in range(length, m):
        hp = 0.5 * (1 + alpha1) * (close[i] - last_close) + alpha1 * last_hp
        filt = c1 * (hp + last_hp) / 2 + c2 * fh1 + c3 * fh0

        # Wave 幅度与功率的 3 根平均
        wave = (filt + fh1 + fh0) / 3
        pwr = (filt * filt + fh1 * fh1 + fh0 * fh0) / 3

        # 平均 Wave 对平均功率均方根归一化
        wave = wave / np.sqrt(pwr) if pwr > 0 else 0.0

        # 状态滚动更新
        fh0 = fh1
        fh1 = filt
        last_hp = hp
        last_close = close[i]
        result[i] = wave

    return result


@TechnicalIndicatorRegistry.register
class EBSW(TechnicalIndicatorBase):
    """更优正弦波（Even Better Sine Wave，Ehlers）。

    公式权威源（逐行移植）：
    https://github.com/xgboosted/pandas-ta-classic/blob/main/pandas_ta_classic/cycles/ebsw.py
    （Ehlers 'Cycle Analytics for Traders' 2014 / prorealcode.com 同源）
    """

    meta = TechnicalIndicatorMeta(
        indicator_id="ebsw",
        name="更优正弦波",
        category="cycle",
        output_columns=["ebsw_40"],
        input_columns=["close"],
        params={"length": 40, "bars": 10},
        version="1.0.0",
        description=(
            "Ehlers 带通滤波去噪：HighPass+SuperSmoother 三极递推，3 根平均 Wave 对均方根 Pwr "
            "归一化（输出钳位 [-1,1]）；length=最大周期（源码 gt=38 约定），bars=低通滤波周期；"
            "第 length−1 根种子 0.0，其后逐根输出（列名列 ebsw_{length}，源命名 EBSW_{length}_{bars} 省略 bars 位）"
        ),
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        length = int(params["length"])
        bars = int(params["bars"])
        core = _ebsw_core(data["close"].to_numpy(dtype=float), length, bars)
        return pd.DataFrame({f"ebsw_{length}": pd.Series(core, index=data.index)}, index=data.index)


# ---------------------------------------------------------------------------
# 2026-09-20 简单指标清欠班波5：CONTINUATION/GPRED（Ehlers TASC 论文移植）
# 公式权威源：
#   CONTINUATION: https://www.mesasoftware.com/papers/Continuation%20Index.pdf
#                 （TASC 2025-09，Ehlers (C) 2025，Code Listing 1/2/3）
#   GPRED:        https://www.mesasoftware.com/papers/Linear%20Predictive%20Filters.pdf
#                 （TASC 2025-01，Ehlers (C) 2024，Code Listing 4）
# HighPass3/SuperSmoother 系数单源复用 trend 模块（FOSC 引 statistics 先例），
# 禁复制粘贴递推——CLONEGUARD 拦 extract 级克隆。
# ---------------------------------------------------------------------------


def _ultimate_smoother(price: np.ndarray, period: int) -> np.ndarray:
    """Ehlers UltimateSmoother（Continuation Index 论文 Listing 2 逐行移植）。

    Q = exp(-1.414π/Period)；c1 = 2Q·cos(1.414π/Period)；c2 = Q²；a0 = (1+c1+c2)/4；
    前 4 根（idx 0..3）种子 US=P；t>=4:
    US = (1-a0)·P[t] + (2a0-c1)·P[t-1] + (c2-a0)·P[t-2] + c1·US[t-1] - c2·US[t-2]
    """
    q = np.exp(-1.414 * np.pi / period)
    c1 = 2.0 * q * np.cos(1.414 * np.pi / period)
    c2 = q * q
    a0 = (1.0 + c1 + c2) / 4.0
    us = price.astype(float).copy()
    for t in range(4, price.size):
        us[t] = (
            (1.0 - a0) * price[t]
            + (2.0 * a0 - c1) * price[t - 1]
            + (c2 - a0) * price[t - 2]
            + c1 * us[t - 1]
            - c2 * us[t - 2]
        )
    return us


def _laguerre(price: np.ndarray, gamma: float, order: int, length: int) -> np.ndarray:
    """Ehlers Laguerre 滤波（Continuation Index 论文 Listing 3 逐行移植）。

    两行状态（本 bar 行/上 bar 行，零种子）：每 bar 先把本行挪到上行走再算新行走，
    k=2..order: LG[k] = -gamma·LG[k-1]_prev + LG[k-1]_prev + gamma·LG[k]_prev
    （读上行走值，k 递增顺序安全）；L1 行 = UltimateSmoother(P, Length)——注意用
    全长 Length，不是调用方的 length/2；输出 = sum(LG[1..order])/order。
    """
    us = _ultimate_smoother(price, length)
    prev = np.zeros(order + 1)
    cur = np.zeros(order + 1)
    out = np.empty(price.size)
    for t in range(price.size):
        prev[:] = cur
        for k in range(2, order + 1):
            cur[k] = (1.0 - gamma) * prev[k - 1] + gamma * prev[k]
        cur[1] = us[t]
        out[t] = cur[1:].sum() / order
    return out


def _continuation_core(close: np.ndarray, gamma: float, order: int, length: int) -> np.ndarray:
    """延续指数核（论文 Listing 1 逐行移植）：逆费雪压缩的 US/Laguerre 偏离归一值。

    Variance = length 根 |US-LG| 滚动均值（前 length-1 根 NaN）；
    Ref = 2·(US-LG)/Variance，Variance 判零时零保护置 0——判零口径为相对容差
    1e-9·(1+|US|)（非零常数下 US/US(L1) 两滤波器浮点不动点相差 1~2 ulp，纯 ==0
    判据永不触发，Ref 会漂到 ±2 违背常数→CI=0 契约；该容差低于真实波动 6 个量级、
    高于浮点噪底 4 个量级）；Ref 钳位 ±20 防 exp 上溢；
    CI = (exp(2·Ref)-1)/(exp(2·Ref)+1) ∈ [-1,1]。
    """
    n = close.size
    out = np.full(n, np.nan)
    us = _ultimate_smoother(close, max(length // 2, 1))
    lg = _laguerre(close, gamma, order, length)
    diff = us - lg
    var = pd.Series(np.abs(diff)).rolling(window=length, min_periods=length).mean().to_numpy()
    valid = np.isfinite(var)
    ref = np.zeros(n)
    np.divide(2.0 * diff, var, out=ref, where=valid & (var > 1e-9 * (1.0 + np.abs(us))))
    ref = np.clip(ref, -20.0, 20.0)
    out[valid] = (np.exp(2.0 * ref[valid]) - 1.0) / (np.exp(2.0 * ref[valid]) + 1.0)
    return out


@TechnicalIndicatorRegistry.register
class CONTINUATION(TechnicalIndicatorBase):
    """延续指数（Continuation Index，Ehlers TASC 2025-09）。

    公式权威源（逐行移植）：
    https://www.mesasoftware.com/papers/Continuation%20Index.pdf
    （TASC 2025-09，Ehlers (C) 2025，Code Listing 1/2/3）

    UltimateSmoother(close, length/2) 与 Laguerre(gamma, order, L1 行全长 US) 之差
    经 length 根 |差| 均值归一后过逆费雪变换压缩到 [-1,1]：价格持续位于 Laguerre
    线上方 → CI≈+1（趋势延续态），下方 → CI≈-1。Variance 判零（相对容差
    1e-9·(1+|US|)，常数输入零保护路径）时 Ref 置 0 → CI=0；Ref 钳位 ±20 防 exp
    上溢。预热：前 length-1 根 NaN。
    """

    meta = TechnicalIndicatorMeta(
        indicator_id="continuation",
        name="延续指数",
        category="cycle",
        output_columns=["continuation_40"],
        input_columns=["close"],
        params={"gamma": 0.8, "order": 8, "length": 40},
        version="1.0.0",
        description=(
            "Ehlers 延续指数：US(close,length/2) 与 Laguerre(gamma,order) 之差按 length 根 "
            "|差| 均值归一（Variance 判零（相对容差 1e-9·(1+|US|)）零保护置 0，常数输入→CI=0），"
            "Ref=2·diff/Variance 钳位 ±20 后过逆费雪 (e^{2R}-1)/(e^{2R}+1) 压缩到 [-1,1]；"
            "+1=价格持续居 Laguerre 线上方的趋势延续态；"
            "列名列 continuation_{length}，gamma/order 覆盖不改列名（源 Code Listing 1/2/3）"
        ),
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        length = int(params["length"])
        core = _continuation_core(
            data["close"].to_numpy(dtype=float),
            gamma=float(params["gamma"]),
            order=int(params["order"]),
            length=length,
        )
        return pd.DataFrame({f"continuation_{length}": pd.Series(core, index=data.index)}, index=data.index)


def _gpred_core(
    close: np.ndarray,
    upper_bound: int,
    lower_bound: int,
    length: int,
    bars_fwd: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Griffiths 线性预测器核（Linear Predictive Filters 论文 Listing 4 逐行移植）。

    HP=HighPass3(close, upper_bound)（复用 trend._highpass3 单源）→
    LP=SuperSmoother(HP, lower_bound)（系数单源 _supersmoother_coeffs，本文件 3 行递推，
    种子 t<2 取 HP 当根值）→ Peak=0.991·Peak_prev（种子 0.1，|LP|>Peak 则抬升），
    Signal=LP/Peak ∈ [-1,1] → Griffiths LMS 自适应：XX[0..length] 反序信号窗
    （XX[j]=Signal[t-(length-j)]，EL 数组 0 基含端点口径），每 bar 窗重灌 +
    coef[count] += Mu·(XX[length]-XBar)·XX[length-count]（Mu=1/length，零种子），
    再前推 bars_fwd 步（XPred=Σ XX[length+1-count]·coef[count] → 窗左移
    （count=advance..length-advance，再 count=1..length-1）→ XX[length]=XPred）。
    预热：前 length 根（HP/LP 未稳+窗未满）输出 NaN，t>=length 起递推。
    """
    n = close.size
    gp_sig = np.full(n, np.nan)
    gp_pred = np.full(n, np.nan)
    if n == 0:
        return gp_sig, gp_pred

    # ① HighPass3(close, upper_bound)——trend 单源，禁复制递推
    hp = _highpass3(pd.Series(close), upper_bound).to_numpy()
    # ② SuperSmoother(HP, lower_bound)：t<2 种子取 HP 当根值
    c1, c2, c3 = _supersmoother_coeffs(lower_bound)
    lp = hp.copy()
    for t in range(2, n):
        lp[t] = c1 * (hp[t] + hp[t - 1]) / 2.0 + c2 * lp[t - 1] + c3 * lp[t - 2]
    # ③ Peak 归一化：Signal = LP/Peak ∈ [-1,1]
    signal = np.empty(n)
    peak = 0.1
    for t in range(n):
        peak *= 0.991
        mag = abs(lp[t])
        if mag > peak:
            peak = mag
        signal[t] = lp[t] / peak
    # ④ Griffiths LMS 递推：coef/XX 跨 bar 持久（零种子），XX 反序窗每 bar 重灌
    mu = 1.0 / length
    coef = np.zeros(length + 1)
    xx = np.zeros(length + 1)
    for t in range(length, n):
        for j in range(length + 1):
            xx[j] = signal[t - length + j]
        xbar = 0.0
        for count in range(1, length + 1):
            xbar += xx[length - count] * coef[count]
        err = xx[length] - xbar
        for count in range(1, length + 1):
            coef[count] += mu * err * xx[length - count]
        xpred = 0.0
        for advance in range(1, bars_fwd + 1):
            xpred = 0.0
            for count in range(1, length + 1):
                xpred += xx[length + 1 - count] * coef[count]
            for count in range(advance, length - advance + 1):
                xx[count] = xx[count + 1]
            for count in range(1, length):
                xx[count] = xx[count + 1]
            xx[length] = xpred
        gp_sig[t] = signal[t]
        gp_pred[t] = xpred
    return gp_sig, gp_pred


@TechnicalIndicatorRegistry.register
class GPRED(TechnicalIndicatorBase):
    """Griffiths 线性预测器（Ehlers TASC 2025-01 Linear Predictive Filters）。

    公式权威源（逐行移植）：
    https://www.mesasoftware.com/papers/Linear%20Predictive%20Filters.pdf
    （TASC 2025-01，Ehlers (C) 2024，Code Listing 4）

    HighPass3(upper_bound) → SuperSmoother(lower_bound) → Peak 归一化信号
    （Signal=LP/Peak ∈ [-1,1]）→ Griffiths LMS（Mu=1/length）自适应估计预测系数，
    前推 bars_fwd 步得线性预测值 gp_pred；gp_sig 即归一化信号。对周期信号预测值
    真实领先 close 若干根（测试以正弦预测相关系数>0.9 为灵魂断言）。
    输出列名固定 gp_sig/gp_pred（kwargs 覆盖参数不改列名）。预热：前 length 根 NaN。
    """

    meta = TechnicalIndicatorMeta(
        indicator_id="gpred",
        name="Griffiths线性预测器",
        category="cycle",
        output_columns=["gp_sig", "gp_pred"],
        input_columns=["close"],
        params={"lower_bound": 18, "upper_bound": 40, "length": 18, "bars_fwd": 2},
        version="1.0.0",
        description=(
            "Ehlers Griffiths 自适应线性预测器：HighPass3(upper_bound)+SuperSmoother"
            "(lower_bound) 带通 → Peak 归一化信号 gp_sig∈[-1,1] → LMS(Mu=1/length) 递推"
            "预测系数并前推 bars_fwd 步得 gp_pred（对周期信号领先真实价格）；"
            "输出列固定 gp_sig/gp_pred，kwargs 覆盖不改列名；前 length 根预热 NaN"
            "（源 Linear Predictive Filters Code Listing 4 逐行移植）"
        ),
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        sig, pred = _gpred_core(
            data["close"].to_numpy(dtype=float),
            upper_bound=int(params["upper_bound"]),
            lower_bound=int(params["lower_bound"]),
            length=int(params["length"]),
            bars_fwd=int(params["bars_fwd"]),
        )
        return pd.DataFrame(
            {"gp_sig": pd.Series(sig, index=data.index), "gp_pred": pd.Series(pred, index=data.index)},
            index=data.index,
        )
