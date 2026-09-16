# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [TESTS] 回测金融正确性 P0 整改回归（2026-09-14 外部审查报告四项 P0 + 三项 P1）
# [SCOPE] P0-1 前视执行硬断言/次根成交 · P0-2 成交量上限+Almgren-Chriss 冲击 ·
#         P0-3 PIT 标的池过滤 · P0-4 合理性护栏+产物隔离 · P1-1 tick 判重接线 ·
#         P1-2 KillSwitch 职责澄清 · P1-3 win_rate 口径
# [TTL] permanent
"""Tests for P0 financial-correctness fixes (external review 2026-09-14).

覆盖四项 P0 缺陷的修复回归：
  P0-1  vectorized_engine 强制 signal(T) → fill(T+1)（open 优先/close 兜底），
        execution_lag_days<1 未显式放行即 LookaheadExecutionError；
  P0-2  matching_engine 成交量参与率上限 + 冲击成本（仅日线合成盘口路径）；
  P0-3  PitUniverseProvider（幸存者池+次新+ST，fail-open）接入引擎 universe；
  P0-4  engine_base.enforce_result_plausibility + result_repository 隔离落盘；
  P1-1  integrity_checker.run_tick_duplication_check 接线；
  P1-2  两套 KillSwitch 职责边界 docstring 锚；
  P1-3  win_rate 口径（日度正收益占比）显式化。
"""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from unittest.mock import patch

import pandas as pd
import pytest

from zephyr.backtest.core import cost_model_calibration as cal
from zephyr.backtest.core.engine_base import (
    ImplausibleBacktestError,
    LookaheadExecutionError,
    enforce_result_plausibility,
)
from zephyr.backtest.core.matching_engine import LiquidityGuardConfig
from zephyr.backtest.implementations.vectorized_engine import (
    BacktestConfig,
    DefaultBacktestEngine,
    PitUniverseProvider,
)
from zephyr.backtest.io.result_repository import (
    ArtifactQuarantinedError,
    BacktestRunArtifact,
    save_artifact,
)
from zephyr.execution_simulation.almgren_chriss_impact_model import AlmgrenChrissImpactModel


D = Decimal


def _make_data(closes, opens=None, volumes=None, symbol="600000"):
    """两列布局的单标的数据（date/symbol/close[+open+volume]）。"""
    dates = pd.bdate_range("2026-08-03", periods=len(closes))
    rows = []
    for i, d in enumerate(dates):
        row = {"symbol": symbol, "date": d, "close": closes[i]}
        if opens is not None:
            row["open"] = opens[i]
        if volumes is not None:
            row["volume"] = volumes[i]
        rows.append(row)
    return pd.DataFrame(rows)


def _signal_first_day(closes, weight=1.0):
    dates = pd.bdate_range("2026-08-03", periods=len(closes))
    vals = [weight] + [None] * (len(closes) - 1)
    return pd.DataFrame({"600000": vals}, index=dates)


# ============================================================================
# P0-1 前视执行防护
# ============================================================================


class TestP01LookaheadGuard:
    def test_same_bar_hard_assert(self):
        """execution_lag_days<1 未显式放行 → LookaheadExecutionError（硬断言）。"""
        engine = DefaultBacktestEngine(
            config=BacktestConfig(execution_lag_days=0, enable_pit_universe_filter=False), enable_stk_limit_provider=False
        )
        data = _make_data([10.0, 10.0])
        sig = _signal_first_day([10.0, 10.0])
        with pytest.raises(LookaheadExecutionError):
            engine.run(data=data, signals=sig)

    def test_same_bar_explicit_opt_out_allowed(self):
        """allow_same_bar_execution=True 显式放行（对照实验口），同日成交。"""
        engine = DefaultBacktestEngine(
            config=BacktestConfig(execution_lag_days=0, allow_same_bar_execution=True, enable_pit_universe_filter=False),
            enable_stk_limit_provider=False,
        )
        data = _make_data([10.0, 10.0])
        sig = _signal_first_day([10.0, 10.0])
        result = engine.run(data=data, signals=sig)
        assert result.trades_count == 1
        trade = engine.last_portfolio.trades_log[0]
        assert trade["date"].startswith("2026-08-03")  # 信号日当日成交（旧语义）

    def test_next_bar_default_fill_on_day2(self):
        """默认 lag=1：day1 信号在 day2 成交（day1 零成交）。"""
        engine = DefaultBacktestEngine(config=BacktestConfig(enable_pit_universe_filter=False), enable_stk_limit_provider=False)
        data = _make_data([10.0, 10.0, 10.0])
        sig = _signal_first_day([10.0, 10.0, 10.0])
        result = engine.run(data=data, signals=sig)
        assert result.trades_count == 1
        trade = engine.last_portfolio.trades_log[0]
        assert trade["date"].startswith("2026-08-04")  # 信号日次日成交

    def test_next_bar_executes_at_open_price(self):
        """有 open 列时按 T+1 开盘价成交（非收盘价）。"""
        engine = DefaultBacktestEngine(config=BacktestConfig(enable_pit_universe_filter=False), enable_stk_limit_provider=False)
        data = _make_data([10.0, 10.0], opens=[10.0, 10.6])
        sig = _signal_first_day([10.0, 10.0])
        engine.run(data=data, signals=sig)
        trade = engine.last_portfolio.trades_log[0]
        assert trade["date"].startswith("2026-08-04")
        # 成交价=day2 开盘 10.6（滑点 1bp 后 10.60106），绝非 day2 收盘 10.0
        assert trade["price"] > D("10.6")

    def test_last_day_signal_never_fills(self):
        """末日信号不成交（无次根可执行——前视消除的结构性保证）。"""
        dates = pd.bdate_range("2026-08-03", periods=2)
        data = _make_data([10.0, 10.0])
        sig = pd.DataFrame({"600000": [None, 1.0]}, index=dates)
        engine = DefaultBacktestEngine(
            config=BacktestConfig(allow_empty_trades=True, enable_pit_universe_filter=False), enable_stk_limit_provider=False
        )
        result = engine.run(data=data, signals=sig)
        assert result.trades_count == 0


# ============================================================================
# P0-2 流动性约束（成交量上限 + 冲击成本）
# ============================================================================


class TestP02LiquidityGuard:
    def _engine(self, **overrides):
        cfg_kwargs = dict(
            initial_capital=D("1000000"),
            sanity_guard=False,  # 本组只验证撮合，不验证护栏
            enable_pit_universe_filter=False,  # 合成数据不做真实股票池裁决
        )
        cfg_kwargs.update(overrides)
        return DefaultBacktestEngine(config=BacktestConfig(**cfg_kwargs), enable_stk_limit_provider=False)

    def test_volume_cap_limits_buy(self):
        """买单被当日量 10% 参与率上限收缩（整手）。"""
        engine = self._engine()
        data = _make_data([10.0, 10.0], volumes=[50000.0, 10000.0])
        sig = _signal_first_day([10.0, 10.0])
        engine.run(data=data, signals=sig)
        trade = engine.last_portfolio.trades_log[0]
        # day2 量 10000×10%=1000 股（整手），远小于 NAV 满仓目标
        assert trade["quantity"] == D("1000")

    def test_impact_cost_raises_buy_price(self):
        """冲击成本按参与率加入成交价（同侧 ask 先抬价，再叠滑点）——两腿均取标定档。

        口径（#23 H2-C 接线后）：冲击参数按该标的当日成交额（10000 股 ×10 元
        =¥100,000）落 ADV 五分位档，滑点腿同层取尺寸无关档；两条腿各计一次。
        """
        engine = self._engine()
        data = _make_data([10.0, 10.0], volumes=[50000.0, 10000.0])
        sig = _signal_first_day([10.0, 10.0])
        engine.run(data=data, signals=sig)
        trade = engine.last_portfolio.trades_log[0]

        daily_notional = 10000 * 10.0  # 当日成交额（元）= 冲击/滑点共同的分层输入
        participation = 1000.0 / 10000.0  # 订单股数 ÷ 当日成交股数（INV-UNIT-001）
        lvl = cal.impact_level_for_notional(daily_notional)
        slip_bps = cal.slippage_bps_for_notional(daily_notional)
        # 撮合顺序：盘口 ask1 先按冲击抬价，MatchingLogic 再叠滑点
        expected = (
            D("10")
            * (D("1") + D(str(lvl.cost_bps_at(participation))) / D("10000"))
            * (D("1") + slip_bps / D("10000"))
        )
        assert trade["price"] == pytest.approx(float(expected), rel=1e-9)
        # 冲击方向恒为不利（买贵）：高于纯滑点价
        assert trade["price"] > float(D("10") * (D("1") + slip_bps / D("10000")))
        # 标定档必须显著严于被弃用的 DEFAULT_PARAMS 档（否则 H2-C 的"旁路"没被治掉）
        legacy_default = AlmgrenChrissImpactModel().quote(1000.0, 10000.0)
        assert lvl.cost_bps_at(participation) > 10 * legacy_default.cost_bps

    def test_impact_disabled_price_matches_slip_only(self):
        """impact_cost_enabled=False 时成交价=纯滑点口径（冲击旁路，只剩标定滑点腿）。"""
        engine = self._engine(impact_cost_enabled=False)
        data = _make_data([10.0, 10.0], volumes=[50000.0, 10000.0])
        sig = _signal_first_day([10.0, 10.0])
        engine.run(data=data, signals=sig)
        trade = engine.last_portfolio.trades_log[0]
        slip_only = D("10") * (D("1") + cal.slippage_bps_for_notional(10000 * 10.0) / D("10000"))
        assert trade["price"] == pytest.approx(float(slip_only), rel=1e-12)

    def test_no_volume_column_legacy_behavior(self):
        """无 volume 列：约束旁路，行为与旧版一致（满仓单不被收缩）。"""
        engine = self._engine()
        data = _make_data([10.0, 10.0])
        sig = _signal_first_day([10.0, 10.0])
        result = engine.run(data=data, signals=sig)
        trade = engine.last_portfolio.trades_log[0]
        assert result.trades_count == 1
        assert trade["quantity"] > D("90000")  # 未受参与率上限收缩


# ============================================================================
# P0-3 PIT 标的池（幸存者/次新/ST）
# ============================================================================


class _FakeUniverseProvider:
    """注入用 fake：按预设返回 allowed 集合或 None（降级）。"""

    def __init__(self, allowed=None, degraded=False):
        self.allowed = allowed  # None=放行全部候选；set()=全剔；非空 set=白名单
        self.degraded = degraded
        self.calls = []

    def __call__(self, trade_date, symbols):
        self.calls.append((trade_date, list(symbols)))
        if self.degraded:
            return None
        basis = symbols if self.allowed is None else self.allowed
        return {s.split(".")[0].zfill(6) for s in basis}


class TestP03PitUniverse:
    def test_universe_filter_excludes_symbol(self):
        """provider 剔除标的 → 无成交（信号被过滤）。"""
        fake = _FakeUniverseProvider(allowed=set())
        engine = DefaultBacktestEngine(
            config=BacktestConfig(allow_empty_trades=True),
            enable_stk_limit_provider=False,
            universe_provider=fake,
        )
        data = _make_data([10.0, 10.0])
        sig = _signal_first_day([10.0, 10.0])
        result = engine.run(data=data, signals=sig)
        assert result.trades_count == 0
        assert fake.calls, "过滤提供器未被调用"

    def test_universe_filter_degraded_passes_through(self):
        """provider 降级（None）→ 不过滤，正常成交。"""
        fake = _FakeUniverseProvider(degraded=True)
        engine = DefaultBacktestEngine(
            config=BacktestConfig(enable_pit_universe_filter=False),
            enable_stk_limit_provider=False,
            universe_provider=fake,
        )
        data = _make_data([10.0, 10.0])
        sig = _signal_first_day([10.0, 10.0])
        result = engine.run(data=data, signals=sig)
        assert result.trades_count == 1

    def test_provider_disabled_by_config(self):
        """enable_pit_universe_filter=False → provider 不构建不调用。"""
        fake = _FakeUniverseProvider(allowed=set())
        engine = DefaultBacktestEngine(
            config=BacktestConfig(enable_pit_universe_filter=False),
            enable_stk_limit_provider=False,
            universe_provider=fake,
        )
        data = _make_data([10.0, 10.0])
        sig = _signal_first_day([10.0, 10.0])
        engine.run(data=data, signals=sig)
        assert fake.calls == []

    def test_provider_logic_delisted_new_st(self):
        """PitUniverseProvider 证据制判定：窗口不覆盖剔除、次新剔除、ST 剔除。"""
        from zephyr.backtest.core.matching_engine import LimitInfo

        provider = PitUniverseProvider(exclude_st=True, min_listing_age_days=120)

        registry = {
            "600000": [(date(1999, 11, 10), None)],  # 正常老股（在市）
            "000001": [(date(2026, 8, 1), None)],  # 次新（上市 <120 天）
            "300750": [(date(2020, 1, 1), None)],  # ST 候选（在市）
            "689009": [(date(2020, 1, 1), date(2024, 1, 1))],  # 已退市（窗口不覆盖当日）
        }
        provider._limit_provider = lambda d, syms: {
            "300750.SH": LimitInfo(st_flag=True),
        }
        with patch.object(provider, "_listing_registry", return_value=registry):
            allowed = provider(
                date(2026, 8, 10),
                ["600000.SH", "000001.SZ", "300750.SH", "689009.SH"],
            )
        assert allowed == {"600000"}

    def test_provider_no_evidence_keeps_symbol(self):
        """证据制：注册表无该码（部分覆盖）→ 不裁决保留，不误剔。"""
        provider = PitUniverseProvider(exclude_st=True, min_listing_age_days=120)
        registry = {"600000": [(date(1999, 1, 1), None)]}
        provider._limit_provider = None
        provider._exclude_st = False
        with patch.object(provider, "_listing_registry", return_value=registry):
            allowed = provider(date(2026, 8, 10), ["600000.SH", "123456.SH"])
        assert allowed == {"600000", "123456"}

    def test_provider_synthetic_code_bypasses_filter(self):
        """非 A 股代码形态（合成/占位代码）不进过滤作用域——注册表即便有退市证据也不误剔合成码。"""
        provider = PitUniverseProvider(exclude_st=False)
        registry = {"600000": [(date(2020, 1, 1), date(2024, 1, 1))]}  # 真实码已退市
        with patch.object(provider, "_listing_registry", return_value=registry):
            allowed = provider(date(2026, 8, 10), ["600000.SH", "default", "MOCK"])
        assert allowed == {"default", "00MOCK"}  # 合成码保留，退市真实码被剔

    def test_provider_degraded_on_empty_registry(self):
        """注册表为空（数据腿故障）→ 降级返回 None（不过滤）。"""
        provider = PitUniverseProvider()
        with patch.object(provider, "_listing_registry", return_value=None):
            assert provider(date(2026, 8, 10), ["600000.SH"]) is None


# ============================================================================
# P0-4 合理性护栏 + 产物隔离
# ============================================================================


class TestP04SanityGuard:
    def test_guard_extreme_return_blocked(self):
        """30x 类极端收益被拦截。"""
        with pytest.raises(ImplausibleBacktestError):
            enforce_result_plausibility(total_return=34.53, trades_count=5)

    def test_guard_empty_trades_blocked(self):
        """trades=0 空跑默认拦截，显式放行可过。"""
        with pytest.raises(ImplausibleBacktestError):
            enforce_result_plausibility(total_return=0.05, trades_count=0)
        assert (
            enforce_result_plausibility(total_return=0.05, trades_count=0, allow_empty_trades=True)
            == []
        )

    def test_guard_boundary_passes(self):
        """±合理带内正常通过（+1000% 边界、-95% 边界）。"""
        assert enforce_result_plausibility(total_return=10.0, trades_count=10) == []
        assert enforce_result_plausibility(total_return=-0.95, trades_count=10) == []

    def test_engine_extreme_return_blocked(self):
        """引擎级：价格路径 10→10→200 产生 ~19x 收益 → 护栏 raise，结果不产出。"""
        engine = DefaultBacktestEngine(config=BacktestConfig(enable_pit_universe_filter=False), enable_stk_limit_provider=False)
        data = _make_data([10.0, 10.0, 200.0])
        sig = _signal_first_day([10.0, 10.0, 200.0])
        with pytest.raises(ImplausibleBacktestError):
            engine.run(data=data, signals=sig)
        assert engine.results == []  # 失真结果不进 results

    def test_engine_sanity_guard_can_be_disabled(self):
        """sanity_guard=False 显式关闭（对照实验），同路径不拦。"""
        engine = DefaultBacktestEngine(
            config=BacktestConfig(sanity_guard=False, enable_pit_universe_filter=False), enable_stk_limit_provider=False
        )
        data = _make_data([10.0, 10.0, 200.0])
        sig = _signal_first_day([10.0, 10.0, 200.0])
        result = engine.run(data=data, signals=sig)
        assert result.total_return > 10.0

    def test_engine_empty_run_blocked_by_default(self):
        """无信号空跑（trades=0）默认拦截。"""
        engine = DefaultBacktestEngine(config=BacktestConfig(enable_pit_universe_filter=False), enable_stk_limit_provider=False)
        dates = pd.bdate_range("2026-08-03", periods=2)
        data = _make_data([10.0, 10.0])
        sig = pd.DataFrame({"600000": [None, None]}, index=dates)
        with pytest.raises(ImplausibleBacktestError):
            engine.run(data=data, signals=sig)


def _artifact(equity_first, equity_last, trades_count):
    return BacktestRunArtifact(
        run_id="bt-test-quarantine",
        strategy_id="s",
        equity_curve=[
            {"timestamp": "2026-08-03", "equity": equity_first},
            {"timestamp": "2026-08-04", "equity": equity_last},
        ],
        metrics={"trades_count": trades_count, "total_return": equity_last / equity_first - 1},
        trade_log=[{"side": "BUY"}] * trades_count,
    )


class TestP04ArtifactQuarantine:
    def test_extreme_artifact_quarantined(self, tmp_path):
        """34.5x 失真产物 → 隔离至 quarantine/，不进正库。"""
        artifact = _artifact(1_000_000.0, 35_534_490.17, 5)
        with pytest.raises(ArtifactQuarantinedError) as exc_info:
            save_artifact(artifact, storage_path=tmp_path)
        main_file = tmp_path / "bt-test-quarantine.json"
        q_file = tmp_path / "quarantine" / "bt-test-quarantine.json"
        assert not main_file.exists()
        assert q_file.exists()
        assert str(q_file) in str(exc_info.value.quarantine_path)
        reasons = json.loads(q_file.read_text(encoding="utf-8"))["quarantine_reasons"]
        assert any(">+1000%" in r for r in reasons)

    def test_zero_trade_artifact_quarantined(self, tmp_path):
        """trades=0 空跑产物 → 隔离。"""
        artifact = _artifact(1_000_000.0, 1_000_000.0, 0)
        with pytest.raises(ArtifactQuarantinedError):
            save_artifact(artifact, storage_path=tmp_path)
        assert (tmp_path / "quarantine" / "bt-test-quarantine.json").exists()

    def test_plausible_artifact_saved(self, tmp_path):
        """合理产物正常落正库。"""
        artifact = _artifact(1_000_000.0, 1_050_000.0, 3)
        run_id = save_artifact(artifact, storage_path=tmp_path)
        assert run_id == "bt-test-quarantine"
        assert (tmp_path / "bt-test-quarantine.json").exists()
        assert not (tmp_path / "quarantine").exists()

    def test_allow_implausible_bypass(self, tmp_path):
        """allow_implausible=True 显式放行落正库（复盘取证口）。"""
        artifact = _artifact(1_000_000.0, 35_534_490.17, 5)
        save_artifact(artifact, storage_path=tmp_path, allow_implausible=True)
        assert (tmp_path / "bt-test-quarantine.json").exists()


# ============================================================================
# P1-1 tick 判重接线 / P1-2 KillSwitch 澄清 / P1-3 win_rate 口径
# ============================================================================


class TestP11TickDuplicationWiring:
    def _patch_subprocess(self, rc, stdout="", stderr=""):
        import types

        fake = types.SimpleNamespace(returncode=rc, stdout=stdout, stderr=stderr)
        return patch(
            "zephyr.data.integrity_checker.subprocess.run", return_value=fake
        )

    def test_exit_0_healthy(self):
        from zephyr.data import integrity_checker as ic

        with self._patch_subprocess(0):
            out = ic.run_tick_duplication_check(month="202608")
        assert out["status"] == "healthy"
        assert out["month"] == "202608"

    def test_exit_1_duplicates(self):
        from zephyr.data import integrity_checker as ic

        with self._patch_subprocess(1, stdout="dup rows"):
            out = ic.run_tick_duplication_check(month="202608")
        assert out["status"] == "duplicates"

    def test_exit_2_degraded(self):
        from zephyr.data import integrity_checker as ic

        with self._patch_subprocess(2, stderr="ch down"):
            out = ic.run_tick_duplication_check()
        assert out["status"] == "degraded"

    def test_daily_check_summary_includes_tick_duplication(self):
        """run_daily_check 汇总带 tick_duplication 键（接线实证）。"""
        from zephyr.data import integrity_checker as ic

        with patch.object(ic, "discover_backfill_tables", return_value=[]), patch.object(
            ic, "run_tick_duplication_check", return_value={"status": "healthy", "month": "202609"}
        ) as fake_check, patch.object(ic, "_reconcile_task_runs", return_value={
            "should_run": 0,
            "succeeded": 0,
            "missing": [],
            "failed": [],
        }):
            summary = ic.run_daily_check(scheduler=None)
        assert summary["tick_duplication"]["status"] == "healthy"
        fake_check.assert_called_once()


class TestP12KillSwitchScope:
    def test_security_kill_switch_declares_scope(self):
        """security 侧 KillSwitch 明示 Agent 风控定位 + 交易真源指针 + 内存态警示。"""
        from zephyr.security.access_control import kill_switch as mod

        doc = mod.__doc__ or ""
        assert "AI Agent 行为风控" in doc
        assert "risk_layer_orchestrator" in doc
        assert "trading_kill_switch" in doc
        assert "内存态" in doc

    def test_trading_kill_switch_declares_scope(self):
        """trading 侧明确自身=交易熔断、与 Agent 风控不同。"""
        from zephyr.trading.trading_contracts.risk import trading_kill_switch as mod

        doc = mod.__doc__ or ""
        assert "security.access_control.kill_switch" in doc
        assert "交易" in doc


class TestP13WinRateCaliber:
    def test_metrics_docstring_declares_caliber(self):
        """metrics 产源显式声明 win_rate=日度正收益占比（非交易胜率）。"""
        from zephyr.backtest.core import metrics as metrics_mod

        doc = metrics_mod.calculate_metrics.__doc__ or ""
        assert "日度正收益占比" in doc
        assert "非交易胜率" in doc or "非逐笔" in doc

    def test_win_rate_semantics_unchanged(self):
        """口径行为不变：单调上涨净值 → win_rate=1.0（日度正收益占比）。"""
        from zephyr.backtest.core.metrics import calculate_metrics

        nav = pd.Series([100.0, 110.0, 121.0, 133.1])
        out = calculate_metrics(nav, trades_count=2)
        assert out["win_rate"] == 1.0
