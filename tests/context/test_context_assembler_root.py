# [A_test] module_id: MOD-GOV_context_assembler_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
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


import pytest

try:
    from zephyr.autonomy_core.context.context_assembler import (
        AssembledContext,
        ContextAssembler,
        FileEntry,
        RawContext,
        build_context,
        validate_authority_chain,
    )

    _IMPORT_OK = True
    _IMPORT_ERR = None
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_ERR = str(exc)

pytestmark = pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_ERR}")


class TestContextAssembler:
    def test_assemble_with_existing_file(self, tmp_path):
        f = tmp_path / "sample.txt"
        f.write_text("hello world content for testing", encoding="utf-8")
        manifest = [{"file_path": str(f), "reason": "test file"}]
        asm = ContextAssembler(require_absolute_paths=False)
        ctx = asm.assemble(manifest, compress=False)
        assert ctx.file_count == 1
        assert "hello world" in ctx.context_text
        assert ctx.is_within_budget

    def test_assemble_missing_file(self, tmp_path):
        manifest = [{"file_path": str(tmp_path / "nonexistent.txt"), "reason": "missing"}]
        asm = ContextAssembler(require_absolute_paths=False)
        ctx = asm.assemble(manifest, compress=False)
        assert len(ctx.errors) > 0
        assert ctx.file_count == 0

    def test_assemble_empty_manifest(self):
        asm = ContextAssembler()
        ctx = asm.assemble([], compress=False)
        assert ctx.file_count == 0
        assert ctx.context_text == ""

    def test_assemble_duplicate_paths(self, tmp_path):
        f = tmp_path / "dup.txt"
        f.write_text("duplicate content", encoding="utf-8")
        manifest = [
            {"file_path": str(f), "reason": "first"},
            {"file_path": str(f), "reason": "second"},
        ]
        asm = ContextAssembler(require_absolute_paths=False)
        ctx = asm.assemble(manifest, compress=False)
        assert ctx.file_count == 1

    def test_validate_success(self, tmp_path):
        f = tmp_path / "ok.txt"
        f.write_text("ok content", encoding="utf-8")
        manifest = [{"file_path": str(f), "reason": "test"}]
        asm = ContextAssembler(require_absolute_paths=False)
        ctx = asm.assemble(manifest, compress=False)
        assert asm.validate(ctx) is True

    def test_validate_failure_no_files(self):
        asm = ContextAssembler()
        ctx = asm.assemble([], compress=False)
        assert asm.validate(ctx) is False

    def test_validate_failure_errors(self, tmp_path):
        manifest = [{"file_path": str(tmp_path / "missing.txt"), "reason": "gone"}]
        asm = ContextAssembler(require_absolute_paths=False)
        ctx = asm.assemble(manifest, compress=False)
        assert asm.validate(ctx) is False

    def test_shadow_creates_file(self, tmp_path):
        f = tmp_path / "shadow_src.txt"
        f.write_text("shadow test content", encoding="utf-8")
        manifest = [{"file_path": str(f), "reason": "shadow test"}]
        asm = ContextAssembler(require_absolute_paths=False)
        ctx = asm.assemble(manifest, compress=False)
        shadow_dir = tmp_path / "shadows"
        shadow_path = asm.shadow(ctx, str(shadow_dir))
        assert shadow_path.exists()
        content = shadow_path.read_text(encoding="utf-8")
        assert "shadow test content" in content

    def test_assemble_require_absolute_paths(self, tmp_path):
        manifest = [{"file_path": "relative/path.txt", "reason": "relative"}]
        asm = ContextAssembler(require_absolute_paths=True)
        ctx = asm.assemble(manifest, compress=False)
        assert any("NOT_ABSOLUTE" in e for e in ctx.errors)

    def test_assemble_large_file_skipped(self, tmp_path):
        f = tmp_path / "big.txt"
        f.write_text("x" * 100, encoding="utf-8")
        manifest = [{"file_path": str(f), "reason": "big"}]
        asm = ContextAssembler(max_file_size_mb=0, require_absolute_paths=False)
        ctx = asm.assemble(manifest, compress=False)
        assert any("FILE_TOO_LARGE" in e for e in ctx.errors)


class TestAssembledContext:
    def test_is_complete_no_errors(self):
        ctx = AssembledContext(
            file_count=2,
            entries=[
                FileEntry(file_path="/a", exists=True, readable=True),
                FileEntry(file_path="/b", exists=True, readable=True),
            ],
        )
        assert ctx.is_complete is True

    def test_is_complete_with_errors(self):
        ctx = AssembledContext(
            file_count=1,
            entries=[
                FileEntry(file_path="/a", exists=True, readable=True),
                FileEntry(file_path="/b", exists=False, readable=False),
            ],
            errors=["FILE_NOT_FOUND: /b"],
        )
        assert ctx.is_complete is False

    def test_is_within_budget(self):
        ctx = AssembledContext(token_estimate=100, token_budget=200)
        assert ctx.is_within_budget is True

    def test_is_over_budget(self):
        ctx = AssembledContext(token_estimate=300, token_budget=200)
        assert ctx.is_within_budget is False


class TestRawContext:
    def test_total_items(self):
        ctx = RawContext(
            ke_entries=["a", "b"],
            vibe_rules=["c"],
            blueprints=["d"],
            failure_patterns=["e", "f", "g"],
        )
        assert ctx.total_items == 7

    def test_is_empty(self):
        ctx = RawContext()
        assert ctx.is_empty is True

    def test_is_not_empty_with_defaults(self):
        ctx = RawContext(embedded_defaults=["rule1"])
        assert ctx.is_empty is False


class TestBuildContext:
    def test_build_context_no_vms(self):
        ctx = build_context(task_type="code_gen", target_layer="D_INFRA_OPS", vms=None)
        assert ctx.degraded is True
        assert len(ctx.embedded_defaults) > 0

    def test_build_context_with_none_task(self):
        ctx = build_context(vms=None)
        assert ctx.degraded is True


class TestValidateAuthorityChain:
    def test_trusted_sources_pass(self):
        sources = ["AGENTS.md", "blueprint:MOD-CONTEXT_ENGINE", "CT-CE-001"]
        passed, score, msg = validate_authority_chain(sources, min_trusted_count=2)
        assert passed is True
        assert score >= 0.7

    def test_untrusted_sources_fail(self):
        sources = ["random_file.py", "another_file.py"]
        passed, score, msg = validate_authority_chain(sources, min_trusted_count=2)
        assert passed is False

    def test_empty_sources(self):
        passed, score, msg = validate_authority_chain([], min_trusted_count=1)
        assert passed is False
