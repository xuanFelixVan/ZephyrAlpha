---
ttl: task_bound
title: F71 AutoRuntime Core（python -m zephyr.trading 三层运行时运营中心）——L08 复飞矿道案卷
session: zc-l08-20260927
updated: 2026-09-29
---

# F71 · AutoRuntime Core

> 总册行：G 段 F71，状态 built，P0，`python -m zephyr.trading`→`src/zephyr/trading/auto_runtime_core.py`。M0=B8。
> 本卷=09-27 复飞复测。代码结构真源=m2_backtest_sim/01_auto_runtime.md（挖干在案，引用不重挖）；本卷补运行态/调度面当日实测。

## 一、六向台账（实证锚点）

| 向 | 内容（09-27 实测） |
|----|------------------|
| 上游输入 | RuntimeConfig/CapabilityRegistry/boot_hooks（M2 册 §二）；trading 面实扫 09-27：`src/zephyr/trading/` 顶层 **56 个 .py**、`trading_contracts/` 递归 **26 个 .py**、`action_dispatcher/` **5 个 .py**、`runtime/async_runtime.py`、`services/` 仅 __init__ 空壳 **〔过时标记 2026-09-29：boot_hooks.py 已被 F62 整改批 35ca1d69cd 修改（+6/-1），见卷末刷新批注〕** |
| 下游消费 | 装配体 13 属性（task_queue/blueprint_watcher/fle_scheduler/dream_cycle/health_monitor/night_shift_queue/status_dashboard 等，M2 册 auto_runtime_core.py:184-306）；health_monitor（F81 入口）、status_dashboard（MOD-INF-035 TUI+JSON 双模式，09-27 头注实读） |
| 自动化触发 | **CLI 手动启动，无常驻主人**：09-27 进程表实扫 `Get-CimInstance ... CommandLine -match "zephyr.trading|auto_runtime"` **零命中**——AutoRuntime 当前未在跑（M2 判"禁跑常驻未实测 boot"一致）；豁免注记=M02 主入口 reconcile 轮询+M10 sleep 心跳（宪法 §9.3 张力已登记豁免） |
| 真源与注册表 | blueprint=docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md（MOD-INF-035，09-27 ls 实存）；本体 auto_runtime_core.py 63,058 字节（09-27 ls，mtime 09-17） |
| 门禁与质量尺 | tests/trading/ 86 件（M2 册）；MEMORY RLIMIT_AS 4GB 在 Windows 静默跳过（__main__.py:44-46，本机内存二级防线空，兜底=reaper 水位=F79 联动） |
| 当前运行状态 | **结构绿/运行空**：代码面 built 维持；本机无常驻实例（09-27 实测）——AutoRuntime 非开机自启件，跑态=人工/会话拉起 |

## 二、子模块三级枚举（09-27 实扫，调度面）

1. **入口层**：`src/zephyr/trading/__main__.py`（main :56；_set_memory_limit :36；reconcile 心跳 :94-103 poll 5s/--once；SIGINT+SIGTERM 停机 :85-88）。
2. **运营中心**：`auto_runtime_core.py`（boot :308、_bootstrap_rbac :353、cron 注册 :414、hooks :429、队列 :437、watcher :445、Ollama 拉活/升级协议 :385-411）。
3. **trading 面实扫族**（09-27）：`trading_contracts/`（broker_interface/factories + execution/market/portfolio/risk 四子域；risk 子域 8 件含 `trading_kill_switch.py`/`kill_switch_state_store.py`=F61 实例族锚点）；`action_dispatcher/`（_annotation_writer/_audit_log_writer/_file_lifecycle_manager/_search_replace_engine 4 件+__init__）；`runtime/async_runtime.py`；`services/` 空壳；顶层散件含 `gpu_consensus_scheduler.py`/`gpu_monitor.py`（F68 联动）、`health_monitor.py`/`status_dashboard.py`（F81）、`process_reaper.py`（F79）。

## 三、接线四态独立复核

- 总册 built → **维持 built（代码态）**；运行态=未常驻（如实注记，非断链：其下游调度职责实际由 DataScheduler+OS 任务群分摊，AutoRuntime 是"运营中心"非"调度唯一主人"）。
- **骨架勘误**：总册 F71 写"三层运行时运营中心（系统大脑）"，但当日无实例在跑且无自启通道——"系统大脑"当前并不 7x24 在岗；若 Owner 期望常驻，缺 windows_service/register 脚本接线（归 F85 环境启动链，已在总册标 partial）。

## 四、缺口清单

| # | 现象 | 处置 | 优先 |
|---|------|------|------|
| 1 | RLIMIT_AS Windows 恒不生效=内存二级防线空 | Job Object API 或量级告警（M2 修法维持）；水位兜底在 F79 | P1 |
| 2 | boot_report 失败仅 print+exit(1) 无告警通道 | 接 AlertManager（M2 修法维持） | P2 |
| 3 | reconcile 轮询 vs §9.3 豁免张力 | 审计时带注记（永久系统四要素） | P2 |
| 4 | services/ 空壳子包 | 内收判据裁定摘/留 | P2 |
| 5 | 无常驻接线（无计划任务/windows_service） | 归 F85 环境启动链；是否常驻=Owner 待裁 | 待裁 |

## 五、自审闸三态

**复核维持（结构挖干+运行态当日补证）**：M2 册六向结构证+本卷当日进程表/文件实体/子目录计数三向补证。三态=**维持 built（代码），运行态"空"如实登记**。**〔过时标记 2026-09-29：引用面有增量变更，刷新见卷末批注〕**

## 刷新批注（2026-09-29 st-finaldel-freshb）

> 刷新基线：HEAD dev @ 0cacd4a64d（09-29）；对卷内真源跑 `git log --since=2026-09-28` 复核。本卷=**轻刷新（非翻面）**。

- **波及 commit**：`35ca1d69cd`（09-29，SW5 夜战卡2·F62 SettlementReconciler 违宪整改）改 `src/zephyr/trading/boot_hooks.py`（+6/-1：事件触发腿+幂等日终 sweep 落地，宪法 §9.3 reconciler 禁 cron 整改）——本卷 §一"上游输入 boot_hooks"引用面被波及，语义=F62 事件化整改经 boot_hooks 挂钩，非 AutoRuntime 本体结构变更。
- **同段邻面（非本卷领地）**：`3065146281`（reaper 孵化收割 PID 复用身份复核）与 `cad41feb2f` H08（process_reaper keep 免死名单身份段匹配）波及 `process_reaper.py`（F79 面）。
- **结构计数复核**：trading 顶层 56 件/trading_contracts 26 件本日复测**不变**；进程表面无常驻实例口径维持。
- **缺口状态修订**：缺口1-5 全部维持原状（本批未触及 F71 缺口面）。
- **自审闸三态（刷新后）**：**维持 built（代码）/运行态空（不变）**——卷内处方全部有效；boot_hooks 行为面变化由 F62 卷领地承载，本卷只登记波及。
- **复跑**：`git log --oneline --since=2026-09-28 -1 -- src/zephyr/trading/boot_hooks.py`（=35ca1d69cd）｜`git show 35ca1d69cd --stat -- src/zephyr/trading/boot_hooks.py`。

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
ls src/zephyr/trading/*.py | wc -l                        # 56
find src/zephyr/trading/trading_contracts -name "*.py" | wc -l  # 26
ls src/zephyr/trading/action_dispatcher/*.py | wc -l      # 5
powershell -NoProfile -Command 'Get-CimInstance Win32_Process | ? {$_.CommandLine -match "zephyr.trading"} | Select ProcessId,CommandLine'  # 当日=空
sed -n '56,110p' src/zephyr/trading/__main__.py
```
