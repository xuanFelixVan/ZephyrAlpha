# [A_test] module_id: MOD-GOV_generate_dataflow_diagram | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_GENERATE_DATAFLOW_DIAGRAM | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §test
# [MODULE] tests.governance.test_generate_dataflow_diagram
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.d5_architecture.generators.generate_dataflow_diagram
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_generate_dataflow_diagram.py
# [A_module] module_id=MOD-GOV_GENERATE_DATAFLOW_DIAGRAM | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-051
"""test_generate_dataflow_diagram.py — generate_dataflow_diagram.py 单元测试

覆盖：
  - _gen_mermaid 返回值类型（tuple[str, int, int, int]）—— 修复"日志显示过滤前总数"瑕疵后补充
  - scope_filter 过滤逻辑（production / backtest_internal / None）
  - edge 计数（仅统计两端都在过滤后集合的边，跨 scope 边不计入）
  - _gen_production_md 统计正确性

依据：ARCH-051 裁定（2026-07-06）；commit 748e0d0356 返回值改型。
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

# 动态加载 scripts/ 下的模块（非 Python 包，需 importlib）
_SCRIPT_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "governance"
    / "d5_architecture"
    / "generators"
    / "generate_dataflow_diagram.py"
)

try:
    _spec = importlib.util.spec_from_file_location("generate_dataflow_diagram", _SCRIPT_PATH)
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    _gen_mermaid = _mod._gen_mermaid
    _gen_panorama_md = _mod._gen_panorama_md
    _gen_domain_md = _mod._gen_domain_md
    _extract_zh_label = _mod._extract_zh_label
except Exception as e:  # noqa: BLE001
    pytest.skip(
        f"generate_dataflow_diagram 模块加载失败（可能缺少 zephyr 依赖）: {e}",
        allow_module_level=True,
    )


# ---------- Fixtures ----------


@pytest.fixture
def sample_datasets():
    """3 个 Dataset：2 production + 1 backtest，全部 design_maturity=production（运营态）。"""
    return [
        {
            "id": 1,
            "name": "market_data.tick",
            "scope": "production",
            "contract": "CTR-001",
            "physical_type": "table",
            "produced_by": "JOB-001",
            "domain": "D_MKT_DATA",
            "maturity": "production",
            "build": "generated",
            "pit": "strict",
        },
        {
            "id": 2,
            "name": "signal.composite",
            "scope": "production",
            "contract": "CTR-002",
            "physical_type": "table",
            "produced_by": "JOB-002",
            "domain": "D_SIGLEGACY",
            "maturity": "production",
            "build": "generated",
            "pit": "strict",
        },
        {
            "id": 3,
            "name": "backtest.fills",
            "scope": "backtest_internal",
            "contract": None,
            "physical_type": "table",
            "produced_by": "JOB-003",
            "domain": "D_BACKTEST",
            "maturity": "production",
            "build": "generated",
            "pit": "strict",
        },
    ]


@pytest.fixture
def sample_jobs():
    """3 个 Job：2 production + 1 backtest，全部 design_maturity=production（运营态）。"""
    return [
        {
            "id": 10,
            "name": "ingest.akshare_kline",
            "scope": "production",
            "source": "src/zephyr/data/ingest.py",
            "trigger": "scheduled",
            "context": "production",
            "maturity": "production",
            "build": "generated",
        },
        {
            "id": 11,
            "name": "synthesize.signal",
            "scope": "production",
            "source": "src/zephyr/signal_ashare/synthesizer.py",
            "trigger": "event_driven",
            "context": "production",
            "maturity": "production",
            "build": "generated",
        },
        {
            "id": 12,
            "name": "backtest.replay_ticks",
            "scope": "backtest_internal",
            "source": "src/zephyr/backtest/tick_replay.py",
            "trigger": "manual",
            "context": "backtest_tick",
            "maturity": "production",
            "build": "generated",
        },
    ]


@pytest.fixture
def sample_datasets_with_design():
    """4 个 Dataset：3 运营态 + 1 设计态（design_maturity=design）。"""
    return [
        {
            "id": 1,
            "name": "market_data.tick",
            "scope": "production",
            "contract": "CTR-001",
            "physical_type": "table",
            "produced_by": "JOB-001",
            "domain": "D_MKT_DATA",
            "maturity": "production",
            "build": "generated",
            "pit": "strict",
        },
        {
            "id": 2,
            "name": "signal.composite",
            "scope": "production",
            "contract": "CTR-002",
            "physical_type": "table",
            "produced_by": "JOB-002",
            "domain": "D_SIGLEGACY",
            "maturity": "production",
            "build": "generated",
            "pit": "strict",
        },
        {
            "id": 3,
            "name": "backtest.fills",
            "scope": "backtest_internal",
            "contract": None,
            "physical_type": "table",
            "produced_by": "JOB-003",
            "domain": "D_BACKTEST",
            "maturity": "production",
            "build": "generated",
            "pit": "strict",
        },
        # 设计态节点（蓝图规划，代码未写）
        {
            "id": 4,
            "name": "factor.alpha_factor",
            "scope": "production",
            "contract": "CTR-009",
            "physical_type": "table",
            "produced_by": "JOB-004",
            "domain": "D_FACTOR",
            "maturity": "design",
            "build": "planned",
            "pit": "strict",
        },
    ]


@pytest.fixture
def sample_jobs_with_design():
    """4 个 Job：3 运营态 + 1 设计态（design_maturity=design）。"""
    return [
        {
            "id": 10,
            "name": "ingest.akshare_kline",
            "scope": "production",
            "source": "src/zephyr/data/ingest.py",
            "trigger": "scheduled",
            "context": "production",
            "maturity": "production",
            "build": "generated",
        },
        {
            "id": 11,
            "name": "synthesize.signal",
            "scope": "production",
            "source": "src/zephyr/signal_ashare/synthesizer.py",
            "trigger": "event_driven",
            "context": "production",
            "maturity": "production",
            "build": "generated",
        },
        {
            "id": 12,
            "name": "backtest.replay_ticks",
            "scope": "backtest_internal",
            "source": "src/zephyr/backtest/tick_replay.py",
            "trigger": "manual",
            "context": "backtest_tick",
            "maturity": "production",
            "build": "generated",
        },
        # 设计态节点（蓝图规划，代码未写）
        {
            "id": 13,
            "name": "compute.alpha_factor",
            "scope": "production",
            "source": "src/zephyr/factor/alpha_factor.py",
            "trigger": "event_driven",
            "context": "production",
            "maturity": "design",
            "build": "planned",
        },
    ]


@pytest.fixture
def sample_edges():
    """5 条边：3 produces + 2 consumed_by。"""
    return [
        # job -> dataset (produces)
        {"from_id": 10, "to_id": 1, "from_type": "job", "to_type": "dataset", "type": "produces"},
        {"from_id": 11, "to_id": 2, "from_type": "job", "to_type": "dataset", "type": "produces"},
        {"from_id": 12, "to_id": 3, "from_type": "job", "to_type": "dataset", "type": "produces"},
        # dataset -> job (consumed by)
        {"from_id": 1, "to_id": 11, "from_type": "dataset", "to_type": "job", "type": "consumed_by"},
        {"from_id": 3, "to_id": 12, "from_type": "dataset", "to_type": "job", "type": "consumed_by"},
    ]


@pytest.fixture
def design_only_datasets():
    """3 个设计态 Dataset（含 format_summary，名称未收录于 glossary，走回退提取中文）。"""
    return [
        {
            "id": 21,
            "name": "factor.ashare_alpha87",
            "scope": "production",
            "contract": None,
            "physical_type": "table",
            "produced_by": "JOB-021",
            "domain": "D_FACTOR",
            "maturity": "design",
            "build": "planned",
            "pit": "strict",
            "format_summary": "A股Alpha#87因子信号（多因子截面排名）",
        },
        {
            "id": 22,
            "name": "factor.ashare_capital_flow",
            "scope": "production",
            "contract": None,
            "physical_type": "table",
            "produced_by": "JOB-022",
            "domain": "D_FACTOR",
            "maturity": "design",
            "build": "planned",
            "pit": "strict",
            "format_summary": "A股资金流向因子（主力资金净流入/流出）",
        },
        {
            "id": 23,
            "name": "factor.ashare_fundamental",
            "scope": "production",
            "contract": None,
            "physical_type": "table",
            "produced_by": "JOB-023",
            "domain": "D_FACTOR",
            "maturity": "design",
            "build": "planned",
            "pit": "strict",
            "format_summary": "A股基本面因子（PE/PB/ROE/股息率等）",
        },
    ]


@pytest.fixture
def design_only_jobs():
    """3 个设计态 Job（含 description，名称未收录于 glossary，走回退提取中文）。"""
    return [
        {
            "id": 31,
            "name": "compute.ashare_alpha87",
            "scope": "production",
            "source": "src/zephyr/factor/ashare/alpha87.py",
            "trigger": "event_driven",
            "context": "production",
            "maturity": "design",
            "build": "planned",
            "description": "计算Alpha#87因子（消费OHLC K线，产出因子信号）",
        },
        {
            "id": 32,
            "name": "compute.ashare_capital_flow",
            "scope": "production",
            "source": "src/zephyr/factor/ashare/capital_flow.py",
            "trigger": "event_driven",
            "context": "production",
            "maturity": "design",
            "build": "planned",
            "description": "计算资金流因子（消费OHLC K线，产出因子信号）",
        },
        {
            "id": 33,
            "name": "compute.ashare_fundamental",
            "scope": "production",
            "source": "src/zephyr/factor/ashare/fundamental.py",
            "trigger": "event_driven",
            "context": "production",
            "maturity": "design",
            "build": "planned",
            "description": "计算基本面因子（消费OHLC K线，产出因子信号）",
        },
    ]


@pytest.fixture
def design_only_edges():
    """3 条 produces 边（job→dataset），单向 push，无交叉消费（横向铺开场景）。"""
    return [
        {"from_id": 31, "to_id": 21, "from_type": "job", "to_type": "dataset", "type": "produces"},
        {"from_id": 32, "to_id": 22, "from_type": "job", "to_type": "dataset", "type": "produces"},
        {"from_id": 33, "to_id": 23, "from_type": "job", "to_type": "dataset", "type": "produces"},
    ]


# ---------- _gen_mermaid 测试 ----------


class TestGenMermaid:
    """_gen_mermaid 返回值与过滤逻辑测试。"""

    def test_returns_tuple_of_four(self, sample_datasets, sample_jobs, sample_edges):
        """返回值必须是 4 元组 (mmd_text, ds_count, job_count, edge_count)。"""
        result = _gen_mermaid(sample_datasets, sample_jobs, sample_edges)
        assert isinstance(result, tuple)
        assert len(result) == 4
        mmd, ds_count, job_count, edge_count = result
        assert isinstance(mmd, str)
        assert isinstance(ds_count, int)
        assert isinstance(job_count, int)
        assert isinstance(edge_count, int)

    def test_no_filter_returns_all(self, sample_datasets, sample_jobs, sample_edges):
        """无 scope_filter 时返回全部数据。"""
        mmd, ds_count, job_count, edge_count = _gen_mermaid(sample_datasets, sample_jobs, sample_edges)
        assert ds_count == 3
        assert job_count == 3
        assert edge_count == 5
        assert "DS1" in mmd and "DS2" in mmd and "DS3" in mmd
        assert "JOB10" in mmd and "JOB11" in mmd and "JOB12" in mmd

    def test_production_filter(self, sample_datasets, sample_jobs, sample_edges):
        """scope_filter=production 只返回 production scope 的数据。"""
        mmd, ds_count, job_count, edge_count = _gen_mermaid(
            sample_datasets, sample_jobs, sample_edges, scope_filter="production"
        )
        assert ds_count == 2  # id=1,2
        assert job_count == 2  # id=10,11
        assert edge_count == 3  # 10→1, 11→2, 1→11
        assert "DS1" in mmd and "DS2" in mmd
        assert "DS3" not in mmd  # backtest 被过滤
        assert "JOB10" in mmd and "JOB11" in mmd
        assert "JOB12" not in mmd

    def test_backtest_filter(self, sample_datasets, sample_jobs, sample_edges):
        """scope_filter=backtest_internal 只返回 backtest scope 的数据。"""
        mmd, ds_count, job_count, edge_count = _gen_mermaid(
            sample_datasets, sample_jobs, sample_edges, scope_filter="backtest_internal"
        )
        assert ds_count == 1  # id=3
        assert job_count == 1  # id=12
        assert edge_count == 2  # 12→3, 3→12
        assert "DS3" in mmd
        assert "DS1" not in mmd and "DS2" not in mmd
        assert "JOB12" in mmd
        assert "JOB10" not in mmd

    def test_edge_count_excludes_cross_scope(self, sample_datasets, sample_jobs, sample_edges):
        """跨 scope 的边不应计入（一端在过滤集合外）。"""
        # 添加一条跨 scope 边：production job 10 -> backtest dataset 3
        edges_with_cross = sample_edges + [
            {"from_id": 10, "to_id": 3, "from_type": "job", "to_type": "dataset", "type": "produces"},
        ]
        # production filter：from_id(10) 在 job_ids 但 to_id(3) 不在 ds_ids → 不计入
        _, _, _, edge_count_prod = _gen_mermaid(
            sample_datasets, sample_jobs, edges_with_cross, scope_filter="production"
        )
        assert edge_count_prod == 3  # 仍是 3，跨 scope 边未计入
        # backtest filter：from_id(10) 不在 job_ids（backtest 只有 12）→ 不计入
        _, _, _, edge_count_bt = _gen_mermaid(
            sample_datasets, sample_jobs, edges_with_cross, scope_filter="backtest_internal"
        )
        assert edge_count_bt == 2  # 仍是 2

    def test_empty_input(self):
        """空输入返回空图 + 零计数。"""
        mmd, ds_count, job_count, edge_count = _gen_mermaid([], [], [])
        assert ds_count == 0
        assert job_count == 0
        assert edge_count == 0
        assert "flowchart TD" in mmd

    def test_mmd_contains_edge_labels(self, sample_datasets, sample_jobs, sample_edges):
        """mmd 文本包含 produces / consumed by 边标签（中英并列）。"""
        mmd, _, _, _ = _gen_mermaid(sample_datasets, sample_jobs, sample_edges)
        assert "|produces / 产出|" in mmd
        assert "|consumed by / 被消费于|" in mmd

    def test_mmd_uses_gray_theme_with_classdef(self, sample_datasets, sample_jobs, sample_edges):
        """mmd 使用灰色主题（%%{init}%% + TD）+ 4-class classDef（模板 V1.2 §4.1/§4.7）。"""
        mmd, _, _, _ = _gen_mermaid(sample_datasets, sample_jobs, sample_edges)
        assert "%%{init:" in mmd
        assert "'primaryColor': '#eaeaea'" in mmd
        assert "flowchart TD" in mmd
        # 模板 V1.2：4-class classDef 始终启用
        assert "classDef production" in mmd
        assert "classDef design" in mmd
        assert "classDef external_prod" in mmd
        assert "classDef external_design" in mmd

    def test_mmd_contains_maturity_prefix(self, sample_datasets, sample_jobs, sample_edges):
        """mmd 节点标签包含 (生产态 / production) 成熟度全称（模板 V1.2 §4.3 四要素）。"""
        mmd, _, _, _ = _gen_mermaid(sample_datasets, sample_jobs, sample_edges)
        # 全部节点 design_maturity=production → 四要素首行含 (生产态 / production)
        assert "(生产态 / production)" in mmd


# ---------- 设计态/运营态（design_maturity）测试 ----------


class TestDesignMaturity:
    """design_maturity 维度测试：(设计态 / design) 四要素 + maturity_filter（模板 V1.2 classDef）。"""

    def test_design_node_has_class_and_label(self, sample_datasets_with_design, sample_jobs_with_design, sample_edges):
        """design_maturity=design 的节点有 class 赋值 + (设计态 / design) 四要素标签。"""
        mmd, _, _, _ = _gen_mermaid(sample_datasets_with_design, sample_jobs_with_design, sample_edges)
        # DS4 是设计态 Dataset → 节点定义存在 + class design 赋值行含 DS4
        assert "DS4" in mmd
        assert "class DS4" in mmd  # design class 赋值行（如 'class DS4,JOB13 design'）
        # JOB13 是设计态 Job → 节点定义存在
        assert "JOB13" in mmd

    def test_design_node_has_design_prefix(self, sample_datasets_with_design, sample_jobs_with_design, sample_edges):
        """design_maturity=design 的节点四要素首行含 (设计态 / design)。"""
        mmd, _, _, _ = _gen_mermaid(sample_datasets_with_design, sample_jobs_with_design, sample_edges)
        assert "(设计态 / design)" in mmd

    def test_production_node_has_class(self, sample_datasets_with_design, sample_jobs_with_design, sample_edges):
        """design_maturity=production 的节点有 class production 赋值（模板 V1.2 §4.8）。"""
        mmd, _, _, _ = _gen_mermaid(sample_datasets_with_design, sample_jobs_with_design, sample_edges)
        # DS1 是 production scope + production maturity → 节点定义存在 + class production
        assert "DS1" in mmd
        assert "class " in mmd  # 有 class 赋值行

    def test_maturity_filter_production_excludes_design(
        self, sample_datasets_with_design, sample_jobs_with_design, sample_edges
    ):
        """maturity_filter=production 排除设计态节点。"""
        mmd, ds_count, job_count, _ = _gen_mermaid(
            sample_datasets_with_design,
            sample_jobs_with_design,
            sample_edges,
            maturity_filter="production",
        )
        # 3 运营态 dataset + 3 运营态 job（设计态 DS4/JOB13 被过滤）
        assert ds_count == 3
        assert job_count == 3
        assert "DS4" not in mmd
        assert "JOB13" not in mmd

    def test_maturity_filter_design_only(self, sample_datasets_with_design, sample_jobs_with_design, sample_edges):
        """maturity_filter=design 只返回设计态节点。"""
        mmd, ds_count, job_count, _ = _gen_mermaid(
            sample_datasets_with_design,
            sample_jobs_with_design,
            sample_edges,
            maturity_filter="design",
        )
        # 仅 1 设计态 dataset + 1 设计态 job
        assert ds_count == 1
        assert job_count == 1
        assert "DS4" in mmd
        assert "JOB13" in mmd
        assert "DS1" not in mmd


# ---------- _gen_panorama_md 测试 ----------


class TestGenPanoramaMd:
    """_gen_panorama_md 统计正确性测试（全项目数据流全景：运营态 + 设计态）。"""

    def test_stats_table(self, sample_datasets, sample_jobs, sample_edges):
        """全景文档统计表正确。"""
        md = _gen_panorama_md(sample_datasets, sample_jobs, sample_edges)
        # | Dataset | 2 | 1 | 3 |  production=2, backtest=1, total=3
        assert "| Dataset | 2 | 1 | 3 |" in md
        assert "| Job | 2 | 1 | 3 |" in md
        assert "| Edge | - | - | 5 |" in md

    def test_design_maturity_stats_table(self, sample_datasets_with_design, sample_jobs_with_design, sample_edges):
        """全景文档包含设计态/运营态统计子表（design_maturity 维度）。"""
        md = _gen_panorama_md(sample_datasets_with_design, sample_jobs_with_design, sample_edges)
        # 4 dataset: 3 production + 1 design（4 列：运营态/设计态/合计）
        assert "| Dataset | 3 | 1 | 4 |" in md
        # 4 job: 3 production + 1 design
        assert "| Job | 3 | 1 | 4 |" in md
        # 设计态 vs 运营态说明
        assert "设计态 vs 运营态" in md

    def test_contains_operation_state_diagram(self, sample_datasets_with_design, sample_jobs_with_design, sample_edges):
        """全景文档包含运营态的图章节（仅 design_maturity=production，模板 V1.2 三视图）。"""
        md = _gen_panorama_md(sample_datasets_with_design, sample_jobs_with_design, sample_edges)
        assert "运营态的图" in md
        # 三视图铁律：全景图 → 运营态的图 → 设计态的图
        assert "### 全景图（全部模块，颜色区分运营态/设计态）" in md
        assert "### 运营态的图（仅 design_maturity=production）" in md
        assert "### 设计态的图（仅 design_maturity=design）" in md

    def test_contains_dataset_list(self, sample_datasets, sample_jobs, sample_edges):
        """全景文档包含 Dataset 清单。"""
        md = _gen_panorama_md(sample_datasets, sample_jobs, sample_edges)
        assert "market_data.tick" in md
        assert "signal.composite" in md
        assert "backtest.fills" in md

    def test_contains_job_list(self, sample_datasets, sample_jobs, sample_edges):
        """全景文档包含 Job 清单。"""
        md = _gen_panorama_md(sample_datasets, sample_jobs, sample_edges)
        assert "ingest.akshare_kline" in md
        assert "synthesize.signal" in md
        assert "backtest.replay_ticks" in md

    def test_panorama_md_has_html_link(self, sample_datasets, sample_jobs, sample_edges):
        """全景文档顶部有 HTML 跳转链接（模板 §14：http:// 绝对路径）。"""
        md = _gen_panorama_md(sample_datasets, sample_jobs, sample_edges)
        assert "可缩放 HTML 版" in md
        assert "http://localhost:8765/" in md
        assert "_zoomable_html/dataflow_panorama.html" in md

    def test_panorama_md_has_three_views(self, sample_datasets, sample_jobs, sample_edges):
        """全景文档有三视图铁律顺序：全景图 → 运营态的图 → 设计态的图。"""
        md = _gen_panorama_md(sample_datasets, sample_jobs, sample_edges)
        idx_panorama = md.find("### 全景图")
        idx_op = md.find("### 运营态的图")
        idx_design = md.find("### 设计态的图")
        assert idx_panorama != -1 and idx_op != -1 and idx_design != -1
        assert idx_panorama < idx_op < idx_design  # 顺序铁律

    def test_panorama_includes_both_production_and_design(
        self, sample_datasets_with_design, sample_jobs_with_design, sample_edges
    ):
        """全景图 Mermaid 块同时含运营态和设计态节点（用户核心需求：一张看完所有东西）。"""
        md = _gen_panorama_md(sample_datasets_with_design, sample_jobs_with_design, sample_edges)
        # 提取全景图 Mermaid 块（### 全景图 到 ### 运营态的图 之间）
        idx_pan = md.find("### 全景图")
        idx_op = md.find("### 运营态的图")
        panorama_block = md[idx_pan:idx_op]
        # 全景图必须同时含生产态和设计态节点
        assert "(生产态 / production)" in panorama_block
        assert "(设计态 / design)" in panorama_block
        # 设计态节点 DS4/JOB13 必须出现在全景图中
        assert "DS4" in panorama_block
        assert "JOB13" in panorama_block


# ---------- 模板 V1.2 对齐测试 ----------


class TestTopologicalLayering:
    """拓扑分层（Kahn + ~~~ 不可见边）测试（模板 §4.6）。"""

    def test_has_invisible_edges_for_layering(self, sample_datasets, sample_jobs, sample_edges):
        """多节点图应含 ~~~ 不可见边强制同 rank 竖排。"""
        mmd, _, _, _ = _gen_mermaid(sample_datasets, sample_jobs, sample_edges)
        assert "~~~" in mmd

    def test_single_node_no_layering(self):
        """单节点无同层串联（无需 ~~~）。"""
        ds = [{"id": 1, "name": "a", "scope": "production", "maturity": "production"}]
        job = [{"id": 10, "name": "j", "scope": "production", "maturity": "production"}]
        edges = [{"from_id": 10, "to_id": 1, "from_type": "job", "to_type": "dataset", "type": "produces"}]
        mmd, _, _, _ = _gen_mermaid(ds, job, edges)
        # 2 节点 1 边，layer 0=JOB10, layer 1=DS1，不同层无 ~~~
        assert "~~~" not in mmd


class TestSolidDashedArrows:
    """实线/虚线箭头测试（模板 §4.5：production 间实线，其余虚线）。"""

    def test_production_to_production_solid(self, sample_datasets, sample_jobs, sample_edges):
        """两端均 production → 实线箭头 -->。"""
        mmd, _, _, _ = _gen_mermaid(sample_datasets, sample_jobs, sample_edges)
        assert "JOB10 -->|produces" in mmd  # production→production

    def test_design_to_design_dashed(self, design_only_datasets, design_only_jobs, design_only_edges):
        """两端均 design → 虚线箭头 -.->。"""
        mmd, _, _, _ = _gen_mermaid(design_only_datasets, design_only_jobs, design_only_edges)
        assert "JOB31 -.->|produces" in mmd  # design→design

    def test_mixed_maturity_dashed(self, sample_datasets_with_design, sample_jobs_with_design, sample_edges):
        """混合 maturity 图含实线（production 间）和虚线（design 相关）。"""
        # sample_edges 无 JOB13→DS4 边，补一条 design→design 边测试虚线
        edges_with_design = sample_edges + [
            {"from_id": 13, "to_id": 4, "from_type": "job", "to_type": "dataset", "type": "produces"},
        ]
        mmd, _, _, _ = _gen_mermaid(sample_datasets_with_design, sample_jobs_with_design, edges_with_design)
        assert "JOB10 -->|produces" in mmd  # production→production 实线
        assert "JOB13 -.->|produces" in mmd  # design→design 虚线


class TestCrossDomainExternal:
    """跨域外部 Dataset 节点测试（模板 §4.3 跨域节点）。"""

    def test_external_ds_rendered_with_class(self):
        """external_ds 参数传入的节点渲染为 external_prod/external_design 类。"""
        local_ds = [
            {
                "id": 1,
                "name": "local.out",
                "scope": "production",
                "maturity": "production",
                "domain": "D_FACTOR",
                "contract": "CTR-1",
            }
        ]
        local_job = [
            {"id": 10, "name": "local.compute", "scope": "production", "maturity": "production", "source": "src/x.py"}
        ]
        ext_ds = [
            {
                "id": 99,
                "name": "ext.market",
                "scope": "production",
                "maturity": "production",
                "domain": "D_MKT_DATA",
                "contract": "CTR-9",
            }
        ]
        edges = [
            {"from_id": 10, "to_id": 1, "from_type": "job", "to_type": "dataset", "type": "produces"},
            {"from_id": 99, "to_id": 10, "from_type": "dataset", "to_type": "job", "type": "consumed_by"},
        ]
        mmd, ds_count, _, _ = _gen_mermaid(local_ds, local_job, edges, external_ds=ext_ds)
        # 外部节点 DS99 出现在图中
        assert "DS99" in mmd
        # 计数只含域内节点（1 dataset），不含外部
        assert ds_count == 1
        # 外部节点绑 external_prod 类（maturity=production）——赋值行含 DS99 + external_prod
        assignment_lines = [l for l in mmd.split("\n") if l.strip().startswith("class ")]
        assert any("DS99" in l and "external_prod" in l for l in assignment_lines)
        # 跨域边为虚线
        assert "DS99 -.->|consumed by" in mmd
        # 跨域标识
        assert "跨域节点 / cross-domain" in mmd

    def test_no_external_ds_when_param_none(self, sample_datasets, sample_jobs, sample_edges):
        """不传 external_ds 时无跨域节点标识，无 external_* class 赋值行。"""
        mmd, _, _, _ = _gen_mermaid(sample_datasets, sample_jobs, sample_edges)
        assert "跨域节点 / cross-domain" not in mmd
        # classDef external_prod 定义行始终存在，但不应有 class ... external_prod 赋值行
        assignment_lines = [l for l in mmd.split("\n") if l.strip().startswith("class ")]
        assert not any("external_prod" in l for l in assignment_lines)
        assert not any("external_design" in l for l in assignment_lines)


class TestDomainMdTemplate:
    """_gen_domain_md 模板 V1.2 对齐测试。"""

    @staticmethod
    def _mk_grp():
        return {"key": "d_test", "title": "测试域", "responsibility": "测试"}

    @staticmethod
    def _mk_ds():
        return [
            {
                "id": 1,
                "name": "a",
                "scope": "production",
                "maturity": "production",
                "domain": "D_TEST",
                "contract": "CTR-1",
            }
        ]

    @staticmethod
    def _mk_job():
        return [
            {
                "id": 10,
                "name": "j",
                "scope": "production",
                "maturity": "production",
                "source": "src/x.py",
                "trigger": "scheduled",
            }
        ]

    def test_domain_md_has_html_link(self):
        """域文档顶部有 HTML 跳转链接。"""
        md = _gen_domain_md(self._mk_grp(), self._mk_ds(), self._mk_job(), [])
        assert "可缩放 HTML 版" in md
        assert "_zoomable_html/d_test.html" in md

    def test_domain_md_three_views_order(self):
        """域文档三视图顺序：全景图 → 运营态的图 → 设计态的图。"""
        md = _gen_domain_md(self._mk_grp(), self._mk_ds(), self._mk_job(), [])
        idx_pan = md.find("### 全景图")
        idx_op = md.find("### 运营态的图")
        idx_des = md.find("### 设计态的图")
        assert idx_pan != -1 and idx_op != -1
        assert idx_pan < idx_op

    def test_domain_md_empty_view_placeholder(self):
        """无设计态节点时，设计态视图用占位说明。"""
        md = _gen_domain_md(self._mk_grp(), self._mk_ds(), self._mk_job(), [])
        assert "（无模块 / No modules）" in md  # 设计态视图占位
