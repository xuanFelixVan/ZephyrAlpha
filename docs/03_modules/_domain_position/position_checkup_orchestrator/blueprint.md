---
ttl: permanent
doc_type: blueprint
module_id: MOD-POS-030
session: st-c9-f42
---

# blueprint — position_checkup_orchestrator（MOD-POS-030）

> 挖干真源: [docs/_working/fullconnect_campaign/e_decision_chain/06_f42_p1_position_checkup.md](file:///d:/ZephyrAlpha/docs/_working/fullconnect_campaign/e_decision_chain/06_f42_p1_position_checkup.md)（G42-1 处方）
> depgraph 设计节点：module_id=MOD-POS-030（2026-09-29，st-c9-f42 登记，granularity=file；物理 node_id 易变不落文档，需要时按 module_id 查 depgraph）。

## 一句话

把建成未接线的持仓体检五件（P1-01 对账快照/P1-02 分级/P1-03 逻辑存活/P1-04 风险否决/P1-05 组合级漂移）
按 TDM-P-P1 边序串成一条盘前链，动作过裁决中心（MOD-POS-024）+审计，挂 dloop premarket 段
（`daily_loop_master_switch._stage_position_checkup`，dloop_post 16:45 自动圈，事件驱动无 cron）。

## 不做什么

- 不重造五件判定逻辑（全委托既有件）；不下单（观察/记录面，#305 同族安全态）；
- 不伪造持仓数据（上游对账取数面未接线，inputs 缺席=skipped 留痕）；
- 不做盘中持续监控节拍（P1-02/P1-05 的 continuous 语义归既有事件入口，本件=盘前单拍编排）。

## 真源与面

| 面 | 位置 |
|---|---|
| 实现 | src/zephyr/position/core/position_checkup_orchestrator.py |
| 测试 | tests/position/test_position_checkup_orchestrator.py |
| 算法图 | docs/03_modules/_domain_position/algo_flow/position_checkup_orchestrator.yaml |
| 地图节点 | TDM-P-P1（module_ref 本件）+ TDM-P-P1-01..06 |
| 消费者 | zephyr.plan_engine.daily_loop_master_switch（MOD-PLAN-033） |
