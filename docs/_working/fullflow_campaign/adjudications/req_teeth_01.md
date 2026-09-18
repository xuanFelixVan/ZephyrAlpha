---
ttl: task_bound
completes_when: 总包对 A18（ALGO-NOTE-SYNC 的 note_confirmed 是否一次性）出裁定，并代解 st-ff-teeth 批次死信
---

# 裁定申请书 · req_teeth_01（施工车道 st-ff-teeth-20260918）

> 本车道执行总包已裁的 R-055a/b/c/d 四条处方（方向已定，本件不再申请方向）。
> 唯一阻塞项 = A18：任务书 §1 R-055a 的 ★ 前提被实测推翻，且**解锁件是总包代管面**，
> 车道侧无合法自愈路径（与 R-012 / A5 同族第三次）。

## A18 【施工阻塞，需总包动手】`note_confirmed: 2026-09-18` 是**一次性凭证**，不能解锁后续 commit

- **任务书原话**（st-ff-teeth-20260918 §1 R-055a ★）：
  "`regime_detector.py` 的 `note_confirmed` 已由总包 22:2x 打到 2026-09-18 并随 `1268f76422`
  落地，所以 ALGO-NOTE-SYNC 这道门现在**不该再拦你**。"
- **实测：仍拦。** 队列项 `q-20260918-st-ff-teeth-20260918-0001`（6 件，含
  `src/zephyr/regime/core/regime_detector.py`）进死信，dead_reason 原文：
  > 门禁 ALGO-NOTE-SYNC 阻断: TDM-E-L1（module_ref=src/zephyr/regime/core/regime_detector.py）
  > ——实现代码被触碰，algo_note_zh 未同 commit 修订（改写该节点 algo_note_zh，或加
  > `note_confirmed: 2026-09-18`）；TDM-E-L1-AGG 同。
- **根因（读门源码确认，不猜）**：`src/zephyr/gov_enforcement/commit_gates/algo_note_sync_gate.py`
  的 INVARIANTS 与 `_collect_node_block_changes*()` 判据都是 **per-commit diff 面**：
  "命中节点须满足之一：a) **同 commit 内**该节点块的 algo_note_zh 行被修订；
  b) **同 commit 内**该节点块新增/更新 `note_confirmed: <日期>`"。
  它读的地图 diff 是 **staged/HEAD 差分**（本件核实：`git show HEAD:config/trading_decision_map.yaml`
  第 261 行确实已是 `note_confirmed: 2026-09-18`）。⇒ **`1268f76422` 把那次
  note_confirmed 用掉了**：HEAD 里"已有"该日期 ≠ 后续 commit 携带该 diff。
  推论：**任何**再触碰 `regime_detector.py` 的 commit 都必须**重新**在地图留一行 diff。
- **为什么这不是车道侧能自愈的**：唯一解锁动作是写 `config/trading_decision_map.yaml`，
  而 COORDINATION_LEDGER §2 判该文件"总包代管"，任务书亦明令"**不要自己去写**，停下来登记"。
- **请总包**（择一，推荐①）：
  1. 对本车道批次**重复**你 22:2x 的解锁动作：`TDM-E-L1` / `TDM-E-L1-AGG` 两节点各加一行
     可差分到的确认注记（例如把 `note_confirmed: 2026-09-18` 改为
     `note_confirmed: 2026-09-18  # teeth R-055a fail-closed`），与队列快照的 6 件
     **同批**落地，然后 `python scripts/commit_queue.py requeue q-20260918-st-ff-teeth-20260918-0001`；
  2. 或显式授权 teeth 车道临时写这两行（登记例外 + GW 计数）。
- **入账建议（协议面，与 R-012 同病）**：给"触碰某 .py 必须先解锁地图"这类门禁补一条
  **一次性凭证**的显式声明——`note_confirmed` 不是"日期窗"而是"随 commit 消耗"，
  派工时把"已打 note_confirmed 所以不会再拦"当前提写成"**只对已落地的那一笔成立**"。
  本役该病已第三次（R-012 pf_alloc/ex_core/risk、A5=本件前手、本件）。
- 现状保护：6 件已入队列快照（`files=6`），工作区字节保持不动，未 `git add -A`，
  未碰他人独占面；本车道其余三条处方（R-055b/c/d）不涉 `regime_detector.py`，**未停等**，
  已另行成批落地。

## 顺带核实的两条对外信息（非申请，供总包记账）

1. **主区 index 存着大面积陈旧快照**（本车道实测）：`git diff --cached --name-only` = **181 件**，
   其中若干文件在 index 里是 **回退代际**：`scripts/backtest/f06_e4_wfa_exam.py`
   （HEAD 有 RB-STATS-01 的 8 处关键符号，index 版 **0 处**，即 staged 净删 117 行）、
   `tests/backtest/test_rb_stats_validator_teeth.py`（index 判**整件删除**，而 HEAD 与工作树都有）、
   `src/zephyr/regime/regime_feature_builder.py`（MM）。
   ⇒ 任何一次 `git add -A`/全量提交都会把前手 RB-STATS 治本**静默回退**（§8 病）。
   本车道按纪律只 `--files` 白名单提交，未触碰他人 index 条目。
2. **测试跑的是工作树字节**：`tests/backtest/test_rb_stats_validator_teeth.py` 以
   `importlib` 直接 exec `scripts/backtest/f06_e4_wfa_exam.py` 的**磁盘版本**（=HEAD 代际，
   非 index 代际），故本车道 E4 相关结论的观测面=HEAD+工作树，特此注明。
