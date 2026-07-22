# [A_test] module_id: MOD-GOV_prompt_lifecycle | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-418 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_prompt_lifecycle
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.infrastructure.a2a_protocol.prompt_lifecycle import (
    PROMPT_REGRESSION_THRESHOLD,
    PROMPT_STORE,
    PromptVersion,
)


class TestPromptVersion:
    def test_create_prompt_version(self):
        pv = PromptVersion(
            prompt_id="test-001",
            semantic_version="1.0.0",
            prompt_text="Hello world",
        )
        assert pv.prompt_id == "test-001"
        assert pv.semantic_version == "1.0.0"
        assert pv.prompt_text == "Hello world"

    def test_prompt_version_fields(self):
        pv = PromptVersion(prompt_id="x", semantic_version="0.1.0", prompt_text="test")
        assert hasattr(pv, "prompt_id")
        assert hasattr(pv, "semantic_version")
        assert hasattr(pv, "prompt_text")

    def test_prompt_version_equality(self):
        pv1 = PromptVersion(prompt_id="a", semantic_version="1.0.0", prompt_text="hello")
        pv2 = PromptVersion(prompt_id="a", semantic_version="1.0.0", prompt_text="hello")
        assert pv1 == pv2


class TestPromptRegressionThreshold:
    def test_threshold_value(self):
        assert PROMPT_REGRESSION_THRESHOLD == 0.05

    def test_threshold_is_float(self):
        assert isinstance(PROMPT_REGRESSION_THRESHOLD, float)

    def test_threshold_positive(self):
        assert PROMPT_REGRESSION_THRESHOLD > 0


class TestPromptStore:
    def test_store_is_dict(self):
        assert isinstance(PROMPT_STORE, dict)

    def test_store_can_add_entry(self):
        test_key = "__test_prompt_key__"
        pv = PromptVersion(prompt_id="test", semantic_version="1.0.0", prompt_text="test")
        PROMPT_STORE[test_key] = pv
        assert test_key in PROMPT_STORE
        assert PROMPT_STORE[test_key].prompt_id == "test"
        del PROMPT_STORE[test_key]
