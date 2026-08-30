# [BLUEPRINT] MOD-L02-009 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-ANA-08
# [MODULE] zephyr.factor.analysis.multifactor_crowding_monitor
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] pandas; numpy
# [CONSUMERS] multifactor_decay_lifecycle(CUSUM联动); multifactor_pit_backtest
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-004: PIT铁律——三代理仅用决策日及之前数据; 与IC衰减正交可同时触发
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 数据不足->对应分量0分+degraded标记; 综合分>0.70->REDUCE_WEIGHT_50
# [TESTS] tests/factor/test_multifactor_crowding_monitor.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: etf_holdings(pd.Series ETF持仓时序) + factor_returns_panel(pd.DataFrame 因子收益面板) + quant_seat_ratio(龙虎榜量化席位占比, §3.11 detect_quant_seat_warning 复用)
# I2: CrowdingParams(etf窗口60/预警0.20; corr窗口40/预警0.70; 席位预警0.35; 崩盘高风险0.70)
# F1: assess(①ETF持仓增长=近20日vs前40日基线 ②因子间平均相关性 ③量化席位占比, 各归一化0-1)
# F2: 分级响应(综合=三者均值; >0.70→REDUCE_WEIGHT_50降权50%+尾部预警; >0.50→ALERT监控+CUSUM联动; 否则MONITOR)
# O1: CrowdingAssessment(etf_score/corr_score/seat_score/composite/level/action/degraded)
# [/ALGO_FLOW]
"""
25号memo §3.7#5 因子拥挤实时监控（CrowdingRealTimeMonitor，MVP 必做）。

§3.3 衰减监控管"信号变弱"（均值），因子拥挤管"太多人用同一因子"（尾部风险）——
拥挤因子风格切换时崩溃概率高 1.7-1.8x（arXiv:2512.11913），2026-07 A 股 57 只
量化基金踩雷即实时验证。两者正交，可同时触发（IC 未衰减但拥挤度高=崩盘前兆）。

三代理指标（MVP 基线）：
  ① ETF 持仓增长（近 20 日 vs 前 40 日基线，arXiv:2512.11913 验证 ρ=-0.63）
  ② 因子间平均相关性（滚动 40 日，共识形成）
  ③ 龙虎榜量化席位占比（A 股特色代理，§3.11 detect_quant_seat_warning 复用）

BM-RC-06-D 三个深度增强项（策略逻辑相似度/去杠杆路径预案/拥挤悖论防护）
登记 design 远期——依赖多策略并发实盘数据，当前无输入不施工。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: etf_holdings 参数
#   fields: 参数 etf_holdings，类型注解 pd.Series | None
#   code: multifactor_crowding_monitor.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: factor_returns_panel 参数
#   fields: 参数 factor_returns_panel，类型注解 pd.DataFrame | None
#   code: multifactor_crowding_monitor.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: quant_seat_ratio 参数
#   fields: 参数 quant_seat_ratio，类型注解 float | None
#   code: multifactor_crowding_monitor.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: params 参数
#   fields: 参数 params，类型注解 CrowdingParams | None
#   code: multifactor_crowding_monitor.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① assess
#   name_en: assess
#   intro: 拥挤实时评估——三代理归一化得分均值 → 分级响应。
#   desc: 拥挤实时评估——三代理归一化得分均值 → 分级响应。 Returns: CrowdingAssessment。composite>0.70→REDUCE_WEIGHT_50；>0…；源码 L167-L199
#   inputs: etf_holdings factor_returns_panel quant_seat_ratio params
#   outputs: CrowdingAssessment
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: CrowdingAssessment
#   name_en: CrowdingAssessment
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: multifactor_decay_lifecycle(CUSUM联动); multifactor_pit_backtest
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

__all__ = [
    "CrowdingParams",
    "CrowdingLevel",
    "CrowdingAssessment",
    "assess",
]


@dataclass(frozen=True)
class CrowdingParams:
    """拥挤监控阈值参数（25号memo §3.7#5 参数表）。"""

    etf_holding_window: int = 60  # ETF 持仓变化滚动窗口
    etf_holding_alert: float = 0.20  # ETF 持仓增长>20%→拥挤加速
    factor_corr_window: int = 40  # 因子收益相关性滚动窗口
    factor_corr_alert: float = 0.70  # 因子间平均相关性>0.70→拥挤
    quant_seat_ratio_alert: float = 0.35  # 龙虎榜量化席位占比>35%→拥挤
    crash_risk_high: float = 0.70  # 综合分>0.70→高崩盘风险→降仓
    crash_risk_mid: float = 0.50  # 综合分>0.50→ALERT


class CrowdingLevel(str, Enum):
    REDUCE_WEIGHT_50 = "REDUCE_WEIGHT_50"  # 降权 50% + 尾部风险预警
    ALERT = "ALERT"  # 监控 + CUSUM 联动
    MONITOR = "MONITOR"


@dataclass(frozen=True)
class CrowdingAssessment:
    """拥挤评估结果。"""

    etf_score: float
    corr_score: float
    seat_score: float
    composite: float
    level: CrowdingLevel
    degraded: tuple[str, ...] = ()  # 数据不足的分量名


def _clip01(x: float) -> float:
    return float(min(max(x, 0.0), 1.0))


def _etf_growth_score(etf_holdings: pd.Series | None, p: CrowdingParams) -> tuple[float, bool]:
    """ETF 持仓增长得分：近 20 日均值 vs 前 40 日基线，>20% 满分。"""
    if etf_holdings is None or len(etf_holdings) < p.etf_holding_window:
        return 0.0, True
    recent = float(etf_holdings.iloc[-20:].mean())
    baseline = float(etf_holdings.iloc[-p.etf_holding_window : -20].mean())
    if baseline <= 0:
        return 0.0, True
    growth = recent / baseline - 1.0
    return _clip01(growth / p.etf_holding_alert), False


def _corr_score(factor_returns_panel: pd.DataFrame | None, p: CrowdingParams) -> tuple[float, bool]:
    """因子间平均相关性得分：滚动窗口内平均两两相关，>0.70 满分。"""
    if factor_returns_panel is None or factor_returns_panel.shape[1] < 2:
        return 0.0, True
    window = factor_returns_panel.dropna().iloc[-p.factor_corr_window :]
    if len(window) < 2:
        return 0.0, True
    corr = window.corr().to_numpy()
    n = corr.shape[0]
    off_diag = corr[np.triu_indices(n, k=1)]
    avg_corr = float(np.nanmean(off_diag)) if off_diag.size else 0.0
    return _clip01(avg_corr / p.factor_corr_alert), False


def _seat_score(quant_seat_ratio: float | None, p: CrowdingParams) -> tuple[float, bool]:
    """量化席位占比得分：>35% 满分。"""
    if quant_seat_ratio is None:
        return 0.0, True
    return _clip01(float(quant_seat_ratio) / p.quant_seat_ratio_alert), False


def assess(
    etf_holdings: pd.Series | None = None,
    factor_returns_panel: pd.DataFrame | None = None,
    quant_seat_ratio: float | None = None,
    params: CrowdingParams | None = None,
) -> CrowdingAssessment:
    """拥挤实时评估——三代理归一化得分均值 → 分级响应。

    Returns:
        CrowdingAssessment。composite>0.70→REDUCE_WEIGHT_50；>0.50→ALERT；否则 MONITOR。
    """
    p = params or CrowdingParams()
    etf_s, etf_deg = _etf_growth_score(etf_holdings, p)
    corr_s, corr_deg = _corr_score(factor_returns_panel, p)
    seat_s, seat_deg = _seat_score(quant_seat_ratio, p)
    degraded = tuple(n for n, d in (("etf", etf_deg), ("corr", corr_deg), ("seat", seat_deg)) if d)
    composite = (etf_s + corr_s + seat_s) / 3.0
    if composite > p.crash_risk_high:
        level = CrowdingLevel.REDUCE_WEIGHT_50
    elif composite > p.crash_risk_mid:
        level = CrowdingLevel.ALERT
    else:
        level = CrowdingLevel.MONITOR
    if level is CrowdingLevel.REDUCE_WEIGHT_50:
        log.warning("crowding: 综合分 %.2f>%.2f 高崩盘风险→降权50%%", composite, p.crash_risk_high)
    return CrowdingAssessment(
        etf_score=etf_s,
        corr_score=corr_s,
        seat_score=seat_s,
        composite=composite,
        level=level,
        degraded=degraded,
    )
