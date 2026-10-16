---
doc_type: mining_segment_doc
parent: docs/_working/mine_fullchain_20261015/00_skeleton.md
map_node: config/trading_day_cycle_map.yaml#D13-45
segment: fig13-B 盘中
mined: 2026-10-15
miner: daily_ops_am
ttl: task_bound
---

# SD13-45 盘中模拟盘桥（做T测试窗双拍）

## 1. 定义

交易日 09:35 与 13:05 两拍（Windows 计划任务 ZephyrAlpha_SimBridgeExecute）拉起模拟桥日跑器（做T测试窗）：注册于 scripts 拆簇批（a4b503a163），执行体自带 is_trading_day 闸（假日触发即退非误判）。10-08 开市复核实测：09:35 拍触发但在册 Action 指向拆簇失准路径（run\run_sim_bridge_execute_daily.ps1 不存在→Result=4294770688 零留痕），09:47 重跑注册器 Register -Force 修正，13:05 修正后首拍 LastRun/Result=0；当日行=「SKIP: XtItClient not running」终端离线诚实跳单。决策问题：桥窗两拍跑了吗？产出与退出码留痕在哪？

地图在册态：wiring=partial、build=partial、evidence 注「升✅候选待骨架 §2 行与状态三态表同步（本批只更证据不动状态）」。骨架 0924 考古「全仓无 SimBridge」已被实存推翻（骨架回写 2026-10-04）。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | 计划任务双拍触发+模拟桥配置+XtItClient 终端态 | `scripts/tasks/register/register_sim_bridge_execute_task.ps1:47`（注册声明面） |
| 输出面 | 做T桥执行留痕（.runtime/logs/sim_bridge_execute.log；11,964B 当日行=诚实 SKIP）+假日 SKIP 三连负向验证（10-01/02/03 各两拍） | `.runtime/logs/sim_bridge_execute.log`；`config/trading_day_cycle_map.yaml#D13-45` evidence |
| SSOT 真源 | 图13 节点契约（行 3534-3602）+ sim_daily_runner 闸面 | `config/trading_day_cycle_map.yaml#D13-45`；`scripts/backtest/sim_daily_runner.py:260-262`（is_trading_day 闸实核） |
| 代码模块 | 注册 ps1+日跑器（MOD-BT-222） | `scripts/tasks/register/register_sim_bridge_execute_task.ps1`；`scripts/backtest/sim_daily_runner.py` |
| 门禁约束 | 注册器源路径自纠机制（Register -Force 可修 Action 失准）；.ps1 纯 ASCII；fallback=无（错过窗不补） | `config/trading_day_cycle_map.yaml#D13-45` evidence/note_zh；`AGENTS.md` §9.7 |
| 自动化触发 | mechanism=B_windows_task，交易日 09:35/13:05 双拍（触发器纯 Daily+执行体日历闸）；trigger_facts last_run=2026-10-08T13:05:00；schtasks 双证 | `config/trading_day_cycle_map.yaml#D13-45` cadence_zh/trigger_facts/machine_facts |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 双拍触发+日历闸+终端态三输入齐 |
| 输出面 | warn | 修正后（10-08 13:05）首拍才恢复留痕，此前 4294770688 零留痕窗已损失 |
| SSOT 真源 | warn | 升✅候选待骨架 §2 行与状态三态表同步（地图证据先行、骨架态滞后一拍） |
| 代码模块 | pass | 注册器/日跑器/日历闸实存实核 |
| 门禁约束 | pass | 拆簇失准已用 Register -Force 自纠（事件留痕在册） |
| 自动化触发 | warn | Action 指向失准型故障（注册面 vs 落地面路径分裂）无预防门，复发不可知 |

## 4. 缺口与建议

- 图13 全图缺口在本格的落点：无 G 节点；本格 red 态争议（骨架 0924 考古误判）已由回写机制处置。
- gap_refs 空。
- 建议：①注册器落地面与在册 Action 路径一致性校验（schtasks 注册后即查 Result 首拍）可作注册族通用自检；②骨架状态三态表同步升✅（属骨架车道回写，本矿只登记候选）。
