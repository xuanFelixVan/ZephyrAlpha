---
ttl: task_bound
doc_type: mined_segment
parent_map: config/trading_day_cycle_map.yaml
segment: fig13-D (夜窗段)
node_id: D13-41
miner_lane: mine_fullchain_20261015/daily_ops_pm
created: 2026-10-15
---

# SD13-41 周批与月批（跨过日界的重活）

## 1. 定义

三槽合并节点（特殊槽分支+两 DAG 槽）：weekend_calibration（周一 03:00 heavy，周末后校准）、
weekend_backfill（"周一"02:00 heavy，周末补下载）、monthly_static（月初 09:00，静态层 20 任务）。
图内决策问题："周窗真在意图中的那天 firing 吗？口径注释互斥时以哪条为准？"——已知在册时钟事故
两起：同一文件内两条互斥星期口径断言（weekend_calibration 修复注记称"crontab 0=周日"已于
09-23 改 "1"=周一；weekend_backfill 注释却称"APScheduler 0=周一，非周日"且 cron 仍为
"00 2 * * 0"）；且周窗未 firing 已咬过一次（09-20，上游链断多日）。图不裁口径（dow_semantics_conflict
=true，判定归机生层与实查）。

## 2. 六向台账

### 2.1 输入面
- QMT 可达+避开晨维护窗（no_ready_gate_reason：周一凌晨已堆 L10 02:00+L8 03:00 两件重活）。
- 入边：D13-01→D13-41（档期对账兜底入边）、D13-41→D13-44（map edges）。
- 历史断供：09-20 周窗未 firing（daban 链断 09-15 起 5 日上游，schedule.yaml:149 注记）。

### 2.2 输出面
- 产物：全量校准/TDX板块/概念板块/美股全量（L8）、过去 7 天缺失 tick/K线补下载（L10）、
  股票列表/板块分类/指数成分/交易日历（L9 月初静态）。
- consumers=count:33（code=7,config=1,doc=22：src/zephyr/frontend/dashboard/api_server.py:1626、
  architecture_issue_registry.yaml:2548、10_d_data.md:14598、data_acquisition_flow.md:562）。

### 2.3 SSOT 真源
- config/trading_day_cycle_map.yaml#D13-41（wiring=partial，red_reason=unwired，🔨）。
- 簿 09（机械抽取：守卫成员数与排班槽总数比值在案，未守卫槽名单已逐名列出）；
  骨架 §2 D13-41 行（互斥口径断言+事故在案）。
- 槽契约：src/zephyr/data/config/schedule.yaml:141-150（weekend_calibration，
  2026-09-23 st-emomine-20260923 根因修复注记）、:152-156（monthly_static）、:158-163
  （weekend_backfill，"APScheduler 0=周一"注记）；map 锚 :119/:125/:136 已漂移。

### 2.4 代码模块
- module_id=MOD-L00-004；module_ref=src/zephyr/data/scheduler.py（实存）。
- machine_facts：weekend_backfill=1 任务+special_branch_exists=true；
  weekend_calibration=43 任务；monthly_static=20 任务；三槽 in_catchup_universe=true、
  calendar_guarded=false。

### 2.5 门禁约束
- dow_semantics_conflict=true：互斥口径在册，机械判定前任何"周窗未 firing"结论作废
  （invalidation 在册）。
- fallback=D13-01（weekly/monthly 桶在册，miss_policy=rerun）——cron 错过由 05:30 catchup_guard
  治本兜底（schedule.yaml:193-197 分工注记）。
- casebooks=MEM-F13#日历与周窗。

### 2.6 自动化触发
- 机制=A_apscheduler；三槽 cron："00 3 * * 1"（calibration）、"00 2 * * 0"（backfill）、
  "16 9 1 * *"（monthly）。
- trigger_facts：task_runs_30d=0（slot=weekend_backfill 任务级求和×1——唯一挂载任务 30 日窗
  0 拍，与互斥口径疑云同向：若 0 实际=周日，QMT 不可达即恒不 firing）。

## 3. 自审闸三态（逐向）

| 向 | 态 | 判据 |
|---|---|---|
| 输入面 | warn | QMT 周末不可达约束在册；晨维护窗错峰已修（calibration 已改周一） |
| 输出面 | pass | 三腿产物面+33 条 consumers 在册 |
| SSOT 真源 | fail | 同一文件两条互斥星期口径断言在册（dow_semantics_conflict=true），SSOT 面自相矛盾 |
| 代码模块 | pass | scheduler+三槽声明实存（map 锚漂移但槽面精确） |
| 门禁约束 | pass | fallback=D13-01 在册+invalidation 判据清晰（互斥判定前不作 firing 结论） |
| 自动化触发 | fail | weekend_backfill 唯一任务 30 日窗 0 拍（trigger_facts 实证），周窗腿疑恒缺勤 |

## 4. 缺口与建议

- 本段 4 gap+11 未接线归属：不在主清单（partial/red_reason=unwired 属一般部分接线），
  但 0 拍实证使其接近 hollow 实质。
- 建议 1：dow 口径机械裁定收口——用 APScheduler 实际解析行为（schedule_overview/机生层实查）
  定 weekend_backfill "0" 的真值，统一两处注释口径；若实查=周日，改 "1" 同 calibration 修复。
- 建议 2：weekend_backfill 0 拍腿优先修——它是 L10 补下载本体，恒缺勤=tick 缺口全靠 17:00
  daily_backfill 单腿承接。
