# [A_test] module_id: SRC-TST-1498 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_runbook_executor
# [INVARIANTS] execute returns True only if runbook_id in runbooks
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_runbook_executor.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.runbook_executor import RunbookExecutor


class TestRunbookExecutorInstantiation:
    def test_default_runbooks_empty(self):
        obj = RunbookExecutor()
        assert obj.runbooks == {}

    def test_custom_runbooks(self):
        runbooks = {"rb-1": "restart_service", "rb-2": "clear_cache"}
        obj = RunbookExecutor(runbooks=runbooks)
        assert obj.runbooks == runbooks

    def test_runbooks_is_dict_type(self):
        obj = RunbookExecutor()
        assert isinstance(obj.runbooks, dict)


class TestRunbookExecutorExecute:
    def test_execute_existing_runbook(self):
        obj = RunbookExecutor(runbooks={"rb-1": "restart_service"})
        assert obj.execute("rb-1") is True

    def test_execute_nonexistent_runbook(self):
        obj = RunbookExecutor(runbooks={"rb-1": "restart_service"})
        assert obj.execute("rb-999") is False

    def test_execute_empty_runbooks(self):
        obj = RunbookExecutor()
        assert obj.execute("any") is False

    def test_execute_empty_string_id(self):
        obj = RunbookExecutor(runbooks={"": "noop"})
        assert obj.execute("") is True

    def test_execute_empty_string_id_not_present(self):
        obj = RunbookExecutor(runbooks={"rb-1": "restart"})
        assert obj.execute("") is False

    def test_execute_returns_bool(self):
        obj = RunbookExecutor(runbooks={"rb-1": "restart"})
        result = obj.execute("rb-1")
        assert isinstance(result, bool)
