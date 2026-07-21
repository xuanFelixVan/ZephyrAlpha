# [A_test] module_id: MOD-GOV_context_pipeline_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §tests
# [MODULE] zephyr.autonomy_core.context.context_pipeline
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.autonomy_core.context.context_assembler import AssemblyError
    from zephyr.autonomy_core.context.context_pipeline import (
        ContextFourStageResult,
        run_context_four_stage,
        run_context_four_stage_or_raise,
    )

    _IMPORT_OK = True
    _IMPORT_ERR = None
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_ERR = str(exc)

pytestmark = pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_ERR}")


class TestRunContextFourStage:
    def test_empty_manifest(self):
        result = run_context_four_stage(
            [],
            require_absolute_manifest_paths=False,
        )
        assert isinstance(result, ContextFourStageResult)
        assert result.assembled.file_count == 0
        assert result.g3_passed is False

    def test_with_existing_file(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("pipeline test content", encoding="utf-8")
        manifest = [{"file_path": str(f), "reason": "pipeline test"}]
        result = run_context_four_stage(
            manifest,
            require_absolute_manifest_paths=False,
        )
        assert result.assembled.file_count == 1
        assert "pipeline test content" in result.final_context

    def test_with_missing_file(self, tmp_path):
        manifest = [{"file_path": str(tmp_path / "missing.txt"), "reason": "missing"}]
        result = run_context_four_stage(
            manifest,
            require_absolute_manifest_paths=False,
        )
        assert result.g3_passed is False
        assert len(result.assembled.errors) > 0

    def test_no_compress(self, tmp_path):
        f = tmp_path / "nocomp.txt"
        f.write_text("no compression", encoding="utf-8")
        manifest = [{"file_path": str(f), "reason": "test"}]
        result = run_context_four_stage(
            manifest,
            compress_manifest=False,
            require_absolute_manifest_paths=False,
        )
        assert result.assembled.was_compressed is False

    def test_inject_mode_none(self, tmp_path):
        f = tmp_path / "inject_test.txt"
        f.write_text("inject test", encoding="utf-8")
        manifest = [{"file_path": str(f), "reason": "test"}]
        result = run_context_four_stage(
            manifest,
            inject_mode="none",
            require_absolute_manifest_paths=False,
        )
        assert result.injected is None

    def test_inject_mode_keyword_no_kb_warns(self, tmp_path):
        f = tmp_path / "inject_nokb.txt"
        f.write_text("inject no kb", encoding="utf-8")
        manifest = [{"file_path": str(f), "reason": "test"}]
        result = run_context_four_stage(
            manifest,
            inject_mode="keyword",
            inject_query="test",
            require_absolute_manifest_paths=False,
        )
        assert result.injected is not None
        assert result.injected.context == ""

    def test_inject_mode_empty_query_warns(self, tmp_path):
        f = tmp_path / "inject_empty.txt"
        f.write_text("inject empty query", encoding="utf-8")
        manifest = [{"file_path": str(f), "reason": "test"}]
        result = run_context_four_stage(
            manifest,
            inject_mode="keyword",
            inject_query="",
            require_absolute_manifest_paths=False,
        )
        assert any("inject_query" in w for w in result.pipeline_warnings)


class TestRunContextFourStageOrRaise:
    def test_raises_on_g3_failure(self, tmp_path):
        manifest = [{"file_path": str(tmp_path / "missing.txt"), "reason": "missing"}]
        with pytest.raises(AssemblyError):
            run_context_four_stage_or_raise(
                manifest,
                require_absolute_manifest_paths=False,
            )

    def test_succeeds_with_valid_file(self, tmp_path):
        f = tmp_path / "valid.txt"
        f.write_text("valid content", encoding="utf-8")
        manifest = [{"file_path": str(f), "reason": "valid"}]
        result = run_context_four_stage_or_raise(
            manifest,
            require_absolute_manifest_paths=False,
        )
        assert result.g3_passed is True


class TestContextFourStageResult:
    def test_default_values(self):
        from zephyr.autonomy_core.context.context_assembler import AssembledContext

        assembled = AssembledContext()
        result = ContextFourStageResult(assembled=assembled, g3_passed=False)
        assert result.injected is None
        assert result.final_context == ""
        assert result.pipeline_warnings == []
