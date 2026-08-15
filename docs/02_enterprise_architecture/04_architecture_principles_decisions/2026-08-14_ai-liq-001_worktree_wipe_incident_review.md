---
title: 架构裁定书——AI-LIQ-001 遗留项六项全面审查（worktree wipe 事故）
doc_type: audit_report
ttl: permanent
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.2"
date: 2026-08-14
---

# 架构裁定书：AI-LIQ-001 遗留项六项全面审查

> 审查人：架构师视角（客观第三方）｜方法：物证驱动 + 第一性原理｜范围：6 项遗留项全部完成代码级/文档级实证调研
> 来源：AI-LIQ-001 会话（37 号流动性危机 Protocol 施工队），2026-08-14 归档 by 统筹会话（AI-SOP-001）
> 关联：#ARCH-GIT-CLEAN-GUARD-FIX（2026-08-11 git clean 灾难）｜67_merge_conflict_resolution_sop｜tracker §六 #34-37
> 恢复注记：本文件曾于 2026-08-14 被不明删除（工作区未暂存删除），由统筹从 git 历史恢复重写（内容与原 commit 14644ab0 一致）。

## 第一部分 · P0 wipe 事故（分析过程 → 裁定）

### 1.1 时间窗与波及面（关键升级：不是孤立事件）

| 时间（+0800） | 事件 | 证据 |
|---|---|---|
| 00:19 | AI-BGT-001 最后正常活动（commit 15b1e40f8a） | 其 .runtime reconcile_reports |
| 01:36:03 | 不明进程在 AI-BGT-001 worktree 内 import zephyr + 跑 pytest | feature_flags.jsonl 注册记录 + pytest nodeids |
| 01:40:06 | AI-SELL-001 做 capability 反查（commit 前置） | 主工作区 lookup_audit/AI-SELL-001.jsonl |
| 01:41:39 | 我（AI-LIQ-001）C4 commit | post_commit_regen_yaml 日志 |
| 01:42–01:47 | 三个 worktree（AI-BGT-001 / AI-LIQ-001 / AI-SELL-001）同步被清空工作文件 | 三方现场互证 |
| 01:47–01:51 | AI-SELL-001 跑 recover_blobs.py 自救，其 docstring 明写"worktree 被 sweep 删除（分支无 commit）" | 主工作区 .runtime/sessions/AI-SELL-001/staging/ |
| ~01:50 | 我发现并 git restore . 全量恢复 | 我的会话记录 |
| 至今 | AI-BGT-001 现场原样保留（6018 个 D），无人恢复 | git status 实测 |

### 1.2 删除器画像（物证反推）

- **删**：三 worktree 全部 tracked 文件 + 根目录 untracked 散文件（我的 liq_loader_check.py 同样消失）
- **留**：目录结构、.git 指针文件、.git/worktrees/ 注册、.runtime 全套、被进程锁定的文件（feature_flags.jsonl=遥测 append 句柄；2 个 portfolio 蓝图=sync_panorama 写入句柄）
- **git 层完好**：index/HEAD/reflog 无损，git restore . 秒级全恢复

### 1.3 排除清单（逐项实证，非推测）

| 嫌疑 | verdict | 决定性证据 |
|---|---|---|
| GATE-RUNTIME-CLEANUP reconciler | 证伪 | 删除半径钉死 .runtime/tmp/（reconciliation_registry.py:9089/9135），事故中 .runtime 完好 |
| 40+ post-commit reconciler | 证伪 | 全部读过，无任何一条具备删除 tracked 文件的能力 |
| ~~排除项勘误~~ | **勘误（2026-08-14 晚，#ARCH-RECONCILER-AUTO-DELETE-GOV-001）** | 上行结论有误：GATE-WORKING-DOCS 幽灵引用归档器具备实质删除能力（move 至 working_archive + _commit_auto 提交删除），系 tracker/handoff/本裁定书 三次"误删"真凶；不影响本裁定书 R1-R4 根因裁定（该归档器删除半径限于 docs/_working/，与三 worktree wipe 非同族） |
| 4 个 reconcile worker 无删除能力 | （但死亡本身异常） | payload 文件未被消费（worker 连读 payload 都没活到）→ 启动即崩；stdio=DEVNULL 无日志可查 |
| pre-commit 框架 stash | 证伪 | 网关一律 --no-verify（gateway:1703/1706），框架 stash 从不执行 |
| git worktree remove | 证伪 | 三 worktree 至今全部在 git worktree list 注册中 |
| OS 计划任务 | 证伪 | TraeCacheCleanup 登录触发（17:50 已跑）/DailyBackup 06:00/DeadmanSwitch 只读心跳发告警 |
| Windows Defender | 证伪 | 实时保护开启但零检测记录（Defender 行动必留痕） |
| 仓库内 .worktrees 自动清理代码 | 不存在 | 全库仅 scripts/session_worktree.py 引用 .worktrees，且删除路径只在人工 abort/merge |

### 1.4 裁定结论

物证不足以定罪到具体会话（文件删除无审计——这本身是缺陷 R3），但足以定罪到架构。**唯一与全部物证吻合的执行者是：主工作区某 AI 会话在 01:42–01:47 执行的临时构造的"worktree 清理"命令**（PowerShell/Python 物理删除，显式排除 .git/.runtime，锁定文件因 Windows 句柄锁幸存）。

第一性原理根因（四层失守）：

- **R1 能力层**：AI 会话终端权限是全域的。git_guard 只拦 git 子命令——Remove-Item / del / os.remove 等删除原语零拦截。2026-08-08 git clean 灾难的治本（git_guard）只收敛了一个原语，删除能力面从未系统性收敛。
- **R2 隔离层**：worktree"物理隔离"是君子协定。NTFS 层面所有会话共享读写权限，任何会话可写、可删任何 worktree，事前无会话活性检查、无未合并工作检查。
- **R3 观测层**：文件批量删除无审计留痕；reconcile worker stdio 全 DEVNULL 死无日志；事故发现靠运气（我恰好跑了 git status；AI-BGT-001 没人发现，至今躺现场）。
- **R4 流程层**：worktree 清理无所有者、无 SOP、无"分支是否有未合并 commit"强制检查点。同类损失已第三次发生（tracker 原文件未 commit 丢失 → AI-SELL-001 blob 自救 → 本次三 worktree wipe），每次都被当孤立事件处理，从未治本。

## 第二部分 · 其余五项裁定

### 遗留项 6（网关 worktree 锚定缺陷）——架构缺陷成立，定级 P1

根因链已实锤：pip editable install（_editable_impl_zephyr_alpha.pth）→ import zephyr 恒解析主工作区 src → paths.py find_repo_root() 从 zephyr.__file__ 向上推 → REPO_ROOT 恒=主工作区。**直接 bug**：git_commit.py L46-48 bootstrap 只把 worktree 根目录插 sys.path（zephyr 在 src/ 下，根目录不含包），而 _shared/constants.py L41-44 的注释明确记载过这个历史 bug（"必须添加 src/ 而非项目根"）——已修复的 bug 在网关入口复发。旁证：AI-SELL-001 的 lookup_audit 写进主工作区 .runtime（同一根因）。PYTHONPATH workaround 有效但依赖每个 AI 自觉、未文档化，且读错 registry 会产生假阴性/假阳性门禁结果。

### 遗留项 2（幽灵锚点）——降级为重复登记，结构性根因新发现

tracker #34 已登记同一批 9 个幽灵锚点（AI-BGT-001 先报，统筹治理路径）。**新发现**：apply_depgraph.py 全文无 battle_map_anchors 引用——删 depgraph 节点时零级联清理锚点，幽灵锚点只会只增不减，align_all 硬阻断将永久报警（报警疲劳→真阻断被无视）。闭环工具 apply_battle_map.py --remove-anchor 已存在。

### 遗留项 3（00_index 未同步）——照先例闭环

tracker #37 同型先例已闭环（bm-fill 释放→统筹同步）。照此办理，无需新机制。

### 遗留项 4（AGENTS.md 计数漂移）——裁定：改动态表述，走 Owner 审批

调研确认 metric_count_drift_reconciler 只管 4 个治理文件的 METRICS 计数，AGENTS.md "179 条"无任何自动校验；且 tracker #9 明确 AGENTS.md 显化修改需 Owner 审批。裁定：把硬编码计数改为"条数以 capability_canonical_file_registry.yaml 实时查询为准（CapabilityLookup）"，一次修改永久免疫漂移——但须走 Owner 审批通道，AI 不得自行改。

### 遗留项 5（蓝图 §5 两项未闭环）——正常跨会话交接，登记排期

编排层接入（35号 §3.13 调用方）与 IPO 数据源（数据层）本就不在 37 号施工范围。登记 tracker，由统筹分配给对应域会话。

## 第三部分 · 治本施工方案（按优先级排序）

### S0 · 紧急恢复（今天，统筹执行）

1. `git -C D:\ZephyrAlpha\.worktrees\AI-BGT-001 restore .` 恢复其 tracked 文件（分支 commit 15b1e40f8a 完好）；其 01:36 后未 commit 工作按 AI-SELL-001 先例跑 blob 恢复评估。
2. 三 worktree 打存活快照：分支 tip、未合并 commit 数登记到 tracker。

### S1 · 删除能力收敛（R1 治本，P0）

新建 ops_guard（或扩展 git_guard）——全原语删除拦截：

- 拦截对 .worktrees/*、仓库根、src/、docs/、tests/ 的递归删除命令（Remove-Item -Recurse、del /s、rd /s、shutil.rmtree、os.remove 批量模式、git clean）
- 合法删除路径白名单化：仅 .runtime/tmp、__pycache__、显式单文件
- 所有删除命令强制落审计 jsonl（命令行+cwd+会话 ID+目标清单 hash），先审计后执行
- 验证：红队测试"模拟 AI 构造批量删除命令"必须 100% 被拦

### S2 · worktree 清理安全 SOP（R2+R4 治本，P0）

新建《worktree 清理 SOP》并接入 merge 流程，清理任何 worktree 前必须四证齐全：

1. **死亡证明**：会话 heartbeat 停跳 >90s 且 registry 无活跃记录
2. **无未合并工作证明**：分支无 ahead commit + git status 无 staged 变更（有则先 commit 或 git stash push 打包存证到 refs/quarantine/）
3. **统筹显式批准**：清理动作登记 tracker 才能执行
4. **可恢复证明**：执行前 git bundle 或分支 ref 快照

### S3 · 观测层补齐（R3 治本，P1）

1. reconcile worker stdio 从 DEVNULL 改为落盘 .runtime/logs/reconcile_worker_<sha>.log——本次 4 个 worker 死因至今不可考，直接原因是零日志
2. 网关 commit 后自动对 worktree 打 git status 快照入审计（事后 wipe 可精确定位责任时段）
3. （可选强化）Windows Object Access Auditing 对 .worktrees/ 开删除审计——治本但需管理员，列 P2

### S4 · 网关锚定修复（遗留项 6 治本，P1）

1. git_commit.py bootstrap 修正：sys.path.insert(0, <repo_root>/src)（repo_root 由 git rev-parse --show-toplevel 从 cwd 解析，而非 __file__ 派生）——与 _shared/constants.py 的已修复先例对齐
2. paths.py find_repo_root() 增加 worktree 感知：cwd 在 worktree 内时优先返回 worktree 根（环境变量 ZEPHYR_WORKTREE_ROOT 显式注入优先）
3. SOP Step 10 补写："worktree 内调用网关必须 PYTHONPATH=<worktree>\src（过渡期内）"，治本落地后移除

### S5 · 锚点级联清理（遗留项 2 治本，P2）

apply_depgraph 删除/弃用节点时级联处理 battle_map_anchors（默认 --remove-anchor 提示；--cascade 自动清理），消除幽灵锚点产生源。存量 9 个由统筹用现成工具清理（tracker #34 闭环）。

### S6 · 登记与审批（本周）

- tracker 补登：wipe 事故（本报告）、网关锚定缺陷、AGENTS.md 计数动态化（挂 #9 审批通道）
- SOP 文本修正：遗留项登记目标章节号与 tracker 现状对齐（§六 vs §七 漂移）
- 遗留项 5 两项分配给 35 号调用方会话 / 数据层会话

**验收标准**：S1 红队测试全拦截；S2 四证流程走通一次真实清理；S3 worker 日志可读+事后快照可定位；S4 无 PYTHONPATH 时 worktree 内网关门禁读到本 worktree registry（AI-SELL-001 场景复测）；S5 删节点后 align_all 幽灵锚点计数不增。

---

**给统筹会话的执行请求**：① S0 恢复 AI-BGT-001 立即执行；② S1/S2 立项为 P0 治理施工（建议独立会话承接）；③ 本裁定书全文归档至 docs/_working/audit/architecture-reviews/（AI-LIQ-001 已按自查建议不再发起新 commit，归档由统筹落地）。

## 统筹执行留痕（2026-08-14，AI-SOP-001）

- S0①：执行时发现 .worktrees 目录已整体消失（二次删除），但三分支 ref 完好（BGT=15b1e40f8a / LIQ=3e39367c37 / SELL=87764ffb29），committed 工作零损失。已从分支重建 BGT/LIQ worktree 并复跑测试验证（33+54 全绿）。
- S0②：快照登记 tracker（见 §六 #38 及批次区）。
- 归档：本文件即归档落地。
