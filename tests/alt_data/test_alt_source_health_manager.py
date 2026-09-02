# [BLUEPRINT] MOD-ALT-011 | docs/03_modules/_domain_alt_data/alt_source_health_manager/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-ALT-011 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.alt_data.test_alt_source_health_manager
# [TESTS] src/zephyr/alt_data/alt_source_health_manager.py
"""MOD-ALT-011 单元测试：alt_source_health_manager 另类数据源健康度管理器。

蓝图验收（B14-04617/CAND-TESTA-019，A9 D-ALT-DATA-31）：
成功率/新鲜度/延迟滑动窗口评分（权重可配）+ 降级阶梯状态机（单次至多降一级）
+ 半开恢复试探（连续成功回 NORMAL，失败回退原态）+ 状态迁移告警回调。
时钟/告警全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.alt_data.alt_source_health_manager",
    reason="alt_source_health_manager not importable",
)

from zephyr.alt_data.alt_source_health_manager import (  # noqa: E402
    AltSourceHealthError,
    AltSourceHealthManager,
    HealthAlert,
    HealthState,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)
_DATA_TS = _T0 - datetime.timedelta(seconds=10)  # 新鲜样本

_SOURCES = ("rss_news", "cninfo_rss")


def _manager(alerts: list | None = None, **kwargs) -> AltSourceHealthManager:
    return AltSourceHealthManager(
        source_ids=_SOURCES,
        clock=lambda: _T0,
        alert_sink=(lambda a: alerts.append(a)) if alerts is not None else None,
        **kwargs,
    )


def _fill_good(mgr: AltSourceHealthManager, source_id: str = "rss_news", n: int = 5) -> None:
    for _ in range(n):
        mgr.record_sample(source_id, success=True, latency_seconds=0.5, data_ts=_DATA_TS)


def _fill_bad(mgr: AltSourceHealthManager, source_id: str = "rss_news", n: int = 5) -> None:
    stale = _T0 - datetime.timedelta(seconds=3600)
    for _ in range(n):
        mgr.record_sample(source_id, success=False, latency_seconds=60.0, data_ts=stale)


# ──────────────────────────────────────────────────────────────────────────────
# 构造期 Fail-Closed
# ──────────────────────────────────────────────────────────────────────────────


class TestConfig:
    def test_empty_sources_raises(self) -> None:
        with pytest.raises(AltSourceHealthError):
            AltSourceHealthManager(source_ids=(), clock=lambda: _T0)

    def test_blank_source_id_raises(self) -> None:
        with pytest.raises(AltSourceHealthError):
            AltSourceHealthManager(source_ids=(" ",), clock=lambda: _T0)

    def test_duplicate_source_id_raises(self) -> None:
        with pytest.raises(AltSourceHealthError):
            AltSourceHealthManager(source_ids=("a", "a"), clock=lambda: _T0)

    def test_weights_sum_invalid_raises(self) -> None:
        with pytest.raises(AltSourceHealthError):
            _manager(weights={"success": 0.5, "freshness": 0.3, "latency": 0.3})

    def test_weights_key_invalid_raises(self) -> None:
        with pytest.raises(AltSourceHealthError):
            _manager(weights={"success": 0.5, "freshness": 0.5})

    def test_thresholds_unordered_raises(self) -> None:
        with pytest.raises(AltSourceHealthError):
            _manager(downweight_threshold=0.5, failover_threshold=0.8)

    def test_window_size_nonpositive_raises(self) -> None:
        with pytest.raises(AltSourceHealthError):
            _manager(window_size=0)

    def test_probe_needed_nonpositive_raises(self) -> None:
        with pytest.raises(AltSourceHealthError):
            _manager(probe_successes_needed=0)


# ──────────────────────────────────────────────────────────────────────────────
# 样本登记
# ──────────────────────────────────────────────────────────────────────────────


class TestRecordSample:
    def test_unknown_source_raises(self) -> None:
        mgr = _manager()
        with pytest.raises(AltSourceHealthError):
            mgr.record_sample("ghost", success=True, latency_seconds=0.1, data_ts=_DATA_TS)

    def test_negative_latency_raises(self) -> None:
        mgr = _manager()
        with pytest.raises(AltSourceHealthError):
            mgr.record_sample("rss_news", success=True, latency_seconds=-0.1, data_ts=_DATA_TS)

    def test_future_data_ts_raises(self) -> None:
        mgr = _manager()
        future = _T0 + datetime.timedelta(seconds=1)
        with pytest.raises(AltSourceHealthError):
            mgr.record_sample("rss_news", success=True, latency_seconds=0.1, data_ts=future)

    def test_sliding_window_evicts_oldest(self) -> None:
        mgr = _manager(window_size=3)
        for i in range(3):
            mgr.record_sample("rss_news", success=True, latency_seconds=0.1, data_ts=_DATA_TS)
        mgr.record_sample("rss_news", success=False, latency_seconds=0.1, data_ts=_DATA_TS)
        mgr.record_sample("rss_news", success=False, latency_seconds=0.1, data_ts=_DATA_TS)
        report = mgr.health_of("rss_news")
        # 窗口仅留 3 条（含 2 条失败）
        assert report.success_rate == pytest.approx(1 / 3)


# ──────────────────────────────────────────────────────────────────────────────
# 评分三分量
# ──────────────────────────────────────────────────────────────────────────────


class TestScoring:
    def test_perfect_score(self) -> None:
        mgr = _manager()
        _fill_good(mgr)
        report = mgr.health_of("rss_news")
        assert report.success_rate == 1.0
        assert report.freshness == pytest.approx(1.0 - 10 / 3600)
        assert report.latency_score == pytest.approx(1.0 - 0.5 / 10)
        assert 0.0 < report.score <= 1.0

    def test_zero_score_components(self) -> None:
        mgr = _manager()
        _fill_bad(mgr)
        report = mgr.health_of("rss_news")
        assert report.success_rate == 0.0
        assert report.freshness == 0.0
        assert report.latency_score == 0.0
        assert report.score == 0.0

    def test_custom_weights_applied(self) -> None:
        mgr = _manager(weights={"success": 1.0, "freshness": 0.0, "latency": 0.0})
        _fill_good(mgr, n=3)
        mgr.record_sample(
            "rss_news", success=False, latency_seconds=9.9, data_ts=_T0 - datetime.timedelta(seconds=3500)
        )
        report = mgr.health_of("rss_news")
        assert report.score == pytest.approx(0.75)  # 仅成功率分量

    def test_score_empty_window_raises(self) -> None:
        mgr = _manager()
        with pytest.raises(AltSourceHealthError):
            mgr.health_of("rss_news")


# ──────────────────────────────────────────────────────────────────────────────
# 降级阶梯状态机
# ──────────────────────────────────────────────────────────────────────────────


class TestDegradeLadder:
    def test_good_health_stays_normal(self) -> None:
        mgr = _manager()
        _fill_good(mgr)
        report = mgr.evaluate("rss_news")
        assert report.state is HealthState.NORMAL

    def test_degrade_one_step_per_evaluate(self) -> None:
        alerts: list[HealthAlert] = []
        mgr = _manager(alerts)
        _fill_bad(mgr)  # score=0 → 目标 DISABLED，但单次仅降一级
        r1 = mgr.evaluate("rss_news")
        assert r1.state is HealthState.DOWNWEIGHTED
        r2 = mgr.evaluate("rss_news")
        assert r2.state is HealthState.FAILOVER
        r3 = mgr.evaluate("rss_news")
        assert r3.state is HealthState.DISABLED
        r4 = mgr.evaluate("rss_news")
        assert r4.state is HealthState.DISABLED  # 触底
        assert len(alerts) == 3
        assert alerts[0].from_state is HealthState.NORMAL
        assert alerts[0].to_state is HealthState.DOWNWEIGHTED

    def test_no_upgrade_via_evaluate(self) -> None:
        mgr = _manager()
        _fill_bad(mgr)
        mgr.evaluate("rss_news")  # → DOWNWEIGHTED
        mgr2_state = mgr.state_of("rss_news")
        assert mgr2_state is HealthState.DOWNWEIGHTED
        _fill_good(mgr, n=50)  # 窗口转好（window=20 全换好样本）
        report = mgr.evaluate("rss_news")
        assert report.state is HealthState.DOWNWEIGHTED  # 恢复仅经探测

    def test_evaluate_in_half_open_raises(self) -> None:
        mgr = _manager()
        _fill_bad(mgr)
        mgr.evaluate("rss_news")  # → DOWNWEIGHTED
        mgr.probe("rss_news", success=True)  # → HALF_OPEN
        with pytest.raises(AltSourceHealthError):
            mgr.evaluate("rss_news")


# ──────────────────────────────────────────────────────────────────────────────
# 半开恢复试探
# ──────────────────────────────────────────────────────────────────────────────


class TestProbe:
    def _downweighted(self, alerts: list | None = None) -> AltSourceHealthManager:
        mgr = _manager(alerts)
        _fill_bad(mgr)
        mgr.evaluate("rss_news")
        return mgr

    def test_probe_enters_half_open_with_alert(self) -> None:
        alerts: list[HealthAlert] = []
        mgr = self._downweighted(alerts)
        state = mgr.probe("rss_news", success=True)
        assert state is HealthState.HALF_OPEN
        assert alerts[-1].to_state is HealthState.HALF_OPEN

    def test_probe_streak_recovers_to_normal(self) -> None:
        alerts: list[HealthAlert] = []
        mgr = self._downweighted(alerts)
        mgr.probe("rss_news", success=True)
        state = mgr.probe("rss_news", success=True)  # 连续 2 次达标
        assert state is HealthState.NORMAL
        assert alerts[-1].to_state is HealthState.NORMAL

    def test_probe_failure_rolls_back(self) -> None:
        alerts: list[HealthAlert] = []
        mgr = self._downweighted(alerts)
        mgr.probe("rss_news", success=True)
        state = mgr.probe("rss_news", success=False)
        assert state is HealthState.DOWNWEIGHTED  # 回退原态
        assert alerts[-1].to_state is HealthState.DOWNWEIGHTED

    def test_probe_streak_reset_after_failure(self) -> None:
        mgr = self._downweighted()
        mgr.probe("rss_news", success=True)
        mgr.probe("rss_news", success=False)  # 回退 DOWNWEIGHTED
        mgr.probe("rss_news", success=True)  # 重新入 HALF_OPEN，计数清零
        assert mgr.state_of("rss_news") is HealthState.HALF_OPEN
        state = mgr.probe("rss_news", success=True)
        assert state is HealthState.NORMAL

    def test_probe_on_normal_raises(self) -> None:
        mgr = _manager()
        with pytest.raises(AltSourceHealthError):
            mgr.probe("rss_news", success=True)

    def test_probe_unknown_source_raises(self) -> None:
        mgr = _manager()
        with pytest.raises(AltSourceHealthError):
            mgr.probe("ghost", success=True)

    def test_probe_from_disabled_recovers(self) -> None:
        mgr = _manager()
        _fill_bad(mgr)
        for _ in range(3):
            mgr.evaluate("rss_news")  # → DISABLED
        mgr.probe("rss_news", success=True)
        state = mgr.probe("rss_news", success=True)
        assert state is HealthState.NORMAL


# ──────────────────────────────────────────────────────────────────────────────
# 查询 / 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestQuery:
    def test_state_of_unknown_raises(self) -> None:
        mgr = _manager()
        with pytest.raises(AltSourceHealthError):
            mgr.state_of("ghost")

    def test_sources_sorted(self) -> None:
        mgr = _manager()
        assert mgr.sources() == ("cninfo_rss", "rss_news")

    def test_independent_windows(self) -> None:
        mgr = _manager()
        _fill_good(mgr, "rss_news")
        _fill_bad(mgr, "cninfo_rss")
        assert mgr.health_of("rss_news").score > 0.9
        assert mgr.health_of("cninfo_rss").score == 0.0

    def test_determinism_same_input_same_output(self) -> None:
        def run() -> tuple:
            mgr = _manager()
            _fill_good(mgr, n=3)
            mgr.record_sample("rss_news", success=False, latency_seconds=1.0, data_ts=_DATA_TS)
            r = mgr.evaluate("rss_news")
            return (r.state, r.score, r.success_rate, r.freshness, r.latency_score)

        assert run() == run()

    def test_alert_sink_exception_not_blocking(self) -> None:
        def bad_sink(_a: HealthAlert) -> None:
            raise RuntimeError("boom")

        mgr = AltSourceHealthManager(source_ids=_SOURCES, clock=lambda: _T0, alert_sink=bad_sink)
        _fill_bad(mgr)
        report = mgr.evaluate("rss_news")  # 告警异常不阻断降级
        assert report.state is HealthState.DOWNWEIGHTED
