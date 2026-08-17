---
ttl: permanent
doc_type: architecture_view
title: Git 安全治理体系——alias 失效修复与多层防护施工总案（Trae IDE 专用）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "2.5.0"
date: 2026-08-14
topic: git_safety_governance
scope: 07_trading_decision_architecture
related_issues:
  - "#ARCH-GIT-SELF-HARM-GUARD（reset/checkout 自伤防护）"
  - "#ARCH-AICOLLAB-001（Git Worktree + File Lock(TTL) + Task Board 三件套）"
  - "#ARCH-GIT-DEOBFUSCATOR（shell 反混淆归一化层——v1.5.0 新登记，v2.1.0 deprecated）"
  - "#ARCH-GIT-VAR-COLLISION（PowerShell 自动变量碰撞检测——v1.5.0 新登记，v2.1.0 deprecated）"
  - "#ARCH-GIT-RISKCHAIN（session 级多步攻击链追踪——v1.5.0 新登记，v2.0.0 deprecated）"
  - "#ARCH-GIT-CVE-2026-44244（git config 注入防护——v1.6.0 新登记，v2.0.0 deprecated）"
  - "#ARCH-GIT-CVE-2026-55607（worktree 沙箱逃逸防护——v1.6.0 新登记，v2.0.0 deprecated）"
  - "#ARCH-GIT-TOCTOU（symlink/junction + TOCTOU 防护——v1.6.0 新登记，v2.0.0 deprecated）"
depends_on:
  - 01_design_memo_management_spec
  - 60_cross_cutting_cleanup
  - 61_lifecycle_multi_ai
related_modules:
  - scripts/git_guard.py
  - scripts/setup_git_guard_aliases.py
  - scripts/lock_files.py
  - scripts/governance/test_concurrent_safety.ps1
  - scripts/backup/backup.ps1
  - scripts/rollback.py
  - src/zephyr/infrastructure/runtime/concurrency_guard.py
  - src/zephyr/gov_enforcement/rule_bridge/session_worktree.py
  - src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py
---

> ## 结案报告（2026-08-16 补记；2026-08-17 追加 AI-FOPEN-001）
>
> **实际开发**：2026-08-14 治理插队批（AI-GIT-001）起多轮施工——wipe 事故治本 S1-S6（删除原语拦截 + 四证清理 SOP + 观测层落盘 + 网关锚定修复）+ task_board 重建 + Phase 1 wrapper（命令包装层）7 项全部落码并激活，含 #68 快照注入打通 Trae AI 命令通道（计划任务每分钟保活，AI 命令归因聚合）。2026-08-17 fail-open 敞口治理批（AI-FOPEN-001，Owner 裁定 B1+B2 全量，#ARCH-119）：4 个 depgraph 类硬阻断门禁（RENAME-DEPGRAPH-SYNC / NEW-FILE-DEPGRAPH-ENFORCEMENT / DEPGRAPH-PRE-REGISTRATION / PRE-MERGE-TOPO-CHECK）fail-open 分支统一接 `log_gate_failure` 持久化留痕（critical_warn + gate_id + 放行原因 + 受影响文件清单；DB 离线类同签名当日去重，真实错误逐次留痕）——放行语义不变只加留痕，下次 commit 网关 banner 自动浮现。
>
> **最终成果**：git 安全多层防护生产运行——危险命令拦截（clean -fd 等实证拦下）、删除审计、worktree 四证清理、AI 通道归因全链路实证；wrapper 40+15 测试全绿。fail-open 敞口闭合（fa25c19e49，merge 8a872d0e59+48ce3d93cb，#ARCH-119 resolved）：PG 离线时 4 gate 不再静默放行——放行必留痕可查询 + banner 浮现；红队四向量实证（PG 真实停服等效）。
>
> **未做事项及原因**：wrapper 将 git branch -d（安全删除）误报为 -D 拦截——规则区分缺陷，归下一治理批顺手修（遗留 #72）；逃生通道已验证可绕行，非阻塞。

# Git 安全治理体系——alias 失效修复与多层防护施工总案（Trae IDE 专用）

> 本备忘是 2026-08-11 灾难事件（AI 执行 `git clean -fd` 物理删除多个 untracked 文件）后的**根因分析 + 调研报告 + 裁定 + 治本施工方案**。
> **开发平台约束**：本项目 100% 围绕 **Trae IDE（编译器）** 开发——AI session 经 RunCommand（PowerShell 5.1）执行命令，Trae 不支持 PreToolUse hooks，AI 规则经 `.trae/rules/` 注入。所有防护层围绕此约束设计。
> 性质：**决策备忘 + 施工计划**混合体。管理规范见 [01_design_memo_management_spec](01_design_memo_management_spec.md)；关联 [60_cross_cutting_cleanup](60_cross_cutting_cleanup.md)｜[61_lifecycle_multi_ai](61_lifecycle_multi_ai.md)。
>
> **⚠️ v2.0.0 精简裁定（2026-08-12）**：v1.x 膨胀到 36 施工项 / 19 层防御 / 293KB，根因是把"AI 误操作"误判为"AI 恶意攻击"（adversarial）——单人单账户 AI 协作中 AI 是协作者不是攻击者。v2.0.0 将 adversarial 防御层全部 deprecated，施工范围收敛到 ~12 项 / 5-6 层防御。详见 §6.2 + §9 + §13。
>
> **⚠️ v2.1.0 第二轮精简（2026-08-12）**：保留项实现细节仍残留 adversarial 思维，再 deprecated 3 项（§7.15/§7.17.1/§7.18）+ 简化 6 项。**实际施工范围 = §13 路线图 8 施工项 / 2 Phase / ~11 天**。
>
> **⚠️ v2.2.0 文档实体精简（2026-08-14，AI-GIT-001 执行）**：前两轮裁定只加标记、未删正文，文档仍 317KB / 4900+ 行。本轮落实裁定：§3 调研 14 轮折叠为摘要（保留最终影响裁定的结论）；§7 deprecated 17 项折叠为 §7.D 一览表；已施工完成项折叠为状态摘要（代码以仓库为准）；**待施工项（§7.7 安装脚本、§7.1 wrapper 函数集、§7.23 四命令、§7.17.2 .git 阻断、§7.10+§7.27 审计日志、§7.32 Session ID、§7.13 pre-commit 接入）完整保留施工细节**。施工状态经 2026-08-14 代码核实，见 §13。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G65 Git 安全治理体系（跨切治理层） |
| 创建 | 2026-08-11 |
| 优先级 | P0（灾难已发生，必须立即治本） |
| 状态 | active v2.4.0（2026-08-14 深夜治理批：①**wrapper 已激活**——$PROFILE 单一 dot-source 真源（旧 v2.1.0 内联 block 已清除，备份 .runtime 外 TEMP），全新会话实证 git=Function/clean -fd BLOCKED/status 透传/审计 JSONL 双记录/Session ID 注入；②**Phase 2 项 8 lock_files TTL+§7.28 Mutex 落地**——Windows 全局命名 Mutex（5s 超时+WAIT_ABANDONED+超时回滚锁目录）+tmp/flush/fsync/replace 原子写+`acquire --ttl`（默认 1800s 真源不变）+expires_at 双写+`list --session` 凑齐五命令，9 新测试+10 回归全绿；③**66 号裁定 7 plumbing 扩展落地**——wrapper git() 拦 read-tree/update-index/write-tree/hash-object+ZEPHYR_SERIALIZER_MODE=1 白名单（45/45），git_guard.py 前置硬阻断+审计（16/16）；④**#56 闭环**——sweep force-clean 接四证语义审计（证2 由证4 quarantine ref 前置补偿、证3 AUTO=72h 窗软批准）、CLI create spawn heartbeat daemon+abort 对称 teardown，顺手治本 3 bug（register pid=0 逻辑 session/abort 分支名提取顺序/refs/heads 前缀）。**新边界发现：Trae AI RunCommand 终端不加载 $PROFILE，wrapper 仅覆盖人工交互终端——AI 通道防护依赖 git_guard 直接调用层+hook 层+规则层**（登记 tracker #58）。66 号 commit_queue 本体仍待排期） |
| 实际施工范围 | §13 路线图 8 施工项 / 2 Phase / ~11 天（v2.1.0 裁定） |
| 开发平台 | **Trae IDE（编译器）**——100% 围绕 Trae 开发，不支持 PreToolUse hooks，PowerShell 5.1 终端 |
| 上游 | [01_design_memo_management_spec](01_design_memo_management_spec.md)｜[60_cross_cutting_cleanup](60_cross_cutting_cleanup.md) |
| 下游 | 所有 AI session（安全规则约束）｜scripts/git_guard.py、lock_files.py、session_worktree.py｜AGENTS.md + .trae/rules/（永久规则）｜$PROFILE（PowerShell wrapper，**已激活**——限人工交互终端，AI RunCommand 通道不加载 profile，见 tracker #58） |

## 2. 背景

### 2.1 灾难事件（2026-08-11）

某并发 AI session 执行 `git clean -fd`，物理删除多个 untracked 文件（`19_northbound_hold_snapshot.md`、`18_cold_archive_build_plan.md` 等）——clean 物理删除不进回收站，且文件从未 commit，git 无法恢复。同时多个 tracked 文件的未提交修改被丢弃（疑似 `git checkout --` 或 `git reset --hard`），design_memos 下 20+ 篇文档增强内容丢失，需从 reflog 和对话历史重建。

### 2.2 直接根因（双重失效）

1. **git_guard.py 代码漏洞**：`_EXTRACTORS` 字典无 `clean` 条目 → 直接 passthrough，零拦截（clean 在 DANGEROUS_SUBCOMMANDS 中但无处理逻辑）。
2. **git alias 机制失效**：`alias.clean` 配置存在，但 `git clean -fd` 直接执行内置命令，完全绕过 alias。实测确认：**git alias 无法覆盖内置命令**——git 设计行为，非 bug。

### 2.3 系统性问题

`reset`/`checkout`/`restore`/`stash`/`revert`/`mv` 全是 git 内置命令，alias 拦截**全部失效**——git_guard.py 的 alias 拦截体系（7 个 DANGEROUS_SUBCOMMANDS）在 Windows git 2.48.1 上形同虚设。

## 3. 调研报告（v2.2.0 折叠：14 轮搜索 → 每轮 1-2 行摘要）

> v1.x 累计 14 轮全网搜索（§3.1-§3.14，约 900 行过程性记录）已折叠为每轮核心发现 + 最终影响裁定的结论；过程性引用、链接、代码片段已删除。

### 3.1-3.14 各轮核心发现

| 轮次 | 核心发现 |
|---|---|
| 3.1 | **git alias 无法覆盖内置命令是 git 官方设计行为**——alias 只能为"不存在的命令名"创建快捷方式，同名内置命令优先。alias 拦截方案从设计上无效。 |
| 3.2 | GitHub 开源方案：git-sentinel（Go 透明 wrapper，PATH 拦截，专门针对 AI coding agent）、dcg/git-safety-guard 等——wrapper 拦截是业界主流。 |
| 3.3 | AI 编程社区：Claude Code 用 PreToolUse hooks（Trae 不支持）；Cursor 论坛多起 `rmdir /s /q` 误删 C: 盘事故——PowerShell 原生命令是最大 gap。 |
| 3.4 | 量化社区：无现成方案，确认"文件锁 + worktree 隔离"是多 AI 协作标配。 |
| 3.5 | SafeRun Guard（双重安全检查）、opencode-fusion PR #12 证实"Windows 上 AI agent 几乎全部用 PowerShell"——必须覆盖 PowerShell 原生破坏性命令。 |
| 3.6 | **trash redirect 算法**：非 CRITICAL 删除重定向到回收站而非阻断——AI 不卡住、文件可恢复。已提炼为 §7.11（远期）。 |
| 3.7 | safe-rm 三层分类（block→auto_allow→auto_trash）：需逐文件 git status 判断，复杂度高——远期改进。 |
| 3.8 | **ProxyCommand 最佳实践**：手写 Remove-Item param() 丢失动态参数/ShouldProcess/管道支持，正确做法用 `ProxyCommand::Create()` 生成代理脚手架。已提炼为 §7.1.4。另发现 RULE-THREE 三步审判已在 .trae/rules/ 中。 |
| 3.9 | fail-open 策略（wrapper 出错放行+记录，行业共识）、opencode-swarm #1875（AI 遇不识别错误无限重试烧 token）、**d6_security 14 脚本未接入 pre-commit（CRITICAL GAP）**。已提炼为 §7.13/§7.14。 |
| 3.10 | GuardFall（单层防护 5 大绕过类）、Codex `$home` 事故、Zed 1.14.2（**.git 写入永久阻断是 kernel 级最佳实践**）、grite C2（file-based tracker 静默丢并发写）、SQLite CAS。仅 .git 阻断（§7.17.2）保留，其余 adversarial 项已 deprecated。 |
| 3.11 | PS 5.1 兼容性（7 种 PS 7+ 语法不兼容，含 `?.`）、git 专属攻击向量（CVE-2026-44244/55607 等）、**PSReadLine 对 AI agent 脚本无效**。git 危险命令 v2.1.0 简化为 4 个（§7.23）。 |
| 3.12 | **Trae 多 AI 并发病根**：session 独立 PowerShell 进程但共享状态文件 RMW 竞态（audit JSONL/registry.json/.git/index 等 7 个）；Claude Code `.claude.json` 423 次并发损坏是决定性证据；f2t.jp 案例（add A B 却 commit 进 C D E）；**PS 5.1 并发写入 4 方案**。已提炼为 §7.27/§7.28。 |
| 3.13 | Named Pipe 单线程协调器、Trae SessionStart hook TRAE_ENV_FILE——过度工程 deprecated（SQLite WAL 已够、$PROFILE 一行 UUID 已够）。 |
| 3.14 | 诚实评估：v1.8.0 到达边际收益递减点；8 个底层方案仅 AST 明确更优但无 adversarial 场景 deprecated。 |

### 3.15 最终影响裁定的结论（施工依据）

1. **git alias 无法覆盖内置命令是设计行为**（§3.1）→ 必须放弃 alias 拦截体系，改用 shell 层拦截。
2. **shell wrapper（PowerShell 函数覆盖）是唯一可靠拦截层**（§3.2/§3.5/§3.11）——Trae 无 PreToolUse hooks，RunCommand 加载 $PROFILE，函数覆盖对所有 session 生效。
3. **PowerShell 原生破坏性命令与 git 危险命令同等危险**（§3.3/§3.5）→ wrapper 必须同时覆盖。
4. **ProxyCommand::Create() 是覆盖内置 cmdlet 的正确方法**（§3.8）→ §7.1.4。
5. **共享状态文件并发 RMW 竞态是多 AI 病根**（§3.12）→ 审计日志改每 session 独立文件（§7.27）、lock_files.py 需 Mutex+原子写（§7.28）。
6. **adversarial 防御不适用于单人 AI 协作**（v2.0.0/v2.1.0 裁定）→ 反混淆/RiskChain/AST/Named Pipe daemon 等全部 deprecated（§9）。

## 4. 现状分析：项目现有 Git 配套设施（与本方案相关部分）

> v2.2.0 折叠：原 71 项设施全量清单（含 .git/hooks、CI 工作流、d6_security 脚本群、安全配置 yaml 明细）仅保留与本方案裁定直接相关的条目。

### 4.1 与本方案直接相关的设施清单（2026-08-14 代码核实状态）

| # | 设施 | 与本方案的关系 | 2026-08-14 核实 |
|---|---|---|---|
| 1 | scripts/git_guard.py | alias 拦截全失效（§2.2）；直接调用仍有效（7 个 porcelain 子命令），作 wrapper 补充层 | ✅ production |
| 2 | scripts/lock_files.py | 三件套之 File Lock（§11.3.2） | ✅ production；**v2.4.0：§7.28 Mutex+原子写已落地，`--ttl` 五命令齐备**（tests/git/test_lock_files_ttl_mutex.py 9 用例） |
| 3 | scripts/session_worktree.py | 三件套之 Worktree（§11.3.1） | ✅ production，五命令齐备 |
| 4 | scripts/task_board.py | 三件套之 Task Board（§11.2.3） | ✅ **已重建**（2026-08-14 AI-GIT-001，66 号 §2.4 #9 schema，17 测试全过，commit 0e5ed3b9） |
| 5 | scripts/install_git_safety_wrapper.ps1 | §7.7 安装脚本（一键装/卸 wrapper 进 $PROFILE） | ✅ **已施工**（2026-08-14 晚 AI-GIT-001，611227d5：幂等 marker/卸载/真源自检/-ProfilePath 测试注入） |
| 6 | .trae/rules/ | RULE-GIT-SAFE 应写入处（§7.2，Trae AI 规则入口） | ✅ **已写入**（2026-08-14 晚，21f447c1，project_rules.md RULE-GIT-SAFE 节） |
| 7 | src/zephyr/infrastructure/runtime/concurrency_guard.py | git_guard.py 依赖的运行时并发守卫 | ✅ 存在 |
| 8 | GitCommitGateway + commit_gates（100 gate） | 唯一合法 commit 入口——只拦 commit 不拦 clean/reset | ✅ 正常运行 |
| 9 | .pre-commit-config.yaml | §7.13 d6_security 3 hook 接入处 | ✅ **已接入**（2026-08-14 晚，21f447c1：detect_git_dangerous/detect_shell_dangerous/detect_permanent_file_deletion 三 hook 注册） |
| 10 | config/immutable_core.yaml | 受保护路径 commit 时检查——与 §7.17.2 运行时阻断两层叠加 | ✅ 正常运行 |
| 11 | memory/project_memory.md | 灾难教训已记录（§7.3） | ✅ 已记录 |
| 12 | scripts/setup_git_guard_aliases.py | alias 安装入口，曾缺 clean（§7.12）——alias 失效后降格维护性 | ✅ clean 已补齐（2026-08-14 晚，21f447c1，对齐 7 命令） |
| 13 | scripts/ops_guard.py | **全原语删除拦截层**（S1，2026-08-14 wipe 治本关联施工）——PowerShell/CMD/Python/git clean 四类删除原语，保护区 fail-closed，删除强制先落审计 | ✅ production（3e2bb5ed70，42 红队向量 100% 拦截，已 merge 回 dev；与 §7.1 wrapper 关系：ops_guard 覆盖删除原语面，wrapper 层覆盖 git 危险命令+硬阻断面，两者互补） |

### 4.2 防护层失效分析

```
AI 执行 git clean -fd
  → [L1 alias 拦截] 失效（alias 无法覆盖内置命令）→ 不经过 git_guard.py
  → [L2 pre-commit hooks] 不触发（clean 不是 commit）
  → [L3 文件锁] 不防护（untracked 文件不在锁管辖范围）
  → [L4 session_worktree] 不触发（AI 未用 worktree，直接在主工作区操作）
  → [L5 GitCommitGateway] 不触发（clean 不是 commit）
  → git 内置 clean 执行 → untracked 文件物理删除
```

**结论**：现有 5 层防护对 `git clean -fd` 全部失效，必须新增 git 执行前的拦截层（PowerShell wrapper）。7 个 DANGEROUS_SUBCOMMANDS 的 alias 拦截全部失效；`git branch -D`/`git push --force` 从未被 alias 体系覆盖。

### 4.3 PowerShell 原生破坏性命令 gap（v0.9.0 发现）

git wrapper 不覆盖非 git 命令。Cursor 论坛 2026-04~07 多起 `rmdir /s /q` 误删事故证实：`Remove-Item -Recurse -Force`/`rd /s`/`del /s /f`/`rm -rf` 与 git clean 同等危险，必须纳入 wrapper。另设 CRITICAL_BLOCKS 硬阻断清单（无逃生通道）：`format`/`vssadmin delete`/`wbadmin delete`/`cipher /w`/`diskpart`/`reg delete`/`bcdedit`/`netsh advfirewall`/`schtasks /delete|/create`/`sc delete|stop`/`powershell -enc`/`iex`/`Invoke-Expression`。

## 5. 第一性原理分析：100%AI 开发项目的文件安全需求模型

### 5.1 与传统项目的本质区别

| 维度 | 传统项目 | 100%AI 开发项目 |
|---|---|---|
| 操作者 | 人类（理解危险） | AI（不理解危险，只执行指令） |
| 并发度 | 1-3 人 | 10-26 个并发 AI session |
| 文件保护意识 | 高 | 零（不知道 clean 不可恢复） |
| 错误恢复 | 高（回收站/stash/reflog） | 低（不会主动恢复） |
| 操作速度 | 慢 | 快（秒级执行，错误瞬间发生） |
| 审查 | code review + 人工确认 | 无（AI 直接执行） |

### 5.2 安全需求模型

**核心需求**：在 AI 不理解危险的情况下，从技术层面阻止危险操作发生。

| 需求 | 内容 | 优先级 |
|---|---|---|
| 1-3 | 阻止 `git clean`/`reset --hard`/`checkout --`/`restore` 删改文件 | P0（灾难已发生） |
| 4 | 新建/修改文件立即 staged（clean 不删 tracked） | P0 |
| 5-6 | 改文件前加锁；worktree 隔离 | P1（设施已有，需激活/强制） |
| 7 | 永久规则写入 AGENTS.md + .trae/rules/ | P0 |
| 8 | 定期 push 远程（最终备份） | P2 |
| 9 | 阻止 PowerShell 原生破坏性命令 | P0（v0.9.0） |
| 10 | 拦截/放行全程审计日志 | P1（v0.9.0） |

### 5.3 约束条件

- **Trae IDE 不支持 PreToolUse hooks** → 必须在 shell 层（PowerShell 函数）拦截
- **PowerShell 5.1**：`&&`/`||` 是语法错误；`;`/`|` 天然使子命令独立触发函数覆盖，无需复合命令拆分
- **RunCommand 加载 $PROFILE**（实测不用 `-NoProfile`）→ 函数覆盖对 AI 命令生效
- **Windows + git 2.48.1**：alias 无法覆盖内置命令（确认）
- **个人项目**：不引入多人协作治理机制；规则必须机器可读、AI 可执行（不依赖人工自觉）

## 6. 裁定结果

### 6.1 方案选型

| 方案 | 机制 | 裁定 |
|---|---|---|
| A. Git Wrapper（PATH 拦截） | git 脚本/函数底层拦截，无法绕过 | ✅ **采用** |
| B. AI 工具层防护 | PreToolUse hooks 精准拦截，但 Trae 不支持 | ❌ 不适用 |
| C. 保护性 git add | staged 文件 clean 不删；零侵入但依赖自觉 | ✅ **采用（补充层）** |
| D. 文件锁系统 | 改文件前先 acquire；防跨 AI 冲突，不防 clean | ✅ **采用（P1 激活）** |
| E. session_worktree | 工作区隔离，根本消除冲突 | ✅ **采用（P1 强制）** |
| F. git hooks（pre-*） | git 无 pre-clean hook | ❌ 不适用 |
| G. 定期 auto-commit | 可能 commit 垃圾文件 | ⏸ 远期考虑 |
| H. PowerShell 原生命令覆盖（v0.9.0） | 函数覆盖 Remove-Item/rd/del 等，拦截非 git 破坏命令 | ✅ **采用** |
| I. 审计日志（v0.9.0） | JSONL 持久化所有拦截/放行，事后可追溯 | ✅ **采用** |
| J. Named Pipe 协调器 daemon（v1.8.0） | 单点故障+复杂度高+SQLite WAL 已够 | ❌ **v2.0.0 deprecated**（见 §9） |
| K. 跨 session GovernanceStore（v1.7.0） | 与 §11.3.3 Task Board 重复 | ❌ **v2.0.0 deprecated**（见 §9） |
| L. adversarial 防御层（v1.5.0-v1.6.0） | 单人 AI 协作无 adversarial 场景 | ❌ **v2.0.0 deprecated**（见 §9） |

### 6.2 最终裁定：v2.1.0 精简防御层（6 层，实现简化）

> **v2.0.0 精简裁定**：v1.x 的 19 层防御（L1-L19）中，L9/L10/L12-L16/L18/L19 共 9 层判定为单人 AI 协作场景过度工程，全部 `deprecated`。保留 6 层核心防御 + §11 三件套。
>
> **v2.1.0 第二轮精简**：保留项实现细节仍残留 adversarial 思维——L4 砍自动变量碰撞（只留 .git 阻断）；L5 Mutex→每 session 独立文件；L6 init-session.ps1→$PROFILE 一行；三件套去 heartbeat/epoch/7 天告警。6 层结构不变，实现大幅精简。

```
L1: PowerShell git wrapper 函数（拦截 git clean/reset --hard/checkout -- + 4 命令：filter-branch/filter-repo/reflog expire/gc --prune）—— §7.1.1 + §7.23（v2.1.0 简化到 4 命令）
L2: PowerShell 原生破坏性命令覆盖（Remove-Item -Recurse -Force/rd/del/format 等）—— §7.1.2
L3: AGENTS.md + .trae/rules/ RULE-GIT-SAFE 永久规则 + 保护性 git add + fail-open 策略 —— §7.2 + §7.14（v2.1.0 §7.15 错误分类 deprecated）
L4: .git 目录运行时硬阻断（v2.1.0 自动变量碰撞检测 deprecated，改为 RULE-GIT-SAFE 规则一条）—— §7.17.2
L5: 审计日志（每 session 独立文件 audit_{yyyyMMdd}_{sessionId}.jsonl，v2.1.0 从 Mutex 简化）—— §7.10 + §7.27
L6: Session ID 注入（$PROFILE 顶部一行 UUID，v2.1.0 从 init-session.ps1 简化）—— §7.32

外加 §11 三件套（P1 并发协调层，v2.1.0 简化版）：
  - Git Worktree（每 AI 独立 checkout + 分支，v2.1.0 去 7 天告警）—— §11.3.1
  - File Lock TTL（lock_files.py 扩展，60min 自动过期，v2.1.0 去 heartbeat）—— §11.3.2
  - Task Board（SQLite CAS 状态机 pending→claimed→completed，v2.1.0 去 epoch/blocked/abandoned）—— §11.3.3
```

**v2.0.0 deprecated 的 v1.x 层级对照**：L9 Trash Redirect→降为 L2 可选细节；L10 反混淆→v2.1.0 deprecated；L11→v2.0.0 保留为 L4、v2.1.0 仅留 .git 阻断；L17→保留为 L5、v2.1.0 Mutex→每 session 独立文件；L12 SafeFix / L13 RiskChain / L14 symlink 防护 / L15 hook 信任链 / L16 4104 / L18 GovernanceStore / L19 Named Pipe daemon→全部 deprecated（无 adversarial 场景/重复造轮子/单点故障/企业级过重，见 §9 + §7.D）。

### 6.3 不采用的方案及理由

| 方案 | 不采用理由 |
|---|---|
| Go 编写的 git wrapper（git-sentinel） | 过度工程——PowerShell 函数足够，无需编译 |
| Claude Code PreToolUse hooks | Trae IDE 不支持 hooks |
| git hooks（pre-clean） | git 没有 pre-clean hook（hook 只覆盖 commit/push/checkout 等） |
| 定期 auto-commit | 可能 commit 垃圾文件，复杂度高，远期考虑 |
| Named Pipe Coordinator Daemon | §11.3.3 Task Board 已用 SQLite WAL + CAS（工业级并发方案）；daemon 单点故障，增益仅微秒级 |
| 跨 session GovernanceStore | 与 Task Board SQLite 重复——Task Board 已是跨 session 协调层 |
| adversarial 防御层 | RiskChain/SafeFix/symlink/hook hash/AST 等均为"防 AI 攻击自己"设计——单人单账户 AI 协作中 AI 是协作者不是攻击者，无 adversarial 场景 |

## 7. 施工方案

> **v2.2.0 结构说明**：本节按施工状态三分——**待施工项（§7.1/§7.7/§7.10/§7.13/§7.14/§7.17.2/§7.23/§7.27/§7.28/§7.32）完整保留施工细节**；已施工完成项（§7.4/§7.5/§7.6 + §11 之 Worktree/File Lock）折叠为状态摘要；`deprecated` 17 项合并为 §7.D 一览表（正文删除）。

### 7.1 施工项 1：PowerShell 安全 wrapper 函数集（L1+L2，P0，**待施工——核心设计规格**）

**目标**：在 PowerShell 中定义 `git()` 函数拦截危险 git 命令，并定义 `Remove-Item()`/`rd()`/`del()` 等函数拦截 PowerShell/CMD 原生破坏性命令。由 §7.7 安装脚本写入 `$PROFILE`。

#### 7.1.1 Part A：git 命令拦截函数

在 PowerShell profile（`$PROFILE`）中添加 `git()` 函数（v2.2.0 删除冗长注释，保留完整可施工代码）：

```powershell
# >>> git-safety-wrapper >>> (ZephyrAlpha #ARCH-GIT-CLEAN-GUARD-FIX)
# 真实 git.exe 路径检测（不用函数名 git 避免循环调用）：环境变量 > 注册表 > 硬编码常见路径 > fallback
$_realGit = $env:ZEPHYR_REAL_GIT_PATH
if (-not $_realGit) {
    $_realGit = (Get-ItemProperty 'HKLM:\SOFTWARE\GitForWindows' -ErrorAction SilentlyContinue).InstallPath
    if ($_realGit) { $_realGit = Join-Path $_realGit 'cmd\git.exe' }
}
if (-not $_realGit -or -not (Test-Path $_realGit)) {
    foreach ($_p in @('C:\Program Files\Git\cmd\git.exe', 'C:\Program Files (x86)\Git\cmd\git.exe', "$env:LOCALAPPDATA\Programs\Git\cmd\git.exe")) {
        if (Test-Path $_p) { $_realGit = $_p; break }
    }
}
if (-not $_realGit) { $_realGit = 'git.exe' }  # 最终 fallback

# 审计日志函数（v2.1.0 规格：每 session 独立文件 audit_{yyyyMMdd}_{sessionId}.jsonl，无 Mutex，见 §7.10+§7.27）
function _ZephyrAuditLog {
    param([string]$Command, [string]$Action, [string]$Reason, [string]$EscapeHint = '')
    $_logDir = Join-Path $env:USERPROFILE '.zephyr_audit'
    if (-not (Test-Path $_logDir)) { New-Item -ItemType Directory -Path $_logDir -Force | Out-Null }
    $_session = if ($env:ZEPHYR_SESSION_ID) { $env:ZEPHYR_SESSION_ID } else { 'nosession' }
    $_logFile = Join-Path $_logDir ("audit_{0:yyyyMMdd}_{1}.jsonl" -f (Get-Date), $_session)
    $_entry = @{
        timestamp = (Get-Date).ToString('o')
        action    = $Action
        command   = $Command
        reason    = $Reason
        session   = $env:ZEPHYR_SESSION_ID
        pid       = $PID
    }
    if ($EscapeHint) { $_entry.escape_hint = $EscapeHint }
    $_entry | ConvertTo-Json -Compress | Add-Content -Path $_logFile -Encoding UTF8
}

function git {
    $cmd = if ($args.Count -gt 0) { $args[0] } else { '' }
    $fullArgs = $args -join ' '
    $blocked = $false
    $reason = ''
    if ($cmd -eq 'clean' -and ($fullArgs -notmatch '(?:^|\s)-(?:n|-dry-run)(?:\s|$)')) {
        $blocked = $true; $reason = 'git clean 删除 untracked 文件（物理删除不进回收站）'
    } elseif ($cmd -eq 'reset' -and ($fullArgs -match '--hard|--merge')) {
        $blocked = $true; $reason = 'git reset --hard/--merge 丢弃未提交修改'
    } elseif ($cmd -eq 'checkout' -and ($fullArgs -match '(?:^|\s)--(?:\s|$)' -or $fullArgs -match 'HEAD\s+--' -or $fullArgs -match '(?:^|\s)\.(?:\s|$)')) {
        $blocked = $true; $reason = 'git checkout 丢弃文件修改'
    } elseif ($cmd -eq 'restore' -and ($fullArgs -match '--worktree' -or ($fullArgs -notmatch '--staged'))) {
        $blocked = $true; $reason = 'git restore 丢弃文件修改'
    } elseif ($cmd -eq 'stash' -and ($args.Count -lt 2 -or $args[1] -notin @('list', 'show'))) {
        $blocked = $true; $reason = 'git stash 移走/删除未提交修改'
    } elseif ($cmd -eq 'rm' -and ($fullArgs -notmatch '--cached')) {
        $blocked = $true; $reason = 'git rm 从工作区删除文件'
    } elseif ($cmd -eq 'branch' -and ($fullArgs -match '-D|--delete-force')) {
        $blocked = $true; $reason = 'git branch -D 强制删除分支（可能丢失未合并代码）'
    } elseif ($cmd -eq 'push' -and ($fullArgs -match '(?:^|\s)-(?:f|-force)(?:\s|$)' -and $fullArgs -notmatch '--force-with-lease')) {
        $blocked = $true; $reason = 'git push --force 覆盖远程历史（可能丢失他人代码）'
    }
    # §7.23（v2.1.0 简化为 4 命令）：filter-branch/filter-repo/reflog expire/gc --prune=now
    elseif ($cmd -eq 'filter-branch' -or $cmd -eq 'filter-repo') {
        $blocked = $true; $reason = "git $cmd 历史重写——不可逆操作"
    } elseif ($cmd -eq 'reflog' -and $args.Count -gt 1 -and $args[1] -eq 'expire') {
        $blocked = $true; $reason = 'git reflog expire 抹除 forensic 证据'
    } elseif ($cmd -eq 'gc' -and ($fullArgs -match '--prune=(now|all)')) {
        $blocked = $true; $reason = 'git gc --prune=now 物理删除 unreachable 对象'
    }

    if ($blocked) {
        Write-Host "[GIT-SAFE] BLOCKED: git $fullArgs — $reason" -ForegroundColor Red
        Write-Host "  逃生通道（确认安全后）：& '$_realGit' $fullArgs" -ForegroundColor Yellow
        _ZephyrAuditLog -Command "git $fullArgs" -Action 'BLOCKED' -Reason $reason -EscapeHint "& '$_realGit' $fullArgs"
        return 1
    }
    _ZephyrAuditLog -Command "git $fullArgs" -Action 'ALLOWED' -Reason 'safe command'
    & $_realGit @args
}
# <<< git-safety-wrapper <<<
```

**git 命令阻断/放行规则明细**：

| 命令 | 阻断条件 | 放行条件 |
|---|---|---|
| `git clean` | `-f`/`-fd`/`-fdx` | `-n`/`--dry-run`（只预览） |
| `git reset` | `--hard`/`--merge` | `--soft`/`--mixed`/无参数 |
| `git checkout` | `-- <file>` / `HEAD -- <file>` / `.` | `<branch>`/`-b`/`--orphan` |
| `git restore` | 不带 `--staged`，或带 `--worktree` | 仅 `--staged` |
| `git stash` | `push`/`pop`/`apply`/`clear`/`branch`/`drop`/无子命令 | `list`/`show` |
| `git rm` | 不带 `--cached` | `--cached` |
| `git branch` | `-D`/`--delete-force` | `-d`（检查合并） |
| `git push` | `--force`/`-f` | `--force-with-lease` |
| `git filter-branch`/`filter-repo` | 任何调用（§7.23，历史重写不可逆） | 无 |
| `git reflog expire` | 任何调用（§7.23，抹除 forensic 证据） | `reflog show` 等只读 |
| `git gc --prune=now/all` | 带 `--prune=now`/`all`（§7.23，物理删对象） | `git gc` 无 `--prune` |

#### 7.1.2 Part B：PowerShell/CMD 原生破坏性命令拦截

> **核心算法**：双重安全检查——Layer 1 危险模式匹配 → Layer 2 CRITICAL_BLOCKS 绝对禁止（硬阻断无逃生通道）。

```powershell
# >>> powershell-destructive-guard >>> (ZephyrAlpha ARCH-POWERSHELL-DESTRUCTIVE-GUARD（待登记） v0.9.0)
# 先保存内置 cmdlet 引用（避免函数覆盖后循环调用）
$_realRemoveItem = (Get-Command Microsoft.PowerShell.Management\Remove-Item -ErrorAction SilentlyContinue)

# CRITICAL_BLOCKS：绝对禁止，无逃生通道（系统级破坏）
$_criticalBlocks = @(
    'format ', 'vssadmin delete', 'wbadmin delete', 'cipher /w', 'diskpart', 'reg delete', 'bcdedit',
    'netsh advfirewall', 'schtasks /delete', 'schtasks /create', 'schtasks /change', 'sc delete', 'sc stop',
    'powershell -enc', 'powershell -encodedcommand', 'powershell.exe -enc', '-encodedcommand'
)

# Remove-Item 覆盖：仅阻断 -Recurse -Force 组合（目标在 $env:TEMP 的放行）
function Remove-Item {
    [CmdletBinding()]
    param([Parameter(Mandatory=$false, Position=0)][string[]]$Path, [switch]$Recurse, [switch]$Force,
        [switch]$Confirm, [switch]$WhatIf, [string]$Filter, [string[]]$Include, [string[]]$Exclude, [string]$LiteralPath)
    $fullCmd = "Remove-Item $($args -join ' ')"
    $isCritical = $false
    foreach ($pattern in $_criticalBlocks) {
        if ($fullCmd -like "*$pattern*") { $isCritical = $true; break }
    }
    if ($Recurse -and $Force) {
        $targetPath = if ($Path) { $Path[0] } elseif ($LiteralPath) { $LiteralPath } else { '' }
        $isTemp = $false
        if ($targetPath -and $env:TEMP) {
            # PS 5.1 兼容写法（无 ?. 运算符）
            $_resolvedPath = Resolve-Path $targetPath -ErrorAction SilentlyContinue
            $resolvedTarget = if ($_resolvedPath) { $_resolvedPath.Path } else { $null }
            if ($resolvedTarget -and $resolvedTarget.StartsWith($env:TEMP, [System.StringComparison]::OrdinalIgnoreCase)) {
                $isTemp = $true
            }
        }
        if (-not $isTemp) {
            Write-Host "[SAFE] BLOCKED: Remove-Item -Recurse -Force — 递归强制删除（物理删除不进回收站）" -ForegroundColor Red
            Write-Host "  逃生通道（确认安全后）：& `$_realRemoveItem -Recurse -Force <path>" -ForegroundColor Yellow
            _ZephyrAuditLog -Command $fullCmd -Action 'BLOCKED' -Reason 'Remove-Item -Recurse -Force 递归强制删除' -EscapeHint "& `$_realRemoveItem -Recurse -Force <path>"
            return
        }
    }
    _ZephyrAuditLog -Command $fullCmd -Action 'ALLOWED' -Reason 'safe Remove-Item call'
    & $_realRemoveItem @PSBoundParameters
}

# rd/rmdir/del/erase/rm 函数覆盖（rd/del/erase 是 Remove-Item 别名，函数优先于别名生效）
function rd { param([Parameter(Position=0)][string]$Path, [string[]]$Args)
    if ($Args -join ' ' -match '/s') {
        Write-Host "[SAFE] BLOCKED: rd /s — CMD 递归删除目录" -ForegroundColor Red
        _ZephyrAuditLog -Command "rd $Path $($Args -join ' ')" -Action 'BLOCKED' -Reason 'rd /s CMD 递归删除'
        return 1
    }
    & $_realRemoveItem -Path $Path @Args
}
Set-Alias -Name rmdir -Value rd -Force -ErrorAction SilentlyContinue

function del { param([Parameter(Position=0)][string[]]$Path, [string[]]$Args)
    $argStr = $Args -join ' '
    if ($argStr -match '/s|/f') {
        Write-Host "[SAFE] BLOCKED: del $argStr — CMD 批量/强制删除" -ForegroundColor Red
        _ZephyrAuditLog -Command "del $Path $argStr" -Action 'BLOCKED' -Reason "del $argStr CMD 批量/强制删除"
        return 1
    }
    & $_realRemoveItem -Path $Path @Args
}
Set-Alias -Name erase -Value del -Force -ErrorAction SilentlyContinue

# rm 函数覆盖（若 GnuWin32 coreutils rm 在 PATH 中）
function rm {
    $argStr = $args -join ' '
    if ($argStr -match '(?:^|\s)-(?:rf|fr)(?:\s|$)') {
        $isTemp = $false
        foreach ($a in $args) {
            if ($a -notmatch '^-' -and $a -and $env:TEMP) {
                $_resolvedPath = Resolve-Path $a -ErrorAction SilentlyContinue  # PS 5.1 兼容写法
                $resolved = if ($_resolvedPath) { $_resolvedPath.Path } else { $null }
                if ($resolved -and $resolved.StartsWith($env:TEMP, [System.StringComparison]::OrdinalIgnoreCase)) { $isTemp = $true; break }
            }
        }
        if (-not $isTemp) {
            Write-Host "[SAFE] BLOCKED: rm -rf — Unix 递归强制删除" -ForegroundColor Red
            _ZephyrAuditLog -Command "rm $argStr" -Action 'BLOCKED' -Reason 'rm -rf 递归强制删除'
            return 1
        }
    }
    $_realRm = Get-Command rm.exe -ErrorAction SilentlyContinue
    if ($_realRm) { & $_realRm.Source @args } else { & $_realRemoveItem @args }
}

# CRITICAL 命令函数覆盖——硬阻断，无逃生通道
function format { param([string]$Drive, [string[]]$Args)
    Write-Host "[SAFE] HARDBLOCKED: format — 格式化磁盘（系统级破坏，永远阻断）" -ForegroundColor Red
    _ZephyrAuditLog -Command "format $Drive $($Args -join ' ')" -Action 'HARDBLOCKED' -Reason 'format 格式化磁盘'
    return 1
}
function vssadmin { param([string]$SubCommand, [string[]]$Args)
    if ($SubCommand -eq 'delete') {
        Write-Host "[SAFE] HARDBLOCKED: vssadmin delete — 删除卷影副本（备份破坏）" -ForegroundColor Red
        _ZephyrAuditLog -Command "vssadmin $SubCommand $($Args -join ' ')" -Action 'HARDBLOCKED' -Reason 'vssadmin delete 删除备份'
        return 1
    }
    $_realCmd = Get-Command vssadmin.exe -ErrorAction SilentlyContinue
    if ($_realCmd) { & $_realCmd.Source $SubCommand @Args }
}
function diskpart { param([string[]]$Args)
    Write-Host "[SAFE] HARDBLOCKED: diskpart — 磁盘分区操作（系统级破坏）" -ForegroundColor Red
    _ZephyrAuditLog -Command "diskpart $($Args -join ' ')" -Action 'HARDBLOCKED' -Reason 'diskpart 磁盘分区操作'
    return 1
}
# <<< powershell-destructive-guard <<<
```

**PowerShell 原生命令阻断/放行规则明细**（逃生通道见 §7.1.5）：

| 命令 | 阻断条件 | 放行条件 |
|---|---|---|
| `Remove-Item` | `-Recurse -Force` 同存且目标不在 `$env:TEMP` | 不带 `-Recurse`，或目标在临时目录 |
| `rd`/`rmdir` | 带 `/s` | 不带 `/s` |
| `del`/`erase` | 带 `/s` 或 `/f` | 不带 `/s`/`/f` |
| `rm` | `-rf`/`-fr` 且目标不在临时目录 | 目标在 `$env:TEMP` |
| `format` / `vssadmin delete` / `diskpart` | 任何调用（CRITICAL，永远阻断） | 无 |

#### 7.1.3 Part C：复合命令行为（PowerShell 5.1 无需拆分逻辑）

PS 5.1 的 `;`/`|` 天然使每个子命令独立触发函数覆盖；`&&`/`||` 是语法错误，AI 不会用。**无需复合命令拆分逻辑**。**残留风险**：`Invoke-Expression "..."` 在新作用域解析字符串可绕过函数覆盖——`iex`/`Invoke-Expression` 已列入 §4.3 CRITICAL_BLOCKS 硬阻断。

#### 7.1.4 Part D：ProxyCommand 最佳实践修正（v1.2.0）

手写 `Remove-Item` 的 param() 块会丢失动态参数（`-Credential`）、ShouldProcess（`-WhatIf`/`-Confirm`）与管道输入。**正确方法**：安装时用 `[System.Management.Automation.ProxyCommand]::Create()` 对 `Microsoft.PowerShell.Management\Remove-Item` 生成完整代理脚手架，Begin 块插入 §7.1.2 拦截逻辑，Process 块经 steppable pipeline 透传，保留 DynamicParam 块。`rd`/`del`/`rm`/`format` 等不是内置 cmdlet（别名或外部命令），保持手写即可。

#### 7.1.5 逃生通道与对现有脚本的影响

| 场景 | 逃生命令 |
|---|---|
| git 危险命令 | `& 'C:\Program Files\Git\cmd\git.exe' clean -fd` |
| Remove-Item 递归删除 | `& $_realRemoveItem -Recurse -Force <path>` |
| rd /s | `& cmd /c "rd /s <path>"`（cmd 子进程绕过函数） |
| rm -rf | `& (Get-Command rm.exe).Source -rf <path>` |
| CRITICAL 命令（format/vssadmin/diskpart） | **无逃生通道**——永远阻断 |

**对现有脚本的影响**（施工时需处理）：①`session_worktree abort` 的 `git checkout --` 会被阻断 → 用 `& $_realGit checkout --` 逃生通道；②pre-commit 框架 stash unstaged 会被阻断 → 配置逃生通道或环境变量绕过；③`test_concurrent_safety.ps1` 的 `Remove-Item <file> -Force`（无 -Recurse）放行，不受影响；④`backup.ps1` 旧备份清理（`-Recurse -Force` 且非 TEMP）会被阻断 → 改用 `& $_realRemoveItem`。

### 7.2 施工项 2：AGENTS.md + .trae/rules/ RULE-GIT-SAFE 永久规则（L3，P0，**待施工**）

**目标**：在 AGENTS.md 和 .trae/rules/project_rules.md 新增 `RULE-GIT-SAFE` 节作为永久规则。AGENTS.md 是项目规则真源（全 AI 工具通用）；.trae/rules/project_rules.md 是 Trae IDE 的 AI 规则入口，不写入则 Trae 的 AI 看不到。

**内容**：
```markdown
## RULE-GIT-SAFE：Git 安全铁律（2026-08-11 #ARCH-GIT-CLEAN-GUARD-FIX）

> **背景**：2026-08-11 灾难——AI 执行 git clean -fd 物理删除多个 untracked 文件。
> git alias 无法覆盖内置命令（git 2.48.1 Windows 实测确认），alias 拦截全部失效。

**所有 AI session MUST 遵守**：

1. **禁止的 git 命令**（阻断/放行边界见 65 号 memo §7.1.1 明细表）：`git clean -f/-fd/-fdx`；`git reset --hard/--merge`（用 `--soft`/`--mixed` 替代）；`git checkout -- <file>`/`HEAD -- <file>`/`checkout .`（切/建分支安全）；`git restore <file>`（`--staged` 安全）；`git stash`（`list`/`show` 只读安全）；`git rm <file>`（`--cached` 安全）；`git branch -D`（用 `-d`）；`git push --force`/`-f`（用 `--force-with-lease`）。
2. **每轮修改后立即 `git add <file>`**：staged 文件不会被 git clean 删除。
3. **修改文件前先加锁**：`python scripts/lock_files.py acquire <file> <session_id>`
4. **完成修改后释放锁**：`python scripts/lock_files.py release <file> <session_id>`
5. **如需执行危险命令**：必须先 commit 所有修改 + 经用户确认 + 用完整路径调用真实 git：`& 'C:\Program Files\Git\cmd\git.exe' clean -fd`
6. **禁止用 $HOME/$PID/$TRUE 等 PowerShell 只读自动变量名作变量名**（v2.1.0 新增，替代 §7.17.1 检测函数——Codex `$home` 事故教训）。
```

**位置**：插入在 AGENTS.md `RULE-WORKTREE` 之后、`RULE-GUARDIAN` 之前（或按现有顺序适当位置）。

### 7.4-7.6 已施工完成项（v2.2.0 折叠为状态摘要）

| 施工项 | 内容 | 状态 |
|---|---|---|
| §7.4 git_guard.py alias 配置清理 | alias 配置保留不删（无害），头注释标注"alias 拦截不生效，依赖 PowerShell wrapper" | ✅ production（直接调用拦 7 个 porcelain 子命令有效，作 wrapper 补充层） |
| §7.5 lock_files.py 激活 | AI 改文件前 acquire/用后 release，经 RULE-GIT-SAFE 规则 3/4 推动 | ✅ production（v2.4.0：§7.28 Mutex+原子写+`--ttl` 已施工） |
| §7.6 session_worktree 强制 | 每 AI 独立 worktree + 分支；GATE-WORKTREE-REQUIRED 软门禁（阈值可调 5→3，见 §10） | ✅ production（五命令齐备） |

### 7.7 施工项 7：git wrapper 安装脚本（P0，**待施工——最关键缺口**）

**目标**：创建 `scripts/install_git_safety_wrapper.ps1`，一键安装/卸载 PowerShell git wrapper（§7.1 全部函数集 + §7.32 Session ID 注入）。

**验收标准**（2026-08-14 核实：脚本不存在，L1/L2/L5/L6 实际未激活——P0 最优先）：新会话 `Get-Command git` 显示 `Function`；`git clean -fd` BLOCKED 且无文件被删；`Remove-Item -Recurse -Force <非TEMP>` BLOCKED；$PROFILE 含两个 marker；`~/.zephyr_audit/audit_*.jsonl` 有记录产生。

**功能**：
- 检测 `$PROFILE` 是否存在，不存在则创建（**追加**到现有 profile 末尾，不覆盖——现有约 1799 字节）
- 幂等：搜索 marker 注释 `# >>> git-safety-wrapper >>>` 判断是否已安装
- 检测 git 真实路径（`Get-Command git.exe`，写入 `ZEPHYR_REAL_GIT_PATH` 或硬编码进生成代码）
- 将 §7.1 函数集追加到 `$PROFILE`（`Remove-Item` 代理按 §7.1.4 用 `ProxyCommand::Create()` 生成后插入拦截逻辑）
- 在 `$PROFILE` 顶部写入 Session ID 注入一行（§7.32）
- 支持 `-Uninstall`（按 marker 注释块删除）

### 7.10 + 7.27 施工项 10/27：审计日志设施（L5，P0，**待施工——v2.1.0 简化版**）

**目标**：wrapper 所有拦截/放行写入 JSONL 审计日志，支持事后追溯。实现已并入 §7.1.1 的 `_ZephyrAuditLog` 函数。

**v2.1.0 简化裁定**：v1.x 的命名 Mutex + StreamWriter 串行化是为"多进程并发写同一文件"设计；审计日志是 append-only 事后追溯，非关键状态（Claude Code `.claude.json` 423 次损坏是 read-modify-write 状态文件，性质不同）。**改为每 session 独立文件，无需 Mutex**，离线合并。

| 项 | 值 |
|---|---|
| 日志目录/文件 | `$env:USERPROFILE\.zephyr_audit\audit_{yyyyMMdd}_{sessionId}.jsonl`（按天 + 按 session 分割） |
| 格式/字段 | JSONL；`timestamp`/`action`/`command`/`reason`/`session`/`pid`/`escape_hint`(可选) |
| action 值 | `ALLOWED`/`BLOCKED`/`HARDBLOCKED`（远期可加 `REDIRECTED`/`FAIL_OPEN`） |
| 保留策略 | 30 天后自动清理（远期 audit_log_rotator） |

**查询**（PowerShell 一行，查看今天的阻断记录）：
```powershell
Get-Content "$env:USERPROFILE\.zephyr_audit\audit_$(Get-Date -Format yyyyMMdd)_*.jsonl" |
    ConvertFrom-Json | Where-Object { $_.action -ne 'ALLOWED' }
```

### 7.13 施工项 13：d6_security 接入 pre-commit config（P0，**待核实/待施工**）

> **背景**：`detect_git_dangerous.py`/`detect_shell_dangerous.py`/`detect_permanent_file_deletion.py` 等脚本存在但曾未在 .pre-commit-config.yaml 注册——静态检测层实际缺失。接入后三层闭环（规则层 RULE-THREE + 静态检测 pre-commit + 运行时 wrapper）才成立。

**接入清单**（添加到 .pre-commit-config.yaml）：

| Hook ID | 脚本 | 功能 |
|---|---|---|
| `gate-detect-git-dangerous` | `scripts/governance/d6_security/detect_git_dangerous.py` | 检测代码/文档中的危险 git 命令（ABS-26/27/28） |
| `gate-detect-shell-dangerous` | `scripts/governance/d6_security/detect_shell_dangerous.py` | 检测代码中的危险 shell 命令（ABS-38/39） |
| `gate-detect-permanent-deletion` | `scripts/governance/d6_security/detect_permanent_file_deletion.py` | 检测 ttl:permanent 文件删除（PS-STD-012 V1） |

```yaml
# 三个 hook 同构（language: system / pass_filenames: true）；git/shell 两个加 always_run: true，deletion 加 stages: [pre-commit]
- id: gate-detect-git-dangerous
  name: 检测危险 git 命令
  entry: python scripts/governance/d6_security/detect_git_dangerous.py
  language: system
  pass_filenames: true
  always_run: true
```

**验证**：commit 一个含 `git reset --hard` 的文档 → 被 `gate-detect-git-dangerous` 阻断。

### 7.14 施工项 14：Wrapper fail-open 策略（P0，**待施工——随 §7.1 一并安装**）

**裁定**：非 CRITICAL 命令 fail-open（wrapper 出错放行并记 FAIL_OPEN 审计），CRITICAL 命令（format/vssadmin delete/diskpart 等）fail-closed（出错也必须阻断——系统级破坏不可逆）。

**实现模板**（应用于 §7.1 所有 wrapper 函数）：
```powershell
function git {
    try {
        # ... 拦截逻辑（§7.1.1 Part A）...
    } catch {
        # fail-open: wrapper 出错时透传给真实 git，不阻断工作
        _ZephyrAuditLog -Command "git $($args -join ' ')" -Action 'FAIL_OPEN' -Reason "wrapper error: $_"
        & $_realGit @args
    }
}
```

### 7.17.2 施工项 17（保留部分）：`.git` 目录写入运行时硬阻断（L4，P0，**待施工——随 §7.1 一并安装**）

> §7.17.1 自动变量碰撞检测 v2.1.0 deprecated（改为 §7.2 RULE-GIT-SAFE 规则第 6 条）。本节仅保留 .git 阻断。

**算法**：在所有写文件类 wrapper（`Remove-Item`/`rd`/`del`/`rm`/`Set-Content`/`Out-File`/`Add-Content`/`New-Item`）中检测目标路径是否在 `.git/` 下：

```powershell
function _ZephyrCheckGitDirProtection {
    param([string[]]$Paths)
    foreach ($p in $Paths) {
        if ($p) {
            # PS 5.1 兼容：不支持 ?. 运算符
            $_resolvedPath = Resolve-Path $p -ErrorAction SilentlyContinue
            $resolved = if ($_resolvedPath) { $_resolvedPath.Path } else { $null }
            if ($resolved -and $resolved -match '[\\/]\.git[\\/]' -or $resolved -match '[\\/]\.git$') {
                Write-Host "[SAFE] HARDBLOCKED: 写入 .git 目录 — $resolved" -ForegroundColor Red
                _ZephyrAuditLog -Command "write to $resolved" -Action 'HARDBLOCKED' -Reason '.git 目录写入永久阻断（Zed 1.14.2 设计）'
                return $false
            }
        }
    }
    return $true
}
```

**放行例外**：git 命令本身（内部写 `.git` 合法——只拦截 PowerShell 原生文件写入）；`.git/hooks/` 的用户授权修改（逃生通道 `& $_realSetContent ...`）。

**与 immutable_core.yaml 的关系**：yaml 是 commit 时检查（配置层），本算法是运行时拦截（执行层），两层叠加。

### 7.23 施工项 23：git 专属危险命令阻断（L1，P0，**待施工——v2.1.0 简化为 4 命令**）

> **v2.1.0 简化（20+→4 命令）**：v1.x 的 20+ 命令中 16+ 防 adversarial RCE（`config core.hooksPath`/`update-index --cacheinfo`/`notes add`/`hash-object -w`/`submodule add` 等）——AI 不会主动写 `git config core.hooksPath /tmp/evil`。**只保留 4 个 AI 易误用命令**：`git filter-branch`（历史重写，官方弃用）/`git filter-repo`（历史重写+force push）/`git reflog expire`（抹除 forensic 证据）/`git gc --prune=now|all`（物理删 unreachable 对象；`gc` 无 --prune、`reflog show` 只读放行）。规则明细已并入 §7.1.1 表（末 3 行），实现代码已并入 `git()` 函数。

### 7.28 施工项 28：lock_files.py registry.json 并发安全升级（P0，**✅ 已施工——v2.4.0 落地**）

> **v2.0.0 部分保留**：过渡方案（registry.json + 命名 Mutex + 原子写）保留施工；SQLite 迁移最终方案 deprecated（Task Board 已用 SQLite，无需重复迁移）。
> **v2.2.0 代码核实**：当前 lock_files.py 无 Mutex、无原子写——26 session 并发 read-modify-write `registry.json` 必然丢锁/双锁（§3.12 grite C2 + PowerShell #24774 证实）。
> **v2.4.0 施工落地（2026-08-14 深夜）**：`_registry_mutex()`（CreateMutexW `Global\ZephyrLockFilesRegistry`，WaitForSingleObject 5000ms，WAIT_ABANDONED 获所有权，finally ReleaseMutex+CloseHandle）；所有 RMW（_add_to_registry/_remove_from_registry/release_all/cleanup）进临界区，超时 DENIED+acquire 回滚锁目录防半锁；tmp+flush+fsync+os.replace 原子写。验收：tests/git/test_lock_files_ttl_mutex.py 9 用例（含 26 线程并发无丢锁+Mutex 超时回滚）。

**过渡方案实现要点**：
1. **Windows 全局命名 Mutex 串行化 RMW**：`CreateMutexW('Global\ZephyrLockFilesRegistry')` + `WaitForSingleObject(5000ms)`，临界区内完成"读 → 检查 → 写 registry.json"，finally 中 `ReleaseMutex`+`CloseHandle`；超时返回 DENIED。
2. **temp + rename 原子写**：先写 `registry.json.tmp`（flush+fsync），再 `Path.replace()`（Windows 原子替换）防崩溃半成品。

### 7.32 施工项 32：Session ID 注入（L6，P0，**待施工——v2.1.0 简化版**）

> **v2.1.0 简化**：Trae SessionStart hook + init-session.ps1 + TRAE_ENV_FILE 机制复杂且 hook 可行性是开放问题。简化为 **`$PROFILE` 顶部一行**，由 §7.7 安装脚本写入：

```powershell
# $PROFILE 顶部——Session ID 注入（v2.1.0 简化版）
if (-not $env:ZEPHYR_SESSION_ID) {
    $env:ZEPHYR_SESSION_ID = [guid]::NewGuid().ToString()
    $env:ZEPHYR_SESSION_START = (Get-Date).ToString('o')
}
```

每 session 启动自动生成 UUID，足够审计日志（§7.10）与 Task Board（§11.3.3）的身份识别。

### 7.33 施工项 33：AI RunCommand 通道防护——profile-snapshot 注入 + AI 会话归因（L1-L6 对 AI 通道等效恢复，tracker #58，2026-08-15 闭环）

**机制根因（实证）**：Trae AI 的 RunCommand 由 `agent-tool-host.exe`（Rust 二进制）spawn `powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command "<preamble>;<用户命令>"`——`-NoProfile` **硬编码在二进制内**（strings 实证），settings.json 无对应配置键（`AI.agent.v2.*.shellExecMode`/`allowList` 仅控制执行模式与白名单），故四个 $PROFILE 变体对 AI 通道全部被抑制。

**注入点（实证）**：硬编码 preamble 内 dot-source 一个**每 toolhost 进程级**环境快照文件——`%USERPROFILE%\.trae-cn\toolhost\native-runcommand-snapshots\process-<pid>-<ts>\powershell-profile-snapshot.ps1`。向其中追加一行 wrapper dot-source 即对**该 toolhost 进程后续所有 RunCommand**恢复 L1/L2/L4/L5/L6 全层（2026-08-15 PoC 实证：git=Function、clean -fd BLOCKED、status 透传、审计落盘）。

**候选方案评估结论**：a. Trae 配置层去 -NoProfile——**不可行**（硬编码无开关）；b. AllUsers profile 迁移——**不可行**（-NoProfile 抑制全部 4 变体）；c. 机器/用户级环境变量注入——**部分采用**（归因语义改由 wrapper 内父进程锚定实现，见下；静态机器级变量不适合每会话 UUID）；d. PATH 前置 git shim——**否决**（系统 PATH 段优先于用户段，需动系统 PATH 顺序，全机影响面过大）；e. 规则层强制 git_guard——**保留为补充**（非强制机制）；f. **profile-snapshot 注入——采纳**（机制内生、零 Trae 文件修改、随 IDE 升级自然失效可重注入）。

**裁定（三项落地）**：
1. **注入**：`scripts/ensure_ai_wrapper_injection.ps1` 幂等扫描全部快照目录（含 `TRAE_NATIVE_RUN_COMMAND_SNAPSHOT_DIR`/`.trae-cn`/`.trae` 三候选根），对缺 marker（`ZEPHYR-AI-WRAPPER-INJECT`）的快照追加 wrapper dot-source 行；支持 `-Remove` 卸载；`-SnapshotRoot` 供测试。
2. **保活**：计划任务 `ZephyrAlpha-AI-Wrapper-Inject`（每分钟，当前用户，`powershell -NoProfile -WindowStyle Hidden -File`）补注入——agent-tool-host 重启（IDE 重启等）生成新快照目录后**最长 1 个调度间隔的裸奔窗口**（减配声明，实测 toolhost 进程常与 IDE 同寿，窗口出现频率低）。
3. **AI 会话归因（§7.32 扩展）**：wrapper Session 块检测父进程为 `agent-tool-host.exe` 时，`ZEPHYR_SESSION_ID = ai-<toolhost_pid>-<toolhost启动yyyyMMddHHmmss>`（同一 IDE 工具宿主下全部 AI 命令共享稳定标识，聚合到单一审计文件；每个 RunCommand 一短命进程若用 UUID 将一命令一文件），审计条目新增 `channel` 字段（`ai-runcommand`/`interactive`）。**已知特性**：AI 会话内 spawn 的子进程（pytest 等）继承 ZEPHYR_SESSION_ID——归因聚合为特性，测试需剔除继承值隔离（两测试文件 `_run_ps` 已适配）。

**验收**：`tests/governance/test_ai_channel_wrapper.py` 15 用例（注入幂等/卸载/缺根静默/fail-closed、快照端到端 git=Function/clean+read-tree BLOCKED/status 透传/Remove-Item 拦截、假 toolhost 父进程 ai- 归因、审计 channel 字段+单文件聚合、计划任务注册）全绿；既有 80 用例（wrapper 45+git_guard 16+lock 19）不回归；人工终端实证不回归。**重评估触发条件**：Trae 升级改变 preamble/快照机制（监测点：快照路径与 dot-source 行）；本机引入 pwsh 通道（pwsh-profile-snapshot.ps1 变体未覆盖）。

**新陷阱登记（本批实证）**：Trae IDE 文档层脏缓冲区会导致 Edit/Write 工具修改不落盘且 Read 回显为缓冲区内容（mtime 不变可识别）——关键施工文件改后须以 `Select-String`/git diff 从进程外核实落盘，必要时 PowerShell 直写。

### 7.3 / 7.8 / 7.9 / 7.12 配套确认与维护项（非路线图项，按需推进）

| 施工项 | 内容 | 状态 |
|---|---|---|
| §7.3 project_memory 确认 | 灾难教训（根因+规则+时间线）已写入 memory/project_memory.md | ✅ 已记录，持续确认 |
| §7.8 AI_review_instructions §0 内嵌 | 规则 9/10 已入 §0 通用规则；各 AI 指令块约束节同步未完成 | ⚠️ 部分完成 |
| §7.9 Trae IDE 开发约束专节 | Trae 约束全集（无 hooks/PS 5.1/加载 $PROFILE/.trae/rules 入口/.traeignore 盲区/共享 $PROFILE+工作目录）——已提炼进 §4.1/§5.3 | ✅ 设计前提，无需施工 |
| §7.12 setup_git_guard_aliases.py 修复 | DANGEROUS_SUBCOMMANDS 补 `clean`——alias 失效后降格维护性 | ⚠️ 低优先级 |

### 7.D `deprecated` 施工项一览（v2.0.0 14 项 + v2.1.0 3 项，共 17 项——正文已删除）

| 项号 | 名称 | 废弃理由（一句话） |
|---|---|---|
| §7.15 | 错误分类 STOP/ALTERNATIVE 格式 | AI 提示工程过度——简单 BLOCKED 消息已够（v2.1.0） |
| §7.16 | Circuit Breaker 模式 | 无 adversarial 场景，AI 不会无限尝试危险命令（v2.0.0） |
| §7.17.1 | 自动变量碰撞检测 | 30+ 变量清单过度——改为 RULE-GIT-SAFE 一条规则（v2.1.0） |
| §7.18 | Shell 反混淆归一化层 9 策略 | 防 shell 注入——AI 不会混淆命令，regex 已够（v2.1.0） |
| §7.19 | SafeFix block+suggest | AI 提示工程层，规则足够（v2.0.0） |
| §7.20 | RiskChain 攻击链追踪 | 防 AI 绕过自己——无 adversarial 场景（v2.0.0） |
| §7.21 | Risk-tiered fail mode 四级 | 分层过度——fail-open/closed 两级已够（v2.0.0） |
| §7.22 | 跨工具/跨 shell 绕过检测 | 防 AI 主动绕过——无 adversarial 场景（v2.0.0） |
| §7.24 | symlink/junction + TOCTOU 防护 | P/Invoke 复杂度高且无场景（v2.0.0） |
| §7.25 | git hook 信任链 + reflog 不可变 | 单人项目无恶意 actor（v2.0.0） |
| §7.26 | Script Block Logging 4104 | 企业级方案，个人项目过重（v2.0.0） |
| §7.28.3 | lock_files.py 迁 SQLite 最终方案 | 与 Task Board SQLite 重复（过渡方案保留）（v2.0.0） |
| §7.29 | 跨 session GovernanceStore | 与 Task Board 重复造轮子（v2.0.0） |
| §7.30 | 共享规则文件完整性防护 | git 版本控制已够（v2.0.0） |
| §7.33 | Named Pipe Coordinator Daemon | 单点故障 + SQLite WAL 已够（v2.0.0） |
| §7.34 | Session 生命周期管理 | 依赖 §7.33 连带废弃；锁 TTL 60min 已覆盖崩溃场景（v2.0.0） |
| §7.35 | Wrapper 热重载+跨项目隔离 | 单项目无跨项目隔离需求（v2.0.0） |
| §7.36 | AST 命令分析替换 regex | 防 adversarial 注入——regex 已够（v2.0.0） |

**deprecated 根因总结**：v1.x 把"AI 误操作"（合法错误）误判为"AI 恶意攻击"（adversarial）。单人单账户 AI 协作开发中 AI 是协作者不是攻击者——真实场景只有两类：①AI 误删文件（§7.1 wrapper 拦截）②多 AI 共用工作区冲突（§11 三件套协调）。

### 7.31 施工项 31：git 并发操作串行化（P1，非路线图项，保留要点）

> 未被 v2.0.0/v2.1.0 deprecated，但不在 §13 路线图 8 项内——作为 wrapper 可选增强保留要点。

三要点：①commit 前 `git diff --cached --stat` 验证暂存内容（防 f2t.jp 式"add A B 却 commit 进 C D E"）；②`$PROFILE` 设 `$env:GIT_OPTIONAL_LOCKS='0'`（防 watcher 抢 .git/index.lock）；③GitCommitGateway single-flight 命名 Mutex（`Global\ZephyrGitCommitGateway`，30s timeout）串行化所有 commit。

### 7.11 施工项 11：Trash Redirect 算法（远期，不施工——仅保留思想）

对非 CRITICAL 删除命令（Remove-Item -Recurse -Force/rd /s/del /s/rm -rf）不阻断，而用 `Microsoft.VisualBasic.FileIO.FileSystem` DeleteDirectory/DeleteFile + `SendToRecycleBin` 重定向到回收站——AI 不卡住、文件可恢复、审计记 `action=REDIRECTED`。§7.1.2 的 BLOCKED 已够安全，trash redirect 是体验优化，Phase 2 后评估。

## 8. 验证（v2.2.0 压缩——仅保留当前施工范围内项的验证）

### 8.1 PowerShell wrapper 验证——git 命令（§7.1.1 + §7.23 安装后执行）

| 测试 | 预期结果 |
|---|---|
| `git clean -fd` / `reset --hard` / `checkout -- f` / `checkout .` / `restore f` / `rm f` / `branch -D x` / `push --force` / `stash` | BLOCKED，返回 1，无文件被删 |
| `git clean -n` / `stash list` / `restore --staged f` / `rm --cached f` / `branch -d merged` / `push --force-with-lease` / `checkout <b>` / `checkout -b x` / `reset --soft HEAD~1` / `add/commit/status/log/diff` | 放行 |
| `git filter-branch` / `filter-repo` / `reflog expire --expire=now` / `gc --prune=now` | BLOCKED（§7.23 四命令） |
| `git gc`（无 --prune） / `reflog show` | 放行 |
| `& 'C:\Program Files\Git\cmd\git.exe' clean -fd` | 逃生通道，直接执行 |

### 8.2 PowerShell 原生破坏性命令验证（§7.1.2 安装后执行）

| 测试 | 预期结果 |
|---|---|
| `Remove-Item -Recurse -Force <dir>` / `rd /s /q <dir>` / `del /s /q *.tmp` / `rm -rf <dir>` | BLOCKED，无文件被删 |
| `Remove-Item temp.txt` / `Remove-Item -Force temp.txt` / `rd <dir>` / `del old.txt` / `rm temp.txt` | 放行（非递归强制） |
| `Remove-Item -Recurse -Force $env:TEMP\old\` / `rm -rf $env:TEMP\cache\` | 放行（临时目录） |
| `format d:` / `vssadmin delete shadows /all` / `diskpart` / `iex "rm x"` | HARDBLOCKED，无逃生通道 |
| `& $_realRemoveItem -Recurse -Force d:\test\` / `& cmd /c "rd /s /q d:\test\"` | 逃生通道，直接执行 |

### 8.3 .git 阻断 + 审计日志 + 规则验证

| 测试 | 预期结果 |
|---|---|
| `Remove-Item -Recurse -Force .git/` / `Set-Content .git\config "..."` / `New-Item .git\hooks\x` | HARDBLOCKED（§7.17.2） |
| `git commit` / `git add .` | 放行（git 命令不触发 .git 保护） |
| 阻断后查 `~/.zephyr_audit/audit_{date}_{session}.jsonl` | 含 BLOCKED/HARDBLOCKED 记录，JSON 可解析 |
| 新 AI 对话读 AGENTS.md / .trae/rules/project_rules.md | 看到 RULE-GIT-SAFE（§7.2） |
| RunCommand 中 `Get-Command git` / `Get-Command Remove-Item` | 显示 `Function` 类型（§7.7 安装成功标志） |
| $PROFILE marker | `# >>> git-safety-wrapper >>>` 与 `# >>> powershell-destructive-guard >>>` 存在 |

### 8.4 三件套 + 并发安全验证（Phase 2）

| 测试 | 预期结果 |
|---|---|
| `lock_files.py acquire file.md AI-01` → AI-02 acquire 同文件 | ACQUIRED → DENIED |
| `acquire doc.md AI-01 --ttl 60`，61 分钟后 check | FREE（需 §11.2.2 扩展落地后） |
| 26 session 并发 acquire/release 后 registry.json | 无损坏无丢锁（需 §7.28 落地后） |
| `session_worktree.py create/exec/merge/abort/list` | 五命令正常（✅ 已 production） |
| `task_board.py create/claim/start/complete`；AI-02 claim 已认领任务 | 状态机正确转换，重复认领 DENIED（✅ 已重建验收通过，tests/governance/test_task_board.py 17 用例） |
| commit 含 `git reset --hard` 的文档 | 被 `gate-detect-git-dangerous` 阻断（§7.13 接入后） |

## 9. 不做什么

| 不做 | 理由 |
|---|---|
| 不编译 Go/Rust 二进制 wrapper | 过度工程——PowerShell 函数足够 |
| 不删除 .git/config 中的 alias 配置 | 无害（不生效≠有害），保留意图记录 |
| 不用 git hooks 拦截 clean | git 没有 pre-clean hook |
| 不引入 Claude Code PreToolUse hooks | Trae IDE 不支持 PreToolUse hooks |
| 不做定期 auto-commit | 可能 commit 垃圾文件，远期考虑 |
| 不删除 git_guard.py | 直接调用时有效，作 wrapper 补充层保留 |
| 不强制所有 AI 用 session_worktree | P1 优先级，先靠 wrapper+规则防护 |
| 不为 CRITICAL_BLOCKS 命令提供逃生通道 | format/vssadmin delete/diskpart 等系统级破坏永远阻断——AI 开发无合法需求 |
| 不覆盖 `robocopy` 函数 | 合法构建工具，`/mir` 滥用低频——远期评估 |
| 不实现密钥模式检测 | pre-commit 已有 `detect-private-key-local` hook 覆盖 |
| 不适配其他 AI 工具（Claude Code/Cursor/Codex） | 项目 100% Trae IDE 开发 |
| 不引入沙箱/容器隔离 | Windows 无 Seatbelt 等效物；Docker/WSL 对量化开发过重 |
| 不施工 safe-rm 三层分类 | 需逐文件 git status 判断，复杂度高——两层方案已够 |
| 不重复实现 d6_security 已有检测 | wrapper 只做运行时拦截，静态检测复用 d6_security（§7.13） |
| 不实现 tokenize-then-check / AST 分析 | 为 adversarial 场景设计——单人 AI 协作无场景（v2.0.0） |
| 不引入 Defender AiAgentProtection / MXC / WDAC+CLM / Job Object | 企业级 Windows 方案，个人项目过重——远期评估 |
| 不引入 PSReadLine 集成 | 仅交互式 REPL 工作，对 AI agent 脚本无效 |
| 不引入跨 session RiskChain / CoAgent MTPO / Raft/Paxos / Redis 锁 | 单机 SQLite CAS 足够，分布式是过度工程 |
| **v2.0.0 deprecated 14 项 + v2.1.0 deprecated 3 项** | 见 §7.D——adversarial/7×24 设计偏离单人 AI 协作实际诉求 |
| **v2.0.0 删除：§14 灾难恢复、§15 性能评估** | 见 §14/§15 删除声明 |

## 10. 开放问题

**已闭环（折叠）**：git 真实路径自动检测（注册表>硬编码>fallback，§7.1）；wrapper 循环调用（用 `$_realGit` 完整路径）；non-interactive 脚本影响（§7.1.5 已评估 4 场景）；PowerShell 原生命令拦截（§7.1.2）；复合命令拆分（§7.1.3 PS 5.1 天然处理）；审计日志需要性（§7.10）。

**未闭环**：

| 问题 | 决策状态 |
|---|---|
| wrapper 对 `git rebase`/`merge` 内部 git 子进程是否安全 | 待测试（子进程 git.exe 不经函数，应安全） |
| `backup.ps1` 清理旧备份（`-Recurse -Force` 非 TEMP）被阻断 | ✅ 已闭环（2026-08-14 晚核实：当前代码仅单文件 -Force 无 -Recurse 组合，wrapper 不拦，无需修复） |
| pre-commit 框架 stash unstaged 适配 | 待处理：逃生通道或环境变量绕过 |
| `iex`/`Invoke-Expression` 别名级绕过 | 待施工：`iex` 是别名需单独函数覆盖 |
| GATE-WORKTREE-REQUIRED 阈值 5→3 | 待评估 |
| 定期 push 远程作最终备份 | 待评估（origin/dev 大量 commits 未 push） |
| setup_git_guard_aliases.py 补 clean | ✅ 已闭环（2026-08-14 晚，21f447c1：DANGEROUS_SUBCOMMANDS 补 clean 对齐 git_guard 7 命令） |
| `robocopy /mir` 函数覆盖 | 远期评估 |
| `.git` 阻断是否影响 git 子进程 | 待测试（应安全） |
| lock_files.py TTL 五命令扩展 | 待施工（当前无 --ttl，2026-08-14 核实） |
| task_board.py 重建 | ✅ 已闭环（2026-08-14，AI-GIT-001，0e5ed3b9） |
| wipe 事故治本 S1-S6 | ✅ 已闭环（2026-08-14 AI-GIT-001 完工，当日 merge 回 dev d8f94d4f2b；S2 四证首次真实清理走通，证1-4 全 PASS——tracker §六 #54） |

## 11. 多 AI 协调层施工方案（Git Worktree + File Lock(TTL) + Task Board 三件套）

> **v2.3.0 状态**：Worktree 与 File Lock 已 production；Task Board（task_board.py）2026-08-14 已由 AI-GIT-001 按 §11.2.3 规格重建（wipe 事故丢失后）。本节保留 v2.1.0 简化版规格要点作维护依据，施工过程细节（§11.4/§11.5）已折叠。

### 11.1 背景与目标

- 26 路 AI 在 Trae 上并发（实为 26 个 Trae IDE 窗口并发，窗口内单 SOLO agent 循环），共用同一 working directory
- 多 AI 共用主工作区必然 silent data loss（A 写 B 覆盖，无冲突标记）——grite 论文 C2 实测证实 file-based tracker 静默丢并发写
- **目标**：Git Worktree 物理隔离（每 AI 独立 checkout+分支）+ File Lock TTL（60min 自动过期，防崩溃 agent 永久阻塞）+ Task Board（SQLite CAS 状态机，协调任务认领）
- 业界事实标准（2026）：Conductor/Superset/Claude Code Agent Teams 均以 git worktree 作隔离原语；agent-sync/agent-coord 采用 file lock TTL + task board；单机 SQLite CAS 足够，无需分布式共识

### 11.2 三件套规格要点（v2.1.0 简化版——重建/维护依据）

#### 11.2.1 Git Worktree（✅ production——scripts/session_worktree.py）

- 目录：`d:\ZephyrAlpha\.worktrees\<AI-ID>\`（.gitignore 排除），独立分支 `ai/<session-id>/<task-id>`
- 五命令：`create <AI-ID> <task-id>` / `exec <AI-ID> -- <cmd>`（透明 cd）/ `merge <AI-ID> --to main`（**必须用户显式确认**）/ `abort <AI-ID>` / `list`
- v2.1.0 简化：去 7 天告警，merge 后即 abort 清理

#### 11.2.2 File Lock TTL（✅ production 基础版——scripts/lock_files.py；TTL 扩展待施工）

- 现有：acquire/release/check 三命令（2026-08-14 核实，无 TTL 参数）
- v2.1.0 目标规格（五命令）：`acquire <file> <session> --ttl 60 --task <id>` / `release` / `check` / `list --session <id>` / `cleanup`（清过期锁，post-commit hook 调用）
- TTL 60min 到期自动释放（registry.json 含 `expires_at`）；**去 heartbeat**（审查任务 30-60min，TTL 已够）
- 并发安全：见 §7.28（Mutex + 原子写，待施工）

#### 11.2.3 Task Board（❌ 丢失，重建中——AI-GIT-001）

- SQLite `d:\ZephyrAlpha\.runtime\task_board.db`，WAL 模式
- 表：`tasks(task_id PK, title, description, status, claimed_by, claimed_at, created_at, completed_at, metadata_json)` + `task_events(event_id, task_id, event_type, actor, timestamp, payload_json)`
- CAS 原子认领：`UPDATE tasks SET claimed_by=?, claimed_at=datetime('now'), status='claimed' WHERE task_id=? AND (claimed_by IS NULL OR claimed_at < datetime('now','-60 minutes'))`——`changes()>0` 即成功
- 状态机（v2.1.0 精简三态）：`pending → claimed → completed`（去 blocked/abandoned/epoch——放弃就删 task 重新 create）
- CLI：`create --title` / `claim <id> --session <s>` / `start <id>` / `complete <id> --result` / `list --status|--session` / `show <id>`（含事件历史）
- 与 #ARCH 议题联动：每议题对应一个 task；认领议题前必须先 task_board 登记

### 11.3 与现有设施的集成 + 不做什么

- worktree 物理隔离 = 即使 AI 在自己 worktree 跑 `git clean -fd`，主工作区不受影响（与 #ARCH-GIT-CLEAN-GUARD-FIX 联动）
- `git_commit_gateway.py` 可扩展为检查 task_board 状态（commit 前需有对应 in_progress task）
- **不做**：Redis 分布式锁（SQLite 足够）/自动 presence heartbeat/messaging 系统/web UI/OAuth/RBAC——均过度工程

## 13. 施工路线图（v2.1.0 精简——8 施工项分 2 Phase；v2.2.0 标注施工状态）

> **v2.1.0 精简裁定**：12 施工项 / ~17 天 → **8 施工项 / 2 Phase / ~11 天**。
> **v2.2.0 状态核实（2026-08-14）**：Phase 1 项 1-7 **全部未落地**（install_git_safety_wrapper.ps1 不存在，wrapper 未装入 $PROFILE——P0 最关键缺口）；Phase 2 中 Worktree/File Lock 基础版已 production。
> **v2.3.0 状态（2026-08-14 定稿）**：Task Board 已由 AI-GIT-001 重建（0e5ed3b9）并随治理批 **merge 回 dev**（d8f94d4f2b）——Phase 2 三件套全部 production；Phase 1 项 1-7 仍全部未落地（待排期，不在本次施工范围）。
> **v2.3.1 状态（2026-08-14 晚，AI-GIT-001 第二批）**：**Phase 1 项 1-7 已全部施工落地**（worktree ai/AI-GIT-001/task-git-wrapper-phase1，commits 611227d5/21f447c1/d7844786）——§7.1 wrapper 函数集 + §7.7 安装脚本 + §7.2 RULE-GIT-SAFE（AGENTS.md + .trae/rules）+ §7.23 四命令（并入 git()）+ §7.17.2 .git 阻断（挂删除类）+ §7.10/7.27 审计（并入 _ZephyrAuditLog）+ §7.13 d6 三 hook 接入 + §7.14 fail-open + §7.32 Session ID；40 验收测试两轮全绿。**激活唯一剩余动作：merge 后跑 `powershell -File scripts/install_git_safety_wrapper.ps1`**。施工偏差如实登记：①§7.1.4 ProxyCommand 未采纳（手写 param 块够用）；②.git 阻断挂删除类 4 函数（写类暂缓）；③memo"函数优先于别名"假设证伪——PS 5.1 实为 Alias>Function，AllScope 别名需 Remove-Item Alias: 删除后函数才生效；④PS 5.1 吞裸 `--`，checkout 路径/分支区分改 rev-parse 校验。

### Phase 1: P0 生存级（立即施工，防灾难重演）

| 顺序 | 施工项 | 防御层 | 依赖 | 工作量 | v2.3.1 状态 |
|---|---|---|---|---|---|
| 1 | §7.1 wrapper 函数集（git 拦截 + Remove-Item/rd/del 覆盖） | L1+L2 | 无 | 2 天 | ✅ 已施工（611227d5，40 测试两轮全绿；PS5.1 别名/吞参修正） |
| 2 | §7.7 安装脚本 install_git_safety_wrapper.ps1 | - | §7.1 | 1 天 | ✅ 已施工（611227d5，幂等/卸载/自检；merge 后跑安装即激活） |
| 3 | §7.2 RULE-GIT-SAFE（AGENTS.md + .trae/rules/）+ §7.14 fail-open | L3 | 无 | 1 天 | ✅ 已施工（21f447c1；fail-open 并入 wrapper） |
| 4 | §7.23 git 危险命令 4 命令 | L1 | §7.1 | 0.5 天 | ✅ 已施工（并入 git() 函数，随 611227d5） |
| 5 | §7.17.2 .git 永久阻断 | L4 | §7.1 | 0.5 天 | ✅ 已施工（挂删除类 4 函数；写类暂缓，随 611227d5） |
| 6 | §7.27+§7.10 审计日志 + §7.13 d6_security pre-commit | L5 | §7.1 | 1.5 天 | ✅ 已施工（_ZephyrAuditLog 无 BOM JSONL + 三 hook 注册，21f447c1） |
| 7 | §7.32 Session ID 注入（$PROFILE 一行 UUID） | L6 | 无 | 0.5 天 | ✅ 已施工（并入 wrapper 头部，随 611227d5） |

**Phase 1 合计：~7 天**——完成后即具备 6 层核心防御（实现精简版）+ session 身份。

### Phase 2: P1 并发协调（Phase 1 完成后）

| 顺序 | 施工项 | 类别 | 依赖 | 工作量 | v2.2.0 状态 |
|---|---|---|---|---|---|
| 8 | §11.2.2 File Lock TTL 五命令 + §7.28 并发安全（Mutex+原子写） | 三件套-1 | §7.27 | 1 天 | ⚠️ 基础三命令 production；**TTL/§7.28 未施工** |
| 9 | §11.2.3 Task Board（SQLite CAS + WAL + 三态） | 三件套-2 | §7.32 | 1.5 天 | ✅ **已重建并 merge 回 dev**（2026-08-14，AI-GIT-001，0e5ed3b9→d8f94d4f2b，17 测试全过） |
| 10 | §11.2.1 Git Worktree（五命令） | 三件套-3 | §11.2.3 | 1.5 天 | ✅ production（五命令齐备） |

**Phase 2 合计：~4 天**——完成后即具备完整并发协调层（Task Board 防重复认领 + File Lock 防同时改 + Worktree 物理隔离）。

### 远期评估（不施工，仅记录）

| 项目 | 评估时机 | 说明 |
|---|---|---|
| §7.3 / §7.8 / §7.9 / §7.12 | Phase 1 后 | 配套确认/维护项，按需推进 |
| §7.11 Trash Redirect | Phase 2 后 | 回收站重定向，体验优化 |
| §7.31 git 并发串行化 | Phase 2 后 | wrapper 可选增强 |
| §11 三件套升级（Phi Accrual/heartbeat/epoch） | 远期 | v2.1.0 已砍，固定 TTL 60min + 基本 CAS 已够 |
| deprecated 17 项（§7.D） | 不评估 | 见 §7.D + §9 |

**总计：Phase 1 (7天) + Phase 2 (4天) = ~11 天**（历程：v1.x 37 天 → v2.0.0 17 天 → v2.1.0 11 天，减 70%）

### 关联施工（2026-08-14 wipe 事故治本，AI-GIT-001 承接）

2026-08-14 发生 worktree wipe 事故（三 worktree tracked 文件被物理清空，含未入 git 的 task_board.py）。裁定书提出治本方案 S1-S6，由 AI-GIT-001 会话施工，**不在本 memo 施工范围**：**S1** ops_guard 全原语删除拦截（扩展到所有文件删除原语）；**S2** worktree 清理四证 SOP；**S3** worker 日志落盘；**S4** 网关锚定修复。

> **v2.3.0 状态（2026-08-14 完工，当日 merge 闭环）**：S1-S6 + task_board 重建**已全部完工并 merge 回 dev**（d8f94d4f2b）——S1 ops_guard（3e2bb5ed70，42 红队向量 100% 拦截）；S2 四证 SOP + session_worktree 接入（69558c6479）；S3 worker stdio 落盘 + commit 后 status 快照（7383bcd1/95f94195/b36507d8）；S4 网关锚定（67abc2ea/a6453e58）；S5 锚点级联提示（7a08eb74）；S6 会话环境三件套随 create 备置（#ARCH-WORKTREE-ENV-001 已落地）；task_board.py 重建（0e5ed3b9）。施工中实证发现并修复 GATE-ROOT-TEMP-SWEEP 扫走 worktree .git 指针新事故机制（65a2e8a6，**已随 merge 在 dev 生效**）。merge 后统筹按四证 SOP 清理 AI-GIT-001 worktree——**证1-4 全 PASS，S2 首次真实清理走通**（refs/quarantine/AI-GIT-001 + 344MB bundle 双存证，tracker §六 #54）；遗留 #50（reconcile 测试污染生产审计日志）亦已修复闭环（e5d7b6decf）。完工细节见 tracker §六与 AI-GIT-001 完工反馈。

详见裁定书：[2026-08-14_ai-liq-001_worktree_wipe_incident_review.md](../../04_architecture_principles_decisions/2026-08-14_ai-liq-001_worktree_wipe_incident_review.md)。65 号 memo 不再视为 git 治理唯一真源——wipe 事故治本以裁定书为准。

## 14. ~~灾难恢复计划~~（v2.0.0 删除）

> **删除理由**：Daemon 崩溃恢复依赖已 deprecated 的 §7.33；SQLite 恢复用 `sqlite3 .recover` 是标准操作；RPO/RTO 是 SRE 话术对个人项目过度。容错由 SQLite WAL + JSONL append-only + git 版本控制天然提供。

## 15. ~~性能影响评估~~（v2.0.0 删除）

> **删除理由**：原评估的是 12 层防御开销——精简到 6 层后开销 <3ms/命令（git 命令本身 >100ms），无需逐层评估。并发由 SQLite WAL + busy_timeout 工业级方案承载。

## 16. 修订记录

| 版本 | 日期 | 改动 |
|---|---|---|
| 0.1.0-0.4.0 | 2026-08-11 | 初稿 + 第 1-4 轮审查：wrapper 路径检测、阻断规则细化、补入 git rm/checkout ./branch -D/push --force |
| 0.5.0-0.7.0 | 2026-08-11 | 第 5-7 轮：开源方案补充；设施盘点扩至 41 项 |
| 0.8.0 | 2026-08-11 | 第 8 轮：新增 §11 三件套（用户裁定全部加入） |
| 0.9.0 | 2026-08-11 | 第 9 轮：PowerShell 原生命令 gap（§7.1 重写 3 Part）+ Trae 约束专节 + 审计日志 |
| 1.0.0-1.4.0 | 2026-08-11 | 第 10-14 轮：trash redirect + d6 盘点 + ProxyCommand + fail-open + 错误分类 + Circuit Breaker |
| 1.5.0-1.6.0 | 2026-08-11 | 第 15-16 轮：第七/八轮搜索（GuardFall/AgentTrust/Codex $home/git CVE）+ PS 5.1 修复 + 扩至 16 层 |
| 1.7.0-1.9.0 | 2026-08-11 | 第 17-19 轮：并发病根 + 3 个 P0 并发修复 + Named Pipe daemon + AST + 36 项/37 天——膨胀至 293KB |
| 2.0.0 | 2026-08-12 | 精简大修：防御层 19→6，14 项 deprecated，§14/§15 删除，路线图→12 项/17 天 |
| 2.1.0 | 2026-08-12 | 第二轮精简：再砍 3 项 + 简化 6 项（4 命令/每 session 审计文件/$PROFILE 一行 UUID/三件套去 heartbeat+epoch+告警），→ 8 项/11 天 |
| 2.2.0 | 2026-08-14 | 文档实体精简（AI-GIT-001）：落实 v2.0.0/v2.1.0 精简裁定——§3 调研 14 轮折叠、§7 已 deprecated 17 项折叠为一览表（§7.D）、已施工项折叠为状态摘要、待施工项（§7.7 等）完整保留；施工状态经代码核实；新增 §13 关联施工小节指向 wipe 事故裁定书 S1-S6 |
| 2.3.0 | 2026-08-14 | **定稿**：frontmatter status→active（三轮裁定收敛稳定，active=裁定确认非施工完成，Phase 1 仍待排期——与 66 号 active 先例一致）；正文状态刷新——§4.1 #4/§8.4/§10/§11/§13 task_board 与 S1-S6 关联施工标注闭环（AI-GIT-001 完工：S1 3e2bb5ed70/S2 69558c6479/S3 7383bcd1+95f94195+b36507d8/S4 67abc2ea+a6453e58/S5 7a08eb74/task_board 0e5ed3b9） |
| 2.4.0 | 2026-08-14 | **深夜治理批全闭环**：①wrapper 激活（清除 $PROFILE 旧 v2.1.0 内联 block，保单一 dot-source；全新会话实证拦截+透传+审计+Session ID）；②§7.28+§11.2.2 施工落地（lock_files Mutex 全局命名锁+fsync 原子写+`--ttl` 五命令，9 测试）；③66 号裁定 7 plumbing 双层落地（wrapper+git_guard 拦 4 命令，SERIALIZER_MODE 白名单，45+16 测试）；④#56 闭环（sweep force-clean 四证语义审计、CLI heartbeat daemon 普及+对称 teardown，顺手治本 register pid=0/分支提取顺序/refs 前缀 3 bug）。**新边界发现**：Trae AI RunCommand 终端不加载 $PROFILE——wrapper 限人工交互终端（tracker #58） |
| 2.5.0 | 2026-08-17 | 结案报告追加 AI-FOPEN-001 施工波（fail-open B1+B2 全量：4 gate fail-open 分支接 log_gate_failure 留痕 / pg_probe PG 前置探针 / FRESHNESS 离线 24h 豁免 / verify_schema_health exit 2 优雅化，fa25c19e49，merge 8a872d0e59+48ce3d93cb，#ARCH-119 resolved）；frontmatter 版本对齐尾部（原 2.3.1 滞后于 2.4.0 行） |
