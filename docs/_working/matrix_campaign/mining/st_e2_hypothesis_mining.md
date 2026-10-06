---
campaign: matrix-20261006
lane: S-skeleton
status: draft
ttl: task_bound
---

# st_e2_hypothesis —— E2 假说预审逻辑门（SPM 8 节点）

- 真源: `config/strategy_production_map.yaml`；行号=SPM:L*。
- 职责: 假说进考卷前的逻辑门与多重测试纪律（BH-FDR=全图三铁律②执法件）。
- 计数: 8 = 1 stage(partial) + 7 mech（built 6 / pending 1）。

## 1. 族内节点全清单

| node_id | 名称 | 状态 | module_ref | 行 |
|---|---|---|---|---|
| FAC-E2 | 假说预审逻辑门（stage） | partial | MOD-BT-091 | SPM:L255 |
| FAC-E2-M-001 | 假说预审逻辑门 | built | MOD-BT-091 | SPM:L1410 |
| FAC-E2-M-002 | 假发现率门（BH-FDR，全图三铁律②执法件） | built | MOD-BT-187 | SPM:L1424 |
| FAC-E2-M-003 | 深审模型适配器——E2 预审复核力 | **pending** | dir:_domain_ml_serve/deep_review_model_adapter | SPM:L1438 |
| FAC-E2-M-004 | 负面否决器——候选池一票否决（E2 同构质量门） | built | MOD-SIG-137 | SPM:L1450 |
| FAC-E2-M-005 | 顺位排序置信键 | built | MOD-SIG-141 | SPM:L1463 |
| FAC-E2-M-006 | 溯源上下文库（预审证据位） | built | dir:_domain_fundamental_signal/trace_context_store | SPM:L1476 |
| FAC-E2-M-007 | LLM Security Gateway（AI 安检门） | built | MOD-LLM_SECURITY | SPM:L1489 |

## 2. 接线现状与缺口判定

- 已接线：逻辑门本体（M-001）+ FDR 纪律（M-002）+ 否决/置信键（M-004/005）+ 证据位（M-006）+ AI 安检（M-007，宪法 RULE-LSG 的工厂侧落点）。
- 缺口：FAC-E2-M-003 深审模型适配器 pending——预审的第二道模型复核力未接，现依赖单门 + FDR。
- 可考性：E2 是工厂内部门，不进回测考卷；其执法有效性由 N 试次账本（FAC-E4-M-020，SPM:L3014，FDR 预算证据位）事后审计。
- 回灌闭环：feedback_loops[0] = E9→E2"实盘归因回灌假说先验"（SPM feedback 区）——E2 是闭环入口，E9 侧回灌执行件=FAC-E9-M-006（built）。

## 3. 修复建议（一句话）

M-003 深审适配器按 _domain_ml_serve 目录设计补齐（pending 件），优先级低于 E4/E7 的 pending 群（见 99 §3 排序建议）。

## 4. 交叉验证

- TDM 同构件：TDM-E-L3-04 负面否决器（TDM:L1799，negative_veto.py）与 FAC-E2-M-004 同族——live 域与工厂域各一门，H9 判 L3（live 在岗回测零）。
- TDM-F-C3-02 升降级管线（lifecycle_state_machine）与 E2 的预审是上下游治理关系（H9 §1.8 判 D 治理域）。
- chief B1 ENV-17 计数一致；无 census 层面交集（census 未触 E2 层内构成——本册为补充挖矿）。
