# [A_test] module_id: SRC-TST-1411 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_prompt_version
# [INVARIANTS] get_version returns v0.0.0 for unregistered; diff returns bool
# [MODIFY-GUARD] src/zephyr/orchestrator/prompt_version.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] register/get_version/diff never raise
# [TESTS] tests/test_prompt_version.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.orchestrator.contracts.prompt_version import PromptVersionManager


class TestPromptVersionManagerInstantiation:
    def test_empty_versions_on_init(self):
        mgr = PromptVersionManager()
        assert mgr._versions == {}


class TestRegister:
    def test_register_stores_version(self):
        mgr = PromptVersionManager()
        mgr.register("prompt-1", "v1.0.0", "template content")
        assert mgr._versions["prompt-1"] == "v1.0.0"

    def test_register_overwrites(self):
        mgr = PromptVersionManager()
        mgr.register("prompt-1", "v1.0.0", "old")
        mgr.register("prompt-1", "v2.0.0", "new")
        assert mgr._versions["prompt-1"] == "v2.0.0"

    def test_register_multiple_prompts(self):
        mgr = PromptVersionManager()
        mgr.register("p-a", "v1.0.0", "a")
        mgr.register("p-b", "v2.0.0", "b")
        assert len(mgr._versions) == 2


class TestGetVersion:
    def test_registered_prompt(self):
        mgr = PromptVersionManager()
        mgr.register("prompt-1", "v1.0.0", "template")
        assert mgr.get_version("prompt-1") == "v1.0.0"

    def test_unregistered_prompt_returns_default(self):
        mgr = PromptVersionManager()
        assert mgr.get_version("unknown") == "v0.0.0"

    def test_empty_string_returns_default(self):
        mgr = PromptVersionManager()
        assert mgr.get_version("") == "v0.0.0"


class TestDiff:
    def test_same_template_returns_false(self):
        mgr = PromptVersionManager()
        result = mgr.diff("p-1", "same content", "same content")
        assert result is False

    def test_different_template_returns_true(self):
        mgr = PromptVersionManager()
        result = mgr.diff("p-1", "old content", "new content")
        assert result is True

    def test_empty_vs_nonempty(self):
        mgr = PromptVersionManager()
        result = mgr.diff("p-1", "", "content")
        assert result is True

    def test_both_empty(self):
        mgr = PromptVersionManager()
        result = mgr.diff("p-1", "", "")
        assert result is False


class TestBoundary:
    def test_register_empty_version_string(self):
        mgr = PromptVersionManager()
        mgr.register("p-x", "", "template")
        assert mgr.get_version("p-x") == ""

    def test_register_empty_template(self):
        mgr = PromptVersionManager()
        mgr.register("p-y", "v1.0.0", "")
        assert mgr._versions["p-y"] == "v1.0.0"

    def test_diff_whitespace_difference(self):
        mgr = PromptVersionManager()
        result = mgr.diff("p-1", "content", "content ")
        assert result is True
