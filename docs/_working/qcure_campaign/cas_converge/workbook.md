---
ttl: task_bound
title: QCure作业簿·cas_converge
session: st-qcure-20260925
---
# cas_converge 作业簿

## 1 环节定义与边界
CAS 推进与收敛环节 = commit_queue_landing.py 的落地点串行化与主区对齐层：dev update-ref CAS（含 _GlobalCommitLock 短窗双锁统一）、CAS 冲突两类死因与池化重放、`_converge_main_workspace` 主区受限收敛、落地后主仓完整性基线刷新、09-24 整树回退治本及其残余面。边界：不含门禁内容判定（→gate_chain）与租约/认领（→queue_scheduler）。

## 2 六向台账

### ①上游输入
- 已过全门禁的 `result.commit_hash`（gateway.commit，LAND:1745-1766；自愈重试 LAND:1772-1797）+ old_dev 点位（`_dev_head` LAND:966）。
- 冲突判定输入：`base_head`（快照真源=入队工作区 HEAD，STALE-01 治本 LAND:1121-1127）、`base_blob`（逐路径，`_entry_base_blob` LAND:1266）、merge-base 锚（LAND:1142）。

### ②下游消费
- dev ref（全仓 HEAD 正门）；主工作区文件字节（受限快进，审计 `.runtime/commit_queue/main_workspace_sync.jsonl`，实测 1703 行）；主仓 integrity 基线（validate_rules_integrity --register，LAND:1613-1640）；done/landed_id（幂等重放判据 LAND:1677-1688）。

### ③机制现状（现行实现+业界参照）
- CAS：`git update-ref refs/heads/dev <new> <old>`（LAND:1431-1477）；CAS 前取 `_GlobalCommitLock(repo_root, timeout=30s)` 消灭与直连提交的 dev 竞态（W4 孤魂提交 301a6ee82a 实证 LAND:1439-1444），锁窗<1s、fail-open 退化裸 CAS（#ARCH-327 曾把异常吞成"锁不可得"致加固静默失效，LAND:1457-1466）。全局锁真源锚主仓根 strip_session_worktree（git_commit_gateway.py:502-519）。
- 两类 CAS 死因：①同路径重叠——legacy 直接死信（LAND:1874-1885），池化拆分后非注册表同路径死信（零覆盖铁律，LAND:1945-1956）、注册表同册交条目级三向合并重放吸收（LAND:1273-1323；基底不可知 fail-closed 死信 LAND:1300-1310）；②重试耗尽——legacy/池均 6 次（`_MAX_CAS_RETRIES` LAND:125）死信"重试耗尽回人工"（LAND:1918-1921,1985-1988）。
- 主区收敛 `_converge_main_workspace`（LAND:1553-1596）：逐文件判 `==new_sha`（already_synced）→`==old_sha`（干净才快进/删除）→脏/缺失/untracked-WIP 一律 skipped_* 留痕（untracked 补盲 LAND:1533-1538）；整体 fail-open——**失败不改变落地结果也不重试**，主区停旧字节等下次同路径落地或人工。
- 基线刷新：落地成功后主仓补跑 --register，不设前缀过滤、幂等、fail-open 留痕（LAND:1612-1640；背景=队列落地的 reconciler 在 worktree 内跑、主仓基线恒 stale→TAMPERED 误报 LAND:1904-1909）。
- 业界参照：GitHub merge queue 对 base 移动=重排队对新 tip 重验（ https://docs.github.com ）；GitLab merge train stalled 车=rebase 后重入（ https://docs.gitlab.com ）；bors=batch 冲突即整批重测（ https://bors.tech ）：三者都以"重放前重验"保正确性——本系统"重放不重跑门禁"是刻意偏离（见 §3.1）。

### ④代码面（实现/测试/调用方全集）
- 实现：WorktreeLanding.__call__ 六步主流程（LAND:1666-1921）；`_pool_cas_replay`/`_replay_commit_without_gates`/`_commit_tree_same_message`（LAND:1926-2038）；池入口 drain_queue_pool（LAND:2201-2273）。
- 测试：test_commit_queue_landing.py(70)+test_commit_queue_landing_nightfix.py+test_commit_queue_pool.py(15)+永久尺 test_audit_fix_lanes_rulers（CAS 例双向验，65c2285a46）。
- 调用方：daemon `_drain_once`→bootstrap_drain_with_landing（DAEMON:112-125）；git_commit.py --enqueue（git_commit.py:930-932）。

### ⑤运维/呈现面
- 分段耗时 landing_phase_stats.jsonl（cas/prestage/converge/baseline/conflict 各段，LAND:794-862）；pool_wave.log；堵点本 bottleneck_ledger.jsonl（registry_drift 记账 LAND 侧调用 DAEMON:184-209）；基线刷新失败仅 logger.warning+返回 note（LAND:1911-1915）——**无独立告警面，TAMPERED 类漂移靠事后审计发现**（已查无基线刷新失败的专项监控）。
- 收敛留痕 main_workspace_sync.jsonl 只记 skipped/error，无聚合视图/告警（已查无消费方，1703 行无人读）。

### ⑥失败态与数据面
- 死信路径全集：CAS 同路径重叠（legacy/池非注册表）、CAS 耗尽、注册表合并冲突/基底不可知（LAND:1302-1320）、NOTHING_TO_COMMIT 假落地防线（LAND:1830-1863，近期实测已产 29 笔——防线本身成新死因族）、重放 RuntimeError（LAND:1959-1960）。
- 环境失败（绝不死信）：LOCK_TIMEOUT（LAND:1821-1825）、瞬态 git 错误 `_TRANSIENT_GIT_MARKERS`（LAND:184-212,1703-1717）、路径锁超时。
- 实测：dead=397；dev==HEAD==77129e94b1（CAS 链当前对齐）；processing=1 在飞。

## 3 缺陷与矿脉清单
已知→QCure 映射：CAS-BASE 15 笔/CASCADE-STALE 8 笔属时序类（方案 §5"预检判不了"）；3WAY 族 64 笔另立矿包（M5.3）。
新矿脉：
1. **【P0·工作区暂存版回退 09-24 治本】** HEAD=65c2285a46 已修"仅当 base_dev..new_dev **零漂移**才复用旧树"（HEAD 版 `_replay_commit_without_gates`：`if not drifted` 才 re-parent，有漂移一律在 new_dev 重建树）；但**当前工作区暂存（git status=M）的 landing 是旧版**：`if not need_remerge`（只看本项注册表路径重叠，LAND:2013 工作区行号）——即 P0 整树回退缺陷本体；同批被剥的还有 `_drift_all_same_session`（同会话迭代放行）、`cat-file -t==commit` 硬化、`_heal_derived_totals`。daemon 纪元自检锚 **HEAD** tree sha（DAEMON:639-713）而进程 import 的是**盘上代码**：现驻 PID 23356（23:16 起）跑的版本不可判定；任何重启/re-exec 即加载暂存旧版。daemon 暂存 diff 另含 +83 行 W-M1 探针（他会话在途件）。按 RULE-WORKSPACE-WIP 不判罚，但 QCure 施工前必须先核清这两文件的 staging 归属。
2. **重放不重跑门禁的正确性风险（评估）**：重放产物="new_dev+再合并注册表"，整册形态（含他会话条目+派生标量）未经门禁；65c2285a46 只补了计数标量自愈，GATE-21 selfcheck/结构类整册门禁在重放段缺位。低频但与矿脉 1 叠加时（旧版判据+池化）回到整树回退风险。
3. **收敛 fail-open 无兜底闭环**：主区 skipped_dirty 留痕后无重试/无周期对账——主区停旧字节直到"某次同路径再落地"；矿脉=收敛 skipped 项入台账聚合+reconciler 事件触发补收敛（禁 cron，符合永久系统四要素）。
4. **基线刷新无告警**：--register 失败（rc!=0/超时 180s）只进 phase note；连续失败可致主仓基线长期 stale→TAMPERED 误报复发（LAND:1904-1909 同形）。建议并入堵点本 kind=alert。
5. **CAS 耗尽死信无退避差异**：6 次重试全速连打（无 backoff），高 CAS 风暴期 6 次可在数秒内耗尽；60s 内 dev 被推进>6 次的物品直接死信——与 queue_scheduler 矿脉 2（B5 attempts 退避）同根，宜统一 attempts 账本。

## 4 自审闸三态裁定
**施工（含前置排障）**——矿脉 1 是 QCure 施工的硬前置：先按 WIP 流程核清 landing/daemon 暂存归属（疑似旧版误暂存），恢复 HEAD 治本态，再谈 M 系列施工；矿脉 3/4 小件可随 M5 并行班；矿脉 2/5 登记不挖。

## 5 长尾清单
- `worktree/`（legacy 单）与 `worktrees/w0-w3`（池）并存，旧 worktree 内 staging 残留无清理通道（已查无 sweeper）。
- `_converge_one` 逐文件两次 `git diff --quiet`+`cat-file`（LAND:1490-1522），大袋时 O(n) 子进程放大；可批量 diff-tree。
- `_noop_overwrite_paths` 读袋 blob 全量算 git blob sha（LAND:1155-1176），无缓存。
- 09-24 两项已登记未做：unborn-HEAD 门侧拒投、--allow-tracked-drift 清单口径（65c2285a46 commit message 尾）。
- main_workspace_sync.jsonl 无轮转/上限（append-only）。
