# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [TTL] permanent
"""per-source 自动熔断器测试（64号 Q17）。

测试内容（注入假时钟，不依赖真实时间）：
- CLOSED 正常放行 / 连续失败达阈值跳闸 / 成功复位连续计数
- OPEN 冷却期拒绝 / 冷却到点半开放行单探针 / 探针在飞拒绝并发
- HALF_OPEN 探针成功→CLOSED / 探针失败→再 OPEN 重计冷却 / 探针超时补探
- 滑窗错误率跳闸（最小样本量保护）
- on_trip 回调 / Registry per-source 隔离与快照
- scheduler 集成：熔断中的源 run_task 直接跳过不调 provider

设计文档：64_data_source_download_spec.md §16.2 Q17
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from zephyr.data.provider_base import FetchResult, IngestProviderBase, IngestProviderMeta
from zephyr.data.scheduler import IntegratorScheduler
from zephyr.data.source_circuit_breaker import (
    CircuitBreakerRegistry,
    CircuitState,
    SourceCircuitBreaker,
)


class _Clock:
    """可推进的假时钟。"""

    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


@pytest.fixture
def clock():
    return _Clock()


@pytest.fixture
def breaker(clock):
    return SourceCircuitBreaker(
        "akshare",
        failure_threshold=3,
        cooldown_seconds=600.0,
        window_size=10,
        error_rate_threshold=0.6,
        min_samples=5,
        clock=clock,
    )


class TestClosedState:
    def test_initial_closed_allows(self, breaker):
        assert breaker.state is CircuitState.CLOSED
        assert breaker.allow_request() is True

    def test_failures_below_threshold_stay_closed(self, breaker):
        breaker.record_failure()
        breaker.record_failure()
        assert breaker.state is CircuitState.CLOSED
        assert breaker.allow_request() is True

    def test_success_resets_consecutive_counter(self, clock):
        # min_samples=99 隔离滑窗错误率路径，只验证连续计数复位
        b = SourceCircuitBreaker(
            "s",
            failure_threshold=3,
            cooldown_seconds=600.0,
            window_size=10,
            error_rate_threshold=0.6,
            min_samples=99,
            clock=clock,
        )
        b.record_failure()
        b.record_failure()
        b.record_success()
        b.record_failure()
        b.record_failure()
        assert b.state is CircuitState.CLOSED  # 未达连续 3 次


class TestTripOnConsecutiveFailures:
    def test_trip_at_threshold(self, breaker):
        for _ in range(3):
            breaker.record_failure()
        assert breaker.state is CircuitState.OPEN
        assert breaker.allow_request() is False

    def test_deny_during_cooldown(self, breaker, clock):
        for _ in range(3):
            breaker.record_failure()
        clock.advance(599.0)
        assert breaker.allow_request() is False
        assert breaker.state is CircuitState.OPEN

    def test_half_open_after_cooldown(self, breaker, clock):
        for _ in range(3):
            breaker.record_failure()
        clock.advance(600.0)
        assert breaker.allow_request() is True  # 放行探针
        assert breaker.state is CircuitState.HALF_OPEN

    def test_second_request_denied_while_probe_in_flight(self, breaker, clock):
        for _ in range(3):
            breaker.record_failure()
        clock.advance(600.0)
        assert breaker.allow_request() is True  # 探针放行
        assert breaker.allow_request() is False  # 探针在飞，并发拒绝

    def test_probe_success_closes(self, breaker, clock):
        for _ in range(3):
            breaker.record_failure()
        clock.advance(600.0)
        breaker.allow_request()
        breaker.record_success()
        assert breaker.state is CircuitState.CLOSED
        assert breaker.allow_request() is True

    def test_probe_failure_reopens_with_new_cooldown(self, breaker, clock):
        for _ in range(3):
            breaker.record_failure()
        clock.advance(600.0)
        breaker.allow_request()
        breaker.record_failure()
        assert breaker.state is CircuitState.OPEN
        clock.advance(599.0)
        assert breaker.allow_request() is False  # 新冷却重计
        clock.advance(1.0)
        assert breaker.allow_request() is True

    def test_probe_timeout_allows_reprobe(self, breaker, clock):
        """探针在飞但超时（进程异常未回报结果）→允许补探，防永久卡死。"""
        for _ in range(3):
            breaker.record_failure()
        clock.advance(600.0)
        assert breaker.allow_request() is True  # 探针 1
        clock.advance(600.0)  # 探针 1 超时（≥ cooldown）
        assert breaker.allow_request() is True  # 补探放行
        assert breaker.state is CircuitState.HALF_OPEN


class TestErrorRateTrip:
    def test_error_rate_trips_without_consecutive(self, breaker):
        """滑窗 5 样本 3 失败（60%）即使不连续也跳闸。"""
        for ok in (False, True, False, True, False):
            (breaker.record_success if ok else breaker.record_failure)()
        assert breaker.state is CircuitState.OPEN

    def test_min_samples_guard(self, breaker):
        """样本不足 min_samples 时错误率判定不生效（防小样本误判）。"""
        breaker.record_failure()
        breaker.record_failure()  # 2/2=100% 但样本 < 5
        assert breaker.state is CircuitState.CLOSED


class TestOnTripCallback:
    def test_on_trip_fired_with_reason(self, clock):
        trips: list[tuple[str, str]] = []
        b = SourceCircuitBreaker(
            "tushare",
            failure_threshold=2,
            cooldown_seconds=60.0,
            min_samples=99,
            clock=clock,
            on_trip=lambda s, r: trips.append((s, r)),
        )
        b.record_failure()
        assert trips == []
        b.record_failure()
        assert len(trips) == 1
        assert trips[0][0] == "tushare"
        assert "连续失败" in trips[0][1]

    def test_on_trip_exception_swallowed(self, clock):
        def _bad_callback(source, reason):
            raise RuntimeError("callback boom")

        b = SourceCircuitBreaker("x", failure_threshold=1, cooldown_seconds=60.0, clock=clock, on_trip=_bad_callback)
        b.record_failure()  # 回调异常不得影响状态机
        assert b.state is CircuitState.OPEN


class TestRegistry:
    def test_per_source_isolation(self, clock):
        reg = CircuitBreakerRegistry(failure_threshold=2, cooldown_seconds=60.0, clock=clock)
        reg.record_failure("akshare")
        reg.record_failure("akshare")
        assert reg.state("akshare") is CircuitState.OPEN
        assert reg.state("tushare") is CircuitState.CLOSED
        assert reg.allow_request("tushare") is True

    def test_snapshot(self, clock):
        reg = CircuitBreakerRegistry(failure_threshold=1, cooldown_seconds=60.0, clock=clock)
        reg.record_failure("akshare")
        reg.allow_request("tushare")
        snap = reg.snapshot()
        assert snap == {"akshare": "open", "tushare": "closed"}


# ============== scheduler 集成（熔断源跳过，不调 provider）==============


class _MockProvider(IngestProviderBase):
    source_name = "mock"
    meta = IngestProviderMeta(
        name="mock",
        display_name="Mock",
        auth_type="anonymous",
        requires_process=False,
        thread_safety="shared",
        rate_limit_default=0,
    )

    def connect(self):
        self._connected = True

    def health_check(self):
        return self._connected

    def fetch(self, payload, policy):
        yield FetchResult(
            table=payload.table,
            columns=["code"],
            rows=[("000001",)],
            last_key="2026-07-05",
            elapsed_sec=0.1,
            rows_fetched=1,
        )

    def disconnect(self):
        self._connected = False


@pytest.fixture
def scheduler(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "schedule.yaml").write_text(
        'schedules:\n  daily_kline:\n    cron: "30 16 * * 1-5"\n    executor: heavy\n',
        encoding="utf-8",
    )
    (config_dir / "tasks.yaml").write_text(
        "tasks:\n"
        "  - task_id: kline_daily_incremental\n"
        "    table: c1_market.kline_daily\n"
        "    source: mock\n"
        "    schedule: daily_kline\n"
        "    incremental: true\n"
        "    dependencies: []\n"
        "    capability: kline_daily\n"
        "    symbols: null\n",
        encoding="utf-8",
    )
    return IntegratorScheduler(
        config_dir=config_dir,
        progress_db=tmp_path / "progress.db",
        jobs_db="sqlite:///" + str(tmp_path / "jobs.db"),
        startup_probes=False,
    )


class TestSchedulerIntegration:
    def test_tripped_breaker_skips_source(self, scheduler, tmp_path):
        """熔断中的源：run_task 直接失败返回，provider.fetch 不被调用。"""
        scheduler.load_config()
        mock_provider = MagicMock()
        scheduler.providers["mock"] = mock_provider
        # 手动触发熔断（连续失败阈值默认 5 次）
        for _ in range(5):
            scheduler._circuit_breakers.record_failure("mock")
        with patch(
            "zephyr.data.fetch_perf_recorder.record_fetch_perf",
            lambda record, **kw: tmp_path / "fp.jsonl",
        ):
            ok = scheduler.run_task("kline_daily_incremental")
        assert ok is False
        mock_provider.fetch.assert_not_called()

    def test_closed_breaker_records_success(self, scheduler, tmp_path):
        """正常路径：成功后熔断器保持 CLOSED 且 fetch_perf 被被动记录。"""
        scheduler.load_config()
        mock_provider = _MockProvider()
        mock_provider.connect()
        scheduler.providers["mock"] = mock_provider
        recorded: list[dict] = []
        with (
            patch("src.zephyr.data.scheduler.BufferedWriter.add", return_value=True),
            patch("src.zephyr.data.scheduler.BufferedWriter.flush", return_value=True),
            patch(
                "zephyr.data.fetch_perf_recorder.record_fetch_perf",
                lambda record, **kw: recorded.append(dict(record)),
            ),
        ):
            ok = scheduler.run_task("kline_daily_incremental")
        assert ok is True
        assert scheduler._circuit_breakers.state("mock") is CircuitState.CLOSED
        assert len(recorded) == 1
        assert recorded[0]["status"] == "SUCCESS"
        assert recorded[0]["source"] == "mock"
        assert recorded[0]["task_id"] == "kline_daily_incremental"
