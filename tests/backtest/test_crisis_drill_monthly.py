# [MODULE] tests.backtest.test_crisis_drill_monthly
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; scripts.backtest.crisis_drill_monthly
# [CONSUMERS] pytest（测试隔离：tmp_path fixture，禁写生产路径）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 测试输出一律 tmp_path（不触生产 data/、tmp/ 真实 marker）；
#   窗口计算用两日假行情断言 MaxDD 手算值；marker due 判定 fail-closed（缺失/损坏=due）；
#   空持仓降级链有标注（不硬造组合）
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] self
# [TTL] permanent
"""月度危机演练件测试（WO-2c）——窗口计算/marker due 判定/空持仓降级，tmp_path 隔离。"""

from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from backtest.crisis_drill_monthly import (  # noqa: E402
    DrillPortfolio,
    build_equal_weight_nav,
    compute_window_metrics,
    is_due,
    load_portfolio_from_rows,
    normalize_weights,
    render_markdown,
)


# ── 窗口计算正确性（两日假行情，MaxDD 手算断言） ──────────────────────────


class TestWindowComputation:
    """窗口净值构建与伤亡指标（构造两日/三日假行情断言）。"""

    def test_two_day_single_symbol_maxdd(self) -> None:
        """两日假行情：100→90，MaxDD=10%，不触 0.85 地板，未恢复。"""
        panel = {"600000": [("2020-02-03", 100.0), ("2020-02-04", 90.0)]}
        nav, included, excluded = build_equal_weight_nav(panel, {"600000": 1.0})
        assert included == ["600000"]
        assert excluded == []
        assert len(nav) == 2
        assert nav[0][1] == pytest.approx(1.0)
        assert nav[1][1] == pytest.approx(0.9)
        metrics = compute_window_metrics(nav)
        assert metrics["max_drawdown"] == pytest.approx(0.10)
        assert metrics["min_nav"] == pytest.approx(0.9)
        assert metrics["bankruptcy_floor_breach"] is False
        assert metrics["recovered"] is False  # 只有两日，无法恢复
        assert metrics["recovery_days"] is None

    def test_two_day_two_symbol_equal_weight(self) -> None:
        """两标的等权：甲 100→90（-10%）、乙 100→100（0%），组合 nav=0.95。"""
        panel = {
            "600000": [("2020-02-03", 100.0), ("2020-02-04", 90.0)],
            "000001": [("2020-02-03", 100.0), ("2020-02-04", 100.0)],
        }
        nav, included, excluded = build_equal_weight_nav(
            panel, {"600000": 1.0, "000001": 1.0}
        )
        assert sorted(included) == ["000001", "600000"]
        assert nav[-1][1] == pytest.approx(0.95)
        metrics = compute_window_metrics(nav)
        assert metrics["max_drawdown"] == pytest.approx(0.05)
        assert metrics["bankruptcy_floor_breach"] is False

    def test_breach_floor_and_recovery_days(self) -> None:
        """三日假行情：1.0→0.80（触地板 0.85，击穿深度 5.88%）→1.00（1 日恢复）。"""
        nav = [("d1", 1.0), ("d2", 0.80), ("d3", 1.00)]
        metrics = compute_window_metrics(nav)
        assert metrics["max_drawdown"] == pytest.approx(0.20)
        assert metrics["trough_date"] == "d2"
        assert metrics["bankruptcy_floor_breach"] is True
        assert metrics["breach_pct"] == pytest.approx((0.85 - 0.80) / 0.85, abs=1e-6)
        assert metrics["recovery_days"] == 1
        assert metrics["recovered"] is True

    def test_no_recovery_stays_below_peak(self) -> None:
        """回撤后未站回前高：恢复天数=None 且 recovered=False。"""
        nav = [("d1", 1.0), ("d2", 0.9), ("d3", 0.95)]
        metrics = compute_window_metrics(nav)
        assert metrics["max_drawdown"] == pytest.approx(0.10)
        assert metrics["recovery_days"] is None
        assert metrics["recovered"] is False

    def test_excluded_symbols_reported(self) -> None:
        """窗内无数据的标的进 excluded，不静默丢弃；权重按有数标的重归一。"""
        panel = {"600000": [("d1", 100.0), ("d2", 110.0)]}
        nav, included, excluded = build_equal_weight_nav(
            panel, {"600000": 1.0, "999999": 1.0}
        )
        assert included == ["600000"]
        assert excluded == ["999999"]
        assert nav[-1][1] == pytest.approx(1.10)

    def test_normalize_weights_rejects_all_nonpositive(self) -> None:
        """全非正权重抛 ValueError（fail-closed）。"""
        with pytest.raises(ValueError):
            normalize_weights({"600000": 0.0, "000001": -1.0})


# ── marker due 判定（tmp_path 隔离） ──────────────────────────


class TestIsDue:
    """月频门控判定：缺失/新鲜/超期/损坏四态。"""

    def test_missing_marker_is_due(self, tmp_path: Path) -> None:
        marker = tmp_path / "crisis_drill_last.json"
        result = is_due(marker, today=date(2026, 9, 18))
        assert result["due"] is True
        assert result["last_run"] is None

    def test_recent_marker_not_due(self, tmp_path: Path) -> None:
        marker = tmp_path / "crisis_drill_last.json"
        marker.write_text(
            json.dumps({"last_run": "2026-09-10T00:00:00+00:00", "run_id": "r1"}),
            encoding="utf-8",
        )
        result = is_due(marker, today=date(2026, 9, 18))
        assert result["due"] is False
        assert result["days_since"] == 8

    def test_older_than_30_days_is_due(self, tmp_path: Path) -> None:
        marker = tmp_path / "crisis_drill_last.json"
        old = (date(2026, 9, 18) - timedelta(days=31)).isoformat()
        marker.write_text(
            json.dumps({"last_run": f"{old}T00:00:00+00:00", "run_id": "r2"}),
            encoding="utf-8",
        )
        result = is_due(marker, today=date(2026, 9, 18))
        assert result["due"] is True
        assert result["days_since"] == 31

    def test_exactly_30_days_not_due(self, tmp_path: Path) -> None:
        """边界：整 30 天不算 due（严格大于）。"""
        marker = tmp_path / "crisis_drill_last.json"
        old = (date(2026, 9, 18) - timedelta(days=30)).isoformat()
        marker.write_text(
            json.dumps({"last_run": f"{old}T00:00:00+00:00", "run_id": "r3"}),
            encoding="utf-8",
        )
        result = is_due(marker, today=date(2026, 9, 18))
        assert result["due"] is False

    def test_corrupt_marker_fail_closed_due(self, tmp_path: Path) -> None:
        marker = tmp_path / "crisis_drill_last.json"
        marker.write_text("not-json{{{", encoding="utf-8")
        result = is_due(marker, today=date(2026, 9, 18))
        assert result["due"] is True


# ── 空持仓降级路径 ──────────────────────────


class TestPortfolioDegradation:
    """持仓加载降级链：最新非空直用/全现金降级/全空不硬造。"""

    def test_latest_positions_used_directly(self) -> None:
        latest = [
            {"trade_date": "2026-09-18", "strategy_id": "S1", "position_symbol": "600000", "position_value": 500000.0},
            {"trade_date": "2026-09-18", "strategy_id": "S2", "position_symbol": "000001", "position_value": 500000.0},
        ]
        portfolio = load_portfolio_from_rows(latest, None)
        assert portfolio is not None
        assert portfolio.source == "sim_pocket_daily_latest"
        assert portfolio.positions == {"600000": 500000.0, "000001": 500000.0}
        assert portfolio.notes == []

    def test_all_cash_degrades_to_last_nonempty_with_annotation(self) -> None:
        """最新快照全现金 → 降级取最近非空快照，且必须带如实标注。"""
        latest = [
            {"trade_date": "2026-09-18", "strategy_id": "S1", "position_symbol": "", "position_value": 0.0},
        ]
        nonempty = [
            {"trade_date": "2026-08-12", "strategy_id": "S1", "position_symbol": "000852", "position_value": 1000000.0},
        ]
        portfolio = load_portfolio_from_rows(latest, nonempty)
        assert portfolio is not None
        assert portfolio.source == "sim_pocket_daily_last_nonempty"
        assert portfolio.as_of == "2026-08-12"
        assert portfolio.positions == {"000852": 1000000.0}
        assert portfolio.notes, "降级必须留标注"

    def test_never_had_positions_returns_empty_not_fabricated(self) -> None:
        """从未有持仓 → 空组合（source=empty），绝不硬造默认组合。"""
        portfolio = load_portfolio_from_rows([], [])
        assert portfolio is not None
        assert portfolio.positions == {}
        assert portfolio.source == "sim_pocket_daily_empty"
        assert portfolio.notes

    def test_merges_same_symbol_across_wallets(self) -> None:
        """多钱包持同一标的：position_value 求和。"""
        latest = [
            {"trade_date": "2026-09-18", "strategy_id": "S1", "position_symbol": "600000", "position_value": 300000.0},
            {"trade_date": "2026-09-18", "strategy_id": "S2", "position_symbol": "600000", "position_value": 700000.0},
        ]
        portfolio = load_portfolio_from_rows(latest, None)
        assert portfolio is not None
        assert portfolio.positions == {"600000": 1000000.0}


# ── 报告渲染冒烟 ──────────────────────────


class TestReportRendering:
    """伤亡报告 md 渲染冒烟（不落生产路径）。"""

    def test_render_markdown_contains_casualty_table(self, tmp_path: Path) -> None:
        report = {
            "meta": {
                "run_id": "crisis_drill_test",
                "generated_at_utc": "2026-09-18T00:00:00+00:00",
                "portfolio": {
                    "source": "sim_pocket_daily_last_nonempty",
                    "as_of": "2026-08-12",
                    "positions": {"000852": 1.0},
                    "notes": ["降级标注"],
                },
            },
            "window_replays": [
                {
                    "window_id": "W2020",
                    "label": "2020 疫情",
                    "start": "2020-02-01",
                    "end": "2020-02-29",
                    "available": True,
                    "max_drawdown": 0.12,
                    "bankruptcy_floor_breach": False,
                    "breach_pct": None,
                    "recovery_days": 5,
                    "recovered": True,
                },
                {
                    "window_id": "W2015",
                    "label": "2015 千股跌停",
                    "start": "2015-06-01",
                    "end": "2015-09-30",
                    "available": False,
                },
            ],
            "stress_engine_crosscheck": [],
            "liquidity_crisis_check": {"available": False, "gap": "g"},
            "breaches": [],
            "gaps": ["g"],
        }
        md = render_markdown(report)
        assert "四预置历史窗伤亡表" in md
        assert "W2020" in md
        assert "否(窗内无持仓标的数据)" in md  # 不可算窗口如实标注
        assert "降级标注" in md
