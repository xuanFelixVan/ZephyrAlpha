# [A_test] module_id: MOD-GOV_generate_decision_diagram | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_SCRIPTS | docs/03_modules/_domain_governance/blueprint.md | §decisiongraph
# [MODULE] tests.governance.test_generate_decision_diagram
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.d5_architecture.generators.generate_decision_diagram
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_generate_decision_diagram.py
# [A_module] module_id=MOD-GOV_SCRIPTS | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #TRAE-061
"""test_generate_decision_diagram.py — generate_decision_diagram.py 单元测试

覆盖：
  - _build_status_color 颜色映射（5 个 build_status + 默认值）
  - _load_invariants 从 YAML 真源读取 5 条承重墙不变量
  - _gen_overview_mmd 返回值类型（tuple[str, int, int, int]）+ 扁平布局（无 subgraph，纯默认主题，无 classDef）
  - _gen_layers_mmd 层级卡片 + 反馈边（L6 → L1/L5）
  - _gen_invariants_mmd 6 节点类型 + 5 不变量 + 非法连接标注
  - _gen_index_md 统计表 + Track/Layer 清单

依据：TRAE-061 任务（2026-07-06）。
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

# 动态加载 scripts/ 下的模块（非 Python 包，需 importlib）
_SCRIPT_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "governance"
    / "d5_architecture"
    / "generators"
    / "generate_decision_diagram.py"
)
_YAML_PATH = Path(__file__).resolve().parents[2] / "architecture_model" / "domain" / "decision_graph_model.yaml"

try:
    _spec = importlib.util.spec_from_file_location("generate_decision_diagram", _SCRIPT_PATH)
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    _build_status_color = _mod.build_status_color
    _load_invariants = _mod.load_invariants
    _gen_overview_mmd = _mod.gen_overview_mmd
    _gen_layers_mmd = _mod.gen_layers_mmd
    _gen_invariants_mmd = _mod.gen_invariants_mmd
    _gen_index_md = _mod.gen_index_md
    _resolve_blueprint_names = _mod.resolve_blueprint_names
    _truncate = _mod.truncate
    # 拆分重构新增函数（per-track / per-domain 文件生成）
    _filter_overview_inputs = _mod.filter_overview_inputs
    _gen_track_file_md = _mod.gen_track_file_md
    _gen_domain_file_md = _mod.gen_domain_file_md
    _gen_layers_file_md = _mod.gen_layers_file_md
    _gen_invariants_file_md = _mod.gen_invariants_file_md
    _track_filename = _mod.track_filename
    _domain_filename = _mod.domain_filename
    _build_domain_index = _mod.build_domain_index
    _node_domain = _mod.node_domain
    _STALE_FILE_REGEX = _mod.STALE_FILE_REGEX
    OUTPUT_DIR = _mod.OUTPUT_DIR
    _YAML_PATH_FROM_MOD = _mod.YAML_PATH
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
        {
            "id": "model_driven",
            "name": "模型驱动轨",
            "name_en": "Model Driven",
            "desc": "正常运行时",
            "priority": 1,
            "activation": "正常运行时",
        },
        {
            "id": "emergency",
            "name": "应急保命轨",
            "name_en": "Emergency",
            "desc": "所有信号失效时",
            "priority": 4,
            "activation": "所有模型/策略/信号失效时",
        },
    ]


@pytest.fixture
def sample_layers():
    """4 个 Layer（L0/L1/L2A/L4），含 module_id + source_code_ref + desc。"""
    return [
        {
            "id": "L0",
            "name": "数据接入与预处理层",
            "name_en": "Data Ingestion",
            "track": "model_driven",
            "desc": "miniQMT+Tushare数据接入与预处理",
            "freq": "tick",
            "maturity": "production",
            "build": "stable",
            "module_id": "MOD-DATA-001",
            "source_code_ref": "src/zephyr/data/ingestion.py",
            "blueprint_name": "数据接入蓝图",
        },
        {
            "id": "L1",
            "name": "因子计算层",
            "name_en": "Factor Computation",
            "track": "model_driven",
            "desc": "因子工厂全生命周期管理",
            "freq": "daily",
            "maturity": "production",
            "build": "stable",
            "module_id": "MOD-FACTOR-001",
            "source_code_ref": "src/zephyr/factor/calc.py",
            "blueprint_name": "因子计算蓝图",
        },
        {
            "id": "L2A",
            "name": "信号层",
            "name_en": "Signal",
            "track": "model_driven",
            "desc": "信号工厂多策略投票",
            "freq": "daily",
            "maturity": "design",
            "build": "planned",
            "module_id": "",
            "source_code_ref": "",
        },
        {
            "id": "L4",
            "name": "风控层",
            "name_en": "Risk Control",
            "track": "model_driven",
            "desc": "Pre/Post-Trade风控校验",
            "freq": "realtime",
            "maturity": "production",
            "build": "stable",
            "module_id": "MOD-RISK-001",
            "source_code_ref": "src/zephyr/risk/checker.py",
            "blueprint_name": "风控蓝图",
        },
    ]


@pytest.fixture
def sample_nodes():
    """3 个 Node（含 design_maturity 区分设计态/运营态 + source_code_ref + name_en 双语）。"""
    return [
        {
            "id": 1,
            "layer_id": "L0",
            "type": "signal",
            "path": "ingest.tick",
            "module_id": "MOD-DATA-001",
            "name": "Tick接入",
            "name_en": "Tick Ingestion",
            "build": "stable",
            "maturity": "production",
            "hash": "abc123",
            "source_code_ref": "src/zephyr/data/ingest.py",
        },
        {
            "id": 2,
            "layer_id": "L2A",
            "type": "signal",
            "path": "signal.momentum",
            "module_id": "MOD-SIG-001",
            "name": "动量信号",
            "name_en": "Momentum Signal",
            "build": "planned",
            "maturity": "design",
            "hash": "def456",
            "source_code_ref": "",
        },
        {
            "id": 3,
            "layer_id": "L4",
            "type": "risk_check",
            "path": "risk.checker",
            "module_id": "MOD-RISK-001",
            "name": "风控检查",
            "name_en": "Risk Check",
            "build": "stable",
            "maturity": "production",
            "hash": "ghi789",
            "source_code_ref": "src/zephyr/risk/check.py",
        },
    ]


@pytest.fixture
def sample_edges():
    """2 条 Edge。"""
    return [
        {"id": 100, "from": 1, "to": 2, "type": "informing", "condition": None, "track": "model_driven"},
        {"id": 101, "from": 2, "to": 3, "type": "triggering", "condition": "signal_active", "track": "model_driven"},
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


@pytest.fixture
def sample_layers_expanded():
    """6 个 Layer（含 L3 策略组合层），覆盖 L2A design + L3 design + L0/L1/L4 production。"""
    return [
        {
            "id": "L0",
            "name": "数据接入层",
            "name_en": "Data",
            "track": "model_driven",
            "desc": "数据接入",
            "freq": "tick",
            "maturity": "production",
            "build": "stable",
            "module_id": "MOD-DATA-001",
            "source_code_ref": "src/zephyr/data.py",
            "blueprint_name": "数据蓝图",
        },
        {
            "id": "L2A",
            "name": "信号层",
            "name_en": "Signal",
            "track": "model_driven",
            "desc": "信号工厂",
            "freq": "daily",
            "maturity": "design",
            "build": "planned",
            "module_id": "",
            "source_code_ref": "",
        },
        {
            "id": "L3",
            "name": "策略组合层",
            "name_en": "Portfolio",
            "track": "model_driven",
            "desc": "组合管理",
            "freq": "daily",
            "maturity": "design",
            "build": "planned",
            "module_id": "",
            "source_code_ref": "",
        },
        {
            "id": "L4",
            "name": "风控层",
            "name_en": "Risk",
            "track": "model_driven",
            "desc": "风控校验",
            "freq": "realtime",
            "maturity": "production",
            "build": "stable",
            "module_id": "MOD-RISK-001",
            "source_code_ref": "src/zephyr/risk.py",
            "blueprint_name": "风控蓝图",
        },
        {
            "id": "L5",
            "name": "学习层",
            "name_en": "Learning",
            "track": "model_driven",
            "desc": "学习闭环",
            "freq": "weekly",
            "maturity": "design",
            "build": "planned",
            "module_id": "",
            "source_code_ref": "",
        },
        {
            "id": "L6",
            "name": "自评估层",
            "name_en": "SelfEval",
            "track": "model_driven",
            "desc": "自评估",
            "freq": "weekly",
            "maturity": "design",
            "build": "planned",
            "module_id": "",
            "source_code_ref": "",
        },
    ]


@pytest.fixture
def sample_nodes_expanded():
    """12 节点跨 3 个 L2A 域（sell/signal/simulation）+ 3 个 L3 域（position/trading/pf_core）。

    path 第 2 段即功能域；用于测试 per-domain 文件生成与跨域边聚合。
    """
    return [
        {
            "id": 101,
            "layer_id": "L2A",
            "type": "sell_decision",
            "path": "decision/sell/sell_01",
            "module_id": "",
            "name": "止盈信号",
            "name_en": "Take-Profit Signal",
            "build": "planned",
            "maturity": "design",
            "hash": "h1",
            "source_code_ref": "",
        },
        {
            "id": 102,
            "layer_id": "L2A",
            "type": "sell_decision",
            "path": "decision/sell/sell_02",
            "module_id": "",
            "name": "止损信号",
            "name_en": "Stop-Loss Signal",
            "build": "planned",
            "maturity": "design",
            "hash": "h2",
            "source_code_ref": "",
        },
        {
            "id": 111,
            "layer_id": "L2A",
            "type": "signal",
            "path": "decision/signal/sg_01",
            "module_id": "",
            "name": "动量信号",
            "name_en": "Momentum Signal",
            "build": "planned",
            "maturity": "design",
            "hash": "h3",
            "source_code_ref": "",
        },
        {
            "id": 112,
            "layer_id": "L2A",
            "type": "signal",
            "path": "decision/signal/sg_02",
            "module_id": "",
            "name": "反转信号",
            "name_en": "Reversal Signal",
            "build": "planned",
            "maturity": "design",
            "hash": "h4",
            "source_code_ref": "",
        },
        {
            "id": 121,
            "layer_id": "L2A",
            "type": "signal",
            "path": "decision/simulation/sim_01",
            "module_id": "",
            "name": "市场仿真",
            "name_en": "Market Simulation",
            "build": "planned",
            "maturity": "design",
            "hash": "h5",
            "source_code_ref": "",
        },
        {
            "id": 201,
            "layer_id": "L3",
            "type": "portfolio_target",
            "path": "decision/position/pos_01",
            "module_id": "",
            "name": "仓位裁决",
            "name_en": "Position Decision",
            "build": "planned",
            "maturity": "design",
            "hash": "h6",
            "source_code_ref": "",
        },
        {
            "id": 202,
            "layer_id": "L3",
            "type": "portfolio_target",
            "path": "decision/position/pos_02",
            "module_id": "",
            "name": "仓位调整",
            "name_en": "Position Adjust",
            "build": "planned",
            "maturity": "design",
            "hash": "h7",
            "source_code_ref": "",
        },
        {
            "id": 203,
            "layer_id": "L3",
            "type": "portfolio_target",
            "path": "decision/position/pos_03",
            "module_id": "",
            "name": "仓位清零",
            "name_en": "Position Flatten",
            "build": "planned",
            "maturity": "design",
            "hash": "h8",
            "source_code_ref": "",
        },
        {
            "id": 211,
            "layer_id": "L3",
            "type": "portfolio_target",
            "path": "decision/trading/tr_01",
            "module_id": "",
            "name": "交易决策",
            "name_en": "Trade Decision",
            "build": "planned",
            "maturity": "design",
            "hash": "h9",
            "source_code_ref": "",
        },
        {
            "id": 212,
            "layer_id": "L3",
            "type": "portfolio_target",
            "path": "decision/trading/tr_02",
            "module_id": "",
            "name": "交易执行",
            "name_en": "Trade Execution",
            "build": "planned",
            "maturity": "design",
            "hash": "h10",
            "source_code_ref": "",
        },
        {
            "id": 221,
            "layer_id": "L3",
            "type": "portfolio_target",
            "path": "decision/pf_core/pc_01",
            "module_id": "",
            "name": "组合核心",
            "name_en": "Portfolio Core",
            "build": "planned",
            "maturity": "design",
            "hash": "h11",
            "source_code_ref": "",
        },
        {
            "id": 222,
            "layer_id": "L3",
            "type": "portfolio_target",
            "path": "decision/pf_core/pc_02",
            "module_id": "",
            "name": "组合优化",
            "name_en": "Portfolio Optimize",
            "build": "planned",
            "maturity": "design",
            "hash": "h12",
            "source_code_ref": "",
        },
    ]


@pytest.fixture
def sample_edges_expanded():
    """8 边：5 域内 + 2 跨域（L2A→L3）+ 1 跨轨（to=999 不存在，被过滤）。"""
    return [
        {"id": 1001, "from": 101, "to": 102, "type": "informing", "condition": None, "track": "model_driven"},
        {"id": 1002, "from": 111, "to": 112, "type": "informing", "condition": None, "track": "model_driven"},
        {"id": 1003, "from": 201, "to": 202, "type": "triggering", "condition": "pos_change", "track": "model_driven"},
        {"id": 1004, "from": 202, "to": 203, "type": "triggering", "condition": "flatten", "track": "model_driven"},
        {"id": 1005, "from": 211, "to": 212, "type": "triggering", "condition": None, "track": "model_driven"},
        {"id": 1006, "from": 102, "to": 201, "type": "informing", "condition": "sell_signal", "track": "model_driven"},
        {"id": 1007, "from": 112, "to": 211, "type": "informing", "condition": "sig_active", "track": "model_driven"},
        {"id": 1008, "from": 201, "to": 999, "type": "approving", "condition": "risk_veto", "track": "model_driven"},
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
        assert callable(_mod.fetch_decision_data)


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
        """计数反映过滤后输入（emergency 无 layer → 被过滤，只留 model_driven）。"""
        mmd, t_count, l_count, e_count = _gen_overview_mmd(sample_tracks, sample_layers, sample_nodes, sample_edges)
        assert t_count == 1  # emergency 无 layer → 被 _filter_overview_inputs 过滤
        assert l_count == 4  # 4 layers
        assert e_count == 2  # 2 edges

    def test_starts_with_flowchart_td(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """mmd 以 flowchart TD 开头。"""
        mmd, _, _, _ = _gen_overview_mmd(sample_tracks, sample_layers, sample_nodes, sample_edges)
        assert "flowchart TD" in mmd

    def test_no_subgraphs(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """mmd 不含 subgraph（扁平布局，与 _gen_layers_mmd/_gen_invariants_mmd 一致）。

        用户实测确认（2026-07-30）：subgraph 内节点使用 secondaryColor 而非
        primaryColor，导致 %%{init}%% 设的 primaryColor 不生效（节点白色）；
        subgraph 容器背景 VS Code 渲染器不识别主题变量，回退白色且增加高度。
        """
        mmd, _, _, _ = _gen_overview_mmd(sample_tracks, sample_layers, sample_nodes, sample_edges)
        assert "subgraph" not in mmd

    def test_contains_layer_nodes(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """mmd 包含 layer 节点（L0/L1/L2A/L4）。"""
        mmd, _, _, _ = _gen_overview_mmd(sample_tracks, sample_layers, sample_nodes, sample_edges)
        assert "LL0" in mmd
        assert "LL1" in mmd
        assert "LL2A" in mmd
        assert "LL4" in mmd

    def test_has_class_defs(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """mmd 含四类 classDef（模板 V1.2 §4.7 铁律：production/design/external_prod/external_design）。"""
        mmd, _, _, _ = _gen_overview_mmd(sample_tracks, sample_layers, sample_nodes, sample_edges)
        assert "classDef production" in mmd
        assert "classDef design" in mmd
        assert "classDef external_prod" in mmd
        assert "classDef external_design" in mmd
        # 用 `class X production` 语法绑类，不用内联 `:::` 标记
        assert ":::" not in mmd

    def test_empty_input(self):
        """空输入返回空图 + 零计数。"""
        mmd, t_count, l_count, e_count = _gen_overview_mmd([], [], [], [])
        assert t_count == 0
        assert l_count == 0
        assert e_count == 0
        assert "flowchart TD" in mmd

    def test_maturity_in_labels(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """全景图节点标签包含 maturity/build 文字标注（精简后无方括号）。"""
        mmd, _, _, _ = _gen_overview_mmd(sample_tracks, sample_layers, sample_nodes, sample_edges)
        # sample_layers 中 L0/L1/L4=production, L2A=design
        assert "production" in mmd
        assert "design" in mmd

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
            {
                "id": "L0",
                "name": "测试",
                "name_en": "Test",
                "track": "model_driven",
                "desc": "",
                "freq": "daily",
                "maturity": "design",
                "build": "planned",
            },
        ]
        mmd, _, l_count, _ = _gen_overview_mmd(sample_tracks, design_only_layers, [], [], production_only=True)
        assert l_count == 0
        assert "flowchart TD" in mmd

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
            {
                "id": "L0",
                "name": "测试",
                "name_en": "Test",
                "track": "model_driven",
                "desc": "",
                "freq": "daily",
                "maturity": "production",
                "build": "stable",
            },
        ]
        mmd, _, l_count, _ = _gen_overview_mmd(sample_tracks, prod_only_layers, [], [], design_only=True)
        assert l_count == 0
        assert "flowchart TD" in mmd


# ---------- _maturity_tag 测试 ----------


class TestMaturityTag:
    """design_maturity → 标注标签映射。"""

    def test_production(self):
        assert _mod.maturity_tag("production") == "[production]"

    def test_design(self):
        assert _mod.maturity_tag("design") == "[design]"

    def test_unknown_value_passthrough(self):
        """ARCH-MM-002: prototype 已删除，_maturity_tag 对未知值透传（无特殊处理）。"""
        assert _mod.maturity_tag("prototype") == "[prototype]"

    def test_none_returns_empty(self):
        assert _mod.maturity_tag(None) == ""

    def test_empty_returns_empty(self):
        assert _mod.maturity_tag("") == ""


# ---------- _gen_layers_mmd 测试 ----------


class TestGenLayersMmd:
    """层级详情图生成测试。"""

    def test_returns_str(self, sample_tracks, sample_layers):
        """返回字符串。"""
        mmd = _gen_layers_mmd(sample_tracks, sample_layers)
        assert isinstance(mmd, str)

    def test_starts_with_flowchart_lr(self, sample_tracks, sample_layers):
        """mmd 以 flowchart TD 开头。"""
        mmd = _gen_layers_mmd(sample_tracks, sample_layers)
        assert "flowchart TD" in mmd

    def test_contains_layer_cards(self, sample_tracks, sample_layers):
        """mmd 包含每个 layer 的卡片。"""
        mmd = _gen_layers_mmd(sample_tracks, sample_layers)
        assert "LL0" in mmd
        assert "LL1" in mmd
        assert "LL2A" in mmd
        assert "LL4" in mmd

    def test_contains_triggering_edges(self, sample_tracks, sample_layers):
        """mmd 包含层间 triggering 边标签（中英文格式）。"""
        mmd = _gen_layers_mmd(sample_tracks, sample_layers)
        assert "|triggering / 触发|" in mmd

    def test_has_class_defs(self, sample_tracks, sample_layers):
        """mmd 含四类 classDef（模板 V1.2 §4.7 铁律）。"""
        mmd = _gen_layers_mmd(sample_tracks, sample_layers)
        assert "classDef production" in mmd
        assert "classDef design" in mmd
        assert "classDef external_prod" in mmd
        assert "classDef external_design" in mmd
        assert ":::" not in mmd

    def test_empty_input(self):
        """空输入返回空图。"""
        mmd = _gen_layers_mmd([], [])
        assert "flowchart TD" in mmd


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
        assert "flowchart TD" in mmd

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

    def test_has_class_defs(self, sample_invariants):
        """mmd 含四类 classDef（模板 V1.2 §4.7 铁律；节点类型/不变量统一 class design）。"""
        mmd = _gen_invariants_mmd(sample_invariants)
        assert "classDef production" in mmd
        assert "classDef design" in mmd
        assert "classDef external_prod" in mmd
        assert "classDef external_design" in mmd
        # 节点类型/不变量均为设计态概念 → class design 应用行存在
        assert "class " in mmd
        assert ":::" not in mmd

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

    def test_contains_track_nav_table_with_links(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """主索引含 Track 导航表，每行带文件链接。"""
        md = _gen_index_md(sample_tracks, sample_layers, sample_nodes, sample_edges)
        assert "model_driven" in md
        assert "应急保命轨" in md
        # 链接格式：[📄 01_decision_track_model_driven.md](01_decision_track_model_driven.md)
        assert "[📄 01_decision_track_model_driven.md](01_decision_track_model_driven.md)" in md
        assert "[📄 04_decision_track_emergency.md](04_decision_track_emergency.md)" in md

    def test_stats_table_contains_design_production_counts(
        self, sample_tracks, sample_layers, sample_nodes, sample_edges, sample_invariants
    ):
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

    def test_track_file_contains_blueprint_name(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """Track 文件 Layer 清单表含蓝图名（精简后字段从 mermaid label 移到表格）。"""
        _di = _build_domain_index(sample_tracks, sample_layers, sample_nodes)
        md = _gen_track_file_md(sample_tracks[0], sample_tracks, sample_layers, sample_nodes, sample_edges, _di)
        # L0 blueprint_name=数据接入蓝图, L4=风控蓝图（Layer 清单表"蓝图名(派生)"列）
        assert "数据接入蓝图" in md
        assert "风控蓝图" in md

    def test_track_file_contains_code_ref(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """Track 文件 Layer 清单表含代码引用。"""
        _di = _build_domain_index(sample_tracks, sample_layers, sample_nodes)
        md = _gen_track_file_md(sample_tracks[0], sample_tracks, sample_layers, sample_nodes, sample_edges, _di)
        assert "src/zephyr/data/ingestion.py" in md
        assert "src/zephyr/risk/checker.py" in md

    def test_track_file_contains_description(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """Track 文件 Layer 清单表含功能简述。"""
        _di = _build_domain_index(sample_tracks, sample_layers, sample_nodes)
        md = _gen_track_file_md(sample_tracks[0], sample_tracks, sample_layers, sample_nodes, sample_edges, _di)
        assert "miniQMT+Tushare数据接入与预处理" in md
        assert "Pre/Post-Trade风控校验" in md

    def test_overview_no_blueprint_when_empty(self, sample_tracks, sample_layers, sample_nodes, sample_edges):
        """module_id 为空时不显示蓝图行。"""
        mmd, _, _, _ = _gen_overview_mmd(sample_tracks, sample_layers, sample_nodes, sample_edges)
        # L2A 的 module_id 为空，不应出现"蓝图:"前缀在 L2A 附近
        # 但由于整体 mmd 中其他 layer 有蓝图行，检查 L2A 不含蓝图
        l2a_section = [l for l in mmd.split("\n") if "LL2A" in l]
        assert l2a_section
        for line in l2a_section:
            assert "蓝图:" not in line

    def test_resolve_blueprint_names_empty_input(self):
        """_resolve_blueprint_names 无 module_id 时返回空 dict。"""
        layers_no_mid = [{"id": "L0", "module_id": None}, {"id": "L1", "module_id": ""}]

        # 使用 mock conn（不会实际查询，因为无 module_id）
        class MockConn:
            def cursor(self):
                class MockCur:
                    def __enter__(self):
                        return self

                    def __exit__(self, *a):
                        pass

                return MockCur()

        result = _resolve_blueprint_names(MockConn(), layers_no_mid)
        assert result == {}


# ---------- _filter_overview_inputs 测试（拆分重构新增） ----------


class TestFilterOverviewInputs:
    """全景图输入过滤辅助测试。

    过滤顺序：maturity → track_id → path_prefix（path 第 2 段精确匹配）→ 边端点 → 空 track。
    sample_layers_expanded: L0/L4=production, L2A/L3/L5/L6=design, 全属 model_driven。
    sample_nodes_expanded: 12 节点全 design，L2A(sell/signal/simulation) + L3(position/trading/pf_core)。
    sample_edges_expanded: 8 边，其中 edge 1008 (201→999) 的 to=999 不在节点集，必被过滤。
    """

    def test_no_filter_returns_all_minus_orphans(
        self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded
    ):
        """无过滤时：layers/nodes 原样，edges 丢掉端点不在节点集的，tracks 丢掉无 layer 的（emergency）。"""
        t, l, n, e = _filter_overview_inputs(
            sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded
        )
        assert len(t) == 1  # emergency 无 layer → 被丢
        assert len(l) == 6
        assert len(n) == 12
        assert len(e) == 7  # edge 1008 (to=999) 被丢

    def test_production_only(self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded):
        """maturity='production'：只留 maturity=production 的 layer/node。expanded 节点全 design → 0 节点。"""
        t, l, n, e = _filter_overview_inputs(
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
            maturity="production",
        )
        assert len(t) == 1  # L0/L4 属 model_driven
        assert len(l) == 2  # L0, L4
        assert len(n) == 0  # expanded 节点全 design
        assert len(e) == 0

    def test_design_only(self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded):
        """maturity='design'：只留 maturity=design。4 layer + 12 节点。"""
        t, l, n, e = _filter_overview_inputs(
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
            maturity="design",
        )
        assert len(t) == 1
        assert len(l) == 4  # L2A, L3, L5, L6
        assert len(n) == 12
        assert len(e) == 7

    def test_track_id_filter_model_driven(
        self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded
    ):
        """track_id=model_driven：留全部（expanded 全属 model_driven）。"""
        t, l, n, e = _filter_overview_inputs(
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
            track_id="model_driven",
        )
        assert len(t) == 1
        assert len(l) == 6
        assert len(n) == 12
        assert len(e) == 7

    def test_track_id_filter_emergency_empty(
        self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded
    ):
        """track_id=emergency：expanded 无 emergency layer → 全空。"""
        t, l, n, e = _filter_overview_inputs(
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
            track_id="emergency",
        )
        assert len(t) == 0
        assert len(l) == 0
        assert len(n) == 0
        assert len(e) == 0

    def test_path_prefix_exact_match_sell(
        self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded
    ):
        """path_prefix=sell：精确匹配 path 第 2 段，留 2 节点 + 1 边。"""
        t, l, n, e = _filter_overview_inputs(
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
            path_prefix="sell",
        )
        assert len(t) == 1  # layers 未受 path_prefix 影响
        assert len(l) == 6
        assert len(n) == 2  # 101, 102
        assert len(e) == 1  # 1001 (101→102)

    def test_path_prefix_rejects_partial_match(
        self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded
    ):
        """path_prefix=sel：精确匹配，不 startswith → 0 节点。"""
        t, l, n, e = _filter_overview_inputs(
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
            path_prefix="sel",
        )
        assert len(n) == 0
        assert len(e) == 0
        assert len(t) == 1  # layers 仍全在 → model_driven 保留

    def test_combination_design_track_path(
        self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded
    ):
        """maturity='design' + track_id=model_driven + path_prefix=sell → 2 节点 + 1 边。"""
        t, l, n, e = _filter_overview_inputs(
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
            maturity="design",
            track_id="model_driven",
            path_prefix="sell",
        )
        assert len(t) == 1
        assert len(l) == 4  # design layers
        assert len(n) == 2  # sell 域
        assert len(e) == 1


# ---------- _gen_track_file_md 测试 ----------


class TestGenTrackFileMd:
    """Per-Track 文件生成测试。"""

    def test_returns_str(self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded):
        """返回字符串。"""
        di = _build_domain_index(sample_tracks, sample_layers_expanded, sample_nodes_expanded)
        md = _gen_track_file_md(
            sample_tracks[0],
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
            di,
        )
        assert isinstance(md, str)

    def test_contains_three_mermaid_blocks(
        self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded
    ):
        """三视图模式：model_driven 轨 3 个 Layer 骨架 mermaid（全景/运营态/设计态）。

        治本（2026-08-01 模板升级）：单骨架图 → 严格三视图（§3.2 铁律）。
        sample_layers_expanded: L0/L4=production, L2A/L3/L5/L6=design → 三视图均非空。
        """
        di = _build_domain_index(sample_tracks, sample_layers_expanded, sample_nodes_expanded)
        md = _gen_track_file_md(
            sample_tracks[0],
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
            di,
        )
        assert md.count("```mermaid") == 3

    def test_contains_layer_table(
        self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded
    ):
        """含 Layer 清单 section。"""
        di = _build_domain_index(sample_tracks, sample_layers_expanded, sample_nodes_expanded)
        md = _gen_track_file_md(
            sample_tracks[0],
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
            di,
        )
        assert "## Layer 清单" in md

    def test_no_node_table(self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded):
        """概览模式不含 Node 清单（决策节点详情在功能域文件）。"""
        di = _build_domain_index(sample_tracks, sample_layers_expanded, sample_nodes_expanded)
        md = _gen_track_file_md(
            sample_tracks[0],
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
            di,
        )
        assert "## Node 清单" not in md

    def test_no_edge_table(self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded):
        """概览模式不含本轨 Edge 清单（决策边详情在功能域文件）。"""
        di = _build_domain_index(sample_tracks, sample_layers_expanded, sample_nodes_expanded)
        md = _gen_track_file_md(
            sample_tracks[0],
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
            di,
        )
        assert "## Edge 清单（本轨内）" not in md

    def test_contains_domain_links(
        self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded
    ):
        """含功能域文件链接表，含 sell 域文件链接。"""
        di = _build_domain_index(sample_tracks, sample_layers_expanded, sample_nodes_expanded)
        md = _gen_track_file_md(
            sample_tracks[0],
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
            di,
        )
        assert "## 功能域文件" in md
        assert "[📄 10_decision_l2a_sell.md](10_decision_l2a_sell.md)" in md

    def test_empty_track_shows_hint(
        self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded
    ):
        """emergency 轨（expanded 无节点）→ 0 mermaid（无决策节点不画骨架图）+ 无功能域文件提示。"""
        di = _build_domain_index(sample_tracks, sample_layers_expanded, sample_nodes_expanded)
        md = _gen_track_file_md(
            sample_tracks[1],
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
            di,
        )
        assert md.count("```mermaid") == 0  # 无决策节点，不画骨架图
        assert "本轨无决策节点" in md
        assert "（本轨无功能域文件" in md  # emergency 无功能域文件


# ---------- _gen_domain_file_md 测试 ----------


class TestGenDomainFileMd:
    """Per-domain 文件生成测试。"""

    def test_returns_str(self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded):
        """返回字符串。"""
        md = _gen_domain_file_md(
            sample_tracks[0],
            "L2A",
            "sell",
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
        )
        assert isinstance(md, str)

    def test_sell_has_three_mermaid_blocks(
        self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded
    ):
        """sell 域三视图 + 跨域依赖图 → 3 mermaid。

        治本（2026-08-01 模板升级）：全景图(1) + 运营态(占位无 mermaid, sell 全 design) +
        设计态(1) + 跨域依赖图(1, sell→position) = 3。
        """
        md = _gen_domain_file_md(
            sample_tracks[0],
            "L2A",
            "sell",
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
        )
        assert md.count("```mermaid") == 3

    def test_contains_node_table_with_sell_paths(
        self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded
    ):
        """Node 清单含 sell 域节点 path。"""
        md = _gen_domain_file_md(
            sample_tracks[0],
            "L2A",
            "sell",
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
        )
        assert "## Node 清单" in md
        assert "decision/sell/sell_01" in md

    def test_contains_outgoing_cross_domain_edges(
        self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded
    ):
        """跨域出边表含 sell→position 边。"""
        md = _gen_domain_file_md(
            sample_tracks[0],
            "L2A",
            "sell",
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
        )
        assert "## 跨域出边（Depends On）" in md
        assert "decision/position/pos_01" in md  # edge 1006 (102→201)

    def test_isolated_domain_has_two_mermaid(
        self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded
    ):
        """simulation 域无跨域边 → 2 mermaid（全景图 + 设计态图；运营态占位无 mermaid）。

        治本（2026-08-01 模板升级）：三视图中运营态无 production 节点 → 占位说明（不输出
        mermaid）；无跨域依赖 → 不输出跨域 mermaid。故全景(1) + 设计态(1) = 2。
        """
        md = _gen_domain_file_md(
            sample_tracks[0],
            "L2A",
            "simulation",
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
        )
        assert md.count("```mermaid") == 2
        assert "（无跨域依赖）" in md


# ---------- _gen_index_md 导航测试（拆分重构后主索引纯导航） ----------


class TestGenIndexMdNavigation:
    """主索引纯导航测试：0 mermaid + Track/L2A/L3 导航表 + 辅助图链接 + 旧锚点重定向。"""

    def test_zero_mermaid_blocks(
        self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded
    ):
        """主索引 0 个 mermaid 块（纯导航）。"""
        di = _build_domain_index(sample_tracks, sample_layers_expanded, sample_nodes_expanded)
        md = _gen_index_md(
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
            [],
            di,
        )
        assert md.count("```mermaid") == 0

    def test_contains_track_nav_with_links(
        self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded
    ):
        """含 Track 导航表 + 文件链接。"""
        di = _build_domain_index(sample_tracks, sample_layers_expanded, sample_nodes_expanded)
        md = _gen_index_md(
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
            [],
            di,
        )
        assert "## Track 导航" in md
        assert "[📄 01_decision_track_model_driven.md](01_decision_track_model_driven.md)" in md

    def test_contains_l2a_nav_with_links(
        self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded
    ):
        """含 L2A 域导航表 + sell 域文件链接。"""
        di = _build_domain_index(sample_tracks, sample_layers_expanded, sample_nodes_expanded)
        md = _gen_index_md(
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
            [],
            di,
        )
        assert "## L2A 信号层 · 功能域导航" in md
        assert "[📄 10_decision_l2a_sell.md](10_decision_l2a_sell.md)" in md

    def test_contains_l3_nav_with_links(
        self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded
    ):
        """含 L3 域导航表 + position 域文件链接。"""
        di = _build_domain_index(sample_tracks, sample_layers_expanded, sample_nodes_expanded)
        md = _gen_index_md(
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
            [],
            di,
        )
        assert "## L3 策略组合层 · 功能域导航" in md
        assert "[📄 18_decision_l3_position.md](18_decision_l3_position.md)" in md

    def test_contains_aux_file_links(
        self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded
    ):
        """含辅助图文件链接。"""
        di = _build_domain_index(sample_tracks, sample_layers_expanded, sample_nodes_expanded)
        md = _gen_index_md(
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
            [],
            di,
        )
        assert "20_decision_layers.md" in md
        assert "21_decision_invariants.md" in md

    def test_contains_redirect_section(
        self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded
    ):
        """含旧锚点重定向 section（兼容外部 wiki 链接）。"""
        di = _build_domain_index(sample_tracks, sample_layers_expanded, sample_nodes_expanded)
        md = _gen_index_md(
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
            [],
            di,
        )
        assert "## 旧锚点重定向" in md


# ---------- _gen_layers_file_md / _gen_invariants_file_md 测试 ----------


class TestGenLayersFileMd:
    """层级详情图独立文件测试。"""

    def test_returns_str(self, sample_tracks, sample_layers_expanded):
        """返回字符串。"""
        md = _gen_layers_file_md(sample_tracks, sample_layers_expanded)
        assert isinstance(md, str)

    def test_one_mermaid_block(self, sample_tracks, sample_layers_expanded):
        """含 1 个 mermaid 块。"""
        md = _gen_layers_file_md(sample_tracks, sample_layers_expanded)
        assert md.count("```mermaid") == 1

    def test_contains_flowchart_lr(self, sample_tracks, sample_layers_expanded):
        """mermaid 使用 flowchart TD。"""
        md = _gen_layers_file_md(sample_tracks, sample_layers_expanded)
        assert "flowchart TD" in md

    def test_has_frontmatter(self, sample_tracks, sample_layers_expanded):
        """含 frontmatter（doc_type: architecture_view）。§3.1。"""
        md = _gen_layers_file_md(sample_tracks, sample_layers_expanded)
        assert md.startswith("---")
        assert "doc_type: architecture_view" in md

    def test_has_html_link(self, sample_tracks, sample_layers_expanded):
        """含 HTML 跳转链接（http://localhost:8765/...）。§14。"""
        md = _gen_layers_file_md(sample_tracks, sample_layers_expanded)
        assert "http://localhost:8765/" in md
        assert "可缩放 HTML 版" in md

    def test_has_legend(self, sample_tracks, sample_layers_expanded):
        """含图例说明（蓝/橙/实线/虚线四种）。§3.1。"""
        md = _gen_layers_file_md(sample_tracks, sample_layers_expanded)
        assert "图例说明" in md
        assert "蓝色 = 运营态" in md
        assert "橙色虚线 = 设计态" in md


class TestGenInvariantsFileMd:
    """不变量图独立文件测试。"""

    def test_returns_str(self, sample_invariants):
        """返回字符串。"""
        md = _gen_invariants_file_md(sample_invariants)
        assert isinstance(md, str)

    def test_one_mermaid_block(self, sample_invariants):
        """含 1 个 mermaid 块。"""
        md = _gen_invariants_file_md(sample_invariants)
        assert md.count("```mermaid") == 1

    def test_has_frontmatter(self, sample_invariants):
        """含 frontmatter（doc_type: architecture_view）。§3.1。"""
        md = _gen_invariants_file_md(sample_invariants)
        assert md.startswith("---")
        assert "doc_type: architecture_view" in md

    def test_has_html_link(self, sample_invariants):
        """含 HTML 跳转链接。§14。"""
        md = _gen_invariants_file_md(sample_invariants)
        assert "http://localhost:8765/" in md

    def test_has_legend(self, sample_invariants):
        """含图例说明。§3.1。"""
        md = _gen_invariants_file_md(sample_invariants)
        assert "图例说明" in md


# ---------- 模板 V1.3 合规测试（四要素/三视图/frontmatter/HTML链接/图例/plain_zh 真源/不截断） ----------


class TestTemplateV13Compliance:
    """可视化模板 V1.3 合规测试。

    覆盖 §9.1 强制规则：MD+HTML 双产物、frontmatter、HTML 链接、灰色主题头、四要素、
    预折行、classDef 四色、箭头规范、三视图铁律、图例说明。

    V1.3 治本增量（§4.11）：③大白话真源=decision_nodes.facets.plain_zh，禁止
    ``{type_zh}·{name_zh}`` 模板话占位；§4.10 Layer desc 不截断；§4.3 双语名去重。
    """

    def test_node_label_4el_has_four_elements(self):
        """_node_label_4el 输出含 ①成熟度 ②双语名 ③大白话 ④文件路径。§4.3。

        V1.3：③大白话取 facets.plain_zh；无 facets 时诚实占位（非 {type_zh}·{name_zh}）。
        """
        n = {
            "maturity": "design",
            "name": "止盈信号",
            "name_en": "Take-Profit Signal",
            "type": "sell_decision",
            "path": "decision/sell/sell_01",
            "facets": {"plain_zh": "持仓达到盈利目标时卖出锁定收益"},
        }
        label = _mod.node_label_4el(n)
        # ① 成熟度
        assert "设计" in label and "design" in label
        # ② 双语名（_split_zh_en 从合并名剥离英文 → 纯中文 / 纯英文）
        assert "止盈信号" in label
        assert "Take-Profit Signal" in label
        # ③ 大白话 = facets.plain_zh 真源（V1.3 §4.11，禁止 {type_zh}·{name_zh} 占位）
        assert "持仓达到盈利目标时卖出锁定收益" in label
        assert "·" not in label  # 不再使用 type_zh·name_zh 占位
        # ④ 文件路径
        assert "文件:" in label
        assert "decision/sell/sell_01" in label

    def test_node_label_4el_pending_placeholder_when_no_facets(self):
        """无 facets.plain_zh 时显示诚实占位，不用 {type_zh}·{name_zh} 模板话。§4.11。"""
        n = {
            "maturity": "design",
            "name": "某节点",
            "name_en": "Some Node",
            "type": "signal",
            "path": "decision/x/y",
        }  # 无 facets 键
        label = _mod.node_label_4el(n)
        assert "大白话待补" in label
        assert "plain_zh pending" in label
        # 禁止回退到 type_zh·name_zh 占位
        assert "·" not in label

    def test_node_label_4el_pending_placeholder_when_facets_empty(self):
        """facets 为空 dict 时也显示诚实占位（非崩溃、非模板话）。§4.11。"""
        n = {
            "maturity": "design",
            "name": "某节点",
            "name_en": "Some Node",
            "type": "signal",
            "path": "p",
            "facets": {},
        }
        label = _mod.node_label_4el(n)
        assert "大白话待补" in label

    def test_split_zh_en_dedup_when_name_equals_name_en(self):
        """name == name_en 时仅返回单名，避免标签显示"同名 / 同名"重复。§4.3 V1.3。"""
        zh, en = _mod.split_zh_en("Synthesizer 信号合成+权重分配", "Synthesizer 信号合成+权重分配")
        assert en == ""  # 英文不重复输出
        assert zh == "Synthesizer 信号合成+权重分配"

    def test_split_zh_en_normal_still_strips_english_suffix(self):
        """name='止盈信号 Take-Profit Signal' + name_en='Take-Profit Signal' → 剥离英文。"""
        zh, en = _mod.split_zh_en("止盈信号 Take-Profit Signal", "Take-Profit Signal")
        assert zh == "止盈信号"
        assert en == "Take-Profit Signal"

    def test_layer_label_4el_no_truncation(self):
        """_layer_label_4el 不截断 desc（V1.3 §4.10 治本：预折行已处理长度）。"""
        long_desc = "这是一个非常非常长的层级描述用于测试不再截断的治本修复是否生效" * 3
        l = {
            "id": "L2A",
            "name": "信号层",
            "name_en": "Signal",
            "maturity": "design",
            "desc": long_desc,
            "module_id": "MOD-SIG-001",
            "source_code_ref": "",
        }
        label = _mod.layer_label_4el(l)
        # 不应有省略号（_truncate 会加 …，V1.3 已移除）
        assert "…" not in label
        # 完整 desc 内容应存在（去掉 <br/> 后比对）
        label_no_br = label.replace("<br/>", "")
        assert long_desc in label_no_br

    def test_node_label_4el_wraps_long_text(self):
        """_node_label_4el 对长文本预折行（<br/> 显式断行，§4.10 铁律）。"""
        n = {
            "maturity": "production",
            "name": "这是一个非常非常长的决策节点名称用于测试预折行功能是否正常工作",
            "name_en": "Very Long Decision Node Name For Testing Text Wrapping",
            "type": "signal",
            "path": "decision/signal/long_name_node_path_here",
        }
        label = _mod.node_label_4el(n)
        # 预折行后应含 <br/> 断行（长文本不可能一行装下）
        assert "<br/>" in label

    def test_node_label_4el_sanitizes_special_chars(self):
        """_node_label_4el 转义 [ ] " | 特殊字符。§4.9。"""
        n = {
            "maturity": "design",
            "name": '含[方括号]"引号"|管道',
            "name_en": "bracket",
            "type": "signal",
            "path": "p/q",
        }
        label = _mod.node_label_4el(n)
        assert "[" not in label
        assert "]" not in label
        assert '"' not in label
        assert "|" not in label

    def test_layer_label_4el_has_four_elements(self):
        """_layer_label_4el 输出含 ①成熟度 ②双语名(含层ID) ③大白话 ④文件。§4.3。"""
        l = {
            "id": "L2A",
            "name": "信号层",
            "name_en": "Signal",
            "maturity": "design",
            "desc": "信号工厂多策略投票",
            "module_id": "MOD-SIG-001",
            "source_code_ref": "",
        }
        label = _mod.layer_label_4el(l)
        assert "L2A" in label
        assert "信号层" in label
        assert "Signal" in label
        assert "信号工厂多策略投票" in label
        assert "文件:" in label

    def test_cross_domain_label_has_four_elements(self):
        """_cross_domain_label 输出含 ①成熟度(design) ②双语名 ③域职责 ④跨域标识。§4.3 跨域外部节点。"""
        label = _mod.cross_domain_label("sell", "卖出", "卖出决策域")
        assert "设计" in label and "design" in label
        assert "卖出" in label and "sell" in label
        assert "卖出决策域" in label
        assert "跨域节点 / cross-domain" in label

    def test_cross_domain_mermaid_uses_td_and_classdef(self):
        """跨域依赖图用 flowchart TD + classDef（§4.2/§4.7）。"""
        mmd = _mod.gen_cross_domain_mermaid(
            "sell",
            [{"other_domain": "position", "count": 2, "types": ["informing"]}],
            [],
        )
        assert "flowchart TD" in mmd
        assert "classDef production" in mmd
        assert "classDef design" in mmd
        assert "classDef external_design" in mmd
        # SELF 标 design，EXT 标 external_design
        assert "class SELF design" in mmd
        assert "external_design" in mmd

    def test_track_file_has_frontmatter(
        self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded
    ):
        """Track 文件含 frontmatter。§3.1。"""
        di = _build_domain_index(sample_tracks, sample_layers_expanded, sample_nodes_expanded)
        md = _gen_track_file_md(
            sample_tracks[0],
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
            di,
        )
        assert md.startswith("---")
        assert "doc_type: architecture_view" in md

    def test_track_file_has_html_link(
        self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded
    ):
        """Track 文件（有决策节点）含 HTML 跳转链接。§14。"""
        di = _build_domain_index(sample_tracks, sample_layers_expanded, sample_nodes_expanded)
        md = _gen_track_file_md(
            sample_tracks[0],
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
            di,
        )
        assert "http://localhost:8765/" in md

    def test_track_file_has_legend_and_three_views(
        self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded
    ):
        """Track 文件含图例 + 三视图小标题（§3.1/§3.2 铁律）。"""
        di = _build_domain_index(sample_tracks, sample_layers_expanded, sample_nodes_expanded)
        md = _gen_track_file_md(
            sample_tracks[0],
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
            di,
        )
        assert "图例说明" in md
        assert "### 全景图" in md
        assert "### 运营态的图" in md
        assert "### 设计态的图" in md

    def test_empty_track_no_html_link(
        self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded
    ):
        """空 track（0 决策节点）不输出 HTML 链接（指向的 HTML 不会生成）。"""
        di = _build_domain_index(sample_tracks, sample_layers_expanded, sample_nodes_expanded)
        md = _gen_track_file_md(
            sample_tracks[1],
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
            di,
        )
        assert "http://localhost:8765/" not in md

    def test_domain_file_has_frontmatter(
        self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded
    ):
        """Domain 文件含 frontmatter。§3.1。"""
        md = _gen_domain_file_md(
            sample_tracks[0],
            "L2A",
            "sell",
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
        )
        assert md.startswith("---")
        assert "doc_type: architecture_view" in md

    def test_domain_file_has_html_link(
        self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded
    ):
        """Domain 文件含 HTML 跳转链接。§14。"""
        md = _gen_domain_file_md(
            sample_tracks[0],
            "L2A",
            "sell",
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
        )
        assert "http://localhost:8765/" in md
        assert "_zoomable_html/10_decision_l2a_sell.html" in md

    def test_domain_file_has_legend_and_three_views(
        self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded
    ):
        """Domain 文件含图例 + 三视图小标题 + 运营态占位（sell 全 design）。§3.1/§3.2。"""
        md = _gen_domain_file_md(
            sample_tracks[0],
            "L2A",
            "sell",
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
        )
        assert "图例说明" in md
        assert "### 全景图（全部模块" in md
        assert "### 运营态的图" in md
        assert "### 设计态的图" in md
        # sell 域全 design → 运营态视图占位（无 mermaid）
        assert "（无模块 / No modules）" in md

    def test_domain_file_mermaid_has_gray_theme(
        self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded
    ):
        """Domain 文件每个 mermaid 块第一行是灰色主题头。§4.1。"""
        md = _gen_domain_file_md(
            sample_tracks[0],
            "L2A",
            "sell",
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
        )
        # 每个 ```mermaid 后第一行含 themeVariables + primaryColor
        blocks = md.split("```mermaid")[1:]
        for block in blocks:
            first_line = block.lstrip("\n").split("\n")[0]
            assert "theme" in first_line
            assert "primaryColor" in first_line
            assert "clusterBkg" in first_line  # transparent clusterBkg（§13.3）

    def test_index_has_frontmatter_no_html_link(
        self, sample_tracks, sample_layers_expanded, sample_nodes_expanded, sample_edges_expanded
    ):
        """主索引含 frontmatter 但无 HTML 链接（0 mermaid 纯导航）。"""
        di = _build_domain_index(sample_tracks, sample_layers_expanded, sample_nodes_expanded)
        md = _gen_index_md(
            sample_tracks,
            sample_layers_expanded,
            sample_nodes_expanded,
            sample_edges_expanded,
            [],
            di,
        )
        assert md.startswith("---")
        assert "doc_type: architecture_view" in md
        assert "http://localhost:8765/" not in md


# ---------- 文件编号与陈旧清理正则测试 ----------


class TestFileNumbering:
    """文件命名序号 + 陈旧清理正则测试。"""

    def test_track_filename_with_priority(self):
        """track priority=1 → 01_decision_track_model_driven.md。"""
        assert _track_filename({"id": "model_driven", "priority": 1}) == "01_decision_track_model_driven.md"

    def test_track_filename_no_priority(self):
        """priority 缺失 → 00 前缀。"""
        assert _track_filename({"id": "xxx"}) == "00_decision_track_xxx.md"

    def test_track_filename_hyphen_replaced(self):
        """track_id 含连字符 → 下划线（model_driven-data → model_driven_data）。"""
        assert _track_filename({"id": "human-override", "priority": 3}) == "03_decision_track_human_override.md"

    def test_domain_filename_l2a_sell(self):
        """L2A sell 域 → 10_decision_l2a_sell.md（sell 是 _L2A_DOMAINS_ALPHA[4]，6+4=10）。"""
        assert _domain_filename("L2A", "sell") == "10_decision_l2a_sell.md"

    def test_domain_filename_l3_position(self):
        """L3 position 域 → 18_decision_l3_position.md（position 是 _L3_DOMAINS_ALPHA[5]，13+5=18）。"""
        assert _domain_filename("L3", "position") == "18_decision_l3_position.md"

    def test_domain_filename_unknown_layer_raises(self):
        """未知 layer_id → ValueError。"""
        with pytest.raises(ValueError):
            _domain_filename("L0", "whatever")

    def test_stale_regex_excludes_index(self):
        """陈旧正则不匹配 decision_index.md（无数字前缀）。"""
        assert re.match(_STALE_FILE_REGEX, "decision_index.md") is None

    def test_stale_regex_matches_numbered(self):
        """陈旧正则匹配 99_decision_obsolete.md。"""
        assert re.match(_STALE_FILE_REGEX, "99_decision_obsolete.md") is not None

    def test_stale_regex_excludes_non_decision(self):
        """陈旧正则不匹配非 decision 前缀的编号文件（不误删其他生成器产物）。"""
        assert re.match(_STALE_FILE_REGEX, "22_d_sell_architecture.md") is None
