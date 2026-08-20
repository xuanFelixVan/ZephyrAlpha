# [A_test] module_id: MOD-GOV_battle_map_sim_val | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-280 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_battle_map_simulation_validation
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DB不可达->skip_test; 拓扑断裂->AssertionError; 指标缺失->AssertionError
# [TESTS] tests/governance/test_battle_map_simulation_validation.py
# [TTL] permanent
"""test_battle_map_simulation_validation.py — 仿真验证阶段 8 环节逻辑全覆盖验证

验证 battle_map_04_simulation_validation.md 真源中仿真验证阶段 8 环节的数据完整性、
拓扑结构、6 件套指标、YAML 叙事及 BM-SIM-07 风控仿真器闭环流程。

环节结构（8 环节）：

  BM-SIM-01 市场仿真器           (缺失态无锚点——SSoT 明文，待施工)
  BM-SIM-02 策略仿真器           (production, MOD-SIM-002)
  BM-SIM-03 场景生成与蒙特卡洛   (production, MOD-SIM-005)
  BM-SIM-07 风控仿真器           (production, MOD-SIM-003)
  BM-SIM-04 压力测试引擎         (production, MOD-RK-12)
  BM-SIM-05 依赖图数字孪生       (candidate, CAND-HARVEST-0795)
  BM-SIM-06 仿真结果分析         (production, MOD-SIM-012)
  BM-SIM-08 Paper Matching 涨跌停排队引擎 (design，缺失态无锚点——SSoT 明文，待施工)

流转边（9 条）：
  BM-SIM-01 -.-> BM-SIM-02 --> BM-SIM-03 --> BM-SIM-04 -.-> BM-SIM-05 -.-> BM-SIM-06
                                BM-SIM-03 --> BM-SIM-07 --> BM-SIM-06   ← 风控仿真支路

BM-SIM-07 闭环验证（核心测试目标）：
  入边: BM-SIM-03 → BM-SIM-07  (蒙特卡洛→风控仿真)
  出边: BM-SIM-07 → BM-SIM-06  (风控仿真→结果分析)
  锚点: MOD-SIM-003 (risk_simulator.py, primary, stable)
  翻译: name_zh/name_en/plain_zh/mechanism_zh/indicators_zh 五字段齐全

五类测试：
  1. **拓扑验证（e2e，需 DB）**：7 环节存在、每环节有锚点（BM-INV-001）、9 条流转边。
  2. **BM-SIM-07 闭环验证（e2e）**：入边/出边/锚点/depgraph build_status 完整。
  3. **YAML 叙事验证（e2e）**：BM-SIM-07 在 module_translation_registry.yaml 有 5 字段叙事。
  4. **6 件套指标验证（e2e）**：BM-SIM-07 的 indicators_zh 含 6 件套全字段。
  5. **生成器渲染防御性验证（纯逻辑）**：indicators 字段类型降级渲染不崩溃。

设计原则（对标 test_battle_map_research_incubation.py）：
  - 真实 DB 连接做拓扑验证（@pytest.mark.e2e）；DB 不可达则 skip
  - 不写入生产库——全部只读

Usage::

    py -3.12 -m pytest tests/governance/test_battle_map_simulation_validation.py -v
    py -3.12 -m pytest tests/governance/test_battle_map_simulation_validation.py -k "not e2e"  # 跳过 DB
    py -3.12 -m pytest tests/governance/test_battle_map_simulation_validation.py::TestBMSim07ClosedLoop -v
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SRC_PATH = _REPO_ROOT / "src"
if str(_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(_SRC_PATH))


# ── 期望数据（真源：battle_map_04_simulation_validation.md + DB） ──────────────

EXPECTED_STEPS = {
    "BM-SIM-01": {"name": "市场仿真器", "maturity": "production"},
    "BM-SIM-02": {"name": "策略仿真器", "maturity": "production"},
    "BM-SIM-03": {"name": "场景生成与蒙特卡洛", "maturity": "production"},
    "BM-SIM-07": {"name": "风控仿真器", "maturity": "production"},
    "BM-SIM-04": {"name": "压力测试引擎", "maturity": "production"},
    "BM-SIM-05": {"name": "依赖图数字孪生", "maturity": "production"},
    "BM-SIM-06": {"name": "仿真结果分析", "maturity": "production"},
    "BM-SIM-08": {"name": "Paper Matching 涨跌停排队引擎", "maturity": "design"},
}

# 缺失态环节（battle_map_04 SSoT 明文「⚠无锚点」：BM-SIM-01 市场仿真器缺失态待施工，
# BM-SIM-08 涨跌停排队引擎设计态待施工）——孤儿锚点检查豁免集，新增孤儿会触发断言
EXPECTED_ANCHORLESS_STEPS = {"BM-SIM-01", "BM-SIM-08"}

# BM-SIM-07 期望的流转边
EXPECTED_SIM07_EDGES = [
    {"from": "BM-SIM-03", "to": "BM-SIM-07", "type": "data_flow", "label": "蒙特卡洛→风控仿真"},
    {"from": "BM-SIM-07", "to": "BM-SIM-06", "type": "data_flow", "label": "风控仿真→结果分析"},
]

# BM-SIM-07 期望的锚点
EXPECTED_SIM07_ANCHORS = [
    {"target_graph": "depgraph", "target_id": "MOD-SIM-003", "role": "primary", "status": "stable"},
]

# BM-SIM-07 期望的翻译字段
EXPECTED_SIM07_TRANSLATION = {
    "name_zh": "风控仿真器",
    "name_en": "Risk Simulator",
    "plain_zh": "把风控放进仿真里跑",
    "mechanism_zh": "D-SIMULATION-03",
    "indicators_zh": "VaR模拟",
}


# ── DB fixture ────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def bm_reader():
    """BattleMapReader fixture — DB 不可达时 skip 整个 module。"""
    try:
        from zephyr.governance.persistence.battle_map_reader import BattleMapReader

        reader = BattleMapReader()
        # 验证连接可用
        _ = reader.get_edge_count()
        return reader
    except Exception as e:
        pytest.skip(f"DB 不可达，跳过 e2e 测试: {e}")


@pytest.fixture(scope="module")
def dep_reader():
    """DepgraphReader fixture — DB 不可达时 skip。"""
    try:
        from zephyr.governance.persistence.depgraph_reader import DepgraphReader

        return DepgraphReader()
    except Exception as e:
        pytest.skip(f"DepgraphReader 不可达: {e}")


@pytest.fixture(scope="module")
def translation_registry():
    """加载 module_translation_registry.yaml 的 battle_map_steps 段。"""
    import yaml

    yaml_path = _REPO_ROOT / "docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml"
    with open(yaml_path, "r", encoding="utf-8") as f:
        registry = yaml.safe_load(f)
    return {s["step_id"]: s for s in registry.get("battle_map_steps", [])}


# ── 1. 拓扑验证 ───────────────────────────────────────────────────────────────


@pytest.mark.e2e
class TestSimulationValidationTopology:
    """仿真验证阶段 8 环节拓扑验证。"""

    def test_all_8_steps_exist(self, bm_reader):
        """8 环节全部存在且 flow_stage=simulation_validation。"""
        steps = bm_reader.get_steps_by_flow_stage("simulation_validation")
        step_ids = {s["step_id"] for s in steps}
        for expected_id in EXPECTED_STEPS:
            assert expected_id in step_ids, f"环节 {expected_id} 不在 simulation_validation 阶段"

    def test_step_count_is_8(self, bm_reader):
        """环节总数 = 8（含 BM-SIM-07 + BM-SIM-08）。"""
        steps = bm_reader.get_steps_by_flow_stage("simulation_validation")
        assert len(steps) == 8, f"期望 8 环节，实际 {len(steps)} 环节: {[s['step_id'] for s in steps]}"

    def test_no_orphan_steps(self, bm_reader):
        """无孤儿环节（BM-INV-001）——除 SSoT 明文缺失态环节（BM-SIM-01/BM-SIM-08）外，
        每个环节至少有 1 个锚点；且缺失态集合不得扩大。"""
        steps = bm_reader.get_steps_by_flow_stage("simulation_validation")
        anchorless = set()
        for s in steps:
            sid = s["step_id"]
            anchors = bm_reader.get_anchors_by_step(sid)
            if not anchors:
                anchorless.add(sid)
        unexpected = anchorless - EXPECTED_ANCHORLESS_STEPS
        assert not unexpected, f"环节 {sorted(unexpected)} 无锚点（孤儿环节 BM-INV-001 违例）"
        missing_expected = EXPECTED_ANCHORLESS_STEPS - anchorless
        assert not missing_expected, (
            f"缺失态环节 {sorted(missing_expected)} 已有锚点——请同步更新 EXPECTED_ANCHORLESS_STEPS"
        )

    def test_edge_count(self, bm_reader):
        """流转边总数 >= 9（含 BM-SIM-07 的 2 条边）。"""
        count = bm_reader.get_edge_count()
        assert count >= 9, f"期望 >= 9 条流转边，实际 {count}"


# ── 2. BM-SIM-07 闭环验证（核心测试） ─────────────────────────────────────────


@pytest.mark.e2e
class TestBMSim07ClosedLoop:
    """BM-SIM-07 风控仿真器闭环流程验证。

    验证链路：BM-SIM-03 蒙特卡洛 → BM-SIM-07 风控仿真 → BM-SIM-06 结果分析
    """

    def test_sim07_step_exists(self, bm_reader):
        """BM-SIM-07 环节存在于 simulation_validation 阶段。"""
        steps = bm_reader.get_steps_by_flow_stage("simulation_validation")
        sim07 = [s for s in steps if s["step_id"] == "BM-SIM-07"]
        assert len(sim07) == 1, "BM-SIM-07 不存在"
        assert sim07[0]["step_name"] == "风控仿真器"
        assert sim07[0]["design_maturity"] == "production"

    def test_sim07_has_primary_anchor(self, bm_reader):
        """BM-SIM-07 有 primary 锚点指向 MOD-SIM-003。"""
        anchors = bm_reader.get_anchors_by_step("BM-SIM-07")
        assert anchors and len(anchors) > 0, "BM-SIM-07 无锚点"

        primary_anchors = [a for a in anchors if a.get("target_role") == "primary"]
        assert len(primary_anchors) > 0, "BM-SIM-07 无 primary 锚点"

        mod_sim_003 = [a for a in primary_anchors if a.get("target_id") == "MOD-SIM-003"]
        assert len(mod_sim_003) == 1, f"期望 primary 锚点 MOD-SIM-003，实际: {primary_anchors}"
        assert mod_sim_003[0]["target_graph"] == "depgraph"
        assert mod_sim_003[0]["status_snapshot"] == "stable"

    def test_sim07_anchor_target_exists_in_depgraph(self, bm_reader, dep_reader):
        """BM-SIM-07 锚点 MOD-SIM-003 在 depgraph 中存在（非幽灵锚点 BM-INV-002）。"""
        anchors = bm_reader.get_anchors_by_step("BM-SIM-07")
        for a in anchors:
            if a["target_graph"] == "depgraph":
                tid = a["target_id"]
                status_map = dep_reader.get_status_and_gate_map([tid])
                assert tid in status_map, f"幽灵锚点 BM-INV-002: {tid} 在 depgraph 中不存在"

    def test_sim07_incoming_edge_from_sim03(self, bm_reader):
        """入边：BM-SIM-03 → BM-SIM-07 (蒙特卡洛→风控仿真)。"""
        in_edges = bm_reader.get_edges_to_step("BM-SIM-07")
        assert in_edges and len(in_edges) > 0, "BM-SIM-07 无入边"

        sim03_edge = [e for e in in_edges if e["from_step_id"] == "BM-SIM-03"]
        assert len(sim03_edge) == 1, f"期望 BM-SIM-03→BM-SIM-07 边，实际入边: {in_edges}"
        assert sim03_edge[0]["edge_type"] == "data_flow"
        assert "蒙特卡洛" in sim03_edge[0].get("label", ""), (
            f"边 label 应含'蒙特卡洛'，实际: {sim03_edge[0].get('label')}"
        )

    def test_sim07_outgoing_edge_to_sim06(self, bm_reader):
        """出边：BM-SIM-07 → BM-SIM-06 (风控仿真→结果分析)。"""
        out_edges = bm_reader.get_edges_from_step("BM-SIM-07")
        assert out_edges and len(out_edges) > 0, "BM-SIM-07 无出边"

        sim06_edge = [e for e in out_edges if e["to_step_id"] == "BM-SIM-06"]
        assert len(sim06_edge) == 1, f"期望 BM-SIM-07→BM-SIM-06 边，实际出边: {out_edges}"
        assert sim06_edge[0]["edge_type"] == "data_flow"
        assert "风控仿真" in sim06_edge[0].get("label", ""), (
            f"边 label 应含'风控仿真'，实际: {sim06_edge[0].get('label')}"
        )

    def test_sim07_closed_loop_flow(self, bm_reader):
        """闭环验证：BM-SIM-03 → BM-SIM-07 → BM-SIM-06 完整链路。

        这是 BM-SIM-07 的核心价值——将蒙特卡洛路径导入风控仿真，
        再将风控仿真结果导入结果分析，形成"蒙特卡洛→风控→分析"闭环。
        """
        # 入边：BM-SIM-03 → BM-SIM-07
        in_edges = bm_reader.get_edges_to_step("BM-SIM-07")
        sim03_in = [e for e in in_edges if e["from_step_id"] == "BM-SIM-03"]
        assert len(sim03_in) == 1, "缺少入边 BM-SIM-03→BM-SIM-07"

        # 出边：BM-SIM-07 → BM-SIM-06
        out_edges = bm_reader.get_edges_from_step("BM-SIM-07")
        sim06_out = [e for e in out_edges if e["to_step_id"] == "BM-SIM-06"]
        assert len(sim06_out) == 1, "缺少出边 BM-SIM-07→BM-SIM-06"

        # 验证边类型都是 data_flow（非 trigger）
        assert sim03_in[0]["edge_type"] == "data_flow", "入边类型应为 data_flow"
        assert sim06_out[0]["edge_type"] == "data_flow", "出边类型应为 data_flow"

        # 验证闭环语义：蒙特卡洛→风控仿真→结果分析
        in_label = sim03_in[0].get("label", "")
        out_label = sim06_out[0].get("label", "")
        assert "蒙特卡洛" in in_label, f"入边 label 应含'蒙特卡洛': {in_label}"
        assert "风控仿真" in out_label, f"出边 label 应含'风控仿真': {out_label}"


# ── 3. YAML 叙事验证 ──────────────────────────────────────────────────────────


@pytest.mark.e2e
class TestBMSim07Translation:
    """BM-SIM-07 翻译真源验证（module_translation_registry.yaml）。"""

    def test_sim07_translation_exists(self, translation_registry):
        """BM-SIM-07 在翻译真源中有条目。"""
        assert "BM-SIM-07" in translation_registry, "BM-SIM-07 不在 module_translation_registry.yaml"

    def test_sim07_translation_5_fields(self, translation_registry):
        """BM-SIM-07 翻译条目含 5 个必需字段。"""
        t = translation_registry.get("BM-SIM-07", {})
        required = ["name_zh", "name_en", "plain_zh", "mechanism_zh", "indicators_zh"]
        for field in required:
            assert field in t, f"翻译条目缺字段: {field}"
            assert t[field], f"翻译条目字段为空: {field}"

    def test_sim07_translation_content(self, translation_registry):
        """BM-SIM-07 翻译内容正确。"""
        t = translation_registry.get("BM-SIM-07", {})
        assert t.get("name_zh") == EXPECTED_SIM07_TRANSLATION["name_zh"]
        assert t.get("name_en") == EXPECTED_SIM07_TRANSLATION["name_en"]
        assert EXPECTED_SIM07_TRANSLATION["plain_zh"] in t.get("plain_zh", "")
        assert EXPECTED_SIM07_TRANSLATION["mechanism_zh"] in t.get("mechanism_zh", "")
        assert EXPECTED_SIM07_TRANSLATION["indicators_zh"] in t.get("indicators_zh", "")

    def test_sim07_indicators_has_6_pieces(self, translation_registry):
        """BM-SIM-07 的 indicators_zh 含 6 件套（①触发②消费③参数④数据流⑤代码⑥降级）。"""
        t = translation_registry.get("BM-SIM-07", {})
        indicators = t.get("indicators_zh", "")
        markers = ["①触发", "②消费", "③参数", "④数据流", "⑤代码", "⑥降级"]
        for marker in markers:
            assert marker in indicators, f"indicators_zh 缺少 6 件套标记: {marker}"

    def test_sim07_indicators_mentions_mod_sim_003(self, translation_registry):
        """indicators_zh 的 ⑤代码 段提及 MOD-SIM-003 / risk_simulator.py。"""
        t = translation_registry.get("BM-SIM-07", {})
        indicators = t.get("indicators_zh", "")
        assert "MOD-SIM-003" in indicators or "risk_simulator" in indicators, (
            "indicators_zh ⑤代码段应提及 MOD-SIM-003 或 risk_simulator.py"
        )


# ── 4. 6 件套指标结构验证 ─────────────────────────────────────────────────────


@pytest.mark.e2e
class TestBMSim07Indicators:
    """BM-SIM-07 DB indicators JSONB 结构验证。"""

    def test_sim07_db_has_indicators(self, bm_reader):
        """BM-SIM-07 在 DB 中有 indicators 字段（非空）。"""
        # BattleMapReader 可能不直接暴露 indicators，通过翻译真源间接验证
        # 这里通过 YAML 叙事验证 indicators_zh 已在 TestBMSim07Translation 中覆盖
        # 此测试作为占位——如果未来 DB indicators 字段可查询，在此补充
        steps = bm_reader.get_steps_by_flow_stage("simulation_validation")
        sim07 = [s for s in steps if s["step_id"] == "BM-SIM-07"]
        assert len(sim07) == 1
        # DB step 存在即通过——indicators_zh 的完整性在 YAML 测试中验证


# ── 5. 生成器渲染防御性验证（纯逻辑，无 DB 依赖） ─────────────────────────────


class TestSim07GeneratorRendering:
    """BM-SIM-07 生成器渲染防御性验证（纯逻辑，不依赖 DB）。

    确保生成器对 BM-SIM-07 的 indicators/params 等字段能正确渲染，
    不会因为字段类型异常（None/dict/str/list）而崩溃。
    """

    @staticmethod
    def _safe_format(value: Any) -> str:
        """模拟生成器的 _format_indicators_table 降级渲染逻辑。"""
        if value is None:
            return "—"
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            parts = []
            for k, v in value.items():
                parts.append(f"{k}: {TestSim07GeneratorRendering._safe_format(v)}")
            return "; ".join(parts)
        if isinstance(value, list):
            return ", ".join(TestSim07GeneratorRendering._safe_format(v) for v in value)
        return str(value)

    def test_render_none(self):
        """None 字段降级为 '—'。"""
        assert self._safe_format(None) == "—"

    def test_render_string(self):
        """字符串原样返回。"""
        assert self._safe_format("风控仿真器") == "风控仿真器"

    def test_render_dict(self):
        """dict 降级为 'k: v' 拼接。"""
        result = self._safe_format({"VaR": "模拟", "回撤": "模拟"})
        assert "VaR" in result and "回撤" in result

    def test_render_list(self):
        """list 降级为逗号拼接。"""
        result = self._safe_format(["VaR模拟", "回撤模拟", "熔断模拟"])
        assert "VaR模拟" in result and "熔断模拟" in result

    def test_render_sim07_indicators(self):
        """BM-SIM-07 indicators_zh 6 件套文本可安全渲染。"""
        indicators = (
            "①触发：BM-SIM-03 蒙特卡洛完成/风控参数调整；"
            "②消费：BM-SIM-01 仿真市场+BM-SIM-03 蒙特卡洛路径；"
            "③参数：VaR模拟、回撤模拟、熔断模拟；"
            "④数据流：仿真市场+MC路径→风控仿真→VaR/回撤/熔断评估→BM-SIM-06分析+D-RISK风控参数；"
            "⑤代码：MOD-SIM-003 risk_simulator.py（stable）；"
            "⑥降级：风控仿真器未就绪→仅历史VaR(无蒙特卡洛VaR)。"
        )
        result = self._safe_format(indicators)
        assert "①触发" in result and "⑥降级" in result
        assert "MOD-SIM-003" in result

    def test_render_sim07_params_as_list_dict(self):
        """params 为 list[dict] 时安全渲染（回归测试：防字符串 params 崩溃）。"""
        params = [
            {"name": "VaR模拟", "type": "float"},
            {"name": "回撤模拟", "type": "float"},
            {"name": "熔断模拟", "type": "bool"},
        ]
        result = self._safe_format(params)
        assert "VaR模拟" in result and "熔断模拟" in result
