# [A_test] module_id: MOD-GOV_prompt_version_manager | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-419 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_prompt_version_manager
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/test_prompt_version_manager.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.shared.adaptation.prompt_version_manager import (
    PromptRegistry,
    PromptVersion,
    PromptVersionManager,
)


class TestPromptVersion:
    def test_default_values(self):
        pv = PromptVersion(
            prompt_id="p1",
            version="1.0",
            content="hello",
            model="deepseek",
            pipeline_module="mod_a",
        )
        assert pv.prompt_id == "p1"
        assert pv.version == "1.0"
        assert pv.content == "hello"
        assert pv.model == "deepseek"
        assert pv.pipeline_module == "mod_a"
        assert pv.performance_score == 0.0
        assert pv.usage_count == 0
        assert pv.deprecated is False

    def test_custom_optional_fields(self):
        pv = PromptVersion(
            prompt_id="p2",
            version="2.0",
            content="world",
            model="gpt-4",
            pipeline_module="mod_b",
            performance_score=0.95,
            usage_count=10,
            deprecated=True,
        )
        assert pv.performance_score == 0.95
        assert pv.usage_count == 10
        assert pv.deprecated is True


class TestPromptRegistry:
    def test_creation(self):
        reg = PromptRegistry(prompts={}, current_versions={}, last_updated="2026-01-01")
        assert reg.prompts == {}
        assert reg.current_versions == {}
        assert reg.last_updated == "2026-01-01"

    def test_with_data(self):
        pv = PromptVersion(prompt_id="p1", version="1.0", content="c", model="m", pipeline_module="")
        reg = PromptRegistry(
            prompts={"p1": [pv]},
            current_versions={"p1": "1.0"},
            last_updated="2026-01-01",
        )
        assert "p1" in reg.prompts
        assert len(reg.prompts["p1"]) == 1
        assert reg.current_versions["p1"] == "1.0"


class TestPromptVersionManager:
    def test_instantiation_with_tmp_path(self, tmp_path):
        mgr = PromptVersionManager(data_dir=tmp_path / "prompts")
        assert mgr._data_dir == tmp_path / "prompts"
        assert mgr._registry.prompts == {}

    def test_register_and_get_current(self, tmp_path):
        mgr = PromptVersionManager(data_dir=tmp_path / "prompts")
        mgr.register("p1", "1.0", "content v1", model="deepseek", pipeline_module="mod_a")
        current = mgr.get_current("p1")
        assert current is not None
        assert current.version == "1.0"
        assert current.content == "content v1"
        assert current.model == "deepseek"

    def test_register_multiple_versions(self, tmp_path):
        mgr = PromptVersionManager(data_dir=tmp_path / "prompts")
        mgr.register("p1", "1.0", "content v1")
        mgr.register("p1", "2.0", "content v2")
        current = mgr.get_current("p1")
        assert current is not None
        assert current.version == "2.0"

    def test_get_current_nonexistent_prompt(self, tmp_path):
        mgr = PromptVersionManager(data_dir=tmp_path / "prompts")
        result = mgr.get_current("nonexistent")
        assert result is None

    def test_get_current_deprecated_version_returns_none(self, tmp_path):
        mgr = PromptVersionManager(data_dir=tmp_path / "prompts")
        mgr.register("p1", "1.0", "content v1")
        mgr.deprecate("p1", "1.0")
        result = mgr.get_current("p1")
        assert result is None

    def test_get_current_increments_usage_count(self, tmp_path):
        mgr = PromptVersionManager(data_dir=tmp_path / "prompts")
        mgr.register("p1", "1.0", "content v1")
        mgr.get_current("p1")
        mgr.get_current("p1")
        versions = mgr.list_versions("p1")
        assert versions[0].usage_count == 2

    def test_deprecate_existing_version(self, tmp_path):
        mgr = PromptVersionManager(data_dir=tmp_path / "prompts")
        mgr.register("p1", "1.0", "content v1")
        result = mgr.deprecate("p1", "1.0")
        assert result is True
        versions = mgr.list_versions("p1")
        assert versions[0].deprecated is True

    def test_deprecate_nonexistent_version(self, tmp_path):
        mgr = PromptVersionManager(data_dir=tmp_path / "prompts")
        mgr.register("p1", "1.0", "content v1")
        result = mgr.deprecate("p1", "9.0")
        assert result is False

    def test_deprecate_nonexistent_prompt(self, tmp_path):
        mgr = PromptVersionManager(data_dir=tmp_path / "prompts")
        result = mgr.deprecate("nonexistent", "1.0")
        assert result is False

    def test_rollback_to_previous_version(self, tmp_path):
        mgr = PromptVersionManager(data_dir=tmp_path / "prompts")
        mgr.register("p1", "1.0", "content v1")
        mgr.register("p1", "2.0", "content v2")
        mgr.deprecate("p1", "1.0")
        result = mgr.rollback_to("p1", "1.0")
        assert result is True
        current = mgr.get_current("p1")
        assert current is not None
        assert current.version == "1.0"
        assert current.deprecated is False

    def test_rollback_to_nonexistent_version(self, tmp_path):
        mgr = PromptVersionManager(data_dir=tmp_path / "prompts")
        mgr.register("p1", "1.0", "content v1")
        result = mgr.rollback_to("p1", "9.0")
        assert result is False

    def test_list_versions(self, tmp_path):
        mgr = PromptVersionManager(data_dir=tmp_path / "prompts")
        mgr.register("p1", "1.0", "content v1")
        mgr.register("p1", "2.0", "content v2")
        versions = mgr.list_versions("p1")
        assert len(versions) == 2
        assert versions[0].version == "1.0"
        assert versions[1].version == "2.0"

    def test_list_versions_empty(self, tmp_path):
        mgr = PromptVersionManager(data_dir=tmp_path / "prompts")
        versions = mgr.list_versions("nonexistent")
        assert versions == []

    def test_persist_creates_file(self, tmp_path):
        mgr = PromptVersionManager(data_dir=tmp_path / "prompts")
        mgr.register("p1", "1.0", "content v1")
        registry_file = tmp_path / "prompts" / "prompt_registry.json"
        assert registry_file.exists()
