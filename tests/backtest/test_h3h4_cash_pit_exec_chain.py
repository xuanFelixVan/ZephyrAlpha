# [A_test] module_id: MOD-GOV_h3h4_exec_chain | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md | §test
# [MODULE] tests.backtest.test_h3h4_cash_pit_exec_chain
# [DOMAIN] D_BACKTEST
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/backtest/test_h3h4_cash_pit_exec_chain.py
# [TTL] task_bound
"""车道 #24（H3/H4 执行链）治本回归锁——现金账本闭合 + PIT 标的池 + 静默点出声。

三侧同锁（缺一不可，否则修复可被静默回退）：
  1. **账本侧**（H4-A/H4-B）：`reconcile_cash_ledger` 用成交流水独立重算现金腿——
     正例（引擎真跑逐日残差 ≤ 容差）+ 反例（流水被动过手脚必须爆：双计手续费/漏记
     成交/脏行/无样本），反例是本文件的价值所在，只留正例等于把绊线当装饰。
  2. **引擎侧**（H3-C/H4-C/H4-D/H4-E）：`_normalize_day_signals` 的 Σ→1 满仓归一、
     全零行=不下单≠清仓、拒单计数、未建模清单——四颗静默点都必须有可核对的读数。
     注意：本组测试**钉住现状语义**（引擎吞掉现金意图是既有口径，裁定#270 §6④），
     断言的是"被吞的量必须被测出来"，不是"引擎应当持现金"。
  3. **组装/验收侧**（H3-A/H3-B/H3-D + 证据接线）：PIT 窗口成份查询谓词、幸存者
     偏差披露、产物 cash_curve 与执行链六键、验收闸 fail-closed。

零生产路径写入：产物落 tmp_path（宪法 §9.6）；CH 由假客户端替身承担（不触实连）。
"""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

from zephyr.backtest.core.portfolio import (
    CASH_LEDGER_TOLERANCE,
    Portfolio,
    _ledger_date_key,
    reconcile_cash_ledger,
)
from zephyr.backtest.implementations.vectorized_engine import (
    EXECUTION_MODEL_CAPABILITY,
    BacktestConfig,
    DefaultBacktestEngine,
    _classify_fill_reject,
    _normalize_day_signals,
)

D = Decimal
_SYMBOLS = ["600519", "000858", "600036"]  # 在市真实 6 位码（同域先例，见 test_lane_k）


# ── 合成行情/信号（进程内，零 CH）──────────────────────────────────────


def _market_data(n_days: int = 12, symbols: list[str] | None = None) -> pd.DataFrame:
    syms = symbols or _SYMBOLS
    dates = pd.date_range("2026-01-05", periods=n_days, freq="B")
    frames = []
    for k, sym in enumerate(syms):
        close = 100.0 + 10 * k
        rows = []
        for t in range(n_days):
            px = close * (1 + 0.002 * t)
            rows.append(
                {
                    "symbol": sym,
                    "date": dates[t],
                    "open": px,
                    "high": px * 1.01,
                    "low": px * 0.99,
                    "close": px,
                    "volume": 2_000_000,
                }
            )
        frames.append(pd.DataFrame(rows))
    return pd.concat(frames, ignore_index=True).set_index(["symbol", "date"]).sort_index()


def _signal_panel(dates: pd.Index, symbols: list[str], row_value: float = 1.0) -> pd.DataFrame:
    idx = pd.DatetimeIndex(dates, name="date")
    return pd.DataFrame({s: row_value for s in symbols}, index=idx)


def _offline_engine(capital: D | None = None, *, allow_empty: bool = False) -> DefaultBacktestEngine:
    """离线确定性引擎：涨跌停 provider 关 + PIT 过滤关（不触 CH，逐笔可复算）。

    allow_empty=True 仅用于"整批成交被注入成必拒"的对照实验——合理性护栏按既有语义
    会拦停 trades=0 空跑，那是护栏在做事，不是被测件坏。
    """
    cfg = BacktestConfig(
        initial_capital=capital if capital is not None else D("1000000"),
        enable_pit_universe_filter=False,
        allow_empty_trades=allow_empty,
    )
    return DefaultBacktestEngine(config=cfg, enable_stk_limit_provider=False)


# ── H4-A/H4-B 现金账本闭合（正例 + 反证）────────────────────────────


class TestCashLedgerClosure:
    def test_engine_run_cash_history_dates_are_nav_subset(self) -> None:
        """现金快照日必须是净值日的子集且严格递增（键错位=对账假阴/假阳）。

        口径钉清楚两件事：①现金快照只在**有成交的交易日**追加（apply_fill 落点），
        净值则逐日都有——两者索引不等长是设计，不是缺陷；②净值首行是初始化快照
        （日期 None → NaT），与 cash_history[0] 的 (None, initial) 同构。
        逐日闭合按"相邻快照窗口内的成交"相减，故只需日期可对齐、无需逐日等长。
        """
        data = _market_data()
        dates = data.index.get_level_values("date").unique().sort_values()
        eng = _offline_engine()
        eng.run(data=data, signals=_signal_panel(dates, _SYMBOLS), strategy_name="align")
        p = eng.last_portfolio
        assert p is not None
        assert p.cash_history[0][0] is None  # 初始化点（与 _nav_history 首行同构）
        assert p.cash_history[0][1] == D("1000000")
        assert pd.isna(p.nav_series.index[0])  # 净值首行=初始化 NaT（既有引擎语义）
        recorded = [d for d, _ in p.cash_history[1:]]
        assert recorded, "回测有成交，必须留下现金快照"
        nav_keys = {_ledger_date_key(d) for d in p.nav_series.index}
        assert all(_ledger_date_key(d) in nav_keys for d in recorded), recorded
        assert recorded == sorted(recorded) and len(set(map(_ledger_date_key, recorded))) == len(recorded)
        # 快照额与初始额同量纲可比（Decimal，禁 float 化致对账残差被噪声淹没）
        assert all(isinstance(cash, D) for _, cash in p.cash_history)

    def test_engine_run_cash_leg_closes(self) -> None:
        """正例：引擎真跑后现金腿由流水独立重算，逐日残差远小于容差（账本闭合）。"""
        data = _market_data()
        dates = data.index.get_level_values("date").unique().sort_values()
        eng = _offline_engine()
        eng.run(data=data, signals=_signal_panel(dates, _SYMBOLS), strategy_name="closure")
        p = eng.last_portfolio
        rec = reconcile_cash_ledger(p.cash_history, p.trades_log, p.initial_capital)
        assert rec["samples"] > 0 and rec["trade_rows"] > 0
        assert rec["within_tolerance"] is True, rec
        assert D(rec["max_abs_residual"]) < D("0.000001")  # 实测 ~1e-11 量级（float 往返噪声）
        assert rec["over_tolerance"] == 0 and rec["bad_trade_rows"] == 0
        # 手续费/过户费真的动了现金：末现金 != 初始（成交额+费 已从现金腿出去）
        assert rec["cash_last"] != float(p.initial_capital)

    def test_double_counted_commission_breaks_closure(self) -> None:
        """反证①：流水里某笔佣金被双计 → 残差张开并被否决（本绊线的立论用例）。

        口径：残差判据必须在**分钟级成本双计**这种真实错法下爆掉，而不是只在
        人为 1e6 的错值下爆掉——所以这里只把一笔的真实佣金再加一次。
        """
        data = _market_data()
        dates = data.index.get_level_values("date").unique().sort_values()
        eng = _offline_engine()
        eng.run(data=data, signals=_signal_panel(dates, _SYMBOLS), strategy_name="doctored")
        p = eng.last_portfolio
        rows = list(p.trades_log)
        victim = next(r for r in rows if r["side"] == "BUY")
        tampered = dict(victim)
        tampered["total_cost"] = victim["total_cost"] + victim["commission"]  # 手续费再扣一次
        doctored = [tampered if r is victim else r for r in rows]
        rec = reconcile_cash_ledger(p.cash_history, doctored, p.initial_capital)
        assert rec["within_tolerance"] is False
        assert rec["over_tolerance"] >= 1
        assert D(rec["max_abs_residual"]) >= D(victim["commission"]) * D("0.5")

    def test_dropped_fill_breaks_closure(self) -> None:
        """反证②：漏记一笔成交（成交没进现金腿）→ 残差张开。"""
        data = _market_data()
        dates = data.index.get_level_values("date").unique().sort_values()
        eng = _offline_engine()
        eng.run(data=data, signals=_signal_panel(dates, _SYMBOLS), strategy_name="dropped")
        p = eng.last_portfolio
        rows = list(p.trades_log)
        assert len(rows) >= 2
        dropped = rows[0]
        rec = reconcile_cash_ledger(
            p.cash_history, rows[1:], p.initial_capital
        )
        assert rec["within_tolerance"] is False
        assert D(rec["max_abs_residual"]) >= D(str(dropped["total_cost"])) * D("0.5")

    def test_unparseable_flow_row_is_not_silently_reconciled(self) -> None:
        """反证③：金额不可解析的流水行=未核对，必须出声（禁"跳过的行"当成通过）。"""
        rows = [
            {"date": "2026-01-05", "side": "BUY", "total_cost": 1000.0},
            {"date": "2026-01-05", "side": "BUY", "total_cost": "not-a-number"},
        ]
        points = [(date(2026, 1, 5), D("999000"))]
        rec = reconcile_cash_ledger(points, rows, D("1000000"))
        assert rec["bad_trade_rows"] == 1
        assert rec["within_tolerance"] is False
        assert "未核对" in rec["note"]

    def test_no_samples_fails_closed(self) -> None:
        """反证④：没有逐日样本＝没核对，判不过（不是判通过）。"""
        rec = reconcile_cash_ledger([], [], D("1000000"))
        assert rec["samples"] == 0
        assert rec["within_tolerance"] is False

    def test_tolerance_single_source_and_cash_nonneg_invariant(self) -> None:
        """容差是单一真源（消费方禁复写口径），且 Portfolio 自身拒绝现金透支。"""
        assert D("0.01") == CASH_LEDGER_TOLERANCE
        p = Portfolio(initial_capital=D("1000"))
        assert p.cash == D("1000")
        with pytest.raises(Exception, match="现金不足"):
            from zephyr.backtest.core.portfolio import BacktestFill

            p.apply_fill(
                BacktestFill(date=date(2026, 1, 5), symbol="600519", side="BUY",
                             quantity=D("1000"), price=D("10"))
            )

    def test_date_key_normalization_mixes_timestamp_and_plain_date(self) -> None:
        """账本键日频归一：Timestamp 成交与 date 快照必须落同一键（错位=假阴/假阳）。"""
        ts = pd.Timestamp("2026-01-05 00:00:00")
        rows = [{"date": str(ts), "side": "BUY", "total_cost": 500.0}]
        rec = reconcile_cash_ledger([(date(2026, 1, 5), D("999500"))], rows, D("1000000"))
        assert rec["within_tolerance"] is True, rec


# ── H3-C/H4-C/H4-D/H4-E 引擎静默点出声 ────────────────────────────


class TestEngineSilentPointTripwires:
    def test_normalize_day_signals_reports_pre_normalization_sum(self) -> None:
        """纯函数口径：返回归一**前**行 Σ，同时把权重仍放大到 Σ=1（行为零变更）。"""
        weights: dict[str, float] = {}
        row = pd.Series({"600519": 0.3, "000858": 0.5})  # Σ=0.8 = 策略想留 20% 现金
        total = _normalize_day_signals(row, weights)
        assert total == pytest.approx(0.8)
        assert sum(weights.values()) == pytest.approx(1.0)  # 满仓口径（现金意图被吞）
        assert _normalize_day_signals(pd.Series(dtype="float64"), {}) is None
        assert _normalize_day_signals(pd.Series({"600519": 0.0}), {}) == 0.0

    def test_partial_exposure_signal_is_measured_not_silent(self) -> None:
        """Σ<1 面板：引擎照旧满仓，但吞掉的现金质量必须被量化（H3-C）。"""
        data = _market_data(n_days=10)
        dates = data.index.get_level_values("date").unique().sort_values()
        panel = _signal_panel(dates, _SYMBOLS, row_value=1.0)
        panel = panel * 0.4  # 每行 Σ=1.2 → 意图含 20% 现金缓冲（Σ<1 的另一种写法见下）
        eng = _offline_engine()
        eng.run(data=data, signals=panel, strategy_name="over")
        stats = eng.last_signal_row_stats
        assert stats["rows_with_signal"] > 0
        assert stats["swallowed_cash_mass"] == 0.0  # Σ>1 的行不产生"被吞现金"
        assert stats["rows_renormalized"] == stats["rows_with_signal"]

        # Σ<1：真的把"留现金"的意图吞掉（3×0.16=0.48，另 52% 是想留的现金）
        panel2 = _signal_panel(dates, _SYMBOLS, row_value=0.16)
        eng2 = _offline_engine()
        eng2.run(data=data, signals=panel2, strategy_name="under")
        s2 = eng2.last_signal_row_stats
        assert s2["target_sum_max"] == pytest.approx(0.48)
        assert s2["rows_below_unit"] == s2["rows_with_signal"]
        assert s2["swallowed_cash_mass"] > 0.0
        assert s2["swallowed_cash_fraction_mean"] == pytest.approx(1 - 0.48)
        # 满仓后果：现金腿被压到零头（意图留 52% 现金却没有留下）
        p = eng2.last_portfolio
        nav = float(p.nav_series.iloc[-1])
        assert float(p.cash) / nav < 0.05

    def test_all_zero_row_means_hold_not_liquidate(self) -> None:
        """全零行=当日不下单（H4-C 现状语义，必须显式钉住+计数，禁被误读成清仓）。"""
        data = _market_data(n_days=10)
        dates = data.index.get_level_values("date").unique().sort_values()
        panel = _signal_panel(dates, _SYMBOLS)
        panel.iloc[6] = 0.0  # 第 7 个信号日"空仓意图"
        eng = _offline_engine()
        eng.run(data=data, signals=panel, strategy_name="zero_row")
        stats = eng.last_signal_row_stats
        assert stats["rows_all_zero"] == 1
        p = eng.last_portfolio
        assert sum(pos.quantity for pos in p.positions.values()) > 0  # 没有清仓
        nav = float(p.nav_series.iloc[-1])
        assert float(p.cash) / nav < 0.05  # "空仓"日实际仍满仓

    def test_skipped_fills_are_counted_and_classified(self, monkeypatch) -> None:
        """拒单必须计数+分类进产物（H4-D）：只写日志的证据不存在。"""
        assert _classify_fill_reject("现金不足: 需要100, 可用10") == "cash_insufficient"
        assert _classify_fill_reject("T+1锁定: 600519 当天买入不能卖出") == "t_plus_1_locked"
        assert _classify_fill_reject("持仓不足: 需要1000, 可用10") == "position_insufficient"
        assert _classify_fill_reject("无持仓可卖: symbol=600519") == "no_position"
        assert _classify_fill_reject("莫名其妙") == "other"

        data = _market_data(n_days=8)
        dates = data.index.get_level_values("date").unique().sort_values()
        eng = _offline_engine(allow_empty=True)  # 全 BUY 被打成必拒=空跑对照，护栏须显式放行
        real = Portfolio.apply_fill
        calls = {"n": 0}

        def flaky(self, fill, allow_t_plus_1: bool = False) -> None:  # noqa: ANN001
            calls["n"] += 1
            if fill.side == "BUY":
                raise RuntimeError("现金不足: 模拟拒单")
            real(self, fill, allow_t_plus_1)

        monkeypatch.setattr(Portfolio, "apply_fill", flaky)
        eng.run(data=data, signals=_signal_panel(dates, _SYMBOLS), strategy_name="rejects")
        monkeypatch.undo()
        skipped = eng.last_skipped_fills
        assert skipped["count"] > 0
        assert skipped["by_reason"]["cash_insufficient"] == skipped["count"]

    def test_execution_model_capability_registers_unmodeled_legs(self) -> None:
        """H4-E：席位/信用账户/做空/利息——无生产者无消费口时登记出声，禁造假功能。"""
        assert EXECUTION_MODEL_CAPABILITY["schema"] == "execution_model_capability/v1"
        for key in ("broker_seat", "margin_financing", "short_selling", "cash_yield"):
            statement = EXECUTION_MODEL_CAPABILITY[key]
            # 每条都必须正面声明"这条没建模"（措辞可为未建模/不支持/不计），不按键豁免
            assert any(m in statement for m in ("未建模", "不支持", "不计")), (key, statement)
        # 佣金口径引用真源字面量（禁在披露里改口径）
        assert "0.0000854" not in json.dumps(EXECUTION_MODEL_CAPABILITY, ensure_ascii=False)
        assert "万0.854" in EXECUTION_MODEL_CAPABILITY["broker_seat"]


# ── H3-B/H4-A 整装回测产物接线（tmp_path，零生产写入）───────────────


class TestFrameworkArtifactChainEvidence:
    @pytest.fixture()
    def fw_env(self, tmp_path, monkeypatch):
        from zephyr.pf_core.strategy_engine import framework_composer as fc

        data = _market_data(n_days=20)
        dates = data.index.get_level_values("date").unique().sort_values()
        signals = _signal_panel(dates, _SYMBOLS)
        plans_path = tmp_path / "fw_plans_h3h4.yaml"
        plans_path.write_text(
            "plans:\n"
            "  - plan_id: fw-h3h4-test\n"
            "    name_zh: 执行链测试方案\n"
            "    risk_profile: balanced\n"
            "    description: lane #24 单测\n"
            "    weights:\n"
            "      - strategy_id: member-a\n"
            "        weight: 1.0\n"
            "        role: test\n",
            encoding="utf-8",
        )
        config = fc.FrameworkBacktestConfig(
            plans_path=str(plans_path),
            storage_path=str(tmp_path / "artifacts"),
            enable_stk_limit_provider=False,
            factor_ids=(),
        )
        monkeypatch.setattr(
            fc, "_build_member_panels", lambda *a, **kw: (data, {"member-a": signals}, [])
        )
        monkeypatch.setattr(
            fc, "_member_signal_contracts", lambda *a, **kw: {"member-a": {"route": "flat"}}
        )
        monkeypatch.setattr(
            fc, "_select_vectorizable_members", lambda plan: ([plan.weights[0]], [])
        )
        return {"fc": fc, "config": config, "tmp_path": tmp_path}

    def test_artifact_metrics_carry_chain_evidence(self, fw_env) -> None:
        fc = fw_env["fc"]
        result, ts = fc._run_framework_backtest_core(
            "fw-h3h4-test", _SYMBOLS, "2026-01-01", "2026-12-31", fw_env["config"]
        )
        assert result["ok"] is True, result
        m = result["metrics"]
        # 六键齐备（缺任一键=验收侧 fail-closed，见 fw_backtest 闸测试）
        for key in (
            "cash_ledger_reconciliation",
            "target_weight_renormalization",
            "skipped_fills",
            "execution_model_disclosure",
            "signal_age_disclosed",
        ):
            assert key in m, f"产物缺执行链键 {key}"
        assert m["cash_ledger_reconciliation"]["within_tolerance"] is True
        assert m["cash_ledger_reconciliation"]["samples"] > 0
        assert m["execution_model_disclosure"]["schema"] == "execution_model_capability/v1"
        assert m["signal_age_disclosed"]["available"] is True
        # 混频实证：恒等目标面板 → 一次调仓后每日按同目标再平衡（龄=面板天数-1）
        assert m["signal_age_disclosed"]["rebalance_days"] == 1
        assert m["signal_age_disclosed"]["signal_age_days_max"] == m["signal_age_disclosed"]["days"] - 1

        # 现金腿时序落产物（同 ts 通道）
        assert ts["cash_curve"], "cash_curve 缺失——现金腿不可外部复核"
        assert len(ts["cash_curve"]) == len(ts["equity_curve"])
        assert {"timestamp", "cash"} <= set(ts["cash_curve"][0])

        saved = fw_env["tmp_path"] / "artifacts" / f"{result['run_id']}.json"
        assert saved.exists()
        disk = json.loads(saved.read_text(encoding="utf-8"))
        assert disk["metrics"]["cash_ledger_reconciliation"]["within_tolerance"] is True
        assert "execution_model_disclosure" in disk["metrics"]
        # H4-B 硬验收：现金腿必须**落盘**（只在内存 ts 构造、被 sink 丢掉=不可事后复核）
        disk_cash = disk["metrics"]["cash_curve"]
        assert disk_cash == ts["cash_curve"], "落盘现金腿与内存不一致（序列化被改写/截断）"
        assert len(disk_cash) == len(disk["equity_curve"]), "现金腿与净值腿不等长→逐日轧差不可核"
        assert {"timestamp", "cash"} <= set(disk_cash[0])

    def test_warn_visible_when_cash_ledger_open(self, fw_env) -> None:
        """账本破口必须进 warn（done 响应可见），不能只躺在 metrics 里。"""
        fc = fw_env["fc"]
        report = fc.compose_weight_panels.__wrapped__ if False else None  # noqa: F841 占位
        from zephyr.pf_core.strategy_engine.framework_composer import (
            ComposeReport,
            _assemble_run_warn,
        )

        plan = fc.get_framework_plan("fw-h3h4-test", fw_env["config"].plans_path)
        panel = pd.DataFrame({s: [1.0, 0.0] for s in _SYMBOLS}, index=pd.Index([0, 1]))
        report = ComposeReport(
            panel=panel,
            participants=["member-a"],
            skipped=[],
            rescale_factor=1.0,
            notes=[],
            dead_weight_disclosed={},
        )
        ts_ok = {"equity_curve": [{"timestamp": "2026-01-05", "equity": 1.0}]}
        warn = _assemble_run_warn(
            ts_ok,
            report,
            None,
            chain={"cash_ledger_reconciliation": {
                "within_tolerance": False, "max_abs_residual": "12.5",
                "tolerance_abs": "0.01", "worst_date": "2026-01-06"}},
        )
        assert warn and "cash ledger OPEN" in warn
        # 缺键同样出声（engine 没接线也是破口）
        warn2 = _assemble_run_warn(ts_ok, report, None, chain={})
        assert warn2 and "MISSING" in warn2
        # 不传 chain 的老调用契约零漂移
        assert _assemble_run_warn(ts_ok, report, None) is None
        assert plan.plan_id == "fw-h3h4-test"


# ── H3-D PIT 标的池 + 幸存者偏差披露 ─────────────────────────────


class _FakeCH:
    def __init__(self, rows):
        self.rows = rows
        self.sql = ""

    def execute(self, sql):
        self.sql = sql
        return self.rows


class TestPitUniverse:
    def test_query_is_window_not_snapshot_and_discloses_gap(self, monkeypatch) -> None:
        from zephyr.data import ch_writer
        from zephyr.strategy_pipeline.fw_backtest import _hs300_symbols

        fake = _FakeCH(
            [
                ("600519.SH", None),                       # 未失效
                ("600036.SH", date(1900, 1, 1)),           # 未失效哨兵
                ("600000.SH", date(2026, 6, 30)),          # 窗口内被调出 → 期末非成份
                ("000001.SZ", date(2026, 12, 31)),         # 期末已失效（=end 不算在池）
            ]
        )
        monkeypatch.setattr(ch_writer, "get_client_strict", lambda: fake)
        syms, disc = _hs300_symbols("2026-01-01", "2026-12-31")
        sql = fake.sql
        assert "valid_from <= toDate('2026-12-31')" in sql
        assert "valid_to > toDate('2026-01-01')" in sql
        assert "1900-01-01" in sql
        # 旧口径病灶不得复现：仅凭 valid_to IS NULL 取期末快照
        assert "AND valid_to IS NULL" not in sql
        assert syms == ["000001", "600000", "600036", "600519"]
        assert disc["mode"] == "pit_index_window"
        assert disc["universe_n"] == 4
        assert disc["snapshot_n"] == 2  # 旧口径只给 2 只
        assert disc["since_exit_n"] == 2
        assert disc["since_exit_share"] == pytest.approx(0.5)
        assert "幸存者偏差" not in disc["note"] or disc["since_exit_n"] > 0

    def test_empty_result_hard_fails(self, monkeypatch) -> None:
        from zephyr.data import ch_writer
        from zephyr.strategy_pipeline.fw_backtest import _hs300_symbols

        monkeypatch.setattr(ch_writer, "get_client_strict", lambda: _FakeCH([]))
        with pytest.raises(RuntimeError, match="成份缺失"):
            _hs300_symbols("2026-01-01", "2026-12-31")

    def test_malformed_date_rejected_before_sql(self, monkeypatch) -> None:
        """payload 可控参数进 SQL 前硬校验（禁拼接面扩大）。"""
        from zephyr.strategy_pipeline.fw_backtest import _hs300_symbols

        with pytest.raises(RuntimeError, match="YYYY-MM-DD"):
            _hs300_symbols("2026-01-01'; DROP TABLE x --", "2026-12-31")

    def test_resolve_symbols_carries_universe_disclosure(self, monkeypatch) -> None:
        from zephyr.pf_core.strategy_engine import framework_composer as fc
        from zephyr.pf_core.strategy_engine import translated_strategy_adapter as tsa
        from zephyr.strategy_pipeline.fw_backtest import resolve_symbols

        class _W:
            strategy_id = "member-a"

        class _P:
            weights = [_W()]

        monkeypatch.setattr(fc, "get_framework_plan", lambda *a, **kw: _P())
        monkeypatch.setattr(tsa, "is_translated_member", lambda sid: False)
        monkeypatch.setattr(tsa, "prefetch_translated_panels", lambda *a, **kw: {})

        syms, info = resolve_symbols("2026-01-01", "2026-12-31", ["600519"])
        assert info["universe_disclosure"]["mode"] == "payload_override"
        assert syms == ["600519"]

        monkeypatch.setattr(
            "zephyr.strategy_pipeline.fw_backtest._hs300_symbols",
            lambda s, e: (["000001"], {"mode": "pit_index_window", "universe_n": 1}),
        )
        syms2, info2 = resolve_symbols("2026-01-01", "2026-12-31", None)
        assert info2["universe_disclosure"]["mode"] == "pit_index_window"
        assert syms2 == ["000001"]


# ── 验收闸（H4-B fail-closed / H3-A 换手实测上提）──────────────────


class TestAcceptanceGateWiring:
    def test_cash_gate_accepts_closed_ledger(self) -> None:
        from zephyr.strategy_pipeline.fw_backtest import _evaluate_cash_closure

        result = {"metrics": {"cash_ledger_reconciliation": {
            "samples": 20, "within_tolerance": True, "max_abs_residual": "1e-11",
            "tolerance_abs": "0.01", "over_tolerance": 0, "bad_trade_rows": 0,
            "worst_date": "2026-01-06", "cash_last": 100.0, "reconstructed_cash_last": 100.0}}}
        gate = _evaluate_cash_closure(result)
        assert gate["accepted"] is True and gate["reasons"] == []

    def test_cash_gate_vetoes_open_ledger(self) -> None:
        from zephyr.strategy_pipeline.fw_backtest import _evaluate_cash_closure

        gate = _evaluate_cash_closure({"metrics": {"cash_ledger_reconciliation": {
            "samples": 20, "within_tolerance": False, "max_abs_residual": "80.0",
            "tolerance_abs": "0.01", "over_tolerance": 3, "bad_trade_rows": 0,
            "worst_date": "2026-01-06"}}})
        assert gate["accepted"] is False
        assert "现金账本不闭合" in gate["reasons"][0]

    def test_cash_gate_fail_closed_on_missing_or_empty(self) -> None:
        from zephyr.strategy_pipeline.fw_backtest import _evaluate_cash_closure

        assert _evaluate_cash_closure({})["accepted"] is False
        assert _evaluate_cash_closure({"metrics": {}})["accepted"] is False
        empty = _evaluate_cash_closure({"metrics": {"cash_ledger_reconciliation": {"samples": 0}}})
        assert empty["accepted"] is False and "无逐日样本" in empty["reasons"][0]

    def test_turnover_disclosure_reads_ssot_threshold(self) -> None:
        from zephyr.backtest.core.cost_attribution import TURNOVER_ONE_SIDE_ANNUAL_ALERT
        from zephyr.strategy_pipeline.fw_backtest import _turnover_disclosure

        result = {"metrics": {"cost_attribution": {
            "friction": {"turnover_one_side_annualized": 50.2, "cost_total": 12345.6},
            "alerts": [{"code": "TURNOVER-BREAKS-SLIPPAGE-PREMISE", "severity": "P1"}]}}}
        d = _turnover_disclosure(result)
        assert d["measured"] is True
        assert d["one_side_annualized"] == 50.2
        assert d["alert_threshold_one_side_annual"] == TURNOVER_ONE_SIDE_ANNUAL_ALERT
        assert d["over_alert"] is True
        assert len(d["cost_alerts"]) == 1

        # 未测/缺节：不静默给 0，也不误报超标
        none_d = _turnover_disclosure({})
        assert none_d["measured"] is False and none_d["over_alert"] is None
        nan_d = _turnover_disclosure({"metrics": {"cost_attribution": {"friction": {
            "turnover_one_side_annualized": float("nan")}}}})
        assert nan_d["measured"] is False and nan_d["over_alert"] is None


# ── GT-15 结构闸：内存里造出来的时序，必须真的到得了盘 ─────────────────────────


def test_every_timeseries_key_reaches_the_persisted_artifact() -> None:
    """大白话：组装器给每根曲线做了"落盘名册"，谁没被记上名册，这里当天就报。

    病根（H4-B）：现金腿在内存里造好、落盘那一步没人接手，产物里根本没有它，
    而旧测试只查内存对象——"看起来有、其实没落盘"这种洞只能靠结构闸堵：
    `_collect_timeseries` 的每个返回键必须 ∈ (`sink_backtest_result` 形参 ∪ metrics
    落盘登记表)，多出一个既不进 sink 也不进 metrics 的键即红。
    """
    import inspect

    from zephyr.backtest.io.backtest_result_sink import sink_backtest_result
    from zephyr.pf_core.strategy_engine.framework_composer import (
        _PERSISTED_VIA_METRICS_TS_KEYS,
        _collect_timeseries,
    )

    import pandas as pd

    keys = set(_collect_timeseries(engine=None))  # 无 portfolio → 空骨架，但键集恒定
    assert keys, "_collect_timeseries 返回键集为空（骨架契约变了，本闸失去意义）"
    landed = set(inspect.signature(sink_backtest_result).parameters) | set(_PERSISTED_VIA_METRICS_TS_KEYS)
    unlanded = keys - landed
    assert not unlanded, (
        f"这些时序键只进内存不落盘（产物会静默缺字段）：{sorted(unlanded)}；"
        "要么接进 sink 形参，要么登记进 _PERSISTED_VIA_METRICS_TS_KEYS"
    )

    # 同一条闸盖住第二条生产路径（CLI 单策略回测 scripts/run_backtest.py，R-H4B-s）：
    # 它与整装路径共用同一个 sink，却有一份自己的采集器——历史上这份连 cash_curve 都不造。
    rb = _load_run_backtest()
    cli_keys = set(
        rb._collect_timeseries(None, None, None, None, _FakeEngine(_fake_portfolio(pd)))
    )
    cli_landed = set(inspect.signature(sink_backtest_result).parameters) | set(
        rb._PERSISTED_VIA_METRICS_TS_KEYS
    )
    assert cli_keys - cli_landed == set(), (
        f"CLI 路径这些时序键只进内存不落盘：{sorted(cli_keys - cli_landed)}"
    )


def _fake_portfolio(pd_module):
    """最小引擎产物替身：nav/现金/成交各两条（含 cash_history 首行 None 建仓前快照）。"""
    d1 = pd_module.Timestamp("2026-01-05")
    d2 = pd_module.Timestamp("2026-01-06")
    return SimpleNamespace(
        nav_series={d1: 100000.0, d2: 101000.0},
        cash_history=[(None, 100000), (d1, 90000), (d2, 91000)],
        trades_log=[
            {
                "date": d1,
                "symbol": "600519",
                "side": "BUY",
                "price": 100.0,
                "quantity": 100,
                "commission": 5.0,
            }
        ],
    )


class _FakeEngine:
    def __init__(self, portfolio) -> None:
        self.last_portfolio = portfolio


def _load_run_backtest():
    """按路径加载 scripts/run_backtest.py（CLI 采集器不在包内，只能 spec 加载）。"""
    import importlib.util

    path = Path(__file__).resolve().parents[2] / "scripts" / "run_backtest.py"
    spec = importlib.util.spec_from_file_location("run_backtest_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_cli_backtest_artifact_carries_cash_leg() -> None:
    """大白话：点仪表盘"运行回测"跑出来的产物，事后要能查到当天口袋里还剩多少现金。

    判据打在采集器 + 落盘名册两处：`cash_curve` 必须①被造出来（含逐日现金、
    丢掉建仓前那行 None 快照），②被登记进 metrics 落盘名册。两者缺一即红——
    这正是 H4-B 在整装路径上栽过的同一条坑（R-H4B-s 是它的第二条生产路径）。
    """
    import pandas as pd

    rb = _load_run_backtest()
    ts = rb._collect_timeseries(None, None, None, None, _FakeEngine(_fake_portfolio(pd)))
    assert ts["cash_curve"] == [
        {"timestamp": "2026-01-05", "cash": 90000.0},
        {"timestamp": "2026-01-06", "cash": 91000.0},
    ], "现金腿内容与 cash_history 不一致（None 首行应被丢弃，其余逐日等值）"
    assert "cash_curve" in rb._PERSISTED_VIA_METRICS_TS_KEYS, (
        "现金腿未登记进落盘名册——产物里不会有它（sink 形参集不含该键）"
    )
    assert len(ts["cash_curve"]) == len(ts["equity_curve"]), "现金腿与净值腿不等长→逐日轧差不可核"
