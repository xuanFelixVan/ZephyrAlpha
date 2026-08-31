---
ttl: permanent
doc_type: architecture_view
title: 多 AI 并发治理施工图
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.2.2"
date: 2026-08-17
topic: multi_ai_concurrency_governance
scope: 09_ai_architecture
---

# 多 AI 并发治理施工图

> ## 结案报告（2026-08-28 全量审查批，代码实证）
> **实际开发**：多 AI 并发治理三件套+提交队列落地——lock_files.py（TTL+Mutex 原子写）/task_board.py（三态机+CAS+死信）/session_worktree.py（四证 SOP+活性登记+心跳 daemon）；commit_queue.py（MOD-GOV-046 A 段：enqueue/status/drain+FIFO+死信+compaction）+commit_queue_landing.py（MOD-GOV-047 B 段：专用 worktree 真落盘+gateway 改道）；flags.yaml commit_queue_serializer enabled:true 已翻开（2026-08-22 Owner 裁定）；.runtime/commit_queue/ 运行中实证（done 74+ 项）。
> **最终成果**：61/65/66 号备忘核心机制全部落地，跨会话并发提交串行化生产启用。
> **未做+原因**：dead/ 积压 40+ 死信项未清理（运维观察项）；CLI drain 自举 stub landing 注记（生产排空只走 gateway 改道）。

> ## 结案补记（2026-08-31，死信清理闭环）
> **dead/ 积压死信已清零**：实测 31 条（非 40+，部分已被历史清理），全量分诊后核销——死因分布 PROTECTED-PATHS 21 / COMMIT_SCOPE 3 / SESSION-REQUIRED 2 / CLAIM_REQUIRED 2 / LOCK_TIMEOUT 2 / 基底冲突 1，**全部为门禁合法拦截记录而非系统故障丢单**；对应改动均已由属主会话后续成功提交落地（git log 实证：GOVTEST-003 三批 6ee5d0802a/86b37c6c38/8e97b6d1a6 及 08-31 各会话重试），核销零工作丢失。分诊审计留痕 `.runtime/commit_queue/dead_triage_20260831.jsonl`（31 条 qid+死因+处置结论），原死信文件已删除。**口径区分留痕**：66 号文 Q3 裁定"dead/ 永不**自动**清理"（无 TTL 机制）与本次人工分诊核销不冲突——本次属 08 号文挂账的"运维观察项"人工处置，且核销前置条件=逐条验证对应改动已由属主会话落地（无 requeue 需求）；requeue 场景的"原死信项只标注不删除"（66 号 §6.4 双向追溯）不受影响。**结论修正**：dead/ 积压本质是「门禁拦截副产物堆积」，反映 08-30 多会话高峰期 PROTECTED-PATHS 门禁被频繁触发（script_manifest.yaml 等受保护路径混入批次），非队列机制缺陷；后续观察项=若拦截率持续偏高应优化门禁提示引导会话先拆出受保护文件再入队。残余未做项仅剩 CLI drain 自举 stub landing 注记（生产排空走 gateway 改道，无实际影响）。

> 本文定位：61/65/66 号备忘的多 AI 并发治理方案施工落地——会话隔离、git 安全、提交队列串行化。
> 与其他文件的分工：结构设计见 [00_index.md](00_index.md)，设计备忘见 `design_memos/61/65/66`。
> **真源边界**：三起事故的事故链细节、方案调研论证、三层防护协议算法（入队 schema/compaction/Serializer 主循环/冲突判定）的**设计真源**在 [66_commit_queue_serialization.md](../../07_trading_decision_architecture/design_memos/66_commit_queue_serialization.md)；git 安全各防御层的施工细节真源在 [65_git_safety_governance.md](../../07_trading_decision_architecture/design_memos/65_git_safety_governance.md)；多 AI 协作纪律真源在 [61_lifecycle_multi_ai.md](../../07_trading_decision_architecture/design_memos/61_lifecycle_multi_ai.md) §3.6。本文不复制上述内容，只负责：①三件套的施工状态实测收口；②剩余缺口（提交队列 MVP 等）的施工排序与验收；③本主题在 AI 层架构中的定位与接口。

---

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | 多 AI 并发治理 |
| 所属 | [00_index.md](00_index.md) §1 目标架构·AI 治理层（横切） |
| 依赖 | 61 号备忘（生命周期多 AI）+ 65 号备忘（git 安全治理）+ 66 号备忘（提交队列串行化） |
| 优先级 | P1——多 AI 并发是当前施工方式的基础设施 |
| 状态 | draft（全文填充完成） |

---

## 2. 背景

### 2.1 项目处境

本项目的施工方式是「1 人在 TRAE 编译器上用多 AI 多对话并发施工」（system_charter §2 约束一）——同一时刻可有 20+ 个 AI 会话在同一仓库上并发读写。这不是理论假设，而是已发生三起实证事故的现实：

| 事故 | 日期 | 一句话 | 真源 |
|---|---|---|---|
| git clean 灾难 | 2026-08-11 | 并发 AI 会话执行 `git clean -fd` 物理删除多个 untracked 文件（不进回收站、从未 commit、git 无法恢复），20+ 篇文档增强内容丢失 | 65 号 §2.1 |
| 23 会话并发事故链 | 2026-08-12 | 23 个并发会话全部遭遇工作区互冲——stash 吞稿/restore 冲稿/共享 index 搭便车/门禁连坐/逃生通道常态化/`git read-tree` 隐形重置共享 index（事故 6） | 66 号 §2.1 |
| worktree wipe 事故 | 2026-08-14 | 三 worktree tracked 文件被物理清空，含未入 git 的 task_board.py | 65 号 §13 关联施工（裁定书 S1-S6） |

**病根（66 号 §2.2 第一性原理）**：共享工作区 + 共享 index = 单资源无调度竞争。文件锁只能保护「编辑期」同一文件不被两会话同时改，保护不了「提交期」git 状态机的互斥，更保护不了「杂项 git 操作期」（read-tree/update-index 等 plumbing 命令）对共享 index 的隐形破坏。三个攻击面需要三层防护。

**当前施工状态（2026-08-17 实测）**：三层防护中**两层半已落地**——
- ✅ **git 安全防护层**（65 号，v2.4.0）：wrapper 已激活、git_guard plumbing 扩展已落地、ops_guard 删除原语拦截已 production、审计/规则层齐备（详见 §2.4）。
- ✅ **会话隔离层**（65 号 §11 三件套 + 66 号第二层）：worktree 五命令、文件锁 TTL 八命令、task_board 全部 production；worktree 隔离强化（会话活性登记+心跳守护+四证清理 SOP）已落地。
- ❌ **提交队列层**（66 号第一层）：MVP 已施工并生产启用——scripts/commit_queue.py（MOD-GOV-046）+commit_queue_landing.py（MOD-GOV-047）在位，flag 已翻开（2026-08-22），.runtime/commit_queue/ 运行中（2026-08-28 实证回填）。当前提交期靠 `_GlobalCommitLock` 全局串行锁（git_commit_gateway.py 内，TTL=1800s）+ AGENTS.md §10.0 过渡期纪律（改完立即 `git_guard.py add`）维持。

本文档读者应能从 §2.4 一张表看清：这个主题在项目里有哪些设施、各自状态、缺口在哪。
### 2.2 核心问题

1. **Q1：66 号备忘的提交队列是否已施工？**——**已实测闭环：未施工**。66 号 2026-08-16 结案报告原文「commit queue（提交队列）本体未做——Serializer 串行器/死信/门禁外移为大工程量单项，MVP 待排期（遗留 #67 登记在案）」；磁盘实测 `scripts/commit_queue.py` 不存在、`.runtime/commit_queue/` 不存在。当前提交期保护 = `_GlobalCommitLock` 串行锁 + 过渡期 add 纪律，能防「同时 commit」，防不了「锁内 commit 读写共享工作区/index」导致的搭便车/staged 污染（66 号 §2.2）。**本文档 §4 的核心施工项就是该 MVP 的落地排序。**
2. **Q2：文件锁是否覆盖全部冲突场景？**——**不覆盖，且这是设计使然而非缺陷**。lock_files.py 管「编辑期」同文件互斥（acquire 前先 check 已是本指令集铁律）；「提交期」互斥由 `_GlobalCommitLock`+未来的队列管；「杂项 git 操作期」由 plumbing 拦截（git_guard `PLUMBING_BLOCKED_SUBCOMMANDS`）+ worktree 独立 index 管。三 attack surface × 三机制，无一多余（66 号 §5 三层架构）。
3. **过渡期纪律在当前 16 个填充 AI 并行施工下是否足够？**——基本足够但有已知缺口：文件锁+网关+worktree 三件套正承载当前施工（本文档的修改即经 lock_files.py acquire 保护）；已知缺口 = ①共享 index 搭便车风险仍在（靠「改完立即 add」纪律对冲）；②Trae AI RunCommand 终端不加载 `$PROFILE`，wrapper 仅覆盖人工交互终端，AI 通道防护依赖 git_guard 直接调用层+hook 层+规则层（tracker #58，65 号 v2.4.0 状态栏）。

### 2.3 约束条件

1. **平台约束**：100% Trae IDE 开发——不支持 PreToolUse hooks，AI 会话经 RunCommand（PowerShell 5.1）执行命令；AI 规则只能经 `.trae/rules/` 注入（65 号平台约束栏）。**且 Trae AI RunCommand 终端不加载 `$PROFILE`**——shell wrapper 管不到 AI 通道，这是与 Claude Code 等平台的本质差异。
2. **git 约束**：Windows git 2.48.1——**alias 无法覆盖内置命令是 git 官方设计行为**（65 号 §3.1 实证），`clean/reset/checkout/restore/stash/revert/mv` 全是内置命令，alias 拦截体系形同虚设；git 没有 pre-clean hook；故拦截只能落在 shell 函数层（人工终端）+ 直接调用层（git_guard，AI 通道纪律）+ hook 层（commit/ref 事务）。
3. **人力约束**：1 人全栈 + AI 协作者，无团队——不做 agent 编排系统（61 号 §2.3 已裁定：多 AI 协作 = 人调度多会话，非 agent 自治）；交接靠文档落盘，AI 间不直接通信（61 号 §3.6）。
4. **单机约束**：单机 PC 工作站，无集群——文件锁/SQLite WAL+CAS 足够，分布式锁/Raft/Redis 一律过度工程（65 号 §9）。
5. **运维约束**：单机无热备——无常驻 daemon 执念，提交队列采纳「入队自举排空」形态（66 号 §8：enqueue/status 成功写队后尝试拿 lease 排空，拿不到就放弃等下次自举），65 号备忘已裁定不采用常驻协调 daemon（单点故障+运维负担教训）。
6. **事故复原约束**：任何防护机制本身不能成为新的事故源——wrapper 采 fail-open（wrapper 出错放行+记录，65 号 §3.9 行业共识），网关采 fail-closed（commit 是状态机写操作，宁可阻断不可错写）。

### 2.4 已施工设施盘点

> 实测时间：2026-08-17。每一行均经 Test-Path/CLI/代码读取实际验证。状态含义：production=已落地运营；missing=磁盘不存在。

**A. 编辑期防护（三件套之文件锁 + 任务板）**

| 类别 | 路径/位置 | 内容简述 | 状态 |
|---|---|---|---|
| 文件锁 | `scripts/lock_files.py` | acquire/release/check/status/release-all/list/cleanup/guard-write 八命令 + `--ttl`（默认 1800s）+ Windows 全局命名 Mutex + tmp/flush/fsync/replace 原子写；`.ailocks/` 锁目录实测存在 | production（65 号 v2.4.0：`tests/git/test_lock_files_ttl_mutex.py` 9 用例实测存在） |
| 任务板 | `scripts/task_board.py` + `.runtime/task_board.db` | SQLite WAL + CAS 原子认领（8 线程恰一胜实测），三态状态机 pending→claimed→completed，metadata_json 可承载死信标签 | production（2026-08-14 重建 0e5ed3b9→d8f94d4f2b，17 测试全过；db 文件实测存在） |

**B. 提交期防护（网关 + 门禁 + hook 链）**

| 类别 | 路径/位置 | 内容简述 | 状态 |
|---|---|---|---|
| 提交网关 CLI | `scripts/git_commit.py` | 全项目唯一合法 commit 入口：`--session/--files/--message(-file)` + `--claim-only` 前移声明 + `--allow-overlap/--allow-non-worktree` 等逃生通道系列；裸 `git commit` 被 GATE-COMMIT-GW 阻断 | production |
| 网关执行体 | `src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py` | `_GlobalCommitLock` 全局跨进程串行锁（`.ailocks/git_commit_global.lock`，TTL=1800s，僵尸 PID 清理）+ stash 隔离 + GW 标记（commit message 附 `[GW:<session>]`） | production |
| 门禁簇 | `src/zephyr/gov_enforcement/commit_gates/`（实测 102 个 .py）+ `rule_bridge/commit_gate_registry.py` + `rule_bridge/gate_auto_registrar.py` | in-process 门禁（YAML 驱动自动注册）；其中 62 个文件含工作区内容读取（66 号 §2.4 #2 实证，temp-index 形态需 blob 喂入改造——MVP 选专用 worktree 形态的关键原因） | production |
| commit 兜底 hook | `scripts/governance/git_hooks/post_commit_guard.sh` | non-GW commit 自动 `git reset --soft HEAD~1` | production |
| ref 事务 hook | `scripts/governance/git_hooks/reference_transaction_guard.sh` | refs/heads/dev forward 更新的 message 不含 `[GW:` 子串即 block 回滚——plumbing ref 绕过已堵（git 2.45+ hook） | production |
| 合法逃生通道 | `src/zephyr/gov_enforcement/rule_bridge/emergency_commit.py` | commit-tree plumbing 直写逃生通道（落审计），与 REFERENCE-TRANSACTION-GUARD 豁免兼容 | production |
| 自动提交链 | `src/zephyr/gov_enforcement/rule_bridge/batched_auto_committer.py` | reconciler 派生文件自动提交（`_commit_auto` + reconcile_runner worker）——**现状 dev 第二写入者**，队列 MVP 落地时必须改道入队（66 号 §7），否则单写者不变量破裂 | production（待改道） |
| 不可变核心 | `config/immutable_core.yaml` | 受保护路径 commit 时检查 | production |
| 回滚工具 | `scripts/rollback.py` | 误提交回滚 | production |
**C. 杂项操作期防护（危险命令拦截 + 删除原语拦截）**

| 类别 | 路径/位置 | 内容简述 | 状态 |
|---|---|---|---|
| 危险命令拦截 | `scripts/git_guard.py` | `DANGEROUS_SUBCOMMANDS` = 7 porcelain（reset/checkout/stash/revert/restore/mv/clean）warn+审计；`PLUMBING_BLOCKED_SUBCOMMANDS` = 4 plumbing（read-tree/update-index/write-tree/hash-object）前置硬阻断+审计，`ZEPHYR_SERIALIZER_MODE=1` 白名单放行 Serializer | production（66 号裁定 7 已落地，16/16 测试全绿；事故 6 根因已治） |
| 删除原语拦截 | `scripts/ops_guard.py` | 全原语删除拦截层（wipe 治本 S1）：PowerShell/CMD/Python/git clean 四类删除原语，保护区 fail-closed，删除强制先落审计 | production（3e2bb5ed70，42 红队向量 100% 拦截） |
| shell wrapper | `scripts/git_safety_wrapper.ps1` + `install_git_safety_wrapper.ps1` + `ensure_ai_wrapper_injection.ps1` | PowerShell 函数覆盖 git 危险命令+plumbing 命令+删除类命令，`.git` 写入阻断，Session ID 注入，审计 JSONL；`$PROFILE` 单一 dot-source 真源已激活 | production（611227d5/21f447c1，45/45 测试全绿；**边界：仅覆盖人工交互终端，AI RunCommand 通道不加载 $PROFILE**，见 §6 Q5） |
| 规则层 | `.trae/rules/project_rules.md` RULE-GIT-SAFE 节（实测 line 361）+ `AGENTS.md` §10.0/§10.0.1 | Trae AI 规则入口：危险命令禁令、「改完立即入队」铁律（队列 MVP 前过渡期 = 改完立即 `git_guard.py add`）、plumbing 命令禁止（commit-tree/update-ref 由 REFERENCE-TRANSACTION-GUARD 专管除外） | production（66 号 v1.0.0 已落地） |

**D. 会话隔离（三件套之 worktree + 活性强化）**

| 类别 | 路径/位置 | 内容简述 | 状态 |
|---|---|---|---|
| worktree CLI | `scripts/session_worktree.py` | 五命令：create/exec/merge/abort/list；目录 `.worktrees/<AI-ID>/`（实测当前 29 个活跃 worktree），独立分支 `ai/<session-id>/<task-id>`；merge 必须用户显式确认 | production |
| worktree 执行体 | `src/zephyr/gov_enforcement/rule_bridge/`：`session_worktree.py`、`worktree_manager.py`、`worktree_pool.py`、`worktree_lifecycle.py` | worktree 创建/池化/生命周期管理；`.aidrafts/` 隔离区 | production |
| 会话活性 | `rule_bridge/session_claim.py` + `heartbeat_daemon.py` | 会话活性登记 + 心跳守护（66 号第二层强化：防「死会话持锁/持 worktree」） | production |
| 漂移看门狗 | `rule_bridge/worktree_drift_watchdog.py` | worktree 漂移监控 | production |
| 四证清理 SOP | `docs/01_policies_and_standards/sop/worktree_cleanup_sop.md` | worktree 清理四证流程（wipe 治本 S2，首次真实清理走通：refs/quarantine + bundle 双存证） | active |
| 冲突裁决 SOP | `docs/01_policies_and_standards/sop/merge_conflict_resolution_sop.md` | 67 号冲突三分法（overlap 类前置判定非互斥才可用逃生通道） | active |
| 并发压测 | `scripts/governance/test_concurrent_safety.ps1` | 47 个治理脚本原子写并发安全压测（借鉴其 Start-Job 并发模式，队列压测需新建） | production |

**E. 未施工缺口**

| 类别 | 路径/位置 | 内容简述 | 状态 |
|---|---|---|---|
| 提交队列 | `scripts/commit_queue.py`（enqueue/status/drain CLI）+ `.runtime/commit_queue/`（pending/processing/done/dead/blobs） | 66 号第一层：快照入队即返回 + Serializer 单写者按序落盘 + 死信不卡队 | **missing（遗留 #67，本文 §4.2 施工）** |

---

## 3. 设计决策

### 3.1 会话隔离设计：worktree 物理隔离 vs 纯 session 逻辑隔离 why

**决策**：会话隔离以 git worktree 物理隔离为主、文件锁逻辑隔离为辅，两层叠加；不追求「全会话强制 worktree」的一刀切，而是「并发即阻断」的门禁触发式强制。

**理由**：
1. **共享 index 是病根，逻辑隔离治不了**。66 号事故 6 实证：`git read-tree HEAD` 在主仓执行直接把共享 index 重置为 HEAD，所有会话的 staged 元数据被清空——该命令不在任何护栏管辖范围。每个 worktree 有独立 checkout + 独立 index，read-tree 在某 worktree 内只崩该 worktree，不碰共享状态。这是纯 session 逻辑隔离（锁+纪律）无法提供的物理边界。
2. **worktree 的价值曾被误判、后被事故反转**。66 号 v0.2.0 曾裁定「worktree 降级为可选」（理由：merge 仍是竞争点，WORKSPACE-CLEAN-CHECK 要求全仓无 WIP，23 会话下永不可 merge）；v0.3.0 被事故 6 推翻反转为「第二层防护」——且队列落地后 Serializer 直提 dev、merge 操作消失，worktree 的最大障碍自动解除（66 号 §3.3 ②、§4 裁定 5）。**这个反转史说明：隔离层的价值不取决于提交期，取决于杂项操作期的爆炸半径。**
3. **人调度多会话不是 agent 编排**。61 号 §2.3 已裁定不做 agent 编排系统；worktree 的 merge 必须用户显式确认（65 号 §11.2.1）——物理隔离 + 人工裁决合并，正好匹配「人调度」模式，不需要自动合并 agent。
4. **2026 行业背书**：VS Code 2026-08-07 起默认为 agent session 启用 git worktree 隔离，「并发 agent 未提交修改被静默覆盖」是 2026-08 行业公认失败模式（66 号 §3.2；61 号 §3.6 引 CMU CAID 实证 branch-and-merge + worktree 是多 agent 协作核心协调机制）。

**考虑过的替代方案**：

| 替代方案 | 否决理由 |
|---|---|
| 纯文件锁逻辑隔离（无 worktree） | 锁只管编辑期同文件互斥，管不到共享 index/工作区的提交期与杂项操作期（66 号 §2.3 失效点表） |
| 全会话强制 worktree（THRESHOLD→0） | 队列未落地前 merge 不可达，强制=形同虚设；正确顺序是队列先行消除 merge，worktree 强制才可达（66 号 §3.3 ⑦） |
| 每会话独立 clone | 对象库重复 N 份、depgraph/注册表路径漂移；worktree 共享对象库天然规避 |
| 沙箱/容器隔离 | 61 号 §3.2 BM-RES-01-C + 65 号 §9 已裁定：Windows 无 Seatbelt 等效物，Docker/WSL 对个人量化开发过重 |
### 3.2 git 安全设计：预防→检测→恢复三层闭环 why

**决策**：git 安全按「预防（拦得住）→检测（看得见）→恢复（救得回）」三层闭环组织；拦截层接受「分通道差异化覆盖」——人工终端靠 shell wrapper，AI 通道靠 git_guard 直接调用层+hook 层+规则层，不追求单一机制全通道覆盖。

**理由**：
1. **单一拦截层必失效，且失效方式已被实证**。65 号 §2.2 双重失效：git_guard 代码漏洞（clean 无处理逻辑）+ git alias 机制失效（内置命令不可覆盖）——两层同时破才酿成灾难。v2.x 的结论是分层：wrapper（L1 shell 函数）→ git_guard 直接调用层（L2）→ 规则层（L3 `.trae/rules`+AGENTS.md）→ `.git` 阻断（L4）→ 审计（L5）→ Session ID（L6）（65 号 §13 Phase 1 六项施工）。
2. **分通道覆盖是平台约束下的务实解，不是缺口**。65 号 v2.4.0 状态栏新边界发现：Trae AI RunCommand 终端不加载 `$PROFILE`，wrapper 仅覆盖人工交互终端。AI 通道的等价防护 = git_guard（AI 纪律要求所有 git 命令经 git_guard 调用，plumbing 4 命令硬阻断）+ REFERENCE-TRANSACTION-GUARD（ref 事务级）+ post-commit guard + `.trae/rules` 规则层。追求 wrapper 注入 AI 通道（如 #68 计划任务快照注入，`ensure_ai_wrapper_injection.ps1` 已存在）是增强项而非必须项（见 §6 Q5）。
3. **检测层（审计）是单人项目的事后法庭**。审计 JSONL 双记录 + Session ID 注入 + GW 标记（`[GW:<session>]`）使每次 commit/危险命令可归因到具体会话——多 AI 并发出事故时，没有归因就没有复盘，没有复盘就没有第三轮防护迭代（66 号三层架构正是 8-12 事故复盘的产物）。
4. **恢复层是最后一道**：ops_guard 删除强制先落审计（删除前快照）、worktree 四证清理 SOP（refs/quarantine + bundle 双存证）、rollback.py、备份脚本。wipe 事故证明「拦住」之外必须有「救回」——42 红队向量 100% 拦截也不能保证第 43 种原语不存在。
5. **fail-open vs fail-closed 的分野**：wrapper 出错放行+记录（fail-open，拦错比漏拦更伤害施工体验，65 号 §3.9 行业共识）；网关/门禁 fail-closed（commit 是写操作，宁阻断勿错写）；删除原语在保护区 fail-closed（物理删除不可逆）。三种语义按操作可逆性分配，不是一刀切。

**多 LLM 交叉审查强制策略（AI 生成代码的供应链层防线）**：system_charter §2 约束六要求 AI 生成代码交叉验证+依赖锁定+自治熔断；26-D-SECURITY 草稿 §8.2.3 将其落成强制阈值——100% AI 生成代码必须经至少 2 个独立 LLM 交叉审查，关键安全代码（加密/认证/权限）必须 3 个 LLM 交叉审查，审查结果写入审计链。本项目审查栈 = GLM-5.1 + DeepSeek V4 Pro + Claude（治理架构草稿 §3.1 多 AI 交叉验证栈）。24-D-SECURITY 侧执行承载 = SEC-001 AISGGate（所有 AI 生成代码/指令必须经 AISG 验证后才能执行，fail-closed）+ SEC-006 SupplyChainSecurity（L0 供应链层：SHA-256 校验/SBOM/依赖锁定）。与本节三层闭环的关系：交叉审查属「预防」层，在代码进入仓库前拦截单模型幻觉与漏洞模式，与 commit 期门禁链（拦错误落盘）前后相续、互不替代。

**Agent 制品门禁（CI/CD）**：Agent 系统制品不止代码——25-D-INFRA-OPS 草稿 §16.4（搬入自 Agent 架构 A7）定义三类 Agent 特有制品阶段：Prompt 模板测试（输出格式校验+边界输入测试）、模型基准评估（基准数据集评估+延迟测试）、技能声明验证（依赖完整性+自治边界合规）。质量门禁阈值：Prompt 输出合规率 ≥95%、Agent 自治边界测试 0 违规、A2A 协议兼容性 100%、LLM 基准评估不劣于基线（仅紧急修复可豁免且须事后补测）、代码覆盖率 ≥80%、安全扫描 0 高危。部署策略：新 Agent 上线走影子模式（接收相同输入但不执行、不影响生产流量），Prompt/模型变更走金丝雀 10% 流量验证，Agent 代码变更走蓝绿秒级切换。与本主题的接口：多 AI 并发施工产出的 Prompt/技能声明变更同样经此门禁——制品级门禁与代码级 commit 门禁链两层互补。

### 3.3 提交队列设计：串行化机制与冲突解决策略 why

**决策**：采纳 66 号三层防护第一层——提交队列串行化作为集成层唯一提交入口：会话提交 = 快照入队即返回；落盘由单写者 Serializer 按序完成。落盘形态 MVP 用专用 worktree 复用现有门禁链，temp-index plumbing 直写降为 P2 优化。

**理由**：
1. **串行化 ≠ 解耦，现状锁已证明不够**。`_GlobalCommitLock` 已串行化 commit 临界区，但锁内 commit 仍读写共享工作区/index——搭便车、staged 污染、门禁连坐、pre-commit stash 四类病灶一个不少；锁等待超时（默认 60s）在 23 会话下演化为 LOCK_TIMEOUT 风暴（66 号 §2.2）。队列的真实增量是「快照落袋 + 门禁外移 + 调用方免等待」，不是串行化本身（66 号 §2.4 #1）。
2. **方案是组装不是发明**（66 号 §3.1）：快照入队即完成 = Transactional Outbox；后台单程序按序落盘 = Merge Queue（GitHub/Rust Bors/Chromium Commit Queue，CI/CD 主干保护标准答案）；单写者定序 = LMAX Disruptor（量化交易 OMS 日志定序同款）；同键覆盖 = Kafka Log Compaction；冲突打标签跳过 = Dead-Letter Queue。2026 实证：fak commit-lane submit/drain 同构、claude-fleet 三层同构、AgenticFlict 论文 27.67% AI PR 冲突率、tenki.cloud 称 merge queue 对 agent 级提交量「近乎必选」（66 号 §3.2）。
3. **MVP 专用 worktree 而非 temp-index 的取舍**：66 号 §4 裁定 3 实测修正——①temp-index「从 base_head 建树」实测为树级回滚 bug（中间 commit 的文件在新树中静默消失）；②66 号裁定 3 实测：in-process 门禁中 62 个直接读工作区文件内容（门禁簇当前实测 102 个 .py），temp-index 无工作区形态需逐门 blob 喂入改造，远超 MVP 预算。专用 worktree 形态下快照落成真实文件，102 门禁零适配、reconciler 链/post-commit 审计/reference-transaction guard 全部自然生效。**这是「复用现有门禁链」压倒「不落文件的优雅」的典型案例。**
4. **冲突解决策略：快进判定 + 死信，不发明智能合并**。逐文件比较 `base_blob` 与当前 HEAD blob——一致则快进；`git merge-file` 三方合并实测偏弱（相邻行编辑/双端 EOF 追加均判冲突，而注册表类热点文件最常见并发形态恰是同区域追加），故内容级自动合并降级为尽力而为，主恢复路径 = 死信 + 属主重新入队（66 号 §6.4）。语义冲突一律回退给人——与「AI 间不直接通信、交接落盘」纪律一致。
5. **入队自举排空避开常驻 daemon**。Serializer 无常驻进程：enqueue/status 成功写队后尝试拿 lease（复用 _GlobalCommitLock 同款 TTL+僵尸 PID 检测），拿到即排空，拿不到放弃等下次自举；崩溃则下一个入队者续排空。65 号备忘已裁定不采用 Named Pipe/常驻协调 daemon（单点故障+运维负担）。

**考虑过的替代方案**（66 号 §3.3 已逐项排除，本文不翻案）：

| 替代方案 | 否决理由 |
|---|---|
| 只做强全局互斥锁（加大超时） | 锁内 commit 仍读写共享工作区/index，四类病灶依旧 |
| 只做 worktree 不做队列 | worktree 解决编辑期+杂项操作，提交期 merge 仍竞争；且 WORKSPACE-CLEAN-CHECK 使 merge 不可达——必须队列先行 |
| 常驻协调 daemon | 65 号备忘已裁定不采用：单点故障+运维负担 |
| 先恢复「改完立即 add」纪律+现状不变 | 8-12 实证 add 快照在多会话 stash 周期下不保险；纪律补丁不改变共享状态模型的数学必然性 |

### 3.4 三攻击面 × 三防护层的映射关系 why

**决策**：按攻击面分配防护机制，不接受「一个机制包打全场」：

| 攻击面 | 病根 | 主防护 | 兜底 |
|---|---|---|---|
| 编辑期（文件读写） | 共享工作区，两会话改同一文件 | 文件锁 lock_files.py（锁先纪律）+ worktree 独立工作区 | 任务板认领前置（减少同文件认领） |
| 提交期（commit/add） | 共享 index + 共享工作区 | 提交队列（快照落袋+单写者，未施工）→ 过渡期：网关 `_GlobalCommitLock` + 改完立即 add 铁律 | post-commit guard + reference-transaction guard |
| 杂项 git 操作（read-tree 等 plumbing） | 共享 index 被隐形重置 | plumbing 拦截（git_guard 硬阻断 + wrapper shell 层） | worktree 独立 index（只崩自己）+ 队列快照（已落袋不受 index 影响） |

**理由**：66 号事故链的 6 起事故分别落在三个面上，任何只盖一面的方案都会留重演路径；三层叠加的不变量是「任一层失效，其余层仍保数据不丢」（66 号 §11 穿透测试口径）。

### 3.5 蓝图-代码-文档三方对齐机制（部署前强制检查）why

**决策**：三方对齐采「部署前强制检查」而非「定期巡检」——蓝图定义「系统应该是什么样」，代码定义「系统实际是什么样」，文档定义「系统被描述成什么样」，三者不一致即漂移；每次变更部署前强制完成一致性验证，不一致即阻断（治理架构草稿 HB-GOV-03）。

**机制构成**（真源：治理架构草稿 §6）：

1. **声明式基线唯一真源**：所有架构决策以 YAML/JSON 声明式定义，蓝图中每个组件/接口/约束都有对应声明式定义文件，作为三方对齐基准。
2. **SHA-256 哈希校验**：关键代码文件（核心模块入口/配置文件/接口定义文件）计算 SHA-256，与蓝图记录对比，不一致即触发架构漂移告警。
3. **git diff 增量检查**：仅对变更文件执行对齐检查而非全量扫描，部署前检查延迟 ≤5 分钟。
4. **CI/CD 部署门禁**：部署前自动执行三方对齐检查，不一致即阻断，结果记入审计日志。

**6 维校验规则**：

| 校验维度 | 校验方法 | 不一致处理 |
|---|---|---|
| 组件存在性 | 蓝图组件清单 vs 代码模块清单 | 缺失组件=部署阻断 |
| 接口契约 | 架构契约定义 vs 代码接口签名 | 契约不一致=部署阻断 |
| 配置一致性 | 声明式配置 vs 运行时实际配置 | 偏差>10%=漂移告警 |
| 文档完整性 | 代码公共接口 vs API 文档覆盖 | 覆盖率<100%=警告 |
| 依赖方向 | 代码 import 关系 vs 架构分层约束 | 违反分层=提交阻断（INV-008）|
| 数据血缘 | 因子计算逻辑 vs 因子文档定义 | 定义不一致=因子下线 |

**与本主题的关系**：三方对齐管「变更内容正确性」（部署门禁），提交队列/网关管「变更过程安全性」（提交门禁）——两者正交：队列保证多 AI 并发提交不互踩（§3.3），三方对齐保证单次部署内容不漂移；其中依赖方向 INV-008 的提交阻断落在 commit 期门禁链职责内。

### 3.6 Prompt 生命周期管理与决策疲劳检测（GOV-005/GOV-003）why

**决策**：Prompt 与 AI 协作规则按「宪法级资产」治理，归 27-D-GOVERNANCE 草稿 §1.1 GOV-005 ConstitutionalGuard 职责集——AI 代码标准执行 + 宪法更新审批 + Vibe Coding 治理 + Prompt 生命周期 + AI 自诊断监督；决策质量监控取 GOV-003 职责集内的决策疲劳检测一项。

**已施工映射（2026-08-17 实测）**：

- Prompt 生命周期：`src/zephyr/governance/context_governance/prompt_lifecycle.py`（实测存在）
- 决策疲劳检测：`src/zephyr/governance/resilience_governance/decision_fatigue.py` + `decision_fatigue_cli.py`（实测存在）
- Vibe Coding 执行器：`src/zephyr/gov_enforcement/behavioral_admission/vibe_coding_enforcer.py`（实测存在）

**边界附注（与 00_index v0.4.0 裁定的关系）**：00_index v0.4.0 已裁定移除「决策溯源链 DAG」（连同 zkCA 零知识审计/AI 伦理声明，属 A6 AI 合规过度工程，不适用个人项目）。决策疲劳检测 ≠ 溯源 DAG——疲劳检测监控「1 人长时间审批 AI 产出导致决策质量下降」，不构建决策因果图数据库；本文档不复活已移除项。

**与本主题的关系**：多 AI 并发施工下 Prompt 是会话间交接的隐性契约——Prompt 变更不经生命周期治理，各会话按各自版本施工，产出漂移无法归因；决策疲劳检测对冲单人审批瓶颈（1 人裁决 20+ 会话产出的质量风险）。

### 3.7 AI 施工门禁（AIConstructionGovernor / VibeCodingGovernance）why

**决策**：AI 改代码行为本身纳入门禁治理，防「AI 反复改代码的错误传播」（01-跨域交叉点与因果链草稿 §3 D-GOVERNANCE 段）。

**机制构成**（真源：29-D-GOVERNANCE 草稿子模块表 + 01-跨域交叉点草稿 §3）：

- **D-GOVERNANCE-15 AIConstructionGovernor**（P0）：公式 Hash 门禁 + 值域偏差检测 + 回归截断——AI 改代码后自动回归对比，偏差>阈值即截断阻止传播（深度 6 错误传播防御工事）；兼变更时段门禁（HC-01/HC-02 交易时段核心进程不可自动重启/依赖库不可自动升级，HC-04 保命轨触发放行全自动，HC-05 强制灰度发布）。**建设状态两源矛盾，见 §6 Q7。**
- **D-GOVERNANCE-14 VibeCodingGovernance**：Session 治理——Session 状态机 + 门禁检查 + 零残留（OPS-VC-* 体系）；仓内实测承载 `vibe_coding_enforcer.py`（§3.6）。

**与本主题的关系**：§3.1~§3.4 管「多 AI 并发不互踩」（空间维度），本节管「单会话多轮修改不传播错误」（因果维度）——回归截断防同一会话内误差累积，与文件锁/提交队列正交互补。

---

## 4. 施工计划

### 4.1 施工总览与排序 why

三件套中会话隔离层与 git 安全层已 production（§2.4），唯一缺口是提交队列 MVP（§2.4 E，遗留 #67）。施工排序 = **队列 MVP 先行**，其余两层转入维护与联动：

1. **队列 MVP 是解锁项而非普通缺口**。66 号 §4 裁定 5 的链条：队列落地 → Serializer 直提 dev → merge 操作消失 → WORKSPACE-CLEAN-CHECK 对象消失 → worktree 强制从「23 会话下不可达」变「可达」。不先做队列，会话隔离层的升硬永不可达。
2. **`_commit_auto` 改道必须随 MVP 同批完成**（66 号 §7）：reconciler 自动提交链是 dev 第二写入者，MVP 落地而不改道 = 单写者不变量当场破裂。
3. **git 安全层无 P0 缺口**，只剩增强项（§6 Q5），不占主线。

### 4.2 Phase 0：提交队列 MVP（P0，唯一未施工项）

> 协议/schema/算法真源在 66 号 §6（入队 schema / compaction / Serializer 主循环 / 冲突判定），本节只排施工顺序与验收口径，不复制协议内容。

| # | 步骤 | 要点 | 验收 |
|---|---|---|---|
| 0 | **depgraph 设计态登记** | 用 `scripts/governance/apply_depgraph.py` 将 `scripts/commit_queue.py` + `.runtime/commit_queue/` 的依赖关系登记为 status=planned（先登记后施工） | depgraph 查询可见 planned 条目 |
| 1 | 队列目录协议 + CLI | `scripts/commit_queue.py`：enqueue/status/drain 三命令；`.runtime/commit_queue/`（pending/processing/done/dead/blobs）；入队轻检（路径穿越/超大 blob/空 message/.git 路径拦截） | 红队畸形入队项全拦（66 号 §11 #3） |
| 2 | Serializer 入队自举排空 | lease 复用 `_GlobalCommitLock` 同款 TTL+僵尸 PID 检测；无常驻进程；崩溃由下一个入队者续排空 | 故障注入：drain 中途 kill → 下次自举幂等续跑（66 号 §11 #2） |
| 3 | 专用 worktree 落盘 | 快照落成真实文件 → GitCommitGateway 全门禁链零适配执行；`[GW:{sid}:q-{qid}]` 标记兼容 POST-COMMIT-GUARD 与 REFERENCE-TRANSACTION-GUARD | 门禁等价性抽查 5 门（66 号 §11 #4）；ref 事务 hook 不拦队列 commit |
| 4 | 死信 + compaction | 同键（session_id, path）整体覆盖；失败项死信不卡队 + task_board 打标签；依赖级联标记 | compaction 竞态测试（66 号 §11 #7） |
| 5 | `_commit_auto` 改道入队 | batched_auto_committer 内部 reroute 到 enqueue（一处改动，66 号 §7） | dev 全历史只剩 Serializer 通道写入（单写者不变量断言） |
| 6 | **depgraph 转 production** | 全部验证通过后 status planned→production | 66 号 §10 MVP 行全量验收：3 会话并发 50 提交零丢失/零搭便车/FIFO 序/死信正确归因 |

**验证设施**：新建 `tests/governance/test_commit_queue.py`（pytest 3 会话 fixture 并发 50 项；不复用 `test_concurrent_safety.ps1`，仅借鉴其 Start-Job 并发模式——66 号 §11 #1）。全量断言清单以 66 号 §10 MVP 行 + §11 七项测试为真源。

**过渡期纪律（MVP 落地前维持不变）**：改完立即 `python scripts/git_guard.py add <file>`（AGENTS.md §10.0）；本文档自身的提交即走 GitCommitGateway 通道。

### 4.3 Phase 1：队列联动与隔离层升硬（P1）

| 步骤 | 要点 | 验收 |
|---|---|---|
| 级联标记 + 死信重新入队 CLI + done/ TTL 清理 | 66 号 §10 P1 行 | 同键 3 连提交仅留最终态；死信取回重入队闭环演示；依赖级联标记正确 |
| task_board 死信标签联动 | metadata_json 承载，无需改表（66 号 §7） | task_board 可见各会话队列深度 |
| worktree 强制升硬联动 | 队列验收后由归属会话联动修订 61 号 §3.6 / 65 号 §7.6 / ARCH-WORKTREE-GATE-001 口径（66 号 §12 #2）——**本文只登记不执行**，见 §6 Q2 | 联动修订落盘 |

### 4.4 Phase 2：优化与可观测（P2，含远期评估项）

- 落盘确认接入 55 号监控设施（MetricsRegistry + alert_generator 三级告警）+ 防饥饿告警（阈值入注册表，不硬编码——66 号 §8）。
- temp-index plumbing 形态评估（含 62 门禁 blob 化工程量评估）——评估≠施工承诺，裁定见 §6 Q4。
- schtasks 每 5 分钟 `drain --if-needed` 兜底排空（可选项，66 号 §8）。
- 多目标分支支持评估（队列 v0.1 仅 dev 单目标，66 号 §9.5）。

### 4.5 与 00_index 及相邻文档的接口

- **在 AI 层架构中的位置**：本主题为 [00_index.md](00_index.md) §1 治理层（横切）设施，本文档从其 §5.2 目录树可达。
- **对 16 号文（AI 安全+运维）**：git 安全审计 JSONL、队列死信/深度告警、GW 标记审计链是 16 号运维闭环 Detect 环节的事件输入候选——16 号文填充中，接口假设见 §6 Q3。
- **对交易决策侧 61/65/66 号备忘**：本施工计划与三备忘逐项对齐（§4.2 ↔ 66 号 §10 MVP；§4.3 ↔ 66 号 §10 P1 + §12 #2；§4.4 ↔ 66 号 §10 P2），引用只读不改。

---

## 5. 不做什么

1. **不做 agent 编排系统**——61 号 §2.3 已裁定：多 AI 协作 = 人调度多会话，非 agent 自治；worktree merge 必须用户显式确认，不建自动合并 agent。
2. **不做分布式锁/Raft/Redis 协调**——单机约束下文件锁（Windows 全局命名 Mutex）+ SQLite WAL+CAS 足够（65 号 §9）；集群级协调机制一律过度工程。
3. **不追求单一机制全通道覆盖**——alias 无法覆盖 git 内置命令是官方设计行为（65 号 §3.1 实证）；拦截只落在 shell 函数层（人工终端）+ git_guard 直接调用层（AI 通道）+ hook 事务层，分通道差异化覆盖即终态。
4. **不做常驻协调 daemon**——Serializer 采入队自举排空（66 号 §8）；65 号备忘已裁定不采用常驻 daemon（单点故障+运维负担）。
5. **不做跨会话自动语义合并**——语义冲突一律死信回退给人/属主会话（66 号 §9.1）；`git merge-file` 三方合并实测偏弱，仅作尽力而为，不作主恢复路径。
6. **不做优先级插队**——纯 FIFO（66 号 §9.3），急单靠「先入队」纪律。
7. **MVP 不做 temp-index 门禁 blob 化改造**——62 个读工作区内容门禁的适配是 P2 评估对象（66 号 §9.6）。
8. **不做主工作区内容同步/回滚**——Serializer 永不改主工作区文件（66 号 §9.7）。
9. **不支持跨分支队列**——v0.1 仅 dev 主干单目标（66 号 §9.5）。
10. **不把 commit-tree/update-ref 加入 DANGEROUS_SUBCOMMANDS**——二者由 REFERENCE-TRANSACTION-GUARD 专管，emergency_commit.py 合法逃生路径必须保留（66 号 §9.8）。
11. **不做双写者并行过渡态**——`_commit_auto` 改道与 MVP 同批完成，不接受「队列 + reconciler 直提并存」（单写者不变量不接受例外）。

---

## 6. 开放问题

| # | 问题 | 现状 | 处置 |
|---|---|---|---|
| Q1 | 提交队列 MVP 排期（遗留 #67）：与 18 篇文档填充、其他施工线的相对优先级 | MVP 未施工；过渡期靠 `_GlobalCommitLock` 串行锁 + 「改完立即 add」纪律维持（§2.2 Q1/Q3） | **待用户裁定** |
| Q2 | 61 号 §3.6 / 65 号 §7.6 / ARCH-WORKTREE-GATE-001 口径联动修订（worktree 从「并发即阻断的门禁触发式强制」升级为「队列落地后可达的强制」） | 66 号 §12 #2 方向已确认，需队列 MVP 验收后由归属会话执行 | 待 MVP 验收；本文只登记，不越界改 |
| Q3 | 与 16 号文的事件接口：git 安全审计 JSONL / 队列死信与深度告警 / GW 审计链以何种格式流入 16 号 AI 安全运维闭环 | 16 号文 v0.1.0 填充中（并行施工）；**本文接口假设** = 上述三类事件为其 Detect 环节输入 | 待 16 号填充后双向对齐 |
| Q4 | temp-index plumbing 形态 P2 评估的触发条件，及 62 门禁 blob 化工程量归属 | 66 号 §9.6 列为 P2 评估对象；评估≠施工承诺 | **待用户裁定** |
| Q5 | AI RunCommand 通道 wrapper 注入增强（计划任务快照注入；`scripts/ensure_ai_wrapper_injection.ps1` 已存在）是否排期 | 65 号 tracker #58 已闭环——git_guard 直接调用层 + hook 层 + 规则层已构成 AI 通道等价防护；快照注入为增强项非必须项（§3.2 理由 2） | **待用户裁定** |
| Q6 | 队列落地后 WORKSPACE-CLEAN-CHECK 的退役登记：66 号 §7 口径为「对象消失自然退役，无需删代码」，是否需在规范/注册表侧显式登记退役状态 | 未登记 | 待 MVP 验收后一并裁定 |
| Q7 | D-GOVERNANCE-15 AIConstructionGovernor 建设状态两源矛盾：01-跨域交叉点草稿 §3 标 ✅ 已建，29-D-GOVERNANCE 草稿子模块表标 ❌ P0 未建；仓内 Grep 未检索到 AIConstructionGovernor/公式Hash/回归截断/值域偏差实现 | 草稿源互相矛盾，仓内未实测到对应模块 | 待用户裁定（以哪份草稿为准、是否排期施工） |

---

## 修订记录

| 日期 | 版本 | 变更 | 原因 |
|------|------|------|------|
| 2026-08-17 | 0.1.0 | 骨架建立（frontmatter + 空节模板） | AI 架构 18 篇施工图批量建档 |
| 2026-08-17 | 0.2.0 | 填充 §1 主题组信息 + §2 背景（含已施工设施盘点实测）+ §3 设计决策 | AI-FILL-08 第一轮填充（会话中途中断） |
| 2026-08-17 | 0.2.1 | 续写补完 §4 施工计划（Phase 0→2，队列 MVP 为唯一 P0 缺口，含 depgraph planned→production 登记步骤）+ §5 不做什么 + §6 开放问题（Q1~Q6）+ 补建修订记录；红蓝对抗修正 4 处实测偏差：文件锁命令数（五/六→八，实测 status/check/acquire/release/release-all/list/cleanup/guard-write）、门禁注册表两文件路径限定 rule_bridge/、62 门禁读工作区数字归因 66 号实测、3 处过渡表述改为当前值断言（PURE-ASSERTION 门禁） | AI-FILL-08 续写补完 |
| 2026-08-17 | 0.2.2 | §3 回填五项：§3.2 补「多 LLM 交叉审查强制策略」（26-D-SECURITY §8.2.3 + 24-D-SECURITY SEC-001/006）与「Agent 制品门禁」（25-D-INFRA-OPS §16.4）；新增 §3.5 三方对齐部署前强制检查（治理架构 §6）、§3.6 Prompt 生命周期与决策疲劳检测（27-D-GOVERNANCE GOV-005/GOV-003，附 00_index v0.4.0 移除溯源 DAG 边界注）、§3.7 AI 施工门禁（D-GOVERNANCE-15/14）；§6 新增 Q7（D-GOV-15 建设状态两源矛盾）；prompt_lifecycle/decision_fatigue/vibe_coding_enforcer 路径均实测 | AI-FILL-08-R2 草稿源回填 |

---

*维护者：AI 架构协调者*