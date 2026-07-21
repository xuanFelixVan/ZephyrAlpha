# [A_test] module_id: MOD-GOV_scope_guard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-427 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_scope_guard
# [INVARIANTS] ScopeGuard is per-instance; no shared state
# [MODIFY-GUARD] scope_guard.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] no raises expected
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path

from zephyr.infrastructure.lifecycle.scope_guard import (
    ScopeDrift,
    ScopeGuard,
    ScopeGuardConfig,
)


class TestScopeDrift:
    def test_creation(self):
        drift = ScopeDrift(
            task_id="T1",
            expected_touch=["a.py", "b.py"],
            actual_touch=["a.py", "b.py", "c.py"],
            extra_touch=["c.py"],
            severity="LOW",
            timestamp_utc="2026-01-01T00:00:00Z",
        )
        assert drift.task_id == "T1"
        assert drift.extra_touch == ["c.py"]
        assert drift.severity == "LOW"


class TestScopeGuardConfig:
    def test_defaults(self):
        cfg = ScopeGuardConfig()
        assert cfg.max_extra_touch == 3
        assert cfg.auto_block_on_critical is True
        assert cfg.warn_on_extra is True

    def test_custom(self):
        cfg = ScopeGuardConfig(
            max_extra_touch=5,
            auto_block_on_critical=False,
            warn_on_extra=False,
        )
        assert cfg.max_extra_touch == 5
        assert cfg.auto_block_on_critical is False


class TestScopeGuardInit:
    def test_default_root(self):
        guard = ScopeGuard()
        assert guard._project_root == Path.cwd()

    def test_custom_root(self, tmp_path):
        guard = ScopeGuard(project_root=tmp_path)
        assert guard._project_root == tmp_path


class TestScopeGuardValidateScope:
    def test_no_drift(self):
        guard = ScopeGuard()
        card = {
            "task_id": "T1",
            "allowed_touch": ["a.py", "b.py"],
            "upstream_files": [],
            "downstream_outputs": [],
        }
        result = guard.validate_scope(card, ["a.py", "b.py"])
        assert result is None

    def test_single_extra_low_severity(self):
        guard = ScopeGuard()
        card = {
            "task_id": "T1",
            "allowed_touch": ["a.py"],
            "upstream_files": [],
            "downstream_outputs": [],
        }
        result = guard.validate_scope(card, ["a.py", "c.py"])
        assert result is not None
        assert result.severity == "LOW"
        assert "c.py" in result.extra_touch

    def test_multiple_extra_high_severity(self):
        guard = ScopeGuard()
        card = {
            "task_id": "T1",
            "allowed_touch": ["a.py"],
            "upstream_files": [],
            "downstream_outputs": [],
        }
        result = guard.validate_scope(card, ["a.py", "c.py", "d.py"])
        assert result is not None
        assert result.severity == "HIGH"

    def test_many_extra_critical_severity(self):
        guard = ScopeGuardConfig(max_extra_touch=3)
        guard = ScopeGuard()
        card = {
            "task_id": "T1",
            "allowed_touch": ["a.py"],
            "upstream_files": [],
            "downstream_outputs": [],
        }
        result = guard.validate_scope(card, ["a.py", "c.py", "d.py", "e.py", "f.py"])
        assert result is not None
        assert result.severity == "CRITICAL"

    def test_upstream_files_included(self):
        guard = ScopeGuard()
        card = {
            "task_id": "T1",
            "allowed_touch": ["a.py"],
            "upstream_files": ["b.py"],
            "downstream_outputs": [],
        }
        result = guard.validate_scope(card, ["a.py", "b.py"])
        assert result is None

    def test_downstream_outputs_included(self):
        guard = ScopeGuard()
        card = {
            "task_id": "T1",
            "allowed_touch": ["a.py"],
            "upstream_files": [],
            "downstream_outputs": [{"path": "out.py"}],
        }
        result = guard.validate_scope(card, ["a.py", "out.py"])
        assert result is None

    def test_empty_task_card(self):
        guard = ScopeGuard()
        card = {}
        result = guard.validate_scope(card, ["a.py"])
        assert result is not None
        assert result.severity == "LOW"

    def test_empty_actual_touch(self):
        guard = ScopeGuard()
        card = {
            "task_id": "T1",
            "allowed_touch": ["a.py"],
            "upstream_files": [],
            "downstream_outputs": [],
        }
        result = guard.validate_scope(card, [])
        assert result is None

    def test_upstream_files_dict_format(self):
        guard = ScopeGuard()
        card = {
            "task_id": "T1",
            "allowed_touch": ["a.py"],
            "upstream_files": [{"file_path": "b.py"}],
            "downstream_outputs": [],
        }
        result = guard.validate_scope(card, ["a.py", "b.py"])
        assert result is None


class TestScopeGuardBlocking:
    def test_critical_auto_blocks(self):
        guard = ScopeGuard()
        card = {
            "task_id": "T1",
            "allowed_touch": ["a.py"],
            "upstream_files": [],
            "downstream_outputs": [],
        }
        guard.validate_scope(card, ["a.py", "c.py", "d.py", "e.py", "f.py"])
        assert guard.is_blocked("T1") is True

    def test_low_does_not_block(self):
        guard = ScopeGuard()
        card = {
            "task_id": "T1",
            "allowed_touch": ["a.py"],
            "upstream_files": [],
            "downstream_outputs": [],
        }
        guard.validate_scope(card, ["a.py", "c.py"])
        assert guard.is_blocked("T1") is False

    def test_unblock(self):
        guard = ScopeGuard()
        card = {
            "task_id": "T1",
            "allowed_touch": ["a.py"],
            "upstream_files": [],
            "downstream_outputs": [],
        }
        guard.validate_scope(card, ["a.py", "c.py", "d.py", "e.py", "f.py"])
        assert guard.is_blocked("T1") is True
        guard.unblock("T1")
        assert guard.is_blocked("T1") is False

    def test_is_blocked_unknown_task(self):
        guard = ScopeGuard()
        assert guard.is_blocked("unknown") is False

    def test_no_auto_block_when_disabled(self):
        cfg = ScopeGuardConfig(auto_block_on_critical=False)
        guard = ScopeGuard()
        guard._config = cfg
        card = {
            "task_id": "T1",
            "allowed_touch": ["a.py"],
            "upstream_files": [],
            "downstream_outputs": [],
        }
        guard.validate_scope(card, ["a.py", "c.py", "d.py", "e.py", "f.py"])
        assert guard.is_blocked("T1") is False


class TestScopeGuardDriftHistory:
    def test_empty_history(self):
        guard = ScopeGuard()
        assert guard.get_drift_history() == []

    def test_history_recorded(self):
        guard = ScopeGuard()
        card = {
            "task_id": "T1",
            "allowed_touch": ["a.py"],
            "upstream_files": [],
            "downstream_outputs": [],
        }
        guard.validate_scope(card, ["a.py", "c.py"])
        history = guard.get_drift_history()
        assert len(history) == 1
        assert history[0].task_id == "T1"

    def test_history_filtered_by_task(self):
        guard = ScopeGuard()
        card1 = {
            "task_id": "T1",
            "allowed_touch": ["a.py"],
            "upstream_files": [],
            "downstream_outputs": [],
        }
        card2 = {
            "task_id": "T2",
            "allowed_touch": ["x.py"],
            "upstream_files": [],
            "downstream_outputs": [],
        }
        guard.validate_scope(card1, ["a.py", "c.py"])
        guard.validate_scope(card2, ["x.py", "y.py"])
        t1_history = guard.get_drift_history("T1")
        assert len(t1_history) == 1
        assert t1_history[0].task_id == "T1"

    def test_no_drift_no_history(self):
        guard = ScopeGuard()
        card = {
            "task_id": "T1",
            "allowed_touch": ["a.py"],
            "upstream_files": [],
            "downstream_outputs": [],
        }
        guard.validate_scope(card, ["a.py"])
        assert guard.get_drift_history() == []
