# [A_test] module_id: MOD-GOV_GENERATE_ALGO_OVERVIEW | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_GENERATE_ALGO_OVERVIEW | docs/03_modules/_cross_layer/gov_scripts/blueprint.md
# [MODULE] tests.governance.generators.test_generate_module_algorithm_overview
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_generate_module_algorithm_overview.py — 模块核心算法纵览生成器单元测试。

覆盖（多文件拆分版）：
- render_index_doc：mock 三档数据 + 环节分类 → 断言索引含环节索引+质量报告+位置链接
- render_stage_doc：mock 环节数据 → 断言环节文件含算法卡片+layer分组+HTML锚点+返回索引链接
- render_system_foundation_doc：mock 未锚定数据 → 断言系统基础文件含卡片+layer分组
- classify_rows_by_stage：mock 模块→环节映射 → 断言锚定/未锚定分类正确
- render_battle_stage_index：mock 环节数据 → 断言环节索引含链接
- render_mermaid_layer_overview / render_quality_report / render_stats：保留
"""

from __future__ import annotations

import sys
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT

_GOV_DIR = str(REPO_ROOT / "scripts" / "governance")
_GEN_DIR = str(REPO_ROOT / "scripts" / "governance" / "d5_architecture" / "generators")
for _p in (_GOV_DIR, _GEN_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from _shared.code_algorithm_extractor import (  # noqa: E402
    AlgoFlowData,
    AlgoFlowNode,
    AlgorithmSummary,
)
from generate_module_algorithm_overview import (  # noqa: E402
    STAGE_ID_TO_FILE,
    STATUS_EMOJI,
    _build_consumers,
    _build_rel_context,
    build_module_to_file_map,
    classify_rows_by_stage,
    render_battle_stage_index,
    render_index_doc,
    render_mermaid_layer_overview,
    render_quality_report,
    render_stage_doc,
    render_stats,
    render_system_foundation_doc,
)


def _make_summary(source_type: str, module_id: str = "MOD-TEST") -> AlgorithmSummary:
    """构造测试用 AlgorithmSummary。"""
    if source_type == "code":
        return AlgorithmSummary(
            source_type="code",
            module_id=module_id,
            module_name="测试运营模块",
            summary="运营态模块概述。",
            algo_steps="① 步骤一 ② 步骤二 ③ 步骤三",
            invariants="input >= 0",
            source_path="src/zephyr/test/module.py",
            source_line_range="L10-L20",
            blueprint_ref="docs/03_modules/test/blueprint.md",
            quality_issue="✅ 完整",
        )
    if source_type == "blueprint":
        return AlgorithmSummary(
            source_type="blueprint",
            module_id=module_id,
            module_name="测试设计模块",
            summary="设计态模块概述。",
            algo_steps="① 蓝图步骤一 ② 蓝图步骤二",
            invariants="input >= 0",
            source_path="docs/03_modules/test/blueprint.md",
            source_line_range="",
            blueprint_ref="docs/03_modules/test/blueprint.md",
            quality_issue="✅ 完整",
        )
    return AlgorithmSummary(
        source_type="empty",
        module_id=module_id,
        quality_issue="无代码文件无蓝图，需补",
    )


def _make_rows() -> list[dict]:
    """构造三档 mock 数据（每档一例，分属不同 layer）。"""
    return [
        {
            "module_id": "MOD-TEST-001",
            "path": "src/zephyr/test/module.py",
            "tier": "operational",
            "domain_id": "D_TEST",
            "layer": "L0_infrastructure",
            "build_status": "stable",
            "bp_ref": "docs/03_modules/test/blueprint.md",
            "summary": _make_summary("code", "MOD-TEST-001"),
            "bi_name": "测试运营模块",
        },
        {
            "module_id": "MOD-TEST-002",
            "path": "",
            "tier": "design",
            "domain_id": "D_TEST",
            "layer": "L1_foundation",
            "build_status": "planned",
            "bp_ref": "docs/03_modules/test2/blueprint.md",
            "summary": _make_summary("blueprint", "MOD-TEST-002"),
            "bi_name": "",
        },
        {
            "module_id": "MOD-TEST-003",
            "path": "",
            "tier": "missing",
            "domain_id": "D_TEST",
            "layer": "L2_domain",
            "build_status": "",
            "bp_ref": "",
            "summary": _make_summary("empty", "MOD-TEST-003"),
            "bi_name": "",
        },
    ]


def _make_edges() -> list[dict]:
    """构造 mock 依赖边（MOD-TEST-002 依赖 MOD-TEST-001）。"""
    return [
        {"from_module_id": "MOD-TEST-002", "to_module_id": "MOD-TEST-001", "dep_type": "import_depends"},
    ]


def _make_mod_to_stages() -> dict[str, set[str]]:
    """构造 mock 模块→环节映射（001→stock_selection, 002→buy_flow, 003 未锚定）。"""
    return {
        "MOD-TEST-001": {"stock_selection"},
        "MOD-TEST-002": {"buy_flow"},
    }


# ── classify_rows_by_stage ──────────────────────────────────


def test_classify_rows_by_stage():
    """锚定/未锚定分类正确：001→stock_selection, 002→buy_flow, 003→未锚定。"""
    rows = _make_rows()
    mod_to_stages = _make_mod_to_stages()
    anchored, unanchored = classify_rows_by_stage(rows, mod_to_stages)

    assert "stock_selection" in anchored, "缺 stock_selection 环节"
    assert "buy_flow" in anchored, "缺 buy_flow 环节"
    assert len(anchored["stock_selection"]) == 1, "stock_selection 应含 1 模块"
    assert anchored["stock_selection"][0]["module_id"] == "MOD-TEST-001"
    assert len(anchored["buy_flow"]) == 1, "buy_flow 应含 1 模块"
    assert anchored["buy_flow"][0]["module_id"] == "MOD-TEST-002"
    assert len(unanchored) == 1, "未锚定应含 1 模块"
    assert unanchored[0]["module_id"] == "MOD-TEST-003"


def test_classify_cross_stage_module():
    """跨环节模块出现在多个 stage 中。"""
    rows = _make_rows()
    mod_to_stages = {
        "MOD-TEST-001": {"stock_selection", "buy_flow"},  # 跨环节
        "MOD-TEST-002": {"buy_flow"},
    }
    anchored, unanchored = classify_rows_by_stage(rows, mod_to_stages)

    assert "MOD-TEST-001" in [r["module_id"] for r in anchored["stock_selection"]]
    assert "MOD-TEST-001" in [r["module_id"] for r in anchored["buy_flow"]]
    assert "MOD-TEST-002" in [r["module_id"] for r in anchored["buy_flow"]]
    assert len(unanchored) == 1  # MOD-TEST-003 未锚定


# ── build_module_to_file_map ────────────────────────────────


def test_build_module_to_file_map():
    """module→文件映射：锚定模块→stage文件, 未锚定→system_foundation.md。"""
    rows = _make_rows()
    mod_to_stages = _make_mod_to_stages()
    anchored, unanchored = classify_rows_by_stage(rows, mod_to_stages)
    mapping = build_module_to_file_map(anchored, unanchored)

    assert mapping["MOD-TEST-001"] == STAGE_ID_TO_FILE["stock_selection"]
    assert mapping["MOD-TEST-002"] == STAGE_ID_TO_FILE["buy_flow"]
    assert mapping["MOD-TEST-003"] == "system_foundation.md"


# ── render_index_doc ────────────────────────────────────────


def test_render_index_doc_contains_stage_index_and_quality():
    """索引含：环节索引 + 质量报告 + 位置链接。"""
    rows = _make_rows()
    edges = _make_edges()
    mod_to_stages = _make_mod_to_stages()
    anchored, unanchored = classify_rows_by_stage(rows, mod_to_stages)
    mapping = build_module_to_file_map(anchored, unanchored)

    doc = render_index_doc(rows, edges, anchored, unanchored, mapping)

    # 环节索引
    assert "按作战环节索引" in doc, "缺环节索引章节"
    assert "选股" in doc, "缺选股环节"
    assert "买入" in doc, "缺买入环节"
    assert STAGE_ID_TO_FILE["stock_selection"] in doc, "缺选股文件链接"
    assert "system_foundation.md" in doc, "缺系统基础链接"

    # 质量报告 + 位置链接
    assert "算法质量报告" in doc, "缺质量报告章节"
    assert "位置" in doc, "缺位置列"
    assert f"{STAGE_ID_TO_FILE['stock_selection']}#mod-test-001" in doc, "缺质量报告位置链接"
    assert "system_foundation.md#mod-test-003" in doc, "缺未锚定模块位置链接"

    # Mermaid 层级总览
    assert "```mermaid" in doc, "缺 Mermaid 图"

    # 三档统计
    assert "模块总数" in doc
    assert "501" not in doc  # mock 数据只有 3 模块


# ── render_stage_doc ────────────────────────────────────────


def test_render_stage_doc_contains_cards_and_anchors():
    """环节文件含：模块卡片 + layer分组 + HTML锚点 + 返回索引链接。"""
    rows = _make_rows()
    edges = _make_edges()
    mod_to_stages = _make_mod_to_stages()
    anchored, _ = classify_rows_by_stage(rows, mod_to_stages)

    stage_rows = anchored["stock_selection"]
    from generate_module_algorithm_overview import _build_consumers

    consumers = _build_consumers(edges)

    doc = render_stage_doc("stock_selection", stage_rows, edges, consumers)

    # 返回索引链接
    assert "../index.md" in doc, "缺返回索引链接"

    # 模块卡片 + 算法步骤
    assert "MOD-TEST-001" in doc, "缺模块 ID"
    assert "步骤一" in doc, "缺算法步骤"
    assert STATUS_EMOJI["operational"] in doc, "缺运营态 emoji"

    # HTML 锚点
    assert '<a id="mod-test-001"></a>' in doc, "缺 HTML 锚点"

    # layer 分组（MOD-TEST-001 在 L0）
    assert "L0_infrastructure" in doc, "缺 L0 layer 分组"

    # 真源链接
    assert "src/zephyr/test/module.py" in doc, "缺代码真源路径"


def test_render_stage_doc_stats():
    """环节文件头部含模块数和三档统计。"""
    rows = _make_rows()
    edges = _make_edges()
    mod_to_stages = _make_mod_to_stages()
    anchored, _ = classify_rows_by_stage(rows, mod_to_stages)

    stage_rows = anchored["stock_selection"]
    from generate_module_algorithm_overview import _build_consumers

    consumers = _build_consumers(edges)

    doc = render_stage_doc("stock_selection", stage_rows, edges, consumers)

    assert "1 模块" in doc, "缺模块数"
    assert "🟦运营 1" in doc, "缺运营态计数"


# ── render_system_foundation_doc ────────────────────────────


def test_render_system_foundation_doc_contains_unanchored():
    """系统基础文件含：未锚定模块卡片 + layer分组 + 返回索引链接。"""
    rows = _make_rows()
    edges = _make_edges()
    mod_to_stages = _make_mod_to_stages()
    _, unanchored = classify_rows_by_stage(rows, mod_to_stages)

    from generate_module_algorithm_overview import _build_consumers

    consumers = _build_consumers(edges)

    doc = render_system_foundation_doc(unanchored, edges, consumers)

    # 返回索引链接（system_foundation.md 在根目录，用 index.md 不用 ../）
    assert "index.md" in doc, "缺返回索引链接"

    # 未锚定模块（MOD-TEST-003, missing tier, L2_domain）
    assert "MOD-TEST-003" in doc, "缺未锚定模块"
    assert STATUS_EMOJI["missing"] in doc, "缺缺失态 emoji"
    assert '<a id="mod-test-003"></a>' in doc, "缺 HTML 锚点"

    # layer 分组（MOD-TEST-003 在 L2）
    assert "L2_domain" in doc, "缺 L2 layer 分组"

    # 头部统计
    assert "1 模块" in doc, "缺模块数"


# ── render_battle_stage_index ───────────────────────────────


def test_render_battle_stage_index_links():
    """环节索引含每个环节的文件链接和模块计数。"""
    rows = _make_rows()
    mod_to_stages = _make_mod_to_stages()
    anchored, unanchored = classify_rows_by_stage(rows, mod_to_stages)

    index = render_battle_stage_index(anchored, unanchored)

    assert "选股" in index, "缺选股环节"
    assert "买入" in index, "缺买入环节"
    assert STAGE_ID_TO_FILE["stock_selection"] in index, "缺选股文件链接"
    assert STAGE_ID_TO_FILE["buy_flow"] in index, "缺买入文件链接"
    assert "system_foundation.md" in index, "缺系统基础链接"
    assert "未锚定" in index, "缺未锚定标注"


# ── render_stats / render_mermaid / render_quality_report（保留）──


def test_render_stats():
    """文档基本信息表含正确的模块计数。"""
    rows = _make_rows()
    stats = render_stats(rows)
    assert "模块总数" in stats
    assert "3" in stats
    assert "运营态" in stats
    assert "设计态" in stats
    assert "缺失" in stats


def test_render_mermaid_contains_layers():
    """Mermaid 总览图含 layer 节点 + 层间依赖流。"""
    rows = _make_rows()
    edges = _make_edges()
    mermaid = render_mermaid_layer_overview(rows, edges)

    assert "```mermaid" in mermaid
    assert "L0_infrastructure" in mermaid, "缺 L0 节点"
    assert "L1_foundation" in mermaid, "缺 L1 节点"
    assert "L2_domain" in mermaid, "缺 L2 节点"
    assert "L1_foundation -->|" in mermaid or "L1_foundation-->" in mermaid, "缺层间依赖箭头"


def test_render_quality_report_with_location():
    """质量报告含位置链接列。"""
    rows = _make_rows()
    mod_to_stages = _make_mod_to_stages()
    anchored, unanchored = classify_rows_by_stage(rows, mod_to_stages)
    mapping = build_module_to_file_map(anchored, unanchored)

    report = render_quality_report(rows, mapping)

    assert "算法质量报告" in report
    assert "位置" in report, "缺位置列"
    assert "MOD-TEST-001" in report
    assert f"{STAGE_ID_TO_FILE['stock_selection']}#mod-test-001" in report, "缺位置链接"
    assert "system_foundation.md#mod-test-003" in report, "缺未锚定模块位置链接"


def test_render_quality_report_layer_sort():
    """质量报告按 layer → module_id 排序（L0 在 L1/L2 之前）。"""
    rows = _make_rows()
    report = render_quality_report(rows)
    pos_l0 = report.find("MOD-TEST-001")  # L0
    pos_l1 = report.find("MOD-TEST-002")  # L1
    pos_l2 = report.find("MOD-TEST-003")  # L2
    assert pos_l0 < pos_l1 < pos_l2, f"layer 排序错误: L0={pos_l0} L1={pos_l1} L2={pos_l2}"


# ── ALGO_FLOW 标记剥离 + 每图 HTML 链接（2026-08-13 回归）──


def test_algo_steps_marker_lines_stripped_with_flow():
    """算法步骤整段是 ALGO_FLOW 标记注释（# - id: 等）且有推导图：不原样贴 YAML，提示看图。"""
    rows = _make_rows()
    rows[0]["summary"].algo_steps = (
        "# - id: A1\n"
        "#   name_zh: ① canonical 路径映射表\n"
        "#   name_en: _LAZY_IMPORTS / _SUBMODULES\n"
        "#   inputs: I1\n"
        "#   outputs: (module_path, attr_name)"
    )
    rows[0]["algo_flow"] = AlgoFlowData(
        nodes=[AlgoFlowNode(id="A1", layer="算法", name_zh="① 测试算法")],
        edges=[],
    )
    consumers = _build_consumers([])

    doc = render_stage_doc("stock_selection", [rows[0]], [], consumers)

    assert "# - id:" not in doc, "算法步骤不应原样贴 ALGO_FLOW YAML 注释"
    assert "name_zh:" not in doc, "算法步骤不应含 ALGO_FLOW 字段行"
    assert "见下方推导流程图" in doc, "整段是标记且有推导图时应提示看图"


def test_algo_steps_human_text_kept_markers_stripped():
    """算法步骤人读文字+标记混合：保留人读文字，剥离标记行（无推导图）。"""
    rows = _make_rows()
    rows[0]["summary"].algo_steps = "① 先做人读步骤\n# - id: A1\n#   name_zh: 机器标记\n② 再做第二步"
    consumers = _build_consumers([])

    doc = render_stage_doc("stock_selection", [rows[0]], [], consumers)

    assert "先做人读步骤" in doc, "人读文字应保留"
    assert "再做第二步" in doc, "人读文字应保留"
    assert "name_zh" not in doc, "标记行应剥离"


def test_html_link_above_every_mermaid_block():
    """环节文件每个 Mermaid 图块上方都有可缩放 HTML 跳转链接（环节总图/关联图/推导图）。"""
    rows = _make_rows()
    # 模块推导图：给 MOD-TEST-001 加 ALGO_FLOW
    rows[0]["algo_flow"] = AlgoFlowData(
        nodes=[AlgoFlowNode(id="A1", layer="算法", name_zh="① 测试算法")],
        edges=[],
    )
    edges = _make_edges()
    consumers = _build_consumers(edges)
    rel = _build_rel_context(rows, edges, consumers)

    doc = render_stage_doc("stock_selection", [rows[0]], edges, consumers, rel)

    mermaid_cnt = doc.count("```mermaid")
    link_cnt = doc.count("可缩放大图（HTML）")
    # 环节总图 1 + 上下游关联图 1（MOD-TEST-002 是 001 下游） + 推导图 1
    assert mermaid_cnt == 3, f"应含 3 个 Mermaid 图块，实际 {mermaid_cnt}"
    assert link_cnt == mermaid_cnt, f"每个图块上方都应有 HTML 链接：图 {mermaid_cnt} 个，链接 {link_cnt} 个"
    assert "_zoomable_html/05_stock_selection.html" in doc, "链接应指向本环节 HTML"
