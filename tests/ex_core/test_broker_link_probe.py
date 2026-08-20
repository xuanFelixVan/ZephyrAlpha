# [BLUEPRINT] MOD-L06-002 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] tests.ex_core.test_broker_link_probe
# [DOMAIN] D_EX_CORE
# [INVARIANTS] 注入式零真实连接; 探活失败不抛; 只读观测; 时钟注入确定性
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidProbeInputError
# [TESTS] self
# [TTL] permanent
"""miniQMT 下单链路探针测试（55 号 §3.2 缺口，AI-NIGHT-001 包P）。"""

from __future__ import annotations

import pytest

from zephyr.ex_core.broker_link_probe import (
    BrokerLinkProbe,
    InvalidProbeInputError,
    LinkHealth,
)


class _FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class TestConfig:
    def test_invalid_thresholds_rejected(self):
        with pytest.raises(InvalidProbeInputError):
            BrokerLinkProbe(warn_latency_ms=0)
        with pytest.raises(InvalidProbeInputError):
            BrokerLinkProbe(warn_latency_ms=2000, crit_latency_ms=500)  # warn > crit
        with pytest.raises(InvalidProbeInputError):
            BrokerLinkProbe(max_consecutive_failures=0)


class TestConnectionProbe:
    def test_connected_with_rtt(self):
        probe = BrokerLinkProbe()
        result = probe.probe_connection(lambda: 0.012)  # 12ms RTT
        assert result.connected is True
        assert result.rtt_ms == pytest.approx(12.0)
        assert probe.snapshot().health is LinkHealth.HEALTHY

    def test_exception_counts_failure_no_raise(self):
        probe = BrokerLinkProbe(max_consecutive_failures=3)

        def _boom():
            raise ConnectionError("miniQMT offline")

        for _ in range(2):
            result = probe.probe_connection(_boom)
            assert result.connected is False
            assert probe.snapshot().health is LinkHealth.DEGRADED
        probe.probe_connection(_boom)
        snap = probe.snapshot()
        assert snap.health is LinkHealth.DOWN
        assert snap.consecutive_connect_failures == 3

    def test_false_return_counts_failure(self):
        probe = BrokerLinkProbe()
        assert probe.probe_connection(lambda: False).connected is False
        assert probe.snapshot().consecutive_connect_failures == 1

    def test_success_resets_failure_streak(self):
        probe = BrokerLinkProbe(max_consecutive_failures=3)
        probe.probe_connection(lambda: (_ for _ in ()).throw(ConnectionError()))
        probe.probe_connection(lambda: (_ for _ in ()).throw(ConnectionError()))
        assert probe.snapshot().consecutive_connect_failures == 2
        probe.probe_connection(lambda: 0.01)
        assert probe.snapshot().consecutive_connect_failures == 0


class TestOrderLatency:
    def test_measures_submission_latency(self):
        clock = _FakeClock()
        probe = BrokerLinkProbe(clock=clock)

        def _submit():
            clock.advance(0.25)  # 250ms
            return "broker-order-1"

        result = probe.time_order_submission(_submit)
        assert result == "broker-order-1"  # 透传返回值
        snap = probe.snapshot()
        assert snap.order_samples == 1
        assert snap.order_latency_avg_ms == pytest.approx(250.0)
        assert snap.order_latency_max_ms == pytest.approx(250.0)

    def test_exception_still_records_and_reraises(self):
        clock = _FakeClock()
        probe = BrokerLinkProbe(clock=clock)

        def _submit():
            clock.advance(0.1)
            raise RuntimeError("submit failed")

        with pytest.raises(RuntimeError):
            probe.time_order_submission(_submit)
        assert probe.snapshot().order_samples == 1  # 异常也落样本（真实延迟证据）

    def test_crit_latency_degrades(self):
        clock = _FakeClock()
        probe = BrokerLinkProbe(warn_latency_ms=100, crit_latency_ms=500, clock=clock)
        probe.time_order_submission(lambda: clock.advance(0.6))  # 600ms ≥ crit
        assert probe.snapshot().health is LinkHealth.DEGRADED


class TestFillReportLatency:
    def test_records_report_latency(self):
        probe = BrokerLinkProbe()
        latency = probe.record_fill_report_latency(submit_ts=100.0, fill_report_ts=100.35)
        assert latency == pytest.approx(350.0)
        snap = probe.snapshot()
        assert snap.fill_report_samples == 1
        assert snap.fill_report_latency_max_ms == pytest.approx(350.0)

    def test_inverted_timestamps_rejected(self):
        probe = BrokerLinkProbe()
        with pytest.raises(InvalidProbeInputError):
            probe.record_fill_report_latency(submit_ts=100.0, fill_report_ts=99.9)

    def test_sample_bound_evicts_oldest(self):
        probe = BrokerLinkProbe(max_samples=3)
        for i in range(5):
            probe.record_fill_report_latency(submit_ts=0.0, fill_report_ts=(i + 1) * 0.01)
        snap = probe.snapshot()
        assert snap.fill_report_samples == 3
        assert snap.fill_report_latency_max_ms == pytest.approx(50.0)


class TestHealthDerivation:
    def test_healthy_when_all_fine(self):
        clock = _FakeClock()
        probe = BrokerLinkProbe(warn_latency_ms=100, crit_latency_ms=500, clock=clock)
        probe.probe_connection(lambda: 0.01)
        probe.time_order_submission(lambda: clock.advance(0.05))  # 50ms < warn
        assert probe.snapshot().health is LinkHealth.HEALTHY

    def test_degraded_on_warn_latency(self):
        clock = _FakeClock()
        probe = BrokerLinkProbe(warn_latency_ms=100, crit_latency_ms=500, clock=clock)
        probe.time_order_submission(lambda: clock.advance(0.2))  # 200ms ≥ warn
        assert probe.snapshot().health is LinkHealth.DEGRADED
