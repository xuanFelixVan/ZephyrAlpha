# [A_test] module_id: MOD-GOV_context_pipeline_unit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-613 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_context_pipeline
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""context_pipeline 组合根单测（对齐 build→compress→validate→inject 顺序）。"""


from pathlib import Path

from zephyr.autonomy_core.context.context_pipeline import run_context_four_stage


def test_four_stage_build_validate_no_inject(tmp_path: Path) -> None:
    p = tmp_path / "ctx.md"
    p.write_text("# T\n\n" + ("word " * 200), encoding="utf-8")

    r = run_context_four_stage(
        [{"file_path": str(p.resolve()), "reason": "test"}],
        token_budget=50,
        require_absolute_manifest_paths=True,
        inject_mode="none",
    )

    assert r.assembled.file_count >= 1
    assert r.final_context == r.assembled.context_text
    assert isinstance(r.g3_passed, bool)


def test_compress_with_provenance_raw_preserved() -> None:
    from zephyr.shared.io.doc_compressor import DocCompressor

    c = DocCompressor.instance(reset=True)
    # 以大量 Markdown 标题为主，规则基压缩后仍可满足 min_chars 不变量
    raw = "\n".join(f"## Section {i}\n\nKeep.\n" for i in range(120))
    out = c.compress_with_provenance(raw)
    assert out.raw_text == raw
    assert len(out.compressed_text) >= c.policy.min_chars
