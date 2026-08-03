# [A_test] module_id: MOD-GOV_coldstart_manager | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_coldstart_manager
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] Imprint期不可跳过;渐进校准速率不可加速
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/escalation-protocol/blueprint.md
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] tests/test_coldstart_manager.py
# [TTL] task_bound


from zephyr.governance.ops_governance.coldstart_manager import ColdstartManager


class TestColdstartManagerInstantiation:
    def test_instantiation(self):
        cm = ColdstartManager()
        assert cm is not None

    def test_not_ready_initially(self):
        cm = ColdstartManager()
        assert cm.ready is False


class TestColdstartManagerInitialize:
    def test_initialize_returns_true(self):
        cm = ColdstartManager()
        result = cm.initialize()
        assert result is True

    def test_ready_after_initialize(self):
        cm = ColdstartManager()
        cm.initialize()
        assert cm.ready is True

    def test_initialize_idempotent(self):
        cm = ColdstartManager()
        cm.initialize()
        assert cm.initialize() is True
        assert cm.ready is True


class TestColdstartManagerHealthReport:
    def test_health_report_before_init(self):
        cm = ColdstartManager()
        report = cm.health_report()
        assert report["ready"] is False
        assert report["checks"] == {}

    def test_health_report_after_init(self):
        cm = ColdstartManager()
        cm.initialize()
        report = cm.health_report()
        assert report["ready"] is True
        assert report["checks"]["rules_loaded"] is True
        assert report["checks"]["engine_ready"] is True
        assert report["checks"]["adapter_ready"] is True

    def test_health_report_has_all_keys(self):
        cm = ColdstartManager()
        cm.initialize()
        report = cm.health_report()
        assert set(report["checks"].keys()) == {"rules_loaded", "engine_ready", "adapter_ready"}

    def test_health_report_returns_dict(self):
        cm = ColdstartManager()
        report = cm.health_report()
        assert isinstance(report, dict)
        assert isinstance(report["checks"], dict)
