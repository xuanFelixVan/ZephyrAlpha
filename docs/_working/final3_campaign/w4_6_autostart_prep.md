---
ttl: task_bound
title: W4-6 服务自启备料【O】——api_server/serve_docs 两案（A 计划任务/B 壳兜底+看门狗）
owner: st-final3-20260919
created: 2026-09-19
---

# W4-6 服务自启备料【O】

- 日期：2026-09-19｜会话：st-final3-20260919｜性质：**备料件，不施工（Owner 门位）**——对接 W8-3 签字册主题五"W4-6/W6-3 服务自启+看门狗两案选一【O】"
- 对象：`zephyr.frontend.dashboard.api_server`（8890，W6-1/W6-2 已落地单端口一体）+ `scripts/serve_docs.py`（8765，本地文档服务）

## 0. 现状基线（亲验）

| 项 | 实测 |
|---|---|
| api_server | 8890 单端口页面+数据一体；健康探针 `http://127.0.0.1:8890/api/health` |
| 壳拉起 | `tools/desktop/main.js` `ensureApi()`（L144）：健康检查未就绪→`spawnApi()`，等待期 `apiProc` 退出重试一次；`killApi()` 随壳退出；另有僵尸端口占用检测+一键提权修复（L75 起）与分离重启代理（`services_registry.py` `_RESTARTER_SRC`，自愈重启已闭环） |
| serve_docs | `scripts/serve_docs.py`，PORT=8765；服务总闸 docs_serve 手动启停；壳自动拉起随面板退出（`noqa: m11-perm-manual-legitimate` 在案） |
| reaper 白名单 | `data/runtime/process_reaper_keep.txt` 已含 `zephyr.frontend.dashboard.api_server`、`python -m http.server` 两行——**防误杀面已闭环；缺口="壳不在时段服务死了谁拉起"无主** |

## 1. 案 A：计划任务开机拉起（先例=register_process_reaper_task.ps1 / register_drift_watchdog_task.ps1）

**注册命令草案**（落地时新写 `scripts/register_api_server_task.ps1`，.ps1 纯 ASCII 红线）：

```powershell
# 任务名 ZephyrAlpha_ApiServer｜触发 AtLogOn（自愈可加 PT10M 重复）｜动作：
pythonw.exe -m zephyr.frontend.dashboard.api_server   # cwd=D:\ZephyrAlpha, stdout/err -> data/runtime/api_server_task.log
# serve_docs 同构：任务名 ZephyrAlpha_ServeDocs，动作用 --no-regen（重生成耗时不塞开机路径）
# 用法: powershell -ExecutionPolicy Bypass -File scripts\register_api_server_task.ps1
```

**与 reaper 先例的关键差异**（直接套用会翻车）：reaper=一次性幂等（ExecutionTimeLimit=10min 合理）；服务=长驻非幂等（端口独占）——必须 `ExecutionTimeLimit=0`（禁 OS 强杀）+ `MultipleInstances=IgnoreNew`（与 #ARCH-BOOT-001 Parallel 教训相反）；"Set-ScheduledTask 就地更新、禁 Unregister+Register"先例保留。

**回滚**：`Unregister-ScheduledTask -TaskName ZephyrAlpha_ApiServer -Confirm:$false`（ServeDocs 同）；涉及 flag 出厂翻转则走 high 域 Owner 门位。

**风险**：①开机拉起与壳 ensureApi 竞争 8890——ensureApi 先健康检查、端口已被占即复用不双拉，冲突面小但施工时须实测；②长驻计划任务=reaper 先例头注批判的 resident 进程模型回归，须白名单+看门狗闭环兜底；③pythonw 无控制台，排障全依赖日志文件；④"自动运行"须配"自动维护/自动关闭"面，否则与永久系统四要素张力。

## 2. 案 B：壳 ensureApi 兜底 + 看门狗挂 process_reaper_keep 族

**机制**：维持"壳拉起随壳退出"为主通道（ensureApi 已建成，零新开发）；补看门狗——复用 reaper 计划任务的 PT10M 扫面形态（ZephyrAlpha_ProcessReaper AtLogOn+PT10M 在案），对 8890/8765 做 socket 探针：端口死+壳不在→写治理告警（`.runtime/workspace_alerts` 族），**只探不拉**（拉起仍归壳/人，reaper 不从清道夫越权变保姆）；服务防误杀继续走 `process_reaper_keep.txt` 既有两行，白名单同源维护。

**注册命令草案**（落地时新写 `scripts/register_api_watchdog_task.ps1`）：

```powershell
# 任务名 ZephyrAlpha_ApiWatchdog｜AtLogOn+PT10M｜动作：pythonw.exe <探针脚本>（幂等一次性：探测->告警->退出）
# ExecutionTimeLimit=10min + MultipleInstances=Parallel（完全对齐 reaper 先例，幂等一次性语义）
# 用法: powershell -ExecutionPolicy Bypass -File scripts\register_api_watchdog_task.ps1
```

**回滚**：Unregister ZephyrAlpha_ApiWatchdog；keep 白名单两行本就存在，零回滚面。

**风险**：①壳不在（未登录/壳崩溃）时段服务死亡无人拉起——本意即"有人用才保活"，无人值守覆盖缺口是本案与案 A 的本质差；②探针误报窗口（API 冷启 20~40s）需容忍带；③reaper 扫面加探测=职责扩张，若触发率持续近零按宪法 §4.2 季度退役审计降级。

## 3. 两案对照与 Owner 门位清单

| 维度 | 案 A 计划任务 | 案 B 壳兜底+看门狗 |
|---|---|---|
| 自启时效 | 开机即活（登录态） | 壳启动才活 |
| 无人值守覆盖 | 有 | 无（本质缺口） |
| resident 风险 | 高（长驻任务回归） | 低（幂等探针一次性） |
| 回滚成本 | 低（Unregister） | 极低 |
| 先例一致性 | 需变体（长驻参数面） | 完全对齐 reaper 形态 |

**Owner 裁定点**：A/B/混合（A 管开机+B 管巡检）三选一；serve_docs（8765）是否纳入自启；ExecutionTimeLimit/Instance 策略确认；flag 出厂翻转走 high 域门位（宪法 §5）。

— 生成：2026-09-19 by st-final3-20260919（W4-6 备料批，不施工）
