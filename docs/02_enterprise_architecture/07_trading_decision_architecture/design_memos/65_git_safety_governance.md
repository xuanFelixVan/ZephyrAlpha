---
ttl: permanent
doc_type: architecture_view
title: Git 安全治理体系——alias 失效修复与多层防护施工总案
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.1.0"
date: 2026-08-11
topic: git_safety_governance
scope: 07_trading_decision_architecture
related_issues:
  - "#ARCH-GIT-CLEAN-GUARD（git clean 误删防护）"
  - "#ARCH-GIT-CLEAN-GUARD-FIX（alias 失效修复+clean 自伤检测）"
  - "#ARCH-GIT-SELF-HARM-GUARD（reset/checkout 自伤防护）"
  - "#ARCH-GIT-CALL-BUDGET（git 调用预算优化）"
depends_on:
  - 01_design_memo_management_spec
  - 60_cross_cutting_cleanup
  - 61_lifecycle_multi_ai
related_modules:
  - scripts/git_guard.py
  - scripts/lock_files.py
  - src/zephyr/infrastructure/runtime/concurrency_guard.py
  - src/zephyr/gov_enforcement/rule_bridge/session_worktree.py
  - src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py
---

# Git 安全治理体系——alias 失效修复与多层防护施工总案

> 本备忘是 2026-08-11 灾难事件（AI 执行 `git clean -fd` 物理删除多个 untracked 文件）后的**根因分析 + 调研报告 + 裁定 + 治本施工方案**。
> 性质：**决策备忘 + 施工计划**混合体，按"背景→调研→现状→分析→裁定→施工→验证→不做→开放问题"组织。
> 管理规范见 [01_design_memo_management_spec](01_design_memo_management_spec.md)。
> 关联：[60_cross_cutting_cleanup](60_cross_cutting_cleanup.md)（跨切治理）｜[61_lifecycle_multi_ai](61_lifecycle_multi_ai.md)（多 AI 生命周期）

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G65 Git 安全治理体系（跨切治理层） |
| 创建 | 2026-08-11 |
| 优先级 | P0（灾难已发生，必须立即治本） |
| 状态 | draft（方案待审查定稿后施工） |
| 上游 | [01_design_memo_management_spec](01_design_memo_management_spec.md)｜[60_cross_cutting_cleanup](60_cross_cutting_cleanup.md) |
| 下游 | 所有 AI session（安全规则约束）｜scripts/git_guard.py（代码修改）｜AGENTS.md（永久规则） |

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

## 4. 现状分析：项目现有 Git 配套设施全貌

### 4.1 设施清单

| # | 设施 | 文件 | 状态 | 问题 |
|---|---|---|---|---|
| 1 | git_guard.py alias 拦截 | scripts/git_guard.py | ⚠️ **全部失效** | alias 无法覆盖内置命令（7 个 DANGEROUS_SUBCOMMANDS 全失效） |
| 2 | git_guard.py 直接调用 | scripts/git_guard.py | ✅ 代码层有效 | 但无人主动调用 `python scripts/git_guard.py` |
| 3 | git_guard.py clean 自伤检测 | scripts/git_guard.py L499-565 | ✅ 已修复 | 仅直接调用时有效，alias 调用不生效 |
| 4 | lock_files.py 文件锁 | scripts/lock_files.py（611行 v2.0.0） | ✅ 系统正常 | **无人使用**（registry.json 为空，最后更新 8月3日） |
| 5 | concurrency_guard.py | src/zephyr/infrastructure/runtime/concurrency_guard.py（225行） | ✅ 系统正常 | 只读扫描 .ailocks，锁为空时全部放行 |
| 6 | pre-commit hooks | .pre-commit-config.yaml | ✅ 正常运行 | 只拦 commit（GATE-WORKTREE-REQUIRED 等），**不拦 clean/reset/checkout** |
| 7 | session_worktree | src/zephyr/gov_enforcement/rule_bridge/session_worktree.py | ✅ 系统正常 | AGENTS.md RULE-WORKTREE 要求但 **AI 未遵守**（直接在主工作区改文件） |
| 8 | GitCommitGateway | src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py | ✅ 正常运行 | 7 gates commit 门禁，但不拦 clean |
| 9 | post_checkout_guard.py | scripts/post_checkout_guard.py | ✅ 存在 | checkout 后扫描锁冲突，但 alias 不生效时不会被触发 |
| 10 | AGENTS.md 规则 | AGENTS.md | ⚠️ 有 RULE-WORKTREE 但 **无 git clean 禁令** | 缺少 git 安全铁律 |
| 11 | project_memory | memory/project_memory.md | ✅ 已记录灾难教训 | 需确认所有 AI 会读 |
| 12 | AI_review_instructions §0 规则9/10 | AI_review_instructions.md | ✅ 已加入 | 仅覆盖审查指令中的 AI |

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

### 5.3 约束条件

- **Trae IDE 不支持 hooks**：无法在 AI 工具层拦截
- **Windows + PowerShell 5.1**：shell 函数覆盖可行
- **git 2.48.1**：alias 无法覆盖内置命令（确认）
- **个人项目**：不能引入需要多人协作的治理机制
- **100%AI 开发**：规则必须机器可读、AI 可执行（不能依赖人工自觉）

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

### 6.2 最终裁定：多层组合防御

```
L1: PowerShell git() 函数（PATH 拦截）——所有 git 调用必经，硬阻断危险命令
L2: 保护性 git add——staged 文件 clean 不删
L3: AGENTS.md RULE-GIT-SAFE——永久规则，所有 AI 遵守
L4: git_guard.py 保留——直接调用时有效，作为 L1 的补充
L5: lock_files.py 激活——AI 改文件前先加锁
L6: session_worktree 强制——AI 使用独立 worktree
```

### 6.3 不采用的方案及理由

| 方案 | 不采用理由 |
|---|---|
| Go 编写的 git wrapper（git-sentinel） | 过度工程——个人项目不需要编译 Go 二进制，PowerShell 函数足够 |
| Claude Code PreToolUse hooks | Trae IDE 不支持 hooks |
| git hooks（pre-clean） | git 没有 pre-clean hook（git hook 只覆盖 commit/push/checkout 等，不覆盖 clean） |
| 定期 auto-commit | 可能 commit 垃圾文件，需设计排除规则，复杂度高，远期考虑 |

## 7. 施工方案

### 7.1 施工项 1：PowerShell git wrapper 函数（L1，P0）

**目标**：在 PowerShell 中定义 `git()` 函数，拦截危险 git 命令。

**实现**：在 PowerShell profile（`$PROFILE`）中添加 `git()` 函数：

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

function git {
    $cmd = if ($args.Count -gt 0) { $args[0] } else { '' }
    $fullArgs = $args -join ' '

    $blocked = $false
    $reason = ''

    if ($cmd -eq 'clean' -and ($fullArgs -notmatch '(?:^|\s)-(?:n|-dry-run)(?:\s|$)')) {
        # 阻断 git clean -f/-fd/-fdx（删除 untracked 文件）
        # 放行 git clean -n / --dry-run（只预览不删除，参考 dcg/git-safety-guard）
        $blocked = $true
        $reason = 'git clean 删除 untracked 文件（物理删除不进回收站）'
    } elseif ($cmd -eq 'reset' -and ($fullArgs -match '--hard|--merge')) {
        # 阻断 git reset --hard（丢弃所有未提交修改）
        # 阻断 git reset --merge（可能丢失未提交修改，参考 dcg）
        # 放行 git reset --soft / --mixed（不覆盖工作区）
        $blocked = $true
        $reason = 'git reset --hard/--merge 丢弃未提交修改'
    } elseif ($cmd -eq 'checkout' -and ($fullArgs -match '(?:^|\s)--(?:\s|$)' -or $fullArgs -match 'HEAD\s+--' -or $fullArgs -match '(?:^|\s)\.(?:\s|$)')) {
        # 阻断 git checkout -- file / git checkout HEAD -- file / git checkout .
        # 放行 git checkout <branch> / git checkout -b <branch> / git checkout --orphan（切分支/建分支）
        $blocked = $true
        $reason = 'git checkout 丢弃文件修改'
    } elseif ($cmd -eq 'restore' -and ($fullArgs -match '--worktree' -or ($fullArgs -notmatch '--staged'))) {
        # 阻断 git restore file（丢弃工作区修改）
        # 阻断 git restore --staged --worktree file（同时丢弃暂存+工作区）
        # 放行 git restore --staged file（仅取消暂存，不丢修改）
        $blocked = $true
        $reason = 'git restore 丢弃文件修改'
    } elseif ($cmd -eq 'stash' -and ($args.Count -lt 2 -or $args[1] -notin @('list', 'show'))) {
        # 阻断 git stash push/pop/apply/clear/branch/drop
        # 放行 git stash list / git stash show（只读）
        $blocked = $true
        $reason = 'git stash 移走/删除未提交修改'
    } elseif ($cmd -eq 'rm' -and ($fullArgs -notmatch '--cached')) {
        # 阻断 git rm file（从工作区+暂存区删除文件）
        # 放行 git rm --cached file（仅从暂存区移除，不删工作区文件）
        $blocked = $true
        $reason = 'git rm 从工作区删除文件'
    } elseif ($cmd -eq 'branch' -and ($fullArgs -match '-D|--delete-force')) {
        # 阻断 git branch -D（强制删除分支，不检查合并状态，参考 dcg）
        # 放行 git branch -d（普通删除，检查合并状态）
        $blocked = $true
        $reason = 'git branch -D 强制删除分支（可能丢失未合并代码）'
    } elseif ($cmd -eq 'push' -and ($fullArgs -match '(?:^|\s)-(?:f|-force)(?:\s|$)' -and $fullArgs -notmatch '--force-with-lease')) {
        # 阻断 git push --force / -f（覆盖远程历史，参考 dcg）
        # 放行 git push --force-with-lease（更安全的 force push，参考 git-safety-guard）
        $blocked = $true
        $reason = 'git push --force 覆盖远程历史（可能丢失他人代码）'
    }

    if ($blocked) {
        Write-Host "[GIT-SAFE] BLOCKED: git $fullArgs — $reason" -ForegroundColor Red
        Write-Host "  如需执行（确认安全后），用完整路径：" -ForegroundColor Yellow
        Write-Host "  & '$_realGit' $fullArgs" -ForegroundColor Yellow
        return 1
    }

    # 安全命令透传给真实 git.exe（用完整路径，不触发函数循环）
    & $_realGit @args
}
# <<< git-safety-wrapper <<<
```

**安装方式**：通过 `scripts/install_git_safety_wrapper.ps1` 一键安装（见 §7.7）。
脚本功能：检测 `$PROFILE` → 检测是否已安装（幂等）→ 检测 git 真实路径 → 追加 wrapper 函数 → 支持 `-Uninstall`。

**逃生通道**：如需执行被阻断的命令（如经用户确认的 `git clean -fd`），用完整路径：
```powershell
& $env:ZEPHYR_REAL_GIT_PATH clean -fd
# 或
& 'C:\Program Files\Git\cmd\git.exe' clean -fd
```

**阻断/放行规则明细**：

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

**对现有脚本的影响评估**：
- `git add`/`git commit`/`git diff`/`git status`/`git log`/`git push`/`git pull`/`git merge`/`git rebase`：全部放行（安全命令）
- `session_worktree_merge` 中的 `git checkout`（切分支）：放行（不带 `--`）
- `session_worktree_abort` 中的 `git checkout --`（恢复文件）：**会被阻断**——需要用 `& $_realGit checkout -- <file>` 逃生通道
- `GitCommitGateway` 中的 `git reset --soft`：放行（不带 `--hard`）
- pre-commit hook 中的 `git diff --cached`/`git stash`（stashing unstaged）：**stash 会被阻断**——pre-commit 框架需用 `& $_realGit stash` 逃生通道

**结论**：wrapper 对现有脚本的影响集中在 `session_worktree_abort`（checkout --）和 pre-commit 框架（stash）两个场景，需用逃生通道处理。其他脚本不受影响。

### 7.2 施工项 2：AGENTS.md RULE-GIT-SAFE 永久规则（L3，P0）

**目标**：在 AGENTS.md 中新增 `RULE-GIT-SAFE` 节，作为所有 AI 必须遵守的永久规则。

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

## 8. 验证

### 8.1 PowerShell wrapper 验证

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

### 8.2 AGENTS.md 规则验证

| 测试 | 预期结果 |
|---|---|
| 新 AI 对话读 AGENTS.md | 看到 RULE-GIT-SAFE |
| AI 执行 git clean | 被 PowerShell wrapper 阻断 |
| AI 修改文件后 | 执行 git add（规则 2） |

### 8.3 文件锁验证

| 测试 | 预期结果 |
|---|---|
| `python scripts/lock_files.py acquire file.md AI-01` | ACQUIRED |
| `python scripts/lock_files.py check file.md` | LOCKED by AI-01 |
| `python scripts/lock_files.py acquire file.md AI-02` | DENIED |
| `python scripts/lock_files.py release file.md AI-01` | RELEASED |
| `python scripts/lock_files.py check file.md` | FREE |

## 9. 不做什么

| 不做 | 理由 |
|---|---|
| 不编译 Go 二进制 wrapper | 过度工程——PowerShell 函数足够，无需编译 |
| 不删除 .git/config 中的 alias 配置 | 无害（不生效≠有害），保留意图记录 |
| 不用 git hooks 拦截 clean | git 没有 pre-clean hook |
| 不引入 Claude Code PreToolUse hooks | Trae IDE 不支持 |
| 不做定期 auto-commit | 可能 commit 垃圾文件，需设计排除规则，远期考虑 |
| 不删除 git_guard.py | 直接调用时有效，作为 wrapper 的补充层保留 |
| 不强制所有 AI 用 session_worktree | P1 优先级，先靠 wrapper+规则防护，worktree 后续激活 |

## 10. 开放问题

| 问题 | 决策状态 |
|---|---|
| ~~PowerShell wrapper 的 git 真实路径如何自动检测~~ | ✅ 已解决：注册表 > 硬编码路径 > fallback（§7.1 已实现） |
| ~~wrapper 是否影响 git 子进程调用~~ | ✅ 已解决：用 `$_realGit`（完整路径）调用真实 git.exe，不触发函数循环 |
| ~~non-interactive 脚本中的 git 调用是否受影响~~ | ✅ 已评估：§7.1 "对现有脚本的影响评估"——session_worktree_abort 和 pre-commit stash 需逃生通道 |
| wrapper 对 `git rebase`/`git merge` 等内部调用 git 的场景是否安全 | 待测试：git rebase 内部可能调用 `git checkout`，但用的是子进程 `git.exe`（不经过 PowerShell 函数），应该安全——需实测确认 |
| RULE-WORKTREE 的 GATE-WORKTREE-REQUIRED 阈值是否调低 | 当前 5 次，可考虑调到 3 次，但需评估对合法 commit 流程的影响 |
| 是否需要定期 push 到远程作为最终备份 | 当前 origin/dev 已有 783 commits ahead，但从未 push，需评估 |
| pre-commit 框架的 stash 操作如何适配 wrapper | pre-commit 框架在 commit 前会 `git stash` unstaged 文件，被 wrapper 阻断后 commit 流程会失败——需在 pre-commit 配置中用逃生通道或设置环境变量绕过 |

## 11. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-11 | 0.1.0 | 初稿 | 2026-08-11 灾难事件后，调研+裁定+施工方案，涵盖所有 git 配套设施 |
| 2026-08-11 | 0.2.0 | 第1轮审查修复：wrapper 路径自动检测（注册表>硬编码>fallback）；阻断规则细化（restore --staged 放行/stash drop 阻断/checkout -- 精确匹配）；对现有脚本影响评估（session_worktree_abort+pre-commit stash 需逃生通道）；3个开放问题已解决 | 技术可行性审查：循环调用风险/阻断条件精确性/现有脚本兼容性 |
| 2026-08-11 | 0.3.0 | 第2轮审查修复：新增 git rm 阻断（不带 --cached 删工作区文件）；新增 git checkout . 阻断（丢弃所有未暂存修改）；过度工程审查通过；开放问题完整性确认 | 过度工程+遗漏命令审查 |
| 2026-08-11 | 0.4.0 | 第3轮审查修复：验证清单补充 git rm/checkout . 测试用例；AGENTS.md RULE-GIT-SAFE 禁令列表补充 git rm；交叉引用/规范符合性/引用纪律确认通过 | 交叉引用+规范符合性+文档质量审查 |
| 2026-08-11 | 0.5.0 | 第4轮审查修复（全网搜索2026-08最新方案）：调研报告补充5个新开源项目（dcg 5.6k星/ai-agent-secure/SafeRun/git-safety-guard/OpenClaw审批系统）；阻断列表补充 git branch -D/git push --force/git reset --merge（参考 dcg）；放行列表修正 git clean -n dry-run（参考 git-safety-guard）；放行 git push --force-with-lease/git checkout -b/git checkout --orphan；验证清单补充8个测试用例；AGENTS.md 禁令列表同步更新 | 全网搜索2026年8月最新研究实践+更好方案对比+遗漏命令补充 |
