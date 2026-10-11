---
ttl: task_bound
owner: st-maint3-20261011
campaign: 维护三班 → GPU 车道 知会件（令 3 项 5）
---

# 知会 · GPU 互斥组重投触发器已满足（SCHED-NOTICE-20261011-T7）

> 触发条件＝总统统筹令 3 项 5"T7 落地"。本班只知会、**不代投**：他会话的袋由属主道或 Owner 处置
> （在册纪律：代投车道的在途字节会因"车道自己后落地"变成回退弹；`ghost_session` 死袋的 CLI 强制
> requeue 属人工/Owner 面，AI 不擅动）。

## 一、T7 已落地的实测凭据（等本班袋进 HEAD 后才会对门生效）

| 面 | 落后面读数 | 取数方式 |
|----|-----------|---------|
| 时间真源 | `register_sim_bridge_execute_task.ps1:47` = `-Daily -At "09:45"`（13:05 腿 `:48` 未动）；`register_decision_chain_sentinel_task.ps1:69` = `-Daily -At "09:50"` | 直读盘面 + `git diff --numstat`＝5/5 与 7/7（行数守恒 60/90 不变） |
| 注册表 | `sch_sim_bridge_execute` = `45 9 * * *|5 13 * * *`；`sch_decision_chain_sentinel` = `50 9 * * *`；`generated_at: 2026-10-11T15:14:11Z`；`total_entities: 103` | 生成器经 `apply_resource_plan.py` 单口写回后自动跟生 |
| 天花板 | `mem_ceiling_gb: 10.0` 未动（表头第 16 行/生成器常量/reaper `_DANGEROUS_MEM_GB` 三面同钉，测试 `test_ceiling_constant_pinned_at_10gb_across_three_truth_sources` 守） | 同上 |
| 自家测试 | `tests/infra/infrastructure/test_resource_schedule_mem_ceiling_invariant.py` **11 passed**（本令进场时 5 failed） | 实测复跑 |

## 二、GPU 袋撞的那两条阻断＝本 T7 消解的那两条（逐字对得上）

死信 `q-20261011-st-gpux-20261011-0010`（属主会话 `st-gpux-20261011`，state=dead）的
`dead_reason` 原文（实测自 `commit_queue.py status` 快照）：

```
门禁 RESOURCE-SCHEDULE 阻断: RESOURCE-SCHEDULE: 2 条阻断级排班冲突——
[sched_mem_ceiling/block] …+sch_sim_bridge_execute: 同窗并发内存和 10.5GB > mem_ceiling_gb=10.0（at=2026-10-12T09:35:00+08:00）;
[sched_mem_ceiling/block] …+sch_decision_chain_sentinel+sch_paper_session+sch_sim_bridge_execute: 同窗并发内存和 11.0GB > mem_ceiling_gb=10.0（at=2026-10-12T09:40:00+08:00）
```

同一把尺（`resource_schedule_gate` 三面 + C-8）对**存档旧代**与**落后面**的逐臂对账（实测）：

| 检查臂 | T7 前 | T7 后 | 消解 |
|---|---|---|---|
| `sched_mem_ceiling` block | 3（10-12 09:35 / 10-12 09:40 / 10-13 05:50） | **1**（10-13 05:50） | 2 ← 正是 GPU 袋撞的那两条 |
| `sched_overlap_group` block | 0 | 0 | 0 |
| `sched_e0_trading` block | 0 | 0 | 0 |
| `sched_pool_concurrency`(C-8) block | 1（10-12 15:10） | 1（同） | 0（非本令对象，未动） |

## 三、重投前须知（两条既存 block 不是本班造的，别当本班回归）

1. **10-13 05:50 同窗内存和超线**（`data_slot_catchup_guard`+`news_slow`+`pf_alloc_rebalance_check`+`weekend_calibration` 族）——
   T7 前就在册存在，本班未触碰该带；
2. **10-12 15:10 池 default 同刻跨组并发 2.5GB**（`data_slot_sector_close_final`+`sch_index_minute_eod`）——同上。

RESOURCE-SCHEDULE 门本体是 **own-scope** 口径（实测
`src/zephyr/gov_enforcement/commit_gates/resource_schedule_gate.py:464`："focus=None=全量判；
否则须命中本次变更实体才报"），故 GPU 袋若改动面不碰上述两组实体，重投不会再被这两条拦；
若碰，则须按各自域处置，**禁为过门放宽 10.0 上限或改判据阈值**。

## 四、请 GPU 车道做的事（本班无权代做）

- 待本班袋进 `dev`（核账：`git show dev:config/resource_profile_registry.yaml | grep -c "45 9 \* \* \*|5 13 \* \* \*"` 应 ≥1）后重投互斥组袋；
- 属主会话已判 `ghost_session` 的袋，按在册复投配方：**新袋重投**（正门重注册 `pid=0`＋重拉 heartbeat_daemon 后重新 enqueue，勿 `--from-bag`）；
- `exclusive_group` 是真源在**表内人审字段**的生产者=人——重投时若改组标，须与 `apply_resource_plan.py` 的 `new_exclusive_group` 通道同批，禁手改册后不再生。
