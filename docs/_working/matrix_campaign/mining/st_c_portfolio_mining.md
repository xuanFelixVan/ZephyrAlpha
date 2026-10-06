---
campaign: matrix-20261006
lane: S-skeleton
status: draft
ttl: task_bound
---

# st_c_portfolio —— TDM 组合与预算/归因反馈（portfolio_flow，13 节点）

- 真源: `config/trading_decision_map.yaml`；行号=TDM:L*。类别=H9 §1.8。
- 计数: 13 = A2 / B7 / C2 / D2。
- 结构注记：chief B1 把 C3 归 ENV-16（复盘回测与归因）而 ENV-14 只剩 F-FLOW+C1+C2=7——chief 表记 6 且四 FLOW 终端无显式落位，账差见 00 §5 C3。

## 1. 族内节点全清单与接线现状

| node_id | 名称 | 类别 | 接线级 | 引擎旋钮/模块 | 行 |
|---|---|---|---|---|---|
| TDM-F-FLOW | 输出组合信号（终端聚合） | B | L2 | F_merge 维占位（schema:44-48）；考卷恒 single（strategy_pool=["primary"]）；strat STR-MULTIFACTOR-098/099 | TDM:L161 |
| TDM-F-C1 | 预算切分（gate） | B | L2 | F 取值含 equal_capital/equal_risk；multi_strategy_capital_allocator（6 mounts MOD-PA-006/013 等）；考卷未开多策略 | TDM:L4114 |
| TDM-F-C2 | 组合聚合（组骨架） | B | L2 | 无 module_ref（mounts MOD-PA-002/PF-002/003/010/011/014/POS-029） | TDM:L4150 |
| TDM-F-C2-01 | 目标聚合与净额轧平 | C | L3 | firm_risk_aggregator（live）；考卷无组合聚合层 | TDM:L4206 |
| TDM-F-C2-02 | 组合约束栈 | A（子集） | L1 | E 单票上限（cap5/10/20 含 B×E 交互）+H 换手惩罚+B Top-N（executor:644-651,530-545）；行业/风格敞口腿缺 | TDM:L4248 |
| TDM-F-C2-03 | 相关性聚类与cluster上限 | C | L3 | correlation_regime_monitor；3 mounts；考卷无相关性约束 | TDM:L4287 |
| TDM-F-C2-04 | budget变动三级升级 | D | ND | budget_change_handler——治理升级流程 | TDM:L4321 |
| TDM-F-C3 | 绩效归因反馈（组骨架） | B | L2 | 无 module_ref；框架 cost_attribution.py 在册（cost_attribution.py:148） | TDM:L4174 |
| TDM-F-C3-01 | 多维归因引擎 | B | L2 | performance_attribution_engine（live）+框架 CostAttribution；考卷 manifest 仅 stats 摘要列 | TDM:L4356 |
| TDM-F-C3-02 | 升降级管线与退役评审 | D | ND | factor/governance/lifecycle_state_machine；3 mounts——因子治理流程；邻近件=考卷 decision_gate/overfitting 判定已实现（f06_e4_wfa_exam.py:43-44） | TDM:L4398 |
| TDM-F-C3-03 | sleeve权重调权 | B | L2 | regime_meta_allocator；MOD-PA-015；owner_regime_switcher scaled_schedule/caps 日级帽在册（switcher.py:223-243） | TDM:L4450 |
| TDM-F-C3-04 | 参数校准闭环 | A | L1 | walk_forward/cpcv/purged_kfold 全在册且 E4-WFA 考卷在用（f06_e4_wfa_exam.py 8 折滚动） | TDM:L4500 |
| TDM-F-C3-05 | 可靠度养成与信号健康 | B | L2 | signal_degradation_monitor；6 mounts（AU-009/BT-018/RK-18/SIGQC-003/005/006）；框架 services/decay_monitor 在册考卷未接 | TDM:L4549 |

## 2. 缺口与可考性判定

- A2（约束栈子集/参数校准）：考卷已行使，但 C2-02 缺行业/风格敞口腿（M6 相关性 cluster 是补腿路径，H9 M 级）。
- B7：整族卡在"多策略未开"一根线上——F 维 context 翻转即 C1/C2/F-FLOW 三节点开考的前置（H9 L4：多策略组合层引擎=PP-001 整装组合 V0 蓝图）。
- C2：C2-01 净额轧平（L 级组合聚合层）、C2-03（M6 滚动相关贪心聚类，O(S²) 注意 GPU）。
- D2：治理流程（budget 升级/退役评审）不进回测；C3-02 的邻近件（decision_gate/overfitting）已在考卷——治理与考卷的分界线在册。

## 3. 一句话修复建议

最小路径=H9 S5（cost_attribution 输出进 manifest 列）先开 C3-01 归因面；多策略层按 PP-001 V0 蓝图立 L4 级专项，F 维翻转与 E8 组装编排联动开考。

## 4. 交叉验证

- SPM 短路互链：C1 mounts MOD-PA-006/013=FAC-E8-M-010/M-005；C3-03 mounts MOD-PA-015=FAC-E8-M-007（见 st_e8 §4）——两图同件不同名，矩阵考试可作"跨图同件"考题。
- H9 §1.8 判定全转录对平；chief ENV-14/ENV-16 分组账差=00 §5 C3。
- feedback：C3 归因结论回灌 E2 假说先验（SPM E9→E2 边的 TDM 侧对应物）。
