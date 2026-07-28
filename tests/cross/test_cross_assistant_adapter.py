# [A_test] module_id: MOD-GOV_cross_assistant_adapter | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_cross_assistant_adapter
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_cross_assistant_adapter.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.intelligence_governance.cross_assistant_adapter import SUPPORTED_IDES, CrossAssistantAdapter


class TestCrossAssistantAdapterInstantiation:
    def test_creates_instance_without_args(self):
        adapter = CrossAssistantAdapter()
        assert isinstance(adapter, CrossAssistantAdapter)

    def test_initial_adapters_empty(self):
        adapter = CrossAssistantAdapter()
        assert adapter.adapters == {}


class TestRegisterAdapter:
    def test_register_supported_ide(self):
        adapter = CrossAssistantAdapter()
        result = adapter.register_adapter("trae")
        assert result is True
        assert "trae" in adapter.adapters

    def test_register_all_supported_ides(self):
        adapter = CrossAssistantAdapter()
        for ide in SUPPORTED_IDES:
            assert adapter.register_adapter(ide) is True

    def test_register_unsupported_ide_returns_false(self):
        adapter = CrossAssistantAdapter()
        result = adapter.register_adapter("unknown_ide")
        assert result is False

    def test_register_with_config(self):
        adapter = CrossAssistantAdapter()
        config = {"endpoint": "http://localhost:8080", "version": "1.0"}
        result = adapter.register_adapter("cursor", config)
        assert result is True
        assert adapter.adapters["cursor"] == config

    def test_register_without_config_stores_empty_dict(self):
        adapter = CrossAssistantAdapter()
        adapter.register_adapter("windsurf")
        assert adapter.adapters["windsurf"] == {}

    def test_register_overwrites_existing(self):
        adapter = CrossAssistantAdapter()
        adapter.register_adapter("trae", {"v": "1"})
        adapter.register_adapter("trae", {"v": "2"})
        assert adapter.adapters["trae"] == {"v": "2"}

    def test_register_case_sensitive(self):
        adapter = CrossAssistantAdapter()
        result = adapter.register_adapter("TRAE")
        assert result is False


class TestTranslateRequest:
    def test_translate_for_registered_ide(self):
        adapter = CrossAssistantAdapter()
        adapter.register_adapter("trae")
        result = adapter.translate_request("trae", {"operation": "escalate"})
        assert result["ide"] == "trae"
        assert result["operation"] == "escalate"
        assert result["normalized"] is True

    def test_translate_for_unregistered_ide_returns_error(self):
        adapter = CrossAssistantAdapter()
        result = adapter.translate_request("trae", {"operation": "escalate"})
        assert "error" in result
        assert result["error"] == "Unsupported IDE"

    def test_translate_missing_operation_defaults_empty(self):
        adapter = CrossAssistantAdapter()
        adapter.register_adapter("cursor")
        result = adapter.translate_request("cursor", {})
        assert result["operation"] == ""

    def test_translate_preserves_operation(self):
        adapter = CrossAssistantAdapter()
        adapter.register_adapter("codex")
        result = adapter.translate_request("codex", {"operation": "validate"})
        assert result["operation"] == "validate"

    def test_translate_empty_request(self):
        adapter = CrossAssistantAdapter()
        adapter.register_adapter("wedata")
        result = adapter.translate_request("wedata", {})
        assert result["ide"] == "wedata"
        assert result["normalized"] is True


class TestListSupported:
    def test_returns_all_supported_ides(self):
        adapter = CrossAssistantAdapter()
        result = adapter.list_supported()
        assert set(result) == set(SUPPORTED_IDES)

    def test_result_is_list(self):
        adapter = CrossAssistantAdapter()
        result = adapter.list_supported()
        assert isinstance(result, list)

    def test_contains_five_ides(self):
        adapter = CrossAssistantAdapter()
        result = adapter.list_supported()
        assert len(result) == 5
