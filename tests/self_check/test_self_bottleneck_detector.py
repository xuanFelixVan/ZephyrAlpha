# [A_test] module_id: SRC-TST-1551 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_self_bottleneck_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.self_bottleneck_detector
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_self_bottleneck_detector.py
# [TTL] task_bound

import pytest

from zephyr.feedback_loop.diagnosers.self_bottleneck_detector import (
    PipelineStage,
    SelfBottleneckDetector,
)


class TestPipelineStageEnum:
    def test_all_stages_exist(self):
        assert PipelineStage.COLLECT.value == "COLLECT"
        assert PipelineStage.DETECT.value == "DETECT"
        assert PipelineStage.DIAGNOSE.value == "DIAGNOSE"
        assert PipelineStage.ACT.value == "ACT"
        assert PipelineStage.VERIFY.value == "VERIFY"


class TestSelfBottleneckDetectorInstantiation:
    def test_default_instantiation(self):
        sbd = SelfBottleneckDetector()
        assert sbd.max_stage_latency_ms == 5000.0
        assert sbd.max_e2e_latency_ms == 30000.0
        assert sbd.max_queue_depth == 100
        assert sbd.window_size == 100
        assert sbd.current_bottleneck == ""
        assert len(sbd.bottleneck_events) == 0

    def test_all_stages_initialized_in_latencies(self):
        sbd = SelfBottleneckDetector()
        for stage in PipelineStage:
            assert stage.value in sbd.stage_latencies
            assert sbd.stage_latencies[stage.value] == []

    def test_all_stages_initialized_in_queue_depths(self):
        sbd = SelfBottleneckDetector()
        for stage in PipelineStage:
            assert stage.value in sbd.stage_queue_depths
            assert sbd.stage_queue_depths[stage.value] == 0


class TestRecordStageLatency:
    def test_record_single_latency(self):
        sbd = SelfBottleneckDetector()
        sbd.record_stage_latency(PipelineStage.DETECT, 100.0)
        assert sbd.stage_latencies["DETECT"] == [100.0]

    def test_record_multiple_latencies(self):
        sbd = SelfBottleneckDetector()
        sbd.record_stage_latency(PipelineStage.DETECT, 100.0)
        sbd.record_stage_latency(PipelineStage.DETECT, 200.0)
        assert len(sbd.stage_latencies["DETECT"]) == 2

    def test_window_size_respected(self):
        sbd = SelfBottleneckDetector(window_size=5)
        for i in range(10):
            sbd.record_stage_latency(PipelineStage.DETECT, float(i))
        assert len(sbd.stage_latencies["DETECT"]) == 5


class TestRecordE2ELatency:
    def test_record_e2e_latency(self):
        sbd = SelfBottleneckDetector()
        sbd.record_e2e_latency(5000.0)
        assert sbd.e2e_latencies == [5000.0]

    def test_e2e_window_size_respected(self):
        sbd = SelfBottleneckDetector(window_size=3)
        for i in range(5):
            sbd.record_e2e_latency(float(i))
        assert len(sbd.e2e_latencies) == 3


class TestSetQueueDepth:
    def test_set_queue_depth(self):
        sbd = SelfBottleneckDetector()
        sbd.set_queue_depth(PipelineStage.DIAGNOSE, 50)
        assert sbd.stage_queue_depths["DIAGNOSE"] == 50


class TestDetectBottleneck:
    def test_no_bottleneck_when_empty(self):
        sbd = SelfBottleneckDetector()
        result = sbd.detect_bottleneck()
        assert result["bottleneck"] == "none"
        assert result["e2e_healthy"] is True

    def test_detect_slow_stage_as_bottleneck(self):
        sbd = SelfBottleneckDetector(max_stage_latency_ms=100.0)
        for _ in range(20):
            sbd.record_stage_latency(PipelineStage.DIAGNOSE, 500.0)
        result = sbd.detect_bottleneck()
        assert result["bottleneck"] == "DIAGNOSE"

    def test_detect_queue_saturation_bottleneck(self):
        sbd = SelfBottleneckDetector(max_queue_depth=10)
        for _ in range(20):
            sbd.record_stage_latency(PipelineStage.COLLECT, 10.0)
        sbd.set_queue_depth(PipelineStage.COLLECT, 50)
        result = sbd.detect_bottleneck()
        assert result["queue_saturated"] is True

    def test_bottleneck_event_recorded_on_change(self):
        sbd = SelfBottleneckDetector(max_stage_latency_ms=100.0)
        for _ in range(20):
            sbd.record_stage_latency(PipelineStage.ACT, 500.0)
        sbd.detect_bottleneck()
        assert len(sbd.bottleneck_events) == 1
        assert sbd.bottleneck_events[0]["stage"] == "ACT"


class TestOverallThroughputHealth:
    def test_healthy_when_no_data(self):
        sbd = SelfBottleneckDetector()
        assert sbd.overall_throughput_health() == 1.0

    def test_healthy_when_low_latency(self):
        sbd = SelfBottleneckDetector(max_e2e_latency_ms=30000.0)
        for _ in range(20):
            sbd.record_e2e_latency(100.0)
        health = sbd.overall_throughput_health()
        assert health > 0.9

    def test_degraded_when_high_latency(self):
        sbd = SelfBottleneckDetector(max_e2e_latency_ms=1000.0)
        for _ in range(20):
            sbd.record_e2e_latency(50000.0)
        health = sbd.overall_throughput_health()
        assert health < 0.5


class TestSelfBottleneckDetectorBoundaries:
    def test_zero_latency(self):
        sbd = SelfBottleneckDetector()
        sbd.record_stage_latency(PipelineStage.VERIFY, 0.0)
        assert sbd.stage_latencies["VERIFY"] == [0.0]

    def test_negative_latency_recorded(self):
        sbd = SelfBottleneckDetector()
        sbd.record_stage_latency(PipelineStage.VERIFY, -10.0)
        assert sbd.stage_latencies["VERIFY"] == [-10.0]

    def test_none_stage_raises(self):
        sbd = SelfBottleneckDetector()
        with pytest.raises((TypeError, AttributeError)):
            sbd.record_stage_latency(None, 100.0)
