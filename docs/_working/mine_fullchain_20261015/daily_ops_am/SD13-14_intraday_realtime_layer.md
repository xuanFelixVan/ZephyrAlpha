---
doc_type: mining_segment_doc
parent: docs/_working/mine_fullchain_20261015/00_skeleton.md
map_node: config/trading_day_cycle_map.yaml#D13-14
segment: fig13-B 盘中
mined: 2026-10-15
miner: daily_ops_am
ttl: task_bound
---

# SD13-14 盘中实时层（Tick/L2/Greeks/IV/期货/涨跌停/港股K）

## 1. 定义

盘中每 5 分钟（交易时段窗+日历守卫在册）realtime 执行器池 DAG 槽 `intraday_realtime`（15 个有效任务）采集盘中实时族：Tick/L2/Greeks/IV/期货/涨跌停/港股K。内部结构归图 12，本格只管运营态时序。决策问题：盘中每 5 分钟这一拍有没有真产出？各腿分别在产吗？

地图在册态：wiring=partial、build=partial、red_reason=broken_supply；freshness_severity_zh=一档实测：本层多腿零产仅进当日执行台账，无 warn/fail 分级（外部对标 A2 缺位）。tdm_refs=TDM-E-L9-A02。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | QMT/行情通道实时源（前置「通道可用」由入边承载）；多腿源族 | `src/zephyr/data/config/schedule.yaml:39`（槽声明）；`src/zephyr/data/trading_calendar.py:151`（日历守卫名单） |
| 输出面 | 各实时表族（归图 12 计数面）；层在产但腿不齐（簿 04：多腿实测零产在册定性） | `docs/_working/map_build/fig13_daycycle/04_盘中采集层群.md`（环节段实测） |
| SSOT 真源 | 图13 节点契约（行 1149-1226）+ 图12 供给链同数据生命周期视角（裁定#482 正交不并） | `config/trading_day_cycle_map.yaml#D13-14`；`config/data_supply_chain_map.yaml` |
| 代码模块 | realtime 池 DAG 槽机制（15 任务挂载） | `src/zephyr/data/config/schedule.yaml:39`；`src/zephyr/data/scheduler.py`（realtime 执行器池） |
| 门禁约束 | fallback=D13-01（intraday 桶在补跑宇宙内）；新鲜度分级 A2/C4 两级未接线（分级归告警系统还是图侧声明留裁） | `config/trading_day_cycle_map.yaml#D13-14` gap_refs/fallback |
| 自动化触发 | mechanism=A_apscheduler，盘中每 5 分钟；30d count=2,053（×15 任务）；calendar_guarded=true、in_catchup_universe=true | `config/trading_day_cycle_map.yaml#D13-14` trigger_facts/machine_facts |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | warn | 通道可用是软前置（无就绪门裁定），断连时 5 分钟槽照 firing |
| 输出面 | warn | 层在产但腿不齐：多腿零产只进台账无分级 |
| SSOT 真源 | pass | 节点契约+图12 正交双视角在册 |
| 代码模块 | pass | 池/槽/日历守卫实存实核 |
| 门禁约束 | warn | A2 freshness_severity 两级未接线、C4 分级归属留裁（gap_refs 在册） |
| 自动化触发 | pass | 30d 2,053 拍 + 可补跑 |

## 4. 缺口与建议

- 图13 全图缺口在本格的落点：无 G 节点；本格是 freshness_severity 分级缺口（A2/C4）的代表格（与 D13-16/18 同族）。
- gap_refs 在册：benchmark:A2（两级未接线）、benchmark:C4（分级归告警系统还是图侧声明，留裁）。
- 建议：①腿级零产检测挂 D13-02 哨兵名单（或图侧 expected_emits 断言），结束「多腿零产仅进台账」；②C4 分级归属走裁定收口后统一接线。
