# [A_test] module_id: SRC-TST-202410 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] ARCHITECTURE-DIAGRAM-PLAN | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §test
# [MODULE] tests.test_align_panoramas
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.d5_architecture.generators.align_panoramas
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_align_panoramas.py
# [TTL] permanent
# [ARCH-REF] #ARCH-053
"""test_align_panoramas.py — align_panoramas.py 单元测试

覆盖：
  - PanoramaNode 数据模型字段
  - _detect_orphans 孤儿检测逻辑（仅一图存在的 module_id）
  - _detect_state_drifts 状态漂移检测逻辑（design_maturity 不一致）
  - _detect_domain_mismatches 域不一致检测逻辑
  - _detect_design_only_in_one 设计态孤立检测逻辑
  - PanoramaEmptyError 异常类型存在性
  - PanoramaAlignmentReport.to_markdown 渲染

依据：ARCH-053 裁定（2026-07-06）。
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

# 动态加载 scripts/ 下的模块（非 Python 包，需 importlib）
_SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts" / "governance" / "d5_architecture" / "generators"
    / "align_panoramas.py"
)

try:
    import sys
    _spec = importlib.util.spec_from_file_location("align_panoramas", _SCRIPT_PATH)
    _mod = importlib.util.module_from_spec(_spec)
    sys.modules["align_panoramas"] = _mod  # 注册到 sys.modules（dataclass 需要）
    _spec.loader.exec_module(_mod)
    PanoramaNode = _mod.PanoramaNode
    PanoramaAlignmentReport = _mod.PanoramaAlignmentReport
    PanoramaEmptyError = _mod.PanoramaEmptyError
    _detect_orphans = _mod._detect_orphans
    _detect_state_drifts = _mod._detect_state_drifts
    _detect_domain_mismatches = _mod._detect_domain_mismatches
    _detect_design_only_in_one = _mod._detect_design_only_in_one
except Exception as e:  # noqa: BLE001
    pytest.skip(
        f"align_panoramas 模块加载失败（可能缺少 zephyr 依赖）: {e}",
        allow_module_level=True,
    )


# ---------------------------------------------------------------------------
# 测试数据工厂
# ---------------------------------------------------------------------------


def _make_node(
    module_id: str,
    graph: str,
    entity_name: str = "",
    design_maturity: str | None = "production",
    build_status: str | None = "stable",
    domain_id: str | None = "D_TEST",
) -> PanoramaNode:
    return PanoramaNode(
        module_id=module_id,
        graph=graph,
        entity_name=entity_name or module_id,
        design_maturity=design_maturity,
        build_status=build_status,
        domain_id=domain_id,
    )


# ---------------------------------------------------------------------------
# PanoramaNode 数据模型测试
# ---------------------------------------------------------------------------


class TestPanoramaNode:
    def test_fields(self):
        n = _make_node("MOD-001", "depgraph", "path/to/mod")
        assert n.module_id == "MOD-001"
        assert n.graph == "depgraph"
        assert n.entity_name == "path/to/mod"
        assert n.design_maturity == "production"
        assert n.build_status == "stable"
        assert n.domain_id == "D_TEST"

    def test_default_entity_name(self):
        """entity_name 默认为 module_id。"""
        n = _make_node("MOD-002", "dataflow")
        assert n.entity_name == "MOD-002"


# ---------------------------------------------------------------------------
# 孤儿检测测试
# ---------------------------------------------------------------------------


class TestDetectOrphans:
    def test_no_orphans_when_same_module_in_all_graphs(self):
        """同一 module_id 在三图都有 → 不是孤儿。"""
        nodes = [
            _make_node("MOD-X", "depgraph"),
            _make_node("MOD-X", "dataflow"),
            _make_node("MOD-X", "decision"),
        ]
        assert _detect_orphans(nodes) == []

    def test_orphan_when_only_in_one_graph(self):
        """module_id 仅在一图 → 孤儿。"""
        nodes = [
            _make_node("MOD-ORPHAN", "depgraph"),
            _make_node("MOD-SHARED", "depgraph"),
            _make_node("MOD-SHARED", "dataflow"),
        ]
        orphans = _detect_orphans(nodes)
        assert len(orphans) == 1
        assert orphans[0]["module_id"] == "MOD-ORPHAN"
        assert orphans[0]["graph"] == "depgraph"

    def test_two_graphs_not_orphan(self):
        """module_id 在两图 → 不是孤儿。"""
        nodes = [
            _make_node("MOD-TWO", "depgraph"),
            _make_node("MOD-TWO", "dataflow"),
        ]
        assert _detect_orphans(nodes) == []

    def test_empty_list(self):
        assert _detect_orphans([]) == []


# ---------------------------------------------------------------------------
# 状态漂移检测测试
# ---------------------------------------------------------------------------


class TestDetectStateDrifts:
    def test_no_drift_when_same_maturity(self):
        """三图 design_maturity 相同 → 无漂移。"""
        nodes = [
            _make_node("MOD-X", "depgraph", design_maturity="design"),
            _make_node("MOD-X", "dataflow", design_maturity="design"),
            _make_node("MOD-X", "decision", design_maturity="design"),
        ]
        assert _detect_state_drifts(nodes) == []

    def test_drift_when_maturity_differs(self):
        """三图 design_maturity 不一致 → 漂移。"""
        nodes = [
            _make_node("MOD-X", "depgraph", design_maturity="design"),
            _make_node("MOD-X", "dataflow", design_maturity="production"),
            _make_node("MOD-X", "decision", design_maturity="prototype"),
        ]
        drifts = _detect_state_drifts(nodes)
        assert len(drifts) == 1
        assert drifts[0]["module_id"] == "MOD-X"
        assert drifts[0]["depgraph"] == "design"
        assert drifts[0]["dataflow"] == "production"
        assert drifts[0]["decision"] == "prototype"

    def test_no_drift_when_only_one_graph(self):
        """仅一图存在 → 不构成漂移。"""
        nodes = [_make_node("MOD-SOLO", "depgraph", design_maturity="design")]
        assert _detect_state_drifts(nodes) == []


# ---------------------------------------------------------------------------
# 域不一致检测测试
# ---------------------------------------------------------------------------


class TestDetectDomainMismatches:
    def test_no_mismatch_when_same_domain(self):
        nodes = [
            _make_node("MOD-X", "depgraph", domain_id="D_A"),
            _make_node("MOD-X", "dataflow", domain_id="D_A"),
        ]
        assert _detect_domain_mismatches(nodes) == []

    def test_mismatch_when_domains_differ(self):
        nodes = [
            _make_node("MOD-X", "depgraph", domain_id="D_A"),
            _make_node("MOD-X", "dataflow", domain_id="D_B"),
        ]
        mismatches = _detect_domain_mismatches(nodes)
        assert len(mismatches) == 1
        assert mismatches[0]["module_id"] == "MOD-X"
        assert mismatches[0]["depgraph"] == "D_A"
        assert mismatches[0]["dataflow"] == "D_B"

    def test_no_mismatch_when_domain_null(self):
        """domain_id 为 None 不参与比较。"""
        nodes = [
            _make_node("MOD-X", "depgraph", domain_id=None),
            _make_node("MOD-X", "dataflow", domain_id="D_A"),
        ]
        assert _detect_domain_mismatches(nodes) == []


# ---------------------------------------------------------------------------
# 设计态孤立检测测试
# ---------------------------------------------------------------------------


class TestDetectDesignOnlyInOne:
    def test_design_only_in_one_graph(self):
        """design 状态仅在一图 → 孤立。"""
        nodes = [
            _make_node("MOD-DESIGN", "depgraph", design_maturity="design"),
        ]
        design_only = _detect_design_only_in_one(nodes)
        assert len(design_only) == 1
        assert design_only[0]["module_id"] == "MOD-DESIGN"
        assert design_only[0]["graph"] == "depgraph"

    def test_design_in_multiple_graphs_not_isolated(self):
        """design 状态在多图 → 不是孤立。"""
        nodes = [
            _make_node("MOD-X", "depgraph", design_maturity="design"),
            _make_node("MOD-X", "dataflow", design_maturity="design"),
        ]
        assert _detect_design_only_in_one(nodes) == []

    def test_production_only_not_isolated(self):
        """非 design 状态不检测孤立。"""
        nodes = [
            _make_node("MOD-PROD", "depgraph", design_maturity="production"),
        ]
        assert _detect_design_only_in_one(nodes) == []


# ---------------------------------------------------------------------------
# PanoramaEmptyError 异常测试
# ---------------------------------------------------------------------------


class TestPanoramaEmptyError:
    def test_is_runtime_error(self):
        assert issubclass(PanoramaEmptyError, RuntimeError)

    def test_can_be_raised(self):
        with pytest.raises(PanoramaEmptyError, match="empty"):
            raise PanoramaEmptyError("test empty")


# ---------------------------------------------------------------------------
# PanoramaAlignmentReport 渲染测试
# ---------------------------------------------------------------------------


class TestPanoramaAlignmentReport:
    def test_to_markdown_contains_sections(self):
        report = PanoramaAlignmentReport(
            generated_at="2026-07-06 12:00:00",
            depgraph_count=10,
            dataflow_count=5,
            decision_count=3,
            issues_total=0,
        )
        md = report.to_markdown()
        assert "# 三图对齐报告" in md
        assert "## 1. 孤儿节点" in md
        assert "## 2. 状态漂移" in md
        assert "## 3. 域不一致" in md
        assert "## 4. 设计态孤立" in md
        assert "## 5. 处置建议" in md

    def test_to_markdown_shows_counts(self):
        report = PanoramaAlignmentReport(
            generated_at="2026-07-06",
            depgraph_count=100,
            dataflow_count=50,
            decision_count=25,
            issues_total=10,
            orphans=[{"module_id": "M1", "graph": "depgraph", "entity_name": "e1"}],
        )
        md = report.to_markdown()
        assert "depgraph=100" in md
        assert "dataflow=50" in md
        assert "decision=25" in md
        assert "孤儿（仅一图）: 1" in md

    def test_empty_report(self):
        report = PanoramaAlignmentReport()
        md = report.to_markdown()
        assert "无孤儿节点" in md
        assert "无状态漂移" in md
        assert "无域不一致" in md
        assert "无设计态孤立" in md
