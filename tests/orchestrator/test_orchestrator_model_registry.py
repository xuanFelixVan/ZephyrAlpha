# [A_test] module_id: SRC-TST-1338 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §test
# [MODULE] tests.test_orchestrator_model_registry
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_orchestrator_model_registry.py
# [TTL] task_bound


from zephyr.orchestrator.governance.model_registry import MODELS, ModelRegistry


class TestModelRegistryInstantiation:
    def test_create_instance(self):
        registry = ModelRegistry()
        assert registry is not None

    def test_has_get_method(self):
        registry = ModelRegistry()
        assert callable(registry.get)

    def test_has_list_all_method(self):
        registry = ModelRegistry()
        assert callable(registry.list_all)

    def test_has_get_by_provider_method(self):
        registry = ModelRegistry()
        assert callable(registry.get_by_provider)

    def test_has_get_cheapest_for_task_method(self):
        registry = ModelRegistry()
        assert callable(registry.get_cheapest_for_task)


class TestGet:
    def test_get_existing_model(self):
        registry = ModelRegistry()
        result = registry.get("deepseek-chat")
        assert result is not None
        assert result["provider"] == "deepseek"
        assert result["tier"] == "standard"

    def test_get_premium_model(self):
        registry = ModelRegistry()
        result = registry.get("claude-opus-4")
        assert result is not None
        assert result["tier"] == "premium"

    def test_get_nonexistent_model(self):
        registry = ModelRegistry()
        result = registry.get("nonexistent-model")
        assert result is None

    def test_get_empty_string(self):
        registry = ModelRegistry()
        result = registry.get("")
        assert result is None

    def test_get_returns_token_limit(self):
        registry = ModelRegistry()
        result = registry.get("deepseek-chat")
        assert "token_limit" in result
        assert result["token_limit"] == 65536


class TestListAll:
    def test_returns_dict(self):
        registry = ModelRegistry()
        result = registry.list_all()
        assert isinstance(result, dict)

    def test_returns_all_models(self):
        registry = ModelRegistry()
        result = registry.list_all()
        assert len(result) == len(MODELS)

    def test_returns_copy(self):
        registry = ModelRegistry()
        result = registry.list_all()
        result["fake-model"] = {"provider": "fake"}
        assert "fake-model" not in registry.list_all()

    def test_contains_all_known_models(self):
        registry = ModelRegistry()
        result = registry.list_all()
        expected_keys = [
            "deepseek-chat",
            "deepseek-reasoner",
            "claude-opus-4",
            "claude-haiku-3.5",
            "gpt-5.2",
            "gpt-4o-mini",
        ]
        for key in expected_keys:
            assert key in result


class TestGetByProvider:
    def test_deepseek_provider(self):
        registry = ModelRegistry()
        result = registry.get_by_provider("deepseek")
        assert "deepseek-chat" in result
        assert "deepseek-reasoner" in result
        assert len(result) == 2

    def test_anthropic_provider(self):
        registry = ModelRegistry()
        result = registry.get_by_provider("anthropic")
        assert "claude-opus-4" in result
        assert "claude-haiku-3.5" in result
        assert len(result) == 2

    def test_openai_provider(self):
        registry = ModelRegistry()
        result = registry.get_by_provider("openai")
        assert "gpt-5.2" in result
        assert "gpt-4o-mini" in result
        assert len(result) == 2

    def test_unknown_provider(self):
        registry = ModelRegistry()
        result = registry.get_by_provider("unknown")
        assert result == []

    def test_empty_provider(self):
        registry = ModelRegistry()
        result = registry.get_by_provider("")
        assert result == []


class TestGetCheapestForTask:
    def test_default_returns_deepseek_chat(self):
        registry = ModelRegistry()
        result = registry.get_cheapest_for_task()
        assert result == "deepseek-chat"

    def test_standard_task(self):
        registry = ModelRegistry()
        result = registry.get_cheapest_for_task("standard")
        assert result == "deepseek-chat"

    def test_returns_string(self):
        registry = ModelRegistry()
        result = registry.get_cheapest_for_task()
        assert isinstance(result, str)


class TestMODELSConstant:
    def test_all_entries_have_provider(self):
        for model_id, info in MODELS.items():
            assert "provider" in info, f"{model_id} missing provider"

    def test_all_entries_have_tier(self):
        for model_id, info in MODELS.items():
            assert "tier" in info, f"{model_id} missing tier"
            assert info["tier"] in ("standard", "premium")

    def test_all_entries_have_token_limit(self):
        for model_id, info in MODELS.items():
            assert "token_limit" in info, f"{model_id} missing token_limit"
            assert info["token_limit"] > 0
