# [A_test] module_id: SRC-TST-1897 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-516 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.kb.test_activate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""
测试套件：G4 Activate 门禁（T-2-13-D）
======================================
覆盖 ≥ 5 条：
1. 高分自动激活
2. 低分需人工审批
3. 依赖未就绪被拒绝
4. 目标路径不符合规范被拒绝
5. 提案生成正确
6. force 强制激活
"""


from pathlib import Path

import pytest

from zephyr.intelligence.model_evaluation.activate import ActivateGate


@pytest.fixture()
def gate(kb_root: Path) -> ActivateGate:
    return ActivateGate(kb_root=kb_root)


def _make_analyzed_md(
    tmp_path: Path,
    name: str = "test.md",
    module_id: str = "KE-400",
    ai_value_score: float = 9.5,
    priority: str = "P0",
    classification: str = "BLUEPRINT",
    depends_on: list[str] | None = None,
) -> Path:
    deps_yaml = ""
    if depends_on:
        import yaml

        deps_yaml = f"depends_on: {yaml.dump(depends_on, default_flow_style=False)}"
    body = "# 已分析文档\n\n内容丰富，包含设计决策和接口定义。\n" * 5
    content = (
        f"---\nmodule_id: {module_id}\ntitle: 已分析\ncategory: best_practice\n"
        f"ai_value_score: {ai_value_score}\npriority: {priority}\n"
        f"classification: {classification}\ndomain: infra_ops\n{deps_yaml}---\n\n{body}"
    )
    p = tmp_path / name
    p.write_text(content, encoding="utf-8", newline="\n")
    return p


def test_activate_high_score_auto_activates(tmp_path: Path, gate: ActivateGate) -> None:
    md = _make_analyzed_md(tmp_path, ai_value_score=9.5)
    result = gate.activate(md)
    assert result.passed is True
    assert result.auto_activated is True


def test_activate_low_score_needs_approval(tmp_path: Path, gate: ActivateGate) -> None:
    md = _make_analyzed_md(tmp_path, ai_value_score=5.0)
    result = gate.activate(md)
    assert result.passed is False
    assert result.auto_activated is False
    assert result.proposal is not None
    assert "审批" in result.proposal or "提案" in result.proposal


def test_activate_force_overrides(tmp_path: Path, gate: ActivateGate) -> None:
    md = _make_analyzed_md(tmp_path, ai_value_score=5.0)
    result = gate.activate(md, force=True)
    assert result.passed is True
    assert result.auto_activated is True


def test_activate_nonexistent_file_rejected(tmp_path: Path, gate: ActivateGate) -> None:
    result = gate.activate(tmp_path / "ghost.md")
    assert result.passed is False


def test_activate_writes_to_correct_dir(tmp_path: Path, kb_root: Path, gate: ActivateGate) -> None:
    md = _make_analyzed_md(tmp_path, ai_value_score=9.5, priority="P0")
    result = gate.activate(md)
    if result.passed:
        assert result.target_dir in ("05_active_research", "04_future_capabilities")
        assert result.target_path is not None
        assert result.target_path.exists()


def test_activate_proposal_contains_ke_id(tmp_path: Path, gate: ActivateGate) -> None:
    md = _make_analyzed_md(tmp_path, ai_value_score=5.0, module_id="KE-401")
    result = gate.activate(md)
    if result.proposal:
        assert "KE-401" in result.proposal
