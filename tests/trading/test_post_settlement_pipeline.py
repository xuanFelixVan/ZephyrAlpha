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
