# [BLUEPRINT] MOD-SIG-064 | 待统筹登记（21号 memo §3.4 路径 A 前置数据装配）
# [MODULE] zephyr.signal_ashare.strength_ic_data_assembler
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.strength_ic_weight_calibrator(STRENGTH_DIMENSIONS/DEFAULT_ROLLING_WINDOW)
# [CONSUMERS] strength_ic_weight_calibrator.compute_rolling_ic_weights（生产数据装配）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 纯函数装配（无 I/O）；60 日滚动窗口切片与 calibrator 对齐；前瞻收益长度与维度序列一致（n_ret == n_dim）；维度缺列 → 空序列（calibrator 回退经验权重）
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/21_stock_selection_engine.md §3.4
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 输入序列长度不一致 → ValueError（fail-closed）；前瞻收益含 NaN → 剔除对应索引（全维度同步）
# [TESTS] tests/signal_ashare/test_strength_ic_data_assembler.py
# [A_module] module_id=MOD-SIG-064 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""MOD-SIG-064 — 选股 6 维权重 IC 校准 60 日窗口数据装配器（21号 memo §3.4 前置）。

职责：将原始日度子分数记录装配为 strength_ic_weight_calibrator.compute_rolling_ic_weights
期望的输入契约：
    dim_series: dict[str, list[float]]  # 6 维子分数历史序列（末 60 日窗口）
    forward_returns: list[float]         # 前瞻收益序列（与维度序列对齐）

装配规则（写清）：
- 输入记录按 trade_date 升序排列（乱序输入自动重排）；
- 前瞻收益 = 次日收盘 / 当日收盘 - 1（T+1 收益，由调用方预计算或 records 含
  next_close 字段时自动推导）；
- 60 日窗口：取末 window 个样本（与 calibrator 内部切片一致，此处预切减少重复）；
- NaN 剔除：任一维度的前瞻收益为 NaN 的索引从所有维度同步剔除（防错位）；
- 维度缺列：记录中无该维度字段 → 该维空序列（calibrator 回退经验权重）。
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Final, Iterable, Sequence

from zephyr.signal_ashare.strength_ic_weight_calibrator import (
    DEFAULT_ROLLING_WINDOW,
    STRENGTH_DIMENSIONS,
)

__all__: Final = [
    "DailyStrengthRecord",
    "assemble_ic_window",
    "assemble_from_records",
]


@dataclass(frozen=True)
class DailyStrengthRecord:
    """单日 6 维子分数 + 收益标签记录（纯数据容器）。"""

    trade_date: str                       # YYYY-MM-DD
    scores: dict[str, float]              # 6 维子分数 {dim: score}
    close: float | None = None            # 当日收盘（前瞻收益推导用）
    next_close: float | None = None       # 次日收盘（前瞻收益推导用；None → 需外部供给收益）
    forward_return: float | None = None   # 预计算前瞻收益（优先于 close/next_close 推导）


def _safe_float(v: object) -> float | None:
    """安全转 float；None/非法/NaN → None。"""
    if v is None:
        return None
    try:
        f = float(v)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


def _derive_forward_return(rec: DailyStrengthRecord) -> float | None:
    """前瞻收益推导：预计算优先，否则 next_close/close - 1。"""
    if rec.forward_return is not None:
        return _safe_float(rec.forward_return)
    if rec.close is None or rec.next_close is None:
        return None
    c = _safe_float(rec.close)
    n = _safe_float(rec.next_close)
    if c is None or n is None or c <= 0:
        return None
    return n / c - 1.0


def assemble_ic_window(
    dim_series: dict[str, list[float]],
    forward_returns: list[float],
    *,
    window: int = DEFAULT_ROLLING_WINDOW,
) -> tuple[dict[str, list[float]], list[float]]:
    """60 日滚动窗口切片（纯函数，与 calibrator 内部对齐）。

    Args:
        dim_series: 6 维子分数历史序列（任意长度，取末 window）。
        forward_returns: 前瞻收益序列（须与各维序列长度一致）。
        window: 窗口长度（默认 60）。

    Returns:
        (dim_series_windowed, forward_returns_windowed)；
        长度 = min(window, 最短输入序列)。

    Raises:
        ValueError: 各维序列长度不一致，或收益序列与维度序列长度不一致（fail-closed）。
    """
    if window < 1:
        raise ValueError(f"window 非法（须正整数）: {window!r}")
    lengths = {len(v) for v in dim_series.values()}
    if len(lengths) > 1:
        raise ValueError(f"维度序列长度不一致: {dict((k, len(v)) for k, v in dim_series.items())}")
    n_dim = lengths.pop() if lengths else 0
    n_ret = len(forward_returns)
    if n_dim != n_ret:
        raise ValueError(f"维度序列长度 {n_dim} ≠ 收益序列长度 {n_ret}")
    m = min(window, n_dim)
    if m == 0:
        return {d: [] for d in STRENGTH_DIMENSIONS}, []
    return (
        {d: list(series[-m:]) for d, series in dim_series.items()},
        list(forward_returns[-m:]),
    )


def assemble_from_records(
    records: Iterable[DailyStrengthRecord],
    *,
    window: int = DEFAULT_ROLLING_WINDOW,
) -> tuple[dict[str, list[float]], list[float]]:
    """从日度记录装配 60 日窗口 IC 前置数据（纯函数主入口）。

    Args:
        records: DailyStrengthRecord 可迭代（自动按 trade_date 升序重排）。
        window: 窗口长度（默认 60）。

    Returns:
        (dim_series, forward_returns)——可直接传入
        strength_ic_weight_calibrator.compute_rolling_ic_weights。

    Raises:
        ValueError: 记录非法（trade_date 空/维度值非数值）。
    """
    sorted_records = sorted(records, key=lambda r: r.trade_date)
    if not sorted_records:
        return {d: [] for d in STRENGTH_DIMENSIONS}, []

    # 逐日提取（NaN 索引同步剔除在窗口切片后执行）
    raw_dim: dict[str, list[float | None]] = {d: [] for d in STRENGTH_DIMENSIONS}
    raw_ret: list[float | None] = []
    for rec in sorted_records:
        if not isinstance(rec.trade_date, str) or not rec.trade_date.strip():
            raise ValueError(f"trade_date 非法（须非空字符串）: {rec.trade_date!r}")
        for dim in STRENGTH_DIMENSIONS:
            raw_dim[dim].append(_safe_float(rec.scores.get(dim)))
        raw_ret.append(_derive_forward_return(rec))

    # 同步剔除：任一维度或收益为 None/NaN 的索引
    n = len(sorted_records)
    valid_idx: list[int] = []
    for i in range(n):
        if raw_ret[i] is None:
            continue
        if any(raw_dim[d][i] is None for d in STRENGTH_DIMENSIONS):
            continue
        valid_idx.append(i)

    dim_series: dict[str, list[float]] = {
        d: [raw_dim[d][i] for i in valid_idx]  # type: ignore[misc]
        for d in STRENGTH_DIMENSIONS
    }
    forward_returns = [raw_ret[i] for i in valid_idx]  # type: ignore[misc]

    return assemble_ic_window(dim_series, forward_returns, window=window)
