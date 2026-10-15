# [BLUEPRINT] MOD-REGIME-017 | 待统筹登记（CONDAXIS-CAMPAIGN 两态线 formreg 包；挖矿真源 docs/04_research_records/cross_domain/condaxis/formreg/4_turning_signal.md）
# [MODULE] zephyr.regime.formreg.cusum_two_sided
# [DOMAIN] D_REGIME
# [DEPENDENCIES] pandas; numpy
# [CONSUMERS] （隔离打靶：docs/04_research_records/cross_domain/condaxis/formreg/8_prereg_targeting.md 冒烟；ARL 预算标定后接拐点信号流——冻结面禁接线）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 双边对称（S⁺ 上行/S⁻ 下行，参 correlation_drift_monitor.py:152 单边先例扩双边）；
#              参数学起点=k 0.5σ/h 4σ（同 :60-61 CUSUM_K_SIGMA/H_SIGMA，正式值须 ARL 预算反推=呈批项）；
#              告警后重置（事件流语义：告警→归零→继续监测）；
#              σ=0/样本不足=degraded 显式标记不静默（挖矿簿 4 坑 1：横盘起动恰是拐点最需处）；
#              输出三元组契约（位置/方向/严重度=CU 累积量）；NaN 输入跳过（热身段）
# [MODIFY-GUARD] tests/regime/formreg/test_cusum_two_sided.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空序列/长度<2→ValueError；σ≤0 或非有限→degraded 结果（不告警不抛错）
# [TESTS] tests/regime/formreg/test_cusum_two_sided.py
# [TTL] permanent
"""cusum_two_sided — 双边 CUSUM 拐点检测（单边仓内先例的对称扩展件）。

条件轴总包战役两态线环节[4]施工产出（P2 车道 st-cdx-formreg-20261013）。
仓内单边先例=src/zephyr/factor/analysis/correlation_drift_monitor.py:152
cusum_upper_alarm()（S⁺ₜ=max(0, S⁺ₜ₋₁+(ρₜ−ρ₀)−k)，S⁺>h 告警；该件是策略对
漂移监控域在产件，INVARIANTS 冻结单边——**本件是另建姊妹件非改动本尊**）。

方法：
    S⁺ₜ = max(0, S⁺ₜ₋₁ + (xₜ − μ₀) − k)    上行累积（做多拐点向）
    S⁻ₜ = max(0, S⁻ₜ₋₁ − (xₜ − μ₀) − k)    下行累积（做空拐点向）
    S⁺ > h → 上行告警；S⁻ > h → 下行告警；告警后双侧归零（事件流语义）。

参数纪律：k=0.5σ/h=4σ 是仓内相关漂移经验起点值（correlation_drift_monitor.py:60-61），
照搬为结构起点；正式阈值须按 ARL 虚报率预算反推标定（研究册 §13-5 呈批项，
预算公式与所需数据=docs/04_research_records/cross_domain/condaxis/formreg/8_prereg_targeting.md §3）。

输出三元组契约（位置/方向/严重度）：
    events DataFrame 列=[date, position, direction('up'/'down'), severity(CU 累积量),
    s_plus, s_minus]——severity=告警时刻越阈侧的累积量（严重度代理）。

PIT 纪律：μ₀（baseline）与 σ 由调用方给定（如训练窗统计）；本件零拟合零重估。

# [ALGO_FLOW] external: docs/03_modules/_domain_regime/algo_flow/cusum_two_sided.yaml
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

import numpy as np
import pandas as pd

__all__: Final = ["CusumTwoSidedParams", "CusumTwoSidedResult", "detect_turning_events"]


# ---------------------------------------------------------------------------
# 结构常数区（参数学起点=仓内相关漂移经验值；正式值须 ARL 预算反推=呈批项禁自拟）
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class CusumTwoSidedParams:
    """双边 CUSUM 参数组。

    Attributes:
        k_sigma: 漂移裕量 k（σ 倍数；默认 0.5=仓内单边先例起点值）。
        h_sigma: 告警阈值 h（σ 倍数；默认 4.0=仓内单边先例起点值）。
        reset_on_alarm: 告警后双侧统计量归零（事件流语义；默认 True）。
    """

    k_sigma: float = 0.5
    h_sigma: float = 4.0
    reset_on_alarm: bool = True


@dataclass(frozen=True)
class CusumTwoSidedResult:
    """双边 CUSUM 输出。

    Attributes:
        events: 告警事件流 DataFrame[date, position, direction, severity, s_plus, s_minus]。
        s_plus / s_minus: 累积量全程轨迹（Series，NaN=输入 NaN 跳过位）。
        k_eff / h_eff: 生效的 k/h（绝对量纲）。
        degraded: True=σ≤0/样本不足，全程不告警（显式降级非静默）。
    """

    events: pd.DataFrame
    s_plus: pd.Series
    s_minus: pd.Series
    k_eff: float
    h_eff: float
    degraded: bool


def detect_turning_events(
    series: pd.Series,
    baseline: float,
    params: CusumTwoSidedParams | None = None,
    sigma: float | None = None,
) -> CusumTwoSidedResult:
    """双边 CUSUM 拐点事件检测（纯函数；告警=拐点候选，非确认段边界）。

    Args:
        series: 监测量序列（如月频收益/特征值；DatetimeIndex 升序）。
        baseline: 基线 μ₀（训练窗统计量，PIT 由调用方保证）。
        params: CusumTwoSidedParams（None=起点默认 k0.5σ/h4σ）。
        sigma: 监测量标准差（None=样本 std(ddof=1)；σ≤0→degraded）。

    Returns:
        CusumTwoSidedResult（事件流+轨迹）。

    Raises:
        ValueError: 序列为空/非 DatetimeIndex/非升序/baseline 非有限。
    """
    p = params or CusumTwoSidedParams()
    if series is None or len(series) == 0:
        raise ValueError("series 不能为空")
    if not isinstance(series.index, pd.DatetimeIndex):
        raise ValueError("series 必须为 DatetimeIndex")
    if not bool(series.index.is_monotonic_increasing):
        raise ValueError("series 必须按日期升序")
    if not math.isfinite(float(baseline)):
        raise ValueError("baseline 非有限（数值禁入消息文本，MSG-EXPOSURE）")

    valid = series.dropna()
    sig = float(valid.std(ddof=1)) if sigma is None else float(sigma)
    nan_track_plus = pd.Series(np.nan, index=series.index, dtype=float)
    nan_track_minus = pd.Series(np.nan, index=series.index, dtype=float)
    empty_events = pd.DataFrame(columns=["date", "position", "direction", "severity", "s_plus", "s_minus"])
    # σ≈0 判定含浮点残渣守卫（常数序列 std 可出 ~1e-16 残渣非精确 0）；
    # 降级显式标记不静默（挖矿簿 4 坑 1：横盘起动恰是拐点最需处，调用方须知）
    sig_floor = max(1e-12, 1e-12 * float(np.abs(valid).max()) if len(valid) else 0.0)
    if not math.isfinite(sig) or sig <= sig_floor or len(valid) < 2:
        return CusumTwoSidedResult(
            empty_events, nan_track_plus, nan_track_minus, float("nan"), float("nan"), degraded=True
        )

    k_eff = p.k_sigma * sig
    h_eff = p.h_sigma * sig

    s_plus = pd.Series(np.nan, index=series.index, dtype=float)
    s_minus = pd.Series(np.nan, index=series.index, dtype=float)
    events: list[dict] = []
    sp = 0.0
    sm = 0.0
    for pos, (idx, x) in enumerate(series.items()):
        x = float(x)
        if math.isnan(x):
            continue
        dev = x - float(baseline)
        sp = max(0.0, sp + dev - k_eff)
        sm = max(0.0, sm - dev - k_eff)
        s_plus.loc[idx] = sp
        s_minus.loc[idx] = sm
        direction: str | None = None
        severity = 0.0
        if sp > h_eff:
            direction, severity = "up", sp
        elif sm > h_eff:
            direction, severity = "down", sm
        if direction is not None:
            events.append(
                {
                    "date": idx.strftime("%Y-%m-%d"),
                    "position": pos,
                    "direction": direction,
                    "severity": round(float(severity), 6),
                    "s_plus": round(float(sp), 6),
                    "s_minus": round(float(sm), 6),
                }
            )
            if p.reset_on_alarm:
                sp = 0.0
                sm = 0.0
                s_plus.loc[idx] = 0.0
                s_minus.loc[idx] = 0.0
    return CusumTwoSidedResult(
        pd.DataFrame(events, columns=["date", "position", "direction", "severity", "s_plus", "s_minus"]),
        s_plus,
        s_minus,
        k_eff,
        h_eff,
        degraded=False,
    )
