# [A_test] module_id: SRC-TST-0522 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-012 | docs/03_modules/_cross_layer/database/blueprint.md | §test
# [MODULE] tests.test_circuit_breaker_types
# [INVARIANTS] Values MUST align with shared.schema.severity_types.CircuitBreakerState
# [MODIFY-GUARD] src/zephyr/db/circuit_breaker_types.py
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] tests/test_circuit_breaker_types.py

from __future__ import annotations

import pytest

cbt_mod = pytest.importorskip("zephyr.data.persistence.circuit_breaker_types")
CircuitBreakerState = cbt_mod.CircuitBreakerState


class TestCircuitBreakerStateEnum:
    def test_closed_value(self):
        assert CircuitBreakerState.CLOSED.value == "CLOSED"

    def test_open_value(self):
        assert CircuitBreakerState.OPEN.value == "OPEN"

    def test_half_open_value(self):
        assert CircuitBreakerState.HALF_OPEN.value == "HALF_OPEN"

    def test_member_count(self):
        assert len(CircuitBreakerState) == 3

    def test_is_str_enum(self):
        assert isinstance(CircuitBreakerState.CLOSED, str)

    def test_from_value(self):
        assert CircuitBreakerState("CLOSED") == CircuitBreakerState.CLOSED
        assert CircuitBreakerState("OPEN") == CircuitBreakerState.OPEN
        assert CircuitBreakerState("HALF_OPEN") == CircuitBreakerState.HALF_OPEN

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError):
            CircuitBreakerState("INVALID")

    def test_iteration(self):
        values = [s.value for s in CircuitBreakerState]
        assert "CLOSED" in values
        assert "OPEN" in values
        assert "HALF_OPEN" in values
