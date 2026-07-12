# [A_test] module_id: SRC-TST-1676 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_stability_guard
# [INVARIANTS] lock_api returns locked=True; check_breaking returns list of removed export messages
# [MODIFY-GUARD] source-change-only
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] no exceptions for empty lists; returns empty list when no breaking changes
# [TESTS] test_stability_guard.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.orchestrator.quality.stability_guard import StabilityGuard


class TestStabilityGuard:
    @pytest.fixture()
    def guard(self):
        return StabilityGuard()

    def test_lock_api(self, guard):
        result = guard.lock_api("my_module", ["func_a", "func_b", "ClassC"])
        assert result["module"] == "my_module"
        assert result["exports"] == ["func_a", "func_b", "ClassC"]
        assert result["locked"] is True

    def test_lock_api_empty_exports(self, guard):
        result = guard.lock_api("empty_mod", [])
        assert result["module"] == "empty_mod"
        assert result["exports"] == []
        assert result["locked"] is True

    def test_lock_api_single_export(self, guard):
        result = guard.lock_api("single_mod", ["only_func"])
        assert len(result["exports"]) == 1

    def test_check_breaking_no_changes(self, guard):
        old = ["func_a", "func_b"]
        new = ["func_a", "func_b"]
        result = guard.check_breaking(old, new)
        assert result == []

    def test_check_breaking_removed_export(self, guard):
        old = ["func_a", "func_b", "func_c"]
        new = ["func_a", "func_c"]
        result = guard.check_breaking(old, new)
        assert len(result) == 1
        assert "func_b" in result[0]
        assert "BREAKING" in result[0]

    def test_check_breaking_multiple_removed(self, guard):
        old = ["a", "b", "c", "d"]
        new = ["a", "d"]
        result = guard.check_breaking(old, new)
        assert len(result) == 2

    def test_check_breaking_added_export_not_breaking(self, guard):
        old = ["func_a"]
        new = ["func_a", "func_b"]
        result = guard.check_breaking(old, new)
        assert result == []

    def test_check_breaking_all_removed(self, guard):
        old = ["x", "y", "z"]
        new = []
        result = guard.check_breaking(old, new)
        assert len(result) == 3

    def test_check_breaking_empty_old(self, guard):
        result = guard.check_breaking([], ["func_a"])
        assert result == []

    def test_check_breaking_both_empty(self, guard):
        result = guard.check_breaking([], [])
        assert result == []

    def test_check_breaking_message_format(self, guard):
        old = ["my_precious_func"]
        new = []
        result = guard.check_breaking(old, new)
        assert result[0] == "BREAKING: my_precious_func removed"
