---
ttl: task_bound
title: L09 案卷 F82 — 订单与结算常驻（盘后管线/夜班队列/工单守护三件接线四态）
session: zc-l09-20260927
updated: 2026-09-29
---

# F82 订单与结算常驻（I 段 S7，骨架态=partial/P0）

## 一、六向台账（2026-09-27 实证）

| 向 | 实测证据 |
|---|---|
| 上游输入 | F57 结算对账三件（settlement_reconciliation/three_way_reconciliation/eod_reconciliation，本卷不重挖）；盘后 15:30 硬时点=A 股 T+1 结算（post_settlement_pipeline.py 头 INVARIANTS，54 号 §3.3） |
| 下游消费 | F63 仓位对账/NAV；`scripts/run_post_settlement.py:87,514` 调 `run_post_settlement_pipeline`（三注入件，产出标注）；`auto_runtime_core.py:84,136,161,249` 持有 NightShiftQueue |
| 自动化触发 | live 计划任务 `ZephyrAlpha_PostSettlement` 存在且 State=Ready（本日 Get-ScheduledTask 实测）；工作日 15:30 one-shot、幂等、exit 0/1/3 语义（M5 05 册基线 09-24 exit 0）；order_daemon 事件驱动设计但零 spawn |
| 真源与注册表 | MOD-TRADING-003（post_settlement_pipeline，[ALGO_FLOW] external yaml）；MOD-INF-035（night_shift_queue）；54_reconciliation_attribution §2.4 缺口#2 |
| 门禁与质量尺 | tests/trading/test_post_settlement_pipeline.py（头 [TESTS] 登记）；对账不一致必告警不静默（INVARIANTS） |
| 当前运行状态 | **黄**：结算腿绿（任务在册+脚本已修），夜班队列半接（宿主未跑），工单守护建成未接线（黄，M5 S4 维持） |

## 二、子模块三级枚举（逐目录实扫）

1. `src/zephyr/trading/post_settlement_pipeline.py`（7471B，MOD-TRADING-003）（已过时，见刷新批注——SW5 卡2 违宪整改后大改，事件触发腿+幂等日终 sweep 落地）
   - `build_post_settlement_jobs()`：任务规格声明（15:30 cron+交易日过滤）——**函数级，不挂生产 APScheduler**（头注自述施工口径）；
   - `run_post_settlement_pipeline()`：SettlementReconciler→DailyAuditor 串联，异常落步骤状态不逃逸；
   - 生产触发面=计划任务→`scripts/run_post_settlement.py`（非 scheduler 槽位）。
2. `src/zephyr/trading/night_shift_queue.py`（6039B，MOD-INF-035）：JSONL 持久化+线程安全夜班登记表；数据路径 `data/runtime/night_shift_queue.jsonl`（shared/contracts/runtime_types.py:43 默认值）。
3. `src/zephyr/ai_layer/scheduling/order_daemon.py`：L5 工单生成守护，消费 SchedulingJournal（单例锁 PID+TTL600s+僵尸检测，零定时器）；胜者落库 emit `evolution_winner_due`。PG 侧 `ai_scheduling.ai_work_order` 表已存在（本日实扫，1 表 0 行）。

## 三、接线四态独立复核

| 件 | 四态判定 | 证据 |
|---|---|---|
| PostSettlement | **已接线** | 任务在册 Ready+消费脚本在+注册脚本坏形态已修（下条） |
| 注册脚本 S1 | **已修复（M5 病灶翻绿）** | HEAD `a0446129e3`"纯回植 8f0e5feba9 修复块"（conhost+cmd /c 真重定向），bc76efe3bf 回退事故已逆转（本日 git log 实证） |
| night_shift_queue | **半接线** | 代码被 auto_runtime_core 持有，但探针时无 auto_runtime_core 进程在跑（Get-CimInstance 零命中）——宿主不在则队列无生产读写 |
| order_daemon | **建成未接线** | `grep OrderDaemon(` src/+scripts 非测试=0 命中；无 __main__、无 register 脚本、无计划任务；`ai_work_order` 0 行=胜者事件零产出（M5 S4 维持） |

## 骨架勘误

1. 骨架括注"recon（order_daemon 建成未接线）"成立，但**结算腿状态被低估**：S1 注册脚本回退病灶已在 HEAD 修复（a0446129e3），"重注册即复断"地雷已排。
2. night_shift_queue.py 头部 `[CONSUMERS]` 为空——实际消费方 auto_runtime_core.py 四处引用，头部声明漂移（登记面欠账实例）。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | order_daemon 零 spawn、ai_work_order 0 行 | 接线须按 journal 事件触发（宪法 §9.3 禁 cron）；与 F86 缺③常驻启动批准同门位 | P1 |
| 2 | night_shift_queue 宿主（AutoRuntime Core）未跑 | 归 F71 启动链；先定宿主再谈队列 | P1 |
| 3 | 注册脚本↔live 任务漂移横断模式（M5 04 册 §三.5） | 重注册惯例前加 action 块 diff 校验 | P2 |
| 4 | build_post_settlement_jobs 函数级未挂 APScheduler（双轨：计划任务 vs scheduler 槽位） | 二选一收敛登记，防双触发 | P2 |

## 五、自审闸三态

**挖干可施工（结算腿与接线判定）**：每态带任务表/进程表/git 锚点 ✅；**待裁**：order_daemon 启动门位与宿主选择（Owner/production 流转）。

## 六、复跑命令

```bash
powershell -NoProfile -Command "(Get-ScheduledTask -TaskName ZephyrAlpha_PostSettlement).State"
grep -n "conhost\|cmd /c" scripts/register_post_settlement_task.ps1 | head -3
grep -rn "OrderDaemon(" src/ scripts/ --include="*.py" | grep -v test | wc -l   # =0
grep -n "NightShiftQueue" src/zephyr/trading/auto_runtime_core.py | head -4
tail -3 data/runtime/post_settlement_last_run.log
```

## 七、刷新批注（2026-09-29 st-finaldel-fresha）

### 9/28 后变更
- `35ca1d69cd`（09-29 SW5 夜战卡2·F62 SettlementReconciler 违宪整改，死袋重投/SW12 代投）：post_settlement_pipeline.py（+176）——**事件触发腿落地**（subscribe_eventbus 幂等订阅+同 trade_date 进程内去重；boot_hooks._subscribe_eventbus_consumers 挂钩）+run_daily_end_sweep 幂等日终 sweep+register_sweep_deps 装配单（**未装配=UNWIRED 显式落状态不伪跑**）；INVARIANTS 增事件触发腿条；99_skipped_for_owner.md +4；test_post_settlement_pipeline.py（+102）。宪法 §9.3 reconciler 禁 cron 违宪点整改（过渡期时钟腿与事件腿并存安全：CLI 幂等+sweep 去重双保险）。
- `a349ddc1fe`（09-28 E8/E9袋）：scheduler.py +28（再平衡调度接线）——本卷 §一调度层引用面行号漂移源。

### 缺口清单状态修订
- 缺口 1（order_daemon 零 spawn）：未见施工，维持。
- 缺口 2（night_shift_queue 宿主）：维持。
- 缺口 3（注册脚本↔live 任务漂移）：维持。
- 缺口 4（build_post_settlement_jobs 双轨二选一）：**部分推进**——过渡期时钟腿+事件腿并存已显式声明（头注 :20-23/:40），收敛未完成；新增 sweep 依赖装配批（register_sweep_deps）待接=UNWIRED 语义（新施工面）。

### 自审闸三态
- **挖干可施工（维持）**；运行状态"黄"维持但构成变化——结算腿增事件触发腿（违宪整改落地），sweep 装配批待接；§二件描述的 file:line/字节数锚全数漂移（7471B→大改），"函数级不挂生产 APScheduler"表述仍准确但需补读事件腿半边。
