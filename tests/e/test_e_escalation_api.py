# [A_test] module_id: MOD-GOV_e_escalation_api | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_escalation_api
# [INVARIANTS] test完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.escalation.escalation_api import EscalationAPI


class TestEscalationAPIInit:
    def test_default_state(self):
        api = EscalationAPI()
        assert api._api_keys == {}


class TestEscalationAPIRegisterService:
    def test_register_single(self):
        api = EscalationAPI()
        api.register_service("payment_svc", "key-123")
        assert api._api_keys["payment_svc"] == "key-123"

    def test_register_multiple(self):
        api = EscalationAPI()
        api.register_service("svc1", "k1")
        api.register_service("svc2", "k2")
        assert len(api._api_keys) == 2

    def test_register_overwrites(self):
        api = EscalationAPI()
        api.register_service("svc", "old-key")
        api.register_service("svc", "new-key")
        assert api._api_keys["svc"] == "new-key"


class TestEscalationAPIValidateRequest:
    def test_valid_request(self):
        api = EscalationAPI()
        api.register_service("svc", "key-123")
        ok, msg = api.validate_request("svc", "key-123", "op")
        assert ok is True
        assert msg == "OK"

    def test_unknown_service(self):
        api = EscalationAPI()
        ok, msg = api.validate_request("svc", "key-123", "op")
        assert ok is False
        assert msg == "Unknown service"

    def test_invalid_key(self):
        api = EscalationAPI()
        api.register_service("svc", "key-123")
        ok, msg = api.validate_request("svc", "wrong-key", "op")
        assert ok is False
        assert msg == "Invalid API key"


class TestEscalationAPITriggerEscalation:
    def test_valid_trigger(self):
        api = EscalationAPI()
        api.register_service("payment_svc", "key-abc")
        result = api.trigger_escalation("payment_svc", "key-abc", "payment_failed", {"txn_id": "123"})
        assert result["status"] == "escalated"
        assert result["operation"] == "payment_failed"
        assert result["service"] == "payment_svc"
        assert result["context"] == {"txn_id": "123"}

    def test_invalid_trigger(self):
        api = EscalationAPI()
        result = api.trigger_escalation("unknown", "key", "op")
        assert result["status"] == "rejected"
        assert "reason" in result

    def test_wrong_key_trigger(self):
        api = EscalationAPI()
        api.register_service("svc", "real-key")
        result = api.trigger_escalation("svc", "wrong-key", "op")
        assert result["status"] == "rejected"

    def test_default_context(self):
        api = EscalationAPI()
        api.register_service("svc", "key")
        result = api.trigger_escalation("svc", "key", "op")
        assert result["context"] == {}
