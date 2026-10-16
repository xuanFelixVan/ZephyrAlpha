---
ttl: task_bound
doc_type: mined_segment
parent_map: config/trading_day_cycle_map.yaml
segment: fig13-C (盘后段)
node_id: D13-26
miner_lane: mine_fullchain_20261015/daily_ops_pm
created: 2026-10-15
---

# SD13-26 指数分钟K日终补拉（峰谷下跌段探测器供料）

## 1. 定义

交易日 15:10（Windows 计划任务 ZephyrAlpha_IndexMinuteEOD）对 SSE 指数 1 分钟K做日终补拉并落
行情表，供峰谷下跌段探测器（counter-trend feeder 族）当日供料；主源失败另有降级源腿且留痕。
图内决策问题："15:10 拉到根数了吗？主源失败降级有没有留痕？"——骨架实查：末次拉取根数与源
标注在 logs/index_minute_eod.log，上一行即源失败降级记录（降级腿亦有留痕=真在跑的第二证）。
本环节是 C 段 wired/built/✅ 三证齐的样板格。

## 2. 六向台账

### 2.1 输入面
- 交易所分钟行情源（主源+降级源两腿）：scripts/tasks/register/register_counter_trend_feeder_tasks.ps1:14
  （tn 声明面：ZephyrAlpha_IndexMinuteEOD - SSE index 1m-K EOD backfill at 15:10）。
- 运行留痕：logs/index_minute_eod.log（实存，末次根数+源标注）。

### 2.2 输出面
- 产物：指数 1 分钟K落行情表（探测器供料）；consumers=count:5（code=4,config=1，含
  config/resource_profile_registry.yaml:1793、generate_trading_day_cycle_map.py:852/1544）。
- 下游：边 D13-24→D13-26、D13-26→D13-28（map edges）。

### 2.3 SSOT 真源
- config/trading_day_cycle_map.yaml#D13-26（wired/built/✅，verified_scope=production）。
- docs/_working/map_build/fig13_daycycle/00_skeleton.md §2 D13-26；
  docs/_working/map_build/fig13_daycycle/06_盘后结算与三账.md（簿 06）。
- 注册脚本注释即触发契约：register_counter_trend_feeder_tasks.ps1:14/86。

### 2.4 代码模块
- 注册器：scripts/tasks/register/register_counter_trend_feeder_tasks.ps1:86（map 锚；本批实读
  :14 命中 tn 声明，锚行内容可复核）。
- 产物留痕：logs/index_minute_eod.log（主区只读 tail 复跑路径在 exec_evidence 在册）。

### 2.5 门禁约束
- casebooks=MEM-F13#计划任务静默（计划任务静默失败族案例挂靠）。
- fallback=无（缺则下跌段探测器无料）；miss_policy=absorb——缺日内补拉无自动兜底，
  只能等次日 15:10 重跑。
- ready_gate=false + no_ready_gate_reason_zh 在册（前置"收盘（交易所时钟）"由入边承载）。

### 2.6 自动化触发
- 机制=B_windows_task；schtasks=ZephyrAlpha_IndexMinuteEOD（registered=true、
  declared_in_register_scripts=true，machine_facts.schtasks_facts 实扫）。
- trigger_facts：schtasks_lastrun_in_window count=1，last_run=2026-10-08T15:10:01
  （Get-ScheduledTaskInfo 只读查询，240h 节拍窗）。

## 3. 自审闸三态（逐向）

| 向 | 态 | 判据 |
|---|---|---|
| 输入面 | pass | 主源+降级源两腿在注册脚本声明面；运行日志实存 |
| 输出面 | pass | consumers 机生计数 5 条在册；探测器供料链在图 |
| SSOT 真源 | pass | 图节点+簿 06+骨架+注册脚本四层一致 |
| 代码模块 | pass | register_counter_trend_feeder_tasks.ps1 实存且锚行命中 |
| 门禁约束 | warn | fallback=无、miss_policy=absorb：缺拍时探测器当日无料且无告警主体（声明为 none 而非缺陷，但属单点） |
| 自动化触发 | pass | schtasks 双证（registered+declared）+last_run 在窗 |

## 4. 缺口与建议

- 不在本段 4 gap/11 未接线清单内（wired/built）。
- 建议：fallback=无 属声明性单点——峰谷下跌段探测器若依赖当日 1mK，可挂入 D13-38 23:00 巡检
  行数阈值名单（配置=config/data_supply_sentinel.yaml 面），把"缺则无料"变成"缺则有告警"。
