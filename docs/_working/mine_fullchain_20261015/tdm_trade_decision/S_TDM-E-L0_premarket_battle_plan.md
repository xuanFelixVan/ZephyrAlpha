---
ttl: task_bound
doc_type: tdm_mining_note
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
skeleton_row: TDM-E-L0
flow: entry_flow
node_count: 5
session: mine-fullchain-tdm-20261015
---

# S_TDM-E-L0 盘前作战计划（5 节点）

## 1. 定义

一句话：盘前把"今天怎么打"落成一纸计划——总仓位建议档、分批建仓预案、禁做清单（sit_out_list 三源合成）、应急触发线；计划是输入不是第二决策点，开闸仍由 L1 大盘总闸唯一裁定（Owner 2026-09-09 定界）。

展开：本环节是 entry_flow 的总装层，四个子环节覆盖全交易日闭环——L0-01 计划生成（盘前）、L0-02 偏离监控与修订（盘中）、L0-03 收盘复盘与明日边界（盘后）、L0-04 明日情绪盘中滚动预测（盘中 10:00/11:00/13:30/14:30 四时点）。跨日闭环靠"盘后 L0-03 生成明日边界→次日盘前 premarket_constraint_loader 装载回本节点"，DAG 不画跨日自环、语义记在节点 algo_note（地图 TDM-E-L0 注记）。正名登记（D23）：现名"作战预案引擎"→未来正名 Game Plan Engine。

## 2. 六向台账

### 2.1 输入面（有证）
- 图内入边：TDM-F-C3-01→TDM-E-L0（昨日归因）、TDM-F-C3-04→TDM-E-L0（参数校准）；L1-AGG→TDM-E-L0（宏观态，经 AGG sequence 边）——config/trading_decision_map.yaml edges 块（261 边实读）。
- 情景概率：algo_refs=[DAL-SCEN-PROB]（TDM-E-L0-01，地图 line 311），实现=src/zephyr/plan_engine/scenario_probability_model.py（MOD-PLAN-017），2026-09-20 final3 P5 接线。
- 跨日输入：L0-03 产明日边界→次日 premarket_constraint_loader 装载（src/zephyr/plan_engine/premarket_constraint_loader.py 实存）。

### 2.2 输出面（有证）
- 出边 11 条：TDM-E-L0→TDM-E-FLOW / →TDM-E-L1 / →TDM-E-L3-06 / →TDM-X-R1；TDM-E-L0-04→TDM-E-L1-AGG / →TDM-E-L2-06-1 / →TDM-P-P2（明日悲观降档预警三反哺 D123-①②③）。
- 产品=作战室前端"今日交易计划"卡（TDM-E-L0-01 algo_note；daily_warroom_pipeline.py 消费）。

### 2.3 SSOT 真源（有证）
- config/trading_decision_map.yaml#TDM-E-L0（line 257-292，map_id=TDMAP-001，schema_version=1.2，effective_from=2026-10-05）；子节点 line 294/332/369/411。
- goal 块：family=F15_L0作战计划，output_contract="总仓位档＋禁做清单＋分批预案＋应急线（计划-执行一致率）"，exam_ref=docs/03_modules/_domain_backtest/exam_cards/**/TDM-E-L0__*。
- 算法登记：DAL-SCEN-PROB 在 REG-DAL-001（docs/01_policies_and_standards/_registry/catalogs/decision_algo_registry.yaml，32 条）；ROOR 行=docs/registry_of_registries.yaml line 605 REG-MAP-TDM-001。

### 2.4 代码模块（有证，5/5 节点 ref 实存）
- 父：src/zephyr/plan_engine/daily_warroom_pipeline.py（MOD-PLAN-018）。
- 子：daily_trade_plan.py（MOD-PLAN-011，纯函数规则模板非 LLM）、plan_deviation_monitor.py（MOD-PLAN-022，修订仅当日有效）、tomorrow_boundary_planner.py（MOD-PLAN-001）、intraday_tomorrow_forecast.py（MOD-PLAN-025）。
- module_mounts 8 件：MOD-EX-063/MOD-PLAN-002/005/019/021/023/MOD-RK-12/MOD-RK-28；配套件 sit_out_list.py、boundary_revision_engine.py、brier_calibration.py、closing_session_decision.py、next_day_forecaster.py、similar_day_evaluator.py 均在 plan_engine/ 实存。

### 2.5 门禁约束（有证）
- MAP-ALIGNMENT（in_process_gate_registry.yaml，register_line 454，enabled）：files_trigger 含 config/trading_decision_map.yaml 与 src/zephyr/plan_engine/daily_loop_master_switch.py；shell 侧 gate_registry.yaml（total_gates: 191）同 MAP-ALIGNMENT 块 watched paths line 1599。
- ALGO-NOTE-SYNC（algo_note_sync_gate.py，硬阻断）：本环节任一 module_ref .py 被触碰，须同批修订该节点 algo_note_zh 或加 note_confirmed 日期。
- TDM-MOUNT-COVERAGE（tdm_mount_coverage_gate.py，priority=151）：本环节新增 .py 须带挂载裁决（module_id 已挂图/豁免册 config/tdm_mount_exemption_registry.yaml/[not-trading] 标记三选一）。

### 2.6 自动化触发（有证）
- 日循环总扳手：src/zephyr/plan_engine/daily_loop_master_switch.py（MOD-PLAN-033）串 warroom scenario_plan 族（MOD-PLAN-018）+晨间预案（MOD-PLAN-030）+次日概率（MOD-PLAN-029）。
- 调度挂接：src/zephyr/data/scheduler.py line 466-538 dloop_post 特殊槽，交易日 16:45 自动圈（2026-09-21 Owner 批解除 MANUAL-ONLY）；总闸开关 data/runtime/daily_loop_master.disabled。
- L0-04 四时点滚动=盘中事件驱动（节点 activation=intraday）。

## 3. 自审闸三态

| 向 | 态 | 打分依据 |
|---|---|---|
| 输入面 | pass | C3-01/C3-04 入边+DAL-SCEN-PROB+跨日装载链三路全有锚 |
| 输出面 | pass | 出边 11 条全在册，作战室卡有消费方 |
| SSOT | pass | 地图行+goal 块+DAL 登记+ROOR 行四层齐 |
| 代码模块 | pass | 5/5 module_ref 实存，107 全图 ref 零缺失之列 |
| 门禁约束 | pass | 四门覆盖本环节文件域 |
| 自动化触发 | pass | dloop_post 16:45 自动圈+盘中事件驱动，Owner 批文在册 |

**总评：pass（6/6）**。confidence=proposed（全环节 5 节点无一 verified，属血肉待考非缺证）。

## 4. 缺口与建议

1. output_contract"计划-执行一致率"暂无机械对账件（L0-02 记执行不一致但无一致率报表产出器）——建议纳入 REG-VALM-001 验证方法学下挂执行质量维。
2. 跨日自环（L0-03→次日 L0）不画 DAG 属人工约定语义，建议在地图 schema 注记处加机读标记防后续图算法误判断链。
3. 骨架总纲写 L0=5 节点与实读一致；骨架行"上游=图13-A 段、E9 归因回流"中图13-A→L0 的直接边未见（入边仅 C3/L1 面），挂接语义靠 dloop 编排，建议骨架下批补注。
