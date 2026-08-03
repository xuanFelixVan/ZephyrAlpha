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
  锚点: MOD-SIM-003 (risk_simulator.py