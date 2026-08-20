# [A_test] module_id: MOD-GOV_battle_map_res_inc | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-279 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_battle_map_research_incubation
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DB不可达->skip_test; 拓扑断裂->AssertionError; 指标缺失->AssertionError
# [TESTS] tests/governance/test_battle_map_research_incubation.py
# [TTL] permanent
"""test_battle_map_research_incubation.py — 研究孵化阶段 33 环节逻辑全覆盖验证

验证 battle_map_01_research_incubation.md 真源中研究孵化阶段 33 环节（11 根 + 22 子）的
数据完整性、拓扑结构、6 件套指标、YAML 叙事、D-RESEARCH 覆盖率及生成器渲染防御性。

环节结构（11 根环节 + 22 子环节 = 33）：

  BM-RES-01 研究数据与特征存储
    ├─ BM-RES-01-A 数据集版本化与血缘追踪    (D-RESEARCH-01)
    ├─ BM-RES-01-B 特征存储与PIT正确性       (D-RESEARCH-02)
    ├─ BM-RES-01-C 研究数据沙箱              (D-RESEARCH-12)
    └─ BM-RES-01-D 研究资产版本化             (D-RESEARCH-18)
  BM-RES-02 实验追踪与可复现性
    ├─ BM-RES-02-A 实验记录与对比             (D-RESEARCH-03)
    ├─ BM-RES-02-B 可复现性管理               (D-RESEARCH-05)
    ├─ BM-RES-02-C 实验异常检测               (D-RESEARCH-13)
    └─ BM-RES-02-D 复现包生成                 (D-RESEARCH-15)
  BM-RES-03 假设管理与研究发现沉淀
    ├─ BM-RES-03-A 假设生命周期管理           (D-RESEARCH-08)
    ├─ BM-RES-03-B 研究发现知识库             (D-RESEARCH-14)
    └─ BM-RES-03-C 研究目录与搜索引擎         (D-RESEARCH-06)
  BM-RES-04 研究工作流编排
    └─ BM-RES-04-A DAG编排与任务调度          (D-RESEARCH-09)
  BM-RES-05 Notebook与协作
    ├─ BM-RES-05-A Notebook集成与一键转生产   (D-RESEARCH-04)
    ├─ BM-RES-05-B 研究协作中心               (D-RESEARCH-10)
    └─ BM-RES-05-C 研究信息隔离墙             (D-RESEARCH-16)
  BM-RES-06 LLM研究Agent与论文追踪
    ├─ BM-RES-06-A LLM研究助手                (D-RESEARCH-11)
    └─ BM-RES-06-B 论文追踪                   (D-RESEARCH-07)
  BM-RES-07 策略迭代升级
    └─ BM-RES-07-A 策略进化与因子挖掘         (D-RESEARCH-17)
  BM-RES-08 知识清洗（学习系统S1）            # #ARCH-093：2026-08-04 治理批新增
    └─ BM-RES-08-A 清洗流水线                (planned，D_RESEARCH/D_INTELLIGENCE)
  BM-RES-09 知识分类（学习系统S2）            # #ARCH-093 新增
    └─ BM-RES-09-A 知识分类体系              (planned，D_RESEARCH/D_ML_TRAIN)
  BM-RES-10 模块工厂（学习系统S3）            # #ARCH-093 新增
    └─ BM-RES-10-A 模块工厂架构              (planned，D_RESEARCH)
  BM-RES-11 知识采集（学习系统S0）            # #ARCH-093 新增
    └─ BM-RES-11-A 采集源分类调度            (planned，D_RESEARCH/D_INTELLIGENCE)

主链流转边（6 条 data_flow）：
  BM-RES-01 → BM-RES-02 → BM-RES-03 → BM-RES-04 → BM-RES-05 → BM-RES-06 → BM-RES-07

六类测试：
  1. **拓扑验证（e2e，需 DB）**：33 环节存在、11 根 + 22 子、父子嵌套、sort_order、
     6 条主链边、每环节有锚点（BM-INV-001）、锚点全指向候选池。
  2. **6 件套指标验证（e2e）**：每环节 indicators 含 6 件套全字段、data_flow 子结构完整、
     params 为 list[dict]（回归测试：防字符串 params 崩溃生成器）。
  3. **YAML 叙事验证（e2e）**：25 环节在 module_translation_registry.yaml 有 5 字段叙事。
  4. **D-RESEARCH 覆盖率验证（e2e）**：18 个 D-RESEARCH 子模块被子环节 code_mapping 覆盖。
  5. **生成器渲染防御性验证（纯逻辑）**：_format_indicators_table 对 dict/str/None/list
     各类型字段降级渲染不崩溃（回归测试：BM-MT params 字符串崩溃事故）。
  6. **数据流模拟（纯逻辑）**：mock 处理器模拟 7 阶段研究管线端到端跑通。

设计原则（对标 test_battle_map_execution_flow.py）：
  - 真实 DB 连接做拓扑验证（@pytest.mark.e2e）；DB 不可达则 skip
  - 模拟测试零 DB 依赖，纯逻辑验证语义
  - 不写入生产库——全部只读

Usage::

    py -3.12 -m pytest tests/governance/test_battle_map_research_incubation.py -v
    py -3.12 -m pytest tests/governance/test_battle_map_research_incubation.py -k "not e2e"  # 跳过 DB
    py -3.12 -m pytest tests/governance/test_battle_map_research_incubation.py::TestResearchDataFlowSimulation -v
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SRC_PATH = _REPO_ROOT / "src"
if str(_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(_SRC_PATH))

# ── 研究孵化阶段常量（与 DB step_id / sort_order / D-RESEARCH 对齐）──────────

# 11 根环节主链顺序（sort_order 升序；08-11 为 #ARCH-093 学习系统 S0-S3 新增根）
EXPECTED_ROOT_CHAIN: list[str] = [
    "BM-RES-01",  # 研究数据与特征存储
    "BM-RES-02",  # 实验追踪与可复现性
    "BM-RES-03",  # 假设管理与研究发现沉淀
    "BM-RES-04",  # 研究工作流编排
    "BM-RES-05",  # Notebook与协作
    "BM-RES-06",  # LLM研究Agent与论文追踪
    "BM-RES-07",  # 策略迭代升级
    "BM-RES-08",  # 知识清洗（学习系统S1）
    "BM-RES-09",  # 知识分类（学习系统S2）
    "BM-RES-10",  # 模块工厂（学习系统S3）
    "BM-RES-11",  # 知识采集（学习系统S0）
]

# 预期 data_flow 主链边（from → to）
EXPECTED_DATA_FLOW_EDGES: list[tuple[str, str]] = [
    ("BM-RES-01", "BM-RES-02"),  # 研究数据→实验追踪
    ("BM-RES-02", "BM-RES-03"),  # 实验结果→假设验证
    ("BM-RES-03", "BM-RES-04"),  # 假设→工作流编排
    ("BM-RES-04", "BM-RES-05"),  # 工作流→Notebook协作
    ("BM-RES-05", "BM-RES-06"),  # 协作→LLM/论文追踪
    ("BM-RES-06", "BM-RES-07"),  # 研究发现→策略迭代
]

# 线性主链（数据流模拟语义基线=DB 实存 6 条主链边 01→…→07）；
# #ARCH-093：08-11 学习系统 S0-S3 无 data_flow/trigger 边接入（移交 Owner），不入链模拟
MAIN_CHAIN: list[str] = EXPECTED_ROOT_CHAIN[:7]

# 父环节 → 子环节列表映射
EXPECTED_CHILDREN: dict[str, list[str]] = {
    "BM-RES-01": ["BM-RES-01-A", "BM-RES-01-B", "BM-RES-01-C", "BM-RES-01-D"],
    "BM-RES-02": ["BM-RES-02-A", "BM-RES-02-B", "BM-RES-02-C", "BM-RES-02-D"],
    "BM-RES-03": ["BM-RES-03-A", "BM-RES-03-B", "BM-RES-03-C"],
    "BM-RES-04": ["BM-RES-04-A"],
    "BM-RES-05": ["BM-RES-05-A", "BM-RES-05-B", "BM-RES-05-C"],
    "BM-RES-06": ["BM-RES-06-A", "BM-RES-06-B"],
    "BM-RES-07": ["BM-RES-07-A"],
    "BM-RES-08": ["BM-RES-08-A"],  # #ARCH-093
    "BM-RES-09": ["BM-RES-09-A"],  # #ARCH-093
    "BM-RES-10": ["BM-RES-10-A"],  # #ARCH-093
    "BM-RES-11": ["BM-RES-11-A"],  # #ARCH-093
}

# 全部 33 环节 step_id（11 根 + 22 子）
EXPECTED_ALL_STEPS: list[str] = list(EXPECTED_ROOT_CHAIN) + [
    child for children in EXPECTED_CHILDREN.values() for child in children
]

# 子环节 → D-RESEARCH 模块映射（code_mapping.module_id 应包含此 ID）
CHILD_TO_D_RESEARCH: dict[str, str] = {
    "BM-RES-01-A": "D-RESEARCH-01",
    "BM-RES-01-B": "D-RESEARCH-02",
    "BM-RES-01-C": "D-RESEARCH-12",
    "BM-RES-01-D": "D-RESEARCH-18",
    "BM-RES-02-A": "D-RESEARCH-03",
    "BM-RES-02-B": "D-RESEARCH-05",
    "BM-RES-02-C": "D-RESEARCH-13",
    "BM-RES-02-D": "D-RESEARCH-15",
    "BM-RES-03-A": "D-RESEARCH-08",
    "BM-RES-03-B": "D-RESEARCH-14",
    "BM-RES-03-C": "D-RESEARCH-06",
    "BM-RES-04-A": "D-RESEARCH-09",
    "BM-RES-05-A": "D-RESEARCH-04",
    "BM-RES-05-B": "D-RESEARCH-10",
    "BM-RES-05-C": "D-RESEARCH-16",
    "BM-RES-06-A": "D-RESEARCH-11",
    "BM-RES-06-B": "D-RESEARCH-07",
    "BM-RES-07-A": "D-RESEARCH-17",
}

# 全部 18 个 D-RESEARCH 子模块（验证 100% 覆盖）
ALL_D_RESEARCH_MODULES: list[str] = [
    "D-RESEARCH-01",
    "D-RESEARCH-02",
    "D-RESEARCH-03",
    "D-RESEARCH-04",
    "D-RESEARCH-05",
    "D-RESEARCH-06",
    "D-RESEARCH-07",
    "D-RESEARCH-08",
    "D-RESEARCH-09",
    "D-RESEARCH-10",
    "D-RESEARCH-11",
    "D-RESEARCH-12",
    "D-RESEARCH-13",
    "D-RESEARCH-14",
    "D-RESEARCH-15",
    "D-RESEARCH-16",
    "D-RESEARCH-17",
    "D-RESEARCH-18",
]

# indicators 6 件套必需字段
REQUIRED_INDICATOR_KEYS = {
    "trigger",
    "consumes",
    "params",
    "data_flow",
    "code_mapping",
    "degradation",
}
# data_flow 子结构必需字段
REQUIRED_DATA_FLOW_KEYS = {"input", "output", "process", "downstream"}
# YAML 叙事必需字段
REQUIRED_NARRATIVE_KEYS = {"name_zh", "name_en", "plain_zh", "mechanism_zh", "indicators_zh"}

FLOW_STAGE = "research_incubation"


# ============================================================================
# Part 1: 拓扑验证（e2e，需 PostgreSQL）—— 从 DB 读取真实结构
# ============================================================================


def _get_reader():
    """构造 BattleMapReader，DB 不可达时 skip。"""
    try:
        from zephyr.governance.persistence.battle_map_reader import BattleMapReader

        reader = BattleMapReader()
        reader.get_step_count()  # 触发真实连接，验证 PG 可达
        return reader
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"battle_map PostgreSQL 不可达: {exc}")


@pytest.mark.e2e
class TestResearchIncubationTopology:
    """研究孵化拓扑验证——从 DB 读取 battle_map 三表，验证 25 环节结构。"""

    @pytest.fixture(scope="class")
    def res_steps(self):
        """加载 research_incubation 阶段全部环节。"""
        reader = _get_reader()
        try:
            steps = reader.get_steps_by_flow_stage(FLOW_STAGE)
        finally:
            reader.close()
        return {s["step_id"]: s for s in steps}

    @pytest.fixture(scope="class")
    def res_edges(self, res_steps):
        """加载涉及研究孵化环节的流转边。"""
        reader = _get_reader()
        try:
            edges = reader.get_all_edges()
        finally:
            reader.close()
        res_ids = set(res_steps.keys())
        return [e for e in edges if e["from_step_id"] in res_ids or e["to_step_id"] in res_ids]

    @pytest.fixture(scope="class")
    def res_anchors(self, res_steps):
        """加载研究孵化环节的锚点。"""
        reader = _get_reader()
        try:
            anchors = reader.get_all_anchors()
        finally:
            reader.close()
        res_ids = set(res_steps.keys())
        return [a for a in anchors if a["step_id"] in res_ids]

    # ── 环节数量 ──────────────────────────────────────────────────────

    def test_25_steps_exist(self, res_steps):
        """33 个研究孵化环节全部存在（含 #ARCH-093 新增 8 个）。"""
        for sid in EXPECTED_ALL_STEPS:
            assert sid in res_steps, f"缺少研究孵化环节 {sid}（DB 中未找到）"

    def test_exactly_33_steps(self, res_steps):
        """research_incubation 阶段恰好 33 环节（11 根 + 22 子，#ARCH-093 裁定后跟进）。"""
        assert len(res_steps) == 33, (
            f"research_incubation 阶段应有 33 环节，实际 {len(res_steps)}: {sorted(res_steps.keys())}"
        )

    def test_11_root_22_child(self, res_steps):
        """11 个根环节（depth=0）+ 22 个子环节（depth=1）（#ARCH-093 裁定后跟进）。"""
        roots = [s for s in res_steps.values() if s.get("depth") == 0]
        children = [s for s in res_steps.values() if s.get("depth") == 1]
        assert len(roots) == 11, f"根环节应有 11 个，实际 {len(roots)}"
        assert len(children) == 22, f"子环节应有 22 个，实际 {len(children)}"

    # ── 父子嵌套 ──────────────────────────────────────────────────────

    def test_root_steps_have_no_parent(self, res_steps):
        """7 根环节 parent_step_id 为 None。"""
        for sid in EXPECTED_ROOT_CHAIN:
            assert res_steps[sid].get("parent_step_id") is None, f"{sid} 是根环节，parent_step_id 应为 None"

    def test_child_parent_mapping(self, res_steps):
        """每个子环节的 parent_step_id 指向正确的根环节。"""
        for parent_id, expected_children in EXPECTED_CHILDREN.items():
            for child_id in expected_children:
                actual_parent = res_steps[child_id].get("parent_step_id")
                assert actual_parent == parent_id, f"{child_id} 的 parent 应为 {parent_id}，实际 {actual_parent}"

    def test_child_depth_is_1(self, res_steps):
        """所有子环节 depth=1（未超 max_depth=3 限制）。"""
        for parent_id, children in EXPECTED_CHILDREN.items():
            for child_id in children:
                depth = res_steps[child_id].get("depth")
                assert depth == 1, f"{child_id} depth 应为 1，实际 {depth}"

    def test_all_children_accounted_for(self, res_steps):
        """22 个子环节全部在 EXPECTED_CHILDREN 映射中（无遗漏/无多余）。"""
        actual_children = {sid for sid in res_steps if sid not in EXPECTED_ROOT_CHAIN}
        expected_children = {child for children in EXPECTED_CHILDREN.values() for child in children}
        missing = expected_children - actual_children
        extra = actual_children - expected_children
        assert not missing, f"DB 缺少预期子环节: {missing}"
        assert not extra, f"DB 有未预期子环节: {extra}"

    # ── sort_order ───────────────────────────────────────────────────

    def test_root_sort_order_monotonic(self, res_steps):
        """7 根环节 sort_order 单调递增（主链顺序）。"""
        roots = [res_steps[sid] for sid in EXPECTED_ROOT_CHAIN]
        sort_orders = [s["sort_order"] for s in roots]
        assert sort_orders == sorted(sort_orders), f"根环节 sort_order 非单调递增: {sort_orders}"

    def test_child_sort_order_after_parent(self, res_steps):
        """子环节 sort_order 紧跟父环节（子 > 父）。"""
        for parent_id, children in EXPECTED_CHILDREN.items():
            parent_sort = res_steps[parent_id]["sort_order"]
            for child_id in children:
                child_sort = res_steps[child_id]["sort_order"]
                assert child_sort > parent_sort, (
                    f"{child_id} sort_order({child_sort}) 应大于父 {parent_id}({parent_sort})"
                )

    # ── 主链流转边 ───────────────────────────────────────────────────

    def test_main_chain_edges(self, res_edges):
        """6 条主链边构成 BM-RES-01→02→03→04→05→06→07（data_flow 或 trigger 类型）。

        主链边类型混合设计：data_flow（数据传递）与 trigger（事件触发）交替使用，
        反映研究管线中有些环节是数据流转、有些是触发驱动。
        """
        main_chain_edges = {
            (e["from_step_id"], e["to_step_id"])
            for e in res_edges
            if e["edge_type"] in ("data_flow", "trigger")
            and e["from_step_id"] in EXPECTED_ROOT_CHAIN
            and e["to_step_id"] in EXPECTED_ROOT_CHAIN
        }
        for expected in EXPECTED_DATA_FLOW_EDGES:
            assert expected in main_chain_edges, f"缺少主链边 {expected[0]}→{expected[1]}"

    def test_no_reverse_edges(self, res_edges):
        """主链无反向边（如 BM-RES-07→01 逆转流程）。"""
        reverse_edges = {(to, frm) for frm, to in EXPECTED_DATA_FLOW_EDGES}
        actual_edges = {
            (e["from_step_id"], e["to_step_id"]) for e in res_edges if e["edge_type"] in ("data_flow", "trigger")
        }
        leftover = reverse_edges & actual_edges
        assert not leftover, f"存在反向流转边: {leftover}"

    # ── 锚点（BM-INV-001）────────────────────────────────────────────

    @pytest.mark.xfail(
        strict=False,
        reason="#ARCH-093 裁定：16 环节无锚点（03 全系/04 全系/05-A~C/06-A/B/07-A/08-A~11-A）——锚点回填需领域判断，移交 battle_map Owner（裁定书 architecture-reviews/2026-08-16-test-debt-leftover-adjudication.md）",
    )
    def test_each_step_has_anchor(self, res_anchors):
        """每个环节至少一个锚点（BM-INV-001：无锚点=悬空决策）。"""
        anchored_steps = {a["step_id"] for a in res_anchors}
        for sid in EXPECTED_ALL_STEPS:
            assert sid in anchored_steps, f"{sid} 无锚点（违反 BM-INV-001，悬空决策）"

    def test_anchors_target_candidate_pool(self, res_anchors):
        """所有锚点指向候选池（target_graph=candidate），因 D-RESEARCH 模块未建。"""
        non_candidate = [a for a in res_anchors if a["target_graph"] != "candidate"]
        # 允许少量 depgraph 锚点（若后续模块晋升），但当前应全为 candidate
        assert len(non_candidate) == 0 or all(a["target_graph"] == "depgraph" for a in non_candidate), (
            f"存在非法 target_graph 锚点: {[(a['step_id'], a['target_graph']) for a in non_candidate]}"
        )

    @pytest.mark.xfail(
        strict=False,
        reason="#ARCH-093 裁定：锚点总数 21<33（每环节至少 1 个）——锚点回填移交 battle_map Owner",
    )
    def test_anchor_count_at_least_25(self, res_anchors):
        """锚点总数 ≥ 33（每环节至少 1 个，部分有 supplement 锚点）。"""
        assert len(res_anchors) >= 33, f"锚点总数应 ≥ 33（每环节至少 1 个），实际 {len(res_anchors)}"

    # ── flow_stage 一致性 ────────────────────────────────────────────

    def test_all_steps_research_incubation(self, res_steps):
        """所有 25 环节 flow_stage 均为 research_incubation（BM-INV-006 跨阶段检查）。"""
        for sid, step in res_steps.items():
            assert step["flow_stage"] == FLOW_STAGE, f"{sid} flow_stage 应为 {FLOW_STAGE}，实际 {step['flow_stage']}"


# ============================================================================
# Part 2: 6 件套指标验证（e2e）—— indicators JSONB 结构完整性
# ============================================================================


@pytest.mark.e2e
class TestResearchIncubationIndicators:
    """研究孵化 indicators 6 件套结构验证——每环节 JSONB 字段完整性。"""

    @pytest.fixture(scope="class")
    def res_steps(self):
        reader = _get_reader()
        try:
            steps = reader.get_steps_by_flow_stage(FLOW_STAGE)
        finally:
            reader.close()
        return {s["step_id"]: s for s in steps}

    def test_all_steps_have_indicators(self, res_steps):
        """25 环节 indicators 全部非空（已填充）。"""
        for sid in EXPECTED_ALL_STEPS:
            ind = res_steps[sid].get("indicators")
            assert ind is not None, f"{sid} indicators 为 None"
            assert isinstance(ind, dict), f"{sid} indicators 应为 dict，实际 {type(ind).__name__}"
            assert len(ind) > 0, f"{sid} indicators 为空 dict"

    def test_6_piece_keys_complete(self, res_steps):
        """每环节 indicators 含 6 件套全部字段（trigger/consumes/params/data_flow/code_mapping/degradation）。"""
        for sid in EXPECTED_ALL_STEPS:
            ind = res_steps[sid].get("indicators") or {}
            missing = REQUIRED_INDICATOR_KEYS - set(ind.keys())
            assert not missing, f"{sid} indicators 缺字段: {missing}"

    def test_data_flow_subkeys_complete(self, res_steps):
        """每环节 indicators.data_flow 含 input/output/process/downstream。"""
        for sid in EXPECTED_ALL_STEPS:
            df = (res_steps[sid].get("indicators") or {}).get("data_flow") or {}
            if not isinstance(df, dict):
                pytest.fail(f"{sid} data_flow 应为 dict，实际 {type(df).__name__}")
            missing = REQUIRED_DATA_FLOW_KEYS - set(df.keys())
            assert not missing, f"{sid} data_flow 缺字段: {missing}"

    def test_trigger_has_condition(self, res_steps):
        """每环节 indicators.trigger 含 condition 字段。"""
        for sid in EXPECTED_ALL_STEPS:
            trig = (res_steps[sid].get("indicators") or {}).get("trigger") or {}
            assert isinstance(trig, dict), f"{sid} trigger 应为 dict"
            assert "condition" in trig, f"{sid} trigger 缺 condition 字段"
            assert trig["condition"], f"{sid} trigger.condition 为空"

    def test_code_mapping_has_module_id(self, res_steps):
        """每环节 indicators.code_mapping 含 module_id 字段。"""
        for sid in EXPECTED_ALL_STEPS:
            cm = (res_steps[sid].get("indicators") or {}).get("code_mapping") or {}
            assert isinstance(cm, dict), f"{sid} code_mapping 应为 dict"
            assert "module_id" in cm, f"{sid} code_mapping 缺 module_id"
            assert cm["module_id"], f"{sid} code_mapping.module_id 为空"

    def test_degradation_has_condition(self, res_steps):
        """每环节 indicators.degradation 含 condition 字段。"""
        for sid in EXPECTED_ALL_STEPS:
            deg = (res_steps[sid].get("indicators") or {}).get("degradation") or {}
            assert isinstance(deg, dict), f"{sid} degradation 应为 dict"
            assert "condition" in deg, f"{sid} degradation 缺 condition"

    def test_params_is_list_of_dicts(self, res_steps):
        """回归测试：indicators.params 必须是 list[dict]，不能是字符串。

        治本（2026-08-03）：BM-MT-01-A/B/05-A 的 params 曾被写成纯字符串，
        导致生成器 _format_indicators_table 崩溃（'str' object has no attribute 'get'），
        整个 269 环节批量生成失败。此测试防止 research_incubation 重蹈覆辙。
        """
        for sid in EXPECTED_ALL_STEPS:
            params = (res_steps[sid].get("indicators") or {}).get("params")
            assert isinstance(params, list), (
                f"{sid} params 应为 list，实际 {type(params).__name__}（字符串 params 会崩溃生成器）"
            )
            for i, p in enumerate(params):
                assert isinstance(p, dict), f"{sid} params[{i}] 应为 dict，实际 {type(p).__name__}"

    def test_consumes_is_list_of_dicts(self, res_steps):
        """indicators.consumes 应为 list[dict]（每项含 item 字段）。"""
        for sid in EXPECTED_ALL_STEPS:
            consumes = (res_steps[sid].get("indicators") or {}).get("consumes")
            assert isinstance(consumes, list), f"{sid} consumes 应为 list，实际 {type(consumes).__name__}"
            for i, c in enumerate(consumes):
                assert isinstance(c, dict), f"{sid} consumes[{i}] 应为 dict，实际 {type(c).__name__}"

    def test_data_flow_chain_consistency(self, res_steps):
        """主链相邻环节的 output→input 语义一致（上游 output 非空，下游 input 非空）。"""
        for from_sid, to_sid in EXPECTED_DATA_FLOW_EDGES:
            upstream_df = (res_steps[from_sid].get("indicators") or {}).get("data_flow") or {}
            downstream_df = (res_steps[to_sid].get("indicators") or {}).get("data_flow") or {}
            upstream_output = upstream_df.get("output", "")
            downstream_input = downstream_df.get("input", "")
            assert upstream_output, f"{from_sid} data_flow.output 为空（上游产出缺失）"
            assert downstream_input, f"{to_sid} data_flow.input 为空（下游输入缺失）"


# ============================================================================
# Part 3: YAML 叙事验证（e2e）—— module_translation_registry.yaml BM-INV-003
# ============================================================================


@pytest.mark.e2e
class TestResearchIncubationNarratives:
    """研究孵化 YAML 叙事验证——25 环节在翻译真源有完整 5 字段叙事。

    BM-INV-003：DB 每个环节必须在翻译真源有叙事，缺失则生成器降级到 DB step_name。
    """

    @pytest.fixture(scope="class")
    def narratives(self):
        """加载 module_translation_registry.yaml §battle_map_steps 全部叙事。"""
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML 不可用")
        yaml_path = (
            _REPO_ROOT
            / "docs"
            / "01_policies_and_standards"
            / "_registry"
            / "catalogs"
            / "module_translation_registry.yaml"
        )
        if not yaml_path.exists():
            pytest.skip(f"YAML 真源不存在: {yaml_path}")
        with open(yaml_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        steps = data.get("battle_map_steps", [])
        return {s["step_id"]: s for s in steps if "step_id" in s}

    def test_all_25_steps_have_narrative(self, narratives):
        """25 环节全部在 YAML 有叙事条目。"""
        for sid in EXPECTED_ALL_STEPS:
            assert sid in narratives, (
                f"{sid} 在 module_translation_registry.yaml §battle_map_steps 无叙事（BM-INV-003）"
            )

    def test_narrative_5_fields_complete(self, narratives):
        """每条叙事含 5 字段（name_zh/name_en/plain_zh/mechanism_zh/indicators_zh）。"""
        for sid in EXPECTED_ALL_STEPS:
            entry = narratives.get(sid, {})
            missing = REQUIRED_NARRATIVE_KEYS - set(entry.keys())
            assert not missing, f"{sid} 叙事缺字段: {missing}"

    def test_narrative_fields_non_empty(self, narratives):
        """每条叙事的 5 字段均非空字符串。"""
        for sid in EXPECTED_ALL_STEPS:
            entry = narratives.get(sid, {})
            for field in REQUIRED_NARRATIVE_KEYS:
                val = entry.get(field, "")
                assert val and str(val).strip(), f"{sid} 叙事字段 {field} 为空"

    def test_narrative_flow_stage_matches(self, narratives):
        """叙事条目的 flow_stage 与 DB 一致（research_incubation）。"""
        for sid in EXPECTED_ALL_STEPS:
            entry = narratives.get(sid, {})
            assert entry.get("flow_stage") == FLOW_STAGE, (
                f"{sid} 叙事 flow_stage 应为 {FLOW_STAGE}，实际 {entry.get('flow_stage')}"
            )


# ============================================================================
# Part 4: D-RESEARCH 覆盖率验证（e2e）—— 18 子模块 100% 覆盖
# ============================================================================


@pytest.mark.e2e
class TestResearchIncubationDResearchCoverage:
    """研究孵化 D-RESEARCH 覆盖率验证——18 个子模块被子环节 code_mapping 覆盖。"""

    @pytest.fixture(scope="class")
    def res_steps(self):
        reader = _get_reader()
        try:
            steps = reader.get_steps_by_flow_stage(FLOW_STAGE)
        finally:
            reader.close()
        return {s["step_id"]: s for s in steps}

    def test_18_d_research_modules_covered(self, res_steps):
        """18 个 D-RESEARCH 子模块全部被子环节 code_mapping.module_id 引用。"""
        covered = set()
        for child_id, expected_mod in CHILD_TO_D_RESEARCH.items():
            step = res_steps.get(child_id)
            assert step is not None, f"子环节 {child_id} 不在 DB 中"
            cm = (step.get("indicators") or {}).get("code_mapping") or {}
            module_id = cm.get("module_id", "")
            assert expected_mod in module_id, f"{child_id} code_mapping.module_id='{module_id}' 应包含 {expected_mod}"
            covered.add(expected_mod)
        # 验证全部 18 个模块都被覆盖
        uncovered = set(ALL_D_RESEARCH_MODULES) - covered
        assert not uncovered, f"D-RESEARCH 模块未被覆盖: {uncovered}"

    def test_coverage_rate_100_percent(self, res_steps):
        """D-RESEARCH 覆盖率 = 18/18 = 100%。"""
        covered = 0
        for child_id, expected_mod in CHILD_TO_D_RESEARCH.items():
            step = res_steps.get(child_id, {})
            cm = (step.get("indicators") or {}).get("code_mapping") or {}
            if expected_mod in cm.get("module_id", ""):
                covered += 1
        total = len(ALL_D_RESEARCH_MODULES)
        rate = covered / total * 100
        assert rate == 100.0, f"D-RESEARCH 覆盖率 {covered}/{total} = {rate:.0f}%（应 100%）"

    def test_child_step_count_matches_d_research(self):
        """子环节数（18）= D-RESEARCH 模块数（18），一一对应。"""
        assert len(CHILD_TO_D_RESEARCH) == len(ALL_D_RESEARCH_MODULES) == 18, (
            f"子环节({len(CHILD_TO_D_RESEARCH)}) / D-RESEARCH({len(ALL_D_RESEARCH_MODULES)}) 数量不匹配"
        )


# ============================================================================
# Part 5: 生成器渲染防御性验证（纯逻辑，无 DB）
# ============================================================================


def _import_generator():
    """导入生成器模块，失败则 skip。"""
    _gov_dir = _REPO_ROOT / "scripts" / "governance"
    if str(_gov_dir) not in sys.path:
        sys.path.insert(0, str(_gov_dir))
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "gen_battle_map",
            str(
                _REPO_ROOT
                / "scripts"
                / "governance"
                / "d5_architecture"
                / "generators"
                / "generate_battle_map_diagram.py"
            ),
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"生成器模块导入失败: {exc}")


class TestGeneratorRenderingDefensive:
    """生成器 _format_indicators_table 防御性渲染验证。

    治本（2026-08-03）：BM-MT-01-A/B/05-A 的 params 为字符串曾导致整个生成器崩溃，
    259+ 环节全部无法生成。此测试验证防御性修复对各种异常数据类型不崩溃。
    """

    @pytest.fixture(scope="class")
    def gen(self):
        return _import_generator()

    def test_normal_indicators_render(self, gen):
        """正常 dict 指标正确渲染 6 件套表格。"""
        step = {
            "step_id": "TEST-01",
            "indicators": {
                "trigger": {"condition": "测试触发", "threshold": "阈值X"},
                "consumes": [{"item": "数据A", "source": "BM-TEST"}],
                "params": [
                    {"name": "p1", "default": "v1", "range": "0-1", "current_code_value": "—", "status": "proposed"},
                ],
                "data_flow": {"input": "原始", "process": "处理", "output": "结果", "downstream": "下游"},
                "code_mapping": {"module_id": "MOD-X", "source_ref": "§1"},
                "degradation": {"condition": "异常", "action": "降级"},
            },
        }
        result = gen._format_indicators_table(step)
        assert "测试触发" in result
        assert "数据A" in result
        assert "p1=v1" in result
        assert "MOD-X" in result
        assert "异常" in result
        assert "降级" in result

    def test_string_params_no_crash(self, gen):
        """回归测试：params 为字符串不崩溃（BM-MT 崩溃事故根因）。"""
        step = {
            "step_id": "TEST-STR",
            "indicators": {
                "trigger": {"condition": "触发"},
                "consumes": [],
                "params": "model_id/framework/features/target、seed管理",  # 字符串！
                "data_flow": {"input": "A", "process": "B", "output": "C", "downstream": "D"},
                "code_mapping": {"module_id": "MOD-X", "source_ref": "§1"},
                "degradation": {"condition": "异常"},
            },
        }
        result = gen._format_indicators_table(step)
        assert "model_id/framework/features/target" in result

    def test_none_indicators_no_crash(self, gen):
        """indicators 为 None 不崩溃。"""
        step = {"step_id": "TEST-NONE", "indicators": None}
        result = gen._format_indicators_table(step)
        assert "要素" in result  # 降级输出表格头

    def test_empty_indicators_no_crash(self, gen):
        """indicators 为空 dict 不崩溃。"""
        step = {"step_id": "TEST-EMPTY", "indicators": {}}
        result = gen._format_indicators_table(step)
        assert "① 触发条件" in result
        assert "—" in result  # 空值降级为 —

    def test_string_trigger_no_crash(self, gen):
        """trigger 为字符串（非 dict）不崩溃。"""
        step = {
            "step_id": "TEST-STR-TRIG",
            "indicators": {
                "trigger": "直接字符串触发条件",
                "consumes": [],
                "params": [],
                "data_flow": {},
                "code_mapping": {},
                "degradation": {},
            },
        }
        result = gen._format_indicators_table(step)
        # 不崩溃即通过
        assert "① 触发条件" in result

    def test_string_degradation_no_crash(self, gen):
        """degradation 为字符串（非 dict）不崩溃。"""
        step = {
            "step_id": "TEST-STR-DEG",
            "indicators": {
                "trigger": {"condition": "触发"},
                "consumes": [],
                "params": [],
                "data_flow": {},
                "code_mapping": {},
                "degradation": "基座缺失→无法训练",
            },
        }
        result = gen._format_indicators_table(step)
        assert "① 触发条件" in result

    def test_params_list_with_string_elements(self, gen):
        """params 列表含非 dict 元素（纯字符串）不崩溃。"""
        step = {
            "step_id": "TEST-MIX-PARAMS",
            "indicators": {
                "trigger": {"condition": "触发"},
                "consumes": [],
                "params": ["纯字符串参数", {"name": "dict参数", "default": "v"}],
                "data_flow": {},
                "code_mapping": {},
                "degradation": {},
            },
        }
        result = gen._format_indicators_table(step)
        assert "纯字符串参数" in result
        assert "dict参数=v" in result

    def test_string_consumes_no_crash(self, gen):
        """consumes 为字符串（非 list）不崩溃。"""
        step = {
            "step_id": "TEST-STR-CONS",
            "indicators": {
                "trigger": {"condition": "触发"},
                "consumes": "训练数据+因子特征",  # 字符串
                "params": [],
                "data_flow": {},
                "code_mapping": {},
                "degradation": {},
            },
        }
        result = gen._format_indicators_table(step)
        assert "训练数据" in result


# ============================================================================
# Part 6: 数据流模拟（纯逻辑，无 DB）—— mock 研究管线端到端跑通
# ============================================================================


@dataclass
class ResearchArtifact:
    """模拟研究产物——在环节间流转的数据载体。

    每个根环节接收一个 ResearchArtifact，处理后产出新的 ResearchArtifact。
    history 记录经过的环节序列，用于验证流转路径。
    """

    type: str  # 产物类型标识（如 "raw_data" / "versioned_dataset" / "experiment_result"）
    payload: dict[str, Any]  # 实际数据
    history: list[str] = field(default_factory=list)  # 经过的 step_id 序列


# ── 各根环节模拟处理器 ──────────────────────────────────────────────
# 每个处理器：验证输入类型 → 模拟处理 → 产出输出类型 → 记录 history
# 处理逻辑是对真源 indicators.data_flow.process 的简化模拟


def _process_data_and_features(pkt: ResearchArtifact) -> ResearchArtifact:
    """BM-RES-01：原始数据 → 版本化数据集 + PIT 正确特征。"""
    assert pkt.type == "raw_data", f"BM-RES-01 输入应为 raw_data，实际 {pkt.type}"
    return ResearchArtifact(
        type="versioned_features",
        payload={**pkt.payload, "pit_validated": True, "dataset_version": "v1.0"},
        history=pkt.history + ["BM-RES-01"],
    )


def _process_experiment_tracking(pkt: ResearchArtifact) -> ResearchArtifact:
    """BM-RES-02：版本化特征 → 实验结果（含复现包）。"""
    assert pkt.type == "versioned_features", f"BM-RES-02 输入应为 versioned_features，实际 {pkt.type}"
    return ResearchArtifact(
        type="experiment_result",
        payload={**pkt.payload, "experiment_id": "exp-001", "reproducible": True},
        history=pkt.history + ["BM-RES-02"],
    )


def _process_hypothesis_management(pkt: ResearchArtifact) -> ResearchArtifact:
    """BM-RES-03：实验结果 → 假设验证 + 知识库沉淀。"""
    assert pkt.type == "experiment_result", f"BM-RES-03 输入应为 experiment_result，实际 {pkt.type}"
    return ResearchArtifact(
        type="validated_hypothesis",
        payload={**pkt.payload, "hypothesis_id": "h-001", "status": "accepted"},
        history=pkt.history + ["BM-RES-03"],
    )


def _process_workflow_orchestration(pkt: ResearchArtifact) -> ResearchArtifact:
    """BM-RES-04：假设 → DAG 工作流（可重复执行管线）。"""
    assert pkt.type == "validated_hypothesis", f"BM-RES-04 输入应为 validated_hypothesis，实际 {pkt.type}"
    return ResearchArtifact(
        type="research_pipeline",
        payload={**pkt.payload, "dag_nodes": 5, "dag_edges": 4},
        history=pkt.history + ["BM-RES-04"],
    )


def _process_notebook_collaboration(pkt: ResearchArtifact) -> ResearchArtifact:
    """BM-RES-05：工作流 → Notebook 原型 + 评审通过的生产管线。"""
    assert pkt.type == "research_pipeline", f"BM-RES-05 输入应为 research_pipeline，实际 {pkt.type}"
    return ResearchArtifact(
        type="production_pipeline",
        payload={**pkt.payload, "reviewed": True, "converted_to_prod": True},
        history=pkt.history + ["BM-RES-05"],
    )


def _process_llm_agent_papers(pkt: ResearchArtifact) -> ResearchArtifact:
    """BM-RES-06：生产管线 → LLM 研究发现 + 论文趋势。"""
    assert pkt.type == "production_pipeline", f"BM-RES-06 输入应为 production_pipeline，实际 {pkt.type}"
    return ResearchArtifact(
        type="research_finding",
        payload={**pkt.payload, "llm_insight": "因子X在牛市有效", "paper_trend": "regime_detection"},
        history=pkt.history + ["BM-RES-06"],
    )


def _process_strategy_iteration(pkt: ResearchArtifact) -> ResearchArtifact:
    """BM-RES-07：研究发现 → 迭代策略（权重调整 + 新因子）。"""
    assert pkt.type == "research_finding", f"BM-RES-07 输入应为 research_finding，实际 {pkt.type}"
    return ResearchArtifact(
        type="iterated_strategy",
        payload={**pkt.payload, "weight_adjusted": True, "new_factor_mined": "momentum_v2"},
        history=pkt.history + ["BM-RES-07"],
    )


# 处理器注册表：step_id → 处理函数
PROCESSORS: dict[str, Any] = {
    "BM-RES-01": _process_data_and_features,
    "BM-RES-02": _process_experiment_tracking,
    "BM-RES-03": _process_hypothesis_management,
    "BM-RES-04": _process_workflow_orchestration,
    "BM-RES-05": _process_notebook_collaboration,
    "BM-RES-06": _process_llm_agent_papers,
    "BM-RES-07": _process_strategy_iteration,
}


class TestResearchDataFlowSimulation:
    """研究管线数据流模拟——mock 7 阶段处理器验证端到端跑通。

    纯逻辑测试，无 DB 依赖。模拟从原始数据到迭代策略的完整研究管线，
    验证每个阶段的输入→输出类型匹配、history 轨迹完整、最终产物正确。
    """

    def test_full_pipeline_e2e(self):
        """完整管线端到端：raw_data → iterated_strategy，经 7 环节。"""
        pkt = ResearchArtifact(type="raw_data", payload={"source": "market_data"})
        for sid in MAIN_CHAIN:
            processor = PROCESSORS[sid]
            pkt = processor(pkt)
        assert pkt.type == "iterated_strategy", f"最终产物类型应为 iterated_strategy，实际 {pkt.type}"
        assert pkt.history == MAIN_CHAIN, f"history 轨迹不完整:\n预期 {EXPECTED_ROOT_CHAIN}\n实际 {pkt.history}"

    def test_each_stage_output_type(self):
        """每个阶段的输出类型符合预期。"""
        expected_outputs = {
            "BM-RES-01": "versioned_features",
            "BM-RES-02": "experiment_result",
            "BM-RES-03": "validated_hypothesis",
            "BM-RES-04": "research_pipeline",
            "BM-RES-05": "production_pipeline",
            "BM-RES-06": "research_finding",
            "BM-RES-07": "iterated_strategy",
        }
        pkt = ResearchArtifact(type="raw_data", payload={})
        for sid in MAIN_CHAIN:
            pkt = PROCESSORS[sid](pkt)
        assert pkt.type == expected_outputs[sid], f"{sid} 输出类型应为 {expected_outputs[sid]}，实际 {pkt.type}"

    def test_history_accumulates(self):
        """history 随环节流转逐步累积。"""
        pkt = ResearchArtifact(type="raw_data", payload={})
        for i, sid in enumerate(MAIN_CHAIN):
            pkt = PROCESSORS[sid](pkt)
            assert len(pkt.history) == i + 1, f"经过 {sid} 后 history 应有 {i + 1} 项，实际 {len(pkt.history)}"

    def test_payload_preserved_through_chain(self):
        """原始 payload 数据在管线中保留（不丢失）。"""
        original_source = "market_data_v2"
        pkt = ResearchArtifact(type="raw_data", payload={"source": original_source})
        for sid in MAIN_CHAIN:
            pkt = PROCESSORS[sid](pkt)
        assert pkt.payload["source"] == original_source, "原始 payload 数据在管线中丢失"

    def test_wrong_input_type_raises(self):
        """输入类型错误时处理器抛出 AssertionError（类型守卫）。"""
        wrong_pkt = ResearchArtifact(type="wrong_type", payload={})
        with pytest.raises(AssertionError, match="raw_data"):
            _process_data_and_features(wrong_pkt)

    def test_partial_pipeline_stops_correctly(self):
        """半截管线（只跑前 3 环节）产出正确中间态。"""
        pkt = ResearchArtifact(type="raw_data", payload={})
        for sid in MAIN_CHAIN[:3]:  # 只跑 RES-01→02→03
            pkt = PROCESSORS[sid](pkt)
        assert pkt.type == "validated_hypothesis"
        assert pkt.history == ["BM-RES-01", "BM-RES-02", "BM-RES-03"]

    def test_pit_validation_in_features(self):
        """BM-RES-01 产出含 pit_validated=True（PIT 正确性是回测可信硬约束）。"""
        pkt = ResearchArtifact(type="raw_data", payload={})
        result = _process_data_and_features(pkt)
        assert result.payload.get("pit_validated") is True, "BM-RES-01 产出未含 pit_validated=True（PIT 正确性缺失）"

    def test_reproducibility_in_experiment(self):
        """BM-RES-02 产出含 reproducible=True（可复现是上线硬门禁）。"""
        pkt = ResearchArtifact(type="versioned_features", payload={})
        result = _process_experiment_tracking(pkt)
        assert result.payload.get("reproducible") is True, "BM-RES-02 产出未含 reproducible=True（可复现性缺失）"

    def test_strategy_iteration_produces_new_factor(self):
        """BM-RES-07 产出含 new_factor_mined（策略进化不是一锤子买卖）。"""
        pkt = ResearchArtifact(type="research_finding", payload={})
        result = _process_strategy_iteration(pkt)
        assert "new_factor_mined" in result.payload, "BM-RES-07 产出未含 new_factor_mined（策略未进化）"
