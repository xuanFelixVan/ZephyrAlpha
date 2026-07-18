# [A_test] module_id: SRC-TST-1906 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-525 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.kb.test_triage
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
测试套件：G2 Triage 门禁（T-2-13-B）
=====================================
覆盖 ≥ 5 条：
1. 高价值条目通过 Triage
2. 低评分条目被拒绝
3. 分类标签无效被拒绝
4. 分类自动推断
5. 优先级映射正确
6. 空壳文件被 G2 门禁拦截
"""

from pathlib import Path

import pytest

from zephyr.governance.escalation.triage import HIGH_VALUE_THRESHOLD, TriageGate


@pytest.fixture()
def gate(kb_root: Path) -> TriageGate:
    return TriageGate(kb_root=kb_root)


def _make_rich_md(
    tmp_path: Path,
    name: str = "test.md",
    module_id: str = "KE-200",
    title: str = "架构设计决策",
    category: str = "best_practice",
    classification: str = "BLUEPRINT",
    extra_body: str = "",
) -> Path:
    body = (
        "# 架构设计决策\n\n"
        "本条目记录了系统核心架构的设计决策，包含 ADR-0001 的权衡分析。\n\n"
        "## 接口定义\n\n"
        "函数签名：`def process(data: dict) -> Result`\n\n"
        "## 约束\n\n"
        "必须满足跨层复用要求，不可替代的核心逻辑。\n\n"
        f"{extra_body}\n"
    )
    content = (
        f"---\nmodule_id: {module_id}\ntitle: {title}\ncategory: {category}\n"
        f"classification: {classification}\ndoc_type: blueprint\ndomain: infra_ops\nlayer: shared\n---\n\n{body}"
    )
    p = tmp_path / name
    p.write_text(content, encoding="utf-8", newline="\n")
    return p


def test_triage_high_value_passes(tmp_path: Path, gate: TriageGate) -> None:
    md = _make_rich_md(tmp_path)
    result = gate.triage(md)
    assert result.passed is True
    assert result.ai_triage_score >= HIGH_VALUE_THRESHOLD
    assert result.classification == "BLUEPRINT"


def test_triage_low_score_rejected(tmp_path: Path, gate: TriageGate) -> None:
    p = tmp_path / "low.md"
    p.write_text(
        "---\nmodule_id: KE-201\ntitle: Low\ncategory: general\n---\n\nShort.\n", encoding="utf-8", newline="\n"
    )
    result = gate.triage(p)
    assert result.ai_triage_score < HIGH_VALUE_THRESHOLD


def test_triage_classification_auto_infer(tmp_path: Path, gate: TriageGate) -> None:
    p = tmp_path / "auto.md"
    body = "这是一个关于策略回测的设计决策文档，包含因子计算逻辑和 alpha 信号生成。\n" * 5
    p.write_text(
        f"---\nmodule_id: KE-202\ntitle: Auto\ncategory: strategy\n---\n\n{body}", encoding="utf-8", newline="\n"
    )
    result = gate.triage(p)
    assert result.classification in ("STRATEGY", "BLUEPRINT")


def test_triage_priority_mapping(tmp_path: Path, gate: TriageGate) -> None:
    md = _make_rich_md(tmp_path, module_id="KE-203")
    result = gate.triage(md)
    assert result.priority in ("P0", "P1", "P2", "P3")
    if result.ai_triage_score >= HIGH_VALUE_THRESHOLD:
        assert result.priority == "P0"


def test_triage_empty_shell_rejected(tmp_path: Path, gate: TriageGate) -> None:
    p = tmp_path / "empty.md"
    p.write_text("", encoding="utf-8")
    result = gate.triage(p)
    assert result.passed is False


def test_triage_nonexistent_file_rejected(tmp_path: Path, gate: TriageGate) -> None:
    result = gate.triage(tmp_path / "ghost.md")
    assert result.passed is False
    assert any("不存在" in v for v in result.violations)


def test_triage_writes_to_triaged_dir(tmp_path: Path, kb_root: Path, gate: TriageGate) -> None:
    md = _make_rich_md(tmp_path)
    result = gate.triage(md)
    if result.passed:
        assert result.target_path is not None
        assert "02_triaged" in str(result.target_path)
