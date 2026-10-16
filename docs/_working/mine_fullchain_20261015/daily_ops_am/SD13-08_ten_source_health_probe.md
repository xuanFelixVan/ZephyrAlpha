---
doc_type: mining_segment_doc
parent: docs/_working/mine_fullchain_20261015/00_skeleton.md
map_node: config/trading_day_cycle_map.yaml#D13-08
segment: fig13-A 盘前
mined: 2026-10-15
miner: daily_ops_am
ttl: task_bound
---

# SD13-08 十源健康探针（归档 57 号 C3 腿）

## 1. 定义

独立探针模块产十源健康日志（logs/source_health_YYYYMMDD.log 每日一份），被调度器在启动挂接处消费。触发者未在排班三表（schedule.yaml 槽/计划任务/资源画像）任何名单内定位——「图照出来的洞」（trigger_owner_unlocated=true）。决策问题：今日十源健康日志有没有产出？谁消费它？

地图在册态：wiring=partial、build=built、red_reason=unwired（探针自动跑而结果不进任何裁定）；mechanism=D_unscheduled。是 D13-09 就绪门 C3 判据（miniqmt connect_ok）的现行执行者。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | 十外部源连通性/新鲜度探测（含 miniqmt connect_ok） | `src/zephyr/data/source_health_check.py` |
| 输出面 | logs/source_health_YYYYMMDD.log 每日一份（30 日窗 19 份）；非交易日与未重启日可缺档（簿 03 纠正「连续每日」口径） | `logs/`（glob 实扫）；地图 evidence/exec_evidence |
| SSOT 真源 | 图13 节点契约（行 698-763）+ 归档 57 号 SOP（C3 腿语义源，已归档且无接替件） | `config/trading_day_cycle_map.yaml#D13-08`；`docs/_archive/57_daily_cycle_sop.md`；`docs/_working/map_build/fig13_daycycle/03_盘前编排与十源探针.md` |
| 代码模块 | 探针执行体 + 调度器启动挂接消费点（两处） | `src/zephyr/data/source_health_check.py`；`src/zephyr/data/scheduler.py:1696`（地图锚）；消费自证面=启动挂接非排班面 |
| 门禁约束 | 结果不进任何裁定=无门禁语义；B4 案例批当场逼出（排班真源里不存在该腿）——排班三表一致性门（GATE-SCHEDULE-CONSISTENCY 826）不覆盖 unscheduled 机制类 | `config/trading_day_cycle_map.yaml#D13-08` evidence/note_zh；map ops_tool_ref |
| 自动化触发 | mechanism=D_unscheduled：触发者待定位；observed=每日 1 份日志（触发证据=日志面非排班面）；metric=source_health_logs_30d count=19 | `config/trading_day_cycle_map.yaml#D13-08` trigger_facts/cadence_zh |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 探针目标十源与 connect_ok 判据在执行体在册 |
| 输出面 | pass | 逐日日志面在盘（19 份/30 日），缺档口径已被簿 03 纠正 |
| SSOT 真源 | warn | 语义源=归档 57 号 SOP 且无接替件（archived_ssot_only 同族风险）；图契约在但排班真源缺位 |
| 代码模块 | warn | 执行体实存，消费点挂启动钩子而非排班面（生命周期不受调度器槽纪律管） |
| 门禁约束 | warn | 结果不进任何裁定：红时不标 SKIP（scheduler 任务级源跳闸≠开盘准入裁定） |
| 自动化触发 | fail | 触发者未在排班三表定位（trigger_owner_unlocated=true）——谁在叫醒它无真源 |

## 4. 缺口与建议

- 图13 全图缺口在本格的落点：本格自身 red_reason=unwired（6 个 unwired_no_caller 之外的 partial 型半接线）；是 **D13-09 就绪门 C3 腿现行执行者**（探针自动跑、结果不进裁定）。
- gap_refs 空；本格与 D13-09 的关系已在地图 note 逐腿点名。
- 建议：①定位触发者并补进排班真源（三表其一），消灭 D_unscheduled；②C3 判据入门时以「当日探针文件存在 ∧ miniqmt 绿」为机器可判口径（地图 D13-09 已钉死此定义）；③57 号归档承诺「并入 55 号监控体系未兑现」——接替件归属需一个裁定收口。
