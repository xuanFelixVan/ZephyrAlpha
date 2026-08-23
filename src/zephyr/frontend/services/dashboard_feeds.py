# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md
# [MODULE] zephyr.frontend.services.dashboard_feeds
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] zephyr.pf_core（相关性口径）; zephyr.signal_ashare.intraday_buy_sell_point_analyzer; zephyr.position.core.t1_sellable/position_state_machine/drawdown_controller/calendar_position_constraint; zephyr.risk.core.stress_test_engine/liquidity_monitor/tail_risk_monitor; zephyr.shared.foundation.errors; numpy; pandas
# [CONSUMERS] 前端 dashboard 各页（作战室 W5/持仓监控/T分析/盘后复盘/盘中实时风控区）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 结论级输出（全部返回 JSON 可序列化 dict）; 数据源依赖注入（禁真连 DB）; 输入非法 fail-closed 抛 DashboardFeedInputError 或透传 prod ValueError; 只读查询无任何写副作用
# [MODIFY-GUARD] 反向账 C 类通道（BFE-01/25/26/27/28/30/31/32 + GAP-F-04）——本层只做 prod 引擎结果的查询整形，禁止内嵌业务算法
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DashboardFeedInputError(ZA-FE-0005，服务层输入校验); prod 引擎错误按各模块 ERROR_CONTRACT 透传
# [TESTS] tests/frontend/test_dashboard_feeds.py
# [A_module] module_id=MOD-L08-001 | layer=service | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Dashboard Feeds — 前端结论级查询接口层（反向账 C 类通道，2026-08-23 AI-K3-GW-CWIRE）。

九条查询接口，把已 production 的后端引擎结果整形为前端可直接渲染的结构化 dict：

| 函数 | 缺口/通道 | 底层 prod 真源 | 前端落点 |
|---|---|---|---|
| query_correlation_netting | GAP-F-04 | 组合域相关性约束口径（MOD-PF-006 C5 阈值族，夜班 #205/#207） | 作战室 W5 / 持仓监控页 |
| query_intraday_buy_sell_points | BFE-01 | MOD-SIG-024 IntradayBuySellAnalyzer | T分析页信号源 |
| query_t1_sellable | BFE-28 | t1_sellable_weights（31号遗留#30/32号§6 口径） | T分析页底仓卡 |
| query_stress_test_summary | BFE-32 | StressTestEngine.run_all_historical（MOD-RK-12） | 复盘页一卡（结论级） |
| query_position_state_snapshot | BFE-25 | PositionStateMachine（MOD-POS-002） | 持仓页状态列 |
| query_drawdown_throttle | BFE-26 | DrawdownController（MOD-POS-008） | 风控实时扩展 |
| query_calendar_position_constraints | BFE-27 | CalendarPositionConstraint（MOD-POS-017） | 作战室 W5 |
| query_liquidity_status | BFE-30 | LiquidityMonitor（MOD-RK-08） | 风控实时一行 |
| query_tail_risk_status | BFE-31 | TailRiskMonitor（MOD-RK-15） | 风控实时一行 |

纪律：本层零业务算法——相关性聚类仅为"高相关合并计 1 笔风险"的展示口径聚合
（union-find 展示层分组，阈值默认对齐 C5 max_correlation=0.7）；所有判定逻辑
一律委托 prod 引擎。数据由调用方注入（mock/真实适配器均可），本层不触 DB。

Version: 0.1.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Final, Mapping, Sequence

import numpy as np
import pandas as pd

from zephyr.position.core.calendar_position_constraint import (
    CalendarPositionConstraint,
    PositionInfo,
)
from zephyr.position.core.drawdown_controller import (
    BlackSwanSignal,
    DrawdownController,
    DrawdownInfo,
    StrategyPnl,
    VarCvarMetrics,
)
from zephyr.position.core.position_state_machine import (
    PositionState,
    PositionStateMachine,
)
from zephyr.position.core.t1_sellable import t1_sellable_weights
from zephyr.risk.core.liquidity_monitor import LiquidityMonitor
from zephyr.risk.core.stress_test_engine import HISTORICAL_SCENARIOS, StressTestEngine
from zephyr.risk.core.tail_risk_monitor import TailRiskMonitor
from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.signal_ashare.intraday_buy_sell_point_analyzer import (
    IntradayBuySellAnalyzer,
    IntradayBuySellInput,
)

__all__ = [
    "DashboardFeedInputError",
    "DrawdownThrottleRequest",
    "query_calendar_position_constraints",
    "query_correlation_netting",
    "query_drawdown_throttle",
    "query_intraday_buy_sell_points",
    "query_liquidity_status",
    "query_position_state_snapshot",
    "query_stress_test_summary",
    "query_t1_sellable",
    "query_tail_risk_status",
]


class DashboardFeedInputError(ZephyrBaseError):
    """前端查询接口层输入非法（权重为负/相关性越界/空输入等）。"""

    error_code = "ZA-FE-0005"


# ──────────────────────────────────────────────────────────────────────────────
# 展示层静态映射（只读，Final）
# ──────────────────────────────────────────────────────────────────────────────

_STATE_ZH: Final[dict[PositionState, str]] = {
    PositionState.NONE: "无持仓",
    PositionState.BUILDING: "建仓中",
    PositionState.ACTIVE: "持仓中",
    PositionState.OBSERVING: "观察期",
    PositionState.REDUCING: "减仓中",
    PositionState.EXITING: "清仓中",
    PositionState.CLOSED: "已平仓",
}

_REC_ZH: Final[dict[str, str]] = {
    "buy": "买入",
    "sell": "卖出",
    "hold": "持有",
    "wait": "等待",
}

_GEAR_ZH: Final[dict[str, str]] = {
    "full": "油门全开",
    "half": "半油门",
    "brake": "刹车",
    "stop": "停机清仓",
}

#: 相关性净额聚合默认阈值——对齐 MOD-PF-006 C5 max_correlation=0.7（展示口径）
DEFAULT_NETTING_THRESHOLD: Final[float] = 0.7


# ──────────────────────────────────────────────────────────────────────────────
# 请求数据类（参数 >7 收敛）
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class DrawdownThrottleRequest:
    """回撤油门刹车查询入参（BFE-26）。

    Attributes:
        drawdown_pct: 当前回撤率（负数，0=无回撤）
        peak_nav: 峰值净值
        current_nav: 当前净值
        var_95: 95% VaR（正值比率）
        cvar_95: 95% CVaR（正值比率，≥ var_95）
        recovered_pct: 回撤回补比例（0=未回补）
        strategy_drawdowns: 策略级回撤 {strategy_id: dd_pct(负)}，可选
        var_breach_state: VaR breach 状态机状态（"NORMAL"/"BREACHED"/"RECOVERY"），可选
    """

    drawdown_pct: float
    peak_nav: float
    current_nav: float
    var_95: float
    cvar_95: float
    recovered_pct: float = 0.0
    strategy_drawdowns: Mapping[str, float] | None = None
    var_breach_state: str | None = None


# ──────────────────────────────────────────────────────────────────────────────
# GAP-F-04 相关性净额（作战室 W5 / 持仓监控页）
# ──────────────────────────────────────────────────────────────────────────────


def query_correlation_netting(
    positions: Mapping[str, float],
    correlation_pairs: Sequence[tuple[str, str, float]],
    threshold: float = DEFAULT_NETTING_THRESHOLD,
    as_of: str | None = None,
) -> dict[str, Any]:
    """相关性净额查询——高相关持仓合并计 1 笔风险（防"五个仓位实则一个赌注"）。

    展示口径：|ρ| ≥ threshold 的持仓两两并入同簇（union-find 传递闭包），
    每簇合并为 1 个净风险单位；阈值默认对齐 MOD-PF-006 C5 max_correlation=0.7。

    Args:
        positions: {symbol: 权重}（非负有限值）
        correlation_pairs: [(symbol_a, symbol_b, rho)]，rho ∈ [-1, 1]
        threshold: 聚合阈值（默认 0.7）
        as_of: 数据日期（展示用，可选）

    Returns:
        dict：threshold/as_of/gross_position_count/net_risk_units/netting_reduction/
        clusters[{members, max_pair_rho, combined_weight}]/singletons

    Raises:
        DashboardFeedInputError: 权重负值/非有限、rho 越界、threshold 越界
    """
    if not 0.0 < threshold <= 1.0:
        raise DashboardFeedInputError(f"threshold 须在 (0,1]，got {threshold}")
    for sym, w in positions.items():
        if not math.isfinite(w) or w < 0:
            raise DashboardFeedInputError(f"持仓权重非法（须为有限非负值）：{sym}={w}")

    parent: dict[str, str] = {s: s for s in positions}

    def find(s: str) -> str:
        while parent[s] != s:
            parent[s] = parent[parent[s]]
            s = parent[s]
        return s

    cluster_best_rho: dict[str, float] = {}
    for a, b, rho in correlation_pairs:
        if not math.isfinite(rho) or not -1.0 <= rho <= 1.0:
            raise DashboardFeedInputError(f"相关性系数越界（须 ∈ [-1,1]）：{a}/{b} rho={rho}")
        if a not in parent or b not in parent or abs(rho) < threshold:
            continue
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra
        root = find(a)
        cluster_best_rho[root] = max(cluster_best_rho.get(root, 0.0), abs(rho))

    groups: dict[str, list[str]] = {}
    for sym in positions:
        groups.setdefault(find(sym), []).append(sym)

    clusters: list[dict[str, Any]] = []
    singletons: list[str] = []
    for members in groups.values():
        if len(members) < 2:
            singletons.extend(members)
            continue
        root = find(members[0])
        clusters.append(
            {
                "members": sorted(members),
                "max_pair_rho": round(cluster_best_rho.get(root, threshold), 4),
                "combined_weight": round(sum(positions[m] for m in members), 6),
            }
        )
    clusters.sort(key=lambda c: c["combined_weight"], reverse=True)
    singletons.sort()

    gross = len(positions)
    net = len(clusters) + len(singletons)
    return {
        "threshold": threshold,
        "as_of": as_of,
        "gross_position_count": gross,
        "net_risk_units": net,
        "netting_reduction": gross - net,
        "clusters": clusters,
        "singletons": singletons,
    }


# ──────────────────────────────────────────────────────────────────────────────
# BFE-01 盘中买卖点（MOD-SIG-024 → T分析页信号源）
# ──────────────────────────────────────────────────────────────────────────────


def query_intraday_buy_sell_points(input_data: IntradayBuySellInput) -> dict[str, Any]:
    """盘中买卖点查询（6 买 6 卖 + 3 重确认，MOD-SIG-024 prod 直出整形）。

    Args:
        input_data: IntradayBuySellInput（现价/阻力位/均线/量比/资金/竞价/封单等 +
            大盘情绪分/板块强度分/资金净流入三重确认分）

    Returns:
        dict：symbol/buy_signals/sell_signals/confirmations/
        all_confirmations_passed/recommendation/recommendation_zh/
        overall_confidence/is_degraded
    """
    result = IntradayBuySellAnalyzer().analyze(input_data)
    return {
        "symbol": result.symbol,
        "buy_signals": [
            {
                "point_type": s.point_type,
                "confidence": s.confidence,
                "reference_price": s.reference_price,
                "reason": s.reason,
            }
            for s in result.buy_signals
        ],
        "sell_signals": [
            {
                "point_type": s.point_type,
                "confidence": s.confidence,
                "reference_price": s.reference_price,
                "reason": s.reason,
            }
            for s in result.sell_signals
        ],
        "confirmations": [
            {
                "confirmation_type": c.confirmation_type,
                "passed": c.passed,
                "actual_value": c.actual_value,
                "threshold": c.threshold,
                "reason": c.reason,
            }
            for c in result.confirmations
        ],
        "all_confirmations_passed": result.all_confirmations_passed,
        "recommendation": result.recommendation,
        "recommendation_zh": _REC_ZH.get(result.recommendation, result.recommendation),
        "overall_confidence": result.overall_confidence,
        "is_degraded": result.is_degraded,
    }


# ──────────────────────────────────────────────────────────────────────────────
# BFE-28 T+1 可卖额度（T分析页底仓卡）
# ──────────────────────────────────────────────────────────────────────────────


def query_t1_sellable(
    last_session_weights: Mapping[str, float],
    today_sold_weights: Mapping[str, float] | None = None,
) -> dict[str, Any]:
    """T+1 可卖额度查询（昨仓 − 今日已卖，负值兜底 0；32号 §6 口径）。

    Args:
        last_session_weights: {symbol: T-1 收盘持仓权重}
        today_sold_weights: {symbol: 今日已卖权重}，可选

    Returns:
        dict：rows[{symbol, last_weight, sold_today_weight, sellable_weight}]/
        position_count/total_sellable_weight

    Raises:
        ValueError: 权重为负或非有限值（prod t1_sellable_weights 透传）
    """
    sellable = t1_sellable_weights(dict(last_session_weights), dict(today_sold_weights or {}))
    sold = today_sold_weights or {}
    rows = [
        {
            "symbol": sym,
            "last_weight": last_session_weights[sym],
            "sold_today_weight": sold.get(sym, 0.0),
            "sellable_weight": w,
        }
        for sym, w in sorted(sellable.items())
    ]
    return {
        "rows": rows,
        "position_count": len(rows),
        "total_sellable_weight": round(sum(sellable.values()), 6),
    }


# ──────────────────────────────────────────────────────────────────────────────
# BFE-32 压力测试盘后风险验证（复盘页一卡，结论级）
# ──────────────────────────────────────────────────────────────────────────────


def query_stress_test_summary(
    weights: Mapping[str, float],
    portfolio_value: float,
    now: datetime | None = None,
) -> dict[str, Any]:
    """压力测试盘后验证摘要——三套历史情景（2008/2015/2020）全跑，结论级输出。

    Args:
        weights: {symbol/sector: weight}（自动归一化，板块键对齐 HISTORICAL_SCENARIOS）
        portfolio_value: 组合总价值
        now: 时间戳（可选，测试注入）

    Returns:
        dict：scenarios[{scenario, description, portfolio_loss_pct,
        portfolio_loss_value, var_exceeded, is_severe}]/worst_scenario/
        severe_count/conclusion_zh
    """
    engine = StressTestEngine()
    results = engine.run_all_historical(dict(weights), portfolio_value, now)
    scenarios = [
        {
            "scenario": r.scenario.name,
            "description": HISTORICAL_SCENARIOS[r.scenario.name]["description"],
            "portfolio_loss_pct": r.portfolio_loss_pct,
            "portfolio_loss_value": r.portfolio_loss_value,
            "var_exceeded": r.var_exceeded,
            "is_severe": r.is_severe,
        }
        for r in results
    ]
    worst = min(scenarios, key=lambda s: s["portfolio_loss_pct"])
    severe_count = sum(1 for s in scenarios if s["is_severe"])
    conclusion = (
        f"三套历史情景最大单日压力损失 {worst['portfolio_loss_pct']:.2%}"
        f"（{worst['description']}），严重情景 {severe_count}/{len(scenarios)} 套"
    )
    return {
        "scenarios": scenarios,
        "worst_scenario": worst,
        "severe_count": severe_count,
        "conclusion_zh": conclusion,
    }


# ──────────────────────────────────────────────────────────────────────────────
# BFE-25 持仓状态机快照（持仓页状态列）
# ──────────────────────────────────────────────────────────────────────────────


def query_position_state_snapshot(
    machines: Sequence[PositionStateMachine],
) -> dict[str, Any]:
    """持仓状态机快照——逐票生命周期状态 + 买/卖权限位。

    Args:
        machines: 各持仓标的的 PositionStateMachine 实例（状态真源在 prod 机内）

    Returns:
        dict：rows[{symbol, state, state_zh, can_buy, can_rebuild, is_observing,
        observing_reason, is_in_cooldown, cooldown_until, graduation_weight}]/
        position_count/observing_count/cooldown_count
    """
    rows: list[dict[str, Any]] = []
    for fsm in machines:
        ctx = fsm.context
        rows.append(
            {
                "symbol": ctx.symbol,
                "state": ctx.state.value,
                "state_zh": _STATE_ZH[ctx.state],
                "can_buy": fsm.can_buy(),
                "can_rebuild": fsm.can_rebuild(),
                "is_observing": fsm.is_observing,
                "observing_reason": (
                    ctx.observing_reason.value if ctx.observing_reason is not None else None
                ),
                "is_in_cooldown": fsm.is_in_cooldown,
                "cooldown_until": (
                    ctx.cooldown_until.isoformat() if ctx.cooldown_until is not None else None
                ),
                "graduation_weight": ctx.graduation_weight,
            }
        )
    rows.sort(key=lambda r: r["symbol"])
    return {
        "rows": rows,
        "position_count": len(rows),
        "observing_count": sum(1 for r in rows if r["is_observing"]),
        "cooldown_count": sum(1 for r in rows if r["is_in_cooldown"]),
    }


# ──────────────────────────────────────────────────────────────────────────────
# BFE-26 回撤油门刹车（风控实时扩展）
# ──────────────────────────────────────────────────────────────────────────────


def _throttle_gear(position_cap: float) -> str:
    if position_cap >= 0.999:
        return "full"
    if position_cap >= 0.5:
        return "half"
    if position_cap >= 0.001:
        return "brake"
    return "stop"


def query_drawdown_throttle(request: DrawdownThrottleRequest) -> dict[str, Any]:
    """回撤油门刹车查询——系统性风险 5 级 + 策略止损 + 黑天鹅合成仓位上限。

    Args:
        request: DrawdownThrottleRequest（回撤/VaR/CVaR/策略回撤/可选 breach 态）

    Returns:
        dict：risk_level/position_cap/reduce_ratio/throttle_gear/throttle_gear_zh/
        actions/strategy_stops/kill_switch_advised/recovery_factor
    """
    response = DrawdownController().evaluate(
        drawdown_info=DrawdownInfo(
            drawdown_pct=request.drawdown_pct,
            peak_nav=request.peak_nav,
            current_nav=request.current_nav,
            recovered_pct=request.recovered_pct,
        ),
        var_cvar=VarCvarMetrics(var_95=request.var_95, cvar_95=request.cvar_95),
        black_swan=BlackSwanSignal(),
        strategy_pnls=[
            StrategyPnl(strategy_id=sid, drawdown_pct=dd)
            for sid, dd in (request.strategy_drawdowns or {}).items()
        ]
        or None,
        var_breach_state=request.var_breach_state,
    )
    gear = _throttle_gear(response.position_cap)
    return {
        "risk_level": response.risk_level.value,
        "position_cap": response.position_cap,
        "reduce_ratio": response.reduce_ratio,
        "throttle_gear": gear,
        "throttle_gear_zh": _GEAR_ZH[gear],
        "actions": list(response.actions),
        "strategy_stops": [
            {
                "strategy_id": s.strategy_id,
                "stop_type": s.stop_type.value,
                "drawdown_pct": s.drawdown_pct,
            }
            for s in response.strategy_stops
        ],
        "kill_switch_advised": response.kill_switch_advised,
        "recovery_factor": response.recovery_factor,
    }


# ──────────────────────────────────────────────────────────────────────────────
# BFE-27 日历仓位约束（作战室 W5）
# ──────────────────────────────────────────────────────────────────────────────


def query_calendar_position_constraints(
    current_date: date,
    positions: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """日历仓位约束查询——7 类日历事件 → 临时仓位上限/禁新/强清。

    Args:
        current_date: 检查日期（自然日口径）
        positions: 持仓元数据列表，每项 {symbol, is_st?, market_cap_yi?,
            has_forecast?, earnings_release_date?}，可选

    Returns:
        dict：check_date/overall_cap_adjustment/block_new_positions/
        block_new_symbols/force_clear_symbols/constraints[{rule, event_type,
        action, cap_adjustment, description, affected_symbols}]/constraint_count
    """
    infos = [
        PositionInfo(
            symbol=p["symbol"],
            is_st=bool(p.get("is_st", False)),
            market_cap_yi=float(p.get("market_cap_yi", 0.0)),
            has_forecast=bool(p.get("has_forecast", True)),
            earnings_release_date=p.get("earnings_release_date"),
        )
        for p in (positions or [])
    ]
    alert = CalendarPositionConstraint().check(current_date, infos)
    return {
        "check_date": alert.check_date.isoformat(),
        "overall_cap_adjustment": alert.overall_cap_adjustment,
        "block_new_positions": alert.block_new_positions,
        "block_new_symbols": sorted(alert.block_new_symbols),
        "force_clear_symbols": sorted(alert.force_clear_symbols),
        "constraints": [
            {
                "rule": c.rule,
                "event_type": c.event_type.value,
                "action": c.action.value,
                "cap_adjustment": c.cap_adjustment,
                "description": c.description,
                "affected_symbols": (
                    "ALL" if c.affected_symbols is None else sorted(c.affected_symbols)
                ),
            }
            for c in alert.active_constraints
        ],
        "constraint_count": len(alert.active_constraints),
    }


# ──────────────────────────────────────────────────────────────────────────────
# BFE-30 流动性监控（风控实时一行）
# ──────────────────────────────────────────────────────────────────────────────


def query_liquidity_status(
    ohlcv_map: Mapping[str, pd.DataFrame],
    bid_ask_spreads: Mapping[str, float] | None = None,
) -> dict[str, Any]:
    """流动性监控查询——Amihud 非流动性 + 成交量萎缩，逐票判定。

    Args:
        ohlcv_map: {symbol: OHLCV DataFrame}（需 close + volume/amount 列，CTR-006）
        bid_ask_spreads: {symbol: 买卖价差}，可选

    Returns:
        dict：rows[{symbol, amihud_illiq, volume_shrinkage_ratio,
        bid_ask_spread, is_illiquid}]/illiquid_symbols/conclusion_zh
    """
    results = LiquidityMonitor().assess_batch(dict(ohlcv_map), dict(bid_ask_spreads or {}))
    rows = [
        {
            "symbol": m.symbol,
            "amihud_illiq": m.amihud_illiq,
            "volume_shrinkage_ratio": m.volume_shrinkage_ratio,
            "bid_ask_spread": m.bid_ask_spread,
            "is_illiquid": m.is_illiquid,
        }
        for m in results
    ]
    illiquid = sorted(r["symbol"] for r in rows if r["is_illiquid"])
    conclusion = (
        f"监控 {len(rows)} 票：{len(illiquid)} 票流动性恶化"
        + (f"（{'、'.join(illiquid)}）" if illiquid else "，全票正常")
    )
    return {
        "rows": rows,
        "illiquid_symbols": illiquid,
        "conclusion_zh": conclusion,
    }


# ──────────────────────────────────────────────────────────────────────────────
# BFE-31 尾部风险监控（风控实时一行）
# ──────────────────────────────────────────────────────────────────────────────


def query_tail_risk_status(
    returns: np.ndarray,
    portfolio_value: float = 1.0,
    now: datetime | None = None,
) -> dict[str, Any]:
    """尾部风险监控查询——VaR/ES/POT 厚尾/跳跃/FRTB 加价 + 告警级别。

    Args:
        returns: 组合收益率序列（负=亏损，≥30 样本）
        portfolio_value: 组合价值（默认 1.0=比率口径）
        now: 时间戳（可选，测试注入）

    Returns:
        dict：var/expected_shortfall/es_var_ratio/jump_count/alert_level/reason/
        frtb_addon/pot_shape/pot_tail_index/pot_fallback_historical
    """
    snapshot = TailRiskMonitor().assess(np.asarray(returns, dtype=float), portfolio_value, now)
    pot = snapshot.pot
    return {
        "var": snapshot.var,
        "expected_shortfall": snapshot.expected_shortfall,
        "es_var_ratio": snapshot.es_var_ratio,
        "jump_count": snapshot.jump_count,
        "alert_level": snapshot.alert_level.value,
        "reason": snapshot.reason,
        "frtb_addon": snapshot.frtb_addon,
        "pot_shape": pot.shape if pot is not None else None,
        "pot_tail_index": pot.tail_index if pot is not None else None,
        "pot_fallback_historical": snapshot.pot_fallback_historical,
    }
