---
module_id: MOD-L00-021
title: 调度对账补跑器（Catch-up Guard）蓝图
doc_type: blueprint
status: active
layer: L2_domain
date: "2026-09-03"
version: "0.1.1"
last_updated: "2026-09-03"
language: zh
ttl: permanent
responsibility_domain: 
design_maturity: production
build_status: stable
description: 数据源集成器补盲区——任务档期 vs 打卡记录对账 + 空表兜底 + 自动补跑（L10.7 catchup_guard）
---

# 调度对账补跑器（Catch-up Guard）蓝图 · MOD-L00-021

## 0. 定位

数据源集成器（MOD-L00-004）的补盲区模块。与既有补下载机制分工：

| 机制 | 检测口径 | 缺陷（本模块治本对象） |
|---|---|---|
| L10 weekend_backfill（周一 02:00） | 表内过去 7 天行数缺口 | 只看数据行数；静态表被 threshold=0 主动跳过 |
| L10.5 daily_backfill（每日 17:00） | 当日行数缺口 | 同上，且只回看 1 天 |
| L11 integrity_check（23:00） | 当日达标率 | 只告警不补跑 |
| **本模块 catchup_guard（03:30）** | **任务档期 vs 打卡记录** | 月度/周度/日频任务错过 cron（如 9/1 调度器宕机错过 monthly_static）+ 静态表空表（如 8/10 schema 重建清空数据）——全项目唯一检测点 |

背景事故：2026-09-01 调度器 10:37 才被守护拉起，月初 09:00 的 monthly_static 整批错过，8 张静态表空缺 32 小时无人发现；同期 8/27~9/2 多表漏采。7 天窗口扫描器（backfill_checker）对上述两类缺口结构性失明。

## 1. 职责

1. **档期对账**：遍历 tasks.yaml 全部非 disabled 任务，按 schedule 档期与 progress_store 打卡记录比对，找出"应跑未跑/上次失败"（overdue）任务
2. **空表兜底**：monthly_static / weekend_calibration 档期任务对应的表额外 COUNT 行数，=0 强制判定 overdue（治"打过卡但数据丢了"）
3. **自动补跑**：overdue 任务逐个 `scheduler.run_task(task_id)`（Provider 懒连接，ReplacingMergeTree 幂等去重）
4. **告警与留痕**：对账汇总写 progress_store（task_id=catchup_guard）+ alerter 通知

## 2. 对账规则（档期 → 判定）

| schedule 档期 | 应跑频率 | overdue 判定 |
|---|---|---|
| monthly_static | 每月 ≥1 次 SUCCESS | 本月（自然月）内无 last_status=SUCCESS 记录 |
| weekend_calibration / weekend_backfill | 每周 ≥1 次 | 最近 7 天内无 SUCCESS |
| daily_kline / daily_capital / daily_event / nightly_financial / daily_backfill | 每交易日 1 次 | last SUCCESS 日期 < 最近一个已收盘交易日 |
| pre_market / intraday_* / auction_highfreq / news_slow / event_driven | 当日多次 | last SUCCESS 日期 < 今日 |
| 其他/未知档期 | 不判定 | 跳过（debug 留痕） |

附加规则：

- **空表兜底**：schedule ∈ {monthly_static, weekend_calibration} 的任务，其表 count()=0 → 无条件 overdue（无视打卡记录）
- **交易日晚点**（extra.trading_day_only=true 且今日非交易日）：不计 overdue，计入 deferred（顺延到下一交易日；QMT 服务器非交易日拒绝连接 error 10061）
- **在飞防重**：last_status=RUNNING 的任务跳过（防与在飞执行撞车）
- **单批上限**：单次补跑 ≤15 个（MAX_RERUN_PER_RUN），按 月度>周度>日频 优先级排序，超出部分顺延次日（每日 03:30 必跑，天然收敛）；顺延计数进告警
- **单实例锁**：tmp/catchup_guard.lock（PID 活性检测，陈旧锁 >30min 清理）

## 3. 接口

```python
run_catchup_guard(scheduler) -> dict
# 返回 {"success": bool, "overdue": [...], "rerun": {task_id: bool},
#        "deferred": [...], "skipped_running": [...], "cap_deferred": [...]}
```

调度接线：`scheduler._run_special_schedule` 增加 `catchup_guard` 分支；schedule.yaml 注册 `catchup_guard: cron "30 5 * * *"`（每日含周末）。**05:30 而非 03:30**：周一凌晨已堆 L10(02:00 heavy)+L8(03:00 heavy) 两件重活，03:30 正落 L8 运行窗口内（源配额竞争），05:30 错峰、RUNNING 跳过仅作兜底。**不进** TRADING_DAY_GUARDED_SCHEDULES（守卫须在非交易日也能跑，per-task 交易日晚点在模块内处理）。

手动入口（前端二期接线）：`python -c "from zephyr.data import get_integrator; from zephyr.data.catchup_guard import run_catchup_guard; print(run_catchup_guard(get_integrator()))"` 或 CLI `python -m zephyr.data run` 单任务补跑。

## 4. 依赖

- zephyr.data.scheduler（run_task 实例注入，不反向 import 避免环）
- zephyr.data.backfill_checker._load_tasks_yaml（任务清单真源复用）
- zephyr.data.progress_store（打卡记录）
- zephyr.data.calendar（交易日判定 + 最近交易日）
- zephyr.data.alerter（scheduler._alerter 注入使用）

## 5. 测试

tests/zephyr/data/test_catchup_guard.py：档期判定 5 桶、空表兜底、trading_day_only 顺延、RUNNING 跳过、单批上限截断、陈旧锁清理。外部依赖（ProgressStore/scheduler/CH）全部注入 mock，测试不触网不触库。

## 6. 边界（不做）

- 不做日期级数据行数检测（L10/L10.5 职责）
- 不做超长期历史缺口（known_data_gaps.yaml 职责）
- 不做快照累积类历史回补（源上无历史，物理不可回补；本模块补跑 overdue 快照任务仅止损当日）
- 前端按钮二期（本模块先提供可编程接口）

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-L00-021`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-L00-021` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-L00-021` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-L00-021 | MOD-L00-021 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 7. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 7.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/data/catchup_guard.py` | ✅ 已实现 | |

### 7.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/zephyr/data/test_catchup_guard.py` | ✅ 已实现 | |

### 7.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §7（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
