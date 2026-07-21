# [A_test] module_id: MOD-GOV_context_assembler_unit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-609 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_context_assembler
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""ContextAssembler 单测（AUDIT-07 补齐）。"""


from pathlib import Path

import pytest

from zephyr.autonomy_core.context.context_assembler import ContextAssembler
from zephyr.autonomy_core.context.context_pipeline import run_context_four_stage


@pytest.fixture()
def tiny_file(tmp_path: Path) -> Path:
    p = tmp_path / "sample.txt"
    p.write_text("hello context\n", encoding="utf-8")
    return p


def test_assemble_requires_absolute_when_configured(tmp_path: Path) -> None:
    p = tmp_path / "sample.txt"
    p.write_text("hello\n", encoding="utf-8")
    asm = ContextAssembler(require_absolute_paths=True)
    rel = "sample.txt"
    ctx = asm.assemble([{"file_path": rel, "reason": "t"}], compress=False)
    assert any("NOT_ABSOLUTE" in e for e in ctx.errors)


def test_assemble_reads_absolute_file(tiny_file: Path) -> None:
    asm = ContextAssembler(require_absolute_paths=False)
    ctx = asm.assemble(
        [{"file_path": str(tiny_file.resolve()), "reason": "t"}],
        token_budget=100_000,
        compress=False,
    )
    assert ctx.file_count == 1
    assert ctx.is_complete
    assert "hello context" in ctx.context_text


def test_validate_requires_non_empty_complete(tiny_file: Path) -> None:
    asm = ContextAssembler(require_absolute_paths=False)
    ctx = asm.assemble([{"file_path": str(tiny_file.resolve()), "reason": "t"}], compress=False)
    assert asm.validate(ctx) is True


def test_pipeline_include_architecture_context_missing_warns(tmp_path: Path, tiny_file: Path) -> None:
    r = run_context_four_stage(
        [{"file_path": str(tiny_file.resolve()), "reason": "t"}],
        require_absolute_manifest_paths=False,
        compress_manifest=False,
        include_architecture_context=True,
        architecture_context_path=tmp_path / "nonexistent.json",
    )
    assert any("architecture_context" in w for w in r.pipeline_warnings)
