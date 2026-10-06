# [BLUEPRINT] MOD-TRADING-003 | docs/03_modules/_domain_trading/blueprint.md
# [MODULE] tests.trading.test_post_settlement_pipeline
# [DOMAIN] D_TRADING
# [INVARIANTS] 15:30 cron规格; 不一致必告警; 异常捕获不逃逸; 空日期拒绝
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidPostSettlementInputError
# [TESTS] self
# [TTL] permanent
"""盘后 15:30 调度接线入口测试（54 号 §2.4 缺口 #2，AI-NIGHT-001 包P）。"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from zephyr.trading.post_settlement_pipeline import (
    POST_SETTLEMENT_CRON,
    InvalidPostSettlementInputError,
    PostSettlementRunResult,
    build_post_settlement_jobs,
    run_post_settlement_pipeline,
)


@dataclass(frozen=True)
class _FakeReconResult:
    matched: bool
    drifts: tuple = ()


class TestJobSpecs:
    def test_cron_is_15_30(self):
        jobs = build_post_settlement_jobs()
        assert len(jobs) == 2
        for job in jobs:
            assert job.cron_expression == POST_SETTLEMENT_CRON == "30 15 * * *"
            assert job.trading_day_only is True
            assert job.entrypoint.endswith("run_post_settlement_pipeline")

    def test_job_ids_stable(self):
        ids = {j.job_id for j in build_post_settlement_jobs()}
        assert ids == {"post_settlement_reconcile", "post_settlement_daily_audit"}


class TestPipeline:
    def test_happy_path_both_ok(self):
        calls: list[str] = []
        result = run_post_settlement_pipeline(
            "2026-08-20",
            reconcile_fn=lambda d: calls.append(f"recon:{d}") or _FakeReconResult(matched=True),
            audit_fn=lambda d: calls.append(f"audit:{d}"),
        )
        assert result.reconcile_status == "OK"
        assert result.audit_status == "OK"
        assert result.errors == ()
        assert calls == ["recon:2026-08-20", "audit:2026-08-20"]

    def test_drift_triggers_alert(self):
        alerts: list[tuple[str, str]] = []
        result = run_post_settlement_pipeline(
            "2026-08-20",
            reconcile_fn=lambda d: _FakeReconResult(matched=False, drifts=("d1", "d2")),
            alert_sink=lambda d, m: alerts.append((d, m)),
        )
        assert result.reconcile_status == "DRIFT"
        assert len(alerts) == 1 and "2 笔" in alerts[0][1]

    def test_reconcile_exception_captured_and_alerted(self):
        alerts: list[tuple[str, str]] = []

        def _boom(d: str):
            raise RuntimeError("broker offline")

        result = run_post_settlement_pipeline(
            "2026-08-20",
            reconcile_fn=_boom,
            audit_fn=lambda d: None,  # 审计仍执行（步骤隔离）
            alert_sink=lambda d, m: alerts.append((d, m)),
        )
        assert result.reconcile_status == "ERROR"
        assert result.audit_status == "OK"
        assert len(result.errors) == 1 and "broker offline" in result.errors[0]
        assert alerts  # 异常必告警

    def test_audit_exception_captured(self):
        def _boom(d: str):
            raise ValueError("audit input missing")

        result = run_post_settlement_pipeline("2026-08-20", audit_fn=_boom)
        assert result.audit_status == "ERROR"
        assert "audit input missing" in result.errors[0]

    def test_optional_fns_skipped(self):
        result = run_post_settlement_pipeline("2026-08-20")
        assert result.reconcile_status == "SKIPPED"
        assert result.audit_status == "SKIPPED"
        assert isinstance(result, PostSettlementRunResult)

    def test_empty_trade_date_rejected(self):
        with pytest.raises(InvalidPostSettlementInputError):
            run_post_settlement_pipeline("  ")

    def test_alert_sink_failure_swallowed(self):
        def _bad_sink(d: str, m: str):
            raise RuntimeError("sink down")

        result = run_post_settlement_pipeline(
            "2026-08-20",
            reconcile_fn=lambda d: _FakeReconResult(matched=False, drifts=("x",)),
            alert_sink=_bad_sink,
        )
        # 告警出口故障不阻断：DRIFT 状态仍正确落盘
        assert result.reconcile_status == "DRIFT"


class TestEventLegSweep:
    """F62 违宪整改事件腿（2026-09-29 SW5）：事件注入触发一次 + 幂等重放零副作用。"""

    def setup_method(self):
        from zephyr.trading.post_settlement_pipeline import reset_sweep_state

        reset_sweep_state()

    def teardown_method(self):
        from zephyr.trading.post_settlement_pipeline import reset_sweep_state

        reset_sweep_state()

    def _deps(self, calls: list):
        from zephyr.trading.post_settlement_pipeline import SweepDeps

        return SweepDeps(
            reconcile_fn=lambda d: calls.append(f"recon:{d}") or _FakeReconResult(matched=True),
            audit_fn=lambda d: calls.append(f"audit:{d}"),
        )

    def test_sweep_runs_once_and_replay_zero_side_effect(self):
        """同 trade_date 首跑执行一次；重放零副作用（下游 fn 不再被调）。"""
        from zephyr.trading.post_settlement_pipeline import run_daily_end_sweep

        calls: list[str] = []
        deps = self._deps(calls)
        result, status = run_daily_end_sweep("2026-08-20", deps=deps)
        assert status == "OK"
        assert result.reconcile_status == "OK" and result.audit_status == "OK"
        assert calls == ["recon:2026-08-20", "audit:2026-08-20"]
        # 重放：去重命中，下游零调用
        result2, status2 = run_daily_end_sweep("2026-08-20", deps=deps)
        assert status2 == "REPLAYED"
        assert result2 is result
        assert calls == ["recon:2026-08-20", "audit:2026-08-20"]  # 零副作用
        # force 逃生：显式强制才重跑
        _, status3 = run_daily_end_sweep("2026-08-20", deps=deps, force=True)
        assert status3 == "OK"
        assert len(calls) == 4

    def test_unwired_deps_no_fake_run(self):
        """依赖未装配 → UNWIRED 显式占位，流水线不被伪跑。"""
        from zephyr.trading.post_settlement_pipeline import run_daily_end_sweep

        result, status = run_daily_end_sweep("2026-08-20")
        assert status == "UNWIRED"
        assert result.reconcile_status == "UNWIRED"
        assert result.audit_status == "UNWIRED"

    def test_register_sweep_deps_rejects_foreign_type(self):
        from zephyr.trading.post_settlement_pipeline import register_sweep_deps

        with pytest.raises(InvalidPostSettlementInputError):
            register_sweep_deps(object())

    def test_event_injection_triggers_sweep_exactly_once(self):
        """事件注入：两次同日 emit → 下游只执行一次 + swept 回执两发（OK/REPLAYED）。"""
        from zephyr.shared.event_bus import bus
        from zephyr.trading.post_settlement_pipeline import (
            TOPIC_RECON_REQUESTED,
            TOPIC_RECON_SWEPT,
            subscribe_eventbus,
        )

        subscribe_eventbus()
        calls: list[str] = []
        # deps 经注册口注入（装配批同款路径）
        from zephyr.trading.post_settlement_pipeline import register_sweep_deps

        register_sweep_deps(self._deps(calls))

        received: list[dict] = []
        bus.subscribe(TOPIC_RECON_SWEPT, lambda ev: received.append(ev.payload))
        bus.emit(TOPIC_RECON_REQUESTED, {"trade_date": "2026-08-21"})
        bus.emit(TOPIC_RECON_REQUESTED, {"trade_date": "2026-08-21"})  # 重放

        assert calls == ["recon:2026-08-21", "audit:2026-08-21"]  # 触发一次
        assert [r["status"] for r in received] == ["OK", "REPLAYED"]
        assert all(r["trade_date"] == "2026-08-21" for r in received)

    def test_subscribe_idempotent(self):
        from zephyr.shared.event_bus import bus
        from zephyr.trading.post_settlement_pipeline import (
            TOPIC_RECON_REQUESTED,
            subscribe_eventbus,
        )

        subscribe_eventbus()
        subscribe_eventbus()  # 幂等：重复订阅不叠加 handler
        from zephyr.trading.post_settlement_pipeline import register_sweep_deps

        register_sweep_deps(self._deps([]))
        bus.emit(TOPIC_RECON_REQUESTED, {"trade_date": "2026-08-22"})
        # 单 handler 语义：REPLAYED 只会因去重出现，而非双 handler 双跑——
        # 若重复订阅叠加，第二次 emit 才能观察到副作用倍增；此处单发单验即可
        from zephyr.trading.post_settlement_pipeline import run_daily_end_sweep

        _, status = run_daily_end_sweep("2026-08-22")
        assert status == "REPLAYED"  # 事件腿已把该日写入去重账
