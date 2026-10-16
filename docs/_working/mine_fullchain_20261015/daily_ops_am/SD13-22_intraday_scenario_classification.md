---
doc_type: mining_segment_doc
parent: docs/_working/mine_fullchain_20261015/00_skeleton.md
map_node: config/trading_day_cycle_map.yaml#D13-22
segment: fig13-B 盘中
mined: 2026-10-15
miner: daily_ops_am
ttl: task_bound
---

# SD13-22 盘中情景归类

## 1. 定义

dloop 盘中族段 `classify`：消费 D13-21 的 L1 状态产出做盘中情景归类（scenario_classifier），无独立排班（同唤醒词驱动）。调用方实测仅 dloop 一处。决策问题：归类段被谁调用？调用方只有 dloop 吗？

地图在册态：wiring=wired、build=partial（验证口径=structure：调用方单一性是结构事实）；时区 invalidation 同 D13-21。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | D13-21 L1 状态判定产出（唤醒词链上游） | `config/trading_day_cycle_map.yaml` 入边 D13-21→D13-22；`src/zephyr/plan_engine/daily_loop_master_switch.py:218`（地图锚） |
| 输出面 | 情景归类结果（供决策链与 pipeline_events） | `src/zephyr/plan_engine/scenario_classifier.py:10`；`src/zephyr/strategy_pipeline/pipeline_events.py:1345`（消费者在册） |
| SSOT 真源 | 图13 节点契约（行 1751-1815）+ 段序契约（PHASE_STAGES 盘中族序 intraday_l1→classify→sentiment_loop→auction_hit 与环节编号逆向——feedback_loops 注记的段界折叠） | `config/trading_day_cycle_map.yaml#D13-22`；feedback_loops D13-23→D13-20 边注 |
| 代码模块 | _stage_classify 段+归类器 | `src/zephyr/plan_engine/daily_loop_master_switch.py:218`；`src/zephyr/plan_engine/scenario_classifier.py` |
| 门禁约束 | 调用方单一=dloop 保险丝（无旁路调用=无绕过窗闸族纪律的面）；UTC 聚合口径同 D13-21 | `config/trading_day_cycle_map.yaml#D13-22` evidence/gap_refs 空+invalidation 同 D13-21 |
| 自动化触发 | mechanism=C_inprocess_stage（dloop_stages=[classify]）；唤醒词驱动；in_phase_stages.classify=true；无独立计数面（产物归上游槽节点计数） | `config/trading_day_cycle_map.yaml#D13-22` trigger_facts（no_count_reason）/machine_facts |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 上游 D13-21 在产（当日 4 行） |
| 输出面 | pass | 归类器+消费者链实存（structure 口径） |
| SSOT 真源 | pass | 节点契约+段序契约边在册 |
| 代码模块 | pass | 段与归类器实存实核 |
| 门禁约束 | pass | 单调用方结构=面收敛 |
| 自动化触发 | pass | 唤醒词驱动在册（no_count_reason 机制类口径自洽） |

## 4. 缺口与建议

- 图13 全图缺口在本格的落点：无。
- gap_refs 空。
- 建议：归类产物如需业绩归因/复盘复用，补一张独立产物表面（当前无独立计数面=产物混在上游节点计数里，审计需借道）——低优先，登记即可。
