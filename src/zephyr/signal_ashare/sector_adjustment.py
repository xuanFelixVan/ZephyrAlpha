# [BLUEPRINT] MOD-SIG-040 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/22_sector_rotation_spec.md §3.1③
# [MODULE] zephyr.signal_ashare.sector_adjustment
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES]
# [CONSUMERS] (待 G05 选股引擎 / BM-BUY-04 分批建仓条件①)
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] progress ∈ [0,1]; 纯函数无副作用; 输入均为盘后截面/滚动标量
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] nh_ratio_peak ≤ nh_ratio_trough → 扩散恢复维退化取 0
# [TESTS] tests/signal_ashare/test_sector_adjustment.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: elapsed_days(调整已持续交易日) + drawdown_pct(板块指数当前回撤深度)
# I2: nh_ratio_current/trough/peak(扩散指标=板块新高占比 当前/谷底/调整前峰值)
# A1: time_prog = min(elapsed/expected_window, 1)（持续时间维）
# A2: dd_prog = min(drawdown/target_drawdown, 1)（回撤深度维）
# A3: breadth_recovery = (current-trough)/(peak-trough) clip[0,1]（扩散指标恢复维, 首轮主指标）
# A4: progress = 0.4×time + 0.3×dd + 0.3×breadth（权重初拟待 G05/G08 校准）
# O1: progress ∈ [0,1] + action(≥80% ACTIVATE_PARTIAL 分批 / <40% BLOCK_DIP 拦截低吸 / 其余 OBSERVE)
# [/ALGO_FLOW]
"""调整周期进度追踪（22 号 spec §3.1③，MOD-SIG-040 planned→落码，BM-SEL-09）。

输入板块扩散指标（新高占比变体）+ 回撤深度 + 持续时间，输出进度百分比：
  - 进度 ≥80% → 激活 BM-BUY-04 分批建仓条件①
  - 进度 <40% → 初期拦截低吸信号（避免接飞刀）
  - 40%-80% → 观察区，不激活不拦截

扩散指标管"调整进度"，RRG（sector_rrg）管"轮动序列"，分工不重叠
（西部金工 2026-05：扩散指标在震荡市/快轮动期滞后，两者互补）。
滚动窗口/归一化权重为初拟，待 G05/G08 定参校准（spec §6 待裁定）。
"""

from __future__ import annotations

# ------------------------------------------------------------------
# 常量（初拟，22 号 spec §6 待 G05/G08 校准）
# ------------------------------------------------------------------

DEFAULT_EXPECTED_WINDOW = 20  # 预期调整窗口（交易日）
DEFAULT_TARGET_DRAWDOWN = 0.15  # 预期/历史典型回撤深度（15%）

_W_TIME = 0.4  # 持续时间维权重
_W_DRAWDOWN = 0.3  # 回撤深度维权重
_W_BREADTH = 0.3  # 扩散指标恢复维权重

PROGRESS_ACTIVATE = 0.80  # ≥80% 激活分批建仓
PROGRESS_BLOCK = 0.40  # <40% 拦截低吸

ACTION_ACTIVATE_PARTIAL = "ACTIVATE_PARTIAL"
ACTION_BLOCK_DIP = "BLOCK_DIP_BUYING"
ACTION_OBSERVE = "OBSERVE"


def compute_adjustment_progress(
    elapsed_days: int,
    drawdown_pct: float,
    nh_ratio_current: float,
    nh_ratio_trough: float,
    nh_ratio_peak: float,
    *,
    expected_window: int = DEFAULT_EXPECTED_WINDOW,
    target_drawdown: float = DEFAULT_TARGET_DRAWDOWN,
) -> float:
    """计算调整周期进度（三维加权，扩散指标恢复为主指标）。

    Args:
        elapsed_days: 调整已持续交易日数（自板块指数阶段高点起算）。
        drawdown_pct: 板块指数当前回撤深度（正数，0.12 = 回撤 12%）。
        nh_ratio_current: 板块新高占比当前值（扩散指标，[0,1]）。
        nh_ratio_trough: 调整期内新高占比谷底值。
        nh_ratio_peak: 调整前高点新高占比峰值。
        expected_window: 预期调整窗口交易日（默认 20）。
        target_drawdown: 预期/历史典型回撤深度（默认 0.15）。

    Returns:
        progress ∈ [0, 1]。
    """
    time_prog = min(max(elapsed_days, 0) / expected_window, 1.0) if expected_window > 0 else 1.0
    dd_prog = min(max(drawdown_pct, 0.0) / target_drawdown, 1.0) if target_drawdown > 0 else 1.0

    span = nh_ratio_peak - nh_ratio_trough
    if span > 0.0:
        breadth_recovery = (nh_ratio_current - nh_ratio_trough) / span
        breadth_recovery = max(0.0, min(1.0, breadth_recovery))
    else:
        breadth_recovery = 0.0

    progress = _W_TIME * time_prog + _W_DRAWDOWN * dd_prog + _W_BREADTH * breadth_recovery
    return max(0.0, min(1.0, progress))


def adjustment_action(progress: float) -> str:
    """进度 → BM-BUY-04 动作（≥80% 激活分批 / <40% 拦截低吸 / 其余观察）。"""
    if progress >= PROGRESS_ACTIVATE:
        return ACTION_ACTIVATE_PARTIAL
    if progress < PROGRESS_BLOCK:
        return ACTION_BLOCK_DIP
    return ACTION_OBSERVE
