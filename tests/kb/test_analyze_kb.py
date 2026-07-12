# [A_test] module_id: SRC-TST-1898 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-517 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.kb.test_analyze
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""
测试套件：G3 Evaluate 门禁（T-2-13-C）
======================================
覆盖 ≥ 5 条：
1. 高价值评分通过 Evaluate
2. 低价值评分被归档
3. 评分维度正确计算
4. 激活条件正确推导
5. 实现复杂度正确评估
6. 无 frontmatter 文件被处理
"""


from pathlib import Path

import pytest

from zephyr.gov_kb.pipeline.analyze import SCORING_DIMENSIONS, VALUE_SCORE_THRESHOLD, AnalyzeGate


@pytest.fixture()
def gate(kb_root: Path) -> AnalyzeGate:
    return AnalyzeGate(kb_root=kb_root)


def _make_analyzed_md(
    tmp_path: Path,
    name: str = "test.md",
    module_id: str = "KE-300",
    ai_triage_score: float = 0.8,
    priority: str = "P0",
    classification: str = "BLUEPRINT",
    body_extra: str = "",
) -> Path:
    body = (
        "# 深度设计文档\n\n"
        "## 设计决策\n\n"
        "ADR-0001: 选择 SQLite 作为元数据层，因为需要嵌入式部署和零运维。"
        "这是一个重要的架构决策，权衡了性能与复杂度。\n\n"
        "ADR-0002: 选择 ChromaDB 作为向量层，因为需要语义搜索能力。"
        "不采用 Pinecone 的原因是需要本地部署。\n\n"
        "## 接口定义\n\n"
        '```python\ndef process(data: dict[str, Any]) -> Result:\n    """处理数据并返回结果。"""\n    pass\n\nclass DataProcessor:\n    def __init__(self, config: Config):\n        self.config = config\n\n    def transform(self, raw: pd.DataFrame) -> pd.DataFrame:\n        pass\n```\n\n'
        "```yaml\nprocessor:\n  type: batch\n  batch_size: 1000\n  timeout: 30\n```\n\n"
        "## 复用性\n\n"
        "此模块可跨层复用（cross_layer），是核心不可替代的唯一实现。"
        "复用场景包括：数据源层、因子层、风控层。"
        "通用接口设计使得任何层都可以调用。\n\n"
        "## 约束\n\n"
        "必须满足嵌入式部署约束，不可替代的核心逻辑。"
        "唯一支持零运维的方案。\n\n"
        f"{body_extra}\n"
    )
    content = (
        f"---\nmodule_id: {module_id}\ntitle: 深度设计\ncategory: best_practice\n"
        f"ai_triage_score: {ai_triage_score}\npriority: {priority}\n"
        f"classification: {classification}\ndomain: infra_ops\n---\n\n{body}"
    )
    p = tmp_path / name
    p.write_text(content, encoding="utf-8", newline="\n")
    return p


def test_analyze_high_value_passes(tmp_path: Path, gate: AnalyzeGate) -> None:
    md = _make_analyzed_md(tmp_path)
    result = gate.analyze(md)
    assert result.passed is True
    assert result.ai_value_score >= VALUE_SCORE_THRESHOLD


def test_analyze_low_value_archived(tmp_path: Path, gate: AnalyzeGate) -> None:
    p = tmp_path / "low.md"
    p.write_text(
        "---\nmodule_id: KE-301\ntitle: Low\ncategory: general\nai_triage_score: 0.3\npriority: P3\n---\n\nMinimal content.\n",
        encoding="utf-8",
        newline="\n",
    )
    result = gate.analyze(p)
    assert result.passed is False
    assert result.ai_value_score < VALUE_SCORE_THRESHOLD


def test_analyze_dimension_scores_computed(tmp_path: Path, gate: AnalyzeGate) -> None:
    md = _make_analyzed_md(tmp_path)
    result = gate.analyze(md)
    assert "dimension_scores" in result.details
    scores = result.details["dimension_scores"]
    for dim in SCORING_DIMENSIONS:
        assert dim in scores
        assert 0.0 <= scores[dim] <= 1.0


def test_analyze_activation_conditions(tmp_path: Path, gate: AnalyzeGate) -> None:
    md = _make_analyzed_md(tmp_path)
    result = gate.analyze(md)
    assert len(result.activation_conditions) > 0


def test_analyze_complexity_assessment(tmp_path: Path, gate: AnalyzeGate) -> None:
    md = _make_analyzed_md(tmp_path)
    result = gate.analyze(md)
    assert result.implementation_complexity in ("low", "medium", "high")


def test_analyze_nonexistent_file_rejected(tmp_path: Path, gate: AnalyzeGate) -> None:
    result = gate.analyze(tmp_path / "ghost.md")
    assert result.passed is False


def test_analyze_writes_to_analyzed_dir(tmp_path: Path, kb_root: Path, gate: AnalyzeGate) -> None:
    md = _make_analyzed_md(tmp_path)
    result = gate.analyze(md)
    if result.passed:
        assert result.target_path is not None
        assert "03_analyzed" in str(result.target_path)
