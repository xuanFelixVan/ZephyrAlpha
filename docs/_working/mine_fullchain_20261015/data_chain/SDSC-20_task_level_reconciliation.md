---
ttl: task_bound
---
# SDSC-20 任务级对账（档期应跑集合 vs task_runs 打卡集合差四计数）

> 挖矿工程：全链路图12 数据供给链 S5 对账修复段 8/8｜真源=config/data_supply_chain_map.yaml#DSC-20｜挖矿时点=2026-10-15（含当日只读复核）
> 自审闸口径：pass=证据实存且复核一致；warn=在册但有未证项/漂移/限定；fail=结构性断裂且无兜底证据。

## 1. 定义

- 环节全名（图12）：任务级对账（档期应跑集合 vs task_runs 打卡集合差四计数），node_type=stage，build_status=built，verified_scope=production（行级 ✅）。批次4 新增行。
- 职责一句话：integrity_checker 的第 4 类检核独立成行：产出应跑/成功/漏跑/失败四计数案卷；与逐表行数/新鲜度（DSC-13）和补执行动作（DSC-14）是三个正交完备性轴；全图唯一能机械证明漏跑真实存在的机生件；图级可证终点四实锚之一（task_reconcile 案卷）。
- 决策问句（图原文）：今天该跑的有没有真跑？漏的那几个是谁？后果落在哪张表上？

## 2. 六向台账

| 向 | 台账要点 | 文件路径证据 |
|---|---|---|
| 输入面 | DSC-13→DSC-20 control 边（同宿主进程两轴检核：表数据完整性 vs 档期执行完整性）；输入=应跑集合（tasks.yaml×schedule.yaml）×打卡集合（task_runs） | config/data_supply_chain_map.yaml edges DSC-13→20；data/integrator_progress.db task_runs（本批复读 233,587 行/266+ task_id） |
| 输出面 | 案卷 data/failures/<ds>_integrity_check_task_reconcile_<hhmmss>.json（按日落盘，无销项字段）+catchup_guard 基准+CLI status+告警三族；本批复核案卷连日：10-08/09/12/13/14（交易日逐日，国庆窗 10-01 起节拍闭合与在案判据一致） | data/failures/20261014_integrity_check_task_reconcile_150130.json 等（本批 ls -t 实读）；config/data_supply_chain_map.yaml#DSC-20 store_refs |
| SSOT 真源 | 应跑集合真源=tasks.yaml×schedule.yaml（机生）；打卡真源=task_runs 台账；语义层=图12 DSC-20 | src/zephyr/data/config/tasks.yaml；src/zephyr/data/config/schedule.yaml；data/integrator_progress.db |
| 代码模块 | module_id=MOD-L00-004，module_ref=src/zephyr/data/integrity_checker.py；执行体 integrity_checker.py+progress_store.py 实存 | src/zephyr/data/integrity_checker.py；src/zephyr/data/progress_store.py（本批 ls） |
| 门禁约束 | alert_only（四计数差>0 即产 ERROR 级案卷；无人消解即无人知晓 residual）；补跑通道只兜档期类漏跑（且 catchup 自身未落 05:30 档——与 SDSC-14 warn 交叉）；编排型任务（eod_reconciliation_daily 等）不入 run_task 管线=打卡集合对其天然盲区 | config/data_supply_chain_map.yaml#DSC-20 fallback；src/zephyr/data/config/tasks.yaml laneB 注记（不入 run_task 管线） |
| 自动化触发 | wired_special_branch：15:00 交易日档特殊分派（dispatched_slots 在册）；trigger_facts alive（期望 3/观测 3 节拍闭合） | config/data_supply_chain_map.yaml#DSC-20 trigger_facts（as_of 2026-10-04）；本批案卷 ls 复核节拍持续 |

## 3. 自审闸三态

| 向 | 三态 | 判据（本批复核 2026-10-15） |
|---|---|---|
| 输入面 | pass | 应跑×打卡双集合机械可算（本批复读 task_runs 23.3 万行 max=今日 13:30Z）；宿主与 DSC-13 同进程 |
| 输出面 | pass | 案卷按交易日连产至 10-14（今日 15:00 档案卷未到复核时点属正常）；四计数读数在案（09-23：应跑 185/成功 146/漏跑 20/失败 19） |
| SSOT 真源 | pass | 双集合真源+图节点一致；09-24 案卷正是 DSC-07/08 改判的下修依据（证据链在案） |
| 代码模块 | pass | 两执行体实存 |
| 门禁约束 | warn | 两条 residual 在册：alert_only 无人消解（同 DSC-13 瓶颈）；编排型任务打卡盲区（eod_reconciliation_daily task_runs=0 by design——本批实证，恰使 SDSC-15 的"跑没跑"落到本环节视野之外） |
| 自动化触发 | pass | 15:00 特殊分派在机+案卷节拍闭合（国庆窗判据自洽） |

## 4. 缺口与建议

1. 【warn 关键盲区】编排型特殊分派任务（eod_reconciliation/consensus_crosscheck/sector_* 等）不入 run_task 管线⇒task_runs 打卡集合照不到：建议给特殊分派分支补写 task_runs 行（source='special_dispatch' 标记），一次消掉"全图最能证明漏跑的机生件"对特殊槽全盲的结构缺口——这也直接补上 SDSC-15 的运行留痕。
2. 【warn 共性】案卷无销项字段（与 DSC-13 同根）：建议随 SDSC-13 建议一（resolved_at/resolved_by）同批落地。
3. 【正向证据】本环节四计数案卷是 DSC-07/DSC-08 改判的证据基座（09-24 件读数 183/149/19/15 在案引用），"无此行则改判无处引证"（图原文）在本批复核中再次成立；作为图级可证终点实锚继续有效。
