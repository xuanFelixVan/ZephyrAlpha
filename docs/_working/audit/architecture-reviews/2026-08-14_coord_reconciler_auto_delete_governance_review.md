---
title: 架构裁定书——reconciler 自动删除/归档失控族（GATE-WORKING-DOCS 误归档 + S1 覆盖面盲区 + I-GOV-2 架空）全面审查
ttl: task_bound
completes_when: "治本施工方案 T0-T2 全部落地验收后归档转 permanent"
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-08-14
topic: reconciler_auto_delete_governance
scope: global
related_issues:
  - "#ARCH-WORKTREE-WIPE-GOV-001（wipe 事故治本 S1-S6，已 merge d8f94d4f2b）"
  - "tracker §六 #53（reconciler 误删统筹文件）/ #55（pre-commit 外部钩阻断链）"
  - "I-GOV-2（reconciler 无写权铁律，architecture_issue_registry L12341）"
depends_on:
  - 65_git_safety_governance
  - 2026-08-14_ai-liq-001_worktree_wipe_incident_review
related_modules:
  - src/zephyr/governance/audit/reconciliation_registry.py
  - scripts/ops_guard.py
---

# 架构裁定书：reconciler 自动删除/归档失控族全面审查

> 审查人：统筹会话（coord-0814-git001）｜方法：物证驱动 + 第一性原理｜触发：AI-GIT-001 遗留项执行报告中五项风险上报
> 关联裁定书：[wipe 事故裁定书](2026-08-14_ai-liq-001_worktree_wipe_incident_review.md)（R1-R4 四层失守 + S1-S6 治本，已完工 merge）

## 第一部分 · 新增实证（本会话一手取证，2026-08-14 晚）

### 1.1 事件时间线（当日三波非授权文件消失）

| 时间 | 事件 | 定性 |
|---|---|---|
| 17:40-18:20 | 主工作区潘潘直播课程/ 16 个 tracked 文件被删（git restore 恢复）；untracked 草稿清风量化交易系统2.0.md 首次消失 | rogue worker PID 26288（锚定已删 AI-DOCS-001 worktree 的 payload 仍被执行）活动窗口吻合，无日志不能定罪到 reconciler |
| 19:09 / 19:25 | 第二批：tracker+裁定书+handoff+潘潘 3 文件被 move 至 .runtime/working_archive/1786707531/ | **GATE-WORKING-DOCS 幽灵引用归档器实证** |
| 19:41-19:47 | 第三批：恢复后的 tracker+裁定书+handoff+因子与策略提炼 再次被归档至 working_archive/1786708848/ | 同上加复发实证 |
| 19:04-19:15 | 清风量化交易系统2.0.md 被重建后第二次消失，未入任何 archive | 非归档器所为；窗口内 data-fix-007 会话/用户活动不能排除，物证不足定罪 |

### 1.2 三份统筹核心文件的归档铁证

`.runtime/working_archive/` 今日三批目录均含 tracker/裁定书/handoff：
- 1786687492（11:04 UTC 前）：tracker + 裁定书 + handoff + 因子与策略提炼 等 9 份——**即 15793c7a4f 所称"accd0cbe36 误删"的真相：不是 TTL reconciler，是 GATE-WORKING-DOCS 幽灵引用归档 + auto-commit 删除**
- 1786707531（19:25）：同上 + 潘潘 3 份（共 7 份）
- 1786708848（19:47）：同上 4 份（恢复后复发实证）

### 1.3 幽灵引用误判的结构性必然

归档器规则：docs/_working 文档引用的项目内路径若磁盘不存在 → 判幽灵 → move 归档 + `_commit_auto` 提交删除。
受害者文档的内容特征：tracker 引用 `.worktrees/AI-GIT-001`（已清理）、裁定书引用事故现场路径、潘潘分析文档引用数据/清单文件——**治理/分析文档天然高频引用短寿命路径，目标一死文档即中招。误判率对该类文档=100%，非调参可修，是判定规则与文档语义的结构性冲突。**

### 1.4 S1 ops_guard 覆盖面盲区实证

ops_guard 审计日志（.runtime/gate_audit/ops_guard_delete.jsonl）对三波删除**零记录**。原因：ops_guard 是 CLI + 可选 API 的**自觉调用层**拦截（check/exec/guard_rmtree），reconcile worker 是 spawn_python_hidden 拉起的独立 python 进程，不加载 $PROFILE、不经过 ops_guard，30+ reconciler 直接调 stdlib os.remove/shutil.move。**65 号六层防御（L1-L6）全部作用于 AI 会话 shell 层；治理自动化代理层零覆盖。**

### 1.5 I-GOV-2 铁律被架空实证

铁律真源（architecture_issue_registry L12341）："reconciler 只允许 warn/skip/fix-in-place，禁止 action=commit"。现实：`chore(reconciler): batched auto-commit by GitCommitGateway post-commit` 每日多笔（_commit_auto 通道）；GATE-WORKING-DOCS 借 `_commit_auto` 提交删除。**铁律与实现已全面漂移，删除类 auto-commit 是高危分支。**

### 1.6 旁证

- TTL cleanup 每次 worker 报 `deleted=0, errors=5161`（.runtime 锁定文件清理空转）——告警噪音疲劳。
- rogue worker 26288：payload 锚定已删 worktree 仍被 spawn 执行——worker 启动合法性零校验（S4 修了锚定解析，未修"该不该启动"）。
- #55：门禁运行向 tracked 文件 feature_flags.jsonl 追加时间戳审计行 → 裸 git commit 被 pre-commit 框架性误报（"files were modified"），外部钩链结构性不可过（65 号 §10 早有登记"pre-commit 框架 stash 适配——待处理"）。

## 第二部分 · 第一性原理分析

65 号 §5 的安全需求模型建立在"操作者=AI 会话"上：AI 不理解危险、无人工审查、错误瞬间发生。本事故族证明该模型漏了一类操作者——**治理自动化代理（reconciler/worker）是 7×24 隐形 AI 操作者**：

| 维度 | AI 会话 | 治理自动化代理 |
|---|---|---|
| 文件系统权限 | 全域 | 全域（同等） |
| 执行频率 | 用户驱动 | 每次 commit 必跑（更高频） |
| 单次动作审查 | 无 | 无（auto-commit 无人看） |
| 判定依据 | 指令 | **启发式规则（幽灵引用/TTL/deprecated），误判率恒>0** |
| 损害固化 | 需主动 commit | **自动 commit 入库（损害自动固化进历史）** |

**第一性原理：自动化代理的不可逆操作能力，必须小于其判定准确率。** 启发式判定准确率恒 <100% → 自动化代理永远不该持有不可逆操作能力。推论：
1. 一切自动删除必须可逆（统一回收站，保留期 >>> 发现周期）；
2. 删除类操作禁止 auto-commit（物理消除"误判×自动执行×自动入库"的放大链）；
3. 治理代理的写/删/移动能力面必须显式声明、注册表可审计（对标 D2 目的声明纪律）。

## 第三部分 · 裁定结果

- **裁定 1（#53 真凶定罪，P0）**：GATE-WORKING-DOCS 幽灵引用归档器 = tracker/handoff/裁定书三波"误删"真凶（含 accd0cbe36 原始事故）。其"归档+auto-commit 删除"能力违反 I-GOV-2 铁律。原"TTL reconciler 误删"假设勘误。
- **裁定 2（wipe 裁定书勘误）**：AI-LIQ-001 裁定书排除清单"40+ post-commit reconciler 无任何一条具备删除 tracked 文件能力"结论有误——GATE-WORKING-DOCS 具备实质删除能力（move+auto-commit）。该排除项更正（不影响 wipe 事故 R1-R4 根因裁定）。
- **裁定 3（S1 定位修正，P0）**：ops_guard 实证为 AI 会话调用层拦截，对 worker 进程零覆盖。"全原语删除拦截"叙事与实现不符；治理代理删除收敛须另立（方案 T1）。
- **裁定 4（清风丢失，P1）**：物证不足定罪到执行者；足以定罪到结构——docs/_working 下 untracked 文件"三重无保护"（不在 git、归档器可动、物理删除无审计）。文件本体请用户从外部副本恢复（若 19:04 后为用户自行移动则无事）。
- **裁定 5（rogue worker，P1）**：worker 启动合法性零校验（锚定已删 worktree 仍执行）。S4 修锚定解析未修启动准入。
- **裁定 6（#55，P1）**：门禁审计写入 tracked 文件 → 外部 pre-commit 链结构性不可过。治本=审计写迁出 tracked 区 + 65 号 §10 既有登记项落地。
- **裁定 7（告警卫生，P2）**：TTL cleanup 5161 errors 等恒定 warn 噪音刷屏→告警疲劳（真告警被淹没）本身即风险。

## 第四部分 · 治本施工方案（分层分期，验收标准可机器验证）

### T0 · 止血（P0，建议今天，低风险可逆）

1. GATE-WORKING-DOCS 归档动作降级 `dry_run=True`（只扫描出报告，不 move 不删）——一行参数，立即止血。
2. 该 reconciler 的 `_commit_auto` 删除提交禁用（删除类永不 auto-commit）。
3. 统筹文件（tracker/handoff/裁定书）入 never-archive 显式白名单——治标。
4. working_archive 三批目录与工作区逐文件比对，确保工作区版本为最新（已实证恢复）。

### T1 · 能力收敛（P0，治本核心）

1. **reconciler 操作面显式声明制**：ReconcilerSpec 增加 `file_ops` 声明字段（none/read/write/delete/move），注册时强校验；未声明 delete/move 的 reconciler 执行删除=阻断+critical_warn。
2. **删除/移动统一走 guard 库 API**：reconciler 内删除/移动原语收敛到 ops_guard 提供的安全 API（内建保护区+审计+回收站），worker 进程同样强制（库层生效，与进程无关）。
3. **统一回收站**：治理代理的一切删除/归档 move 至 `.runtime/recycle_bin/<ts>/`，保留 30 天 + 容量封顶；回收站外物理删除=违规（门禁静态扫描 + 运行时审计双保险）。

### T2 · 观测与准入（P1）

1. worker 启动三证：payload 锚定 worktree 存活 + payload TTL 新鲜度 + 发起 session 活性，缺一拒启+落日志。
2. reconciler 动作全量落盘（不只 warning——删除/移动类动作必记 detail）。
3. 文件删除审计覆盖率指标化：ops_guard 审计 / 实际删除 比=100% 入 RECONCILER-HEALTH。

### T3 · 文档保护区（P1）

1. docs/_working 分级：统筹文件迁 `_working/_coordination/` 或 frontmatter `protection: coordinator`，归档/清理器禁区。
2. docs/ 下 untracked 文件的删除/移动需人工确认（guard 规则）——清风类损失归零。
3. 本裁定书与 wipe 裁定书 ttl 转 permanent（用户已示意向）。

### T4 · #55 治本（P1）

1. 门禁审计写入迁出 tracked 区：feature_flags.jsonl 等审计日志改 .runtime/audit/（gitignored）；历史 tracked 审计文件 git rm --cached 迁出。
2. 65 号 §10 "pre-commit 框架 stash 适配"立项：裸 commit 在干净工作区全过为验收。

### T5 · 告警卫生（P2）

1. TTL cleanup errors 聚类归因（锁定跳过=clean 语义），warn 只报新增异常。
2. RECONCILER-HEALTH 横幅 24h dedup。

### T6 · 登记与文本对齐（随批）

1. I-GOV-2 表述对齐实现："_commit_auto 仅限非删除写回；删除类禁止 auto-commit"。
2. wipe 裁定书排除清单勘误（裁定 2）。
3. tracker #53 闭环路径更新 + 本裁定书 ARCH 登记。

### 验收标准

- T0：连续 3 天 post-commit 无 docs/_working 文件非授权消失（commit 后快照 diff 自动监控）。
- T1：红队测试"reconciler 删除保护区文件"100% 阻断+审计落盘；worker 进程内直接 os.remove 保护区路径同样被拦。
- T2：构造锚定已删 worktree 的 payload → worker 拒启+日志可查。
- T3：docs/ 下 untracked 文件被删必有审计记录；无记录事件=0。
- T4：干净工作区裸 `git commit` pre-commit 全过。

## 登记事项（本裁定书落地动作）

- [ ] 本文件归档 + creation_token 登记（capability_canonical_file_registry.yaml）
- [ ] #ARCH-RECONCILER-AUTO-DELETE-GOV-001 登记（architecture_issue_registry.yaml）
- [ ] tracker §六 #53 更新（真凶定罪+本裁定书引用）
- [ ] T0 止血待用户授权后执行
