# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l01_infrastructure.a2a_protocol.test_semantic_diff
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""测试: SemanticDiff"""

from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.semantic_diff import (
    SemanticDiffEngine,
    SemanticRegion,
    SemanticDiffReport,
    SemanticDiffType,
)


def test_diff_no_overlap():
    engine = SemanticDiffEngine()
    regions_a = [SemanticRegion(name="func_a", start_line=1, end_line=10, content="def func_a(): pass")]
    regions_b = [SemanticRegion(name="func_b", start_line=1, end_line=10, content="def func_b(): pass")]
    report = engine.diff("agent-a", "agent-b", regions_a, regions_b, "src/main.py")
    assert isinstance(report, SemanticDiffReport)
    assert report.agent_a_id == "agent-a"
    assert report.agent_b_id == "agent-b"


def test_diff_same_function_modified():
    engine = SemanticDiffEngine()
    regions_a = [SemanticRegion(name="func_x", start_line=1, end_line=10, content="def func_x(): return 1")]
    regions_b = [SemanticRegion(name="func_x", start_line=1, end_line=10, content="def func_x(): return 2")]
    report = engine.diff("agent-a", "agent-b", regions_a, regions_b, "src/main.py")
    assert len(report.entries) > 0
    assert report.entries[0].region_name == "func_x"


def test_diff_has_conflict():
    engine = SemanticDiffEngine()
    regions_a = [SemanticRegion(name="func_x", start_line=1, end_line=10, content="def func_x(): return 1")]
    regions_b = [SemanticRegion(name="func_x", start_line=1, end_line=10, content="def func_x(): return 2")]
    report = engine.diff("agent-a", "agent-b", regions_a, regions_b, "src/main.py")
    assert report.max_conflict_risk >= 0.0


def test_extract_regions():
    source = "def hello():\n    pass\n\ndef world():\n    return 42\n"
    engine = SemanticDiffEngine()
    regions = engine.extract_regions(source)
    assert len(regions) >= 2
    names = [r.name for r in regions]
    assert "hello" in names
    assert "world" in names
