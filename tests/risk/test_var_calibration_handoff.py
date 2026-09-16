# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md | §
# [MODULE] tests.risk.test_var_calibration_handoff
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] task_bound
"""VaR 回测定级跨进程闭环（H5-P0 链2：双端死链 → 产端归档 + 消费端单一执行者）。

链路（36号 §3.9 装配 / §3.10 三档 / §3.18 阶段 2·6 持久化）：
    会话进程  RiskLayerOrchestrator.evaluate_intraday 健康轮 → save_premarket_baseline
              （latest + 按日归档 var_premarket_baseline_YYYY-MM-DD = 预测腿）
    盘后进程  DailyAuditor.run_var_backtest_from_store（宿主 run_post_settlement）
              两腿配对 → run_var_backtest 定级 → save_backtest_report
    会话进程  构造期 _consume_var_calibration_verdict 读回 → **唯一执行者**
              apply_var_backtest_action → var_model_status / 静态映射
              + 消费指针 var_calibration_applied（同一 trade_date 只扣一次）

实证要点：
  1. 盘前基线双写（latest 会被次日覆盖，归档才是回测预测腿的唯一历史来源）
  2. 缺腿日剔除不补 0；两腿零配对 → 不归档不定级（无数据≠通过）
  3. 定级归档 JSON 可序列化（numpy 标量降级），消费端 load 即得
  4. 消费端只在启动跑一次、动作只经 §3.10 执行者（本链路不另立决策头）
  5. 消费指针幂等：业主 clear 后重启不被旧报告复扣；产端出新报告才再扣
  6. 报告损坏 / 动作字段非法 → fail-closed 按 REBUILD（绝不按 PASS 放行、不猜动作）
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from zephyr.ex_core.risk_layer_orchestrator import RiskLayerOrchestrator
from zephyr.position.core.drawdown_controller import DrawdownController
from zephyr.risk.core.backtest_store import VarBacktestStore
from zephyr.risk.core.daily_auditor import DailyAuditor, InvalidAuditInputError
from zephyr.risk.core.drawdown_tracker import DrawdownTracker
from zephyr.risk.core.tail_risk_monitor import TailRiskMonitor
from zephyr.risk.core.var_calculator import VaRCalculator
from zephyr.shared.contracts.order import Order
from zephyr.shared.contracts.position import PositionSnapshot
from zephyr.shared.state_store import JsonStateStore
from zephyr.trading.trading_contracts.broker_interface import BrokerInterface

_T0 = datetime(2026, 9, 16, 10, 0, tzinfo=UTC)
_NAV = 1_000_000.0


class FakeBroker(BrokerInterface):
    """券商替身（外部边界）：静态空仓快照 + 订单留痕。"""

    def __init__(self) -> None:
        self.submitted: list[Order] = []

    @property
    def broker_id(self) -> str:
        return "fake"

    def connect(self) -> bool:
        return True

    def disconnect(self) -> None:
        pass

    def submit_order(self, order: Order) -> str:
        self.submitted.append(order)
        return f"bk-{order.order_id}"

    def cancel_order(self, broker_order_id: str) -> bool:
        return True

    def query_order(self, broker_order_id: str) -> Order | None:
        return None

    def get_positions(self) -> PositionSnapshot:
        return PositionSnapshot(
            as_of_timestamp=datetime.now(UTC),
            portfolio_id="fake",
            idempotency_key="fake",
            cash=Decimal("1000000"),
            gross_leverage=0.0,
            holdings={},
            market_values={},
            total_market_value=Decimal("0"),
        )

    def register_fill_callback(self, callback) -> None:
        pass


def _make_orchestrator(
    *,
    store: JsonStateStore | None = None,
    capital: float | None = None,
    clock_now: datetime = _T0,
) -> RiskLayerOrchestrator:
    return RiskLayerOrchestrator(
        drawdown_controller=DrawdownController(),
        drawdown_tracker=DrawdownTracker(initial_net_value=_NAV),
        var_calculator=VaRCalculator(),
        tail_risk_monitor=TailRiskMonitor(),
        broker=FakeBroker(),
        bankruptcy_floor_initial_capital=capital,
        state_store=store,
        clock=lambda: clock_now,
    )


def _seed_healthy_nav(orch: RiskLayerOrchestrator, *, rounds: int = 31, day: date | None = None) -> None:
    """灌入震荡净值序列使 VaR 动态口径健康（degraded=False）——盘前基线落盘前置条件。"""
    stamp = datetime(day.year, day.month, day.day, 10, 0, tzinfo=UTC) if day else _T0
    for i in range(rounds):
        orch.evaluate_intraday(_NAV * (1.05 if i % 2 else 1.0), now=stamp)


def _write_legs(store: VarBacktestStore, start: date, days: int, *, var: float = 40_000.0, pnl: float = 100.0) -> list[date]:
    """写 days 天两腿（跳过周末），返回写入日序。"""
    written: list[date] = []
    k = 0
    while len(written) < days:
        d = start + timedelta(days=k)
        k += 1
        if d.weekday() >= 5:
            continue
        store.save_premarket_baseline(d, var, var * 1.3)
        store.save_pnl_dual(d, pnl, pnl * 1.1)
        written.append(d)
    return written


# ---------------------------------------------------------------------
# ① 预测腿：盘前基线双写（latest + 按日归档）
# ---------------------------------------------------------------------


class TestPremarketBaselineArchive:
    def test_double_write_keeps_history_after_latest_is_overwritten(self, tmp_path: Path) -> None:
        store = VarBacktestStore(JsonStateStore(tmp_path / "state"))
        d1, d2 = date(2026, 9, 1), date(2026, 9, 2)
        store.save_premarket_baseline(d1, 30_000.0, 40_000.0)
        store.save_premarket_baseline(d2, 50_000.0, 60_000.0)

        latest = store.load_premarket_baseline()
        assert latest is not None and latest["trade_date"] == "2026-09-02"  # latest 语义不变
        # 归档：旧日预测腿必须仍在（latest 单记录不足以支撑回测的根因）
        assert store.load_premarket_baseline_for_date(d1)["var_95"] == pytest.approx(30_000.0)
        assert store.load_premarket_baseline_for_date(d2)["var_95"] == pytest.approx(50_000.0)

    def test_history_missing_day_is_none_not_zero(self, tmp_path: Path) -> None:
        store = VarBacktestStore(JsonStateStore(tmp_path / "state"))
        store.save_premarket_baseline(date(2026, 9, 1), 30_000.0, 40_000.0)
        hist = store.load_premarket_baseline_history([date(2026, 9, 1), date(2026, 9, 2)])
        assert hist[0] is not None and hist[1] is None  # 数据缺口即缺口


# ---------------------------------------------------------------------
# ② 产端：两腿配对定级 + 归档
# ---------------------------------------------------------------------


class TestProducerGradingAndArchive:
    def test_no_legs_writes_no_report(self, tmp_path: Path) -> None:
        root = tmp_path / "state"
        store = VarBacktestStore(JsonStateStore(root))
        report = DailyAuditor().run_var_backtest_from_store(store, date(2026, 9, 16))
        assert report is None
        assert not any(p.name.startswith("var_backtest_report_") for p in root.iterdir())

    def test_forecast_leg_only_is_not_paired(self, tmp_path: Path) -> None:
        """只有预测腿（实现腿未接线）→ 零配对不归档，绝不补 0 造样本。"""
        root = tmp_path / "state"
        store = VarBacktestStore(JsonStateStore(root))
        d = date(2026, 9, 1)
        for k in range(40):
            store.save_premarket_baseline(d + timedelta(days=k), 40_000.0, 52_000.0)
        assert DailyAuditor().run_var_backtest_from_store(store, date(2026, 10, 20)) is None
        assert not any(p.name.startswith("var_backtest_report_") for p in root.iterdir())

    def test_insufficient_pairs_archives_skip_verdict(self, tmp_path: Path) -> None:
        root = tmp_path / "state"
        store = VarBacktestStore(JsonStateStore(root))
        days = _write_legs(store, date(2026, 9, 1), days=10)
        report = DailyAuditor().run_var_backtest_from_store(store, date(2026, 9, 20), trade_dates=days)
        assert report is not None and report.n_obs == 10
        assert report.action == "PASS" and "INSUFFICIENT_SAMPLE_SKIP" in report.flags

        rec = store.load_backtest_report(date(2026, 9, 20))
        assert rec is not None and rec["action"] == "PASS" and rec["n_obs"] == 10
        assert rec["gap_days"] == 0
        json.dumps(rec)  # 归档必须 JSON 安全（JsonStateStore 原子写前提）

    def test_persistent_breaches_never_grade_pass(self, tmp_path: Path) -> None:
        """实现腿持续超限 → 定级不得为 PASS（校准闭环有意义的前提）。"""
        root = tmp_path / "state"
        store = VarBacktestStore(JsonStateStore(root))
        _write_legs(store, date(2026, 6, 1), days=40, var=40_000.0, pnl=-120_000.0)
        report = DailyAuditor().run_var_backtest_from_store(store, date(2026, 9, 20))
        assert report is not None and report.n_obs == 40
        assert report.action in ("RECALIBRATE", "REBUILD")
        assert store.load_backtest_report(date(2026, 9, 20))["action"] == report.action

    def test_store_without_facade_interface_raises(self, tmp_path: Path) -> None:
        with pytest.raises(InvalidAuditInputError):
            DailyAuditor().run_var_backtest_from_store(object(), date(2026, 9, 16))  # type: ignore[arg-type]


# ---------------------------------------------------------------------
# ③ 消费端：启动读取 → 唯一执行者落地
# ---------------------------------------------------------------------


class TestConsumerAppliesThroughSingleActuator:
    def test_rebuild_verdict_applied_at_startup(self, tmp_path: Path) -> None:
        root = JsonStateStore(tmp_path / "state")
        store = VarBacktestStore(root)
        store.save_backtest_report(date(2026, 9, 15), {"action": "REBUILD", "reason": "basel red", "n_obs": 80})

        orch = _make_orchestrator(store=root)
        result = orch.var_calibration_result
        assert result is not None and result["action"] == "REBUILD"
        assert orch.var_model_unavailable is True
        snap = orch.evaluate_intraday(_NAV, now=_T0)
        assert snap.var_model_status == "STATIC_REBUILD"  # 静态映射下一轮起生效
        assert root.load("var_model_status")["status"] == "UNAVAILABLE"

    def test_restart_does_not_reapply_same_trade_date(self, tmp_path: Path) -> None:
        """消费指针幂等：业主解除后重启不被旧报告复扣（否则 §3.10 恢复永远走不完）。"""
        root = JsonStateStore(tmp_path / "state")
        VarBacktestStore(root).save_backtest_report(date(2026, 9, 15), {"action": "REBUILD", "reason": "r", "n_obs": 80})

        first = _make_orchestrator(store=root)
        assert first.var_model_unavailable is True
        first.clear_var_model_unavailable(owner_confirmed=True)

        second = _make_orchestrator(store=root)
        assert second.var_calibration_result is None  # 同一份报告不再复扣
        assert second.var_model_unavailable is False  # 业主确认结果存活

    def test_fresh_verdict_from_producer_is_consumed(self, tmp_path: Path) -> None:
        root = JsonStateStore(tmp_path / "state")
        VarBacktestStore(root).save_backtest_report(date(2026, 9, 15), {"action": "REBUILD", "reason": "r", "n_obs": 80})
        assert _make_orchestrator(store=root).var_calibration_result is not None

        VarBacktestStore(root).save_backtest_report(date(2026, 9, 16), {"action": "PASS", "reason": "green", "n_obs": 90})
        third = _make_orchestrator(store=root, clock_now=datetime(2026, 9, 16, 9, 0, tzinfo=UTC))
        assert third.var_calibration_result is not None
        assert third.var_calibration_result["action"] == "PASS"

    def test_corrupt_report_fails_closed_to_rebuild(self, tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
        root = JsonStateStore(tmp_path / "state")
        VarBacktestStore(root).save_backtest_report(date(2026, 9, 15), {"action": "PASS", "reason": "g", "n_obs": 90})
        victim = tmp_path / "state" / "var_backtest_report_2026-09-15.json"
        victim.write_text("{not json", encoding="utf-8")

        with caplog.at_level(logging.CRITICAL, logger="zephyr.ex_core.risk_layer_orchestrator"):
            orch = _make_orchestrator(store=root)
        assert orch.var_calibration_result["action"] == "REBUILD"  # 损坏≠放行
        assert orch.var_model_unavailable is True
        assert any("fail-closed" in r.getMessage() for r in caplog.records)

    def test_illegal_action_field_fails_closed_to_rebuild(self, tmp_path: Path) -> None:
        root = JsonStateStore(tmp_path / "state")
        VarBacktestStore(root).save_backtest_report(date(2026, 9, 15), {"action": "DO_WHATEVER", "reason": "x", "n_obs": 90})
        orch = _make_orchestrator(store=root)
        assert orch.var_calibration_result["action"] == "REBUILD"
        assert orch.var_model_unavailable is True

    def test_no_report_and_no_store_are_quiet_cold_starts(self, tmp_path: Path) -> None:
        assert _make_orchestrator(store=JsonStateStore(tmp_path / "empty")).var_calibration_result is None
        assert _make_orchestrator(store=None).var_calibration_result is None


# ---------------------------------------------------------------------
# ④ 端到端接缝：会话写预测腿 → 盘后读同一根定级
# ---------------------------------------------------------------------


class TestSessionToPostSettlementSeam:
    def test_healthy_round_archives_forecast_leg_once_per_day(self, tmp_path: Path) -> None:
        root = JsonStateStore(tmp_path / "state")
        orch = _make_orchestrator(store=root)
        _seed_healthy_nav(orch)
        assert orch.evaluate_intraday(_NAV, now=_T0).degraded is False  # 动态口径健康轮

        store = VarBacktestStore(root)
        first = store.load_premarket_baseline()
        assert first is not None and first["var_95"] > 0 and first["cvar_95"] >= first["var_95"]
        orch.evaluate_intraday(_NAV * 1.05, now=_T0)  # 同日再来一轮
        assert store.load_premarket_baseline() == first  # 每交易日只落一次（不逐轮刷）

        archives = sorted(p.name for p in root.root_dir.glob("var_premarket_baseline_*.json"))
        assert archives == ["var_premarket_baseline_2026-09-16.json"]
        assert store.load_premarket_baseline_for_date(_T0.date()) == first

    def test_degraded_round_writes_no_forecast_leg(self, tmp_path: Path) -> None:
        root = JsonStateStore(tmp_path / "state")
        orch = _make_orchestrator(store=root)
        assert orch.evaluate_intraday(_NAV, now=_T0).degraded is True  # 冷启动无历史
        assert not list(root.root_dir.glob("var_premarket_baseline*.json"))

    def test_session_legs_feed_producer_pairing(self, tmp_path: Path) -> None:
        """会话归档的预测腿 + 双轨 clean P&L → 产端按日配对成样本（接缝真连通）。"""
        root = JsonStateStore(tmp_path / "state")
        store = VarBacktestStore(root)
        orch = _make_orchestrator(store=root)
        _seed_healthy_nav(orch)
        assert orch.evaluate_intraday(_NAV, now=_T0).degraded is False  # 落 2026-09-16 基线
        store.save_pnl_dual(_T0.date(), clean_pnl=-500.0, dirty_pnl=-700.0)

        report = DailyAuditor().run_var_backtest_from_store(store, _T0.date(), window_days=30)
        assert report is not None
        assert report.n_obs == 1 and "INSUFFICIENT_SAMPLE_SKIP" in report.flags
        archived = store.load_backtest_report(_T0.date())
        assert isinstance(archived, dict) and archived["n_obs"] == 1
        json.dumps(archived)
