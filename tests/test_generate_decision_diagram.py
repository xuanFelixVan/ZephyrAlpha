# [A_test] module_id: SRC-TST-9006 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-SCRIPTS | docs/03_modules/_domain_governance/blueprint.md | §decisiongraph
# [MODULE] tests.test_generate_decision_diagram
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.d5_architecture.generators.generate_decision_diagram
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_generate_decision_diagram.py
# [TTL] permanent
# [ARCH-REF] #TRAE-061
"""test_generate_decision_diagram.py — generate_decision_diagram.py 单元测试

覆盖：
  - _build_status_color 颜色映射（5 个 build_status + 默认值）
  - _load_invariants 从 YAML 真源读取 5 条承重墙不变量
  - _gen_overview_mmd 返回值类型（tuple[str, int, int, int]）+ subgraph + classDef
  - _gen_layers_mmd 层级卡片 + 反馈边（L6 → L1/L5）
  - _gen_invariants_mmd 6 节点类型 + 5 不变量 + 非法连接标注
  - _gen_index_md 统计表 + Track/Layer 清单

依据：TRAE-061 任务（2026-07-06）。
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

# 动态加载 scripts/ 下的模块（非 Python 包，需 importlib）
_SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts" / "governance" / "d5_architecture" / "generators"
    / "generate_decision_diagram.py"
)
_YAML_PATH = (
    Path(__file__).resolve().parents[1]
    / "architecture_model" / "domain" / "decision_graph_model.yaml"
)

try:
    _spec = importlib.util.spec_from_file_location(
        "generate_decision_diagram", _SCRIPT_PATH
    )
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    _build_status_color = _mod._build_status_color
    _load_invariants = _mod._load_invariants
    _gen_overview_mmd = _mod._gen_overview_mmd
    _gen_layers_mmd = _mod._gen_layers_mmd
    _gen_invariants_mmd = _mod._gen_invariants_mmd
    _gen_index_md = _mod._gen_index_md
    _resolve_blueprint_names = _mod._resolve_blueprint_names
    _truncate = _mod._truncate
    OUTPUT_DIR = _mod.OUTPUT_DIR
    _YAML_PATH_FROM_MOD = _mod._YAML_PATH
except Exception as e:  # noqa: BLE001
    pytest.skip(
        f"generate_decision_diagram 模块加载失败（可能缺少 zephyr 依赖）: {e}",
        allow_module_level=True,
    )


# ---------- Fixtures ----------

@pytest.fixture
def sample_tracks():
    """2 个 Track（model_driven + emergency）。"""
    return [
        {"id": "model_driven", "name": "模型驱动轨", "name_en": "Model Driven",
         "desc": "正常运行时", "priority": 1, "activation": "正常运行时"},
        {"id": "emergency", "name": "应急保命轨", "name_en": "Emergency",
         "desc": "所有信号失效时", "priority": 4, "activation": "所有模型/策略/信号失效时"},
    ]


@pytest.fixture
def sample_layers():
    """4 个 Layer（L0/L1/L2A/L4），含 module_id + source_code_ref + desc。"""
    return [
        {"id": "L0", "name": "数据接入与预处理层", "name_en": "Data Ingestion",
         "track": "model_driven", "desc": "miniQMT+iFind数据接入与预处理", "freq": "tick",
         "maturity": "production", "build": "stable",
         "module_id": "MOD-DATA-001", "source_code_ref": "src/zephyr/data/ingestion.py",
         "blueprint_name": "数据接入蓝图"},
        {"id": "L1", "name": "因子计算层", "name_en": "Factor Computation",
         "track": "model_driven", "desc": "因子工厂全生命周期管理", "freq": "daily",
         "maturity": "production", "build": "stable",
         "module_id": "MOD-FACTOR-001", "source_code_ref": "src/zephyr/factor/calc.py",
         "blueprint_name": "因子计算蓝图"},
        {"id": "L2A", "name": "信号层", "name_en": "Signal",
         "track": "model_driven", "desc": "信号工厂多策略投票", "freq": "daily",
         "maturity": "design", "build": "planned",
         "module_id": "", "source_code_ref": ""},
        {"id": "L4", "name": "风控层", "name_en": "Risk Control",
         "track": "model_driven", "desc": "Pre/Post-Trade风控校验", "freq": "realtime",
         "maturity": "production", "build": "stable",
         "module_id": "MOD-RISK-001", "source_code_ref": "src/zephyr/risk/checker.py",
         "blueprint_name": "风控蓝图"},
    ]


@pytest.fixture
def sample_nodes():
    """3 个 Node（含 design_maturity 区分设计态/运营态 + source_code_ref）。"""
    return [
        {"id": 1, "layer_id": "L0", "type": "signal", "path": "ingest.tick",
         "module_id": "MOD-DATA-001", "name": "Tick接入", "build": "stable",
         "maturity": "production", "hash": "abc123", "source_code_ref": "src/zephyr/data/ingest.py"},
        {"id": 2, "layer_id": "L2A", "type": "signal", "path": "signal.momentum",
         "module_id": "MOD-SIG-001", "name": "动量信号", "build": "planned",
         "maturity": "design", "hash": "def456", "source_code_ref": ""},
        {"id": 3, "layer_id": "L4", "type": "risk_check", "path": "risk.checker",
         "module_id": "MOD-RISK-001", "name": "风控检查", "build": "stable",
         "maturity": "production", "hash": "ghi789", "source_code_ref": "src/zephyr/risk/check.py"},
    ]


@pytest.fixture
def sample_edges():
    """2 条 Edge。"""
    return [
        {"id": 100, "from": 1, "to": 2, "type": "informing",
         "condition": None, "track": "model_driven"},
        {"id": 101, "from": 2, "to": 3, "type": "triggering",
         "condition": "signal_active", "track": "model_driven"},
    ]


@pytest.fixture
def sample_invariants():
    """5 条承重墙不变量（与 YAML 真源一致）。"""
    return [
        {"id": "DEC-INV-001", "name": "风控一票否决", "name_en": "Risk Veto Mandatory"},
        {"id": "DEC-INV-002", "name": "信号仓位分离", "name_en": "Signal-Order Separation"},
        {"id": "DEC-INV-003", "name": "DAG 无环", "name_en": "DAG No Cycle"},
        {"id": "DEC-INV-004", "name": "时间单调性", "name_en": "Time Monotonicity"},
        {"id": "DEC-INV-005", "name": "证据哈希必填", "name_en": "Evidence Hash Required"},
    ]


# ---------- 导入与结构测试 ----------

class TestImportAndStructure:
    """模块导入与常量结构验证。"""

    def test_module_loads(self):
        """模块成功加载。"""
        assert _mod is not None

    def test_output_dir_constant(self):
        """OUTPUT_DIR 指向 06_decision_architecture/。"""
        assert "docs" in str(OUTPUT_DIR)
        assert "02_enterprise_architecture" in str(OUTPUT_DIR)
        assert "06_decision_architecture" in str(OUTPUT_DIR)

    def test_yaml_path_constant(self):
        """_YAML_PATH 指向 decision_graph_model.yaml。"""
        assert _YAML_PATH_FROM_MOD.name == "decision_graph_model.yaml"
        assert _YAML_PATH_FROM_MOD.exists()

    def test_main_function_exists(self):
        """main 函数存在且可调用。"""
        assert callable(_mod.main)

    def test_fetch_function_exists(self):
        """_fetch_decision_data 函数存在。"""
        assert callable(_mod._fetch_decision_data)


# ---------- _build_status_color 测试 ----------

class TestBuildStatusColor:
    """build_status → mermaid 颜色类映射。"""

    def test_stable(self):
        assert _build_status_color("stable") == "bsStable"

    def test_generated(self):
        assert _build_status_color("generated") == "bsGenerated"

    def test_testing(self):
        assert _build_status_color("testing") == "bsTesting"

    def test_planned(self):
        assert _build_status_color("planned") == "bsPlanned"

    def test_deprecated(self):
        assert _build_status_color("deprecated") == "bsDeprecated"

    def test_unknown_returns_default(self):
        """未知 build_status 返回默认 bsGenerated。"""
        assert _build_status_color("unknown") == "bsGenerated"
        assert _build_status_color("") == "bsGenerated"


# ---------- _load_invariants 测试 ----------

class TestLoadInvariants:
    """从 YAML 真源读取 invariants。"""

    def test_returns_list(self):
        """返回列表。"""
        invs = _load_invariants()
        assert isinstance(invs, list)

    def test_returns_five_invariants(self):
        """返回 5 条承重墙不变量。"""
        invs = _load_invariants()
        assert len(invs) == 5

    def test_invariant_ids(self):
        """5 条不变量 ID 为 DEC-INV-001~005。"""
        invs = _load_invariants()
        ids = [inv["id"] for inv in invs]
        assert "DEC-INV-001" in ids
        assert "DEC-INV-002" in ids
        assert "DEC-INV-003" in ids
        assert "DEC-INV-004" in ids
        assert "DEC-INV-005" in ids

    def test_invariant_has_required_fields(self):
        """每条不变量含 id/name/name_en 字段。"""
        invs = _load_invariants()
        for inv in invs:
            assert "id" in inv
            assert "name" in inv
            assert "name_en" in inv


# ---------- _gen_overview_mmd 测试 ----------

class TestGenOverviewMmd:
    """全景图生成测试。"""

    def test_returns_tuple_of_four(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """返回 4 元组 (mmd_text, track_count, layer_count, edge_count)。"""
        result = _gen_overview_mmd(sample_tracks, sample_layers, sample_nodes, sample_edges)
        assert isinstance(result, tuple)
        assert len(result) == 4
        mmd, t_count, l_count, e_count = result
        assert isinstance(mmd, str)
        assert isinstance(t_count, int)
        assert isinstance(l_count, int)
        assert isinstance(e_count, int)

    def test_counts_match_input(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """计数与输入一致。"""
        mmd, t_count, l_count, e_count = _gen_overview_mmd(
            sample_tracks, sample_layers, sample_nodes, sample_edges
        )
        assert t_count == 2  # 2 tracks
        assert l_count == 4  # 4 layers
        assert e_count == 2  # 2 edges

    def test_starts_with_flowchart_td(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """mmd 以 flowchart TD 开头。"""
        mmd, _, _, _ = _gen_overview_mmd(sample_tracks, sample_layers, sample_nodes, sample_edges)
        assert mmd.startswith("flowchart TD")

    def test_contains_subgraphs(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """mmd 包含每个 track 的 subgraph。"""
        mmd, _, _, _ = _gen_overview_mmd(sample_tracks, sample_layers, sample_nodes, sample_edges)
        assert "subgraph track_model_driven" in mmd
        assert "subgraph track_emergency" in mmd

    def test_contains_layer_nodes(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """mmd 包含 layer 节点（L0/L1/L2A/L4）。"""
        mmd, _, _, _ = _gen_overview_mmd(sample_tracks, sample_layers, sample_nodes, sample_edges)
        assert "LL0" in mmd
        assert "LL1" in mmd
        assert "LL2A" in mmd
        assert "LL4" in mmd

    def test_contains_class_defs(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """mmd 包含 5 个 classDef 样式定义。"""
        mmd, _, _, _ = _gen_overview_mmd(sample_tracks, sample_layers, sample_nodes, sample_edges)
        assert "classDef bsStable" in mmd
        assert "classDef bsGenerated" in mmd
        assert "classDef bsTesting" in mmd
        assert "classDef bsPlanned" in mmd
        assert "classDef bsDeprecated" in mmd

    def test_empty_input(self):
        """空输入返回空图 + 零计数。"""
        mmd, t_count, l_count, e_count = _gen_overview_mmd([], [], [], [])
        assert t_count == 0
        assert l_count == 0
        assert e_count == 0
        assert mmd.startswith("flowchart TD")

    def test_maturity_tag_in_labels(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """全景图节点标签包含 [design]/[production] 标注。"""
        mmd, _, _, _ = _gen_overview_mmd(sample_tracks, sample_layers, sample_nodes, sample_edges)
        # sample_layers 中 L0/L1/L4=production, L2A=design
        assert "[production]" in mmd
        assert "[design]" in mmd

    def test_production_only_filters_design(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """production_only=True 过滤掉 design_maturity=design 的 layer/node。"""
        mmd, _, l_count, _ = _gen_overview_mmd(
            sample_tracks, sample_layers, sample_nodes, sample_edges, production_only=True
        )
        # sample_layers: L0/L1/L4=production(3), L2A=design(1) → 过滤后 3 层
        assert l_count == 3
        # L2A（design）不应出现
        assert "LL2A" not in mmd
        # L0/L1/L4（production）应出现
        assert "LL0" in mmd
        assert "LL1" in mmd
        assert "LL4" in mmd
        # node 2（design, layer=L2A）不应出现
        assert "N2" not in mmd
        # node 1/3（production）应出现
        assert "N1" in mmd
        assert "N3" in mmd

    def test_production_only_empty_when_no_production(self, sample_tracks):
        """production_only=True 时若无 production layer 则返回空图。"""
        design_only_layers = [
            {"id": "L0", "name": "测试", "name_en": "Test", "track": "model_driven",
             "desc": "", "freq": "daily", "maturity": "design", "build": "planned"},
        ]
        mmd, _, l_count, _ = _gen_overview_mmd(
            sample_tracks, design_only_layers, [], [], production_only=True
        )
        assert l_count == 0
        assert mmd.startswith("flowchart TD")

    def test_design_only_filters_production(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """design_only=True 过滤掉 design_maturity=production 的 layer/node。"""
        mmd, _, l_count, _ = _gen_overview_mmd(
            sample_tracks, sample_layers, sample_nodes, sample_edges, design_only=True
        )
        # sample_layers: L0/L1/L4=production(3), L2A=design(1) → 过滤后 1 层
        assert l_count == 1
        # L0/L1/L4（production）不应出现
        assert "LL0" not in mmd
        assert "LL1" not in mmd
        assert "LL4" not in mmd
        # L2A（design）应出现
        assert "LL2A" in mmd
        # node 1/3（production）不应出现
        assert "N1" not in mmd
        assert "N3" not in mmd
        # node 2（design, layer=L2A）应出现
        assert "N2" in mmd

    def test_design_only_empty_when_no_design(self, sample_tracks):
        """design_only=True 时若无 design layer 则返回空图。"""
        prod_only_layers = [
            {"id": "L0", "name": "测试", "name_en": "Test", "track": "model_driven",
             "desc": "", "freq": "daily", "maturity": "production", "build": "stable"},
        ]
        mmd, _, l_count, _ = _gen_overview_mmd(
            sample_tracks, prod_only_layers, [], [], design_only=True
        )
        assert l_count == 0
        assert mmd.startswith("flowchart TD")


# ---------- _maturity_tag 测试 ----------

class TestMaturityTag:
    """design_maturity → 标注标签映射。"""

    def test_production(self):
        assert _mod._maturity_tag("production") == "[production]"

    def test_design(self):
        assert _mod._maturity_tag("design") == "[design]"

    def test_prototype(self):
        assert _mod._maturity_tag("prototype") == "[prototype]"

    def test_none_returns_empty(self):
        assert _mod._maturity_tag(None) == ""

    def test_empty_returns_empty(self):
        assert _mod._maturity_tag("") == ""


# ---------- _gen_layers_mmd 测试 ----------

class TestGenLayersMmd:
    """层级详情图生成测试。"""

    def test_returns_str(self, sample_tracks, sample_layers):
        """返回字符串。"""
        mmd = _gen_layers_mmd(sample_tracks, sample_layers)
        assert isinstance(mmd, str)

    def test_starts_with_flowchart_lr(self, sample_tracks, sample_layers):
        """mmd 以 flowchart LR 开头。"""
        mmd = _gen_layers_mmd(sample_tracks, sample_layers)
        assert mmd.startswith("flowchart LR")

    def test_contains_layer_cards(self, sample_tracks, sample_layers):
        """mmd 包含每个 layer 的卡片。"""
        mmd = _gen_layers_mmd(sample_tracks, sample_layers)
        assert "LL0" in mmd
        assert "LL1" in mmd
        assert "LL2A" in mmd
        assert "LL4" in mmd

    def test_contains_triggering_edges(self, sample_tracks, sample_layers):
        """mmd 包含层间 triggering 边。"""
        mmd = _gen_layers_mmd(sample_tracks, sample_layers)
        assert "|triggering|" in mmd

    def test_contains_class_defs(self, sample_tracks, sample_layers):
        """mmd 包含 classDef 样式。"""
        mmd = _gen_layers_mmd(sample_tracks, sample_layers)
        assert "classDef bsStable" in mmd
        assert "classDef bsPlanned" in mmd

    def test_empty_input(self):
        """空输入返回空图。"""
        mmd = _gen_layers_mmd([], [])
        assert mmd.startswith("flowchart LR")


# ---------- _gen_invariants_mmd 测试 ----------

class TestGenInvariantsMmd:
    """不变量图生成测试。"""

    def test_returns_str(self, sample_invariants):
        """返回字符串。"""
        mmd = _gen_invariants_mmd(sample_invariants)
        assert isinstance(mmd, str)

    def test_starts_with_flowchart_td(self, sample_invariants):
        """mmd 以 flowchart TD 开头。"""
        mmd = _gen_invariants_mmd(sample_invariants)
        assert mmd.startswith("flowchart TD")

    def test_contains_six_node_types(self, sample_invariants):
        """mmd 包含 6 个节点类型（signal/portfolio_target/risk_check/order/execution/feedback）。"""
        mmd = _gen_invariants_mmd(sample_invariants)
        assert "NT_signal" in mmd
        assert "NT_portfolio_target" in mmd
        assert "NT_risk_check" in mmd
        assert "NT_order" in mmd
        assert "NT_execution" in mmd
        assert "NT_feedback" in mmd

    def test_contains_invariant_annotations(self, sample_invariants):
        """mmd 包含 5 个不变量标注节点。"""
        mmd = _gen_invariants_mmd(sample_invariants)
        assert "INV_DEC_INV_001" in mmd
        assert "INV_DEC_INV_002" in mmd
        assert "INV_DEC_INV_003" in mmd
        assert "INV_DEC_INV_004" in mmd
        assert "INV_DEC_INV_005" in mmd

    def test_contains_illegal_connection(self, sample_invariants):
        """mmd 包含 DEC-INV-002 非法连接标注（signal -.->|禁止| order）。"""
        mmd = _gen_invariants_mmd(sample_invariants)
        assert "禁止" in mmd
        assert "NT_signal" in mmd
        assert "NT_order" in mmd

    def test_contains_class_defs(self, sample_invariants):
        """mmd 包含 nodeType + invariant classDef。"""
        mmd = _gen_invariants_mmd(sample_invariants)
        assert "classDef nodeType" in mmd
        assert "classDef invariant" in mmd

    def test_empty_invariants(self):
        """空 invariants 仍生成 6 节点类型（不变量标注为空）。"""
        mmd = _gen_invariants_mmd([])
        assert "NT_signal" in mmd
        assert "NT_order" in mmd


# ---------- _gen_index_md 测试 ----------

class TestGenIndexMd:
    """索引文档生成测试。"""

    def test_returns_str(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """返回字符串。"""
        md = _gen_index_md(sample_tracks, sample_layers, sample_nodes, sample_edges)
        assert isinstance(md, str)

    def test_contains_title(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """md 包含标题。"""
        md = _gen_index_md(sample_tracks, sample_layers, sample_nodes, sample_edges)
        assert "# 决策流图（decisiongraph）索引" in md

    def test_stats_table(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """统计表正确。"""
        md = _gen_index_md(sample_tracks, sample_layers, sample_nodes, sample_edges)
        assert "| Track（轨） | 2 |" in md
        assert "| Layer（层） | 4 |" in md
        assert "| Node（节点） | 3 |" in md
        assert "| Edge（边） | 2 |" in md

    def test_contains_track_list(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """md 包含 Track 清单。"""
        md = _gen_index_md(sample_tracks, sample_layers, sample_nodes, sample_edges)
        assert "model_driven" in md
        assert "emergency" in md
        assert "模型驱动轨" in md
        assert "应急保命轨" in md

    def test_contains_layer_list(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """md 包含 Layer 清单。"""
        md = _gen_index_md(sample_tracks, sample_layers, sample_nodes, sample_edges)
        assert "L0" in md
        assert "L1" in md
        assert "L2A" in md
        assert "L4" in md
        assert "数据接入与预处理层" in md
        assert "风控层" in md

    def test_contains_node_list(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """md 包含 Node 清单。"""
        md = _gen_index_md(sample_tracks, sample_layers, sample_nodes, sample_edges)
        assert "ingest.tick" in md
        assert "signal.momentum" in md
        assert "risk.checker" in md

    def test_contains_edge_list(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """md 包含 Edge 清单。"""
        md = _gen_index_md(sample_tracks, sample_layers, sample_nodes, sample_edges)
        assert "informing" in md
        assert "triggering" in md

    def test_empty_input_no_node_edge_tables(self):
        """空 nodes/edges 时不生成 Node/Edge 清单表。"""
        md = _gen_index_md([], [], [], [])
        assert "## Node 清单" not in md
        assert "## Edge 清单" not in md

    def test_contains_embedded_mermaid_blocks(self, sample_tracks, sample_layers, sample_nodes, sample_edges, sample_invariants):
        """md 包含 5 个内嵌 ```mermaid 代码块（全景图 + 运营态 + 设计态 + 层级图 + 不变量图）。"""
        md = _gen_index_md(sample_tracks, sample_layers, sample_nodes, sample_edges, sample_invariants)
        # 5 个 ```mermaid 开场标记
        assert md.count("```mermaid") == 5
        # 不再生成 .mmd 文件链接
        assert "decision_overview.mmd" not in md
        assert "decision_layers.mmd" not in md
        assert "decision_invariants.mmd" not in md
        # 内嵌的 Mermaid 图表内容应存在
        assert "flowchart TD" in md  # overview + production overview + design overview + invariants
        assert "flowchart LR" in md  # layers

    def test_stats_table_contains_design_production_counts(self, sample_tracks, sample_layers, sample_nodes, sample_edges, sample_invariants):
        """统计表包含设计态/运营态计数行。"""
        md = _gen_index_md(sample_tracks, sample_layers, sample_nodes, sample_edges, sample_invariants)
        # sample_layers: L0/L1/L4=production(3), L2A=design(1)
        assert "运营态 Layer" in md
        assert "设计态 Layer" in md
        assert f"| 运营态 Layer（design_maturity=production） | {3} |" in md
        assert f"| 设计态 Layer（design_maturity=design） | {1} |" in md
        # sample_nodes: node 1/3=production(2), node 2=design(1)
        assert f"| 运营态 Node（design_maturity=production） | {2} |" in md
        assert f"| 设计态 Node（design_maturity=design） | {1} |" in md

    def test_contains_production_overview_section(self, sample_tracks, sample_layers, sample_nodes, sample_edges, sample_invariants):
        """md 包含运营态全景图 section。"""
        md = _gen_index_md(sample_tracks, sample_layers, sample_nodes, sample_edges, sample_invariants)
        assert "运营态全景图" in md
        assert "design_maturity=production" in md

    def test_contains_design_overview_section(self, sample_tracks, sample_layers, sample_nodes, sample_edges, sample_invariants):
        """md 包含设计态全景图 section。"""
        md = _gen_index_md(sample_tracks, sample_layers, sample_nodes, sample_edges, sample_invariants)
        assert "设计态全景图" in md
        assert "design_maturity=design" in md


# ---------- 新字段测试（module_id / source_code_ref / description） ----------

class TestNewFields:
    """新增字段（module_id / source_code_ref / description）展示测试。"""

    def test_truncate_short_text(self):
        """_truncate 对短文本不截断。"""
        assert _truncate("短文本") == "短文本"

    def test_truncate_long_text(self):
        """_truncate 对长文本截断到 max_len 并加省略号。"""
        long_text = "这是一个很长的功能描述文本需要被截断处理"
        result = _truncate(long_text, max_len=10)
        assert len(result) == 10
        assert result.endswith("…")

    def test_truncate_empty(self):
        """_truncate 对空文本返回空字符串。"""
        assert _truncate("") == ""
        assert _truncate(None) == ""

    def test_truncate_strips_newlines(self):
        """_truncate 将换行替换为空格。"""
        result = _truncate("第一行\n第二行", max_len=50)
        assert "\n" not in result

    def test_overview_contains_blueprint_name(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """全景图标签包含蓝图名（module_id 有值时）。"""
        mmd, _, _, _ = _gen_overview_mmd(sample_tracks, sample_layers, sample_nodes, sample_edges)
        # L0 有 module_id=MOD-DATA-001, blueprint_name=数据接入蓝图
        assert "蓝图: 数据接入蓝图" in mmd
        # L4 有 module_id=MOD-RISK-001, blueprint_name=风控蓝图
        assert "蓝图: 风控蓝图" in mmd

    def test_overview_contains_code_ref(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """全景图标签包含代码引用（source_code_ref 有值时）。"""
        mmd, _, _, _ = _gen_overview_mmd(sample_tracks, sample_layers, sample_nodes, sample_edges)
        assert "代码: src/zephyr/data/ingestion.py" in mmd
        assert "代码: src/zephyr/risk/checker.py" in mmd

    def test_overview_contains_description(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """全景图标签包含功能简述（desc 有值时，截断到~20字）。"""
        mmd, _, _, _ = _gen_overview_mmd(sample_tracks, sample_layers, sample_nodes, sample_edges)
        # 使用 _truncate 计算期望值，避免截断导致的断言失败
        assert f"功能: {_truncate('miniQMT+iFind数据接入与预处理')}" in mmd
        assert f"功能: {_truncate('Pre/Post-Trade风控校验')}" in mmd

    def test_overview_no_blueprint_when_empty(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """module_id 为空时不显示蓝图行。"""
        mmd, _, _, _ = _gen_overview_mmd(sample_tracks, sample_layers, sample_nodes, sample_edges)
        # L2A 的 module_id 为空，不应出现"蓝图:"前缀在 L2A 附近
        # 但由于整体 mmd 中其他 layer 有蓝图行，检查 L2A 不含蓝图
        l2a_section = [l for l in mmd.split("\n") if "LL2A" in l]
        assert l2a_section
        for line in l2a_section:
            assert "蓝图:" not in line

    def test_layers_mmd_contains_blueprint_name(self, sample_tracks, sample_layers):
        """层级详情图标签包含蓝图名。"""
        mmd = _gen_layers_mmd(sample_tracks, sample_layers)
        assert "蓝图: 数据接入蓝图" in mmd
        assert "蓝图: 因子计算蓝图" in mmd

    def test_layers_mmd_contains_code_ref(self, sample_tracks, sample_layers):
        """层级详情图标签包含代码引用。"""
        mmd = _gen_layers_mmd(sample_tracks, sample_layers)
        assert "代码: src/zephyr/factor/calc.py" in mmd

    def test_layers_mmd_contains_description(self, sample_tracks, sample_layers):
        """层级详情图标签包含功能简述。"""
        mmd = _gen_layers_mmd(sample_tracks, sample_layers)
        assert "功能: 因子工厂全生命周期管理" in mmd

    def test_index_md_layer_table_has_new_columns(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """Layer 清单表包含新列头。"""
        md = _gen_index_md(sample_tracks, sample_layers, sample_nodes, sample_edges)
        assert "蓝图(module_id)" in md
        assert "蓝图名(派生)" in md
        assert "代码引用" in md
        assert "功能简述" in md

    def test_index_md_layer_table_has_module_id_values(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """Layer 清单表包含 module_id 值。"""
        md = _gen_index_md(sample_tracks, sample_layers, sample_nodes, sample_edges)
        assert "MOD-DATA-001" in md
        assert "MOD-FACTOR-001" in md
        assert "MOD-RISK-001" in md

    def test_index_md_layer_table_has_blueprint_names(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """Layer 清单表包含派生蓝图名。"""
        md = _gen_index_md(sample_tracks, sample_layers, sample_nodes, sample_edges)
        assert "数据接入蓝图" in md
        assert "因子计算蓝图" in md
        assert "风控蓝图" in md

    def test_index_md_layer_table_has_source_code_ref(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """Layer 清单表包含代码引用值。"""
        md = _gen_index_md(sample_tracks, sample_layers, sample_nodes, sample_edges)
        assert "src/zephyr/data/ingestion.py" in md
        assert "src/zephyr/factor/calc.py" in md

    def test_index_md_layer_table_has_description(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """Layer 清单表包含功能简述值。"""
        md = _gen_index_md(sample_tracks, sample_layers, sample_nodes, sample_edges)
        assert "miniQMT+iFind数据接入与预处理" in md
        assert "Pre/Post-Trade风控校验" in md

    def test_index_md_node_table_has_source_code_ref(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """Node 清单表包含代码引用列和值。"""
        md = _gen_index_md(sample_tracks, sample_layers, sample_nodes, sample_edges)
        assert "代码引用" in md
        assert "src/zephyr/data/ingest.py" in md
        assert "src/zephyr/risk/check.py" in md

    def test_index_md_empty_module_id_shows_dash(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """module_id 为空时清单表显示 '-'。"""
        md = _gen_index_md(sample_tracks, sample_layers, sample_nodes, sample_edges)
        # L2A 的 module_id 为空
        assert "| - | - | - |" in md or "| - |" in md

    def test_resolve_blueprint_names_empty_input(self):
        """_resolve_blueprint_names 无 module_id 时返回空 dict。"""
        layers_no_mid = [{"id": "L0", "module_id": None}, {"id": "L1", "module_id": ""}]
        # 使用 mock conn（不会实际查询，因为无 module_id）
        class MockConn:
            def cursor(self):
                class MockCur:
                    def __enter__(self): return self
                    def __exit__(self, *a): pass
                return MockCur()
        result = _resolve_blueprint_names(MockConn(), layers_no_mid)
        assert result == {}
