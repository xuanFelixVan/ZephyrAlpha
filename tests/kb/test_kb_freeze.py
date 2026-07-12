# [A_test] module_id: SRC-TST-1164 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] tests.test_kb_freeze
# [INVARIANTS] FreezeCircuitBreaker must manage NORMAL/SAFE/FROZEN states; gate failures trigger safe mode
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path

from zephyr.gov_kb.freeze import (
    FreezeCircuitBreaker,
    FreezeMode,
    FreezeReason,
    FreezeRecord,
)


class TestFreezeMode:
    def test_enum_values(self):
        assert FreezeMode.NORMAL.value == "normal"
        assert FreezeMode.SAFE.value == "safe"
        assert FreezeMode.FROZEN.value == "frozen"


class TestFreezeReason:
    def test_enum_values(self):
        assert FreezeReason.MANUAL.value == "manual"
        assert FreezeReason.GATE_CASCADE_FAILURE.value == "gate_cascade_failure"
        assert FreezeReason.GHOST_VECTOR_BREACH.value == "ghost_vector_breach"
        assert FreezeReason.SECURITY_BREACH.value == "security_breach"
        assert FreezeReason.INTEGRITY_FAILURE.value == "integrity_failure"


class TestFreezeRecord:
    def test_creation(self):
        r = FreezeRecord(
            mode=FreezeMode.FROZEN,
            reason=FreezeReason.MANUAL,
            since="2026-01-01T00:00:00",
            triggered_by="test",
            details="test details",
        )
        assert r.mode == FreezeMode.FROZEN
        assert r.reason == FreezeReason.MANUAL
        assert r.details == "test details"


class TestFreezeCircuitBreaker:
    def test_initial_state_is_none(self, tmp_path: Path):
        cb = FreezeCircuitBreaker(project_root=tmp_path)
        assert cb.current_state() is None
        assert cb.is_frozen() is False
        assert cb.can_write() is True
        assert cb.can_read() is True

    def test_freeze(self, tmp_path: Path):
        cb = FreezeCircuitBreaker(project_root=tmp_path)
        record = cb.freeze(reason=FreezeReason.MANUAL, triggered_by="test")
        assert record.mode == FreezeMode.FROZEN
        assert cb.is_frozen() is True
        assert cb.can_write() is False
        assert cb.can_read() is False

    def test_safe_mode(self, tmp_path: Path):
        cb = FreezeCircuitBreaker(project_root=tmp_path)
        record = cb.safe_mode(reason=FreezeReason.MANUAL, triggered_by="test")
        assert record.mode == FreezeMode.SAFE
        assert cb.is_frozen() is True
        assert cb.can_write() is False
        assert cb.can_read() is True

    def test_unfreeze(self, tmp_path: Path):
        cb = FreezeCircuitBreaker(project_root=tmp_path)
        cb.freeze(reason=FreezeReason.MANUAL, triggered_by="test")
        record = cb.unfreeze(triggered_by="test")
        assert record.mode == FreezeMode.NORMAL
        assert cb.is_frozen() is False
        assert cb.can_write() is True
        assert cb.can_read() is True

    def test_state_path(self, tmp_path: Path):
        cb = FreezeCircuitBreaker(project_root=tmp_path)
        assert cb.state_path.parent.name == "snapshots"

    def test_current_state_persists(self, tmp_path: Path):
        cb1 = FreezeCircuitBreaker(project_root=tmp_path)
        cb1.freeze(reason=FreezeReason.SECURITY_BREACH, triggered_by="scanner", details="XSS detected")
        cb2 = FreezeCircuitBreaker(project_root=tmp_path)
        state = cb2.current_state()
        assert state is not None
        assert state.mode == FreezeMode.FROZEN
        assert state.reason == FreezeReason.SECURITY_BREACH

    def test_record_gate_failure_below_threshold(self, tmp_path: Path):
        cb = FreezeCircuitBreaker(project_root=tmp_path)
        triggered = cb.record_gate_failure("G1")
        assert triggered is False
        triggered = cb.record_gate_failure("G1")
        assert triggered is False

    def test_record_gate_failure_triggers_safe_mode(self, tmp_path: Path):
        cb = FreezeCircuitBreaker(project_root=tmp_path)
        cb.record_gate_failure("G1")
        cb.record_gate_failure("G1")
        triggered = cb.record_gate_failure("G1")
        assert triggered is True
        assert cb.is_frozen() is True
        state = cb.current_state()
        assert state.reason == FreezeReason.GATE_CASCADE_FAILURE

    def test_reset_gate_failures(self, tmp_path: Path):
        cb = FreezeCircuitBreaker(project_root=tmp_path)
        cb.record_gate_failure("G1")
        cb.record_gate_failure("G1")
        cb.reset_gate_failures("G1")
        cb.record_gate_failure("G1")
        assert cb.is_frozen() is False

    def test_evaluate_ghost_ratio_below_threshold(self, tmp_path: Path):
        cb = FreezeCircuitBreaker(project_root=tmp_path)
        triggered = cb.evaluate_ghost_ratio(100, 90)
        assert triggered is False

    def test_evaluate_ghost_ratio_above_threshold(self, tmp_path: Path):
        cb = FreezeCircuitBreaker(project_root=tmp_path)
        triggered = cb.evaluate_ghost_ratio(100, 50)
        assert triggered is True
        state = cb.current_state()
        assert state.reason == FreezeReason.GHOST_VECTOR_BREACH

    def test_evaluate_ghost_ratio_zero_md(self, tmp_path: Path):
        cb = FreezeCircuitBreaker(project_root=tmp_path)
        triggered = cb.evaluate_ghost_ratio(0, 10)
        assert triggered is False

    def test_security_breach_detected(self, tmp_path: Path):
        cb = FreezeCircuitBreaker(project_root=tmp_path)
        record = cb.security_breach_detected("XSS")
        assert record.mode == FreezeMode.FROZEN
        assert record.reason == FreezeReason.SECURITY_BREACH
        assert "XSS" in record.details

    def test_integrity_breach_detected(self, tmp_path: Path):
        cb = FreezeCircuitBreaker(project_root=tmp_path)
        record = cb.integrity_breach_detected("file.md", "abc123def456", "xyz789uvw012")
        assert record.mode == FreezeMode.FROZEN
        assert record.reason == FreezeReason.INTEGRITY_FAILURE
        assert "file.md" in record.details

    def test_corrupted_lock_file_returns_none(self, tmp_path: Path):
        cb = FreezeCircuitBreaker(project_root=tmp_path)
        lock_path = cb.state_path
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        lock_path.write_text("invalid json{{{", encoding="utf-8")
        assert cb.current_state() is None
