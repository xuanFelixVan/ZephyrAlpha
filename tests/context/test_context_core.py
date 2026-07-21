# [A_test] module_id: MOD-GOV_context_core | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-460 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.context_engine.test_context_core
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound

"""Test suite: context_core"""

import os
import shutil
import tempfile

import pytest

from zephyr.autonomy_core.context.context_assembler import (
    AssembledContext,
    AssemblyError,
    ContextAssembler,
)
from zephyr.autonomy_core.context.context_pipeline import (
    ContextFourStageResult,
    run_context_four_stage,
    run_context_four_stage_or_raise,
)
from zephyr.infrastructure.capacity_assurance.token_budget import (
    DEFAULT_CONTEXT_TOKEN_BUDGET,
    estimate_tokens,
)


class TestEstimateTokens:
    def test_empty_string(self):
        assert estimate_tokens("") == 0

    def test_single_char(self):
        assert estimate_tokens("a") == 1

    def test_short_string(self):
        result = estimate_tokens("hello")
        assert result == 1

    def test_medium_string(self):
        text = "a" * 100
        result = estimate_tokens(text)
        assert result == 25

    def test_long_string(self):
        text = "x" * 4000
        result = estimate_tokens(text)
        assert result == 1000

    def test_minimum_one_token(self):
        result = estimate_tokens("ab")
        assert result >= 1

    def test_non_ascii_text(self):
        result = estimate_tokens("你好世界测试")
        assert result >= 1


class TestDefaultContextTokenBudget:
    def test_is_positive_integer(self):
        assert isinstance(DEFAULT_CONTEXT_TOKEN_BUDGET, int)
        assert DEFAULT_CONTEXT_TOKEN_BUDGET > 0

    def test_reasonable_default(self):
        assert DEFAULT_CONTEXT_TOKEN_BUDGET >= 1000


class TestContextAssembler:
    @pytest.fixture()
    def tmp_dir(self):
        d = tempfile.mkdtemp(prefix="ctx_test_")
        sub = os.path.join(d, "docs")
        os.makedirs(sub, exist_ok=True)
        test_file = os.path.join(sub, "test_doc.md")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("# Test Document\n\nThis is test content for context assembly.\n")
        yield d
        shutil.rmtree(d, ignore_errors=True)

    def test_assemble_with_empty_manifest(self):
        asm = ContextAssembler(require_absolute_paths=False)
        result = asm.assemble([], token_budget=1000)
        assert isinstance(result, AssembledContext)

    def test_assemble_with_manifest(self, tmp_dir):
        test_file = os.path.join(tmp_dir, "docs", "test_doc.md")
        asm = ContextAssembler(require_absolute_paths=False)
        manifest = [{"path": test_file, "role": "reference"}]
        result = asm.assemble(manifest, token_budget=8000)
        assert isinstance(result, AssembledContext)

    def test_validate_returns_bool(self, tmp_dir):
        asm = ContextAssembler(require_absolute_paths=False)
        manifest = [{"path": os.path.join(tmp_dir, "docs", "test_doc.md"), "role": "reference"}]
        assembled = asm.assemble(manifest, token_budget=8000)
        result = asm.validate(assembled)
        assert isinstance(result, bool)


class TestRunContextFourStage:
    @pytest.fixture()
    def tmp_dir(self):
        d = tempfile.mkdtemp(prefix="ctx_4stage_")
        sub = os.path.join(d, "docs")
        os.makedirs(sub, exist_ok=True)
        test_file = os.path.join(sub, "test_doc.md")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("# Test\n\nContent for four-stage pipeline test.\n")
        yield d
        shutil.rmtree(d, ignore_errors=True)

    def test_empty_manifest(self):
        result = run_context_four_stage(
            [],
            token_budget=1000,
            require_absolute_manifest_paths=False,
        )
        assert isinstance(result, ContextFourStageResult)
        assert isinstance(result.assembled, AssembledContext)
        assert isinstance(result.g3_passed, bool)
        assert isinstance(result.pipeline_warnings, list)

    def test_with_manifest_no_inject(self, tmp_dir):
        test_file = os.path.join(tmp_dir, "docs", "test_doc.md")
        result = run_context_four_stage(
            [{"path": test_file, "role": "reference"}],
            token_budget=8000,
            require_absolute_manifest_paths=False,
            inject_mode="none",
        )
        assert isinstance(result, ContextFourStageResult)
        assert result.assembled is not None

    def test_inject_mode_none_skips_inject(self, tmp_dir):
        test_file = os.path.join(tmp_dir, "docs", "test_doc.md")
        result = run_context_four_stage(
            [{"path": test_file, "role": "reference"}],
            token_budget=8000,
            require_absolute_manifest_paths=False,
            inject_mode="none",
        )
        assert result.injected is None

    def test_inject_without_kb_repo_returns_empty(self, tmp_dir):
        test_file = os.path.join(tmp_dir, "docs", "test_doc.md")
        result = run_context_four_stage(
            [{"path": test_file, "role": "reference"}],
            token_budget=8000,
            require_absolute_manifest_paths=False,
            inject_mode="keyword",
            inject_query="test",
        )
        assert result.injected is not None
        assert result.injected.context == ""

    def test_inject_with_empty_query_warns(self, tmp_dir):
        test_file = os.path.join(tmp_dir, "docs", "test_doc.md")
        result = run_context_four_stage(
            [{"path": test_file, "role": "reference"}],
            token_budget=8000,
            require_absolute_manifest_paths=False,
            inject_mode="keyword",
            inject_query="",
        )
        assert any("inject_query" in w or "inject" in w for w in result.pipeline_warnings)

    def test_final_context_is_string(self, tmp_dir):
        test_file = os.path.join(tmp_dir, "docs", "test_doc.md")
        result = run_context_four_stage(
            [{"path": test_file, "role": "reference"}],
            token_budget=8000,
            require_absolute_manifest_paths=False,
        )
        assert isinstance(result.final_context, str)


class TestRunContextFourStageOrRaise:
    def test_raises_on_g3_failure(self):
        with pytest.raises(AssemblyError):
            run_context_four_stage_or_raise(
                [],
                token_budget=0,
                require_absolute_manifest_paths=False,
            )
