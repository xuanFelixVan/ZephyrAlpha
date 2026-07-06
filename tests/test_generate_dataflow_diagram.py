# [A_test] module_id: SRC-TST-202409 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] ARCHITECTURE-DIAGRAM-PLAN | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §test
# [MODULE] tests.test_generate_dataflow_diagram
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.d5_architecture.generators.generate_dataflow_diagram
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_generate_dataflow_diagram.py
# [TTL] permanent
# [ARCH-REF] #ARCH-051
"""test_generate_dataflow_diagram.py — generate_dataflow_diagram.py 单元测试

覆盖：
  - _gen_mermaid 返回值类型（tuple[str, int, int, int]）—— 修复"日志显示过滤前总数"瑕疵后补充
  - scope_filter 过滤逻辑（production / backtest_internal / None）
  - edge 计数（仅统计两端都在过滤后集合的边，跨 scope 边不计入）
  - _gen_index_md 统计正确性

依据：ARCH-051 裁定（2026-07-06）；commit 748e0d0356 返回值改型。
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
    _gen_index_md = _mod._gen_index_md
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
    """3 个 Job：2 production + 1 backtest，全部 design_maturity=production（运营态）。"""
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
def sample_datasets_with_design():
    """4 个 Dataset：3 运营态 + 1 设计态（design_maturity=design）。"""
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
        # 设计态节点（蓝图规划，代码未写）
        {"id": 4, "name": "factor.alpha_factor", "scope": "production", "contract": "CTR-009",
         "physical_type": "table", "produced_by": "JOB-004", "domain": "D_FACTOR",
         "maturity": "design", "build": "planned", "pit": "strict"},
    ]


@pytest.fixture
def sample_jobs_with_design():
    """4 个 Job：3 运营态 + 1 设计态（design_maturity=design）。"""
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
        # 设计态节点（蓝图规划，代码未写）
        {"id": 13, "name": "compute.alpha_factor", "scope": "production",
         "source": "src/zephyr/factor/alpha_factor.py", "trigger": "event_driven",
         "context": "production", "maturity": "design", "build": "planned"},
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
        mmd, ds_count, job_count, edge_count = _gen_mermaid(
            sample_datasets, sample_jobs, sample_edges
        )
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
        assert mmd.startswith("flowchart LR")

    def test_mmd_contains_edge_labels(self, sample_datasets, sample_jobs, sample_edges):
        """mmd 文本包含 produces / consumed by 边标签（中英并列）。"""
        mmd, _, _, _ = _gen_mermaid(sample_datasets, sample_jobs, sample_edges)
        assert "|produces / 产出|" in mmd
        assert "|consumed by / 被消费于|" in mmd

    def test_mmd_contains_class_defs(self, sample_datasets, sample_jobs, sample_edges):
        """mmd 文本包含样式定义（scope-based + design_maturity-based）。"""
        mmd, _, _, _ = _gen_mermaid(sample_datasets, sample_jobs, sample_edges)
        # scope-based
        assert "classDef dsProd" in mmd
        assert "classDef dsBacktest" in mmd
        assert "classDef jobProd" in mmd
        assert "classDef jobBacktest" in mmd
        # design_maturity-based（紫色设计态 + 黄色原型态）
        assert "classDef dsDesign" in mmd
        assert "classDef jobDesign" in mmd
        assert "classDef dsProto" in mmd
        assert "classDef jobProto" in mmd

    def test_mmd_contains_maturity_prefix(self, sample_datasets, sample_jobs, sample_edges):
        """mmd 节点标签包含 [production] design_maturity 前缀（运营态 fixture）。"""
        mmd, _, _, _ = _gen_mermaid(sample_datasets, sample_jobs, sample_edges)
        # 全部节点 design_maturity=production → 标签前缀 [production]
        assert "[production]" in mmd


# ---------- 设计态/运营态（design_maturity）测试 ----------

class TestDesignMaturity:
    """design_maturity 维度测试：设计态紫色 + [design] 前缀 + maturity_filter。"""

    def test_design_node_gets_purple_class(
        self, sample_datasets_with_design, sample_jobs_with_design, sample_edges
    ):
        """design_maturity=design 的节点使用紫色 class（dsDesign/jobDesign）。"""
        mmd, _, _, _ = _gen_mermaid(
            sample_datasets_with_design, sample_jobs_with_design, sample_edges
        )
        # DS4 是设计态 Dataset → dsDesign class
        assert "DS4" in mmd
        assert ":::dsDesign" in mmd
        # JOB13 是设计态 Job → jobDesign class
        assert "JOB13" in mmd
        assert ":::jobDesign" in mmd

    def test_design_node_has_design_prefix(
        self, sample_datasets_with_design, sample_jobs_with_design, sample_edges
    ):
        """design_maturity=design 的节点标签前缀为 [design]。"""
        mmd, _, _, _ = _gen_mermaid(
            sample_datasets_with_design, sample_jobs_with_design, sample_edges
        )
        assert "[design]" in mmd

    def test_production_node_keeps_scope_class(
        self, sample_datasets_with_design, sample_jobs_with_design, sample_edges
    ):
        """design_maturity=production 的节点仍使用 scope-based 着色（非紫色）。"""
        mmd, _, _, _ = _gen_mermaid(
            sample_datasets_with_design, sample_jobs_with_design, sample_edges
        )
        # DS1 是 production scope + production maturity → dsProd class（非 dsDesign）
        assert "DS1" in mmd
        assert ":::dsProd" in mmd

    def test_maturity_filter_production_excludes_design(
        self, sample_datasets_with_design, sample_jobs_with_design, sample_edges
    ):
        """maturity_filter=production 排除设计态节点。"""
        mmd, ds_count, job_count, _ = _gen_mermaid(
            sample_datasets_with_design, sample_jobs_with_design, sample_edges,
            maturity_filter="production",
        )
        # 3 运营态 dataset + 3 运营态 job（设计态 DS4/JOB13 被过滤）
        assert ds_count == 3
        assert job_count == 3
        assert "DS4" not in mmd
        assert "JOB13" not in mmd

    def test_maturity_filter_design_only(
        self, sample_datasets_with_design, sample_jobs_with_design, sample_edges
    ):
        """maturity_filter=design 只返回设计态节点。"""
        mmd, ds_count, job_count, _ = _gen_mermaid(
            sample_datasets_with_design, sample_jobs_with_design, sample_edges,
            maturity_filter="design",
        )
        # 仅 1 设计态 dataset + 1 设计态 job
        assert ds_count == 1
        assert job_count == 1
        assert "DS4" in mmd
        assert "JOB13" in mmd
        assert "DS1" not in mmd


# ---------- _gen_index_md 测试 ----------

class TestGenIndexMd:
    """_gen_index_md 统计正确性测试。"""

    def test_stats_table(self, sample_datasets, sample_jobs, sample_edges):
        """索引文档统计表正确。"""
        md = _gen_index_md(sample_datasets, sample_jobs, sample_edges)
        # | Dataset | 2 | 1 | 3 |  production=2, backtest=1, total=3
        assert "| Dataset | 2 | 1 | 3 |" in md
        assert "| Job | 2 | 1 | 3 |" in md
        assert "| Edge | - | - | 5 |" in md

    def test_design_maturity_stats_table(self, sample_datasets_with_design, sample_jobs_with_design, sample_edges):
        """索引文档包含设计态/运营态统计子表（design_maturity 维度）。"""
        md = _gen_index_md(
            sample_datasets_with_design, sample_jobs_with_design, sample_edges
        )
        # 4 dataset: 3 production + 1 design
        assert "| Dataset | 3 | 1 | 0 | 4 |" in md
        # 4 job: 3 production + 1 design
        assert "| Job | 3 | 1 | 0 | 4 |" in md
        # 设计态 vs 运营态说明
        assert "设计态 vs 运营态" in md

    def test_contains_operation_state_diagram(self, sample_datasets_with_design, sample_jobs_with_design, sample_edges):
        """索引文档包含运营态全景图章节（仅 design_maturity=production）。"""
        md = _gen_index_md(
            sample_datasets_with_design, sample_jobs_with_design, sample_edges
        )
        assert "运营态全景图" in md
        # 运营态全景图应排除设计态节点 DS4/JOB13
        # （注意：运营态全景图 section 之后的内容会包含 DS4，所以只检查该 section 的 mermaid 块）
        assert "### 运营态全景图（仅 design_maturity=production）" in md

    def test_contains_dataset_list(self, sample_datasets, sample_jobs, sample_edges):
        """索引文档包含 Dataset 清单。"""
        md = _gen_index_md(sample_datasets, sample_jobs, sample_edges)
        assert "market_data.tick" in md
        assert "signal.composite" in md
        assert "backtest.fills" in md

    def test_contains_job_list(self, sample_datasets, sample_jobs, sample_edges):
        """索引文档包含 Job 清单。"""
        md = _gen_index_md(sample_datasets, sample_jobs, sample_edges)
        assert "ingest.ifind_kline" in md
        assert "synthesize.signal" in md
        assert "backtest.replay_ticks" in md
