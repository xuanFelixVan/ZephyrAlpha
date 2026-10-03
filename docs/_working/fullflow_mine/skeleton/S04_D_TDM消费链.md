---
ttl: task_bound
title: "S04 D段·TDM 消费链（F37-F52）"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-01
topic: fullflow_mine
---

# S04 · D 段 交易决策消费链（F37-F52，✅14 🔨1 ⬜1）

> 真源：config/trading_decision_map.yaml（TDM 182 节点：E128/P18/X19/F13/C4；activation=premarket46/intraday43/postmarket51/continuous40/on_demand2）｜三态判定：s5_skeleton §三 D 段（D 段=挖干档）。
> 职责一句话：四流（决策 L0-L4/持仓 P1-P3/离场 S1-S2+R1/组合 C1-C3）把 TDM 182 节点的判定落到执行。

## 环节逐个（16）

| # | 环节 | 数据消费 | 产出 | 自动化状态 | 断态 |
|---|---|---|---|---|---|
| F37 | L0 盘前作战计划 | F33 快照/F50 归因 | 计划/偏离监控/明日边界/滚动预测 | 自动（warroom_pipeline 等 4 件；dloop 段内） | ✅ |
| F38 | L1 大盘总闸 | A 段行情+六传感器 | 7 态状态机判定 | 自动（regime 当日 09:20 写；宏观传感器缺件） | ✅ |
| F39 | L2 板块选择 | F38 | 10 组 30 节点板块判定 | 自动（sector/ 全族） | ✅ |
| F40 | L3 个股选择 | F39 | 九阶段选票→候选池 | 自动（selection_funnel/negative_veto） | ✅ |
| F41 | L4 买卖点与执行 | F40 | 15 节点执行指令 | 自动 | ✅ |
| F42 | P1 持仓体检 | F57 对账 | 6 节点体检/动作清单 | 自动（position/core/ 全族） | ✅ |
| F43 | P2 做T加减仓 | F42 | 做T 闭环+再平衡 | 自动 | ✅ |
| F44 | P3 加仓决策 | F42 | 金字塔加仓 4 节点 | 自动 | ✅ |
| F45 | S1 卖出信号 | F42/F38 | 六桶分类+紧迫度融合 | 自动 | ✅ |
| F46 | S2 离场执行 | F45 | 6 节点离场计划 | 自动 | ✅ |
| F47 | R1 应急保命 | F59/F60 | 熔断分级/减仓/白名单 | 自动横切全流 | ✅ |
| F48 | C1 预算切分 | F27/F71 | 多策略资金预算 | alloc_budget_daily 停 09-28（与 F27 同根同治） | 🔨P0 |
| F49 | C2 组合聚合 | F48 | 净额轧平/约束栈/相关性聚类 | 自动（运行面【未干】） | ✅ |
| F50 | C3 绩效归因反馈 | F49/F28 | 5 节点归因/升降级评审 | 自动（sim_attribution 当日 13:10）；回灌 F37/F21 | ✅ |
| F51 | 币圈决策骨架 | — | TDM-C-L1..L4 第二实例 | module_ref 全空=空壳 | ⬜ |
| F52 | 验证方法学+决策算法库 | — | 5 类验证方法+27 条 DAL | 静态库在册 | ✅ |

## 自动化状态小结

- 四流当日端到端实证：decision_daily 15:18（104 行）——盘前计划→总闸→板块→个股→执行的决策面在流。
- TDM 182 节点是本段 16 环节的**判定单元层**（环节管时序与编排，TDM 管"遇什么情况怎么判"，两轴分工见 fig13 §3 禁则一/二）。

## 断链点

1. P0 F48（+F27）：E8/C1 资金链停摆——schedule 新槽 pf_alloc_rebalance_check 零任务挂载，补日历驱动+补跑。
2. P1 F38 宏观腿：macro_regime_sensor.py+macro_indicator_series_map.yaml 不在 HEAD（9ec1ae0f6e 仅落 capability token），macro_data 已在灌水、供数侧就绪，补两实体。
3. F51 币圈：V0 骨架空壳，挂起待裁。
4. 【未干】缺口移交：F49 运行面样本。
