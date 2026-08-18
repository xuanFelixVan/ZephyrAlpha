# [BLUEPRINT] MOD-RK-19 | docs/03_modules/_domain_risk/operational_risk_monitor/blueprint.md | §test
# [MODULE] tests.risk.core.test_operational_risk_monitor
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.core.operational_risk_monitor; zephyr.ex_core.audit_journal.auditor
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_operational_risk_monitor.py
# [A_test] module_id: MOD-RK-19 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""G6 单元测试: OperationalRiskMonitor — 阈值解释层。

覆盖: 失败率/延迟突破判定、严重度分级（info/warning/HALT）、
findings 内容、零提交数据、RiskCheckResult 转换、自定义阈值、异常输入。
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

pytest.importorskip(
    "zephyr.risk.core.operational_risk_monitor",
    reason="operational_risk_monitor not importable",
)

from zephyr.ex_core.audit_journal.auditor import OperationalRiskStats  # noqa: E402
from zephyr.risk.core.operational_risk_monitor import (  # noqa: E402
    DEFAULT_FAILURE_RATE_THRESHOLD,
    DEFAULT_LATENCY_P95_THRESHOLD_MS,
    InvalidOperationalRiskInputError,
    OperationalRiskAssessment,
    OperationalRiskMonitor,
)

# ── 辅助 ─────────────────────────────────────────────────────────────


def _make_stats(
    submission_count: int = 100,
    rejection_count: int = 2,
    filled_count: int = 98,
    failure_rate: float = 0.02,
    fill_rate: float = 0.98,
    latency_count: int = 98,
    latency_p50_ms: float = 50.0,
    latency_p95_ms: float = 80.0,
    latency_max_ms: float = 200.0,
    latency_mean_ms: float = 60.0,
) -> OperationalRiskStats:
    """构造 OperationalRiskStats（全字段可控）。"""
    now = datetime.now(UTC)
    return OperationalRiskStats(
        period_start=now,
        period_end=now,
        submission_count=submission_count,
        rejection_count=rejection_count,
        filled_count=filled_count,
        failure_rate=failure_rate,
        fill_rate=fill_rate,
        latency_count=latency_count,
        latency_p50_ms=latency_p50_ms,
        latency_p95_ms=latency_p95_ms,
        latency_max_ms=latency_max_ms,
        latency_mean_ms=latency_mean_ms,
        generated_at=now,
    )


# ── 健康场景 ─────────────────────────────────────────────────────────


class TestHealthy:
    def test_no_breach_info(self):
        """无突破 → info，passed=True。"""
        mon = OperationalRiskMonitor()
        a = mon.assess(_make_stats())
        assert a.overall_severity == "info"
        assert a.failure_rate_breached is False
        assert a.latency_breached is False

    def test_healthy_passed(self):
        mon = OperationalRiskMonitor()
        a = mon.assess(_make_stats())
        check = mon.to_risk_check_result(a)
        assert check.passed is True
        assert check.severity == "info"

    def test_no_findings_when_healthy(self):
        mon = OperationalRiskMonitor()
        a = mon.assess(_make_stats())
        assert len(a.findings) == 0


# ── 失败率突破 ───────────────────────────────────────────────────────


class TestFailureRateBreach:
    def test_failure_rate_warning(self):
        """failure_rate > threshold 但 < 2× → warning。"""
        mon = OperationalRiskMonitor()
        # 0.08 > 0.05, < 0.10
        a = mon.assess(_make_stats(failure_rate=0.08, rejection_count=8))
        assert a.failure_rate_breached is True
        assert a.failure_rate_severe is False
        assert a.overall_severity == "warning"

    def test_failure_rate_severe_halt(self):
        """failure_rate >= 2× threshold → HALT。"""
        mon = OperationalRiskMonitor()
        # 0.15 >= 0.10 (2× 0.05)
        a = mon.assess(_make_stats(failure_rate=0.15, rejection_count=15))
        assert a.failure_rate_severe is True
        assert a.overall_severity == "HALT"

    def test_failure_rate_exactly_threshold_not_breached(self):
        """failure_rate == threshold（使用 > 不是 >=）→ 不突破。"""
        mon = OperationalRiskMonitor()
        a = mon.assess(_make_stats(failure_rate=0.05))
        assert a.failure_rate_breached is False

    def test_failure_rate_finding_content(self):
        mon = OperationalRiskMonitor()
        a = mon.assess(_make_stats(failure_rate=0.08, rejection_count=8))
        assert any("failure_rate" in f for f in a.findings)
        assert any("0.0800" in f or "0.08" in f for f in a.findings)


# ── 延迟突破 ─────────────────────────────────────────────────────────


class TestLatencyBreach:
    def test_latency_warning(self):
        """latency_p95 > threshold 但 < 2× → warning。"""
        mon = OperationalRiskMonitor()
        a = mon.assess(_make_stats(latency_p95_ms=600.0))
        assert a.latency_breached is True
        assert a.latency_severe is False
        assert a.overall_severity == "warning"

    def test_latency_severe_halt(self):
        """latency_p95 >= 2× threshold → HALT。"""
        mon = OperationalRiskMonitor()
        # 1100 >= 1000 (2× 500)
        a = mon.assess(_make_stats(latency_p95_ms=1100.0))
        assert a.latency_severe is True
        assert a.overall_severity == "HALT"

    def test_latency_finding_content(self):
        mon = OperationalRiskMonitor()
        a = mon.assess(_make_stats(latency_p95_ms=600.0))
        assert any("latency_p95" in f for f in a.findings)


# ── 双维度组合 ───────────────────────────────────────────────────────


class TestCombinedBreach:
    def test_both_breached_halt(self):
        """failure + latency 都突破（非 severe）→ HALT。"""
        mon = OperationalRiskMonitor()
        a = mon.assess(_make_stats(failure_rate=0.08, latency_p95_ms=600.0))
        assert a.failure_rate_breached is True
        assert a.latency_breached is True
        assert a.overall_severity == "HALT"
        assert len(a.findings) == 2

    def test_failure_severe_latency_ok_halt(self):
        """failure severe + latency ok → HALT。"""
        mon = OperationalRiskMonitor()
        a = mon.assess(_make_stats(failure_rate=0.15, latency_p95_ms=80.0))
        assert a.failure_rate_severe is True
        assert a.latency_breached is False
        assert a.overall_severity == "HALT"

    def test_latency_severe_failure_ok_halt(self):
        """latency severe + failure ok → HALT。"""
        mon = OperationalRiskMonitor()
        a = mon.assess(_make_stats(failure_rate=0.02, latency_p95_ms=1100.0))
        assert a.latency_severe is True
        assert a.failure_rate_breached is False
        assert a.overall_severity == "HALT"


# ── 零提交数据 ───────────────────────────────────────────────────────


class TestZeroSubmissions:
    def test_zero_submissions_info_with_finding(self):
        """submission_count=0 → info（无突破）+ insufficient data finding。"""
        mon = OperationalRiskMonitor()
        a = mon.assess(_make_stats(submission_count=0, rejection_count=0, filled_count=0, failure_rate=0.0, fill_rate=0.0, latency_count=0))
        assert a.overall_severity == "info"
        assert len(a.findings) == 1
        assert "insufficient data" in a.findings[0] or "no submissions" in a.findings[0].lower()


# ── RiskCheckResult 转换 ─────────────────────────────────────────────


class TestToRiskCheckResult:
    def test_info_passed(self):
        mon = OperationalRiskMonitor()
        a = mon.assess(_make_stats())
        check = mon.to_risk_check_result(a)
        assert check.passed is True
        assert check.severity == "info"
        assert check.rule_name == "operational_risk_monitor"

    def test_warning_not_passed(self):
        mon = OperationalRiskMonitor()
        a = mon.assess(_make_stats(failure_rate=0.08))
        check = mon.to_risk_check_result(a)
        assert check.passed is False
        assert check.severity == "warning"

    def test_halt_not_passed(self):
        mon = OperationalRiskMonitor()
        a = mon.assess(_make_stats(failure_rate=0.15))
        check = mon.to_risk_check_result(a)
        assert check.passed is False
        assert check.severity == "HALT"

    def test_actual_value_is_failure_rate(self):
        mon = OperationalRiskMonitor()
        a = mon.assess(_make_stats(failure_rate=0.08))
        check = mon.to_risk_check_result(a)
        assert check.actual_value == Decimal("0.08")

    def test_limit_value_is_threshold(self):
        mon = OperationalRiskMonitor()
        a = mon.assess(_make_stats())
        check = mon.to_risk_check_result(a)
        assert check.limit_value == Decimal(str(DEFAULT_FAILURE_RATE_THRESHOLD))


# ── 自定义阈值 ───────────────────────────────────────────────────────


class TestCustomThresholds:
    def test_custom_failure_rate_threshold(self):
        """自定义高阈值 → 更难突破。"""
        mon = OperationalRiskMonitor(failure_rate_threshold=0.20)
        a = mon.assess(_make_stats(failure_rate=0.08))
        assert a.failure_rate_breached is False
        assert a.overall_severity == "info"

    def test_custom_latency_threshold(self):
        mon = OperationalRiskMonitor(latency_p95_threshold_ms=1000.0)
        a = mon.assess(_make_stats(latency_p95_ms=600.0))
        assert a.latency_breached is False
        assert a.overall_severity == "info"

    def test_default_thresholds(self):
        assert DEFAULT_FAILURE_RATE_THRESHOLD == 0.05
        assert DEFAULT_LATENCY_P95_THRESHOLD_MS == 500.0


# ── 异常输入 ─────────────────────────────────────────────────────────


class TestInvalidInput:
    def test_none_stats_raises(self):
        mon = OperationalRiskMonitor()
        with pytest.raises(InvalidOperationalRiskInputError):
            mon.assess(None)


# ── 幂等键 + frozen ─────────────────────────────────────────────────


class TestIdempotencyKey:
    def test_unique_keys(self):
        mon = OperationalRiskMonitor()
        a1 = mon.assess(_make_stats())
        a2 = mon.assess(_make_stats())
        assert a1.idempotency_key != a2.idempotency_key
        assert a1.idempotency_key.startswith("oprisk-")

    def test_frozen_assessment(self):
        mon = OperationalRiskMonitor()
        a = mon.assess(_make_stats())
        with pytest.raises(Exception):
            a.overall_severity = "HALT"  # type: ignore[misc]

    def test_stats_preserved(self):
        """assess 不修改原始 stats（薄包装）。"""
        mon = OperationalRiskMonitor()
        stats = _make_stats(failure_rate=0.08)
        original_failure = stats.failure_rate
        a = mon.assess(stats)
        assert a.stats is stats
        assert a.stats.failure_rate == original_failure
