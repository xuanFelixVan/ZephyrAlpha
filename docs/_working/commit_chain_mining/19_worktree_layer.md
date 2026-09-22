---
ttl: task_bound
---

# 环节9：worktree 隔离层与合并回主区

> 挖矿：子代理 2026-09-22 凌晨（LANDING 1217 行全文+CQ enqueue/lease/drain/requeue+GW 临时索引段）。与环节4互引。

## A 两套 worktree 一个仓

| | serializer worktree（队列落地） | session worktree（会话隔离） |
|---|---|---|
| 路径/分支 | `.runtime/commit_queue/worktree`｜serializer/commit-queue | `.aidrafts/{sid}/`｜session/{sid} |
| 写者 | 单写者（lease 持有 drain） | 每会话独立 |
| 生命周期 | 常驻复用，每项 reset 回 dev | start 建→merge 后删 |
| 回主区 | **无 merge**：update-ref CAS 推 dev+逐文件字节级收敛 | git merge --no-ff，冲突 abort |

## B 关键机制

- ensure_worktree（LANDING:346-399 建/复用状态机+_provision_env）；_sync_worktree（:401-428 reset --hard+clean -fd，clean 瞬态降级 warning）；_apply_snapshot（:482-513 纯 Python 写盘）；_prestage_snapshot（:518-576 批量 pathspec add/rm）；gateway.commit（worktree 内全链）；_advance_dev CAS（:578-622）；_converge_main_workspace（:669-740 逐文件 4-5 子进程：diff×2+cat-file×2）。
- own-scope 临时索引（#341 方案②，GW:3134-3255）：mkstemp→read-tree HEAD（17003 文件）→200/批 add→pre-commit run 分 chunk→归因（own 阻断/foreign warn）→删。
- 幂等三重（:433-450）+NOTHING_TO_COMMIT 假落地防线（:957-992 逐 blob sha256 对 old_dev 复核）。

## C 六向台账（关键发现）

- **requeue 吃当前快照坑根因**：CQ:1359-1370 快照重建从 `Path.cwd()` 工作区逐文件 read_bytes，**完全无视 dead/ 项里的 blob_ref/blob_sha256 与袋内原始内容**——工作区已推进/换会话时 requeue 落袋的是新内容；base_head 又可空→快进锚漂移。
- **收敛=逐文件子进程**：111 文件≈500 个 git 子进程——批量化的最大单点。
- **reconciler auto-commit 白烧**：落地后 30+ reconciler 在 serializer 分支 auto-commit，产物下次 reset --hard 即弃（LANDING docstring 88-91 自认）。
- **09-17 抢锁事故链**（CQ:782-797/822-831/1125-1131 三处互证）：超 TTL 抢租约→双 drain 同 worktree→thief 的 clean -fd 删 victim 未提交 untracked 新文件→pathspec 死信簇——F9 活体不可抢+逐项 renew 的立法 origin。
- **测试**：landing 46+integration 29+session_worktree 89；缺口=requeue 原袋一致性零回归钉、大批 landing 无性能测试、收敛 untracked 盲区仅 1 正向用例。

## D 成本模型

慢不在逐文件 git 操作（prestage/pre-commit 均 200/批批量），在**每项固定大成本×单写者串行**：reset --hard 全树扫描+171 gate 串行+68 hooks 通道+reconciler 白烧+收敛 500 子进程。拆批摊薄收敛/prestage/通道按文件数项，摊不掉每项固定成本——故配套 reset 短路。

## E 升级机会

1. 【快】**requeue 改从 dead/ 原袋重建**（blob_ref 直读 blobs/{sha}+sha256 自校验；--from-worktree 显式降级选项）——真 bug 修复+回归钉。
2. 【快】**收敛批量化**（一次 diff 分类+cat-file --batch：500→3-4 子进程）。
3. 【快】**reset 短路**（worktree HEAD==dev 且 porcelain 干净→跳过 reset --hard，clean 保留）。
4. 【快】enqueue_item 分步计时（并入环节1 E5）。
5. 🌑 reconciler worktree 禁 auto-commit（契约面+需"派生件不丢"证明）——挂起。
6. 🌑 blob GC（引用计数先行）——挂起 Owner。
7. 封矿：主区真 checkout 化（动 §9.7 受控放松+WIP 零丢失铁律）；任何 clean -fd 绕过/弱化。

## F 自审闸三态裁定（主会话融合）

施工：E1+E2+E3+E4。挂起：E5/E6。封矿：E7 两项。
