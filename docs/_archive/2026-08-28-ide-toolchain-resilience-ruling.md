---
ttl: permanent
---

# 裁定：IDE 工具链韧性（100% AI 开发场景）— 综合分析与治本施工方案

> **文档类型**: 架构裁定（ruling）+ 治本施工方案
> **编号**: #ARCH-IDE-RESILIENCE-001
> **关联**: ruling_100pct_ai_governance_hardening.md（治理加固，仓库内）；本裁定覆盖仓库外的生产工具链
> **日期**: 2026-08-28
> **状态**: open（P0 部分已落地，待 Owner 验收）
> **作者**: ZephyrAlpha AI Architect（客观第三方架构师视角）
> **调研基础**: Windows 事件日志/WER 报告/崩溃转储/Trae 自有日志取证 + 项目文档体系审查

> **结案审查（2026-08-28 复核）**：未结案（P0 已闭环，P1 制度化 2 项待施工）
> - 已实证闭环：误杀真凶根治三件套已落盘启用——`classify_trae_process` 内核态拓扑判据（WMI 三函数已删）、`_advance_ghost_state` 3 轮确认状态机、`kill_ghost_windows` 杀前复查赦免；轻导入隔离 + 计划任务改脚本直跑（commit a82ac30a）；IDE 崩溃链已止。
> - 未结案项：R4（应急 runbook 沉淀至 sop/，现 sop/ 下无此件）、R5（工作区卫生制度化）未见落地实证。
> - 后续：R4/R5 施工完成后本篇可归档结案；ttl=permanent 保留为裁定先例。

---

## 0. 摘要（TL;DR）

2026-08-26 起 Trae IDE 反复弹窗"窗口意外终止（crashed，代码 15）"，8-28 恶化为"AI 一执行指令 1 分钟内必崩"。取证确认为 **Trae 8-25 静默自动更新引入的原生组件 bug（ai_agent.dll / ckg 代码索引服务，0xC0000409 快速失败）**，被**工作区 30 万文件规模**（监听/索引子系统被打满，CPU 96~99%）放大为必现。同期宿主机另有 3 次 0x13A 内核堆损坏蓝屏（7-22 NVIDIA 驱动装机当日起有前科），构成背景放大器。

**核心裁定**: 6 条子裁定，分 P0（今日应急）/ P1（本周制度化）/ P2（条件触发）三档。治本主线 = 把 IDE 从"不可替换的单点"降级为"可替换的执行器"，把宿主系统从"未知状态"拉回"可观测状态"。**不换 IDE、不自建替代组件、不引入第二套日常环境**（防过度工程）。

---

## 1. 证据链（全部取自本机取证）

| # | 证据 | 来源 |
|---|---|---|
| E1 | 崩溃签名：Trae CN.exe 2.3.10589.0 / 故障模块 ai_agent.dll / 异常 0xC0000409（程序自检致命错误后主动自杀）/ 故障参数 7（FATAL_APP_EXIT），同一故障桶出现 ≥2 次 = 确定性 bug | WER ReportArchive，8-26 23:33、8-27 11:57 |
| E2 | 8-28 10:20 实锤：**ckg 进程（代码知识图谱服务）以 0xC0000409 崩溃 → 渲染进程被连带杀死（exit 15）→ 弹窗**。触发时机 = AI 执行指令调用代码索引 | aha_electron_2026.0828.log L70967-70971 |
| E3 | ai_agent.dll（263MB）+ agent-tool-host.exe 于 **8-25 16:21 被自动更新**，次日首崩 | 文件时间戳 |
| E4 | 崩溃窗口内 CPU 持续 kCritical 96~99%：renderer 138%、gpu-process 102%、**fileWatcher 96%** | aha_electron_2026.0827.log |
| E5 | 工作区规模：.runtime 25.3 万文件、tmp 1.8 万、.worktrees 2.3 万、.git.backup.20260803 1.7 万；旧 files.watcherExclude 写法缺 `**/` 前缀，大概率未生效 | 目录统计 + settings.json 审查 |
| E6 | 宿主系统：0x13A 内核堆损坏蓝屏 ×3（8-13/8-24/8-26）；7-22 NVIDIA 驱动安装当日蓝屏 0xD1/0x0A；llama-server、XtItClient、同花顺、explorer 多进程连环崩 | System 事件日志 |
| E7 | 蓝屏 minidump 被存储感知自动清理，无法回溯凶手驱动 → **已于本次处置关闭（StoragePolicy 04=0）** | 注册表取证+修复 |

**时间线**: 8-25 更新 → 8-26 首崩 + 当日蓝屏 → 8-27 二连崩 → 8-28 必现化。

## 2. 第一性原理分析

### 2.1 第一性命题

100% AI 开发 = 生产力的唯一载体是 AI IDE。**IDE 故障 = 项目全面停产**，这在可靠性工程里叫单点故障（SPOF）。

### 2.2 治理盲区

项目治理体系（pre-commit 门禁、注册表、设计备忘录、记忆系统）全部建在**仓库内**；而 IDE 这个生产工具在**仓库外**：静默自动更新、闭源原生组件、无回滚通道、无质量门禁。8-25 的推送绕过了我们给代码设定的全部防线——**我们对进入本机的"供应商变更"零管控**。

### 2.3 三个叠加故障域

- **(a) 供应商推送质量**：8-25 更新引入确定性 bug（主因）
- **(b) 工作区规模压力**：30 万文件喂爆 watcher/ckg，把"偶发 bug"放大为"必现崩溃"（放大器，且是本项目唯一能自控的变量）
- **(c) 宿主系统稳定性**：0x13A 蓝屏史 + 多进程连环崩（背景噪声，疑与显卡驱动/内存相关，待 dump 取证确认）

本次事件 = a × b 共振，c 垫底。

### 2.4 已有韧性资产（不重建，直接依托）

git 全量历史、pre-commit 门禁、设计备忘录/注册表驱动施工（天然 IDE 无关）、会话记忆在仓库外目录。**项目的"知识"从不依赖 IDE，只有"操作"依赖 IDE。** 这决定了治本方向。

### 2.5 结论

治本不是换 IDE（供应商讨论无意义），而是两件事：①把 IDE 从"不可替换的单点"降级为"可替换的执行器"（冷备 + 应急 Runbook + 知识资产与 IDE 解耦）；②把宿主系统从"未知状态"拉回"可观测状态"（dump 留存 + 内存体检 + 驱动取证）。

## 3. 裁定

| 子裁定 | 档位 | 内容 | 状态 |
|---|---|---|---|
| R1 | P0 今日 | 重建 ckg 索引 + 清纯缓存（桌面脚本 `Trae修复-清缓存重建索引.ps1`，不动 User/Partitions = 聊天记录保全） | 已交付，待执行 |
| R2 | P0 今日 | files.watcherExclude 改 `**/` 规范写法并补 6 个巨型目录（Owner 手动粘贴后重启 Trae） | 已交付，待执行 |
| R3 | P0 今日 | dump 保留常态化（存储感知临时文件清理已关闭）；下次蓝屏后 `C:\Windows\Minidump` 用 WinDbg 预览版 `!analyze -v` 定凶手 | 已落地 |
| R4 | P1 本周 | 崩溃应急 Runbook 沉淀至 docs/01_policies_and_standards/sop/；会话记忆目录（c:\Users\fanzi\.trae-cn\memory）+ Trae User 目录纳入周期备份 | 待施工 |
| R5 | P1 本周 | 工作区卫生制度化：新增巨型目录（>1 万文件）必须同步 watcherExclude；评估 .git.backup.20260803（6.5GB）归档或删除 | 待施工 |
| R6 | P2 条件触发 | 内存体检（mdsched，先在 BIOS 关 XMP 再测）；**NVIDIA 驱动 DDU 干净重装仅当"蓝屏复现且 dump 指向显卡驱动"时执行**（Owner 裁定：留作最后手段）；向日葵 Oray 保留不动 | 待触发 |

## 4. 边界（不做清单）

- 不更换主力 IDE、不 fork Trae、不自建 ckg 替代品
- VS Code 仅作冷备（R6 同档），不日常维护双环境
- 不为 IDE 崩溃建监控告警系统（频次不值得，Runbook 足够）

## 4.5 终审增补：真凶落网（2026-08-28 午间取证）

**最终根因**：项目自己的 `ZephyrAlpha_ProcessReaper` 计划任务（`zephyr.trading.process_reaper`，每 10 分钟一次）的"Trae 幽灵窗口清理"功能误杀活进程。该功能 8-28 当天刚从 ide_health_daemon 迁入并修复匹配 bug（此前从未真正生效），首日生效即事故。

**误杀机理**：Electron 渲染进程 MainWindowHandle 天生为 0；"可见窗口"判定走 WMI，高负载下超时返回空 → 全部活渲染进程被判幽灵 → `os.kill(pid, SIGTERM)` → 弹窗"窗口意外终止，代码 15"（SIGTERM=15）。**reaper 杀进程日志与 Trae 崩溃日志逐秒逐 PID 完全吻合（09:41~11:20 共 20 次，如 10:20:37 杀 PID 7512 = 崩溃日志 10:20:37 renderer 7512 exit 15）**。

**处置记录**：
- 止血：`ZephyrAlpha_ProcessReaper` 任务已禁用（14:xx）
- 修复：`scan_ghost_windows()` 加双 fail-safe 闸——可见集为空不杀 / 全部判幽灵不杀（[process_reaper.py](../../../src/zephyr/trading/process_reaper.py)），单测 19/19 通过；任务保持禁用，观察 24h 后由 Owner 决定是否重新启用
- 干扰项排除与复查：ckg 当日 6 次 fast-fail 全部发生在 reaper 杀渲染进程后 3~5 秒（连带自杀特征），**判定为受害者而非凶手，libckg.dll 已恢复原名**（观察标准：无 reaper 时仍独立 fast-fail 才是真 bug）；三个第三方 AI 扩展（Cline/Roo/Kimi）已卸载不恢复（与原生 AI 重复索引放大负载）；files.watcherExclude 已改 `**/` 规范写法并补 6 个巨型目录（永久保留，属正确配置而非临时措施）

**追加裁定**：
- R7：治理类后台任务凡涉及杀进程/写 IDE 活跃文件，fail-safe 方向必须为"不动作"；上线前须通过"高负载误杀"演练（WMI 超时注入）
- R8：后台任务全量盘点（17 个项目计划任务 + 系统启动项）结论：数据管道五件套（DataScheduler/TickSubscriber/CHHealthProbe/WorktreeDriftWatchdog/DeadmanSwitch）保留；`AI-Wrapper-Inject`（每分钟写 toolhost 快照）降频至 5 分钟并纳入观察；`TraeCacheCleanup` 加"Trae 运行中跳过"守卫；TRAE SOLO CN 与 Trae CN 双 IDE 并行建议错时关闭其一

## 5. 大白话附录（Owner 要求的通俗解释）

- **mdsched（内存诊断）**：Windows 自带的"内存条体检"。重启后进系统前自动跑一遍，逐格读写内存条，有坏块会报出来。用法：Win+R 输 `mdsched` → 选"立即重新启动"。体检完自动进系统，结果在事件查看器（Windows 日志→System→来源 MemoryDiagnostics-Results）。
- **XMP**：内存超频开关（让内存跑得比标称快，在 BIOS 里）。超频不稳会导致各种莫名崩溃/蓝屏，且难以复现定位。所以体检前先关掉它（BIOS 里找 XMP/EXPO 设 Disabled），排除干扰项；测完确认内存没问题再决定要不要开回来。
- **dump（转储）**：蓝屏瞬间的"现场照片"。Windows 会把凶手线索写进 `C:\Windows\Minidump`。之前照片被系统的自动清理删了（现已关闭该清理）。下次蓝屏后用微软免费工具 WinDbg 打开照片，`!analyze -v` 直接告诉你哪个驱动闯的祸，再决定要不要动 NVIDIA 驱动（R6）。
