# [BLUEPRINT] MOD-ML-003 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_test] module_id: MOD-ML_test_training_dataset_manager | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.ml_train.test_training_dataset_manager
# [TESTS] src/zephyr/ml_train/training_dataset_manager/manager.py
# [TTL] task_bound
"""MOD-ML-003 训练数据集管理器 toy 断言（版本化/快照/血缘登记）。

合成小数据，无 DB/网络（内存态存储注入）。
"""

from __future__ import annotations

import numpy as np
import pytest

from zephyr.ml_train.training_dataset_manager import (
    DatasetLineageError,
    TrainingDatasetManager,
)


def _rows(n: int = 20) -> list[dict]:
    rng = np.random.default_rng(1)
    return [{"f0": float(v), "label": int(i % 2)} for i, v in enumerate(rng.normal(size=n))]


class TestSnapshotVersioning:
    def test_register_creates_v1_snapshot(self):
        mgr = TrainingDatasetManager()
        ds = mgr.register_dataset("ds-limit-up", rows=_rows(), description="首版")
        assert ds.version == 1
        assert ds.row_count == 20
        assert len(ds.content_hash) == 64  # sha256 hex

    def test_reregister_bumps_version_and_keeps_history(self):
        mgr = TrainingDatasetManager()
        mgr.register_dataset("ds-1", rows=_rows())
        v2 = mgr.register_dataset("ds-1", rows=_rows(25))
        assert v2.version == 2
        assert [d.version for d in mgr.list_versions("ds-1")] == [1, 2]

    def test_same_content_different_hash_when_rows_differ(self):
        mgr = TrainingDatasetManager()
        a = mgr.register_dataset("ds-1", rows=_rows(20))
        b = mgr.register_dataset("ds-1", rows=_rows(21))
        assert a.content_hash != b.content_hash

    def test_empty_rows_rejected(self):
        mgr = TrainingDatasetManager()
        with pytest.raises(ValueError, match="rows"):
            mgr.register_dataset("ds-1", rows=[])


class TestLineage:
    def test_lineage_records_parent_versions(self):
        mgr = TrainingDatasetManager()
        v1 = mgr.register_dataset("ds-1", rows=_rows())
        v2 = mgr.register_dataset("ds-1", rows=_rows(22), parent_version=v1.version)
        assert v2.parent_version == 1
        chain = mgr.lineage("ds-1", version=2)
        assert [c.version for c in chain] == [2, 1]

    def test_lineage_unknown_dataset_raises(self):
        mgr = TrainingDatasetManager()
        with pytest.raises(DatasetLineageError) as exc:
            mgr.lineage("nope", version=1)
        assert exc.value.error_code == "ZA-MLT-0006"

    def test_parent_version_must_exist(self):
        mgr = TrainingDatasetManager()
        mgr.register_dataset("ds-1", rows=_rows())
        with pytest.raises(DatasetLineageError, match="parent"):
            mgr.register_dataset("ds-1", rows=_rows(22), parent_version=99)


class TestSnapshotRetrieval:
    def test_get_snapshot_roundtrip(self):
        mgr = TrainingDatasetManager()
        rows = _rows()
        mgr.register_dataset("ds-1", rows=rows)
        snap = mgr.get_snapshot("ds-1", version=1)
        assert snap.row_count == 20
        assert mgr.load_rows("ds-1", version=1) == rows

    def test_unknown_version_raises(self):
        mgr = TrainingDatasetManager()
        mgr.register_dataset("ds-1", rows=_rows())
        with pytest.raises(DatasetLineageError, match="version"):
            mgr.get_snapshot("ds-1", version=7)
