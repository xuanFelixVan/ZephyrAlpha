---
ttl: task_bound
---
# SDSC-13 完整性巡检 + 新鲜度哨兵（四检核器，只检测不回补）

> 挖矿工程：全链路图12 数据供给链 S5 对账修复段 1/8｜真源=config/data_supply_chain_map.yaml#DSC-13｜挖矿时点=2026-10-15（含当日只读复核）
> 自审闸口径：pass=证据实存且复核一致；warn=在册但有未证项/漂移/限定；fail=结构性断裂且无兜底证据。

## 1. 定义

- 环节全名（图12）：完整性巡检+新鲜度哨兵（四检核器，只检测不回补），node_type=stage，build_status=built，verified_scope=production（行级 ✅）。
- 职责一句话：integrity_check（23:00 达标检测）+supply_sentinel（06:50 业务新鲜度阈值/切片/行数地板，托管 quality_sentinel 变异巡检）+calendar_coverage（07:10 日历×表日期差集）+任务级对账（已独立成行 DSC-20）。全族只检测+告警，回补由 DSC-14 按各自口径独立发现。
- 决策问句（图原文）：数据该新没新、该全没全？检出来的缺口谁来修？

## 2. 六向台账

| 向 | 台账要点 | 文件路径证据 |
|---|---|---|
| 输入面 | DSC-06→DSC-13（被检对象=在库数据）；检核基准=日历+契约阈值 | config/data_supply_chain_map.yaml edges DSC-06→13；src/zephyr/data/config/data_supply_sentinel.yaml（阈值配置） |
| 输出面 | 告警件 data/failures/*.json（落盘即止，无确认/销项字段）+巡检台账 integrator_progress.db task_progress+catchup_guard 对账基准+CLI status；本批复核：今日 failures 167 件（circuit_breaker_fred 10+/stale_reaper 6/tdx connect 3 等）、sentinel 案卷连日（10-12/13/14 22:50 档） | data/failures/（本批 ls）；data/integrator_progress.db task_progress（本批复读）；config/data_supply_chain_map.yaml#DSC-13 store_refs |
| SSOT 真源 | 三检核器槽位真源=schedule.yaml 三槽（特殊分派 task_count=0）；阈值真源=data_supply_sentinel.yaml；语义层=图12 DSC-13 | src/zephyr/data/config/schedule.yaml（integrity_check/data_supply_sentinel/calendar_coverage_check）；src/zephyr/data/config/data_supply_sentinel.yaml |
| 代码模块 | module_id=MOD-L00-004，module_ref=src/zephyr/data/integrity_checker.py；四执行体 integrity_checker/supply_sentinel/calendar_coverage_checker/alerter 全实存 | src/zephyr/data/integrity_checker.py；src/zephyr/data/supply_sentinel.py；src/zephyr/data/calendar_coverage_checker.py；src/zephyr/data/alerter.py（本批 ls） |
| 门禁约束 | 只检测不回补（downstream_action=detect_only，结论无下游补跑通道时须登记缺口——法条）；CRITICAL 才 webhook 外发；禁把"查不到"写成"无问题"（system.* 枚举面禁令+空串判绿禁令） | config/data_supply_chain_map.yaml laws（检测≠修复/禁依赖 system.*）+DSC-13 fallback |
| 自动化触发 | wired_special_branch：三槽全特殊分派（dispatched_slots 在册）；23:00/06:50/07:10 三档；task_progress[integrity_check_daily] 台账在册（09-24T15:01Z 判 lagging 在案） | config/data_supply_chain_map.yaml#DSC-13 machine.slots/freshness_evidence；本批复读 task_runs 233,587 行 max=10-15T13:30Z（宿主进程活着） |

## 3. 自审闸三态

| 向 | 三态 | 判据（本批复核 2026-10-15） |
|---|---|---|
| 输入面 | pass | 在库数据+日历+阈值三基准在册且今日可读（CH 探测全通） |
| 输出面 | pass | 告警件今日 167 件持续在产、sentinel 案卷连日、台账常驻——检测产出三通道全活 |
| SSOT 真源 | pass | 三槽+阈值配置+图节点一致；DSC-20 独立成行后的分工界面清晰 |
| 代码模块 | pass | 四执行体实存 |
| 门禁约束 | warn | 两条 residual 未消：empty_string_as_pass（逐阈值分支未逐条审计）、CRITICAL 才外发（连续多日数十告警件无人消解即无人知晓——今日 167 件即实例） |
| 自动化触发 | warn | 三档特殊分派在机且宿主进程活；但 09-25 曾出现"23:00 档当日缺跑疑点"（slot_run_missing 在册）——档期执行带一日级缺口史，禁写成全绿 |

## 4. 缺口与建议

1. 【warn 根瓶颈】告警无人消解：案卷无确认/销项字段（store_refs 原文），今日 167 件持续累积。建议最小改法=failures 文件加 resolved_at/resolved_by 两字段+一个 CLI 销项命令，让"检出来了"与"有人管了"分层。
2. 【warn 审计项】empty_string_as_pass 逐阈值分支未逐条审计：建议随 DSC-06 fail-visible 改法（query_rows 严格通道）推广到三检核器的全部判据读数，一次消掉假绿类。
3. 【正向证据】四检核器"只检测不回补"的边界被图法条保护（检测≠修复），与 DSC-14/DSC-20 的正交三轴（检测/任务对账/补执行）分工在本批复核中无越界。
