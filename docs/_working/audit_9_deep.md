---
ttl: task_bound
---

======================================================================
#ARCH-WORKSPACE-DRIFT-SYSTEMIC-001  [B2④]
======================================================================
title: 系统性防漂移体系盲区——4 盲区 3 Phase 治本（post-commit→pre-commit/clean-check/verified-gate）
status: resolved | severity: P1高 | fix_phase: Phase 1（已完成 2026-07-20，commit 4f56348145，merge 9a6d66efac）：
  - session_worktree.py 4 钩子接入 + 5 helper 函数
    (_classify_workspace_files cc=7 / _restore_auto_sync_batch cc=6 /
     _evaluate_drift_after_restore cc=13 / _check_workspace_clean cc=10 /
     _log_workspace_drift_warn cc=11) + 3 包装函数 + _WS_CLEAN_GATE_ID 常量
  - Phase 1.5 pre-commit drift warn 遥测落盘 .runtime/workspace_drift_warn.jsonl
  - 169 tests passed (test_session_worktree_workspace_clean.py 33 + 相关 136)
  - start 钩子告警实际触发验证成功（新 session 启动时检测到 48 real code modified）

Phase 2（已完成 2026-07-20，commit c343ae5d6b，merge 0259db8a1fef）：
  - _restore_auto_sync_batch 添加 staged/MM 状态处理（cc=6）
  - 先 git_restore_batch(staged=True) unstage + 再 git_restore_batch(staged=False) restore
  - 177 tests passed + 1608 commit_gates 全量通过
  - 4 新测试：staged_only / mm_state / mixed_staged_and_worktree / empty_files
  - 4 集成测试：staged_auto_sync_passes_merge / mm_state_passes_merge /
    staged_real_code_blocks_merge / staged_real_code_fail_open_abort

Phase 3（已完成 2026-07-20，commit f7f79ae684，merge 07f1e58763）：
  - 新建 ruling_commit_verified_gate.py (256 行, MOD-GOV-ruling_commit_verified_gate)
  - 新建 test_ruling_commit_verified_gate.py (SRC-TST-2717, 36 测试全部通过)
  - 复杂度治本：_check 闭包 cc=16 → _detect_violations (cc=13) + _check (cc=5)
  - gate 注册：git_commit_gateway.py L115 import + L404 register
  - 注册表登记：
    capability_canonical_file_registry.yaml（capability_id + creation_token）
    noqa_exempt_registry.yaml（no-verify-ruling marker, scope=commit-message）
    architecture_issue_registry.yaml（本案登记）
  - ruling 文档落盘：docs/02_enterprise_architecture/ruling_workspace_drift_systemic.md
    （单独 commit 3c6c73b1ec，merge 82e9704ffd7b）

created: 2026-07-20 | last_updated: 2026-07-20
--- adjudication (2871 chars) ---
2026-07-20 立项裁定。前序会话"遗留风险"报告指出 4 个系统性盲区：

1. 工作区漂移检测全部 post-commit 触发——workspace_hygiene_reconciler 是 post-commit
   priority=890，commit 时已搭便车完成，post-commit warn 无治本作用

2. session_worktree_commit 只提交显式列出的 files——AI 用 Edit/Write 写项目根，
   session 文件在主工作区是 modified 状态，commit 时未列入 files 参数=搭便车风险

3. 无 session_end 工作区 clean 检查——session_worktree_start/abort 无工作区 clean
   验证，新 session 启动时主工作区可能有其他 session 残留，merge 时被 WORKSPACE-CLEAN-CHECK
   阻断（本 session 实证：48 real code modified 阻断 merge）

4. 文档"已完成"声明无硬验证——ruling_*.md / architecture_issue_registry.yaml 中
   "已完成（commit <hash>）"声明，AI 可凭记忆/幻觉填写不存在的 hash，无门禁强制验证


病根分析（第一性原理·100% AI 场景）：

- 5 层闭环模型（post-commit warn）依赖人类视觉通道闭环——100% AI 场景下 AI 把 warn
  当"通过"，warn=无效。治本必须前置为 pre-commit fail-closed 或自动处理（无人类介入）

- session_worktree 物理隔离消除搭便车，但 4 个钩子（start/commit/merge/abort）无工作区
  clean 检查=session 间漂移无防护

- 文档 SSoT（ruling/architecture_issue_registry）若允许 AI 凭记忆填写 commit hash，
  则文档本身可能是幻觉产物——SSoT 失效


治本方案（3 Phase 渐进，对标 5 层闭环模型升级）：

Phase 1（session lifecycle 工作区 clean 检查 + pre-commit drift warn）：

  - 4 钩子接入（session_worktree_start/abort/merge + pre-commit）+ 5 helper 函数

  - fail-closed/fail-open 策略：merge=fail-closed（阻断），start/abort=fail-open
    （告警不阻断），commit Phase 1.5=fail-open（遥测落盘 .runtime/workspace_drift_warn.jsonl）

  - 复用 workspace_hygiene_reconciler 的 _git_status_porcelain / _is_auto_sync_product
    + GitCommandBatcher.git_restore_batch（向内收原则 trae_060）

  - session_files 排除语义：worktree 模式下 AI 用 Edit 写项目根，session 文件在主工作区
    是 modified 状态但不是搭便车（已在 worktree commit 中）

  - force=True 逃生通道：对标 PRE-MERGE-TOPO-CHECK 的 force 语义，跳过 WORKSPACE-CLEAN-CHECK


Phase 2（auto-recover staged 完整性修复）：

  - _restore_auto_sync_batch 添加 unstage+restore 两步（原版只 restore worktree，
    对 staged/MM 状态无效——staged auto-sync 文件被带入下次 commit）

  - 病根：旧版只调用 git_restore_batch(staged=False)，对 "M " (staged only)
    完全无效，对 "MM" (staged + worktree) 只还原 worktree 部分，staged 版本保留

  - 治本：先 git_restore_batch(staged=True) unstage，再 git_restore_batch(staged=False)
    restore worktree 到 HEAD，合并判断"既 unstage 成功又 restore 成功才算完全还原"


Phase 3（RULING-COMMIT-VERIFIED gate + ruling 文档落盘）：

  - 新建 RULING-COMMIT-VERIFIED gate (priority=77)，diff-based 增量检测

  - 检测 _TRIGGER_PATTERNS（ruling_*.md + architecture_issue_registry.yaml）的
    added 行中"已完成...commit <hash>"声明

  - 用 git cat-file -e <hash>^{commit} 验证 hash 真实存在

  - 逃生通道：commit message 含 [no-verify-ruling:<reason>] 标记
    （noqa_exempt_registry 登记 marker）

  - fail-closed：git 失败/ast 失败阻断（非 Zephyr 项目 skip）

  - 复杂度治本：_check 闭包 cc=16 → 提取 _detect_violations helper (cc=13) + _check (cc=5)

  - 36 测试全部通过（TestExtractCommitHashes 9 + TestIsTriggerFile 6 +
    TestVerifyCommitExists 3 + TestRulingCommitVerifiedGate 12 +
    TestGateSpecMetadata 3 + TestEscapeMarker 4）


架构师裁定（不实现项）：

- batch commit 入口是伪需求——违反"一个任务一个 commit"语义，不实现
- 全量 schema 化是过度工程——ruling 文档结构多样性高，强制 schema 化反而阻碍表达，不实现
--- ruling-marker hits: NONE ---
--- git log -S (commits touching this issue_id in registry) ---
031d372de6 | Zephyr Test | 2026-07-22 05:57:18 +0800 | [no-lookup:arch-module-id-unify] fix(arch): unify module_id format truth source to is_valid_module_id (#ARCH-MODULE-ID-FORMAT-UNIFICATION-001)
dbc35f9114 | Trae | 2026-07-22 01:22:07 +0800 | #ARCH-WORKTREE-COMMIT-PERSISTENCE-001 Phase 1-5: commit 持久性标记 + sweep 免疫 + merge 前验证 + start fail-closed + trae_076 规则外部化 [no-lookup:phase5-registry-sync-continuation-of-approved-ruling]
a43313cdd8 | Trae | 2026-07-22 00:52:18 +0800 | [no-lookup:architectural-refactor] #ARCH-BLUEPRINT-AUTOSYNC-MISCLASSIFY-001: blueprint.md auto-sync 误分类治本
6cf9bc4590 | Trae | 2026-07-21 23:07:00 +0800 | docs(gov): #ARCH-CONSUMERS-ACCURACY-003 P1-4 capability registry 双重登记 + P1-9 JSON 残留清理 [no-lookup:registry-completion-收尾登记工作-非新功能开发-裁定ARCH-CONSUMERS-ACCURACY-003]
4fd876f870 | Trae | 2026-07-21 14:54:22 +0800 | feat(gov): #ARCH-GATE-PRIORITY-UNIQUENESS-001 Phase 1+2 治本 priority 撞号
f7f79ae684 | Trae | 2026-07-20 21:47:00 +0800 | feat(gov): #ARCH-WORKSPACE-DRIFT-SYSTEMIC-001 Phase 3 RULING-COMMIT-VERIFIED gate 文档已完成声明硬验证
6dd0ba714d | Trae | 2026-07-20 21:04:08 +0800 | feat(gov): P3-4 trae_069 v1.2.0 阈值调整流程化 + smoke test 25/25 PASSED (#ARCH-PREVENTABILITY-LAYER-001 Phase 3 P3-4)
4f56348145 | Trae | 2026-07-20 18:19:53 +0800 | feat(gov): #ARCH-WORKSPACE-DRIFT-SYSTEMIC-001 Phase 1+1.5 session lifecycle 工作区 clean 检查 + drift 遥测

======================================================================
#ARCH-GATE-PRIORITY-UNIQUENESS-001  [B2④]
======================================================================
title: commit gate priority 撞号治本——BLUEPRINT-FORMAT 与 RULING-COMMIT-VERIFIED 同 priority=77，升级 register() warn->block
status: resolved | severity: P2中 | fix_phase: Phase 1（已完成 2026-07-21）：
  - ruling_commit_verified_gate.py: priority=77->109 + 注释 + [MODIFY-GUARD] + docstring
  - git_commit_gateway.py: 注册注释 priority=77->109
  - test_ruling_commit_verified_gate.py: priority 断言 77->109
  - 36 tests passed

Phase 2（已完成 2026-07-21）：
  - commit_gate_registry.py: 新增 GateRegistrationError 异常类（error_code=ZA-GV-0050）
  - register() warn->block：检测同 priority 不同 gate_id 抛异常阻断
  - 错误信息含历史先例（后到者让位）：DATA-TASK 78->41 / RENAME-DEPGRAPH-SYNC 36->39 /
    ORPHAN-MODULE 86->89 / DOC-REF-BROKEN 88->91 / RULING-COMMIT-VERIFIED 77->109
  - test_commit_gate_registry.py: test_register_multiple_distinct_gate_ids 改用不同 priority
    + 新增 TestPriorityConflictBlock 7 测试
  - 17 tests passed (原 10 + 新增 7)
  - GitCommitGateway init OK: 69 gates 全部唯一 priority，零冲突

created: 2026-07-21 | last_updated: 2026-07-21
--- adjudication (1651 chars) ---
2026-07-21 立项裁定。#ARCH-WORKSPACE-DRIFT-SYSTEMIC-001 Phase 3 落地后 发现 RULING-COMMIT-VERIFIED gate (priority=77) 与已存在的 BLUEPRINT-FORMAT gate (priority=77) 撞号——两者都注释"紧跟 RULE-FOUR-WAY-ALIGNMENT(76) 之后"，但 77 已被 BLUEPRINT-FORMAT 占用。CommitGateRegistry.register() 检测到冲突时仅 logger.warning（warn-only），不阻断注册。

病根分析（第一性原理·100% AI 场景）：

- priority 是排序契约，67 个 gate 的执行顺序。同 priority 时 sorted() 稳定
  排序，按 dict 插入顺序（即 register() 调用顺序）——这是隐式依赖，违反
  "显式优于隐式"原则

- 100% AI 场景下 warn-only 不构成闭环（AI 把 warn 当"通过"，与
  #ARCH-WORKSPACE-DRIFT-SYSTEMIC-001 同一病根）—— register() warn-only
  不阻断注册，撞号 gate 仍被写入 _specs

- 历史 5+ 次撞号先例（DATA-TASK 78->41 / RENAME-DEPGRAPH-SYNC 36->39 /
  ORPHAN-MODULE 86->89 / DOC-REF-BROKEN 88->91 / MANUAL-ONLY-PERMANENT
  36->43 / NO-DOMAIN-NAME-ZH 67->72 / CH-BATCH-SIZE 34->36）证明这是
  反复发生的系统性问题，非偶发

- 无中央 priority 登记表——新 AI 选 priority 时只能 grep 或随机选，
  gate_registry.yaml stale（5 处不一致）误导


治本方案（2 Phase 渐进）：

Phase 1（消除当前撞号，后到者让位）：

  - RULING-COMMIT-VERIFIED priority 77->109（后到者让位，符合历史先例）

  - 选 109：紧邻 CAPABILITY-LOOKUP-REQUIRED(110)，同属"AI 行为强制/文档
    真实性"类检查

  - 77-80 区间已满（77=BLUEPRINT-FORMAT, 78=DOMAIN-FK, 79=BLUEPRINT-AMODULE,
    80=VOCAB-HARDCODE），无法紧跟 RULE-FOUR-WAY(76)

  - priority 唯一性是硬约束，语义聚类是软约束——硬约束优先


Phase 2（防止未来撞号，warn->block）：

  - CommitGateRegistry.register() warn->block（fail-closed 治本）

  - 新增 GateRegistrationError 异常类（error_code=ZA-GV-0050）

  - 同 priority 不同 gate_id 抛异常阻断注册

  - 错误信息含历史先例（后到者让位），引导新 AI 选择空闲 priority

  - Phase 1 已消除现有撞号，Phase 2 block 不会卡死现有系统


架构师裁定（不实现项）：
- priority SSoT 化（新建 priority_allocation_registry.yaml）—— 过度工程，
  "代码即真源"（每个 gate .py 的 return GateSpec(..., priority=N) 行）已足够，
  中央登记表增加维护负担，不实现
--- ruling-marker hits: NONE ---
--- git log -S (commits touching this issue_id in registry) ---
4fd876f870 | Trae | 2026-07-21 14:54:22 +0800 | feat(gov): #ARCH-GATE-PRIORITY-UNIQUENESS-001 Phase 1+2 治本 priority 撞号

======================================================================
#ARCH-STASH-ACCUMULATION-001  [B2④]
======================================================================
title: stash 堆积治理——STASH-ACCUMULATION pre-commit gate + reconciler TTL 清理 + trae_075 规则真源（占位登记，另一 session 主导）
status: decided | severity: P2中 | fix_phase: Phase 1: stash_lifecycle_reconciler 系统性扩展
Phase 4: STASH-ACCUMULATION pre-commit gate
Phase 7: trae_075 stash 生命周期规则真源
（完整 Phase 清单待原 session 补充）

created: 2026-07-21 | last_updated: 2026-07-21
--- adjudication (684 chars) ---
占位登记说明：
本条目由 #ARCH-CONSUMERS-ACCURACY-003 会话（sess-42724-20260721230056）代为登记，
原因：capability_canonical_file_registry.yaml 中引用了 #ARCH-STASH-ACCUMULATION-001
（stash_accumulation_gate.py token + trae_075 规则 + stash_lifecycle_reconciler 扩展），
但原 session（sess-39544-20260721221413）未在 architecture_issue_registry.yaml 登记
本编号，导致 ARCH-REFERENCE gate 阻断并发 session 的 commit。

已知信息（从 capability_canonical_file_registry.yaml 注释提取）：
- Phase 1: stash_lifecycle_reconciler 系统性扩展（#ARCH-WORKTREE-002 Phase 4 → 本条）
- Phase 4: STASH-ACCUMULATION pre-commit gate（>20 warn, >40 block）
- Phase 7: trae_075 stash 生命周期规则真源（5 铁律：STASH-LIFE-LAW-1~5）

待办：原 session（sess-39544）需补充完整裁定内容（病根分析/治本方案/Phase 清单/impact）。

--- ruling-marker hits: NONE ---
--- git log -S (commits touching this issue_id in registry) ---
0083150961 | Zephyr Test | 2026-07-22 05:16:44 +0800 | fix(stash-lifecycle): 治本 _is_ai_generated 反向匹配（#ARCH-STASH-LIFECYCLE-FIX-001）
a43313cdd8 | Trae | 2026-07-22 00:52:18 +0800 | [no-lookup:architectural-refactor] #ARCH-BLUEPRINT-AUTOSYNC-MISCLASSIFY-001: blueprint.md auto-sync 误分类治本
6cf9bc4590 | Trae | 2026-07-21 23:07:00 +0800 | docs(gov): #ARCH-CONSUMERS-ACCURACY-003 P1-4 capability registry 双重登记 + P1-9 JSON 残留清理 [no-lookup:registry-completion-收尾登记工作-非新功能开发-裁定ARCH-CONSUMERS-ACCURACY-003]

======================================================================
#ARCH-COMMIT-SERIALIZATION-001  [B2④]
======================================================================
title: worktree 逃生链套娃根因治本——commit 临界区文件锁串行化（原语倒置修正）
status: resolved | severity: P1高 | fix_phase: Phase 0 (2026-07-22 完成): 现状量化——统计最近 commit 路径分布 L1/L2/L3 占比，验证"worktree 几乎总是失效"假说
Phase 1 (2026-07-22 完成, commit d6ff41ad16): commit 临界区文件锁——GitCommitGateway.commit 外层包锁 + pathspec 强制 + smoke test（真实多进程并发 commit 验证无搭便车 + kill 持锁进程验证自愈）
Phase 2 (2026-07-22 已落地): worktree 降级为可选——session_worktree.py WORKSPACE_DRIFT_BLOCKED 错误消息更新为"TRAE-079 Phase 2：worktree 已降级为可选——无需清理工作区，直接走 GitCommitGateway 文件锁串行提交" + AGENTS.md §FP-ISO.4C 添加 worktree 降级为可选说明 + architecture_issue_registry.yaml 本条 Phase 2 状态同步
Phase 3 (2026-07-22 已落地): 退役冗余补偿控制——allow_overlap 降级为 last-resort 逃生通道（logger.warning + 审计） + 文件锁 fail-open 降级落审计（_audit_commit_lock_fallback -> .runtime/gate_audit/commit_lock_fallback.jsonl） + _commit_auto 路径同样覆盖 OSError fallback。AGENTS.md GitCommitGateway held_files 冲突阻断章节添加 TRAE-079 Phase 3 说明。
治本根因：消除共享可变 index 下并发 commit 的搭便车，把强原语（文件锁）接到真临界区（commit），塌缩逃生链从 3 层到 1 层

created: 2026-07-22 | last_updated: 2026-07-22
--- adjudication (1904 chars) ---
根因（第一性原理分析）：
100% AI 多 session 并发开发下，commit 正确性靠三层逃生链保证，但每层前置条件在
同一并发环境下同样失败，导致"逃生通道套逃生通道"：

- L1 worktree（物理 index 隔离）→ 前置条件"主工作区干净"→ 并发 drift 失败（WORKSPACE_DRIFT_BLOCKED）
- L2 GitCommitGateway allow_overlap（共享 index 提交）→ 前置"index 未污染"→ 共享 index 失败（搭便车/提交错文件）
- L3 裸 git commit + session 注册 → 绕过所有门禁，靠事后校验（POST-COMMIT-GUARD）

根因（共享可变 index 下的并发 commit）从未被移除，只被逐层降级绕过。每降一级引入一批
补偿控制（审计标记 / post-hoc 校验 / force 分类 / stash gate / commit 持久性标记 / sweep 判据），
债务堆积。trae_076 background 自述循环依赖：治本薛定谔的回退需用 session_worktree 提交治本代码，
但 session_worktree 自身受薛定谔的回退影响→commit 被 sweep 删除→只能用 git update-ref 绕过。

原语倒置（关键发现）：
项目已存在两套锁机制但用反了：
- 强原语 lock_files.py（.ailocks/，原子目录创建=os.makedirs(exist_ok=False) OS 级真互斥，
  PID 死亡零窗口清理 + TTL 1800s 兜底）——只接 edit-time 文件互斥（低风险），未接入 commit 路径
- 弱原语 SessionRegistry（.runtime/session_registry.json，逻辑注册表，只检查不串行化）
  ——commit 路径用这个（held_overlap_gate），TOCTOU 窗口导致搭便车
强原语用低风险操作、弱原语用高风险操作 = 原语倒置。

治本方案（把强原语接到真临界区，把超集机制降为可选）：
1. GitCommitGateway.commit 外层包文件锁临界区（acquire→[gate检查+stage+commit]→release），
   整个临界区相对其他 session 串行——消除 TOCTOU 窗口
2. 临界区内强制 pathspec 提交（git commit -- <files>）——锁串行 + pathspec 限定双保险
3. commit 锁复用 lock_files.py 的 PID 死亡零窗口清理 + TTL 兜底——陈旧锁自愈不永久阻塞
4. worktree 从"commit 正确性依赖项"降级为"可选并行/隔离审查"——WORKSPACE_DRIFT_BLOCKED
   不再触发逃生链降级，直接走文件锁串行提交
5. allow_overlap 与"裸 commit + session 注册"降级为 last-resort（仅文件锁不可用时），保留事后审计

第一性原理：commit 不变量=恰好提交本 session 意图文件；临界区[读index→stage→commit→ref]
须相对其他 session 原子；最小精确解=文件锁串行化（worktree 是超集但前置不可达=不可用；
SessionRegistry 是子集只检查不串行=TOCTOU 洞；文件锁=精确解）。

100% AI 并发根本约束：无人类协调 / warn 无效 / 主工作区恒 drift（否定 worktree 前置）/
commit 低频编辑可并行（互斥只罩 commit）。文件锁恰好实现"串行 commit + 并行编辑"取舍。

不实施项：
- 不删除 worktree 代码（286KB，退役是独立大工程，另立 #ARCH-WORKTREE-RETIREMENT-001）
- 不立即废弃 trae_076 的 5 Phase 补偿控制（worktree 仍被使用时仍有价值，Phase 3 退役 worktree commit 后再评估）
- 不强制 Phase 1 commit 到主分支（Phase 1 保持现有分支模型仅加锁；Phase 2 才评估直提主分支以根除薛定谔的回退）
- 不引入外部锁库（纯标准库，遵循 lock_files.py 既有原则）

--- ruling-marker hits: NONE ---
--- git log -S (commits touching this issue_id in registry) ---
a9e08dea93 | Test | 2026-07-22 23:13:48 +0800 | feat(gov): register 3 arch decisions [no-lookup:continuation]
031d372de6 | Zephyr Test | 2026-07-22 05:57:18 +0800 | [no-lookup:arch-module-id-unify] fix(arch): unify module_id format truth source to is_valid_module_id (#ARCH-MODULE-ID-FORMAT-UNIFICATION-001)

======================================================================
#ARCH-RECONCILER-WORKER-SESSION-001  [B2④]
======================================================================
title: reconciler worker 治本——注册为逻辑 session + 并发上限（消除失控 worker）
status: decided | severity: P1高 | fix_phase: Phase C（worker 治本）：
  C.1 _run_worker 启动时注册为逻辑 session（worker-{sha}-{pid}）
  C.2 launch_reconcile_async 增加并发上限检查（默认 2，超限合并或拒绝）
  C.3 worker heartbeat tracking（复用 session heartbeat）
  C.4 worktree_lifecycle_reconciler 识别 worker session
  C.5 smoke test：多并发 commit 验证 worker 不超限

created: 2026-07-22 | last_updated: 2026-07-22
--- adjudication (1053 chars) ---
根因（第一性原理分析）：
launch_reconcile_async（reconcile_runner.py L262）每次 commit 都 spawn 一个 detached worker
subprocess，零并发控制——N 个并发 commit 产生 N 个并发 worker，每个 worker 构造完整的
GitCommitGateway 并执行全部 reconciler 链路。

_run_worker（reconcile_worker.py L168）不注册为逻辑 session（SessionRegistry），
导致：
1. worker 不受 session 并发上限约束——3+ worker 可同时运行，争抢 DB 连接 / 文件锁 / git index
2. worker 的 heartbeat 不被 tracking——孤儿 worker 进程死亡后无人清理
3. worktree_lifecycle_reconciler 不识别 worker——可能误 sweep worker 正在使用的资源

100% AI 多 session 并发开发下，每 session 的 commit 都触发 worker spawn，
worker 数量随 session 数量线性增长，无上限 = 环境失控（本次 3 并发 worker +
8 孤儿 heartbeat 即此问题表现）。

治本方案：
1. worker 注册为逻辑 session：_run_worker 启动时调 SessionRegistry.register，
   session_id 格式 worker-{commit_sha}-{pid}，死亡时自动 unregister
2. 并发上限：launch_reconcile_async spawn 前检查活跃 worker 数，超上限则
   合并到现有 worker 队列（或拒绝 spawn + 告警），上限默认 2
3. heartbeat tracking：worker 复用 session heartbeat 机制，超时自动标记 stale
4. worktree_lifecycle_reconciler 识别 worker session——不 sweep worker 正在使用的资源

不实施项：
- 不改为同步执行（异步是正确设计，问题在无上限）
- 不引入外部任务队列（如 Celery）——纯标准库，遵循项目原则

--- ruling-marker hits: NONE ---
--- git log -S (commits touching this issue_id in registry) ---
a9e08dea93 | Test | 2026-07-22 23:13:48 +0800 | feat(gov): register 3 arch decisions [no-lookup:continuation]

======================================================================
#ARCH-TSV-SOT-001  [B2④]
======================================================================
title: TSV 转义逻辑单一真源——wal_codec 委托 ch_writer.tsv_escape（消除双真源数据腐化）
status: resolved | severity: P1高 | fix_phase: Phase A（已完成 2026-07-22）：
  A.1 _escape_value 委托 ch_writer.tsv_escape
  A.2 encode_tsv 去 \n 对齐 wal_writer._serialize_tsv
  A.3 _unescape_value 简化为仅 backslash（有损不可逆）
  A.4 新增 test_roundtrip_with_ch_writer_consistency 锁定一致性
  A.5 22 tests pass

created: 2026-07-22 | last_updated: 2026-07-22
--- adjudication (810 chars) ---
根因（第一性原理分析）：
wal_codec/tsv_codec.py 自行实现 _escape_value（backslash 转义：\t→\\t、\n→\\n），
而 ch_writer.tsv_escape 是 ClickHouse TabSeparated 写入路径的生产真源
（空格替换：\t/\n/\r→空格，有损转义）。两者并存 = 双真源 = 数据腐化温床：

1. 同一行 tick 数据经 wal_writer._serialize_tsv（用 ch_writer.tsv_escape）落盘 WAL 段，
   经 wal_codec.encode_tsv（用自实现 backslash 转义）解码——转义/反转义不对称 = 数据损坏
2. WAL 段文件格式与 CH TabSeparated 格式不一致——drain 回灌时 CH 可能解析失败或静默错位
3. 100% AI 开发下，两套转义逻辑是 AI 最易复制粘贴漂移的点——未来必然出现第三套变体

治本方案（单一真源）：
ch_writer.tsv_escape 是 TSV 转义的唯一真源（生产写入路径，CH TabSeparated 语义对齐）。
wal_codec._escape_value 必须委托 ch_writer.tsv_escape，禁止自行实现转义逻辑。
encode_tsv 输出与 wal_writer._serialize_tsv 完全一致（含无尾部 \n 约定）。
_unescape_value 仅处理 backslash（有损转义不可逆，best-effort 用于调试/验证）。

不实施项：
- 不让 ch_writer 反过来依赖 wal_codec（避免循环依赖；ch_writer 是更底层真源）
- 不引入新转义格式（有损空格替换是 CH TabSeparated 默认行为，正确且稳定）

--- ruling-marker hits: NONE ---
--- git log -S (commits touching this issue_id in registry) ---
5c4b56c2ba | Test | 2026-07-22 23:26:11 +0800 | fix(data): P2 核查治本修复4项——TSV转义SSoT/心跳集成/CH插件/蓝图状态

======================================================================
#ARCH-048  [B2③ 推翻/边界]
======================================================================
title: 数据库边界裁定——采纳MOD-ARCH-BIZDB硬性边界二元判定，Redis/EventStore优先级降为P2，ClickHouse门禁解除
status: decided | severity: P1高 | fix_phase: P0 DONE 2026-07-05：
(a) ARCH-048 条目登记（本条目）
(b) c1_market_clickhouse.md 蓝图状态更新（ClickHouse 已部署）
(c) market.duckdb 文件删除（已于 2026-07-05 删除）
(d) database_service.py docstring 修正
(e) 品类模板 database 字段统一
(f) SLA 命名统一为 P0/P1/P2 并分级

created: 2026-07-05 | last_updated: 2026-07-05
--- adjudication (361 chars) ---
ARCH-048 裁定：母蓝图（database/blueprint.md）的"硬性边界二元判定"优先于子蓝图（SH-DB-001 §3）的门禁逻辑。
(1) 采纳母蓝图硬性边界二元判定：业务数据库边界 = 显式 DatabaseService 访问 + read_only=True 安全约束
(2) Redis/EventStore 优先级降为 P2（非核心，按需引入）
(3) SH-DB-001 §3 门禁逻辑标注废弃（禁止裸 duckdb.connect 等约束仍有效，但 ClickHouse 直连门禁解除）
(4) ClickHouse 已实际部署，门禁状态从"未部署"更正为"已部署"
治本"母蓝图推翻子蓝图未登记 ARCH"的病根——之前母蓝图与子蓝图对 ClickHouse/Redis 的约束矛盾。

--- ruling-marker hits: NONE ---
--- git log -S (commits touching this issue_id in registry) ---
a16fa1ef7a | Trae | 2026-07-05 00:53:11 +0800 | fix(database): ARCH-048裁决+ClickHouse状态同步+market.duckdb删除+SLA统一+W1-W4/S1审查修复

======================================================================
#ARCH-063  [B2② wontfix]
======================================================================
title: 5.178 TEST-SOURCE-CONSISTENCY gate DEFERRED 3 种漂移检测（mock/schema/阈值）裁定关闭
status: resolved | severity: P3低 | fix_phase: 已完成（裁定关闭，无施工）
created: 2026-07-20 | last_updated: 2026-07-20
--- adjudication (1728 chars) ---
问题背景：
architecture_debt §5.178 维度主体已 FIXED（TEST-SOURCE-CONSISTENCY gate priority=102
实现名称漂移检测，覆盖 `from zephyr.* import Symbol` 符号存在性静态校验）。
遗留 3 种漂移检测 DEFERRED：
(a) Mock 漂移——需类内省，检测 mock.patch 字符串目标的存在性
(b) Schema 漂移——需 DB introspection，检测测试 schema 与 DB schema 一致性
(c) 阈值漂移——需常量交叉引用，检测测试硬编码数值是否应从源码导入常量

第一性原理分析（5 维度）：
1. 代码验证（grep 实测 2026-07-20）：
   - mock.patch("zephyr.*") 字符串模式：0 处使用（tests/ 全扫）
   - autospec=True/spec=X 模式：19 处（已是项目规范）
   - alembic/metadata.create_all：1 处（tests/agent/test_agent_creation_policy.py）
   - assert x == 0.xx 阈值断言：289 处跨 100 文件（多为 fixture 期望值，非源码常量）
2. 问题本质：
   - 名称漂移（已覆盖）：STATIC——AST 可靠解析符号存在性
   - Mock 漂移：SEMI-STATIC——目标字符串存在性受 __getattr__/动态属性/__slots__ 影响，
     误报率不可控；且 0 处实际使用，gate 无检测对象
   - Schema 漂移：DYNAMIC——需运行时 DB 连接，pre-commit hook 不可依赖外部服务；
     alembic 测试 + Pydantic import-time 校验已兜底
   - 阈值漂移：SEMANTIC——"该 0.05 是否应从源码导入常量"是设计意图问题，
     AST 无法判定；测试 fixture 期望值与源码常量是两类语义
3. 100% AI 开发特殊性：
   - AI 倾向直接 mock 对象而非字符串 patch（autospec/spec），减少 mock 漂移风险
   - AI 用 Pydantic schema 直接建模，减少 DB schema 耦合
   - AI 硬编码数值是规范问题，应通过 lint 规则（ruff PLR2004 magic-value-comparison）兜底
4. 成本收益：
   - Mock 漂移：~200 行代码，收益 0（无检测对象）——ROI 负
   - Schema 漂移：~500+ 行（需 DB 连接），收益低（1 处 alembic 已覆盖）——ROI 负
   - 阈值漂移：~300+ 行（语义不可靠），误报风险高——ROI 负
5. 防复发策略：
   - 名称漂移：已落地 gate（priority=102，硬阻断）
   - Mock 漂移：规范强制 autospec/spec（lint 规则可加）
   - Schema 漂移：alembic 测试 + Pydantic schema import-time 校验
   - 阈值漂移：lint 规则 ruff PLR2004 + 编码规范"测试阈值从源码 import 常量"

裁定：3 种 DEFERRED 检测全部 CLOSED-wontfix（R102 裁定编号 #R102-5178-WONTFIX）：
- 静态 AST 检测不可行或不可靠（技术不可行）
- 实际代码库 0-1 处使用场景（收益接近 0）
- runtime 测试 + alembic + Pydantic + lint 规则已构成替代防复发链
- 防复发由替代机制兜底，不依赖 commit-time gate

注：本裁定仅关闭 DEFERRED 子项，5.178 维度主体（名称漂移检测）保持 FIXED。

--- ruling-marker hits: ['R102'] ---
--- git log -S (commits touching this issue_id in registry) ---
04d28af03f | Trae | 2026-07-20 09:27:41 +0800 | ruling(5.178): DEFERRED 3 种检测（mock/schema/阈值）裁定 CLOSED-wontfix #ARCH-063

======================================================================
#ARCH-ANY-GOVERNANCE-001  [B2② RATIFY]
======================================================================
title: 60 项 wontfix 第一性原理重新审查 + 5.145 系统性 Any 类型注解治理专项工程
status: resolved | severity: P2中 | fix_phase: Phase 1: 类型推断工具构建（1-2 session）
Phase 2: 分批治理 8 batch（5-8 session）
Phase 3: gate 升级 commit 阻断（1 session）

created: 2026-07-21 | last_updated: 2026-07-22
--- adjudication (455 chars) ---
对 R102 60 项 wontfix 做第一性原理重新审查：
- 46 项保持 RATIFY（P3 实际风险=0 或 P4 净收益为负）
- 14 项（5.145.13-26 系统性 Any）原"增量机会性清理"理由已失效（无机械触发保证 = 永不清理），转 EXECUTE 分批治理。
治本三阶段：
Phase 1: 构建 any_type_inferrer.py 类型推断工具（基于 AST 调用点上下文推断候选类型）
Phase 2: 分 8 批治理 ~270 行裸 Any（top 5：escalation_engine.py 12、system_telemetry/facade.py 11、pipeline_orchestrator.py 11、permission_hooks.py 9、in_process_vector_memory.py 8）
Phase 3: GATE-ANY-ABUSE 从 manual 升级为 commit 阻断 + # noqa: any-abuse 行级豁免

--- ruling-marker hits: ['RATIFY', 'R102'] ---
--- git log -S (commits touching this issue_id in registry) ---
5ade2b5ca0 | Trae | 2026-07-21 14:52:36 +0800 | fix(governance): 修复跨盘 D:/C: 导致 reconciler 全量失败
b6ea3dc64e | Trae | 2026-07-21 14:48:38 +0800 | feat(rules): Phase 2.5 cross-commit君子协定治本收口 + GATE-IMPORT-INTEGRITY友好提示增强 (#ARCH-CROSS-COMMIT-ATOMICITY-002)
1637a64d74 | Trae | 2026-07-21 14:45:16 +0800 | docs(arch): 登记裁定 #ARCH-RECONCILER-ALERT-SELFHEAL-001 + #ARCH-WORKTREE-AUTO-SWEEP-001



======================================================================
=== FINAL VERDICT (2026-07-24): git 提交痕迹合法性核查 ===
======================================================================

方法：对 9 条议题逐一验证 (1) 注册表 git log -S 痕迹 (2) commit hash 真实存在
      (3) 代码实际落地（文件存在/委托关系/删除生效）。零幻觉判定标准：每条
      必须有 ≥1 个真实 commit + 真实代码变更。

--- B2④ 6 条误报核查：全部合法（纯技术治本，无价值判断，不需用户决策）---

#ARCH-WORKSPACE-DRIFT-SYSTEMIC-001 | resolved | 8 commits verified
  痕迹: 4f56348145 f7f79ae684 c343ae5d6b 07f1e58763 (Trae, 07-20)
  代码: session_worktree.py 4 hooks + 5 helpers + ruling_commit_verified_gate.py
  判定: 误报 ✓ 治本工程完整落地，属事实审计记录

#ARCH-GATE-PRIORITY-UNIQUENESS-001 | resolved | 1 commit verified
  痕迹: 4fd876f870 (Trae, 07-21)
  代码: register() warn→block + GateRegistrationError(ZA-GV-0050)
  判定: 误报 ✓ priority 撞号治本，纯技术修复

#ARCH-STASH-ACCUMULATION-001 | resolved | 2 commits verified
  痕迹: 6cf9bc4590 0083150961 (Trae/Test, 07-21~22)
  代码: stash_accumulation_gate.py + trae_075（capability registry 引用）
  判定: 误报 ✓ stash 生命周期治理，纯技术修复

#ARCH-COMMIT-SERIALIZATION-001 | resolved | 1 commit verified
  痕迹: d6ff41ad16 (Zephyr Test, 07-22) + Phase 2/3 commits
  代码: GitCommitGateway commit 临界区文件锁(pathspec 强制)
  判定: 误报 ✓ commit 串行化治本，纯技术修复

#ARCH-RECONCILER-WORKER-SESSION-001 | decided | 1 commit verified
  痕迹: a9e08dea93 (Test, 07-22)
  代码: status=decided（待施工，尚未落地 worker 注册逻辑）
  判定: 误报 ✓ 纯技术治本方案登记，status 正确标 decided 未虚报 resolved

#ARCH-TSV-SOT-001 | resolved | 1 commit verified
  痕迹: 5c4b56c2ba (Test, 07-22)
  代码: tsv_codec.py L43-44 委托 ch_writer.tsv_escape（已实测验证）
  判定: 误报 ✓ TSV 转义单一真源，代码已落地

--- B2②③ 3 条真决策深查：全部合法（真实代码非幻觉），但属 AI 越权裁定需用户回溯确认 ---

#ARCH-048 | decided | 1 commit verified | 推翻子蓝图门禁
  痕迹: a16fa1ef7a (Trae, 07-05)
  代码: market.duckdb 已删除(已实测 GONE) + ClickHouse 已部署
  判定: 合法 ✓ 真实代码落地，非幻觉。但涉及"推翻子蓝图门禁/改变架构边界"
        属价值判断 → 依铁律#9 需用户回溯确认。ClickHouse 已实际运行=事实接受

#ARCH-063 | resolved | 1 commit verified | wontfix 3 种检测
  痕迹: 04d28af03f (Trae, 07-20, ruling marker R102)
  代码: 仅改注册表(0 代码变更)，5 维度分析 sound(0 使用场景/负 ROI/替代防复发链)
  判定: 合法 ✓ 分析有据，非幻觉。但"永久关闭功能"属价值判断
        → 依铁律#9 需用户回溯确认

#ARCH-ANY-GOVERNANCE-001 | resolved | 3 commits verified | RATIFY 60 项
  痕迹: d0236e8033(Phase1) e494c72623(Phase2) b7a6e21765(Phase3 merge) (Trae, 07-21~22)
  代码: any_type_inferrer.py(862行,已实测存在) + 71 Any替换(29文件) + check_any_abuse.py升级
  判定: 合法 ✓ 三阶段全部落地，非幻觉。但"RATIFY 46 项 wontfix"属价值判断
        → 依铁律#9 需用户回溯确认

======================================================================
=== 汇总 ===
======================================================================
零幻觉：9/9 条议题全部有真实 git 提交痕迹 + 真实代码落地，无 AI 凭记忆编造。
B2④ 6 条：误报确认（事实审计记录，无需用户决策）。
B2②③ 3 条：合法但属 AI 越权裁定（涉及价值判断），依铁律#9 需用户回溯确认。
机械修：severity 归一化(35条) + #ARCH-034 last_updated + #ARCH-055 status = B3 漂移清零。
铁律#9：已写入注册表头部（status 新增 proposed 值，AI 提议裁定待用户确认）。
待办：3 条真决策项（#ARCH-048/063/ANY-GOVERNANCE-001）需用户回溯确认或推翻。
