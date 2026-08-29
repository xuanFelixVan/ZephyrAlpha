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
"""shared/alerts AlertPrecisionTracker 测试债清偿（55 号 §7 新发现 2，AI-NIGHT-001 包P）。

P1-3②（16号文 §4.3）：append-only 落盘 + 启动回放恢复计数；
默认纯内存行为与历史版本一致（既有消费方零破坏）。
"""

from __future__ import annotations

import json

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


class TestAlertPrecisionTrackerPersistence:
    """P1-3②：append-only 落盘（.runtime/ 下 jsonl）+ 启动回放恢复计数。"""

    def test_default_tracker_is_memory_only(self):
        tracker = AlertPrecisionTracker()
        assert tracker.persist_path is None, "无参构造 MUST 保持纯内存（既有消费方零破坏）"
        tracker.record_true_positive()
        assert tracker.compute().true_positives == 1

    def test_records_appended_as_jsonl(self, tmp_path):
        path = tmp_path / "precision.jsonl"
        tracker = AlertPrecisionTracker(persist_path=path)
        tracker.record_true_positive()
        tracker.record_true_positive()
        tracker.record_false_positive()
        tracker.record_false_negative()
        lines = [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert [line["kind"] for line in lines] == [
            "true_positive",
            "true_positive",
            "false_positive",
            "false_negative",
        ]
        assert all(line["ts"] for line in lines), "每条落盘记录 MUST 含时间戳"

    def test_replay_recovers_counts_on_restart(self, tmp_path):
        path = tmp_path / "precision.jsonl"
        first = AlertPrecisionTracker(persist_path=path)
        first.record_true_positive()
        first.record_false_positive()
        first.record_false_negative()
        restarted = AlertPrecisionTracker(persist_path=path)
        assert restarted.compute() == first.compute(), "启动回放 MUST 恢复计数"

    def test_replay_then_append_keeps_append_only(self, tmp_path):
        path = tmp_path / "precision.jsonl"
        AlertPrecisionTracker(persist_path=path).record_true_positive()
        second = AlertPrecisionTracker(persist_path=path)
        second.record_false_positive()
        third = AlertPrecisionTracker(persist_path=path)
        metrics = third.compute()
        assert metrics.true_positives == 1
        assert metrics.false_positives == 1
        lines = [
            line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
        ]
        assert len(lines) == 2, "落盘 MUST append-only（回放不回写/不压缩）"

    def test_precision_math_unchanged_with_persistence(self, tmp_path):
        tracker = AlertPrecisionTracker(persist_path=tmp_path / "precision.jsonl")
        for _ in range(3):
            tracker.record_true_positive()
        tracker.record_false_positive()
        assert tracker.compute().precision == pytest.approx(0.75)
