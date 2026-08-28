# [MODULE] tests.zephyr.data.transport.test_cross_border_dual
# [DOMAIN] D_DATA
# [TESTS] src/zephyr/data/transport/cross_border_dual.py
# [TTL] permanent
"""跨境网络双活传输层单测（CAND-CRYPTO-009 / 94号 §7.2）。

覆盖：
- cloudflared tunnel 配置 YAML 生成（tunnel/credentials/ingress/兜底 404）
- 切备三感知纪律：失败+吞吐下降+积压超阈值同时成立才切（任一缺失不切）
- 切回纯时间驱动：未满 60s 不探测、满 60s 探测成功切回、失败保持并顺延
- 积压计数器饱和递减（纪律③：0-1 不下溢）
"""

from __future__ import annotations

import pytest

from zephyr.data.transport import (
    BucketStats,
    CloudflareTunnelSpec,
    CrossBorderDualTransport,
    DualPathConfig,
    TransportPath,
    render_cloudflared_config,
)

_BASELINE = 1_000_000.0


class FakeClock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def _make(probe_result: bool = True) -> tuple[CrossBorderDualTransport, FakeClock, list[bool]]:
    clock = FakeClock()
    probe_calls: list[bool] = []

    def probe() -> bool:
        probe_calls.append(probe_result)
        return probe_result

    cfg = DualPathConfig(baseline_throughput_bps=_BASELINE)
    return CrossBorderDualTransport(cfg, probe=probe, clock=clock), clock, probe_calls


def _trigger_stats() -> BucketStats:
    return BucketStats(connection_failed=True, throughput_bps=100_000.0, backlog=30)


class TestCloudflaredConfig:
    def test_render_contains_tunnel_identity(self) -> None:
        spec = CloudflareTunnelSpec(
            tunnel_id="abcd-1234",
            credentials_file="/etc/cloudflared/abcd-1234.json",
            hostname="edge.example.com",
            service="https://127.0.0.1:8443",
        )
        yml = render_cloudflared_config(spec)
        assert "tunnel: abcd-1234" in yml
        assert "credentials-file: /etc/cloudflared/abcd-1234.json" in yml
        assert "hostname: edge.example.com" in yml
        assert "service: https://127.0.0.1:8443" in yml

    def test_render_fallback_404_and_warp_default_off(self) -> None:
        spec = CloudflareTunnelSpec(
            tunnel_id="t", credentials_file="c", hostname="h", service="s"
        )
        yml = render_cloudflared_config(spec)
        # ingress 兜底规则（cloudflared 强制要求最后一条为兜底）
        assert yml.rstrip().endswith("- service: http_status:404")
        assert "enabled: false" in yml

    def test_render_warp_on(self) -> None:
        spec = CloudflareTunnelSpec(
            tunnel_id="t", credentials_file="c", hostname="h", service="s", warp_routing=True
        )
        assert "enabled: true" in render_cloudflared_config(spec)


class TestSwitchToBackup:
    def test_all_three_signals_switch(self) -> None:
        dual, _, _ = _make()
        event = dual.record_bucket(_trigger_stats())
        assert event is not None
        assert event.from_path is TransportPath.PRIMARY
        assert event.to_path is TransportPath.BACKUP
        assert dual.active_path is TransportPath.BACKUP

    @pytest.mark.parametrize(
        "stats",
        [
            # 仅连接失败
            BucketStats(connection_failed=True, throughput_bps=_BASELINE, backlog=0),
            # 仅吞吐下降
            BucketStats(connection_failed=False, throughput_bps=100_000.0, backlog=0),
            # 仅积压超阈值
            BucketStats(connection_failed=False, throughput_bps=_BASELINE, backlog=30),
            # 失败+吞吐下降但积压未超阈值
            BucketStats(connection_failed=True, throughput_bps=100_000.0, backlog=24),
            # 失败+积压但吞吐未降
            BucketStats(connection_failed=True, throughput_bps=_BASELINE, backlog=30),
            # 吞吐下降+积压但连接未失败
            BucketStats(connection_failed=False, throughput_bps=100_000.0, backlog=30),
        ],
    )
    def test_partial_signals_no_switch(self, stats: BucketStats) -> None:
        dual, _, _ = _make()
        assert dual.record_bucket(stats) is None
        assert dual.active_path is TransportPath.PRIMARY

    def test_backlog_threshold_boundary(self) -> None:
        dual, _, _ = _make()
        # 积压=阈值（24）不触发——需严格大于
        assert (
            dual.record_bucket(
                BucketStats(connection_failed=True, throughput_bps=100_000.0, backlog=24)
            )
            is None
        )
        assert (
            dual.record_bucket(
                BucketStats(connection_failed=True, throughput_bps=100_000.0, backlog=25)
            )
            is not None
        )

    def test_throughput_boundary(self) -> None:
        dual, _, _ = _make()
        # 吞吐=基线×0.5 不判定下降（严格小于）
        assert (
            dual.record_bucket(
                BucketStats(connection_failed=True, throughput_bps=500_000.0, backlog=30)
            )
            is None
        )

    def test_no_double_switch_on_backup(self) -> None:
        dual, _, _ = _make()
        assert dual.record_bucket(_trigger_stats()) is not None
        # 备线路期继续喂桶不再产生切换事件
        assert dual.record_bucket(_trigger_stats()) is None
        assert len(dual.events) == 1


class TestProbeSwitchBack:
    def _on_backup(self) -> tuple[CrossBorderDualTransport, FakeClock, list[bool]]:
        dual, clock, calls = _make(probe_result=True)
        dual.record_bucket(_trigger_stats())
        assert dual.active_path is TransportPath.BACKUP
        return dual, clock, calls

    def test_no_probe_before_interval(self) -> None:
        dual, clock, calls = self._on_backup()
        clock.advance(59.9)
        assert dual.maybe_probe_primary() is None
        assert calls == []  # 纯时间驱动：未满 60s 不发起探测
        assert dual.active_path is TransportPath.BACKUP

    def test_probe_success_switches_back(self) -> None:
        dual, clock, calls = self._on_backup()
        clock.advance(60.0)
        event = dual.maybe_probe_primary()
        assert event is not None
        assert event.from_path is TransportPath.BACKUP
        assert event.to_path is TransportPath.PRIMARY
        assert dual.active_path is TransportPath.PRIMARY
        assert len(calls) == 1

    def test_probe_backlog_nonzero_still_switches_back(self) -> None:
        # 纪律②：切回不依赖"积压=0"静态条件——发送中积压恒非零也可切回
        dual, clock, _ = self._on_backup()
        dual.add_backlog(7)
        clock.advance(60.0)
        assert dual.maybe_probe_primary() is not None
        assert dual.active_path is TransportPath.PRIMARY

    def test_probe_failure_stays_and_defers_next_probe(self) -> None:
        dual, clock, calls = _make(probe_result=False)
        dual.record_bucket(_trigger_stats())
        clock.advance(60.0)
        assert dual.maybe_probe_primary() is None
        assert dual.active_path is TransportPath.BACKUP
        assert len(calls) == 1
        # 失败顺延：再 30s 不发起新探测，满下一周期才再探
        clock.advance(30.0)
        assert dual.maybe_probe_primary() is None
        assert len(calls) == 1
        clock.advance(30.0)
        assert dual.maybe_probe_primary() is None
        assert len(calls) == 2

    def test_probe_exception_stays_on_backup(self) -> None:
        clock = FakeClock()

        def bad_probe() -> bool:
            raise ConnectionError("primary unreachable")

        dual = CrossBorderDualTransport(
            DualPathConfig(baseline_throughput_bps=_BASELINE), probe=bad_probe, clock=clock
        )
        dual.record_bucket(_trigger_stats())
        clock.advance(60.0)
        assert dual.maybe_probe_primary() is None
        assert dual.active_path is TransportPath.BACKUP

    def test_probe_noop_on_primary(self) -> None:
        dual, _, calls = _make()
        assert dual.maybe_probe_primary() is None
        assert calls == []


class TestBacklogSaturation:
    def test_saturating_decrement_no_underflow(self) -> None:
        # 纪律③：0-1 不得下溢为天文数字（外部实战 2^64 误判事故）
        dual, _, _ = _make()
        assert dual.decr_backlog(1) == 0
        assert dual.backlog == 0

    def test_add_then_decr(self) -> None:
        dual, _, _ = _make()
        dual.add_backlog(10)
        assert dual.decr_backlog(4) == 6
        assert dual.decr_backlog(100) == 0

    def test_negative_decr_ignored(self) -> None:
        dual, _, _ = _make()
        dual.add_backlog(5)
        assert dual.decr_backlog(-3) == 5

    def test_record_bucket_syncs_backlog_saturated(self) -> None:
        dual, _, _ = _make()
        dual.add_backlog(9)
        dual.record_bucket(BucketStats(connection_failed=False, throughput_bps=_BASELINE, backlog=-5))
        assert dual.backlog == 0
