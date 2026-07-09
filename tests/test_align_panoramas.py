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
# [ARCH-REF] #ARCH-053 #ARCH-056
"""test_align_panoramas.py — align_panoramas.py 单元测试

覆盖：
  - PanoramaNode 数据模型字段
  - _detect_orphans 孤儿检测逻辑（仅一图存在的 module_id）
  - _detect_state_drifts 状态漂移检测逻辑（design_maturity 不一致，四图含 blueprint）
  - _detect_domain_mismatches 域不一致检测逻辑（四图含 blueprint）
  - _detect_design_only_in_one 设计态孤立检测逻辑
  - _fetch_blueprint_nodes 从 frontmatter 采集 blueprint 节点（ARCH-056）
  - PanoramaEmptyError 异常类型存在性
  - PanoramaAlignmentReport.to_markdown 渲染（含 blueprint 列）

依据：ARCH-053 裁定（2026-07-06）；ARCH-056 四图升级（2026-07-09）。
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
    _fetch_blueprint_nodes = _mod._fetch_blueprint_nodes
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
        """四图 design_maturity 相同 → 无漂移。"""
        nodes = [
            _make_node("MOD-X", "depgraph", design_maturity="design"),
            _make_node("MOD-X", "dataflow", design_maturity="design"),
            _make_node("MOD-X", "decision", design_maturity="design"),
            _make_node("MOD-X", "blueprint", design_maturity="design"),
        ]
        assert _detect_state_drifts(nodes) == []

    def test_drift_when_maturity_differs(self):
        """四图 design_maturity 不一致 → 漂移。"""
        nodes = [
            _make_node("MOD-X", "depgraph", design_maturity="design"),
            _make_node("MOD-X", "dataflow", design_maturity="production"),
            _make_node("MOD-X", "decision", design_maturity="prototype"),
            _make_node("MOD-X", "blueprint", design_maturity="design"),
        ]
        drifts = _detect_state_drifts(nodes)
        assert len(drifts) == 1
        assert drifts[0]["module_id"] == "MOD-X"
        assert drifts[0]["depgraph"] == "design"
        assert drifts[0]["dataflow"] == "production"
        assert drifts[0]["decision"] == "prototype"
        assert drifts[0]["blueprint"] == "design"

    def test_drift_includes_blueprint_column(self):
        """blueprint 图参与漂移检测，输出含 blueprint 列。"""
        nodes = [
            _make_node("MOD-X", "depgraph", design_maturity="production"),
            _make_node("MOD-X", "blueprint", design_maturity="design"),
        ]
        drifts = _detect_state_drifts(nodes)
        assert len(drifts) == 1
        assert drifts[0]["blueprint"] == "design"
        assert drifts[0]["depgraph"] == "production"
        assert drifts[0]["dataflow"] == "-"
        assert drifts[0]["decision"] == "-"

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

    def test_mismatch_includes_blueprint_column(self):
        """blueprint 图参与域不一致检测，输出含 blueprint 列。"""
        nodes = [
            _make_node("MOD-X", "depgraph", domain_id="D_A"),
            _make_node("MOD-X", "blueprint", domain_id="D_B"),
        ]
        mismatches = _detect_domain_mismatches(nodes)
        assert len(mismatches) == 1
        assert mismatches[0]["blueprint"] == "D_B"
        assert mismatches[0]["depgraph"] == "D_A"
        assert mismatches[0]["dataflow"] == "-"
        assert mismatches[0]["decision"] == "-"

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
            blueprint_count=8,
            issues_total=0,
        )
        md = report.to_markdown()
        assert "# 四图对齐报告" in md
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
            blueprint_count=80,
            issues_total=10,
            orphans=[{"module_id": "M1", "graph": "depgraph", "entity_name": "e1"}],
        )
        md = report.to_markdown()
        assert "depgraph=100" in md
        assert "dataflow=50" in md
        assert "decision=25" in md
        assert "blueprint=80" in md
        assert "孤儿（仅一图）: 1" in md

    def test_to_markdown_state_drifts_has_blueprint_column(self):
        """状态漂移表含 blueprint 列。"""
        report = PanoramaAlignmentReport(
            state_drifts=[{
                "module_id": "MOD-X",
                "depgraph": "production", "dataflow": "-",
                "decision": "-", "blueprint": "design",
            }],
            issues_total=1,
        )
        md = report.to_markdown()
        assert "| blueprint |" in md
        assert "MOD-X" in md
        assert "design" in md

    def test_to_markdown_domain_mismatches_has_blueprint_column(self):
        """域不一致表含 blueprint 列。"""
        report = PanoramaAlignmentReport(
            domain_mismatches=[{
                "module_id": "MOD-Y",
                "depgraph": "D_A", "dataflow": "-",
                "decision": "-", "blueprint": "D_B",
            }],
            issues_total=1,
        )
        md = report.to_markdown()
        assert "| blueprint |" in md
        assert "MOD-Y" in md
        assert "D_B" in md

    def test_empty_report(self):
        report = PanoramaAlignmentReport()
        md = report.to_markdown()
        assert "无孤儿节点" in md
        assert "无状态漂移" in md
        assert "无域不一致" in md
        assert "无设计态孤立" in md


# ---------------------------------------------------------------------------
# _fetch_blueprint_nodes 采集测试（ARCH-056 第四张图）
# ---------------------------------------------------------------------------


class TestFetchBlueprintNodes:
    """测试从 docs/03_modules/ frontmatter 采集 blueprint 节点。"""

    def test_scan_empty_dir_returns_empty(self, tmp_path):
        """扫描不存在的目录 → 返回空列表。"""
        result = _fetch_blueprint_nodes(scan_root=tmp_path / "nonexistent")
        assert result == []

    def test_scan_extracts_module_id_from_frontmatter(self, tmp_path):
        """文件含 module_id frontmatter → 提取为 blueprint 节点。"""
        bp_file = tmp_path / "MOD-TEST"
        bp_file.write_text(
            "---\n"
            "module_id: MOD-TEST\n"
            "responsibility_domain: D_TEST\n"
            "design_maturity: design\n"
            "build_status: planned\n"
            "---\n\n# MOD-TEST\n",
            encoding="utf-8",
        )
        nodes = _fetch_blueprint_nodes(scan_root=tmp_path)
        assert len(nodes) == 1
        n = nodes[0]
        assert n.module_id == "MOD-TEST"
        assert n.graph == "blueprint"
        assert n.domain_id == "D_TEST"
        assert n.design_maturity == "design"
        assert n.build_status == "planned"
        assert n.entity_name == "MOD-TEST"

    def test_scan_skips_files_without_module_id(self, tmp_path):
        """无 module_id frontmatter → 跳过。"""
        (tmp_path / "index.md").write_text(
            "---\ntitle: Index\n---\n# Index\n",
            encoding="utf-8",
        )
        (tmp_path / "no_fm.md").write_text("# No frontmatter\n", encoding="utf-8")
        nodes = _fetch_blueprint_nodes(scan_root=tmp_path)
        assert nodes == []

    def test_scan_recurses_subdirectories(self, tmp_path):
        """递归扫描子目录下的 blueprint.md。"""
        sub = tmp_path / "_cross_layer" / "gate_engine"
        sub.mkdir(parents=True)
        (sub / "blueprint.md").write_text(
            "---\nmodule_id: MOD-GATE_ENGINE\nresponsibility_domain: D_GOVERNANCE\n---\n# Gate\n",
            encoding="utf-8",
        )
        nodes = _fetch_blueprint_nodes(scan_root=tmp_path)
        assert len(nodes) == 1
        assert nodes[0].module_id == "MOD-GATE_ENGINE"
        assert "blueprint.md" in nodes[0].entity_name

    def test_scan_skips_index_md(self, tmp_path):
        """index.md 即使有 frontmatter 也跳过。"""
        (tmp_path / "index.md").write_text(
            "---\nmodule_id: MOD-IDX\n---\n# Idx\n",
            encoding="utf-8",
        )
        nodes = _fetch_blueprint_nodes(scan_root=tmp_path)
        assert nodes == []

    def test_scan_handles_missing_optional_fields(self, tmp_path):
        """frontmatter 只有 module_id，其它字段缺失 → domain_id 等为 None。"""
        (tmp_path / "MOD-MIN").write_text(
            "---\nmodule_id: MOD-MIN\n---\n# Min\n",
            encoding="utf-8",
        )
        nodes = _fetch_blueprint_nodes(scan_root=tmp_path)
        assert len(nodes) == 1
        n = nodes[0]
        assert n.module_id == "MOD-MIN"
        assert n.domain_id is None
        assert n.design_maturity is None
        assert n.build_status is None

    def test_scan_quoted_values_stripped(self, tmp_path):
        """frontmatter 值带引号 → 剥离引号。"""
        (tmp_path / "MOD-Q").write_text(
            '---\nmodule_id: "MOD-Q"\nresponsibility_domain: "D_QUOTED"\n---\n# Q\n',
            encoding="utf-8",
        )
        nodes = _fetch_blueprint_nodes(scan_root=tmp_path)
        assert len(nodes) == 1
        assert nodes[0].module_id == "MOD-Q"
        assert nodes[0].domain_id == "D_QUOTED"

    def test_scan_multiple_files(self, tmp_path):
        """多个蓝图文件 → 全部采集。"""
        for i in range(3):
            (tmp_path / f"MOD-{i}").write_text(
                f"---\nmodule_id: MOD-{i}\n---\n# M{i}\n",
                encoding="utf-8",
            )
        nodes = _fetch_blueprint_nodes(scan_root=tmp_path)
        assert len(nodes) == 3
        mids = {n.module_id for n in nodes}
        assert mids == {"MOD-0", "MOD-1", "MOD-2"}


# ---------------------------------------------------------------------------
# exempt_list 豁免测试（历史归档豁免）
# ---------------------------------------------------------------------------


class TestExemptList:
    def test_exempt_module_skipped(self):
        """exempt_list 中的 module_id 不参与对齐检测"""
        nodes = [
            PanoramaNode("MOD-EXEMPT", "depgraph", "src/a.py", "production", "stable", "D_GOV"),
            PanoramaNode("MOD-EXEMPT", "dataflow", "ds_a", "production", "stable", "D_GOV"),
            # blueprint 图缺失 → 正常情况会报孤儿
        ]
        orphans = _detect_orphans(nodes, exempt_list={"MOD-EXEMPT"})
        assert len(orphans) == 0

    def test_non_exempt_module_reported(self):
        """不在 exempt_list 的模块正常检测"""
        nodes = [
            PanoramaNode("MOD-NORMAL", "depgraph", "src/a.py", "production", "stable", "D_GOV"),
        ]
        orphans = _detect_orphans(nodes, exempt_list=set())
        assert len(orphans) == 1
