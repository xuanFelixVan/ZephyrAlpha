# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.technical_indicators.cycle
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.technical_indicators.indicator_base; numpy(pip); pandas(pip)
# [CONSUMERS] zephyr.data.implementations.internal_compute_provider（包级 autodiscover 动态接线：internal_compute_provider L545/L1113 延迟导入本包+注册表消费）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 循环族指标 5 个/7 输出列，纯自实现 numpy；compute→DataFrame 多列输出；共享 _ht_core 单遍递推
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] compute 输入空 DataFrame→返回空 DataFrame 不抛；输入缺列→ValueError
# [TESTS] tests/zephyr/factor/technical_indicators/test_cycle.py
# [A_module] module_id=MOD-L02-029 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

循环族技术指标（5 个指标/7 输出列，2026-09-14 批 3 新建）。

指标清单：HT_DCPERIOD/HT_DCPHASE/HT_PHASOR/HT_SINE/HT_TRENDMODE

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

_WARMUP = 63  # TA-Lib 同款稳定预热期
_PERIOD_MIN, _PERIOD_MAX = 6.0, 50.0


def _ht_core(real: np.ndarray) -> dict[str, np.ndarray]:
    """Ehlers 相位累积 Hilbert 变换核，单遍递推。

    返回 dict：dcperiod/dcphase/ip/qp/sine/leadsine/trendmode（预热期 NaN）。
    """
    n = len(real)
    out = {k: np.full(n, np.nan) for k in (
        "dcperiod", "dcphase", "ip", "qp", "sine", "leadsine", "trendmode",
    )}
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
        cols = dict(zip(self._keys, self.meta.output_columns))
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
