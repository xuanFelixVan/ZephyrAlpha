---
doc_type: mining_segment_doc
parent: docs/_working/mine_fullchain_20261015/00_skeleton.md
map_node: config/trading_day_cycle_map.yaml#D13-01
segment: fig13-A 盘前
mined: 2026-10-15
miner: daily_ops_am
ttl: task_bound
---

# SD13-01 调度对账补跑（错过档期自愈）

## 1. 定义

每日 05:30（全周含周末）APScheduler 特殊槽 `catchup_guard` 驱动档期对账补跑器：扫描昨日错过排班时刻的任务，按档期分桶（intraday/always_on 等，补跑宇宙=catchup_guard.py 档期分桶常量集）在单批上限内顺延补跑。决策问题：05:30 这一圈跑完了吗？跑不完谁的手被麻住？错过档期今天还有谁接？

地图在册态：wiring=partial、build=partial、red_reason=unwired、remediation_broken=true（晨间调度器重启风暴腰斩长批 + 锁留死 PID）。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | 排班三表（schedule.yaml 槽声明 + integrator task_runs 打卡 + 资源画像）；错档任务宇宙=档期分桶常量 | `src/zephyr/data/config/schedule.yaml`；`src/zephyr/data/catchup_guard.py`（分桶常量）；`data/integrator_progress.db:task_runs` |
| 输出面 | 补跑执行结果 + task_progress 汇总台账 + 锁文件；失败可见性=台账+锁，崩溃腿无降级告警=静默 | `tmp/catchup_guard.lock`；`tmp/scheduler_run.log`；地图 evidence：自 09-21 起无一圈完成、锁现值 PID 经 tasklist 实测已死 |
| SSOT 真源 | 图13 节点契约（行 133-223）+ data_ops SOP | `config/trading_day_cycle_map.yaml#D13-01`；`docs/01_policies_and_standards/sop/data_ops_sop/`；`docs/_working/map_build/fig13_daycycle/01_盘前就绪链.md` |
| 代码模块 | run_catchup_guard 执行体 + 调度器特殊槽分支（地图锚 scheduler.py:231 已漂移，HEAD 实位=336） | `src/zephyr/data/catchup_guard.py:42`；`src/zephyr/data/scheduler.py:336-340`（实核 `if schedule_name == "catchup_guard"`） |
| 门禁约束 | RULE-GUARDIAN（写操作前提=reaper 存活）；长批须登记 process_reaper_keep.txt 防误杀；GATE-SCHEDULE-CONSISTENCY(826) 管排班三表一致性；锁文件语义（死 PID 锁留=占位无主） | `scripts/register_process_reaper_task.ps1`；`AGENTS.md` §0-2/§1；`config/trading_day_cycle_map.yaml` ops_tool_ref（`scripts/ops/schedule_overview.py` + gate 826） |
| 自动化触发 | mechanism=A_apscheduler，每日 05:30 全周（守卫本身须非交易日可跑，calendar_guarded=false）；trigger_facts：30 日任务级完成 count=0；special_branch_exists=true、in_catchup_universe=false（自身不在补跑宇宙） | `config/trading_day_cycle_map.yaml#D13-01` trigger_facts/machine_facts 块（as_of 2026-10-08） |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 槽声明与特殊分支在位，补跑宇宙机生实扫在册 |
| 输出面 | fail | 30 日 0 完成圈；task_progress 最后成功汇总非 05:30 档期时点且 rows 打满上限；锁留死 PID |
| SSOT 真源 | pass | 图13 节点契约完整（含 evidence/trigger_facts/machine_facts），confidence=verified |
| 代码模块 | warn | 执行体与分支实存实核；地图锚 scheduler.py:231 vs HEAD 实位 336（锚漂移） |
| 门禁约束 | warn | 长批防误杀登记面在册但本轮补跑全断期间未见 reaper 交互留痕；锁清理无主体 |
| 自动化触发 | warn | 每日 firing 正常但完成率 0；重启风暴与长批互斥未解 |

## 4. 缺口与建议

- 图13 全图缺口在本格的落点：无 G 节点挂本格；本格是 miss_policy=rerun 的兜底器本身，其断裂放大 D13-05（不在补跑宇宙）与 D13-35（行数腿）的缺口。
- gap_refs 在册：benchmark:A6（miss_policy「每格声明」层缺失，本图按机生面派生）、benchmark:C1（rerun 是否=给定时器补跑发准生证，措辞权在总包）、4 个 task: 台账项（dividend_incremental / futures_warehouse_receipt_backfill_czce / futures_warehouse_receipt_backfill_shfe / road_freight_index_full_refresh）。
- 建议：①补跑圈错峰（避开晨间调度器重启风暴窗）或加重启后自恢复；②锁文件加死 PID 检测与陈旧锁接管；③崩溃腿补一条降级告警（对照 D13-02 两腿均有）。
