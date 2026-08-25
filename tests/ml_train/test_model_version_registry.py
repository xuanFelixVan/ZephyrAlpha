# [TTL] permanent
# [TESTS] src/zephyr/ml_train/core/model_version_registry.py (MOD-ML-012)
"""MOD-ML-012 model_version_registry 单元测试（B4-06880 D-ML-TRAIN 训练域）。"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from zephyr.ml_train.core.model_version_registry import (
    ModelTrainedEvent,
    ModelValidatedEvent,
    ModelVersionRecord,
    ModelVersionRegistry,
    ModelVersionRegistryError,
    ModelVersionStage,
)

NOW = datetime(2026, 8, 25, 12, 0, tzinfo=timezone.utc)


def _registry(events: list | None = None) -> ModelVersionRegistry:
    return ModelVersionRegistry(
        event_sink=events.append if events is not None else None,
        clock=lambda: NOW,
    )


class TestLifecycleHappyPath:
    def test_full_lifecycle(self) -> None:
        reg = _registry()
        r1 = reg.register_trained("m1", "v1", training_metrics={"loss": 0.1})
        assert r1.stage is ModelVersionStage.TRAINED
        r2 = reg.record_validated("m1", "v1", validation_metrics={"ic": 0.05})
        assert r2.stage is ModelVersionStage.VALIDATED
        r3 = reg.record_shadow_verified("m1", "v1", shadow_proof="shadow-session-001")
        assert r3.stage is ModelVersionStage.SHADOW_VERIFIED
        r4 = reg.activate("m1", "v1", approved_by="owner")
        assert r4.stage is ModelVersionStage.ACTIVATED
        r5 = reg.deprecate("m1", "v1", reason="superseded")
        assert r5.stage is ModelVersionStage.DEPRECATED

    def test_events_emitted(self) -> None:
        events: list = []
        reg = _registry(events)
        reg.register_trained("m1", "v1")
        reg.record_validated("m1", "v1", validation_metrics={"ic": 0.05})
        assert isinstance(events[0], ModelTrainedEvent)
        assert events[0].model_id == "m1" and events[0].version == "v1"
        assert isinstance(events[1], ModelValidatedEvent)
        assert events[1].metrics == {"ic": 0.05}

    def test_active_version_lookup(self) -> None:
        reg = _registry()
        reg.register_trained("m1", "v1")
        assert reg.active_version("m1") is None
        reg.record_validated("m1", "v1", validation_metrics={"ic": 0.05})
        reg.record_shadow_verified("m1", "v1", shadow_proof="p")
        reg.activate("m1", "v1", approved_by="owner")
        active = reg.active_version("m1")
        assert active is not None and active.version == "v1"


class TestInv011Gate:
    def test_activate_requires_shadow_verified(self) -> None:
        reg = _registry()
        reg.register_trained("m1", "v1")
        reg.record_validated("m1", "v1", validation_metrics={"ic": 0.05})
        with pytest.raises(ModelVersionRegistryError):
            reg.activate("m1", "v1", approved_by="owner")

    def test_shadow_verified_requires_proof(self) -> None:
        reg = _registry()
        reg.register_trained("m1", "v1")
        reg.record_validated("m1", "v1", validation_metrics={"ic": 0.05})
        with pytest.raises(ModelVersionRegistryError):
            reg.record_shadow_verified("m1", "v1", shadow_proof="")

    def test_activate_requires_human_approval(self) -> None:
        reg = _registry()
        reg.register_trained("m1", "v1")
        reg.record_validated("m1", "v1", validation_metrics={"ic": 0.05})
        reg.record_shadow_verified("m1", "v1", shadow_proof="p")
        with pytest.raises(ModelVersionRegistryError):
            reg.activate("m1", "v1", approved_by="")

    def test_single_active_per_model(self) -> None:
        reg = _registry()
        for v in ("v1", "v2"):
            reg.register_trained("m1", v)
            reg.record_validated("m1", v, validation_metrics={"ic": 0.05})
            reg.record_shadow_verified("m1", v, shadow_proof="p")
        reg.activate("m1", "v1", approved_by="owner")
        with pytest.raises(ModelVersionRegistryError):
            reg.activate("m1", "v2", approved_by="owner")
        reg.deprecate("m1", "v1", reason="rotate")
        reg.activate("m1", "v2", approved_by="owner")
        assert reg.active_version("m1").version == "v2"  # type: ignore[union-attr]


class TestFailClosed:
    def test_empty_ids_rejected(self) -> None:
        reg = _registry()
        with pytest.raises(ModelVersionRegistryError):
            reg.register_trained("", "v1")
        with pytest.raises(ModelVersionRegistryError):
            reg.register_trained("m1", "")

    def test_duplicate_version_rejected(self) -> None:
        reg = _registry()
        reg.register_trained("m1", "v1")
        with pytest.raises(ModelVersionRegistryError):
            reg.register_trained("m1", "v1")

    def test_validate_requires_nonempty_metrics(self) -> None:
        reg = _registry()
        reg.register_trained("m1", "v1")
        with pytest.raises(ModelVersionRegistryError):
            reg.record_validated("m1", "v1", validation_metrics={})
        with pytest.raises(ModelVersionRegistryError):
            reg.record_validated("m1", "v1", validation_metrics={"ic": float("nan")})

    def test_illegal_transition_rejected(self) -> None:
        reg = _registry()
        reg.register_trained("m1", "v1")
        with pytest.raises(ModelVersionRegistryError):
            reg.record_shadow_verified("m1", "v1", shadow_proof="p")

    def test_deprecated_is_terminal(self) -> None:
        reg = _registry()
        reg.register_trained("m1", "v1")
        reg.deprecate("m1", "v1", reason="dead")
        with pytest.raises(ModelVersionRegistryError):
            reg.record_validated("m1", "v1", validation_metrics={"ic": 0.05})

    def test_unknown_model_or_version(self) -> None:
        reg = _registry()
        with pytest.raises(ModelVersionRegistryError):
            reg.record_validated("ghost", "v1", validation_metrics={"ic": 0.05})
        reg.register_trained("m1", "v1")
        with pytest.raises(ModelVersionRegistryError):
            reg.record_validated("m1", "v9", validation_metrics={"ic": 0.05})
        with pytest.raises(ModelVersionRegistryError):
            reg.get("m1", "v9")


class TestRecordShape:
    def test_record_is_frozen_snapshot(self) -> None:
        reg = _registry()
        rec = reg.register_trained("m1", "v1", lineage={"dataset": "d1"})
        assert isinstance(rec, ModelVersionRecord)
        assert rec.trained_at == NOW
        assert rec.lineage == {"dataset": "d1"}
        with pytest.raises(AttributeError):
            rec.stage = ModelVersionStage.DEPRECATED  # type: ignore[misc]

    def test_list_versions_ordered(self) -> None:
        reg = _registry()
        reg.register_trained("m1", "v2")
        reg.register_trained("m1", "v1")
        assert [r.version for r in reg.list_versions("m1")] == ["v1", "v2"]
