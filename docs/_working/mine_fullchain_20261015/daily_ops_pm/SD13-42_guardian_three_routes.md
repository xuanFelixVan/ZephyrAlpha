---
ttl: task_bound
doc_type: mined_segment
parent_map: config/trading_day_cycle_map.yaml
segment: fig13-D (夜窗/贯穿段)
node_id: D13-42
miner_lane: mine_fullchain_20261015/daily_ops_pm
created: 2026-10-15
---

# SD13-42 常驻守护三路（reaper / deadman 心跳 / guard 三件套）

## 1. 定义

ps1 注册守护族（登录时+每 5 分钟重点火）：process_reaper（收割）/deadman 心跳/guard 三件套，
另含 DataScheduler/TickSubscriber/TradingWatchdog 等/trading 服务拉起。单实例唯一真源=脚本级
PID 锁+心跳判定（计划任务必须不参与单实例决策——两日静默死亡根因已锁在此）；一台看门狗
（ZephyrAlpha_TradingWatchdog）按裁定（INT-03，92 D3 ruling）注册于禁用态。主体让渡 GOMAP
（图 boundary 第 5 条），本图只留日序接缝三点：09:25 前谁必须活着、15:05 后谁该退、心跳缺失
是否当日 FAIL。图内决策问题即此三点。

## 2. 六向台账

### 2.1 输入面
- 全域进程/心跳面（.runtime/ 心跳文件族）；晨间重启风暴与 D13-01 长批夭亡同时点（簿 01 O-2，
  重启主体与节律归 GOMAP，日序风险本图记账）。
- 入边/出边：feedback edge D13-42→D13-12（心跳陈旧→计划任务重跑拉起腿——09:25 前必须活着是
  日序前置）；边 D13-42→D13-43。

### 2.2 输出面
- 产物：心跳文件+deadman 告警；陈旧则由计划任务重跑（fallback 在册）。
- consumers=count:33（code=17,doc=13：src/zephyr/ex_core/live_strategy_adapter.py:355、
  src/zephyr/feedback_loop/resilience/deadman_switch.py:2、
  src/zephyr/feedback_loop/resilience/__init__.py:21、
  src/zephyr/frontend/dashboard/api_server.py:5108）。
- downstream_action=auto_remediate（本段唯一自动补位格之一）。

### 2.3 SSOT 真源
- config/trading_day_cycle_map.yaml#D13-42（wired/partial/🔨）。
- 簿 01 O-2+骨架 §2 D13-42 行（静默死亡根因+看门狗禁用态在案）；
  docs/_working/map_build/fig13_daycycle/09_夜窗与日界贯穿.md。
- 注册契约：scripts/tasks/register/register_guard_tasks.ps1（:33 INT-03 看门狗裁定注记、
  :46 任务表、:118 $tradingSvc 看门狗注册行）；scripts/deadman_switch.ps1:138。

### 2.4 代码模块
- module_id=MOD-L00-004；module_ref=scripts/tasks/register/register_guard_tasks.ps1:20
  （注册守卫任务）。
- 服务件：src/zephyr/trading/process_reaper.py（宪法 RULE-GUARDIAN 真源件，实存）；
  src/zephyr/feedback_loop/resilience/deadman_switch.py（consumers 命中）。

### 2.5 门禁约束
- 宪法 RULE-GUARDIAN：reaper 计划任务存活是写操作前提（本格是宪法硬规则在图 13 的挂点）；
  长批任务须登记 data/runtime/process_reaper_keep.txt 防误杀。
- 单实例纪律：脚本级 PID 锁+心跳判定，计划任务禁参与单实例决策（静默死亡根因修复约束）。
- casebooks：AP#域一、RV2#缺口、RV2#观察、MEM-F13#守护判活与误杀、MEM-F13#计划任务静默
  （本段案例挂靠最密格，5 件）。

### 2.6 自动化触发
- 机制=B_windows_task；schtasks 五件：ZephyrAlpha_ProcessReaper/ZephyrAlpha_DeadmanSwitch/
  ZephyrAlpha_DataScheduler/ZephyrAlpha_TickSubscriber/ZephyrAlpha_TradingWatchdog——
  machine_facts：五件 registered=true 且 declared_in_register_scripts=true（双证满格）。
- trigger_facts：count=4（TradingWatchdog 视角，last_run=2026-10-08T15:49:23，禁用态按裁定
  仍留注册面）；cadence declared"登录时+每 5 分钟重点火"、observed"每 5 分钟重点火"。

## 3. 自审闸三态（逐向）

| 向 | 态 | 判据 |
|---|---|---|
| 输入面 | pass | 心跳面+重启风暴记账清晰（主体让渡边界明确） |
| 输出面 | pass | 心跳文件+deadman 告警+33 条 consumers+auto_remediate |
| SSOT 真源 | pass | 注册脚本裁定注记（INT-03）+簿 01+骨架三层齐 |
| 代码模块 | pass | register_guard_tasks.ps1/deadman_switch.ps1/process_reaper.py 实存 |
| 门禁约束 | warn | 看门狗一台禁用态（裁定内）；静默死亡根因修复约束靠纪律维持；宪法 RULE-GUARDIAN 挂点责任重 |
| 自动化触发 | pass | 五件 schtasks 双证满格+5 分钟节拍在窗 |

## 4. 缺口与建议

- 本段 4 gap+11 未接线归属：不在主清单（wired）。
- 建议：日序接缝三点（09:25 活/15:05 退/心跳缺失=FAIL?）目前只有接缝一有边（42→12），
  建议把"心跳缺失是否构成当日 FAIL"落为图面判定字段（当前 cadence/miss_policy 未覆盖该问），
  避免三点问题只剩一点有答案。
