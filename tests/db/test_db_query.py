# [A_test] module_id: SRC-TST-0706 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-DATABASE | docs/03_modules/_cross_layer/database/blueprint.md
# [MODULE] tests.test_db_query
# [INVARIANTS] 只读查询; 不修改任务状态; TaskRepository 接口契约完整性验证
# [MODIFY-GUARD] task_repo.py 组合入口; base_repo.py _row_to_taskcard
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] tests/test_db_query.py
# [TTL] task_bound
# [HISTORY] 2026-07-16 ARCH-MIGRATION-CLOSE: 修复幽灵 QueryMixin 引用——原测试错误推断
#          zephyr.governance.observability_governance.query.QueryMixin（全代码库不存在），
#          实际期望验证的接口契约在 zephyr.governance.persistence.task_repo.TaskRepository。

from zephyr.governance.persistence.task_repo import TaskRepository


class TestTaskRepositoryInterface:
    """验证 TaskRepository 查询接口契约完整性（任务系统 SSoT L3 铁律）。"""

    def test_import(self):
        assert TaskRepository is not None

    def test_has_get_method(self):
        assert hasattr(TaskRepository, "get")

    def test_has_list_by_status(self):
        assert hasattr(TaskRepository, "list_by_status")

    def test_has_query_tasks(self):
        assert hasattr(TaskRepository, "query_tasks")

    def test_has_count_by_status(self):
        assert hasattr(TaskRepository, "count_by_status")

    def test_has_list_by_phase(self):
        assert hasattr(TaskRepository, "list_by_phase")

    def test_has_list_by_session(self):
        assert hasattr(TaskRepository, "list_by_session")

    def test_has_list_active(self):
        assert hasattr(TaskRepository, "list_active")

    def test_has_list_by_namespace(self):
        assert hasattr(TaskRepository, "list_by_namespace")

    def test_has_list_by_dependency(self):
        assert hasattr(TaskRepository, "list_by_dependency")

    def test_has_list_by_tag(self):
        assert hasattr(TaskRepository, "list_by_tag")

    def test_has_list_by_blocked_by(self):
        assert hasattr(TaskRepository, "list_by_blocked_by")

    def test_has_get_or_raise(self):
        assert hasattr(TaskRepository, "get_or_raise")


class TestTaskRepositoryReadOnly:
    def test_get_nonexistent_returns_none(self):
        repo = TaskRepository(enable_gate=False)
        result = repo.get("NONEXISTENT-99999")
        assert result is None

    def test_count_by_status(self):
        repo = TaskRepository(enable_gate=False)
        counts = repo.count_by_status()
        assert isinstance(counts, dict)
