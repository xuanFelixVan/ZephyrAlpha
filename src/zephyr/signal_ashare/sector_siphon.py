# [BLUEPRINT] MOD-SIG-026 supplement | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/22_sector_rotation_spec.md §3.1⑤
# [MODULE] zephyr.signal_ashare.sector_siphon
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES]
# [CONSUMERS] (待 G05 选股引擎市场状态适配输入 / sector_rotation_state 串联精判)
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] hhi ∈ [0,1]; outflow_ratio ∈ [0,1]; 纯函数无副作用
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空板块列表 → is_siphon=False; 历史窗口样本 <2 或 σ=0 → z=0(降级不触发)
# [TESTS] tests/signal_ashare/test_sector_siphon.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: sectors(当日全市场板块 turnover+net_inflow, money_flow×sector_constituent 聚合)
# I2: hhi/conc/outflow 三信号各自滚动窗口历史序列（z-score 标准化用）
# A1: 信号① hhi_top_n = Σ(头部N板块成交额份额)², N=5
# A2: 信号② inflow_concentration = 头部N净流入和 / 全市场|净流入|和
# A3: 信号③ outflow_ratio = 其余板块净流出家数 / 其余板块家数
# A4: rolling_zscore 三信号标准化 → siphon_score = 0.4×z_hhi + 0.35×z_conc + 0.25×z_outflow
# O1: SiphonResult(is_siphon = score>1.5σ, siphon_score, siphon_sectors=头部N名单)
# [/ALGO_FLOW]
"""虹吸态识别（22 号 spec §3.1⑤，BM-SEL-08 增强补施工）。

虹吸态 = 少数头部强势板块吸金致其余板块缺血的极端分化状态（情绪周期
主升/疯狂态的板块级表现；2026 实证：国海固收 2026-07 "AI 产业链持续虹吸"，
上半年电子+86%/通信+74% vs 商贸零售-29%，首尾差超 115pct）。

三信号滚动 z-score 加权（HHI 0.4 / 净流入集中度 0.35 / 净流出比例 0.25），
z > 1.5σ（正态 ~93% 分位）触发。虹吸态用相对 z-score（相对近期常态的极端
分化），5 状态分类用绝对阈值——两者可串联（5 状态先判大类，虹吸态再精判）。

参数（N=5 / 权重 / 阈值 1.5）均待 G05/G08 实盘校准（spec §6 待裁定，
需 ≥3 个月虹吸态样本后标定）。
"""

from __future__ import annotations

from dataclasses import dataclass, field

# ------------------------------------------------------------------
# 常量（初拟，22 号 spec §6 待 G05/G08 校准）
# ------------------------------------------------------------------

DEFAULT_N_TOP = 5  # 头部 N 板块数（与 §3.1⑨ hhi_top5 协同）
DEFAULT_ZSCORE_THRESHOLD = 1.5  # z > 1.5σ = 虹吸态（~93% 分位极端分化）

_W_HHI = 0.4  # 成交额集中度权重（核心）
_W_CONC = 0.35  # 净流入集中度权重
_W_OUTFLOW = 0.25  # 其余板块净流出比例权重（流出是后果非原因）


@dataclass(frozen=True)
class SectorFlowSnapshot:
    """板块资金截面（money_flow × sector_constituent 聚合后的板块级输入）"""

    name: str
    turnover: float  # 成交额
    net_inflow: float  # 净流入


@dataclass(frozen=True)
class SiphonResult:
    """虹吸态识别结果"""

    is_siphon: bool
    siphon_score: float
    siphon_sectors: list[str] = field(default_factory=list)
    z_hhi: float = 0.0
    z_conc: float = 0.0
    z_outflow: float = 0.0


def rolling_zscore(value: float, history: list[float]) -> float:
    """当前值相对滚动窗口历史序列的 z-score。

    历史样本 <2 或标准差为 0 时返回 0.0（降级不触发，不误报）。
    """
    if len(history) < 2:
        return 0.0
    mean = sum(history) / len(history)
    var = sum((x - mean) ** 2 for x in history) / (len(history) - 1)
    std = var**0.5
    if std == 0.0:
        return 0.0
    return (value - mean) / std


def detect_siphon_state(
    sectors: list[SectorFlowSnapshot],
    hhi_history: list[float],
    conc_history: list[float],
    outflow_history: list[float],
    *,
    n_top: int = DEFAULT_N_TOP,
    threshold: float = DEFAULT_ZSCORE_THRESHOLD,
) -> SiphonResult:
    """虹吸态识别——三信号滚动 z-score 加权。

    Args:
        sectors: 当日全市场板块列表（含 turnover, net_inflow）。
        hhi_history: 信号① HHI 的滚动窗口历史序列（不含当日）。
        conc_history: 信号② 净流入集中度的滚动窗口历史序列。
        outflow_history: 信号③ 净流出比例的滚动窗口历史序列。
        n_top: 头部 N 板块数（默认 5，与 hhi_top5 协同）。
        threshold: 触发阈值（默认 1.5σ）。

    Returns:
        SiphonResult(is_siphon, siphon_score, siphon_sectors, z 明细)。
    """
    if not sectors:
        return SiphonResult(is_siphon=False, siphon_score=0.0)

    total_turnover = sum(s.turnover for s in sectors)
    top_n = sorted(sectors, key=lambda s: s.turnover, reverse=True)[:n_top]

    # 信号①：头部 N 板块成交额集中度（HHI，越接近 1 越集中）
    if total_turnover > 0:
        hhi_top_n = sum((s.turnover / total_turnover) ** 2 for s in top_n)
    else:
        hhi_top_n = 0.0

    # 信号②：净流入集中度（头部 N 净流入和 / 全市场 |净流入| 和）
    total_abs_inflow = sum(abs(s.net_inflow) for s in sectors)
    top_n_inflow = sum(s.net_inflow for s in top_n)
    inflow_concentration = top_n_inflow / total_abs_inflow if total_abs_inflow > 0 else 0.0

    # 信号③：其余板块资金净流出比例
    top_n_ids = {id(s) for s in top_n}
    rest = [s for s in sectors if id(s) not in top_n_ids]
    outflow_ratio = sum(1 for s in rest if s.net_inflow < 0) / len(rest) if rest else 0.0

    # 三信号滚动 z-score 标准化后加权
    z_hhi = rolling_zscore(hhi_top_n, hhi_history)
    z_conc = rolling_zscore(inflow_concentration, conc_history)
    z_outflow = rolling_zscore(outflow_ratio, outflow_history)
    siphon_score = _W_HHI * z_hhi + _W_CONC * z_conc + _W_OUTFLOW * z_outflow

    is_siphon = siphon_score > threshold
    return SiphonResult(
        is_siphon=is_siphon,
        siphon_score=siphon_score,
        siphon_sectors=[s.name for s in top_n] if is_siphon else [],
        z_hhi=z_hhi,
        z_conc=z_conc,
        z_outflow=z_outflow,
    )
