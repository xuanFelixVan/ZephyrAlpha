---
doc_type: forensics_report
campaign: decision_map_campaign_20260924
title: 主区蒸发连环案取证报告（03:47-07:46 窗口执行源追凶）
date: 2026-09-24
author: 蒸发案取证班（只读取证，唯一可写=本文件）
status: delivered
ttl: task_bound
---

# 10_evaporation_forensics.md — 主区蒸发连环案取证报告

> 案情：2026-09-24 凌晨 03:47-07:46 主区至少四起同族蒸发（untracked 全灭 + 共享 index 567→9），
> 特征被受害方推定为 `git reset --hard + git clean -fd`；另 t0 班 16:xx 见 9 条暂存删除（现增至 27 条）。
> 本报告全部只读取证（schtasks/reflog/status/quarantine 枚举/源码审读），未做任何 git 写操作。
> 注：本文件为新建件，CREATE-GUARD creation_token 登记由落地车道随批补办（取证班仅授权写本文件）。

## ① 时间线重建（本地时间；drift_<ts> 目录名为 UTC，+8=本地）

| 时刻 | 证据 | 来源 |
|---|---|---|
| 02:30:01 | `\tilib_indicator_backfill_nightly` 跑 `D:\ZephyrAlpha\scripts\data\backfill_night.bat`（rc=1；数据车道，无 git 写证据） | schtasks /v |
| 03:30:00 | `\ZephyrAlpha_LibraryLedgerBackup`（library_ledger_backup.py backup，rc=0，读侧） | schtasks /v |
| 03:30:01 | `\ZephyrAlpha_GateFullTreeAudit`（run_fulltree_gate_audit.py --quiet，rc=1 失败无人盯） | schtasks /v |
| 03:31:38-03:45:10 | **post-commit reconciler 全功率运转**（session=st-backup-cold-20260924，commit 47e9673e94b）：32 reconcilers、GATE-TMP-CLEANUP **deleted=520**、GATE-RUNTIME-CLEANUP **deleted=476**（locked_skipped=939）、GATE-SESSION-STAGING-LIFECYCLE **deleted=15**、GATE-ROOT-TEMP-SWEEP purged=41；**drift scan 148 项（auto_fixable:83）**；"restored 8 auto-sync files"；auto_committed=5 | .runtime/logs/reconcile_worker_47e9673e….log + reconcile_status json |
| 03:41:05 / 03:41:21 | drift watchdog quarantine 存证：drift_20260923T194105（tests/gov_enforcement/test_tag_vocab_gate.py）、drift_20260923T194121（tests/governance/generators/test_generate_commit_guide.py） | .runtime/quarantine/ 枚举 |
| 03:47 | **第一蒸发现场**（受害方 LEDGER 记录窗口开启） | ai_layer_vision/LEDGER_final.md 事故章 |
| 03:47:07-03:47:34 | commit_gate_run21/22.log、msg_prewrap.txt；commit_queue/worktree 门禁文件群同秒刷新；**03:47:20.96-21.21 w0/w1/w2/w3 四 serializer worktree 在 300ms 内同步爆发**（=landing 周期进行时） | find .runtime -newermt 窗口枚举 |
| 04:25-06:22 | drift quarantine 稀疏连发（drift_20260924T042550…T062217，19 个）；06:00:41 w3 hook_tracked_drift.jsonl 刷新 | .runtime/quarantine/ 枚举 |
| 07:03 / 07:15-07:16 / 07:22:40-53 | drift quarantine 再连发（07:22 五连发） | 同上 |
| 07:24:12-07:30:45 | **watchdog quarantine 15 连发爆发**（drift_20260923T2324xx-233045）：开箱亲验含 config/resource_profile_registry.yaml、docs/_working/ai_layer_vision/LEDGER_final.md、ultimate_library/COVERAGE.md、src/zephyr/backtest/regime_validation/__init__.py 等 | .runtime/quarantine/ 枚举 + 开目录亲验 |
| 07:36:55 | gpu merge 落 dev（4fc2cf6d04，"Merge branch 'ai/st-gpu-final-20260924/gpu-final-campaign' into dev"） | 主 reflog |
| 07:36-07:42 | **同一 gpu merge 六次重试**（"merge ai/st-gpu-final…: updating HEAD"×5 + commit(merge)×1，间隔 11-60s）——merge 重试循环实证 | 主 reflog |
| 07:46 | 窗口闭合（受害方口径） | 受害 LEDGER |
| 07:49:27 | 备份馆三件被 gpu merge"拍平吞没"后从 be42d6759b 原文重投（B 班上报 #3"跨班静默蒸发新通道"） | 主 reflog + ultimate_library/11_handoff |
| 16:xx | t0 班见主区 index 出现 9 条暂存删除（含 7 件已落 dev） | t0_matrix/LEDGER + campaign 08 |
| 22:13 / 23:08 | metaq_* 注册表批（8f959906f8）与 qmt_bridge_regression_smoke.py 等（27449507e1）由属主车道落 dev | git log --diff-filter=A |
| 23:37（取证时） | 暂存删除已增至 **27 条**，抽验 4 件（metaq_e1c/qmt_smoke/两 ps1/test_regen_offload_m2）**磁盘全部在位** → 纯 index 条目蒸发，非文件删除 | git status --short + ls 亲验 |

关键反证事实：**主 reflog 在 03:00-07:59 窗口共 65 条记录（45 条空 action=update-ref 型 plumbing 落地），其中 reset 记录=0 条**（全天唯一 reset 在 22:09:56）。即：窗口内没有任何 porcelain `git reset` 触碰过主区 HEAD——受害方"reset --hard 特征"系症状推断；`git clean -fd` 天然零 reflog 痕迹，与受害者自述"reflog 无 independent 痕迹"吻合。

## ② 嫌疑人排序（证据强度 A/B/C + 反证）

### S1 提交队列 landing 链 `_sync_worktree`（reset --hard + clean -fd）打穿主仓 —— 强度 A-
- 证据：
  1. `scripts/governance/commit_queue_landing.py:1050` `_sync_worktree` **每个队列项处理前**执行 `reset --hard refs/heads/dev` + `clean -fd`；
  2. `commit_queue_landing.py:949` 治本注释**自认前科**："专用 worktree 目录在但 .git 链接丢失时，git 以 cwd 向上查找会命中主仓 .git——reset --hard/clean 直接打穿主工作区（**2026-08-29 当日 reflog 实证 6 次成对 reset**）"；
  3. `scripts/commit_queue.py:850/889/1220` 三处注释自认同类前科（2026-09-16/09-17）："thief 的 _sync_worktree(reset --hard + clean -fd) 删掉 victim 已 materialize 未 commit 的 untracked 新文件"；
  4. 守卫 `_git_wt`（:951-971）是 **check-then-act（TOCTOU）**：先查 `.git` 链接存在 + toplevel 解析回自身，再执行 reset/clean——两步之间链接被摘即打穿；
  5. 摘链接机制有前科：GATE-ROOT-TEMP-SWEEP 曾"扫走 worktree .git 指针"（archive/design_memos/65_git_safety_governance.md，65a2e8a6 事故机制）；
  6. `\ZephyrAlpha_BeltDaemon` 计划任务**每 1 分钟**自举 `commit_belt_daemon D:\ZephyrAlpha`（全夜在跑）；03:47:20-21 四 worktree 同步爆发与第一蒸发现场同分钟；
  7. 当日 B 班上报："队列 worktree 旧分支病（serializer/commit-queue-w0）→五袋 identity 全灭冤死"——serializer worktree 当天本来就带病。
- 反证：若走 porcelain reset 打穿，主 reflog 应留 reset 记录而窗口内为 0（08-29 前科有 6 次成对 reset 记录可对照）。解释：index 清除也可能经 plumbing（read-tree/update-index，serializer 白名单内、reflog 静默），`clean -fd` 本身永远静默；不排除打穿的是 clean-only 或 plumbing 变体。

### S2 session_worktree merge 流 `_pre_merge_auto_clean` —— 强度 B+
- 证据：
  1. `src/zephyr/gov_enforcement/rule_bridge/session_worktree.py:5283`：merge 前对**主区**做 auto_clean——场景1 tracked dirty"git stash push 保存修改（文件还原到 HEAD）"；场景2 untracked"**内容一致时物理删除 untracked 文件**（merge 会重新创建）"；
  2. 致命缺陷自认：merge 冲突时 `WorktreeManager.merge_session_worktree`（worktree_manager.py:404）`git merge --abort` 后 **auto_clean 删掉的 untracked 不会被重建**；
  3. 本夜 07:36-07:42 gpu merge 六次重试=重试循环实证；07:49 三件被 merge 拍平吞没需手工重投；
  4. **同族前科时间签名完全一致**：09-18 凌晨 03:47-03:54 "tdchain 车道连续 pre-merge sweep + reset: moving to HEAD（reflog 实证）抹除全仓未提交件"（automation/campaign/mining/coordination_st_mineline_20260918.md）；
  5. `_pre_merge_gate_check` 用 `git reset --soft merge-base` 模拟、`git reset --soft orig_head` 恢复——两段式之间崩溃=主区 HEAD 钉死在 merge-base（另一型蒸发）。
- 反证：内容一致性检查 + 其他活跃会话 claim skip（Ruling 100PCT P2-2）应挡住多数误删；场景1 stash push 会留 reflog reset 记录（本窗 0 条）——故本窗其 index 侧参与度存疑，untracked 侧（静默物理删除）高度可疑。

### S3 worktree_drift_watchdog（每 5 分钟 daemon，计划任务 `\ZephyrAlpha_WorktreeDriftWatchdog`）—— 强度 B（从犯/放大器）
- 证据：
  1. 源码自述三路 index 写行为：B2 护盾"docs/_working 新增 untracked 由 daemon 每轮自动 git add 进 index"；A1 死会话清扫"git reset HEAD 仅动 index"（卸 staged）；A2 派生自动收敛 `_commit_auto`；
  2. A1 依赖 SessionRegistry 存活判定——PID 复用/心跳超时误判即把在飞会话 staged 件整批卸下（staged→untracked 化），正好给 clean 类凶手喂料；
  3. 窗口内 quarantine 实证运行：03:41 两连发、07:24-07:30 **15 连发**；B 班定性"watchdog quarantine 为搬移真身（F 包定性 epidemic）"；
  4. 30 天 retention 自扫 `_sweep_quarantine` 会物理删 drift_<ts> 目录（带 tamper 审计）。
- 反证：设计上"只告警不阻断、快照先于告警、工作树内容永不销毁"，quarantine 按源码是快照存证非搬移（抽验目录=单文件副本）；无直接证据表明其独立删除过主区 untracked。

### S4 post-commit reconciler 清扫 gate 族 —— 强度 B-（untracked 侧）/ C（index 侧）
- 证据：03:31-03:45 一轮实删 520+476+15+41 件、auto-fix 83 项、"restored 8 auto-sync files"（git checkout 类还原无 reflog 痕迹）；05:40/05:50/06:00/06:31 有 ResourceSamplerWriteback/ViewPublish/DailyBackup/MorningReport 计划任务接力在跑。
- 反证：清扫作用域=tmp/.runtime/sessions staging，受害面是 docs/_working、src/、config/ 的 untracked 与 staged——作用域不符；但同一轮曾报"447 non-auto-sync modified files detected"，存在 auto-sync 还原清单误扩散通道，不能完全豁免。

### S5 计划任务其余嫌疑 —— 强度 C（基本排除）
- `Git Maintenance (hourly/daily/weekly)`：每小时跑 `git maintenance run`（本仓在 maintenance.repo 名单，strategy=incremental）——maintenance 只做 gc/prefetch/commit-graph/loose-objects，**不触碰工作区与 index**。排除。
- `ZephyrAlpha_TraeCacheCleanup`（clean_trae_cache.ps1）：仅登录触发，LastRun 09-20——不在窗口。排除（作为常驻风险另记）。
- `ZephyrAlpha_ProcessReaper`（每 10 分钟）：杀进程不删文件；`ZephyrAlpha-DailyBackup` 06:00、`ZEPHYR-RESTORE-DRILL`（每月 1 日 4:30，LastTaskResult=267011 即从未成功运行过）、`ZephyrAlpha-CH-OptimizeMerge-Weekly`（周日 3:30，9/24 为周四）——均无 git 写证据。排除。
- 现存 python 进程普查（清单⑦）：worktree_drift_watchdog daemon（pid 29020）、commit_belt_daemon（23356）、write_audit_daemon（17848）、heartbeat_daemon×2、session_keeper（st-metaq-gc）等 13 支——无 clean/reset 类野进程、无第二执行体，与 t0 班 15:3x 心跳普查结论互证。

### t0 的"9 条暂存删除"机制裁定（清单⑧）
非独立案，是 index 条目蒸发的**尾迹**：某时点主区 index 被卸/重置（567→9 族的残余），条目缺失而磁盘文件在；此后属主车道把同路径文件落进 dev（22:13 metaq 批、23:08 qmt 批）→ HEAD 有、index 无 → 呈现"D "暂存删除且磁盘在位。实测 16:xx=9 条 → 取证时=27 条，随落地批次递增，与该模型严格吻合。

## ③ 最可能凶手结论 + 置信度

**结论**：本夜蒸发是"landing/serializer 链（S1）为主犯、pre-merge auto_clean（S2）与 drift watchdog A1 卸 staged（S3）为从犯"的**同族复合案**——三者共享同一指纹：`clean -fd` 静默抹 untracked + index 条目被卸/重置（reflog 零痕）。"某定时任务半夜跑 reset/clean"假说被计划任务全查排除。
- 头号嫌疑人：**commit_queue landing 的 `_sync_worktree`（reset --hard + clean -fd）经 worktree .git 链接缺失/竞态打穿主仓**。代码三处自认前科 + TOCTOU 守卫 + 当日 serializer worktree 带病 + 03:47:20 现场同步爆发四证合一。
- 置信度：**主犯判定 ~65%（中高）**；"S1+S2+S3 复合"整体解释 ~80%。未达 90%+ 的原因：clean 无日志、缺进程级与计划任务级审计，无法把具体 pid 钉死在 03:47:xx 那一分钟。

## ④ 治本建议（按性价比排序）

1. **git 操作黑匣子（最优先）**：主仓 index/reflog 快照哨兵——每 5 分钟快照 `.git/index` 至 `.runtime/git_index_snapshots/`（保 72h，drift watchdog 同款 retention）+ `git config core.logAllRefUpdates always` + stash list 轮询（09-18 靠 stash 抢救、本夜 stash=空，stash 消失本身也是线索）。下次蒸发即可二分定位到分钟。
2. **封死 TOCTOU**：`_git_wt` 守卫从"前置检查"升级为"执行后验证"——reset/clean 前后各读一次 `rev-parse --git-dir` 与 `git status --porcelain` 条目数；gitdir 解析漂移或主区 staged 计数骤降>30% 立即反向回滚+告警。更彻底：弃用 reset/clean，改 `git restore --source=HEAD --worktree --staged -- <本袋 files>` own-diff 作用域。
3. **landing staged 守恒断言**：每项落地前后 `git diff --cached --name-only` 对账，差集非空即拒落并写 dead_reason（align_dirty 台账 D12 处方，落地侧至今未生效——连坐通道仍在）。
4. **_pre_merge_auto_clean 可逆化**：场景2"物理删除"改"移入 .runtime/quarantine/premerge_<ts>/（带 manifest）"，merge abort 自动回搬；删除范围收紧为"本 session branch changed_files ∩ 内容逐字节一致 ∩ 无任何 24h 内活跃会话 claim"。
5. **watchdog A1 保守化**：卸 staged 前把条目 blob 存 `refs/quarantine/<sid>-staged`（worktree 四证 SOP 同款双存证），误判一条命令拉回；PID 判死加双周期确认。
6. **计划任务审计**：开启 TaskScheduler 操作日志（事件 4698-4704）转储进 .runtime 审计；`ZephyrAlpha_GateFullTreeAudit` rc=1 这类带病任务进告警面；为全部 ZephyrAlpha_* 任务建 keep-list（process_reaper 同款）防误杀+漂移。
7. **验收即提交入队常态化**（09-18 与本夜两度实证的唯一可靠防御）：docs/_working 产出落盘即 enqueue，不在主区裸放 untracked 超 30 分钟。

## ⑤ 取证过程日志附尾（命令→要点）

```
1. schtasks /query /fo LIST /v（MSYS_NO_PATHCONV=1 + iconv GBK）→ ZephyrAlpha_* 74 任务全录；
   凌晨窗实跑：LibraryLedgerBackup 3:30 / GateFullTreeAudit 3:30(rc=1) / ResourceSamplerWriteback 5:40 /
   ViewPublish 5:50 / DailyBackup 6:00 / MorningReport 6:31 / ConfigCheck 8:05 / Git Maintenance 每小时 /
   tilib backfill 2:30 / TraeCacheCleanup=仅登录(9/20)。
2. git reflog --date=iso（全量+窗口 grep）→ 窗口 65 条：45 空 action（update-ref 型落地）、
   merge 重试 6 连（07:36-07:42）、reset=0；.git/worktrees/*/logs/HEAD 窗口 reset=0。
3. git stash list → 空；.runtime/workspace_alerts/stash_notice.json → 不存在。
   （依题示先核 reflog：clean 无痕、reset 留痕而窗口无 reset → fsck --lost-found 未执行，零 git 写。）
4. git status --short → 865 行，"D " 暂存删除 27 条（16:xx 为 9 条）；抽验 4 件磁盘在位；
   git ls-files=17229；.git/index mtime=23:37；HEAD=11923233c2(dev)。
5. grep quarantine docs/_working → .runtime/quarantine/ + drift_<ts> 命名真源
   （worktree_drift_watchdog.py MODIFY-GUARD）；B 班 11_handoff §重大上报#2"watchdog quarantine 为搬移真身"。
6. grep 清扫|clean docs/_working/align_dirty/align_dirty_ledger.md → §D12 连坐实证
   （q-0014 声明 1 件落地 4 件、把他会话陈旧 index 残项一并提交、两次蒸发）+ 主区 1156 脏件/index 648 基线。
7. Get-CimInstance python* → 13 支，无 clean/reset 类野进程（watchdog/belt/reaper 均为注册任务在管）。
8. 源码审读：commit_queue_landing.py:949(打穿前科)/951(_git_wt TOCTOU)/1050(_sync_worktree)；
   commit_queue.py:850/889/1220(三处前科注释)；session_worktree.py:5283(_pre_merge_auto_clean 物理删除 untracked)；
   worktree_manager.py:404(merge abort 不回搬)；worktree_drift_watchdog.py(B2 auto-add/A1 reset HEAD/A2 _commit_auto)。
9. .runtime/quarantine 枚举 → 09-23:218 个 + 09-24:92 个 drift 目录；窗口内 03:41 两连发、07:24-07:30 十五连发，
   开箱亲验含 LEDGER_final.md/COVERAGE.md/resource_profile_registry.yaml 等。
10. find .runtime -newermt 窗口 → 11271 文件；03:47:20.96-21.21 w0-w3 四 worktree 300ms 同步爆发为最强现场。
```

> 取证纪律声明：全程零 git 写操作、零现有文件改动；本文件经 safe_write_text CAS 写入。
> 未尽事项：①03:47:xx 分钟级 pid 归罪需④-1 黑匣子落地后才可能；②09-18 抢救链 stash@{3}-@{7} 存在而本夜 stash=空——stash 消失路径建议纳入④-1 监控。
