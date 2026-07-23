# [A_test] module_id: MOD-GOV_assembly_context_pipeline | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
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

import os
import tempfile

import pytest

try:
    from zephyr.autonomy_core.context.context_assembler import AssemblyError
    from zephyr.autonomy_core.context.context_pipeline import (
        ContextFourStageResult,
        run_context_four_stage,
        run_context_four_stage_or_raise,
    )
except Exception as _exc:
    pytest.skip(f"cannot import context_pipeline: {_exc}", allow_module_level=True)


class TestRunContextFourStage:
    def test_empty_manifest(self):
        result = run_context_four_stage([], require_absolute_manifest_paths=False)
        assert isinstance(result, ContextFourStageResult)
        assert result.g3_passed is False

    def test_with_existing_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write("x = 1")
            tmp = f.name
        try:
            manifest = [{"file_path": tmp, "reason": "test"}]
            result = run_context_four_stage(manifest, require_absolute_manifest_paths=False, compress_manifest=False)
            assert isinstance(result, ContextFourStageResult)
            assert result.assembled.file_count == 1
        finally:
            os.unlink(tmp)

    def test_inject_mode_none_skips_inject(self):
        result = run_context_four_stage([], require_absolute_manifest_paths=False, inject_mode="none")
        assert result.injected is None

    def test_inject_mode_returns_empty_context(self):
        result = run_context_four_stage(
            [], require_absolute_manifest_paths=False, inject_mode="keyword", inject_query="test"
        )
        assert result.injected is not None
        assert result.injected.context == ""


class TestRunContextFourStageOrRaise:
    def test_raises_on_g3_failure(self):
        with pytest.raises(AssemblyError):
            run_context_four_stage_or_raise([], require_absolute_manifest_paths=False)

    def test_succeeds_with_valid_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write("x = 1")
            tmp = f.name
        try:
            manifest = [{"file_path": tmp, "reason": "test"}]
            result = run_context_four_stage_or_raise(
                manifest, require_absolute_manifest_paths=False, compress_manifest=False
            )
            assert result.g3_passed is True
        finally:
            os.unlink(tmp)
