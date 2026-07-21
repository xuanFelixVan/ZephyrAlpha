# [A_test] module_id: MOD-GOV_escalation_api | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_escalation_api
# [INVARIANTS] 模块接口签名不可变
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] tests/test_escalation_api.py
# [TTL] task_bound


from zephyr.governance.escalation.escalation_api import EscalationAPI


class TestEscalationAPIInstantiation:
    def test_instantiation(self):
        api = EscalationAPI()
        assert api is not None

    def test_empty_api_keys(self):
        api = EscalationAPI()
        assert api._api_keys == {}


class TestRegisterService:
    def test_register_service(self):
        api = EscalationAPI()
        api.register_service("monitoring", "key-123")
        assert api._api_keys["monitoring"] == "key-123"

    def test_register_multiple_services(self):
        api = EscalationAPI()
        api.register_service("monitoring", "key-1")
        api.register_service("deployer", "key-2")
        assert len(api._api_keys) == 2

    def test_register_overwrites(self):
        api = EscalationAPI()
        api.register_service("svc", "old-key")
        api.register_service("svc", "new-key")
        assert api._api_keys["svc"] == "new-key"


class TestValidateRequest:
    def test_valid_request(self):
        api = EscalationAPI()
        api.register_service("svc", "key-1")
        ok, msg = api.validate_request("svc", "key-1", "escalate")
        assert ok is True
        assert msg == "OK"

    def test_unknown_service(self):
        api = EscalationAPI()
        ok, msg = api.validate_request("unknown", "key-1", "escalate")
        assert ok is False
        assert msg == "Unknown service"

    def test_invalid_api_key(self):
        api = EscalationAPI()
        api.register_service("svc", "key-1")
        ok, msg = api.validate_request("svc", "wrong-key", "escalate")
        assert ok is False
        assert msg == "Invalid API key"

    def test_empty_api_key(self):
        api = EscalationAPI()
        api.register_service("svc", "key-1")
        ok, msg = api.validate_request("svc", "", "escalate")
        assert ok is False


class TestTriggerEscalation:
    def test_valid_escalation(self):
        api = EscalationAPI()
        api.register_service("svc", "key-1")
        result = api.trigger_escalation("svc", "key-1", "restart", {"reason": "timeout"})
        assert result["status"] == "escalated"
        assert result["operation"] == "restart"
        assert result["service"] == "svc"
        assert result["context"] == {"reason": "timeout"}

    def test_rejected_escalation(self):
        api = EscalationAPI()
        result = api.trigger_escalation("unknown", "bad-key", "restart")
        assert result["status"] == "rejected"
        assert "reason" in result

    def test_escalation_without_context(self):
        api = EscalationAPI()
        api.register_service("svc", "key-1")
        result = api.trigger_escalation("svc", "key-1", "restart")
        assert result["status"] == "escalated"
        assert result["context"] == {}

    def test_escalation_with_none_context(self):
        api = EscalationAPI()
        api.register_service("svc", "key-1")
        result = api.trigger_escalation("svc", "key-1", "restart", None)
        assert result["status"] == "escalated"
        assert result["context"] == {}


class TestRateLimiting:
    def test_rate_limit_allows_under_limit(self):
        api = EscalationAPI(rate_limit_per_hour=5)
        api.register_service("svc", "key-1")
        for _ in range(5):
            result = api.trigger_escalation("svc", "key-1", "op")
            assert result["status"] == "escalated"

    def test_rate_limit_blocks_over_limit(self):
        api = EscalationAPI(rate_limit_per_hour=2)
        api.register_service("svc", "key-1")
        api.trigger_escalation("svc", "key-1", "op1")
        api.trigger_escalation("svc", "key-1", "op2")
        result = api.trigger_escalation("svc", "key-1", "op3")
        assert result["status"] == "rate_limited"

    def test_rate_limit_independent_per_service(self):
        api = EscalationAPI(rate_limit_per_hour=1)
        api.register_service("svc1", "key-1")
        api.register_service("svc2", "key-2")
        r1 = api.trigger_escalation("svc1", "key-1", "op")
        r2 = api.trigger_escalation("svc2", "key-2", "op")
        assert r1["status"] == "escalated"
        assert r2["status"] == "escalated"


class TestAuditLog:
    def test_audit_log_records_escalation(self):
        api = EscalationAPI()
        api.register_service("svc", "key-1")
        api.trigger_escalation("svc", "key-1", "restart", {"reason": "timeout"})
        log = api.get_audit_log()
        assert len(log) == 1
        assert log[0]["status"] == "escalated"
        assert log[0]["service"] == "svc"
        assert log[0]["operation"] == "restart"

    def test_audit_log_records_rejection(self):
        api = EscalationAPI()
        api.trigger_escalation("unknown", "bad-key", "op")
        log = api.get_audit_log()
        assert len(log) == 1
        assert log[0]["status"] == "rejected"

    def test_clear_audit_log(self):
        api = EscalationAPI()
        api.register_service("svc", "key-1")
        api.trigger_escalation("svc", "key-1", "op")
        assert len(api.get_audit_log()) == 1
        api.clear_audit_log()
        assert len(api.get_audit_log()) == 0


class TestEngineIntegration:
    def test_engine_integration_adds_result(self):
        class MockEngine:
            def evaluate(self, category, description, owner_id):
                class MockEvent:
                    event_id = "evt-001"
                    level = "L1"
                    state = "EVALUATING"

                return MockEvent()

        api = EscalationAPI(engine=MockEngine())
        api.register_service("svc", "key-1")
        result = api.trigger_escalation("svc", "key-1", "op")
        assert result["status"] == "escalated"
        assert "engine_result" in result
        assert result["engine_result"]["event_id"] == "evt-001"

    def test_engine_failure_does_not_block(self):
        class FailingEngine:
            def evaluate(self, category, description, owner_id):
                raise RuntimeError("engine down")

        api = EscalationAPI(engine=FailingEngine())
        api.register_service("svc", "key-1")
        result = api.trigger_escalation("svc", "key-1", "op")
        assert result["status"] == "escalated"
        assert "engine_result" not in result
