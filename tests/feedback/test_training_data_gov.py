# [A_test] module_id: SRC-TST-1762 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_training_data_gov
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.evolution.training_data_gov
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_training_data_gov.py
# [TTL] task_bound

import pytest

from zephyr.feedback_loop.evolution.training_data_gov import (
    DataSnapshot,
    TrainingDataGov,
)


class TestTrainingDataGovInstantiation:
    def test_default_instantiation(self):
        obj = TrainingDataGov()
        assert obj is not None
        assert obj.snapshots == []
        assert obj.drift_threshold == pytest.approx(0.05)

    def test_custom_threshold(self):
        obj = TrainingDataGov(drift_threshold=0.1)
        assert obj.drift_threshold == pytest.approx(0.1)

    def test_is_dataclass(self):
        obj = TrainingDataGov()
        assert hasattr(obj, "__dataclass_fields__")


class TestTrainingDataGovSnapshot:
    def test_snapshot_creates_entry(self):
        tdg = TrainingDataGov()
        snap = tdg.snapshot(data_checksum="abc123", rows=1000, features=50)
        assert isinstance(snap, DataSnapshot)
        assert snap.row_count == 1000
        assert snap.feature_count == 50
        assert len(snap.snapshot_id) == 8

    def test_snapshot_appends_to_list(self):
        tdg = TrainingDataGov()
        tdg.snapshot(data_checksum="a", rows=100, features=10)
        tdg.snapshot(data_checksum="b", rows=200, features=20)
        assert len(tdg.snapshots) == 2

    def test_snapshot_has_distribution_hash(self):
        tdg = TrainingDataGov()
        snap = tdg.snapshot(data_checksum="test", rows=50, features=5)
        assert len(snap.distribution_hash) == 16

    def test_snapshot_has_timestamp(self):
        tdg = TrainingDataGov()
        snap = tdg.snapshot(data_checksum="x", rows=10, features=2)
        assert snap.timestamp > 0


class TestTrainingDataGovDetectDrift:
    def test_no_drift_with_one_snapshot(self):
        tdg = TrainingDataGov()
        tdg.snapshot(data_checksum="a", rows=100, features=10)
        drift = tdg.detect_drift()
        assert drift == pytest.approx(0.0)

    def test_no_drift_with_no_snapshots(self):
        tdg = TrainingDataGov()
        drift = tdg.detect_drift()
        assert drift == pytest.approx(0.0)

    def test_detect_drift_between_snapshots(self):
        tdg = TrainingDataGov()
        tdg.snapshot(data_checksum="a", rows=100, features=10)
        tdg.snapshot(data_checksum="b", rows=150, features=10)
        drift = tdg.detect_drift()
        assert drift == pytest.approx(0.5)

    def test_detect_no_drift_same_rows(self):
        tdg = TrainingDataGov()
        tdg.snapshot(data_checksum="a", rows=100, features=10)
        tdg.snapshot(data_checksum="b", rows=100, features=10)
        drift = tdg.detect_drift()
        assert drift == pytest.approx(0.0)


class TestTrainingDataGovBoundaries:
    def test_zero_rows(self):
        tdg = TrainingDataGov()
        tdg.snapshot(data_checksum="a", rows=0, features=10)
        tdg.snapshot(data_checksum="b", rows=100, features=10)
        drift = tdg.detect_drift()
        assert drift >= 0.0

    def test_many_snapshots(self):
        tdg = TrainingDataGov()
        for i in range(100):
            tdg.snapshot(data_checksum=f"ck_{i}", rows=100 + i, features=10)
        assert len(tdg.snapshots) == 100
        drift = tdg.detect_drift()
        assert isinstance(drift, float)

    def test_empty_checksum(self):
        tdg = TrainingDataGov()
        snap = tdg.snapshot(data_checksum="", rows=50, features=5)
        assert isinstance(snap.snapshot_id, str)
