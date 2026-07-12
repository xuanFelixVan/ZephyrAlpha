# [A_test] module_id: SRC-TST-1600 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_silent_corruption_detector
# [INVARIANTS] seal returns (data,sha256_hex); validate checks checksum; quarantine at rate>3x threshold
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_silent_corruption_detector.py
# [TTL] task_bound

import hashlib

from zephyr.feedback_loop.detectors.silent_corruption_detector import (
    CorruptionSeverity,
    SilentCorruptionDetector,
)


class TestCorruptionSeverity:
    def test_enum_values(self):
        assert CorruptionSeverity.NONE == "NONE"
        assert CorruptionSeverity.ISOLATED == "ISOLATED"
        assert CorruptionSeverity.PATTERN == "PATTERN"
        assert CorruptionSeverity.SYSTEMIC == "SYSTEMIC"


class TestSilentCorruptionDetectorInstantiation:
    def test_default_params(self):
        obj = SilentCorruptionDetector()
        assert obj.max_corruption_rate == 0.001
        assert obj.systemic_threshold == 5
        assert obj.read_validations == {}
        assert obj.corruption_events == []
        assert obj.quarantined_sinks == set()

    def test_custom_params(self):
        obj = SilentCorruptionDetector(max_corruption_rate=0.01, systemic_threshold=10)
        assert obj.max_corruption_rate == 0.01
        assert obj.systemic_threshold == 10


class TestSilentCorruptionDetectorSeal:
    def test_seal_returns_data_and_checksum(self):
        obj = SilentCorruptionDetector()
        data = b"hello world"
        result_data, checksum = obj.seal(data)
        assert result_data == data
        assert checksum == hashlib.sha256(data).hexdigest()

    def test_seal_empty_bytes(self):
        obj = SilentCorruptionDetector()
        data = b""
        result_data, checksum = obj.seal(data)
        assert result_data == data
        assert len(checksum) == 64

    def test_seal_deterministic(self):
        obj = SilentCorruptionDetector()
        data = b"test data"
        _, c1 = obj.seal(data)
        _, c2 = obj.seal(data)
        assert c1 == c2


class TestSilentCorruptionDetectorValidate:
    def test_validate_correct_checksum(self):
        obj = SilentCorruptionDetector()
        data = b"valid data"
        _, checksum = obj.seal(data)
        result = obj.validate("sink-1", "block-1", data, checksum)
        assert result["valid"] is True
        assert result["severity"] == CorruptionSeverity.NONE.value
        assert result["recommendation"] == "continue"

    def test_validate_incorrect_checksum_isolated(self):
        obj = SilentCorruptionDetector(max_corruption_rate=0.5)
        data = b"valid data"
        _, checksum = obj.seal(data)
        obj.validate("sink-1", "block-1", data, checksum)
        obj.validate("sink-1", "block-2", data, checksum)
        result = obj.validate("sink-1", "block-3", b"corrupted", "bad_checksum")
        assert result["valid"] is False
        assert result["severity"] == CorruptionSeverity.ISOLATED.value
        assert result["recommendation"] == "log_and_monitor"

    def test_validate_returns_dict_structure(self):
        obj = SilentCorruptionDetector()
        data = b"test"
        _, checksum = obj.seal(data)
        result = obj.validate("sink-1", "block-1", data, checksum)
        assert "valid" in result
        assert "sink" in result
        assert "block_id" in result
        assert "severity" in result
        assert "corruption_rate" in result
        assert "recommendation" in result

    def test_validate_tracks_corruption_rate(self):
        obj = SilentCorruptionDetector()
        data = b"test"
        _, checksum = obj.seal(data)
        obj.validate("sink-1", "block-1", data, checksum)
        obj.validate("sink-1", "block-2", b"corrupted", "bad")
        summary = obj.get_sink_health_summary()
        assert summary["sink-1"]["total_reads"] == 2
        assert summary["sink-1"]["corrupted_reads"] == 1


class TestSilentCorruptionDetectorQuarantine:
    def test_not_quarantined_by_default(self):
        obj = SilentCorruptionDetector()
        assert obj.is_sink_quarantined("sink-1") is False

    def test_systemic_corruption_triggers_quarantine(self):
        obj = SilentCorruptionDetector(max_corruption_rate=0.001)
        for i in range(10):
            obj.validate("sink-1", f"block-{i}", b"corrupted", "bad_checksum")
        assert obj.is_sink_quarantined("sink-1") is True

    def test_healthy_sink_not_quarantined(self):
        obj = SilentCorruptionDetector()
        data = b"good data"
        _, checksum = obj.seal(data)
        for i in range(10):
            obj.validate("sink-1", f"block-{i}", data, checksum)
        assert obj.is_sink_quarantined("sink-1") is False


class TestSilentCorruptionDetectorHealthSummary:
    def test_empty_summary(self):
        obj = SilentCorruptionDetector()
        assert obj.get_sink_health_summary() == {}

    def test_summary_structure(self):
        obj = SilentCorruptionDetector()
        data = b"test"
        _, checksum = obj.seal(data)
        obj.validate("sink-1", "block-1", data, checksum)
        summary = obj.get_sink_health_summary()
        assert "sink-1" in summary
        assert "total_reads" in summary["sink-1"]
        assert "corrupted_reads" in summary["sink-1"]
        assert "corruption_rate" in summary["sink-1"]
        assert "quarantined" in summary["sink-1"]
        assert "healthy" in summary["sink-1"]


class TestSilentCorruptionDetectorTotalCorruptions:
    def test_no_corruptions_initially(self):
        obj = SilentCorruptionDetector()
        assert obj.get_total_corruptions() == 0

    def test_corruption_count_increases(self):
        obj = SilentCorruptionDetector()
        obj.validate("sink-1", "block-1", b"bad", "wrong")
        assert obj.get_total_corruptions() == 1
        obj.validate("sink-1", "block-2", b"bad2", "wrong2")
        assert obj.get_total_corruptions() == 2


class TestSilentCorruptionDetectorOverallIntegrity:
    def test_no_reads_returns_one(self):
        obj = SilentCorruptionDetector()
        assert obj.overall_data_integrity() == 1.0

    def test_all_valid_high_integrity(self):
        obj = SilentCorruptionDetector()
        data = b"test"
        _, checksum = obj.seal(data)
        obj.validate("sink-1", "block-1", data, checksum)
        assert obj.overall_data_integrity() == 1.0

    def test_mixed_validity(self):
        obj = SilentCorruptionDetector()
        data = b"test"
        _, checksum = obj.seal(data)
        obj.validate("sink-1", "block-1", data, checksum)
        obj.validate("sink-1", "block-2", b"corrupted", "bad")
        integrity = obj.overall_data_integrity()
        assert 0.0 <= integrity <= 1.0
