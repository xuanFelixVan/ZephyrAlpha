---
ttl: permanent
doc_type: architecture_view
title: Git 安全治理体系——alias 失效修复与多层防护施工总案（Trae IDE 专用）
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "1.4.0"
date: 2026-08-11
topic: git_safety_governance
scope: 07_trading_decision_architecture
related_issues:
  - "#ARCH-GIT-CLEAN-GUARD（git clean 误删防护）"
  - "#ARCH-GIT-CLEAN-GUARD-FIX（alias 失效修复+clean 自伤检测）"
  - "#ARCH-GIT-SELF-HARM-GUARD（reset/checkout 自伤防护）"
  - "#ARCH-GIT-CALL-BUDGET（git 调用预算优化）"
  - "#ARCH-AICOLLAB-001（Git Worktree + File Lock(TTL) + Task Board 三件套）"
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

# Git 安全治理体系——alias 失效修复与多层防护施工总案（Trae IDE 专用）

> 本备忘是 2026-08-11 灾难事件（AI 执行 `git clean -fd` 物理删除多个 untracked 文件）后的**根因分析 + 调研报告 + 裁定 + 治本施工方案**。
> **开发平台约束**：本项目 100% 围绕 **Trae IDE（编译器）** 开发——所有 AI session 通过 Trae IDE 的 RunCommand（PowerShell 5.1）执行命令，Trae IDE 不支持 PreToolUse hooks，AI 规则通过 `.trae/rules/` 目录注入。本方案的所有防护层均围绕此约束设计。
> 性质：**决策备忘 + 施工计划**混合体，按"背景→调研→现状→分析→裁定→施工→验证→不做→开放问题"组织。
> 管理规范见 [01_design_memo_management_spec](01_design_memo_management_spec.md)。
> 关联：[60_cross_cutting_cleanup](60_cross_cutting_cleanup.md)（跨切治理）｜[61_lifecycle_multi_ai](61_lifecycle_multi_ai.md)（多 AI 生命周期）

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G65 Git 安全治理体系（跨切治理层） |
| 创建 | 2026-08-11 |
| 优先级 | P0（灾难已发生，必须立即治本） |
| 状态 | draft v1.4.0（第13轮审查完成，Circuit Breaker三态状态机+第六轮全网搜索+AGENTS.md 12+RULE系统确认） |
| 设施总数 | 71 项（commit_gates 实际 100 个文件，v1.2.0 更正原"80+"） |
| 开发平台 | **Trae IDE（编译器）**——100% 围绕 Trae 开发，不支持 PreToolUse hooks，PowerShell 5.1 终端 |
| 上游 | [01_design_memo_management_spec](01_design_memo_management_spec.md)｜[60_cross_cutting_cleanup](60_cross_cutting_cleanup.md) |
| 下游 | 所有 AI session（安全规则约束）｜scripts/git_guard.py｜scripts/setup_git_guard_aliases.py｜AGENTS.md + .trae/rules/（永久规则）｜$PROFILE（PowerShell wrapper） |

## 2. 背景

### 2.1 灾难事件（2026-08-11）

某个并发 AI session 执行了 `git clean -fd`，物理删除了 `19_northbound_hold_snapshot.md`、`18_cold_archive_build_plan.md` 等多个 untracked 文件。git clean 直接物理删除（不进回收站），且这些文件从未 commit 过，git 无法恢复。

同时，多个 tracked 文件的未提交修改被丢弃（疑似 `git checkout --` 或 `git reset --hard`），导致 design_memos 下 20+ 篇文档的增强内容丢失，需要从 reflog 和对话历史重建。

### 2.2 直接根因

**双重失效**：

1. **git_guard.py 代码漏洞**：`_EXTRACTORS` 字典无 `clean` 条目 → `extractor=None` → 直接 `passthrough`，零拦截。clean 被标记为 DANGEROUS_SUBCOMMANDS 但没有实际处理逻辑。

2. **git alias 机制失效**：`git config alias.clean = !python scripts/git_guard.py clean` 配置存在，但 `git clean -fd` 直接执行了 git 内置 clean 命令，完全绕过 alias。实测确认：**git alias 无法覆盖内置命令**——这是 git 的设计行为，不是 bug。

### 2.3 系统性问题

alias 失效不仅影响 clean——`reset`/`checkout`/`restore`/`stash`/`revert`/`mv` 全部是 git 内置命令，它们的 alias 拦截**可能全部失效**。这意味着 git_guard.py 的整个 alias 拦截体系（7 个 DANGEROUS_SUBCOMMANDS）在 Windows git 2.48.1 上可能形同虚设。

## 3. 调研报告

### 3.1 git alias 无法覆盖内置命令——确认与溯源

**git 官方设计**：alias 只能为"不存在的命令名"创建快捷方式。当 alias 名与内置命令同名时，git 优先执行内置命令，alias 被忽略。

来源：
- [StackOverflow](https://wiki.cyberandi.synology.me/content/stackoverflow.com_en_all_2023-11/questions/52123145/)："Git doesn't allow you to override internal commands in aliases, because doing so would break any scripting that uses those internal commands."
- [Git Alias Builder](https://www.dev-toolbox.tech/tools/git-alias-builder) FAQ："Will aliases override built-in git commands? No. Git will not allow an alias to shadow a built-in command."

**结论**：通过 alias 拦截内置命令的方案从设计上就是无效的。需要替代方案。

### 3.2 GitHub 开源方案

| 项目 | 语言 | 机制 | 适用场景 | 星/活跃度 |
|---|---|---|---|---|
| [git-sentinel](https://github.com/balyakin/git-sentinel)（2026-04） | Go | 透明 git wrapper（PATH 拦截），阻断 `reset --hard`/`clean -fd`/`push --force`，**专门针对 AI coding agent** | 单人+AI 项目 | 新项目（1 commit） |
| [git-wrapper](https://github.com/jbrahy/git-wrapper)（2026-06） | Go | 透明 git shim，阻断 git-native 代码执行陷阱（hooks/fsmonitor/sshCommand） | 安全防护 | 活跃（17 commits） |
| [git-safe-toolkit](https://github.com/wangyaok1/git-safe-toolkit)（2025） | Shell | shell 函数覆盖 `git`，拦截 7 种危险命令，需输入确认词 | 通用 | 中等 |
| [mattpocock/git-guardrails](https://tessl.io/registry/skills/github/mattpocock/skills/git-guardrails-claude-code) | Shell | Claude Code PreToolUse hook，阻断 5 类 git 命令 | Claude Code 专用 | 活跃 |
| [FileSafe Guardian](https://github.com/rwzlestudio/claude-code-guardian)（2026-05） | 多语言 | 拦截文件操作 + 自动备份 + 回滚 | 多 AI 工具通用 | 新项目 |
| [dcg (Destructive Command Guard)](https://github.com/Dicklesworthstone/destructive_command_guard)（2026-08，**5.6k 星**） | Rust | PreToolUse hook + 50+ 安全包，SIMD 加速 <1ms，支持 Windows PowerShell 安装 | Claude Code/Codex/Gemini/Copilot/Cursor/Hermes/Grok | **最活跃**（1885 commits） |
| [ai-agent-secure](https://github.com/joelaniol/ai-agent-secure)（2026-07） | C# | Windows 专用，覆盖 git 危险操作 + CRCRLF 字节损坏 + git rate-limit + curl API 调用 | Windows AI agent | 活跃 |
| [SafeRun](https://github.com/Cocabadger/saferun-api)（2026-07） | Python | 三层防护：Shell Wrapper + API + GitHub 集成，Slack 通知手机审批 | CI/CD + 本地 | 活跃 |
| [git-safety-guard (terraphim)](https://claudeskills.club/skills/git-safety-guard-by-terraphim)（2026-01） | Shell | PreToolUse hook，regex 模式匹配 + allowlist，fail-open | Claude Code/Codex CLI | 中等 |

**核心洞察**：
1. 所有开源方案的共同模式是 **PATH 拦截**（在 PATH 中放一个叫 `git` 的脚本/函数，先于真正 git 执行）。这是唯一能从底层彻底拦截的方案。
2. **dcg（5.6k 星）是当前最成熟的方案**，但它是 PreToolUse hook（只拦截 AI 工具发起的命令），不是 PATH wrapper（不拦截终端直接执行的命令）。且不支持 Trae IDE。
3. **git-safety-guard 的放行规则值得参考**：放行 `git clean -n`（dry-run 安全）、`git push --force-with-lease`（更安全的 force push）、`git checkout -b`/`--orphan`（创建分支不修改文件）。
4. **dcg 阻断列表比本方案更完整**：额外阻断 `git branch -D`（强制删分支）、`git push --force`/`-f`（覆盖远程历史）、`git reset --merge`（可能丢失修改）。
5. **OpenClaw PowerShell 审批系统**有审计日志（JSON 格式写入所有阻断/放行操作）——本方案可借鉴。
6. **ai-agent-secure** 检测 CRCRLF 字节损坏——本项目遇到过 BOM 字符导致 frontmatter 解析失败的问题（2026-08-11 commit 1319325fac），可借鉴。

### 3.3 AI 编程社区实践

| 平台/社区 | 机制 | 效果 |
|---|---|---|
| **Claude Code v2.1.183**（2026-06） | 系统级阻断：非交互模式下 `git reset --hard`/`git clean -fd`/`git push --force`/`git checkout .` 4 命令直接阻断 | AI 无法执行这些命令 |
| **Claude Code Hooks** | `PreToolUse` hook + `permissions.deny` 配置 | 拦截 `Bash(git clean*)` 等 |
| **Cursor** | 终端命令需用户确认 | 人工确认 |
| **腾讯云开发者社区**（2026-06） | 总结：Claude Code 最完善（hooks+permissions），Cursor 最简单（确认），LangChain 工具级权限 | 多层防御 |
| **bswen.com**（2026-03） | 5 层防御：Hooks→Allowlists→Cloud Permissions→Manual Approval→Skills/Rules | 多层防御 |
| **Trae IDE** | **不支持 PreToolUse hook**（AGENTS.md L47 确认"Trae IDE 不可 hook"） | 无法在 AI 工具层拦截 |

**核心洞察**：Trae IDE 不支持 hooks，无法在 AI 工具层拦截。必须在 git 层面（PATH wrapper）或 shell 层面（PowerShell 函数）拦截。

### 3.4 量化社区实践

量化交易项目通常是单人或小团队开发，文件安全关注点：
- **回测代码丢失**：策略代码未 commit 被 git clean 删除（与本项目灾难相同）
- **数据管道配置丢失**：YAML 配置被 checkout 覆盖
- **社区共识**：①所有代码立即 commit ②不用 git clean ③用 git stash 替代 clean（stash 可恢复，clean 不可恢复）④定期 push 到远程作为备份

### 3.5 2026 年 8 月最新研究与实践（v0.9.0 全网搜索补充）

> 搜索时间：2026-08-11，覆盖 GitHub/掘金/Cursor 论坛/Claude Code 更新日志

#### 3.5.1 新发现的开源项目与平台更新

| 项目/平台 | 时间 | 关键发现 | 与本方案的关系 |
|---|---|---|---|
| **SafeRun Guard**（Cocabadger） | 2026-07-03 | Claude Code Plugin，243-test suite，**复合命令拆分**（`cmd1 && rm -rf /` 拆段独立检查），**密钥模式检测**（AWS keys/private keys/API tokens 写入前拦截），~20ms 延迟 | 复合命令拆分+密钥检测可借鉴 |
| **Claude Code v2.1.183** | 2026-06 | 非交互模式（`--non-interactive`）下系统级阻断 4 个 git 命令（`reset --hard`/`clean -fd`/`push --force`/`checkout .`）+ 3 个基础设施命令（`terraform destroy` 等）；交互模式仍弹确认框 | Claude Code 已内置非交互阻断——Trae IDE 无此能力，更需 wrapper |
| **opencode-fusion PR #12** | 2026-07-14 | **关键发现**：Windows 上 AI agent 几乎全部用 PowerShell，Unix `rm` 模式匹配从不触发。PR 补充了 `Remove-Item *-Recurse*`/`Remove-Item *-Force*`/`rd /s*`/`del /s*` 的 PowerShell/CMD 破坏性命令拦截 | **暴露本方案重大 gap**：我们的 wrapper 只拦 `git`，不拦 PowerShell 原生删除命令 |
| **Cursor 论坛事故** | 2026-04~07 | 多起 AI agent 执行 `rmdir /s /q`/`Remove-Item -Recurse -Force` 误删整个 C: 盘的严重事故；Cursor 官方确认 Windows 无 sandbox（macOS 有 Seatbelt） | 证实 PowerShell 原生命令的破坏力——必须拦截 |
| **cmd_command_execution_ai_agent** | 2025-10 | Python 实现的 Windows 命令安全检查器，**双重安全检查**（pattern match + critical block verify），**管道/链式命令拆分检测**（`|`/`&&`/`&` 拆段），DANGEROUS_PATTERNS 列表覆盖 35+ 模式 | 双重检查+管道拆分算法可借鉴；DANGEROUS_PATTERNS 列表可直接参考 |
| **AI-CLI-Safe-Mode** | 2026-02 | Claude Code 插件，阻止危险 git 和文件删除命令；支持 OpenCode/Gemini CLI/GitHub Copilot CLI | 多平台适配参考（本方案仅 Trae IDE） |

#### 3.5.2 关键洞察与对本方案的影响

**洞察 1（CRITICAL）：PowerShell 原生破坏性命令是本方案最大 gap**

当前 wrapper 只定义了 `git()` 函数拦截 git 命令。但 AI 完全可以用 PowerShell 原生命令绕过：

```powershell
# 以下命令全部绕过 git wrapper，直接删除文件
Remove-Item -Recurse -Force d:\ZephyrAlpha\docs\     # PowerShell 原生递归删除
rd /s /q d:\ZephyrAlpha\docs\                         # CMD 递归删除（已致多起 C: 盘全删事故）
del /s /q d:\ZephyrAlpha\docs\*.md                    # CMD 批量删除
rmdir /s /q d:\ZephyrAlpha                            # CMD 递归删除目录
robocopy /mir empty_dir d:\ZephyrAlpha\docs\          # 镜像同步删除目标文件
vssadmin delete shadows /all                          # 删除 Windows 卷影副本（备份！）
format d: /fs:ntfs /q                                 # 格式化磁盘
```

opencode-fusion PR #12 的 DB 审计发现：**Windows 上 AI agent 几乎全部用 PowerShell**，Unix `rm` 模式匹配从不触发。Cursor 论坛 2026-04~07 有多起 `rmdir /s /q` 误删整个 C: 盘的严重事故。

**结论**：必须扩展 wrapper 覆盖 PowerShell/CMD 原生破坏性命令（见 §7.1 重写）。

**洞察 2：复合命令拆分是必要算法**

SafeRun Guard 和 cmd_command_execution_ai_agent 都实现了复合命令拆分：将 `cmd1 && cmd2 | cmd3 ; cmd4` 按 `&&`/`||`/`;`/`|` 拆分为独立段，逐段检查。当前 wrapper 不处理复合命令——`echo ok && git clean -fd` 中的 `git clean -fd` 会被 PowerShell 的 `git()` 函数拦截（因为 `&&` 右侧的 `git` 调用会触发函数），但 `echo ok && Remove-Item -Recurse -Force x` 不触发任何拦截。

**结论**：wrapper 需增加复合命令拆分逻辑（见 §7.1 算法补充）。

**洞察 3：审计日志是合规必备**

dcg/SafeRun Guard/OpenClaw 审批系统都有 JSON 格式审计日志，记录所有阻断/放行操作。当前 wrapper 只 `Write-Host` 到控制台，无持久化记录——无法事后追溯 AI 尝试了哪些危险命令。

**结论**：wrapper 需增加审计日志（见 §7.10 新增）。

**洞察 4：双重安全检查算法**

cmd_command_execution_ai_agent 实现了**双重安全检查**：①第一次 pattern match（DANGEROUS_PATTERNS 列表），②第二次 critical block verify（CRITICAL_BLOCKS 列表，绝对禁止执行的模式）。两层检查都通过才执行。这种设计比单层检查更鲁棒——即使第一层漏判，第二层 critical block 仍能兜底。

**结论**：wrapper 的 PowerShell 原生命令拦截采用双重检查算法（见 §7.1）。

### 3.6 2026 年 8 月第二轮搜索补充（v1.0.0——trash redirect 算法发现）

> 搜索时间：2026-08-11 第二轮，覆盖 GitHub/gist/Claude Code Issues/掘金

#### 3.6.1 新发现

| 项目/事件 | 时间 | 关键发现 | 与本方案的关系 |
|---|---|---|---|
| **prevent-llm-delete**（Munasco） | 2026-02 | 跨平台 CLI，**不阻断而是剥离危险 flag（-r/-f/-rf）并重定向到 trash/回收站**。AI 仍可完成任务（删除发生），但文件进回收站可恢复 | **BETTER 算法**：redirect 优于 block——AI 不卡住，文件可恢复 |
| **Claude Code Issue #64310** | 2026-05-31 | **真实事故**：Claude Code 写 PowerShell 脚本用 `Get-ChildItem -Include` 不带 `-Recurse`（PowerShell 5.1 静默返回空），然后 `Remove-Item -Recurse -Force` 删"看起来空"的文件夹，**永久删除 34 个客户视频文件**。SSD+TRIM=完全不可恢复 | **证实 `Remove-Item -Recurse -Force` 的现实危险性**——正是我们 §7.1.2 Part B 拦截的命令 |
| **dcg v0.9.4** | 2026-08-07 | dcg 从 v0.6.9（7月）升级到 v0.9.4（8月7日），新增 Windows pack/scan extractor/heredoc improvements。原生支持 PowerShell 安装 | dcg 持续活跃，Windows 支持已成熟——但我们仍用 PowerShell 函数覆盖（Trae IDE 不支持 PreToolUse hook） |
| **agent-coord**（ThatHunky） | 2026-06-27 | 零依赖多 AI 协调：MCP server + JSON 文件 board（`~/.agent-coord/board.json`），原子多进程安全 mutex。File locks + task claims + status messages | **验证 §11 三件套方案的可行性**——JSON 文件 board 与我们的 SQLite Task Board 设计思路一致 |
| **agentlocks**（simke9445） | 2026-06 | Advisory file locks for AI agents。Agent-native：JSON 输出、self-describing contract、错误消息教学式。PreToolUse hook for `git verify` before commit | **验证 lock_files.py 设计方向**——advisory lock + JSON 输出 + 教学式错误消息 |
| **Vibe Kanban** | 2026-04~06 | 27K+ stars，280+ releases。Kanban board + Git worktree 隔离，10+ agent 并行。Rust 后端 + SQLite。MCP 双向集成 | **验证 worktree+task board 架构**——业界最成熟的方案，我们的 §11 与其设计思路一致 |
| **AI Agent Guardrails gist**（bral） | 2026-03 | 6 层防御：binary wrapper（PATH 拦截 gh/npm/pip）→ deny rules → managed settings → filesystem flags。关键洞察："wrapper 可被绝对路径绕过" | **验证我们的 escape hatch 设计**——绝对路径绕过是已知风险，我们已通过逃生通道管理 |

#### 3.6.2 关键洞察：trash redirect 是比 block 更好的算法

**prevent-llm-delete 的核心创新**：不阻断删除命令，而是**剥离危险 flag 并重定向到回收站**。

| 对比 | block 算法（当前 v0.9.0） | redirect 算法（v1.0.0 新增） |
|---|---|---|
| AI 体验 | 命令被阻断，AI 需要换命令或用逃生通道 | 命令"成功"执行，AI 继续工作 |
| 文件安全 | 文件不被删（最安全） | 文件进回收站（可恢复） |
| 适用场景 | CRITICAL 命令（format/vssadmin） | 非 CRITICAL 命令（Remove-Item -Recurse） |
| 实现复杂度 | 低（只拦截） | 中（需调用 Recycle Bin API） |
| 副作用 | AI 可能反复尝试被阻断的命令 | 回收站可能堆积文件（需定期清理） |

**结论**：对 `Remove-Item -Recurse -Force` 等非 CRITICAL 命令，采用 **redirect 到回收站** 而非 block。对 `format`/`vssadmin delete`/`diskpart` 等 CRITICAL 命令，保持 **hard block**（无逃生通道）。

**Windows Recycle Bin API**（PowerShell 调用）：
```powershell
# 使用 Microsoft.VisualBasic.FileIO 发送到回收站
Add-Type -AssemblyName Microsoft.VisualBasic
[Microsoft.VisualBasic.FileIO.FileSystem]::DeleteDirectory(
    $path,
    [Microsoft.VisualBasic.FileIO.UIOption]::OnlyErrorDialogs,
    [Microsoft.VisualBasic.FileIO.RecycleOption]::SendToRecycleBin
)
[Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile(
    $path,
    [Microsoft.VisualBasic.FileIO.UIOption]::OnlyErrorDialogs,
    [Microsoft.VisualBasic.FileIO.RecycleOption]::SendToRecycleBin
)
```

### 3.7 safe-rm 三层分类算法（v1.1.0 新增——参考 kayaman/safe-rm）

> 搜索发现 `kayaman/safe-rm`（2026-05）实现了比 trash redirect 更精细的**三层分类算法**。

#### 3.7.1 算法核心

safe-rm 的核心创新是**情境感知的差异化管理**——结合 Git 状态信息（`git status --porcelain`）判断文件是否被跟踪，然后按三层规则链分类：

```
待删除文件
  → Tier 1: block_patterns 匹配？（.git/ / 系统根目录）
    → 是 → 硬阻断（永久保护）
    → 否 ↓
  → Tier 2: auto_allow_patterns 匹配？（node_modules/ dist/ __pycache__/ *.log）
    → 是 → 直接删除（构建垃圾，无需保护）
    → 否 ↓
  → Tier 3: Git untracked 或 unstaged 文件？
    → 是 → 重定向到回收站（有价值但不在 git 中，可恢复）
    → 否 → 直接删除（已 tracked，git 可恢复）
```

#### 3.7.2 与本方案 v1.0.0 的对比

| 维度 | v1.0.0（两层） | v1.1.0（三层，参考 safe-rm） |
|---|---|---|
| 分类依据 | 命令类型（CRITICAL vs 非 CRITICAL） | **文件类型 + Git 状态** |
| 构建垃圾（node_modules） | 重定向到回收站（浪费回收站空间） | **直接删除**（不是源代码，无需保护） |
| 未提交源代码（.py/.md） | 重定向到回收站 | **重定向到回收站**（一致） |
| 已 tracked 文件 | 重定向到回收站 | **直接删除**（git 可恢复，不浪费回收站） |
| .git/ 目录 | 硬阻断 | **硬阻断**（一致） |
| 回收站空间效率 | 低（所有删除都进回收站） | **高**（只有未提交源代码进回收站） |

#### 3.7.3 结论

safe-rm 的三层分类算法在**回收站空间效率**上优于 v1.0.0 的两层方案。但实现复杂度更高（需调用 `git status --porcelain` 判断每个目标文件的 Git 状态）。

**裁定**：v1.1.0 将三层分类作为 §7.11 Trash Redirect 的**改进方向**记录，但暂不施工——当前 v1.0.0 的两层方案已足够安全（回收站默认 10% 磁盘空间，远期由 `recycle_bin_monitor.py` 监控容量）。三层分类作为 v2.0.0 远期改进项。

### 3.8 第四轮搜索补充（v1.2.0——Proxy Function 最佳实践+隔离区算法+RULE-THREE）

#### 3.8.1 PowerShell Proxy Function 是覆盖 cmdlet 的正确方法

> 来源：commandinline.com（2026-06）《PowerShell Proxy Functions Intercept and Extend Built-In Cmdlets》

v1.0.0/v1.1.0 中手写 `Remove-Item` 函数的 `param()` 块是**错误做法**——会丢失动态参数（如 `-Credential`）、`-WhatIf` 支持、管道输入支持。正确方法：

```powershell
# 使用 ProxyCommand::Create() 自动生成代理脚手架
$meta = [System.Management.Automation.CommandMetaData](Get-Command Microsoft.PowerShell.Management\Remove-Item)
$proxyCode = [System.Management.Automation.ProxyCommand]::Create($meta)
# $proxyCode 包含：完整 param() 块 + DynamicParam + Begin/Process/End steppable pipeline
# 在 Begin 块中插入拦截逻辑，在 Process 块中通过 steppable pipeline 透传给原始 cmdlet
```

**关键规则**：
1. **永远用 `ProxyCommand::Create()` 生成脚手架**——手写 param() 块会在原始 cmdlet 更新时断裂
2. **通过模块限定名调用原始 cmdlet**——`Microsoft.PowerShell.Management\Remove-Item`，避免无限递归
3. **保留 DynamicParam 块**——provider 供应的参数（如 `-Credential`）依赖此块
4. **用 steppable pipeline 透传**——保留管道流式行为和内存效率

**对本方案的影响**：§7.1.2 Part B 的 `Remove-Item` 函数需用 ProxyCommand 模式重写（见 §7.1.4 新增）。

#### 3.8.2 隔离区算法（agent-file-safety-kit）

> 来源：Nina0-0/agent-file-safety-kit（2026-04）—— Windows + PowerShell 专用 AI 文件安全护栏

隔离区算法是 block 和 trash redirect 之外的**第三种选择**：

```
待删除文件
  → 列出候选文件清单
  → 生成 manifest.json（记录文件路径/大小/hash/时间）
  → 验证每个候选文件在预期根目录内（防越界删除）
  → 移动到隔离区（.quarantine/ 目录），不永久删除
  → 验证重要文件仍存在
  → 用户确认后可：① restore.ps1 恢复 ② 确认后永久删除
```

| 对比 | block | trash redirect | **quarantine（隔离区）** |
|---|---|---|---|
| AI 体验 | 命令被阻断 | 命令"成功" | 命令"成功" |
| 文件位置 | 原位不动 | 回收站 | 项目内 .quarantine/ |
| 恢复方式 | 无需恢复 | 回收站恢复 | restore.ps1 恢复 |
| 审计信息 | 日志 | 日志 | **manifest.json（含 hash/大小/时间）** |
| 空间占用 | 零 | 回收站 | 项目内（需 .gitignore） |
| 适用场景 | CRITICAL 命令 | 非 CRITICAL 删除 | **批量清理（有 manifest 可审计）** |

**裁定**：隔离区算法作为**批量清理场景的可选增强**记录——当 AI 执行多文件删除时（如清理 `_temp*` 文件），用隔离区+manifest 比逐个回收站更可审计。暂不施工，作为 v2.0.0 远期改进。

#### 3.8.3 RULE-THREE 三步审判（项目已有规则）

> v1.2.0 审查发现：`.trae/rules/project_rules.md` 已有 RULE-THREE（三步审判），是文件删除的安全规则，但未在 §4.1 设施清单中登记。

**RULE-THREE 三步审判**（来自 .trae/rules/project_rules.md）：
> 删除任何文件前 MUST 三步验证：①**必要性**——是否真的需要删？②**安全性**——文件每一行内容在别处还有？③**可逆性**——删了能恢复？

这与 §7.1 的 wrapper 拦截互补：
- RULE-THREE 是**规则层**（AI 自觉遵守，君子协定）
- wrapper 是**技术层**（机械拦截，不依赖自觉）
- d6_security `detect_permanent_file_deletion.py` 是**静态检测层**（commit 时检查）

三层叠加：规则引导 + 静态检测 + 运行时拦截 = 文件删除安全闭环。

### 3.9 第五轮搜索补充（v1.3.0——OpenClaw 四级风险+fail-open 策略+PowerShell # 注释陷阱+d6_security 未接入 pre-commit）

#### 3.9.1 OpenClaw 四级风险动态评估系统

> 来源：CSDN（2026-03）《构建 OpenClaw"防内鬼"防线：基于 PowerShell 的高危命令审批与全链路审计系统》

OpenClaw 实现了比我们二级（block/redirect）更精细的**四级风险动态评估**：

| 级别 | 颜色 | 处理 | 示例 | 本方案对应 |
|---|---|---|---|---|
| 🔴 禁止级 | Red | 直接阻断+记录 | `rm -rf /`/`format` | HARDBLOCKED |
| 🟠 高危级 | Orange | 弹出人工审批界面 | `git reset --hard`/`Remove-Item -Recurse -Force` | BLOCKED（v1.0.0）/ REDIRECTED（v1.1.0+） |
| 🟡 中危级 | Yellow | 二次确认提示 | `git stash`/`git rm` | BLOCKED |
| 🟢 低危级 | Green | 自动执行 | `git status`/`git add` | ALLOWED |

**OpenClaw 的额外特性**：
- **紧急模式 -Force**：跳过审批但记录原因（类似我们的逃生通道）
- **safe-rm 替代方案**：将不可逆操作转化为可恢复操作（类似我们的 trash redirect）
- **全量留痕**：所有操作（包括被拒绝和强制执行的）均写入 JSON 日志（类似我们的审计日志）

**裁定**：OpenClaw 的四级分级比我们的二级更精细，但实现复杂度更高（需人工审批 UI）。当前二级（block/redirect）+逃生通道已足够。四级分级作为 v2.0.0 远期改进。

#### 3.9.2 Wrapper 失败模式策略：fail-open

> 来源：git-safety-guard（terraphim）明确采用 **fail-open 语义**——"If guard fails, commands pass through"

**问题**：wrapper 本身可能出错（git 路径解析失败/Recycle Bin API 加载失败/ProxyCommand 生成失败）。此时应：
- **fail-closed**（阻断）：安全但不阻断合法工作——开发工具不应因安全防护故障而停止开发
- **fail-open**（放行）：不阻断但记录错误——安全防护故障时退化为无防护状态，但开发继续

**裁定**：采用 **fail-open**——wrapper 出错时放行命令并记录 `[SAFE-ERROR]` 到审计日志。理由：
1. 开发工具的可用性优先——wrapper 故障不应阻止 AI 完成任务
2. 审计日志记录了 fail-open 事件——事后可追溯
3. git-safety-guard/terraphim 也采用 fail-open（行业共识）
4. Trae IDE 无其他防护层——wrapper 是唯一拦截层，fail-closed 会导致 AI 完全无法执行 git 命令

**实现**：wrapper 函数的 try/catch 中，catch 块记录错误后透传给原始命令：
```powershell
function git {
    try {
        # ... 拦截逻辑 ...
    } catch {
        _ZephyrAuditLog -Command "git $($args -join ' ')" -Action 'FAIL_OPEN' -Reason "wrapper error: $_"
        & $_realGit @args  # fail-open: 透传给真实 git
    }
}
```

#### 3.9.3 PowerShell `#` 注释陷阱

> 来源：opencode-swarm Issue #1875（2026-07-17）—— PowerShell sanitizer 导致 Agent 无限循环

**问题**：PowerShell 中 `#` 是行尾注释。当代码通过 `powershell -Command "..."` 执行时，换行被规范化为空格，`#` 注释会**吞掉其后所有内容**（包括 `}` 和 `catch` 块）。

**对本方案的影响**：如果 `install_git_safety_wrapper.ps1` 生成的 wrapper 代码含 `#` 注释，且某场景下通过 `-Command` 执行，可能导致代码被截断。

**修复**：
1. wrapper 代码写入 `$PROFILE` 文件（`-File` 模式），不通过 `-Command` 执行 → `#` 注释正常工作
2. 若必须通过 `-Command` 执行，用 `<# comment #>` 块注释替代 `#` 行注释
3. `install_git_safety_wrapper.ps1` 需验证生成的代码在 `-File` 模式下正确解析

#### 3.9.4 d6_security 未接入 pre-commit config（CRITICAL GAP）

> v1.3.0 审查发现：`detect_git_dangerous.py`/`detect_shell_dangerous.py`/`detect_permanent_file_deletion.py` 存在但**未在 .pre-commit-config.yaml 中注册**——代码存在但从未运行！

**验证**：grep `.pre-commit-config.yaml` 只找到 `check_protected_paths.py` 和 `retire_tmp_artifacts.py` 两个 d6_security 脚本。`detect_git_dangerous.py`/`detect_shell_dangerous.py`/`detect_permanent_file_deletion.py` 等 14 个脚本**未接入 pre-commit**。

**影响**：这些脚本作为静态检测层（§4.M #57-65）声称"正常运行"，但实际上从未被 pre-commit 调用——它们只是存在但未激活的代码。文件删除安全三层闭环（RULE-THREE + d6_security + wrapper）中的**静态检测层实际缺失**。

**修复**：见新增 §7.13 施工项。

## 4. 现状分析：项目现有 Git 配套设施全貌

### 4.1 设施清单

#### A. Git 命令拦截层

| # | 设施 | 文件 | 状态 | 问题 |
|---|---|---|---|---|
| 1 | git_guard.py alias 拦截 | scripts/git_guard.py | ⚠️ **全部失效** | alias 无法覆盖内置命令（7 个 DANGEROUS_SUBCOMMANDS 全失效） |
| 2 | git_guard.py 直接调用 | scripts/git_guard.py | ✅ 代码层有效 | 但无人主动调用 `python scripts/git_guard.py` |
| 3 | git_guard.py clean 自伤检测 | scripts/git_guard.py L528-565 | ✅ 已修复 | 仅直接调用时有效，alias 调用不生效 |
| 4 | post_checkout_guard.py | scripts/post_checkout_guard.py | ✅ 存在 | checkout 后扫描锁冲突（只警告不阻断），alias 不生效时不触发 |
| 5 | post_commit_guard.sh | scripts/governance/git_hooks/post_commit_guard.sh | ✅ 存在 | Shell post-commit 守卫（forged_gw_marker 检测原位置） |
| 5a | **setup_git_guard_aliases.py**（v0.9.0 补登） | scripts/setup_git_guard_aliases.py（200行） | ⚠️ **DANGEROUS_SUBCOMMANDS 不一致** | 安装 alias 的入口脚本，但其列表只有 6 个命令（reset/checkout/stash/revert/restore/mv），**缺少 `clean`**——git_guard.py 有 7 个含 clean。导致 `git clean` 的 alias 从未被安装 |

#### B. 文件锁与并发防护层

| # | 设施 | 文件 | 状态 | 问题 |
|---|---|---|---|---|
| 6 | lock_files.py 文件锁 | scripts/lock_files.py（611行 v2.0.0） | ✅ 系统正常 | **无人使用**（registry.json 为空，最后更新 8月3日） |
| 7 | concurrency_guard.py | src/zephyr/infrastructure/runtime/concurrency_guard.py（225行） | ✅ 系统正常 | 只读扫描 .ailocks，锁为空时全部放行 |
| 8 | .ailocks/ 锁目录 | .ailocks/registry.json + hard_locks.json | ✅ 存在 | locks 为空，hard_locks 仅 1 条（launcher.py） |

#### C. Commit 门禁层（80+ gates）

| # | 设施 | 文件 | 状态 | 问题 |
|---|---|---|---|---|
| 9 | GitCommitGateway | src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py | ✅ 正常运行 | 全项目唯一合法 commit 入口，但只拦 commit 不拦 clean |
| 10 | CommitGateRegistry | src/zephyr/gov_enforcement/rule_bridge/commit_gate_registry.py | ✅ 正常运行 | 门禁注册表（架构债务 #AD-001 治本），43 个门禁注册 |
| 11 | .pre-commit-config.yaml | .pre-commit-config.yaml（1026行，40+ hooks） | ✅ 正常运行 | 见下表安全相关 hook |
| 12 | commit_gates/ 目录 | src/zephyr/gov_enforcement/commit_gates/（**100 个 gate 文件**，v1.2.0 更正） | ✅ 正常运行 | 见下表 git 安全相关 gate |
| 13 | rule_enforcement 注册表 | src/zephyr/gov_enforcement/rule_enforcement/_registry.yaml | ✅ 正常运行 | 43 个门禁真源 |
| 14 | emergency_commit | src/zephyr/gov_enforcement/rule_bridge/emergency_commit.py | ✅ 存在 | 紧急 commit（governance black hole，有一致性检查） |
| 15 | batched_auto_committer | src/zephyr/gov_enforcement/rule_bridge/batched_auto_committer.py | ✅ 存在 | 批量自动提交器 |

#### D. Worktree 隔离层

| # | 设施 | 文件 | 状态 | 问题 |
|---|---|---|---|---|
| 16 | session_worktree | src/zephyr/gov_enforcement/rule_bridge/session_worktree.py | ✅ 系统正常 | AGENTS.md RULE-WORKTREE 要求但 **AI 未遵守** |
| 17 | worktree_pool/manager/lifecycle | src/zephyr/gov_enforcement/rule_bridge/worktree_*.py | ✅ 存在 | worktree 生命周期管理 |
| 18 | session_claim | src/zephyr/gov_enforcement/rule_bridge/session_claim.py | ✅ 存在 | session claim 管理（HELD-OVERLAP 原子 check-and-claim） |

#### E. 受保护路径层

| # | 设施 | 文件 | 状态 | 问题 |
|---|---|---|---|---|
| 19 | immutable_core.yaml | config/immutable_core.yaml（77行） | ✅ 正常运行 | 25 个禁止操作 + 26 个受保护路径（含 .git/**/AGENTS.md/.ailocks/ 等） |
| 20 | check_protected_paths | scripts/governance/d6_security/check_protected_paths.py | ✅ 正常运行 | GATE-PROTECTED-PATHS Layer 2 + 手动工具 Layer 3 |
| 21 | .gitignore 根目录白名单 | .gitignore L236-276 | ✅ 正常运行 | `/*` 忽略全部 + `!` 例外恢复 25 个合法根文件 |
| 22 | .gitattributes | .gitattributes（59行） | ✅ 正常运行 | `* text=auto eol=lf` + 二进制文件 binary 标记 |
| 23 | .editorconfig | .editorconfig（32行） | ✅ 正常运行 | `charset = utf-8` / `end_of_line = lf`（防编码损坏） |

#### F. 规则与文档层

| # | 设施 | 文件 | 状态 | 问题 |
|---|---|---|---|---|
| 24 | AGENTS.md 规则 | AGENTS.md | ⚠️ 有 RULE-WORKTREE + #ARCH-GIT-SELF-HARM-GUARD L1+L2 但 **无 RULE-GIT-SAFE** | 缺少 git clean 禁令 |
| 25 | .trae/rules/ 规则 | .trae/rules/project_rules.md + onboarding_detail.md | ⚠️ 有 RULE-ZERO（文件锁）/RULE-ONE（原子写）/RULE-THREE（三步审判）/RULE-TWENTY（写完即提交）但 **无 git 安全铁律** | Trae IDE 规则目录，AI 读这里获取规则。**RULE-THREE 三步审判**（删除文件前验证必要性/安全性/可逆性）与 wrapper 互补 |
| 26 | project_memory | memory/project_memory.md | ✅ 已记录灾难教训 | 需确认所有 AI 会读 |
| 27 | AI_review_instructions §0 规则9/10 | AI_review_instructions.md | ✅ 已加入 | 仅覆盖审查指令中的 AI |
| 28 | SECURITY.md | SECURITY.md | ✅ 存在 | 安全策略文档（漏洞报告流程） |

#### G. 检测与审计层

| # | 设施 | 文件 | 状态 | 问题 |
|---|---|---|---|---|
| 29 | echo-guard.yml | echo-guard.yml（43行） | ✅ 正常运行 | 重复代码检测（3+副本硬阻断） |
| 30 | clone_guard.yml | clone_guard.yml | ✅ 正常运行 | 3 层检测（pre-commit/audit/compare） |
| 31 | git_secrets_setup.sh | scripts/hooks/git_secrets_setup.sh | ✅ 存在 | git secrets 密钥扫描 hook 安装 |
| 32 | MCP governance | config/mcp.json L76-87 | ✅ 正常运行 | governance.acquire_lock / check_lock / run_gate MCP 工具 |
| 33 | behavioral_admission | src/zephyr/gov_enforcement/behavioral_admission/ | ✅ 存在 | 行为准入门禁控制器（admission_controller/verdict_engine） |
| 34 | invariants 检查 | src/zephyr/gov_enforcement/rule_enforcement/invariants/ | ✅ 存在 | 零残留检查 + 循环依赖 + 契约兼容性 |

#### H. Trae IDE 约束（关键）

| # | 约束 | 说明 |
|---|---|---|
| 35 | **Trae IDE 不支持 PreToolUse hooks** | AGENTS.md L47 确认"Trae IDE 不可 hook"——无法在 AI 工具层拦截命令 |
| 36 | **Trae IDE 终端为 PowerShell 5.1** | 所有 AI 通过 RunCommand 执行的命令都在 PowerShell 5.1 中运行——PowerShell `git()` 函数覆盖在此生效 |
| 37 | **.trae/rules/ 是 AI 规则入口** | Trae IDE 的 AI 读 .trae/rules/project_rules.md 获取项目规则——RULE-GIT-SAFE 必须写入此文件 |
| 38 | **.traeignore 让 AI 忽略 .ailocks/ 和 .git/** | Trae IDE 的 AI 看不到文件锁状态（.ailocks/registry.json）和 git hook 配置（.git/hooks/）——AI 不知道文件锁是否存在，也不知道有哪些 hook 在运行 |
| 39 | **无其他 AI 工具配置** | 项目无 .claude/ / .cursor/ / .codex/ / .continue/ 目录——确认 100% Trae IDE 开发，无需适配其他 AI 工具 |
| 40 | **PowerShell $PROFILE 已存在**（1799 字节） | 安装 wrapper 时需追加到现有 profile 末尾，不能覆盖——安装脚本需检测 marker 注释实现幂等 |
| 41 | **-NoProfile 边缘风险** | 若某些工具用 `powershell -NoProfile` 启动子进程，$PROFILE 中的 wrapper 不会加载——需确认 Trae IDE 的 RunCommand 不使用 -NoProfile（实测确认：RunCommand 加载 $PROFILE） |

#### I. .git/hooks/ 实际安装的 hook（遗漏补充）

| Hook | 文件 | 功能 | 与 git 安全的关系 |
|---|---|---|---|
| pre-commit | .git/hooks/pre-commit（680B） | pre-commit 框架入口（generated by pre-commit） | 调用 .pre-commit-config.yaml 中的所有 hook |
| pre-commit.py | .git/hooks/pre-commit.py（4188B） | pre-commit Python 入口 | pre-commit 框架的 Python 实现 |
| post-checkout | .git/hooks/post-checkout（554B） | checkout 后触发 | 调用 post_checkout_guard.py 扫描锁冲突 |
| post-commit | .git/hooks/post-commit（1189B） | commit 后触发 | 调用 post_commit_guard.sh + auto_handoff_log.py |
| post-merge | .git/hooks/post-merge（354B） | merge 后触发 | 清理 worktree 临时状态 |
| pre-push | .git/hooks/pre-push（350B） | push 前触发 | push 前安全检查 |
| reference-transaction | .git/hooks/reference-transaction（369B） | 引用变更触发 | 审计 ref 变更（branch 创建/删除等） |

#### J. .github/workflows/ CI 工作流（遗漏补充）

| 工作流 | 文件 | 功能 | 与 git 安全的关系 |
|---|---|---|---|
| governance.yml | .github/workflows/governance.yml | CI 治理（含 Tier 5 架构债务扫描） | CI 层面的治理门禁 |
| commit_message_guard.yml | .github/workflows/commit_message_guard.yml | commit message 格式校验 | 防非规范 commit message |
| red-blue-validator.yml | .github/workflows/red-blue-validator.yml | 红蓝对抗测试 | 安全测试 |
| dedup-test.yml | .github/workflows/dedup-test.yml | 代码重复检测 | echo-guard CI 集成 |
| deploy.yml | .github/workflows/deploy.yml | 部署工作流 | 与 git 安全无关 |

#### .pre-commit-config.yaml 中与 git 安全直接相关的 hook

| Hook ID | 行号 | 功能 | 与 git 安全的关系 |
|---|---|---|---|
| gate-commit-gw | L854-860 | 裸 commit 检测（always_run=true） | 强制所有 commit 走 GitCommitGateway |
| gate-protected-paths | L101-107 | 受保护路径写入检测 Layer 2 | 保护 .gitignore/.gitattributes/AGENTS.md |
| gate-worktree-required | L116-122 | 主工作区 commit 软门禁 L3.1 | 累计≥5 次主工作区 commit 升级阻断 |
| gate-worktree-ops-telemetry | L715-722 | 主工作区擦除操作遥测审计 | 审计 git stash push / git restore / Path.unlink |
| gate-encoding-safety | L836-844 | 编码安全（BOM/CRLF/mojibake）硬阻断 | 防编码损坏（本项目遇到过 BOM 导致 frontmatter 解析失败） |
| gate-rules-integrity | L225-233 | 规则文件 golden hash 校验 | 防脚本自篡改 |
| gate-no-commit-derived | L1018-1025 | 阻断派生产物 git add | 防派生产物入库 |
| check-merge-conflict-marker | L79-85 | 检测合并冲突标记 | 防冲突标记入库 |
| detect-private-key-local | L86-92 | 检测私钥 | 防密钥泄露 |

#### commit_gates/ 中与 git 安全直接相关的 gate

| Gate | 文件 | 功能 |
|---|---|---|
| WORKTREE-REQUIRED | worktree_required_gate.py (priority=44) | worktree 隔离强制 |
| PROTECTED-PATHS | protected_paths_gate.py (priority=28) | 受保护路径写入检测 Layer 1（in-process，--no-verify 绕不过） |
| FORGED-GW-MARKER | forged_gw_marker_gate.py | 防伪造 GW 标记 |
| GIT-CALL-BUDGET | git_call_budget_gate.py (priority=105) | git 调用预算 warn-only |
| HELD-OVERLAP | held_overlap_gate.py | 搭便车防护（文件级冲突阻断） |
| CLAIM-REQUIRED | claim_required_gate.py | claim_files 前置检查 |
| STASH-ACCUMULATION | stash_accumulation_gate.py | stash 堆积检测 |
| DERIVED-FILE-DELETION | derived_file_deletion_gate.py | 派生文件删除检测 |
| CREATE-GUARD | create_guard.py (priority=60) | 新建 .py 文件 creation_token 阻断 |
| DIRECTORY-CONTRACT | directory_contract_gate.py (priority=30) | 目录契约校验（--no-verify 补偿） |

#### K. 灾难恢复与运维设施（v0.9.0 补登——原 §4.1 遗漏盘点）

> v0.9.0 审查发现：原 §4.1 设施清单聚焦于"防误删"层面，遗漏了"灾难恢复"和"运维保障"层面的现有设施。以下设施虽不直接拦截危险命令，但构成灾难发生后的**恢复底座**，属于 git 安全治理体系的必要组成部分。

| # | 设施 | 文件 | 状态 | 与 git 安全的关系 |
|---|---|---|---|---|
| 42 | **backup.ps1** | scripts/backup/backup.ps1 | ✅ 存在 | 日常备份脚本——灾难发生后的恢复源 |
| 43 | **restore.ps1** | scripts/backup/restore.ps1 | ✅ 存在 | 恢复脚本——从备份恢复项目文件 |
| 44 | **backup_daily_trigger.ps1** | scripts/backup/backup_daily_trigger.ps1 | ✅ 存在 | 每日备份触发器——定时保护 |
| 45 | **backup_ch_vm.ps1** | scripts/backup/backup_ch_vm.ps1 | ✅ 存在 | ClickHouse VM 备份——数据库层恢复 |
| 46 | **backup_manual.ps1** | scripts/backup/backup_manual.ps1 | ✅ 存在 | 手动备份入口 |
| 47 | **rollback.py** | scripts/rollback.py | ✅ 存在 | 回滚脚本——项目级回滚能力 |
| 48 | **deadman_switch.ps1** | scripts/deadman_switch.ps1 | ✅ 存在 | 死人开关——进程异常退出时触发保护 |
| 49 | **record_session_start_commit.py** | scripts/record_session_start_commit.py | ✅ 存在 | 记录 session 启动时的 commit hash——用于事后追溯 AI 操作起点 |
| 50 | **ide_health_service.py** | scripts/ide_health_service.py | ✅ 存在 | IDE 健康服务——监控 Trae IDE 运行状态 |
| 51 | **test_concurrent_safety.ps1** | scripts/governance/test_concurrent_safety.ps1（253行） | ✅ 存在 | **47 脚本并发安全测试**+ 5 实例同脚本压测——验证 RULE-ONE temp+rename 原子写模式的并发正确性。直接关联多 AI 并发安全 |
| 52 | **file_lock.py（shared）** | scripts/governance/_shared/file_lock.py | ✅ 存在 | 共享文件锁模块——被多个 governance 脚本复用的底层锁原语 |
| 53 | **auto_handoff_log.py** | scripts/hooks/auto_handoff_log.py | ✅ 存在 | 自动交接日志——post-commit hook 调用，记录 AI session 交接信息 |
| 54 | **git_commit.py**（v1.0.0 补登） | scripts/git_commit.py | ✅ 正常运行 | **全项目唯一合法 git commit CLI 入口**——封装 GitCommitGateway，串行化所有 commit。9 种错误码（exit 1-9）覆盖各种阻断场景。禁止裸 `git commit`（GATE-COMMIT-GW 门禁强制） |
| 55 | **clone_guard_audit.py**（v1.0.0 补登） | scripts/clone_guard_audit.py | ✅ 正常运行 | CloneGuard L2 周期审计触发脚本——事件驱动（非 cron），检测代码重复。与 echo-guard.yml 互补 |
| 56 | **validate_worktree_required.py**（v1.0.0 补登） | scripts/governance/d11_compliance/validate_worktree_required.py | ✅ 正常运行 | **GATE-WORKTREE-REQUIRED 门禁实现**——将 RULE-WORKTREE 从"君子协定"升级为"软门禁"。主工作区 commit 累计≥阈值升级阻断。§10 开放问题中的阈值调整在此实现 |

#### M. d6_security 静态检测脚本群（v1.1.0 补登——16 个安全检测脚本深度盘点）

> v1.1.0 审查发现：`scripts/governance/d6_security/` 目录下有 16 个安全检测脚本，是 pre-commit hook 的静态分析层。这些脚本扫描代码/文档中的危险模式，与 §7.1 的运行时 PowerShell wrapper 互补——wrapper 拦截执行时命令，d6_security 拦截代码中嵌入的危险模式。

| # | 设施 | 文件 | 状态 | 与 git 安全的关系 |
|---|---|---|---|---|
| 57 | **detect_git_dangerous.py** | scripts/governance/d6_security/detect_git_dangerous.py | ✅ 正常运行 | **检测代码/文档中的危险 git 命令**——对标 ABS-26/27/28（禁止 git push --force/git reset --hard/git clean -fdx 建议）。扫描文档和脚本中出现的 `git push --force`/`git reset --hard`/`git clean -fd`/`git branch -D`/`git rebase` 危险变体 |
| 58 | **detect_shell_dangerous.py** | scripts/governance/d6_security/detect_shell_dangerous.py | ✅ 正常运行 | **检测代码中的危险 shell 命令**——对标 ABS-38/39。扫描 `rm -rf /`/`del /f /s /q`/`format`/`mkfs`/`dd`/fork bomb/`chmod 777`。与 §7.1.2 Part B 的运行时拦截互补——此脚本在 commit 时检测代码中是否嵌入了危险命令 |
| 59 | **detect_permanent_file_deletion.py** | scripts/governance/d6_security/detect_permanent_file_deletion.py | ✅ 正常运行 | **检测 ttl:permanent 文件删除**——对标 PS-STD-012 V1/PS-STD-009 §7。扫描 git staged 删除操作，若被删文件 frontmatter 含 `ttl: permanent` 则阻断。保护项目永久资产 |
| 60 | **detect_anchor_file_deletion.py** | scripts/governance/d6_security/detect_anchor_file_deletion.py | ✅ 存在 | 检测锚点文件删除——锚点文件是模块结构的关键节点 |
| 61 | **detect_secrets.py + scan_secret_leak.py + scan_runtime_log_secrets.py** | scripts/governance/d6_security/detect_secrets.py 等 3 个 | ✅ 正常运行 | 三层密钥检测：代码静态扫描 + 泄漏扫描 + 运行时日志扫描。与 pre-commit `detect-private-key-local` 互补 |
| 62 | **run_adversarial_checks.py** | scripts/governance/d6_security/run_adversarial_checks.py | ✅ 存在 | 红蓝对抗安全检查入口——聚合所有 d6_security 检测脚本 |
| 63 | **validate_gate_discipline.py** | scripts/governance/d6_security/validate_gate_discipline.py | ✅ 存在 | 门禁纪律验证——检查 gate 是否被绕过 |
| 64 | **detect_shell_true.py** | scripts/governance/d6_security/detect_shell_true.py | ✅ 存在 | 检测 `shell=True` 使用——防止 Python subprocess 命令注入 |
| 65 | **detect_threading_lock.py** | scripts/governance/d6_security/detect_threading_lock.py | ✅ 存在 | 检测线程锁使用——并发安全静态检查 |

#### N. 安全相关配置文件（v1.1.0 补登——config/ 目录深度盘点）

| # | 设施 | 文件 | 状态 | 与 git 安全的关系 |
|---|---|---|---|---|
| 66 | **immutable_core.yaml** | config/immutable_core.yaml | ✅ 正常运行 | 25 个禁止操作 + 26 个受保护路径（含 .git/AGENTS.md/.ailocks/ 等） |
| 67 | **dr_policy.yaml** | config/dr_policy.yaml | ✅ 存在 | 灾难恢复策略——定义灾难发生后的恢复流程 |
| 68 | **worktree_state_machine.yaml** | config/worktree_state_machine.yaml | ✅ 存在 | worktree 状态机配置——定义 worktree 生命周期状态转换 |
| 69 | **external_watchdog.yaml** | config/external_watchdog.yaml | ✅ 存在 | 外部看门狗配置——外部进程监控系统安全 |
| 70 | **sandbox_policy.yaml** | config/sandbox_policy.yaml | ✅ 存在 | 沙箱策略——定义 AI 操作的沙箱边界 |
| 71 | **secret_registry.yaml** | config/secret_registry.yaml | ✅ 存在 | 密钥注册表——已知的密钥模式列表 |

#### L. PowerShell 原生破坏性命令 gap 分析（v0.9.0 新增——ARCH-POWERSHELL-DESTRUCTIVE-GUARD（待登记））

> **这是 v0.9.0 审查发现的最大安全 gap**。当前 wrapper 只定义了 `git()` 函数，仅拦截 git 命令。AI 可以用 PowerShell/CMD 原生命令完全绕过 wrapper 删除文件。

**gap 演示**：

```
AI 想删除 docs/ 目录
  → [L1 git wrapper] 不触发（Remove-Item 不是 git 命令）
  → [L2 pre-commit hooks] 不触发（不是 commit 操作）
  → [L3 文件锁] 不防护（Remove-Item 不检查 .ailocks/）
  → [L4 session_worktree] 不触发（AI 在主工作区操作）
  → [L5 GitCommitGateway] 不触发（不是 commit）
  → PowerShell 直接执行 Remove-Item -Recurse -Force docs/
  → 文件物理删除（不进回收站）
```

**需拦截的 PowerShell/CMD 原生破坏性命令清单**（参考 cmd_command_execution_ai_agent DANGEROUS_PATTERNS + dcg Windows pack + opencode-fusion PR #12）：

| 命令 | 破坏性 | 阻断条件 | 放行条件 |
|---|---|---|---|
| `Remove-Item -Recurse -Force` | 递归删除目录 | 带 `-Recurse` 且带 `-Force` | 不带 `-Recurse`（单文件删除可恢复）或目标在 `$env:TEMP` |
| `rd /s` / `rmdir /s` | CMD 递归删除 | 带 `/s` 标志 | 不带 `/s` |
| `del /s` / `erase /s` | CMD 批量删除 | 带 `/s` 标志 | 不带 `/s` |
| `del /f` | CMD 强制删除 | 带 `/f` 标志（删只读文件） | 不带 `/f` |
| `rm -rf` / `rm -fr` | Unix 递归删除（若 GnuWin32 rm 在 PATH） | 带 `-rf`/`-fr` | 目标在 `$env:TEMP`/`/tmp`/`/var/tmp` |
| `robocopy /mir` | 镜像同步删除目标文件 | 带 `/mir` 或 `/purge` | 不带 `/mir`/`/purge` |
| `format` | 格式化磁盘 | 任何 `format` + 盘符 | 无放行（永远阻断） |
| `vssadmin delete shadows` | 删除卷影副本（备份） | `vssadmin delete` | 无放行（永远阻断） |
| `wbadmin delete` | 删除 Windows 备份 | `wbadmin delete` | 无放行（永远阻断） |
| `cipher /w` | 擦除空闲空间 | `cipher /w` | 无放行（永远阻断） |
| `diskpart` | 磁盘分区操作 | 任何 `diskpart` | 无放行（永远阻断） |
| `reg delete` | 删除注册表 | `reg delete` | 无放行（永远阻断） |
| `bcdedit` | 启动配置修改 | 任何 `bcdedit` | 无放行（永远阻断） |
| `netsh advfirewall` | 防火墙规则修改 | `netsh advfirewall` | 无放行（永远阻断） |
| `schtasks /delete` / `/create` | 计划任务篡改 | `schtasks /delete` 或 `/create` | 无放行（永远阻断） |
| `sc delete` / `sc stop` | 服务删除/停止 | `sc delete` 或 `sc stop` | 无放行（永远阻断） |
| `taskkill /f` | 强制结束进程 | `taskkill /f` | 不带 `/f`（普通结束可恢复） |
| `takeown` / `icacls` | 文件权限篡改 | 任何 `takeown`/`icacls` | 无放行（永远阻断） |
| `powershell -enc` | 编码执行（绕过审计） | `powershell -enc` 或 `-EncodedCommand` | 无放行（永远阻断） |
| `iex` / `invoke-expression` | 动态执行（绕过审计） | `iex`/`invoke-expression` 作为命令 | 无放行（永远阻断） |

**双重安全检查算法**（参考 cmd_command_execution_ai_agent）：

```
Layer 1: DANGEROUS_PATTERNS 模式匹配（上表 20+ 模式）
  → 匹配 → 进入 Layer 2
  → 不匹配 → 放行

Layer 2: CRITICAL_BLOCKS 绝对禁止验证（format/vssadmin delete/wbadmin delete/cipher /w/diskpart/reg delete/bcdedit/netsh advfirewall/schtasks delete|create/sc delete|stop/powershell -enc/iex）
  → 匹配 → 硬阻断（无逃生通道）
  → 不匹配 → 阻断但提供逃生通道（用完整路径）
```

**逃生通道**（仅对非 CRITICAL 命令）：
```powershell
# Remove-Item 等非 CRITICAL 命令的逃生通道
& (Get-Command Microsoft.PowerShell.Management\Remove-Item -ErrorAction SilentlyContinue) -Recurse -Force <path>
```

**注意**：CRITICAL_BLOCKS 命令（format/vssadmin delete/diskpart 等）**无逃生通道**——这些命令在任何情况下都不应在 AI 开发项目中执行。

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

**结论**：现有 5 层防护对 `git clean -fd` 全部失效。需要新增一个在 git 执行前的拦截层。

### 4.3 alias 失效影响范围

| 命令 | alias 配置 | alias 是否生效 | 影响 |
|---|---|---|---|
| `git clean` | `alias.clean = !python scripts/git_guard.py clean` | ❌ 不生效 | untracked 文件被删除 |
| `git reset --hard` | `alias.reset = !python scripts/git_guard.py reset` | ❌ 不生效 | 未提交修改被丢弃 |
| `git checkout --` | `alias.checkout = !python scripts/git_guard.py checkout` | ❌ 不生效 | 文件修改被覆盖 |
| `git restore` | `alias.restore = !python scripts/git_guard.py restore` | ❌ 不生效 | 文件修改被覆盖 |
| `git stash` | `alias.stash = !python scripts/git_guard.py stash` | ❌ 不生效 | 修改被移走（可恢复但风险高） |
| `git revert` | `alias.revert = !python scripts/git_guard.py revert` | ❌ 不生效 | 提交被反转 |
| `git mv` | `alias.mv = !python scripts/git_guard.py mv` | ❌ 不生效 | 文件被移动 |

**结论**：全部 7 个 DANGEROUS_SUBCOMMANDS 的 alias 拦截均失效。此外 `git branch -D` 和 `git push --force` 不在 DANGEROUS_SUBCOMMANDS 中，alias 拦截从未覆盖这两个命令。

## 5. 第一性原理分析：100%AI 开发项目的文件安全需求模型

### 5.1 与传统项目的本质区别

| 维度 | 传统项目 | 100%AI 开发项目 |
|---|---|---|
| 操作者 | 人类（理解危险） | AI（不理解危险，只执行指令） |
| 并发度 | 1-3 人 | 10-26 个并发 AI session |
| 文件保护意识 | 高（人类知道 git clean 会删文件） | 零（AI 不知道 clean 不可恢复） |
| 错误恢复能力 | 高（人类会从回收站/stash/reflog 恢复） | 低（AI 不会主动恢复，甚至不知道发生了什么） |
| 操作速度 | 慢（人类思考后执行） | 快（AI 秒级执行，错误瞬间发生） |
| 审查机制 | code review + 人工确认 | 无（AI 直接执行） |

### 5.2 安全需求模型

**核心需求**：在 AI 不理解危险的情况下，从技术层面阻止危险操作发生。

**分层需求**：

| 层 | 需求 | 优先级 |
|---|---|---|
| 需求 1 | 阻止 `git clean` 删除 untracked 文件 | P0（灾难已发生） |
| 需求 2 | 阻止 `git reset --hard` 丢弃未提交修改 | P0（灾难已发生） |
| 需求 3 | 阻止 `git checkout --` / `git restore` 覆盖文件修改 | P0（灾难已发生） |
| 需求 4 | 所有新建/修改文件立即被 git 跟踪（staged/tracked） | P0（clean 不删 tracked） |
| 需求 5 | AI session 修改文件前先加锁（防跨 AI 冲突） | P1（已有设施，需激活使用） |
| 需求 6 | AI session 使用 worktree 隔离（防主工作区污染） | P1（已有设施，需强制遵守） |
| 需求 7 | 永久规则写入 AGENTS.md（所有未来 AI 遵守） | P0（规则持久化） |
| 需求 8 | 定期 push 到远程（最终备份层） | P2（已有 origin/dev，需定期 push） |
| 需求 9 | 阻止 PowerShell 原生破坏性命令（Remove-Item -Recurse -Force/rd /s/del /s 等） | P0（v0.9.0 新增——git wrapper 不覆盖非 git 命令） |
| 需求 10 | 所有拦截/放行操作有审计日志（事后可追溯） | P1（v0.9.0 新增——参考 dcg/SafeRun Guard） |

### 5.3 约束条件

- **Trae IDE 不支持 PreToolUse hooks**：无法在 AI 工具层拦截——必须在 shell 层（PowerShell 函数）拦截
- **Trae IDE 终端为 PowerShell 5.1**：`&&`/`||` 不支持（语法错误），`;`/`|` 是唯一复合命令分隔符——函数覆盖自动处理子命令
- **Trae IDE RunCommand 加载 $PROFILE**：PowerShell 函数覆盖对 AI 发起的命令生效
- **Windows + PowerShell 5.1**：shell 函数覆盖可行（Remove-Item/rd/del 等均可覆盖）
- **git 2.48.1**：alias 无法覆盖内置命令（确认）
- **个人项目**：不能引入需要多人协作的治理机制
- **100% AI 开发（围绕 Trae 编译器）**：规则必须机器可读、AI 可执行（不能依赖人工自觉）

## 6. 裁定结果

### 6.1 方案选型

| 方案 | 机制 | 优点 | 缺点 | 裁定 |
|---|---|---|---|---|
| A. Git Wrapper（PATH 拦截） | PATH 中放 git 脚本/函数 | 底层拦截，无法绕过 | 需处理 git 全局选项 | ✅ **采用** |
| B. AI 工具层防护 | PreToolUse hooks / permissions | 精准拦截 | Trae IDE 不支持 hooks | ❌ 不适用 |
| C. 保护性 git add | 文件 staged 后 clean 不删 | 零侵入 | 依赖 AI 自觉 | ✅ **采用（补充层）** |
| D. 文件锁系统 | AI 改文件前先 acquire | 防跨 AI 冲突 | 不防 clean，依赖自觉 | ✅ **采用（P1 激活）** |
| E. session_worktree | 工作区隔离 | 根本消除冲突 | AI 未遵守 | ✅ **采用（P1 强制）** |
| F. git hooks（pre-*） | git 内置 hook | git 原生支持 | git 无 pre-clean hook | ❌ 不适用 |
| G. 定期 auto-commit | 定时把 untracked 变 tracked | 自动保护 | 可能 commit 垃圾文件 | ⏸ 远期考虑 |
| H. PowerShell 原生命令覆盖（v0.9.0） | 函数覆盖 Remove-Item/rd/del 等 | 拦截非 git 破坏性命令 | 需处理 cmdlet 参数绑定 | ✅ **采用（L7）** |
| I. 审计日志（v0.9.0） | JSONL 持久化所有拦截/放行 | 事后可追溯 | 日志文件增长 | ✅ **采用（L8）** |

### 6.2 最终裁定：多层组合防御（v0.9.0 更新——新增 L7/L8）

```
L1: PowerShell git() 函数（PATH 拦截）——所有 git 调用必经，硬阻断危险 git 命令
L2: 保护性 git add——staged 文件 clean 不删
L3: AGENTS.md + .trae/rules/ RULE-GIT-SAFE——永久规则，所有 Trae IDE AI 遵守
L4: git_guard.py 保留——直接调用时有效，作为 L1 的补充
L5: lock_files.py 激活——AI 改文件前先加锁
L6: session_worktree 强制——AI 使用独立 worktree
L7: PowerShell 原生命令拦截（v0.9.0 新增）——Remove-Item/rd/del/rm/format/vssadmin/diskpart 函数覆盖
L8: 审计日志（v0.9.0 新增）——所有拦截/放行操作写入 JSONL 日志，事后可追溯
L9: Trash Redirect（v1.0.0 新增）——非 CRITICAL 删除命令重定向到回收站而非阻断，AI 不卡住且文件可恢复
```

### 6.3 不采用的方案及理由

| 方案 | 不采用理由 |
|---|---|
| Go 编写的 git wrapper（git-sentinel） | 过度工程——个人项目不需要编译 Go 二进制，PowerShell 函数足够 |
| Claude Code PreToolUse hooks | Trae IDE 不支持 hooks |
| git hooks（pre-clean） | git 没有 pre-clean hook（git hook 只覆盖 commit/push/checkout 等，不覆盖 clean） |
| 定期 auto-commit | 可能 commit 垃圾文件，需设计排除规则，复杂度高，远期考虑 |

## 7. 施工方案

### 7.1 施工项 1：PowerShell 安全 wrapper 函数集（L1，P0）

**目标**：在 PowerShell 中定义 `git()` 函数拦截危险 git 命令，**并定义 `Remove-Item()`/`rd()`/`del()` 等函数拦截 PowerShell/CMD 原生破坏性命令**（v0.9.0 新增）。

**v0.9.0 变更说明**：原 v0.8.0 只覆盖 git 命令。v0.9.0 全网搜索发现 opencode-fusion PR #12 证实"Windows 上 AI agent 几乎全部用 PowerShell"，Cursor 论坛 2026-04~07 有多起 `rmdir /s /q` 误删整个 C: 盘事故。必须扩展 wrapper 覆盖 PowerShell/CMD 原生破坏性命令。

#### 7.1.1 Part A：git 命令拦截函数（保持 v0.8.0 不变）

在 PowerShell profile（`$PROFILE`）中添加 `git()` 函数：

```powershell
# >>> git-safety-wrapper >>> (ZephyrAlpha #ARCH-GIT-CLEAN-GUARD-FIX)
# 自动检测真实 git.exe 路径（不用函数名 git，避免循环调用）
# 优先级：环境变量 > 注册表 > 硬编码常见路径
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

# 审计日志函数（v0.9.0 新增，见 §7.10）
function _ZephyrAuditLog {
    param([string]$Command, [string]$Action, [string]$Reason, [string]$EscapeHint = '')
    $_logDir = Join-Path $env:USERPROFILE '.zephyr_audit'
    if (-not (Test-Path $_logDir)) { New-Item -ItemType Directory -Path $_logDir -Force | Out-Null }
    $_logFile = Join-Path $_logDir ("audit_{0:yyyyMMdd}.jsonl" -f (Get-Date))
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

    if ($blocked) {
        Write-Host "[GIT-SAFE] BLOCKED: git $fullArgs — $reason" -ForegroundColor Red
        Write-Host "  如需执行（确认安全后），用完整路径：" -ForegroundColor Yellow
        Write-Host "  & '$_realGit' $fullArgs" -ForegroundColor Yellow
        _ZephyrAuditLog -Command "git $fullArgs" -Action 'BLOCKED' -Reason $reason -EscapeHint "& '$_realGit' $fullArgs"
        return 1
    }

    _ZephyrAuditLog -Command "git $fullArgs" -Action 'ALLOWED' -Reason 'safe command'
    & $_realGit @args
}
# <<< git-safety-wrapper <<<
```

#### 7.1.2 Part B：PowerShell/CMD 原生破坏性命令拦截（v0.9.0 新增——ARCH-POWERSHELL-DESTRUCTIVE-GUARD（待登记））

> **核心算法**：双重安全检查（参考 cmd_command_execution_ai_agent）
> - Layer 1: DANGEROUS_PATTERNS 模式匹配 → 匹配则进入 Layer 2
> - Layer 2: CRITICAL_BLOCKS 绝对禁止验证 → 匹配则硬阻断（无逃生通道）

```powershell
# >>> powershell-destructive-guard >>> (ZephyrAlpha ARCH-POWERSHELL-DESTRUCTIVE-GUARD（待登记） v0.9.0)

# 保存内置 cmdlet 引用（在函数覆盖之前获取，避免循环调用）
$_realRemoveItem = (Get-Command Microsoft.PowerShell.Management\Remove-Item -ErrorAction SilentlyContinue)

# CRITICAL_BLOCKS：绝对禁止，无逃生通道（系统级破坏，任何情况都不应在 AI 开发中执行）
$_criticalBlocks = @(
    'format ', 'vssadmin delete', 'wbadmin delete', 'cipher /w',
    'diskpart', 'reg delete', 'bcdedit', 'netsh advfirewall',
    'schtasks /delete', 'schtasks /create', 'schtasks /change',
    'sc delete', 'sc stop',
    'powershell -enc', 'powershell -encodedcommand',
    'powershell.exe -enc', '-encodedcommand'
)

# Remove-Item 覆盖：仅阻断 -Recurse -Force 组合（递归强制删除）
# 不阻断：不带 -Recurse 的单文件删除（可恢复），目标在 $env:TEMP 的临时文件删除
function Remove-Item {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false, Position=0)]
        [string[]]$Path,
        [switch]$Recurse,
        [switch]$Force,
        [switch]$Confirm,
        [switch]$WhatIf,
        [string]$Filter,
        [string[]]$Include,
        [string[]]$Exclude,
        [string]$LiteralPath
    )

    $fullCmd = "Remove-Item $($_args -join ' ')"
    $isCritical = $false
    foreach ($pattern in $_criticalBlocks) {
        if ($fullCmd -like "*$pattern*") { $isCritical = $true; break }
    }

    if ($Recurse -and $Force) {
        # 检查目标是否在临时目录（放行临时文件清理）
        $targetPath = if ($Path) { $Path[0] } elseif ($LiteralPath) { $LiteralPath } else { '' }
        $isTemp = $false
        if ($targetPath -and $env:TEMP) {
            $resolvedTarget = (Resolve-Path $targetPath -ErrorAction SilentlyContinue)?.Path
            if ($resolvedTarget -and $resolvedTarget.StartsWith($env:TEMP, [System.StringComparison]::OrdinalIgnoreCase)) {
                $isTemp = $true
            }
        }

        if (-not $isTemp) {
            Write-Host "[SAFE] BLOCKED: Remove-Item -Recurse -Force — 递归强制删除（物理删除不进回收站）" -ForegroundColor Red
            Write-Host "  如需执行（确认安全后），用内置 cmdlet：" -ForegroundColor Yellow
            Write-Host "  & $_realRemoveItem -Recurse -Force <path>" -ForegroundColor Yellow
            _ZephyrAuditLog -Command $fullCmd -Action 'BLOCKED' -Reason 'Remove-Item -Recurse -Force 递归强制删除' -EscapeHint "& `$_realRemoveItem -Recurse -Force <path>"
            return
        }
    }

    # 非危险调用：透传给内置 Remove-Item
    $_ZephyrAuditLog -Command $fullCmd -Action 'ALLOWED' -Reason 'safe Remove-Item call'
    & $_realRemoveItem @PSBoundParameters
}

# rd / rmdir / del / erase / rm 函数覆盖（CMD 兼容命令）
# PowerShell 中 rd/del/erase 是 Remove-Item 的别名，定义函数会优先于别名
function rd { param([Parameter(Position=0)][string]$Path, [string[]]$Args)
    if ($Args -join ' ' -match '/s') {
        Write-Host "[SAFE] BLOCKED: rd /s — CMD 递归删除目录" -ForegroundColor Red
        _ZephyrAuditLog -Command "rd $Path $($Args -join ' ')" -Action 'BLOCKED' -Reason 'rd /s CMD 递归删除'
        return 1
    }
    # 不带 /s 的 rd 安全，透传
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
        # 检查目标是否在临时目录
        $isTemp = $false
        foreach ($a in $args) {
            if ($a -notmatch '^-' -and $a -and $env:TEMP) {
                $resolved = (Resolve-Path $a -ErrorAction SilentlyContinue)?.Path
                if ($resolved -and $resolved.StartsWith($env:TEMP, [System.StringComparison]::OrdinalIgnoreCase)) {
                    $isTemp = $true; break
                }
            }
        }
        if (-not $isTemp) {
            Write-Host "[SAFE] BLOCKED: rm -rf — Unix 递归强制删除" -ForegroundColor Red
            _ZephyrAuditLog -Command "rm $argStr" -Action 'BLOCKED' -Reason 'rm -rf 递归强制删除'
            return 1
        }
    }
    # 透传给真实 rm（若存在）或 Remove-Item
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

> **注意**：以上代码是**设计规格**，实际施工时由 `scripts/install_git_safety_wrapper.ps1`（§7.7）写入 `$PROFILE`。`Remove-Item` 覆盖使用 `Get-Command Microsoft.PowerShell.Management\Remove-Item` 获取内置 cmdlet 引用，避免循环调用。

#### 7.1.3 Part C：复合命令拆分算法（v0.9.0 新增——参考 SafeRun Guard）

> **问题**：AI 可能执行 `echo ok && Remove-Item -Recurse -Force x` 等复合命令。PowerShell 中 `&&`（v7+）和 `;` 分隔的命令会分别执行，`Remove-Item` 函数会触发拦截。但 PowerShell 5.1 不支持 `&&`，Trae IDE 的 RunCommand 使用 PowerShell 5.1，所以 `&&` 会被当作语法错误或字面量处理。需确认 Trae IDE RunCommand 的实际行为。

**PowerShell 5.1 复合命令行为**：
- `cmd1 ; cmd2`：顺序执行，每个命令独立调用函数 → `Remove-Item` 函数会触发拦截 ✅
- `cmd1 | cmd2`：管道，管道左侧输出传给右侧 → 函数调用仍触发 ✅
- `cmd1 && cmd2`：PowerShell 5.1 **不支持** `&&`（语法错误）→ AI 不会用此形式
- `cmd1 || cmd2`：PowerShell 5.1 **不支持** `||`（语法错误）→ AI 不会用此形式
- `& { cmd1; cmd2 }`：脚本块调用 → 函数调用仍触发 ✅

**结论**：PowerShell 5.1 的命令分隔符（`;`/`|`）天然使每个命令独立调用函数，**无需额外的复合命令拆分逻辑**。函数覆盖机制自动处理复合命令的每个子命令。这与 SafeRun Guard 需要 shell 层拆分不同——因为 SafeRun Guard 是 PreToolUse hook（拦截整个命令字符串），而我们是函数覆盖（每个命令独立触发函数）。

**残留风险**：`Invoke-Expression "Remove-Item -Recurse -Force x"` 会绕过函数覆盖（因为 `Invoke-Expression` 在新作用域中解析字符串，可能直接调用内置 cmdlet 而非函数）。`iex`/`Invoke-Expression` 已列入 §4.L 的 CRITICAL_BLOCKS 拦截列表。

#### 7.1.4 Part D：ProxyCommand 最佳实践修正（v1.2.0 新增）

> **v1.2.0 发现**：v1.0.0/v1.1.0 中手写 `Remove-Item` 函数的 `param()` 块是错误做法（来源：commandinline.com 2026-06）。正确方法是用 `ProxyCommand::Create()` 生成代理脚手架。

**v1.0.0 的问题**：
- 手写 `param()` 块丢失了动态参数（`-Credential`/`-Stream` 等 provider 供应参数）
- 丢失了 `-WhatIf`/`-Confirm` 的 ShouldProcess 支持
- 丢失了管道输入支持（`Get-ChildItem | Remove-Item` 不工作）
- 原始 cmdlet 更新时手写 param() 会断裂

**v1.2.0 修正方案**：使用 `ProxyCommand::Create()` 自动生成完整代理：

```powershell
# v1.2.0 修正：用 ProxyCommand 生成 Remove-Item 代理
$meta = [System.Management.Automation.CommandMetaData](
    Get-Command Microsoft.PowerShell.Management\Remove-Item
)
$proxyCode = [System.Management.Automation.ProxyCommand]::Create($meta)

# 在生成的代理代码中插入拦截逻辑：
# 1. 在 Begin 块中检查 $PSBoundParameters 是否含 -Recurse + -Force
# 2. 若含且目标不在 $env:TEMP → 重定向到回收站（v1.0.0 trash redirect）
# 3. 若不含 → 通过 steppable pipeline 透传给 Microsoft.PowerShell.Management\Remove-Item
# 4. 保留 DynamicParam 块（-Credential 等动态参数依赖此块）

# 安装时：install_git_safety_wrapper.ps1 用 ProxyCommand::Create() 生成代理代码写入 $PROFILE
```

**关键修正点**：
1. 用 `Microsoft.PowerShell.Management\Remove-Item`（模块限定名）调用原始 cmdlet，避免无限递归
2. 保留 `DynamicParam` 块——`-Credential` 等 provider 参数依赖此块
3. 用 steppable pipeline 透传——保留 `Get-ChildItem | Remove-Item` 管道行为
4. 保留 `-WhatIf`/`-Confirm` 的 ShouldProcess 支持

**对 §7.1.2 Part B 代码的影响**：Part B 的手写 `Remove-Item` 函数应替换为 ProxyCommand 生成的代理。`rd`/`del`/`rm` 等函数因不是内置 cmdlet，不受此问题影响（它们是别名或外部命令），保持手写即可。

**安装方式**：通过 `scripts/install_git_safety_wrapper.ps1` 一键安装（见 §7.7）。
脚本功能：检测 `$PROFILE` → 检测是否已安装（幂等，搜索 marker 注释）→ 检测 git/cmdlet 真实路径 → 追加 wrapper 函数集 → 支持 `-Uninstall`。

**逃生通道**：

| 场景 | 逃生命令 |
|---|---|
| git 危险命令 | `& 'C:\Program Files\Git\cmd\git.exe' clean -fd` |
| Remove-Item 递归删除 | `& $_realRemoveItem -Recurse -Force <path>` |
| rd /s（CMD 递归删除） | `& cmd /c "rd /s <path>"`（通过 cmd 子进程绕过函数） |
| rm -rf（Unix 递归删除） | `& (Get-Command rm.exe).Source -rf <path>` |
| CRITICAL 命令（format/vssadmin/diskpart） | **无逃生通道**——永远阻断 |

**git 命令阻断/放行规则明细**（保持 v0.8.0 不变）：

| 命令 | 阻断条件 | 放行条件 | 理由 |
|---|---|---|---|
| `git clean` | `-f`/`-fd`/`-fdx`（删除文件） | `-n`/`--dry-run`（只预览） | dry-run 安全，参考 dcg/git-safety-guard |
| `git reset` | `--hard`/`--merge` | `--soft`/`--mixed`/无参数 | --hard/--merge 覆盖工作区，--soft/--mixed 不覆盖 |
| `git checkout` | `-- <file>` / `HEAD -- <file>` / `.` | `<branch>`/`-b <branch>`/`--orphan` | `--`/`.` 形式丢弃修改，切分支/建分支安全 |
| `git restore` | 不带 `--staged`，或带 `--worktree` | 仅 `--staged` | `--staged` 仅取消暂存不丢修改，`--worktree` 丢弃修改 |
| `git stash` | `push`/`pop`/`apply`/`clear`/`branch`/`drop`/无子命令 | `list`/`show` | 只读操作放行，修改性操作阻断 |
| `git rm` | 不带 `--cached` | `--cached`（仅从暂存区移除） | 不带 --cached 会删工作区文件 |
| `git branch` | `-D`/`--delete-force` | `-d`（普通删除，检查合并） | -D 不检查合并状态，可能丢失未合并代码 |
| `git push` | `--force`/`-f` | `--force-with-lease`（安全 force push） | --force 覆盖远程历史，--force-with-lease 有远程检查 |

**PowerShell 原生命令阻断/放行规则明细**（v0.9.0 新增）：

| 命令 | 阻断条件 | 放行条件 | 逃生通道 | 理由 |
|---|---|---|---|---|
| `Remove-Item` | `-Recurse -Force` 同时存在且目标不在 `$env:TEMP` | 不带 `-Recurse`，或目标在临时目录 | `& $_realRemoveItem -Recurse -Force <path>` | 递归强制删除不可恢复 |
| `rd`/`rmdir` | 带 `/s` | 不带 `/s` | `& cmd /c "rd /s <path>"` | /s 递归删除（已致多起 C: 盘全删事故） |
| `del`/`erase` | 带 `/s` 或 `/f` | 不带 `/s`/`/f` | `& cmd /c "del /s <path>"` | /s 批量删除 /f 强制删除 |
| `rm` | `-rf`/`-fr` 且目标不在临时目录 | 目标在 `$env:TEMP`/`/tmp` | `& (Get-Command rm.exe).Source -rf <path>` | Unix 递归强制删除 |
| `format` | 任何调用 | 无放行 | **无** | 格式化磁盘——系统级破坏 |
| `vssadmin delete` | `delete` 子命令 | 非 delete 子命令 | **无** | 删除卷影副本（备份破坏） |
| `diskpart` | 任何调用 | 无放行 | **无** | 磁盘分区操作——系统级破坏 |

**对现有脚本的影响评估**：
- `git add`/`git commit`/`git diff`/`git status`/`git log`/`git push`/`git pull`/`git merge`/`git rebase`：全部放行（安全命令）
- `Remove-Item` 不带 `-Recurse -Force`（如 `Remove-Item temp.txt`）：放行（单文件删除）
- `Remove-Item -Recurse -Force $env:TEMP\*`：放行（临时目录清理）
- `test_concurrent_safety.ps1` 中的 `Remove-Item $_.FullName -Force`（Phase 1 清理 .tmp 文件）：**会被阻断**——因为 `-Force` 存在但无 `-Recurse`...实际上不带 `-Recurse` 应该放行。需确认：`Remove-Item <file> -Force`（单文件+强制）是否阻断？→ **不阻断**（只有 `-Recurse -Force` 组合才阻断）
- `session_worktree_abort` 中的 `git checkout --`（恢复文件）：**会被阻断**——需用 `& $_realGit checkout -- <file>` 逃生通道
- `GitCommitGateway` 中的 `git reset --soft`：放行（不带 `--hard`）
- pre-commit hook 中的 `git diff --cached`/`git stash`（stashing unstaged）：**stash 会被阻断**——pre-commit 框架需用 `& $_realGit stash` 逃生通道
- `backup.ps1` 中的 `Remove-Item` 清理旧备份：若带 `-Recurse -Force` 且目标不在 TEMP → **会被阻断**——需用逃生通道或调整脚本使用 `& $_realRemoveItem`

**结论**：v0.9.0 扩展后，wrapper 对现有脚本的影响从 2 个场景（session_worktree_abort + pre-commit stash）增加到 4 个场景（+test_concurrent_safety 清理 + backup.ps1 旧备份清理）。后两个场景可通过确认目标安全性后使用逃生通道处理。**关键收益**：覆盖了 PowerShell 原生破坏性命令这一最大安全 gap。

### 7.2 施工项 2：AGENTS.md + .trae/rules/ RULE-GIT-SAFE 永久规则（L3，P0）

**目标**：在 AGENTS.md 和 .trae/rules/project_rules.md 中新增 `RULE-GIT-SAFE` 节，作为所有 AI 必须遵守的永久规则。

**为什么要写两个文件**：
- AGENTS.md 是项目规则真源（所有 AI 工具通用）
- .trae/rules/project_rules.md 是 **Trae IDE 的 AI 规则入口**——Trae IDE 的 AI 读此文件获取项目规则，如果不写入此文件，Trae IDE 的 AI 不会看到 RULE-GIT-SAFE

**内容**：
```markdown
## RULE-GIT-SAFE：Git 安全铁律（2026-08-11 #ARCH-GIT-CLEAN-GUARD-FIX）

> **背景**：2026-08-11 灾难——AI 执行 git clean -fd 物理删除多个 untracked 文件。
> git alias 无法覆盖内置命令（git 2.48.1 Windows 实测确认），alias 拦截全部失效。

**所有 AI session MUST 遵守**：

1. **禁止执行以下 git 命令**：
   - `git clean -f`/`-fd`/`-fdx`（`git clean -n` dry-run 预览是安全的）
   - `git reset --hard`/`--merge`（用 `git reset --soft` 或 `git reset --mixed` 替代）
   - `git checkout -- <file>` / `git checkout HEAD -- <file>` / `git checkout .`（用 `git checkout <branch>` / `git checkout -b` 切/建分支是安全的）
   - `git restore <file>`（`git restore --staged` 取消暂存是安全的）
   - `git stash`（`git stash list`/`git stash show` 只读是安全的）
   - `git rm <file>`（`git rm --cached` 仅从暂存区移除是安全的）
   - `git branch -D`（强制删分支，用 `git branch -d` 普通删除是安全的）
   - `git push --force`/`-f`（用 `git push --force-with-lease` 安全 force push 是安全的）

2. **每轮修改后立即 `git add <file>`**：staged 文件不会被 git clean 删除。

3. **修改文件前先加锁**：`python scripts/lock_files.py acquire <file> <session_id>`

4. **完成修改后释放锁**：`python scripts/lock_files.py release <file> <session_id>`

5. **如需执行危险命令**：必须先 commit 所有修改 + 经用户确认 + 用完整路径调用真实 git：
   `& 'C:\Program Files\Git\cmd\git.exe' clean -fd`
```

**位置**：插入在 AGENTS.md `RULE-WORKTREE` 之后、`RULE-GUARDIAN` 之前（或按现有顺序适当位置）。

### 7.3 施工项 3：project_memory 确认（L3，P0）

已在上一轮写入 project_memory.md。需确认内容完整，包含：
- alias 失效根因
- 防护规则（4 条）
- 灾难时间线

### 7.4 施工项 4：git_guard.py alias 配置清理（L4，P1）

**目标**：alias 已失效，但配置仍在 `.git/config` 中。保留配置不删（无害），但在 git_guard.py 文件头注释中标注"alias 拦截在 Windows git 2.48.1 上不生效，依赖 PowerShell wrapper"。

**不删 alias 配置的理由**：①在其他 git 版本/平台上 alias 可能生效 ②删除配置会丢失意图记录 ③配置无害（不生效≠有害）

### 7.5 施工项 5：lock_files.py 激活（L5，P1）

**目标**：让 AI session 主动使用文件锁。

**方式**：在 AGENTS.md RULE-GIT-SAFE 和 AI_review_instructions §0 规则 10 中要求 AI 修改文件前先 acquire 锁。

**已完成的配置**：AI_review_instructions §0 规则 10 已加入文件锁使用要求。

### 7.6 施工项 6：session_worktree 强制（L6，P1）

**目标**：让 AI session 遵守 RULE-WORKTREE，使用独立 worktree。

**方式**：AGENTS.md 已有 RULE-WORKTREE，但 AI 未遵守。后续考虑在 pre-commit hook 中检测主工作区 commit 次数（已有 GATE-WORKTREE-REQUIRED，但阈值 5 次太高，可调低到 3 次）。

### 7.7 施工项 7：git wrapper 安装脚本（P0）

**目标**：创建 `scripts/install_git_safety_wrapper.ps1`，一键安装/卸载 PowerShell git wrapper。

**功能**：
- 检测 `$PROFILE` 是否存在，不存在则创建
- 检测是否已安装（幂等，搜索 marker 注释）
- 检测 git 真实路径（`Get-Command git.exe`）
- 将 wrapper 函数追加到 `$PROFILE`
- 支持 `-Uninstall` 参数卸载

### 7.8 施工项 8：AI_review_instructions §0 内嵌确认（P0）

**目标**：确认 AI_review_instructions §0 规则 9（Git 安全铁律）和规则 10（文件锁使用）已正确写入，且每个 AI 指令块的约束节也包含 git 安全要求。

**当前状态**：§0 通用规则已加入规则 9/10。各 AI 指令块的约束节尚未同步更新。

### 7.9 施工项 9：Trae IDE 开发约束专节（v0.9.0 新增——围绕 Trae 编译器开发）

> **用户强调**："整个开发是围绕着 TRae编译器来开发的。"
> 本节将 Trae IDE 的所有约束集中声明，作为整个安全方案的设计前提。

#### 7.9.1 Trae IDE 是唯一开发平台

本项目 100% 围绕 Trae IDE（编译器）开发，无其他 AI 工具参与：

| 维度 | Trae IDE 约束 | 对安全方案的影响 |
|---|---|---|
| **AI 工具** | Trae IDE 是唯一 AI 开发工具 | 只需适配 Trae，无需适配 Claude Code/Cursor/Codex |
| **命令执行** | AI 通过 RunCommand 执行命令 | RunCommand 使用 PowerShell 5.1 → PowerShell 函数覆盖有效 |
| **AI 规则入口** | `.trae/rules/project_rules.md` | RULE-GIT-SAFE 必须写入此文件（非 AGENTS.md 唯一） |
| **Hook 支持** | **不支持 PreToolUse hooks** | 无法在 AI 工具层拦截命令 → 必须在 shell 层（PowerShell 函数）拦截 |
| **终端类型** | PowerShell 5.1 | `&&`/`||` 不支持（语法错误），`;`/`|` 是唯一复合命令分隔符 |
| **$PROFILE 加载** | RunCommand 加载 `$PROFILE` | PowerShell 函数覆盖生效 |
| **-NoProfile 风险** | 实测 RunCommand 不使用 `-NoProfile` | $PROFILE 中的 wrapper 会加载 |
| **.traeignore** | AI 忽略 `.ailocks/` 和 `.git/` | AI 看不到文件锁状态和 git hook 配置——需通过 `.trae/rules/` 显式告知 |
| **无其他 AI 配置** | 无 `.claude/`/`.cursor/`/`.codex/`/`.continue/` 目录 | 确认 100% Trae IDE 开发 |

#### 7.9.2 Trae IDE 约束驱动的方案选型

| 方案 | Trae IDE 是否支持 | 选型 |
|---|---|---|
| PreToolUse hooks（dcg/SafeRun Guard/Claude Code 方式） | ❌ 不支持 | 不采用 |
| PowerShell 函数覆盖（$PROFILE 注入） | ✅ RunCommand 加载 $PROFILE | **采用（L1 主防线）** |
| `.trae/rules/` 规则注入 | ✅ AI 读此文件 | **采用（L3 规则层）** |
| AGENTS.md 规则 | ✅ AI 读此文件 | **采用（L3 补充）** |
| git hooks（pre-commit/post-commit） | ✅ git 原生支持 | 采用（L2 commit 门禁） |
| git alias 拦截 | ❌ Windows git 2.48.1 alias 无法覆盖内置命令 | 不采用（已失效） |
| Go/Rust 编译 wrapper | ⚠️ 可行但过度工程 | 不采用（PowerShell 足够） |

#### 7.9.3 Trae IDE 多 AI 并发模型

Trae IDE 支持多 AI session 并发（当前 26 路），每个 session 通过 RunCommand 在同一 PowerShell 环境中执行命令。这意味着：
- 所有 session 共享同一 `$PROFILE` → wrapper 函数对所有 session 生效 ✅
- 所有 session 共享同一工作目录 `d:\ZephyrAlpha` → 需文件锁防冲突（§7.5/§11.3.2）
- 所有 session 共享同一 `.trae/rules/` → 规则对所有 session 生效 ✅
- session 间无隔离 → 需 worktree 隔离（§11.3.1）

#### 7.9.4 Trae IDE 验证清单

| 验证项 | 验证方法 | 预期结果 |
|---|---|---|
| RunCommand 加载 $PROFILE | 在 RunCommand 中执行 `Get-Command git` | 显示 `Function` 而非 `Application` |
| wrapper 函数生效 | 在 RunCommand 中执行 `git clean -fd` | BLOCKED |
| .trae/rules/ 被读取 | 新 AI session 读 project_rules.md | 看到 RULE-GIT-SAFE |
| -NoProfile 不使用 | 检查 RunCommand 进程命令行 | 无 `-NoProfile` 参数 |

### 7.10 施工项 10：审计日志设施（v0.9.0 新增——JSON 格式持久化）

> **参考**：dcg/SafeRun Guard/OpenClaw 审批系统均有审计日志。当前 wrapper 只 `Write-Host` 到控制台，无持久化记录。

**目标**：所有 wrapper 拦截/放行操作写入 JSONL 审计日志，支持事后追溯。

**实现**：已在 §7.1.1 的 `_ZephyrAuditLog` 函数中实现。日志规格：

| 项 | 值 |
|---|---|
| 日志目录 | `$env:USERPROFILE\.zephyr_audit\` |
| 日志文件 | `audit_{yyyyMMdd}.jsonl`（按天分割） |
| 日志格式 | JSONL（每行一个 JSON 对象） |
| 日志字段 | `timestamp`/`action`/`command`/`reason`/`session`/`pid`/`escape_hint`(可选) |
| action 值 | `ALLOWED`/`BLOCKED`/`HARDBLOCKED` |
| 保留策略 | 30 天后自动清理（由 `scripts/governance/audit_log_rotator.py` 实现，远期） |

**日志示例**：
```jsonl
{"timestamp":"2026-08-11T14:30:00.1234567+08:00","action":"BLOCKED","command":"git clean -fd","reason":"git clean 删除 untracked 文件","session":"AI-06","pid":12345,"escape_hint":"& 'C:\\Program Files\\Git\\cmd\\git.exe' clean -fd"}
{"timestamp":"2026-08-11T14:31:00.2345678+08:00","action":"ALLOWED","command":"git status","reason":"safe command","session":"AI-06","pid":12345}
{"timestamp":"2026-08-11T14:32:00.3456789+08:00","action":"HARDBLOCKED","command":"format d:","reason":"format 格式化磁盘","session":"AI-08","pid":12346}
```

**查询工具**（远期施工）：
```bash
# 查看今天的阻断记录
Get-Content "$env:USERPROFILE\.zephyr_audit\audit_$(Get-Date -Format yyyyMMdd).jsonl" |
    ConvertFrom-Json | Where-Object { $_.action -ne 'ALLOWED' }

# 查看特定 session 的操作
Get-Content "$env:USERPROFILE\.zephyr_audit\audit_*.jsonl" |
    ConvertFrom-Json | Where-Object { $_.session -eq 'AI-06' }
```

### 7.11 施工项 11：Trash Redirect 算法（v1.0.0 新增——参考 prevent-llm-delete）

> **核心创新**：对非 CRITICAL 的破坏性命令，不阻断而是**重定向到 Windows 回收站**。AI "成功"完成删除，但文件可从回收站恢复。

**为什么 redirect 优于 block**（参考 §3.6.2 分析）：
1. AI 不卡住——命令"成功"返回，AI 继续后续工作流
2. 文件可恢复——回收站一键还原，不永久丢失
3. 减少 escape hatch 滥用——AI 不需要学习逃生通道
4. 审计完整——日志记录 `action=REDIRECTED`（区别于 `BLOCKED`/`HARDBLOCKED`）

**适用范围**：

| 命令 | v0.9.0 行为 | v1.0.0 行为 | 理由 |
|---|---|---|---|
| `Remove-Item -Recurse -Force` | BLOCKED | **REDIRECTED**（到回收站） | 非 CRITICAL，文件可恢复 |
| `rd /s` | BLOCKED | **REDIRECTED** | 非 CRITICAL |
| `del /s` | BLOCKED | **REDIRECTED** | 非 CRITICAL |
| `rm -rf` | BLOCKED | **REDIRECTED** | 非 CRITICAL |
| `format` | HARDBLOCKED | HARDBLOCKED（不变） | CRITICAL——系统级破坏 |
| `vssadmin delete` | HARDBLOCKED | HARDBLOCKED（不变） | CRITICAL——备份破坏 |
| `diskpart` | HARDBLOCKED | HARDBLOCKED（不变） | CRITICAL——系统级破坏 |

**实现**：在 §7.1.2 Part B 的 `Remove-Item` 函数中，将 `BLOCKED` 分支替换为 `REDIRECTED` 分支：

```powershell
# v1.0.0 改进：Remove-Item -Recurse -Force 重定向到回收站而非阻断
if ($Recurse -and $Force -and -not $isTemp) {
    # 加载 Recycle Bin API
    Add-Type -AssemblyName Microsoft.VisualBasic

    # 对每个目标路径执行回收站删除
    foreach ($target in ($Path + $LiteralPath | Where-Object { $_ })) {
        $resolvedTarget = (Resolve-Path $target -ErrorAction SilentlyContinue)?.Path
        if ($resolvedTarget) {
            if (Test-Path $resolvedTarget -PathType Container) {
                [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteDirectory(
                    $resolvedTarget,
                    [Microsoft.VisualBasic.FileIO.UIOption]::OnlyErrorDialogs,
                    [Microsoft.VisualBasic.FileIO.RecycleOption]::SendToRecycleBin
                )
            } else {
                [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile(
                    $resolvedTarget,
                    [Microsoft.VisualBasic.FileIO.UIOption]::OnlyErrorDialogs,
                    [Microsoft.VisualBasic.FileIO.RecycleOption]::SendToRecycleBin
                )
            }
            Write-Host "[SAFE] REDIRECTED: Remove-Item -Recurse -Force $resolvedTarget — 已发送到回收站（可恢复）" -ForegroundColor Yellow
            _ZephyrAuditLog -Command $fullCmd -Action 'REDIRECTED' -Reason 'Remove-Item -Recurse -Force 重定向到回收站' -EscapeHint '从回收站恢复：explorer.exe shell:RecycleBinFolder'
        }
    }
    return
}
```

**逃生通道变更**：
- v0.9.0：`& $_realRemoveItem -Recurse -Force <path>`（绕过函数直接删除）
- v1.0.0：从回收站恢复即可（`explorer.exe shell:RecycleBinFolder`），无需绕过函数

**回收站清理策略**：回收站容量有限（默认 10% 磁盘空间），需定期清理。由 `scripts/governance/recycle_bin_monitor.py`（远期）监控回收站容量，超 5GB 时告警。

### 7.12 施工项 12：setup_git_guard_aliases.py 修复（v1.0.0 新增）

**目标**：修复 `scripts/setup_git_guard_aliases.py` 的 DANGEROUS_SUBCOMMANDS 不一致问题。

**当前状态**：`DANGEROUS_SUBCOMMANDS = ["reset", "checkout", "stash", "revert", "restore", "mv"]`（6 个，缺 `clean`）

**修复**：添加 `"clean"` 到列表，与 `git_guard.py` 的 7 个命令对齐。

```python
# 修复前
DANGEROUS_SUBCOMMANDS = ["reset", "checkout", "stash", "revert", "restore", "mv"]

# 修复后
DANGEROUS_SUBCOMMANDS = ["reset", "checkout", "stash", "revert", "restore", "mv", "clean"]
```

**验证**：执行 `python scripts/setup_git_guard_aliases.py status` 后确认 7/7 活跃。

### 7.13 施工项 13：d6_security 接入 pre-commit config（v1.3.0 新增——CRITICAL GAP 修复）

> **背景**：§3.9.4 发现 `detect_git_dangerous.py`/`detect_shell_dangerous.py`/`detect_permanent_file_deletion.py` 等 14 个 d6_security 脚本存在但**未在 .pre-commit-config.yaml 中注册**——静态检测层实际缺失。

**目标**：将 3 个关键 d6_security 脚本接入 .pre-commit-config.yaml，激活静态检测层。

**接入清单**：

| Hook ID | 脚本 | 优先级 | 功能 |
|---|---|---|---|
| `gate-detect-git-dangerous` | `detect_git_dangerous.py` | P0 | 检测代码/文档中的危险 git 命令（ABS-26/27/28） |
| `gate-detect-shell-dangerous` | `detect_shell_dangerous.py` | P0 | 检测代码中的危险 shell 命令（ABS-38/39） |
| `gate-detect-permanent-deletion` | `detect_permanent_file_deletion.py` | P0 | 检测 ttl:permanent 文件删除（PS-STD-012 V1） |

**pre-commit config 片段**（添加到 .pre-commit-config.yaml）：
```yaml
- id: gate-detect-git-dangerous
  name: 检测危险 git 命令
  entry: python scripts/governance/d6_security/detect_git_dangerous.py
  language: system
  pass_filenames: true
  always_run: true

- id: gate-detect-shell-dangerous
  name: 检测危险 shell 命令
  entry: python scripts/governance/d6_security/detect_shell_dangerous.py
  language: system
  pass_filenames: true
  always_run: true

- id: gate-detect-permanent-deletion
  name: 检测 ttl:permanent 文件删除
  entry: python scripts/governance/d6_security/detect_permanent_file_deletion.py
  language: system
  pass_filenames: true
  stages: [pre-commit]
```

**验证**：commit 一个含 `git reset --hard` 的文档 → 被 `gate-detect-git-dangerous` 阻断。

**完整闭环**：接入后，文件删除安全三层闭环真正成立：
- **规则层**：RULE-THREE（AI 自觉遵守）
- **静态检测层**：d6_security pre-commit hooks（commit 时检查）✅ 激活
- **运行时拦截层**：PowerShell wrapper（执行时拦截）

### 7.14 施工项 14：Wrapper fail-open 策略（v1.3.0 新增）

> **背景**：§3.9.2 裁定 wrapper 采用 fail-open 语义——wrapper 出错时放行命令并记录错误。

**目标**：所有 wrapper 函数（git/Remove-Item/rd/del/rm/format/vssadmin/diskpart）统一采用 try/catch + fail-open 模式。

**实现模板**：
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

**fail-open 不适用的场景**：
- CRITICAL_BLOCKS 命令（format/vssadmin delete/diskpart）——这些命令即使 wrapper 出错也**必须阻断**（fail-closed），因为系统级破坏不可逆

**裁定**：非 CRITICAL 命令 fail-open，CRITICAL 命令 fail-closed。

### 7.15 施工项 15：错误分类与 AI 重试防护（v1.3.0 新增）

> **背景**：§3.9.3 opencode-swarm #1875 揭示 AI agent 遇到不识别的错误会无限重试（8000-15000 tokens/循环）。

**目标**：wrapper 返回的错误消息必须**AI 可识别为 STOP 信号**，防止无限重试。

**错误消息格式规范**：
```
[GIT-SAFE] BLOCKED: git clean -fd — git clean 删除 untracked 文件（物理删除不进回收站）
  STOP: 此命令已被安全策略永久阻断，不要重试。
  ALTERNATIVE: 用 git clean -n 预览，或用 & 'C:\Program Files\Git\cmd\git.exe' clean -fd 逃生通道。
```

**关键元素**：
1. `BLOCKED`/`HARDBLOCKED`/`REDIRECTED`/`FAIL_OPEN` action 标签——AI 可解析
2. `STOP: 不要重试` 明确指令——AI 理解为终止信号
3. `ALTERNATIVE:` 替代方案——AI 知道下一步该做什么

**对 AI 的指导**（写入 .trae/rules/project_rules.md RULE-GIT-SAFE）：
```
遇到 [GIT-SAFE] BLOCKED 或 [SAFE] BLOCKED 消息时：
  1. 不要重试相同命令
  2. 查看 ALTERNATIVE: 行的替代方案
  3. 如需执行被阻断的命令，用逃生通道（完整路径调用真实 git/cmdlet）
```

### 7.16 施工项 16：Circuit Breaker 模式（v1.4.0 新增——防 AI 无限尝试危险命令）

> **背景**：第六轮搜索发现 Circuit Breaker 是 AI agent 安全的关键模式（来源：valuestreamai/pockit.tools/channel.tel/truefoundry，均为 2026 年发表）。AI agent 被阻断后可能反复尝试不同的危险命令变体——circuit breaker 在 N 次阻断后"跳闸"，拒绝所有命令一段时间，防止 AI 浪费 token 反复尝试。

#### 7.16.1 三态状态机

```
CLOSED（正常运行）
  → 追踪 blocked 次数（滚动窗口 120 秒）
  → blocked ≥ 5 次 → 跳闸 → OPEN

OPEN（熔断状态）
  → 所有命令直接拒绝（包括安全命令）
  → 返回 "[CIRCUIT-OPEN] 安全熔断器已跳闸，N 秒后恢复" 消息
  → 持续 60 秒 → → HALF-OPEN

HALF-OPEN（恢复探测）
  → 允许 1 个命令通过
  → 成功（非 blocked）→ → CLOSED（恢复正常）
  → 失败（blocked）→ → OPEN（再熔断 60 秒）
```

#### 7.16.2 实现规格

| 参数 | 值 | 理由 |
|---|---|---|
| 阈值 | 5 次 blocked | 参考 channel.tel（5 failures in 120s）|
| 滚动窗口 | 120 秒 | 参考 channel.tel |
| 熔断持续时间 | 60 秒 | 参考 channel.tel（60-second recovery）|
| HALF-OPEN 探测数 | 1 个命令 | 标准 circuit breaker 模式 |
| 追踪范围 | 每个 PowerShell session（$PID 级别） | 不跨 session 累积 |

**PowerShell 实现核心**：
```powershell
# Circuit breaker 状态（session 级别）
$_circuitState = @{ Status = 'CLOSED'; BlockedCount = 0; LastBlocked = $null; OpenedAt = $null }

function _ZephyrCircuitCheck {
    $now = Get-Date
    if ($_circuitState.Status -eq 'OPEN') {
        $elapsed = ($now - $_circuitState.OpenedAt).TotalSeconds
        if ($elapsed -ge 60) {
            $_circuitState.Status = 'HALF-OPEN'
        } else {
            $remaining = [math]::Ceiling(60 - $elapsed)
            Write-Host "[CIRCUIT-OPEN] 安全熔断器已跳闸，${remaining}s 后恢复。原因：120s 内 5 次危险命令被阻断。" -ForegroundColor Red
            Write-Host "  STOP: 不要重试任何命令。等待熔断器恢复后使用安全命令。" -ForegroundColor Yellow
            return $false  # 拒绝
        }
    }
    return $true  # 允许
}

function _ZephyrCircuitRecordBlock {
    $now = Get-Date
    # 清理 120 秒前的记录
    if ($_circuitState.LastBlocked -and ($now - $_circuitState.LastBlocked).TotalSeconds -gt 120) {
        $_circuitState.BlockedCount = 0
    }
    $_circuitState.BlockedCount++
    $_circuitState.LastBlocked = $now
    if ($_circuitState.BlockedCount -ge 5 -and $_circuitState.Status -ne 'OPEN') {
        $_circuitState.Status = 'OPEN'
        $_circuitState.OpenedAt = $now
        _ZephyrAuditLog -Command "CIRCUIT_BREAKER" -Action 'CIRCUIT_OPEN' -Reason "5 blocked attempts in 120s"
    }
}

function _ZephyrCircuitRecordSuccess {
    if ($_circuitState.Status -eq 'HALF-OPEN') {
        $_circuitState.Status = 'CLOSED'
        $_circuitState.BlockedCount = 0
        _ZephyrAuditLog -Command "CIRCUIT_BREAKER" -Action 'CIRCUIT_CLOSE' -Reason 'HALF-OPEN probe succeeded'
    }
}
```

**在 wrapper 函数中集成**：
```powershell
function git {
    # Circuit breaker 检查
    if (-not (_ZephyrCircuitCheck)) { return 1 }

    try {
        # ... 拦截逻辑 ...
        if ($blocked) {
            _ZephyrCircuitRecordBlock  # 记录阻断
            # ... 阻断逻辑 ...
            return 1
        }
        _ZephyrCircuitRecordSuccess  # 记录成功
        & $_realGit @args
    } catch {
        # ... fail-open 逻辑 ...
    }
}
```

#### 7.16.3 对 AI 的指导（写入 .trae/rules/ RULE-GIT-SAFE）

```
遇到 [CIRCUIT-OPEN] 消息时：
  1. STOP: 不要重试任何命令（包括安全命令如 git status）
  2. 等待熔断器恢复（60 秒）
  3. 恢复后先执行安全命令（如 git status）验证熔断器已关闭
  4. 如需执行危险命令，用逃生通道并说明原因
```

#### 7.16.4 裁定

**采用 circuit breaker**——防止 AI 被阻断后反复尝试危险命令变体（每次尝试消耗 2000-15000 tokens）。阈值 5 次/120 秒/熔断 60 秒。仅 session 级别（不跨 session 累积，避免一个 session 的行为影响其他 session）。

## 8. 验证

### 8.1 PowerShell wrapper 验证——git 命令

| 测试 | 预期结果 |
|---|---|
| `git clean -fd` | BLOCKED，返回 1，无文件被删 |
| `git clean -n` | 放行，dry-run 只预览 |
| `git reset --hard` | BLOCKED，返回 1 |
| `git reset --merge` | BLOCKED，返回 1 |
| `git checkout -- file.md` | BLOCKED，返回 1 |
| `git checkout .` | BLOCKED，返回 1 |
| `git restore file.md` | BLOCKED，返回 1 |
| `git rm file.md` | BLOCKED，返回 1 |
| `git branch -D feature` | BLOCKED，返回 1 |
| `git push --force origin main` | BLOCKED，返回 1 |
| `git stash` | BLOCKED，返回 1 |
| `git stash list` | 放行，正常输出 |
| `git restore --staged file.md` | 放行，取消暂存 |
| `git rm --cached file.md` | 放行，仅从暂存区移除 |
| `git branch -d merged-branch` | 放行，普通删除（检查合并） |
| `git push --force-with-lease` | 放行，安全 force push |
| `git checkout branch-name` | 放行，切分支 |
| `git checkout -b new-branch` | 放行，建分支 |
| `git reset --soft HEAD~1` | 放行，软重置 |
| `git add file.md` | 放行，正常暂存 |
| `git commit -m "test"` | 放行，正常提交 |
| `git status` | 放行，正常输出 |
| `& 'C:\Program Files\Git\cmd\git.exe' clean -fd` | 逃生通道，直接执行 |

### 8.2 PowerShell 原生破坏性命令验证（v0.9.0 新增）

| 测试 | 预期结果 |
|---|---|
| `Remove-Item -Recurse -Force d:\ZephyrAlpha\docs\` | BLOCKED，无文件被删 |
| `Remove-Item temp.txt` | 放行（单文件删除） |
| `Remove-Item -Recurse -Force $env:TEMP\old_cache\` | 放行（临时目录） |
| `Remove-Item -Force temp.txt` | 放行（-Force 但无 -Recurse） |
| `rd /s /q d:\ZephyrAlpha\docs\` | BLOCKED，CMD 递归删除 |
| `rd d:\ZephyrAlpha\empty_dir` | 放行（不带 /s） |
| `del /s /q *.tmp` | BLOCKED，CMD 批量删除 |
| `del old.txt` | 放行（不带 /s/`/f） |
| `rmdir /s /q d:\ZephyrAlpha` | BLOCKED，CMD 递归删除 |
| `rm -rf d:\ZephyrAlpha\docs\` | BLOCKED，Unix 递归删除 |
| `rm -rf $env:TEMP\cache\` | 放行（临时目录） |
| `rm temp.txt` | 放行（不带 -rf） |
| `format d: /fs:ntfs /q` | HARDBLOCKED，无逃生通道 |
| `vssadmin delete shadows /all` | HARDBLOCKED，无逃生通道 |
| `diskpart` | HARDBLOCKED，无逃生通道 |
| `robocopy /mir empty_dir d:\ZephyrAlpha\docs\` | 待施工：robocopy 覆盖函数未实现（远期） |
| `& $_realRemoveItem -Recurse -Force d:\test\` | 逃生通道，直接执行 |
| `& cmd /c "rd /s /q d:\test\"` | 逃生通道，通过 cmd 子进程绕过 |

### 8.3 审计日志验证（v0.9.0 新增）

| 测试 | 预期结果 |
|---|---|
| 执行 `git clean -fd` 后检查日志 | `~/.zephyr_audit/audit_{date}.jsonl` 含 BLOCKED 记录 |
| 执行 `git status` 后检查日志 | 日志含 ALLOWED 记录 |
| 执行 `format d:` 后检查日志 | 日志含 HARDBLOCKED 记录 |
| 日志 JSON 格式校验 | `ConvertFrom-Json` 成功解析 |
| 日志按天分割 | 不同日期写入不同文件 |

### 8.4 AGENTS.md + .trae/rules/ 规则验证

| 测试 | 预期结果 |
|---|---|
| 新 AI 对话读 AGENTS.md | 看到 RULE-GIT-SAFE |
| 新 AI 对话读 .trae/rules/project_rules.md | 看到 RULE-GIT-SAFE（Trae IDE AI 必读） |
| AI 执行 git clean | 被 PowerShell wrapper 阻断 |
| AI 执行 Remove-Item -Recurse -Force | 被 PowerShell wrapper 阻断 |
| AI 修改文件后 | 执行 git add（规则 2） |

### 8.5 文件锁验证

| 测试 | 预期结果 |
|---|---|
| `python scripts/lock_files.py acquire file.md AI-01` | ACQUIRED |
| `python scripts/lock_files.py check file.md` | LOCKED by AI-01 |
| `python scripts/lock_files.py acquire file.md AI-02` | DENIED |
| `python scripts/lock_files.py release file.md AI-01` | RELEASED |
| `python scripts/lock_files.py check file.md` | FREE |

### 8.6 Trae IDE 约束验证（v0.9.0 新增）

| 测试 | 预期结果 |
|---|---|
| 在 RunCommand 中执行 `Get-Command git` | 显示 `Function` 类型 |
| 在 RunCommand 中执行 `Get-Command Remove-Item` | 显示 `Function` 类型（覆盖内置 cmdlet） |
| 新 AI session 读 .trae/rules/project_rules.md | 看到 RULE-GIT-SAFE |
| 检查 $PROFILE 是否含 wrapper marker | `# >>> git-safety-wrapper >>>` 存在 |
| 检查 $PROFILE 是否含 destructive guard marker | `# >>> powershell-destructive-guard >>>` 存在 |

## 9. 不做什么

| 不做 | 理由 |
|---|---|
| 不编译 Go/Rust 二进制 wrapper | 过度工程——PowerShell 函数足够，无需编译（v0.9.0 确认 PowerShell 覆盖 Remove-Item 等 cmdlet 可行） |
| 不删除 .git/config 中的 alias 配置 | 无害（不生效≠有害），保留意图记录 |
| 不用 git hooks 拦截 clean | git 没有 pre-clean hook |
| 不引入 Claude Code PreToolUse hooks | Trae IDE 不支持 PreToolUse hooks（§7.9.1 确认） |
| 不做定期 auto-commit | 可能 commit 垃圾文件，需设计排除规则，远期考虑 |
| 不删除 git_guard.py | 直接调用时有效，作为 wrapper 的补充层保留 |
| 不强制所有 AI 用 session_worktree | P1 优先级，先靠 wrapper+规则防护，worktree 后续激活 |
| 不为 CRITICAL_BLOCKS 命令提供逃生通道 | format/vssadmin delete/diskpart 等系统级破坏命令永远阻断——AI 开发项目无合法需求 |
| 不覆盖 `robocopy` 函数（v0.9.0） | robocopy 是合法构建工具，`/mir` 滥用场景低频——远期评估后决定 |
| 不实现密钥模式检测（v0.9.0） | SafeRun Guard 的 AWS keys/private keys 写入前检测——pre-commit 已有 `detect-private-key-local` hook 覆盖 commit 时检测 |
| 不适配其他 AI 工具（Claude Code/Cursor/Codex） | 项目 100% Trae IDE 开发（§7.9.1 确认），无其他 AI 工具配置目录 |
| 不引入沙箱/容器隔离 | Windows 无 macOS Seatbelt 等效物；容器方案（Docker/WSL）对量化交易开发过重 |
| 不施工 safe-rm 三层分类（v1.1.0） | 回收站空间效率更优但实现复杂度高（需调用 git status --porcelain 判断每个文件 Git 状态）——v1.0.0 两层方案已足够安全，三层分类作为 v2.0.0 远期改进 |
| 不重复实现 d6_security 已有检测（v1.1.0） | d6_security 目录已有 detect_git_dangerous.py/detect_shell_dangerous.py/detect_permanent_file_deletion.py 等 16 个静态检测脚本——wrapper 只做运行时拦截，静态检测复用 d6_security |

## 10. 开放问题

| 问题 | 决策状态 |
|---|---|
| ~~PowerShell wrapper 的 git 真实路径如何自动检测~~ | ✅ 已解决：注册表 > 硬编码路径 > fallback（§7.1 已实现） |
| ~~wrapper 是否影响 git 子进程调用~~ | ✅ 已解决：用 `$_realGit`（完整路径）调用真实 git.exe，不触发函数循环 |
| ~~non-interactive 脚本中的 git 调用是否受影响~~ | ✅ 已评估：§7.1 "对现有脚本的影响评估"——session_worktree_abort 和 pre-commit stash 需逃生通道 |
| ~~PowerShell 原生破坏性命令是否需拦截~~ | ✅ v0.9.0 已解决：§4.L gap 分析 + §7.1.2 Part B 实现 Remove-Item/rd/del/rm/format/vssadmin/diskpart 拦截 |
| ~~复合命令拆分是否需要~~ | ✅ v0.9.0 已解决：§7.1.3 Part C 分析——PowerShell 5.1 的 `;`/`|` 天然拆分，函数覆盖自动处理子命令 |
| ~~审计日志是否需要~~ | ✅ v0.9.0 已解决：§7.10 实现 `_ZephyrAuditLog` JSONL 日志 |
| wrapper 对 `git rebase`/`git merge` 等内部调用 git 的场景是否安全 | 待测试：git rebase 内部可能调用 `git checkout`，但用的是子进程 `git.exe`（不经过 PowerShell 函数），应该安全——需实测确认 |
| `Remove-Item` 函数覆盖是否影响 `test_concurrent_safety.ps1` | 待测试：该脚本 Phase 1 用 `Remove-Item $_.FullName -Force` 清理 .tmp 文件——不带 `-Recurse` 应放行，需实测 |
| `backup.ps1` 的 `Remove-Item -Recurse -Force` 清理旧备份是否被阻断 | 待确认：若目标不在 `$env:TEMP` 会被阻断——需调整脚本使用 `& $_realRemoveItem` 逃生通道 |
| `Invoke-Expression` 绕过风险如何处理 | 待施工：`iex`/`Invoke-Expression` 已列入 CRITICAL_BLOCKS，但函数覆盖可能不够——`iex` 是别名需单独处理 |
| RULE-WORKTREE 的 GATE-WORKTREE-REQUIRED 阈值是否调低 | 当前 5 次，可考虑调到 3 次，但需评估对合法 commit 流程的影响 |
| 是否需要定期 push 到远程作为最终备份 | 当前 origin/dev 已有 783 commits ahead，但从未 push，需评估 |
| pre-commit 框架的 stash 操作如何适配 wrapper | pre-commit 框架在 commit 前会 `git stash` unstaged 文件，被 wrapper 阻断后 commit 流程会失败——需在 pre-commit 配置中用逃生通道或设置环境变量绕过 |
| setup_git_guard_aliases.py 的 DANGEROUS_SUBCOMMANDS 是否补 clean | v0.9.0 发现不一致：git_guard.py 有 7 个含 clean，setup 脚本只有 6 个缺 clean——需补齐 |
| `robocopy /mir` 是否需函数覆盖 | 远期评估：robocopy 是合法工具，`/mir` 滥用低频；若需拦截，参考 `Remove-Item` 覆盖模式 |

## 11. 多 AI 协调层施工方案（Git Worktree + File Lock(TTL) + Task Board 三件套）

> **本节新增于 v0.8.0**，由 2026-08-11 第一性原理调研发现 #ARCH-AICOLLAB-001 议题触发。
> **方案设计供另一 AI 直接施工**，无需重新调研。
> 关联议题：[#ARCH-AICOLLAB-001](architecture_issue_registry.yaml) Git Worktree + File Lock(TTL) + Task Board 三件套（26 路协调层）

### 11.1 背景与目标

#### 11.1.1 痛点
- 项目当前 26 路 AI 在 Trae 上并发施工，但共用同一 working directory（`d:\ZephyrAlpha`）
- 现有 `scripts/lock_files.py`（611 行 v2.0.0）已实现文件锁，但 `registry.json` 为空——AI 未真正用上
- 多 AI 共用主工作区 → 必然出现 silent data loss（A 写 formatToken、B 覆盖为 parseHeaders，无冲突标记）
- 65 号 §7.6 已简短提及"session_worktree 强制"，但未给出完整三件套方案

#### 11.1.2 目标
- **Git Worktree**：每路 AI 独立 checkout 目录 + 独立分支，物理隔离避免 last-write-wins
- **File Lock(TTL)**：激活现有 `lock_files.py`，加 TTL 60min 自动过期，防崩溃 agent 永久阻塞他人
- **Task Board**：基于 SQLite 的 claim/complete/block 状态机，让 AI 间协调任务认领

#### 11.1.3 第一性原理依据
- P3 状态确定性：多 AI 共用主工作区违反状态确定性原则——任一 AI 的破坏性操作（如 2026-08-11 `git clean -fd`）会波及全部 AI 的工作成果
- P1 资金安全：多 AI 并行修改关键模块（如风控/执行代码）若无声冲突，bug 直入主干

### 11.2 业界事实标准

#### 11.2.1 主流工具对标（2026）
- **Conductor / Superset / Emdash / Claude Code Agent Teams**：均采用 git worktree 作为隔离原语
- **agent-sync 0.4.0（PyPI claude-agent-sync, 2026-06）**：file lock with TTL（60 min 自动过期）+ task board（claim/complete/block）+ presence（heartbeat 自动衰减）+ messaging，基于共享 SQLite，无服务器
- **agent-coord v2matosevic（2026-07）**：同类工具，TTL + heartbeat + claim/release
- **Claude Code `--worktree <name>` + `isolation: worktree` frontmatter**：原生支持
- **Anthropic 报告**：multi-agent 相比单 agent 任务完成率 +90%
- **Cognition 数据**：单 agent 60% 时间在搜索（context 污染）

#### 11.2.2 决策依据
用户裁定（2026-08-11）：**全部加入**三件套——Git Worktree + File Lock(TTL) + Task Board。理由：①Trae 上就是多 AI 并发施工 ②另一 AI 正施工 ③未来真多 AI 并行可直接用。

### 11.3 三件套设计

#### 11.3.1 Git Worktree（每 AI 独立 checkout+分支）

**目录结构**：
```
d:\ZephyrAlpha\                          # 主工作区（main branch，只读给 AI 看）
└── .worktrees\                          # worktree 根目录（.gitignore）
    ├── AI-01\                           # AI-01 的独立 checkout
    │   └── (完整项目副本，branch=ai/AI-01/<task-id>)
    ├── AI-02\
    ├── ...
    └── AI-26\
```

**CLI 接口**（扩展 `scripts/lock_files.py` 同级目录的新脚本 `scripts/session_worktree.py`）：

```bash
# 创建/切换 worktree
python scripts/session_worktree.py create AI-01 task-factor-registry
# → 创建 d:\ZephyrAlpha\.worktrees\AI-01\ + branch ai/AI-01/task-factor-registry

# 在 worktree 中执行命令（透明 cd）
python scripts/session_worktree.py exec AI-01 -- python -m pytest tests/

# 合并 worktree 回主分支（用户确认后）
python scripts/session_worktree.py merge AI-01 --to main --squash

# 清理废弃 worktree（与 #ARCH-WORKTREE-001 联动）
python scripts/session_worktree.py abort AI-01

# 列出所有 worktree
python scripts/session_worktree.py list
```

**实现要点**：
- 使用 `git worktree add` 原生命令，包装在 Python 脚本中
- worktree 目录在 `.gitignore` 中排除（防 commit 进 git）
- 每个 worktree 创建独立分支 `ai/<session-id>/<task-id>`，避免分支冲突
- merge 阶段必须用户显式确认（不自动 merge），防 AI 越权
- 与 #ARCH-WORKTREE-001（stale worktree 堆积治本）联动：7 天未活动的 worktree 自动告警

**配置 frontmatter**（在 `AGENTS.md` 中声明）：
```yaml
RULE-WORKTREE:
  enforcement: required
  worktree_root: d:\ZephyrAlpha\.worktrees\
  branch_prefix: ai/
  auto_cleanup_days: 7  # 7 天未活动告警
  merge_requires_user_confirm: true
```

#### 11.3.2 File Lock(TTL) 激活 lock_files.py

**现有设施**：`scripts/lock_files.py` v2.0.0 已实现 acquire/release/check 三命令，但 `registry.json` 为空——AI 未主动调用。

**扩展点 1：TTL 60min 自动过期**
- 现有 `acquire` 不带 TTL，崩溃 AI 永久阻塞他人
- 扩展 `acquire` 命令支持 `--ttl 60`（默认 60min），到期自动释放
- `registry.json` 结构扩展：
  ```json
  {
    "file_path.md": {
      "session_id": "AI-01",
      "acquired_at": "2026-08-11T10:30:00Z",
      "ttl_minutes": 60,
      "expires_at": "2026-08-11T11:30:00Z",
      "task_id": "task-factor-registry"
    }
  }
  ```

**扩展点 2：heartbeat 续期**
- 长任务支持 `python scripts/lock_files.py heartbeat <file> <session_id>` 续期 30min
- 5 分钟无 heartbeat 自动告警（warning 不释放，但提示用户检查）

**扩展点 3：AGENTS.md RULE-LOCK 强制**
```yaml
RULE-LOCK:
  enforcement: required
  default_ttl: 60  # 分钟
  heartbeat_interval: 5  # 分钟
  expire_silently: false  # 到期释放前 warning
  bypass_for_read_only: true  # 只读不需加锁
```

**CLI 接口扩展**（兼容现有）：
```bash
# 现有
python scripts/lock_files.py acquire <file> <session_id>
python scripts/lock_files.py release <file> <session_id>
python scripts/lock_files.py check <file>

# 新增
python scripts/lock_files.py acquire <file> <session_id> --ttl 60 --task <task-id>
python scripts/lock_files.py heartbeat <file> <session_id>  # 续期 30min
python scripts/lock_files.py list --session AI-01  # 列出 session 持有的锁
python scripts/lock_files.py cleanup  # 清理过期锁（post-commit hook 调用）
```

**post-commit hook 集成**：
- 新增 `scripts/governance/lock_cleanup_reconciler.py`（post-commit priority=200）
- 每次提交后扫描 registry.json，释放过期锁
- 与现有 reconciler 框架对齐（参考 `metric_count_drift_reconciler` 先例）

#### 11.3.3 Task Board（SQLite-based claim/complete/block 状态机）

**数据模型**（SQLite `d:\ZephyrAlpha\.runtime\task_board.db`）：

```sql
CREATE TABLE tasks (
    task_id TEXT PRIMARY KEY,           -- task-factor-registry
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL,                -- pending/claimed/in_progress/blocked/completed/abandoned
    claimed_by TEXT,                     -- AI-01
    claimed_at TIMESTAMP,
    due_at TIMESTAMP,
    blocked_reason TEXT,
    blocked_by TEXT,
    created_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    metadata_json TEXT                   -- 任意附加元数据
);

CREATE TABLE task_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    event_type TEXT NOT NULL,            -- created/claimed/released/blocked/completed/commented
    actor TEXT NOT NULL,                 -- AI-01 / user
    timestamp TIMESTAMP NOT NULL,
    payload_json TEXT,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id)
);

CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_claimed_by ON tasks(claimed_by);
CREATE INDEX idx_events_task_id ON task_events(task_id);
```

**状态机**：
```
pending → claimed → in_progress → completed
                ↑              ↓
                └─ blocked ────┘
                    ↓
                abandoned
```

**CLI 接口**（新建 `scripts/task_board.py`）：

```bash
# 用户/AI 创建任务
python scripts/task_board.py create --title "落地 factor_registry schema" \
    --description "按 #ARCH-REG-001 落地" --priority P1

# AI 认领任务
python scripts/task_board.py claim <task_id> --session AI-01
# → status: pending → claimed，claimed_by=AI-01

# AI 开始执行
python scripts/task_board.py start <task_id>
# → status: claimed → in_progress

# AI 标记阻塞（等待用户决策）
python scripts/task_board.py block <task_id> --reason "等用户确认 schema 字段"
# → status: in_progress → blocked

# AI 完成
python scripts/task_board.py complete <task_id> --result "已落地，commit abc123"
# → status: in_progress → completed

# AI 放弃
python scripts/task_board.py abandon <task_id> --reason "依赖未就绪"
# → status: * → abandoned

# 查询
python scripts/task_board.py list --status pending
python scripts/task_board.py list --session AI-01
python scripts/task_board.py show <task_id>  # 含事件历史
```

**与 #ARCH 议题的联动**：
- 每个 #ARCH 议题对应一个 task（如 #ARCH-REG-001 → task-arch-reg-001）
- AI 认领 #ARCH 议题前必须先在 task_board 登记认领
- 任务完成时自动更新 architecture_issue_registry.yaml 的 `last_updated` 字段

**与 26 路 AI 审查的联动**：
- `AI_review_instructions.md` §0 通用规则新增："AI 启动前 MUST 调用 `task_board.py claim` 认领对应文档"
- 防止两个 AI 同时审查同一文档（如 AI-06 与 AI-08 都涉及 30 号）

### 11.4 施工步骤（另一 AI 直接照做）

#### 步骤 1：创建 worktree 基础设施（约 2 天）
1. 新建 `scripts/session_worktree.py`（参考 §11.3.1 接口）
2. `.gitignore` 添加 `.worktrees/`
3. AGENTS.md 新增 `RULE-WORKTREE` 节
4. 单元测试：`tests/scripts/test_session_worktree.py`（≥10 用例）

#### 步骤 2：扩展 lock_files.py 支持 TTL（约 2 天）
1. 扩展 `scripts/lock_files.py` `acquire` 命令支持 `--ttl`/`--task` 参数
2. 新增 `heartbeat` / `list` / `cleanup` 命令
3. 扩展 `registry.json` schema（含 ttl/expires_at/task_id）
4. 新建 `scripts/governance/lock_cleanup_reconciler.py`（post-commit priority=200）
5. AGENTS.md 新增 `RULE-LOCK` 节
6. 单元测试：扩展 `tests/scripts/test_lock_files.py`（≥15 用例含 TTL 场景）

#### 步骤 3：创建 Task Board（约 3 天）
1. 新建 `scripts/task_board.py`（参考 §11.3.3 接口）
2. SQLite schema 初始化脚本 `scripts/init_task_board.py`
3. 与 architecture_issue_registry.yaml 联动：新增 `scripts/sync_arch_to_task_board.py`
4. AGENTS.md 新增 `RULE-TASKBOARD` 节
5. 单元测试：`tests/scripts/test_task_board.py`（≥20 用例含状态机所有转换）

#### 步骤 4：集成与文档（约 1 天）
1. 更新 `AI_review_instructions.md` §0 通用规则新增 task_board 认领要求
2. 更新 `00_index_trading_decision.md` §7 多 AI 分工指南引用 task_board
3. 更新 `61_lifecycle_multi_ai.md` §3.6 交接点纪律引用 task_board
4. 跑 `python scripts/governance/d5_architecture/generators/generate_battle_map_diagram.py` 让 #ARCH-AICOLLAB-001 在作战地图显化

### 11.5 验证

| 测试 | 预期结果 |
|---|---|
| `python scripts/session_worktree.py create AI-01 task-001` | 创建 `.worktrees/AI-01/` + 分支 `ai/AI-01/task-001` |
| `python scripts/session_worktree.py list` | 显示 AI-01 worktree + 分支 + 最后活动时间 |
| `python scripts/lock_files.py acquire doc.md AI-01 --ttl 60` | ACQUIRED，registry.json 含 expires_at |
| `python scripts/lock_files.py check doc.md` | LOCKED by AI-01, expires in 59min |
| 等待 61 分钟后 `python scripts/lock_files.py check doc.md` | FREE（TTL 已过期） |
| `python scripts/lock_files.py cleanup` | 清理过期锁，输出 "Released 1 expired lock" |
| `python scripts/task_board.py create --title "test"` | task_id 返回，status=pending |
| `python scripts/task_board.py claim <task_id> --session AI-01` | status=claimed，claimed_by=AI-01 |
| `python scripts/task_board.py start <task_id>` | status=in_progress |
| `python scripts/task_board.py complete <task_id>` | status=completed，事件历史含 5 条 |
| AI-02 尝试 `task_board.py claim <已认领 task>` | DENIED: "task already claimed by AI-01" |
| 7 天后 `session_worktree.py list` | 显示 AI-01 worktree 标记 stale |

### 11.6 与现有设施的集成

- **#ARCH-WORKTREE-001（stale worktree 堆积治本）**：本方案 §11.3.1 的 7 天自动告警是该议题的延续
- **#ARCH-GIT-CLEAN-GUARD-FIX**：worktree 物理隔离 = 即使 AI 在自己 worktree 跑 `git clean -fd`，主工作区不受影响
- **现有 `git_commit_gateway.py`**：扩展为检查 task_board 状态（commit 前需有对应 in_progress task）
- **现有 `session_worktree.py` 占位**：项目记忆显示 `src/zephyr/gov_enforcement/rule_bridge/session_worktree.py` 已登记但未激活，本方案激活并扩展
- **现有 `concurrency_guard.py`**：`src/zephyr/infrastructure/runtime/concurrency_guard.py` 可作为 Task Board 的运行时后端

### 11.7 不做什么（过度工程防线）

| 不做 | 理由 |
|---|---|
| 不引入 Redis-based 分布式锁 | 个人单机项目，SQLite 足够；分布式是过度工程 |
| 不实现 presence 自动 heartbeat | 简化版用 CLI heartbeat 即可，自动 presence 是过度工程 |
| 不实现 messaging 系统 | AI 间通过 design_memo + 文件交接已够；messaging 是过度工程 |
| 不做 web UI | CLI 足够，web UI 是过度工程 |
| 不强制每路 AI 必须用 worktree | 先 P1 激活 file_lock+task_board；worktree P2 渐进推进 |
| 不引入 OAuth/RBAC | 单人项目，所有人都是 owner；权限模型是过度工程 |

### 11.8 开放问题

| 问题 | 决策状态 |
|---|---|
| worktree 目录位置（`.worktrees/` vs `d:\zephyr_worktrees\`） | 建议 `.worktrees/`（项目内，便于 .gitignore） |
| TTL 默认值（30/60/120 min） | 建议 60min（业界 agent-sync 默认） |
| Task Board 数据库位置 | 建议 `d:\ZephyrAlpha\.runtime\task_board.db`（与现有 runtime 设施对齐） |
| 是否自动从 architecture_issue_registry 同步 task | 建议半自动：用户/AI 手动 create，但 sync 脚本检测 orphan task |
| Trae IDE 是否支持自动触发 worktree | 待测：Trae 无 PreToolUse hook，需 AI 主动调用 CLI |

## 12. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-11 | 0.1.0 | 初稿 | 2026-08-11 灾难事件后，调研+裁定+施工方案，涵盖所有 git 配套设施 |
| 2026-08-11 | 0.2.0 | 第1轮审查修复：wrapper 路径自动检测（注册表>硬编码>fallback）；阻断规则细化（restore --staged 放行/stash drop 阻断/checkout -- 精确匹配）；对现有脚本影响评估（session_worktree_abort+pre-commit stash 需逃生通道）；3个开放问题已解决 | 技术可行性审查：循环调用风险/阻断条件精确性/现有脚本兼容性 |
| 2026-08-11 | 0.3.0 | 第2轮审查修复：新增 git rm 阻断（不带 --cached 删工作区文件）；新增 git checkout . 阻断（丢弃所有未暂存修改）；过度工程审查通过；开放问题完整性确认 | 过度工程+遗漏命令审查 |
| 2026-08-11 | 0.4.0 | 第3轮审查修复：验证清单补充 git rm/checkout . 测试用例；AGENTS.md RULE-GIT-SAFE 禁令列表补充 git rm；交叉引用/规范符合性/引用纪律确认通过 | 交叉引用+规范符合性+文档质量审查 |
| 2026-08-11 | 0.5.0 | 第4轮审查修复（全网搜索2026-08最新方案）：调研报告补充5个新开源项目（dcg 5.6k星/ai-agent-secure/SafeRun/git-safety-guard/OpenClaw审批系统）；阻断列表补充 git branch -D/git push --force/git reset --merge（参考 dcg）；放行列表修正 git clean -n dry-run（参考 git-safety-guard）；放行 git push --force-with-lease/git checkout -b/git checkout --orphan；验证清单补充8个测试用例；AGENTS.md 禁令列表同步更新 | 全网搜索2026年8月最新研究实践+更好方案对比+遗漏命令补充 |
| 2026-08-11 | 0.6.0 | 第5轮审查修复（项目设施全量盘点）：§4.1 设施清单从12项扩展到37项（8层分类：Git命令拦截/文件锁/Commit门禁80+gates/Worktree隔离/受保护路径/规则文档/检测审计/Trae IDE约束）；补充pre-commit 9个安全hook详表；补充commit_gates 10个安全gate详表；新增§H Trae IDE约束节（3条关键约束）；§7.2 补充.trae/rules/规则写入要求 | 项目已有基础设施全量盘点+遗漏设施补充+Trae IDE开发约束强调 |
| 2026-08-11 | 0.7.0 | 第6轮审查修复（深度设施盘点+Trae IDE约束）：§H Trae IDE约束从3条扩展到7条（补充.traeignore盲区/无其他AI工具确认/$PROFILE已存在/-NoProfile边缘风险）；新增§I .git/hooks/ 7个实际安装hook详表；新增§J .github/workflows/ 5个CI工作流详表；设施总数从37项扩展到41项 | 深度搜索.git/hooks+CI工作流+Trae IDE配置+PowerShell profile状态确认 |
| 2026-08-11 | 0.8.0 | 第7轮审查扩展（多AI协调层三件套方案）：新增§11（原§12）完整三件套方案（Git Worktree + File Lock(TTL) + Task Board），由 #ARCH-AICOLLAB-001 议题触发；用户裁定全部加入；方案设计供另一 AI 直接施工（CLI 接口/SQLite schema/状态机/施工步骤/验证清单/过度工程防线全列出） | 第一性原理调研发现的 #ARCH-AICOLLAB-001 议题登记后，方案需写入本备忘供另一 AI 施工 |
| 2026-08-11 | 0.9.0 | 第8轮审查修复（PowerShell原生破坏性命令gap+Trae IDE强调+审计日志+结构修复）：①§3.5 新增2026年8月最新研究（SafeRun Guard/Claude Code v2.1.183/opencode-fusion PR#12/Cursor事故/cmd_command_execution_ai_agent）；②§4.1 补登12项遗漏设施（#42-53：setup_git_guard_aliases.py/test_concurrent_safety.ps1/backup脚本群/rollback.py/deadman_switch.ps1/file_lock.py等）；③§4.K 新增灾难恢复设施层；④§4.L 新增PowerShell原生破坏性命令gap分析（ARCH-POWERSHELL-DESTRUCTIVE-GUARD（待登记））+20+命令拦截清单+双重安全检查算法；⑤§7.1 重写为3 Part结构（git拦截+PowerShell原生拦截+复合命令拆分）；⑥§7.9 新增Trae IDE开发约束专节（用户强调围绕Trae编译器开发）；⑦§7.10 新增审计日志设施（JSONL格式）；⑧§8 验证补充PowerShell原生命令+审计日志+Trae IDE约束测试用例（共18个新测试）；⑨§9/§10 更新不做什么（+5条）和开放问题（+6条解决/新增）；⑩结构修复：§12重编号为§11，修订记录移至§12（末尾）；⑪frontmatter 新增 ARCH-POWERSHELL-DESTRUCTIVE-GUARD（待登记） + #ARCH-AICOLLAB-001 议题引用 | 全网搜索2026年8月最新研究+PowerShell原生命令gap发现+项目设施全量盘点补遗+Trae IDE开发平台强调+审计日志+结构修复 |
| 2026-08-11 | 1.0.0 | 第9轮审查修复（trash redirect算法+第二轮全网搜索+3项遗漏设施）：①§3.6 新增第二轮搜索（prevent-llm-delete trash redirect算法/Claude Code #64310真实事故/dcg v0.9.4/agent-coord/agentlocks/Vibe Kanban/AI Agent Guardrails gist）；②§3.6.2 发现BETTER算法：trash redirect优于block（AI不卡住+文件可恢复）；③§4.1 补登3项遗漏设施（#54 git_commit.py唯一合法commit入口/#55 clone_guard_audit.py/#56 validate_worktree_required.py GATE-WORKTREE-REQUIRED实现）；④§7.11 新增Trash Redirect施工项（Recycle Bin API+REDIRECTED审计action+回收站清理策略）；⑤§7.12 新增setup_git_guard_aliases.py修复（补齐clean到DANGEROUS_SUBCOMMANDS）；⑥§6.2 防御层从8层扩展到9层（新增L9 Trash Redirect）；⑦设施总数从53扩展到56项 | 第二轮全网搜索2026年8月最新研究+发现trash redirect更好算法+遗漏设施深度盘点+代码修复施工项 |
| 2026-08-11 | 1.1.0 | 第10轮审查修复（d6_security深度盘点+safe-rm三层算法+config安全配置）：①§4.M 新增d6_security静态检测脚本群（#57-65：detect_git_dangerous.py检测代码中危险git命令/detect_shell_dangerous.py检测危险shell命令/detect_permanent_file_deletion.py检测ttl:permanent文件删除等9项）；②§4.N 新增安全相关配置文件（#66-71：immutable_core.yaml/dr_policy.yaml/worktree_state_machine.yaml/external_watchdog.yaml/sandbox_policy.yaml/secret_registry.yaml）；③§3.7 新增safe-rm三层分类算法分析（block→auto_allow→auto_trash，结合git status情境感知，回收站空间效率优于v1.0.0两层方案，裁定为v2.0.0远期改进）；④设施总数从56扩展到71项 | d6_security目录16脚本深度盘点+config安全配置补登+safe-rm三层算法发现+第三轮全网搜索 |
| 2026-08-11 | 1.2.0 | 第11轮审查修复（ProxyCommand最佳实践+隔离区算法+RULE-THREE+commit_gates更正）：①§3.8.1 发现Remove-Item手写param()块是错误做法——正确方法用ProxyCommand::Create()生成代理脚手架（保留DynamicParam/-WhatIf/管道输入）；②§7.1.4 新增Part D ProxyCommand修正方案（模块限定名调用+steppable pipeline透传+保留DynamicParam）；③§3.8.2 新增隔离区算法（agent-file-safety-kit，manifest.json+restore.ps1，批量清理场景可选增强）；④§3.8.3 发现RULE-THREE三步审判（删除文件前验证必要性/安全性/可逆性）已在.trae/rules/中存在但未登记——规则层+静态检测层+运行时拦截层三层叠加=文件删除安全闭环；⑤§4.1 commit_gates文件数从"80+"更正为"100个"（实际盘点）；⑥§4.1.F .trae/rules/规则列表补充RULE-THREE | 第四轮全网搜索+ProxyCommand最佳实践发现+commit_gates全量盘点+RULE-THREE遗漏发现 |
| 2026-08-11 | 1.3.0 | 第12轮审查修复（d6_security未接入pre-commit+fail-open策略+错误分类防重试+OpenClaw四级风险）：①§3.9.4 CRITICAL发现：d6_security的detect_git_dangerous.py/detect_shell_dangerous.py/detect_permanent_file_deletion.py等14个脚本存在但未在.pre-commit-config.yaml中注册——静态检测层实际缺失；②§7.13 新增施工项：将3个关键d6_security脚本接入pre-commit config，激活文件删除安全三层闭环；③§3.9.2 裁定wrapper采用fail-open策略（wrapper出错时放行命令并记录FAIL_OPEN审计日志，参考git-safety-guard行业共识），CRITICAL命令fail-closed；④§7.14 新增施工项：wrapper fail-open策略实现模板（try/catch+透传+审计日志）；⑤§3.9.3 发现PowerShell #注释陷阱（opencode-swarm #1875：-Command模式下#吞掉后续代码）；⑥§7.15 新增施工项：错误分类与AI重试防护（STOP:不要重试+ALTERNATIVE:替代方案格式规范，防AI无限重试8000-15000 tokens/循环）；⑦§3.9.1 新增OpenClaw四级风险动态评估系统分析（禁止/高危/中危/低危，裁定为v2.0.0远期改进） | 第五轮全网搜索+d6_security pre-commit接入gap发现+fail-open策略裁定+opencode-swarm无限重试教训+OpenClaw四级风险算法发现 |
| 2026-08-11 | 1.4.0 | 第13轮审查修复（Circuit Breaker三态状态机+第六轮全网搜索）：①§7.16 新增施工项：Circuit Breaker模式——CLOSED→OPEN→HALF-OPEN三态状态机，5次blocked/120秒阈值→熔断60秒，防AI反复尝试危险命令变体浪费token（参考channel.tel/valuestreamai/pockit.tools/truefoundry 2026年发表）；②PowerShell实现核心（_ZephyrCircuitCheck/_ZephyrCircuitRecordBlock/_ZephyrCircuitRecordSuccess三函数+session级别状态）；③CIRCUIT-OPEN消息格式规范（STOP:不要重试任何命令+等待60秒恢复）；④确认.traeignore存在；⑤确认AGENTS.md有12+个RULE-*规则（RULE-ENV→RULE-CLONEGUARD），本方案RULE-GIT-SAFE将作为第13个规则插入；⑥确认"TRAE 不可 hook shell 启动"在AGENTS.md L19明确声明 | 第六轮全网搜索+Circuit Breaker算法发现+AGENTS.md RULE系统全量确认+.traeignore存在性验证 |
