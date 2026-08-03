# [A_test] module_id: MOD-GOV_battle_map_sim_val | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
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
"""test_battle_map_simulation_validation.py — 仿真验证阶段 7 环节逻辑全覆盖验证

验证 battle_map_04_simulation_validation.md 真源中仿真验证阶段 7 环节的数据完整性、
拓扑结构、6 件套指标、YAML 叙事及 BM-SIM-07 风控仿真器闭环流程。

环节结构（7 环节）：

  BM-SIM-01 市场仿真器           (candidate, CAND-HARVEST-0143)
  BM-SIM-02 策略仿真器           (production, MOD-SIM-002)
  BM-SIM-03 场景生成与蒙特卡洛   (production, MOD-SIM-005)
  BM-SIM-07 风控仿真器           (production, MOD-SIM-003)  ← 新增环节
  BM-SIM-04 压力测试引擎         (production, MOD-RK-12)
  BM-SIM-05 依赖图数字孪生       (candidate, CAND-HARVEST-0795)
  BM-SIM-06 仿真结果分析         (production, MOD-SIM-012)

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
}

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
