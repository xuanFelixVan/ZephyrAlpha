# [A_test] module_id: SRC-TST-1579 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_serialization_format_tracker
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.forensic.serialization_format_tracker
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_serialization_format_tracker.py
# [TTL] task_bound

from __future__ import annotations

import pickle

from zephyr.feedback_loop.forensic.serialization_format_tracker import (
    Compatibility,
    SerdeFormat,
    SerializationFormatTracker,
)


class TestSerdeFormat:
    def test_enum_values(self):
        assert SerdeFormat.PICKLE.value == "PICKLE"
        assert SerdeFormat.JSON.value == "JSON"
        assert SerdeFormat.YAML.value == "YAML"
        assert SerdeFormat.MSGPACK.value == "MSGPACK"


class TestCompatibility:
    def test_enum_values(self):
        assert Compatibility.COMPATIBLE.value == "COMPATIBLE"
        assert Compatibility.MINOR_CHANGE.value == "MINOR_CHANGE"
        assert Compatibility.BREAKING.value == "BREAKING"


class TestSerializationFormatTracker:
    def test_instantiation_defaults(self):
        sft = SerializationFormatTracker()
        assert sft.max_tracked_artifacts == 500
        assert "pickle" in sft.format_versions
        assert "json" in sft.format_versions
        assert sft.version_changes == []

    def test_record_artifact_pickle(self):
        sft = SerializationFormatTracker()
        result = sft.record_artifact("state-v1", SerdeFormat.PICKLE, b"data-bytes")
        assert result["artifact_id"] == "state-v1"
        assert len(result["hash"]) == 16
        assert result["size"] == len(b"data-bytes")

    def test_record_artifact_json(self):
        sft = SerializationFormatTracker()
        result = sft.record_artifact("config-v1", SerdeFormat.JSON, b'{"key": "val"}')
        assert result["artifact_id"] == "config-v1"
        assert result["size"] == len(b'{"key": "val"}')

    def test_record_artifact_deterministic_hash(self):
        sft1 = SerializationFormatTracker()
        sft2 = SerializationFormatTracker()
        data = b"same-data"
        r1 = sft1.record_artifact("a1", SerdeFormat.JSON, data)
        r2 = sft2.record_artifact("a1", SerdeFormat.JSON, data)
        assert r1["hash"] == r2["hash"]

    def test_check_compatibility_no_prior_record(self):
        sft = SerializationFormatTracker()
        result = sft.check_compatibility("new-artifact", SerdeFormat.JSON)
        assert result["compatibility"] == Compatibility.COMPATIBLE.value
        assert result["reason"] == "no_prior_record"

    def test_check_compatibility_same_format(self):
        sft = SerializationFormatTracker()
        sft.record_artifact("state-v1", SerdeFormat.JSON, b"data")
        result = sft.check_compatibility("state-v1", SerdeFormat.JSON)
        assert result["compatibility"] == Compatibility.COMPATIBLE.value

    def test_check_compatibility_format_changed(self):
        sft = SerializationFormatTracker()
        sft.record_artifact("state-v1", SerdeFormat.PICKLE, b"data")
        result = sft.check_compatibility("state-v1", SerdeFormat.JSON)
        assert result["compatibility"] == Compatibility.BREAKING.value
        assert "format_changed" in result["reason"]

    def test_check_compatibility_pickle_protocol_change(self):
        sft = SerializationFormatTracker()
        sft.format_versions["state-v1"] = {
            "format": "PICKLE",
            "pickle_protocol": 2,
            "recorded_at": 0,
        }
        result = sft.check_compatibility("state-v1", SerdeFormat.PICKLE)
        if pickle.HIGHEST_PROTOCOL != 2:
            assert result["compatibility"] == Compatibility.MINOR_CHANGE.value
        else:
            assert result["compatibility"] == Compatibility.COMPATIBLE.value

    def test_validate_state_load_correct_type(self):
        sft = SerializationFormatTracker()
        result = sft.validate_state_load("state-v1", {"key": "val"}, dict)
        assert result["valid"] is True

    def test_validate_state_load_wrong_type(self):
        sft = SerializationFormatTracker()
        result = sft.validate_state_load("state-v1", [1, 2, 3], dict)
        assert result["valid"] is False
        assert result["expected_type"] == "dict"
        assert result["actual_type"] == "list"

    def test_get_format_history(self):
        sft = SerializationFormatTracker()
        sft.record_artifact("a1", SerdeFormat.JSON, b"data1")
        sft.record_artifact("a2", SerdeFormat.PICKLE, b"data2")
        history = sft.get_format_history()
        assert len(history) == 2
        ids = [h["id"] for h in history]
        assert "a1" in ids
        assert "a2" in ids

    def test_get_breaking_changes_count(self):
        sft = SerializationFormatTracker()
        sft.record_artifact("a1", SerdeFormat.PICKLE, b"data")
        sft.check_compatibility("a1", SerdeFormat.JSON)
        assert sft.get_breaking_changes_count() == 1

    def test_overall_format_health_clean(self):
        sft = SerializationFormatTracker()
        assert sft.overall_format_health() == 1.0

    def test_overall_format_health_with_breaking(self):
        sft = SerializationFormatTracker()
        for i in range(5):
            sft.version_changes.append({"severity": "BREAKING"})
        health = sft.overall_format_health()
        assert health == 0.5

    def test_max_tracked_artifacts_truncation(self):
        sft = SerializationFormatTracker(max_tracked_artifacts=5)
        for i in range(10):
            sft.record_artifact(f"artifact-{i}", SerdeFormat.JSON, f"data-{i}".encode())
        artifact_keys = [k for k in sft.format_versions if k not in ("pickle", "json")]
        assert len(artifact_keys) <= 5
