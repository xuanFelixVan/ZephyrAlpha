---
ttl: task_bound
doc_type: mined_segment
parent_map: config/trading_day_cycle_map.yaml
segment: fig13-C (盘后段)
node_id: D13-35
miner_lane: mine_fullchain_20261015/daily_ops_pm
created: 2026-10-15
---

# SD13-35 盘后数据批次群（资金面·事件·当日补下载）

## 1. 定义

三拍批次节点（内部结构归图 12，让渡三）：17:00 daily_backfill（行数视角补下载——本段唯一
"有手"腿，src/zephyr/data/backfill_checker.py）、18:00 daily_capital（资金面 39 任务）、
19:00 daily_event（事件面 40 任务）。图内决策问题："三拍各自动手了吗？17:00 补下载有没有把
'仍在跑'误判为'缺'？"——已知真缺陷（簿 08 X-11）：16:30 heavy 批未收口时 17:00 补下载把
"仍在跑"误判为"缺"，同一任务两实例并发写同一表、flush 行序交错；17:00 腿缺"daily_kline 批次
已收口"前置（ready_gate_absent_zh 在册=本图可红用例）。

## 2. 六向台账

### 2.1 输入面
- 三槽输入：daily_backfill/daily_capital/daily_event（slot_refs 在册）；machine_facts：
  daily_backfill effective_task_count=0+special_branch_exists=true（特殊槽编排面）、
  daily_capital=39、daily_event=40；三槽 calendar_guarded 与 in_catchup_universe 全 true。
- 就绪门入边：D13-30→D13-35（admission edge=应然；实然=前置缺失，缺格事实记 ready_gate_absent_zh）。
- 圈入边：D13-32→D13-35；兜底=D13-01 档期视角/D13-38 仅告警。

### 2.2 输出面
- 产物：资金流向/龙虎榜/大宗/期货/股本变动/限售解禁/美股（18:00 槽 description）、分析师预期/
  财报快报/审计/分红配股/质押/披露计划（19:00 槽）、当日缺口补下载行数（17:00 腿）。
- consumers=count:30（code=13：src/zephyr/frontend/dashboard/api_server.py:1627、
  architecture_issue_registry.yaml:10005、ruling_registry.yaml:3754、
  docs/03_modules/_domain_data/catchup_guard/blueprint.md:27）。
- downstream_action=auto_remediate（17:00 腿有手）；miss_policy=rerun。

### 2.3 SSOT 真源
- config/trading_day_cycle_map.yaml#D13-35（partial/built/✅，red_reason=unwired）。
- 簿 08（X-11 并发写）；docs/_working/map_build/fig13_daycycle/08_盘后批次与当日回测.md。
- 槽契约：src/zephyr/data/config/schedule.yaml:84-94（capital/event）、:165-173（daily_backfill，
  治本#ARCH-DATA-TICK-GAP-001 注记）；map 锚 :148 已漂移至 :170。

### 2.4 代码模块
- module_id=MOD-L00-004；module_ref=src/zephyr/data/backfill_checker.py（实存，"L10 周末补下载
  检测器——检测过去N天缺失数据并精准补下载"）。daily_backfill 槽 0 有效任务+特殊槽分支=
  执行面靠 _run_special_schedule 白名单（防 R-021 假通道）。

### 2.5 门禁约束
- ready_gate_absent_zh：17:00 腿缺"daily_kline 批次已收口"前置（本图可红用例，admission edge
  D13-30→35 应然而非实然）——本段实名 fail 项。
- gap_refs benchmark:C1：rerun 措辞权留总包（17:00 补下载是"有手"腿）。
- casebooks=MEM-F13#断供补数。

### 2.6 自动化触发
- 机制=A_apscheduler；三拍 cron：17:00 "00 17 * * 0-4"/18:00 "00 18 * * 0-4"/19:00 "00 19 * * 0-4"
  （schedule.yaml 实读）。
- trigger_facts：task_runs_30d=0（slot=daily_backfill 任务级求和×0）——三拍中补下载腿计数面为 0；
  资金面/事件面挂载数实（39/40）但 trigger_facts 只取了 daily_backfill 视角。

## 3. 自审闸三态（逐向）

| 向 | 态 | 判据 |
|---|---|---|
| 输入面 | warn | 三槽在册且守卫/补跑宇宙全 true；但就绪门前置实然缺失（16:30 收口无标记） |
| 输出面 | pass | 资金/事件两腿产物面实（39+40 任务）、consumers 30 条、有手腿在册 |
| SSOT 真源 | warn | 槽契约在 schedule.yaml（锚漂移 148→170）；X-11 缺陷与治本注记在册未收口 |
| 代码模块 | pass | backfill_checker.py+三槽声明面实存 |
| 门禁约束 | fail | ready_gate_absent_zh=实名缺门（17:00 腿无收口前置闸→两实例并发写真缺陷） |
| 自动化触发 | warn | 17:00 补下载腿 task_runs=0（特殊槽编排面无计数）；18/19 拍挂载实但本格 trigger 视角单一 |

## 4. 缺口与建议

- 本段 4 gap+11 未接线归属：本格 wiring=partial/red_reason=unwired，不在 4 gap/6 no_caller/
  5 hollow 主清单，但其 ready_gate_absent 是 admission_edges 顶层登记的两条"应然边"之一。
- 建议 1：给 16:30 heavy 批落"收口完成"水位标记（表侧 max(trade_date)+标的数看门铃已现成），
  daily_backfill 以此为前置闸——一次性收掉 X-11 并发写与缺门两案。
- 建议 2：daily_backfill 腿补圈级/槽级心跳行（同 D13-32 建议 2），消除 0 计数面。
