# [A_test] module_id: SRC-TST-1670 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_spiral_ews
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_spiral_ews.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_drift.spiral_ews import SpiralEarlyWarningSystem, SpiralSignal


class TestSpiralEWSInit:
    def test_default_init(self):
        ews = SpiralEarlyWarningSystem()
        assert ews.is_spiraling() is False

    def test_custom_init(self):
        ews = SpiralEarlyWarningSystem(window=5, threshold=2.0)
        assert ews.is_spiraling() is False


class TestFeed:
    def test_feed_accumulates_history(self):
        ews = SpiralEarlyWarningSystem(window=10)
        ews.feed(100, 0.5, depth=1)
        ews.feed(200, 1.0, depth=2)
        signal = ews.check()
        assert isinstance(signal, SpiralSignal)

    def test_feed_zero_values(self):
        ews = SpiralEarlyWarningSystem(window=10)
        ews.feed(0, 0.0, depth=0)
        ews.feed(0, 0.0, depth=0)
        signal = ews.check()
        assert signal.level == "NORMAL"


class TestCheck:
    def test_check_normal_with_stable_usage(self):
        ews = SpiralEarlyWarningSystem(window=10, threshold=1.5)
        for _ in range(6):
            ews.feed(100, 0.5, depth=1)
        signal = ews.check()
        assert signal.level == "NORMAL"

    def test_check_warning_with_growing_usage(self):
        ews = SpiralEarlyWarningSystem(window=10, threshold=1.5)
        for i in range(6):
            ews.feed(100 + i * 200, 0.5 + i * 2.0, depth=1 + i * 2)
        signal = ews.check()
        assert signal.level in ("WARNING", "CRITICAL")

    def test_check_critical_with_extreme_growth(self):
        ews = SpiralEarlyWarningSystem(window=10, threshold=0.1)
        ews.feed(1, 0.001, depth=1)
        ews.feed(1, 0.001, depth=1)
        ews.feed(10000, 100.0, depth=100)
        ews.feed(10000, 100.0, depth=100)
        ews.feed(10000, 100.0, depth=100)
        ews.feed(10000, 100.0, depth=100)
        signal = ews.check()
        assert signal.level == "CRITICAL"

    def test_check_returns_spiral_signal(self):
        ews = SpiralEarlyWarningSystem(window=10)
        ews.feed(100, 0.5, depth=1)
        signal = ews.check()
        assert isinstance(signal, SpiralSignal)
        assert hasattr(signal, "composite_score")
        assert hasattr(signal, "level")

    def test_check_single_entry(self):
        ews = SpiralEarlyWarningSystem(window=10)
        ews.feed(100, 0.5, depth=1)
        signal = ews.check()
        assert signal.token_growth_rate == 0.0
        assert signal.level == "NORMAL"


class TestRecentSignals:
    def test_recent_signals_empty(self):
        ews = SpiralEarlyWarningSystem()
        assert ews.recent_signals() == []

    def test_recent_signals_returns_last_n(self):
        ews = SpiralEarlyWarningSystem(window=10)
        for i in range(5):
            ews.feed(100, 0.5, depth=1)
            ews.check()
        signals = ews.recent_signals(n=3)
        assert len(signals) == 3


class TestIsSpiraling:
    def test_not_spiraling_initially(self):
        ews = SpiralEarlyWarningSystem()
        assert ews.is_spiraling() is False

    def test_not_spiraling_normal(self):
        ews = SpiralEarlyWarningSystem(window=10, threshold=1.5)
        for _ in range(6):
            ews.feed(100, 0.5, depth=1)
        ews.check()
        assert ews.is_spiraling() is False

    def test_spiraling_when_critical(self):
        ews = SpiralEarlyWarningSystem(window=10, threshold=0.1)
        ews.feed(1, 0.001, depth=1)
        ews.feed(1, 0.001, depth=1)
        ews.feed(10000, 100.0, depth=100)
        ews.feed(10000, 100.0, depth=100)
        ews.feed(10000, 100.0, depth=100)
        ews.feed(10000, 100.0, depth=100)
        ews.check()
        assert ews.is_spiraling() is True


class TestReset:
    def test_reset_clears_all(self):
        ews = SpiralEarlyWarningSystem(window=10)
        for _ in range(5):
            ews.feed(100, 0.5, depth=1)
            ews.check()
        ews.reset()
        assert ews.is_spiraling() is False
        assert ews.recent_signals() == []
