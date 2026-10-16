---
ttl: task_bound
---
# SDSC-01 盘后批量采集（日K/估值/资金/事件/财务/静态/校准族）

> 挖矿工程：全链路图12 数据供给链 S1 采集段 1/3｜真源=config/data_supply_chain_map.yaml#DSC-01（nodes 行，机生层+语义层双层，最后重生成 commit f61474f 2026-10-10）｜挖矿时点=2026-10-15
> 自审闸口径：pass=该向证据实存且本批复核一致；warn=证据在册但有未证项/漂移/限定；fail=该向结构性断裂且无兜底证据。

## 1. 定义

- 环节全名（图12）：盘后批量采集（日K/估值/资金/事件/财务/静态/校准族），node_type=stage，build_status=built，verified_scope=production（骨架 §1 行级 ✅，本图 10 个 production 节点之一）。
- 职责一句话：六个盘后档期（daily_kline/daily_capital/daily_event/nightly_financial/monthly_static/weekend_calibration）按 tasks.yaml schedule 字段精确字符串匹配派工，同槽任务进 TaskQueue 按 DAG 跑，把 23 家外部源数据落成盘后原始表族。
- 决策问句（图原文）：盘后各档期该产出的原始表今天出齐了吗？缺的是源侧现实还是本仓断链？

## 2. 六向台账

| 向 | 台账要点 | 文件路径证据 |
|---|---|---|
| 输入面 | DSC-SRC（23 源/275 任务分母）→本环节 data_flow 边；provider 归一层 FetchPayload→FetchResult+CapabilityContract 启动期 fail-closed 校验；副源 fallback_nonempty=38 任务 | config/data_supply_chain_map.yaml#DSC-SRC/DSC-01；src/zephyr/data/provider_base.py；src/zephyr/data/error_classifier.py；src/zephyr/data/config/tasks.yaml |
| 输出面 | 盘后原始表族（c1_market.kline_daily/stock_daily_basic/money_flow 等，目标表全集 197 张）→DSC-04 写通道；消费端=TDM 16 表约 64 点+SPM 276/56+backtest/factor 代码锚 | config/data_supply_chain_map.yaml edges DSC-01→DSC-04；本批复跑 kline_daily max(trade_date)=2026-10-15 FINAL（lag 0，非 FINAL 10,108,162/FINAL 10,108,049 双版族在产）；doc 锚=docs/_archive/_working_cleared/map_build/fig12_datachain/11_消费端需求反查.md §1A |
| SSOT 真源 | 槽位/任务/档期唯一真源=tasks.yaml+schedule.yaml（机生层全量重建）；语义层=图12 DSC-01 节点块 | src/zephyr/data/config/tasks.yaml（275 任务唯一、duplicate_task_ids=[]——cohort_ledger_daily 重复 E-4 已修）；src/zephyr/data/config/schedule.yaml（33 槽）；config/data_supply_chain_map.yaml machine.tasks_yaml |
| 代码模块 | module_id=MOD-L00-004，module_ref=src/zephyr/data/scheduler.py；执行体 scheduler.py+provider_base.py 均实存（本批 ls 核实） | src/zephyr/data/scheduler.py；src/zephyr/data/provider_base.py |
| 门禁约束 | 图法条：INV-1 引用不复制、挂槽≠在跑、新鲜度主口径=max(date)+近窗计数（UTC 折北京）、静默失败即假绿、ReplacingMergeTree 判真必 FINAL 双版并报；硬规则 RULE-DATA-OPS/RULE-SCHEMA-TZ 约束其下游写面 | config/data_supply_chain_map.yaml laws 块；AGENTS.md §1 RULE-DATA-OPS；AGENTS.md §11.1.1（RULE-SCHEMA-TZ） |
| 自动化触发 | wired_cron：六槽全部 in_schedule=true（机生 task_count：daily_capital 45/weekend_calibration 44/daily_event 42/daily_kline 37[special_dispatch]/monthly_static 21/nightly_financial 10）；task_runs 打卡腿=批次4 升级（7 日窗 480 笔/期望 961，verdict=alive） | config/data_supply_chain_map.yaml#DSC-01 machine.slots+trigger_facts（as_of 2026-10-04）；data/integrator_progress.db task_runs（本批复读 233,587 行 max=2026-10-15T13:30Z） |

## 3. 自审闸三态

| 向 | 三态 | 判据（本批复核 2026-10-15） |
|---|---|---|
| 输入面 | pass | 23 源面/provider 归一/副源清单在册且文件实存；今日 data/failures 仍产源侧失败件（circuit_breaker_fred 族 10+件）=源熔断在岗留痕 |
| 输出面 | pass | kline_daily max=2026-10-15 FINAL 直查 lag=0；消费锚三族在册 |
| SSOT 真源 | pass | tasks/schedule/图三层同源机生；旧缺口 cohort_ledger_daily 重复 task_id 已清（machine 现值 duplicate_task_ids=[]，地图语义层 trigger_facts 照录旧值=仅注记滞后） |
| 代码模块 | pass | 两执行体实存（本批 ls） |
| 门禁约束 | pass | laws 六条全挂；FINAL 双版并报在本批复跑中实际执行 |
| 自动化触发 | warn | 六槽 cron 在机、task_runs alive；但 7 日窗观测 480 vs 期望 961（月/周末腿期望折算差异大）、monthly_static 子族档期级执行不可证（20 表仅 4 表两日内有写）、weekend_calibration dow 双口径冲突未销——档期级完备性带限定 |

## 4. 缺口与建议

1. 【warn 持续】monthly_static 月度子族"档期级执行不可证"（图 gaps 在册，measured 09-24）：建议以 DSC-20 四计数案卷按槽聚合出月腿专项读数，把"月腿窗内 0 发"从期望折算争议变成机械计数。
2. 【warn 持续】weekend_calibration crontab dow 双口径（0=周日 vs APScheduler 0=周一）：建议在 schedule.yaml 逐槽加注释锚钉死口径，消灭第二解释空间。
3. 【已闭合，留痕】cohort_ledger_daily 全仓唯一重复 task_id 已在 tasks.yaml 侧清零（machine 现值无重复）；建议图语义层 trigger_facts 的"271/270 duplicate 口径（E-4 未修照录）"注记随下次重生成刷新。
4. 【机制在岗】副源长期顶班无收敛指标（LEVEL_ERROR 告警逐次发）：建议给 fallback_sources 使用率加周聚合读数，收敛判据挂 DSC-13 哨兵阈值面。
