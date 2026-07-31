# [A_test] module_id: MOD-GOV_DATAFLOW_DIAGRAM | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_DATAFLOW_DIAGRAM | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §test
# [MODULE] tests.test_dataflow_design_layout
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.d5_architecture.generators.generate_dataflow_diagram
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_dataflow_design_layout.py
# [TTL] permanent
# [ARCH-REF] #ARCH-051
"""test_dataflow_design_layout.py — 设计态数据流文档视觉风格测试

覆盖 generate_dataflow_diagram.py 的设计态域文档增强功能：
  - _extract_zh_label：从 format_summary/description 提取简短中文标签（glossary 回退）
  - force_vertical：~~~ 不可见链接强制竖向布局（设计态单向 push 边场景）
  - _gen_domain_md：域职责（Responsibility）段落渲染

依据：用户需求（2026-07-31）——设计态 d_*.md 视觉风格对齐 dataflow_production.md
（中英文标签 + 竖向高列布局）+ 06_decision_l2a_data.md（域职责说明）。
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

# 动态加载 scripts/ 下的模块（非 Python 包，需 importlib）
_SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts" / "governance" / "d5_architecture" / "generators"
    / "generate_dataflow_diagram.py"
)

try:
    _spec = importlib.util.spec_from_file_location(
        "generate_dataflow_diagram", _SCRIPT_PATH
    )
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
        {"id": 1, "name": "market_data.tick", "scope": "production", "contract": "CTR-001",
         "physical_type": "table", "produced_by": "JOB-001", "domain": "D_MKT_DATA",
         "maturity": "production", "build": "generated", "pit": "strict"},
        {"id": 2, "name": "signal.composite", "scope": "production", "contract": "CTR-002",
         "physical_type": "table", "produced_by": "JOB-002", "domain": "D_SIGLEGACY",
         "maturity": "production", "build": "generated", "pit": "strict"},
        {"id": 3, "name": "backtest.fills", "scope": "backtest_internal", "contract": None,
         "physical_type": "table", "produced_by": "JOB-003", "domain": "D_BACKTEST",
         "maturity": "production", "build": "generated", "pit": "strict"},
    ]


@pytest.fixture
def sample_jobs():
    """3 个运营态 Job。"""
    return [
        {"id": 10, "name": "ingest.ifind_kline", "scope": "production",
         "source": "src/zephyr/data/ingest.py", "trigger": "scheduled",
         "context": "production", "maturity": "production", "build": "generated"},
        {"id": 11, "name": "synthesize.signal", "scope": "production",
         "source": "src/zephyr/signal_ashare/synthesizer.py", "trigger": "event_driven",
         "context": "production", "maturity": "production", "build": "generated"},
        {"id": 12, "name": "backtest.replay_ticks", "scope": "backtest_internal",
         "source": "src/zephyr/backtest/tick_replay.py", "trigger": "manual",
         "context": "backtest_tick", "maturity": "production", "build": "generated"},
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
        {"id": 21, "name": "factor.ashare_alpha87", "scope": "production", "contract": None,
         "physical_type": "table", "produced_by": "JOB-021", "domain": "D_FACTOR",
         "maturity": "design", "build": "planned", "pit": "strict",
         "format_summary": "A股Alpha#87因子信号（多因子截面排名）"},
        {"id": 22, "name": "factor.ashare_capital_flow", "scope": "production", "contract": None,
         "physical_type": "table", "produced_by": "JOB-022", "domain": "D_FACTOR",
         "maturity": "design", "build": "planned", "pit": "strict",
         "format_summary": "A股资金流向因子（主力资金净流入/流出）"},
        {"id": 23, "name": "factor.ashare_fundamental", "scope": "production", "contract": None,
         "physical_type": "table", "produced_by": "JOB-023", "domain": "D_FACTOR",
         "maturity": "design", "build": "planned", "pit": "strict",
         "format_summary": "A股基本面因子（PE/PB/ROE/股息率等）"},
    ]


@pytest.fixture
def design_only_jobs():
    """3 个设计态 Job（含 description，名称未收录于 glossary，走回退提取中文）。"""
    return [
        {"id": 31, "name": "compute.ashare_alpha87", "scope": "production",
         "source": "src/zephyr/factor/ashare/alpha87.py", "trigger": "event_driven",
         "context": "production", "maturity": "design", "build": "planned",
         "description": "计算Alpha#87因子（消费OHLC K线，产出因子信号）"},
        {"id": 32, "name": "compute.ashare_capital_flow", "scope": "production",
         "source": "src/zephyr/factor/ashare/capital_flow.py", "trigger": "event_driven",
         "context": "production", "maturity": "design", "build": "planned",
         "description": "计算资金流因子（消费OHLC K线，产出因子信号）"},
        {"id": 33, "name": "compute.ashare_fundamental", "scope": "production",
         "source": "src/zephyr/factor/ashare/fundamental.py", "trigger": "event_driven",
         "context": "production", "maturity": "design", "build": "planned",
         "description": "计算基本面因子（消费OHLC K线，产出因子信号）"},
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
        """取"（"前的部分作为中文标签。"""
        assert _extract_zh_label("A股Alpha#87因子信号（多因子截面排名）") == "A股Alpha#87因子信号"

    def test_extract_before_ascii_paren(self):
        """支持半角"("分隔。"""
        assert _extract_zh_label("因子信号(multifactor)") == "因子信号"

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


# ---------- force_vertical 竖向布局测试 ----------

class TestForceVertical:
    """force_vertical 参数：设计态单向 push 边场景下用 ~~~ 不可见链接强制竖向。"""

    def test_force_vertical_adds_invisible_chain(
        self, design_only_datasets, design_only_jobs, design_only_edges
    ):
        """force_vertical=True 时添加 ~~~ 不可见链接串联相邻 JOB→DS 对。"""
        mmd, _, job_count, edge_count = _gen_mermaid(
            design_only_datasets, design_only_jobs, design_only_edges,
            maturity_filter="design", force_vertical=True,
        )
        # 3 个 job → 2 条不可见链（DS_of_job[0]~~~JOB[1], DS_of_job[1]~~~JOB[2]）
        assert "~~~" in mmd
        # 不可见链不计入 edge_count（仍为 3 条 produces 边）
        assert edge_count == 3
        assert job_count == 3
        # 链方向：DS21~~~JOB32, DS22~~~JOB33（前一个 DS → 下一个 JOB）
        assert "DS21 ~~~ JOB32" in mmd
        assert "DS22 ~~~ JOB33" in mmd

    def test_no_force_vertical_no_chain(
        self, design_only_datasets, design_only_jobs, design_only_edges
    ):
        """默认（force_vertical=False）不添加 ~~~ 不可见链接。"""
        mmd, _, _, _ = _gen_mermaid(
            design_only_datasets, design_only_jobs, design_only_edges,
            maturity_filter="design",
        )
        assert "~~~" not in mmd

    def test_force_vertical_single_job_no_chain(
        self, design_only_datasets, design_only_jobs, design_only_edges
    ):
        """仅 1 个 job 时无需串联（不添加 ~~~）。"""
        single_ds = [design_only_datasets[0]]
        single_job = [design_only_jobs[0]]
        single_edge = [design_only_edges[0]]
        mmd, _, _, _ = _gen_mermaid(
            single_ds, single_job, single_edge,
            maturity_filter="design", force_vertical=True,
        )
        assert "~~~" not in mmd

    def test_production_not_affected_by_vertical_flag(
        self, sample_datasets, sample_jobs, sample_edges
    ):
        """运营态文档（有交叉边）传 force_vertical=True 也不破坏已有边。"""
        mmd, _, _, edge_count = _gen_mermaid(
            sample_datasets, sample_jobs, sample_edges, force_vertical=True,
        )
        # 运营态有交叉边，force_vertical 会额外加 ~~~ 链，但 produces/consumed 边不变
        assert edge_count == 5
        assert "|produces / 产出|" in mmd
        assert "|consumed by / 被消费于|" in mmd


# ---------- 中文标签回退测试 ----------

class TestZhLabelFallback:
    """设计态节点中文标签回退：glossary 未收录时从 format_summary/description 提取。"""

    def test_design_dataset_label_has_zh_from_summary(
        self, design_only_datasets, design_only_jobs, design_only_edges
    ):
        """设计态 Dataset 节点标签含从 format_summary 提取的中文（<br/> 分隔）。"""
        mmd, _, _, _ = _gen_mermaid(
            design_only_datasets, design_only_jobs, design_only_edges,
            maturity_filter="design",
        )
        # DS21: factor.ashare_alpha87 → "A股Alpha#87因子信号"
        assert "factor.ashare_alpha87<br/>A股Alpha#87因子信号" in mmd
        # DS22: factor.ashare_capital_flow → "A股资金流向因子"
        assert "factor.ashare_capital_flow<br/>A股资金流向因子" in mmd

    def test_design_job_label_has_zh_from_description(
        self, design_only_datasets, design_only_jobs, design_only_edges
    ):
        """设计态 Job 节点标签含从 description 提取的中文（<br/> 分隔）。"""
        mmd, _, _, _ = _gen_mermaid(
            design_only_datasets, design_only_jobs, design_only_edges,
            maturity_filter="design",
        )
        # JOB31: compute.ashare_alpha87 → "计算Alpha#87因子"
        assert "compute.ashare_alpha87<br/>计算Alpha#87因子" in mmd

    def test_production_dataset_uses_glossary_not_summary(
        self, sample_datasets, sample_jobs, sample_edges
    ):
        """运营态 Dataset 优先用 glossary 短名（如"回测.模拟成交"），不走回退。"""
        mmd, _, _, _ = _gen_mermaid(sample_datasets, sample_jobs, sample_edges)
        # backtest.fills 在 glossary 中有映射 → 用短名，不用 format_summary
        assert "backtest.fills<br/>回测.模拟成交" in mmd


# ---------- _gen_domain_md 域职责测试 ----------

class TestGenDomainMd:
    """_gen_domain_md 域职责段落 + force_vertical 传递。"""

    def test_domain_md_contains_responsibility(
        self, design_only_datasets, design_only_jobs, design_only_edges
    ):
        """域文档包含"域职责 / Responsibility"段落。"""
        grp = {
            "key": "d_test", "title": "测试域（设计态）",
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

    def test_domain_md_mermaid_has_vertical_chain(
        self, design_only_datasets, design_only_jobs, design_only_edges
    ):
        """域文档内嵌 Mermaid 图含 ~~~ 竖向链（force_vertical=True 传递）。"""
        grp = {
            "key": "d_test", "title": "测试域（设计态）",
            "responsibility": "测试职责",
        }
        md = _gen_domain_md(grp, design_only_datasets, design_only_jobs, design_only_edges)
        assert "~~~" in md
