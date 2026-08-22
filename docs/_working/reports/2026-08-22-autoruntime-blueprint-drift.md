---
ttl: task_bound
title: AutoRuntime Core 蓝图-代码漂移 5 项实证与裁定（04号文 Phase 0 步骤 0.1）
date: 2026-08-22
module_id: MOD-INF-035
source_plan: docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/04_autoruntime_core_build.md §4 Phase 0 步骤 0.1
blueprint: docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md（v6.0.2）
---

# AutoRuntime Core 蓝图-代码漂移 5 项实证与裁定

> 工单：18号清单 §6 波3-04（04号文 AutoRuntime T0 拐点，GP0 退出项 E0-5）。
> 实证基准日 2026-08-22，验证方式：`Test-Path` / LS / Grep。
> 04号文原文写「蓝图只读，本文不代改，走 §6 Q3 裁定流程」；本工单授权施工代理按实证直接修正蓝图文本，逐项裁定如下。

## 漂移项逐项实证与裁定

| # | 蓝图条目 | 实证（2026-08-22） | 裁定 | 蓝图修正 |
|---|---------|-------------------|------|---------|
| 1 | §0.1 行8 `circadian_scheduler.py`「已实现」 | `src/zephyr/trading/circadian_scheduler.py` **不存在**（`Test-Path`=False）。节律阶段展示由 `status_dashboard.py` 模块级纯函数 `_current_phase()` 承载（原 `CircadianScheduler.get_current_phase()` 内联实现，文件头注释注明 2026-06-26 裁定废除定时调度）；boot 流程钩子保留在 `auto_runtime_core.py`；`start_brain.py` docstring 明示「定时调度已废除，start/register_task/stop/save_state 为 no-op」 | **幽灵文件，不复活**。功能承载=status_dashboard.py（展示）+ auto_runtime_core.py（boot 钩子）；T2「CircadianScheduler 轮转」承载文件裁定=`dream_cycle.py`（04号文 §4 步骤 2.3 候选之一，与夜间固化同域） | §0.1 行8 改为「~~circadian_scheduler.py~~（无独立文件，2026-06-26 裁定废除）」；§16.3 步骤3 变更清单与 §17 升级组件清单的 `circadian_scheduler.py` 改为 `dream_cycle.py` |
| 2 | §0.1 行10 `health-monitor.py`（连字符） | `src/zephyr/trading/health-monitor.py` **不存在**；`src/zephyr/trading/health_monitor.py`（下划线）**存在**，production，含 `pressure_level()`/`pressure_response()`/`auto_restart()` | **命名漂移**：连字符→下划线。Python 模块不可含连字符，代码为准 | §0.1 行10、§16.3 步骤2 变更清单、§16.5 行3、§17 升级组件清单全部改为 `health_monitor.py` |
| 3 | §0.1 行11 `feedback_loop.py`（挂在 trading 包清单下） | `src/zephyr/trading/feedback_loop.py` **不存在**；独立包 `src/zephyr/feedback_loop/` **存在**（含 core.py，蓝图 §16 自身行 1029 亦实测登记 `src/zephyr/feedback_loop/core.py` ✅） | **落盘位置漂移**：反馈闭环是独立包而非 trading 下单文件，代码为准 | §0.1 行11 改为 `feedback_loop/（独立包 src/zephyr/feedback_loop/）` |
| 4 | §0.1 附加行 `boot_cron_jobs.py` | `src/zephyr/trading/boot_cron_jobs.py` **不存在**；`src/zephyr/trading/boot_hooks.py` **存在**（production，启动钩子） | **更名漂移**：boot_cron_jobs.py → boot_hooks.py，代码为准 | §0.1 附加行改为「~~boot_cron_jobs.py~~（更名为 boot_hooks.py，见下行）」（保名留痕不删行，遵守安全删除协议） |
| 5 | §16.3 步骤1~4「产出位置 `src/zephyr/runtime\`」+ 验证命令 `tests/runtime/...`；§16.5 产出绝对路径 `src/zephyr/runtime/...`、`tests/runtime\`；§11 产出物目录；§16「涉及的文件范围」 | `tests/runtime/` **不存在**（`Test-Path`=False）；`src/zephyr/runtime/` 存在但属 MOD-RUNTIME_INTRADAY（intraday_main.py 盘中数据流编排，不同物，04号文 §3.3 已裁定）；大脑代码实测在 `src/zephyr/trading/`（44 个 .py），测试在 `tests/trading/` + `tests/automation/` | **产出位置/测试目录漂移**：runtime→trading，代码为准。验证命令按实测存在的测试文件改写；`test_mape_k.py`/`test_circadian_scheduler.py` 无实测等价物——前者登记 T1 施工时补建，后者随幽灵文件一并废除 | §16.3 四处产出位置、四条验证命令、§16.5 五行路径与存在性勾选（全部 ✅）、§11 产出物目录、§16 涉及文件范围全部改为 trading 口径 |

## 蓝图文本修正落点汇总（diff 已直接落蓝图文件）

- `docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md`：
  - §0.1 文件清单：行8/10/11 + 附加行 boot_cron_jobs.py（4 处）
  - §11 产出物存放目录：业务代码/测试代码两行
  - §16.3 步骤 1~4：产出位置 ×4、验证命令 ×4、变更清单（health_monitor.py / dream_cycle.py）×2
  - §16.5 施工完成标准：5 行路径改为 trading/tests-trading+automation，存在性按实测全部标 ✅
  - §16「涉及的文件范围」：2 行
  - §17 升级组件清单：`health-monitor.py`→`health_monitor.py`、`circadian_scheduler.py`→`dream_cycle.py`；T0 三项（CapabilityRegistry 内存缓存 / StatusDashboard 聚合视图 / StopGate 预算）状态按本工单施工结果标 ✅ 已施工（2026-08-22）

## 遗留登记

| 项 | 说明 | 归属 |
|---|------|------|
| test_mape_k.py 无实测等价物 | MAPE-K 循环现经 `tests/automation/test_auto_runtime_core.py` / `test_auto_runtime_e2e.py` 覆盖；T1 事件驱动落地时补建专测 | 04号文 Phase 1（触发式，未触发不施工） |
| trading.health_monitor 无独立单测 | 现经 `test_status_dashboard.py`（mock）与 e2e 间接覆盖；`tests/governance/ops/test_health_monitor.py` 测的是 gov_code_quality 同名不同物 | T1「HealthMonitor 分层检查」施工时补建 |
