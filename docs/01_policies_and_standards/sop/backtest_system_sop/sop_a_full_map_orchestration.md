---
ttl: permanent
doc_type: policy
rule_form: procedural
verifiability: manual
title: SOP-A 全图回测编排——注册·分类·优先级·批次推进·归档升级
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-09-11
topic: backtest_system_sop
scope: 07_trading_decision_architecture
related_issues:
  - "#ARCH-TRADING-DECISION-MAP-001"
---

# SOP-A 全图回测编排

> **定位**：回答"先回测什么、后回测什么、一批多少、谁在哪拍板"。本 SOP 管**顺序与编排**；单个对象怎么回测看 [SOP-B](sop_b_node_loop.md)。
> **执行者**：AI 自驱推进，Owner 只在批次决策点介入。
> **总纲**：[README.md](README.md)（五约束投影 / 金字塔 / 全局护栏）。

## 1. Step A0 回测对象注册（从地图导出，不手工挑）

从 `config/trading_decision_map.yaml` 解析导出回测对象清单，每个对象一条注册条目：

```
backtest_object:
  object_id: BT-<批次>-<序号>
  node_ids: [TDM-...]          # 覆盖的地图节点（可多个=行为合并体）
  node_type: sensor|gate|strategy|aggregation
  layer: L0节点|L1组件|L2层级|L3流|L4全图
  module_ref: MOD-... | null   # 代码缺口对象标记 pending_build，不许回测不存在的行为
  confidence: verified|proposed|untested
  plan: 对象的验收阈值（预注册，未填禁跑）
```

- 产出物：`data/backtest/backtest_backlog.yaml`（或等价注册表），一次生成全量 130+ 节点候选。
- 硬规则：**注册先行**——没有注册条目的回测结果不予归档（防"顺手跑一个"绕过预注册护栏）。

## 2. Step A1 分类与合并（判据见总纲 §4）

1. 按 node_type 打四类标签（sensor/gate/strategy/aggregation）；
2. 行为合并：子节点行为相同仅参数不同 → 合并为一个回测对象 + 参数扫描（D108 判据）；
3. 合并后预期独立可回测行为约 40-60 个——若显著超出，说明合并判据执行不严，重审。

## 3. Step A2 优先级排序

| 级 | 对象 | 理由 |
|---|---|---|
| **P0** | TDM-E-L1-AGG 状态判定、TDM-E-L1 总闸、成本模型三件套 | 约束三生死线：识别不准 = 用错误状态切错误策略，比单策略还糟；成本模型是所有下游结论的口径地基 |
| **P1** | 主链：L2-01 板块强度 → L3 漏斗（L3-02→08）→ L4 时序 | 全图收益主血管 |
| **P2** | 各层树枝（L2-02~10、L3-11/12、L4 分支） | 依附主干的增量增强 |
| **P3** | 持仓流（P1-P3）、离场流（X-S1/S2）、组合流（F-C1~C3）、R1 熔断 | 流级/全图层在 P1 主链冒烟后推进 |

排序铁律：**先上游后下游**（误差级联）；同层内先高流量边后低流量边。

## 4. Step A3 批次推进

- **批次大小 ≤5 个回测对象**；每批统一走 SOP-B 七步循环。
- 批次内并行无依赖对象；有上下游依赖的不得同批（上游结论未出，下游禁跑——固定上游输入用的是历史真实数据，但对象结论的解读依赖上游状态）。
- 每批产出：批次报告（对象×验收阈值×结果×六段分档×遗留问题），追加到 `docs/_working/` 批次记录。

## 5. 批次决策点（Owner 只需看这三个问题）

1. **淘汰**：哪些对象判死/降级（proposed→untested 或直接拆节点）？——默认 AI 建议方案，Owner 否决才保留；
2. **下一批范围**：AI 提议下一批 5 个对象，Owner 增删；
3. **口径变更**：是否有发现动摇既有结论（如成本口径、数据 PIT 问题）需要回溯已归档对象？

## 6. Step A4 主链 E2E 冒烟时点（强制插入）

- **触发条件**：P1 主链对象完成第一轮宽回测（SOP-B ④）后，立即插一次主链 E2E 冒烟（L2→L3→L4 粗端到端）。
- 目的：①暴露层间口径断点（如 L2 板块强度分与 L3 漏斗输入的契约不一致）；②产出"各节点对全图净值的边际贡献"初版排序，用于重排 P2 精修优先级。
- 注意：节点局部最优 ≠ 全局最优——精修顺序以边际贡献排序，不以节点级指标排序。

## 7. Step A5 归档与地图升级

- 通过对象：BacktestResult → `decisiongraph_adapter` 写 decisiongraph L5 学习层节点（evidence_hash 唯一键）→ 地图对应节点/state_matrix 格子 confidence 由 proposed 升 verified（引用 evidence）。
- 未通过对象：地图条目降级或标注 `untested` + 原因；节点本身是否拆除由 F-C3-02 升降级评审流承接。
- 回测区间早于 `effective_from=2026-09-08` → 按 D120 打知识漂移标注放行，报告内声明。

## 8. 验收清单（本 SOP 自检）

- [ ] 所有已跑对象在 backlog 有注册条目且验收阈值先于回测填写；
- [ ] 批次 ≤5、上下游不同批；
- [ ] 每对象结论含六段分档 + 成本口径 + 区间（IS/OOS）；
- [ ] 升级 verified 的条目在 decisiongraph 有 evidence_hash 可查；
- [ ] 无绕过 P0 直接回测下游的记录。
