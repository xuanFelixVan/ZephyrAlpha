---
ttl: task_bound
session: st-ailayer-fullflow-sc
creation_token: m5sc-boot-chain-20260925
---

# M5 补挖分册 02：环境与启动链（F85）——五层形态实测

> 证据：sc query/Startup 文件夹/端口/进程表活探 + 源头读，2026-09-25。总册标 partial（M5 补挖项）——**本册判定：形态五层齐备，缺一件部署+一件探活**。

## 一、五层启动形态（谁把系统带起来）

### L1 OS 服务层（windows_service.py，118 行）——建成未部署
- 设计：`sc create ZephyrAlpha binPath="python -m zephyr.trading"` + `start=auto`，SCM 触发（M02-manual/M10 豁免注在案：while True+WaitForSingleObject 是 Windows Service 标准形态）。
- 实测：`sc query ZephyrAlpha` → **1060 指定服务未安装**；且 `install_service()` 全仓零调用方（__main__/auto_runtime_core 均无接线）——**双缺：未部署+无部署入口**。当前 Windows 服务形态=纯设计态。

### L2 登录壳层（裁定 #374 topic5 plan B）——在册，本次未活
- `scripts/register_desktop_shell_startup.ps1`：往用户 Startup 文件夹放 `ZephyrAlpha Dashboard.lnk` → Electron 壳（tools/desktop/main.js）ensureApi 自动拉起/复用 8890 api_server（`python -m zephyr.frontend.dashboard.api_server`，main.js:60-70）+ 8765 serve_docs；一个快捷键覆盖"壳+服务"全链；幂等（重跑覆盖同 .lnk）；回滚=删 .lnk。
- 实测：**`ZephyrAlpha Dashboard.lnk` 在 Startup 文件夹存在**；但 electron 进程无、8890/8765 均无监听——登录自启链在册而当前会话壳未运行（手动关闭或未重登录，非链断）。main.js 另有僵尸端口占用检测+一键提权修复（09-09 实证件）。

### L3 常驻任务层（LogOn 触发群）——绿
- M5 主波 01 册已挖干：LogOn+PTxM 八件（guard×3/BeltDaemon PT1M/Reaper PT10M/DriftWatchdog/AI-Wrapper-Inject/ResourceSamplerScan），本波复核时间点全部在册在跑。

### L4 手动 CLI 层——常态主入口
- `python -m zephyr.trading`（__main__.py）：AutoRuntime Core 入口，reconcile 轮询循环（M10 豁免：CLI 主入口心跳设计，转纯事件驱动=独立架构倡议）；进程级 RLIMIT_AS 内存上限二级防线（5.43.2）。
- 冷启动三步=宪法 AGENTS §0（RULE-ENV PATH 修正→RULE-GUARDIAN reaper 存活→RULE-WORKTREE），是所有人工/会话启动的前置序。

### L5 AI wrapper 注入链——活
- 机制（ensure_ai_wrapper_injection.ps1，tracker #58）：toolhost 硬编码 dot-source 每 toolhost 进程的 powershell-profile-snapshot → 追加幂等 marker 行恢复 git_safety_wrapper 全层包装；快照随 toolhost 生灭 → PT1M 计划任务补注射（最坏裸奔窗=1 个调度间隔）。
- 实测：ZephyrAlpha-AI-Wrapper-Inject Running（本波时间点，主波 01 册基线一致）。

## 二、六向台账
- **上游输入**：Windows SCM（L1，未装）；用户登录会话（L2 .lnk/L3 任务 LogOn 触发）；Owner 手动 CLI（L4）；toolhost 进程生灭事件（L5）。
- **下游消费**：AutoRuntime Core+FLE 子系统束（_BootSubsystemRegistrar：TaskQueue/BlueprintWatcher/FLE/triple_alignment 四 boot 段，auto_runtime_core.py:1100-1160）；api_server 8890+serve_docs 8765；guard 三卫士族（02 册 §三）。
- **自动化触发**：SCM auto（设计态）；Logon 触发（.lnk+8 计划任务）；PT1M 注入；其余手动。
- **真源与注册表**：windows_service.py（服务定义真源）；register_desktop_shell_startup.ps1（#374 真源）；AGENTS.md §0（冷启动序）；main.js（壳拉起真源）；ensure_ai_wrapper_injection.ps1（tracker #58，INJ-007 ASCII gate）。
- **门禁与质量尺**：M02/M10 豁免登记（windows_service/__main__）；.ps1 纯 ASCII 铁律；creation token 在册；reaper keep-list 保护启动链长跑件。
- **当前运行状态：黄**。L3/L5 绿；L2 在册未活（无探活判据=谁死了没人知）；L1 双缺；L4 常态。

## 三、堵点与修法
| # | 堵点 | 修法 | 归属 |
|---|------|------|------|
| 1 | windows_service.py 零入口零部署 | 二选一：接 CLI 入口（__main__ 加 --install-service）+Owner 批部署；或声明退役（净零铁律：不留无入口死件） | Owner 门位+施工 |
| 2 | 桌面壳/8890 无健康判据 | 健康总表（主波 05 册）增一行：盘中 api_server 8890 `/api/health` 探活；壳死=黄 | 本车道小单 |
| 3 | L2 与 L4 双轨无优先级声明（壳拉起的 api_server vs 手动起的 AutoRuntime 关系） | 在 73_d_infrastructure 域文档补一句归属声明即可，非代码件 | 文档小单 |

## 四、自审闸三态
**挖干可施工**：五层每层有活探命令+实测结果（服务 1060/.lnk 在/端口空/任务绿/注入活）双源闭合；堵点修法均为小单，无未知依赖。
