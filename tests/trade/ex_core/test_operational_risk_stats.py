"""OperationalRiskStats 单元测试 — MOD-EX-003 操作风险聚合层（G6 / BM-RC-08-E）

覆盖: 失败率聚合(ORDER_REJECTED/ORDER_SUBMITTED) + 成交延迟配对 + 边界(零提交/全拒/无成交/时钟偏移/周期过滤)
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from zephyr.ex_core.audit_journal.auditor import (
    AuditSource,
    ExecutionAuditEventType,
    ExecutionAuditLogger,
    OperationalRiskStats,
)

# ──────────────────────────────────────────────────────────────────────────────
# fixtures
# ──────────────────────────────────────────────────────────────────────────────

BASE = datetime(2026, 8, 5, 9, 30, tzinfo=UTC)
PERIOD_START = BASE - timedelta(minutes=1)
PERIOD_END = BASE + timedelta(hours=2)


def _log_submitted(audit: ExecutionAuditLogger, order_id: str, ts: datetime) -> None:
    audit.log(
        ExecutionAuditEventType.ORDER_SUBMITTED,
        order_id,
        "600000.SH",
        AuditSource.SIMULATION,
        {"qty": 100},
        timestamp=ts,
    )


def _log_rejected(audit: ExecutionAuditLogger, order_id: str, ts: datetime) -> None:
    audit.log(
        ExecutionAuditEventType.ORDER_REJECTED,
        order_id,
        "600000.SH",
        AuditSource.SIMULATION,
        {"reason": "RISK_REJECT"},
        timestamp=ts,
    )


def _log_filled(audit: ExecutionAuditLogger, order_id: str, ts: datetime) -> None:
    audit.log(
        ExecutionAuditEventType.ORDER_FILLED,
        order_id,
        "600000.SH",
        AuditSource.SIMULATION,
        {"fill_price": "10.52", "filled_qty": 100},
        timestamp=ts,
    )


@pytest.fixture
def audit() -> ExecutionAuditLogger:
    return ExecutionAuditLogger()


# ──────────────────────────────────────────────────────────────────────────────
# 失败率聚合（用户明确要求验证 ORDER_REJECTED 失败率）
# ──────────────────────────────────────────────────────────────────────────────


class TestFailureRate:
    """失败率 = ORDER_REJECTED / ORDER_SUBMITTED。"""

    def test_failure_rate_basic(self, audit: ExecutionAuditLogger):
        """10 提交 / 3 拒绝 → 失败率 0.3。"""
        for i in range(10):
            _log_submitted(audit, f"ord-{i}", BASE + timedelta(seconds=i))
        for i in range(3):
            _log_rejected(audit, f"ord-rej-{i}", BASE + timedelta(seconds=100 + i))

        stats = audit.compute_operational_risk_stats(PERIOD_START, PERIOD_END)

        assert stats.submission_count == 10
        assert stats.rejection_count == 3
        assert stats.failure_rate == pytest.approx(0.3)

    def test_failure_rate_zero_submissions_no_div_by_zero(self, audit: ExecutionAuditLogger):
        """零提交 + 若干拒绝 → 失败率 0.0（不除零）。"""
        for i in range(3):
            _log_rejected(audit, f"ord-rej-{i}", BASE + timedelta(seconds=i))

        stats = audit.compute_operational_risk_stats(PERIOD_START, PERIOD_END)

        assert stats.submission_count == 0
        assert stats.rejection_count == 3
        assert stats.failure_rate == 0.0  # 不抛 ZeroDivisionError

    def test_failure_rate_all_rejected(self, audit: ExecutionAuditLogger):
        """5 提交 + 5 拒绝 → 失败率 1.0。"""
        for i in range(5):
            _log_submitted(audit, f"ord-{i}", BASE + timedelta(seconds=i))
            _log_rejected(audit, f"ord-{i}", BASE + timedelta(seconds=100 + i))

        stats = audit.compute_operational_risk_stats(PERIOD_START, PERIOD_END)

        assert stats.submission_count == 5
        assert stats.rejection_count == 5
        assert stats.failure_rate == pytest.approx(1.0)

    def test_failure_rate_none_rejected(self, audit: ExecutionAuditLogger):
        """4 提交 + 0 拒绝 → 失败率 0.0。"""
        for i in range(4):
            _log_submitted(audit, f"ord-{i}", BASE + timedelta(seconds=i))

        stats = audit.compute_operational_risk_stats(PERIOD_START, PERIOD_END)

        assert stats.submission_count == 4
        assert stats.rejection_count == 0
        assert stats.failure_rate == 0.0

    def test_failure_rate_resubmits_count_each_submission(self, audit: ExecutionAuditLogger):
        """同一订单多次 SUBMITTED 各计一次（分母=提交次数，非订单数）。"""
        _log_submitted(audit, "ord-1", BASE)
        _log_submitted(audit, "ord-1", BASE + timedelta(seconds=1))  # 重提
        _log_submitted(audit, "ord-2", BASE + timedelta(seconds=2))
        _log_rejected(audit, "ord-1", BASE + timedelta(seconds=3))

        stats = audit.compute_operational_risk_stats(PERIOD_START, PERIOD_END)

        assert stats.submission_count == 3
        assert stats.rejection_count == 1
        assert stats.failure_rate == pytest.approx(1 / 3)


# ──────────────────────────────────────────────────────────────────────────────
# 成交延迟配对
# ──────────────────────────────────────────────────────────────────────────────


class TestLatency:
    """延迟 = SUBMITTED → FILLED 时间差（ms），按 order_id 配对首条。"""

    def test_latency_single_pair(self, audit: ExecutionAuditLogger):
        """提交后 500ms 成交 → latency 500ms。"""
        sub_ts = BASE
        fill_ts = BASE + timedelta(milliseconds=500)
        _log_submitted(audit, "ord-1", sub_ts)
        _log_filled(audit, "ord-1", fill_ts)

        stats = audit.compute_operational_risk_stats(PERIOD_START, PERIOD_END)

        assert stats.latency_count == 1
        assert stats.latency_mean_ms == pytest.approx(500.0)
        assert stats.latency_max_ms == pytest.approx(500.0)
        assert stats.latency_p50_ms == pytest.approx(500.0)
        assert stats.latency_p95_ms == pytest.approx(500.0)

    def test_latency_multiple_pairs_percentiles(self, audit: ExecutionAuditLogger):
        """3 单: 100ms / 200ms / 300ms → max=300, mean=200。"""
        deltas = [100, 200, 300]
        for i, d in enumerate(deltas):
            _log_submitted(audit, f"ord-{i}", BASE + timedelta(seconds=i))
            _log_filled(audit, f"ord-{i}", BASE + timedelta(seconds=i, milliseconds=d))

        stats = audit.compute_operational_risk_stats(PERIOD_START, PERIOD_END)

        assert stats.latency_count == 3
        assert stats.latency_max_ms == pytest.approx(300.0)
        assert stats.latency_mean_ms == pytest.approx(200.0)
        # nearest-rank p50 of [100,200,300]: ceil(0.5*3)-1 = index 1 → 200
        assert stats.latency_p50_ms == pytest.approx(200.0)

    def test_latency_no_fills(self, audit: ExecutionAuditLogger):
        """仅提交无成交 → latency_count=0，延迟统计为 0.0。"""
        _log_submitted(audit, "ord-1", BASE)

        stats = audit.compute_operational_risk_stats(PERIOD_START, PERIOD_END)

        assert stats.latency_count == 0
        assert stats.latency_mean_ms == 0.0
        assert stats.latency_max_ms == 0.0
        assert stats.latency_p50_ms == 0.0

    def test_latency_skips_clock_skew(self, audit: ExecutionAuditLogger):
        """FILLED 早于 SUBMITTED（时钟偏移）→ 跳过该配对。"""
        _log_submitted(audit, "ord-1", BASE + timedelta(milliseconds=500))
        _log_filled(audit, "ord-1", BASE)  # 早于 submitted

        stats = audit.compute_operational_risk_stats(PERIOD_START, PERIOD_END)

        assert stats.latency_count == 0
        # filled_count 仍计 1（计数与配对解耦）
        assert stats.filled_count == 1

    def test_latency_uses_first_pair_per_order(self, audit: ExecutionAuditLogger):
        """同订单多次 SUBMITTED/FILLED → 取各自首条配对。"""
        _log_submitted(audit, "ord-1", BASE)
        _log_submitted(audit, "ord-1", BASE + timedelta(seconds=10))  # 重提（晚）
        _log_filled(audit, "ord-1", BASE + timedelta(milliseconds=200))  # 首次成交

        stats = audit.compute_operational_risk_stats(PERIOD_START, PERIOD_END)

        # 首条 SUBMITTED@BASE → 首条 FILLED@+200ms → 200ms
        assert stats.latency_count == 1
        assert stats.latency_mean_ms == pytest.approx(200.0)


# ──────────────────────────────────────────────────────────────────────────────
# 周期过滤 + 整体
# ──────────────────────────────────────────────────────────────────────────────


class TestPeriodFilter:
    """compute_operational_risk_stats 只统计周期内记录。"""

    def test_period_excludes_out_of_window(self, audit: ExecutionAuditLogger):
        """周期外的提交/拒绝不计入。"""
        # 周期内: 3 提交 1 拒绝
        for i in range(3):
            _log_submitted(audit, f"in-{i}", BASE + timedelta(seconds=i))
        _log_rejected(audit, "in-rej", BASE + timedelta(seconds=50))
        # 周期外（早于 PERIOD_START）: 5 提交 5 拒绝
        far_past = PERIOD_START - timedelta(hours=1)
        for i in range(5):
            _log_submitted(audit, f"out-{i}", far_past + timedelta(seconds=i))
            _log_rejected(audit, f"out-{i}", far_past + timedelta(seconds=100 + i))

        stats = audit.compute_operational_risk_stats(PERIOD_START, PERIOD_END)

        assert stats.submission_count == 3
        assert stats.rejection_count == 1
        assert stats.failure_rate == pytest.approx(1 / 3)

    def test_empty_audit_returns_zeros(self, audit: ExecutionAuditLogger):
        """空审计器 → 全零统计，不抛异常。"""
        stats = audit.compute_operational_risk_stats(PERIOD_START, PERIOD_END)

        assert isinstance(stats, OperationalRiskStats)
        assert stats.submission_count == 0
        assert stats.rejection_count == 0
        assert stats.filled_count == 0
        assert stats.failure_rate == 0.0
        assert stats.fill_rate == 0.0
        assert stats.latency_count == 0

    def test_fill_rate_companion(self, audit: ExecutionAuditLogger):
        """成交率 = filled/submitted。"""
        for i in range(4):
            _log_submitted(audit, f"ord-{i}", BASE + timedelta(seconds=i))
        # 2 笔成交
        _log_filled(audit, "ord-0", BASE + timedelta(milliseconds=100))
        _log_filled(audit, "ord-1", BASE + timedelta(milliseconds=200))

        stats = audit.compute_operational_risk_stats(PERIOD_START, PERIOD_END)

        assert stats.filled_count == 2
        assert stats.fill_rate == pytest.approx(0.5)
