---
doc_type: mining_segment_doc
parent: docs/_working/mine_fullchain_20261015/00_skeleton.md
map_node: config/trading_day_cycle_map.yaml#D13-21
segment: fig13-B 盘中
mined: 2026-10-15
miner: daily_ops_am
ttl: task_bound
---

# SD13-21 盘中 L1 市场状态跟踪

## 1. 定义

dloop 盘中族段 `intraday_l1`：60 分钟K唤醒词过滤通过才跑（唤醒词源=D13-15 的 60 分钟K新数据），跟踪当日盘中 L1 大盘市场状态并落判定台账。产物按上海日读数（asof_ts 为 UTC 存储——不按 Asia/Shanghai 日聚合会差 8 小时而误判）。决策问题：当日有没有产出行？每交易日几行？

地图在册态：wiring=wired、build=built、skeleton ✅（B 段 P0 节点）；产物 judgment_intraday_market_state 当日 4 行（三证齐）；tdm_refs=TDM-E-L1-AGG、TDM-P-P2。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | 60 分钟K新数据唤醒词（D13-15 供料） | `src/zephyr/plan_engine/daily_loop_master_switch.py:68`（地图锚/PHASE_STAGES 实核 :393-395）；`src/zephyr/data/config/schedule.yaml:45` |
| 输出面 | judgment_intraday_market_state 判定台账（当日 4 行，DatabaseService CH reader 只读复跑在案） | `config/trading_day_cycle_map.yaml#D13-21` trigger_facts（table_rows_latest_shanghai_date=4）；`src/zephyr/plan_engine/judgment_ledger.py:93` |
| SSOT 真源 | 图13 节点契约（行 1679-1750）+ TDM-E-L1-AGG 挂点 | `config/trading_day_cycle_map.yaml#D13-21`；`config/trading_decision_map.yaml#TDM-E-L1` |
| 代码模块 | _stage_intraday_l1 段+跟踪器+判定台账 | `src/zephyr/plan_engine/daily_loop_master_switch.py:211`（地图锚，_stage_intraday_l1 在位实核）；`src/zephyr/plan_engine/intraday_l1_tracker.py:7` |
| 门禁约束 | RULE-SCHEMA-TZ/UTC 存储陷阱（invalidation 在册：必须 toDate(asof_ts,'Asia/Shanghai') 聚合）；fallback=16:45 圈兜底重放（幂等全命中则空转） | `config/trading_day_cycle_map.yaml#D13-21` invalidation/fallback |
| 自动化触发 | mechanism=C_inprocess_stage（dloop_stages=[intraday_l1]）；唤醒词驱动当日数拍；feedback 边 D13-32→D13-21（段界折叠注记） | `config/trading_day_cycle_map.yaml#D13-21` cadence_zh/machine_facts.dloop_facts；feedback_loops |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 60 分钟K供料层在产（D13-15 30d 1,242 拍） |
| 输出面 | pass | 当日 4 行在产，复跑口径=上海日聚合 |
| SSOT 真源 | pass | 节点契约+TDM 挂点双册 |
| 代码模块 | pass | 段/跟踪器/台账三层实存实核 |
| 门禁约束 | pass | UTC 陷阱已作 invalidation 显式登记（防假红/假绿双向） |
| 自动化触发 | pass | 唤醒词驱动+16:45 兜底重放双路在册 |

## 4. 缺口与建议

- 图13 全图缺口在本格的落点：无；B 段决策层健康样板（段内 3 个 ✅ 之一）。
- gap_refs 空。
- 建议：UTC 聚合口径建议固化为台账查询 helper（消灭每个消费点各自 toDate 的重复纪律负担），归 plan_engine 小件，非本段缺口。
