# [A_test] module_id: MOD-GOV_backpressure_types | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] tests.test_backpressure_types
# [INVARIANTS] All three types are frozen dataclasses; action and schema_version have correct defaults; trace_context defaults to None
# [MODIFY-GUARD] zephyr.infrastructure.pipeline.backpressure_types
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FrozenInstanceError on mutation; TypeError on missing required fields
# [TESTS] —
# [TTL] task_bound

import dataclasses

import pytest

from zephyr.infrastructure.pipeline.backpressure_types import (
    BackpressurePause,
    BackpressureResume,
    BackpressureThrottle,
)


class TestBackpressurePause:
    def test_construction_with_required_fields(self):
        bp = BackpressurePause(
            duration_ms=5000,
            idempotency_key="key-001",
            reason="queue overload",
            signal_id="sig-001",
            symbol="BTC-PERP",
        )
        assert bp.duration_ms == 5000
        assert bp.idempotency_key == "key-001"
        assert bp.reason == "queue overload"
        assert bp.signal_id == "sig-001"
        assert bp.symbol == "BTC-PERP"

    def test_default_action(self):
        bp = BackpressurePause(
            duration_ms=5000,
            idempotency_key="key-001",
            reason="overload",
            signal_id="sig-001",
            symbol="BTC-PERP",
        )
        assert bp.action == "PAUSE"

    def test_default_schema_version(self):
        bp = BackpressurePause(
            duration_ms=5000,
            idempotency_key="key-001",
            reason="overload",
            signal_id="sig-001",
            symbol="BTC-PERP",
        )
        assert bp.schema_version == "1.0"

    def test_default_trace_context(self):
        bp = BackpressurePause(
            duration_ms=5000,
            idempotency_key="key-001",
            reason="overload",
            signal_id="sig-001",
            symbol="BTC-PERP",
        )
        assert bp.trace_context is None

    def test_frozen_immutability(self):
        bp = BackpressurePause(
            duration_ms=5000,
            idempotency_key="key-001",
            reason="overload",
            signal_id="sig-001",
            symbol="BTC-PERP",
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            bp.duration_ms = 10000

    def test_frozen_immutability_reason(self):
        bp = BackpressurePause(
            duration_ms=5000,
            idempotency_key="key-001",
            reason="overload",
            signal_id="sig-001",
            symbol="BTC-PERP",
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            bp.reason = "new reason"

    def test_missing_required_field_raises(self):
        with pytest.raises(TypeError):
            BackpressurePause(
                duration_ms=5000,
                reason="overload",
            )

    def test_custom_action(self):
        bp = BackpressurePause(
            duration_ms=5000,
            idempotency_key="key-001",
            reason="overload",
            signal_id="sig-001",
            symbol="BTC-PERP",
            action="CUSTOM_PAUSE",
        )
        assert bp.action == "CUSTOM_PAUSE"


class TestBackpressureThrottle:
    def test_construction_with_required_fields(self):
        bt = BackpressureThrottle(
            idempotency_key="key-002",
            max_rate_per_sec=10,
            reason="queue buildup",
            signal_id="sig-002",
            symbol="ETH-PERP",
        )
        assert bt.max_rate_per_sec == 10
        assert bt.idempotency_key == "key-002"
        assert bt.reason == "queue buildup"
        assert bt.signal_id == "sig-002"
        assert bt.symbol == "ETH-PERP"

    def test_default_action(self):
        bt = BackpressureThrottle(
            idempotency_key="key-002",
            max_rate_per_sec=10,
            reason="buildup",
            signal_id="sig-002",
            symbol="ETH-PERP",
        )
        assert bt.action == "THROTTLE"

    def test_default_schema_version(self):
        bt = BackpressureThrottle(
            idempotency_key="key-002",
            max_rate_per_sec=10,
            reason="buildup",
            signal_id="sig-002",
            symbol="ETH-PERP",
        )
        assert bt.schema_version == "1.0"

    def test_default_trace_context(self):
        bt = BackpressureThrottle(
            idempotency_key="key-002",
            max_rate_per_sec=10,
            reason="buildup",
            signal_id="sig-002",
            symbol="ETH-PERP",
        )
        assert bt.trace_context is None

    def test_frozen_immutability(self):
        bt = BackpressureThrottle(
            idempotency_key="key-002",
            max_rate_per_sec=10,
            reason="buildup",
            signal_id="sig-002",
            symbol="ETH-PERP",
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            bt.max_rate_per_sec = 20

    def test_missing_required_field_raises(self):
        with pytest.raises(TypeError):
            BackpressureThrottle(
                max_rate_per_sec=10,
                reason="buildup",
            )


class TestBackpressureResume:
    def test_construction_with_required_fields(self):
        br = BackpressureResume(
            idempotency_key="key-003",
            reason="recovered",
            signal_id="sig-003",
            symbol="BTC-PERP",
        )
        assert br.idempotency_key == "key-003"
        assert br.reason == "recovered"
        assert br.signal_id == "sig-003"
        assert br.symbol == "BTC-PERP"

    def test_default_action(self):
        br = BackpressureResume(
            idempotency_key="key-003",
            reason="recovered",
            signal_id="sig-003",
            symbol="BTC-PERP",
        )
        assert br.action == "RESUME"

    def test_default_schema_version(self):
        br = BackpressureResume(
            idempotency_key="key-003",
            reason="recovered",
            signal_id="sig-003",
            symbol="BTC-PERP",
        )
        assert br.schema_version == "1.0"

    def test_default_trace_context(self):
        br = BackpressureResume(
            idempotency_key="key-003",
            reason="recovered",
            signal_id="sig-003",
            symbol="BTC-PERP",
        )
        assert br.trace_context is None

    def test_frozen_immutability(self):
        br = BackpressureResume(
            idempotency_key="key-003",
            reason="recovered",
            signal_id="sig-003",
            symbol="BTC-PERP",
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            br.reason = "new reason"

    def test_missing_required_field_raises(self):
        with pytest.raises(TypeError):
            BackpressureResume(
                reason="recovered",
            )


class TestCrossTypeDistinction:
    def test_different_actions(self):
        bp = BackpressurePause(
            duration_ms=5000,
            idempotency_key="k1",
            reason="r",
            signal_id="s1",
            symbol="A",
        )
        bt = BackpressureThrottle(
            idempotency_key="k2",
            max_rate_per_sec=10,
            reason="r",
            signal_id="s2",
            symbol="A",
        )
        br = BackpressureResume(
            idempotency_key="k3",
            reason="r",
            signal_id="s3",
            symbol="A",
        )
        assert bp.action != bt.action
        assert bt.action != br.action
        assert bp.action != br.action

    def test_equality_same_values(self):
        bp1 = BackpressurePause(
            duration_ms=5000,
            idempotency_key="k1",
            reason="r",
            signal_id="s1",
            symbol="A",
        )
        bp2 = BackpressurePause(
            duration_ms=5000,
            idempotency_key="k1",
            reason="r",
            signal_id="s1",
            symbol="A",
        )
        assert bp1 == bp2
