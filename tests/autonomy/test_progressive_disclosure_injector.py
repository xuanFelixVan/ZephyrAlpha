# [A_test] module_id: MOD-GOV_progressive_disclosure_injector | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_progressive_disclosure_injector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_progressive_disclosure_injector.py -q
# [TTL] task_bound
from __future__ import annotations

from zephyr.autonomy_core.progressive_disclosure_injector import (
    DisclosureResult,
    ProgressiveDisclosureInjector,
)


class TestDisclosureResult:
    def test_default_expanded_ke_id_is_empty(self):
        result = DisclosureResult(summary_injected=True, ke_ids_available=["KE-1"])
        assert result.expanded_ke_id == ""

    def test_all_fields_assigned(self):
        result = DisclosureResult(
            summary_injected=False,
            ke_ids_available=["KE-1", "KE-2"],
            expanded_ke_id="KE-1",
        )
        assert result.summary_injected is False
        assert result.ke_ids_available == ["KE-1", "KE-2"]
        assert result.expanded_ke_id == "KE-1"


class TestProgressiveDisclosureInjectorInstantiation:
    def test_can_instantiate(self):
        injector = ProgressiveDisclosureInjector()
        assert injector is not None


class TestInjectSummary:
    def test_returns_summary_injected_true(self):
        injector = ProgressiveDisclosureInjector()
        result = injector.inject_summary(["KE-1", "KE-2"])
        assert result.summary_injected is True

    def test_ke_ids_available_reflects_input(self):
        injector = ProgressiveDisclosureInjector()
        ke_ids = ["KE-A", "KE-B", "KE-C"]
        result = injector.inject_summary(ke_ids)
        assert result.ke_ids_available == ke_ids

    def test_empty_ke_ids_list(self):
        injector = ProgressiveDisclosureInjector()
        result = injector.inject_summary([])
        assert result.summary_injected is True
        assert result.ke_ids_available == []

    def test_single_ke_id(self):
        injector = ProgressiveDisclosureInjector()
        result = injector.inject_summary(["KE-ONLY"])
        assert result.ke_ids_available == ["KE-ONLY"]

    def test_result_is_disclosure_result_type(self):
        injector = ProgressiveDisclosureInjector()
        result = injector.inject_summary(["KE-1"])
        assert isinstance(result, DisclosureResult)


class TestExpand:
    def test_expand_returns_content_string(self):
        injector = ProgressiveDisclosureInjector()
        content = injector.expand("KE-42")
        assert content == "Full content for KE-42"

    def test_expand_different_ke_ids(self):
        injector = ProgressiveDisclosureInjector()
        assert injector.expand("KE-A") == "Full content for KE-A"
        assert injector.expand("KE-B") == "Full content for KE-B"

    def test_expand_empty_ke_id(self):
        injector = ProgressiveDisclosureInjector()
        content = injector.expand("")
        assert content == "Full content for "

    def test_expand_returns_string_type(self):
        injector = ProgressiveDisclosureInjector()
        result = injector.expand("KE-1")
        assert isinstance(result, str)
