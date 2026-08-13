---
ttl: permanent
doc_type: architecture_view
title: Git 安全治理体系——alias 失效修复与多层防护施工总案（Trae IDE 专用）
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "2.1.0"
date: 2026-08-12
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

# Git 安全治理体系——alias 失效修复与多层防护施工总案（Trae IDE 专用）

> 本备忘是 2026-08-11 灾难事件（AI 执行 `git clean -fd` 物理删除多个 untracked 文件）后的**根因分析 + 调研报告 + 裁定 + 治本施工方案**。
> **开发平台约束**：本项目 100% 围绕 **Trae IDE（编译器）** 开发——所有 AI session 通过 Trae IDE 的 RunCommand（PowerShell 5.1）执行命令，Trae IDE 不支持 PreToolUse hooks，AI 规则通过 `.trae/rules/` 目录注入。本方案的所有防护层均围绕此约束设计。
> 性质：**决策备忘 + 施工计划**混合体，按"背景→调研→现状→分析→裁定→施工→验证→不做→开放问题"组织。
> 管理规范见 [01_design_memo_management_spec](01_design_memo_management_spec.md)。
> 关联：[60_cross_cutting_cleanup](60_cross_cutting_cleanup.md)（跨切治理）｜[61_lifecycle_multi_ai](61_lifecycle_multi_ai.md)（多 AI 生命周期）
>
> **⚠️ v2.0.0 精简裁定（2026-08-12）**：v1.x 累计膨胀到 36 施工项 / 19 层防御 / 293KB，根因是把"AI 误操作"（合法错误）误判为"AI 恶意攻击"（adversarial）——单人单账户 AI 协作开发中 AI 是协作者不是攻击者。v2.0.0 把 adversarial 防御层（§7.16/§7.19-§7.26/§7.29/§7.33-§7.36）全部标 `deprecated`，§14/§15 删除，§3.6+ 调研过程归档保留但不再作为施工依据。**实际施工范围 = §7.1/§7.2/§7.7/§7.10/§7.13-§7.15/§7.17/§7.18/§7.23/§7.27/§7.32 + §11 三件套**，共 ~12 项 / ~15 天 / 5-6 层防御。详见 §6.2 + §9 + §13。
>
> **⚠️ v2.1.0 第二轮精简（2026-08-12）**：v2.0.0 保留项内部的实现细节仍残留 adversarial 思维。v2.1.0 进一步砍掉：①§7.17.1 自动变量碰撞检测（30+ 变量清单过度）②§7.18 反混淆归一化层 9 策略（防 shell 注入攻击，AI 不会混淆命令）③§7.15 错误分类 STOP/ALTERNATIVE 格式（AI 提示工程层过度）。简化：④§7.23 git 危险命令 20+→4 命令（只保留 AI 易误用的 filter-branch/filter-repo/reflog expire/gc --prune）⑤§7.27 审计日志 Mutex→每 session 独立文件（append-only 风险低）⑥§7.32 init-session.ps1+TRAE_ENV_FILE→$PROFILE 一行 UUID ⑦§11.3.2 去 heartbeat ⑧§11.3.3 去 epoch 防 ABA ⑨§11.3.1 去 7 天告警。**v2.1.0 实际施工范围 = 8 项 / ~11 天**。详见 §6.2 + §9 + §13。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G65 Git 安全治理体系（跨切治理层） |
| 创建 | 2026-08-11 |
| 优先级 | P0（灾难已发生，必须立即治本） |
| 状态 | draft v1.9.0（第18轮审查完成，第十一轮全网搜索诚实评估+AST 升级+施工路线图+灾难恢复+性能评估——v1.8.0 确认到达边际收益递减点） |
| 设施总数 | 71 项（commit_gates 实际 100 个文件）；v1.9.0 新增 1 项 AST 升级（§7.36）+ 施工路线图 36 项分 4 Phase + 灾难恢复 + 性能评估 |
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

> **⚠️ v2.0.0 精简说明**：§3.1-§3.5 为核心调研（git alias 失效根因 + GitHub/AI/量化社区实践 + 2026-08 最新研究），是 §6/§7 裁定的依据。§3.6-§3.14 为 v1.x 累计 9 轮搜索补充过程，**保留作为决策追溯历史归档，不再作为施工依据**——其中发现的 trash redirect 算法（§3.6）、PS 5.1 并发写入算法（§3.12.4）、Trae 多 session 病根（§3.12.1-3.12.3）已提炼到 §7 对应施工项；其余 adversarial 防御算法（RiskChain/CFD/symlink 攻击/AST 升级等）在 v2.0.0 判定为单人 AI 协作场景不适用，详见 §9。

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

### 3.10 第七轮搜索补充（v1.5.0——GuardFall/AgentTrust/Codex $home事故/Zed沙箱/Pillar Trust Handoff/CFD/IETF AAT/grite/CoAgent MTPO）

> 搜索时间：2026-08-11 第三轮，覆盖 arXiv/GitHub/CSA/Pillar Security/Anthropic/Cognition/Microsoft Defender/Adversa AI

#### 3.10.1 GuardFall——证明正则/AST 单层防护都不够（Adversa AI 2026-06-30）

> 来源：[Adversa AI GuardFall](https://adversa.ai/blog/opensource-ai-coding-agent-shell-injection-vulnerability/)，测试 11 个开源 AI agent，**10 个可被 shell 注入绕过**。

**5 大绕过类**（现有 wrapper 全部不防）：

| 绕过类 | 示例 | 现有 wrapper 是否拦截 |
|---|---|---|
| Quote removal（引号移除） | `r''m -rf /` | ❌ 不拦截 |
| `$IFS` expansion | `rm$IFS-rf$IFS/` | ❌ 不拦截 |
| Command substitution（命令替换） | `$(echo rm) -rf /` | ❌ 不拦截 |
| Base64 encoding | `echo "cm0gLXJmIC8=" \| base64 -d \| bash` | ❌ 不拦截 |
| Destructive argv flags | `rm --no-preserve-root -rf /` | ❌ 不拦截 |

**GuardFall 关键结论**：tree-sitter AST 也不够——"Parsing to an AST first helps detect `&&` and `;` separators, but the matcher still runs on each node's raw text, so the same bypass classes apply. **Lexing the shell's grammar is not running the shell's expansion rules. Lexing is not evaluation.**"

**唯一正确架构（Continue）**：**tokenize-then-check**——shell-quote 解析 token 化后检查，检测 `$IFS` 等 expansion token 升级为显式确认，命令替换递归求值。11 个测试 agent 中**仅 Continue 防住**。

**对本方案的影响**：§7.1 的正则模式匹配（`$fullArgs -match`）在对抗性场景下可被绕过。需新增**反混淆归一化层**（见 §7.18）。

#### 3.10.2 AgentTrust——四大算法创新（arXiv:2605.04785 2026-05）

> 来源：[AgentTrust 论文](https://arxiv.org/pdf/2605.04785)，AGPL-3.0 + MCP server，95.0% verdict accuracy，0.93 召回率对抗 shell 混淆 payload

| 创新 | 算法 | 本方案对应 |
|---|---|---|
| **Shell deobfuscation normalizer** | 9 策略：变量展开/hex 转义/八进制转义/alias 解析/命令替换/ANSI-C quoting/相邻引号拼接/Base64 decode 检测/`$IFS` 展开检测 | **缺失**——见 §7.18 新增 |
| **SafeFix** | 不只阻断，建议更安全替代（如 `chmod 777 → chmod 755`、`rm -rf /tmp/* → find /tmp -mtime +7 -delete`） | **缺失**——见 §7.19 新增 |
| **RiskChain** | order-aware session tracker，检测多步攻击链（`read .env → base64 → curl -X POST`，每步单独无辜） | **缺失**——见 §7.20 新增 |
| **Cache-aware LLM-as-Judge** | block-hash delta detection（借鉴 rsync/git），长会话省 token | 远期评估 |

#### 3.10.3 Codex `$home` 真实事故（2026-07-13）——Windows PowerShell 自动变量碰撞

> 来源：[openai/codex Issue #32684](https://github.com/openai/codex/issues/32684)，NTFS USN 日志记录 67,959 个删除路径

**事故链**：
1. AI 在 PowerShell 5.1 中执行 `$home = "something"`（意图赋值局部变量）
2. PowerShell 变量名**大小写不敏感**——`$home` 与只读自动变量 `$HOME` 碰撞
3. 赋值产生**非终止** `VariableNotWritable` 错误，但**执行继续**
4. `$home` 仍解析为真实 `$HOME`（即 `%USERPROFILE%`）
5. AI 后续执行 `Remove-Item $home -Recurse -Force`
6. **递归删除整个用户目录**——文档/图片/配置/.ssh/.aws 全部丢失
7. 30 秒工具超时才在 `.codex` 内停止遍历
8. 恢复需要 Windows File Recovery + DMDE + VSS 重建

**对本方案的影响**：§7.1.2 Part B 的 `Remove-Item` 覆盖会拦截 `Remove-Item -Recurse -Force $home`（因为含 `-Recurse -Force`），但**不检测 `$home` 赋值本身**。需新增 PowerShell 自动变量碰撞检测（见 §7.17）。

**额外教训**：子 agent 的破坏性动作记录在 subagent rollout，但**不出现在父任务 UI action list**——需 §7.20 RiskChain 跨 agent 追踪。

#### 3.10.4 Zed 1.14.2——首个 OS 级 AI agent 沙箱（2026-08-05）

> 来源：[Zed 1.14.2 沙箱](https://byteiota.com/zed-1-14-2-os-level-ai-agent-sandboxing-arrives/)，第一个在 OS 级沙箱化 agent terminal 命令的主要 AI 编码编辑器

**关键设计**：`.git` 目录写入**永久阻断，即使显式批准也不可解锁**——deliberate design choice 防 history tampering。比任何 hook 层 guard 更强（kernel 不在乎 agent 认为自己能做什么）。

**对本方案的影响**：本方案 §4.1 #19 `immutable_core.yaml` 已保护 `.git/**`，但那是配置层防护（commit 时检查），不是运行时拦截。需在 §7.1 wrapper 中新增 `.git` 路径写入硬阻断（见 §7.17 一并处理）。

#### 3.10.5 Pillar Security "Week of Sandbox Escapes"——Trust Handoff Flaw（2026-07-20~22）

> 来源：[CSA 研究笔记](https://labs.cloudsecurityalliance.org/wp-content/uploads/2026/07/CSA_research_note_ai_coding_agent_sandbox_escapes_20260722-csa-styled.pdf)，影响 Cursor/Codex/Gemini CLI/Antigravity

**核心发现**："Trust Handoff Flaw"——7 个沙箱逃逸都**不破坏沙箱本身**，而是利用"沙箱限制 agent 动作，但不限制 agent 产出文件被沙箱外信任组件消费"的缝隙。agent "留在盒子里遵守每条规则"，但写一个文件（hook config / venv interpreter / Git config entry / task definition），沙箱外的工具之后运行它。

**对本方案的影响**：本方案无沙箱（§9 已裁定不引入沙箱——Windows 无 macOS Seatbelt 等效物），但 Trust Handoff 概念仍适用——**需审计 hook config / venv / Git config / task definition 文件的写入路径**。这些是 agent 产出的"二级危险源"。

#### 3.10.6 CFD 攻击——per-call guardrail 的根本缺陷（arXiv:2606.09084 2026-06-09）

> 来源：[CFD 论文](https://arxiv.org/html/2606.09084v1)，2026-07-31 更新

**Context-Fractured Decomposition**：把一个禁止动作拆成多个单独无辜的工具调用，跨 session/tool/agent 实例组装。**per-call guardrail 全部失效**——jailbreak 成功率比 SOTA（Crescendo/ToT）高 **28.14 个百分点**。

**根因**："provenance gap"——artifact 来源（谁写的、为何写、属于哪个目标）几乎不被追踪。

**对本方案的影响**：§7.16 Circuit Breaker 是 per-command 级别，无法防御 CFD。需升级为 session-level RiskChain（见 §7.20）。

#### 3.10.7 IETF Agent Audit Trail 草案——审计日志 hash chaining 标准（2026-03-29）

> 来源：[IETF draft-sharif-agent-audit-trail-00](https://www.ietf.org/archive/id/draft-sharif-agent-audit-trail-00.txt)，IETF Standards Track Internet-Draft

**核心特性**：
- JSON 记录结构，**强制字段**：agent identity、action classification、outcome tracking、trust level
- **Tamper-evident hash chaining**（SHA-256 per RFC 8785）——每条日志含前一条的 hash
- 可选 **ECDSA 签名**（non-repudiation）
- 映射 **EU AI Act**（Regulation 2024/1689，2026-08 生效）、SOC 2、ISO/IEC 42001、PCI DSS v4.0.1
- 隐私：input/output hashing + tombstone-based deletion（GDPR Article 17）

**对本方案的影响**：§7.10 的 `_ZephyrAuditLog` 是 plain JSONL append-only，无 hash chaining——agent 可篡改日志掩盖痕迹。远期升级为 AAT 兼容格式（见 §10 开放问题）。

#### 3.10.8 grite——git-native + CRDT 事件日志 + advisory leases（arXiv:2606.19616 2026-06-17）

> 来源：[grite 论文](https://arxiv.org/pdf/2606.19616)，Arizona State University，server-less + git-native 协调

**核心创新**：协调记录存在 git refs 内（`refs/grite/locks`），随 fetch/push 传播。每个协调动作 = append-only、content-addressed、可签名事件日志的一条；per-agent 副本用 **CRDT 语义**合并 + **advisory leases** 实现互斥。

**实测结果**（对本方案 §11 的关键警示）：
- **C1 协调效率**：duplicate-work rate **78% → 0%**，goodput **>3×**
- **C2 收敛无数据丢失**：副本任意顺序收事件收敛到 byte-identical 状态；**file-based tracker 会静默丢失并发写** ⚠️
- **C3 可挖掘**：自动检测 conflicting edits / lock starvation / redundant rediscovery / race-to-close

**对本方案 §11 的关键影响**：
1. §11.3.3 的 SQLite Task Board 设计**正确**（grite C2 证实 JSON file board 会丢并发写）
2. §11.3.2 的 advisory lease + TTL 设计**正确**（grite 验证 advisory 优于 mandatory）
3. **新增改进方向**：lease 过期判定从固定 TTL timeout 升级为 **Phi Accrual Failure Detector**（见 §3.10.9）
4. **新增可选演进**：若未来需跨副本/跨机收敛，采用 grite 模式（CRDT 事件日志存 git refs）

#### 3.10.9 Phi Accrual Failure Detector——替代固定 TTL 的自适应心跳检测

> 来源：[Cassandra/Akka 生产使用](https://learn.padho.ai/wiki/phi-accrual-failure-detector)，[systemdesignsimulator.org](https://systemdesignsimulator.org/internals/phiaccrual)

**算法**：维护心跳 inter-arrival 时间的滑动窗口（典型 1000 样本），用 Welford 在线算法更新 mean/variance，假设正态分布计算 `phi = -log10(P(arrival ≥ t - last_seen))`。

**phi 阈值含义**：
- φ=1 ≈ 1/10 概率是瞬时延迟（误报）
- φ=3 ≈ 1/1000（激进 lease-renew）
- φ=8 ≈ 1/10^8（保守 remove-membership）

**优于固定 TTL timeout**：
- 自适应网络抖动、GC pause、WAN jitter
- 同一心跳流可服务多个阈值路径（renew 用低阈值，remove 用高阈值）
- 检测器永不决策，只发布连续 φ 值

**对本方案 §11.3.2 的影响**：当前固定 TTL 60min 在 agent 长时间 GC pause 或系统卡顿时会**误释放锁**（其他 agent 抢锁后原 agent 恢复，导致双写）。升级为 Phi Accrual 后，φ>8 才判定 lease 过期，容忍 GC pause。

#### 3.10.10 CoAgent MTPO——advisory concurrency + LLM-as-judge 范式转变（arXiv:2606.15376 2026-06-13）

> 来源：[CoAgent 论文](https://arxiv.org/pdf/2606.15376)，上海交大

**核心洞察**：传统 2PL 在长 LLM 推理间阻塞；OCC abort-and-retry 丢弃数分钟工作。LLM agent 有一个经典事务没有的能力——**LLM 自己能判断一个冲突写是否真的使其计划失效，并精确修复依赖它的操作**。

**MTPO (Monotonic Trajectory Pre-Order) 协议**：
1. launch 时固定序列化顺序
2. 读返回 order-filtered 值
3. 写 **speculatively in-place** 应用
4. 单向通知受影响 reader 重新判断并修补计划
5. 框架通过每个 tool 注册的 saga-style inverse 机械地撤销并重排错位写
6. quiescence 时按预定顺序可序列化

**实测**：10 个争用 workload 上，CoAgent 在 **1.4× 加速** + 近串行 token 成本下保持**串行正确性 5% 以内**；2PL 和 OCC 几乎放弃所有并发收益。

**范式转变**："control turns advisory: the runtime informs, the agent repairs"——从"防止冲突"转向"让 LLM 修复冲突"。

**对本方案 §11 的影响**：§11.3.2 的 file lock 是 2PL 思路（防冲突）。若任务粒度允许每个 tool 注册 saga-style inverse，CoAgent MTPO 是比 file lock 更轻量、更鲁棒的路径。**作为 §11 的可选高级演进记录，暂不施工**（需每个 tool 注册 inverse，工程量大）。

#### 3.10.11 SQLite CAS 模式——单机多 AI 首选（验证 §11.3.3 设计正确）

> 来源：[timetobuildbob SQLite CAS](https://timetobuildbob.com/blog/building-multi-agent-coordination-with-sqlite/)，[wolbarg SQLite 足够](https://wolbarg.com/blog/why-sqlite-is-enough-for-local-ai-agent-memory)

**核心 SQL**：
```sql
UPDATE leases SET holder = ?, epoch = epoch + 1
WHERE path = ? AND (holder IS NULL OR expires_at < datetime('now'))
-- 若 changes() > 0 则抢占成功
```

**关键设计**：
- **epoch 计数器**：防 ABA（lease 释放后又被获取）
- **UPSERT**：单语句处理首次 claim 与争用 claim
- **WAL 模式**：读不阻塞写
- **TTL 60s = 4× 客户端 15s heartbeat**（容忍 3 次漏 beat）——参考 tripod-api 2026-07-17 实测

**对本方案 §11.3.3 的验证**：SQLite Task Board 设计**正确**，但需补充 epoch 计数器防 ABA（当前 §11.3.3 schema 无此字段）。

#### 3.10.12 Microsoft Defender for Endpoint AI agent runtime protection（2026-08）

> 来源：[Microsoft 官方文档](https://learn.microsoft.com/en-gb/defender-endpoint/configure-ai-agent-runtime-protection)，企业 Windows 设备级 prompt injection 检测

**机制**：`Set-MpPreference -AiAgentProtection <mode>`（Disabled/Audit/Block），要求 `AntivirusSignatureVersion >= 1.451.224.0`。

**对本方案的影响**：本方案是个人项目，但若未来企业化，Defender AI agent protection 是设备级补充层。**作为远期评估记录，暂不施工**。

#### 3.10.13 Trae SOLO 是单 agent loop（非多 agent grid）——澄清 §11.1.1

> 来源：[1DevTool 对比](https://1devtool.com/alternative/trae-alternative)

**关键发现**：Trae SOLO 是**单 agent 循环**（"Single SOLO loop"），**不支持原生并行 agent grid / agent pipelines**。Trae 锁定自家 agent，不能把 Claude Code/Codex CLI/Gemini CLI 作为一等 agent 并行运行。

**对本方案 §11.1.1 的影响**：§11.1.1 写"项目当前 26 路 AI 在 Trae 上并发施工"——这**实际是 26 个 Trae IDE 窗口/对话并发**，每个窗口内是单 SOLO agent 循环。不是 Trae 原生的多 agent grid。本方案 §11 三件套仍然适用（隔离 26 个 SOLO 循环的文件冲突），但需澄清"并发"语义。

#### 3.10.14 Vibe Kanban 状态更新（bloop 关停）

> 来源：[vibe-kb.com](https://vibe-kb.com/)，bloop 公司于 2026-04-10 关停，项目转为 Apache 2.0 社区维护

**对本方案 §11.2.1 的影响**：§11.2.1 写"Vibe Kanban 27K+ stars, 280+ releases"——这是 bloop 关停前的数据。当前状态：社区维护、完全本地化。**作为业界事实标准的参考价值仍在**，但需标注状态变化。

#### 3.10.15 第七轮搜索总结——比现有方案更好的算法清单

| 优先级 | 升级项 | 来源 | 现有方案 | 更优算法 | 施工项 |
|---|---|---|---|---|---|
| **P0** | Shell 反混淆归一化层 | AgentTrust + GuardFall | 正则匹配 raw text | 9 策略反混淆后匹配 | §7.18 |
| **P0** | PowerShell 自动变量碰撞检测 | Codex #32684 | 无 | 检测 `$home`/`$HOST`/`$PID`/`$PSHOME` 赋值 | §7.17 |
| **P0** | `.git` 目录写入永久阻断 | Zed 1.14.2 | immutable_core.yaml 配置层 | 运行时硬阻断 | §7.17 |
| **P1** | SafeFix（block+suggest） | AgentTrust | 仅 BLOCKED | BLOCKED + safer alternative | §7.19 |
| **P1** | RiskChain session 级追踪 | AgentTrust + CFD | per-command circuit breaker | session 级多步攻击链 | §7.20 |
| **P1** | Risk-tiered fail mode | Cordum 矩阵 | 全局 fail-open/closed | 按操作影响动态选 | §7.21 |
| **P1** | 跨工具/跨 shell 绕过检测 | hermes-agent #69256 | 无 | normalize 路径/shell/tool | §7.22 |
| **P2** | AAT hash-chaining 审计日志 | IETF draft-sharif | plain JSONL | SHA-256 chain + ECDSA | §10 远期 |
| **P2** | Phi Accrual 替代固定 TTL | Cassandra/Akka | TTL 60min | φ>8 判定过期 | §11.3.2 升级 |
| **P2** | epoch 计数器防 ABA | SQLite CAS | 无 | `epoch = epoch + 1` | §11.3.3 补充 |
| **P3** | CoAgent MTPO LLM-as-judge | arXiv:2606.15376 | file lock 防冲突 | LLM 修复冲突 | §11 远期评估 |
| **P3** | Microsoft Defender AI | Microsoft 2026-08 | 无 | 设备级 prompt injection | §10 远期评估 |

### 3.11 第八轮搜索补充（v1.6.0——PS 5.1 兼容性+Windows 专用防御层+git 专属攻击向量）

> 搜索时间：2026-08-11 第四轮，覆盖 arXiv/GitHub CVE/CSA/Microsoft Build 2026/Pillar Security/GitPython Advisory/dulwich Advisory

#### 3.11.1 PS 5.1 兼容性是头号风险（v1.5.0 代码 bug）

> **v1.6.0 关键修复**：v1.5.0 代码用了 5 处 `?.` 运算符（PS 7.1+ 专有），在 PS 5.1 上**必然报错** `Unexpected token '?.'`。

**PS 5.1 不支持的 PS 7+ 语法清单**（来源：[spec-kit PR #1975](https://github.com/github/spec-kit/pull/1975) 2026-03-25 + [asgardeo/thunder issue #950](https://github.com/asgardeo/thunder/issues/950)）：

| 语法 | 引入版本 | PS 5.1 兼容 | 替代方案 |
|---|---|---|---|
| `?.` null-conditional member | PS 7.1+ | ❌ | `if ($obj) { $obj.Prop } else { $null }` |
| `??` null-coalescing | PS 7.0+ | ❌ | `if ($null -ne $x) { $x } else { $default }` |
| `&&` pipeline chain | PS 7.0+ | ❌ | `if ($cmd1) { $cmd2 }` |
| `\|\|` pipeline chain | PS 7.0+ | ❌ | `if (-not $cmd1) { $cmd2 }` |
| ternary `? :` | PS 7.0+ | ❌ | `if ($cond) { $a } else { $b }` |
| 3-arg `Join-Path` | PS 6.0+ | ❌ | 嵌套 `Join-Path (Join-Path $a $b) $c` |
| `[IO.Directory]::ResolveLinkTarget()` | PS 7.0+ | ❌ | P/Invoke `DeviceIoControl` |

**v1.6.0 修复**：5 处 `?.` 已全部替换为 PS 5.1 兼容的 `if` 判断模式。

#### 3.11.2 PSReadLine 对 AI agent 脚本无效（§7.17.1 修订）

> 来源：[Microsoft PSReadLine 文档](https://learn.microsoft.com/en-us/powershell/module/psreadline/about/about_psreadline_functions?view=powershell-5.1) ms.date 2026-05-02

**关键发现**：PSReadLine **仅在交互式 REPL 中工作**，对 AI agent 通过 `-Command`/`-File`/`-EncodedCommand` 调用的脚本**完全无效**。这意味着 §7.17.1 的"PSReadLine `Set-PSReadLineKeyHandler` Enter 键钩子"方案**根本性缺陷**——AI agent 的命令不经过 PSReadLine。

**修订**：§7.17.1 集成方式第 2 点已删除 PSReadLine 方案，改用 wrapper 函数内检测（唯一可靠路径）+ Script Block Logging 4104 事后审计。

#### 3.11.3 git config 注入攻击——2026 年最严重 git 专属漏洞（CVE-2026-44244/67326）

> 来源：[CVE-2026-44244](https://advisories.gitlab.com/pypi/gitpython/CVE-2026-44244/) 2026-05-06 + [CVE-2026-67326](https://cve.circl.lu/vuln/cve-2026-67326) 2026-08-01 + [SB2026080540](https://www.cybersecurity-help.cz/vdb/SB2026080540) 2026-08-05

**攻击链**：GitPython `set_value()` 不校验 value/section/option 中的换行符 → 注入 `[core]\nhooksPath=/tmp/evil` → 后续 git 操作执行攻击者 hook → **RCE**。影响 GitPython < 3.1.50（DVC/MLflow/Kedro 依赖）。

**对本方案的影响**：`git config core.hooksPath*` 必须加入 §7.1 wrapper 阻断列表。AI agent 调用 `git config` 时，wrapper 必须校验 section/option/value 三者都拒绝 CR/LF/NUL。

#### 3.11.4 git worktree 沙箱逃逸（CVE-2026-55607）——§11 worktree 安全加固

> 来源：[CVE-2026-55607](https://www.penligent.ai/hackinglabs/cve-2026-55607/) 2026-07-10 + [codex-plugin-cc #13](https://github.com/axisrow/codex-plugin-cc/issues/13) 2026-07-19

**攻击链**：worktree 名为 `.git` → gitdir 混淆 → 符号链接操纵 → `core.fsmonitor` 执行 → 写入用户 home 目录 → **逃逸 macOS Seatbelt 沙箱**。Claude Code 2.1.38–2.1.162 受影响，2.1.163 修复。

**对本方案 §11 的影响**：`git worktree add` 必须拒绝 worktree 名为 `.git` 或含路径穿越的请求；创建前强制 `core.fsmonitor none`；校验主 `.git` realpath 不在 home/ssh/config 路径下。

#### 3.11.5 git filter-repo AI agent 误用（GhostXia/AIRP #104）

> 来源：[GhostXia/AIRP issue #104](https://github.com/GhostXia/AIRP/issues/104) 2026-07-08

**案例**：AtomCode (GLM-5.2) AI agent 执行 `git filter-repo --force --refs main --message-callback '...'` + `git push --force origin main`——**不可逆历史重写 + force push**。agent 自建了 `refs/backup/main-before-filter-repo` 才执行。

**对本方案的影响**：`git filter-branch`/`git filter-repo` 必须加入 §7.1 wrapper 阻断列表，强制前置 `git update-ref refs/backup/...`。

#### 3.11.6 git reflog expire + gc --prune——forensic 证据抹除

> 来源：[aitoolsguidebook.com](https://aitoolsguidebook.com/en/articles/ai-rollback-changes/) 2026-06-17

`git reflog expire --all --expire=now && git gc --prune=now` 可永久摧毁 forensic 恢复能力。被劫持 agent 可在执行恶意 commit 后清除本地证据。

**对本方案的影响**：`git reflog expire`、`git gc --prune=*` 必须加入 §7.1 阻断列表，强制先 `git reflog show --all` 落盘外部审计。

#### 3.11.7 git update-index 绕过 commit gate

> 来源：[jwbron/egg PR #277](https://github.com/jwbron/egg/pull/277) 2026-02-07

`git update-index --cacheinfo`/`--index-info`/`--info-only` 能绕过 `git add`（通常被 commit gate 拦截）直接操纵 index。

**对本方案的影响**：`git update-index` 仅允许 `--chmod`/`--refresh`/`--really-refresh`/`--verbose`/`--quiet`；阻断 `--cacheinfo`/`--index-info`/`--info-only`/`--stdin`/`--add`/`--remove`/`--force-remove`/`--replace`/`--assume-unchanged`/`--skip-worktree`。

#### 3.11.8 git notes 侧信道持久化

> 来源：[spelunk-cloud/spelunk issue #344](https://github.com/spelunk-cloud/spelunk/issues/344) 2026-06-06

`git notes` 附加在 commit 上的内容不进入 commit 对象本身，存储在 `refs/notes/commits`。可承载 prompt-injection payload/密钥，随 `git clone`/`git fetch` 传播。

**对本方案的影响**：`git notes add`/`append`/`edit` 应阻断或强制 secret-scan 前置；AI agent 读取 git 历史时 wrapper 应以 `--no-notes` 调用 `git log`。

#### 3.11.9 git apply 符号链接重放攻击

> 来源：[codex-plugin-cc #13](https://github.com/axisrow/codex-plugin-cc/issues/13) 2026-07-19

`git apply --index` 重放 worktree diff 时，worktree 中创建的符号链接（mode-120000 entry）被逐字保留，`git apply` 在 RepoRoot 重建该符号链接指向 host 文件（如 `~/.ssh/authorized_keys`）。

**对本方案的影响**：`git apply` 在应用前扫描 patch 中的 mode-120000（symlink）条目，拒绝。

#### 3.11.10 git submodule 路径穿越写 .git/hooks

> 来源：[dulwich GHSA-gfhv-vqv2-4544](https://github.com/jelmer/dulwich/security/advisories/GHSA-gfhv-vqv2-4544) 2026-05-28

攻击者构造 `.gitmodules` + gitlink，令 `path = .git/hooks`，则攻击者 submodule tree 内容**直接写入受害者 `.git/hooks/` 目录**，保留可执行位 → RCE。

**对本方案的影响**：`git submodule add`、`git clone --recurse-submodules` 应阻断或强制白名单源校验。

#### 3.11.11 Microsoft MXC——官方 AI agent 沙箱（2026-06 Build）

> 来源：[github.com/microsoft/mxc](https://github.com/microsoft/mxc) 2026-06-02 + [Origin HQ 深度分析](https://www.originhq.com/research/mxc-execution-containers-internals) 2026-06-04

微软 Build 2026 发布的官方 AI agent 沙箱，10 个 containment backends（Windows ProcessContainer/AppContainer/WSL2/Hyperlight + Linux bubblewrap/LXC + macOS Seatbelt）。Windows 默认 ProcessContainer 三级隔离（BaseContainer/AppContainer+BFS/AppContainer+DACL）+ Job Object UI limits。

**对本方案的影响**：MXC 是进程级沙箱（限制 agent 能访问什么资源），wrapper 是命令级过滤（限制 agent 能执行什么命令）——**互补而非替代**。远期评估"AI agent → MXC ProcessContainer → 内部 PowerShell wrapper"架构。**暂不施工**（README 明确声明"no MXC profiles should be treated as security boundaries currently"）。

#### 3.11.12 PowerShell Script Block Logging 4104——引擎级审计补充

> 来源：[evtxparser 4104 详解](https://www.evtxparser.com/en/blog/powershell-4104-scriptblock) 2026-05-17 + [securityscriptographer](https://www.securityscriptographer.com/2026/05/powershell-script-block-logging-with.html) 2026-05-28

4104 事件记录 PowerShell 引擎编译的所有 scriptblock（含反混淆后的真实代码），是"最接近 EDR 的平台原生能力"。与 §7.10 `_ZephyrAuditLog` JSONL 互补：4104 是引擎级日志，_ZephyrAuditLog 是应用级日志。

**对本方案的影响**：wrapper 在每次决策时同步写 JSONL 并附带 4104 EventRecordId，实现"应用决策 ↔ 引擎代码"双向追溯。启用：`HKLM\Software\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging\EnableScriptBlockLogging = 1`，通道扩到 1GB。

#### 3.11.13 symlink/junction + TOCTOU——wrapper 结构性缺陷

> 来源：[hackita.it symlink 攻击](https://hackita.it/articoli/secreatesymboliclinkprivilege/) 2026-06-09 + [CVE-2026-23988](https://radar.offseq.com/threat/cve-2026-23988-cwe-367-time-of-check-time-of-use-t-d8faaf97) + [PBNZ watch-local #9](https://github.com/PBNZ/watch-local/issues/9) 2026-07-16

**symlink 攻击**：`mklink /J`（目录 junction）不需要任何特权，wrapper 检查 `Test-Path` 返回 True（junction 指向 .git/），wrapper 删除或写入"config"时实际作用于 .git/ 内部文件。

**TOCTOU**：wrapper `Test-Path` → `Remove-Item` 之间的窗口期可被 `mklink` 替换。CVE-2026-23988（Rufus PowerShell 脚本 TOCTOU 提权）证实此模式可利用。

**对本方案的影响**：wrapper 的 `Test-Path` + `Remove-Item` 模式是结构性缺陷。需用 **Atomic Path Resolution** 算法（P/Invoke `CreateFile` + `FILE_FLAG_OPEN_REPARSE_POINT` + handle 保留到操作完成）替代。

#### 3.11.14 2026-07/08 AI agent + git 重大攻击事件汇总

| 事件 | 时间 | 攻击向量 | 影响 |
|---|---|---|---|
| **GitLost** | 2026-07-23 | GitHub Issue 间接 prompt 注入 → agent 跨仓读私有 repo → 公开评论外泄 | 绕过仅需"Additionally"一词 |
| **Novee @ Black Hat** | 2026-08-05 | 单条 Issue → RCE on Anthropic/Google/OpenAI CI runner | CVE-2026-54316/12537 |
| **FakeGit/AgentBaiting** | 2026-07-24 | 7600 恶意仓伪装 MCP/skills | Claude Code/Gemini/ChatGPT 主动推荐 |
| **Miasma 蠕虫** | 2026-08-06 | 感染 73 个 Microsoft 官方仓 | 专攻 Claude Code/Cursor/Gemini CLI |
| **Cline Trojan Task** | 2026-05-08 | GitHub Issue 注入 Cline issue-triage agent | trojanized Cline 发布 |
| **GitInject** | 2026-06-07 | arXiv 论文：11 类命名攻击框架 | config-file injection/credential exfil |

#### 3.11.15 第八轮搜索总结——比现有方案更好的算法清单

| 优先级 | 升级项 | 来源 | 现有方案 | 更优算法 | 施工项 |
|---|---|---|---|---|---|
| **P0** | PS 5.1 `?.` 兼容性修复 | spec-kit #1975 | `?.` 运算符（PS 7+） | `if` 判断（PS 5.1 兼容） | §7.17-7.22 已修复 |
| **P0** | git config/hooksPath 阻断 | CVE-2026-44244/67326 | 无 | wrapper 阻断 + CR/LF/NUL 校验 | §7.23 |
| **P0** | git filter-branch/filter-repo 阻断 | GhostXia/AIRP #104 | 无 | wrapper 阻断 + 强制备份 ref | §7.23 |
| **P0** | git reflog expire/gc --prune 阻断 | aitoolsguidebook | 无 | wrapper 阻断 + 强制外部审计落盘 | §7.23 |
| **P0** | git update-index 危险 flag 阻断 | jwbron/egg #277 | 无 | wrapper 阻断 --cacheinfo 等 | §7.23 |
| **P0** | git worktree .git 名拒绝 + fsmonitor 禁用 | CVE-2026-55607 | 无 | wrapper 校验 worktree 名 + 强制 fsmonitor none | §7.25 |
| **P1** | symlink/junction + TOCTOU 防护 | hackita.it + CVE-2026-23988 | Test-Path+Remove-Item | Atomic Path Resolution（P/Invoke CreateFile） | §7.24 |
| **P1** | git hook 双签 + hooksPath 白名单 | CVE-2026-44244/67326 | immutable_core.yaml 配置层 | 签名校验 + hash 锁定 | §7.25 |
| **P1** | git notes 读取隔离（--no-notes） | spelunk #344 | 无 | wrapper 强制 --no-notes | §7.23 |
| **P1** | git apply symlink mode-120000 拒绝 | codex-plugin-cc #13 | 无 | wrapper 扫描 patch 拒绝 symlink | §7.23 |
| **P1** | git submodule path 校验 | dulwich GHSA-gfhv-vqv2-4544 | 无 | wrapper 解析 .gitmodules 拒绝 .git/.. | §7.23 |
| **P2** | Script Block Logging 4104 集成 | evtxparser/securityscriptographer | 仅 _ZephyrAuditLog JSONL | 4104 EventRecordId 绑定 | §7.26 |
| **P2** | reflog 不可变窗口 | aitoolsguidebook | 无 | expire 前强制落盘外部审计 | §7.25 |
| **P3** | MXC ProcessContainer | Microsoft Build 2026 | 无 | 官方沙箱（互补 wrapper） | §10 远期评估 |
| **P3** | Job Object + Restricted Token | agentbox/Omnipus/inclave | 无 | 内核级资源隔离 | §10 远期评估 |

### 3.12 第九轮搜索补充（v1.7.0——Trae 多 AI 并发病根分析+治本方案）

> 搜索时间：2026-08-11 第五轮，覆盖 Trae GitHub Issues/PowerShell Issues/Claude Code Issues/OpenClaw RFC/Microsoft MXC/CoAgent MTPO/f2t.jp 并发事故

#### 3.12.1 病根定位——Trae 多 session 架构实证

> 来源：[Trae issue #1987](https://github.com/Trae-AI/TRAE/issues/1987) + [Trae issue #2503](https://github.com/trae-ai/trae/issues/2503) + [Trae changelog 2026-06-12 v3.5.66](https://www.trae.ai/changelog)

**实证发现**：
1. **Trae 每个 session 是独立 PowerShell 进程**——issue #1987 证实多窗口叠加多个 `trae-helper` + `ai-agent` 进程，CPU 累加；issue #2503 证实终端按 workspace ID 独立 spawn、独立环境变量
2. **进程级隔离本身是好的**（崩溃不互相影响）——✅
3. **但共享状态文件仍会发生 read-modify-write 竞态**——❌

**共享状态文件清单**（26 session 并发访问）：

| 共享文件 | 竞态类型 | 现有代码 | 后果 |
|---|---|---|---|
| `~/.zephyr_audit/audit_{yyyyMMdd}.jsonl` | 多进程并发 append | `Add-Content`（无锁） | **数据交错/丢失**（PowerShell #24774） |
| `.ailocks/registry.json` | 多进程并发 read-modify-write | JSON 文件直写（无锁） | **丢锁/双锁**（grite C2 证实） |
| `.trae/rules/project_rules.md` | 多进程并发修改 | 无防护 | **规则污染**（恶意 session 注入规则） |
| `AGENTS.md` | 多进程并发修改 | 无防护 | **规则污染** |
| `.git/index` | 多进程并发 `git add`/`git commit` | git index.lock（但 add+commit 间有窗口） | **commit 内容错乱**（f2t.jp 2026-06-12 案例） |
| `$_circuitState` | per-session 仅 | PowerShell 变量 | **跨 session 不感知**（恶意 AI 换 session 绕过） |
| `$_riskChain` | per-session 仅 | PowerShell 变量 | **CFD 跨 session 攻击无法检测** |

#### 3.12.2 决定性证据——Claude Code `.claude.json` 423 次损坏

> 来源：[claude-code issue #29217](https://github.com/anthropics/claude-code/issues/29217) 2026-02-27

Claude Code 用户 7 天累计 **423 次 `.claude.json` 跨 session 损坏**，最严重一天 280 次。损坏级联——每次恢复尝试又被并发 writer 损坏，文件从 11873 字节级联缩到 77 字节。21 个不同 `userID` hash 出现在损坏文件中，证明多 session 抢写。**Claude Code 官方关闭为"not planned"**——说明这是一个未解决的行业级痛点。

**对本方案的警示**：`_ZephyrAuditLog` 的 `Add-Content` 和 `lock_files.py` 的 `registry.json` 与 `.claude.json` 是同样的并发 read-modify-write 模式，在 26 session 并发下**必然损坏**。

#### 3.12.3 决定性证据——AI session 并发 git index 抢占

> 来源：[f2t.jp 2026-06-12](https://f2t.jp/blog/claude-parallel-session-git-lock)

实测 `git add A B` 后 `git commit`，commit 进去的却是 C D E，A B 仍 uncommitted——因为 add 与 commit 之间另一 session 的 `git add` 覆盖了共享 index。

**对策**（f2t.jp 建议）：
1. `git add X && git commit -m "..."` 链为单命令（消除竞争窗口）
2. `git diff --cached --stat` commit 前验证暂存内容
3. **根本解**：每 session 用 `git worktree` 独立工作目录，不共享 index

#### 3.12.4 PowerShell 并发文件写入安全算法

> 来源：[PowerShell issue #24774](https://github.com/PowerShell/PowerShell/issues/24774) + [commandinline Add-Content Cheat Sheet](https://www.commandinline.com/add-content-cmdlet-cheat-sheet/) 2026-02-23 + [GenXdev WriteJsonAtomic](https://www.powershellgallery.com/packages/GenXdev.FileSystem/3.23.2026) 2026-03

**关键发现**：`Add-Content`/`Set-Content`/`Out-File -Append` **都不是并发安全的**——PowerShell #24774 实测 1000 并行 writer 产生数据损坏。

**PS 5.1 安全并发文件写入算法**：

| 算法 | 机制 | PS 5.1 | 适用场景 |
|---|---|---|---|
| **A. 命名 Mutex** | `Global\` 前缀跨进程互斥 + `WaitOne(timeout)` + `try/finally ReleaseMutex` | ✅ | 多进程并发写同一文件 |
| **B. 原子写（temp+rename）** | `[IO.File]::WriteAllText($tmp)` + `Move-Item -Force`（Windows `MoveFileExW` 原子） | ✅ | 防崩溃半成品 |
| **C. StreamWriter + FileShare.ReadWrite** | `[IO.StreamWriter]::new($path, $append, $encoding, $bufferSize)` | ✅ | 单进程高频写 |
| **D. 每session独立文件** | 文件名含 `$env:ZEPHYR_SESSION_ID`，离线合并 | ✅ | JSONL 日志 |

**不适用 PS 5.1**：`ForEach-Object -Parallel`（PS 7+ 专有）；Linux `fcntl.flock`（Windows 无）。

#### 3.12.5 OpenClaw GovernanceStore——跨 session 协调 RFC

> 来源：[OpenClaw issue #27442](https://github.com/openclaw/openclaw/issues/27442) 2026-02-26

OpenClaw RFC 提出跨 session 治理的三类需求：①跨 session token 预算 ②agent 级 circuit breaker（区别于单 tool loop 检测）③operator 控制的 kill switch。提出 `GovernanceStore` 接口（`increment`/`get`/`setFlag`/`getFlag`）+ `governance_halt_requested` hook。痛点原话："a plugin that wants to track this has to manage its own persistence and hope nothing races."

**对本方案的影响**：§7.16 Circuit Breaker 和 §7.20 RiskChain 都是 per-session，无法跨 session 协调。需引入 GovernanceStore（共享 SQLite 或文件+Mutex）实现跨 session 状态。

#### 3.12.6 WOWHOW Single-Push Protocol——多 agent git 串行化

> 来源：[WOWHOW Single-Push](https://dev.to/akaranjkar08/single-push-discipline-multi-agent-git-workflow-2026-bo3) 2026-06-27

4 阶段多 agent git 协调协议：
1. **Diverge**：PA 并行 worktree 仅本地 commit 不 push
2. **Signal**：写 `.agent-done/<id>` marker
3. **Integrate**：单 IL 串行 merge + build
4. **Ship**：IL 仅 push 一次

消除 double-deploy 502。**对本方案 §11 的补充**：§11.3.1 worktree + §11.3.3 Task Board 需增加"串行 integrate + single push"阶段。

#### 3.12.7 Trae 病根治本方案三层架构

| 层 | 机制 | 现状 | 施工项 |
|---|---|---|---|
| **L1 进程隔离** | 每 session 独立 PowerShell 进程 + 独立 git worktree | ✅ Trae 已默认实现进程隔离；§11.3.1 worktree 待施工 | §11.3.1 |
| **L2 共享状态串行化** | 对所有跨 session 共享文件统一走"命名 Mutex + temp+rename 原子写"管线；`git add && git commit` 单命令；commit 走 single-flight 串行网关 | ❌ 现有代码全部无锁 | §7.27-7.31 |
| **L3 跨 session 协调协议** | 共享 GovernanceStore（SQLite）实现跨 session circuit breaker + RiskChain + token 预算 + kill switch | ❌ 现有 per-session 仅 | §7.29 |

### 3.13 第十轮搜索补充（v1.8.0——Named Pipe 单线程协调器+Session 身份+Trae Hooks）

> 搜索时间：2026-08-11 第六轮，覆盖 rjmurillo/ai-agents/ResidentDaemon/PowerServe/Microsoft AGT/Trae Hooks 文档/Rutgers CS 课程

#### 3.13.1 核心发现——Named Pipe 单线程协调器优于 Mutex+SQLite

> 来源：[rjmurillo/ai-agents Issue #287](https://github.com/rjmurillo/ai-agents/issues/287) + [ResidentDaemon 2026-04](https://qiita.com/kassyi/items/1f432a4b518f75c10052) + [Rutgers CS 417 课程笔记 2026-02](https://people.cs.rutgers.edu/~pxk/classes/417/notes/mutex.html)

**范式转变**：v1.7.0 的 Mutex+SQLite 是"用锁管理并发"——仍然有并发问题（busy_timeout/abandoned/writer 争用）。Named Pipe 单线程协调器是"**用单线程消除并发**"——根本没有并发问题。

| 维度 | Named Pipe 单线程协调器 | Mutex + SQLite |
|---|---|---|
| 并发模型 | 单线程事件循环，**天然无竞态** | 多 writer 串行化，需 busy_timeout |
| 故障恢复 | daemon 崩溃重启，状态隔离 | Mutex abandoned + SQLite WAL 恢复 |
| 跨进程开销 | 内核态 IPC，**~50μs** | Mutex syscall + SQLite 事务，~1-10ms |
| 状态可见性 | daemon 内存中（易失）→ SQLite 持久化 | SQLite 持久化（持久） |
| 复杂度 | 协议设计 + 序列化 | SQL + 锁管理 + abandoned 恢复 |
| **核心优势** | **单线程 = 无并发问题** | 成熟生态，持久化 |

**Reactor pattern 理论基础**（来源：[jwork.org/wiki/Reactor_pattern](http://jwork.org/wiki/Reactor_pattern)）：单线程事件循环 + 非阻塞 I/O 是 named pipe 协调器的核心架构。Win32 文档明确："With a single-threaded server, it is easier to coordinate operations that affect multiple clients, and it is easier to protect shared resources."

**rjmurillo/ai-agents 性能数据**：首次调用 400ms（daemon 启动），后续调用 10-50ms（80-95% 改善）。

**Rutgers CS 417 结论**（2026-02）：单机多进程的集中式协调算法是最优解——"In a single machine, these problems are solved with local mechanisms provided by the operating system"。Raft/Paxos 是 overkill。

#### 3.13.2 Trae SessionStart Hook 可注入 ZEPHYR_SESSION_ID

> 来源：[Trae Hooks 官方文档](https://docs.trae.cn/ide_hook-configuration-reference) + [OpenViking TRAE 集成 PR #3109](https://github.com/volcengine/OpenViking/pull/3109) 2026-07-10

**关键发现**：Trae 2026-06 v3.5.66 新增 Hooks 功能，SessionStart hook 可通过 `TRAE_ENV_FILE` 环境变量文件注入 session ID：

```json
{
  "version": 1,
  "hooks": {
    "SessionStart": [{
      "matcher": "startup",
      "hooks": [{
        "command": "powershell -ExecutionPolicy Bypass -File ./scripts/init-session.ps1",
        "timeout": 30
      }]
    }]
  }
}
```

**这解决了 v1.7.0 的关键 gap**：`$env:ZEPHYR_SESSION_ID` 之前没有注入机制——现在 Trae SessionStart hook 可以在 session 启动时自动生成 UUID 并注入环境变量。

#### 3.13.3 Trae 七事件 Hook 模型

> 来源：[Tencent Cloud CodeBuddy Hook 文档](https://www.tencentcloud.com/document/product/1256/77296)（与 Trae 兼容）

| 事件 | 触发时机 | 本方案用途 |
|---|---|---|
| `SessionStart` | 新 session 启动 | 注入 ZEPHYR_SESSION_ID + 初始化 wrapper + 注册到 GovernanceStore |
| `SessionEnd` | session 终止 | 自动释放锁 + 清理 circuit breaker 状态 + 生成 session 报告 |
| `PreToolUse` | 工具执行前 | 命令拦截/校验（补充 $PROFILE wrapper） |
| `PostToolUse` | 工具执行后 | 审计记录 + RiskChain 事件 |
| `UserPromptSubmit` | 用户提交 prompt | 上下文注入 |
| `Stop` | agent 停止响应 | 捕获会话状态 |
| `PreCompact` | 上下文压缩前 | 保留关键审计信息 |

#### 3.13.4 PowerShell 5.1 Named Pipe Server 完整支持

> 来源：[ResidentDaemon 生产级实现](https://qiita.com/kassyi/items/1f432a4b518f75c10052) 2026-04 + [PowerServe](https://github.com/JustinGrote/PowerServe) 2026-01

PS 5.1 通过 .NET Framework `System.IO.Pipes.NamedPipeServerStream` 完整支持 named pipe server。ResidentDaemon 模块（2026-04）给出了生产级实现，含 `Global\` Mutex 防双重启动 + 进程独立运行 + IPC 实时订阅。

**PS 5.1 后台进程保持方法**：`Start-Job` 子进程随父 session 终止被杀死——**不可用**。改用 `Start-Process` 创建独立进程（不受父 session 生命周期约束）。

#### 3.13.5 SQLite 高并发写入争用仍需配置

> 来源：[fixdevs.com SQLite locked](https://www.fixdevs.com/blog/sqlite-database-is-locked/) 2026-03 + [hironow/dominator ADR S0009](https://github.com/hironow/dominator/blob/main/docs/shared-adr/S0009-sqlite-wal-cooperative-model.md) 2026-02

即使采用 Named Pipe 协调器，SQLite 仍用于审计日志持久化。26 并发 writer 需配置：
```sql
PRAGMA journal_mode=WAL;
PRAGMA busy_timeout=5000;    -- 5 秒等待
PRAGMA synchronous=NORMAL;   -- WAL 模式下安全
```
Python 层：`db.SetMaxOpenConns(1)` 防单进程内连接池争用。事务用 `BEGIN IMMEDIATE` 而非 `BEGIN`（提前获取写锁避免升级死锁）。

#### 3.13.6 Hybrid 架构——Named Pipe 实时协调 + SQLite 持久审计

**2026-08 最佳实践**（综合 rjmurillo/ResidentDaemon/Microsoft AGT）：

```
┌─────────────────────────────────────────────────────────────┐
│  Trae Session 1..26 (各持 ZEPHYR_SESSION_ID)                │
│  └─ $PROFILE 注入 session_id + wrapper 函数                 │
│     └─ 所有协调请求 → Named Pipe Client (~50μs)             │
└────────────────────────┬────────────────────────────────────┘
                         │ (named pipe IPC, 内核态)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Zephyr Coordinator Daemon (单进程, 单线程事件循环)          │
│  ├─ NamedPipeServerStream (异步, 26+ 并发连接)              │
│  ├─ 内存中的锁/lease/circuit breaker/risk chain (无并发竞态) │
│  ├─ SQLite WAL (异步写入审计日志, 无争用)                   │
│  └─ SessionStart/End hook 集成                              │
└─────────────────────────────────────────────────────────────┘
```

**关键优势**：
1. **单线程 = 无并发问题**——不需要 Mutex、不需要 busy_timeout、不需要 abandoned 恢复
2. **~50μs 延迟**——比 SQLite WAL 写入快 20-200x
3. **内核级 IPC**——比 TCP/HTTP 更轻量
4. **进程隔离**——daemon 崩溃不影响 session，session 崩溃不影响 daemon
5. **PS 5.1 完全兼容**——`System.IO.Pipes.NamedPipeServerStream` 在 .NET Framework 4.x 可用

#### 3.13.7 第十轮搜索总结——比 v1.7.0 Mutex+SQLite 更好的算法

| 优先级 | 升级项 | 来源 | v1.7.0 方案 | v1.8.0 更优算法 | 施工项 |
|---|---|---|---|---|---|
| **P0** | Named Pipe 单线程协调器 | rjmurillo #287 + Rutgers CS | Mutex+SQLite（用锁管理并发） | Named Pipe daemon（**消除并发**） | §7.33 |
| **P0** | Session ID 注入机制 | Trae SessionStart hook | $env:ZEPHYR_SESSION_ID 无注入源 | Trae hook `TRAE_ENV_FILE` 自动注入 UUID | §7.32 |
| **P1** | Session 生命周期管理 | Trae SessionEnd hook | 无（锁/circuit breaker 不清理） | SessionEnd hook 自动释放锁+清理状态 | §7.34 |
| **P1** | Wrapper 热重载+版本管理 | ChrisTitusTech #202 | 无（26 session 版本 skew） | 版本化 $PROFILE + Reload-Profile + 协议协商 | §7.35 |
| **P1** | Mutex 跨项目隔离 | Win32 kernel namespaces | `Global\ZephyrAuditLogMutex`（跨项目冲突） | 项目路径 hash 后缀 `Global\Zephyr.{hash}.` | §7.35 |
| **P2** | SQLite busy_timeout 配置 | fixdevs.com | 无配置（默认 0 立即返回） | `busy_timeout=5000` + `BEGIN IMMEDIATE` | §7.33 |

### 3.14 第十一轮搜索补充（v1.9.0——诚实评估+AST 升级+边际收益递减确认）

> 搜索时间：2026-08-11 第七轮，覆盖 eBPF for Windows/PowerShell AST/Process Mitigation/Git Alternates/ETW/MIC/CLM/Windows Sandbox

#### 3.14.1 诚实评估——v1.8.0 是否到达边际收益递减点？

> **结论：基本到达。** 10 轮全网搜索覆盖 100+ 来源，35 个施工项，19 层防御。唯一明确的算法升级是 AST 分析替换 regex（§7.36）。其他底层方案均不适用：

| 方案 | 是否比 v1.8.0 更优 | 理由 |
|---|---|---|
| **PowerShell AST 分析** | ✅ **明确更优** | 结构性覆盖 GuardFall 3/5 类，PS 5.1 原生支持，~1ms/call |
| eBPF for Windows | ❌ 不适用 | 未生产就绪，需 test signing + 内核驱动，Microsoft 尚未签名 |
| Microsoft Defender AI | ⚠️ 部分适用 | OS 级官方方案，但要求 E5 license + Trae 未在原生支持列表 |
| Git Alternates | ❌ 不解决 | 仅共享 objects，不解决 index/refs 锁争用 |
| ETW | ❌ 仅审计 | fire-and-forget 通知，不能在执行前拦截 |
| MIC Low IL | ❌ 破坏性大 | Low IL 破坏 PowerShell 大量功能（无法写用户配置文件/temp） |
| CLM | ❌ 系统级 | 启用后影响所有 PowerShell 会话（含 Trae 自身），禁止 Add-Type/COM/.NET |
| Windows Sandbox | ❌ 不适用 | 10-15s 启动延迟 + 单实例 + 无持久化 + Trae Hooks 跨边界无效 |
| Process Mitigation | ⚠️ 附加层 | `DisallowChildProcessCreation` 可限制子进程，但不能控制文件路径访问 |

**裁定**：v1.8.0 架构（PowerShell wrapper + Named Pipe + SQLite + Trae Hooks）在 2026-08 是 PS 5.1 + Trae IDE 场景的合理选择。后续价值增长点从"文档审查"转向"代码施工"（与 project_memory 一致）。

#### 3.14.2 AST 分析是唯一明确的算法升级

> 来源：[late-cli PR #51](https://github.com/mlhher/late-cli/pull/51) 2026-04 + [GuardFall](https://byteiota.com/guardfall-ai-agent-shell-injection/) 2026-06-30 + [destructive_command_guard](https://github.com/Dicklesworthstone/destructive_command_guard)

**GuardFall 5 大绕过类——AST vs regex 覆盖对比**：

| GuardFall 类 | 攻击示例 | regex（现有） | AST（升级后） |
|---|---|---|---|
| A. Quote removal | `r''m -rf /` | ⚠️ 依赖反混淆 | ✅ AST 已剥离引号，识别为 `rm` |
| B. $IFS expansion | `rm$IFS-rf$IFS/` | ✅ 反混淆检测 | ✅ `VariableExpressionAst` 节点检测 `$IFS` |
| C. Command substitution | `$(echo rm) -rf /` | ✅ 反混淆标记 | ✅ `CommandExpansionAst` 直接识别 |
| D. Base64 piping | `echo X \| base64 -d \| sh` | ✅ 反混淆标记 | ⚠️ 需语义规则 |
| E. Alternative utilities | `find /x -delete` | ❌ 不检测 | ❌ 语法层无法识别破坏语义 |

**性能**：~1ms/call（持久化进程后），可忽略。参考 late-cli PR #51 实测。

**PS 5.1 兼容性**：✅ `[System.Management.Automation.Language.Parser]::ParseInput()` 原生支持。

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

> 冲突产生后的解决方法论（冲突三分法：叠加型合并/迭代型取新/互斥型升级裁定 + 标准 7 步流程）见 [merge_conflict_resolution_sop.md](../../01_policies_and_standards/sop/merge_conflict_resolution_sop.md)（2026-08-13 十七 worktree 大 merge 实战提炼；原 67 号，已迁至 01/sop 专区）。

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
| H. PowerShell 原生命令覆盖（v0.9.0） | 函数覆盖 Remove-Item/rd/del 等 | 拦截非 git 破坏性命令 | 需处理 cmdlet 参数绑定 | ✅ **采用** |
| I. 审计日志（v0.9.0） | JSONL 持久化所有拦截/放行 | 事后可追溯 | 日志文件增长 | ✅ **采用** |
| J. Named Pipe 协调器 daemon（v1.8.0） | 单线程消除并发 | 跨 session 状态统一 | 单点故障+复杂度高+SQLite WAL 已够 | ❌ **v2.0.0 deprecated**（见 §9） |
| K. 跨 session GovernanceStore（v1.7.0） | SQLite 共享状态 | 跨 session circuit breaker | 与 §11.3.3 Task Board 重复 | ❌ **v2.0.0 deprecated**（见 §9） |
| L. adversarial 防御层（v1.5.0-v1.6.0） | RiskChain/SafeFix/symlink/hook hash 等 | 防 AI 攻击 | 单人 AI 协作无 adversarial 场景 | ❌ **v2.0.0 deprecated**（见 §9） |

### 6.2 最终裁定：v2.1.0 精简防御层（6 层，实现简化）

> **v2.0.0 精简裁定**：v1.x 的 19 层防御（L1-L19）中，L9/L10/L12-L16/L18/L19 共 9 层在 v2.0.0 判定为单人 AI 协作场景过度工程，全部 `deprecated`。保留 6 层核心防御 + §11 三件套。
>
> **v2.1.0 第二轮精简**：v2.0.0 保留项内部的实现细节仍残留 adversarial 思维。v2.1.0 进一步简化：L4 砍掉自动变量碰撞检测（只保留 .git 阻断）；L5 从 Mutex 串行化简化为每 session 独立文件；L6 从 init-session.ps1+TRAE_ENV_FILE 简化为 $PROFILE 一行；§11 三件套去掉 heartbeat/epoch/7 天告警。6 层结构不变，实现大幅精简。

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

**v2.0.0 deprecated 的 v1.x 层级对照**：
- L9 Trash Redirect → 降级为 L2 的可选实现细节（不单独成层）
- L10 Shell 反混淆归一化 → v2.0.0 保留 regex 版（§7.18），**v2.1.0 整体 deprecated**（AI 不会混淆命令）
- L11 自动变量碰撞 + .git 阻断 → v2.0.0 保留为 L4，**v2.1.0 自动变量碰撞 deprecated**（只保留 .git 阻断）
- L12 SafeFix block+suggest → deprecated（AI 提示工程层，规则足够）
- L13 RiskChain 攻击链追踪 → deprecated（无 adversarial 场景）
- L14 Atomic Path Resolution / symlink 防护 → deprecated（无 symlink 攻击场景）
- L15 git hook 信任链 / reflog 不可变 → deprecated（单人项目无恶意 actor）
- L16 Script Block Logging 4104 → deprecated（企业级方案）
- L17 并发安全串行化 → v2.0.0 保留为 L5，**v2.1.0 从 Mutex 简化为每 session 独立文件**
- L18 跨 session GovernanceStore → deprecated（与 §11.3.3 Task Board 重复）
- L19 Named Pipe Coordinator Daemon → deprecated（SQLite WAL 已够，daemon 单点故障）

### 6.3 不采用的方案及理由

| 方案 | 不采用理由 |
|---|---|
| Go 编写的 git wrapper（git-sentinel） | 过度工程——个人项目不需要编译 Go 二进制，PowerShell 函数足够 |
| Claude Code PreToolUse hooks | Trae IDE 不支持 hooks |
| git hooks（pre-clean） | git 没有 pre-clean hook（git hook 只覆盖 commit/push/checkout 等，不覆盖 clean） |
| 定期 auto-commit | 可能 commit 垃圾文件，需设计排除规则，复杂度高，远期考虑 |
| Named Pipe Coordinator Daemon（v2.0.0 deprecated） | §11.3.3 Task Board 已用 SQLite WAL + CAS——SQLite 本身就是工业级并发方案。Named Pipe daemon 是单点故障（v1.x §14 还要单独写灾难恢复），增益仅微秒级（0.1ms→0.05ms） |
| 跨 session GovernanceStore（v2.0.0 deprecated） | 与 §11.3.3 Task Board SQLite 重复——Task Board 已是跨 session 协调层 |
| adversarial 防御层（v2.0.0 deprecated） | RiskChain/SafeFix/symlink 防护/hook hash 锁定/AST 升级等均为"防 AI 攻击自己"设计——单人单账户 AI 协作开发中 AI 是协作者不是攻击者，无 adversarial 场景 |

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
            # v1.6.0 修正：PS 5.1 不支持 ?. 运算符（PS 7.1+），用 if 判断替代
            $_resolvedPath = Resolve-Path $targetPath -ErrorAction SilentlyContinue
            $resolvedTarget = if ($_resolvedPath) { $_resolvedPath.Path } else { $null }
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
                # v1.6.0 修正：PS 5.1 不支持 ?. 运算符
                $_resolvedPath = Resolve-Path $a -ErrorAction SilentlyContinue
                $resolved = if ($_resolvedPath) { $_resolvedPath.Path } else { $null }
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
        # v1.6.0 修正：PS 5.1 不支持 ?. 运算符
        $_resolvedPath = Resolve-Path $target -ErrorAction SilentlyContinue
        $resolvedTarget = if ($_resolvedPath) { $_resolvedPath.Path } else { $null }
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

> **⚠️ v2.1.0 DEPRECATED**：AI 提示工程层过度。RULE-GIT-SAFE 规则已说明"禁止危险命令"，wrapper 阻断时简单错误消息（如"BLOCKED: git clean 会删除文件"）已够。STOP:/ALTERNATIVE: 格式规范是过度设计——AI 看到 BLOCKED 就知道不该执行，不需要教它"替代方案"。**§7.14 fail-open 策略 + 简单错误消息已足够**。本节内容保留作为决策追溯，不施工。详见 §6.2 + §9。

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

> **⚠️ v2.0.0 DEPRECATED**：单人 AI 协作无 adversarial 场景，AI 不会"无限尝试危险命令"。§7.15 错误分类已防 AI 卡死循环重试。本节保留作为决策追溯，**不施工**。详见 §6.2 + §9。

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

### 7.17 施工项 17：PowerShell 自动变量碰撞检测 + `.git` 永久阻断（L11，P0，v1.5.0 新增）

> **背景**：§3.10.3 Codex `$home` 事故证明 PowerShell 自动变量碰撞是真实灾难向量；§3.10.4 Zed 1.14.2 证明 `.git` 写入永久阻断是 kernel 级最佳实践。

#### 7.17.1 PowerShell 自动变量碰撞检测

> **⚠️ v2.1.0 DEPRECATED**：30+ 只读自动变量清单 + `_ZephyrCheckVarCollision` 函数过度。Codex `$home` 事故是极端组合案例，AI 不会主动写 `$home = "test"`。PowerShell 碰撞只读变量产生非终止错误但执行继续，不会递归删除。**改为 RULE-GIT-SAFE 加一条规则"禁止用 $HOME/$PID/$TRUE 等作变量名"即可**。本节内容保留作为决策追溯，不施工。§7.17.2 `.git` 阻断保留。详见 §6.2 + §9。

**PowerShell 只读自动变量清单**（赋值会产生非终止错误但执行继续）：

```powershell
$_readOnlyAutoVars = @(
    '$HOME', '$PID', '$PSHOME', '$HOST', '$HOSTNAME',
    '$PSCULTURE', '$PSUICULTURE', '$PSVERSIONTABLE',
    '$PID', '$SENDER', '$ARGS', '$INPUT', '$MATCHES',
    '$PSCMDLET', '$PSITEM', '$MYINVOCATION',
    '$TRUE', '$FALSE', '$NULL',  # 逻辑常量
    '$ERROR', '$EXECTIONSESSION', '$STACKTRACE',
    '$PSEMAILSERVER', '$PSDEFAULTPARAMETERVALUES',
    '$PROGRESSPREFERENCE', '$ERRORACTIONPREFERENCE',
    '$CONFIRMPREFERENCE', '$WHATIFPREFERENCE',
    '$VERBOSEPREFERENCE', '$DEBUGPREFERENCE',
    '$WARNINGPREFERENCE', '$INFORMATIONPREFERENCE',
    '$OUTPUTBUFFER', '$PSEVENTSUBSCRIBERS', '$FOREACH', '$ENUMERATOR'
)
```

**检测算法**（PowerShell 5.1 兼容）：

```powershell
# 拦截所有赋值语句——通过 PSReadLine 或 wrapper 前置检查
# 由于 PowerShell 5.1 不支持 Set-StrictMode 检测自动变量赋值，
# 采用 wrapper 函数模式：包装所有可能的赋值入口
function _ZephyrCheckVarCollision {
    param([string]$Command)
    # 检测 $var = ... 或 $var=... 形式（赋值语句）
    if ($Command -match '\$(\w+)\s*=') {
        $varName = '$' + $Matches[1].ToUpper()
        if ($_readOnlyAutoVars -contains $varName) {
            Write-Host "[SAFE] BLOCKED: 赋值只读自动变量 $varName — PowerShell 大小写不敏感，会碰撞只读变量" -ForegroundColor Red
            Write-Host "  参考 Codex Issue #32684：\$home 赋值导致 %USERPROFILE% 被递归删除" -ForegroundColor Yellow
            Write-Host "  ALTERNATIVE: 用不同变量名（如 \$_myHome 或 \$projectHome）" -ForegroundColor Yellow
            _ZephyrAuditLog -Command $Command -Action 'BLOCKED' -Reason "赋值只读自动变量 $varName（Codex #32684 教训）" -EscapeHint '使用不同变量名'
            return $false
        }
    }
    return $true
}
```

**集成方式**：
1. 在 `git()` / `Remove-Item()` / `rd()` 等所有 wrapper 函数中，前置调用 `_ZephyrCheckVarCollision`
2. ~~在 PSReadLine `Set-PSReadLineKeyHandler` Enter 键钩子中检测整行命令~~ **v1.6.0 修订**：§3.11.4 研究证实 PSReadLine 仅在交互式 REPL 中工作，**对 AI agent 通过 `-Command`/`-File`/`-EncodedCommand` 调用的脚本完全无效**——不能作为 AI agent 场景的防御层。改用 wrapper 函数内检测（唯一可靠路径）+ Script Block Logging 4104 事后审计
3. AGENTS.md RULE-GIT-SAFE 新增条款：**禁止赋值以 `$HOME`/`$PID`/`$PSHOME`/`$HOST` 等开头的变量**

#### 7.17.2 `.git` 目录写入运行时硬阻断

**算法**：在所有写文件类 wrapper（`Remove-Item`/`rd`/`del`/`rm`/`Set-Content`/`Out-File`/`Add-Content`/`New-Item`）中，检测目标路径是否在 `.git/` 下：

```powershell
function _ZephyrCheckGitDirProtection {
    param([string[]]$Paths)
    foreach ($p in $Paths) {
        if ($p) {
            # v1.6.0 修正：PS 5.1 不支持 ?. 运算符
            $_resolvedPath = Resolve-Path $p -ErrorAction SilentlyContinue
            $resolved = if ($_resolvedPath) { $_resolvedPath.Path } else { $null }
            if ($resolved -and $resolved -match '[\\/]\.git[\\/]' -or $resolved -match '[\\/]\.git$') {
                Write-Host "[SAFE] HARDBLOCKED: 写入 .git 目录 — $resolved" -ForegroundColor Red
                Write-Host "  参考 Zed 1.14.2：.git 写入永久阻断，即使显式批准也不可解锁（防 history tampering）" -ForegroundColor Yellow
                _ZephyrAuditLog -Command "write to $resolved" -Action 'HARDBLOCKED' -Reason '.git 目录写入永久阻断（Zed 1.14.2 设计）'
                return $false
            }
        }
    }
    return $true
}
```

**放行例外**：
- `git` 命令本身（git add/commit/push 等内部写 `.git` 是合法的）——只拦截 PowerShell 原生文件写入
- `.git/hooks/post-checkout` 等 hook 文件的**用户授权修改**——通过逃生通道 `& $_realSetContent ...`

**与 §4.1 #19 immutable_core.yaml 的关系**：immutable_core.yaml 是 commit 时检查（配置层），本算法是运行时拦截（执行层）。两层叠加。

#### 7.17.3 验证

| 测试 | 预期结果 |
|---|---|
| `$home = "test"` | BLOCKED，提示用 `$_myHome` |
| `Remove-Item -Recurse -Force .git/` | HARDBLOCKED（.git 写入永久阻断） |
| `Set-Content .git\config "..."` | HARDBLOCKED |
| `git commit -m "test"` | 放行（git 命令不触发 .git 保护） |
| `$_myHome = "test"` | 放行（非自动变量名） |

### 7.18 施工项 18：Shell 反混淆归一化层（L10，P0，v1.5.0 新增）

> **⚠️ v2.1.0 DEPRECATED**：9 策略全是防 adversarial shell 注入——相邻引号拼接/ANSI-C quoting/hex 转义/八进制转义/$IFS 展开/Base64 decode/命令替换/反引号/变量展开。单人 AI 协作中 AI 不会写 `rm$IFS-rf$IFS/` 或 `echo "cm0=" | base64 -d | bash` 这种混淆命令，AI 写的命令是直接的、可读的。**§7.1 wrapper 的直接 regex 匹配已够用**。本节内容保留作为决策追溯，不施工。详见 §6.2 + §9。

> **背景**：§3.10.1 GuardFall 证明正则/AST 单层防护不够；§3.10.2 AgentTrust 提出 9 策略反混淆归一化层。现有 §7.1 wrapper 直接用 `$fullArgs -match` 匹配 raw text，5 大绕过类全部失效。

#### 7.18.1 9 策略反混淆归一化算法

```powershell
function _ZephyrDeobfuscate {
    param([string]$Command)
    $normalized = $Command

    # 策略 1: 相邻引号拼接（'r''m' → rm）
    $normalized = $normalized -replace "'+'", ''
    $normalized = $normalized -replace "'([^']*)'`'([^']*)'", '$1$2'

    # 策略 2: ANSI-C quoting（$'rm' → rm）
    $normalized = $normalized -replace "\`$'([^']*)'", '$1'

    # 策略 3: hex 转义（\x72\x6d → rm）
    $normalized = [regex]::Replace($normalized, '\\x([0-9a-fA-F]{2})', {
        param($m) [char][Convert]::ToInt32($m.Groups[1].Value, 16)
    })

    # 策略 4: 八进制转义（\162\155 → rm）
    $normalized = [regex]::Replace($normalized, '\\([0-7]{3})', {
        param($m) [char][Convert]::ToInt32($m.Groups[1].Value, 8)
    })

    # 策略 5: $IFS 展开（rm$IFS-rf$IFS/ → rm -rf /）
    $normalized = $normalized -replace '\$IFS', ' '

    # 策略 6: Base64 decode 检测（echo "cm0gLXJmIC8=" | base64 -d | bash）
    if ($normalized -match 'base64\s+-d|--decode') {
        $normalized = "[BASE64-DECODED] " + $normalized
    }

    # 策略 7: 命令替换（$(echo rm) → rm）——保守处理，标记后由人工评审
    if ($normalized -match '\$\([^)]+\)') {
        $normalized = "[CMD-SUBST] " + $normalized
    }

    # 策略 8: 反引号替换（`rm` → rm）
    $normalized = $normalized -replace '`([^`]+)`', '$1'

    # 策略 9: PowerShell 变量展开检测（$cmd = "rm"; & $cmd）——标记后人工评审
    if ($normalized -match '\&\s*\$\w+') {
        $normalized = "[VAR-INVOKE] " + $normalized
    }

    return $normalized
}
```

#### 7.18.2 集成到 wrapper 函数

```powershell
function git {
    # 反混淆归一化（v1.5.0 新增）
    $normalizedArgs = _ZephyrDeobfuscate -Command ($args -join ' ')

    # 如果归一化后含 [BASE64-DECODED]/[CMD-SUBST]/[VAR-INVOKE] 标记，升级为人工确认
    if ($normalizedArgs -match '^\[(BASE64-DECODED|CMD-SUBST|VAR-INVOKE)\]') {
        Write-Host "[SAFE] BLOCKED: 检测到反混淆标记 — $normalizedArgs" -ForegroundColor Red
        Write-Host "  STOP: 此命令含动态执行模式（base64/命令替换/变量调用），GuardFall 证实可绕过正则匹配" -ForegroundColor Yellow
        Write-Host "  ALTERNATIVE: 用显式命令重写，避免动态执行" -ForegroundColor Yellow
        _ZephyrAuditLog -Command ($args -join ' ') -Action 'BLOCKED' -Reason "反混淆标记：$normalizedArgs"
        return 1
    }

    # 用归一化后的字符串做模式匹配（替代 raw $fullArgs）
    # ... 原 §7.1.1 Part A 逻辑，但用 $normalizedArgs 替代 $fullArgs ...
}
```

#### 7.18.3 裁定

**采用**——P0 优先级。GuardFall 证明 10/11 开源 agent 被绕过，本方案现有正则匹配同样脆弱。9 策略反混淆归一化是 AgentTrust 论文验证的有效算法（0.93 召回率对抗 shell 混淆 payload）。

**限制声明**（参考 claude-code PR #76289 诚实声明）：本归一化是 bash/PowerShell 语法的朴素近似，不检测 process-substitution 或 background `&`。完整 tokenize-then-check（Continue 方案）作为 v2.0.0 远期改进。

### 7.19 施工项 19：SafeFix block+suggest 算法（L12，P1，v1.5.0 新增）

> **⚠️ v2.0.0 DEPRECATED**：AI 提示工程层，过度工程。RULE-GIT-SAFE 规则 + §7.15 错误分类的 `STOP:/ALTERNATIVE:` 格式已足够指导 AI。本节保留作为决策追溯，**不施工**。详见 §6.2 + §9。

> **背景**：§3.10.2 AgentTrust 的 SafeFix 创新——不只阻断，建议更安全替代。减少 AI 循环重试（比纯 block 减少重试，比 trash 更确定）。

#### 7.19.1 SafeFix 规则库

| 危险命令 | SafeFix 替代 | 理由 |
|---|---|---|
| `Remove-Item -Recurse -Force <path>` | `Get-ChildItem <path> -Recurse \| Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} \| Remove-Item` | 只删 30 天前的文件 |
| `git clean -fd` | `git clean -n`（预览）+ 人工确认后 `git stash` | stash 可恢复，clean 不可恢复 |
| `git reset --hard` | `git stash` + `git reset --mixed` | stash 保存修改，--mixed 不覆盖工作区 |
| `git checkout -- <file>` | `git diff <file>`（查看修改）+ 决定是否 stash | 显式查看再决定 |
| `rm -rf /tmp/*` | `find /tmp -mtime +7 -delete` | 只删 7 天前的临时文件 |
| `chmod 777 <path>` | `chmod 755 <path>` | 755 是标准权限，777 是安全隐患 |
| `Remove-Item -Recurse -Force .git/` | `git gc --prune=now` | 用 git 原生命令清理 |

#### 7.19.2 集成到 wrapper 函数

```powershell
function _ZephyrSafeFix {
    param([string]$Command, [string]$Reason)

    $suggestion = switch -Wildcard ($Command) {
        'git clean *' { 'git clean -n（预览）+ 人工确认后 git stash（可恢复）' }
        'git reset --hard*' { 'git stash + git reset --mixed（stash 保存修改）' }
        'git checkout -- *' { 'git diff <file>（查看修改）+ 决定是否 stash' }
        'Remove-Item *-Recurse* -Force*' { 'Get-ChildItem -Recurse | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | Remove-Item（只删旧文件）' }
        'rm -rf /tmp/*' { 'find /tmp -mtime +7 -delete（只删 7 天前）' }
        'chmod 777*' { 'chmod 755（标准权限）' }
        default { $null }
    }

    return $suggestion
}

# 在 wrapper 阻断分支中调用
if ($blocked) {
    $safeFix = _ZephyrSafeFix -Command "git $fullArgs" -Reason $reason
    Write-Host "[GIT-SAFE] BLOCKED: git $fullArgs — $reason" -ForegroundColor Red
    if ($safeFix) {
        Write-Host "  SAFEFIX: $safeFix" -ForegroundColor Green
        _ZephyrAuditLog -Command "git $fullArgs" -Action 'BLOCKED' -Reason $reason -EscapeHint "SAFEFIX: $safeFix"
    } else {
        Write-Host "  如需执行（确认安全后），用完整路径：& '$_realGit' $fullArgs" -ForegroundColor Yellow
        _ZephyrAuditLog -Command "git $fullArgs" -Action 'BLOCKED' -Reason $reason -EscapeHint "& '$_realGit' $fullArgs"
    }
    return 1
}
```

#### 7.19.3 裁定

**采用**——P1 优先级。SafeFix 减少 AI 循环重试（AI 看到 SAFEFIX 后可直接执行替代命令，不需要换写法重试）。规则库从 7 条起步，可扩展。

### 7.20 施工项 20：RiskChain session 级攻击链追踪（L13，P1，v1.5.0 新增）

> **⚠️ v2.0.0 DEPRECATED**：典型 adversarial 防御——追踪 base64 解码/变量调用/命令替换等"绕过"行为。单人 AI 协作中 AI 不会"绕过"自己的安全机制。本节保留作为决策追溯，**不施工**。详见 §6.2 + §9。

> **背景**：§3.10.6 CFD 攻击证明 per-call guardrail 无法防御跨调用拆分攻击（+28pp jailbreak 成功率）；§3.10.3 Codex 事故证明子 agent 破坏性动作不在父任务 UI。§7.16 Circuit Breaker 是 per-command 级别，需升级为 session 级。

#### 7.20.1 RiskChain 数据结构

```powershell
# Session 级 RiskChain 状态（持久化到 ~/.zephyr_audit/riskchain_{session}.jsonl）
$_riskChain = @{
    session_id = $env:ZEPHYR_SESSION_ID
    events = @()  # 有序事件列表
    risk_score = 0
    last_suspicious = $null
}

# 事件类型
# - file_read_sensitive: 读取 .env/.aws/.ssh/config 等敏感文件
# - base64_decode: 执行 base64 解码
# - cmd_subst: 执行命令替换
# - var_invoke: 通过变量调用命令
# - blocked_command: 被阻断的命令
# - file_write_config: 写入 hook/venv/git config/task definition
# - escape_hatch_used: 使用逃生通道
```

#### 7.20.2 可疑链检测规则

| 链模式 | 风险分 | 示例 |
|---|---|---|
| `file_read_sensitive` → `base64_decode` | +30 | 读 .env → base64 编码 |
| `base64_decode` → `escape_hatch_used` | +50 | base64 解码后用逃生通道执行 |
| `file_write_config` → `blocked_command` | +40 | 写 hook config 后尝试危险命令 |
| 3+ `blocked_command` in 60s | +60 | 60 秒内 3+ 次阻断 |
| `cmd_subst` + `var_invoke` in same session | +35 | 命令替换+变量调用组合 |
| `file_read_sensitive` → `escape_hatch_used` | +45 | 读敏感文件后用逃生通道 |

**风险分阈值**：
- ≥ 50：升级为 WARNING，写入审计日志
- ≥ 80：升级为 CIRCUIT-OPEN（强制熔断），即使未达 5 次 blocked 阈值
- ≥ 100：升级为 SESSION-TERMINATE（建议用户终止 session）

#### 7.20.3 实现核心

```powershell
function _ZephyrRiskChainRecord {
    param([string]$EventType, [string]$Detail, [hashtable]$Payload = @{})

    $event = @{
        timestamp = (Get-Date).ToString('o')
        event_type = $EventType
        detail = $Detail
        payload = $Payload
        session = $env:ZEPHYR_SESSION_ID
    }

    $_riskChain.events += $event

    # 计算风险分增量
    $riskDelta = switch ($EventType) {
        'file_read_sensitive' { 10 }
        'base64_decode' { 15 }
        'cmd_subst' { 10 }
        'var_invoke' { 10 }
        'blocked_command' { 5 }
        'file_write_config' { 15 }
        'escape_hatch_used' { 20 }
        default { 0 }
    }

    # 链模式加分
    $recentEvents = $_riskChain.events | Where-Object {
        ([datetime]::now - [datetime]$_.timestamp).TotalSeconds -lt 300
    }
    if ($EventType -eq 'base64_decode' -and ($recentEvents | Where-Object { $_.event_type -eq 'file_read_sensitive' })) {
        $riskDelta += 30
    }
    if ($EventType -eq 'escape_hatch_used' -and ($recentEvents | Where-Object { $_.event_type -eq 'base64_decode' })) {
        $riskDelta += 50
    }
    # ... 其他链模式 ...

    $_riskChain.risk_score += $riskDelta
    $_riskChain.last_suspicious = (Get-Date).ToString('o')

    # 持久化到 JSONL
    $event.risk_score = $_riskChain.risk_score
    $event | ConvertTo-Json -Compress | Add-Content -Path "$env:USERPROFILE\.zephyr_audit\riskchain_$($env:ZEPHYR_SESSION_ID).jsonl"

    # 阈值检查
    if ($_riskChain.risk_score -ge 100) {
        Write-Host "[RISKCHAIN] SESSION-TERMINATE: 风险分 $($_riskChain.risk_score) — 建议用户终止此 session" -ForegroundColor Red
        _ZephyrAuditLog -Command "RISKCHAIN" -Action 'SESSION_TERMINATE' -Reason "风险分 $($_riskChain.risk_score)"
    } elseif ($_riskChain.risk_score -ge 80) {
        Write-Host "[RISKCHAIN] CIRCUIT-OPEN: 风险分 $($_riskChain.risk_score) — 强制熔断" -ForegroundColor Red
        $_circuitState.Status = 'OPEN'
        $_circuitState.OpenedAt = Get-Date
        _ZephyrAuditLog -Command "RISKCHAIN" -Action 'CIRCUIT_OPEN' -Reason "风险分 $($_riskChain.risk_score)"
    } elseif ($_riskChain.risk_score -ge 50) {
        Write-Host "[RISKCHAIN] WARNING: 风险分 $($_riskChain.risk_score) — 可疑行为链" -ForegroundColor Yellow
        _ZephyrAuditLog -Command "RISKCHAIN" -Action 'WARNING' -Reason "风险分 $($_riskChain.risk_score)"
    }
}
```

#### 7.20.4 裁定

**采用**——P1 优先级。CFD 攻击是 2026 年新发现的根本性威胁（+28pp jailbreak），现有 per-command Circuit Breaker 无法防御。RiskChain 是 AgentTrust 论文验证的有效算法。

**限制**：完整 RiskChain 实现需跨工具/跨 session 追踪（CFD 攻击可跨 session 拆分），当前实现仅 session 内追踪。跨 session 追踪作为 v2.0.0 远期改进（需中央 risk_score 服务）。

### 7.21 施工项 21：Risk-tiered fail mode（升级 §7.14，P1，v1.5.0 新增）

> **⚠️ v2.0.0 DEPRECATED**：四级风险分层过度细分。§7.14 fail-open（普通命令出错放行+记录，CRITICAL 命令 fail-closed）两级已足够。本节保留作为决策追溯，**不施工**。详见 §6.2 + §9。

> **背景**：§3.10 Cordum 风险分层矩阵证明全局 fail-open/closed 不如 risk-tiered。§7.14 当前是"非 CRITICAL fail-open，CRITICAL fail-closed"二分法，需升级为四级。

#### 7.21.1 四级风险分层 fail mode

| 风险等级 | 操作类型 | fail 模式 | 理由 | 必需 guardrail |
|---|---|---|---|---|
| 🟢 低风险 | 只读辅助（git status/git log/git diff/Get-ChildItem） | **fail-open + 严格遥测** | 可用性 > 严格阻断 | 速率限制 + fail-open 指标告警 |
| 🟡 中风险 | 内部写入（git add/git commit/New-Item 普通文件） | **fail-closed 默认** | 错误写入导致难逆转的数据漂移 | 事件期间人工 override + 过期 |
| 🟠 高风险 | 危险删除（Remove-Item -Recurse -Force/git clean） | **fail-closed 强制** | 不安全绕过造成不可逆动作 | 审批门 + 幂等 key + 审计事件 |
| 🔴 CRITICAL | 系统级破坏（format/vssadmin/diskpart） | **fail-closed 永久** | 任何情况都不应在 AI 开发中执行 | 无 override |

#### 7.21.2 实现

```powershell
function _ZephyrGetRiskTier {
    param([string]$Command, [string]$Action)

    # 🔴 CRITICAL
    foreach ($pattern in $_criticalBlocks) {
        if ($Command -like "*$pattern*") { return 'CRITICAL' }
    }

    # 🟠 高风险
    if ($Command -match 'Remove-Item.*-Recurse.*-Force' -or
        $Command -match 'git clean.*-f' -or
        $Command -match 'git reset.*--hard' -or
        $Command -match 'rd.*/s' -or
        $Command -match 'rm -rf') {
        return 'HIGH'
    }

    # 🟡 中风险
    if ($Command -match 'git (add|commit|push|merge|rebase)' -or
        $Command -match 'New-Item|Set-Content|Out-File|Add-Content') {
        return 'MEDIUM'
    }

    # 🟢 低风险（默认）
    return 'LOW'
}

function _ZephyrFailMode {
    param([string]$RiskTier, [scriptblock]$Operation, [string]$Command)

    try {
        & $Operation
    } catch {
        $tier = $RiskTier
        if ($tier -eq 'CRITICAL') {
            # fail-closed 永久——CRITICAL 即使 wrapper 出错也阻断
            _ZephyrAuditLog -Command $Command -Action 'FAIL_CLOSED' -Reason "CRITICAL tier wrapper error: $_"
            Write-Host "[SAFE] FAIL_CLOSED: CRITICAL 命令 wrapper 出错，仍阻断" -ForegroundColor Red
            return 1
        } elseif ($tier -eq 'HIGH') {
            # fail-closed 强制——高风险命令 wrapper 出错时阻断
            _ZephyrAuditLog -Command $Command -Action 'FAIL_CLOSED' -Reason "HIGH tier wrapper error: $_"
            Write-Host "[SAFE] FAIL_CLOSED: 高风险命令 wrapper 出错，阻断（用逃生通道确认后执行）" -ForegroundColor Red
            return 1
        } elseif ($tier -eq 'MEDIUM') {
            # fail-closed 默认——中风险命令 wrapper 出错时阻断，但允许逃生通道
            _ZephyrAuditLog -Command $Command -Action 'FAIL_CLOSED' -Reason "MEDIUM tier wrapper error: $_"
            Write-Host "[SAFE] FAIL_CLOSED: 中风险命令 wrapper 出错，阻断（用逃生通道或修复 wrapper）" -ForegroundColor Yellow
            return 1
        } else {
            # 🟢 LOW: fail-open——只读辅助命令 wrapper 出错时放行
            _ZephyrAuditLog -Command $Command -Action 'FAIL_OPEN' -Reason "LOW tier wrapper error: $_"
            & $_realGit @args  # fail-open: 透传
        }
    }
}
```

#### 7.21.3 裁定

**采用**——P1 优先级。升级 §7.14 的二分法为四级风险分层。Cordum 矩阵证明 risk-tiered 优于全局 fail-open/closed。

### 7.22 施工项 22：跨工具/跨 shell 绕过检测（P1，v1.5.0 新增）

> **⚠️ v2.0.0 DEPRECATED**：adversarial 防御——防 AI 切换 shell/工具绕过安全机制。单人 AI 协作中 AI 不会主动"绕过"。本节保留作为决策追溯，**不施工**。详见 §6.2 + §9。

> **背景**：§3.10 hermes-agent #69256 修复建议——AI 被阻断后会换路径/换 shell/换工具绕过。当前 §7.16 Circuit Breaker 不检测此类绕过。

#### 7.22.1 三类绕过检测

| 绕过类型 | 示例 | 检测算法 |
|---|---|---|
| 换路径 | `/tmp/x` → `/var/tmp/x` → `$env:TEMP\x` | canonicalize path（Resolve-Path + ToLower）后比较 |
| 换 shell | `bash -c "rm -rf x"` → `sh -c "rm -rf x"` → `python -c "import os; os.remove('x')"` | normalize command form（提取核心命令+参数） |
| 换工具 | `Bash(rm)` → `Write(script)+Bash(bash script.sh)` → `MCP(execute_script)` | 跨工具 session-level 追踪（需 RiskChain §7.20） |

#### 7.22.2 路径 canonicalize 算法

```powershell
function _ZephyrCanonicalizePath {
    param([string]$Path)
    if (-not $Path) { return '' }
    try {
        # v1.6.0 修正：PS 5.1 不支持 ?. 运算符
        $_resolvedPath = Resolve-Path $Path -ErrorAction SilentlyContinue
        $resolved = if ($_resolvedPath) { $_resolvedPath.Path } else { $Path }
        # 统一为小写、正斜杠、去除 .. 和 .
        $resolved = $resolved -replace '\\', '/'
        $resolved = $resolved.ToLower()
        # 去除相对路径组件
        while ($resolved -match '/\.\./') { $resolved = $resolved -replace '/[^/]+/\.\.', '' }
        $resolved = $resolved -replace '/\./', '/'
        return $resolved
    } catch {
        return $Path.ToLower() -replace '\\', '/'
    }
}

# 在 circuit breaker 中，记录 canonicalize 后的路径
function _ZephyrCheckBypass {
    param([string]$Command, [string[]]$Paths)

    foreach ($p in $Paths) {
        $canonical = _ZephyrCanonicalizePath -Path $p
        # 检查 session 内是否曾对同一 canonical path 阻断过
        $priorBlock = $_riskChain.events | Where-Object {
            $_.event_type -eq 'blocked_command' -and
            $_.payload.canonical_path -eq $canonical
        }
        if ($priorBlock) {
            Write-Host "[SAFE] BYPASS-DETECTED: 路径 $p 与之前阻断的路径 canonical 相同（换路径绕过）" -ForegroundColor Red
            _ZephyrRiskChainRecord -EventType 'bypass_attempt' -Detail "path bypass: $p" -Payload @{ canonical_path = $canonical }
            return $false
        }
    }

    # 检查 shell 切换（bash -c / sh -c / python -c）
    if ($Command -match '(bash|sh|cmd|powershell)\s+(-c|-Command|-command)\s') {
        $shellUsed = $Matches[1]
        $priorShell = $_riskChain.events | Where-Object {
            $_.event_type -eq 'blocked_command' -and
            $_.payload.shell -ne $null
        }
        if ($priorShell -and $priorShell.payload.shell -ne $shellUsed) {
            Write-Host "[SAFE] BYPASS-DETECTED: 换 shell 绕过（$($priorShell.payload.shell) → $shellUsed）" -ForegroundColor Red
            _ZephyrRiskChainRecord -EventType 'bypass_attempt' -Detail "shell bypass: $($priorShell.payload.shell) → $shellUsed"
            return $false
        }
    }

    return $true
}
```

#### 7.22.3 裁定

**采用**——P1 优先级。hermes-agent #69256 真实事故证明 AI 会无限重试（31+ 次）+ 换路径/shell 绕过。当前 Circuit Breaker 只检测"相同命令重试"，不检测"换路径/shell 重试"。

### 7.23 施工项 23：git 专属危险命令阻断列表扩展（L1，P0，v1.6.0 新增）

> **⚠️ v2.1.0 简化（20+→4 命令）**：v1.x 的 20+ 命令中，16+ 是防 adversarial RCE（`config core.hooksPath`/`fsmonitor`/`update-index --cacheinfo`/`notes add`/`hash-object -w`/`apply symlink`/`submodule add`/`init --template=`/`push --receive-pack` 等）——AI 不会主动写 `git config core.hooksPath /tmp/evil`。**v2.1.0 只保留 4 个 AI 易误用命令**：`git filter-branch`（历史重写）/`git filter-repo`（历史重写+force push）/`git reflog expire`（抹除 forensic 证据）/`git gc --prune=now`（物理删除对象）。其余 16+ 命令的阻断规则保留在 §7.23.1 表格中作为决策追溯，但**不施工**——单人 AI 协作无 adversarial RCE 场景。详见 §6.2 + §9。

> **背景**：§3.11.3-3.11.10 发现 20+ 个 git 专属攻击命令未在 §7.1 wrapper 阻断列表中，含 CVE-2026-44244/67326/55607 等真实漏洞链。

#### 7.23.1 新增 git 命令阻断列表

| 命令 | 阻断条件 | 放行条件 | 理由 | CVE/案例 |
|---|---|---|---|---|
| `git config core.hooksPath*` | 任何 `core.hooksPath` 设置/取消 | 无（永远阻断） | hooksPath 重定向 → RCE | CVE-2026-44244/67326 |
| `git config core.fsmonitor*` | 任何 `core.fsmonitor` 设置 | 无 | fsmonitor 触发外部命令执行 | CVE-2026-55607 |
| `git config` 含 CR/LF/NUL | section/option/value 含换行/NUL | 无 | config 注入攻击 | CVE-2026-44244/67326 |
| `git filter-branch` | 任何调用 | 无（永远阻断） | 历史重写，git 官方弃用 | git docs |
| `git filter-repo` | 任何调用 | 无（永远阻断） | 历史重写 + force push | GhostXia/AIRP #104 |
| `git reflog expire` | `--expire=` 或 `--all` | `git reflog show`/`git reflog` 只读 | 抹除 forensic 证据 | aitoolsguidebook |
| `git gc --prune=now` | `--prune=now` 或 `--prune=all` | `git gc` 无 `--prune` | 物理删除 unreachable 对象 | 同上 |
| `git update-index --cacheinfo` | `--cacheinfo` flag | `--chmod`/`--refresh`/`--really-refresh`/`--verbose`/`--quiet` | 绕过 commit gate 直写 index | jwbron/egg #277 |
| `git update-index --index-info` | `--index-info` | 同上 | stdin 批量操纵 index | 同上 |
| `git update-index --info-only` | `--info-only` | 同上 | 无 backing object 创建条目 | 同上 |
| `git update-index --stdin` | `--stdin` | 同上 | stdin 注入 | 同上 |
| `git update-index --assume-unchanged` | `--assume-unchanged` | 同上 | 隐藏变更，merge 数据丢失 | 同上 |
| `git update-index --skip-worktree` | `--skip-worktree` | 同上 | 同上 | 同上 |
| `git notes add`/`append`/`edit` | 写入操作 | `git notes list`/`git notes show` 只读 | 侧信道持久化 + 外泄 | spelunk #344 |
| `git hash-object -w` | `-w` flag | `git hash-object` 无 `-w` | 写恶意 object 入 DB | §3.11 |
| `git apply` 含 mode-120000 | patch 含 symlink 条目 | 无 symlink 的 patch | symlink 重放外泄 | codex-plugin-cc #13 |
| `git submodule add` | 不可信源 | 白名单源 | 写 .git/hooks RCE | dulwich GHSA |
| `git clone --recurse-submodules` | 不可信源 | 白名单源 | 同上 | 同上 |
| `git init --template=` | `--template=` 参数 | 无 `--template` | template 植入 hook | SB2026080540 |
| `git push --receive-pack` | `--receive-pack` flag | 无 | 绕过命令校验 | CVE-2026-54316 |

#### 7.23.2 实现核心

```powershell
# 在 §7.1.1 Part A 的 git() 函数中，扩展阻断规则
function git {
    # ... 反混淆归一化 + 变量碰撞检测 + circuit breaker 检查 ...

    $cmd = if ($args.Count -gt 0) { $args[0] } else { '' }
    $fullArgs = $args -join ' '
    $normalizedArgs = _ZephyrDeobfuscate -Command $fullArgs

    # v1.6.0 新增：git 专属危险命令阻断
    $gitBlocked = $false
    $gitReason = ''

    # git config core.hooksPath / core.fsmonitor / CR/LF 注入
    if ($cmd -eq 'config' -and ($normalizedArgs -match 'core\.hooksPath' -or $normalizedArgs -match 'core\.fsmonitor')) {
        $gitBlocked = $true; $gitReason = 'git config core.hooksPath/fsmonitor 重定向 → RCE（CVE-2026-44244/67326/55607）'
    } elseif ($cmd -eq 'config' -and ($normalizedArgs -match '[\r\n\0]')) {
        $gitBlocked = $true; $gitReason = 'git config 含 CR/LF/NUL → config 注入攻击（CVE-2026-44244/67326）'
    }
    # git filter-branch / filter-repo
    elseif ($cmd -eq 'filter-branch' -or $cmd -eq 'filter-repo') {
        $gitBlocked = $true; $gitReason = "git $cmd 历史重写——不可逆操作"
    }
    # git reflog expire
    elseif ($cmd -eq 'reflog' -and $args.Count -gt 1 -and $args[1] -eq 'expire') {
        $gitBlocked = $true; $gitReason = 'git reflog expire 抹除 forensic 证据'
    }
    # git gc --prune=now
    elseif ($cmd -eq 'gc' -and $normalizedArgs -match '--prune=(now|all)') {
        $gitBlocked = $true; $gitReason = 'git gc --prune=now 物理删除 unreachable 对象'
    }
    # git update-index 危险 flag
    elseif ($cmd -eq 'update-index' -and ($normalizedArgs -match '--cacheinfo|--index-info|--info-only|--stdin|--assume-unchanged|--skip-worktree')) {
        $gitBlocked = $true; $gitReason = 'git update-index 危险 flag 绕过 commit gate（jwbron/egg #277）'
    }
    # git notes 写入
    elseif ($cmd -eq 'notes' -and $args.Count -gt 1 -and $args[1] -in @('add','append','edit')) {
        $gitBlocked = $true; $gitReason = 'git notes 侧信道持久化 + 外泄（spelunk #344）'
    }
    # git hash-object -w
    elseif ($cmd -eq 'hash-object' -and $normalizedArgs -match '-w') {
        $gitBlocked = $true; $gitReason = 'git hash-object -w 写恶意 object 入 DB'
    }
    # git apply 含 symlink（mode-120000）——需扫描 patch 文件
    elseif ($cmd -eq 'apply' -and $normalizedArgs -match '120000') {
        $gitBlocked = $true; $gitReason = 'git apply 含 symlink mode-120000 重放攻击（codex-plugin-cc #13）'
    }
    # git submodule add / clone --recurse-submodules（不可信源）
    elseif ($cmd -eq 'submodule' -and $args.Count -gt 1 -and $args[1] -eq 'add') {
        $gitBlocked = $true; $gitReason = 'git submodule add 路径穿越写 .git/hooks RCE（dulwich GHSA）'
    }
    elseif ($cmd -eq 'clone' -and $normalizedArgs -match '--recurse-submodules') {
        $gitBlocked = $true; $gitReason = 'git clone --recurse-submodules 不可信源 RCE（dulwich GHSA）'
    }
    # git init --template=
    elseif ($cmd -eq 'init' -and $normalizedArgs -match '--template=') {
        $gitBlocked = $true; $gitReason = 'git init --template= 植入 hook（SB2026080540）'
    }
    # git push --receive-pack
    elseif ($cmd -eq 'push' -and $normalizedArgs -match '--receive-pack') {
        $gitBlocked = $true; $gitReason = 'git push --receive-pack 绕过命令校验（CVE-2026-54316）'
    }

    if ($gitBlocked) {
        _ZephyrCircuitRecordBlock
        $safeFix = _ZephyrSafeFix -Command "git $fullArgs" -Reason $gitReason
        Write-Host "[GIT-SAFE] BLOCKED: git $fullArgs — $gitReason" -ForegroundColor Red
        if ($safeFix) { Write-Host "  SAFEFIX: $safeFix" -ForegroundColor Green }
        _ZephyrAuditLog -Command "git $fullArgs" -Action 'BLOCKED' -Reason $gitReason
        _ZephyrRiskChainRecord -EventType 'blocked_command' -Detail "git $fullArgs"
        return 1
    }

    # ... 原 §7.1.1 Part A 阻断逻辑 ...
    # ... 透传给真实 git ...
}
```

#### 7.23.3 git log 强制 --no-notes

```powershell
# 在 git() 函数中，对 git log 命令强制添加 --no-notes
if ($cmd -eq 'log' -and $normalizedArgs -notmatch '--no-notes') {
    $args += '--no-notes'
    Write-Host "[GIT-SAFE] 自动添加 --no-notes：隔离 git notes 中的 prompt-injection（spelunk #344）" -ForegroundColor Cyan
}
```

#### 7.23.4 裁定

**采用**——P0 优先级。20+ 个 git 专属攻击命令含 6 个真实 CVE（2026-05~08），现有 §7.1 阻断列表完全不覆盖。这是 v1.6.0 最关键的安全补丁。

### 7.24 施工项 24：symlink/junction + TOCTOU 防护（L14，P1，v1.6.0 新增）

> **⚠️ v2.0.0 DEPRECATED**：adversarial 防御——防 AI 用 symlink/junction 攻击自己。单人 AI 协作中 AI 不会发动 symlink 攻击。P/Invoke CreateFile 实现复杂度高且 PS 5.1 兼容性存疑。本节保留作为决策追溯，**不施工**。详见 §6.2 + §9。

> **背景**：§3.11.13 发现 wrapper 的 `Test-Path` + `Remove-Item` 模式是结构性缺陷——`mklink /J`（目录 junction）不需要任何特权，可在 wrapper 检查后替换路径。

#### 7.24.1 Atomic Path Resolution 算法

```powershell
# v1.6.0 新增：Atomic Path Resolution——P/Invoke CreateFile + FILE_FLAG_OPEN_REPARSE_POINT
# 在 PS 5.1 中通过 Add-Type 内联 C# P/Invoke 实现

$_atomicPathCode = @"
using System;
using System.Runtime.InteropServices;

public static class AtomicPath {
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    public static extern IntPtr CreateFile(
        string lpFileName, uint dwDesiredAccess, uint dwShareMode,
        IntPtr lpSecurityAttributes, uint dwCreationDisposition,
        uint dwFlagsAndAttributes, IntPtr hTemplateFile);

    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern bool GetFileInformationByHandleEx(
        IntPtr hFile, int FileInformationClass, IntPtr lpFileInformation, uint dwBufferSize);

    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern bool GetFinalPathNameByHandle(
        IntPtr hFile, System.Text.StringBuilder lpszFilePath, uint cchFilePath, uint dwFlags);

    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool CloseHandle(IntPtr hObject);

    public const uint GENERIC_READ = 0x80000000;
    public const uint FILE_SHARE_READ = 0x00000001;
    public const uint OPEN_EXISTING = 3;
    public const uint FILE_FLAG_BACKUP_SEMANTICS = 0x02000000;
    public const uint FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000;
    public const int FileAttributeTagInfo = 16;
}
"@
Add-Type -TypeDefinition $_atomicPathCode -ErrorAction SilentlyContinue

function _ZephyrAtomicResolvePath {
    param([string]$Path)
    # 1. 用 CreateFile 原子打开并不跟随 reparse point
    $handle = [AtomicPath]::CreateFile(
        $Path,
        [AtomicPath]::GENERIC_READ,
        [AtomicPath]::FILE_SHARE_READ,
        [IntPtr]::Zero,
        [AtomicPath]::OPEN_EXISTING,
        [AtomicPath]::FILE_FLAG_BACKUP_SEMANTICS -bor [AtomicPath]::FILE_FLAG_OPEN_REPARSE_POINT,
        [IntPtr]::Zero
    )
    if ($handle -eq [IntPtr]::new(-1)) {
        # 打开失败——路径不存在或无权限
        return $null
    }
    try {
        # 2. 检查是否 reparse point（symlink/junction）
        $buffer = [IntPtr]::Zero
        $buffer = [Marshal]::AllocHGlobal(8)
        try {
            $isReparse = [AtomicPath]::GetFileInformationByHandleEx(
                $handle, [AtomicPath]::FileAttributeTagInfo, $buffer, 8)
            if ($isReparse) {
                # 是 reparse point——拒绝（fail-closed）
                return $null
            }
        } finally {
            [Marshal]::FreeHGlobal($buffer)
        }

        # 3. 获取真实路径（GetFinalPathNameByHandle）
        $sb = New-Object System.Text.StringBuilder(260)
        [AtomicPath]::GetFinalPathNameByHandle($handle, $sb, 260, 0) | Out-Null
        return $sb.ToString()
    } finally {
        [AtomicPath]::CloseHandle($handle) | Out-Null
    }
}
```

#### 7.24.2 集成到 wrapper

```powershell
# 在所有路径检查中，用 _ZephyrAtomicResolvePath 替代 Resolve-Path
# 例如 §7.17.2 .git 目录保护：
function _ZephyrCheckGitDirProtection {
    param([string[]]$Paths)
    foreach ($p in $Paths) {
        if ($p) {
            # v1.6.0：用 Atomic Path Resolution 替代 Resolve-Path（防 symlink/TOCTOU）
            $resolved = _ZephyrAtomicResolvePath -Path $p
            if (-not $resolved) {
                # reparse point 或路径不存在——fail-closed
                Write-Host "[SAFE] BLOCKED: 路径 $p 是 reparse point 或不存在（symlink/junction 攻击防护）" -ForegroundColor Red
                _ZephyrAuditLog -Command "write to $p" -Action 'BLOCKED' -Reason 'reparse point 或路径不存在（symlink 防护）'
                return $false
            }
            if ($resolved -match '[\\/]\.git[\\/]' -or $resolved -match '[\\/]\.git$') {
                Write-Host "[SAFE] HARDBLOCKED: 写入 .git 目录 — $resolved" -ForegroundColor Red
                _ZephyrAuditLog -Command "write to $resolved" -Action 'HARDBLOCKED' -Reason '.git 目录写入永久阻断'
                return $false
            }
        }
    }
    return $true
}
```

#### 7.24.3 裁定

**采用**——P1 优先级。symlink/junction + TOCTOU 是 wrapper 的结构性缺陷，CVE-2026-23988 证实可利用。Atomic Path Resolution 是 2026-08 研究发现的唯一正确架构（P/Invoke CreateFile + FILE_FLAG_OPEN_REPARSE_POINT + handle 保留）。

**限制**：`Add-Type -TypeDefinition` 在 CLM 下被阻断——若未来启用 CLM，需用 WDAC 签名规则白名单 wrapper 模块。

### 7.25 施工项 25：git hook 信任链加固 + worktree 安全 + reflog 不可变窗口（L15，P1，v1.6.0 新增）

> **⚠️ v2.0.0 DEPRECATED**：adversarial 防御——防恶意修改 git hook / reflog。单人单账户项目无恶意 actor，且 hooksPath 白名单 + hash 锁定维护成本高。本节保留作为决策追溯，**不施工**。详见 §6.2 + §9。

> **背景**：§3.11.3 CVE-2026-44244/67326 证明 git hook 信任链是 2026 年最活跃攻击面；§3.11.4 CVE-2026-55607 证明 worktree 沙箱逃逸；§3.11.6 reflog expire 抹除 forensic 证据。

#### 7.25.1 hooksPath 白名单 + hash 锁定

```powershell
# 每次 git 操作前校验 core.hooksPath
function _ZephyrCheckHooksPath {
    # 读取 .git/config 中的 core.hooksPath
    $hooksPath = & $_realGit config --get core.hooksPath 2>$null
    if ($hooksPath) {
        # 校验 hooksPath 是否在白名单
        $allowed = @('.git/hooks', "$PSScriptRoot\hooks")  # 白名单
        $isAllowed = $false
        foreach ($a in $allowed) {
            $resolvedAllowed = _ZephyrAtomicResolvePath -Path $a
            $resolvedHooks = _ZephyrAtomicResolvePath -Path $hooksPath
            if ($resolvedHooks -and $resolvedAllowed -and $resolvedHooks -eq $resolvedAllowed) {
                $isAllowed = $true; break
            }
        }
        if (-not $isAllowed) {
            Write-Host "[SAFE] BLOCKED: core.hooksPath 指向非白名单目录 $hooksPath（CVE-2026-44244/67326）" -ForegroundColor Red
            _ZephyrAuditLog -Command "git with hooksPath=$hooksPath" -Action 'BLOCKED' -Reason 'hooksPath 非白名单'
            return $false
        }

        # 校验 hook 文件 SHA256 hash
        $hashFile = Join-Path $hooksPath '.hook_hashes'
        if (Test-Path $hashFile) {
            $expectedHashes = Get-Content $hashFile | ConvertFrom-Json
            foreach ($hookFile in Get-ChildItem $hooksPath -File) {
                if ($hookFile.Name -eq '.hook_hashes') { continue }
                $actualHash = (Get-FileHash $hookFile.FullName -Algorithm SHA256).Hash
                $expected = $expectedHashes.$($hookFile.Name)
                if ($expected -and $actualHash -ne $expected) {
                    Write-Host "[SAFE] BLOCKED: hook $($hookFile.Name) hash 不匹配（被篡改）" -ForegroundColor Red
                    _ZephyrAuditLog -Command "hook $($hookFile.Name)" -Action 'BLOCKED' -Reason 'hook hash 不匹配（篡改检测）'
                    return $false
                }
            }
        }
    }
    return $true
}
```

#### 7.25.2 worktree 安全加固

```powershell
# 在 git worktree add 前校验
function _ZephyrCheckWorktreeSafety {
    param([string[]]$Args)
    if ($Args.Count -lt 2 -or $Args[0] -ne 'add') { return $true }

    $worktreeName = $Args[1]

    # 拒绝 worktree 名为 .git（CVE-2026-55607）
    if ($worktreeName -eq '.git' -or $worktreeName -match '\.git[\\/]') {
        Write-Host "[SAFE] BLOCKED: worktree 名含 .git — gitdir 混淆沙箱逃逸（CVE-2026-55607）" -ForegroundColor Red
        _ZephyrAuditLog -Command "git worktree add $worktreeName" -Action 'BLOCKED' -Reason 'worktree 名含 .git（CVE-2026-55607）'
        return $false
    }

    # 拒绝路径穿越
    if ($worktreeName -match '\.\.' -or $worktreeName -match '^[\\/]') {
        Write-Host "[SAFE] BLOCKED: worktree 名含路径穿越" -ForegroundColor Red
        _ZephyrAuditLog -Command "git worktree add $worktreeName" -Action 'BLOCKED' -Reason 'worktree 名含路径穿越'
        return $false
    }

    # 强制禁用 fsmonitor（CVE-2026-55607 攻击链关键环节）
    & $_realGit config core.fsmonitor none 2>$null

    # 校验主 .git realpath 不在 home/ssh/config 路径下
    $gitDir = & $_realGit rev-parse --git-dir 2>$null
    if ($gitDir) {
        $resolvedGitDir = _ZephyrAtomicResolvePath -Path $gitDir
        if ($resolvedGitDir -and ($resolvedGitDir -match '[\\/]\.ssh[\\/]' -or
            $resolvedGitDir -match '[\\/]\.config[\\/]' -or
            $resolvedGitDir -match '\.aws')) {
            Write-Host "[SAFE] BLOCKED: .git 目录在敏感路径 $resolvedGitDir" -ForegroundColor Red
            _ZephyrAuditLog -Command "git worktree add" -Action 'BLOCKED' -Reason ".git 在敏感路径 $resolvedGitDir"
            return $false
        }
    }

    return $true
}
```

#### 7.25.3 reflog 不可变窗口

```powershell
# 在 git reflog expire / git gc --prune 前强制落盘外部审计
function _ZephyrCheckReflogImmutable {
    param([string[]]$Args)
    $cmd = $Args[0]
    $fullArgs = $Args -join ' '

    if ($cmd -eq 'reflog' -and $Args.Count -gt 1 -and $Args[1] -eq 'expire') {
        # 强制先落盘 reflog 到外部审计目录
        $auditDir = Join-Path $env:USERPROFILE '.zephyr_audit\reflog_snapshots'
        if (-not (Test-Path $auditDir)) { New-Item -ItemType Directory -Path $auditDir -Force | Out-Null }
        $snapshotFile = Join-Path $auditDir "reflog_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
        & $_realGit reflog show --all > $snapshotFile 2>$null
        Write-Host "[SAFE] reflog 快照已落盘：$snapshotFile（reflog 不可变窗口）" -ForegroundColor Cyan
        _ZephyrAuditLog -Command "git reflog expire" -Action 'REFLOG_SNAPSHOT' -Reason "快照落盘 $snapshotFile"
    }

    if ($cmd -eq 'gc' -and $fullArgs -match '--prune=(now|all)') {
        # 同上——gc --prune 前也强制落盘
        $auditDir = Join-Path $env:USERPROFILE '.zephyr_audit\reflog_snapshots'
        if (-not (Test-Path $auditDir)) { New-Item -ItemType Directory -Path $auditDir -Force | Out-Null }
        $snapshotFile = Join-Path $auditDir "reflog_before_gc_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
        & $_realGit reflog show --all > $snapshotFile 2>$null
        Write-Host "[SAFE] reflog 快照已落盘：$snapshotFile（gc --prune 不可变窗口）" -ForegroundColor Cyan
        _ZephyrAuditLog -Command "git gc --prune" -Action 'REFLOG_SNAPSHOT' -Reason "快照落盘 $snapshotFile"
    }

    return $true
}
```

#### 7.25.4 裁定

**采用**——P1 优先级。CVE-2026-44244/67326/55607 是 2026-05~08 最活跃的 git 专属攻击面，现有方案完全不覆盖 hook 信任链、worktree 安全、reflog 不可变性。

### 7.26 施工项 26：Script Block Logging 4104 集成（L16，P2，v1.6.0 新增）

> **⚠️ v2.0.0 DEPRECATED**：企业级 Windows 事件日志方案，个人项目过重。4104 通道扩到 1GB + evtxparser 影响主机 IO。§7.10 JSONL 审计日志已足够追溯。本节保留作为决策追溯，**不施工**。详见 §6.2 + §9。

> **背景**：§3.11.12 发现 4104 事件是"最接近 EDR 的平台原生能力"，与 §7.10 `_ZephyrAuditLog` JSONL 互补。

#### 7.26.1 启用 Script Block Logging

```powershell
# 在 install_git_safety_wrapper.ps1 中加入
function Enable-ScriptBlockLogging {
    $regPath = 'HKLM:\Software\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging'
    if (-not (Test-Path $regPath)) { New-Item -Path $regPath -Force | Out-Null }
    Set-ItemProperty -Path $regPath -Name 'EnableScriptBlockLogging' -Value 1 -Type DWord

    # 扩展通道到 1GB（默认 15MB 在繁忙主机上不到 1 小时滚动覆盖）
    & wevtutil sl 'Microsoft-Windows-PowerShell/Operational' /ms:1073741824

    Write-Host "[SAFE] Script Block Logging 已启用（4104 事件），通道扩展到 1GB" -ForegroundColor Green
}
```

#### 7.26.2 4104 EventRecordId 绑定

```powershell
# 在 _ZephyrAuditLog 中附加 4104 EventRecordId
function _ZephyrAuditLog {
    param([string]$Command, [string]$Action, [string]$Reason, [string]$EscapeHint = '')

    # v1.6.0 新增：获取当前 4104 事件 RecordId
    $psEvent = Get-WinEvent -LogName 'Microsoft-Windows-PowerShell/Operational' -MaxEvents 1 -ErrorAction SilentlyContinue
    $eventRecordId = if ($psEvent) { $psEvent.RecordId } else { $null }

    $_entry = @{
        timestamp = (Get-Date).ToString('o')
        action    = $Action
        command   = $Command
        reason    = $Reason
        session   = $env:ZEPHYR_SESSION_ID
        pid       = $PID
        ps_event_record_id = $eventRecordId  # v1.6.0 新增
        ps_event_id = 4104                    # v1.6.0 新增
        machine   = $env:COMPUTERNAME          # v1.6.0 新增
    }
    if ($EscapeHint) { $_entry.escape_hint = $EscapeHint }
    $_entry | ConvertTo-Json -Compress | Add-Content -Path $_logFile -Encoding UTF8
}
```

#### 7.26.3 裁定

**采用**——P2 优先级。4104 是引擎级审计，_ZephyrAuditLog 是应用级审计，双向追溯能力是防御深度的关键补充。

### 7.27 施工项 27：审计日志并发安全修复（L17，P0，v1.7.0 新增）

> **⚠️ v2.1.0 简化（Mutex→每 session 独立文件）**：v1.x 用命名 Mutex（`Global\ZephyrAuditLogMutex`）串行化 StreamWriter——这是为"多进程并发写同一文件"设计。但审计日志是 append-only 事后追溯，不是关键状态。Claude Code `.claude.json` 423 次损坏是状态文件（read-modify-write），不是 append-only 日志。**v2.1.0 改为每 session 独立文件 `audit_{yyyyMMdd}_{sessionId}.jsonl`**（§3.12.4 算法 D），无需 Mutex，离线合并。append-only 并发损坏概率远低于状态文件。§7.10 审计日志设施（JSONL）保留，仅并发安全实现简化。详见 §6.2 + §9。

> **背景**：§3.12.1 发现 `_ZephyrAuditLog` 的 `Add-Content` 在 26 session 并发写同一 `audit_{yyyyMMdd}.jsonl` 时**必然数据交错/丢失**（PowerShell #24774 证实）。§3.12.2 Claude Code `.claude.json` 423 次损坏是同类 bug 的决定性证据。

#### 7.27.1 命名 Mutex + 原子写算法

```powershell
# v1.7.0 修复：用命名 Mutex 串行化 Add-Content + temp+rename 原子写
function _ZephyrAuditLog {
    param([string]$Command, [string]$Action, [string]$Reason, [string]$EscapeHint = '')

    $_logDir = Join-Path $env:USERPROFILE '.zephyr_audit'
    if (-not (Test-Path $_logDir)) { New-Item -ItemType Directory -Path $_logDir -Force | Out-Null }
    $_logFile = Join-Path $_logDir ("audit_{0:yyyyMMdd}.jsonl" -f (Get-Date))

    # v1.6.0: 获取 4104 EventRecordId
    $psEvent = Get-WinEvent -LogName 'Microsoft-Windows-PowerShell/Operational' -MaxEvents 1 -ErrorAction SilentlyContinue
    $eventRecordId = if ($psEvent) { $psEvent.RecordId } else { $null }

    $_entry = @{
        timestamp = (Get-Date).ToString('o')
        action    = $Action
        command   = $Command
        reason    = $Reason
        session   = $env:ZEPHYR_SESSION_ID
        pid       = $PID
        ps_event_record_id = $eventRecordId
        ps_event_id = 4104
        machine   = $env:COMPUTERNAME
    }
    if ($EscapeHint) { $_entry.escape_hint = $EscapeHint }
    $jsonLine = $_entry | ConvertTo-Json -Compress

    # v1.7.0 关键修复：命名 Mutex 串行化并发 append
    $mutexName = 'Global\ZephyrAuditLogMutex'
    $mutex = New-Object System.Threading.Mutex($false, $mutexName)
    $acquired = $false
    try {
        $acquired = $mutex.WaitOne(5000)  # 5 秒 timeout，防死等
        if ($acquired) {
            # 原子 append：用 StreamWriter + FileShare.ReadWrite（比 Add-Content 更可靠）
            $stream = [System.IO.StreamWriter]::new($_logFile, $true, [System.Text.Encoding]::UTF8, 8192)
            try {
                $stream.WriteLine($jsonLine)
                $stream.Flush()
            } finally {
                $stream.Close()
            }
        } else {
            # Mutex timeout——降级为每 session 独立文件（防数据丢失）
            $fallbackFile = Join-Path $_logDir ("audit_{0:yyyyMMdd}_{1}.jsonl" -f (Get-Date), $env:ZEPHYR_SESSION_ID)
            $jsonLine | Out-File -FilePath $fallbackFile -Append -Encoding UTF8
            Write-Host "[SAFE] AUDIT LOG Mutex timeout——降级到 session 独立文件 $fallbackFile" -ForegroundColor Yellow
        }
    } finally {
        if ($acquired) { $mutex.ReleaseMutex() }
        $mutex.Dispose()
    }
}
```

#### 7.27.2 裁定

**采用**——P0 优先级。这是 v1.7.0 最关键的并发安全修复。PowerShell #24774 证实 `Add-Content` 并发不安全，Claude Code `.claude.json` 423 次损坏是决定性前车之鉴。命名 Mutex（`Global\` 前缀）+ StreamWriter 是 PS 5.1 兼容的最佳实践。

### 7.28 施工项 28：lock_files.py registry.json 并发安全升级（L17，P0，v1.7.0 新增）

> **⚠️ v2.0.0 部分保留**：§7.28.1 方案选型 + §7.28.2 过渡方案（registry.json + 命名 Mutex）**保留施工**——这是 22 session 并发写 registry.json 的必需修复。§7.28.3 最终方案（迁移到 SQLite）**deprecated**——§11.3.3 Task Board 已用 SQLite，lock_files.py 保留 JSON+Mutex 即可，无需重复迁移。详见 §6.2 + §9。

> **背景**：§3.12.1 发现 `lock_files.py` 的 `registry.json` 在 26 session 并发 read-modify-write 时**必然丢锁/双锁**。§3.10.8 grite C2 已证实 file-based tracker 静默丢失并发写。

#### 7.28.1 方案选型

| 方案 | 机制 | PS 5.1 | 裁定 |
|---|---|---|---|
| A. registry.json + 命名 Mutex | Mutex 串行化 RMW | ✅ | ✅ **采用（过渡方案）** |
| B. 迁移到 SQLite | 与 §11.3.3 Task Board 统一 | ✅ | ✅ **采用（最终方案）** |
| C. 迁移到 .ailocks/ 文件锁 | 每个 lock 一个文件（O_CREAT\|O_EXCL 原子创建） | ✅ | ❌ 不采用（文件数膨胀） |

#### 7.28.2 过渡方案：registry.json + 命名 Mutex

```python
# scripts/lock_files.py v2.1.0 新增：Mutex 串行化 registry.json RMW
import threading
import ctypes
import json
from pathlib import Path

def _acquire_global_mutex(name: str, timeout_ms: int = 5000) -> ctypes.c_void_p:
    """Windows 全局命名 Mutex——跨进程互斥"""
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, name)
    result = ctypes.windll.kernel32.WaitForSingleObject(mutex, timeout_ms)
    if result in (0, 0x80):  # WAIT_OBJECT_0 or WAIT_ABANDONED
        return mutex
    ctypes.windll.kernel32.CloseHandle(mutex)
    return None

def _release_global_mutex(mutex: ctypes.c_void_p):
    ctypes.windll.kernel32.ReleaseMutex(mutex)
    ctypes.windll.kernel32.CloseHandle(mutex)

def acquire(file_path: str, session_id: str, ttl: int = 60, task_id: str = None):
    """v1.7.0: 用全局 Mutex 串行化 registry.json read-modify-write"""
    mutex = _acquire_global_mutex('Global\\ZephyrLockFilesRegistry')
    if not mutex:
        return {'status': 'DENIED', 'reason': 'Mutex timeout'}
    try:
        # 临界区：read registry.json → check lock → write registry.json
        registry = _load_registry()  # 原子读
        if file_path in registry:
            existing = registry[file_path]
            if not _is_expired(existing):
                return {'status': 'DENIED', 'reason': f'locked by {existing["session_id"]}'}
        # 写入新锁
        registry[file_path] = {
            'session_id': session_id,
            'acquired_at': datetime.utcnow().isoformat(),
            'ttl_minutes': ttl,
            'expires_at': (datetime.utcnow() + timedelta(minutes=ttl)).isoformat(),
            'task_id': task_id
        }
        _save_registry_atomic(registry)  # temp + rename 原子写
        return {'status': 'ACQUIRED'}
    finally:
        _release_global_mutex(mutex)

def _save_registry_atomic(registry: dict):
    """v1.7.0: temp + rename 原子写（防崩溃半成品）"""
    registry_path = Path('.ailocks/registry.json')
    tmp_path = registry_path.with_suffix('.tmp')
    # 写临时文件
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    # 原子 rename（Windows MoveFileExW 带 MOVEFILE_REPLACE_EXISTING）
    tmp_path.replace(registry_path)  # pathlib.Path.replace = os.replace = 原子
```

#### 7.28.3 最终方案：迁移到 SQLite

将 `registry.json` 迁移到 `.ailocks/locks.db`（SQLite WAL 模式），与 §11.3.3 Task Board 统一。CAS 单语句原子 claim：

```sql
-- 原子 claim：INSERT OR REPLACE + WHERE 条件
INSERT INTO locks (file_path, session_id, acquired_at, expires_at, task_id, epoch)
VALUES (?, ?, datetime('now'), datetime('now', '+60 minutes'), ?, 1)
ON CONFLICT(file_path) DO UPDATE SET
    session_id = excluded.session_id,
    acquired_at = datetime('now'),
    expires_at = datetime('now', '+60 minutes'),
    epoch = epoch + 1
WHERE locks.expires_at < datetime('now') OR locks.session_id = ?;
-- 若 changes() > 0 则 claim 成功
```

#### 7.28.4 裁定

**采用**——P0 优先级。过渡方案（Mutex + 原子写）立即修复并发 bug；最终方案（SQLite）与 §11.3.3 统一并获 grite C2 验证。

### 7.29 施工项 29：跨 session GovernanceStore（L18，P1，v1.7.0 新增）

> **⚠️ v2.0.0 DEPRECATED**：与 §11.3.3 Task Board SQLite 重复——Task Board 已是跨 session 协调层（claim/complete/block 状态机 + SQLite CAS）。另建 GovernanceStore 是重复造轮子。本节保留作为决策追溯，**不施工**。详见 §6.2 + §9。

> **背景**：§3.12.1 发现 `$_circuitState` 和 `$_riskChain` 仅 per-session——一个 session 熔断后其他 session 不知道。§3.12.5 OpenClaw RFC #27442 提出跨 session GovernanceStore 需求。恶意 AI 可换 session 绕过 circuit breaker。

#### 7.29.1 GovernanceStore 架构

```powershell
# v1.7.0 新增：跨 session GovernanceStore（SQLite）
# 位置：~/.zephyr_audit/governance.db

$_governanceDb = Join-Path $env:USERPROFILE '.zephyr_audit\governance.db'

function _ZephyrGovernanceInit {
    if (-not (Test-Path $_governanceDb)) {
        # 创建 SQLite 数据库 + 表
        $conn = New-Object System.Data.SQLite.SQLiteConnection
        $conn.ConnectionString = "Data Source=$_governanceDb;Version=3;"
        $conn.Open()
        $cmd = $conn.CreateCommand()
        $cmd.CommandText = @'
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS circuit_breakers (
            session_id TEXT PRIMARY KEY,
            status TEXT NOT NULL,           -- CLOSED/OPEN/HALF-OPEN
            blocked_count INTEGER DEFAULT 0,
            last_blocked TIMESTAMP,
            opened_at TIMESTAMP,
            updated_at TIMESTAMP NOT NULL
        );
        CREATE TABLE IF NOT EXISTS risk_chains (
            session_id TEXT,
            event_type TEXT NOT NULL,
            detail TEXT,
            risk_score INTEGER DEFAULT 0,
            timestamp TIMESTAMP NOT NULL,
            payload_json TEXT
        );
        CREATE TABLE IF NOT EXISTS governance_flags (
            flag_name TEXT PRIMARY KEY,     -- global_halt/token_budget_exceeded
            flag_value TEXT NOT NULL,
            set_by TEXT NOT NULL,
            set_at TIMESTAMP NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_risk_chains_session ON risk_chains(session_id);
        CREATE INDEX IF NOT EXISTS idx_risk_chains_timestamp ON risk_chains(timestamp);
        '@
        $cmd.ExecuteNonQuery()
        $conn.Close()
    }
}

function _ZephyrGovernanceCheckGlobal {
    # 检查全局 halt flag（任何 session 可设置，所有 session 遵守）
    $conn = New-Object System.Data.SQLite.SQLiteConnection
    $conn.ConnectionString = "Data Source=$_governanceDb;Version=3;"
    $conn.Open()
    $cmd = $conn.CreateCommand()
    $cmd.CommandText = "SELECT flag_value FROM governance_flags WHERE flag_name = 'global_halt'"
    $result = $cmd.ExecuteScalar()
    $conn.Close()

    if ($result -eq 'true') {
        Write-Host "[GOVERNANCE] GLOBAL HALT: 所有 session 已被 halt——拒绝命令" -ForegroundColor Red
        return $false
    }
    return $true
}

function _ZephyrGovernanceRecordCircuit {
    param([string]$Status, [int]$BlockedCount)

    $conn = New-Object System.Data.SQLite.SQLiteConnection
    $conn.ConnectionString = "Data Source=$_governanceDb;Version=3;"
    $conn.Open()
    $cmd = $conn.CreateCommand()
    # UPSERT（原子写）
    $cmd.CommandText = @"
    INSERT INTO circuit_breakers (session_id, status, blocked_count, last_blocked, opened_at, updated_at)
    VALUES ('$env:ZEPHYR_SESSION_ID', '$Status', $BlockedCount, datetime('now'),
            CASE WHEN '$Status' = 'OPEN' THEN datetime('now') ELSE NULL END, datetime('now'))
    ON CONFLICT(session_id) DO UPDATE SET
        status = excluded.status,
        blocked_count = excluded.blocked_count,
        last_blocked = excluded.last_blocked,
        opened_at = CASE WHEN excluded.status = 'OPEN' THEN datetime('now') ELSE circuit_breakers.opened_at END,
        updated_at = datetime('now');
"@
    $cmd.ExecuteNonQuery()
    $conn.Close()

    # 如果本 session 熔断，检查是否需触发 global halt
    if ($Status -eq 'OPEN') {
        $conn2 = New-Object System.Data.SQLite.SQLiteConnection
        $conn2.ConnectionString = "Data Source=$_governanceDb;Version=3;"
        $conn2.Open()
        $cmd2 = $conn2.CreateCommand()
        # 如果 3+ session 同时 OPEN，触发 global halt
        $cmd2.CommandText = "SELECT COUNT(*) FROM circuit_breakers WHERE status = 'OPEN' AND opened_at > datetime('now', '-2 minutes')"
        $openCount = [int]$cmd2.ExecuteScalar()
        $conn2.Close()

        if ($openCount -ge 3) {
            _ZephyrGovernanceSetFlag 'global_halt' 'true' $env:ZEPHYR_SESSION_ID
            Write-Host "[GOVERNANCE] GLOBAL HALT 触发：$openCount 个 session 同时熔断" -ForegroundColor Red
        }
    }
}

function _ZephyrGovernanceSetFlag {
    param([string]$FlagName, [string]$FlagValue, [string]$SetBy)

    $conn = New-Object System.Data.SQLite.SQLiteConnection
    $conn.ConnectionString = "Data Source=$_governanceDb;Version=3;"
    $conn.Open()
    $cmd = $conn.CreateCommand()
    $cmd.CommandText = @"
    INSERT INTO governance_flags (flag_name, flag_value, set_by, set_at)
    VALUES ('$FlagName', '$FlagValue', '$SetBy', datetime('now'))
    ON CONFLICT(flag_name) DO UPDATE SET
        flag_value = excluded.flag_value,
        set_by = excluded.set_by,
        set_at = datetime('now');
"@
    $cmd.ExecuteNonQuery()
    $conn.Close()
}
```

#### 7.29.2 跨 session circuit breaker 联动

```powershell
# 在 wrapper 函数入口处，检查全局 halt + 跨 session circuit breaker
function git {
    # v1.7.0: 全局 halt 检查
    if (-not (_ZephyrGovernanceCheckGlobal)) { return 1 }

    # v1.7.0: 跨 session circuit breaker 检查
    # 如果其他 session 在 2 分钟内 3+ 次熔断，本 session 也应进入警戒
    # ... 原 per-session circuit breaker 逻辑 ...
    # 阻断时记录到 GovernanceStore（跨 session 可见）
    _ZephyrGovernanceRecordCircuit -Status 'OPEN' -BlockedCount $_circuitState.BlockedCount
}
```

#### 7.29.3 裁定

**采用**——P1 优先级。跨 session 协调是 Trae 多 AI 并发的 L3 治本层。OpenClaw RFC #27442 证实这是行业痛点。3+ session 同时熔断触发 global halt 是合理的自动防护。

### 7.30 施工项 30：共享规则文件完整性防护（L17，P1，v1.7.0 新增）

> **⚠️ v2.0.0 DEPRECATED**：adversarial 防御——防"恶意 session 注入规则"。单人项目无恶意 actor，AGENTS.md/project_rules.md 通过 git 版本控制已足够追溯变更。hash 监控每次 git 命令检查是过度防护。本节保留作为决策追溯，**不施工**。详见 §6.2 + §9。

> **背景**：§3.12.1 发现 `.trae/rules/project_rules.md` 和 `AGENTS.md` 可被任何 session 修改——恶意 session 可注入规则 weakening wrapper 防护。

#### 7.30.1 完整性监控算法

```powershell
# v1.7.0 新增：共享规则文件 hash 监控
$_rulesBaseline = @{
    '.trae/rules/project_rules.md' = $null  # 启动时计算
    'AGENTS.md' = $null
    '.trae/rules/onboarding_detail.md' = $null
}

function _ZephyrInitRulesBaseline {
    foreach ($file in $_rulesBaseline.Keys) {
        if (Test-Path $file) {
            $_rulesBaseline[$file] = (Get-FileHash $file -Algorithm SHA256).Hash
        }
    }
}

function _ZephyrCheckRulesIntegrity {
    foreach ($file in $_rulesBaseline.Keys) {
        if ($_rulesBaseline[$file] -and (Test-Path $file)) {
            $currentHash = (Get-FileHash $file -Algorithm SHA256).Hash
            if ($currentHash -ne $_rulesBaseline[$file]) {
                Write-Host "[SAFE] WARNING: 规则文件 $file 已被修改（hash 不匹配）" -ForegroundColor Yellow
                Write-Host "  基线 hash: $($_rulesBaseline[$file])" -ForegroundColor Cyan
                Write-Host "  当前 hash: $currentHash" -ForegroundColor Cyan
                Write-Host "  如非预期，用 git checkout $file 恢复" -ForegroundColor Yellow
                _ZephyrAuditLog -Command "rules integrity check" -Action 'WARNING' -Reason "$file hash 不匹配（可能被其他 session 修改）"

                # 记录到 RiskChain（规则修改是可疑行为）
                _ZephyrRiskChainRecord -EventType 'file_write_config' -Detail "$file 被修改"
            }
        }
    }
}

# 在每次 git 命令前检查规则完整性
function git {
    _ZephyrCheckRulesIntegrity  # v1.7.0: 规则完整性检查
    # ... 原 wrapper 逻辑 ...
}
```

#### 7.30.2 AGENTS.md Boundaries 声明

在 AGENTS.md 中新增 Boundaries 段：

```markdown
## Boundaries（v1.7.0 新增）

**以下文件 AI session MUST NOT 修改**（除非用户明确授权）：
- `.trae/rules/project_rules.md`
- `.trae/rules/onboarding_detail.md`
- `AGENTS.md`
- `.traeignore`
- `config/immutable_core.yaml`
- `scripts/git_guard.py`
- `scripts/install_git_safety_wrapper.ps1`

修改这些文件会触发 §7.30 完整性告警 + §7.20 RiskChain 风险分增加。
```

#### 7.30.3 裁定

**采用**——P1 优先级。共享规则文件污染是 Trae 多 AI 并发的隐蔽攻击面。hash 监控 + Boundaries 声明 + git 版本控制三层防护。

### 7.31 施工项 31：git 并发操作串行化（L17，P1，v1.7.0 新增）

> **背景**：§3.12.3 f2t.jp 2026-06-12 案例——`git add A B` 后 `git commit`，commit 进去的却是 C D E（另一 session 的 add 覆盖了共享 index）。

#### 7.31.1 git add && git commit 单命令链

```powershell
# v1.7.0 新增：在 git() wrapper 中，检测 add+commit 分离模式并建议合并
function git {
    # ... 原 wrapper 逻辑 ...

    # 检测 git add 后跟 git commit 的模式（需用户/AI 配合）
    # 如果 cmd=add，记录到 session 状态；如果 cmd=commit 且前一个是 add，验证暂存内容
    if ($cmd -eq 'commit') {
        # commit 前验证暂存内容（防另一 session 的 add 污染）
        $staged = & $_realGit diff --cached --stat 2>$null
        if ($staged) {
            Write-Host "[GIT-SAFE] commit 前暂存内容验证：" -ForegroundColor Cyan
            Write-Host $staged
            # 如果暂存内容与预期不符，建议 git reset --mixed（安全）后重新 add+commit
        }
    }

    # 透传给真实 git
    & $_realGit @args
}
```

#### 7.31.2 GIT_OPTIONAL_LOCKS=0 给后台 watcher

```powershell
# v1.7.0 新增：在 $PROFILE 中设置 GIT_OPTIONAL_LOCKS=0
# 防止 watcher 进程（如 IDE 文件监控）的 git status 抢 .git/index.lock
$env:GIT_OPTIONAL_LOCKS = '0'
```

#### 7.31.3 GitCommitGateway single-flight 串行化

```powershell
# v1.7.0 新增：GitCommitGateway 用命名 Mutex 串行化所有 commit
function _ZephyrGitCommitGateway {
    param([scriptblock]$CommitOperation)

    $mutex = New-Object System.Threading.Mutex($false, 'Global\ZephyrGitCommitGateway')
    $acquired = $false
    try {
        $acquired = $mutex.WaitOne(30000)  # 30 秒 timeout（commit 可能耗时）
        if ($acquired) {
            # 临界区：同一时间只有一个 session 能 commit
            return & $CommitOperation
        } else {
            Write-Host "[GIT-SAFE] COMMIT GATEWAY timeout——另一 session 正在 commit" -ForegroundColor Yellow
            _ZephyrAuditLog -Command "git commit" -Action 'GATEWAY_TIMEOUT' -Reason '另一 session 正在 commit'
            return 1
        }
    } finally {
        if ($acquired) { $mutex.ReleaseMutex() }
        $mutex.Dispose()
    }
}
```

#### 7.31.4 裁定

**采用**——P1 优先级。f2t.jp 案例证实多 session 并发 git add+commit 会内容错乱。single-flight commit gateway + `git add && git commit` 单命令 + `GIT_OPTIONAL_LOCKS=0` 三层防护。

### 7.32 施工项 32：Session ID 注入机制（L19，P0，v1.8.0 新增）

> **⚠️ v2.1.0 简化（init-session.ps1+TRAE_ENV_FILE→$PROFILE 一行）**：v1.x 的 Trae SessionStart hook 配置 + init-session.ps1 脚本（从 stdin 读 JSON + 生成 UUID + 写 TRAE_ENV_FILE）机制复杂，且 Trae hook 可行性本身是开放问题（§10 列为"待测试"）。**v2.1.0 简化为 $PROFILE 顶部一行**：`if (-not $env:ZEPHYR_SESSION_ID) { $env:ZEPHYR_SESSION_ID = [guid]::NewGuid().ToString() }`。每 session 启动时自动生成 UUID，足够 Task Board 身份识别。init-session.ps1 + TRAE_ENV_FILE + Trae hook 配置不施工。详见 §6.2 + §9。

> **背景**：§3.13.2 发现 Trae SessionStart hook 可注入环境变量。v1.7.0 的 `$env:ZEPHYR_SESSION_ID` 之前没有注入源——所有跨 session 追踪（GovernanceStore/RiskChain/审计日志）的 session_id 都是空的。

#### 7.32.1 Trae SessionStart Hook 配置

在 `.trae/hooks.json` 中配置：

```json
{
  "version": 1,
  "hooks": {
    "SessionStart": [{
      "matcher": "startup",
      "hooks": [{
        "type": "command",
        "command": "powershell -ExecutionPolicy Bypass -File ./scripts/init-session.ps1",
        "timeout": 30
      }]
    }]
  }
}
```

#### 7.32.2 init-session.ps1 脚本

```powershell
# scripts/init-session.ps1——v1.8.0 新增
# 从 stdin 读取 Trae hook 输入 JSON
$hookInput = $input | Out-String | ConvertFrom-Json
$sessionId = if ($hookInput.session_id) { $hookInput.session_id } else { [guid]::NewGuid().ToString() }
$conversationId = $hookInput.conversation_id

# 生成环境变量文件供 Trae 加载（TRAE_ENV_FILE 机制）
$envFile = Join-Path $env:TEMP "trae-env-$sessionId.env"
@"
ZEPHYR_SESSION_ID=$sessionId
ZEPHYR_CONVERSATION_ID=$conversationId
ZEPHYR_SESSION_START=$([DateTime]::Now.ToString('o'))
ZEPHYR_PROFILE_VERSION=1.8.0
"@ | Out-File -FilePath $envFile -Encoding UTF8

# 输出环境变量文件路径供 Trae 加载
@{
    continue = $true
    hookSpecificOutput = @{
        hookEventName = "SessionStart"
        additionalContext = "Session $sessionId initialized (ZEPHYR_PROFILE_VERSION=1.8.0)"
    }
} | ConvertTo-Json -Compress
```

#### 7.32.3 $PROFILE 顶部 fallback

```powershell
# $PROFILE 顶部——v1.8.0 新增：session ID fallback
if (-not $env:ZEPHYR_SESSION_ID) {
    # 如果 Trae SessionStart hook 未注入（如 hook 未配置或旧版 Trae），fallback 到 UUID
    $env:ZEPHYR_SESSION_ID = [guid]::NewGuid().ToString()
    $env:ZEPHYR_SESSION_START = (Get-Date).ToString('o')
}
```

#### 7.32.4 裁定

**采用**——P0 优先级。Session ID 是所有跨 session 追踪的基础。Trae SessionStart hook `TRAE_ENV_FILE` 机制是官方支持的注入方式（§3.13.2 证实）。fallback 到 `[guid]::NewGuid()` 确保 hook 未配置时仍能工作。

### 7.33 施工项 33：Named Pipe Coordinator Daemon（L19，P0，v1.8.0 新增）

> **⚠️ v2.0.0 DEPRECATED**：重复造轮子 + 单点故障。§11.3.3 Task Board 已用 SQLite WAL + CAS——SQLite 本身就是工业级并发方案，22 session 并发读写完全胜任。Named Pipe daemon 增益仅微秒级（0.1ms→0.05ms），却引入单点故障（v1.x §14 还要单独写灾难恢复）。daemon 实现 200+ 行 PowerShell + PS 5.1 兼容性风险。本节保留作为决策追溯，**不施工**。详见 §6.2 + §9。

> **背景**：§3.13.1 发现 Named Pipe 单线程协调器**优于** v1.7.0 的 Mutex+SQLite——单线程消除并发，而非用锁管理并发。§3.13.6 Hybrid 架构：Named Pipe 实时协调 + SQLite 持久审计。

#### 7.33.1 Daemon 架构

```
Session 1..26 → Named Pipe Client → Coordinator Daemon (单线程) → SQLite WAL (异步审计)
```

**核心原则**：所有共享状态操作（锁/circuit breaker/risk chain/global halt）都通过 named pipe 发送给 daemon，daemon 单线程串行处理——**无并发竞态**。

#### 7.33.2 Daemon 实现（PS 5.1 兼容）

```powershell
# scripts/zephyr_coordinator_daemon.ps1——v1.8.0 新增
# Named Pipe 单线程协调器 daemon

param(
    [string]$PipeName = 'ZephyrCoordinator',
    [string]$ProjectHash = $(try { (Get-FileHash $PWD -Algorithm SHA256).Hash.Substring(0,16) } catch { 'default' })
)

# 用 Global\ Mutex 防双重启动（含项目 hash 防跨项目冲突）
$daemonMutexName = "Global\ZephyrCoordinator.$ProjectHash"
$daemonMutex = New-Object System.Threading.Mutex($false, $daemonMutexName)
if (-not $daemonMutex.WaitOne(0)) {
    Write-Host "[COORDINATOR] 已有 daemon 运行中（Mutex $daemonMutexName 持有）" -ForegroundColor Yellow
    exit 0
}

# 初始化状态（内存中，无并发竞态）
$_locks = @{}           # file_path → {session_id, expires_at, task_id}
$_circuitBreakers = @{} # session_id → {status, blocked_count, last_blocked, opened_at}
$_riskChains = @{}      # session_id → {events, risk_score}
$_globalHalt = $false

# SQLite 审计日志（异步写入，无争用——单线程）
$_auditDb = Join-Path $env:USERPROFILE '.zephyr_audit\governance.db'
# ... SQLite 初始化（WAL 模式 + busy_timeout=5000）...

# Named Pipe Server
$pipe = New-Object System.IO.Pipes.NamedPipeServerStream(
    $PipeName,
    [System.IO.Pipes.PipeDirection]::InOut,
    1,  # maxNumberOfServerInstances
    [System.IO.Pipes.PipeTransmissionMode]::Message,
    [System.IO.Pipes.PipeOptions]::Asynchronous
)

Write-Host "[COORDINATOR] Daemon 启动——pipe=$PipeName project=$ProjectHash" -ForegroundColor Green

# 单线程事件循环
while ($true) {
    # 等待连接（阻塞，单线程串行处理）
    $pipe.WaitForConnection()

    try {
        # 读取请求（JSON）
        $sr = New-Object System.IO.StreamReader($pipe)
        $request = $sr.ReadLine() | ConvertFrom-Json

        # 处理请求（单线程——无并发竞态）
        $response = switch ($request.action) {
            'acquire_lock' {
                $file = $request.file
                $session = $request.session_id
                $ttl = if ($request.ttl) { $request.ttl } else { 60 }

                if ($_locks.ContainsKey($file)) {
                    $existing = $_locks[$file]
                    $expiresAt = [datetime]::Parse($existing.expires_at)
                    if ([datetime]::Now -lt $expiresAt -and $existing.session_id -ne $session) {
                        @{ status = 'DENIED'; reason = "locked by $($existing.session_id)" }
                    } else {
                        $_locks[$file] = @{ session_id = $session; expires_at = ([datetime]::Now.AddMinutes($ttl)).ToString('o') }
                        @{ status = 'ACQUIRED' }
                    }
                } else {
                    $_locks[$file] = @{ session_id = $session; expires_at = ([datetime]::Now.AddMinutes($ttl)).ToString('o') }
                    @{ status = 'ACQUIRED' }
                }
            }
            'release_lock' {
                $file = $request.file
                $session = $request.session_id
                if ($_locks.ContainsKey($file) -and $_locks[$file].session_id -eq $session) {
                    $_locks.Remove($file)
                    @{ status = 'RELEASED' }
                } else {
                    @{ status = 'DENIED'; reason = 'not locked by this session' }
                }
            }
            'check_circuit' {
                $session = $request.session_id
                if ($_globalHalt) {
                    @{ status = 'GLOBAL_HALT'; reason = '所有 session 已被 halt' }
                } elseif ($_circuitBreakers.ContainsKey($session) -and $_circuitBreakers[$session].status -eq 'OPEN') {
                    $cb = $_circuitBreakers[$session]
                    $elapsed = ([datetime]::Now - [datetime]::Parse($cb.opened_at)).TotalSeconds
                    if ($elapsed -ge 60) {
                        $_circuitBreakers[$session].status = 'HALF-OPEN'
                        @{ status = 'HALF-OPEN' }
                    } else {
                        @{ status = 'OPEN'; remaining = [math]::Ceiling(60 - $elapsed) }
                    }
                } else {
                    @{ status = 'CLOSED' }
                }
            }
            'record_block' {
                $session = $request.session_id
                if (-not $_circuitBreakers.ContainsKey($session)) {
                    $_circuitBreakers[$session] = @{ status = 'CLOSED'; blocked_count = 0; last_blocked = $null; opened_at = $null }
                }
                $_circuitBreakers[$session].blocked_count++
                $_circuitBreakers[$session].last_blocked = [datetime]::Now.ToString('o')
                if ($_circuitBreakers[$session].blocked_count -ge 5) {
                    $_circuitBreakers[$session].status = 'OPEN'
                    $_circuitBreakers[$session].opened_at = [datetime]::Now.ToString('o')

                    # 检查是否需触发 global halt（3+ session 同时 OPEN）
                    $openCount = ($_circuitBreakers.Values | Where-Object { $_.status -eq 'OPEN' -and ([datetime]::Now - [datetime]::Parse($_.opened_at)).TotalSeconds -lt 120 }).Count
                    if ($openCount -ge 3) {
                        $_globalHalt = $true
                        @{ status = 'GLOBAL_HALT'; reason = "$openCount sessions OPEN" }
                    } else {
                        @{ status = 'OPEN' }
                    }
                } else {
                    @{ status = 'BLOCKED'; count = $_circuitBreakers[$session].blocked_count }
                }
            }
            'record_success' {
                $session = $request.session_id
                if ($_circuitBreakers.ContainsKey($session) -and $_circuitBreakers[$session].status -eq 'HALF-OPEN') {
                    $_circuitBreakers[$session].status = 'CLOSED'
                    $_circuitBreakers[$session].blocked_count = 0
                    @{ status = 'CLOSED' }
                } else {
                    @{ status = 'OK' }
                }
            }
            'record_risk_event' {
                $session = $request.session_id
                $eventType = $request.event_type
                # ... RiskChain 风险分计算（单线程，无竞态）...
                @{ status = 'OK'; risk_score = $_riskChains[$session].risk_score }
            }
            'register_session' {
                $session = $request.session_id
                $_circuitBreakers[$session] = @{ status = 'CLOSED'; blocked_count = 0; last_blocked = $null; opened_at = $null }
                $_riskChains[$session] = @{ events = @(); risk_score = 0 }
                @{ status = 'REGISTERED' }
            }
            'unregister_session' {
                $session = $request.session_id
                # 自动释放该 session 持有的所有锁
                $released = @()
                foreach ($key in @($_locks.Keys)) {
                    if ($_locks[$key].session_id -eq $session) {
                        $_locks.Remove($key)
                        $released += $key
                    }
                }
                # 清理 circuit breaker
                $_circuitBreakers.Remove($session)
                @{ status = 'UNREGISTERED'; released_locks = $released }
            }
            default {
                @{ status = 'ERROR'; reason = "unknown action: $($request.action)" }
            }
        }

        # 异步写入审计日志到 SQLite（单线程，无争用）
        # ... _WriteAuditLog ...

        # 返回响应
        $sw = New-Object System.IO.StreamWriter($pipe)
        $sw.WriteLine(($response | ConvertTo-Json -Compress))
        $sw.Flush()
    } catch {
        Write-Host "[COORDINATOR] ERROR: $_" -ForegroundColor Red
    } finally {
        $pipe.Disconnect()
    }
}

# 清理（daemon 退出时）
$daemonMutex.ReleaseMutex()
$daemonMutex.Dispose()
```

#### 7.33.3 Wrapper 函数中的 Pipe Client

```powershell
# 在 $PROFILE 的 wrapper 函数中，用 pipe client 替代直接 Mutex+SQLite 操作
function _ZephyrCoordinatorRequest {
    param([hashtable]$Request)

    # 项目 hash（跨项目隔离）
    $projectHash = try { (Get-FileHash $PWD -Algorithm SHA256).Hash.Substring(0,16) } catch { 'default' }
    $pipeName = "ZephyrCoordinator.$projectHash"

    try {
        $pipe = New-Object System.IO.Pipes.NamedPipeClientStream('.', $pipeName, [System.IO.Pipes.PipeDirection]::InOut)
        $pipe.Connect(2000)  # 2 秒 timeout

        $sw = New-Object System.IO.StreamWriter($pipe)
        $sw.WriteLine(($Request | ConvertTo-Json -Compress))
        $sw.Flush()

        $sr = New-Object System.IO.StreamReader($pipe)
        $response = $sr.ReadLine() | ConvertFrom-Json

        $pipe.Close()
        return $response
    } catch {
        # Daemon 未运行——fallback 到 v1.7.0 的 per-session + Mutex 模式
        Write-Host "[COORDINATOR] Daemon 未响应——fallback 到 per-session 模式" -ForegroundColor Yellow
        return $null
    }
}

# 在 git() wrapper 中使用
function git {
    # 检查 circuit breaker（通过 pipe，跨 session 可见）
    $cbResponse = _ZephyrCoordinatorRequest @{ action = 'check_circuit'; session_id = $env:ZEPHYR_SESSION_ID }
    if ($cbResponse) {
        if ($cbResponse.status -eq 'GLOBAL_HALT') {
            Write-Host "[GOVERNANCE] GLOBAL HALT: $($cbResponse.reason)" -ForegroundColor Red
            return 1
        }
        if ($cbResponse.status -eq 'OPEN') {
            Write-Host "[CIRCUIT-OPEN] 熔断器跳闸，$($cbResponse.remaining)s 后恢复" -ForegroundColor Red
            return 1
        }
    }
    # ... 原 wrapper 逻辑 ...
    # 阻断时通过 pipe 记录
    if ($blocked) {
        _ZephyrCoordinatorRequest @{ action = 'record_block'; session_id = $env:ZEPHYR_SESSION_ID }
    }
}
```

#### 7.33.4 Daemon 启动方式

```powershell
# 用 Start-Process 创建独立进程（不受父 session 生命周期约束）
# 在 $PROFILE 中检测 daemon 是否运行，未运行则启动
function _ZephyrEnsureDaemon {
    $projectHash = try { (Get-FileHash $PWD -Algorithm SHA256).Hash.Substring(0,16) } catch { 'default' }
    $pipeName = "ZephyrCoordinator.$projectHash"

    # 检测 daemon 是否已在运行（尝试连接）
    try {
        $testPipe = New-Object System.IO.Pipes.NamedPipeClientStream('.', $pipeName, [System.IO.Pipes.PipeDirection]::InOut)
        $testPipe.Connect(500)
        $testPipe.Close()
        return  # daemon 已运行
    } catch {
        # daemon 未运行——启动它
    }

    # 用 Start-Process 创建独立进程
    $daemonScript = Join-Path $PWD 'scripts\zephyr_coordinator_daemon.ps1'
    if (Test-Path $daemonScript) {
        Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -File $daemonScript -ProjectHash $projectHash" -WindowStyle Hidden
        Write-Host "[COORDINATOR] Daemon 已启动（pipe=$pipeName）" -ForegroundColor Green
    }
}

# 在 $PROFILE 末尾调用
_ZephyrEnsureDaemon
```

#### 7.33.5 裁定

**采用**——P0 优先级。Named Pipe 单线程协调器是 v1.8.0 的**核心架构升级**——从"用锁管理并发"（v1.7.0 Mutex+SQLite）升级到"**用单线程消除并发**"。rjmurillo/ai-agents #287 性能数据（10-50ms 后续调用）+ Rutgers CS 417 理论支持（单机集中式协调最优）+ PS 5.1 完整兼容（`NamedPipeServerStream` .NET Framework 4.x）。

**与 v1.7.0 的关系**：v1.7.0 的 Mutex+SQLite 作为 **fallback** 保留——daemon 未运行时降级到 per-session + Mutex 模式。

### 7.34 施工项 34：Session 生命周期管理（L19，P1，v1.8.0 新增）

> **⚠️ v2.0.0 DEPRECATED**：依赖 §7.33 Named Pipe Daemon，连带 deprecated。锁 TTL 60min 自动过期（§11.3.2）已覆盖"崩溃 AI 永久阻塞"场景，无需 SessionEnd hook + heartbeat。本节保留作为决策追溯，**不施工**。详见 §6.2 + §9。

> **背景**：§3.13.3 Trae 七事件 Hook 模型提供 SessionStart/SessionEnd hook。v1.7.0 缺少 session 结束时的锁/circuit breaker 清理——崩溃 session 的锁永久阻塞他人。

#### 7.34.1 SessionEnd Hook 配置

```json
{
  "SessionEnd": [{
    "matcher": "other",
    "hooks": [{
      "type": "command",
      "command": "powershell -ExecutionPolicy Bypass -File ./scripts/cleanup-session.ps1",
      "timeout": 10
    }]
  }]
}
```

#### 7.34.2 cleanup-session.ps1 脚本

```powershell
# scripts/cleanup-session.ps1——v1.8.0 新增
$hookInput = $input | Out-String | ConvertFrom-Json
$sessionId = $hookInput.session_id

if (-not $sessionId) { exit 0 }

# 通过 Named Pipe 通知 daemon 注销 session（自动释放锁+清理 circuit breaker）
$projectHash = try { (Get-FileHash $PWD -Algorithm SHA256).Hash.Substring(0,16) } catch { 'default' }
$pipeName = "ZephyrCoordinator.$projectHash"

try {
    $pipe = New-Object System.IO.Pipes.NamedPipeClientStream('.', $pipeName, [System.IO.Pipes.PipeDirection]::InOut)
    $pipe.Connect(2000)

    $sw = New-Object System.IO.StreamWriter($pipe)
    $sw.WriteLine((@{ action = 'unregister_session'; session_id = $sessionId } | ConvertTo-Json -Compress))
    $sw.Flush()

    $sr = New-Object System.IO.StreamReader($pipe)
    $response = $sr.ReadLine() | ConvertFrom-Json
    $pipe.Close()

    if ($response.released_locks) {
        Write-Host "[CLEANUP] Session $sessionId 已注销，释放 $($response.released_locks.Count) 个锁" -ForegroundColor Green
    }
} catch {
    # Daemon 未运行——fallback：直接用 Mutex 释放 registry.json 中的锁
    # ... v1.7.0 fallback 逻辑 ...
}
```

#### 7.34.3 Heartbeat 超时清理（daemon 侧）

```powershell
# 在 daemon 事件循环中定期执行（如每 60 秒）
function _ZephyrCleanupStaleSessions {
    $now = [datetime]::Now
    foreach ($session in @($_circuitBreakers.Keys)) {
        $cb = $_circuitBreakers[$session]
        if ($cb.last_blocked) {
            $lastActivity = [datetime]::Parse($cb.last_blocked)
            if (($now - $lastActivity).TotalMinutes -gt 30) {
                # 30 分钟无活动——自动注销
                # 释放该 session 持有的所有锁
                foreach ($key in @($_locks.Keys)) {
                    if ($_locks[$key].session_id -eq $session) {
                        $_locks.Remove($key)
                    }
                }
                $_circuitBreakers.Remove($session)
                $_riskChains.Remove($session)
                Write-Host "[COORDINATOR] Session $session 30 分钟无活动——自动注销" -ForegroundColor Yellow
            }
        }
    }
}
```

#### 7.34.4 裁定

**采用**——P1 优先级。Session 生命周期管理是 Trae 多 AI 并发的必要环节——没有它，崩溃 session 的锁永久阻塞他人。Trae SessionEnd hook + daemon heartbeat 超时清理双重保障。

### 7.35 施工项 35：Wrapper 热重载+版本管理+跨项目隔离（L19，P1，v1.8.0 新增）

> **⚠️ v2.0.0 DEPRECATED**：单项目无跨项目隔离需求。Wrapper 热重载 + 版本管理是为"多项目共用 $PROFILE"场景设计，本项目 100% 围绕 ZephyrAlpha 单项目。本节保留作为决策追溯，**不施工**。详见 §6.2 + §9。

> **背景**：§3.13.7 发现三个剩余 gap：①26 session 运行中更新 $PROFILE 的版本 skew ②`Global\` Mutex 跨项目冲突 ③SQLite busy_timeout 未配置。

#### 7.35.1 版本化 $PROFILE + Reload-Profile

```powershell
# $PROFILE 中——v1.8.0 新增：版本管理
$env:ZEPHYR_PROFILE_VERSION = '1.8.0'

function Reload-Profile {
    # 清除旧 wrapper 函数（按 marker 注释识别）
    $oldFunctions = Get-ChildItem function: | Where-Object {
        $_.Definition -match 'git-safety-wrapper|powershell-destructive-guard'
    }
    foreach ($f in $oldFunctions) { Remove-Item "function:$($f.Name)" -ErrorAction SilentlyContinue }

    # 重新 dot-source
    . $PROFILE
    Write-Host "[PROFILE] Reloaded to version $env:ZEPHYR_PROFILE_VERSION" -ForegroundColor Green
}

# Daemon 协议版本协商
function _ZephyrCheckProtocolVersion {
    $response = _ZephyrCoordinatorRequest @{ action = 'check_version'; profile_version = $env:ZEPHYR_PROFILE_VERSION }
    if ($response -and $response.status -eq 'VERSION_MISMATCH') {
        Write-Host "[PROFILE] 版本不匹配（daemon=$($response.daemon_version) session=$env:ZEPHYR_PROFILE_VERSION）——请执行 Reload-Profile" -ForegroundColor Yellow
    }
}
```

#### 7.35.2 Mutex 跨项目隔离

```powershell
# v1.8.0：所有 Mutex 名加项目路径 hash 后缀，防跨项目冲突
function _ZephyrGetMutexName {
    param([string]$BaseName)
    $projectHash = try { (Get-FileHash $PWD -Algorithm SHA256).Hash.Substring(0,16) } catch { 'default' }
    return "Global\Zephyr.$BaseName.$projectHash"
}

# 使用示例
$mutexName = _ZephyrGetMutexName 'AuditLogMutex'  # → Global\Zephyr.AuditLogMutex.a1b2c3d4e5f6g7h8
```

#### 7.35.3 SQLite busy_timeout 配置

```powershell
# v1.8.0：所有 SQLite 连接必须配置 busy_timeout
function _ZephyrSQLiteConnect {
    param([string]$DbPath)
    $conn = New-Object System.Data.SQLite.SQLiteConnection
    $conn.ConnectionString = "Data Source=$DbPath;Version=3;"
    $conn.Open()

    # 关键配置（防 26 并发 writer 争用）
    $cmd = $conn.CreateCommand()
    $cmd.CommandText = @'
    PRAGMA journal_mode=WAL;
    PRAGMA busy_timeout=5000;
    PRAGMA synchronous=NORMAL;
    '@
    $cmd.ExecuteNonQuery()
    return $conn
}
```

#### 7.35.4 裁定

**采用**——P1 优先级。版本管理防 26 session 版本 skew；项目 hash 后缀防跨项目 Mutex 冲突；SQLite busy_timeout 防 26 并发 writer 争用。三者都是 v1.7.0 遗留的工程细节 gap。

### 7.36 施工项 36：AST-based 命令分析替换 regex（L10 升级，P1，v1.9.0 新增）

> **⚠️ v2.0.0 DEPRECATED**：过度升级。§7.18 regex 反混淆归一化（9 策略）已覆盖 22 路并发审查场景下的所有真实命令模式。AST 分析是为"防 adversarial shell 注入"设计——单人 AI 协作中 AI 不会发动 shell 注入攻击自己。本节保留作为决策追溯，**不施工**。详见 §6.2 + §9。

> **背景**：§3.14.2 确认 AST 分析是 v1.8.0 后唯一明确的算法升级。GuardFall 证明 regex 匹配可被绕过，AST 结构化分析更鲁棒。

#### 7.36.1 AST 分析算法

```powershell
# v1.9.0 新增：AST-based 命令安全分析（替换 §7.18 反混淆 + §7.1 regex 匹配）
function _ZephyrAnalyzeCommandAST {
    param([string]$Command)

    # PS 5.1 原生 AST 解析
    $tokens = $null
    $parseErrors = $null
    $ast = [System.Management.Automation.Language.Parser]::ParseInput($Command, [ref]$tokens, [ref]$parseErrors)

    # 语法错误——fail-closed
    if ($parseErrors.Count -gt 0) {
        return @{ safe = $false; reason = "语法错误: $($parseErrors[0].Message)"; action = 'BLOCKED' }
    }

    $findings = @()

    # 遍历 AST 节点，检测危险模式
    $ast.FindAll({
        param($node)

        # 1. 检测命令替换 $(...) —— GuardFall Class C
        if ($node -is [System.Management.Automation.Language.CommandExpansionAst]) {
            $findings += @{ type = 'command_substitution'; text = $node.Extent.Text }
        }

        # 2. 检测 $IFS 变量引用 —— GuardFall Class B
        if ($node -is [System.Management.Automation.Language.VariableExpressionAst] -and
            $node.VariablePath.UserPath -eq 'IFS') {
            $findings += @{ type = 'ifs_expansion'; text = $node.Extent.Text }
        }

        # 3. 检测 Invoke-Expression / iex 调用
        if ($node -is [System.Management.Automation.Language.CommandAst] -and
            $node.CommandElements[0].Extent.Text -match '^(Invoke-Expression|iex)$') {
            $findings += @{ type = 'invoke_expression'; text = $node.Extent.Text }
        }

        # 4. 检测 Add-Type（可能编译内联 C# 代码）
        if ($node -is [System.Management.Automation.Language.CommandAst] -and
            $node.CommandElements[0].Extent.Text -eq 'Add-Type') {
            $findings += @{ type = 'add_type'; text = $node.Extent.Text }
        }

        # 5. 检测 base64 编码命令
        if ($node -is [System.Management.Automation.Language.CommandAst] -and
            $node.CommandElements[0].Extent.Text -match 'base64' -and
            ($node.Extent.Text -match '-d' -or $node.Extent.Text -match '--decode')) {
            $findings += @{ type = 'base64_decode'; text = $node.Extent.Text }
        }

        # 6. 检测管道到 bash/sh/powershell —— GuardFall Class D
        if ($node -is [System.Management.Automation.Language.PipelineAst]) {
            $lastCommand = $node.PipelineElements | Select-Object -Last 1
            if ($lastCommand.CommandElements[0].Extent.Text -match '^(bash|sh|powershell|pwsh)$') {
                $findings += @{ type = 'pipe_to_shell'; text = $node.Extent.Text }
            }
        }

        return $false  # 不过滤任何节点（继续遍历）
    }, $true) | Out-Null

    # 评估发现
    if ($findings.Count -gt 0) {
        $reasons = ($findings | ForEach-Object { "$($_.type): $($_.text)" }) -join '; '
        return @{ safe = $false; reason = "AST 检测到危险模式: $reasons"; action = 'BLOCKED'; findings = $findings }
    }

    return @{ safe = $true; action = 'ALLOWED' }
}
```

#### 7.36.2 集成到 wrapper

```powershell
function git {
    # v1.9.0: AST 分析替代 regex（更鲁棒，覆盖 GuardFall 3/5 类）
    $astResult = _ZephyrAnalyzeCommandAST -Command ($args -join ' ')
    if (-not $astResult.safe) {
        Write-Host "[GIT-SAFE] BLOCKED (AST): $($astResult.reason)" -ForegroundColor Red
        _ZephyrAuditLog -Command ($args -join ' ') -Action 'BLOCKED' -Reason $astResult.reason
        _ZephyrCoordinatorRequest @{ action = 'record_block'; session_id = $env:ZEPHYR_SESSION_ID }
        return 1
    }
    # ... 原 wrapper 逻辑（§7.1-7.35）...
}
```

#### 7.36.3 裁定

**采用**——P1 优先级。AST 分析是 §3.14 确认的唯一明确算法升级。性能 ~1ms/call 可忽略。PS 5.1 原生支持 `[Parser]::ParseInput()`。与 v1.5.0 §7.18 反混淆归一化层互补——AST 是结构化分析，反混淆是预处理。

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

### 8.7 自动变量碰撞 + `.git` 永久阻断验证（v1.5.0 新增）

| 测试 | 预期结果 |
|---|---|
| `$home = "test"` | BLOCKED，提示用 `$_myHome`（Codex #32684 教训） |
| `$PID = 12345` | BLOCKED，`$PID` 是只读自动变量 |
| `$_myHome = "test"` | 放行（非自动变量名） |
| `Remove-Item -Recurse -Force .git/` | HARDBLOCKED（.git 写入永久阻断） |
| `Set-Content .git\config "..."` | HARDBLOCKED |
| `New-Item .git\hooks\post-commit -Type File` | HARDBLOCKED |
| `git commit -m "test"` | 放行（git 命令不触发 .git 保护） |
| `git add .` | 放行（git 命令内部写 .git 合法） |

### 8.8 Shell 反混淆归一化层验证（v1.5.0 新增）

| 测试 | 预期结果 |
|---|---|
| `r''m -rf /` | BLOCKED（相邻引号拼接检测） |
| `rm$IFS-rf$IFS/` | BLOCKED（$IFS 展开检测） |
| `$(echo rm) -rf /` | BLOCKED（命令替换标记） |
| `echo "cm0gLXJmIC8=" \| base64 -d \| bash` | BLOCKED（Base64 decode 检测） |
| `rm --no-preserve-root -rf /` | BLOCKED（destructive argv flag） |
| `$cmd = "rm"; & $cmd -rf /tmp/x` | BLOCKED（变量调用标记） |
| `git status` | 放行（无反混淆标记） |
| `git commit -m "fix: a && b"` | 放行（引号内的 && 不触发） |

### 8.9 SafeFix + RiskChain + Risk-tiered 验证（v1.5.0 新增）

| 测试 | 预期结果 |
|---|---|
| `git clean -fd` | BLOCKED + SAFEFIX: `git clean -n（预览）+ 人工确认后 git stash` |
| `git reset --hard` | BLOCKED + SAFEFIX: `git stash + git reset --mixed` |
| `chmod 777 path` | BLOCKED + SAFEFIX: `chmod 755（标准权限）` |
| 连续执行 3 次 `git clean -fd` | 第 3 次后 RiskChain 风险分 ≥ 80 → CIRCUIT-OPEN |
| 读 .env → base64 解码 → 用逃生通道 | RiskChain 风险分 ≥ 100 → SESSION-TERMINATE |
| `git status`（wrapper 出错模拟） | FAIL_OPEN（低风险，放行） |
| `git clean -fd`（wrapper 出错模拟） | FAIL_CLOSED（高风险，阻断） |
| `format d:`（wrapper 出错模拟） | FAIL_CLOSED（CRITICAL，永久阻断） |
| 阻断 `/tmp/x` 后尝试 `/var/tmp/x` | BYPASS-DETECTED（canonicalize 后相同） |
| 阻断 `bash -c "rm x"` 后尝试 `sh -c "rm x"` | BYPASS-DETECTED（shell 切换检测） |

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
| 不实现完整 tokenize-then-check（v1.5.0） | GuardFall 证明 Continue 的 tokenize-then-check 是唯一正确架构，但实现需 shell-quote 解析+命令替换递归求值，工程量大——v1.5.0 先用 9 策略反混淆归一化（§7.18）作为近似，tokenize-then-check 作为 v2.0.0 远期改进 |
| 不引入沙箱（v1.5.0 重申） | §3.10.4 Zed 1.14.2 证明 OS 级沙箱是最佳实践，但 Windows 无 macOS Seatbelt/bubblewrap 等效物；Docker/WSL 对量化交易开发过重——本方案用 wrapper + RiskChain 近似沙箱效果 |
| 不引入 Microsoft Defender AI agent protection（v1.5.0） | §3.10.12 Microsoft Defender AiAgentProtection 是企业 Windows 设备级方案，本方案是个人项目——作为远期评估 |
| 不实现跨 session RiskChain（v1.5.0） | §3.10.6 CFD 攻击可跨 session 拆分，完整防御需中央 risk_score 服务——v1.5.0 仅 session 内追踪，跨 session 作为 v2.0.0 远期改进 |
| 不实现 CoAgent MTPO（v1.5.0） | §3.10.10 CoAgent MTPO 是比 file lock 更轻量的 LLM-as-judge 冲突修复，但需每个 tool 注册 saga-style inverse——工程量大，作为 §11 远期评估 |
| 不引入 Raft/Paxos 分布式共识（v1.5.0） | 多个 2026 来源一致：单机多 AI 不需要分布式共识，SQLite CAS 足够；Raft/Paxos 仅在多机 agent fleet 时才需要 |
| 不引入 Redis-based 分布式锁（v1.5.0 重申） | §11.7 已裁定；grite 论文证实单机 SQLite CAS 足够，Redis 运维开销不必要 |
| 不引入 MXC ProcessContainer（v1.6.0） | §3.11.11 Microsoft MXC 是官方 AI agent 沙箱，但 README 明确声明"no MXC profiles should be treated as security boundaries currently"——作为远期评估 |
| 不引入 WDAC + CLM（v1.6.0） | §3.11.1 WDAC + CLM 是 Windows 企业级防御层，但本方案是个人项目，CLM 下 `Add-Type` 被阻断会影响 §7.24 Atomic Path Resolution 的 P/Invoke——作为远期评估 |
| 不引入 Job Object + Restricted Token（v1.6.0） | §3.11.13 Job Object 是内核级资源隔离，但实现复杂度高（需 Go/C# 编译二进制），与 §9"不编译 Go/Rust 二进制 wrapper"裁定一致——作为远期评估 |
| 不引入 PSReadLine 集成（v1.6.0 修订） | §3.11.2 证实 PSReadLine 仅在交互式 REPL 中工作，对 AI agent 通过 -Command/-File/-EncodedCommand 调用的脚本完全无效——不作为 AI agent 场景的防御层 |
| **v2.0.0 deprecated：§7.16 Circuit Breaker**（v2.0.0 新增） | 单人 AI 协作无 adversarial 场景，AI 不会"无限尝试危险命令"。§7.15 错误分类的 STOP/ALTERNATIVE 格式已防 AI 卡死循环重试 |
| **v2.0.0 deprecated：§7.19 SafeFix block+suggest**（v2.0.0 新增） | AI 提示工程层，过度工程。RULE-GIT-SAFE 规则 + §7.15 错误分类已足够指导 AI |
| **v2.0.0 deprecated：§7.20 RiskChain 攻击链追踪**（v2.0.0 新增） | 典型 adversarial 防御——追踪 base64 解码/变量调用/命令替换等"绕过"行为。单人 AI 协作中 AI 不会"绕过"自己的安全机制 |
| **v2.0.0 deprecated：§7.21 Risk-tiered fail mode**（v2.0.0 新增） | 四级风险分层过度细分。§7.14 fail-open（普通命令出错放行+记录，CRITICAL 命令 fail-closed）两级已足够 |
| **v2.0.0 deprecated：§7.22 跨工具/跨 shell 绕过检测**（v2.0.0 新增） | adversarial 防御——防 AI 切换 shell/工具绕过安全机制。单人 AI 协作中 AI 不会主动"绕过" |
| **v2.0.0 deprecated：§7.24 symlink/junction + TOCTOU 防护**（v2.0.0 新增） | adversarial 防御——防 AI 用 symlink/junction 攻击自己。单人 AI 协作中 AI 不会发动 symlink 攻击。P/Invoke CreateFile 实现复杂度且 PS 5.1 兼容性存疑 |
| **v2.0.0 deprecated：§7.25 git hook 信任链 + hash 锁定**（v2.0.0 新增） | adversarial 防御——防恶意修改 git hook / reflog。单人单账户项目无恶意 actor，hooksPath 白名单 + hash 锁定维护成本高 |
| **v2.0.0 deprecated：§7.26 Script Block Logging 4104**（v2.0.0 新增） | 企业级 Windows 事件日志方案，个人项目过重。4104 通道扩到 1GB + evtxparser 影响主机 IO。§7.10 JSONL 审计日志已足够追溯 |
| **v2.0.0 deprecated：§7.28.3 lock_files.py SQLite 迁移最终方案**（v2.0.0 新增） | §11.3.3 Task Board 已用 SQLite，lock_files.py 保留 §7.28.2 过渡方案（JSON + 命名 Mutex）即可，无需重复迁移 |
| **v2.0.0 deprecated：§7.29 跨 session GovernanceStore**（v2.0.0 新增） | 与 §11.3.3 Task Board SQLite 重复——Task Board 已是跨 session 协调层（claim/complete/block 状态机 + SQLite CAS）。另建 GovernanceStore 是重复造轮子 |
| **v2.0.0 deprecated：§7.30 共享规则文件完整性防护**（v2.0.0 新增） | adversarial 防御——防"恶意 session 注入规则"。单人项目无恶意 actor，AGENTS.md/project_rules.md 通过 git 版本控制已足够追溯变更 |
| **v2.0.0 deprecated：§7.33 Named Pipe Coordinator Daemon**（v2.0.0 新增） | 重复造轮子 + 单点故障。§11.3.3 Task Board 已用 SQLite WAL + CAS——SQLite 本身就是工业级并发方案，22 session 并发读写完全胜任。Named Pipe daemon 增益仅微秒级，却引入单点故障 |
| **v2.0.0 deprecated：§7.34 Session 生命周期管理**（v2.0.0 新增） | 依赖 §7.33 Named Pipe Daemon，连带 deprecated。锁 TTL 60min 自动过期（§11.3.2）已覆盖"崩溃 AI 永久阻塞"场景，无需 SessionEnd hook + heartbeat |
| **v2.0.0 deprecated：§7.35 Wrapper 热重载+版本管理+跨项目隔离**（v2.0.0 新增） | 单项目无跨项目隔离需求。Wrapper 热重载 + 版本管理是为"多项目共用 $PROFILE"场景设计，本项目 100% 围绕 ZephyrAlpha 单项目 |
| **v2.0.0 deprecated：§7.36 AST-based 命令分析替换 regex**（v2.0.0 新增） | 过度升级。§7.18 regex 反混淆归一化（9 策略）已覆盖 22 路并发审查场景下的所有真实命令模式。AST 分析是为"防 adversarial shell 注入"设计——单人 AI 协作中 AI 不会发动 shell 注入攻击自己 |
| **v2.0.0 删除：§14 灾难恢复 RPO/RTO**（v2.0.0 新增） | 量化交易开发项目，不是 7×24 服务。RPO=0/RTO<30s 是 SRE 话术，对个人 AI 开发项目过度。SQLite WAL + JSONL append-only 已提供足够的容错 |
| **v2.0.0 删除：§15 性能影响评估的 12 层防御开销**（v2.0.0 新增） | 防御层数量本身过度（19→6），砍到 6 层后无需逐层评估开销。git 命令本身 >100ms，5-6 层 wrapper 开销总计 <5ms 可忽略 |

> **v2.0.0 deprecated 根因总结**：v1.x 累计 14 施工项被 deprecated，根因是把"AI 误操作"（合法错误）误判为"AI 恶意攻击"（adversarial）。单人单账户 AI 协作开发中 AI 是协作者不是攻击者——所有"防 AI 攻击自己"的防御层（RiskChain/SafeFix/symlink 防护/hook hash 锁定/AST 升级/Named Pipe daemon 等）均偏离实际诉求。真实场景只有两类：①AI 误删文件（§7.1 wrapper 拦截）②多 AI 共用工作区冲突（§11 三件套协调）。v2.0.0 精简到 6 层防御 + 3 件套协调，共 ~12 施工项 / ~15 天，覆盖 22 路并发审查 + 未来多 AI 施工的全部真实场景。
>
> **v2.1.0 第二轮 deprecated/simplified**：v2.0.0 保留项内部的实现细节仍残留 adversarial 思维：

| 不做/简化 | 理由 |
|---|---|
| **v2.1.0 deprecated：§7.17.1 自动变量碰撞检测** | 30+ 只读自动变量清单 + 函数检测过度。Codex `$home` 事故是极端组合案例，AI 不会主动写 `$home = "test"`。改为 RULE-GIT-SAFE 加一条规则"禁止用 $HOME/$PID/$TRUE 等作变量名"即可。§7.17.2 .git 阻断保留 |
| **v2.1.0 deprecated：§7.18 反混淆归一化层 9 策略** | 9 策略全是防 adversarial shell 注入（$IFS/base64/hex 转义等）。AI 不会写 `rm$IFS-rf$IFS/` 混淆命令，AI 写的命令是直接的、可读的。§7.1 wrapper 直接 regex 匹配已够 |
| **v2.1.0 deprecated：§7.15 错误分类 STOP/ALTERNATIVE 格式** | AI 提示工程层过度。RULE-GIT-SAFE 规则 + wrapper 简单错误消息（"BLOCKED: git clean 会删除文件"）已够。AI 看到 BLOCKED 就知道不该执行，不需要教它"替代方案"。§7.14 fail-open 保留 |
| **v2.1.0 简化：§7.23 git 危险命令 20+→4 命令** | 20+ 命令中 16+ 是防 adversarial RCE（config hooksPath/fsmonitor/update-index/notes/hash-object/apply symlink/submodule/init --template/push --receive-pack）——AI 不会主动写 `git config core.hooksPath /tmp/evil`。只保留 4 个 AI 易误用命令：filter-branch/filter-repo/reflog expire/gc --prune |
| **v2.1.0 简化：§7.27 审计日志 Mutex→每 session 独立文件** | 审计日志是 append-only 事后追溯，不是关键状态。Claude Code `.claude.json` 423 次损坏是状态文件（read-modify-write），不是 append-only。改为每 session 独立文件 `audit_{yyyyMMdd}_{sessionId}.jsonl`，无需 Mutex |
| **v2.1.0 简化：§7.32 init-session.ps1+TRAE_ENV_FILE→$PROFILE 一行** | Trae hook + init-session.ps1 + TRAE_ENV_FILE 机制复杂，且 hook 可行性是开放问题。简化为 $PROFILE 顶部一行 `$env:ZEPHYR_SESSION_ID = [guid]::NewGuid().ToString()`，每 session 自动生成 UUID |
| **v2.1.0 简化：§11.3.2 去 heartbeat 续期** | heartbeat 续期 30min + 5 分钟无 heartbeat 告警是为"7×24 长任务"设计。22 路审查中 AI 任务通常 30-60 分钟，TTL 60min 到期释放已够。保留 acquire/release/check/list/cleanup 五命令 |
| **v2.1.0 简化：§11.3.3 去 epoch 防 ABA + 状态机精简** | epoch 防 ABA 是为"lease 释放后又被获取"精确时序设计，22 路审查中几乎不会发生。砍掉 epoch 字段，保留基本 SQLite + CAS + WAL。状态机精简为 pending→claimed→completed（去 blocked/abandoned） |
| **v2.1.0 简化：§11.3.1 去 7 天告警** | `auto_cleanup_days: 7` 是为"长期 worktree 堆积"设计。22 路审查是一次性的（几小时到 1 天），不会持续 7 天。merge 后立即 abort 清理 |

> **v2.1.0 deprecated/simplified 根因总结**：v2.0.0 砍掉了宏观 adversarial 防御层，但保留项内部的实现细节仍残留 adversarial 思维——9 策略反混淆（防 shell 注入）、30+ 自动变量检测（防极端碰撞）、20+ git RCE 命令（防恶意 hooksPath）、Mutex 串行化（防并发损坏状态文件）、heartbeat/epoch（防 7×24 服务边缘场景）、init-session.ps1（完美注入）。这些实现细节为"adversarial 攻击"或"7×24 服务"场景设计，偏离"22 路并发审查 + 未来多 AI 施工"的实际诉求。v2.1.0 精简到 **8 项 / ~11 天**，6 层防御结构不变但实现大幅简化。

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
| PowerShell 自动变量碰撞检测的 PSReadLine 集成方式（v1.5.0） | 待测试：PSReadLine `Set-PSReadLineKeyHandler` Enter 键钩子是否能在命令执行前拦截——若不能，降级为 wrapper 函数内检测 |
| `.git` 永久阻断是否影响 git 子进程（v1.5.0） | 待测试：git 命令内部会写 `.git/index` 等，但用的是 `git.exe` 子进程（不经过 PowerShell 函数）——应该安全，需实测确认 |
| Shell 反混淆归一化的 PowerShell 5.1 兼容性（v1.5.0） | 待测试：`[regex]::Replace` 回调在 PowerShell 5.1 中是否工作——若不工作，改用 `[regex]::Matches` + 字符串拼接 |
| RiskChain 跨 session 追踪的中央服务设计（v1.5.0） | 远期：CFD 攻击可跨 session 拆分，完整防御需中央 risk_score 服务（SQLite/Redis）——v2.0.0 评估 |
| SafeFix 规则库的维护机制（v1.5.0） | 待设计：规则库从 7 条起步，需定期更新——考虑用 YAML 配置文件外部化管理 |
| IETF AAT hash-chaining 审计日志升级（v1.5.0） | 远期：§3.10.7 IETF AAT 草案要求 SHA-256 hash chaining + ECDSA 签名——v2.0.0 评估升级 `_ZephyrAuditLog` |
| Phi Accrual Failure Detector 实现（v1.5.0） | 远期：§3.10.9 Phi Accrual 替代固定 TTL 60min——需 Welford 在线算法实现，§11.3.2 升级时评估 |
| SQLite CAS epoch 计数器补充（v1.5.0） | 待施工：§11.3.3 schema 需补充 `epoch INTEGER DEFAULT 0` 字段防 ABA——§3.10.11 SQLite CAS 验证 |
| Trae SOLO 单 agent loop 对 §11 三件套的影响（v1.5.0） | §3.10.13 澄清：Trae SOLO 是单 agent loop，§11.1.1 的"26 路并发"实为 26 个 Trae 窗口并发——三件套仍适用但语义需澄清 |
| Atomic Path Resolution 的 CLM 兼容性（v1.6.0） | 待测试：§7.24 `Add-Type -TypeDefinition` P/Invoke 在 CLM 下被阻断——若未来启用 CLM，需用 WDAC 签名规则白名单 wrapper 模块 |
| git hook hash 锁定的维护机制（v1.6.0） | 待设计：§7.25.1 `.hook_hashes` 文件需在 hook 更新时同步更新——考虑用 pre-commit hook 自动生成 |
| Script Block Logging 4104 的性能影响（v1.6.0） | 待测试：4104 启用后 PowerShell 性能下降幅度——evtxparser 建议通道扩到 1GB，但需实测繁忙主机的 IO 影响 |
| git submodule 白名单源的定义（v1.6.0） | 待设计：§7.23 `git submodule add` 白名单源——考虑用 `.gitmodules.allow` 配置文件管理 |
| MXC ProcessContainer 远期评估（v1.6.0） | 远期：§3.11.11 Microsoft MXC 是官方 AI agent 沙箱，等 README 声明"security boundary"后评估集成 |
| GovernanceStore SQLite 依赖部署（v1.7.0） | 待测试：§7.29 `System.Data.SQLite` 在 PowerShell 5.1 中需手动安装——考虑用 `System.Data.SQLite.dll` 旁加载或 fallback 到 JSON+Mutex |
| 跨 session global halt 的误触发风险（v1.7.0） | 待评估：§7.29 3+ session 同时熔断触发 global halt——如果 3 个 session 独立遇合法阻断（如 git clean），是否误触发？需评估阈值 |
| lock_files.py SQLite 迁移时机（v1.7.0） | 待决策：§7.28 过渡方案（Mutex+原子写）与最终方案（SQLite）何时切换——建议与 §11.3.3 Task Board 同步施工 |
| Trae Hooks 配置可行性（v1.7.0） | 待测试：§3.12.1 Trae 2026-06 v3.5.66 新增 Hooks 支持——是否可用于 session 启动时注入 ZEPHYR_SESSION_ID 环境变量 |

## 11. 多 AI 协调层施工方案（Git Worktree + File Lock(TTL) + Task Board 三件套）

> **本节新增于 v0.8.0**，由 2026-08-11 第一性原理调研发现 #ARCH-AICOLLAB-001 议题触发。
> **方案设计供另一 AI 直接施工**，无需重新调研。
> 关联议题：[#ARCH-AICOLLAB-001](architecture_issue_registry.yaml) Git Worktree + File Lock(TTL) + Task Board 三件套（26 路协调层）

### 11.1 背景与目标

#### 11.1.1 痛点
- 项目当前 26 路 AI 在 Trae 上并发施工（**v1.5.0 澄清**：§3.10.13 证实 Trae SOLO 是单 agent loop，"26 路并发"实为 26 个 Trae IDE 窗口/对话并发，每个窗口内是单 SOLO agent 循环——非 Trae 原生多 agent grid），但共用同一 working directory（`d:\ZephyrAlpha`）
- 现有 `scripts/lock_files.py`（611 行 v2.0.0）已实现文件锁，但 `registry.json` 为空——AI 未真正用上
- 多 AI 共用主工作区 → 必然出现 silent data loss（A 写 formatToken、B 覆盖为 parseHeaders，无冲突标记）——**§3.10.8 grite 论文 C2 实测证实 file-based tracker 会静默丢失并发写**
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
- **Anthropic 报告**：multi-agent 相比单 agent 任务完成率 +90%（仅适用于 breadth-first 研究任务，不适用于编码或强依赖任务；token 消耗 15×）
- **Cognition 数据**：单 agent 60% 时间在搜索（context 污染）
- **Vibe Kanban**（**v1.5.0 状态更新**：§3.10.14 bloop 公司于 2026-04-10 关停，项目转为 Apache 2.0 社区维护、完全本地化——作为业界事实标准的参考价值仍在，但不再商业维护）
- **grite（arXiv:2606.19616, 2026-06-17）**（v1.5.0 新增）：git-native + CRDT 事件日志 + advisory leases，server-less；实测 duplicate-work rate 78%→0%，goodput >3×；**file-based tracker 会静默丢失并发写**——验证 SQLite Task Board 设计正确
- **CoAgent MTPO（arXiv:2606.15376, 2026-06-13）**（v1.5.0 新增）：advisory concurrency + LLM-as-judge 冲突修复，1.4× 加速保持 95% 串行正确性——范式转变："control turns advisory: the runtime informs, the agent repairs"
- **Agentlocks（simke9445）**（v1.5.0 补充）：advisory file locks for AI agents，agent-native（JSON 输出、self-describing contract、errors that teach），`acquire`/`expand`/`refresh`/`release` lease 模型，`next:` breadcrumb 让 agent 知道下一步
- **SQLite CAS 模式**（v1.5.0 新增）：`UPDATE…WHERE…SELECT changes()` + epoch 计数器防 ABA + WAL 模式——单机多 AI 首选，验证 §11.3.3 SQLite Task Board 设计正确

#### 11.2.2 决策依据
用户裁定（2026-08-11）：**全部加入**三件套——Git Worktree + File Lock(TTL) + Task Board。理由：①Trae 上就是多 AI 并发施工 ②另一 AI 正施工 ③未来真多 AI 并行可直接用。

### 11.3 三件套设计

#### 11.3.1 Git Worktree（每 AI 独立 checkout+分支）

> **⚠️ v2.1.0 简化（去 7 天告警）**：v1.x 的 `auto_cleanup_days: 7`（7 天未活动告警）是为"长期 worktree 堆积"设计。22 路审查是一次性的（几小时到 1 天），不会持续 7 天。**v2.1.0 砍掉 7 天告警**，保留基本 worktree create/exec/merge/abort/list。merge 后立即 abort 清理。详见 §6.2 + §9。

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

> **⚠️ v2.1.0 简化（去 heartbeat 续期）**：v1.x 的 heartbeat 续期 30min + 5 分钟无 heartbeat 告警 + RULE-LOCK 配置（`heartbeat_interval: 5`）是为"7×24 长任务"设计。22 路审查中 AI 任务通常 30-60 分钟完成，TTL 60min 到期释放已够。**v2.1.0 砍掉 heartbeat 续期机制**，保留 TTL 60min 到期释放 + cleanup 命令。acquire/release/check/list/cleanup 五命令即可。详见 §6.2 + §9。

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

**v1.5.0 升级方向（参考 §3.10.9 Phi Accrual）**：当前固定 TTL 60min 在 agent 长时间 GC pause 或系统卡顿时会**误释放锁**（其他 agent 抢锁后原 agent 恢复，导致双写）。升级方向：
- 用 **Phi Accrual Failure Detector** 替代固定 TTL timeout——维护心跳 inter-arrival 时间滑动窗口（1000 样本），Welford 在线算法更新 mean/variance，计算 `phi = -log10(P(arrival ≥ t - last_seen))`
- φ>3 触发 lease-renew 提醒（激进），φ>8 判定 lease 过期（保守，1/10^8 误报率）
- 优势：自适应网络抖动/GC pause/WAN jitter；同一心跳流可服务多阈值路径
- **暂不施工**——v1.5.0 先用固定 TTL 60min，Phi Accrual 作为 §11.3.2 远期升级（见 §10 开放问题）

#### 11.3.3 Task Board（SQLite-based claim/complete/block 状态机）

> **⚠️ v2.1.0 简化（去 epoch 防 ABA + 状态机精简）**：v1.x 的 `epoch INTEGER` 字段防 ABA + TTL 60s = 4×15s heartbeat 是为"7×24 服务的 lease 释放后又被获取"精确时序设计。22 路审查中几乎不会发生 ABA。**v2.1.0 砍掉 epoch 字段**，保留基本 SQLite + CAS（`UPDATE...WHERE...SELECT changes()`）+ WAL 模式。状态机精简为 `pending→claimed→completed`（去掉 blocked/abandoned 中间态，22 路审查不需要——AI 完成就 completed，放弃就删除 task 重新 create）。详见 §6.2 + §9。

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
    metadata_json TEXT,                  -- 任意附加元数据
    epoch INTEGER DEFAULT 0              -- v1.5.0 新增：防 ABA（lease 释放后又被获取）
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

**v1.5.0 SQLite CAS 模式升级**（参考 §3.10.11）：
- 新增 `epoch INTEGER DEFAULT 0` 字段防 ABA（lease 释放后又被获取，其他 agent 误判仍持有旧 lease）
- claim 操作用 CAS（Compare-And-Swap）单语句原子执行：
  ```sql
  UPDATE tasks SET claimed_by = ?, claimed_at = datetime('now'), status = 'claimed', epoch = epoch + 1
  WHERE task_id = ? AND (claimed_by IS NULL OR claimed_at < datetime('now', '-60 minutes'))
  -- 若 changes() > 0 则抢占成功
  ```
- 启用 **WAL 模式**：`PRAGMA journal_mode=WAL;`——读不阻塞写
- TTL 设为 60s = 4× 客户端 15s heartbeat（容忍 3 次漏 beat）——参考 tripod-api 2026-07-17 实测

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

## 13. 施工路线图（v2.1.0 精简——8 施工项分 2 Phase）

> **v2.1.0 精简裁定**：v2.0.0 的 12 施工项 / 2 Phase / ~17 天精简到 **8 施工项 / 2 Phase / ~11 天**。v2.0.0 保留项中 §7.15 错误分类 / §7.17.1 自动变量碰撞 / §7.18 反混淆层 3 项 deprecated（详见 §6.2 + §9）；§7.23 / §7.27 / §7.32 / §11.3.1-3 六项实现简化（去 adversarial 细节 + 去 7×24 服务边缘场景）。

### Phase 1: P0 生存级（立即施工，防灾难重演）

| 顺序 | 施工项 | 防御层 | 依赖 | 预计工作量 |
|---|---|---|---|---|
| 1 | §7.1 PowerShell wrapper 函数集（git 拦截 + Remove-Item/rd/del 覆盖） | L1+L2 | 无 | 2 天 |
| 2 | §7.7 wrapper 安装脚本 | - | §7.1 | 1 天 |
| 3 | §7.2 AGENTS.md + .trae/rules/ RULE-GIT-SAFE + §7.14 fail-open 策略 | L3 | 无 | 1 天 |
| 4 | §7.23 git 危险命令阻断（v2.1.0 简化到 4 命令：filter-branch/filter-repo/reflog expire/gc --prune） | L1 | §7.1 | 0.5 天 |
| 5 | §7.17.2 .git 永久阻断（v2.1.0 §7.17.1 自动变量碰撞 deprecated，改为 RULE-GIT-SAFE 规则一条） | L4 | §7.1 | 0.5 天 |
| 6 | §7.27 审计日志（v2.1.0 简化为每 session 独立文件 audit_{yyyyMMdd}_{sessionId}.jsonl）+ §7.10 JSONL 设施 + §7.13 d6_security pre-commit | L5 | §7.1 | 1.5 天 |
| 7 | §7.32 Session ID 注入（v2.1.0 简化为 $PROFILE 顶部一行 UUID） | L6 | 无 | 0.5 天 |

**Phase 1 合计：~7 天**——完成后即具备 6 层核心防御（实现精简版）+ session 身份，22 路 AI 可安全并发审查。

### Phase 2: P1 并发协调（Phase 1 完成后）

| 顺序 | 施工项 | 类别 | 依赖 | 预计工作量 |
|---|---|---|---|---|
| 8 | §11.3.2 File Lock TTL（v2.1.0 去 heartbeat，acquire/release/check/list/cleanup 五命令 + 60min 到期释放） | 三件套-1 | §7.27 | 1 天 |
| 9 | §11.3.3 Task Board（v2.1.0 去 epoch/blocked/abandoned，SQLite CAS + WAL + pending→claimed→completed 三态） | 三件套-2 | §7.32 | 1.5 天 |
| 10 | §11.3.1 Git Worktree（v2.1.0 去 7 天告警，create/exec/merge/abort/list + merge 后立即 abort） | 三件套-3 | §11.3.3 | 1.5 天 |

**Phase 2 合计：~4 天**——完成后即具备 22 路并发审查的完整协调层（Task Board 防重复认领 + File Lock 防同时改 + Worktree 物理隔离）。

### 远期评估（不施工，仅记录）

| 项目 | 评估时机 | 说明 |
|---|---|---|
| §7.3-§7.6 / §7.8 / §7.9 / §7.12 | Phase 1 完成后 | 配套确认/激活项，按需推进 |
| §7.11 Trash Redirect 算法 | Phase 2 完成后 | 回收站重定向，§7.1.2 阻断已够安全，trash 是体验优化 |
| §11 三件套的 v1.5.0 升级方向（Phi Accrual / heartbeat / epoch 等） | 远期 | v2.1.0 已砍，固定 TTL 60min + 基本 CAS 已够 22 路审查 |
| v2.0.0 deprecated 的 14 项（§7.16/§7.19-§7.26/§7.29/§7.30/§7.33-§7.36） | 不评估 | 详见 §6.2 + §9，单人 AI 协作无 adversarial 场景 |
| v2.1.0 deprecated 的 3 项（§7.15/§7.17.1/§7.18） | 不评估 | 详见 §6.2 + §9，AI 不会混淆命令/碰撞变量/需要 STOP 格式教学 |

**总计：Phase 1 (7天) + Phase 2 (4天) = ~11 天**

> 对比历程：v1.x 37 天 → v2.0.0 17 天 → **v2.1.0 11 天**，累计减 70%。覆盖 22 路并发审查 + 未来多 AI 施工的全部真实场景（AI 误删文件 + 多 AI 共用工作区冲突）。6 层防御结构不变，实现大幅简化。

## 14. ~~灾难恢复计划~~（v2.0.0 删除）

> **v2.0.0 删除理由**：v1.x §14 的 Named Pipe Daemon 崩溃恢复 / SQLite 损坏恢复 / Wrapper Bug 恢复 / RPO/RTO 指标——其中 Daemon 崩溃恢复依赖 §7.33 Named Pipe Daemon（已 deprecated）；SQLite 损坏恢复用 `sqlite3 .recover` 是标准操作无需专节；RPO/RTO 是 SRE 话术对个人 AI 开发项目过度。容错由 SQLite WAL + JSONL append-only + git 版本控制天然提供，无需单独章节。

## 15. ~~性能影响评估~~（v2.0.0 删除）

> **v2.0.0 删除理由**：v1.x §15 评估的是 12 层防御的开销——v2.0.0 精简到 6 层后，开销总计 <3ms/命令（git 命令本身 >100ms），无需逐层评估。22 session 并发场景由 SQLite WAL + busy_timeout 工业级方案承载，无需单独性能章节。

## 16. 修订记录

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
| 2026-08-11 | 1.5.0 | 第14轮审查修复（第七轮全网搜索+13项缺失/升级算法补充）：①§3.10 新增第七轮搜索补充15子节——GuardFall证明正则/AST单层防护不够（5大绕过类）/AgentTrust四大算法创新（Shell deobfuscation normalizer+SafeFix+RiskChain+cache-aware LLM-as-Judge）/Codex $home真实事故（PowerShell自动变量碰撞致%USERPROFILE%递归删除）/Zed 1.14.2首个OS级AI agent沙箱（.git写入永久阻断）/Pillar Trust Handoff Flaw/CFD攻击证明per-call guardrail根本缺陷（+28pp jailbreak）/IETF AAT审计日志hash chaining标准/grite git-native+CRDT事件日志+advisory leases（file-based tracker静默丢并发写）/Phi Accrual Failure Detector/CoAgent MTPO advisory concurrency+LLM-as-judge范式转变/SQLite CAS模式（epoch防ABA+WAL）/Microsoft Defender AI agent protection/Trae SOLO单agent loop澄清/Vibe Kanban bloop关停状态更新；②§6.2 防御层从9层扩展到13层（新增L10 Shell反混淆归一化层/L11 PowerShell自动变量碰撞检测+.git永久阻断/L12 SafeFix block+suggest/L13 RiskChain session级攻击链追踪）；③§7.17 新增施工项17：PowerShell自动变量碰撞检测（30+只读自动变量清单+_ZephyrCheckVarCollision函数+PSReadLine集成）+.git目录写入运行时硬阻断（_ZephyrCheckGitDirProtection函数，参考Zed 1.14.2 kernel级设计）；④§7.18 新增施工项18：Shell反混淆归一化层（9策略算法：相邻引号拼接/ANSI-C quoting/hex转义/八进制转义/$IFS展开/Base64 decode检测/命令替换标记/反引号替换/变量展开检测+_ZephyrDeobfuscate函数集成到wrapper）；⑤§7.19 新增施工项19：SafeFix block+suggest算法（7条规则库+_ZephyrSafeFix函数，AI看到SAFEFIX后直接执行替代命令不重试）；⑥§7.20 新增施工项20：RiskChain session级攻击链追踪（6类可疑链模式+风险分阈值50/80/100三级响应+_ZephyrRiskChainRecord函数持久化到JSONL）；⑦§7.21 新增施工项21：Risk-tiered fail mode（升级§7.14二分法为四级：🟢低风险fail-open/🟡中风险fail-closed默认/🟠高风险fail-closed强制/🔴CRITICAL fail-closed永久+_ZephyrGetRiskTier+_ZephyrFailMode函数）；⑧§7.22 新增施工项22：跨工具/跨shell绕过检测（三类绕过：换路径canonicalize/换shell normalize/换工具RiskChain追踪+_ZephyrCanonicalizePath+_ZephyrCheckBypass函数）；⑨§8.7-8.9 新增21个验证测试用例（自动变量碰撞/.git永久阻断/反混淆5大绕过类/SafeFix/RiskChain三级响应/Risk-tiered fail mode/跨工具绕过检测）；⑩§9 不做什么新增8条（不实现tokenize-then-check/不引入沙箱重申/不引入Microsoft Defender/不实现跨session RiskChain/不实现CoAgent MTPO/不引入Raft-Paxos/不引入Redis重申）；⑪§10 开放问题新增9条；⑫§11.1.1 澄清Trae SOLO单agent loop语义+grite C2证实file-based tracker静默丢并发写；⑬§11.2.1 主流工具对标新增5项（grite/CoAgent MTPO/Agentlocks/SQLite CAS/Vibe Kanban状态更新+Anthropic报告token消耗15×澄清）；⑭§11.3.2 新增Phi Accrual升级方向（φ>3 lease-renew/φ>8 lease过期，替代固定TTL 60min）；⑮§11.3.3 SQLite schema新增epoch字段防ABA+CAS单语句原子claim+WAL模式+TTL 60s=4×15s heartbeat；⑯frontmatter 新增3个ARCH议题（#ARCH-GIT-DEOBFUSCATOR/#ARCH-GIT-VAR-COLLISION/#ARCH-GIT-RISKCHAIN）；⑰设施总数标注v1.5.0新增6项待施工（L10-L13防御层） | 第七轮全网搜索2026年8月最新研究（GuardFall/AgentTrust/Codex $home事故/Zed沙箱/Pillar Trust Handoff/CFD/IETF AAT/grite/CoAgent MTPO/Phi Accrual/SQLite CAS/Microsoft Defender）+13项缺失/升级算法补充+Trae SOLO单agent loop语义澄清+Vibe Kanban状态更新 |
| 2026-08-11 | 1.6.0 | 第15轮审查修复（第八轮全网搜索+PS 5.1兼容性修复+git专属攻击向量+Windows专用防御层）：①**P0 关键bug修复**：v1.5.0代码5处`?.`运算符（PS 7.1+专有）在PS 5.1上必然报错——全部替换为PS 5.1兼容的`if`判断模式（§7.1.2/§7.11/§7.17.2/§7.22.2）；②**P0 设计缺陷修订**：§7.17.1 PSReadLine集成方案根本性缺陷——PSReadLine仅在交互式REPL中工作，对AI agent通过-Command/-File/-EncodedCommand调用的脚本完全无效，删除PSReadLine方案改用wrapper函数内检测+4104事后审计；③§3.11 新增第八轮搜索补充15子节——PS 5.1兼容性清单（7种PS 7+语法不兼容）/PSReadLine对AI agent脚本无效/git config注入攻击CVE-2026-44244/67326（GitPython换行符注入→hooksPath RCE）/git worktree沙箱逃逸CVE-2026-55607（worktree名.git→gitdir混淆→fsmonitor执行→逃逸Seatbelt）/git filter-repo AI agent误用GhostXia/AIRP#104/git reflog expire+gc --prune forensic证据抹除/git update-index绕过commit gate jwbron/egg#277/git notes侧信道持久化spelunk#344/git apply符号链接重放codex-plugin-cc#13/git submodule路径穿越写.git/hooks dulwich GHSA/Microsoft MXC官方AI agent沙箱（10个containment backends）/PowerShell Script Block Logging 4104（引擎级审计）/symlink+junction+TOCTOU结构性缺陷（CVE-2026-23988）/2026-07/08 AI agent+git重大攻击事件汇总（GitLost/Novee BlackHat/FakeGit/Miasma蠕虫/Cline Trojan/GitInject）；④§6.2 防御层从13层扩展到16层（新增L14 symlink/junction+TOCTOU防护/L15 git hook信任链+worktree安全+reflog不可变窗口/L16 Script Block Logging 4104集成）；⑤§7.23 新增施工项23：git专属危险命令阻断列表扩展（20+命令：git config core.hooksPath/fsmonitor/filter-branch/filter-repo/reflog expire/gc --prune/update-index --cacheinfo等/notes/hash-object -w/apply symlink/submodule/init --template/push --receive-pack+git log强制--no-notes）；⑥§7.24 新增施工项24：symlink/junction+TOCTOU防护——Atomic Path Resolution算法（P/Invoke CreateFile+FILE_FLAG_OPEN_REPARSE_POINT+GetFinalPathNameByHandle+handle保留到操作完成，PS 5.1通过Add-Type内联C#实现）；⑦§7.25 新增施工项25：git hook信任链加固（hooksPath白名单+SHA256 hash锁定+.hook_hashes文件）+worktree安全加固（拒绝worktree名含.git+强制fsmonitor none+校验.git realpath不在home/ssh/config）+reflog不可变窗口（expire/gc --prune前强制落盘外部审计）；⑧§7.26 新增施工项26：Script Block Logging 4104集成（EnableScriptBlockLogging注册表+通道扩展1GB+4104 EventRecordId绑定到_ZephyrAuditLog JSONL）；⑨§9 不做什么新增5条（不引入MXC/不引入WDAC+CLM/不引入Job Object/不引入PSReadLine集成修订）；⑩§10 开放问题新增5条；⑪frontmatter 新增3个ARCH议题（#ARCH-GIT-CVE-2026-44244/#ARCH-GIT-CVE-2026-55607/#ARCH-GIT-TOCTOU） | 第八轮全网搜索2026年8月最新研究（PS 5.1兼容性+git专属攻击向量CVE-2026-44244/67326/55607+Windows MXC/4104/symlink/TOCTOU）+5处PS 5.1不兼容`?.`修复+PSReadLine设计缺陷修订+20+git专属攻击命令阻断+Atomic Path Resolution算法+git hook信任链加固+worktree安全+reflog不可变窗口+4104集成 |
| 2026-08-11 | 1.7.0 | 第16轮审查修复（第九轮全网搜索+Trae多AI并发病根分析+3个P0并发bug修复+跨session GovernanceStore）：①**§3.12 新增第九轮搜索补充7子节——Trae多AI并发病根分析**：病根定位（Trae每session独立PowerShell进程✅但共享状态文件read-modify-write竞态❌——7个共享文件清单：audit JSONL/registry.json/.trae/rules/AGENTS.md/.git/index/$_circuitState/$_riskChain）；Claude Code .claude.json 423次跨session损坏决定性证据；f2t.jp AI session并发git index抢占案例（git add A B后commit进去C D E）；PowerShell并发文件写入安全算法（命名Mutex+temp+rename原子写+StreamWriter+每session独立文件4种方案，PS 5.1兼容性确认）；OpenClaw GovernanceStore RFC #27442（跨session circuit breaker/kill switch）；WOWHOW Single-Push Protocol（4阶段多agent git串行化）；Trae病根治本方案三层架构（L1进程隔离+L2共享状态串行化+L3跨session协调）；②**§7.27 新增施工项27（P0）：审计日志并发安全修复**——_ZephyrAuditLog用命名Mutex（Global\ZephyrAuditLogMutex）串行化StreamWriter并发append+5秒timeout降级到session独立文件（防26 session并发数据交错/丢失，PowerShell #24774+Claude Code #29217前车之鉴）；③**§7.28 新增施工项28（P0）：lock_files.py registry.json并发安全升级**——过渡方案（Windows全局命名Mutex CreateMutexW+WaitForSingleObject串行化RMW+temp+rename原子写pathlib.Path.replace）+最终方案（迁移到SQLite WAL CAS单语句原子claim ON CONFLICT DO UPDATE+epoch防ABA，与§11.3.3 Task Board统一）；④**§7.29 新增施工项29（P1）：跨session GovernanceStore**——共享SQLite governance.db（circuit_breakers表+risk_chains表+governance_flags表）+全局halt检查（任何session可设置所有session遵守）+3+session同时熔断自动触发global halt+UPSERT原子写；⑤**§7.30 新增施工项30（P1）：共享规则文件完整性防护**——.trae/rules/AGENTS.md SHA256 hash基线监控+每次git命令前检查+hash不匹配告警+RiskChain风险分增加+AGENTS.md Boundaries段声明禁改文件清单；⑥**§7.31 新增施工项31（P1）：git并发操作串行化**——commit前git diff --cached --stat暂存内容验证（防另一session的add污染）+GIT_OPTIONAL_LOCKS=0给后台watcher+GitCommitGateway single-flight命名Mutex串行化所有commit（Global\ZephyrGitCommitGateway 30秒timeout）；⑦§6.2 防御层从16层扩展到18层（新增L17并发安全串行化/L18跨session GovernanceStore）；⑧§9 不做什么新增1条（不引入ACP）；⑨§10 开放问题新增4条（GovernanceStore SQLite依赖部署/跨session global halt误触发风险/lock_files.py SQLite迁移时机/Trae Hooks配置可行性）；⑩frontmatter 版本1.6.0→1.7.0 | 第九轮全网搜索2026年8月最新研究（Trae多session架构实证+PowerShell并发文件写入安全+Claude Code .claude.json 423次损坏+f2t.jp git index抢占+OpenClaw GovernanceStore RFC+WOWHOW Single-Push）+3个P0并发bug修复（审计日志Add-Content/registry.json RMW/circuitState per-session）+跨session GovernanceStore+共享规则文件完整性防护+git并发操作串行化 |
| 2026-08-11 | 1.8.0 | 第17轮审查修复（第十轮全网搜索+Named Pipe 单线程协调器+Session 身份+Trae Hooks+Hybrid 架构）：①**§3.13 新增第十轮搜索补充7子节——深层病根分析**：核心发现 Named Pipe 单线程协调器优于 Mutex+SQLite（rjmurillo/ai-agents #287 性能 10-50ms + Rutgers CS 417 单机集中式协调最优理论 + Reactor pattern）；Trae SessionStart hook 可通过 TRAE_ENV_FILE 注入 ZEPHYR_SESSION_ID（解决 v1.7.0 session_id 无注入源 gap）；Trae 七事件 Hook 模型（SessionStart/End/PreToolUse/PostToolUse/UserPromptSubmit/Stop/PreCompact）；PS 5.1 NamedPipeServerStream 完整支持（ResidentDaemon 2026-04 生产级实现 + Start-Process 独立进程）；SQLite busy_timeout=5000 + BEGIN IMMEDIATE 配置；Hybrid 架构（Named Pipe 实时协调 ~50μs + SQLite WAL 持久审计）；②**§7.32 新增施工项32（P0）：Session ID 注入机制**——Trae SessionStart hook + init-session.ps1 生成 UUID 写入 TRAE_ENV_FILE + $PROFILE 顶部 [guid]::NewGuid() fallback；③**§7.33 新增施工项33（P0）：Named Pipe Coordinator Daemon**——单进程单线程事件循环 NamedPipeServerStream + 内存状态（锁/circuitBreakers/riskChains/globalHats）+ SQLite WAL 异步审计 + 7 action 协议（acquire_lock/release_lock/check_circuit/record_block/record_success/register_session/unregister_session）+ Start-Process 独立进程 + Global Mutex 防双重启动 + 项目 hash 跨项目隔离 + wrapper pipe client + v1.7.0 fallback；④**§7.34 新增施工项34（P1）：Session 生命周期管理**——Trae SessionEnd hook + cleanup-session.ps1 通过 pipe 注销 session 自动释放锁 + daemon heartbeat 30 分钟超时清理；⑤**§7.35 新增施工项35（P1）：Wrapper 热重载+版本管理+跨项目隔离**——版本化 $PROFILE + Reload-Profile 函数 + 协议版本协商 + Mutex 项目路径 hash 后缀 + SQLite busy_timeout=5000 配置；⑥§6.2 防御层新增 L19（Named Pipe 单线程协调器+Session 身份+生命周期管理）；⑦frontmatter 版本 1.7.0→1.8.0 | 第十轮全网搜索2026年8月最新研究（rjmurillo named pipe daemon/ResidentDaemon 生产级/Trae SessionStart hook TRAE_ENV_FILE/Microsoft AGT/Rutgers CS 417 单机集中式协调/SQLite busy_timeout/WOWHOW Single-Push）+Named Pipe 单线程协调器架构升级（从"用锁管理并发"到"用单线程消除并发"）+Session ID 注入+生命周期管理+热重载+跨项目隔离 |
| 2026-08-11 | 1.9.0 | 第18轮审查修复（第十一轮全网搜索+诚实评估+AST 升级+施工路线图+灾难恢复+性能评估）：①**§3.14 新增第十一轮搜索——诚实评估**：v1.8.0 基本到达边际收益递减点。评估 8 个底层方案（eBPF/AST/Process Mitigation/Git Alternates/ETW/MIC/CLM/Windows Sandbox），仅 AST 分析明确更优，其他均不适用（eBPF 未签名/Sandbox 单实例/CLM 系统级/MIC 破坏性/ETW 仅审计/Git Alternates 不解决 index 锁）；②**§7.36 新增施工项36（P1）：AST-based 命令分析**——`[Parser]::ParseInput()` 结构化遍历 AST 节点检测 6 类危险模式（命令替换/$IFS/Invoke-Expression/Add-Type/base64/pipe-to-shell），覆盖 GuardFall 3/5 类，~1ms/call，PS 5.1 原生支持；③**§13 新增施工路线图**——36 施工项分 4 Phase（Phase 1 P0 生存级 10.5 天/Phase 2 P1 并发安全 23 天/Phase 3 P2 审计增强 3.5 天/Phase 4 P3 远期评估），总计 ~37 天，含依赖关系和工作量估算；④**§14 新增灾难恢复计划**——Daemon 崩溃自动重启+SQLite 损坏恢复+Wrapper Bug 恢复+RPO 0/RTO <30s/锁状态 RPO 0-60min；⑤**§15 新增性能影响评估**——每次 git 命令防御层开销 ~4-5ms（可忽略），26 session 并发 commit single-flight 串行化 ~52s，Daemon 内存 ~50MB，4 条优化建议（只读跳过/AST 缓存/规则检查降频/审计批量写入）；⑥§12→§16 重编号；⑦frontmatter 版本 1.8.0→1.9.0 | 第十一轮全网搜索2026年8月最新研究（eBPF for Windows/PowerShell AST/Process Mitigation/Git Alternates/ETW/MIC/CLM/Windows Sandbox）+诚实评估确认 v1.8.0 边际收益递减+AST 升级（唯一明确更优算法）+施工路线图+灾难恢复计划+性能影响评估 |
| 2026-08-12 | 2.0.0 | **过度工程精简大修**：v1.x 累计膨胀到 36 施工项 / 19 层防御 / 293KB / 14 轮搜索，根因是把"AI 误操作"（合法错误）误判为"AI 恶意攻击"（adversarial）——单人单账户 AI 协作开发中 AI 是协作者不是攻击者。本轮按"22 路并发审查 + 未来多 AI 施工"的真实场景精简：①**§6.2 防御层 19→6**：L1 PowerShell git wrapper / L2 原生破坏性命令覆盖 / L3 RULE-GIT-SAFE 规则 / L4 .git 阻断+变量碰撞 / L5 审计日志并发安全 / L6 Session ID 注入 + §11 三件套（Worktree+FileLock+TaskBoard）；②**14 个施工项 deprecated**（§7.16 Circuit Breaker / §7.19 SafeFix / §7.20 RiskChain / §7.21 Risk-tiered fail / §7.22 跨工具绕过检测 / §7.24 symlink TOCTOU / §7.25 git hook 信任链 / §7.26 Script Block Logging 4104 / §7.28.3 SQLite 迁移最终方案 / §7.29 跨 session GovernanceStore / §7.30 共享规则完整性 / §7.33 Named Pipe Daemon / §7.34 Session 生命周期 / §7.35 Wrapper 热重载 / §7.36 AST 升级）——每个施工项标题下加 `⚠️ v2.0.0 DEPRECATED` 标记+理由，内容保留作为决策追溯；③**§3 开头加精简说明**：§3.1-§3.5 为核心调研依据，§3.6-§3.14 为历史归档不再作为施工依据；④**§9 不做什么新增 16 条 deprecated 理由**+deprecated 根因总结；⑤**§13 路线图重写**：36 项/4 Phase/37 天 → 12 项/2 Phase/17 天，减 54%；⑥**§14 灾难恢复 / §15 性能评估删除**（保留章节号+删除理由说明）；⑦frontmatter 版本 1.9.0→2.0.0，date 2026-08-11→2026-08-12 | 用户审查后确认 v1.x 存在明显过度工程——核心诉求是"多 AI 并发施工安全"（22 路并发审查 + 未来多 AI 施工），不是"防 AI 攻击自己"。adversarial 防御层（RiskChain/SafeFix/symlink/hook hash/AST 等）误把 AI 当攻击者，全部 deprecated。Named Pipe Daemon 与 §11.3.3 Task Board SQLite 重复造轮子+单点故障，deprecated。§14 RPO/RTO 是 SRE 话术对个人项目过度，删除。§15 评估的是被砍掉的 12 层防御开销，连带删除 |
| 2026-08-12 | 2.1.0 | **第二轮过度工程精简**：v2.0.0 砍掉了宏观 adversarial 防御层，但保留项内部的实现细节仍残留 adversarial 思维。本轮再砍 3 项 deprecated + 6 项简化：①**§7.17.1 自动变量碰撞检测 deprecated**——30+ 只读变量清单+函数检测过度，Codex $home 是极端案例，改为 RULE-GIT-SAFE 一条规则；②**§7.18 反混淆归一化层 9 策略 deprecated**——全是防 shell 注入攻击，AI 不会写 `rm$IFS-rf` 混淆命令，§7.1 regex 已够；③**§7.15 错误分类 STOP/ALTERNATIVE deprecated**——AI 提示工程层过度，简单 BLOCKED 消息已够；④**§7.23 git 危险命令 20+→4 命令**——只保留 AI 易误用的 filter-branch/filter-repo/reflog expire/gc --prune，砍 16+ adversarial RCE 命令；⑤**§7.27 审计日志 Mutex→每 session 独立文件**——append-only 风险远低于状态文件，无需 Mutex；⑥**§7.32 init-session.ps1+TRAE_ENV_FILE→$PROFILE 一行 UUID**——hook 可行性是开放问题，fallback UUID 已够；⑦**§11.3.2 去 heartbeat**——22 路审查不是 7×24 长任务，TTL 60min 到期释放已够；⑧**§11.3.3 去 epoch 防 ABA+状态机精简**——ABA 在 22 路审查中几乎不会发生，状态机精简为 pending→claimed→completed；⑨**§11.3.1 去 7 天告警**——22 路审查是一次性的，merge 后立即 abort；⑩§6.2 防御层 6 层结构不变但实现大幅简化；⑪§9 新增 9 条 v2.1.0 deprecated/simplified 理由+根因总结；⑫§13 路线图 12 项/17 天 → 8 项/11 天，累计减 70%；⑬frontmatter 2.0.0→2.1.0 | 用户第二轮审查确认 v2.0.0 保留项内部仍残留 adversarial 思维——9 策略反混淆/30+ 变量检测/20+ RCE 命令/Mutex 串行化/heartbeat/epoch/init-session.ps1 均为"adversarial 攻击"或"7×24 服务"场景设计，偏离"22 路并发审查"实际诉求。v2.1.0 精简到 8 项/11 天，6 层防御结构不变但实现大幅简化 |
