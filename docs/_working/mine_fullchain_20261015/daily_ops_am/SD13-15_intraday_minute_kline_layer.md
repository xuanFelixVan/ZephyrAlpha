---
doc_type: mining_segment_doc
parent: docs/_working/mine_fullchain_20261015/00_skeleton.md
map_node: config/trading_day_cycle_map.yaml#D13-15
segment: fig13-B 盘中
mined: 2026-10-15
miner: daily_ops_am
ttl: task_bound
---

# SD13-15 盘中分钟K线滚动层

## 1. 定义

盘中每 5 分钟（交易时段窗+日历守卫在册）独立执行器池 DAG 槽 `intraday_minute`（11 个有效任务）滚动产分钟 K 线层；其产出的 60 分钟K是 dloop 盘中族（D13-21/22/23）唤醒词来源。决策问题：分钟K滚动有没有落到当日？60 分钟K唤醒词腿是否由它喂？

地图在册态：wiring=wired、build=partial（簿 04 复判补第三证后升为在产）、tdm_refs=TDM-E-L9-A01。admission 注记：09:30 起本层须经 D13-09 准入（未过门照跑=把红色天缺料透传三层）。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | 实时行情源（与 D13-14 同源异池）；QMT 断连时周末回填兜底注在槽注释 | `src/zephyr/data/config/schedule.yaml:45-48`（槽声明+executor=intraday_minute）；`src/zephyr/data/kline_resampler.py`（重采样执行体，骨架指针） |
| 输出面 | 分钟K族表（60 分钟K=dloop 唤醒词源）；30d count=1,242（×11 任务） | `config/trading_day_cycle_map.yaml#D13-15` trigger_facts；`src/zephyr/plan_engine/intraday_l1_tracker.py:598`（消费点在册） |
| SSOT 真源 | 图13 节点契约（行 1227-1301）+ admission_edges 第二条（D13-09→D13-15） | `config/trading_day_cycle_map.yaml#D13-15` + 行 115-118 注 |
| 代码模块 | intraday_minute 池 + 重采样器 + 唤醒词消费链 | `src/zephyr/data/config/schedule.yaml:45`；`src/zephyr/data/kline_resampler.py`；`src/zephyr/plan_engine/intraday_l1_tracker.py:598`、`src/zephyr/strategy_pipeline/pipeline_events.py:52` |
| 门禁约束 | 日历守卫 9 槽名单内+补跑宇宙内（fallback=D13-01）；RULE-SCHEMA-TZ（K 线时戳显式时区——D13-21 的 UTC 存储陷阱上游即本层） | `src/zephyr/data/trading_calendar.py:151`；`config/trading_day_cycle_map.yaml#D13-21` invalidation |
| 自动化触发 | mechanism=A_apscheduler，盘中每 5 分钟；calendar_guarded=true、in_catchup_universe=true、special_branch_exists=false（常规 DAG 槽） | `config/trading_day_cycle_map.yaml#D13-15` trigger_facts/machine_facts |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 实时源与池化隔离（独立执行器避开全市场慢任务）在册 |
| 输出面 | pass | 30d 1,242 拍在产，唤醒词下游消费点实存 |
| SSOT 真源 | pass | 节点契约+admission 等待语义在册 |
| 代码模块 | pass | 池/重采样/消费链三层实存（build=partial 系验证口径，簿 04 已补第三证升在产） |
| 门禁约束 | pass | 日历守卫+可补跑双面在册 |
| 自动化触发 | pass | 每 5 分钟 firing 在案 |

## 4. 缺口与建议

- 图13 全图缺口在本格的落点：无；本格是 B 段采集层群中最健康的 DAG 槽样板。
- gap_refs 空。
- 建议：D13-09 门施工后本层接准入读数（admission_edges 已声明等待语义，属四个拒准入下游之一）；UTC/上海日聚合口径在下消费端（D13-21）强制 toDate(asof_ts,'Asia/Shanghai')。
