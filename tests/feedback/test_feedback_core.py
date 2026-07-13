# [A_test] module_id: SRC-TST-1877 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.unit.feedback_loop.test_feedback_core
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound

"""Test suite: feedback-loop core (FeedbackCollector + FeedbackLoopScheduler)"""

import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from zephyr.feedback_loop.feedback_collector import (
    FeedbackCollector,
    FeedbackEntry,
)

# ---------------------------------------------------------------------------
# FeedbackCollector
# ---------------------------------------------------------------------------


class TestFeedbackEntry:
    def test_valid_entry(self):
        entry = FeedbackEntry(
            entry_id="FB-0001",
            task_id="T-001",
            score=4,
            comment="good",
            tags=["fast"],
            created_at=datetime.now(),
        )
        assert entry.entry_id == "FB-0001"
        assert entry.score == 4
        assert entry.tags == ["fast"]

    def test_score_out_of_range_raises(self):
        with pytest.raises(Exception):
            FeedbackEntry(
                entry_id="FB-0001",
                task_id="T-001",
                score=0,
                created_at=datetime.now(),
            )

    def test_score_above_max_raises(self):
        with pytest.raises(Exception):
            FeedbackEntry(
                entry_id="FB-0001",
                task_id="T-001",
                score=6,
                created_at=datetime.now(),
            )

    def test_tags_deduplication(self):
        entry = FeedbackEntry(
            entry_id="FB-0001",
            task_id="T-001",
            score=3,
            tags=["fast", "fast", "slow"],
            created_at=datetime.now(),
        )
        assert entry.tags == ["fast", "slow"]

    def test_empty_entry_id_raises(self):
        with pytest.raises(Exception):
            FeedbackEntry(
                entry_id="",
                task_id="T-001",
                score=3,
                created_at=datetime.now(),
            )


class TestFeedbackCollector:
    @pytest.fixture
    def collector(self):
        return FeedbackCollector()

    def test_add_returns_entry(self, collector):
        entry = collector.add(task_id="T-001", score=5, comment="excellent")
        assert entry.entry_id == "FB-0001"
        assert entry.task_id == "T-001"
        assert entry.score == 5
        assert entry.comment == "excellent"

    def test_add_auto_increments_id(self, collector):
        collector.add(task_id="T-001", score=4)
        entry2 = collector.add(task_id="T-002", score=3)
        assert entry2.entry_id == "FB-0002"

    def test_add_with_tags(self, collector):
        entry = collector.add(task_id="T-001", score=4, tags=["fast", "accurate"])
        assert entry.tags == ["fast", "accurate"]

    def test_add_with_custom_timestamp(self, collector):
        ts = datetime(2026, 1, 1, 12, 0, 0)
        entry = collector.add(task_id="T-001", score=3, created_at=ts)
        assert entry.created_at == ts

    def test_get_entries_all(self, collector):
        collector.add(task_id="T-001", score=4)
        collector.add(task_id="T-002", score=3)
        all_entries = collector.get_entries()
        assert len(all_entries) == 2

    def test_get_entries_filtered_by_task(self, collector):
        collector.add(task_id="T-001", score=4)
        collector.add(task_id="T-002", score=3)
        collector.add(task_id="T-001", score=5)
        filtered = collector.get_entries(task_id="T-001")
        assert len(filtered) == 2
        assert all(e.task_id == "T-001" for e in filtered)

    def test_get_entries_returns_copy(self, collector):
        collector.add(task_id="T-001", score=4)
        entries = collector.get_entries()
        entries.clear()
        assert collector.entry_count == 1

    def test_summarize_with_entries(self, collector):
        collector.add(task_id="T-001", score=4, tags=["fast"])
        collector.add(task_id="T-001", score=2, tags=["slow", "fast"])
        summary = collector.summarize("T-001")
        assert summary.task_id == "T-001"
        assert summary.count == 2
        assert summary.average_score == 3.0
        assert summary.tag_frequencies == {"fast": 2, "slow": 1}
        assert summary.latest_comment == ""

    def test_summarize_no_entries(self, collector):
        summary = collector.summarize("T-999")
        assert summary.count == 0
        assert summary.average_score == 0.0
        assert summary.tag_frequencies == {}

    def test_entry_count(self, collector):
        assert collector.entry_count == 0
        collector.add(task_id="T-001", score=4)
        assert collector.entry_count == 1

    def test_clear_returns_count(self, collector):
        collector.add(task_id="T-001", score=4)
        collector.add(task_id="T-002", score=3)
        count = collector.clear()
        assert count == 2
        assert collector.entry_count == 0

    def test_clear_resets_id_counter(self, collector):
        collector.add(task_id="T-001", score=4)
        collector.clear()
        entry = collector.add(task_id="T-002", score=3)
        assert entry.entry_id == "FB-0001"

    def test_flush_without_store_path(self, collector):
        assert collector.flush() == 0

    def test_flush_with_store_path(self, tmp_path):
        store = tmp_path / "feedback.json"
        c = FeedbackCollector(store_path=store)
        c.add(task_id="T-001", score=4, comment="ok")
        count = c.flush()
        assert count == 1
        assert store.exists()
        data = json.loads(store.read_text(encoding="utf-8"))
        assert len(data) == 1
        assert data[0]["task_id"] == "T-001"

    def test_load_from_store(self, tmp_path):
        store = tmp_path / "feedback.json"
        c1 = FeedbackCollector(store_path=store)
        c1.add(task_id="T-001", score=4)
        c1.flush()
        c2 = FeedbackCollector(store_path=store)
        loaded = c2.load()
        assert loaded == 1
        assert c2.entry_count == 1
        assert c2.get_entries()[0].task_id == "T-001"

    def test_load_resumes_id_counter(self, tmp_path):
        store = tmp_path / "feedback.json"
        c1 = FeedbackCollector(store_path=store)
        c1.add(task_id="T-001", score=4)
        c1.add(task_id="T-002", score=3)
        c1.flush()
        c2 = FeedbackCollector(store_path=store)
        c2.load()
        entry = c2.add(task_id="T-003", score=5)
        assert entry.entry_id == "FB-0003"

    def test_load_nonexistent_returns_zero(self, tmp_path):
        c = FeedbackCollector(store_path=tmp_path / "nonexistent.json")
        assert c.load() == 0

    def test_store_path_property(self, tmp_path):
        store = tmp_path / "fb.json"
        c = FeedbackCollector(store_path=store)
        assert c.store_path == store

    def test_store_path_none_when_in_memory(self):
        c = FeedbackCollector()
        assert c.store_path is None


# ---------------------------------------------------------------------------
# FeedbackLoopScheduler (mock-heavy: avoid real sub-component init)
# ---------------------------------------------------------------------------


class TestFeedbackLoopScheduler:
    @pytest.fixture
    def mock_scheduler(self):
        with (
            patch("zephyr.feedback_loop.scheduler.HealthReporter") as hr_cls,
            patch("zephyr.feedback_loop.scheduler.SafetyGateManager") as sgm_cls,
            patch("zephyr.feedback_loop.scheduler.ActPhaseHandler") as aph_cls,
            patch("zephyr.feedback_loop.scheduler.CollectDetectHandler") as cdh_cls,
            patch("zephyr.feedback_loop.scheduler.MetricsCollector") as mc_cls,
            patch("zephyr.feedback_loop.scheduler.FeedbackCollector") as fc_cls,
            patch("zephyr.feedback_loop.scheduler.DependencyFreshnessMonitor") as dfm_cls,
            patch("zephyr.feedback_loop.scheduler.SilentCorruptionDetector") as scd_cls,
            patch("zephyr.feedback_loop.scheduler.RecursiveDiagnosisTrustEvaluator") as rdte_cls,
            patch("zephyr.feedback_loop.scheduler.TemporalCoherenceOfSelfModel") as tcos_cls,
            patch("zephyr.feedback_loop.scheduler.SelfDiagnosisDataLeakDetector") as sdld_cls,
            patch("zephyr.feedback_loop.scheduler.ModelVersionSemanticDrift") as mvsd_cls,
            patch("zephyr.feedback_loop.scheduler.HumanAnomalyFloodDetector") as hafd_cls,
            patch("zephyr.feedback_loop.scheduler.AdaptiveParamTuning") as apt_cls,
            patch("zephyr.feedback_loop.scheduler.RegimeGainScheduling") as rgs_cls,
            patch("zephyr.feedback_loop.scheduler.RecoveryTimeStats") as rts_cls,
            patch("zephyr.feedback_loop.scheduler.NonstationaryEffectiveness") as ne_cls,
            patch("zephyr.feedback_loop.scheduler.TimezoneSemanticReasoner") as tsr_cls,
            patch("zephyr.feedback_loop.scheduler.ActionSelector") as as_cls,
        ):
            from zephyr.feedback_loop.scheduler import FeedbackLoopScheduler

            mock_hr = MagicMock()
            mock_hr.numerical_guard = MagicMock()
            mock_hr.throttle_defense = MagicMock()
            mock_hr.degradation_planner = MagicMock()
            mock_hr.mod_rate_limiter = MagicMock()
            mock_hr.guard_oscillation = MagicMock()
            mock_hr.context_pressure = MagicMock()
            mock_hr.bottleneck_detector = MagicMock()
            mock_hr.stats_hygiene = MagicMock()
            mock_hr.guard_consistency = MagicMock()
            mock_hr.cold_start = MagicMock()
            mock_hr.dogfood_monitor = MagicMock()
            mock_hr.bus_factor_monitor = MagicMock()
            mock_hr.entropy_monitor = MagicMock()
            mock_hr.diminishing_returns = MagicMock()
            hr_cls.return_value = mock_hr

            mock_sgm = MagicMock()
            mock_sgm.boot_attestation = MagicMock()
            mock_sgm.boot_attestation.attest.return_value = {
                "degraded": False,
                "integrity": "ok",
            }
            mock_sgm.temporal_guard = MagicMock()
            mock_sgm.temporal_guard.validate_timestamp.return_value = {
                "valid": True,
            }
            sgm_cls.return_value = mock_sgm

            mock_aph = MagicMock()
            aph_cls.return_value = mock_aph

            mock_cdh = MagicMock()
            cdh_cls.return_value = mock_cdh

            scheduler = FeedbackLoopScheduler(poll_interval=1.0)
            scheduler.safety_gate_manager = mock_sgm
            scheduler.act_handler = mock_aph
            scheduler.collect_detect_handler = mock_cdh
            scheduler.health_reporter = mock_hr
            yield scheduler

    def test_instantiation(self, mock_scheduler):
        assert mock_scheduler.poll_interval == 1.0
        assert mock_scheduler._running is False
        assert mock_scheduler._events == []
        assert mock_scheduler._cycle_count == 0

    def test_events_initially_empty(self, mock_scheduler):
        result = mock_scheduler.events()
        assert result == []

    def test_run_count_initially_zero(self, mock_scheduler):
        assert mock_scheduler.run_count() == 0

    def test_health_report_delegates(self, mock_scheduler):
        mock_scheduler.health_reporter.report.return_value = {"status": "ok"}
        report = mock_scheduler.health_report()
        assert report == {"status": "ok"}
        mock_scheduler.health_reporter.report.assert_called_once()

    def test_stop_without_start(self, mock_scheduler):
        mock_scheduler.stop()
        assert mock_scheduler._running is False

    def test_get_instance_creates_singleton(self):
        from zephyr.feedback_loop.scheduler import FeedbackLoopScheduler

        FeedbackLoopScheduler.reset_instance()
        with (
            patch("zephyr.feedback_loop.scheduler.HealthReporter"),
            patch("zephyr.feedback_loop.scheduler.SafetyGateManager"),
            patch("zephyr.feedback_loop.scheduler.ActPhaseHandler"),
            patch("zephyr.feedback_loop.scheduler.CollectDetectHandler"),
            patch("zephyr.feedback_loop.scheduler.MetricsCollector"),
            patch("zephyr.feedback_loop.scheduler.FeedbackCollector"),
            patch("zephyr.feedback_loop.scheduler.DependencyFreshnessMonitor"),
            patch("zephyr.feedback_loop.scheduler.SilentCorruptionDetector"),
            patch("zephyr.feedback_loop.scheduler.RecursiveDiagnosisTrustEvaluator"),
            patch("zephyr.feedback_loop.scheduler.TemporalCoherenceOfSelfModel"),
            patch("zephyr.feedback_loop.scheduler.SelfDiagnosisDataLeakDetector"),
            patch("zephyr.feedback_loop.scheduler.ModelVersionSemanticDrift"),
            patch("zephyr.feedback_loop.scheduler.HumanAnomalyFloodDetector"),
            patch("zephyr.feedback_loop.scheduler.AdaptiveParamTuning"),
            patch("zephyr.feedback_loop.scheduler.RegimeGainScheduling"),
            patch("zephyr.feedback_loop.scheduler.RecoveryTimeStats"),
            patch("zephyr.feedback_loop.scheduler.NonstationaryEffectiveness"),
            patch("zephyr.feedback_loop.scheduler.TimezoneSemanticReasoner"),
            patch("zephyr.feedback_loop.scheduler.ActionSelector"),
        ):
            inst = FeedbackLoopScheduler.get_instance(poll_interval=5.0)
            assert inst is not None
            inst2 = FeedbackLoopScheduler.get_instance()
            assert inst2 is inst
            FeedbackLoopScheduler.reset_instance()

    def test_fle_pipeline_event_to_dict(self):
        from zephyr.feedback_loop.scheduler import FLEPipelineEvent

        event = FLEPipelineEvent(
            run_id="abc123",
            timestamp=1000000.0,
            phase="collect",
        )
        d = event.to_dict()
        assert d["run_id"] == "abc123"
        assert d["phase"] == "collect"
        assert d["anomaly_triggered"] is False
        assert d["g6_gate_pass"] is True

    def test_max_events_trimming(self, mock_scheduler):
        from zephyr.feedback_loop.scheduler import FLEPipelineEvent

        mock_scheduler.max_events = 5
        for i in range(8):
            mock_scheduler._events.append(FLEPipelineEvent(run_id=f"r{i}", timestamp=float(i), phase="collect"))
        mock_scheduler._append_event(FLEPipelineEvent(run_id="r8", timestamp=8.0, phase="collect"))
        assert len(mock_scheduler._events) == 5
        assert mock_scheduler._events[0].run_id == "r4"
