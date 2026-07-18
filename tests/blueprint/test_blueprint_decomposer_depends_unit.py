# [A_test] module_id: SRC-TST-1980 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-597 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_blueprint_decomposer_depends
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""BlueprintDecomposer — depends_on 与 extract_depends_from_content。"""


from pathlib import Path

from zephyr.shared.blueprint_tools.blueprint_decomposer import BlueprintDecomposer, _split_desc_and_depends


def test_split_desc_and_depends() -> None:
    lines = ["第一行说明", "depends_on: [CP-1, CP-2]", "尾部"]
    narrative, deps = _split_desc_and_depends(lines)
    assert deps == ["CP-1", "CP-2"]
    assert narrative == ["第一行说明", "尾部"]


def test_extract_depends_from_content_anchors_to_module_title() -> None:
    md = """
- CP-1 **Mod A** — 描述 A
  depends_on: [CP-99]
"""
    d = BlueprintDecomposer().extract_depends_from_content(md)
    assert d.get("Mod A") == ["CP-99"]


def test_decompose_applies_depends(tmp_path: Path) -> None:
    bp = tmp_path / "bp.md"
    bp.write_text(
        "\n".join(
            [
                "- CP-1 **First** — 描述一",
                "- CP-1 **Second** — 描述二",
                "  depends_on: [First]",
            ]
        ),
        encoding="utf-8",
    )
    dec = BlueprintDecomposer()
    result = dec.decompose_blueprint(str(bp), namespace="CP", phase=1)
    assert len(result.tasks) == 2
    t_second = next(t for t in result.tasks if "Second" in t.title)
    assert t_second.task_id in result.dependency_graph
    assert result.dependency_graph[t_second.task_id]  # 应解析出 First 对应 task_id
