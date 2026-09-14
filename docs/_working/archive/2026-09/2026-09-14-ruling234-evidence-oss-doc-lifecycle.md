---
ttl: task_bound
---

# 外部实践对照：开源社区与 AI 编程生态的"工作区/草稿文档"生命周期治理

调研日期：2026-09-14。
方法：web_search 检索 + autoglm-open-link 打开原文核实；下列每条实践均已核实到原文（标注"经 raw 核实"的为 raw.githubusercontent.com 原文，与 GitHub blob 页同源）。
背景：ZephyrAlpha monorepo 的 docs/_working/（zone=temporary，120 tracked 文件容量上限，顶格拦截一切提交，人工归档到 docs/_working/archive/YYYY-MM/ 或 docs/_archive/）。

---

## 维度一：开源社区 docs / 工作目录治理

### 1. actions/stale：TTL 两阶段"先标记、后关闭"自动化（GitHub 官方 Action）
- 机制：按 cron 定时扫描，60 天无活动先打 Stale 标签并评论，再过 7 天仍无活动才关闭；任何更新/评论即重置计时器，`exempt-*-labels` 可豁免指定内容，`debug-only` 支持干跑。
- 来源：https://github.com/actions/stale （README 原文核实：days-before-stale=60、days-before-close=7 默认值、豁免标签、状态重置逻辑）
- 可借鉴点：把"120 顶格即全面阻断"改造为两阶段"TTL 预警 → 到期自动归档"——先对 N 天未变更文档打标/列清单（不阻断），到期再自动移入 archive/YYYY-MM/，容量上限降级为告警线；豁免标签机制等价于保护"跨会话在途"文档。

### 2. Chromium Documentation Guidelines：docs 治理靠"耐久文档少而精、贴近代码、轻量审核"的约定
- 机制：基于"所有文档都是错的且会过时"的原则，把耐久文档压缩为三层（组件 README.md / 接口注释 / 实现注释）并要求自包含组件目录必有 README 说明边界；文档改动只需 TBR 轻量审核（不设数量门槛）。
- 来源：https://github.com/chromium/chromium/blob/main/docs/documentation_guidelines.md （经 raw 核实）
- 可借鉴点：明确"什么才配成为耐久文档"并把耐久/临时的边界写进约定，使 docs/_working/ 只收留真正的临时件，缩小需要容量治理的范围。

### 3. 目录容量 lint（数字文件数硬上限 + 顶格阻断）：未找到
- 检索了多组查询（Chromium PRESUBMIT directory size/limit、LLVM/AOSP 目录治理、monorepo 结构检查等），未找到任何大型开源项目对 docs/ 或工作目录设"数字文件数上限、超限即拦截提交"的公开证据；外部主流替代机制是 TTL 标记（actions/stale）、所有权（OWNERS/CODEOWNERS）与文档约定（如上）。
- 结论：如保留 120 上限，建议参照条目 1/4 降级为告警并叠加自动化归档路径，而非唯一的硬闸门。

---

## 维度二：AI 编程生态对会话过程产物的处置

### 4. OpenHands SDK：`.pr/` PR 域临时产物区 + 事件驱动自动清理
- 机制：仓库约定把"只给评审者看、不进 main"的设计文档/脚本/验证证据放进根目录 `.pr/`（明确 "intentionally temporary"）；PR 被批准时 CI 工作流自动删除该目录；若产物泄漏进 main，工作流自动开 cleanup PR 清理。
- 来源：https://github.com/OpenHands/software-agent-sdk/blob/main/AGENTS.md （经 raw 核实，`<PR_ARTIFACTS>` 节，配套 `.github/workflows/pr-artifacts.yml`）
- 可借鉴点：把临时区生命周期绑到"事件"（评审通过/合并）而非"数量"——每个任务的 AI 交接文档在合并时自动归档/清除，可替代绝大部分人工归档动作。

### 5. OpenHands SDK：`.agent_tmp` 统一 agent 临时输出目录约定
- 机制：所有工具产生的观察文件（浏览器录制、任务跟踪数据等）统一写入约定名 `.agent_tmp/`，使其可整体加进 .gitignore、会话后可整体清理、且可识别为 agent 生成物（与会话持久化目录分离）。
- 来源：https://github.com/OpenHands/software-agent-sdk/blob/main/AGENTS.md （经 raw 核实，`<AGENT_TMP_DIRECTORY>` 节）
- 可借鉴点：让 AI 会话把过程性产物（运行记录、中间输出）写进单一约定目录并整体 gitignore，tracked 容量只留给真正需要跨会话的交接文档。

### 6. Claude Code：工具层自动 git exclude，个人/会话产物默认不入库
- 机制：`.claude/settings.local.json`（个人覆盖、会话内权限批准）首次写入时由工具自动加入 git 全局 excludes 文件从而永不进提交；仅团队共享的 `.claude/settings.json` 建议提交。
- 来源：https://code.claude.com/docs/en/settings （原文核实："Claude Code adds it to your global git excludes … so it stays out of your commits"）
- 可借鉴点："会话级/个人级产物默认 untracked，共享耐久物才入库"可以由工具自动执行，不依赖人的自觉或事后 gate 拦截。

### 7. Aider：会话历史默认留本地，分享是显式动作
- 机制：聊天记录 `.aider.chat.history.md` 与输入历史是本地文件，aider 自身仓库的 .gitignore 收录整个 `.aider*` 模式；需要分享时由用户手动导出 gist 生成链接，而非提交进仓库。
- 来源：https://aider.chat/docs/faq.html （原文核实：从 `.aider.chat.history.md` 复制日志分享的指引）+ https://raw.githubusercontent.com/Aider-AI/aider/main/.gitignore （经 raw 核实：`.aider*` 条目）
- 可借鉴点："默认本地、opt-in 入档"给 docs/_working/ 一个目标比例：多数会话草稿不必进 tracked，只有提炼的交接摘要被显式晋升入库。

### 8. OpenClaw：agent 记忆/工作区与项目仓库彻底分离
- 机制：agent 工作区（AGENTS.md、memory/YYYY-MM-DD.md、MEMORY.md 等）位于独立的私有 git 仓库（~/.openclaw/workspace），会话/运行时状态（sessions、sqlite、credentials）被明确列为 "should NOT be committed"；项目仓库只放项目本体。
- 来源：https://docs.openclaw.ai/concepts/agent-workspace （原文核实）
- 可借鉴点："跨会话记忆"与"项目交付物"可以是两个存储体：会话交接草稿放 agent 工作区或仓库外暂存区，只把提炼结论 promote 进 docs/，从源头减少 tracked 容量压力。

### 9. Seroter 实践：策展式"会话摘要"显式入库（对照面：入库的另一极）
- 机制：用 AGENTS.md 规则 + team-sync skill 在会话结束后，把策展过的 summary.md（TL;DR、关键决策、验证、教训）与 transcript 复制到 `.antigravity/history/<conversation-id>/` 并随代码一起提交——过程产物入库不是默认倾倒，而是"策展 + 按会话 ID 归位"。
- 来源：https://seroter.com/2026/07/22/how-to-share-agentic-coding-artifacts-with-your-teammates/ （原文核实）
- 可借鉴点：若确有保留 AI 决策上下文的需求，"交接摘要模板（TL;DR + 决策 + 验证）"比保留全文交接档更省容量；全文走本地或 archive。

---

## 总评（对 ZephyrAlpha 的可迁移组合）

- 外部开源社区未发现"数字容量上限 + 顶格全面阻断"的先例；主流是 TTL 标记（条目 1）、约定收窄（条目 2）、事件驱动自动清理（条目 4）。
- AI 生态共识：过程产物默认不入库（条目 5/6/7/8 的 gitignore/exclude/分离工作区），入库只有两种合法通道——策展晋升（条目 9）或作用域化临时区 + 自动清理（条目 4）。
- 可迁移组合：① docs/_working/ 加 TTL 预警层（先打标不阻断）；② 把归档绑定到会话收尾事件（任务合并后自动归档/晋升该会话文档）；③ 过程性产物迁入整体 gitignore 的约定目录（.agent_tmp 模式）；④ 120 上限保留为告警线而非唯一硬闸门。
