# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] tests.shared.alerts.test_alert_precision_tracker
# [DOMAIN] D_SHARED
# [INVARIANTS] precision/recall 口径正确; 零除退化 0.0; 计数单调
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [TTL] permanent
"""shared/alerts AlertPrecisionTracker 测试债清偿（55 号 §7 新发现 2，AI-NIGHT-001 包P）。"""

from __future__ import annotations

import pytest

from zephyr.shared.alerts.alert_precision_tracker import AlertPrecisionTracker


class TestAlertPrecisionTracker:
    def test_zero_division_degenerates_zero(self):
        metrics = AlertPrecisionTracker().compute()
        assert metrics.precision == 0.0
        assert metrics.recall == 0.0
        assert metrics.total_alerts == 0

    def test_precision_and_recall_math(self):
        tracker = AlertPrecisionTracker()
        for _ in range(3):
            tracker.record_true_positive()
        tracker.record_false_positive()
        tracker.record_false_negative()
        metrics = tracker.compute()
        # precision = TP/(TP+FP) = 3/4; recall = TP/(TP+FN) = 3/4
        assert metrics.precision == pytest.approx(0.75)
        assert metrics.recall == pytest.approx(0.75)
        assert metrics.total_alerts == 4
        assert metrics.true_positives == 3
        assert metrics.false_positives == 1

    def test_all_false_positives_zero_precision(self):
        tracker = AlertPrecisionTracker()
        tracker.record_false_positive()
        tracker.record_false_positive()
        assert tracker.compute().precision == 0.0

    def test_metrics_alias_equals_compute(self):
        tracker = AlertPrecisionTracker()
        tracker.record_true_positive()
        assert tracker.metrics() == tracker.compute()

    def test_counts_monotonic(self):
        tracker = AlertPrecisionTracker()
        tracker.record_true_positive()
        first = tracker.compute().true_positives
        tracker.record_true_positive()
        assert tracker.compute().true_positives == first + 1
