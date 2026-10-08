---
ttl: task_bound
completes_when: 战役收尾（99_final_delivery 落账）后随役归档 archive/2026-10
---

# [BLUEPRINT] | docs/_working/chief_fullchain_20261006/env_mining/env_06d_nightwindow.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# ENV-06d 夜窗与贯穿段（20:00–次日 05:30 + 全日不变量）挖矿作业簿（B1 批次，2026-10-06）

## §0 环节档案

- **真源锚**：FIG13 车道 `docs/_working/map_build/fig13_daycycle/`（00_skeleton.md §2 段 D + 簿09 + 簿01 §2 托管巡检面）；机生图 `config/trading_day_cycle_map.yaml` segments.D（purpose_tag t11/t12/t13）。
- **现役挖掘 = st-fig13-bone-20261004**。本簿只读其领地；价值=①挂接收编 ②补代码消费面/字段面 ③本役三态裁定。
- **职责一句话**：夜窗="白天的账在这里对完、明天的状态在这里交出去"——研报/财务/巡检/一致预期/汇率五槽+周月批+守护三路+日历闸+日界交接；本段实测总线：五槽全 firing 但四路"检出"没接"动手"，日界交接是唯一"执行体活着、产出因变量名 bug 而死"的链。
- **节点与状态（图本体 2026-10-06 机生读数，10 节点）**：🔨9（D13-36/37/38*/39/40/41/42/43/47；* 簿09 升 ✅ 抓到 09-23 23:01 30 条产物，图镜像滞后）｜⬜1（D13-44 日界交接——簿09 改判 🔨 并锁定根因，recheck=🔨 已在册）。

## §1 六向台账

| 向 | 内部反查发现（带路径） | 外部 | 判定 |
|---|---|---|---|
| 上（谁触发） | 夜窗五槽全机制 A（research_nightly 20:30/nightly_financial 22:00/integrity_check 23:00/consensus_crosscheck 00:30 跨午夜已移窗/daily_alt_fx 23:35）+ 周月批三槽（weekend_backfill 周一 02:00/weekend_calibration 周一 03:00/monthly_static 月初 09:16）；贯穿段=AtLogOn+每 5 分钟重点火（`register_guard_tasks.ps1:46-52`）；D13-43 日历守卫实测 9/29 槽（`trading_calendar.py:151-163`），簿09 补"夜窗三槽全不在守卫内" | GOMAP 让渡：守护主体（C4Exam/ModelExam/GateFullTreeAudit ~28 schtasks）归治理夜班图，本图只留三接缝（09:25 前谁须活/15:05 后谁该退/心跳缺失算不算当日 FAIL） | signal |
| 下（谁消费） | **本簿补充·代码消费面**：①`consensus_daily` 是 D13-39 双向验证 ours 侧唯一输入（`consensus_crosscheck.py:73-81` `_SQL_OURS_DAY/_SQL_OURS_FRESH` 全限定）——上游停 8 交易日→下游每日 2 条 fail，夜窗唯一"上游停→下游检出的正是上游停"完整因果链（簿09 §1.3）；②D13-44 断供根因=`next_day_forecaster.py:268-271,294` 变量名错位把预期振幅喂成均值次日收益→负值被 `judgment_ledger.py:273-275` payload 校验 fail-closed 拒发，按桶确定性杀 30 个交易日中 21 个；下游 daily_plan **不静默**——按业务日精确查、查不到明写 absent 并 confidence×0.9（0.90→0.81 实测），真正静默的是 dloop 段 6 硬编码 ok 与校准腿（簿09 总线②）；③净值序列 `c1_market.account_nav_daily` 的存活度分析消费面在 `infrastructure/system_telemetry/alerts/ops_alert_feed.py:39,192-228`（ SurvivalInput）——供料腿 2026-09-29 已由 st-c9-emptyfill 接入 15:30 结算管线（详见 env_15 簿） | catchup_guard 基准+CLI status+告警件三族吃 DSC-20 任务级对账案卷（图12，本簿只记接缝） | signal |
| 内（子环节） | D13-38 完整性巡检=第 4 类检核"档期应跑集合 vs task_runs 打卡集合差四计数"——**全图唯一能机械证明漏跑真实存在的机生件**（图12 DSC-20 行级，wired_special_branch）；D13-02 托管 quality_sentinel 变异巡检 7 天节奏闸（`config/quality_sentinel_tables.yaml` wiring 块，报告文件名即状态真源）挂本段宿主 `supply_sentinel.py:532-555`；D13-41 dow 双口径事故：L125"0=周日"实测与 L139"APScheduler 0=周一"注释互斥，09-23"根因修复"把对的改成错的——weekend_calibration 现落周二 03:00（红条目在册） | 周月批时序语义跨日界，APScheduler dow 机械化判定（CronTrigger 逐日展开）已在簿02 §3 实测方法论 | signal |
| 旁（撞车面） | 夜窗四路检测分工：06:50 sentinel（新鲜度）/07:10 coverage（逐日 diff）/17:00 backfill（行数缺口，唯一动手）/23:00 integrity（达标四计数）——分工真源= schedule.yaml 散文注释，fig13 簿01/08/09 已变三条边；告警纪律=webhook 只发 CRITICAL+task_id 冷却→06:50 一夜 11 条检出只 1 条留可操作产物（簿09 §3.3）；D13-36/37 断供 4/8/4 交易日而 sentinel 58 条目不含 research_report/consensus_daily/margin_trading——**检测真空是配置面事实**（簿09 §1.4） | 与 DSC-13（图12 完整性巡检+哨兵族）同码同读两图各记账不互抄 | signal |
| 史 | D13-44 曾为四段唯一"名义在产实测断链"格（骨架 09-24），簿09 升级为可复现根因（变量名错位）——从"断供"改"产出被校验器正确拒绝"：**链是活的，喂的值是错的**，修复=一行变量名+补发校准；D13-41 周窗 09-20 未 firing 致 daban 链断 5 日的上游根因在册 | 57 号 SOP 六环节不含夜窗槽（晚于归档出生） | signal |
| 新 | fig13 溢出在册：D13-40 假红（ECB 保守游标被 23:00 巡检判永久漏跑——巡检阈值不认识"假日缺价保守游标"语义）、D13-39 检查面自身坍缩（per-symbol 腿 09-21 起零行）、`derived_table_lag_days` 字段提案（consensus_daily 比原料多滞后 4 交易日）；**本簿补**：D13-42 三路心跳中 `live_strategy_biz` 心跳冻在 15:05:07=收口设计态——"冻值"与"死进程"在心跳面上同形，`heartbeat_stale_reason`（设计态/真失联）字段缺口本簿登记 | 无 | signal |

## §2 挖干自评

- **三扫收敛**：簿09 单簿覆盖 9 节点（449 行，本段最厚簿），六向齐+断供根因全部锁定；本役补面（消费面/心跳字段面）后增量归零。
- **长尾**：①D13-44 修复体量最小收益最大（一行变量名+补发），但属 plan_engine 域施工，须 fig13 封矿+施工令；②D13-41 dow 口径须机械化判定器（非读注释）——簿02 §3 的 CronTrigger 展开法已验证可复用；③夜窗检测真空（3 表不入 sentinel 名单）是 YAML 配置补条目，最小施工件。
- **🌑 清点**：无新增 🌑（本段无不可得项；D13-44 曾疑似 🌑 已被簿09 根因化消解）。

## §3 挖后自审闸三态裁定

**挂起排期**（内含一个"低成本可先行"备注）。
- 理由：①10 节点全部经簿09 六向挖透且断供根因可复现，本役无独有矿脉；②施工方向收敛为三类：修 bug（D13-44 一行）、补配置（sentinel 名单 3 表、dow 判定器）、落字段（heartbeat_stale_reason/derived_table_lag_days）——全部应随图本体施工批整批落，零散施工会绕过 claim/gate 纪律；③D13-41 红条目（周末校准落周二）是现役在咬的时序事故，但其修复（改 cron 或改注释取一）涉及"时刻值不搬家"让渡——时刻真源在 schedule.yaml，图13 车道禁改，回传排班体系处置。
- 解锁条件：fig13 封矿 → 三类施工项随图本体施工批排期；D13-41 时序事故回传排班战役（非本役解锁项）。

## §4 挖矿日志

| 轮 | 矿脉 | 判定 | 产出 |
|---|---|---|---|
| 1 | 读簿09 全文（总线+§0+§1/§6 关键节） | 挂接完成：D13-44 根因化改判、D13-38 升 ✅、D13-40 假红、D13-41 红条目收编 | §0/§1 |
| 2 | 机生图 segments.D 解析对表 | signal：D13-38 图镜像滞后（🔨 vs 簿09 ✅）、D13-44 recheck=🔨 已在册 | §0 状态行 |
| 3 | 消费面复核：consensus_crosscheck SQL 真源/account_nav_daily 消费方/心跳面字段 | signal：存活度分析消费面与 15:30 供料腿的接线状态归 env_15；heartbeat_stale_reason 字段缺口为本簿新增登记 | §1 下/新 向 |
| 4 | 三态裁定自审 | 挂起排期成立；D13-41 回传排班体系显式化 | §3 |
