# [A_test] module_id: SRC-TST-1404 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_prompt_factory_governance
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.evolution.prompt_factory_governance
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_prompt_factory_governance.py
# [TTL] task_bound


from zephyr.feedback_loop.evolution.prompt_factory_governance import (
    PromptFactoryGovernance,
)


class TestPromptFactoryGovernanceInstantiation:
    def test_default_instantiation(self):
        obj = PromptFactoryGovernance()
        assert obj is not None
        assert obj.variants == {}

    def test_is_dataclass(self):
        obj = PromptFactoryGovernance()
        assert hasattr(obj, "__dataclass_fields__")


class TestPromptFactoryGovernanceRegister:
    def test_register_first_variant(self):
        pfg = PromptFactoryGovernance()
        variant = pfg.register(template_id="diag_v1", content="Diagnose {symptom}")
        assert variant.template_id == "diag_v1"
        assert variant.version == 1
        assert variant.variant_id == "diag_v1-v1"

    def test_register_increments_version(self):
        pfg = PromptFactoryGovernance()
        pfg.register(template_id="t1", content="content_a")
        v2 = pfg.register(template_id="t1", content="content_b")
        assert v2.version == 2
        assert v2.variant_id == "t1-v2"

    def test_register_computes_hash(self):
        pfg = PromptFactoryGovernance()
        variant = pfg.register(template_id="t1", content="hello")
        assert len(variant.content_hash) == 12
        assert isinstance(variant.content_hash, str)

    def test_register_different_templates(self):
        pfg = PromptFactoryGovernance()
        pfg.register(template_id="t1", content="a")
        pfg.register(template_id="t2", content="b")
        assert "t1" in pfg.variants
        assert "t2" in pfg.variants


class TestPromptFactoryGovernanceLatest:
    def test_latest_returns_newest(self):
        pfg = PromptFactoryGovernance()
        pfg.register(template_id="t1", content="first")
        pfg.register(template_id="t1", content="second")
        latest = pfg.latest(template_id="t1")
        assert latest is not None
        assert latest.content == "second"

    def test_latest_unknown_template(self):
        pfg = PromptFactoryGovernance()
        result = pfg.latest(template_id="nonexistent")
        assert result is None

    def test_latest_single_variant(self):
        pfg = PromptFactoryGovernance()
        pfg.register(template_id="t1", content="only")
        latest = pfg.latest(template_id="t1")
        assert latest is not None
        assert latest.version == 1


class TestPromptFactoryGovernanceBoundaries:
    def test_register_empty_content(self):
        pfg = PromptFactoryGovernance()
        variant = pfg.register(template_id="t1", content="")
        assert variant.content == ""
        assert len(variant.content_hash) == 12

    def test_register_very_long_content(self):
        pfg = PromptFactoryGovernance()
        long_content = "x" * 100000
        variant = pfg.register(template_id="t1", content=long_content)
        assert variant.content == long_content

    def test_many_versions(self):
        pfg = PromptFactoryGovernance()
        for i in range(50):
            pfg.register(template_id="t1", content=f"v{i}")
        assert len(pfg.variants["t1"]) == 50
        assert pfg.latest(template_id="t1").version == 50
