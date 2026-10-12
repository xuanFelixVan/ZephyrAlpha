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

## 五、2026-10-12 03:1x 现网补证：方向尺在**今天的共享池**上又抓到同形态（本班未拦截，只如实呈报）

本班用刚落地的姊妹尺（`registry_mass_deletion_gate.classify_pool_regression_direction`，与
写者层/入队层同一口径）对主区 `git diff --cached --diff-filter=M` 全集跑了一次读数：
**14 件在途 M 件＝clean 6／mixed 5／纯驱逐 1／近子集 2／读不动 0**。

| 形态 | 件 | 读数（HEAD 独有／staged 独有） | 本班处置 |
|------|----|------------------------------|---------|
| 纯驱逐 strict | `docs/_working/gpufeed_campaign/03_gpux_final_report.md` | 61／0 | **GPU 车道自证**：这是"删了已入库 61 行却一行没加"的形状，与 2026-10-11 夜案卷受害件同形态。若属你道有意收尾（整档改写）请走 `git checkout HEAD -- <件>` 重基后再改；确要覆盖则提交信息带 pool-regression-ack 理由≥10 字（仍留痕）。本班不代判意图、不代改字节。 |
| 近子集 near | `src/zephyr/backtest/gpu_core.py` | 140／6 | warn 级：比值 0.043≤0.05。请核一遍是不是旧稿覆盖（该件 10-11 案卷里也出现在嫌疑清单）。 |
| 近子集 near | `tests/research/backtest/test_l2_gpu_landing.py` | 231／1 | 同上（比值 0.004）。 |

复核口令（属主车道可自行跑，只读）：

```
PYTHONPATH=src python -c "import subprocess,sys;sys.path.insert(0,'src');from zephyr.gov_enforcement.commit_gates.registry_mass_deletion_gate import classify_pool_regression_direction as c,_pool_direction_pair as dp;o=lambda a:subprocess.run(a,capture_output=True).stdout.decode('utf-8','replace');[print(p,c(o(['git','show','HEAD:'+p]),o(['git','show',':'+p])),dp(o(['git','show','HEAD:'+p]),o(['git','show',':'+p]))) for p in subprocess.run(['git','diff','--cached','--name-only','--diff-filter=M'],capture_output=True).stdout.decode().splitlines() if p]"
```

说明两点口径：①这三件都是**他道在途件**，本门 own-scope 生效（外来 staged 只 warn+审计，不连坐），
所以本班提交不会拦它们、也不该拦；列在这里是因为**形态重现**必须留痕，而不是本班要替谁修。
②本班自己的两本门册此刻也在同一清单里（clean/mixed），已逐件核过＝纯追加＋标量改行，非驱逐。
