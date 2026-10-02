---
ttl: task_bound
gate_selfdoc: GIT-DANGEROUS
session: st-ffchief-20261002
date: 2026-10-02
title: 分支判定矩阵台账
completes_when: 153 分支全判定+清零执行+二轮观察清单移交
---

# 分支清零台账（branches_ledger）— st-ffchief-20261002 / B1 车道

> 执行时点：2026-10-02 04:00 +08:00｜执行者：B1 分支清零代理｜授权：Owner 总授自裁（00_orchestration.md §1）
> 基线：本地 153 分支 + 远端 3 ref；基准分支=dev（5aa2b07cb0）。
> 判定规则：①已并入 dev（merge-base is-ancestor）→直删；②未并入有独特 commit→`tag archive/<名斜杠转双下划线>` 后删（零丢失可复活）；③未并入无独特 commit→直删；④worktree 占用/活跃会话（registry last_activity<7200s：st-c10-t0gpu/st-c10-f56ch/st-c10-inv/st-c10-final3/st-chief7-20260928/st-ffchief-20261001）→保留观察；⑤主干保留；⑥远端只读登记不动。
> 顺序纪律：**先写本台账，后执行删除**；tag 先打后删分支，顺序不可反。
> 活跃会话佐证：.runtime/session_registry.json 7 会话，其中 6 个 <2h（st-lanech-main-20261001 已 4.2h 超阈值，其分支按规则归档，tag 可复活）。

## 一、判定矩阵（153 本地 + 3 远端，全量）

### A. 保留·主干（1）

| # | 分支 | 并入dev | 独特commit | 末活动(+08:00) | 判定 | 去向 |
|---|------|---------|-----------|---------------|------|------|
| 1 | dev | 是(基准) | 0 | 2026-10-02 02:37 | 主分支 | 保留 |

### B. 保留观察·worktree 占用（12）

| # | 分支 | 并入dev | 独特commit | 末活动(+08:00) | 判定 | 去向 |
|---|------|---------|-----------|---------------|------|------|
| 2 | session/st-chief7-20260928 | 是 | 0 | 2026-09-28 03:59 | 活跃会话 sid=st-chief7-20260928(<2h) + worktree 占用(.aidrafts/st-chief7-20260928) | 保留观察 |
| 3 | session/st-ffchief-20261001 | 是 | 0 | 2026-10-02 02:14 | 活跃会话总包 sid=st-ffchief-20261001(<2h) + worktree 占用 | 保留观察 |
| 4 | session/st-mapcensus-20260924 | 是 | 0 | 2026-10-02 00:54 | worktree 占用(.aidrafts/st-mapcensus-20260924)，末提交今日 | 保留观察 |
| 5 | session/st-commitfix-20261001 | 是 | 0 | 2026-10-01 02:09 | worktree 占用(.aidrafts/st-commitfix-20261001, locked) | 保留观察 |
| 6 | serializer/commit-queue | 是 | 0 | 2026-10-02 02:14 | 提交队列永久系统分支 + worktree 占用(.runtime/commit_queue/worktree, locked) | 保留观察(基建) |
| 7 | serializer/commit-queue-w0 | 是 | 0 | 2026-10-02 01:53 | 同上(w0) | 保留观察(基建) |
| 8 | serializer/commit-queue-w1 | 是 | 0 | 2026-10-02 02:14 | 同上(w1) | 保留观察(基建) |
| 9 | serializer/commit-queue-w2 | 是 | 0 | 2026-10-02 01:29 | 同上(w2) | 保留观察(基建) |
| 10 | serializer/commit-queue-w3 | 是 | 0 | 2026-10-02 02:37 | 同上(w3) | 保留观察(基建) |
| 11 | ai/st-c7-autofix-20260927/task-automation-false-green | 是 | 0 | 2026-09-27 15:57 | worktree 占用(.worktrees/st-c7-autofix-20260927, locked) | 保留观察 |
| 12 | ai/st-chief7w-20260927/task-fullconnect-landing | 是 | 0 | 2026-09-27 12:25 | worktree 占用(.worktrees/st-chief7w-20260927, locked) | 保留观察 |
| 13 | ai/st-chief4-20260927/gate-and-landing | 否 | 1 | 2026-09-27 12:24 | worktree 占用(locked)+未并入 1 commit | 保留观察+保险tag `archive/ai__st-chief4-20260927__gate-and-landing`（防 worktree 强拆后 GC） |

### C. 归档后删除·未并入有独特 commit（24）

| # | 分支 | 并入dev | 独特commit | 末活动(+08:00) | 判定 | 去向 |
|---|------|---------|-----------|---------------|------|------|
| 14 | ai/chiefzc-surgeon-20260928/dead-letter-rescue | 否 | 1 | 2026-09-28 05:32 | 未并入有独特 commit，属会话已退役 | tag `archive/ai__chiefzc-surgeon-20260928__dead-letter-rescue`→删 |
| 15 | ai/st-ailayer-sx-20260927/task-ai-12items | 否 | 12 | 2026-09-28 02:56 | 未并入 12 commit（本批最大），属会话已退役；tag 全量可复活 | tag `archive/ai__st-ailayer-sx-20260927__task-ai-12items`→删 |
| 16 | ai/st-c8-digest2/task-digest-main-landing | 否 | 2 | 2026-09-29 08:11 | 未并入有独特 commit | tag `archive/ai__st-c8-digest2__task-digest-main-landing`→删 |
| 17 | ai/st-chiefzc-docs-20260928/fullflow_closeout | 否 | 1 | 2026-09-28 05:03 | 未并入有独特 commit | tag `archive/ai__st-chiefzc-docs-20260928__fullflow_closeout`→删 |
| 18 | ai/st-commitspeed-tbl-20260924/task-commit-chain-instrumentation | 否 | 1 | 2026-09-25 04:02 | 未并入有独特 commit | tag `archive/ai__st-commitspeed-tbl-20260924__task-commit-chain-instrumentation`→删 |
| 19 | ai/st-e2e-20260924/e2e-integration | 否 | 2 | 2026-09-23 21:50 | 未并入有独特 commit | tag `archive/ai__st-e2e-20260924__e2e-integration`→删 |
| 20 | ai/st-gpu-final-20260924/gpu-final-campaign | 否 | 1 | 2026-09-24 07:40 | 未并入有独特 commit | tag `archive/ai__st-gpu-final-20260924__gpu-final-campaign`→删 |
| 21 | ai/st-lanech-20261001/task-lane-chain-fix | 否 | 9 | 2026-10-01 22:51 | 未并入 9 commit；registry sid=st-lanech-main-20261001 末活动 4.2h>7200s 阈值，按规则归档（tag 可复活，若该队复活从 tag 恢复） | tag `archive/ai__st-lanech-20261001__task-lane-chain-fix`→删 |
| 22 | ai/st-menu-t1b6-20260930/task-t1b6-indicator-disposal | 否 | 1 | 2026-10-01 00:25 | 未并入有独特 commit（与 session 分支互不包含，双 tag 各自保全） | tag `archive/ai__st-menu-t1b6-20260930__task-t1b6-indicator-disposal`→删 |
| 23 | ai/st-nightsweep-sw11-20260929/nightsweep-sw11 | 否 | 2 | 2026-09-29 07:11 | 未并入有独特 commit | tag `archive/ai__st-nightsweep-sw11-20260929__nightsweep-sw11`→删 |
| 24 | ai/st-nightsweep2-merge2-20260930/merge-train | 否 | 7 | 2026-09-30 16:45 | 未并入有独特 commit | tag `archive/ai__st-nightsweep2-merge2-20260930__merge-train`→删 |
| 25 | ai/st-nightsweep2-nb1-20260930/nightsweep2-B-lane-mining | 否 | 1 | 2026-09-30 07:25 | 未并入有独特 commit | tag `archive/ai__st-nightsweep2-nb1-20260930__nightsweep2-B-lane-mining`→删 |
| 26 | ai/st-nightsweep2-nb2-20260930/nightsweep2-nb2 | 否 | 6 | 2026-09-30 07:21 | 未并入有独特 commit | tag `archive/ai__st-nightsweep2-nb2-20260930__nightsweep2-nb2`→删 |
| 27 | ai/st-nightsweep2-nf-20260930/nf-exec-lane | 否 | 6 | 2026-09-30 09:27 | 未并入有独特 commit | tag `archive/ai__st-nightsweep2-nf-20260930__nf-exec-lane`→删 |
| 28 | ai/st-secbuild-20260923/sector-line-construction | 否 | 2 | 2026-09-23 11:14 | 未并入有独特 commit | tag `archive/ai__st-secbuild-20260923__sector-line-construction`→删 |
| 29 | ai/st-t0-matrix-20260924/t0-matrix-reexam | 否 | 4 | 2026-09-24 01:35 | 未并入有独特 commit | tag `archive/ai__st-t0-matrix-20260924__t0-matrix-reexam`→删 |
| 30 | ai/st-zmaster2-20260926/three-piece-infra | 否 | 1 | 2026-09-27 10:39 | 未并入有独特 commit | tag `archive/ai__st-zmaster2-20260926__three-piece-infra`→删 |
| 31 | session/st-chiefzc-micro-20260928 | 否 | 5 | 2026-09-28 02:08 | 未并入有独特 commit | tag `archive/session__st-chiefzc-micro-20260928`→删 |
| 32 | session/st-chiefzc-rescue-20260928 | 否 | 1 | 2026-09-28 04:22 | 未并入有独特 commit | tag `archive/session__st-chiefzc-rescue-20260928`→删 |
| 33 | session/st-finaldel-m4-20260929 | 否 | 1 | 2026-09-29 13:07 | 未并入有独特 commit | tag `archive/session__st-finaldel-m4-20260929`→删 |
| 34 | session/st-finaldel-m5-20260929 | 否 | 1 | 2026-09-29 13:07 | 未并入有独特 commit（与 m4 同 sha 3942796dba，双 tag 保全两名） | tag `archive/session__st-finaldel-m5-20260929`→删 |
| 35 | session/st-menu-t1b6-20260930 | 否 | 2 | 2026-10-01 04:04 | 未并入有独特 commit | tag `archive/session__st-menu-t1b6-20260930`→删 |
| 36 | session/st-t0-revival-20260922 | 否 | 3 | 2026-09-22 07:10 | 未并入有独特 commit | tag `archive/session__st-t0-revival-20260922`→删 |
| 37 | st/st-zcloseout-defect6 | 否 | 1 | 2026-09-29 04:00 | 未并入有独特 commit | tag `archive/st__st-zcloseout-defect6`→删 |

### D. 直删·已并入 dev 零信息价值（116）

| # | 分支 | 并入dev | 独特commit | 末活动(+08:00) | 判定 | 去向 |
|---|------|---------|-----------|---------------|------|------|
| 38 | ai/st-ailayer-final-20260924/fullflow-closure | 是 | 0 | 2026-09-26 02:05 | 已并入 | git branch -d |
| 39 | ai/st-c7-1a5-20260927/task-dead-db | 是 | 0 | 2026-09-27 11:48 | 已并入 | git branch -d |
| 40 | ai/st-c7-f56-20260927/task-f56-bridge-kernel | 是 | 0 | 2026-09-27 11:48 | 已并入 | git branch -d |
| 41 | ai/st-c7-govfix-20260927/task-govtool-gate-fixes | 是 | 0 | 2026-09-27 14:07 | 已并入 | git branch -d |
| 42 | ai/st-c7-mine-20260927/task-env-mining | 是 | 0 | 2026-09-27 15:08 | 已并入 | git branch -d |
| 43 | ai/st-c7-qbag-20260927/task-qbag-reapply | 是 | 0 | 2026-09-27 15:57 | 已并入 | git branch -d |
| 44 | ai/st-c7-rb-20260927/task-redblue-wave73 | 是 | 0 | 2026-09-27 16:31 | 已并入 | git branch -d |
| 45 | ai/st-c7-resc-20260927/task-orphan-rescue | 是 | 0 | 2026-09-27 14:03 | 已并入 | git branch -d |
| 46 | ai/st-c7-s4-20260927/s4-factory-repair | 是 | 0 | 2026-09-27 10:56 | 已并入 | git branch -d |
| 47 | ai/st-c7-wire-20260927/task-dead-impl-wiring | 是 | 0 | 2026-09-27 15:08 | 已并入 | git branch -d |
| 48 | ai/st-chief3-20260926/chief-handoff | 是 | 0 | 2026-09-26 22:03 | 已并入 | git branch -d |
| 49 | ai/st-chief3b-20260926/wave2-realbody | 是 | 0 | 2026-09-26 23:12 | 已并入 | git branch -d |
| 50 | ai/st-chief8-20260928/task-chief8-fullcirculation | 是 | 0 | 2026-09-28 01:32 | 已并入 | git branch -d |
| 51 | ai/st-cmd-20260924/task-sixstate-unify | 是 | 0 | 2026-09-25 14:19 | 已并入 | git branch -d |
| 52 | ai/st-combine-20260923/task-pf-alloc-wiring | 是 | 0 | 2026-09-23 06:52 | 已并入 | git branch -d |
| 53 | ai/st-gate-fix/gate-tree-read-fix | 是 | 0 | 2026-09-27 01:39 | 已并入 | git branch -d |
| 54 | ai/st-m1-leaf/mining-family-leafs | 是 | 0 | 2026-09-26 20:40 | 已并入 | git branch -d |
| 55 | ai/st-m2-seal/mining-seal-audit | 是 | 0 | 2026-09-26 20:40 | 已并入 | git branch -d |
| 56 | ai/st-menu-t1b2-20260930/T1-B2-F128-wiring | 是 | 0 | 2026-09-30 21:24 | 已并入 | git branch -d |
| 57 | ai/st-menu-t1b5-20260930/t1b5-cn-macro-revival | 是 | 0 | 2026-09-30 23:07 | 已并入 | git branch -d |
| 58 | ai/st-nightsweep-sw7-20260929/nightsweep-r5-fix | 是 | 0 | 2026-09-29 06:12 | 已并入 | git branch -d |
| 59 | ai/st-nightsweep-sw9-20260929/task-saga-cleaning | 是 | 0 | 2026-09-29 06:07 | 已并入 | git branch -d |
| 60 | ai/st-nightsweep2-merge-20260930/merge-train | 是 | 0 | 2026-09-30 14:52 | 已并入 | git branch -d |
| 61 | ai/st-nightsweep2-ne4-20260930/NE4-landing-bottleneck | 是 | 0 | 2026-09-30 06:13 | 已并入 | git branch -d |
| 62 | ai/st-p1-gate/piece-one-guard | 是 | 0 | 2026-09-26 20:40 | 已并入 | git branch -d |
| 63 | ai/st-p10-bridge/bridge-gate-compliance | 是 | 0 | 2026-09-26 23:12 | 已并入 | git branch -d |
| 64 | ai/st-p11-board/concurrency-visibility-bus | 是 | 0 | 2026-09-26 23:12 | 已并入 | git branch -d |
| 65 | ai/st-p12-heartbeat/session-liveness-truth | 是 | 0 | 2026-09-26 23:12 | 已并入 | git branch -d |
| 66 | ai/st-p14-schedule/unscheduled-items-into-waves | 是 | 0 | 2026-09-26 23:12 | 已并入 | git branch -d |
| 67 | ai/st-p15-phantom/phantom-citation-cure | 是 | 0 | 2026-09-26 23:12 | 已并入 | git branch -d |
| 68 | ai/st-p16-t2gate/batch-window-preflight | 是 | 0 | 2026-09-26 23:12 | 已并入 | git branch -d |
| 69 | ai/st-p17-storage/storage-decision | 是 | 0 | 2026-09-27 00:33 | 已并入 | git branch -d |
| 70 | ai/st-p18-du11/du11-daily-valuation-cure | 是 | 0 | 2026-09-27 01:39 | 已并入 | git branch -d |
| 71 | ai/st-p19-ibt/ibt-d01-cost-caliber | 是 | 0 | 2026-09-27 01:39 | 已并入 | git branch -d |
| 72 | ai/st-p1b-libr/library-reconcilers | 是 | 0 | 2026-09-26 20:40 | 已并入 | git branch -d |
| 73 | ai/st-p2-cens/consumption-census | 是 | 0 | 2026-09-26 20:40 | 已并入 | git branch -d |
| 74 | ai/st-p20-wire/l04-l09-wiring | 是 | 0 | 2026-09-27 01:39 | 已并入 | git branch -d |
| 75 | ai/st-p21-ledger/trial-ledger-wiring | 是 | 0 | 2026-09-27 01:39 | 已并入 | git branch -d |
| 76 | ai/st-p22-precheck/preenqueue-compliance | 是 | 0 | 2026-09-27 01:39 | 已并入 | git branch -d |
| 77 | ai/st-p3-matrix/connection-matrix | 是 | 0 | 2026-10-01 06:08 | 已并入 | git branch -d |
| 78 | ai/st-p4-bridge/trda10-bridge-defects | 是 | 0 | 2026-09-26 20:40 | 已并入 | git branch -d |
| 79 | ai/st-p5-chart/chart-signal-wiring | 是 | 0 | 2026-09-26 20:40 | 已并入 | git branch -d |
| 80 | ai/st-p6-t1top/t1-scorecard-analysis | 是 | 0 | 2026-09-26 20:40 | 已并入 | git branch -d |
| 81 | ai/st-p7-scope/scope-convergence | 是 | 0 | 2026-09-26 21:18 | 已并入 | git branch -d |
| 82 | ai/st-p8-integrate/wave13-integration | 是 | 0 | 2026-09-26 22:03 | 已并入 | git branch -d |
| 83 | ai/st-p9-fixchart/chart-bag-integration | 是 | 0 | 2026-09-26 22:03 | 已并入 | git branch -d |
| 84 | ai/st-statreplay-20260923/sector-state-replay | 是 | 0 | 2026-09-23 18:08 | 已并入 | git branch -d |
| 85 | ai/st-wm1-buildA-20260923/wm1-registry-ledger | 是 | 0 | 2026-09-23 13:39 | 已并入 | git branch -d |
| 86 | csx/d4-ghostfix | 是 | 0 | 2026-09-24 21:13 | 已并入 | git branch -d |
| 87 | csx/p13-stats | 是 | 0 | 2026-09-24 23:20 | 已并入 | git branch -d |
| 88 | csx/w4-envfix | 是 | 0 | 2026-09-24 21:25 | 已并入 | git branch -d |
| 89 | r2clean | 是 | 0 | 2026-09-30 08:30 | 已并入 | git branch -d |
| 90 | session/st-audit-fix-20260924 | 是 | 0 | 2026-09-26 00:55 | 已并入 | git branch -d |
| 91 | session/st-circ-a1-20260930 | 是 | 0 | 2026-10-01 00:10 | 已并入 | git branch -d |
| 92 | session/st-circ-a2-20260930 | 是 | 0 | 2026-10-01 05:52 | 已并入 | git branch -d |
| 93 | session/st-circ-a4-20260930 | 是 | 0 | 2026-10-01 08:18 | 已并入 | git branch -d |
| 94 | session/st-circ-a8-20260930 | 是 | 0 | 2026-10-01 02:09 | 已并入 | git branch -d |
| 95 | session/st-circ-g3-20260930 | 是 | 0 | 2026-10-01 00:10 | 已并入 | git branch -d |
| 96 | session/st-datasop-20260930 | 是 | 0 | 2026-10-01 12:26 | 已并入 | git branch -d |
| 97 | session/st-emoreplay-20260923 | 是 | 0 | 2026-09-23 18:08 | 已并入 | git branch -d |
| 98 | session/st-final-build-20260926 | 是 | 0 | 2026-09-27 06:27 | 已并入 | git branch -d |
| 99 | session/st-finaldel-cseal-20260929 | 是 | 0 | 2026-09-29 16:01 | 已并入 | git branch -d |
| 100 | session/st-fms-chief-20260927 | 是 | 0 | 2026-09-29 01:51 | 已并入 | git branch -d |
| 101 | session/st-fullscore-20260930 | 是 | 0 | 2026-10-01 09:36 | 已并入 | git branch -d |
| 102 | session/st-mapbuild-20260924 | 是 | 0 | 2026-09-24 12:36 | 已并入 | git branch -d |
| 103 | session/st-matrix-revive-20260928 | 是 | 0 | 2026-09-29 03:23 | 已并入 | git branch -d |
| 104 | session/st-menu-t1c1-20260930 | 是 | 0 | 2026-09-30 22:13 | 已并入 | git branch -d |
| 105 | session/st-menu-w3c1-20260930 | 是 | 0 | 2026-10-01 02:09 | 已并入 | git branch -d |
| 106 | session/st-nightclean-20260929 | 是 | 0 | 2026-09-29 13:26 | 已并入 | git branch -d |
| 107 | session/st-nightsweep-sw13-20260929 | 是 | 0 | 2026-09-29 07:44 | 已并入 | git branch -d |
| 108 | session/st-nightsweep-sw15-20260929 | 是 | 0 | 2026-09-29 08:02 | 已并入 | git branch -d |
| 109 | session/st-nightsweep-sw18-20260929 | 是 | 0 | 2026-09-29 17:28 | 已并入 | git branch -d |
| 110 | session/st-nightsweep2-fin-20260930 | 是 | 0 | 2026-09-30 20:47 | 已并入 | git branch -d |
| 111 | session/st-nightsweep2-nc-20260930 | 是 | 0 | 2026-09-30 07:47 | 已并入 | git branch -d |
| 112 | session/st-nightsweep2-ne4-20260930 | 是 | 0 | 2026-09-30 06:48 | 已并入 | git branch -d |
| 113 | session/st-nightsweep2-nf2-20260930 | 是 | 0 | 2026-09-30 13:29 | 已并入 | git branch -d |
| 114 | session/st-qmine-20260925 | 是 | 0 | 2026-09-25 21:07 | 已并入 | git branch -d |
| 115 | session/st-wm1-buildB-20260923 | 是 | 0 | 2026-09-23 13:39 | 已并入 | git branch -d |
| 116 | session/st-zcloseout-20260928 | 是 | 0 | 2026-09-28 18:04 | 已并入 | git branch -d |
| 117 | st-zc8-lane-dbr-20260928 | 是 | 0 | 2026-09-28 08:41 | 已并入 | git branch -d |
| 118 | st/st-zcloseout-20260928 | 是 | 0 | 2026-10-01 00:10 | 已并入 | git branch -d |
| 119 | st/st-zcloseout-chart | 是 | 0 | 2026-09-28 08:12 | 已并入 | git branch -d |
| 120 | st/st-zcloseout-costtier | 是 | 0 | 2026-09-29 00:05 | 已并入 | git branch -d |
| 121 | st/st-zcloseout-debt | 是 | 0 | 2026-09-28 19:50 | 已并入 | git branch -d |
| 122 | st/st-zcloseout-envcheck | 是 | 0 | 2026-09-29 02:55 | 已并入 | git branch -d |
| 123 | st/st-zcloseout-f62 | 是 | 0 | 2026-09-28 08:12 | 已并入 | git branch -d |
| 124 | st/st-zcloseout-f74 | 是 | 0 | 2026-09-28 08:12 | 已并入 | git branch -d |
| 125 | st/st-zcloseout-leaves | 是 | 0 | 2026-09-28 15:31 | 已并入 | git branch -d |
| 126 | st/st-zcloseout-quarantine | 是 | 0 | 2026-09-28 22:23 | 已并入 | git branch -d |
| 127 | st/st-zcloseout-queuefix | 是 | 0 | 2026-09-30 02:55 | 已并入 | git branch -d |
| 128 | st/st-zcloseout-relaunch | 是 | 0 | 2026-09-28 19:12 | 已并入 | git branch -d |
| 129 | st/st-zcloseout-rootcure | 是 | 0 | 2026-09-30 02:55 | 已并入 | git branch -d |
| 130 | st/st-zcloseout-trial | 是 | 0 | 2026-09-28 19:50 | 已并入 | git branch -d |
| 131 | st/st-zcloseout-verify | 是 | 0 | 2026-09-28 19:50 | 已并入 | git branch -d |
| 132 | worktree-agent-general-purpose-0221c4d4 | 是 | 0 | 2026-09-23 13:39 | 已并入（无主 agent 孤儿指针） | git branch -d |
| 133 | worktree-agent-general-purpose-0a33c75b | 是 | 0 | 2026-09-23 13:39 | 已并入 | git branch -d |
| 134 | worktree-agent-general-purpose-1e788bf7 | 是 | 0 | 2026-09-23 13:39 | 已并入 | git branch -d |
| 135 | worktree-agent-general-purpose-208ad861 | 是 | 0 | 2026-09-23 13:39 | 已并入 | git branch -d |
| 136 | worktree-agent-general-purpose-2a7e8d6a | 是 | 0 | 2026-09-23 13:39 | 已并入 | git branch -d |
| 137 | worktree-agent-general-purpose-4044d5c5 | 是 | 0 | 2026-09-23 13:39 | 已并入 | git branch -d |
| 138 | worktree-agent-general-purpose-47966ee6 | 是 | 0 | 2026-09-23 13:39 | 已并入 | git branch -d |
| 139 | worktree-agent-general-purpose-5a931884 | 是 | 0 | 2026-09-23 13:39 | 已并入 | git branch -d |
| 140 | worktree-agent-general-purpose-6f173268 | 是 | 0 | 2026-09-23 13:39 | 已并入 | git branch -d |
| 141 | worktree-agent-general-purpose-740571c9 | 是 | 0 | 2026-09-23 13:39 | 已并入 | git branch -d |
| 142 | worktree-agent-general-purpose-8b745eb5 | 是 | 0 | 2026-09-23 13:39 | 已并入 | git branch -d |
| 143 | worktree-agent-general-purpose-92e04e0d | 是 | 0 | 2026-09-23 13:39 | 已并入 | git branch -d |
| 144 | worktree-agent-general-purpose-9cc66a12 | 是 | 0 | 2026-09-23 13:39 | 已并入 | git branch -d |
| 145 | worktree-agent-general-purpose-b2012cc5 | 是 | 0 | 2026-09-08 00:31 | 已并入（指向 origin/master 同代 commit，dev 已含） | git branch -d |
| 146 | worktree-agent-general-purpose-b2b033b4 | 是 | 0 | 2026-09-23 13:39 | 已并入 | git branch -d |
| 147 | worktree-agent-general-purpose-c065182d | 是 | 0 | 2026-09-23 13:39 | 已并入 | git branch -d |
| 148 | worktree-agent-general-purpose-cd243618 | 是 | 0 | 2026-09-23 13:39 | 已并入 | git branch -d |
| 149 | worktree-agent-general-purpose-ce874b1c | 是 | 0 | 2026-09-23 13:39 | 已并入 | git branch -d |
| 150 | worktree-agent-general-purpose-e29d83e4 | 是 | 0 | 2026-09-23 13:39 | 已并入 | git branch -d |
| 151 | worktree-agent-general-purpose-f1ec3d50 | 是 | 0 | 2026-09-23 13:39 | 已并入 | git branch -d |
| 152 | worktree-agent-general-purpose-fe047874 | 是 | 0 | 2026-09-23 13:39 | 已并入 | git branch -d |
| 153 | wt-clean87 | 是 | 0 | 2026-09-30 18:05 | 已并入 | git branch -d |

### E. 远端（3，只读登记不动——推送权在 Owner）

| # | 远端 ref | 指向 | 判定 | 去向 |
|---|----------|------|------|------|
| R1 | origin/HEAD | →origin/dev | 符号指针非分支 | 不动 |
| R2 | origin/dev | bbcad37ec3 | 本地 dev 祖先（上游跟踪） | 不动 |
| R3 | origin/master | d92ea66538 | 主干世系根（dev 已含其历史） | 不动（删除远端=Owner 职权） |

## 二、执行记录（终节）

执行时点：2026-10-02 04:00–04:10 +08:00｜执行序：census → 台账 → tag → 删已并入 → 删已归档 → 终态核验。

| 项 | 计划 | 实际 | 备注 |
|----|------|------|------|
| 本地分支总数 | 153 | 153 | census 与台账 153/153 零漂移（程序化 diff 核对） |
| 直删（已并入 dev） | 116 | 116 | `git branch -d`，进度每 20 报点，零拒绝 |
| tag 归档后删（未并入有独特 commit） | 24 | 24 | 先打 tag（25 个含保险 1 个）后 `git branch 强删(-D 旗标)`；删前逐条复核 tag 在位 |
| 保留·主干 | 1 | 1 | dev=5aa2b07cb0 未动；origin/dev 仍为其祖先 |
| 保留观察·worktree 占用 | 12 | 12 | 11 条已并入 + 1 条未并入（chief4，另打保险 tag） |
| 归档 tag | — | 25 | `archive/*` 全量 sha 复核通过（24 归档 + 1 保险 chief4=55b46e74f0） |
| 删除失败/跳过 | 0 | 0 | 唯一 DEL-FAIL=chief4 保留观察分支，`-D` 被 worktree 占用拒绝=预期防线，非事故 |
| 待 Owner | 0 | 0 | 无——所有未并入独特工作均已 tag 归档（零丢失可复活） |

## 三、终态

```
$ git branch（13 条）
+ ai/st-c7-autofix-20260927/task-automation-false-green   (worktree 占用, locked)
+ ai/st-chief4-20260927/gate-and-landing                  (worktree 占用, locked, 未并入1commit已保险tag)
+ ai/st-chief7w-20260927/task-fullconnect-landing         (worktree 占用, locked)
* dev                                                      (主干)
+ serializer/commit-queue                                  (提交队列基建)
+ serializer/commit-queue-w0/w1/w2/w3                      (提交队列基建×4)
+ session/st-chief7-20260928                               (活跃会话 sid)
+ session/st-commitfix-20261001                            (worktree 占用, locked)
+ session/st-ffchief-20261001                              (总包活跃会话 sid)
+ session/st-mapcensus-20260924                            (worktree 占用, 末提交今日)

$ git branch -r（3 ref 只读登记不动）
  origin/HEAD -> origin/dev
  origin/dev        bbcad37ec3
  origin/master     d92ea66538
```

**终态摘要**：本地 153 = 保留主干 1（dev）+ 保留观察 12（worktree 占用/活跃会话/基建）+ 直删 116 + 归档删 24；远端 3 ref 登记 不动；归档 tag 25（复活命令 `git branch <名> <tag>`）。
**红线遵守**：dev/master/main 未动（本地无 master/main 分支）；活跃会话分支（st-c10-*/st-c12-* 本地无分支；st-chief7/st-ffchief 保留）全保；tag 先于删，顺序未反；台账先写后执行；worktree 占用拒绝一律跳过登记未蛮干；worktree 本体零触碰（B1 只动 refs）。
**移交事项**：①12 条观察分支待其 worktree 退役后按同规则二轮清零（chief4 未并入 1 commit 有保险 tag 兜底）；②本台账为新文件，提交时经 gateway 并补 CREATE-GUARD creation_token 登记；③远端 origin/master 删除权在 Owner。
**执行证据**：`.runtime/tmp/b1_branch_zero/`（occupied/del_merged/arch/tags_done/refused 清单）。
