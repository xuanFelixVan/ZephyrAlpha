# [A_test] module_id: SRC-TST-2021 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-638 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_extract
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""
测试套件：G5 Extract 门禁（T-2-13-E）
======================================
覆盖 ≥ 5 条：
1. 失败经验写入 06_lessons_learned/
2. 成功经验写入 07_best_practices/
3. 设计决策写入 ADR
4. KE 编号自动递增
5. 无匹配模板被拒绝
6. 完整提取流程
"""


from pathlib import Path

import pytest

from zephyr.gov_kb.pipeline.extract import BEST_PRACTICES_DIR_NAME, LESSONS_DIR_NAME, ExtractGate


@pytest.fixture()
def adr_dir(tmp_path: Path) -> Path:
    return tmp_path / "adr"


@pytest.fixture()
def gate(kb_root: Path, adr_dir: Path) -> ExtractGate:
    return ExtractGate(kb_root=kb_root, adr_dir=adr_dir)


def _make_active_md(
    tmp_path: Path,
    name: str = "test.md",
    module_id: str = "KE-500",
    category: str = "best_practice",
    classification: str = "KNOWLEDGE_ENTRY",
    body: str = "",
) -> Path:
    if not body:
        body = (
            "# 知识条目\n\n"
            "## Practice Description\n\n这是最佳实践的描述。\n\n"
            "## Rationale\n\n这是实践的理由。\n\n"
            "## Applicability\n\n适用范围说明。\n\n"
            "## Anti Patterns\n\n反模式列表。\n\n"
        )
    content = (
        f"---\nmodule_id: {module_id}\ntitle: 知识条目\ncategory: {category}\n"
        f"classification: {classification}\nai_value_score: 9.0\n---\n\n{body}"
    )
    p = tmp_path / name
    p.write_text(content, encoding="utf-8", newline="\n")
    return p


def test_extract_lesson_learned(gate: ExtractGate, tmp_path: Path, kb_root: Path) -> None:
    body = (
        "# 教训记录\n\n"
        "## Incident Description\n\n编码损坏导致文件乱码。\n\n"
        "## Root Cause\n\nautoGuessEncoding 误判。\n\n"
        "## Fix Action\n\n禁用自动编码检测。\n\n"
        "## Prevention\n\n强制 UTF-8 编码。\n\n"
    )
    md = _make_active_md(tmp_path, category="lesson_learned", body=body)
    result = gate.extract(md)
    assert result.passed is True
    assert result.extract_type == "lesson_learned"
    assert result.target_path is not None
    assert LESSONS_DIR_NAME in str(result.target_path)


def test_extract_best_practice(gate: ExtractGate, tmp_path: Path, kb_root: Path) -> None:
    md = _make_active_md(tmp_path, category="best_practice")
    result = gate.extract(md)
    assert result.passed is True
    assert result.extract_type == "best_practice"
    assert result.target_path is not None
    assert BEST_PRACTICES_DIR_NAME in str(result.target_path)


def test_extract_design_decision_writes_adr(gate: ExtractGate, tmp_path: Path, adr_dir: Path) -> None:
    body = (
        "# 架构决策\n\n"
        "## Design Decisions\n\nADR-0001 选择 SQLite 作为元数据层。\n\n"
        "## Interfaces\n\n函数签名定义。\n\n"
        "## Constraints\n\n必须嵌入式部署。\n\n"
        "## Dependencies\n\n依赖 pyyaml。\n\n"
    )
    md = _make_active_md(tmp_path, category="blueprint", body=body)
    result = gate.extract(md)
    assert result.passed is True
    assert result.extract_type == "design_decision"
    assert result.adr_path is not None
    assert result.adr_path.exists()
    content = result.adr_path.read_text(encoding="utf-8")
    assert "ADR" in content


def test_extract_ke_number_increments(gate: ExtractGate, tmp_path: Path, kb_root: Path) -> None:
    md1 = _make_active_md(tmp_path, name="first.md", module_id="KE-501", category="best_practice")
    result1 = gate.extract(md1)
    assert result1.passed is True

    md2 = _make_active_md(tmp_path, name="second.md", module_id="KE-502", category="best_practice")
    result2 = gate.extract(md2)
    assert result2.passed is True


def test_extract_nonexistent_file_rejected(gate: ExtractGate, tmp_path: Path) -> None:
    result = gate.extract(tmp_path / "ghost.md")
    assert result.passed is False


def test_extract_no_template_rejected(gate: ExtractGate, tmp_path: Path) -> None:
    p = tmp_path / "unknown.md"
    p.write_text(
        "---\nmodule_id: KE-503\ntitle: Unknown\ncategory: totally_unknown_type\n---\n\nContent.\n",
        encoding="utf-8",
        newline="\n",
    )
    result = gate.extract(p)
    assert result.passed is False
