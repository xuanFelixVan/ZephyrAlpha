# [A_test] module_id: MOD-GOV_auto_integrator | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] tests.test_auto_integrator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_auto_integrator.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.trading.auto_integrator import AutoIntegrator, IntegrationAnalysis
from zephyr.trading.capability_card import CapabilityCard, CapabilityCategory
from zephyr.trading.capability_registry import CapabilityRegistry
from zephyr.trading.module_onboarding_scanner import ModuleDiscovery, UnregisteredModule


def _make_module(
    module_name: str = "test_mod",
    package: str = "governance",
    has_class: bool = True,
    has_funcs: bool = True,
    has_blueprint: bool = False,
    docstring: str | None = "A test module",
    priority: str = "P1",
    suggested_layer: str = "local",
) -> UnregisteredModule:
    disc = ModuleDiscovery(
        module_path=f"src/zephyr/{package}/{module_name}.py",
        module_name=module_name,
        package=package,
        has_class=has_class,
        has_public_functions=has_funcs,
        has_blueprint=has_blueprint,
        docstring=docstring,
    )
    return UnregisteredModule(
        discovery=disc,
        priority=priority,
        suggested_layer=suggested_layer,
    )


class TestAutoIntegratorInit:
    def test_default_init(self, tmp_path):
        registry = CapabilityRegistry(card_dir=tmp_path)
        integrator = AutoIntegrator(registry)
        assert integrator._max_daily_l3 == 10
        assert integrator._daily_l3_count == 0

    def test_custom_max_daily(self, tmp_path):
        registry = CapabilityRegistry(card_dir=tmp_path)
        integrator = AutoIntegrator(registry, max_daily_l3_activations=5)
        assert integrator._max_daily_l3 == 5


class TestAutoIntegratorAnalyzeModule:
    def test_analyze_no_public_api(self, tmp_path):
        registry = CapabilityRegistry(card_dir=tmp_path)
        integrator = AutoIntegrator(registry)
        module = _make_module(has_class=False, has_funcs=False)
        analysis = integrator.analyze_module(module)
        assert analysis.should_integrate is False
        assert analysis.confidence >= 0.9
        assert "no public API" in analysis.reason

    def test_analyze_with_blueprint(self, tmp_path):
        registry = CapabilityRegistry(card_dir=tmp_path)
        integrator = AutoIntegrator(registry)
        module = _make_module(has_blueprint=True)
        analysis = integrator.analyze_module(module)
        assert analysis.should_integrate is True
        assert analysis.confidence == 0.85
        assert "blueprint" in analysis.reason

    def test_analyze_with_class_no_blueprint(self, tmp_path):
        registry = CapabilityRegistry(card_dir=tmp_path)
        integrator = AutoIntegrator(registry)
        module = _make_module(has_class=True, has_funcs=False, has_blueprint=False)
        analysis = integrator.analyze_module(module)
        assert analysis.should_integrate is True
        assert analysis.confidence == 0.75
        assert "class" in analysis.reason

    def test_analyze_with_funcs_only(self, tmp_path):
        registry = CapabilityRegistry(card_dir=tmp_path)
        integrator = AutoIntegrator(registry)
        module = _make_module(has_class=False, has_funcs=True, has_blueprint=False)
        analysis = integrator.analyze_module(module)
        assert analysis.should_integrate is True
        assert analysis.confidence == 0.6
        assert "functions" in analysis.reason

    def test_analyze_suggests_capability_card(self, tmp_path):
        registry = CapabilityRegistry(card_dir=tmp_path)
        integrator = AutoIntegrator(registry)
        module = _make_module(module_name="my_module", package="governance")
        analysis = integrator.analyze_module(module)
        assert analysis.suggested_capability_card is not None
        assert analysis.suggested_capability_card.category == CapabilityCategory.GOVERNANCE

    def test_analyze_suggested_priority_and_layer(self, tmp_path):
        registry = CapabilityRegistry(card_dir=tmp_path)
        integrator = AutoIntegrator(registry)
        module = _make_module(priority="P0", suggested_layer="cloud")
        analysis = integrator.analyze_module(module)
        assert analysis.suggested_priority == "P0"
        assert analysis.suggested_layer == "cloud"


class TestAutoIntegratorShouldIntegrate:
    def test_should_integrate_true(self, tmp_path):
        registry = CapabilityRegistry(card_dir=tmp_path)
        integrator = AutoIntegrator(registry)
        analysis = IntegrationAnalysis(
            module_path="x",
            should_integrate=True,
            confidence=0.8,
        )
        assert integrator.should_integrate(analysis) is True

    def test_should_not_integrate_low_confidence(self, tmp_path):
        registry = CapabilityRegistry(card_dir=tmp_path)
        integrator = AutoIntegrator(registry)
        analysis = IntegrationAnalysis(
            module_path="x",
            should_integrate=True,
            confidence=0.3,
        )
        assert integrator.should_integrate(analysis) is False

    def test_should_not_integrate_flag_false(self, tmp_path):
        registry = CapabilityRegistry(card_dir=tmp_path)
        integrator = AutoIntegrator(registry)
        analysis = IntegrationAnalysis(
            module_path="x",
            should_integrate=False,
            confidence=0.9,
        )
        assert integrator.should_integrate(analysis) is False


class TestAutoIntegratorGenerateCard:
    def test_generate_card_returns_card(self, tmp_path):
        registry = CapabilityRegistry(card_dir=tmp_path)
        integrator = AutoIntegrator(registry)
        card = CapabilityCard(
            capability_id="test-card",
            name="Test Card",
            category=CapabilityCategory.INFRA,
            description="test",
        )
        analysis = IntegrationAnalysis(module_path="x", suggested_capability_card=card)
        result = integrator.generate_card(analysis)
        assert result is not None
        assert result.capability_id == "test-card"

    def test_generate_card_none(self, tmp_path):
        registry = CapabilityRegistry(card_dir=tmp_path)
        integrator = AutoIntegrator(registry)
        analysis = IntegrationAnalysis(module_path="x", suggested_capability_card=None)
        assert integrator.generate_card(analysis) is None


class TestAutoIntegratorAutoRegister:
    def test_auto_register_high_confidence(self, tmp_path):
        registry = CapabilityRegistry(card_dir=tmp_path)
        integrator = AutoIntegrator(registry)
        card = CapabilityCard(
            capability_id="auto-reg",
            name="Auto Reg",
            category=CapabilityCategory.INFRA,
            description="auto",
        )
        analysis = IntegrationAnalysis(
            module_path="x",
            should_integrate=True,
            confidence=0.85,
            suggested_capability_card=card,
        )
        result = integrator.auto_register(analysis)
        assert result is True
        assert registry.get("auto-reg") is not None

    def test_auto_register_low_confidence(self, tmp_path):
        registry = CapabilityRegistry(card_dir=tmp_path)
        integrator = AutoIntegrator(registry)
        card = CapabilityCard(
            capability_id="low-conf",
            name="Low Conf",
            category=CapabilityCategory.INFRA,
            description="low",
        )
        analysis = IntegrationAnalysis(
            module_path="x",
            should_integrate=True,
            confidence=0.6,
            suggested_capability_card=card,
        )
        result = integrator.auto_register(analysis)
        assert result is False
        assert registry.get("low-conf") is None

    def test_auto_register_no_card(self, tmp_path):
        registry = CapabilityRegistry(card_dir=tmp_path)
        integrator = AutoIntegrator(registry)
        analysis = IntegrationAnalysis(
            module_path="x",
            should_integrate=True,
            confidence=0.9,
            suggested_capability_card=None,
        )
        assert integrator.auto_register(analysis) is False


class TestAutoIntegratorInferCategory:
    def test_infer_category_known_packages(self, tmp_path):
        registry = CapabilityRegistry(card_dir=tmp_path)
        integrator = AutoIntegrator(registry)
        assert integrator._infer_category("pipeline") == CapabilityCategory.ORCHESTRATION
        assert integrator._infer_category("gates") == CapabilityCategory.SECURITY
        assert integrator._infer_category("kb") == CapabilityCategory.DATA
        assert integrator._infer_category("mcp") == CapabilityCategory.INFRA

    def test_infer_category_unknown_defaults_infra(self, tmp_path):
        registry = CapabilityRegistry(card_dir=tmp_path)
        integrator = AutoIntegrator(registry)
        assert integrator._infer_category("unknown_pkg") == CapabilityCategory.INFRA


class TestAutoIntegratorDailyReset:
    def test_daily_reset(self, tmp_path):
        registry = CapabilityRegistry(card_dir=tmp_path)
        integrator = AutoIntegrator(registry)
        integrator._daily_l3_count = 5
        integrator._last_reset_date = "2000-01-01"
        integrator._check_daily_reset()
        assert integrator._daily_l3_count == 0
