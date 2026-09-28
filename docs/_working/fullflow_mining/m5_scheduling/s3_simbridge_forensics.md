---
ttl: task_bound
creation_token: m5-sched-s3-simbridge-forensics-20260925
---

# M5 分册 06：S3 SimBridgeExecute 09-24 断链取证结案（st-commitspeed-tbl-20260924）

> 04 册 S3 的取证专册。只取证不施工不重注册（涉交易语义归 Owner/M7）。证据三源：git 考古 + log 缺席 + 退出码机器实证。

## 一、结案陈词

1. **直接死因**：任务 `ZephyrAlpha_SimBridgeExecute`（Action=`powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "D:\ZephyrAlpha\scripts\run_sim_bridge_execute_daily.ps1"`，触发 09:35/13:05）在 09-24 两班（09:35:01/13:05:01，LastRun 实测=13:05:01）点火时，**wrapper ps1 不在盘上**。该文件 09-23 由 st-sim-launch 以未提交工件创建，随 09-23→09-24 的 uncommitted 工作区丢失事件蒸发（与 M7 B1 的 runner 侧 `bridge-execute` 子命令丢失**同一事件、同一暴露面**），直到 **09-24 23:08 才以 27449507e1c 首次入库**。`powershell.exe -File` 指向不存在文件 = 进程退出 0xFFFD0000（无符号 4294770688）——与 04 册记录的 LastTaskResult 逐位吻合。
2. **无日志的真义**：`.runtime/logs/sim_bridge_execute.log` 末条=09-23 13:05:07 exit 0，09-24 零新增——包装层连第一行都没执行（不是 04 册猜的"Write-SimLog 前死（交易日闸/PATH/解码类）"，是文件根本不在）。SKIP 路径（非交易日/终端离线）也必写日志，SKIP 亦被排除。
3. **4294770688 语义修正（S6 族判读）**：本机实测（详见 §三矩阵）`powershell.exe -File` **无论脚本存在与否、exit 0/2、CRLF/LF、Hidden 与否、MSYS/clean env，一律返回 -196608**；`-Command` 正常传播（2→2）。⇒ 该任务 LastTaskResult **恒为 4294770688，零信息量**：09-23 三次成功班次（05:31 手测 / 09:35 / 13:05，log 全 exit 0）的 LastTaskResult 亦应同值。04 册"非标准调度码=异常线索"的方向就此修正：**码是常量，真相在 log 缺席 + git 考古**。
4. **与 M7 B1 合流**：B1 断 runner 子命令（未提交丢失），S3 断包装 ps1（未提交丢失）——**整条 SimBridgeExecute 调度链（register ps1 + wrapper ps1 + runner 子命令）09-23 全程运行在 uncommitted 态**。09-23 首单实弹（sysid=4820）来自该态的判读（B1 原文）由本册补全为全链判读。

## 二、证据链时间轴（全部可复跑，命令见 §五）

| # | 时点 | 证据 |
|---|------|------|
| 1 | 09-22 | st-sim-launch 批 fb5a7821d7 / 28b85901bf：FIX-3 v2 cmd /c 重定向入已提交 runner；bridge-execute 子命令、wrapper ps1、register ps1 均未随批（28b85901bf 版文件 grep bridge-execute=0） |
| 2 | 09-23 | 任务注册（XML 实拍：InteractiveToken、PT30M、StartWhenAvailable、双 CalendarTrigger 09:35/13:05，注册起点 2026-09-23T09:35）；log 三次成功：05:31:34 / 09:35:04 / 13:05:07 全 exit_code=0（13:05 班 posture=flat 无单行在案） |
| 3 | 09-23 13:05 后～09-24 09:35 前 | uncommitted 工作区丢失事件：runner 侧=M7 B1 已证；wrapper 侧=git show 27449507e1c~1 报 "exists on disk, but not in <parent>"，name-status=A 纯增 |
| 4 | 09-24 09:35:01 / 13:05:01 | 两班点火 → -File 指空 → 0xFFFD0000=4294770688；log 零新增；任务 LastRun/LastTaskResult 停在 13:05 班（本班实拍） |
| 5 | 09-24 23:08:26 | 27449507e1c（e2e 终批窄批）以 A 状态补录两调度 ps1（+140 行）——首次入库 |
| 6 | 09-25 00:30 | 主区 wrapper 两件 mtime（merge/checkout 落盘触发） |
| 7 | 09-25 02:57 | 主区 sim_daily_runner.py 重建 bridge-execute（+379/-22，**仍未提交**——M7 施工在途件，`bridge-execute --help` 本班实测解析正常）；再丢失暴露面持续开着 |
| 8 | 09-25 取证时点 | 任务 State=Ready、LastRun=09-24 13:05:01、LastTaskResult=4294770688（Get-ScheduledTaskInfo 实拍）；XtItClient/交易面本班未触碰 |

## 三、退出码实证矩阵（本班机器，双环境通道）

| 场景 | rc |
|---|---|
| `-File` 存在 + `exit 0` | -196608 |
| `-File` 存在 + `exit 2`（LF 与 CRLF 各测） | -196608 |
| `-File` 缺失文件 | -196608 |
| `-File` + `-WindowStyle Hidden`（任务实配形态） | -196608 |
| `-Command "exit 2"` / `"exit 1"` | 2 / 1（正常传播） |

- 环境通道①=MSYS bash→cmd 链；通道②=WMI `Win32_Process.Create` 干净 env spawn（排除会话环境变量因素）——两通道同结果。
- 外部口径（web 检索）：0xFFFD0000/4294770688 即社区通知的"Task Scheduler 下 powershell -File 启动失败"签名码（techcommunity/superuser/robvit 多源）。本机把该码扩大化为 -File 全场景常量，机制层（为何 -File 不传播）未深挖——**不影响 S3 结案**（log 缺席+git 考古已闭合），登记为独立观察项。

## 四、取证通道缺口（为什么 Get-WinEvent 无数据）

- `Microsoft-Windows-TaskScheduler/Operational` 通道 **enabled=false**（wevtutil gl 实拍）——04 册 S3 预定的"事件日志 Task Scheduler 操作通道 09-24 13:05 记录"无数据可取。
- 经典 `Windows PowerShell` log 最老事件=09-24 23:44:20（两班已滚出，10789 条环形覆盖）。
- 本结案因此改走三源闭合：git 考古（文件何时存在/何时入库）+ log 缺席（wrapper 是否执行过）+ 退出码机器实证（码值语义）。通道启用建议见 §五.3。

## 五、修复建议（归属标注；本班只取证未施工未重注册）

1. 【M7 施工·急】bridge-execute 现存主区未提交件（09-25 02:57 +379 行）尽快经 commit_queue 入库——**正重演同一丢失暴露面**（丢一次=调度链再断，且这次没人知道哪天丢）。
2. 【M5 施工/待裁·Owner 门】包装链加固二选一或并用：(a) Action 改 cmd /c shim：先落时间戳心跳行再调 powershell 并 `echo EXIT %errorlevel%`——cmd 层可区分"没跑起来（文件缺失/-196608）"vs"跑了死中间"，即 04 册原案"ps1 首行前 file-level 旁落日志"的可行实现；(b) 按 S10 先例 wscript+launch_hidden.vbs 换装。改 Action=重注册=Owner 门位（本班红线禁触）。
3. 【运维/待裁】`wevtutil sl Microsoft-Windows-TaskScheduler/Operational /e:true` 启用操作通道（当前 enabled=false=取证盲区）；是否常开留 Owner 权衡事件量。本班未动。
4. 【M3/S6 族】凡 powershell -File 型任务的 LastTaskResult 一律按常量 4294770688 处理（无鉴别力），健康判据改走文件心跳/log 水位——05 册健康表如有按 LastTaskResult 判黄的行位请对齐本结论。
5. 【遗留雷·登记】wrapper L56 交易日闸 `& $PythonExe -c "..." 2>&1` 在 `$ErrorActionPreference="Stop"` 下=PS5.1 stderr 陷阱：本班实测任何 stderr 输出（含 INFO 级日志回流）→ NativeCommandError → 脚本死于 L56、rc=1、零日志——与 L76 已修的 cmd /c 构型（FIX-3 v2）不同构，属同族漏网。修法=L56 同走 cmd /c 或 Stop 局部化。归属 M7/M5 施工待批（当前不触发仅因日历链尚无 stderr 输出，属时序侥幸）。

## 六、复跑探针命令（全部只读/无副作用）

```bash
# 任务现状（State/LastRun/LastTaskResult）
powershell -NoProfile -Command "(Get-ScheduledTaskInfo -TaskName 'ZephyrAlpha_SimBridgeExecute') | Format-List LastRunTime,LastTaskResult"
powershell -NoProfile -Command "Export-ScheduledTask -TaskName 'ZephyrAlpha_SimBridgeExecute'"   # Action 实配
# log 水位（末条应 >= 本册落地时刻；若仍停 09-23 13:05 则 09-25 班次亦未跑成）
tail -3 /d/ZephyrAlpha/.runtime/logs/sim_bridge_execute.log
# git 考古：wrapper 首次入库=27449507e1c（09-24 23:08，纯 A）
git log --oneline --diff-filter=A -- scripts/run_sim_bridge_execute_daily.ps1
git show 27449507e1c~1:scripts/run_sim_bridge_execute_daily.ps1   # 应报 not in <sha>
# runner 重建件在途态（M 状态=仍未提交）
git status --porcelain scripts/backtest/sim_daily_runner.py
python scripts/backtest/sim_daily_runner.py bridge-execute --help   # 解析性探针
# 退出码实证（复制本班 .runtime/tmp/s3probe 探针或重写最小件；cmd 层取 %errorlevel%）
# 取证通道状态
wevtutil gl Microsoft-Windows-TaskScheduler/Operational | findstr enabled
```
