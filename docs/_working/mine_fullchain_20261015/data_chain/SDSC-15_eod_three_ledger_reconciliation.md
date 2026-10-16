---
ttl: task_bound
---
# SDSC-15 日终三账对账（回测 vs 模拟盘 L1/L2/L3）——图级终点环（P0）

> 挖矿工程：全链路图12 数据供给链 S5 对账修复段 3/8（全图 P0 唯一环节）｜真源=config/data_supply_chain_map.yaml#DSC-15｜挖矿时点=2026-10-15（含当日只读复核）
> 自审闸口径：pass=证据实存且复核一致；warn=在册但有未证项/漂移/限定；fail=结构性断裂且无兜底证据。
> **本批复核心发现：该环节已于 2026-10-07 接线（st-vm12final-20261007-laneB），图语义层 unwired 判词已过时——接线为真、运行留痕仍缺。**

## 1. 定义

- 环节全名（图12）：日终三账对账（回测 vs 模拟盘 L1/L2/L3）——未接线（语义层原判），node_type=stage，build_status=pending，verified_scope=structure，行级 ⬜。
- 职责一句话：L1 交易级、L2 持仓零容差、L3 PnL 0.1%，A/B/C 归因三分类，差异 append-only 落 governance.db:reconciliation_differences；boundary.terminal_declared 唯一成员=图级"对账 PASS"终点语义的实现件。
- 决策问句（图原文）：回测与柜台今天还对得上吗？——这一问目前无人问（接线后=有人问了，但答案仍无运行台账可查）。

## 2. 六向台账

| 向 | 台账要点 | 文件路径证据 |
|---|---|---|
| 输入面 | DSC-GAP-RECDIFF→DSC-15 gap 边（消费侧受损）+结算/回测产物供料；broker=MiniQmtBroker（position_monitor 装配同款）；无当日回测产物→WARN 出声不硬跑（I4 不变量） | src/zephyr/data/scheduler.py:605-660（本批实读接线分支全文）；src/zephyr/ex_core/adapters/miniqmt_broker.py |
| 输出面 | governance.db:reconciliation_differences（append-only 仅 INSERT）+C 类清单当日必告警；本批复跑差异表 count=0（接线后仍 0 行=不可区分"全绿"与"未跑成"）；消费=backtest_backlog.yaml:1222 按空表降级 | src/zephyr/trading/recon_runner.py（run_daily_reconciliation 契约：C 类告警/A/B 留痕）；docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml:1222；本批 CH 直查 reconciliation_differences=0 行 |
| SSOT 真源 | 槽位登记真源=tasks.yaml eod_reconciliation_daily 条目（2026-10-07 laneB 注记：编排型任务、走 _run_special_schedule 分支、不入 run_task 管线、catchup 档期桶不含本槽）；语义层=图12 DSC-15 | src/zephyr/data/config/tasks.yaml:3888-3925（laneB 注记+条目全文本批实读）；src/zephyr/data/config/schedule.yaml:255（eod_reconciliation 槽 cron "40 15 * * 0-4"） |
| 代码模块 | module_id=MOD-TRADING-007，module_ref=src/zephyr/trading/recon_runner.py；执行体 recon_runner.py+ex_core/eod_reconciliation.py+scheduler.py 分支（611-660 行）全实存且实接 | src/zephyr/trading/recon_runner.py；src/zephyr/ex_core/eod_reconciliation.py；src/zephyr/data/scheduler.py:611-660（grep+sed 本批实读） |
| 门禁约束 | 总闸 data/runtime/eod_reconciliation.disabled（存在=停用，本批复核不存在=在岗）；无 run_id 幂等键=补跑同日双计差异行 residual；差异表 append-only；模块自述"不挂调度"与编排分支并存（编排职责在 scheduler 分支，注记已对齐） | src/zephyr/data/scheduler.py:609-615（总闸逻辑）；config/data_supply_chain_map.yaml#DSC-15 fallback |
| 自动化触发 | wired_special_branch（2026-10-07 laneB 起）：cron 15:40 周一~五+TRADING_DAY_GUARDED_SCHEDULES 交易日守卫；图 machine 层已反映接线（dispatched_slots 含 eod_reconciliation/per_slot_task_counts eod_reconciliation=1）；但 task_runs=0 by design（编排任务不入 run_task 管线）=运行成功无打卡面 | src/zephyr/data/config/tasks.yaml laneB 注记；config/data_supply_chain_map.yaml machine.scheduler_dispatch（本批 YAML 解析）；data/integrator_progress.db task_runs（本批复读 eod_reconciliation_daily=0 行） |

## 3. 自审闸三态

| 向 | 三态 | 判据（本批复核 2026-10-15） |
|---|---|---|
| 输入面 | pass | 回测产物/broker/交易日守卫三供料在码在册；无产物时 WARN 出声不硬跑=非静默槽 |
| 输出面 | fail | 差异表 0 行+运行台账结构性不存在（只有差异表、无 run 表）：接线后"对账 PASS/FAIL/没跑"三态仍不可分=图级终点（TERMINUS）承载面未闭合——本环节为全图唯一 fail 向 |
| SSOT 真源 | pass | tasks.yaml laneB 登记注记与 scheduler 分支/图 machine 层三方一致；总闸+交易日守卫双闸在册 |
| 代码模块 | pass | 分支 611-660 实读接线（委托 run_daily_reconciliation，异常降级告警不炸调度器，C 类当日必告警） |
| 门禁约束 | warn | 总闸机制在岗；无幂等键 residual 未消（接线后补跑同日会双计差异行）；reconcile_execution_log 近亲名假绿陷阱（图11 台账 89,115 行）判读纪律依赖人工 |
| 自动化触发 | warn | cron/守卫/分派三层真接线；但执行成功无任何留痕（无 task_runs/无 run 表/无成功案卷）——触发面"跑没跑"只能靠 WARN 反面推断 |

## 4. 缺口与建议

1. 【fail 收口项=图12 最高优先】运行台账缺位：建议 recon_runner 每次执行（含 skip/WARN 路径）写一行 run 台账（run_id/trade_date/verdict/层计数）——落点可复用 integrator_progress.db 新表或 reconciliation_runs.jsonl。此一件同时消 DSC-GAP-TERMINUS 与 DSC-GAP-RECDIFF 的不可证根。
2. 【warn 同批小改】差异表补 run_id 幂等键（residual 原文）：防补跑双计。
3. 【判词刷新建议】图语义层 DSC-15 节点块（unwired_slot_hollow+trigger_facts hollow 三证）与 tasks.yaml/scheduler.py/machine 层三处现值矛盾：建议随下次重生成把接线事实回写语义层（保留"行级 ⬜ 直到 run 台账补齐"的严格判词）。
4. 【正向证据】"这一问无人问"已成历史：调度分支+WARN 告警+C 类当日告警=检测面已闭环；缺的只是成功路径的账。
