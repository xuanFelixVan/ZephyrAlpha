---
doc_type: mining_segment_doc
parent: docs/_working/mine_fullchain_20261015/00_skeleton.md
map_node: config/trading_day_cycle_map.yaml#D13-10
segment: fig13-A 盘前
mined: 2026-10-15
miner: daily_ops_am
ttl: task_bound
---

# SD13-10 板块状态盘前复制（close_final→pre_open + 偏好重映射）

## 1. 定义

交易日 09:15（与 D13-11 同分钟）特殊槽 `sector_pre_open`（sector 双槽合一分支）驱动板块状态管线：把 T-1 日 15:10 close_final 定格态复制为 T 日 pre_open 态并做偏好重映射（消费 emotion_index@T close_final——晚于情绪班落库时点，无竞速；同一时戳禁循环）。决策问题：09:15 的盘前复制产了吗？产物停在 T 日还是 T-1 日？

地图在册态：wiring=partial、build=partial、red_reason=broken_supply、lag_trading_days=1（pre_open 态 max(trade_date) 滞后 1 交易日：该槽新增后未热载，调度器重启后生效）；tdm_refs=TDM-E-L9-V3。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | T-1 日 close_final 定格态（D13-25 盘后定格产物）+ emotion_index@close_final | `src/zephyr/data/sector_state_pipeline.py:27-31`（实核 stage 契约注释：close_final=T 日 15:10 行情定格；pre_open=T+1 09:15 复制+偏好重映射） |
| 输出面 | c1_market.sector_state(pre_open) + c1_market.sector_preference(pre_open) | `src/zephyr/data/sector_state_pipeline.py:29`（产物面注释实核）；地图 evidence：pre_open max(trade_date) 滞后 1 交易日 |
| SSOT 真源 | 图13 节点契约（行 845-919）+ 管线头注释契约 | `config/trading_day_cycle_map.yaml#D13-10`；`src/zephyr/data/sector_state_pipeline.py:1-31`（CONSUMERS+stage 契约+排班声明） |
| 代码模块 | 板块状态落库编排器 + 调度器特殊槽分支（sector 双槽合一） | `src/zephyr/data/sector_state_pipeline.py:164`；`src/zephyr/data/scheduler.py:439/552`（sector_close_final 分支实核在位） |
| 门禁约束 | 前置「D13-25 close_final 已定格」由入边承载（本格非就绪门格）；消费者三件（板块聚合器/L2 门快照/编排链经 gate 快照间接消费） | `src/zephyr/data/sector_state_pipeline.py:5`（CONSUMERS 实核：daily_gate_snapshot L2 门三原料供料、丁线 owner_gate C1 乙档）；`src/zephyr/strategy_pipeline/daily_gate_snapshot.py:9` |
| 自动化触发 | mechanism=A_apscheduler，交易日 09:15；observed 每日 1 拍；30d count=0（特殊槽 bool 返回无任务计数面）；slot_effective_task_count=0+special_branch_exists=true（特殊槽形态） | `config/trading_day_cycle_map.yaml#D13-10` trigger_facts/machine_facts |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | close_final 上游槽（D13-25，段外）与 emotion_index 时序契约无竞速在册 |
| 输出面 | warn | 产物滞后 1 交易日（槽未热载），当日 pre_open 未产 |
| SSOT 真源 | pass | 节点契约+管线自述契约一致 |
| 代码模块 | pass | 编排器+双槽分支实存实核 |
| 门禁约束 | pass | L2 门供料契约在消费者侧显式声明 |
| 自动化触发 | warn | 槽挂载后未热载：需调度器重启才生效（同文件在册先例），当前 firing 是否已带该槽待复判 |

## 4. 缺口与建议

- 图13 全图缺口在本格的落点：无 G 节点；本格 red_reason=broken_supply 的成因是运维时序（未热载）而非代码缺失。
- gap_refs 空；invalidation 注记在册：T 日 09:15 前读数必然停在上期，判「滞后」须在该拍之后复跑。
- 建议：①择交易日盘前安排调度器热载/重启窗使 sector_pre_open 生效，重启后按 invalidation 口径复判 lag 归零；②热载机制本身（新增槽免重启）归调度器车道 Enhancement，不属本段。
