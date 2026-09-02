# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md | §test
# [MODULE] tests.frontend.test_dashboard_feeds
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] zephyr.frontend.services.dashboard_feeds
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme;mock 数据源禁真连 DB
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_dashboard_feeds.py
# [A_test] module_id: MOD-L08-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""MOD-L08-001 单元测试: dashboard_feeds — 前端结论级查询接口层（C 类通道缺口施工）。

蓝图验收: 9 个查询函数全部返回 JSON 可序列化 dict，结构字段齐全，输入校验 fail-closed。
覆盖: GAP-F-04 相关性净额（聚合/无聚合/非法输入）、BFE-01 盘中买卖点（命中买点/
无信号/降级）、BFE-28 T+1 可卖（扣减/兜底 0/非法权重）、BFE-32 压力测试摘要
（三情景/最坏情景/结论）、BFE-25 持仓状态机快照（观察期/冷却期权限）、BFE-26 回撤
油门刹车（绿级全油门/红级刹车/黑级停机）、BFE-27 日历仓位约束（无约束/交割日窗口）、
BFE-30 流动性（正常/萎缩判定）、BFE-31 尾部风险（快照字段/厚尾告警）。
数据源全部为内存 mock（构造输入直接注入），不连接任何真实 DB/行情。
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

import numpy as np
import pandas as pd
import pytest

pytest.importorskip(
    "zephyr.frontend.services.dashboard_feeds",
    reason="dashboard_feeds not importable",
)

from zephyr.frontend.services.dashboard_feeds import (  # noqa: E402
    DashboardFeedInputError,
    DrawdownThrottleRequest,
    query_calendar_position_constraints,
    query_correlation_netting,
    query_drawdown_throttle,
    query_intraday_buy_sell_points,
    query_liquidity_status,
    query_position_state_snapshot,
    query_stress_test_summary,
    query_t1_sellable,
    query_tail_risk_status,
)
from zephyr.position.core.position_state_machine import (  # noqa: E402
    ObservingReason,
    PositionStateMachine,
)
from zephyr.signal_ashare.intraday_buy_sell_point_analyzer import (  # noqa: E402
    IntradayBuySellInput,
)

_NOW = datetime(2026, 8, 21, 15, 0, tzinfo=UTC)


# ──────────────────────────────────────────────────────────────────────────────
# GAP-F-04 相关性净额
# ──────────────────────────────────────────────────────────────────────────────


def test_correlation_netting_merges_high_corr_cluster() -> None:
    out = query_correlation_netting(
        positions={"600519.SH": 0.13, "300750.SZ": 0.06, "688981.SH": 0.07, "603986.SH": 0.05},
        correlation_pairs=[
            ("688981.SH", "603986.SH", 0.82),  # 半导体双票高相关
            ("600519.SH", "300750.SZ", 0.31),
        ],
        threshold=0.7,
        as_of="2026-08-21",
    )
    assert out["threshold"] == 0.7
    assert out["gross_position_count"] == 4
    assert out["net_risk_units"] == 3  # 4 票 → 3 笔净风险
    assert out["netting_reduction"] == 1
    assert len(out["clusters"]) == 1
    cluster = out["clusters"][0]
    assert set(cluster["members"]) == {"688981.SH", "603986.SH"}
    assert cluster["max_pair_rho"] == pytest.approx(0.82)
    assert cluster["combined_weight"] == pytest.approx(0.12)
    assert set(out["singletons"]) == {"600519.SH", "300750.SZ"}
    assert out["as_of"] == "2026-08-21"


def test_correlation_netting_no_cluster_when_below_threshold() -> None:
    out = query_correlation_netting(
        positions={"600519.SH": 0.13, "300750.SZ": 0.06},
        correlation_pairs=[("600519.SH", "300750.SZ", 0.55)],
        threshold=0.7,
    )
    assert out["clusters"] == []
    assert out["net_risk_units"] == 2
    assert out["netting_reduction"] == 0


def test_correlation_netting_transitive_cluster() -> None:
    out = query_correlation_netting(
        positions={"A": 0.1, "B": 0.1, "C": 0.1},
        correlation_pairs=[("A", "B", 0.9), ("B", "C", 0.85)],
        threshold=0.7,
    )
    assert len(out["clusters"]) == 1
    assert set(out["clusters"][0]["members"]) == {"A", "B", "C"}
    assert out["net_risk_units"] == 1


def test_correlation_netting_rejects_bad_input() -> None:
    with pytest.raises(DashboardFeedInputError):
        query_correlation_netting(
            positions={"A": 0.1},
            correlation_pairs=[("A", "B", 1.2)],  # rho 越界
        )
    with pytest.raises(DashboardFeedInputError):
        query_correlation_netting(positions={"A": -0.1}, correlation_pairs=[])


# ──────────────────────────────────────────────────────────────────────────────
# BFE-01 盘中买卖点（MOD-SIG-024）
# ──────────────────────────────────────────────────────────────────────────────


def _breakout_input() -> IntradayBuySellInput:
    return IntradayBuySellInput(
        symbol="600519.SH",
        current_price=1735.0,
        resistance_price=1700.0,  # 突破 +2.06% ≥ 2%
        volume_ratio=2.0,  # ≥ 1.5
        market_sentiment_score=60.0,  # ≥ 40
        sector_strength_score=70.0,  # ≥ 60
        capital_flow_inflow=500.0,  # 3 重确认：资金净流入 > 0
    )


def test_intraday_buy_sell_points_buy_breakout() -> None:
    out = query_intraday_buy_sell_points(_breakout_input())
    assert out["symbol"] == "600519.SH"
    assert out["is_degraded"] is False
    assert any(s["point_type"] == "突破买点" for s in out["buy_signals"])
    assert out["all_confirmations_passed"] is True
    assert out["recommendation"] in {"buy", "wait", "hold", "sell"}
    assert out["recommendation_zh"] in {"买入", "卖出", "持有", "等待"}
    assert 0.0 <= out["overall_confidence"] <= 100.0
    buy = next(s for s in out["buy_signals"] if s["point_type"] == "突破买点")
    assert 50.0 <= buy["confidence"] <= 100.0
    assert buy["reference_price"] > 0
    assert len(out["confirmations"]) == 3


def test_intraday_buy_sell_points_no_signal() -> None:
    out = query_intraday_buy_sell_points(IntradayBuySellInput(symbol="600519.SH", current_price=1700.0))
    assert out["buy_signals"] == []
    assert out["sell_signals"] == []
    assert out["recommendation"] in {"hold", "wait"}


def test_intraday_buy_sell_points_degraded_on_bad_input() -> None:
    out = query_intraday_buy_sell_points(IntradayBuySellInput(symbol="", current_price=-1.0))
    assert out["is_degraded"] is True
    assert out["recommendation"] == "wait"


# ──────────────────────────────────────────────────────────────────────────────
# BFE-28 T+1 可卖额度
# ──────────────────────────────────────────────────────────────────────────────


def test_t1_sellable_deducts_today_sold() -> None:
    out = query_t1_sellable(
        last_session_weights={"600519.SH": 0.13, "300750.SZ": 0.06},
        today_sold_weights={"600519.SH": 0.04},
    )
    rows = {r["symbol"]: r for r in out["rows"]}
    assert rows["600519.SH"]["sellable_weight"] == pytest.approx(0.09)
    assert rows["300750.SZ"]["sellable_weight"] == pytest.approx(0.06)
    assert rows["300750.SZ"]["sold_today_weight"] == 0.0
    assert out["position_count"] == 2
    assert out["total_sellable_weight"] == pytest.approx(0.15)


def test_t1_sellable_clamps_over_sold_to_zero() -> None:
    out = query_t1_sellable(
        last_session_weights={"600519.SH": 0.05},
        today_sold_weights={"600519.SH": 0.08},  # 数据异常：卖出>昨仓 → 兜底 0
    )
    assert out["rows"][0]["sellable_weight"] == 0.0


def test_t1_sellable_rejects_negative_weight() -> None:
    with pytest.raises(ValueError, match="昨仓权重非法"):
        query_t1_sellable(last_session_weights={"600519.SH": -0.01})


# ──────────────────────────────────────────────────────────────────────────────
# BFE-32 压力测试盘后风险验证（复盘页结论级）
# ──────────────────────────────────────────────────────────────────────────────


def test_stress_test_summary_three_scenarios() -> None:
    out = query_stress_test_summary(
        weights={"financial": 0.3, "tech": 0.4, "consumer": 0.3},
        portfolio_value=1_284_530.0,
        now=_NOW,
    )
    assert [s["scenario"] for s in out["scenarios"]] == [
        "2008_financial_crisis",
        "2015_china_stock_crash",
        "2020_covid_crash",
    ]
    for s in out["scenarios"]:
        assert s["portfolio_loss_pct"] < 0
        assert s["portfolio_loss_value"] < 0
        assert isinstance(s["is_severe"], bool)
        assert s["description"]
    # 2008: 0.3×-9.5% + 0.4×-7.2% + 0.3×-6.5% = -7.68%
    s2008 = out["scenarios"][0]
    assert s2008["portfolio_loss_pct"] == pytest.approx(-0.0768, abs=1e-6)
    assert s2008["is_severe"] is True
    assert out["worst_scenario"]["portfolio_loss_pct"] == min(s["portfolio_loss_pct"] for s in out["scenarios"])
    assert out["severe_count"] >= 1
    assert out["conclusion_zh"]


# ──────────────────────────────────────────────────────────────────────────────
# BFE-25 持仓状态机快照
# ──────────────────────────────────────────────────────────────────────────────


def test_position_state_snapshot_observing_blocks_buy() -> None:
    fsm = PositionStateMachine("300750.SZ", clock=lambda: _NOW)
    fsm.start_building(now=_NOW - timedelta(days=30))
    fsm.activate(now=_NOW - timedelta(days=9))
    fsm.enter_observing(ObservingReason.SOFT_STOP, now=_NOW - timedelta(minutes=5))
    out = query_position_state_snapshot([fsm])
    row = out["rows"][0]
    assert row["symbol"] == "300750.SZ"
    assert row["state"] == "OBSERVING"
    assert row["state_zh"] == "观察期"
    assert row["can_buy"] is False
    assert row["is_observing"] is True
    assert row["observing_reason"] == "SOFT_STOP"
    assert out["observing_count"] == 1


def test_position_state_snapshot_cooldown_blocks_rebuild() -> None:
    fsm = PositionStateMachine("600519.SH", clock=lambda: _NOW)
    fsm.start_building(now=_NOW - timedelta(days=40))
    fsm.activate(now=_NOW - timedelta(days=19))
    fsm.start_exiting(now=_NOW - timedelta(days=2))
    fsm.close(now=_NOW - timedelta(days=1))  # 默认冷却 5 个交易日
    out = query_position_state_snapshot([fsm])
    row = out["rows"][0]
    assert row["state"] == "CLOSED"
    assert row["state_zh"] == "已平仓"
    assert row["is_in_cooldown"] is True
    assert row["can_rebuild"] is False
    assert row["cooldown_until"] is not None
    assert out["cooldown_count"] == 1


def test_position_state_snapshot_active_normal() -> None:
    fsm = PositionStateMachine("688981.SH", clock=lambda: _NOW)
    fsm.start_building(now=_NOW - timedelta(days=30))
    fsm.activate(now=_NOW - timedelta(days=9))
    out = query_position_state_snapshot([fsm])
    row = out["rows"][0]
    assert row["state"] == "ACTIVE"
    assert row["can_buy"] is True
    assert row["can_rebuild"] is False  # 非 NONE/CLOSED 不可重建
    assert row["graduation_weight"] == pytest.approx(1.0)
    assert out["position_count"] == 1


# ──────────────────────────────────────────────────────────────────────────────
# BFE-26 回撤油门刹车
# ──────────────────────────────────────────────────────────────────────────────


def test_drawdown_throttle_green_full_throttle() -> None:
    out = query_drawdown_throttle(
        DrawdownThrottleRequest(
            drawdown_pct=-0.01,
            peak_nav=1.30,
            current_nav=1.287,
            var_95=0.018,  # < 2% → GREEN
            cvar_95=0.022,
        )
    )
    assert out["risk_level"] == "GREEN"
    assert out["position_cap"] == pytest.approx(1.0)
    assert out["throttle_gear"] == "full"
    assert out["throttle_gear_zh"] == "油门全开"
    assert out["kill_switch_advised"] is False


def test_drawdown_throttle_red_brake() -> None:
    out = query_drawdown_throttle(
        DrawdownThrottleRequest(
            drawdown_pct=-0.07,
            peak_nav=1.30,
            current_nav=1.209,
            var_95=0.065,  # > 6% → RED
            cvar_95=0.08,
        )
    )
    assert out["risk_level"] == "RED"
    assert out["position_cap"] <= 0.5
    assert out["reduce_ratio"] >= 0.5
    assert out["throttle_gear"] in {"half", "brake"}
    assert out["actions"]


def test_drawdown_throttle_black_stop() -> None:
    out = query_drawdown_throttle(
        DrawdownThrottleRequest(
            drawdown_pct=-0.12,
            peak_nav=1.30,
            current_nav=1.144,
            var_95=0.07,
            cvar_95=0.11,  # > 10% → BLACK
        )
    )
    assert out["risk_level"] == "BLACK"
    assert out["position_cap"] == pytest.approx(0.0)
    assert out["throttle_gear"] == "stop"
    assert out["throttle_gear_zh"] == "停机清仓"


def test_drawdown_throttle_strategy_stop_listed() -> None:
    out = query_drawdown_throttle(
        DrawdownThrottleRequest(
            drawdown_pct=-0.01,
            peak_nav=1.30,
            current_nav=1.287,
            var_95=0.018,
            cvar_95=0.022,
            strategy_drawdowns={"hot_money_v3": -0.06},  # 超 5% 软止损
        )
    )
    assert out["strategy_stops"]
    assert out["strategy_stops"][0]["strategy_id"] == "hot_money_v3"
    assert out["strategy_stops"][0]["stop_type"] in {"SOFT", "HARD"}


# ──────────────────────────────────────────────────────────────────────────────
# BFE-27 日历仓位约束
# ──────────────────────────────────────────────────────────────────────────────


def test_calendar_constraint_no_constraint_day() -> None:
    out = query_calendar_position_constraints(
        current_date=date(2026, 8, 12),
        positions=[{"symbol": "600519.SH", "market_cap_yi": 21000.0}],
    )
    assert out["check_date"] == "2026-08-12"
    assert out["overall_cap_adjustment"] == pytest.approx(1.0)
    assert out["block_new_positions"] is False
    assert out["constraints"] == []
    assert out["constraint_count"] == 0


def test_calendar_constraint_option_expiry_window() -> None:
    # 2026-08 第四个周三 = 2026-08-26；前后窗口 08-24~08-27 → cap 0.9
    out = query_calendar_position_constraints(current_date=date(2026, 8, 25))
    assert out["constraint_count"] >= 1
    assert out["overall_cap_adjustment"] == pytest.approx(0.9)
    rules = {c["rule"] for c in out["constraints"]}
    assert any("期权" in r or "OPTION" in r.upper() for r in rules)


def test_calendar_constraint_rejects_non_date() -> None:
    with pytest.raises(Exception, match="date"):
        query_calendar_position_constraints(current_date="2026-08-21")  # type: ignore[arg-type]


# ──────────────────────────────────────────────────────────────────────────────
# BFE-30 流动性监控
# ──────────────────────────────────────────────────────────────────────────────


def _ohlcv(closes: list[float], amounts: list[float]) -> pd.DataFrame:
    return pd.DataFrame({"close": closes, "amount": amounts})


def test_liquidity_status_normal_and_shrinkage() -> None:
    stable = _ohlcv(
        closes=[100.0 + 0.1 * i for i in range(25)],
        amounts=[1e8] * 24 + [1e8],
    )
    shrinking = _ohlcv(
        closes=[50.0 + 0.05 * i for i in range(25)],
        amounts=[1e8] * 24 + [1e7],  # 末日成交额萎缩到 1/10
    )
    out = query_liquidity_status({"600519.SH": stable, "603986.SH": shrinking})
    rows = {r["symbol"]: r for r in out["rows"]}
    assert rows["600519.SH"]["is_illiquid"] is False
    assert rows["603986.SH"]["is_illiquid"] is True
    assert rows["603986.SH"]["volume_shrinkage_ratio"] < 0.5
    assert "603986.SH" in out["illiquid_symbols"]
    assert out["conclusion_zh"]


# ──────────────────────────────────────────────────────────────────────────────
# BFE-31 尾部风险监控
# ──────────────────────────────────────────────────────────────────────────────


def test_tail_risk_status_snapshot_fields() -> None:
    rng = np.random.default_rng(42)
    returns = rng.normal(loc=0.0005, scale=0.015, size=120)
    out = query_tail_risk_status(returns, portfolio_value=1_284_530.0, now=_NOW)
    assert out["var"] >= 0
    assert out["expected_shortfall"] >= out["var"]
    assert out["es_var_ratio"] >= 1.0
    assert out["alert_level"] in {"none", "warning", "critical", "emergency"}
    assert out["jump_count"] >= 0
    assert out["frtb_addon"] >= 0
    assert "pot_fallback_historical" in out


def test_tail_risk_status_heavy_tail_alerts() -> None:
    rng = np.random.default_rng(7)
    base = rng.normal(loc=0.0, scale=0.01, size=110)
    crashes = np.array([-0.09, -0.11, -0.08, -0.10, -0.12, -0.07, -0.09, -0.10, -0.08, -0.09])
    returns = np.concatenate([base, crashes])
    out = query_tail_risk_status(returns, portfolio_value=1.0, now=_NOW)
    assert out["alert_level"] in {"warning", "critical", "emergency"}
    assert out["reason"]
