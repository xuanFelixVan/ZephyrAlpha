---
ttl: task_bound
---

# lane_pipe · auto_runtime_trading（AutoRuntime Core 实盘运行时入口）— 判定：不通 ❌（"全部能运行"口径）/ 待裁（是否应常备）

## 六向台账

### 1 做什么
`python -m zephyr.trading` = AutoRuntime Core 主循环（CLI 触发启动后自动运行 reconcile 循环 + 信号→下单→风控），是"业务能运行"的顶层执行链。

### 2 依据
- 入口在册：`src/zephyr/trading/__main__.py` 头标 `[MATURITY] production` / `[STARTUP] manual`（M02/M10 豁免：CLI 心跳轮询设计）。
- 计划任务在册：`ZephyrAlpha_TradingWatchdog` → `scripts/start_trading.ps1`，State=**Disabled**，LastRunTime=1999-11-30（从未成功跑）。
- 宪法 §7 列其为"核心系统"，§9.3 要求永久系统四要素（自动触发/运行/维护/关闭）。

### 3 改动点（不改，门位/设计裁量）
- 无实盘进程：`Get-CimInstance` 过滤 `zephyr.trading|auto_runtime` **无**（仅 process_reaper 子进程在册）。
- 唯一产出面 `c1_market.execution_report` 仅 **1 行 · 2026-09-18**（结算/成交报告近乎停摆，连带 #47 对账）。
- 现行业态疑为 模拟盘/仿真桥（#45 PaperSession、#46 SimBridge 有产出）而非实盘常驻。

### 4 判据
- 若 Owner 口径要"实盘全流通"：需 AutoRuntime 常驻 + QMT 桥连（QMT 9/18 退役，见 known_data_gaps）+ execution_report 逐日推进。
- 若口径为"纸面/仿真即达标"：则本链"不通"降级为"设计内 manual"，但须显式承认。

### 5 读数（实测·只读）
- AutoRuntime 进程：无。TradingWatchdog：Disabled。execution_report：1 行/09-18。

### 6 风险
- "全部通道打通、全部能运行"若在实盘语义下评估，则顶层执行链当前未闭合；若纸面语义，需锁口径防误读。

## 自审三态
- **PASS**：进程态/计划任务态/产出面行数三项独立只读核实。
- **FAIL（未做）**：未拉起 AutoRuntime（启停生产进程 + 触及实盘 = 越红线）。
- **待裁（明确不自裁）**：`python -m zephyr.trading` 应否常备、TradingWatchdog 应否 Enable —— 属"production 流转"级 Owner 门位（§5.2）。
  - 选项A 常备实盘：Enable TradingWatchdog + 保活；后果=需确保 QMT 桥可用 + killswitch/风控演练。
  - 选项B 纸面达标：显式声明实盘为 manual-on-demand，"能运行"口径以仿真桥为准；后果=本链从"不通"改记"设计内"。
  - 选项C 维持现状不表态：后果=普查结论与"全部能运行"目标存在口径缺口，须留痕。

## 处方与复现命令（全部只读）
```
powershell -NoProfile -Command "Get-CimInstance Win32_Process | ? { $_.CommandLine -match 'zephyr.trading|auto_runtime|AutoRuntime' } | Select CommandLine"
powershell -NoProfile -Command "(Get-ScheduledTask ZephyrAlpha_TradingWatchdog).State; (Get-ScheduledTask ZephyrAlpha_TradingWatchdog|Get-ScheduledTaskInfo).LastRunTime"
python -c "from zephyr.data import ch_writer as c; print('execution_report=',c.query('SELECT count(),max(execution_start) FROM c1_market.execution_report FORMAT TSV'))"
```
处方：先由 Owner 锁"能运行"口径（实盘 vs 仿真），再决定 Enable 与桥接验收；本轮只登记缺口，不拉起、不 Enable。
