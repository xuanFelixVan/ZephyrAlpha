---
ttl: task_bound
doc_type: mined_segment
parent_map: config/trading_day_cycle_map.yaml
segment: fig13-D (夜窗/贯穿段)
node_id: D13-43
miner_lane: mine_fullchain_20261015/daily_ops_pm
created: 2026-10-15
---

# SD13-43 交易日历闸门（本图不变量载体：事件触发禁定时器）

## 1. 定义

全图不变量载体：每槽触发时实查交易日历（无独立时点，全日每拍实查），非交易日由日历守卫名单
（src/zephyr/data/trading_calendar.py:151 TRADING_DAY_GUARDED_SCHEDULES）显式 SKIP
（生效实证=非交易日会话拉起腿 SKIP(is_trading_day=False)）；守卫名单外槽集靠底层幂等闸吸收。
铁律真源=图 9 laws 第 3 条与宪法运维红线 §9.3（事件触发禁定时器），本图不复制正文。
图内决策问题："今天该不该跑？这一拍是被守卫跳掉还是被幂等吸收？"——已知表达缺口：
guards_only_subset=true（少数槽受守卫，"无守卫是有意还是漏配"读不出）；
calendar_gated 三值（true/false/null）的 null 语义与补填义务留总包（benchmark C5）。

## 2. 六向台账

### 2.1 输入面
- 交易日历本身（保守判据前置）；各槽触发事件（机制=C_inprocess_stage，随每槽触发实查）。
- 入边：D13-42→D13-43（守护→日历，贯穿链）。

### 2.2 输出面
- 判定输出：SKIP（非交易日守卫命中）/放行（守卫名单内交易日）/放行（名单外，幂等吸收）。
- 守卫名单覆盖：本段 machine_facts 中 calendar_guarded=true 的槽=eod_reconciliation/daily_kline/
  daily_backfill/daily_capital/daily_event/nightly_financial/integrity_check/cross_validation；
  =false 的槽=sector_close_final/dloop_post/research_nightly/consensus_crosscheck/daily_alt_fx/
  weekend 三槽/monthly_static（图 13 全图守卫槽 11/32，counts.machine.calendar_guarded_slot_total=11）。
- consumers=count:16（code=11,doc=4：architecture_issue_registry.yaml:10007、
  54_d_gov_scripts.md:12627、data_source_integrator_blueprint.md:479、
  docs/03_modules/_domain_data/catchup_guard/blueprint.md:66）。

### 2.3 SSOT 真源
- config/trading_day_cycle_map.yaml#D13-43（wired/partial/🔨）。
- 铁律：宪法 AGENTS.md §9.3（事件触发禁定时器）+图 9 laws 第 3 条（不复制正文）。
- 名单真源：src/zephyr/data/trading_calendar.py:151 TRADING_DAY_GUARDED_SCHEDULES
  （本批实读精确命中）；不进名单的例外注记=schedule.yaml:200-201（catchup_guard：守卫本身须
  非交易日可跑）。

### 2.4 代码模块
- module_id=MOD-L00-004；module_ref=src/zephyr/data/trading_calendar.py:151（精确锚）；
  scheduler.py:184（map 锚已漂移，当前行内容=Args docstring）。
- 伴随件：src/zephyr/data/calendar_coverage_checker.py（D13-03 日历逐日 diff，A 段，本段不重复）。

### 2.5 门禁约束
- guards_only_subset=true：守卫覆盖是子集，名单外"有意还是漏配"不可读（表达缺口在册）。
- gap_refs：benchmark:C5-calendar_gated 三值 null 语义+补填义务留总包；本图只登记表达缺口，
  不改守卫名单。
- casebooks=MEM-F13#日历与周窗。

### 2.6 自动化触发
- 机制=C_inprocess_stage（每槽触发时实查，无独立时点/无独立产物表面）；trigger_facts metric=none
  （事件触发段无独立产物表面）；counts.machine.calendar_guarded_slot_total=11（slot_total=32）。

## 3. 自审闸三态（逐向）

| 向 | 态 | 判据 |
|---|---|---|
| 输入面 | pass | 日历+触发事件面清晰（保守判据前置在册） |
| 输出面 | warn | SKIP/放行判定实存且名单实扫（11/32），但 null 语义缺口=覆盖面意图不可读 |
| SSOT 真源 | pass | 宪法红线+图 9 laws+代码名单三层齐（精确锚命中） |
| 代码模块 | warn | trading_calendar.py 精确；scheduler.py:184 锚漂移 |
| 门禁约束 | warn | guards_only_subset 的"有意/漏配"不可读+null 补填义务留总包（留裁项） |
| 自动化触发 | warn | 事件触发段无计数面（by design），节拍=槽触发隐含 |

## 4. 缺口与建议

- 本段 4 gap+11 未接线归属：不在主清单（wired）；C5 null 语义留裁是其门禁向登记项。
- 建议：calendar_gated 补第三值语义——名单外槽显式声明 null（有意豁免）或 false（待补配），
  与 catchup_guard"守卫须非交易日可跑"同款例外注记逐槽落座，消除"漏配读不出"。
