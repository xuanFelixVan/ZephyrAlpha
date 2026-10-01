---
created: 2026-10-01
ttl: task_bound
title: E4 journal 手术记录（st-lanech-20261001 总包亲做）
note: 20261001 删除事故后重建
---

# E4 事件总线 journal 手术记录

## 手术前实态（00:31）

交叉验证发现：本会话挖矿时（09-30 23:30）journal=18 行，手术时（10-01 00:31）仅剩 4 行——
**他队在 21:07 已做过一次毒丸清理**（`pending_events.jsonl.poisonbak-20260930` 留痕）：
坏行、c4_batch_due×2、sim_wallet×10、paper_outpost 旧条目已被处置。00:30 调度器仍活跃
（emit 新 paper_outpost_due 并被 drain 正常出队）——事件面是活的。

## 本手术处置（00:31-00:35）

| 处置 | 对象 | 依据 |
|---|---|---|
| 备份 | 全量 4 行 → `pending_events.jsonl.bak-surgery-20261001` | 可逆性 |
| 删废件毒丸 ×3 | pf_alloc_daily（PIPE-20260923-*，attempts=3 poison） | 09-23 一次性数据事故当日已自愈（last_audit marker 18:25:22 在案），毒丸=过期废件 |
| 摘毒重放 ×1 | sim_observe_daily（PIPE-20260925-105718） | 版本时序错位（事件 09-25 早于 handler 09-27 上库 commit 3522eb8c6d），handler 现已存在 |

## 手术后 drain --all 验证（00:35）

- sim_observe_daily：消费成功 rc=0（day=2026-09-30，观察面四步真实补跑）
- 新 emit 的 paper_outpost_due：正常出队（skipped=module_not_ready，E7 前哨模块未建=已知设计态）
- **pending_left=0，failed=0**——事件面 9 天来首次清零

## 六向台账

上游触发=DataScheduler 唤醒链/CLI/钩子；下游消费=drain FIFO（light 全自动+heavy 显式）；
输入=pending_events.jsonl；输出=last_receipt.json+各 handler 副作用；
真源锚=src/zephyr/strategy_pipeline/pipeline_events.py；耗时账=手术 4min+drain 3min。

**自审闸：挖干**（运行时面；代码面治本见 e4_code_fix.md，已随 582c93ae 落地）。
