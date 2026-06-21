# [A_test] module_id: SRC-TST-0706 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-012 | docs/03_modules/_cross_layer/database/blueprint.md
# [MODULE] tests.test_db_query
# [INVARIANTS] 只读查询; 不修改任务状态; QueryMixin 无副作用
# [MODIFY-GUARD] task_repo.py 组合入口; base_repo.py _row_to_taskcard
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] tests/test_db_query.py

import pytest

from zephyr.governance.persistence.base_repo import TaskNotFoundError
from zephyr.governance.query import QueryMixin
from zephyr.governance.rule_enforcement.task_types import TaskStatus


class TestQueryMixinImport:
    def test_import(self):
        assert QueryMixin is not None

    def test_has_get_method(self):
        assert hasattr(QueryMixin, "get")

    def test_has_list_by_status(self):
        assert hasattr(QueryMixin, "list_by_status")

    def test_has_query_tasks(self):
        assert hasattr(QueryMixin, "query_tasks")

    def test_has_count_by_status(self):
        assert hasattr(QueryMixin, "count_by_status")

    def test_has_list_by_phase(self):
        assert hasattr(QueryMixin, "list_by_phase")

    def test_has_list_by_session(self):
        assert hasattr(QueryMixin, "list_by_session")

    def test_has_list_active(self):
        assert hasattr(QueryMixin, "list_active")

    def test_has_list_by_namespace(self):
        assert hasattr(QueryMixin, "list_by_namespace")

    def test_has_list_by_dependency(self):
        assert hasattr(QueryMixin, "list_by_dependency")

    def test_has_list_by_tag(self):
        assert hasattr(QueryMixin, "list_by_tag")

    def test_has_list_by_blocked_by(self):
        assert hasattr(QueryMixin, "list_by_blocked_by")

    def test_has_get_or_raise(self):
        assert hasattr(QueryMixin, "get_or_raise")


class TestQueryMixinViaTaskRepo:
    def test_get_nonexistent_returns_none(self):
        import sys
        sys.path.insert(0, "src")
        from zephyr.governance.persistence.task_repo import TaskRepository
        repo = TaskRepository(enable_gate=False)
        result = repo.get("NONEXISTENT-99999")
        assert result is None

    def test_count_by_status(self):
        import sys
        sys.path.insert(0, "src")
        from zephyr.governance.persistence.task_repo import TaskRepository
        repo = TaskRepository(enable_gate=False)
        counts = repo.count_by_status()
        assert isinstance(counts, dict)
