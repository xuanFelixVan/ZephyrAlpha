# [BLUEPRINT] MOD-FEEDBACK_LOOP | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [MODULE] tests.risk.test_backtest_store
# [DOMAIN] D_RISK
# [TESTS] zephyr.risk.core.backtest_store; zephyr.risk.core.var_backtester(pnl_type 契约)
# [COVERAGE] 36号 §3.18 持久化门面(回测报告/双轨P&L/盘中日志/盘前基线) + §3.4 entry_var 链路 + §3.13 BacktestObservation pnl_type 守卫
# [MATURITY] evolving
# [TTL] task_bound

"""VarBacktestStore + entry_var 链路 + pnl_type 契约测试 (36号 §3.4/§3.13/§3.18)。

实证目标:
    1. save/load 往返一致 (回测报告/双轨 P&L/盘中重算日志/盘前基线/entry_var)
    2. 冷启动 None (首次启动/前日未持久化, §3.4/§3.19 冷启动守卫)
    3. 写入守卫: 非有限值/负 var/cvar<var(ES≥VaR 不变式,§3.18 阶段0)/非法日期 → raise
    4. 历史加载: 缺失日记 None 不补 0 (数据缺口即缺口)
    5. 读取损坏 → StateCorruptError 上抛 (fail-closed)
    6. BacktestObservation pnl_type: "dirty" 构造即拒绝, 默认 "clean" 零回归
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

import pytest

from zephyr.risk.core.backtest_store import (
    ENTRY_VAR_NAMESPACE,
    PREMARKET_BASELINE_NAMESPACE,
    InvalidBacktestStoreError,
    VarBacktestStore,
)
from zephyr.risk.core.var_backtester import BacktestObservation, InvalidBacktestInputError
from zephyr.shared.state_store import JsonStateStore, StateCorruptError

D0 = date(2026, 8, 20)


@pytest.fixture()
def store(tmp_path) -> VarBacktestStore:
    return VarBacktestStore(JsonStateStore(tmp_path))


# ── 回测报告 (§3.18 阶段 6) ───────────────────────────────────────────────────


class TestBacktestReport:
    def test_roundtrip(self, store: VarBacktestStore) -> None:
        report = {"action": "RECALIBRATE", "n_obs": 250, "kupiec_pof": {"reject": True}}
        store.save_backtest_report(D0, report)
        assert store.load_backtest_report(D0) == report

    def test_missing_returns_none(self, store: VarBacktestStore) -> None:
        assert store.load_backtest_report(D0) is None

    def test_per_day_isolation(self, store: VarBacktestStore) -> None:
        store.save_backtest_report(D0, {"action": "PASS"})
        store.save_backtest_report(D0 + timedelta(days=1), {"action": "REBUILD"})
        assert store.load_backtest_report(D0)["action"] == "PASS"
        assert store.load_backtest_report(D0 + timedelta(days=1))["action"] == "REBUILD"

    def test_non_mapping_rejected(self, store: VarBacktestStore) -> None:
        with pytest.raises(InvalidBacktestStoreError):
            store.save_backtest_report(D0, ["not", "a", "dict"])


# ── clean/dirty P&L 双轨 (§3.13/§3.18 阶段 4) ────────────────────────────────


class TestPnlDual:
    def test_roundtrip(self, store: VarBacktestStore) -> None:
        store.save_pnl_dual(D0, clean_pnl=-1234.5, dirty_pnl=-1300.0)
        rec = store.load_pnl_dual(D0)
        assert rec == {"trade_date": D0.isoformat(), "clean_pnl": -1234.5, "dirty_pnl": -1300.0}

    def test_missing_returns_none(self, store: VarBacktestStore) -> None:
        assert store.load_pnl_dual(D0) is None

    @pytest.mark.parametrize("field,value", [("clean_pnl", float("nan")), ("dirty_pnl", float("inf"))])
    def test_non_finite_rejected(self, store: VarBacktestStore, field: str, value: float) -> None:
        kwargs = {"clean_pnl": 1.0, "dirty_pnl": 1.0, field: value}
        with pytest.raises(InvalidBacktestStoreError):
            store.save_pnl_dual(D0, **kwargs)

    def test_history_missing_days_none_not_zero(self, store: VarBacktestStore) -> None:
        """历史加载缺日记 None (不静默补 0 污染回测)。"""
        dates = [D0 + timedelta(days=i) for i in range(3)]
        store.save_pnl_dual(dates[0], 100.0, 95.0)
        store.save_pnl_dual(dates[2], 300.0, 290.0)
        history = store.load_pnl_dual_history(dates)
        assert [h is None for h in history] == [False, True, False]
        assert history[0]["clean_pnl"] == 100.0
        assert history[2]["clean_pnl"] == 300.0


# ── entry_var 链路 (§3.4, latest 单记录) ─────────────────────────────────────


class TestEntryVar:
    def test_roundtrip(self, store: VarBacktestStore) -> None:
        store.save_entry_var(D0, 0.023, entry_es=0.031)
        rec = store.load_entry_var()
        assert rec == {
            "trade_date": D0.isoformat(),
            "entry_var": 0.023,
            "entry_es": 0.031,
        }

    def test_es_optional(self, store: VarBacktestStore) -> None:
        store.save_entry_var(D0, 0.02)
        assert store.load_entry_var()["entry_es"] is None

    def test_cold_start_none(self, store: VarBacktestStore) -> None:
        """§3.4 冷启动守卫: 首次启动无历史 entry_var → None (消费方 None 守卫)。"""
        assert store.load_entry_var() is None

    def test_latest_wins(self, store: VarBacktestStore) -> None:
        store.save_entry_var(D0, 0.02)
        store.save_entry_var(D0 + timedelta(days=1), 0.025)
        assert store.load_entry_var()["entry_var"] == 0.025

    def test_negative_var_rejected(self, store: VarBacktestStore) -> None:
        with pytest.raises(InvalidBacktestStoreError):
            store.save_entry_var(D0, -0.01)

    def test_es_below_var_rejected(self, store: VarBacktestStore) -> None:
        """ES ≥ VaR 不变式写入守卫。"""
        with pytest.raises(InvalidBacktestStoreError):
            store.save_entry_var(D0, 0.03, entry_es=0.02)


# ── 盘前基线 (§3.18 阶段 2, latest 单记录) ───────────────────────────────────


class TestPremarketBaseline:
    def test_roundtrip(self, store: VarBacktestStore) -> None:
        store.save_premarket_baseline(D0, 0.021, 0.028)
        rec = store.load_premarket_baseline()
        assert rec == {
            "trade_date": D0.isoformat(),
            "var_95": 0.021,
            "cvar_95": 0.028,
        }

    def test_cold_start_none(self, store: VarBacktestStore) -> None:
        """§3.19 阶段 2: None=首次启动, §3.12 盘中 var_change_ratio 跳过对比。"""
        assert store.load_premarket_baseline() is None

    def test_cvar_below_var_rejected(self, store: VarBacktestStore) -> None:
        """§3.18 阶段 0 ES ≥ VaR 不变式: 违反即拒绝持久化。"""
        with pytest.raises(InvalidBacktestStoreError):
            store.save_premarket_baseline(D0, 0.03, 0.02)

    def test_negative_var_rejected(self, store: VarBacktestStore) -> None:
        with pytest.raises(InvalidBacktestStoreError):
            store.save_premarket_baseline(D0, -0.01, 0.02)

    def test_non_finite_rejected(self, store: VarBacktestStore) -> None:
        with pytest.raises(InvalidBacktestStoreError):
            store.save_premarket_baseline(D0, float("nan"), 0.02)


# ── 盘中重算日志 (§3.18 阶段 3) ───────────────────────────────────────────────


class TestIntradayRecalcLog:
    def test_roundtrip(self, store: VarBacktestStore) -> None:
        entries = [
            {"timestamp": "2026-08-20T10:30:00+00:00", "var_95": 0.03, "significant_change": True},
            {"timestamp": "2026-08-20T11:00:00+00:00", "var_95": 0.028, "significant_change": False},
        ]
        store.save_intraday_recalc_log(D0, entries)
        loaded = store.load_intraday_recalc_log(D0)
        assert loaded == entries

    def test_missing_returns_none(self, store: VarBacktestStore) -> None:
        assert store.load_intraday_recalc_log(D0) is None

    def test_empty_entries_roundtrip(self, store: VarBacktestStore) -> None:
        store.save_intraday_recalc_log(D0, [])
        assert store.load_intraday_recalc_log(D0) == []


# ── 横切: 日期校验 + 读取损坏 fail-closed ────────────────────────────────────


class TestCrossCutting:
    def test_invalid_trade_date_rejected(self, store: VarBacktestStore) -> None:
        with pytest.raises(InvalidBacktestStoreError):
            store.save_pnl_dual("2026-08-20", 1.0, 1.0)  # type: ignore[arg-type]

    def test_corrupt_read_raises(self, store: VarBacktestStore, tmp_path) -> None:
        (tmp_path / f"{ENTRY_VAR_NAMESPACE}.json").write_text("{broken", encoding="utf-8")
        with pytest.raises(StateCorruptError):
            store.load_entry_var()

    def test_corrupt_baseline_read_raises(self, store: VarBacktestStore, tmp_path) -> None:
        (tmp_path / f"{PREMARKET_BASELINE_NAMESPACE}.json").write_text("[]", encoding="utf-8")
        with pytest.raises(StateCorruptError):
            store.load_premarket_baseline()


# ── BacktestObservation pnl_type 契约 (§3.13) ────────────────────────────────


class TestPnlTypeContract:
    def test_default_clean_zero_regression(self) -> None:
        obs = BacktestObservation(
            date=datetime(2024, 1, 1), var_forecast=0.02, es_forecast=0.025, realized_return=-0.01
        )
        assert obs.pnl_type == "clean"
        assert obs.is_violation is False

    def test_explicit_clean_accepted(self) -> None:
        obs = BacktestObservation(
            date=datetime(2024, 1, 1),
            var_forecast=0.02,
            es_forecast=0.025,
            realized_return=-0.01,
            pnl_type="clean",
        )
        assert obs.pnl_type == "clean"

    def test_dirty_rejected(self) -> None:
        """dirty P&L 会污染模型纯度检验, 构造即拒绝 (§3.13 契约)。"""
        with pytest.raises(InvalidBacktestInputError):
            BacktestObservation(
                date=datetime(2024, 1, 1),
                var_forecast=0.02,
                es_forecast=0.025,
                realized_return=-0.01,
                pnl_type="dirty",
            )
