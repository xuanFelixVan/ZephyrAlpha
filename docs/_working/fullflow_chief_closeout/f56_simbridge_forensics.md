---
ttl: task_bound
completes_when: "F56 取证闭环：SimBridge 执行腿 alive/dead/zombie 判定+全证据链（任务态/日志逐行/git 时间线）+最小修复处方落盘；只读取证零代码改动"
---

# F56 · SimBridge 取证报告（read-only，2026-09-28 SECURITY BATCH）

## 0. 判定

**ZOMBIE（已当夜复活，待下次实弹验证）**——精确态：调度腿 ALIVE、包装腿 ALIVE、执行腿 2026-09-28 两窗全灭（exit 2），当晚 15:05 由 dd3b17f9fd 修复重建，主区现行检出已含修复；下一次实弹=2026-09-29 09:35。

## 1. 证据链（全部实查于 2026-09-28 晚）

| # | 证据 | 内容 | 推论 |
|---|------|------|------|
| 1 | 计划任务 `schtasks //query //tn ZephyrAlpha_SimBridgeExecute` | 模式=就绪，下次运行 2026/9/29 9:35:00 | 调度腿 ALIVE（09:35/13:05 工作日双窗在册） |
| 2 | `D:\ZephyrAlpha\.runtime\logs\sim_bridge_execute.log` 2026-09-23 13:05 | 全链绿：CH 连接建立、QmtFileBridgeBroker connected env=sim、quote age_s=1.9（新鲜）、`{"posture":"flat","action":"none","placed":false,"why":"no_order_action(none)"}`、`exited: exit_code=0` | 修复前 4 天（09-23）执行腿健康：诚实无单行，非静默坏 |
| 3 | 同日志 09-25/26/27 六条 `SKIP: non-trading day` | 09-25=中秋节（XSHG 休市合规跳过）；09-26/27=周末 | fail-closed skip 语义工作正常（非故障） |
| 4 | 同日志 2026-09-28 09:35:13 与 13:05:04 两条 | `sim_daily_runner.py: error: argument cmd: invalid choice: 'bridge-execute' (choose from plan-bridge, plan-execute, e4-replay, report, settle)` → `exited: exit_code=2` | **执行腿断**：部署面 runner 无 bridge-execute 子命令，当日两窗零执行（交易日白失两窗） |
| 5 | git 时间线 | dd3b17f9fd `[F56 断腿重建] sim_daily_runner 新增 bridge-execute 子命令` 落于 **2026-09-28 15:05:23 +0800**（晚于两窗）；dev HEAD=fa9ae36533 含之；主区现行检出 c50b8a593c 的 `scripts/backtest/sim_daily_runner.py:1162` 六子命令含 bridge-execute | 断因=主区部署面滞后（ fire 时 runner 尚为修复前版本）；15:05 修复落地后主区已含子命令 |
| 6 | `scripts/run_sim_bridge_execute_daily.ps1:12-31` | 09:35/13:05 一发一跑：is_trading_day fail-closed skip → XtItClient 存活探针 → cmd /c 调 `bridge-execute --day <today>`；日志落 `.runtime/logs/sim_bridge_execute.log` | 包装腿逻辑与部署（st-sim-launch-20260923）一致，非断因 |

## 2. 断腿根因（一句话）

**部署滞后型断腿**：执行腿代码（bridge-execute 子命令）在 dev 的存在性与主区部署面的检出版本错位——09-28 两窗 fire 时主区 runner 为五子命令旧版，argparse 拒绝 `bridge-execute`（exit 2）；15:05 dd3b17f9fd 落地后主区检出已同步，腿已物理接回。

## 3. 残余缺口与最小修复处方（未实施，本件只读）

1. **退出码契约漂移**（ps1:28 vs 实际）：ps1 头注写 "1 = runner/bridge failure"，但 argparse 无效子命令实际 exit 2——按码分诊的任何消费方会把"断腿"误桶。最小修复：ps1 头注补 "2 = argparse/调用面错（含子命令缺失）" 或 `cmd /c` 后把非 0/1 归一为 1，二选一，一行级。
2. **失败可见性=零升级通道**：exit 2 只进日志文件，无 alert/dead-letter——本次断腿两窗静默，靠人读日志才发现（F56 立案同款病）。最小修复：ps1 末尾 exit 非零时追加一条既有 `data/alert_webhook_dispatch` 或安全事件总线告警（复用在册外推面，不造第二套通知通道）。
3. **fire 漂移观测**：09-27 09:45:17 起跳（计划 09:35，晚 10 分钟，机器唤醒尾差），单次未复发——留观即可，不施工。
4. **验证处方（Owner/运维）**：明日 09:35 后 `tail .runtime/logs/sim_bridge_execute.log` 应见 exit_code=0（或诚实无单行）；或手动 `powershell -ExecutionPolicy Bypass -File scripts\run_sim_bridge_execute_daily.ps1` 干跑验证（ps1:31 自带入口）。

## 4. 取证边界

本件零代码改动、零配置改动、零主区写入（schtasks 查询与日志读为只读）；CH/交易面未触碰。09-28 两窗因断腿未执行的任何计划动作是否需要补执行，属交易侧裁定（交易侧熔断有独立持久化覆盖，宪法 kill_switch 职责边界注），不在本件代答范围。
