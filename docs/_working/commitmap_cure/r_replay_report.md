---
ttl: task_bound
session: st-r-replay-20261004
date: '2026-10-04'
title: R 车道·八袋重放 8→1 金标准·执行报告（袋1重放死信硬停，0/8 落地）
completes_when: 总筹死因判定消费后随一本账收敛批转归档
---

# 八袋重放执行报告（sid=st-r-replay-20261004）

> **执行摘要**：两道前置核验全过后按任务书发车；袋 1（-0004）plain requeue 被**复发熔断**拦（非死信），按工具文书处方 `--force`（留痕）越过发出重放袋 `q-20261004-st-deadletter-cure-20261003-0014`；该袋经 2 次落地尝试后于 23:34:17 死信（CLAIM_REQUIRED_VIOLATION）→ **触发硬停止条件，立即停全车道**，袋 2-8 按铁律零 requeue。金标准 8/8 一过=**未达成（0/8 落地）**，呈总筹终审。全程零 git commit/零 git add，写操作仅 requeue 命令 2 次。

## 0. 前置核验（两道全过，证据留档）

| 前置 | 结论 | 证据 |
|---|---|---|
| ① 手术批+一本账批落地 | **过** | 手术批三件 `5611dbf3ca`(st-sA 手术③④)/`1d291d36e5`(st-sB 活性合流)/`28907940e5`(st-sC C-2/D 三件套)在 HEAD；wave-2 切换宣告 `7f0beccac4`+`d0abe696ee`（Owner 放行令）在 HEAD；合并器 aliases 地雷修 `fdfe8fe302`（06 号 §3.3「等窗口」条件）在 HEAD |
| ② health 无新增死因族 | **过** | `commit_queue.py health` ALERT fired=false；观测窗内 +1 死（`q-20261004-st-tdm-mountgate-20261005-0001`，dead_reason=dev CAS 冲突重试耗尽，池化重放竞争类=已知 env 族，他会话袋非新车道） |

## 1. 八袋清单（法源注记）

任务书指定 qid 清单以 `04_ruling_package.md` D 节为准——D 节只载金标准定义（「八袋接力原始死袋重放，8 次→1 次过」）**不含 qid**；qid 清单双源一致采信：`f6_doctorscan_refresh.md:200` 与 `06_replay_evidence.md:9`（总筹定稿）→ `q-20261003-st-deadletter-cure-20261003-0004..0011`，共 8 袋，每袋 9 文件，属主会话 st-deadletter-cure-20261003。

## 2. 八袋×结果表

| # | 原始 qid（尾号） | 原始死因族 | 重放动作（本车道） | 重放 qid | 结果 | 本次尝试次数 | 落地 commit | 本次死因 |
|---|---|---|---|---|---|---|---|---|
| 1 | -0004 | ghost_session 存活闸拒（历史复发 23） | plain requeue 22:23:28 被复发熔断拒 → `--force` 22:24:12 发出（工具处方，meta.requeue_forced=true 留痕） | `q-20261004-st-deadletter-cure-20261003-0014` | **DEAD** 23:34:17 | attempts=2 | 无 | CLAIM_REQUIRED_VIOLATION（原文见 §3） |
| 2 | -0005 | MODULE-ID-CONSISTENCY 碰撞 | **未 requeue（硬停止条件）** | — | NOT_REQUEUED | 0 | 无 | —（原始死信项原样在 dead/） |
| 3 | -0006 | ghost 三连 | 同上 | — | NOT_REQUEUED | 0 | 无 | — |
| 4 | -0007 | ghost 三连 | 同上 | — | NOT_REQUEUED | 0 | 无 | — |
| 5 | -0008 | ghost 三连 | 同上 | — | NOT_REQUEUED | 0 | 无 | — |
| 6 | -0009 | MODULE-ID-CONSISTENCY 碰撞 | 同上 | — | NOT_REQUEUED | 0 | 无 | — |
| 7 | -0010 | NEW-FILE-DEPGRAPH 未登记 | 同上 | — | NOT_REQUEUED | 0 | 无 | — |
| 8 | -0011 | NO-SECRET-HARDCODE 误伤 | 同上 | — | NOT_REQUEUED | 0 | 无 | — |

袋 2-8 零触碰实证：其 `requeued` 标注与 `requeue_count`(1-7) 全部为 2026-10-03 原接力链历史，本车道未新增任何标注（逐袋读 dead/*.json 核验于 23:40）。

## 3. 死信原文抄录（袋 1 重放袋 -0014，判定权归总筹）

**dead_reason（逐字）**：

> 网关落盘失败（CLAIM_REQUIRED_VIOLATION）: session 'st-deadletter-cure-20261003' 已注册但目标文件未 claim（claim 前移协议，宪法 RULE-WORKTREE「并发与提交」）: ['D:\ZephyrAlpha\.runtime\commit_queue\worktrees\w2\scripts\commit_queue.py', 'D:\ZephyrAlpha\.runtime\commit_queue\worktrees\w2\scripts\governance\commit_queue_landing.py', 'D:\ZephyrAlpha\.runtime\commit_queue\worktrees\w2\scripts\governance\dead_letter_doctor.py', 'D:\ZephyrAlpha\.runtime\commit_queue\worktrees\w2\tests\governance\test_commit_queue_b5_backoff.py', 'D:\ZephyrAlpha\.runtime\commit_queue\worktrees\w2\tests\governance\test_commit_queue_backfill_lane.py', 'D:\ZephyrAlpha\.runtime\commit_queue\worktrees\w2\tests\governance\test_commit_queue_landing_qmine_a1.py', 'D:\ZephyrAlpha\.runtime\commit_queue\worktrees\w2\tests\governance\test_dead_letter_doctor.py', 'D:\ZephyrAlpha\.runtime\commit_queue\worktrees\w2\tests\governance\test_pool_dead_letter_seal.py']. commit 前 MUST 调 claim_files 声明工作范围。

**袋内 files 清单（9 文件，action 全=modify）**：

1. `scripts/governance/commit_queue_landing.py`
2. `scripts/commit_queue.py`
3. `scripts/governance/dead_letter_doctor.py`
4. `tests/governance/test_pool_dead_letter_seal.py`
5. `tests/governance/test_commit_queue_backfill_lane.py`
6. `tests/governance/test_dead_letter_doctor.py`
7. `tests/governance/test_commit_queue_b5_backoff.py`
8. `tests/governance/test_commit_queue_landing_qmine_a1.py`
9. `docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml`

**死信元数据**：dead_at=2026-10-04T23:34:17+08:00｜dead_signature=`item:网关落盘失败（CLAIM_REQUIRED_VIOLATION）`｜attempts=2｜meta.requeued_from=q-20261003-st-deadletter-cure-20261003-0004｜meta.requeue_forced=true｜requeue_count=1｜session_id=owner_session=st-deadletter-cure-20261003｜branch=dev｜base_head=9d246347f98e（10-03 原基座随袋字段）｜处方字段=「门禁物品性失败：按 dead_reason 中 gate 标识修复物品本身后重投」。

**两次尝试经过（事实还原）**：attempt 1 死于 `LandingEnvironmentError: 路径锁等待超时（同路径项在途持锁）: .../capability_canonical_file_registry.yaml`（hot-registry 并发退避自动重试）；attempt 2（last_retry_at 23:26:15）死于 CLAIM_REQUIRED_VIOLATION（23:34:17）。落袋前置均过：ghost 存活闸放行（属主 heartbeat 末行 status=alive@2026-10-03T05:37Z，按判定序① heartbeat 优先）、registration_gate findings=0、冲突标记预扫零命中。

## 4. 金标准判定

**8/8 一过 = 未达成（0/8 落地）**：袋 1 重放袋死信即触发任务书硬停止条件，本车道立即停车，袋 2-8 未重投。判定呈总筹终审。

供总筹判读的事实面（本车道不判定）：

1. **裸 requeue 对八袋不可行**：八袋同签名历史死亡 23-64 次全部触发复发熔断（波 1B 1.7c），plain requeue 在重投口即拒；工具文书处方=修因后 `--force` 留痕越过。本车道仅对袋 1 用了一次 `--force`。
2. **重放袋继承原属主死会话**：`commit_queue.py:2978` `enqueue_item(session_id or old_item.get("session_id", ""))`——不带 `--session` 的 requeue 把新袋绑回 st-deadletter-cure-20261003；CLAIM-REQUIRED 门（claim 前移协议）按该会话索 claim，而死会话无法补 claim=结构性缺口（本轮死因）。CLI 有 `--session` 形参可换绑，任务书命令为裸 requeue，本车道未越权换绑。
3. **原八死因对治面未被证伪**：本次死因（CLAIM_REQUIRED_VIOLATION）不在原八死因族内，属新管线门（claim 前移协议）与死会话属主继承的交集面；ghost 闸/合并器/内容合并/noop 幂等路径均未到达或未拦截。
4. **总筹既有定稿口径并存**：`06_replay_evidence.md`（总筹定稿 2026-10-04，bffc7ae267 落 HEAD）载「F6 终判：八袋内容全被收编无需重投——故重放取逐死因对治+术后零复发实证口径」；本车道执行的是任务书的物理重放口径。两口径关系归总筹。
5. 队列夜况：本车道在制期间队列正常排水（22:46-23:16 他车道 7 袋 done），本轮死信非排队饥饿所致（袋获拾取并两次实跑落地链）。

## 5. 纪律执行自证

- 全程零 `git commit`/零 `git add`；全部写操作=2 次 requeue 命令（袋 1 plain 1 次[被拒，零副作用]+--force 1 次[产生 -0014]）。
- 死信后零二次 requeue：袋 2-8 原始死信项原样留 dead/，-0004 原项仅按 requeue 协议获 `requeued={new_qid}` 双向留痕标注。
- 看护器（`.runtime/tmp/r_replay/relay_watch.py`）串行链设计=前袋终态才发下袋、死信即 chain_stop；journal 全程留痕 `.runtime/tmp/r_replay/journal.jsonl`（7 事件：chain_start/pre_dispatched_adopt/requeue_refused[seed]/requeued_force[seed]/bag_result DEAD/chain_stop）。
- 停车时点队列态：本袋已终态，无本车道遗留 pending/processing 项。

[no-lookup: 重放执行，任务书已含全部真源指针]

**本车道未做任何判定，全部判定权归总筹。**
