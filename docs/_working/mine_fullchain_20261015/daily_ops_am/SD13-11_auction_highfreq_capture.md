---
doc_type: mining_segment_doc
parent: docs/_working/mine_fullchain_20261015/00_skeleton.md
map_node: config/trading_day_cycle_map.yaml#D13-11
segment: fig13-A 盘前
mined: 2026-10-15
miner: daily_ops_am
ttl: task_bound
---

# SD13-11 集合竞价高频五档采集

## 1. 定义

交易日 09:15–09:25 每 10 秒（含秒的间隔槽，coalesce 理由见槽注释）常规 DAG 槽 `auction_highfreq`（2 个有效任务，realtime 执行器）采集合竞价五档快照与档位表。日历守卫在册 9 槽之一且在补跑宇宙内。行数读数归图 12。决策问题：竞价窗内每拍都采到了吗？窗内快照数够吗？

地图在册态：wiring=wired、build=built、skeleton ✅；tdm_refs=TDM-E-L3-11-1。采集本身不等 D13-09 门（错过即无），但其产物进情绪指数档（D13-13）与盘前选股链须经准入（admission_edges 注记的等待语义）。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | 交易所集合竞价行情（五档/逐秒） | `src/zephyr/data.connectors`（行情采集腿）；`src/zephyr/data/config/schedule.yaml` auction_highfreq 槽（含秒槽在册） |
| 输出面 | 竞价快照表+档位表（max(trade_date)=当日 + 行数量级读数在案，骨架 §7 C 组） | 地图 exec_evidence 引骨架 §7 C 组复跑记录 |
| SSOT 真源 | 图13 节点契约（行 920-994）+ 槽声明与日历守卫名单 | `config/trading_day_cycle_map.yaml#D13-11`；`src/zephyr/data/trading_calendar.py:151`（日历守卫 9 槽名单） |
| 代码模块 | 调度器 realtime 执行器池 DAG 槽（2 任务；地图锚 schedule.yaml:183/186 已漂移，实核槽键在 234 行区——工作树在途编辑，锚漂移不判罚不代修） | `src/zephyr/data/config/schedule.yaml`（auction_highfreq 槽键实核）；`src/zephyr/data/scheduler.py`（realtime 池） |
| 门禁约束 | 资源排班门消费该槽（commit gate 侧在册）；日历守卫+coalesce 语义；RULE-SCHEMA-TZ（含秒时戳列显式时区） | `src/zephyr/gov_enforcement/commit_gates/resource_schedule_gate.py:250`（消费者在册）；`AGENTS.md` §1 规则 10 |
| 自动化触发 | mechanism=A_apscheduler，交易日 09:15–09:25 每 10 秒；30d count=1225（×2 任务）；calendar_guarded=true、in_catchup_universe=true | `config/trading_day_cycle_map.yaml#D13-11` trigger_facts/machine_facts |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 竞价窗源在产，30d 1,225 拍 |
| 输出面 | pass | 当日快照/档位表读数在案，verified_scope=production |
| SSOT 真源 | pass | 节点契约完整，admission 等待语义显式 |
| 代码模块 | pass | 槽+日历守卫实存实核（锚漂移已注记） |
| 门禁约束 | pass | 资源门消费+日历守卫双面在册 |
| 自动化触发 | pass | 含秒槽 firing 在案且可补跑 |

## 4. 缺口与建议

- 图13 全图缺口在本格的落点：无；本格下游 D13-13（情绪指数竞价档）是空心槽——采集在产而聚合端缺位，产物「采而未聚」。
- gap_refs 空。fallback=「窗过不补」：miss_policy=rerun 但窗本身 10 秒级，错过即无——已知取舍。
- 建议：①D13-13 聚合端补执行体（见 SD13-13）；②地图 schedule.yaml 锚行号在下次机生时刷新（本矿实测工作树槽键在 234 行区）。
