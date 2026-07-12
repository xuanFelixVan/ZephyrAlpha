# [A_test] module_id: SRC-TST-0737 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_dependency_lock
# [INVARIANTS] 5 default deps; get returns "unknown" for missing pkg; check_safety returns empty list
# [MODIFY-GUARD] source-change-only
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] get returns "unknown" for unregistered packages; no exceptions raised
# [TESTS] test_dependency_lock.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.orchestrator.governance.dependency_lock import DependencyLock


class TestDependencyLock:
    @pytest.fixture()
    def lock(self):
        return DependencyLock()

    def test_get_known_package(self, lock):
        assert lock.get("pydantic") == ">=2.0"
        assert lock.get("pytest") == ">=8.0"
        assert lock.get("yaml") == ">=0.2"

    def test_get_builtin_package(self, lock):
        assert lock.get("sqlite3") == "builtin"
        assert lock.get("hashlib") == "builtin"

    def test_get_unknown_package(self, lock):
        assert lock.get("nonexistent_pkg") == "unknown"

    def test_get_empty_string(self, lock):
        assert lock.get("") == "unknown"

    def test_list_all(self, lock):
        all_deps = lock.list_all()
        assert isinstance(all_deps, dict)
        assert len(all_deps) == 5
        assert "pydantic" in all_deps
        assert "pytest" in all_deps
        assert "yaml" in all_deps
        assert "sqlite3" in all_deps
        assert "hashlib" in all_deps

    def test_list_all_returns_copy(self, lock):
        d1 = lock.list_all()
        d1["new_pkg"] = "1.0"
        d2 = lock.list_all()
        assert "new_pkg" not in d2

    def test_check_safety(self, lock):
        result = lock.check_safety()
        assert isinstance(result, list)
        assert len(result) == 0

    def test_default_deps_count(self, lock):
        all_deps = lock.list_all()
        assert len(all_deps) >= 5
