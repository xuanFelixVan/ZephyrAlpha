# [A_test] module_id: MOD-GOV_DATAFLOW_DIAGRAM | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_DATAFLOW_DIAGRAM | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §test
# [MODULE] tests.governance.test_dataflow_design_layout
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.d5_architecture.generators.generate_dataflow_diagram
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_dataflow_design_layout.py
# [A_module] module_id=MOD-GOV_DATAFLOW_DIAGRAM | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-051
"""test_dataflow_design_layout.py — 设计态数据流文档视觉风格测试（V1.2 模板对齐）

覆盖 generate_dataflow_diagram.py 的设计态域文档增强功能：
  - _extract_zh_label：从 format_summary/description 提取中文标签（V1.2：<br/> 分隔+全角括号）
  - 拓扑分层：Kahn 算法自动计算层级，同层 ~~~ 不可见边串联（V1.2 替代旧 force_vertical 参数）
  - _gen_domain_md：域职责（Responsibility）段落渲染

依据：用户需求（2026-07-31）——设计态 d_*.md 视觉风格对齐 dataflow_panorama.md
（四要素标签 + 竖向高列布局）+ 06_decision_l2a_data.md（域职责说明）。
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
    """3 个运营态 Dataset（glossary 有映射，不走回退）。"""
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
    """3 个运营态 Job。"""
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
def sample_edges():
    """5 条边：3 produces + 2 consumed_by（运营态有交叉消费边）。"""
    return [
        {"from_id": 10, "to_id": 1, "from_type": "job", "to_type": "dataset", "type": "produces"},
        {"from_id": 11, "to_id": 2, "from_type": "job", "to_type": "dataset", "type": "produces"},
        {"from_id": 12, "to_id": 3, "from_type": "job", "to_type": "dataset", "type": "produces"},
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


# ---------- _extract_zh_label 测试 ----------


class TestExtractZhLabel:
    """_extract_zh_label 从 format_summary/description 提取简短中文标签。"""

    def test_extract_before_paren(self):
        """V1.2：在"（"前插入 <br/> 分隔，保留括号内容（四要素标签多行显示）。"""
        assert (
            _extract_zh_label("A股Alpha#87因子信号（多因子截面排名）") == "A股Alpha#87因子信号<br/>（多因子截面排名）"
        )

    def test_extract_before_ascii_paren(self):
        """V1.2：半角"("也插入 <br/> 并归一化为全角括号。"""
        assert _extract_zh_label("因子信号(multifactor)") == "因子信号<br/>（multifactor）"

    def test_truncate_overlong(self):
        """超长（>max_len）截断并加省略号。"""
        long_text = "这是一个非常长的中文功能描述句子用于测试截断逻辑是否正常工作"
        result = _extract_zh_label(long_text, max_len=10)
        # 前 10 字符 + 省略号（U+2026 单字符）
        assert result == "这是一个非常长的中文" + "…"
        assert len(result) == 11  # 10 + 省略号

    def test_empty_input(self):
        """空输入返回空串。"""
        assert _extract_zh_label(None) == ""
        assert _extract_zh_label("") == ""

    def test_no_paren_returns_full(self):
        """无括号时返回完整文本（截断后）。"""
        assert _extract_zh_label("因子信号") == "因子信号"


# ---------- 拓扑分层竖向布局测试（V1.2：自动 Kahn 分层，无需 force_vertical 参数）----------


class TestTopologicalLayering:
    """V1.2 拓扑分层：Kahn 算法自动计算节点层级，同层节点用 ~~~ 不可见边串联强制竖排。"""

    def test_auto_layering_adds_invisible_chain(self, design_only_datasets, design_only_jobs, design_only_edges):
        """多节点同层时自动添加 ~~~ 不可见边串联（无需 force_vertical 参数）。"""
        mmd, _, job_count, edge_count = _gen_mermaid(
            design_only_datasets,
            design_only_jobs,
            design_only_edges,
            maturity_filter="design",
        )
        # 3 个 job 在同层（layer 0）→ ~~~ 串联；3 个 DS 在同层（layer 1）→ ~~~ 串联
        assert "~~~" in mmd
        # 不可见边不计入 edge_count（仍为 3 条 produces 边）
        assert edge_count == 3
        assert job_count == 3

    def test_layering_always_on_for_multi_node(self, design_only_datasets, design_only_jobs, design_only_edges):
        """V1.2 拓扑分层始终启用——多节点同层即有 ~~~，无开关可关。"""
        mmd, _, _, _ = _gen_mermaid(
            design_only_datasets,
            design_only_jobs,
            design_only_edges,
            maturity_filter="design",
        )
        assert "~~~" in mmd  # 同层 JOB 间 + 同层 DS 间均有 ~~~

    def test_single_node_no_layering(self, design_only_datasets, design_only_jobs, design_only_edges):
        """仅 1 job + 1 DS（不同层）时无需 ~~~ 串联。"""
        single_ds = [design_only_datasets[0]]
        single_job = [design_only_jobs[0]]
        single_edge = [design_only_edges[0]]
        mmd, _, _, _ = _gen_mermaid(
            single_ds,
            single_job,
            single_edge,
            maturity_filter="design",
        )
        assert "~~~" not in mmd

    def test_production_has_solid_arrows(self, sample_datasets, sample_jobs, sample_edges):
        """运营态节点间用实线箭头 -->（模板 §4.5），produces/consumed 边不受分层影响。"""
        mmd, _, _, edge_count = _gen_mermaid(
            sample_datasets,
            sample_jobs,
            sample_edges,
        )
        assert edge_count == 5
        assert "|produces / 产出|" in mmd
        assert "|consumed by / 被消费于|" in mmd
        # production→production 实线
        assert "JOB10 -->|produces" in mmd


# ---------- 中文标签回退测试 ----------


class TestZhLabelFallback:
    """设计态节点中文标签回退：glossary 未收录时从 format_summary/description 提取。"""

    def test_design_dataset_label_has_zh_from_summary(self, design_only_datasets, design_only_jobs, design_only_edges):
        """V1.2 四要素：设计态 Dataset 标签含"name / zh_short"格式（ / 分隔+预折行）。"""
        mmd, _, _, _ = _gen_mermaid(
            design_only_datasets,
            design_only_jobs,
            design_only_edges,
            maturity_filter="design",
        )
        # DS21: factor.ashare_alpha87 / A股Alpha#87因子信号（ / 分隔，预折行后 <br/> 换行）
        assert "factor.ashare_alpha87 /<br/>A股Alpha#87因子信号" in mmd
        # DS22: factor.ashare_capital_flow / A股资金流向因子
        assert "factor.ashare_capital_flow /<br/>A股资金流向因子" in mmd

    def test_design_job_label_has_zh_from_description(self, design_only_datasets, design_only_jobs, design_only_edges):
        """V1.2 四要素：设计态 Job 标签含"name / zh_short"格式（ / 分隔+预折行）。"""
        mmd, _, _, _ = _gen_mermaid(
            design_only_datasets,
            design_only_jobs,
            design_only_edges,
            maturity_filter="design",
        )
        # JOB31: compute.ashare_alpha87 / 计算Alpha#87因子
        assert "compute.ashare_alpha87 /<br/>计算Alpha#87因子" in mmd

    def test_production_dataset_uses_glossary_not_summary(self, sample_datasets, sample_jobs, sample_edges):
        """V1.2 四要素：运营态 Dataset 优先用 glossary 短名（ / 分隔+预折行）。"""
        mmd, _, _, _ = _gen_mermaid(sample_datasets, sample_jobs, sample_edges)
        # backtest.fills 在 glossary 中有映射 → 用短名"回测.模拟成交"
        assert "backtest.fills /<br/>回测.模拟成交" in mmd


# ---------- _gen_domain_md 域职责测试 ----------


class TestGenDomainMd:
    """_gen_domain_md 域职责段落 + 拓扑分层自动传递。"""

    def test_domain_md_contains_responsibility(self, design_only_datasets, design_only_jobs, design_only_edges):
        """域文档包含"域职责 / Responsibility"段落。"""
        grp = {
            "key": "d_test",
            "title": "测试域（设计态）",
            "responsibility": "测试域职责说明——因子计算/分析",
        }
        md = _gen_domain_md(grp, design_only_datasets, design_only_jobs, design_only_edges)
        assert "**域职责 / Responsibility**: 测试域职责说明——因子计算/分析" in md

    def test_domain_md_no_responsibility_field_skips_section(
        self, design_only_datasets, design_only_jobs, design_only_edges
    ):
        """无 responsibility 字段时不渲染域职责段落。"""
        grp = {"key": "d_test", "title": "测试域（设计态）"}
        md = _gen_domain_md(grp, design_only_datasets, design_only_jobs, design_only_edges)
        assert "域职责" not in md

    def test_domain_md_mermaid_has_vertical_chain(self, design_only_datasets, design_only_jobs, design_only_edges):
        """域文档内嵌 Mermaid 图含 ~~~ 竖向链（V1.2 拓扑分层自动传递）。"""
        grp = {
            "key": "d_test",
            "title": "测试域（设计态）",
            "responsibility": "测试职责",
        }
        md = _gen_domain_md(grp, design_only_datasets, design_only_jobs, design_only_edges)
        assert "~~~" in md
