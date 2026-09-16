---
ttl: task_bound
completes_when: 模块晋升 docs/03_modules（H-01 解冻）或工单废弃
---

# MOD-AUTO-L2-001（暂编号）promotion_combo_gate 蓝图

> 冻结区变通：正式蓝图待 docs/03_modules 解冻后晋升（挂单 H-01）。本件=施工期蓝图真源。

## 定位

骨架 v1.1 §7/§8 首件：模拟盘准入组合门打分器+转正建议书渲染。生命周期轴"模拟竞争→实盘生产"的闸门设备，消费已有件（promotion_advisory MOD-BT-199 / strategy_screen / sim_pocket_daily / sim_trade_log），零重建。

## ALGO_FLOW

层: 输入
- I1: promotion_advisories/*.json（advisory 证据）
- I2: strategy_screen 最近行（OOS Sharpe/DSR，CH 可达时）
- I3: sim_pocket_daily+sim_trade_log（回撤/笔数，CH 可达时）
层: 算法
- A1: score_candidate 纯函数——四条组合门（OOS≥1.5/回撤≤15%/笔数≥30/DSR>0），证据缺失=unknown
- A2: 裁定三分：全过=promote_ready / 任一硬败=reject / 有缺证=borderline（不冤枉不放水）
- A3: render_report 一页式 markdown（阈值出处+逐候选表+逐检查明细+建议语）
层: 输出
- O1: docs/_working/pipeline-research/promotion-reports/promotion-report-<ts>.md（CAS 写）

## 不变量

只读生成；降级不阻断；阈值预注册冻结（修标走标准库重考历史）；promote_ready 仍须 Owner 门。

## 施工块

B1 打分器+渲染（✅）；B2 测试 9 例（✅）；B3 登记+提交（本批）。
