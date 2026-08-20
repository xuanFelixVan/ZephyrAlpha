# [A_test] module_id: MOD-GOV_batch_fixer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §test
# [MODULE] tests.test_batch_fixer
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_batch_fixer.py
# [TTL] task_bound

from unittest.mock import MagicMock

import pytest

batch_mod = pytest.importorskip("zephyr.infrastructure.auto_fix_engine.batch_fixer", reason="batch_fixer not available")
BatchFixer = batch_mod.BatchFixer

models = pytest.importorskip("zephyr.infrastructure.auto_fix_engine.models", reason="models not available")
FixAction = models.FixAction
FixStatus = models.FixStatus
FixLevel = models.FixLevel
FixConfidence = models.FixConfidence
FixReport = models.FixReport

budget_mod = pytest.importorskip("zephyr.infrastructure.auto_fix_engine.fix_budget", reason="fix_budget not available")
FixBudget = budget_mod.FixBudget
FixStormGuard = budget_mod.FixStormGuard

reliability_mod = pytest.importorskip(
    "zephyr.infrastructure.auto_fix_engine.fix_reliability", reason="fix_reliability not available"
)
ConflictResolver = reliability_mod.ConflictResolver
IdempotencyGuard = reliability_mod.IdempotencyGuard


def _make_action(target="test_file.py", action_type="test_fix"):
    return FixAction(
        action_type=action_type,
        level=FixLevel.L1_RULE,
        target=target,
        confidence=FixConfidence.HIGH,
    )


def _mock_conflict_resolver():
    resolver = MagicMock(spec=ConflictResolver)
    resolver.resolve.side_effect = lambda actions: actions
    resolver.acquire.return_value = MagicMock(__enter__=MagicMock(), __exit__=MagicMock())
    return resolver


@pytest.fixture
def temp_db(tmp_path):
    return str(tmp_path / "test_batch.db")


@pytest.fixture
def batch_fixer(temp_db):
    budget = FixBudget(db_path=temp_db)
    storm_guard = FixStormGuard()
    idempotency = IdempotencyGuard(db_path=temp_db)
    conflict_resolver = _mock_conflict_resolver()
    return BatchFixer(
        max_workers=2,
        fix_budget=budget,
        storm_guard=storm_guard,
        idempotency_guard=idempotency,
        conflict_resolver=conflict_resolver,
    )


class TestBatchFixerInstantiation:
    def test_default_max_workers(self, temp_db):
        budget = FixBudget(db_path=temp_db)
        fixer = BatchFixer(fix_budget=budget)
        assert fixer.max_workers == 8

    def test_custom_max_workers(self, temp_db):
        budget = FixBudget(db_path=temp_db)
        fixer = BatchFixer(max_workers=4, fix_budget=budget)
        assert fixer.max_workers == 4

    def test_default_components_created(self, temp_db):
        budget = FixBudget(db_path=temp_db)
        fixer = BatchFixer(fix_budget=budget)
        assert fixer.budget is not None
        assert fixer.storm_guard is not None
        assert fixer.idempotency is not None
        assert fixer.conflict_resolver is not None


class TestBatchFixerExecuteBatch:
    def test_empty_actions_returns_report(self, batch_fixer):
        report = batch_fixer.execute_batch([], lambda a: a)
        assert isinstance(report, FixReport)
        assert report.total_attempted == 0

    def test_single_action_succeeds(self, batch_fixer):
        action = _make_action()

        def success_fn(a):
            a.status = FixStatus.COMPLETED
            return a

        report = batch_fixer.execute_batch([action], success_fn)
        assert report.total_attempted == 1
        assert report.succeeded == 1

    def test_multiple_actions(self, batch_fixer):
        actions = [_make_action(target=f"file_{i}.py") for i in range(3)]

        def success_fn(a):
            a.status = FixStatus.COMPLETED
            return a

        report = batch_fixer.execute_batch(actions, success_fn)
        assert report.total_attempted == 3
        assert report.succeeded == 3

    def test_failed_action_counted(self, batch_fixer):
        action = _make_action()

        def fail_fn(a):
            a.status = FixStatus.FAILED
            return a

        report = batch_fixer.execute_batch([action], fail_fn)
        assert report.failed >= 1

    def test_exception_in_fix_fn_handled(self, batch_fixer):
        action = _make_action()

        def raise_fn(a):
            raise RuntimeError("test error")

        report = batch_fixer.execute_batch([action], raise_fn)
        assert report.failed >= 1

    def test_report_has_budget_info(self, batch_fixer):
        action = _make_action()

        def success_fn(a):
            a.status = FixStatus.COMPLETED
            return a

        report = batch_fixer.execute_batch([action], success_fn)
        assert report.budget_remaining is not None


class TestBatchFixerStormGuard:
    def test_storm_guard_blocks_execution(self, temp_db):
        budget = FixBudget(db_path=temp_db)
        storm_config = {
            "short_window_sec": 60,
            "short_threshold": 1,
            "long_window_sec": 300,
            "long_threshold": 100,
            "cooldown_sec": 900,
        }
        storm_guard = FixStormGuard(config=storm_config)
        storm_guard.record()
        idempotency = IdempotencyGuard(db_path=temp_db)
        conflict_resolver = _mock_conflict_resolver()
        fixer = BatchFixer(
            max_workers=2,
            fix_budget=budget,
            storm_guard=storm_guard,
            idempotency_guard=idempotency,
            conflict_resolver=conflict_resolver,
        )
        actions = [_make_action()]

        def success_fn(a):
            a.status = FixStatus.COMPLETED
            return a

        report = fixer.execute_batch(actions, success_fn)
        assert len(report.cascade_alerts) > 0 or report.succeeded == 0 or report.total_attempted == 0
