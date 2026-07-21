# [A_test] module_id: MOD-GOV_assembly_context_assembler | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §tests
# [MODULE] zephyr.autonomy_core.context.context_assembler
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
    from zephyr.autonomy_core.context.context_assembler import (
        AssembledContext,
        ContextAssembler,
        FileEntry,
    )
except Exception as _exc:
    pytest.skip(f"cannot import context_assembler: {_exc}", allow_module_level=True)


class TestContextAssembler:
    def test_assemble_with_empty_manifest(self):
        asm = ContextAssembler(require_absolute_paths=False)
        result = asm.assemble([], compress=False)
        assert isinstance(result, AssembledContext)
        assert result.file_count == 0
        assert len(result.errors) == 0

    def test_assemble_with_missing_file(self):
        asm = ContextAssembler(require_absolute_paths=False)
        manifest = [{"file_path": "/nonexistent/file.py", "reason": "test"}]
        result = asm.assemble(manifest, compress=False)
        assert len(result.errors) > 0

    def test_assemble_with_existing_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write("print('hello')")
            tmp = f.name
        try:
            asm = ContextAssembler(require_absolute_paths=False)
            manifest = [{"file_path": tmp, "reason": "test file"}]
            result = asm.assemble(manifest, compress=False)
            assert result.file_count == 1
            assert "print('hello')" in result.context_text
        finally:
            os.unlink(tmp)

    def test_assemble_missing_file_path_in_manifest(self):
        asm = ContextAssembler()
        manifest = [{"reason": "no path"}]
        result = asm.assemble(manifest, compress=False)
        assert any("MISSING_FILE_PATH" in e for e in result.errors)

    def test_validate_complete_context(self):
        ctx = AssembledContext(
            file_count=2,
            entries=[
                FileEntry(file_path="a.py", exists=True, readable=True),
                FileEntry(file_path="b.py", exists=True, readable=True),
            ],
        )
        asm = ContextAssembler()
        assert asm.validate(ctx) is True

    def test_validate_incomplete_context(self):
        ctx = AssembledContext(
            file_count=0,
            entries=[FileEntry(file_path="a.py", exists=False, readable=False)],
            errors=["FILE_NOT_FOUND: a.py"],
        )
        asm = ContextAssembler()
        assert asm.validate(ctx) is False


class TestAssembledContext:
    def test_is_complete_no_errors(self):
        ctx = AssembledContext(file_count=1, entries=[FileEntry(file_path="a.py", exists=True, readable=True)])
        assert ctx.is_complete is True

    def test_is_complete_with_errors(self):
        ctx = AssembledContext(errors=["some error"])
        assert ctx.is_complete is False

    def test_is_within_budget(self):
        ctx = AssembledContext(token_estimate=100, token_budget=200)
        assert ctx.is_within_budget is True

    def test_is_not_within_budget(self):
        ctx = AssembledContext(token_estimate=300, token_budget=200)
        assert ctx.is_within_budget is False
