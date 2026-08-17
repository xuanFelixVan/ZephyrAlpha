---
ttl: permanent
doc_type: architecture_view
title: 提交队列串行化——多 AI 并发施工的集成层总案（三层防护：队列串行 + worktree 隔离 + plumbing 拦截）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.2.0"
date: 2026-08-14
topic: commit_queue_serialization
scope: 07_trading_decision_architecture
related_issues:
  - "#ARCH-GIT-CLEAN-GUARD-FIX（2026-08-11 git clean 灾难）"
  - "#ARCH-AICOLLAB-001（Git Worktree + File Lock + Task Board 三件套）"
  - "#ARCH-WORKTREE-GATE-001（WORKTREE-REQUIRED 门禁）"
  - "#ARCH-GOV-BUDGET-002（治理预算三纪律 I-GOV-3 v2；注册表条目在 2026-08-12 并发事故中丢失，2026-08-14 已重登记）"
depends_on:
  - 01_design_memo_management_spec
  - 60_cross_cutting_cleanup
  - 61_lifecycle_multi_ai
  - 65_git_safety_governance
related_modules:
  - src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py
  - src/zephyr/gov_enforcement/rule_bridge/session_worktree.py
  - scripts/lock_files.py
  - scripts/git_guard.py
  - scripts/task_board.py
---

> ## 结案报告（2026-08-16 补记；2026-08-17 追加 AI-FOPEN-001）
>
> **实际开发**：三层防护中两层已落地——worktree 隔离强化（会话活性登记 + 心跳守护 + 四证清理）与 plumbing 底层命令拦截（wrapper 拦 read-tree/update-index 等 + git_guard 前置硬阻断，45/45+16/16 测试全绿）；§2.4 #9 task_board（任务板）按本档 schema 重建至生产态（SQLite WAL + CAS，17 测试全绿，含 8 线程并发恰一胜）。2026-08-17 AI-FOPEN-001（B2）补强提交链路 PG 依赖韧性：新建 `pg_probe.py` PG 可用性前置探针（网关 commit 前置 TCP 5432 ≤1s 探测，失败不阻断只落 `.runtime/pg_probe_state.json`；merge 前置复跑），门禁读取区分「DB 离线降级」vs「真无违规」；DEPGRAPH-FRESHNESS 在探针证实离线超 24h 时豁免 saved_at 停更误伤（豁免留痕）；`verify_schema_health.py` 连接调用移入 try 块——PG 离线从崩溃式阻断转 exit 2 明确告警（[PG-UNREACHABLE] + 引导文案）。
>
> **最终成果**：多 AI 并发施工的隔离与任务认领基础设施就位并实证；提交链路在 PG 离线场景不再误判阻断/静默放行——探针前置 + 豁免留痕 + 优雅降级三件套落地（fa25c19e49，merge 8a872d0e59+48ce3d93cb，#ARCH-119 resolved；test_pg_probe.py 等 6 测试文件全绿）。
>
> **未做事项及原因**：commit queue（提交队列）本体未做——Serializer 串行器/死信/门禁外移为大工程量单项，MVP 待排期（遗留 #67 登记在案）。

# 提交队列串行化——多 AI 并发施工的集成层总案（三层防护：队列串行 + worktree 隔离 + plumbing 拦截）

> 本备忘针对 2026-08-12 的 23 会话并发事故链（互冲/吞稿/搭便车/连坐阻断/隐形 index 重置），给出**三层治本方案**：①提交队列串行化（提交期）②worktree 隔离强化（编辑期+杂项操作）③plumbing 命令拦截（危险底层命令）。
> 性质：**决策备忘 + 施工计划**，按"背景→病根→对标→裁定→设计→施工→验证→不做→开放问题"组织。关键历程：v0.3.0 三层防护反转（事故 6 推翻 worktree 降级裁定）、v0.4.0 补全 7 处施工算法、v1.0.0 用户确认 3 项裁定升 active（详见 §13）。
> 管理规范见 [01_design_memo_management_spec](01_design_memo_management_spec.md)。
> 关联：[65_git_safety_governance](65_git_safety_governance.md)（git 安全防护层）｜[61_lifecycle_multi_ai](61_lifecycle_multi_ai.md)（多 AI 生命周期）｜[2026-08-14 worktree wipe 事故裁定书](../../04_architecture_principles_decisions/2026-08-14_ai-liq-001_worktree_wipe_incident_review.md)（姊妹篇：本文管提交期串行化，其 S1-S6 管删除原语/清理流程/观测层）

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G66 提交队列串行化（跨切治理层·集成基建） |
| 创建 | 2026-08-12 |
| 优先级 | P0（23 会话并发已实证不可施工 + read-tree 隐形 index 重置事故） |
| 状态 | active v1.1.0（3 项裁定用户已确认；**MVP 未施工**：.runtime/commit_queue/ 零施工痕迹、git_guard.py plumbing 扩展未施工、install_git_safety_wrapper.ps1 不存在；AGENTS.md §10.0 铁律已落地；**§2.4 #9 task_board 已重建并 merge 回 dev production**——2026-08-14 AI-GIT-001 按本 memo schema 重建，0e5ed3b9→d8f94d4f2b，17 测试全过） |
| 开发平台 | Trae IDE（PowerShell 5.1，无 PreToolUse hooks） |
| 上游 | [65_git_safety_governance](65_git_safety_governance.md)（安全护栏层） |
| 下游 | 所有 AI session（提交入口）｜GitCommitGateway（落盘执行体）｜task_board（死信承载）｜git_guard.py（plumbing 拦截扩展） |

## 2. 背景与病根

### 2.1 事故链实证（2026-08-12，23 会话并发审查施工）

当日 23 个并发会话全部遭遇工作区互冲。事故 1-5 简表如下；事故 6 单独详述——它是三层防护架构（§4/§5）的裁定依据。

| # | 事故 | 一句话 |
|---|---|---|
| 1 | 裸 commit 触发 pre-commit stash 吞稿 | 裸 `git commit` 触发 pre-commit 全树 stash+恢复周期，冲掉其他会话暂存（多起，靠 dangling blob 字节级恢复；网关提交走 `--no-verify` 不触发，触发源是裸 commit 尝试本身） |
| 2 | 全区 restore 冲稿 | `git restore .` / `git checkout -- .` 无差别清空其他会话未暂存修改（本会话 6 文件被冲 2 次，含已登记 ARCH 条目） |
| 3 | 共享 index 搭便车/漏收 | commit f7c4ad2e 漏收 50 号文档；A 会话 commit 卷入 B 会话 WIP |
| 4 | 门禁连坐 | `task_board.py`/`session_worktree.py` 等 WIP 文件未过门禁，阻断所有会话提交；`WORKSPACE-CLEAN-CHECK`（fail-closed）要求全仓无 WIP → 23 会话下永远不可 merge |
| 5 | 逃生通道常态化 | `--allow-non-worktree`/`--allow-overlap` 被当正门用，门禁审计稀释（65 号 §4.1 D 层第 16 项"AI 未遵守"君子协定） |
| 6 | `git read-tree` 隐形重置共享 index | 见下方完整描述 |

**事故 6 完整描述（v0.3.0 新增实证）**：架构审查 AI 在测试仓库验证 plumbing 链路时，终端 cwd 被系统重置回主仓，`git read-tree HEAD` 在主仓执行——该命令**不在任何护栏管辖范围**（不在 DANGEROUS_SUBCOMMANDS、不触发任何 hook、AGENTS.md 未提及），直接把共享 index 重置为 HEAD 状态，所有会话的 staged 元数据被清空。既有两道护栏（GATE-COMMIT-GW 拦了裸 commit、REFERENCE-TRANSACTION-GUARD 拦了无标记 update-ref）实时立功——dev 分支未动，但共享 index 已被重置。**此事故证明：即使提交路径被队列完全保护，非 commit 的 git 操作仍可破坏共享状态。**

### 2.2 病根（第一性原理）

**共享工作区 + 共享 index = 单资源无调度竞争**。23 个生产者对同一资源（工作区文件 + index + HEAD）自由读写，任何会话的 git 操作都是对其他会话的写中断。文件锁（.ailocks）只能保护"编辑期"同一文件不被两人同时改，**保护不了"提交期"git 状态机的互斥**，**更保护不了"杂项 git 操作期"（read-tree/update-index 等）对共享 index 的隐形破坏**。

既有 `_GlobalCommitLock`（git_commit_gateway.py，TTL=1800s）已串行化 commit 临界区，但锁只解决"同一时刻只有一个 commit 在进行"，**不解决**：①锁内 commit 仍读写共享工作区/index（搭便车、staged 污染）；②锁等待超时（默认 60s）在 23 会话下演化为 LOCK_TIMEOUT 风暴；③锁管不到 pre-commit stash、restore、clean、**read-tree** 等非 commit 路径的写破坏。

**三个攻击面，三种病根**：

| 攻击面 | 病根 | 实证事故 |
|---|---|---|
| 提交期（commit/stage/add） | 共享 index + 共享工作区 → 搭便车/stash 吞稿/连坐 | 事故 1/3/4 |
| 编辑期（文件读写） | 共享工作区 → restore 冲稿/两会话改同一文件 | 事故 2 |
| 杂项 git 操作（read-tree/update-index/clean 等） | 共享 index 被隐形重置 → staged 元数据全清 | 事故 6（v0.3.0 新增） |

早期 2-3 会话不恼火，不是当年方案好，是冲突概率低自然排队。**并发数超过阈值后，共享状态模型的崩溃是数学必然。**

### 2.3 既有防护的失效点

| 层 | 失效 |
|---|---|
| git_guard alias 拦截 | git 2.48.1 内置命令不可覆盖（8-11 已证实）；且 DANGEROUS_SUBCOMMANDS 只含 7 个 porcelain 命令（reset/checkout/stash/revert/restore/mv/clean），**plumbing 命令（read-tree/update-index/write-tree/hash-object）全裸无防护** |
| .ailocks 文件锁 | 只管编辑期，不管提交期；stash/restore/read-tree 不经过锁 |
| WORKTREE-REQUIRED 门禁 | Layer-1 in-process gate 并发即阻断（fail-closed 有效），Layer-2 pre-commit hook warn×5 额度形同虚设且 gateway 路径 `--no-verify` 根本不到 Layer-2 |
| pre-commit 框架 stash | 裸 commit 尝试即触发 stash/恢复周期，并发恢复互相踩掉暂存 |
| REFERENCE-TRANSACTION-GUARD | 有效堵住 commit-tree+update-ref 绕过，但**管不到 read-tree/update-index 等不涉及 ref 更新的 index 操纵命令** |

### 2.4 已施工设施盘点（2026-08-12 架构审查实测，方案设计的起点）

> 通用规则 #11 要求：先清楚有什么 → 才能知道怎么改 → 才能知道该退役什么。以下逐项经代码/配置核对。

| # | 设施 | 位置 | 现状 | 与本方案的关系 |
|---|---|---|---|---|
| 1 | `_GlobalCommitLock` 全局跨进程串行锁 | git_commit_gateway.py（.ailocks/git_commit_global.lock，TTL=1800s，超时默认 60s，僵尸 PID 清理） | production | **commit 串行化已存在**——队列的真实增量是"快照落袋 + 门禁外移 + 调用方免等待"，不是串行化本身 |
| 2 | CommitGateRegistry in-process 门禁簇 | commit_gates/ 目录 100 个 gate 文件（auto_register_gates YAML 驱动注册） | production | **其中 62 个文件含工作区内容读取**（read_text/open/isfile 共 148 处实证）——temp-index 形态需 blob 喂入改造（大工程）；专用 worktree 形态零适配 |
| 3 | GATE-COMMIT-GW 裸 commit 硬阻断 | .pre-commit-config.yaml + validate_commit_gateway.py | production | 裸 commit 已被拦，但拦截发生在 pre-commit stash 之后——stash 周期触发源仍在 |
| 4 | POST-COMMIT-GUARD | scripts/governance/git_hooks/post_commit_guard.sh | production | non-GW commit 自动 `git reset --soft HEAD~1`；**plumbing（commit-tree/update-ref）不触发 post-commit hook，本层管不到** |
| 5 | REFERENCE-TRANSACTION-GUARD | scripts/governance/git_hooks/reference_transaction_guard.sh（git 2.45+ hook） | production | **plumbing ref 绕过已堵**：refs/heads/dev forward 更新的 commit message 不含 `[GW:` 子串即 block 回滚。本方案落盘 message 附 `[GW:{sid}:q-{qid}]`，前缀匹配兼容（已核对 hook 的 `grep '\[GW:'` 子串匹配逻辑）。**但 read-tree/update-index 等不涉及 ref 的 index 操纵管不到** |
| 6 | reconciler auto-commit 链 | `_commit_auto` + BatchedAutoCommitter + reconcile_runner worker（32+ reconciler 产出派生文件自动提交） | production | **第二写入者**：走共享 index + 全局锁。单写者不变量要求它改道入队（§7 关系表） |
| 7 | session_worktree 族 | session_worktree.py / worktree_manager.py / worktree_pool.py / worktree_lifecycle.py（.aidrafts/{sid}/） | production | merge 前置 WORKSPACE-CLEAN-CHECK 在 23 会话下永不可达；**队列落地后 merge 消失 → 该检查对象消失 → worktree 从"23会话下不可达的强制"变为"queue 消除 merge 后可达的强制"——不是降级，是升级** |
| 8 | lock_files.py 文件锁 | .ailocks/（TTL + PID 检测） | production | 保留——编辑期同文件互斥仍由它负责 |
| 9 | task_board.py | .runtime/task_board.db（SQLite WAL + CAS，状态机 pending→claimed→completed，`metadata_json` + `task_events.payload_json` 可扩展字段） | ✅ **已重建并 merge 回 dev production**（2026-08-14 AI-GIT-001 按本表 schema 重建，0e5ed3b9→d8f94d4f2b，17 测试全过含 8 线程 CAS 恰一胜/60min TTL/exit 2 DENIED/死信 metadata 承载/板根锚主仓跨 worktree 单板） | schema 可承载死信标签（qid+原因+属主进 metadata_json）；无现成 dead_letter 状态，用 metadata 标签即可，无需改表 |
| 10 | git_guard.py 危险命令拦截 | DANGEROUS_SUBCOMMANDS={reset,checkout,stash,revert,restore,mv,clean} | production | **7 个 porcelain 命令已覆盖；read-tree/update-index/write-tree/hash-object 4 个 plumbing 命令完全缺失（v0.3.0 新发现）**。alias 失效问题依旧，但 install_git_safety_wrapper.ps1 落地后可在 shell 函数层扩展覆盖 |
| 11 | install_git_safety_wrapper.ps1 | 65 号 §7.7 施工项 7（P0） | **不存在（未施工）** | 落地后可在 shell 层拦截裸 `git commit` + 扩展拦截 plumbing 命令，是 stash 周期触发源 + index 隐形重置的真正清零手段（§7 关系表） |
| 12 | test_concurrent_safety.ps1 | scripts/governance/ | production | **真实用途：47 个治理脚本的并发安全压测**（RULE-ONE 原子写模式），不含 git commit 场景——§11 的"复用"修正为"借鉴其 Start-Job 并发模式，新建 commit queue 压测" |
| 13 | .runtime/commit_queue/ | — | **零施工痕迹** | 本方案全新建 |
| 14 | AGENTS.md §10 | git 命令封装约定 + POST-COMMIT-GUARD + REFERENCE-TRANSACTION-GUARD 文本 | production | **不含"改完立即 add"铁律文本**（2026-08-12 曾写入，并发事故中被 wipe 未落盘）——§4 裁定 6 的"演化"实为"新建" |
| 15 | emergency_commit.py | rule_bridge/（commit-tree plumbing 合法逃生通道，落审计） | production | 证明 plumbing 直写在本仓已有生产先例，且与 REFERENCE-TRANSACTION-GUARD 豁免兼容 |
| 16 | DANGEROUS_SUBCOMMANDS plumbing 盲区 | git_guard.py | **4 个 plumbing 命令完全未覆盖** | `read-tree`/`update-index`/`write-tree`/`hash-object` 直接操纵 index/对象库，不受任何 hook/gate 管辖——事故 6 的根因。需扩展（§4 裁定 7） |

**盘点结论**：串行化锁、门禁链、plumbing ref 绕过封堵、worktree 隔离、文件锁、任务板均已存在；缺口集中在三个面：①提交期与共享工作区/index 的解耦（队列解决）②worktree 在 23 会话下因 merge 不可达而形同虚设（队列消除 merge 后可达）③plumbing index 操纵命令零防护（shell wrapper 扩展解决）。三层叠加才能覆盖全部攻击面。

## 3. 业界对标（本方案不是发明，是组装）

### 3.1 组装对照表

| 本方案组件 | 业界对应物 | 来源 |
|---|---|---|
| 快照入队即完成 | Transactional Outbox（事务发件箱） | 微服务社区 |
| 后台单程序按序落盘 | **Merge Queue**（GitHub Merge Queue / Rust Bors / OpenStack Zuul / Chromium Commit Queue） | CI/CD 社区主干保护标准答案 |
| 单写者定序 | **LMAX Disruptor** Single-Writer Sequencer | 量化交易低延迟骨架（机构 OMS 日志定序同款） |
| 同会话同文件二次提交覆盖首次 | Kafka Log Compaction（同 key 留最新） | 消息队列社区 |
| 冲突打标签跳过+人工处理 | Dead-Letter Queue + 人工分拣 | 消息队列/支付系统 |
| 不碰工作区直接造 commit | Merge bot 惯例（plumbing 直写） | GitHub/GitLab merge bot 实现方式 |
| 入队自举排空（无常驻 daemon） | Outbox relay 轮询 / SQLite WAL 下次打开即恢复 | 微服务+嵌入式 DB 社区 |
| worktree 隔离（每会话独立 checkout+index） | Claude Code `--worktree` / Codex Worktree 模式 / VS Code 2026-08 默认 agent worktree | AI 编程社区 2026 标准实践 |
| plumbing 命令拦截 | git hook 不可覆盖 plumbing → shell wrapper 是唯一可靠层 | 65 号 §3.1 已证实；git-courer（2026-05）同模式 |

### 3.2 2026 年最新实践核验（2026-08-12 两轮 WebSearch，结论式摘要）

- **Merge Queue 是主干保护标准答案**：GitHub Merge Queue 现行有效；rust-lang（bors→GH MQ）、Chromium（Commit Queue，与本方案同名）、VS Code、K8s Prow/Tide 全部采"落盘前对最新基底重验证"形态；tenki.cloud（2026-07）称 merge queue 对 agent 级提交量"近乎必选"。
- **worktree 隔离 + merge queue 串行叠加是 2026 社区共识（非二选一）**：Claude Code `--worktree` + 内部 commit 串行；Codex Worktree 模式 + PR 合并；VS Code 2026-08-07 起默认为 agent session 启用 git worktree 隔离（"concurrent agents 未提交修改被静默覆盖"是 2026-08 行业公认失败模式，worktree 隔离是其标准解法）；"2-4 个并发 agent 是可管理上限"是社区经验值。v0.3.0 三层架构与该共识对齐。
- **claude-fleet（2026-07）三层同构**：git-worktree 隔离 + sequential merge gate + tool-layer guard hooks，与本文三层架构几乎完全同构；其 crash recovery + "dead agent never holds a lock" 设计验证了 Serializer lease TTL+僵尸 PID 检测方向。
- **fak commit-lane（2026-06）submit/drain 同构**：`fak commit submit` = 本文 enqueue，`fak commit drain` = 本文 Serializer drain；intent 记录字段与本文 qid/base_head/files/blob/session_id/message 结构同构；并发提交不取 git index 锁、stale-base/dirty-path 在 drain 前拒绝——验证本文核心设计原则。**submit/drain 单写者队列是 2026 新兴工业模式，非过度工程。**
- **AgenticFlict（AIware 2026 学术论文）27.67% 冲突率**：107K+ AI 生成 PR 确定性合并模拟，27.67% 命中合并冲突（336K+ 冲突区域）——冲突是规模化的中位结果，实证 worktree+queue 三层架构的必要性。
- 其他同向实证：git-courer（2026-05）plumbing 直写生产实证（write-tree 预览 + commit-tree + update-ref 落盘，工作区全程不碰，与 §6.3 P2 同路径）；Cursor 3.0（2026-04）虚拟快照（本文 `base_head` 语义同向）；agentlocks（2026-07）无 daemon 无数据库纯文件（与入队自举排空哲学一致）；Dekaf.Outbox（2026-07）确认 at-least-once + 幂等消费 + relay 轮询标准形态（与"快照落盘即安全 + 重放幂等"同构）。

### 3.3 更轻量替代方案与排除理由（v0.3.0 修正——worktree 从"排除"翻为"采纳"）

| 替代方案 | 排除/采纳理由 |
|---|---|
| ① 只做强全局互斥锁（现状 `_GlobalCommitLock` 加大超时） | **排除为终点**：锁已存在，但锁内 commit 仍读写共享工作区/index——搭便车、staged 污染、门禁连坐、pre-commit stash 四类病灶一个不少。串行化 ≠ 解耦 |
| ② worktree 强制升硬（THRESHOLD→0，全会话强制） | **v0.2.0 排除 → v0.3.0 翻转为采纳（第二层防护）**：v0.2.0 排除理由是"merge 仍是竞争点（WORKSPACE-CLEAN-CHECK 要求全仓无 WIP，23 会话下永不可 merge）"。但队列落地后 merge 操作消失（Serializer 直提 dev），WORKSPACE-CLEAN-CHECK 对象消失——worktree 的最大障碍自动解除。且事故 6（read-tree 隐形重置 index）证明 worktree 不只防提交期冲突，还防杂项 git 操作的共享 index 破坏（每 worktree 有独立 index）。**三层架构：队列消除 merge 障碍 → worktree 变可行 → worktree 隔离 index → 非提交操作只崩自己不崩全仓** |
| ③ Named Pipe / 常驻协调 daemon | **排除**（65 号 v2.1.0 已 deprecated 同形态 L19：单点故障 + 运维负担）。本方案 Serializer 采纳"入队自举排空"形态（§8），无常驻进程，避开该否决 |
| ④ 只拦裸 commit（wrapper 落地即 stash 触发源清零） | **部分采纳为配套（第三层防护的组成）**：install_git_safety_wrapper.ps1 落地后 stash 周期频次趋零，但搭便车/连坐/共享 index 病灶仍在——是配套不是替代。**v0.3.0 扩展：该 wrapper 同时拦截 plumbing 命令（read-tree/update-index/write-tree/hash-object），堵住事故 6 的根因** |
| ⑤ 先恢复"改完立即 add"纪律 + 现有 gateway 不变 | **排除**：8-12 实证 add 快照在多会话 stash 周期下不保险（dangling blob 恢复实战）；纪律层补丁不改变共享状态模型的数学必然性（§2.2） |
| ⑥ **队列 + 专用 worktree + 现有 gateway 落盘** | **采纳为 MVP 落盘形态**（§4 裁定 3）：Serializer 在专用 worktree（.aidrafts/serializer/）内把快照落成真实文件、走现有 gateway 全门禁提交——100 个门禁零适配、reconciler 链/post-commit 审计/reference-transaction guard 全部自然生效 |
| ⑦ 只做 worktree 不做队列 | **排除**：worktree 解决编辑期+杂项操作隔离，但提交期仍有竞争（多 worktree merge 到 dev 仍需串行）；且 WORKSPACE-CLEAN-CHECK 在 23 会话下使 merge 不可达——不消除 merge，worktree 形同虚设。必须队列先行消除 merge，worktree 才能跟进 |

## 4. 裁定

> v0.3.0 关键反转：原 v0.2.0 裁定 5"worktree 降级为可选"被事故 6（read-tree 隐形重置 index）推翻。改为"三层叠加"——队列 + worktree + plumbing 拦截，缺一则事故重演。
> v1.0.0：用户确认全部 3 项裁定——整体方案采纳 / worktree 强化 / AGENTS.md 新建铁律。文档升 active。

1. **采用提交队列串行化为集成层唯一提交入口**【采纳，用户已确认】：会话提交 = 快照入队即返回；落盘由单写者定序器（Serializer）按序完成。既有 `_GlobalCommitLock` 保留为 Serializer 内部实现细节与逃生通道兜底。
2. **快照语义**【采纳】：入队项携带**完整文件内容快照**（非 diff），同会话同文件的后续入队直接**整体替换**前项（compaction）。审查论证：入队是会话显式动作（"改完立即入队"），pending 旧快照被同键新快照覆盖无"有意保留的中间态"损失场景——旧项的内容必然已被工作区最新内容包含；覆盖仅作用于 pending 项，done/dead 不参与。
3. **落盘形态：MVP 专用 worktree 复用现有门禁链，temp-index plumbing 降级为 P2 优化**【修正】：v0.1.0 的"Serializer 直接 plumbing 直写（临时 index）"实测**技术可行**（2026-08-12 测试仓库验证：GIT_INDEX_FILE 独立 index + read-tree + hash-object -w + update-index --cacheinfo + write-tree + commit-tree -F + update-ref 全链跑通，工作区零接触，删除经 --force-remove 支持），但两处实测发现要求修正：
   - **§6.3 原伪代码"从 base_head 建树"实测为树级回滚 bug**：基底滞后时，新 commit 的 tree 会把中间 commit 的其他文件改动静默回滚（测试仓库实证：中间 commit 的 c.txt 在新 HEAD 树中消失）。**必须改为"从当前分支 HEAD 建树 + 快照覆盖 + 逐文件 base_blob 冲突检查"**。
   - **门禁适配成本被低估**：100 个 in-process gate 中 62 个直接读工作区文件内容（§2.4 #2），temp-index 无工作区形态需逐门 blob 喂入改造，远超 MVP 预算。专用 worktree 形态下快照落成真实文件、现有 gateway 全门禁链（含 post-commit reconciler 链、审计落盘）零改动生效。
   - plumbing temp-index 路径保留为 P2 性能优化方向（跳过文件复制），届时需同步完成门禁 blob 化与 reconciler 显式触发改造。
4. **门禁在出队端逐项执行**【采纳，执行位置修正】：每项经 GitCommitGateway 全门禁（MVP 在专用 worktree 内）；失败弹出入死信（task_board 打标签），**不卡队**；依赖被弹出项的后续项级联标记。门禁一套不裁（守 65 号安全层），只是执行点从"会话本地"挪到"定序器出队端"。
5. **worktree 从"降级为可选"反转为"强化为第二层防护"**【v0.3.0 关键反转，用户已确认】：v0.2.0 原"降级"裁定被事故 6 推翻。`git read-tree` 隐形重置共享 index 证明 worktree 的隔离价值不限于提交期——每 worktree 有独立 index，`read-tree` 在某 worktree 内只崩该 worktree，不碰共享 index。且 66 号队列消除 merge（Serializer 直提 dev）→ WORKSPACE-CLEAN-CHECK 对象消失 → worktree 的最大障碍（23 会话下 merge 不可达）自动解除。**三层架构：队列消除 merge 障碍 → worktree 变可行 → worktree 隔离 index → 非提交操作只崩自己不崩全仓**。建议口径：队列 MVP 验收通过后，worktree 从"23会话下不可达的强制"升级为"queue 消除 merge 后可达的强制"——不是降级，是升级。61 号 §3.6 / 65 号 §7.6 / ARCH-WORKTREE-GATE-001 三处口径随之联动修订（§12 开放问题 6）。
6. **AGENTS.md §10 铁律演化**【采纳，用户已确认，事实修正】：AGENTS.md 现行文本**不含**"改完立即 add"条款（2026-08-12 曾写入但并发事故中被 wipe 未落盘，§2.4 #14）——本项实为**新建**"改完立即入队"铁律。v1.0.0 起随本文 active 生效，AGENTS.md §10 同步新增条款。队列 MVP 落地前，会话纪律按现行"改完立即 `git_guard.py add`"（记忆层）执行。
7. **plumbing 命令拦截扩展（第三层防护）**【v0.3.0 新增，采纳】：事故 6 证明 `read-tree`/`update-index`/`write-tree`/`hash-object` 4 个 plumbing 命令完全无防护，可直接操纵共享 index/对象库。裁定：①扩展 git_guard.py 的 DANGEROUS_SUBCOMMANDS 加入这 4 个命令（warn+审计，非硬阻断——emergency_commit.py 合法使用 commit-tree 需保留逃生通道，故 commit-tree/update-ref 不加入，由 REFERENCE-TRANSACTION-GUARD 专管）；②install_git_safety_wrapper.ps1（65 号 §7.7 P0 待施工）落地时在 shell 函数层同步覆盖这 4 个命令的拦截。**例外**：Serializer 专用 worktree 内的 plumbing 操作不拦（在隔离环境内，不影响共享 index）——通过 `ZEPHYR_SERIALIZER_MODE=1` 环境变量白名单实现。

## 5. 总体架构（v0.3.0 三层防护）

```text
┌─────────────────────────────────────────────────────────────┐
│                    三层防护架构                              │
│                                                             │
│  Layer 3: plumbing 命令拦截（shell wrapper + git_guard.py） │
│  拦截 read-tree/update-index/write-tree/hash-object          │
│  → 防止隐形 index 重置（事故 6 根治）                        │
│                                                             │
│  Layer 2: worktree 隔离（每会话独立 checkout+index）        │
│  → 隔离编辑期+杂项操作的共享状态                             │
│  → read-tree 在 worktree 内只崩自己（事故 6 防线）           │
│  → 队列消除 merge 障碍后 worktree 变可行                     │
│                                                             │
│  Layer 1: 提交队列串行化（Serializer 单写者）               │
│  ┌─ 会话 A/B/…/W ─────────────────────────────────┐         │
│  │  edit → enqueue(快照) → 继续干活               │         │
│  └──────────────────┬─────────────────────────────┘         │
│                     ▼                                       │
│  ┌─ Commit Queue ───────────────────────────────┐          │
│  │  pending/ → processing/ → done/ | dead/      │          │
│  │  同键覆盖：(session_id, path) 最新替换旧      │          │
│  └──────────────────┬───────────────────────────┘          │
│                     ▼                                       │
│  ┌─ Serializer（入队自举排空，专用 worktree）──┐          │
│  │  取项 → 快照落 worktree → gateway 全门禁     │          │
│  │  → commit 前进 dev → done/                   │          │
│  │  失败 → dead/ + task_board 标签              │          │
│  └──────────────────┬───────────────────────────┘          │
│                     ▼                                       │
│               dev 主干（唯一写入者 = Serializer 通道）       │
└─────────────────────────────────────────────────────────────┘
```

**关键不变量**：①dev 分支的 ref 更新只经 Serializer 通道（单写者）；②会话永不在主干上直接 commit；③每会话有独立 worktree index（非 commit 操作不碰共享状态）；④plumbing 命令在会话层被拦截（只在 Serializer worktree 内放行）。注意 reconciler auto-commit 是现状第二写入者（§2.4 #6），MVP 必须将其改道入队（§7 关系表），否则不变量①破裂。

## 6. 核心协议

### 6.1 入队项 schema（`.runtime/commit_queue/pending/{qid}.yaml`）

```yaml
qid: q-20260812-{session_id}-{seq:04d}     # 唯一 ID（单调序号保 FIFO）
session_id: sess-xxx                        # 生产者
created_at: 2026-08-12T21:30:00+08:00
branch: dev                                 # 目标分支
message_file: msg.txt                       # commit message（同目录，UTF-8 无 BOM）
base_head: f7c4ad2e...                      # 入队时观察到的目标分支 HEAD
files:                                      # 快照清单（完整内容，非 diff）
  - path: docs/.../36_var_es_monitoring.md
    blob: blobs/f34adb8b...                 # 内容快照（queue 内嵌 blob 存储，按内容 hash 命名天然去重）
    base_blob: 9c2e...                      # 编辑基底 blob（用于冲突判定）
    action: modify                          # add / modify / delete
supersedes: q-20260812-sess-xxx-0002        # compaction：被本项整体替换的旧项
```

**快照即落袋**：blob 写入队列目录即任务完成，工作区后续被 restore/清空不影响本项。
**大小约束**：单 blob 上限 10MB（本仓提交对象以文本为主，超限拒绝入队并提示走人工）；done/ 保留 7 天由 TTL 清理（复用 make_runtime_cleanup_reconciler 模式）；dead/ 永不自动清理。

**v0.4.0 补全——enqueue 原子性与并发安全**：
- **qid 生成**：`q-{date}-{session_id}-{seq:04d}`，seq 是 session 内单调递增序号（维护在 `.runtime/commit_queue/{session_id}.seq` 文件中，CAS 原子递增）。多会话各自独立 seq，qid 天然不冲突（session_id 不同）。
- **文件创建原子性**：`pending/{qid}.yaml` 用 `os.open(O_CREAT|O_EXCL)` 原子创建——若 qid 碰撞（极端情况）则 O_EXCL 失败，重试 seq+1。
- **blob 写入原子性**：blob 先写 `blobs/{sha}.tmp` 再 `os.replace` 为 `blobs/{sha}`（对标 SessionRegistry._save 原子写入模式）。按内容 hash 命名天然去重——同内容不重复存储。
- **base_blob 获取**：enqueue CLI 执行 `git rev-parse HEAD:{path}` 获取该文件在 HEAD 中的 blob hash，写入 `base_blob` 字段。若 HEAD 中不存在该文件（新文件），base_blob 为空。
- **快照内容读取**：从**工作区文件**读取（非 git index），因工作区是 AI 编辑的最终态。读取前 MUST 先 `lock_files.py acquire {path}` 确保无其他会话正在编辑该文件（编辑期锁保护），读取完成后再 release。这与既有 .ailocks 编辑期锁协议无缝衔接——enqueue 只是"读取时也需持锁"的扩展。
- **并发安全结论**：多会话同时 enqueue 各自的 `{qid}.yaml` 独立文件，无共享写状态，天然并发安全（fak commit-lane 同构："Submit is safe to call concurrently and does not take the git index lock"）。

### 6.2 同键覆盖（compaction）

- 键 = `(session_id, path)`。同键新项入队时，若旧项仍在 pending → 旧项标记 `superseded_by` 并移除，新快照整体替换（Kafka compaction 语义）。
- **仅快照语义下安全**：因为存的是完整新内容而非增量补丁，替换=最终态正确。
- 跨会话同文件不产生覆盖（键不同）——走正常 FIFO + 冲突判定（§6.4）。
- **v0.4.0 补全——compaction 竞态防护**：同一 session 的两次 enqueue 几乎同时到达时（AI 快速连续入队同一文件两次），compaction 的"检查旧项 → 标记 → 替换"序列需在 session seq 锁内完成（seq 递增本身就是串行点——seq N 的 enqueue 必须在 seq N-1 的 enqueue 完成后才能开始，因为 seq 文件是 CAS 递增）。因此 compaction 天然串行，无竞态。**死信恢复项重入队也参与 compaction**：死信被属主会话取回重新入队时，若该会话同文件已有更新的 pending 项，死信恢复项的快照（基于当前 worktree 读取）必然比 pending 项更新（因为死信的 base_head 更新），compaction 保留死信恢复项、移除旧 pending 项——正确行为。

### 6.3 Serializer 主循环（v0.2.0 修正版——实测修正树级回滚 bug）

**MVP 形态（专用 worktree）**：

```powershell
# 伪代码（Python 实现，入队自举排空：enqueue 成功即尝试拿 lease 排空，无常驻进程）
# ★v0.4.0 补全：Serializer lease 获取算法
$lease = Acquire-SerializerLease ".ailocks/commit_serializer.lock" -TTL 300 -Timeout 5
if (-not $lease) { break }   # 另一个 Serializer 在跑，放弃（自举模式：不等待）

while ($true) {
    $item = Queue-TakeHead   # FIFO，原子移动 pending/ → processing/
    if (-not $item) { break }                              # 排空即退出
    if (Test-AlreadyLanded $item) { Queue-MarkDone $item; continue }  # 幂等重放保护（§8）

    # ★v0.4.0 补全：worktree 准备步骤（每次取项前同步 HEAD + 清理工作区）
    # 1. 同步 worktree HEAD 到当前 dev（上一项 commit 后 dev 已前进）
    git -C ".aidrafts/serializer" merge --ff-only refs/heads/dev
    # 2. 清理 worktree 中上一项的残留文件（删除不在 HEAD 中的文件）
    git -C ".aidrafts/serializer" clean -fd   # 只在 serializer worktree 内，安全
    # 3. 重置 worktree 工作区到 HEAD（丢弃上一项的文件修改）
    git -C ".aidrafts/serializer" reset --hard HEAD

    # ★v0.4.0 补全：快照应用（含 delete 处理）
    Apply-SnapshotToWorktree $item ".aidrafts/serializer/"  # 快照写成真实文件（含 delete 删除文件）

    # ★v0.4.0 补全：message_file 用绝对路径（worktree cwd 与队列目录不同）
    $msgAbsPath = [IO.Path]::GetFullPath("$item.queue_dir/$item.message_file")
    $result = Gateway-Commit -Worktree ".aidrafts/serializer/" `
        -SessionId $item.session_id -MessageFile $msgAbsPath  # 现有全门禁链零适配
    if ($result.status -eq "OK") {
        Queue-MarkDone $item
    } else {
        Queue-MarkDead $item -Reason $result.message       # 死信 + task_board 标签
        MarkDependents $item                               # 级联标记（§6.4）
    }
}
Release-SerializerLease $lease
```

**P2 优化形态（plumbing temp-index 直写，修正后伪代码）**：

```powershell
$env:GIT_INDEX_FILE = ".runtime/commit_queue/serializer.index"   # 独立 index
$env:ZEPHYR_SERIALIZER_MODE = "1"                     # plumbing 拦截白名单（§4 裁定 7）
# ★修正1：从当前分支 HEAD 建树（不是 base_head——base_head 建树实测树级回滚，
#         2026-08-12 测试仓库实证中间 commit 的文件在新树中静默消失）
git read-tree refs/heads/$item.branch
foreach ($f in $item.files) {
    # ★修正2：逐文件冲突检查在覆盖前（§6.4）
    if ($f.action -eq "delete") { git update-index --force-remove $f.path; continue }
    $sha = git hash-object -w $f.blob                # 快照入对象库
    git update-index --add --cacheinfo 100644,$sha,$f.path
}
$tree = git write-tree
$head = git rev-parse refs/heads/$item.branch
# ★修正3：commit message 用 -F 文件传入（commit-tree 支持 -F）——
#         PowerShell 5.1 管道传中文 message 必毁编码（项目既有教训），禁止 stdin 管道
$commit = git commit-tree $tree -p $head -F $item.message_file   # message 含 [GW:{sid}:q-{qid}]
# ★修正4：update-ref 用 CAS 形式（带上期望旧值）——单写者下是免费保险，
#         防 reconciler auto-commit 等漏网第二写入者静默竞态
git update-ref refs/heads/$item.branch $commit $head
# ★修正5：落盘后同步主工作区共享 index（git read-tree HEAD，默认 index）——
#         否则共享 index 相对新 HEAD 陈旧，git status 出现幻影 staged 条目
#         （实测确认该副作用）。注意：此操作重置 staged 区——队列纪律下会话
#         不再手工 git add（入队替代暂存），staged 区恒为空，重置无损失
git read-tree HEAD
Remove-Item Env:GIT_INDEX_FILE
Remove-Item Env:ZEPHYR_SERIALIZER_MODE
```

**与工作区零接触（指主工作区文件内容）**：Serializer 只写对象库 + 独立 index + ref（P2）或专用 worktree 文件（MVP），主工作区文件、各会话未入队修改全程不被触碰。专用 worktree 形态下 WORKTREE-REQUIRED gate 自然满足（Serializer 本就在 worktree 内）。P2 形态下 plumbing 拦截层通过 `ZEPHYR_SERIALIZER_MODE=1` 白名单放行（§4 裁定 7）。

### 6.4 冲突判定与死信（v0.2.0 修正——merge-file 实测偏弱）

- **逐文件快进判定**：出队时对每项文件比较 `base_blob` 与当前 HEAD 中该路径 blob——一致 → 快进应用；快照内容与 HEAD 内容已一致 → 幂等跳过。
- **内容级合并实测结论（2026-08-12 测试仓库）**：`git merge-file` 三方合并对**相邻行编辑**和**双端 EOF 追加**均判冲突（rc=1）——而注册表类热点文件的最常见并发形态恰是"两会话同区域追加条目"。故内容级自动合并**降级为尽力而为的优化**，主恢复路径为死信 + 重新入队：
- **门禁失败 / 冲突不可判 → 死信**：项移 `dead/`，task_board 打标签（qid + 失败原因 + 所属 session，写入 metadata_json，无需改表），队列继续前进（DLQ 语义，不堵队）。
- **级联标记**：项 X 被弹出后，队列中 `base_head` 经由 X 的后续项全部标记 `stale`，重校验基底——仍适用则放行，不适用则降级为死信候选。
- **死信闭环（低摩擦实证路径）**：标签进入 task_board，由属主会话（或人工）取回——取回动作 = **基于当前 worktree 文件内容重新入队**。因每会话有独立 worktree，重新入队的快照基于本会话 worktree 状态，一次重试即可通过快进判定。
- **语义冲突不自动合并**（§9 第 1 条不变）：两会话改同一文件的语义冲突一律死信回退给人/属主会话。

### 6.5 门禁位置

| 时机 | 内容 |
|---|---|
| 入队时（轻） | schema 校验 + 快照完整性 + pathspec 白名单（禁止 .git/密钥路径入队）+ 单 blob 10MB 上限 |
| 出队时（重） | GitCommitGateway 全门禁（in-process gates + pre-commit 等价检查）——**MVP 在专用 worktree 内执行，100 个现有门禁零适配**；P2 temp-index 形态需先完成 62 个读工作区内容门禁的 blob 喂入改造（§2.4 #2 实证清单） |
| 失败处置 | 死信，不卡队；门禁误报由属主会话修后重新入队 |

**原则**：门禁一套不裁（守 65 号安全层），只是执行点从"会话本地"挪到"定序器出队端"。

### 6.6 落盘确认接口

- `python scripts/commit_queue.py status --session <sid>` → 返回该会话各 qid 的 pending/done/dead 状态。
- **硬约束**：会话执行 push / 通知他人消费 / 声明任务完成前，MUST 先确认自己的队列项全部 done（防"以为提交了其实还在排队"的读旧历史事故）。
- task_board 显示各会话队列深度（可观测性）。
- status 调用本身触发一次排空尝试（自举形态下队列永不长期滞留）。

## 7. 与既有机制的关系

| 机制 | 关系 |
|---|---|
| GitCommitGateway | 复用其门禁链与串行锁概念，Serializer 是其"后台化"形态；MVP 直接调用它完成落盘 |
| reconciler auto-commit（`_commit_auto` + BatchedAutoCommitter + reconcile_runner worker） | **现状第二写入者，MVP 必须改道入队**（`_commit_auto` 内部 reroute 到 enqueue，一处改动）——否则 dev 存在两个 ref 写入者，单写者不变量破裂，且其共享 index `git add` 路径仍是搭便车面 |
| session_worktree | **v0.3.0 反转：从"降级"改为"强化为第二层防护"**——队列消除 merge 障碍后 worktree 变可行，worktree 隔离 index 防 read-tree 类隐形破坏。待用户裁定（§4 裁定 5），过渡期内现行纪律不变 |
| AGENTS.md §10 | 新增"改完立即入队"铁律（**新建**非演化，现行文本无"改完立即 add"条款）；全区恢复命令禁令不变 |
| pre-commit 框架 stash | 队列消灭的是"AI 主动裸 commit 的动机"（入队替代），触发频次趋零；**真正清零靠 install_git_safety_wrapper.ps1 落地在 shell 层拦截裸 `git commit`**（65 号 §7.7，当前未施工） |
| task_board.py | 死信标签的承载与展示（**wipe 丢失，AI-GIT-001 重建中**；schema 的 metadata_json 可承载，无需改表——§2.4 #9） |
| WORKSPACE-CLEAN-CHECK | 队列落地后 merge 操作消失（Serializer 直提 dev），该检查**对象消失**自然退役，无需删代码 |
| REFERENCE-TRANSACTION-GUARD | 既有 plumbing ref 绕过封堵（[GW: 前缀豁免）——本方案落盘 message 附 `[GW:{sid}:q-{qid}]` 前缀匹配兼容（hook grep 逻辑已核对）；MVP 验收必测此路径 |
| 文件锁 .ailocks | 保留——编辑期同文件互斥仍由它负责 |
| git_guard.py DANGEROUS_SUBCOMMANDS | **v0.3.0 扩展**：加入 read-tree/update-index/write-tree/hash-object（warn+审计），commit-tree/update-ref 不加（由 REFERENCE-TRANSACTION-GUARD 专管）。Serializer 通过 `ZEPHYR_SERIALIZER_MODE=1` 白名单放行 |
| install_git_safety_wrapper.ps1 | **v0.3.0 扩展**：落地时同步覆盖 plumbing 命令拦截（4 个新命令 + 既有 7 个 porcelain），是 shell 层真正清零 stash 触发源 + index 隐形重置的手段 |

## 8. 故障与恢复

| 故障 | 处置 |
|---|---|
| Serializer 形态 | **入队自举排空，无常驻进程**：enqueue/status CLI 成功写队后尝试获取 serializer lease（.ailocks/commit_serializer.lock，复用 _GlobalCommitLock 同款 TTL+僵尸 PID 检测模式），拿到即排空至空后释放；崩溃则下一个入队者/任意 status 调用续排空。**v0.4.0 补全 lease 算法**：lease 获取用 `os.open(O_CREAT|O_EXCL)` 原子创建（与 _GlobalCommitLock 同款）；TTL=300s（Serializer 排空一批通常 <30s，5 分钟足够）；超时 5s（自举模式不等待——拿不到就放弃，队列项留在 pending 等下次自举）；释放时 `os.remove`；崩溃时 TTL 过期 + 僵尸 PID 检测自动清理（与 _GlobalCommitLock 完全同款）。可选 P2 加 Windows 计划任务（schtasks 每 5 分钟 `drain --if-needed`）兜底——避开 65 号 v2.1.0 deprecated L19 常驻 daemon 的教训 |
| Serializer 崩溃 | 队列持久化在磁盘，重启/下一次自举从 processing/ 续跑。**幂等判定精确语义**：重放前先查 `git merge-base --is-ancestor <已落盘commit> dev` 或 done/ 记录——同一 qid 已落盘则直接 MarkDone；否则重新执行落盘（同快照同 message，若中间无新落盘则产生同内容 commit，update-ref CAS 保护不产生分叉） |
| 断电 | 同上；blob 已落盘即不丢 |
| 队列腐败 | append-only + 每项独立文件，fsck 可校验；死信永不自动清理（人工） |
| 审计 | commit message 附 `[GW:{session_id}:q-{qid}]` 标记，衔接既有 GW 审计体系（POST-COMMIT-GUARD 标记豁免与 reference-transaction guard [GW: 前缀豁免均兼容，已核对） |
| 防饥饿 | dead/ 超 N 项告警；队列深度超阈值告警——对接 55 号 §3.1 已施工设施（MetricsRegistry + alert_generator 三级告警）与 §3.3 阈值注册表（阈值入注册表，不硬编码） |
| read-tree 类隐形 index 重置 | **v0.3.0 新增**：Layer 3（plumbing 拦截）在 shell 层阻断 → Layer 2（worktree 隔离）兜底（即使拦不住，read-tree 只崩该 worktree 的 index，不碰共享 index）→ Layer 1（队列）第三层兜底（已入队快照不受 index 状态影响）。三层叠加根治 |

## 9. 不做什么（边界）

1. **不做跨会话自动语义合并**——两个会话改同一文件的语义冲突，一律死信回退给人/属主会话，不发明三路智能合并（内容级 merge-file 实测偏弱，§6.4，仅作尽力而为优化）。
2. **不替代编辑期文件锁**——.ailocks 继续管"别同时改同一文件"。
3. **不做优先级插队**（v0.1 纯 FIFO）——急单靠"先入队"纪律，不搞优先级反转防护。
4. **不删逃生通道**——gateway 逃生通道保留用于故障应急，但常态化使用会被审计点名（65 号口径不变）。（2026-08-13 更新：用户裁定口径反转——逃生通道改为 **AI 可默认使用 + GW 标记留痕 + trae_069 阈值监控兜底**，原"AI 不得自行使用/常态化点名"口径废止；overlap 类前置须按 [67 号](../../../01_policies_and_standards/sop/merge_conflict_resolution_sop.md)冲突三分法判定非互斥）
5. **不支持跨分支队列**（v0.1 仅 dev 主干单目标）。
6. **MVP 不做 temp-index 门禁 blob 化改造**——62 个读工作区内容的门禁适配是 P2 工程量评估对象，不进 MVP（§4 裁定 3）。
7. **不做主工作区内容同步/回滚**——Serializer 永不改主工作区文件；工作区与 HEAD 的收敛由"worktree 独立工作区 + 死信重新入队"机制覆盖（§6.4），不引入任何主工作区写操作。
8. **不把 commit-tree/update-ref 加入 DANGEROUS_SUBCOMMANDS**——这两个命令由 REFERENCE-TRANSACTION-GUARD 专管（基于 [GW: 标记的 ref 事务级拦截，比命令级更精准），且 emergency_commit.py 合法使用 commit-tree 需保留通道。加入 DANGEROUS_SUBCOMMANDS 会误伤合法逃生路径。

## 10. 施工分期

| 期 | 内容 | 验收（全部可自动化断言） |
|---|---|---|
| MVP（P0） | 队列目录协议 + enqueue/status/drain CLI + 入队自举排空 + 专用 worktree 落盘（复用 gateway 全门禁）+ 死信 + compaction + `_commit_auto` 改道入队 + **git_guard.py DANGEROUS_SUBCOMMANDS 扩展 4 个 plumbing 命令** + **install_git_safety_wrapper.ps1 落地（含 plumbing 拦截）** | 3 会话并发 50 提交：零丢失（done 数=有效入队数）、零搭便车（逐 commit `git show` 内容 == 入队快照 hash 比对）、FIFO 序（拓扑序 == qid 序）、死信正确归因；REFERENCE-TRANSACTION-GUARD 不拦队列 commit；**read-tree 在会话层被拦（exit 1 + 审计日志），在 Serializer worktree 内放行**；压测脚本见 §11 |
| P1 | 级联标记 + task_board 死信标签联动 + 死信重新入队 CLI + done/ TTL 清理 + **worktree 强制升硬（WORKTREE-REQUIRED gate THRESHOLD 概念废除——队列落地后会话不 commit，gate 只管 Serializer 专用 worktree 之外的会话直接 git 操作）** | 同键 3 连提交仅留最终态；死信取回重入队闭环演示；依赖级联标记正确；**会话层 git read-tree 被拦后会话改在自己 worktree 内执行不报错** |
| P2 | 落盘确认接入 55 号监控 + 防饥饿告警（阈值入注册表）+ temp-index plumbing 形态评估（含 62 门禁 blob 化工程量）+ 多目标分支支持评估 + schtasks 兜底排空 | 监控面板可见；告警触发演示；temp-index 形态做/不做裁定 |

**前置条件（2026-08-12 审查核验修正）**：

1. ~~`task_board.py`/`session_worktree.py`/`install_git_safety_wrapper.ps1` 三个 WIP 文件过门禁或移出暂存区~~ → **核验修正**：`task_board.py`/`session_worktree.py` 当前为 **untracked** 新文件（未入暂存区，不直接卡他人 commit；真实连坐机制是 WORKSPACE-CLEAN-CHECK 要求全仓无 WIP 导致 merge 永不可达 + 裸 commit stash 周期）；`install_git_safety_wrapper.ps1` **不存在**（65 号 §7.7 待施工项，疑在并发事故中 wipe）。MVP 开工前需确认这两份 untracked WIP 的归属会话将其入队/提交，避免长期悬空。
2. ~~WORKTREE-REQUIRED 升硬（_THRESHOLD 5→0）~~ → **核验修正**：`_THRESHOLD=5` 在 Layer-2 pre-commit hook（validate_worktree_required.py），gateway 路径 `--no-verify` 根本不经 Layer-2，5→0 对 gateway 路径零效果；Layer-1 in-process gate 已是"并发即阻断"无阈值概念。且队列落地后 WORKTREE-REQUIRED 对会话提交失去对象（会话不再 commit）。故此前置条件**撤销**，真正配套是 install_git_safety_wrapper.ps1 落地（拦裸 commit = stash 触发源清零 + plumbing 拦截，65 号 §7.7 P0 项）。

## 11. 验证方案

1. **并发压测**：新建 `tests/governance/test_commit_queue.py`（pytest，3 会话 fixture 并发入队 50 项；**不**复用 test_concurrent_safety.ps1——核验确认该脚本是 47 个治理脚本的原子写并发安全测试，不含 git commit 场景，仅借鉴其 Start-Job 并发模式）。断言清单：done 数 == 有效入队数；逐 commit 内容 hash == 入队快照 hash；拓扑序 == qid 序；dead 项归因正确；无 `[GW:*:overlap]` 标记混入。**v0.4.0 新增**：50 个 enqueue 操作本身不丢不重（pending 数 == 50，无 qid 碰撞）。
2. **故障注入**：drain 中途 kill → 下次自举续跑幂等（is-ancestor 判定不产生重复 commit）；工作区在施工中被 `git restore .` → 已入队项不受影响；reference-transaction guard 对 `[GW:*:q-*]` 标记放行、对无标记 plumbing 更新仍阻断（回归既有防护）。
3. **红队**：恶意/畸形入队项（路径穿越、超大 blob、空 message、.git 路径）全部被入队轻检拦下。**v0.3.0 新增**：会话层执行 `git read-tree HEAD` 被拦（exit 1 + 审计日志）；`ZEPHYR_SERIALIZER_MODE=1` 环境下放行；无该环境变量的会话执行 `git update-index` 被拦。
4. **门禁等价性抽查**：抽 5 个代表性门禁（DIRECTORY-CONTRACT / FOREIGN-CHANGE / encoding / naming / frontmatter）验证在专用 worktree 内对同一快照的判定与主工作区一致。
5. **三层防护穿透测试**（v0.3.0 新增）：Layer 3 被绕过（AI 用完整路径调用 git.exe 跳过 shell 函数）→ Layer 2 worktree 隔离兜底（read-tree 只崩该 worktree index）→ Layer 1 队列兜底（已入队快照不受 index 状态影响）。断言：三层任一层失效，其余层仍能保证数据不丢。
6. **worktree HEAD 同步测试**（v0.4.0 新增）：Serializer 连续处理 3 项（每项修改同一文件），断言每项处理前 worktree HEAD == 当前 dev HEAD（`git -C .aidrafts/serializer rev-parse HEAD` == `git rev-parse refs/heads/dev`）；断言 worktree 工作区在每项处理前为 clean（`git -C .aidrafts/serializer status --porcelain` 输出为空）。
7. **compaction 竞态测试**（v0.4.0 新增）：同一 session 连续 enqueue 同一文件 3 次（seq 0001/0002/0003），断言 pending 只留 0003（compaction 生效）；done/ 无中间态记录。

## 12. 开放问题

> **已闭环（v1.0.0 用户裁定）**：Q1 门禁出队端适配 → MVP 专用 worktree 形态、100 门禁零适配（temp-index 封存 P2）；Q2 `_commit_auto` 改道入队保住单写者不变量；Q3 单 blob 10MB 上限 / done 保留 7 天 TTL / dead 永不自动清理；Q4 无需"队列空窗才 merge"硬门禁（merge 消失，反向约束在 §6.6）；Q7 AGENTS.md §10"改完立即入队"铁律随本文 active 生效（已落地 §10.0）。

1. **GOV-BUDGET-002 注册表条目重登记** → **已闭环（2026-08-14）**：治理预算三纪律（I-GOV-3 v2）条目已重登记为 `#ARCH-GOV-BUDGET-002`，本文 frontmatter related_issues 引用已恢复 `#` 前缀。
2. **61 号 §3.6 / 65 号 §7.6 / ARCH-WORKTREE-GATE-001 口径联动**（待施工，裁定已确认）：用户已确认 worktree 强化方向。队列 MVP 验收通过后，由归属会话联动修订（61 号 §3.6 第 5 条改为"队列+worktree 双层"、65 号 §7.6 改为"worktree 强制（队列落地后可达）"、gate 代码注记同步），本文不越界改。

## 13. 修订记录

| 版本 | 日期 | 内容 |
|---|---|---|
| v0.1.0 | 2026-08-12 | 首版：23 会话事故链病根 → Outbox+MergeQueue+Compaction+DLQ 组装方案（plumbing 直写不碰工作区、门禁出队端执行、worktree 降级可选） |
| v0.2.0 | 2026-08-12 | 架构审查轮：新增 §2.4 设施盘点（15 项实证）；§6.3 修正树级回滚 bug（改从当前 HEAD 建树+CAS update-ref）；落盘形态改 MVP 专用 worktree、temp-index 降 P2；merge-file 实测偏弱降级；Serializer 改入队自举排空；前置条件核验修正；§12 新增 3 项 |
| v0.3.0 | 2026-08-12 | 三层防护修订（事故 6 read-tree 隐形重置 index 根治）：worktree 从"降级"反转为"第二层防护"；新增裁定 7（4 个 plumbing 命令入 DANGEROUS_SUBCOMMANDS + ZEPHYR_SERIALIZER_MODE 白名单）；§2/§3.3/§5/§7/§8/§9/§10/§11 同步扩展 |
| v0.4.0 | 2026-08-12 | 算法补全：7 处施工算法（enqueue 原子性/compaction 竞态/Serializer lease/worktree HEAD 同步/message 绝对路径等）；第二轮搜索实证 5 项（claude-fleet 三层同构/fak submit-drain 同构/AgenticFlict 27.67% 冲突率/VS Code 默认 worktree/Cursor 3.0 虚拟快照/agentlocks）；§11 新增测试 2 项 |
| v1.0.0 | 2026-08-12 | 用户确认全部 3 项裁定，文档升 active：①队列串行化为集成层唯一提交入口；②worktree 强化为第二层防护（队列消除 merge 障碍后升级为可达的强制）；③AGENTS.md §10 新建"改完立即入队"铁律（已落地 §10.0）。§12 Q1/Q2/Q3/Q4/Q7 裁定闭环，Q5/Q6 待施工 |
| v1.1.0 | 2026-08-14 | 文档实体精简（AI-GIT-001）：§2.1 事故链表化、§3.2 搜索实证摘要化、§12 已闭环开放问题折叠、§13 修订记录压缩；§4-§6/§8-§11 施工核心零改动；task_board.py 现状更新（wipe 丢失，按 §2.4 #9 schema 重建中） |
| v1.2.0 | 2026-08-17 | 结案报告追加 AI-FOPEN-001（B2 提交链路 PG 韧性三件套：pg_probe 前置探针 + FRESHNESS 离线 24h 豁免 + verify_schema_health exit 2 优雅化，fa25c19e49，merge 8a872d0e59+48ce3d93cb，#ARCH-119 resolved） |
