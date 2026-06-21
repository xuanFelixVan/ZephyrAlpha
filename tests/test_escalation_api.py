# [A_test] module_id: SRC-TST-0846 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md | §
# [MODULE] tests.test_escalation_api
# [INVARIANTS] 模块接口签名不可变
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/escalation-protocol/blueprint.md
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] tests/test_escalation_api.py

import pytest

from zephyr.governance.escalation_api import EscalationAPI


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
