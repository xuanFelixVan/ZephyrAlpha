# [A_test] module_id: SRC-TST-1196 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §test
# [MODULE] tests.test_knowledge_freshness
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_knowledge_freshness.py
# [TTL] task_bound

from datetime import UTC, datetime, timedelta

from zephyr.orchestrator.quality.knowledge_freshness import KnowledgeFreshnessManager


class TestKnowledgeFreshnessManagerInstantiation:
    def test_create_instance(self):
        mgr = KnowledgeFreshnessManager()
        assert mgr is not None

    def test_has_is_stale_method(self):
        mgr = KnowledgeFreshnessManager()
        assert callable(mgr.is_stale)

    def test_has_should_deprecate_method(self):
        mgr = KnowledgeFreshnessManager()
        assert callable(mgr.should_deprecate)

    def test_max_age_days(self):
        mgr = KnowledgeFreshnessManager()
        assert mgr.MAX_AGE_DAYS == 90


class TestIsStale:
    def test_fresh_entry(self):
        mgr = KnowledgeFreshnessManager()
        now = datetime.now(UTC)
        assert mgr.is_stale(now) is False

    def test_entry_just_under_max_age(self):
        mgr = KnowledgeFreshnessManager()
        created = datetime.now(UTC) - timedelta(days=89)
        assert mgr.is_stale(created) is False

    def test_entry_at_max_age(self):
        mgr = KnowledgeFreshnessManager()
        created = datetime.now(UTC) - timedelta(days=90)
        assert mgr.is_stale(created) is False

    def test_stale_entry(self):
        mgr = KnowledgeFreshnessManager()
        created = datetime.now(UTC) - timedelta(days=91)
        assert mgr.is_stale(created) is True

    def test_very_old_entry(self):
        mgr = KnowledgeFreshnessManager()
        created = datetime.now(UTC) - timedelta(days=365)
        assert mgr.is_stale(created) is True

    def test_entry_one_day_old(self):
        mgr = KnowledgeFreshnessManager()
        created = datetime.now(UTC) - timedelta(days=1)
        assert mgr.is_stale(created) is False


class TestShouldDeprecate:
    def test_delegates_to_is_stale(self):
        mgr = KnowledgeFreshnessManager()
        now = datetime.now(UTC)
        assert mgr.should_deprecate(now) is False

    def test_stale_entry_should_deprecate(self):
        mgr = KnowledgeFreshnessManager()
        created = datetime.now(UTC) - timedelta(days=100)
        assert mgr.should_deprecate(created) is True

    def test_fresh_entry_should_not_deprecate(self):
        mgr = KnowledgeFreshnessManager()
        created = datetime.now(UTC) - timedelta(days=10)
        assert mgr.should_deprecate(created) is False
