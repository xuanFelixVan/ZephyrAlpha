---
ttl: task_bound
title: L09 案卷 F84 — 反馈循环 FBL（collectors/detectors/diagnosers/actors+SLO+自动回滚）
session: zc-l09-20260927
---

# F84 反馈循环 FBL（I 段 S9，骨架态=partial/P1）

## 一、六向台账（2026-09-27 实证）

| 向 | 实测证据 |
|---|---|
| 上游输入 | F81 监控告警族（alert_threshold 38 条+health_monitor）；collectors/ 采集器族（目录实存） |
| 下游消费 | 治理/演进面：evolution_engine.py、auto_evolution.py、evolution/ 目录；宿主注入点=`auto_runtime_core.py:51,172,203-208`（`FeedbackLoopScheduler` 属性注入） |
| 自动化触发 | `scheduler.py:332 poll_interval=30.0`，:530-553 后台轮询循环（`time.sleep` 分片等待）——**进程内轮询型调度器**；探针时全仓无 auto_runtime_core 进程 ⇒ 调度器当前不在跑 |
| 真源与注册表 | `src/zephyr/feedback_loop/` 包本体（scheduler.py 头 [STARTUP] imported/[INVARIANTS] none）；包内 docs/、tests/ 自带 |
| 门禁与质量尺 | 包内 gates/、resilience/、security/、verifiers/、fitness_functions.py、error_budget.py（SLO 面实测在包）；eval_harness.py+meta_harness_optimizer.py 评估面 |
| 当前运行状态 | **黄**：包面大而全（44+ 条目实扫），但宿主未运行 ⇒ 全链当前零生产流量；且与宪法 §9.3"reconciler 禁 sleep-loop"存在口径张力（调度器≠reconciler，但需豁免登记或改事件化，待裁） |

## 二、子模块三级枚举（src/zephyr/feedback_loop/ 逐条实扫，44 项）

1. 编排三件：`core.py`（回路核心）/`scheduler.py`（30s 轮询宿主）/`config.py`。
2. 四段流水线目录：`collectors/`+`detectors/`+`diagnosers/`+`actors/`（骨架所称四段，目录全实存）+`metrics_collector.py`/`feedback_collector.py`。
3. 演进面：`evolution_engine.py`/`auto_evolution.py`/`evolution/`/`session_learner.py`/`skill_library.py`/`self_diagnosis.py`。
4. 安全与质量：`gates/`/`resilience/`/`security/`/`verifiers/`/`validator.py`/`fitness_functions.py`/`error_budget.py`/`slo_manager.py`。
5. 支撑：`db_bridge.py`/`db_writer.py`/`alert_dispatcher.py`/`backpressure_bridge.py`/`module_matcher.py`/`template.py`/`protocols.py`/`exceptions.py`/`forensic/`/`eval_harness.py`/`meta_harness_optimizer.py`/`scheduler_act.py`/`scheduler_collect_detect.py`/`scheduler_health.py`/`scheduler_safety.py`/`generator.py`/`docs/`/`tests/`。

## 三、接线四态独立复核

- **代码面=建成**：44+ 条目在盘，四段流水线目录齐。
- **宿主面=半接线**：唯一生产宿主是 auto_runtime_core 的可选属性注入（`_fle_scheduler: FeedbackLoopScheduler | None = None`，:172）——注入为 None 缺省，宿主进程又未跑 ⇒ **双重空置**。
- **进程面=未接线**：探针 Get-CimInstance 零命中（无 python -m zephyr.trading / auto_runtime_core 实例）。
- **悬空面=无**：非悬空件——有明确唯一宿主声明，属"宿主缺位"而非"无承接"。

## 骨架勘误

1. 骨架括注"partial（M5 补挖项）"方向正确，但缺口定性可收窄：**不是包缺件，是宿主缺位+缺省 None**——包面 44 条目远超骨架"core.py、evolution_engine.py、error_budget.py 等"三件举例。
2. 新发现：scheduler 30s 轮询+sleep 分片设计与宪法 §9.3 事件触发纪律存在**口径张力**（调度器是否属"reconciler"范畴未裁定），建议登记豁免或改事件化——进待裁。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 宿主 AutoRuntime Core 未跑 ⇒ FBL 零流量 | 归 F71/F85 启动链先行 | P1 |
| 2 | 轮询型调度 vs §9.3 事件触发纪律张力 | Owner 裁定：豁免登记（scheduler 类）或改事件化 | P2 |
| 3 | 44 条目子模块与四段流水线的调用图无机检 | 抽 1 条 collect→detect→diagnose→act 链路做真实流量验证 | P2 |

## 五、自审闸三态

**挖干（包面穷举+宿主注入点 file:line+进程探针）✅；待裁（缺口#2 口径）；待挖（深挖四段流水线内部逐件接线，归 M5 补挖项，本卷只判接线态）。**

## 六、复跑命令

```bash
ls src/zephyr/feedback_loop/ | wc -l
sed -n '332p;530,553p' src/zephyr/feedback_loop/scheduler.py
grep -n "FeedbackLoopScheduler" src/zephyr/trading/auto_runtime_core.py | head -4
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object CommandLine -match 'auto_runtime_core' | Measure-Object | Select Count"
```
