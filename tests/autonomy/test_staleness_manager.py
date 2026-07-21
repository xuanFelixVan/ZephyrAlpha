# [A_test] module_id: MOD-GOV_staleness_manager | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_staleness_manager
# [INVARIANTS] exceeded_when_age_gt_ttl;mark_legacy_when_exceeded;active_when_within_ttl
# [MODIFY-GUARD] source-change-only
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.ExitCode
# [TESTS] test_staleness_manager.py
# [TTL] task_bound

from zephyr.autonomy_core.context.staleness_manager import StalenessManager, StalenessReport


class TestStalenessReport:
    def test_creation(self):
        r = StalenessReport(ke_id="ke-001", age_days=100.0, ttl_days=90.0, exceeded=True, proposed_action="mark_legacy")
        assert r.ke_id == "ke-001"
        assert r.exceeded is True
        assert r.proposed_action == "mark_legacy"


class TestStalenessManager:
    def test_fresh_ke(self):
        mgr = StalenessManager()
        report = mgr.check("ke-001", age_days=30.0, ttl_days=90.0)
        assert report.exceeded is False
        assert report.proposed_action == "active"

    def test_expired_ke(self):
        mgr = StalenessManager()
        report = mgr.check("ke-001", age_days=100.0, ttl_days=90.0)
        assert report.exceeded is True
        assert report.proposed_action == "mark_legacy"

    def test_exactly_at_ttl(self):
        mgr = StalenessManager()
        report = mgr.check("ke-001", age_days=90.0, ttl_days=90.0)
        assert report.exceeded is False
        assert report.proposed_action == "active"

    def test_one_day_over_ttl(self):
        mgr = StalenessManager()
        report = mgr.check("ke-001", age_days=91.0, ttl_days=90.0)
        assert report.exceeded is True

    def test_custom_ttl(self):
        mgr = StalenessManager()
        report = mgr.check("ke-001", age_days=15.0, ttl_days=10.0)
        assert report.exceeded is True

    def test_zero_age(self):
        mgr = StalenessManager()
        report = mgr.check("ke-001", age_days=0.0, ttl_days=90.0)
        assert report.exceeded is False

    def test_report_preserves_ke_id(self):
        mgr = StalenessManager()
        report = mgr.check("my-special-ke", age_days=50.0)
        assert report.ke_id == "my-special-ke"

    def test_default_ttl_is_90(self):
        mgr = StalenessManager()
        report = mgr.check("ke-001", age_days=50.0)
        assert report.ttl_days == 90.0
