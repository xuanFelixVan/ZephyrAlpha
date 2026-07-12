# [A_test] module_id: SRC-TST-0581 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_construction_guide
# [INVARIANTS] get_mock_strategy returns STUB for unknown; require_phase0_context_check returns bool
# [MODIFY-GUARD] src/zephyr/orchestrator/construction_guide.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] get_mock_strategy/require_phase0_context_check/is_dev_mode never raise
# [TESTS] tests/test_construction_guide.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.orchestrator.contracts.construction_guide import (
    MOCK_STRATEGIES,
    ConstructionConfig,
    ConstructionGuide,
    ConstructionMode,
    MockStrategy,
)


class TestMockStrategyEnum:
    def test_stub_value(self):
        assert MockStrategy.STUB == "stub"

    def test_partial_value(self):
        assert MockStrategy.PARTIAL == "partial"

    def test_full_value(self):
        assert MockStrategy.FULL == "full"


class TestConstructionModeEnum:
    def test_dev_value(self):
        assert ConstructionMode.DEV == "dev"

    def test_prod_value(self):
        assert ConstructionMode.PROD == "prod"


class TestConstructionConfigModel:
    def test_default_values(self):
        cfg = ConstructionConfig()
        assert cfg.mode == ConstructionMode.DEV
        assert cfg.cheap_model == "deepseek-chat"
        assert cfg.token_budget == 500
        assert cfg.skip_feishu is True
        assert cfg.phase0_check_required is True

    def test_prod_mode(self):
        cfg = ConstructionConfig(mode=ConstructionMode.PROD)
        assert cfg.mode == ConstructionMode.PROD


class TestConstructionGuideInstantiation:
    def test_default_dev_mode(self):
        guide = ConstructionGuide()
        assert guide.config.mode == ConstructionMode.DEV

    def test_prod_mode(self):
        guide = ConstructionGuide(mode=ConstructionMode.PROD)
        assert guide.config.mode == ConstructionMode.PROD


class TestGetMockStrategy:
    def test_known_contract(self):
        guide = ConstructionGuide()
        strategy = guide.get_mock_strategy("CT-ORC-SCRIPT-001")
        assert strategy == MockStrategy.PARTIAL

    def test_unknown_contract_returns_stub(self):
        guide = ConstructionGuide()
        strategy = guide.get_mock_strategy("CT-UNKNOWN-999")
        assert strategy == MockStrategy.STUB

    def test_empty_string_returns_stub(self):
        guide = ConstructionGuide()
        assert guide.get_mock_strategy("") == MockStrategy.STUB

    def test_full_strategy_contract(self):
        guide = ConstructionGuide()
        strategy = guide.get_mock_strategy("CT-ORC-VMS-001")
        assert strategy == MockStrategy.FULL


class TestRequirePhase0ContextCheck:
    def test_dev_mode_requires_check(self):
        guide = ConstructionGuide(mode=ConstructionMode.DEV)
        assert guide.require_phase0_context_check() is True


class TestIsDevMode:
    def test_dev_mode_true(self):
        guide = ConstructionGuide(mode=ConstructionMode.DEV)
        assert guide.is_dev_mode() is True

    def test_prod_mode_false(self):
        guide = ConstructionGuide(mode=ConstructionMode.PROD)
        assert guide.is_dev_mode() is False


class TestMockStrategiesData:
    def test_has_entries(self):
        assert len(MOCK_STRATEGIES) > 0

    def test_all_values_are_mock_strategy(self):
        for val in MOCK_STRATEGIES.values():
            assert isinstance(val, MockStrategy)


class TestBoundary:
    def test_config_property_returns_same_object(self):
        guide = ConstructionGuide()
        assert guide.config is guide.config

    def test_get_mock_strategy_all_known_ids(self):
        guide = ConstructionGuide()
        for cid in MOCK_STRATEGIES:
            result = guide.get_mock_strategy(cid)
            assert isinstance(result, MockStrategy)
