# [BLUEPRINT] MOD-REGIME-017 | 待统筹登记（CONDAXIS-CAMPAIGN 两态线 formreg 包；挖矿真源 docs/04_research_records/cross_domain/condaxis/formreg/2_state_machine.md / 7_validation.md）
# [MODULE] zephyr.regime.formreg.ps_chronology
# [DOMAIN] D_REGIME
# [DEPENDENCIES] pandas; numpy
# [CONSUMERS] （隔离打靶：docs/04_research_records/cross_domain/condaxis/formreg/8_prereg_targeting.md；裁定#229 反转落地后接 [7] 标定集真值段——冻结面禁接线）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 纯函数核零 IO 零随机（同输入永远同输出）；峰谷交替强制（同类相邻留更极端者）；
#              censoring 迭代至收敛（相位<4 月硬剔除；牛<15 月/熊<6 月且幅度≤20% 剔除；
#              完整周期<16 月且幅度≤30% 剔除）；边界候选（截断窗）标 confirmed=False 不冒充定案；
#              离线年代学右端确认滞后≠实时态（研究册 §3.3 分工）；
#              参数组=文献美股月频默认值，A 股重标定=P2 呈批项禁自拟
# [MODIFY-GUARD] tests/regime/formreg/test_ps_chronology.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 输入空/非 DatetimeIndex/长度不足搜索窗→ValueError（fail-closed）；无有效转折点→空段表（调用方判空）
# [TESTS] tests/regime/formreg/test_ps_chronology.py
# [TTL] permanent
"""ps_chronology — P-S 牛熊年代学纯函数核（Pagan & Sossounov 2003 月频规则层）。

条件轴总包战役（st-condaxis-20261013）两态线环节[2]规则层施工产出（P2 车道
st-cdx-formreg-20261013）。定位＝**离线定"历史真值段"**——供给 [7] 标定集与
[4] 离线复核做对照基准；实时面状态归拐点/日层，禁拿本件定案段冒充实时态。

方法（Pagan & Sossounov 2003, J. Applied Econometrics 18(1)，Bry-Boschan 月频改编）：

    1. 转折点搜索：±search_window(默认 8) 月窗内局部峰/谷（窗截断处=边界候选，
       confirmed=False——右端须未来窗口确认，即离线年代学的确认滞后）。
    2. 交替强制：相邻同类转折点留更极端者（双峰留高、双谷留低）。
    3. censoring（迭代至不动点，删点后回到第 2 步重排）：
       a. 相位 < min_phase_months(4) 月 → 剔除（无豁免）；
       b. 牛市相位 < bull_min_months(15) 月 / 熊市相位 < bear_min_months(6) 月
          且幅度 ≤ phase_amp_exempt(20%) → 剔除；
       c. 完整周期（峰→峰或谷→谷）< cycle_min_months(16) 月
          且周期幅度 ≤ cycle_amp_exempt(30%) → 剔除。
       删点选择约定（P-S 文本未细化 BB 程序实现，仓内显式约定留痕）：删相邻两相位
       中"显著度更低"的转折点——显著度=该转折点两侧相位幅度的较大者；平手删后点。

参数纪律（挖矿簿 2_state_machine.md §3.1 结构常数纪律同款）：
    默认值=文献美股月频值（±8 月窗/15/6/16 月/20%/30%）。A 股重标定＝P2 呈批项
    **禁自拟**——重标定换值=语义复核留痕事件，不是随手调参；换算呈批面见
    docs/04_research_records/cross_domain/condaxis/formreg/8_prereg_targeting.md §2（周层换算说明）。

用法：
    to_monthly(close_daily) -> pd.Series（月频收盘，ME 重采样）
    build_chronology(monthly_close, PSParams()) -> P-S 结果帧（转折点+段表）

先决门：裁定 #229 反转未裁——本件禁做 TDM 挂接/消费面接线/词表登记（冻结面）。

# [ALGO_FLOW] external: docs/03_modules/_domain_regime/algo_flow/ps_chronology.yaml
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import pairwise
from typing import Final

import numpy as np
import pandas as pd

__all__: Final = [
    "PSParams",
    "TurningPoint",
    "to_monthly",
    "find_turning_points",
    "enforce_alternation",
    "apply_censoring",
    "build_chronology",
]


# ---------------------------------------------------------------------------
# 结构常数区（P-S 文献美股月频默认值；调整须语义复核留痕——A 股重标定=呈批项禁自拟）
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class PSParams:
    """P-S 年代学参数组（默认=文献美股月频值；A 股重标定=P2 呈批项禁自拟）。

    Attributes:
        search_window: 转折点搜索窗（单侧月数，默认 8）。
        min_phase_months: 相位最短月数（<4 剔除，无豁免）。
        bull_min_months: 牛市相位（谷→峰）最短月数。
        bear_min_months: 熊市相位（峰→谷）最短月数。
        phase_amp_exempt: 相位幅度豁免线（>该幅度免最短相位约束，文献 0.20）。
        cycle_min_months: 完整周期（同类转折点间隔）最短月数。
        cycle_amp_exempt: 周期幅度豁免线（>该幅度免最短周期约束，文献 0.30）。
    """

    search_window: int = 8
    min_phase_months: int = 4
    bull_min_months: int = 15
    bear_min_months: int = 6
    phase_amp_exempt: float = 0.20
    cycle_min_months: int = 16
    cycle_amp_exempt: float = 0.30


@dataclass(frozen=True)
class TurningPoint:
    """转折点（idx=月频序列位置；kind='P' 峰/'T' 谷；confirmed=非截断窗候选）。"""

    idx: int
    kind: str  # 'P' | 'T'
    confirmed: bool


# ---------------------------------------------------------------------------
# 月频聚合
# ---------------------------------------------------------------------------


def to_monthly(close_daily: pd.Series) -> pd.Series:
    """日频收盘 → 月频收盘（每月最后交易日收盘，ME 重采样）。

    Args:
        close_daily: 升序 DatetimeIndex 日频收盘序列。

    Returns:
        月频收盘序列（index=各月末）。

    Raises:
        ValueError: 输入为空/非 DatetimeIndex。
    """
    _validate_series(close_daily)
    return close_daily.resample("ME").last().dropna()


# ---------------------------------------------------------------------------
# 转折点搜索
# ---------------------------------------------------------------------------


def find_turning_points(monthly_close: pd.Series, params: PSParams | None = None) -> list[TurningPoint]:
    """±search_window 月窗内找局部峰谷（纯函数）。

    峰=窗内最大值且严格高于窗内其余值（并列取首现，后者交由交替强制收敛）；
    窗在序列左右端截断处的候选 confirmed=False（右端=离线年代学确认滞后面）。

    Args:
        monthly_close: 月频收盘序列（DatetimeIndex 升序）。
        params: PSParams（None=文献默认）。

    Returns:
        转折点列表（按 idx 升序）。
    """
    p = params or PSParams()
    _validate_series(monthly_close)
    vals = monthly_close.to_numpy(dtype=float)
    n = len(vals)
    w = p.search_window
    if n < 2 * w + 1:
        raise ValueError("序列长度不足双侧搜索窗，拒绝找转折点（fail-closed；数值入 details）")
    out: list[TurningPoint] = []
    for i in range(n):
        lo, hi = max(0, i - w), min(n, i + w + 1)
        seg = vals[lo:hi]
        confirmed = (i - w >= 0) and (i + w < n)
        if vals[i] == seg.max() and (seg > vals[i]).sum() == 0:
            first_max = lo + int(np.argmax(seg))
            if first_max == i:
                out.append(TurningPoint(i, "P", confirmed))
        elif vals[i] == seg.min() and (seg < vals[i]).sum() == 0:
            first_min = lo + int(np.argmin(seg))
            if first_min == i:
                out.append(TurningPoint(i, "T", confirmed))
    return out


# ---------------------------------------------------------------------------
# 交替强制
# ---------------------------------------------------------------------------


def enforce_alternation(tps: list[TurningPoint], close: pd.Series) -> list[TurningPoint]:
    """相邻同类转折点留更极端者（双峰留高/双谷留低；纯函数）。

    Args:
        tps: 转折点列表。
        close: 对应月频收盘序列（取值判极端）。

    Returns:
        交替化后的转折点列表。
    """
    vals = close.to_numpy(dtype=float)
    kept: list[TurningPoint] = []
    for tp in tps:
        if not kept or kept[-1].kind != tp.kind:
            kept.append(tp)
            continue
        prev = kept[-1]
        keep_new = (tp.kind == "P" and vals[tp.idx] > vals[prev.idx]) or (
            tp.kind == "T" and vals[tp.idx] < vals[prev.idx]
        )
        if keep_new:
            kept[-1] = tp
    return kept


# ---------------------------------------------------------------------------
# censoring（迭代至不动点）
# ---------------------------------------------------------------------------


def _months_between(d1: pd.Timestamp, d2: pd.Timestamp) -> int:
    return (d2.year - d1.year) * 12 + (d2.month - d1.month)


def _phase_amplitude(vals: np.ndarray, i1: int, i2: int) -> float:
    return abs(float(vals[i2]) / float(vals[i1]) - 1.0)


def _prominence(vals: np.ndarray, tps: list[TurningPoint], pos: int) -> float:
    """转折点显著度=两侧相位幅度的较大者（端点只有一侧相位，取该侧）。"""
    amps: list[float] = []
    if pos > 0:
        amps.append(_phase_amplitude(vals, tps[pos - 1].idx, tps[pos].idx))
    if pos + 1 < len(tps):
        amps.append(_phase_amplitude(vals, tps[pos].idx, tps[pos + 1].idx))
    return max(amps) if amps else float("inf")


def apply_censoring(tps: list[TurningPoint], close: pd.Series, params: PSParams | None = None) -> list[TurningPoint]:
    """P-S censoring 迭代至不动点（纯函数；删点后重排交替再查）。

    规则（任务预注册口径＝P-S 2003）：
        a. 相位 < 4 月 → 剔除（无豁免）；
        b. 牛 < 15 月 / 熊 < 6 月 且幅度 ≤ 20% → 剔除；
        c. 完整周期（同类间隔）< 16 月 且周期幅度 ≤ 30% → 剔除。
    删点选择：删显著度（两侧相位幅度较大者）更低的端点；平手删后点（仓内约定，见模块 docstring）。

    Args:
        tps: 交替化后的转折点列表（非交替输入先被交替强制）。
        close: 月频收盘序列。
        params: PSParams（None=文献默认）。

    Returns:
        censoring 后的转折点列表（保持交替）。
    """
    p = params or PSParams()
    _validate_series(close)
    vals = close.to_numpy(dtype=float)
    dates = close.index

    cur = enforce_alternation(list(tps), close)
    while len(cur) >= 2:
        delete_pos: int | None = None
        # 规则 a/b：相位门槛（逐对检查，取首个违规）
        for i in range(len(cur) - 1):
            a, b = cur[i], cur[i + 1]
            months = _months_between(dates[a.idx], dates[b.idx])
            amp = _phase_amplitude(vals, a.idx, b.idx)
            if months < p.min_phase_months:
                required_exemption = False
            elif a.kind == "T":  # 谷→峰=牛市相位
                required_exemption = months >= p.bull_min_months or amp > p.phase_amp_exempt
            else:  # 峰→谷=熊市相位
                required_exemption = months >= p.bear_min_months or amp > p.phase_amp_exempt
            if not required_exemption:
                delete_pos = _weaker_endpoint(vals, cur, i, i + 1)
                break
        # 规则 c：完整周期门槛（同类转折点间隔；删两同类端点中显著度更低者）
        if delete_pos is None:
            for i in range(len(cur) - 2):
                a, b = cur[i], cur[i + 2]
                months = _months_between(dates[a.idx], dates[b.idx])
                amp = _phase_amplitude(vals, a.idx, b.idx)
                if months < p.cycle_min_months and amp <= p.cycle_amp_exempt:
                    delete_pos = _weaker_endpoint(vals, cur, i, i + 2)
                    break
        if delete_pos is None:
            break  # 不动点：全部规则不再触发
        cur.pop(delete_pos)
        cur = enforce_alternation(cur, close)
    return cur


def _weaker_endpoint(vals: np.ndarray, tps: list[TurningPoint], i: int, j: int) -> int:
    """相位两端点中删显著度更低者；平手删后点 j。"""
    return i if _prominence(vals, tps, i) > _prominence(vals, tps, j) else j


# ---------------------------------------------------------------------------
# 段表构建
# ---------------------------------------------------------------------------


def build_chronology(monthly_close: pd.Series, params: PSParams | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """月频收盘 → P-S 牛熊年代学（转折点表+段表；纯函数核）。

    Args:
        monthly_close: 月频收盘序列（DatetimeIndex 升序，ME 频率）。
        params: PSParams（None=文献默认；A 股重标定=呈批项禁自拟）。

    Returns:
        (turning_points, segments) 二元组：
        turning_points: DataFrame[idx, date, kind('P'/'T'), price, confirmed]；
        segments: DataFrame[phase('bull'/'bear'), start_date, end_date, start_price,
                             end_price, months, amplitude, confirmed]——
        bull=谷→峰、bear=峰→谷；首尾与序列端点间的残段 confirmed=False（边界残段）。

    Raises:
        ValueError: 输入空/非 DatetimeIndex/长度不足搜索窗。
    """
    p = params or PSParams()
    _validate_series(monthly_close)
    tps_raw = find_turning_points(monthly_close, p)
    tps = apply_censoring(tps_raw, monthly_close, p)
    vals = monthly_close.to_numpy(dtype=float)
    dates = monthly_close.index

    tp_frame = pd.DataFrame(
        [
            {
                "idx": tp.idx,
                "date": dates[tp.idx].strftime("%Y-%m-%d"),
                "kind": tp.kind,
                "price": float(vals[tp.idx]),
                "confirmed": tp.confirmed,
            }
            for tp in tps
        ]
    )

    seg_rows: list[dict] = []
    # 边界残段：序列起点→首个转折点
    if tps:
        first = tps[0]
        if first.idx > 0:
            seg_rows.append(_make_segment(vals, dates, None, first, confirmed=False))
        for a, b in pairwise(tps):
            seg_rows.append(_make_segment(vals, dates, a, b, confirmed=a.confirmed and b.confirmed))
        last = tps[-1]
        if last.idx < len(vals) - 1:
            seg_rows.append(_make_segment(vals, dates, last, None, confirmed=False))
    segs = pd.DataFrame(
        seg_rows,
        columns=["phase", "start_date", "end_date", "start_price", "end_price", "months", "amplitude", "confirmed"],
    )
    return tp_frame, segs


def _make_segment(
    vals: np.ndarray,
    dates: pd.DatetimeIndex,
    a: TurningPoint | None,
    b: TurningPoint | None,
    *,
    confirmed: bool,
) -> dict:
    """构段（a=None 时以序列起点为界；b=None 时以序列终点为界；残段 confirmed=False）。"""
    i1 = 0 if a is None else a.idx
    i2 = len(vals) - 1 if b is None else b.idx
    start_kind = "T" if a is None else a.kind  # 序列起点残段按后继转折点反推相位
    phase = "bull" if start_kind == "T" else "bear"
    return {
        "phase": phase,
        "start_date": dates[i1].strftime("%Y-%m-%d"),
        "end_date": dates[i2].strftime("%Y-%m-%d"),
        "start_price": float(vals[i1]),
        "end_price": float(vals[i2]),
        "months": _months_between(dates[i1], dates[i2]),
        "amplitude": round(_phase_amplitude(vals, i1, i2), 6),
        "confirmed": confirmed,
    }


def _validate_series(s: pd.Series) -> None:
    if s is None or len(s) == 0:
        raise ValueError("输入序列为空（fail-closed）")
    if not isinstance(s.index, pd.DatetimeIndex):
        raise ValueError("输入序列必须为 DatetimeIndex（月频收盘）")
    if not bool(s.index.is_monotonic_increasing):
        raise ValueError("输入序列必须按日期升序")
