---
module_id: MOD-INF-017
doc_type: blueprint
status: Draft
layer: L01
version: 0.10.0
owner: ZephyrAlpha-Owner
classification: internal
language: zh
created_by: AI
date: "2026-05-05"
valid_from: "2026-05-05"
ttl: permanent
construction_progress: not_started
belongs_to: MOD-MASTER-001
depends_on:
  - MOD-INF-005
  - MOD-INF-007
  - MOD-INF-008
  - MOD-INF-010
  - MOD-INF-016
  - MOD-INF-012
references:
  - {id: "MOD-INF-005", at: "§6", why: "退出码约定 0/1/2/3/4 + Finding Schema + manifest 注册契约"}
  - {id: "MOD-INF-007", at: "§3", why: "GATE-DEDUP pre-commit 门禁判定逻辑——Wave 1 即落地"}
  - {id: "MOD-INF-008", at: "§2~§4", why: "生成时注入共享API影子清单——防重第一道防线 + 消费验证回环"}
  - {id: "MOD-INF-010", at: "§3~§5", why: "重复模式→FLE→evolve()→EvolutionProposal 进化闭环"}
  - {id: "MOD-INF-016", at: "§2", why: "SSoT Guard + shared 目录结构——去重后的提取目标"}
  - {id: "MOD-INF-012", at: "§3", why: "发现的重复模式/健忘热点→KB持久化→未来AI session 主动查阅"}
title: "代码去重引擎蓝图 — Monoculture免疫 · 原子修复 · 决策审计链 · 主动发现 · 漏报可视 · 微克隆感知 · 测试生成 · 契约验证 · 跨边界 · 全生命周期治理 · 自审计闭环"
summary: "Monoculture免疫（去重成功=代码库脆弱性上升——Blast Radius Score追踪单点故障爆炸半径）+ 原子性修复（WAL式fix_plan+崩溃恢复——中断操作不留代码库不一致状态）+ 决策审计链（DecisionFingerprint不可变追加日志——'我没看的时候引擎做了什么？'——对标Google Tricorder/Meta Sapienz证据链）+ 主动函数发现（签名驱动+语义驱动双通道——不等AI犯错，主动告知'这个功能已存在'——对标Sourcegraph Cody/Google Code Search）+ Grandfather三定律（30天以上古老重复不自动修复）+ 漏报盲审（Sensitivity Sweep影子低阈值扫描+Canary注入+抽样审查——'请证明没有系统性遗漏'）+ Shadow Manifest信任链验证（AI幻觉函数→ImportError防护回路+行为正确性验证）+ Temporal Signature Drift追踪（渐进类型化打破指纹缓存）+ 引擎成本效益自审计（Simplicity Audit——'引擎自己是否已成为最重的技术债'）+ 死共享模块检测 + 提取后稳定观察期 + 恢复失败的恢复 + 噪声信号比主题聚类 + 并发修改检测 + 微型克隆检测（n-gram频率计数——AI生成的高频1-2行模式聚合）+ 提取后自动测试生成（类型驱动+金丝雀录制+契约测试——BRS缓解的落地机制）+ API契约一致性验证（存在性+行为正确性+契约一致性三维信任模型）+ 跨边界克隆感知（src/tests/scripts/L01-L05/ vendored四大边界差异化策略）——去重最大化悖论：不是消除所有重复，而是找到'去重收益 vs Monoculture风险 vs 碎片化风险 vs 引擎维护成本'的四体最优边界。"
tags:
  - code-dedup
  - deduplication
  - ast-analysis
  - semantic-similarity
  - code-quality
  - infrastructure
  - full-lifecycle
  - incremental-scanning
  - auto-fix
  - pre-commit-gate
  - ssot-integration
  - feedback-loop
  - signature-fingerprint
  - code-health
  - degraded-mode
  - policy-tree
  - vibe-coding
  - extraction-safety
  - project-scale-aware
  - partial-extraction
  - dedup-debt
  - self-dogfooding
  - doom-loop-prevention
  - shared-lifecycle
  - import-surface-area
  - behavioral-sampling
  - design-pattern-whitelist
  - monoculture-immunity
  - atomic-fix-crash-recovery
  - grandfather-laws
  - false-negative-audit
  - shadow-manifest-trust
  - temporal-signature-drift
  - blast-radius-score
  - self-audit
  - simplicity-audit
  - dead-module-detection
  - observation-window
  - staged-rollout
  - recovery-from-recovery
  - thematic-clustering
  - signal-to-noise
  - behavioral-trust
  - concurrent-modification-detection
  - micro-clone-detection
  - auto-test-generation
  - contract-consistency
  - cross-boundary-clone
  - decision-audit-trail
  - active-function-discovery
priority: P2
---

# 代码去重引擎（Code Dedup Engine）蓝图 — Monoculture免疫 · 原子修复 · 决策审计链 · 主动发现 · 漏报可视 · 微克隆感知 · 测试生成 · 契约验证 · 跨边界 · 全生命周期 · 自审计

> **module_id**: MOD-INF-017 | **version**: 0.10.0 | **status**: draft | **layer**: l01_infrastructure

> **v0.10.0 关键升级**：解决1人+AI维护场景的终极信任问题——"我没看的时候引擎做了什么？" + "AI如何主动找到已有函数而不是等着被拦截？"
> 补入 2 个第九次审计发现的运维级盲点：
> ①**去重决策审计链**（Decision Audit Trail——DecisionFingerprint不可变追加日志 + 证据包 + 可回滚——"休假2周回来，知道引擎做了什么、为什么做、怎么撤销"——对标Google Tricorder/Meta Sapienz/Netflix Staged Rollout Decision Log）+ 
> ②**共享函数主动发现**（Active Function Discovery——签名驱动+语义驱动双通道——不等AI犯错，主动告知已有实现——从"被动拦截→主动赋能"——对标Sourcegraph Cody/Google Code Search）。

> **v0.9.0 关键升级**：与专业机构（Google/Meta/JetBrains）及学术界（MSR 2024/ICPC 2023/Google Testing Culture）最后差距弥合。
> ①**Monoculture免疫**（Blast Radius Score——去重成功的悖论：消除重复=所有caller共享同一bug=单点故障爆炸半径增大N倍）+
> ②**原子性修复**（WAL式fix_plan+崩溃恢复——中断操作不留代码库不一致状态——断电/OOM/crash后自动恢复）+
> ③**Grandfather三定律**（30天以上古老重复永不自动修复+60天以上进入"化石记录"——古老纠缠是挖不得的考古禁区）+
> ④**漏报盲审**（Sensitivity Sweep影子低阈值扫描+Canary故意注入已知重复+抽样人工审查——"请证明没有系统性遗漏"）+
> ⑤**Shadow Manifest信任链验证**（AI幻觉函数→ImportError防护回路——引擎生成的影子清单中的函数必须可import，否则自动清除）+
> ⑥**Temporal Signature Drift**（渐进类型化打破指纹缓存——`Optional[str]`→`str`→`float | None`的类型演化→签名指纹漂移检测+自动重算）。

> **v0.8.0 终极升级**：外部取证审计师的致命追问——"你自己值得存在吗？"。
> 补入 7 个前六次审计全部遗漏的递归悖论：
> ①**引擎成本效益自审计**（Simplicity Audit——SAS 0-100 + "33模块引擎自己是否已成为项目最重的技术债"——每月强制自评估，NET_NEGATIVE→自动退役建议）+
> ②**死共享模块检测**（整个 shared/ 子模块所有函数退役→DEAD→自动标记删除——补全生命周期管理的模块级维度）+
> ③**提取后稳定观察期**（Microsoft SDP/Netflix Staged Rollout 工业实践——提取→14天观察→验证稳定→下一轮——防止隐藏bug在观察期才暴露）+
> ④**恢复失败的恢复**（Recovery-from-Recovery——tar.gz损坏→R2纯文本Recovery Manifest→R3 git恢复→防止恢复机制本身的单点故障）+
> ⑤**噪声信号比·主题聚类摘要**（50组重复→3个主题——IEEE TSE研究：第20条告警后审查准确率从85%→40%）+
> ⑥**影子清单行为正确性验证**（从"函数存在"升级到"函数行为正确"——原始行为签名+每次全量扫描重新采样验证+行为漂移告警）+
> ⑦**并发源文件修改检测**（Pre-Apply Integrity Gate——修复APPLY前重新验证目标文件未被外部进程修改——防止PREFLIGHT→APPLY窗口中的并发写入破坏）。

> **v0.9.0 关键升级**：与专业机构（Google/Meta/JetBrains）+ 学术界（MSR 2024/ICPC 2023/Google Testing Culture）最后差距弥合。
> 补入 4 个前七次审计全部遗漏的行业级盲点：
> ①**微型克隆检测**（Micro-Clone Detection——1-2行高频模式n-gram频率计数——Vibe Coding场景下微克隆密度是传统项目的3.8倍——MSR 2024）+ 
> ②**提取后自动测试生成**（Auto-Test-Gen Pipeline——类型驱动边界测试+执行轨迹金丝雀录制+调用方契约测试——对标Google Mozart/Test Certified——BRS缓解的落地机制）+ 
> ③**API契约一致性验证**（Contract Consistency——存在性·行为正确性·契约一致性三维信任模型——对标Google Tricorder/Meta Pyre——防止docstring/类型注解/影子清单描述腐烂）+ 
> ④**跨边界克隆感知**（Cross-Boundary Clone Awareness——SRC_TEST_BRIDGE/SRC_SCRIPTS_DIVERGENCE/CROSS_LAYER_REDUNDANCY/VENDORED_REIMPLEMENTATION 四大边界差异化策略——对标Google Blaze/JetBrains IntelliJ 2025.1）。

> **v0.6.0 核心升级**：从"安全提取+规模自适应+债务规划"升级为"自保护+防退化+全生命周期治理"。
> 补入第三轮深度审计发现的 17 个新盲点：引擎自保护与Dogfooding（引擎扫描自己）、Codegen覆盖防护（BLIND-CODGEN-INIT-OVERWRITE）+
> Doom Loop检测与修复升级阶梯（回滚→部分提取→停止→Owner告警）+ 行为采样验证（低测试覆盖安全网——采样输入→输出diff验证）+
> 共享函数生命周期管理（Deprecation→Grace Period→Sunset→Retirement）+ Import表面积负债追踪（Shared Burden Score——共享越多耦合越重）+
> 设计模式白名单（Strategy/Adapter/Factory/Template Method——结构相似但语义独立）+
> 引擎冷启动问题（首次运行无缓存——全量扫描性能预期）+ 多Session去重状态机（Session A检测→Session B修复→Session C继续——状态一致性）+
> 去重幂等性保证深度（MinHash概率性→确定性哈希+缓存签名+版本锁定）+
> 跨AI工具影子清单适配（Claude/GPT-5/Gemini的不同上下文格式）+ LLM跨文化偏倚（中文命名函数判断可靠性）。

> **v0.5.0 核心升级**：从"代码健康平台"升级为"安全提取 + 规模自适应 + 债务规划"三位一体。
> 补入第二轮深度审计发现的 12 个新盲点：提取适配性评估（Suitability Score）、项目规模感知阈值（5000行魔咒自适应）、
> 不安全提取模式目录、过期共享函数检测、部分共享提取（LCS核心+差异保留）、去重债务还本付息规划、
> 提取影响预分析、引擎自观性指标（FPR/检测延迟/修复成功率/缓存命中率）、
> 重复引入速率追踪、Knowledge Base持久化、@generated-code排除、多语言边界优雅跳过。

---

## §1 问题陈述

### 1.1 现象

Vibe Coding AI 的上下文记忆极短（AGENTS.md §5.1），每次新 session 不知道已有代码，导致：

- `_now_iso()` 在 9 个文件中重复定义（词法完全相同）
- `_default_now()` 在 5 个文件中重复定义（词法相同，命名不同）
- `REPO_ROOT` 在 7 个文件中独立计算（语义相同，写法不同）
- `_estimate_tokens()` 在 3 个文件中重复（词法微差——空字符串处理不一致）
- 同一组 `import` 语句在 20+ 文件中重复出现
- 三个验证函数的 body 共享 80% 结构但参数名不同（`validate_email` / `validate_phone` / `validate_url`）

### 1.2 当前工具的局限

| 工具 | 检测能力 | 盲区 |
|------|---------|------|
| `validate_script_quality.py` D-D-07 | 词法精确匹配（符号名 = _shared API 名） | ❌ 无法检测 `_now_iso` vs `now_iso`（命名不同） |
| `fix_shared_bypass.py` | 词法精确匹配 + 自动修复 | ❌ 同上 |
| Ruff F811 | 同一文件内重定义 | ❌ 无法跨文件检测 |
| Ruff/per-file-ignores | 导入风格 | ❌ 无法检测语义重复 |

**核心盲区**：词法不同但语义相同的重复定义——`_now_iso()` 和 `now_iso()` 和 `_default_now()` 功能完全相同，但名字不同，现有工具检测不到。
**行业数据佐证**：GitClear 2025 年度分析报告显示 AI 辅助编码使代码克隆率增长 4 倍；多个团队独立验证"5000 行魔咒"——项目超过~5000 行代码后 AI 开始系统性地遗忘已有功能、重复生成。

### 1.3 项目运维约束

本引擎运行在以下硬约束下：

| 约束 | 值 | 对设计的冲击 |
|------|-----|------------|
| 开发模式 | 100% AI 施工（Vibe Coding） | 重复会持续产生——不能只靠一次清理 |
| 运维模式 | 1人 + AI 维护 | 误报成本极高——人的时间是瓶颈 |
| 施工频率 | 高频（每天多个 session） | 增量扫描是刚需，全量扫描不可持续 |
| 上下文记忆 | AI 每次 session 零记忆 | 生成时预防比事后检测重要 10 倍 |
| **Session边界** | **AI session ≠ Git commit 边界——session内可能数小时无commit** | **Pre-commit 不是唯一防线——需要 session 内轻量拦截 + Session Log Wave 1 落地** |
| **依赖脆弱性** | **Tree-sitter Python grammar 每年随 Python 版本更新；MinHash/LSH 库可能弃坑** | **引擎依赖版本漂移 = CI 全红风险——需要锁定版本 + 自检 + 降级运行** |
| **增长非线性** | **项目 5000+ 行后 AI "创造性漂移"指数级恶化（"5000行魔咒"）；342 函数→2000 函数时数据结构退化风险** | **阈值必须规模感知——小项目(0-5000行)偏漏报/大项目(5000+)偏拦截；引擎需项目规模自检** |

### 1.4 目标

构建**Monoculture免疫 · 原子修复保障 · 决策审计链 · 主动发现 · 漏报可视 · 微克隆感知 · 测试生成 · 契约验证 · 跨边界 · 全生命周期 · 自审计闭环**的去重系统，实现二十五维闭环：

1. **生成时预防** — AI 写代码前就知道哪些函数已存在
2. **提交时拦截** — Pre-commit 增量扫描，阻止新重复引入
3. **定期扫描** — 全量深度扫描，发现累积的语义重复
4. **安全提取评估** — 修复前评估：①提取适配性（Suitability Score）②影响范围 ③是否适合部分提取 —— **防止盲提取创建更重技术债**
5. **自动修复** — 高置信度 + 高适配性重复 → 安全提取到 shared + 替换引用 + 部分共享 + **Doom Loop 检测**（修复失败3次→回滚→停止→Owner告警）
6. **SSoT 注册** — 提取的函数自动注册到 shared API 清单 + 知识库持久化
7. **进化沉淀** — 重复模式反馈给 Feedback Loop → evolve() → KB 存储
8. **健康监控** — 去重健康仪表盘（Health Score + 引入速率 + 债务预测 + 引擎自观指标）——Owner 30 秒判断全貌
9. **自保护** — 引擎吃自己的狗粮：定期扫描引擎自身源码 + **Codegen 覆盖防护**（检测 codegen 是否覆盖了已修复的 __init__.py/共享导入）+ 引擎冷启动性能预期
10. **防退化** — 共享函数生命周期管理（Deprecation→Grace Period→Sunset→Retirement）+ Import表面积负债追踪（Shared Burden Score——防止去重后的耦合陷阱）+ 设计模式白名单
11. **Monoculture 免疫** — Blast Radius Score 0-100 + 去重成功的悖论（消除重复=单点故障爆炸半径增大）——不是所有重复都该消除；分散重复是天然的blast radius隔离机制
12. **原子修复保障 + 漏报可视** — WAL式修复原子性+崩溃恢复 + 三层漏报盲审（Sweep+Canary+抽样——FNR从黑洞变为可追踪）+ 影子清单信任链 + 时态签名维护
13. **引擎自审计** — Simplicity Audit 月度自审——SAS 0-100——"引擎自己是否已成为项目最重的技术债"——NET_NEGATIVE→自动退役建议——从根本上回答"这个系统值得存在吗"
14. **死共享模块检测** — 生命周期从函数级扩展到模块级——整个 shared/ 子模块中所有函数退役→DEAD→自动标记删除——防止僵尸坟场扩大到文件系统
15. **提取后稳定观察期** — 对标 Microsoft SDP/Netflix Staged Rollout——提取→14天观察→验证稳定→下一轮——隐藏 bug 有时间暴露——防止"修完立刻修下一个"的工业莽撞
16. **恢复失败的恢复** — R0-R3 四层递归恢复安全网——R2 纯文本 Recovery Manifest 作为 tar.gz 损坏的最后防线——"恢复机制的恢复"——是递归信任的终结
17. **噪声信号比·主题聚类** — 50 组重复→3 个主题——IEEE TSE 告警疲劳研究落地——Owner 30 秒读懂全貌而非 30 分钟审查——将"分析负担"转化为"行动信号"
18. **影子清单行为正确性** — 信任链从"函数存在"升级到"函数行为正确"——behavior_signature + 全量扫描重新采样验证 + 行为漂移 DIVERGED 告警——防止静默的语义破坏
19. **并发修改防护** — Pre-Apply Integrity Gate——修复 APPLY 前全量 SHA256 重验证 + ABORT 冲突报告——防止 PREFLIGHT→APPLY 窗口中的外部写入破坏代码库
20. **微型克隆检测** — n-gram 频率计数——1-2 行高频模式聚合——Vibe Coding 微克隆密度是传统项目 3.8x（MSR 2024）——对标 Google Tricorder/JetBrains IntelliJ——决不自修——仅检测+建议
21. **提取后自动测试生成** — 类型驱动边界测试 + 执行轨迹金丝雀录制 + 调用方契约测试——对标 Google Mozart/Test Certified——BRS 从 78→48 的落地机制——测试文件带 @auto-generated-by-dedup 标记
22. **API契约一致性验证** — 存在性·行为正确性·契约一致性三维信任模型——docstring参数+类型注解精确度+影子清单描述时效性+异常契约四层校验——对标 Google Tricorder/Meta Pyre
23. **跨边界克隆感知** — SRC_TEST_BRIDGE / SRC_SCRIPTS_DIVERGENCE / CROSS_LAYER_REDUNDANCY / VENDORED_REIMPLEMENTATION 四大边界差异化策略——对标 Google Blaze——跨边界 auto_fix 比同区域内更保守
24. **去重决策审计链** — DecisionFingerprint 不可变追加日志 + 证据包 + 可回滚——"休假2周回来，知道引擎做了什么、为什么做、怎么撤销"——对标 Google Tricorder/Meta Sapienz/Netflix——复杂度≈0，价值极大
25. **共享函数主动发现** — 签名驱动 + 语义驱动双通道——不等 AI 犯错，主动告知已有实现——从"被动拦截→主动赋能"——对标 Sourcegraph Cody/Google Code Search——整个模块 <150 行

---

## §2 专业对标

### 2.1 大厂与工业界

| 机构 | 工具 | 方法 | 我们能学什么 |
|------|------|------|------------|
| Google | Kythe + Tricorder | 全局符号索引 + AST 结构匹配 + 跨仓库追踪 | **先建图、再查重**——符号级图谱是基础。Kythe 能回答"`now_iso` 被谁定义/引用/调用链是什么"，`function_cache.json` 只能回答"哪些函数签名相似"。全局图谱建一次，后续 import 整理、循环依赖检测、影响分析都可复用 |
| Meta | Glean + Pyre | **增量式、按需**代码索引 + 类型推断辅助匹配 | **函数粒度增量**而非文件粒度——一个文件 10 个函数只改 1 个，只重新索引这 1 个。类型签名是强力指纹，`(int, str) -> bool` 比函数名更可靠 |
| SonarQube | 内置重复检测 | Token 序列归一化 + Karp-Rabin 哈希 + **可配置最小克隆长度（token 数）** | 工业级可靠性——快、稳、可集成 CI。**最小克隆长度**是关键参数：4行 import 在 20 文件中重复是严重问题，4 行函数体可能不值得提取——用 token 数而非行数判定 |
| PMD CPD | Copy-Paste Detector | Token 序列匹配 + 跨语言支持 | 零依赖、开源、CLI 友好 |
| JetBrains | IntelliJ 重复检测 | AST 子树哈希 + 滑动窗口 | IDE 内实时反馈——开发时阻止而非提交时拦截 |
| CodeAnt AI | AI 驱动检测 | **跨服务/跨语言逻辑级重复** + PR 评论 | 不只匹配文本，识别"看起来不同但行为相同" |

### 2.2 学术界前沿

| 来源 | 方法 | 关键结论 |
|------|------|---------|
| ASE 2025 · 语义克隆检测 | 对比学习 + LLM 作为克隆检测器 | LLM 对**未见过功能**的泛化能力远超专用模型（F1 仅降 3% vs 专用模型降 31%）——LLM 是最强的语义等价判断器 |
| ACL 2025 · RPG（Repetition Penalization based on Grammar） | 在 LLM 解码时用语法规则惩罚重复 token | **从源头阻止重复产生**——不是检测重复代码，而是让 LLM 不生成重复代码 |
| CCFinder | Token 后缀树 | 经典 Type-1/2 克隆检测 |
| Deckard | AST 向量聚类 | 可扩展到百万行级代码库 |

### 2.3 氛围编程社区

| 实践 | 做了什么 | 局限 | 我们能学什么 |
|------|---------|------|------------|
| MCP Server 去重 `dedupe-mcp` | AI 生成代码后自动调用 MCP tool 检测 + 修复 | 只针对当前生成片段，不跨文件 | MCP tool 模式：检测→修复→重新生成 |
| GitHub Copilot duplication detection | 检测生成代码与训练数据的重复 | 防版权侵权，不防项目内重复 | — |
| Cursor Rules / CLAUDE.md | 项目级规则约束 AI 行为，**自动注入每次对话** | 软约束，AI 可能忽略；上下文窗口有限时规则被截断 | **规则需要"硬落地"——与 Gate Engine 绑定**；但注入 ≠ 消费——需要验证回环确认 AI 真的读了 |
| AGENTS.md 共享 API 清单 | 在项目入口文件声明已有函数 | 依赖 AI 主动查阅，上下文窗口有限；**影子清单被注入后无消费验证** | **共享 API 影子清单**——精简版自动注入到每次 session；但必须追加回环验证："影子清单里有但 AI 还是重复生成了 → 为什么？→ 优化清单格式/长度/优先级" |
| "commit early and often" | 靠人工 review 发现重复 | 1 人团队不可持续 | 必须自动化 |
| **Cursor .cursorrules 自动注入** | 项目约定 + 禁止模式在每次对话中自动注入 LLM 上下文 | AI 选择性忽略（上下文太长时注意力衰减） | **渐进式披露**——分三级注入：①热规则（≤400 tokens，始终注入）②领域规则（触发特定关键词时注入）③冷规则（仅在明确引用时加载）——对标 arXiv 2602.20478 三层记忆模型 |

**核心差距与演进路线**：

| 层级 | 做法 | 代表 | 我们当前的差距 | 演进方向 |
|:---:|------|------|------------|---------|
| L3 | **平台级去重**——全局符号图谱 + 持续监控 + 跨仓库追踪 | Google Kythe、Meta Glean | 无全局符号索引 | Wave 2 引入 Symbol Index（轻量版图谱——函数签名+调用关系+import 图的 SQLite 存储） |
| L2 | **引擎级去重**——六阶段闭环 + 多维度检测 + 自动修复 | SonarQube、PMD CPD | 当前蓝图定位——但缺降级模式、缓存自愈、惯用法白名单 | v0.4.0 补全（本版） |
| L1 | **提示词级防重**——上下文约束 + 生成后检查 + 规则注入 | Cursor Rules、AGENTS.md | 已有基础——但缺消费验证回环 + 渐进式披露 | Wave 2 落地验证回环；Wave 3 落地三层记忆注入 |

**核心洞察**：Google/Meta 的做法（建图→查重→演进）是正确方向，但 1 人团队不需要全量 Kythe。一个**轻量符号索引**（函数签名+调用计数+互引用）只需要 SQLite 一张表 + `ast.NodeVisitor`，完全在 Wave 2 能力范围内——建一次，后续 import 整理、循环依赖检测、影响分析三大场景都受益。

---

## §3 核心架构：全生命周期七维模型

### 3.1 从"事后检测"到"全生命周期去重+健康监控"

```
                        ┌─────────────────────────────────────────────────┐
                        │              代码去重全生命周期                     │
                        │                                                  │
                        │  ① 生成时预防  ──→  ② 提交时拦截  ──→  ③ 定期扫描    │
                        │   (Prevent)        (Block)          (Audit)       │
                        │       │                │                │         │
                        │       │    ┌───────────┴───────────┐    │         │
                        │       │    │  ④ 自动修复 (Fix)     │    │         │
                        │       │    │  ⑤ SSoT注册 (Register)│    │         │
                        │       │    │  ⑥ 进化沉淀 (Evolve)  │    │         │
                        │       │    └───────────────────────┘    │         │
                        │       │                                  │         │
                        │       └──────────  ⑦ 健康监控  ─────────┘         │
                        │                  (Health Monitor)                 │
                        └─────────────────────────────────────────────────┘
```

| 阶段 | 触发时机 | 做什么 | 成本 | 防重效果 |
|:---:|---------|------|:---:|:---:|
| **① Prevent** | 每次 AI session 开始 | Context Engine 注入"共享API影子清单" + 渐进式三层记忆注入 | 0 token（已在内） | ★★★★★ |
| **② Block** | Pre-commit | 增量扫描变更文件 → 命中已知重复模式 → BLOCKED（Wave 1 即落地阻断！） | ~2s | ★★★★★ |
| **③ Audit** | 每周 / 每 N 个 commit | 全量 MinHash + AST 深度扫描 | ~30s | ★★★ |
| **④ Fix** | Audit 后 or 手动 `--fix` | 高置信度重复自动提取→替换→验证（含ROI评估排序 + **Doom Loop检测**——3次失败→停止+告警） | ~60s | ★★★★ |
| **⑤ Register** | Fix 后自动 | 提取的函数注册到 shared + 更新 AGENTS.md | ~1s | ★★★★★ |
| **⑥ Evolve** | 定期批处理 | 重复模式→FLE→evolve()→EvolutionProposal | ~5s | ★★★ |
| **⑦ Monitor** | 每次扫描后自动 | 更新代码健康仪表盘（Dedup Health Score + 趋势 + 健忘热点）→ 写入 Session Log（Wave 1 即落地交接！） | ~1s | — |
| **⑧ Self-Protect** | 每次全量扫描后自动 + 每周 | 引擎扫描自身源码去重 + **Codegen覆盖检测**（BLIND-CODGEN-INIT-OVERWRITE）——吃自己的狗粮 | ~3s | — |
| **⑨ Lifecycle Manage** | 每月 / shared 函数 > 50 时 | 共享函数生命周期巡检（Deprecation→Grace Period→Sunset→Retirement）+ Import表面积负债评分 | ~5s | ★★ |
| **⑩ Anti-Degrade** | 每次扫描后自动 | Doom Loop日志分析 + 设计模式白名单更新 + 幂等性自校验 + 冷启动性能基准 | ~2s | — |

### 3.2 增强版五阶段检测流水线（含降级运行）

```
Stage 0: 缓存预热 + 变更检测（毫秒级）
  → 加载 function_cache.json
    · 每个函数的签名指纹（参数类型+返回类型的 SHA256[:12]）
    · AST 子树归一化哈希
    · MinHash 签名
    · 文件路径 + 行号范围
    · last_modified 时间戳
    · intentional_duplicate 标记
    · known_shared_equivalent（已知共享等价函数）
  → 缓存完整性自检：
    · _integrity 字段：SHA256(cache_content) 跨磁盘写入校验
    · 加载时验证 hash → 不一致 → 自动 full rebuild → 记录 Session Log
    · 写入用原子操作：先写 .tmp → os.replace(.tmp, cache.json)
  → git diff 检测变更文件
  → 快速路径：只扫描变更/新增函数
  → 全量扫描路径：复用未变更函数的缓存

Stage 0.5: 签名指纹碰撞检测（毫秒级，新增！)
  → 对每个新增函数计算 signature_fingerprint（SHA256[:12]）
  → O(1) 精确匹配缓存中所有函数的 signature_fingerprint
  → 签名碰撞判定：
    · signature 完全相同 → "Signature Collision"（高置信度，直接标记）
    · signature 含相同参数类型但不同返回类型 → "Signature Near-Collision"（中置信度）
  → 为什么是 Stage 0.5 而非 Stage 3：
    · Vibe Coding AI 重新发明函数时通常保持相同签名（输入输出类型不变）
    · 不需要 MinHash、不需要 AST——纯缓存查询，零额外计算
    · 这是 Vibe Coding 语境下性价比最高的检测维度
  → 路径感知阈值同样适用：
    · shared/ 内签名碰撞 → CRITICAL（shared 里绝不允许签名冲突）
    · core/ 内签名碰撞 → HIGH
    · tests/ 内签名碰撞 → LOW（测试函数签名冲突容忍度高）

Stage 0.25: 行为采样快速验证（秒级，v0.6.0 新增！——低测试覆盖安全网）
  → 背景：Vibe Coding 项目中测试覆盖率通常极低（< 20%），verifier.py 依赖 pytest 不现实
  → 对每个签名碰撞候选对，进行轻量级行为采样验证：
    · 自动生成 N 组类型兼容的采样输入（基于类型注解推断——int→[0,1,-1,MAX]，str→["","test","中文"]，List→[[], [1], [1,2,3]]）
    · 分别对原始函数和候选重复函数执行采样输入
    · 比对输出：完全相同 → "behavioral_match" 标记 + 提升置信度
    · 输出部分不同 → "behavioral_divergence" 标记 + 降低置信度 → 降级为 needs_review
    · 函数有副作用（I/O/网络/数据库）→ 跳过行为采样 → 标记 "side_effect_skip"
  → 安全约束：
    · 仅对纯函数执行（无 I/O、无 global、无 random、无 time 调用——通过 AST 静态判定）
    · 永不执行 `eval()`/`exec()`/`__import__()`/`os.system()`/`subprocess` 相关代码
    · 执行超时 500ms/func——超时 → 跳过
    · 执行环境：subprocess 沙箱隔离（独立进程，内存限制 256MB）
  → 采样输入生成策略：
    · 基础类型映射：int→[0,1,-1,2,10,100], float→[0.0,1.0,-1.0], str→["","test","你好"], bool→[True,False]
    · 可选类型：Optional[X]→ +[None]
    · 集合类型：List[X]→ [[],[x1],[x1,x2,x3]], Dict[K,V]→ [{},{k1:v1}], Set[X]→ [set(),{x1}]
    · 自定义类 → 尝试无参构造 __init__()，失败则跳过
    · 最多生成 10 组采样输入（减少执行开销）

Stage 1: Token 级快速扫描（秒级）
  → 提取所有新增/变更函数的 token 序列
  → 归一化：统一变量名为 _VAR_、函数名为 _FUNC_
  → 剥离 docstring + 注释
  → 计算归一化 token 序列的 MinHash
  → LSH 近似去重：候选对集合
  → 路径感知阈值：
    · src/zephyr/shared/   → 0.3（shared 里重复是严重 bug）
    · src/zephyr/core/     → 0.6
    · src/zephyr/*/        → 0.7
    · tests/               → 0.9（测试允许更高的重复容忍度）
    · scripts/             → 0.7
  → **新增：代码块级去重**（非函数级别）
    · 对整个文件做 N 行窗口滑动（min_block_size=5，默认最少 5 行）
    · 计算每个窗口的 MinHash → 跨文件比对
    · 检测目标：import 块重复（20+ 文件中相同 import 段）、异常处理模板、配置读取+验证逻辑

Stage 2: AST 级精确比对（分钟级）
  → 对候选对进行 AST 子树哈希
  → 增强处理：
    · 剥离 docstring 后比对
    · 归一化变量名后比对
    · 装饰器剥离——@timer 和 @cache 不应阻止函数体比对
    · **Python 惯用法自动豁免**（新增）：
      - `__init__(self, ...): self._xxx = xxx` → 豁免
      - `__repr__/__str__` 返回 f-string 模式 → 豁免
      - `__enter__/__exit__` Context Manager 协议骨架 → 豁免
      - `@property` getter/setter 模式 → 豁免
      - ABC 抽象方法（`raise NotImplementedError`）→ 豁免
      - `@overload` 类型重载 → 豁免
    · **设计模式自动豁免**（v0.6.0 新增）：
      - **Strategy 模式**：同接口不同实现——`def execute(data: X) -> Y` 签名的多个类方法 → 豁免
      - **Adapter 模式**：包装第三方/旧API——含 `self._wrapped` / `self._adaptee` AST 节点 → 豁免
      - **Factory 模式**：`create_*()` 方法返回不同子类——识别 `if/elif/else` 分发结构 → 豁免
      - **Template Method**：基类骨架 + 子类覆写——基类有具体实现 + 子类有同名方法 → 豁免
      - **Observer**：`notify()`/`update()` 同名方法多个类——检测到 callback/listener 注册 → 豁免
      - **Decorator/Wrapper**：含 `@wraps(func)` + `def wrapper(*args, **kwargs)` 模式 → 豁免
    → 检测方法：AST 模式匹配规则库（`DESIGN_PATTERN_WHITELIST` in config.py）——不依赖 LLM，纯 AST 规则
  → 结构相似度判定：
    · > 0.95 → "几乎确定重复"（可自动修复）
    · 0.85~0.95 → "高度疑似重复"（建议修复，需确认）
    · 0.70~0.85 → "可能重复"（需 LLM 辅助判断）
    · < 0.70 → "非重复"
  → 新增检测能力：
    · 部分重复检测（滑动窗口 + 最长公共子序列 LCS）
    · 重排序语句容忍（a=1;b=2 ≈ b=2;a=1）
    · 参数化模板识别（validate_* 模式）

Stage 3: 语义级验证（可选，需 LLM）
  → 对 AST 相似度 0.70~0.85 的不确定候选对
  → LLM 判断：
    Prompt: "这两个函数是否实现相同的功能？请给出0-100的置信度评分和理由。"
  → 输出：确认为重复（置信度≥80）/ 非重复 / 需人工判断
  → 不依赖 LLM——LLM 只是锦上添花，Stage 0.5-2 已经能覆盖 95% 的场景

降级运行策略（为保证1人+AI维护下的引擎鲁棒性）:
  → 每层 Stage 独立 try/except，失败时降级而非崩溃：
    · Stage 0 缓存损坏 → 跳过缓存，全程 AST 解析（降级但不退出）
    · Stage 0.5 签名比对异常 → 跳过 Stage 0.5，Stage 1 继续（缺失精确匹配但不影响整体）
    · Stage 1 MinHash OOM → 降级为仅 Stage 0.5 结果 + 报告中标注"本次仅签名匹配"
    · Stage 2 AST 解析失败（Tree-sitter grammar 版本漂移）→ 降级为仅 Stage 0.5+1 结果 + 报告中标注"本次跳过AST比对: Tree-sitter grammar incompatible"
    · Stage 3 LLM API 不可用 → 完全不阻塞——Stage 0.5-2 结果完整可用
  → 降级时 exit code 仍可为 0/1/2/3，但报告中 degradation_level 字段记录降级原因
  → 降级日志写入 Session Log——Owner 下次 session 或下次 audit 时知晓引擎需要维护

### 3.3 十八维检测矩阵

| # | 检测维度 | 检测方法 | Type | 精确度 | 速度 | 备注 |
|:---:|---------|---------|:---:|:---:|:---:|------|
| 1 | **词法精确匹配** | 符号名 = 已知 SSoT 名 | Type-1 | ★★★★★ | ★★★★★ | Stage 0.5/1 |
| 2 | **签名+返回值匹配** | 参数类型 + 返回类型的并集指纹——SHA256[:12] O(1)精确匹配 | Type-2 | ★★★★ | ★★★★★ | **Stage 0.5——Vibe Coding 场景下性价比最高的防线**（AI 重实现时通常保持相同签名） |
| 3 | **Token 归一化匹配** | MinHash + LSH | Type-2 | ★★★★ | ★★★★ | Stage 1 |
| 4 | **代码块级重复** | 滑动窗口 MinHash（非函数级别，min_block_size≥5行） | Type-2/3 | ★★★★ | ★★ | Stage 1——import块/异常处理模板/配置逻辑 |
| 5 | **AST 结构匹配** | 归一化子树哈希 + 相似度 + Python惯用法豁免 | Type-3 | ★★★★★ | ★★★ | Stage 2 |
| 6 | **部分重复检测** | 滑动窗口 + LCS（最长公共子序列） | Type-3 | ★★★★ | ★★ | Stage 2 |
| 7 | **重排序语句容忍** | AST 子树集合比对而非序列比对 | Type-3 | ★★★★ | ★★★ | Stage 2 |
| 8 | **参数化模板识别** | 同名前缀 + 结构相似 > 0.7 → 聚类 | Type-3 | ★★★ | ★★★★ | Stage 2 |
| 9 | **常量/import/类/枚举重复** | Token 归一化（非函数结构也纳入） | Type-1/2 | ★★★★★ | ★★★★★ | Stage 1 + code block dedup |
| 10 | **Python 惯用法豁免** | AST 模式匹配自动跳过（`__init__`/`__repr__`/`@property`/`@overload`/ABC骨架） | — | — | ★★★★★ | Stage 2——减少误报 |
| 11 | **配置文件语义重复** | YAML/TOML AST 比对（Tree-sitter） | Type-2 | ★★★★ | ★★★★ | Wave 2 |
| 12 | **LLM 语义等价判断** | Prompt: "是否等价？给出置信度" | Type-4 | ★★★★ | ★ | Stage 3——可选 |
| 13 | **微型克隆检测** | n-gram 频率计数——逐行SHA256 + 归一化 + 2-3行滑动窗口 | Type-1/2/3 | ★★★★★ | ★★★★★ | **v0.9.0 / Stage 1——Vibe Coding 微克隆密度 3.8x（MSR 2024）——对标 Google Tricorder** |
| 14 | **提取后自动测试生成** | 类型驱动边界测试 + 执行轨迹金丝雀录制 + 调用方契约测试——生成pytest parametrize | — | ★★★★ | ★★★ | **v0.9.0 / auto_fixer 后触发——对标 Google Mozart/Test Certified——BRS 缓解** |
| 15 | **API契约一致性验证** | docstring参数校验+类型注解精确度+影子清单描述时效性+异常契约——三维信任模型 | — | ★★★★★ | ★★★★ | **v0.9.0 / Wave 2——对标 Google Tricorder/Meta Pyre——防止契约腐烂** |
| 16 | **跨边界克隆感知** | 四大边界差异化策略（SRC_TEST_BRIDGE/SRC_SCRIPTS_DIVERGENCE/CROSS_LAYER_REDUNDANCY/VENDORED） | Type-2/3 | ★★★★ | ★★★ | **v0.9.0 / Wave 2——对标 Google Blaze/JetBrains IntelliJ——最高价值去重** |
| 17 | **去重决策审计链** | DecisionFingerprint 不可变追加日志 + 证据包 + 可回滚——决策指纹永久可追溯 | — | ★★★★★ | ★★★★★ | **v0.10.0 / Wave 2——"我没看的时候引擎做了什么？"——对标 Google Tricorder/Meta Sapienz** |
| 18 | **共享函数主动发现** | 签名归一化匹配(Channel A) + TF-IDF语义匹配(Channel B)——主动通知AI已有实现 | Type-2/4 | ★★★★ | ★★★★★ | **v0.10.0 / Wave 2——从"被动拦截→主动赋能"——对标 Sourcegraph Cody/Google Code Search——<150行** |

### 3.4 增强版输出格式

```yaml
# function_cache.json —— 预计算缓存（加速增量扫描）
# 存放路径: D:\ZephyrAlpha\data\cache\function_cache.json
cache_metadata:
  generated_at: "2026-05-05T..."
  total_functions: 342
  last_full_scan: "2026-05-05T..."
  version: "1.0.0"
  _integrity: "sha256:a1b2c3d4e5f6..."   # SHA256(整个cache内容) —— 加载时验证 → 损坏 → 自动重建

functions:
  - id: "func-001"
    file: "orchestrator/state_synchronizer.py"
    name: "_now_iso"
    signature_fingerprint: "a1b2c3d4e5f6"     # 参数类型+返回类型的 SHA256[:12] —— Stage 0.5 签名碰撞检测的关键
    ast_fingerprint: "f6e5d4c3b2a1"            # 归一化AST子树的 SHA256[:12]
    token_minhash: [123, 456, 789, 234, 567]   # MinHash 签名（128个哈希值的前5个采样）
    loc_start: 45
    loc_end: 48
    loc_count: 4
    last_modified: "2026-05-03T14:22:00Z"
    intentional_duplicate: false
    known_shared_equivalent: "zephyr.shared.time_utils.now_iso"
    decorator_count: 0
    complexity: 2    # 圈复杂度
    caller_count: 12   # 被多少其他函数调用（Symbol Index 数据——Wave 2）
    category: "time_utils"  # 函数名前缀聚类——用于AI健忘热点追踪

# dedup_report.yaml —— 完整检测报告
dedup_report:
  scan_metadata:
    generated_at: "2026-05-05T..."
    scan_mode: "incremental"          # full | incremental
    trigger: "pre-commit"            # pre-commit | weekly | manual
    scope: "src/zephyr/"
    total_functions: 342
    scanned_functions: 12             # 本次只扫描了12个变更函数（增量模式）
    cached_functions: 330             # 其余330个来自缓存
    scan_duration_ms: 2147
    exit_code: 1                      # 0=无重复 / 1=发现重复(WARN) / 2=严重重复(ERROR) / 3=工具故障 / 4=降级运行
    degradation_level: "none"        # none | stage1_only | stage0.5_only | no_ast | no_cache ——降级运行标记

  health_score:                       # 代码健康仪表盘数据（新增——Wave 1 即产出，v0.5.0 扩展）
    overall: 87                       # 0-100，综合代码健康度
    trend: "up"                       # up | down | flat（较上次扫描的趋势）
    components:
      duplication_rate: 3.5           # 重复函数占比 %
      shared_coverage: 45             # shared/ 中函数占比 %
      signature_collisions: 0         # 签名碰撞数
      import_health: 85               # import 健康度
      stale_shared_count: 0           # 过期共享函数数（v0.5.0 新增）
      auto_fix_success_rate: 100      # 自动修复成功率 %（v0.5.0 新增）
    introduction_velocity: 2.0         # 新重复引入速率——组/周（v0.5.0 新增——暴露 Prevent 阶段是否有效）
    debt_projection_weeks: 4          # 按当前速率预计 N 周还清去重债务（v0.5.0 新增）
    engine_observability:              # 引擎自观指标（v0.5.0 新增——用于调试引擎自身）
      scan_duration_p50_ms: 1200      # 增量扫描中位数耗时
      cache_hit_ratio: 0.94           # 缓存命中率——增量扫描复用缓存比例
      detection_latency_hours: 4.2    # 从重复引入到检测发现的平均延迟
      false_positive_rate_7d: 0.03    # 最近 7 天误报率（需 Owner 确认标记来更新）
    hotspot_categories:               # AI 健忘热点 Top 3
      - category: "time_utils"
        duplicate_count: 3
        trend: "down"
      - category: "path_utils"
        duplicate_count: 2
        trend: "flat"

  summary:
    duplicate_groups_total: 3
    signature_collisions: 1           # Stage 0.5 检测到的签名碰撞数（新增）
    high_confidence: 2                # similarity > 0.95
    medium_confidence: 1              # 0.85~0.95
    low_confidence: 0                 # 0.70~0.85
    affected_files: 7
    auto_fixable: 2                   # 可自动修复的组数
    roi_top_pick: "DUP-20260505-001"  # ROI最高的修复组（prioritizer.py 产出）——新增

  duplicate_groups:
    - group_id: "DUP-20260505-000"
      similarity: 1.0   # 签名碰撞——函数体可能完全不同但签名相同
      confidence: 90
      category: "needs_review"          # 签名碰撞默认 needs_review——可能是 Vibe Coding 重实现
      detection_method: "signature_collision"   # Stage 0.5
      clone_type: "Type-2 (signature)" # 签名相同但实现可能完全不同
      signature_fingerprint: "a1b2c3d4e5f6"
      signature: "() -> str"
      members:
        - id: "func-001"
          file: "orchestrator/state_synchronizer.py"
          function: "_now_iso"
          loc: "45-48"
        - id: "func-015"
          file: "orchestrator/file_task_mapper.py"
          function: "_now_iso"
          loc: "45-48"
        - id: "func-023"
          file: "context_engine/context_injector.py"
          function: "_default_now"
          loc: "31-34"
      llm_verdict: "pending"
      recommendation: "签名完全相同 `()->str`——可能为 Vibe Coding AI 重实现，需要 AST 比对确认函数体是否一致"
      severity: "high"
      priority_score: 85

    - group_id: "DUP-20260505-001"
      similarity: 1.0
      confidence: 100                 # 置信度评分 0-100
      category: "accidental"         # accidental | intentional | needs_review
      detection_method: "token_minhash"
      clone_type: "Type-1"           # Type-1(完全) / Type-2(重命名) / Type-3(结构) / Type-4(语义)

      members:
        - id: "func-001"
          file: "orchestrator/state_synchronizer.py"
          function: "_now_iso"
          loc: "45-48"
        - id: "func-015"
          file: "orchestrator/file_task_mapper.py"
          function: "_now_iso"
          loc: "45-48"
        - id: "func-023"
          file: "context_engine/context_injector.py"
          function: "_now_iso"
          loc: "31-34"

      auto_fix:
        safe: true                    # similarity=1.0 + 词法完全相同 → 绝对安全
        plan:
          - action: "ensure_shared_exists"
            target: "src/zephyr/shared/time_utils.py"
            function: "now_iso"
            signature: "def now_iso() -> str"
          - action: "replace_definition_with_import"
            files:
              - "orchestrator/state_synchronizer.py:45-48"
              - "orchestrator/file_task_mapper.py:45-48"
              - "context_engine/context_injector.py:31-34"
            replace_with: "from zephyr.shared.time_utils import now_iso"
          - action: "update_cache"
            entries: ["func-001", "func-015", "func-023"]
          - action: "register_ssot"
            target: "b_shared.yaml"
            entry: "zephyr.shared.time_utils.now_iso"
        verification_commands:
          - "python -m pytest tests/ -q"
          - "python -c 'from zephyr.shared.time_utils import now_iso; assert now_iso().endswith(\"Z\")'"

      recommendation: "提取到 zephyr.shared.time_utils.now_iso()"
      severity: "critical"
      priority_score: 100             # 排序分数：重复次数(3) × 相似度(1.0) × 影响文件数(3) × 100

    - group_id: "DUP-20260505-002"
      similarity: 0.88
      confidence: 92
      category: "accidental"
      detection_method: "ast_subtree_hash"
      clone_type: "Type-3"

      members:
        - id: "func-042"
          file: "context_engine/context_injector.py"
          function: "_estimate_tokens"
          loc: "49-56"
        - id: "func-058"
          file: "context_engine/prompt_registry.py"
          function: "_estimate_tokens"
          loc: "76-83"

      auto_fix:
        safe: true                    # similarity > 0.85 + 同目录 → 安全
        plan:
          - action: "create_shared"
            target: "src/zephyr/shared/token_utils.py"
            function: "estimate_tokens"
          - action: "replace_and_verify"
            files:
              - "context_engine/context_injector.py:49-56"
              - "context_engine/prompt_registry.py:76-83"

      recommendation: "提取到 zephyr.shared.token_utils.estimate_tokens()"
      severity: "high"
      priority_score: 78              # 2 × 0.88 × 2 × 100

    - group_id: "DUP-20260505-003"
      similarity: 0.72
      confidence: 65
      category: "needs_review"        # LLM 判断后才能确定
      detection_method: "lcs_partial"
      clone_type: "Type-3 (partial)"
      llm_verdict: "pending"          # pending | confirmed | rejected
      recommendation: "这两个函数共享60%的结构——可能需要提取公共部分"
      severity: "medium"
      priority_score: 43
```

### 3.5 策略树 YAML 设计（顶层设计——Wave 3 正式落地，参数在 config.py 中从 Wave 1 开始逐步配置）

去重行为不应该硬编码在 Python 中——顶尖设计用**声明式策略树**替代硬编码阈值表。
Owner 或 AI 可以修改 YAML 调整行为，不需要读懂 Python 代码。
对标 1 人 + AI 维护的最优解。

```yaml
# config/policy_tree.yaml —— Wave 3 正式落地
# 优先级自上而下——第一个匹配的条件执行对应动作

policy_tree:
  - name: "shared_internal_conflict"
    condition:
      any_member_in_path: "src/zephyr/shared/"
      similarity: ">= 0.3"
    action: "CRITICAL"
    auto_fix: false
    explanation: "shared/ 目录中出现重复函数 = 架构违规——SSoT 分裂"

  - name: "high_confidence_duplicate"
    condition:
      similarity: ">= 0.95"
      any_member_in_path: ["src/zephyr/core/", "src/zephyr/orchestrator/"]
    action: "ERROR"
    auto_fix: true
    auto_fix_batch_size: 3
    explanation: "几乎确定重复——自动提取到 shared"

  - name: "signature_collision_vibe_coding"
    condition:
      detection_method: "signature_collision"
      similarity: "< 0.3"
    action: "WARN"
    auto_fix: false
    category: "needs_review"
    explanation: "签名完全相同但函数体差异大——Vibe Coding AI 重实现已有功能。标记 needs_review"

  - name: "test_high_duplication"
    condition:
      any_member_in_path: "tests/"
      similarity: ">= 0.9"
    action: "WARN"
    auto_fix: false
    explanation: "测试代码合理重复阈值更高——只警告极高相似度"

  - name: "idiom_whitelist"
    condition:
      match_idiom_pattern: ["__init__", "__repr__", "@property", "@overload", "abstract_method"]
    action: "SKIP"
    auto_fix: false
    explanation: "Python 惯用法——结构相似但语义不同，不标记为重复"

  - name: "intentional_duplicate_marked"
    condition:
      has_annotation: "@intentional-duplicate"
    action: "SUPPRESS"
    auto_fix: false
    suppress_similar: true
    explanation: "开发者已标记为有意重复——完全压制 + 学习模式"

  - name: "default"
    condition: "true"
    action: "INFO"
    auto_fix: false
    explanation: "默认——低置信度重复仅供参考"

# 95/4/1 分布监控（§11 目标分布）
distribution_targets:
  auto_guard_pct: 4       # auto_guard ≤ 4%
  agent_review_pct: 95    # agent_review ≥ 95%
  owner_approval_pct: 1   # owner_approval ≤ 1%
  alert_threshold_pct:    # 偏离目标 > 50% → 告警
    auto_guard_max: 8
    owner_approval_max: 3
```

**操作码与 Gate Engine 映射**：

| 操作码 | Gate 判定 | 是否阻断 commit | auto_fix 可用性 |
|:---:|:---:|:---:|:---:|
| `CRITICAL` | FAIL | ✅ 阻断 | ❌ 不自动修（需人工） |
| `ERROR` | FAIL | ✅ 阻断 | ✅ 可自动修（高置信度） |
| `WARN` | WARN | ❌ 不阻断 | ❌ 不自动修 |
| `INFO` | PASS | ❌ 不阻断 | ❌ |
| `SKIP` | PASS（跳过） | ❌ | ❌ |
| `SUPPRESS` | PASS（完全压制） | ❌ | ❌ |

### 3.6 安全提取适配性评估（Suitability Score —— v0.5.0 新增 — Wave 2 落地）

**核心问题**：行业实践反复告诫——"盲目提取代码到共享库有时比保留重复代码更糟糕"（Latenode 社区、Microsoft 培训模块、AugmentCode 指南）。
不是所有检测到的重复都应该被提取。提取前必须评估**适配性**。

```yaml
# suitability_score 评估维度
suitability:
  extraction_safety_score: 0-100     # 综合适配性——< 40 = 绝对不提取
  dimensions:
    caller_compatibility: 85         # 所有调用方是否需要完全相同的逻辑？（越一致越好）
    divergence_risk: 15              # 调用方未来需求差异化的可能性？（越低越好）
    test_coverage_of_callers: 60     # 调用方的测试覆盖率？（越高越安全）
    public_api_stability: 100        # 提取后是否会破坏公开API契约？（不会被破坏 = 100）
    customization_need: 10           # 调用方是否有独特的定制需求？（越低越好）
    platform_specificity: 0          # 是否包含平台特定代码（sys.platform/os.name）？（包含 = 高风险）
    caller_count_safety: 90          # 调用方数量是否在安全范围？（< 20 = 安全，> 50 = 高风险）
    performance_sensitivity: 20      # 是否涉及性能热点路径？（越高越需要谨慎——提取 = 间接调用开销）
  verdict: "SAFE_TO_EXTRACT"         # SAFE_TO_EXTRACT | PARTIAL_EXTRACT | NEEDS_REVIEW | DO_NOT_EXTRACT
  partial_extraction_plan:           # 仅当 verdict=PARTIAL_EXTRACT 时有值
    common_core_pct: 60              # 可提取的公共核心占比 %
    divergent_parts:                 # 各调用方的差异化部分
      - caller: "caller_a.py"
        keep_local: "空字符串处理逻辑"
      - caller: "caller_b.py"
        keep_local: "性能优化的缓存逻辑"
```

**不安全提取模式目录**（以下模式 NEVER auto-extract）：

| 模式 | 为什么不能盲提取 | 策略 |
|------|---------------|------|
| **高调用方函数（caller_count > 50）** | 修改共享函数影响面巨大，一轮测试覆盖不到所有调用路径 | 需全量集成测试通过 + Owner 人工确认 |
| **平台条件代码**（含 `sys.platform` / `os.name`） | 提取后平台分支逻辑膨胀——共享函数变成 if/else 地狱 | 提取平台无关核心 + 保留平台适配层 |
| **公开 API 契约函数** | 提取 = 变更 import 路径 = 破坏下游依赖 | 保留原位置 + 内部委托到 shared（Adapter 模式） |
| **性能热点函数**（被高频调用） | 提取增加间接调用开销 + import 开销 | 仅在性能测试通过后提取 |
| **生成代码**（`# @generated` 标记） | 生成代码会被重新生成——提取会被覆盖 | **直接跳过——不检测、不报告** |
| **Vendored/第三方代码** | 每次升级需要重新合入 | 标记为 excluded，加入 config.py EXCLUSION_PATTERNS |
| **类型 stub 文件（`.pyi`）** | stub 文件本身就是类型声明重复——正常现象 | 豁免 |

### 3.7 项目规模感知 —— 自适应阈值（v0.5.0 新增 — Wave 1 即落地参数）

**背景**：Chromat Research 的 Context Rot 研究发现 32K tokens 以上模型性能断崖式下降；多个团队验证"5000行魔咒"。
引擎必须根据项目规模自动调整行为。

| 项目规模 | 函数数估算 | 阈值策略 | 扫描策略 | 自动修复策略 |
|------|:---:|------|---------|---------|
| **Tier 1: 起步期** (< 5000 行 / < 150 函数) | ~100-150 | 偏向漏报——默认全局阈值 0.80（高于标准的 0.70）。小项目不怕重复多、怕误报打断开发节奏 | 全量扫描性能压力极小——每次可全量 | 不自动修复——项目太小，shared 结构不稳定 |
| **Tier 2: 成长期** (5000-15000 行 / 150-500 函数) | ~342（当前） | 标准阈值——全局 0.70 / shared 0.30 / tests 0.90 | 增量扫描为主——全量每周一次 | 高置信度(>0.95)可自动修复——分批 ≤3 组 |
| **Tier 3: 规模期** (> 15000 行 / > 500 函数) | ~500+ | 偏向拦截——全局阈值 0.60（更激进）。大项目重复的维护成本极高（修一处漏三处） | 依赖缓存 + 增量——全量仅月度 | 中置信度(>0.85)即可自动修复——但仍需适配性 ≥ 60 |
| **Tier 4: 大型期** (> 50000 行 / > 2000 函数) | ~2000+ | 激进拦截——全局 0.50 + 启用 Stage 3 LLM 辅助。5000行魔咒在此阶段系统性爆发 | 分层扫描——仅增量模块 + 定期全量 | 适配性阈值提升至 70——大规模代码更谨慎 |

### 3.8 引擎自保护与Dogfooding（v0.6.0 新增 — Wave 1 即落地自我扫描，Wave 2 落地Codegen防护）

**核心问题**：引擎本身也是 Vibe Coding AI 生成的代码，可能包含重复函数。顶尖设计必须"吃自己的狗粮"。

**三层自保护机制**：

| 层级 | 触发 | 检查内容 | 失败策略 |
|:---:|------|------|------|
| **L1: 引擎自扫描** | 每次全量扫描后自动运行 | 对 `l01_infrastructure/code_dedup_engine/` 下所有 Python 文件运行去重检测（Stage 0.5+1） | 发现重复 → 标记 "SELF-DUP-*" + 报告 + 不自动修复（引擎自己修自己 = 递归噩梦） |
| **L2: Codegen 覆盖防护** | 每次全量扫描 + 每次 CI 运行 | 检查所有层 `__init__.py` 的 SHA256 哈希是否有已知修复（对比 `codegen_fix_manifest.json` 中的"已修复哈希白名单"）。检测到覆盖 → "CODEGEN-OVERWRITE-DETECTED" 信号 | ①告警不阻断 ②写入 Session Log ③生成修复diff——AI session 可一键重新应用修复 |
| **L3: 引擎依赖自检** | 每次加载时 | 检查 Tree-sitter/MinHash 库版本是否在锁定范围内 + 校验依赖 hash（poetry.lock 对比） | 版本漂移 → exit code 4（DEGRADED）+ 降级运行 |

**Codegen 覆盖防护清单**：

```yaml
# data/cache/codegen_fix_manifest.json —— 引擎自动维护
# 记录所有被 codegen 覆盖但已手动修复的文件及修复 diff
fixes:
  - file: "src/zephyr/l02_alpha_factor/__init__.py"
    sha256_before_fix: "abc123..."        # codegen 生成的原始 __init__.py
    sha256_after_fix: "def456..."          # 手动修复后的 __init__.py
    fix_description: "补全 FactorRegistry/autodiscover_factors 导出"
    fix_source: "session-20260505-005"     # 哪个 session 做的修复
    detection:
      current_sha256: "abc123..."          # ← 引擎运行时检测到的当前值
      status: "OVERWRITTEN"                # OK | OVERWRITTEN
      overwritten_by: "codegen-v2.3.0"     # 推断的覆盖源
```

### 3.9 Doom Loop 防护与修复升级阶梯（v0.6.0 新增 — Wave 2 落地）

**核心问题**：Vibe Coding 项目有一个已知的"末日循环"——每次 AI 修复创造 1 个新问题 + 打碎 1 个旧功能。如果去重引擎的自动修复也触发了这个模式，后果是灾难性的。
业界研究证实了 4 个加剧因子：Context Rot（32K tokens → 50%性能下降）、Non-determinism（相同 prompt → 不同代码，方差可达 70%）、No Blast Radius（AI 改代码无依赖图）、Symptom Patching（修症状不修根源）。

**Doom Loop 在去重场景下的具体表现**：
  1. auto_fixer 提取函数到 shared
  2. verifier.py 测试失败
  3. AI 尝试修复 import/引用问题
  4. 修复导致 3 个新文件 break
  5. 尝试修复新的 breakage
  6. 原始 shared 函数又被无意改动
  7. 循环...

**修复升级阶梯（Fix Escalation Ladder）**：
去重引擎不是"修 or 不修"的二元选择——顶尖设计需要阶梯式响应。

| 阶梯 | 条件 | 动作 | 触发下一阶梯条件 |
|:---:|------|------|------|
| **L0: Direct Fix** | suitability ≥ 70 + similarity ≥ 0.95 + pure function | 自动提取→替换→行为采样验证（Stage 0.25）→通过 | — |
| **L1: Partial Fix** | L0 失败 or suitability 40-69 or 有副作用 | 只提取 LCS 公共核心（partial_extraction）→ 保留差异→验证 | 行为采样 pass + import 无循环依赖 |
| **L2: Retry Once** | L1 失败 + 失败原因为 import/引用问题 | 回滚 L1 → 分析失败原因 → 修正 → 重新尝试 partial fix | — |
| **L3: Escalate** | L2 失败 or 是第二次尝试该 DUP group | 回滚全部 → 生成详细失败分析报告 → 写入 Session Log → 标记 needs_review → **分配 TaskCard DEDUP-REVIEW-{N}** | — |
| **L4: Stop + Alert** | 任何 DUP group 在 24h 内被尝试修复 ≥3 次 | **冻结该 DUP group**（加入 `doom_loop_freeze_list.json`）→ 告警写入 Session Log → 生成"为什么修不好"的分析报告 → **需要 Owner 手动解除冻结** | Owner 手动 1 次性解除 |

```yaml
# data/cache/doom_loop_freeze_list.json —— 引擎自动维护
frozen_groups:
  - dup_id: "DUP-20260505-003"
    frozen_at: "2026-05-05T15:30:00Z"
    attempt_count: 3
    last_failure_reason: "修复后 L05 层 reports.py 导入解析失败——循环依赖检测触发"
    analysis: "该重复组涉及 4 层之间的契约数据流，直接提取会打破跨层导入约定"
    suggested_approach: "分两阶段处理——①先提取数据转换核心到 shared ②更新各层 __init__.py 导入路径"
    unfreeze_by: "Owner 手动检查后执行 --unfreeze DUP-20260505-003"
```

### 3.10 共享函数生命周期管理（v0.6.0 新增 — Wave 2 落地）

**核心问题**：行业实践反复强调——共享库的真正挑战不是创建，而是**持续维护**。Shared 函数随时间演化，版本漂移、过时废弃、被 fork 替代...但无人跟踪这些状态。
当前蓝图有 `stale_shared_detector.py` 能检测"变陈旧了"，但没有定义"然后呢？"。

**共享函数生命周期五阶段**：

```
[Active] ──→ [Deprecated] ──→ [Grace Period] ──→ [Sunset] ──→ [Retired]
  活跃          被标记废弃        宽限期（N 天）     日落期             已移除
  │                │                 │                 │                 │
  │                │                 │                 │                 │
  所有 caller     新增 caller      仅存量 caller    仅存量 caller    代码中已删除
  正常使用         告警（WARN）     告警（ERROR）    告警（ERROR）    仅存历史记录
                                  迁移指引注释     阻断 pre-commit  KB 中保留指纹
```

| 阶段 | 触发条件 | 引擎行为 | 对 Caller 的影响 |
|------|------|------|------|
| **Active** | `stale_score < 30` | 正常情况——健康报告中列为正常共享函数 | 无影响 |
| **Deprecated** | `stale_score ≥ 30` or 有替代函数 or Owner 手动标记 | ①报告中标记 `deprecated: true` ②Session Log 中提示 ③**不自动推荐给新 AI session 的影子清单（降级为"冷规则"）** | 新增 caller 首次引用 → WARN（exit code 1） |
| **Grace Period** | Deprecated 状态 ≥ 14 天 or stale_score ≥ 60 | ①影子清单中移除 ②CI 中标记为"宽限期" ③生成迁移 diff（`deprecated_func` → `new_func`） | 新增 caller → ERROR（exit code 2） |
| **Sunset** | Grace Period 状态 ≥ 30 天 or stale_score ≥ 80 or 所有 caller 已迁移 | ①pre-commit 阻断引用 ②引擎报告 Highlight "应移除" ③自动生成移除 PR（TaskCard SUNSET-SHARED-{N}） | pre-commit 阻断（exit code 2） |
| **Retired** | Sunset 后函数已被删除 | ①KB 中保留函数签名指纹 + 退役原因 ②`function_cache.json` 中标记 `status: retired`（供历史查询） | 无——代码中已不存在 |

```yaml
# shared_lifecycle.yaml —— 引擎 + shared_lifecycle_manager.py 自动维护
lifecycle_entries:
  - shared_func: "zephyr.shared.time_utils.legacy_timestamp"
    status: "deprecated"
    deprecated_since: "2026-05-01"
    stale_score: 45
    replacement: "zephyr.shared.time_utils.now_iso"
    active_caller_count: 3
    callers:
      - "orchestrator/backup_scheduler.py"
      - "context_engine/legacy_adapter.py"
    grace_period_ends: "2026-05-15"
    sunset_date: "2026-06-01"
    migration_diff: "s/legacy_timestamp()/now_iso()/g"
```

### 3.11 Import表面积负债追踪（Shared Burden Score — v0.6.0 新增 — Wave 2 落地）

**核心问题**：每一次去重提取到 shared，都创造了一个新的耦合点。项目从 A→B、A→C 的简单依赖变成 A→shared、B→shared、C→shared——代码行数减少了，但**导入边数**增加了。
当有 30+ 模块 import 同一个 shared 函数时，修改这个函数的影响面比原来分散在各处的重复函数更严重。

**Shared Burden Score（SBS）——0-100**：

```
SBS = min(
  100,
  (shared_import_total / max_safe_shared_imports) * 50 +
  (max_dependents_per_func / max_safe_per_func) * 30 +
  (cross_layer_dependency_pct / max_safe_cross_layer) * 20
)

其中：
- shared_import_total: 项目中所有 "from zephyr.shared" 的 import 次数
- max_safe_shared_imports: 项目安全上限（当前=80）
- max_dependents_per_func: 单个 shared 函数被最多模块依赖的数量
- max_safe_per_func: 单个函数安全上限（当前=15）
- cross_layer_dependency_pct: 跨层 shared 引用占所有 shared 引用的比例
- max_safe_cross_layer: 跨层引用安全上限（当前=40%）
```

| SBS | 等级 | 引擎行为 |
|:---:|:---:|------|
| 0-30 | **LIGHT** | 正常去重→提取——shared 负担轻 |
| 31-55 | **MODERATE** | 去重正常但新提取需 Suitability Score ≥ 70（而非默认 60）——提高提取门槛 |
| 56-75 | **HEAVY** | 仅提取 similarity ≥ 0.98 的重复 + partial-extract 优先（而非全量提取）+ Health Score 中 SBS 权重提升至 20% |
| 76-100 | **CRITICAL** | ①停止自动提取——引擎建议"shared 债务清算优先级 > 去重" ②生成 TaskCard SHARED-REFACTOR——建议分拆 shared 为 shared-core / shared-utils / shared-contracts ③Owner 需手动解冻 shared 提取 |

```yaml
# shared_burden.yaml —— health_monitor.py 产出
shared_burden:
  score: 42                        # MODERATE
  shared_import_total: 35          # 项目中有 35 个 from zephyr.shared 导入
  max_dependents_per_func: 12       # 最依赖的 shared 函数被 12 模块引用
  cross_layer_dependency_pct: 25    # 25% 的 shared 引用跨层
  top_burdened_functions:
    - "now_iso()": {dependents: 12, cross_layer: 5, risk: "MEDIUM"}
    - "get_repo_root()": {dependents: 10, cross_layer: 7, risk: "HIGH"}
  recommendation: "now_iso() 被 12 模块引用——修改前确保全量测试"
```

### 3.12 Monoculture 免疫——去重成功的根本性悖论（v0.7.0 终极审视——外部取证审计师发现 #1）

**发现**：前三次审计围绕"如何更好地检测/安全地修复重复"。但从未有人问一个根本问题：
**如果去重引擎 100% 成功了，代码库是更安全了还是更脆弱了？**

**悖论**：去重消除重复 → 所有 caller 共享同一个 shared 函数实现 → 这个 shared 函数中的任何一个 bug 现在影响 N 个 caller 而非 1 个。
去重前：N 个 caller 各自有各自的实现 → bug 被隔离在单个 caller。去重后 → **Monoculture**——单一实现成为全系统单点故障。

**Blast Radius Score（BRS）——爆炸半径评分 0-100**：

```
BRS = min(
  100,
  (caller_count / max_caller_threshold) * 40 +                    // 调用方越多，爆炸越大
  (cross_layer_ratio / max_cross_layer) * 30 +                    // 跨层调用越多，破坏越深
  (is_critical_path ? 20 : 0) +                                   // 关键路径=炸弹
  (has_no_independent_test ? 10 : 0)                              // 无独立测试=安全性更低
)

max_caller_threshold: 当前=10, max_cross_layer: 当前=0.5
```

| BRS | 等级 | 含义 | 引擎行为 |
|:---:|:---:|------|------|
| 0-25 | **SAFE** | 爆炸半径低 | 正常去重 |
| 26-50 | **CAUTION** | 开始形成单点依赖 | 去重但标记 `blast_radius: CAUTION`——强烈建议为该 shared 函数增加独立单元测试 |
| 51-75 | **RISKY** | 单点故障可能引发级联故障 | ①去重后必须在 Session Log 中高亮 ②Health Score 中 BRS 权重=15% ③自动生成 TaskCard BRS-AUDIT-{N}——"N 模块依赖同一实现——建议故障注入测试" |
| 76-100 | **DANGEROUS** | 该提取创造了比重复更高的风险 | ①**停止去重**——引擎建议"该重复应保持原状——风险优先于简洁" ②生成"为什么不修复"的报告 ③只有 Owner 手动 `--force-monoculture` 可覆盖 |

```yaml
# monoculture_risk.yaml —— health_monitor.py 产出
monoculture_top_risks:
  - shared_func: "zephyr.shared.time_utils.now_iso"
    blast_radius_score: 78             # DANGEROUS——被 12 模块引用+跨 5 层
    caller_count: 12
    cross_layer_count: 5
    layers_affected: ["L01", "L02", "L04", "L05", "L07"]
    on_critical_path: true             # Event Loop → 所有时间计算依赖此函数
    has_independent_unit_test: false   # 只有集成测试经过此函数
    recommendation: "KEEP_DUPLICATED——为该函数编写独立单元测试后再考虑去重；当前去重风险 > 收益"
    mitigating_action: "先实现 now_iso 的独立单元测试 ≥ 5 条 → BRS 降至 48 → 可去重"
```

**Monoculture 免疫的核心洞察**：不是所有重复都该消除。当 `shared_func.blast_radius_score > duplication_debt_score` 时，去重本身在创造新的、更危险的技术债——**分散的重复是天然的 blast radius 隔离机制**。

### 3.13 Grandfather 三定律——引擎安装前的古老纠缠（v0.7.0 终极审视 #2）

**发现**：蓝图假设去重引擎安装于项目初期。但外部审计师会问：**引擎安装时项目已有大量"古老"的重复代码——它们可能已经被测试了 6 个月，多个模块深度依赖，提取 = 灾难**。

**Grandfather 三定律**（超过 30 天的重复代码适用）：

| 定律 | 内容 | 实现 |
|:---:|------|------|
| **第一定律：永不自动修复** | 任何在 `function_cache.json` 中首次记录时间 ≥ 30 天前（即引擎安装前就存在的重复），默认 `auto_fix = false`——**只能 manually reviewed** | `grandfather_check()`——检测 `first_detected_at` 字段 → 距今 > 30 天 → 自动标记 `grandfather: true` + `auto_fix: false` |
| **第二定律：化石记录** | ≥ 60 天的古老重复进入"化石记录"——保留在报告中但降级为 informational（exit code 0），不再作为 WARN/ERROR。它们被认定为"architecture-as-is"——不是债务而是地质层 | `fossilize()`——距今 > 60 天 → 报告中 `severity: informational` → 不参与 Health Score 减值 → 保留 `function_cache.json` 中的 `grandfather_record` 用于历史追溯 |
| **第三定律：考古豁免** | 移除一个 Grandpa 重复前必须先通过"考古测试"：①该重复首次出现的 commit 能找到（git log -S）②该重复的所有 caller 有独立测试覆盖 ③该重复的修复有 rollback plan（一个 `git revert` 命令）。三点全部满足 → Owner 可手动 `--override-grandfather DUP-xxx` | `archaeology_check()` → 生成考古报告 → 不满足则拒绝提取 |

```yaml
# grandfather_registry.yaml —— cache_manager.py 自动维护
grandfathered_duplicates:
  - dup_id: "DUP-20251101-007"
    first_detected: "2025-11-01"
    age_days: 186                           # 6个月老的重复
    status: "FOSSILIZED"
    functions: ["_parse_args_old", "parse_cli_args"]
    callers: ["cli/report.py", "cli/scan.py", "cli/watch.py"]
    archaeology:
      first_commit: "abc1234 (2025-10-15, 'initial CLI skeleton')"
      callers_with_tests: 1                 # 只有 1 个 caller 有测试 → 不满足第三定律
      rollback_plan: "git revert <fix-commit> — 单命令可回滚"
    recommendation: "KEEP——考古测试未通过（caller测试覆盖不足）。此重复是 CLI 架构的基石部分"
```

### 3.14 原子性修复——中断操作的崩溃恢复（v0.7.0 终极审视 #3）

**发现**：当前 auto_fixer 的描述是"提取→替换→验证→回滚失败"。外部审计师立刻发现一个致命漏洞：**如果进程在"提取"和"替换"之间崩溃了（断电/OOM/crash），代码库会处于不一致状态**——shared 中有新函数但 caller 没更新，或 caller 更新了 import 但 shared 没创建函数。

**WAL 式 fix_plan + 原子性提交**：

```
1. PREFLIGHT（干运行）：
   → 生成 fix_plan.yaml（所有要创建/修改/删除的文件及 diff）
   → 验证 fix_plan 语义完整性（所有 import 可解析 + 无循环依赖 + 所有引用可追溯）
   → 计算 plan_hash = SHA256(fix_plan)

2. CHECKPOINT（快照）：
   → 备份所有被影响的文件的原始内容到 fix_checkpoint_{plan_hash}.tar.gz
   → 备份所有被影响的文件的 SHA256 列表到 fix_manifest_{plan_hash}.json

3. APPLY（顺序执行）：
   → 按 fix_plan 中的依赖顺序依次执行文件修改
   → 每个文件修改后立即验证其 SHA256 与 plan 中的 expected_sha256 一致
   → 任何步骤 SHA256 不匹配 → ABORT → 跳转到 RECOVER

4. RECOVER（崩溃恢复）：
   → 引擎下次启动时扫描 fix_checkpoint_*.tar.gz 残留文件
   → 发现未完成的 fix_plan（checkpoint 存在但 completion_marker 不存在）
   → 自动从 checkpoint tar.gz 恢复所有原始文件
   → 写入 Session Log："检测到未完成的修复操作 DUP-xxx，已自动恢复代码库到修复前状态"
```

```yaml
# fix_plan.yaml —— auto_fixer.py 生成，引擎崩溃后恢复的依据
plan:
  plan_hash: "sha256:abc123def456..."
  dup_id: "DUP-20260505-012"
  status: "in_progress"                    # preflight | in_progress | completed | recovered
  created_at: "2026-05-05T16:00:00Z"
  steps:
    - step: 1
      action: "CREATE_FILE"
      file: "src/zephyr/shared/time_utils.py"
      expected_sha256: "sha256:111..."
      depends_on: []
      completed: true
    - step: 2
      action: "MODIFY_FILE"
      file: "src/zephyr/l02_alpha_factor/factor_registry.py"
      expected_sha256: "sha256:222..."
      depends_on: [1]
      completed: false                     # ← 崩溃发生在这里——step 1 已执行，step 2 未执行
      diff: |
        -from .time_utils import _now_iso
        +from zephyr.shared.time_utils import now_iso
  crash_marker: "checkpoint saved at fix_checkpoint_abc123def456.tar.gz"
  completion_marker: null                  # ← null = 未完成——引擎下次启动自动 recover
```

### 3.15 漏报盲审——请证明没有系统性遗漏（v0.7.0 终极审视 #4）

**发现**：前三次审计围绕误报（FPR）做了详尽防御（惯用法豁免+设计模式白名单+路径感知阈值+Owner学习+策略树）。但外部审计师会问一个更致命的问题：**你的系统偏向漏报——你怎么知道没有系统性遗漏？你怎么证明漏报率在可接受范围内？**

当前的 `engine_self_observability` 只追踪 FPR，没有追踪 FNR（False Negative Rate）。

**三层漏报盲审机制（Wave 2 落地）**：

| 层级 | 名称 | 方法 | 频率 | 输出 |
|:---:|------|------|:---:|------|
| **L1: Sensitivity Sweep** | 影子低阈值扫描 | 每月降低全局阈值 0.15（context: 0.6→0.45, general: 0.7→0.55），重新全量扫描，发现低阈值下的"新重复"——它们是当前阈值漏掉的潜在重复。生成 diff_of_diffs 报告——"正常阈值漏掉了 X 组" | 每月 | `sensitivity_report.yaml` + `threshold_delta_analysis.md` |
| **L2: Canary注入** | 故意埋入已知重复 | 在 `tests/fixtures/canary_duplicates/` 中维护 5-10 组已知的、不应该被检测出来的"非重复对"（canary_negatives——测试特异性）+ 5-10 组已知"应该被检测出来的重复对"（canary_positives——测试灵敏度）。每次全量扫描后自动验证 canary 结果。canary 漏掉 → FNR 上升告警 | 每次全量扫描 | `canary_report.yaml` + FNR 趋势曲线 |
| **L3: Sampled Human Audit** | 抽样人工审查 | 每周从"引擎报告为 non-duplicate 但相似度 ≥ 0.55 的对"中随机抽 10 组 → 生成审查卡片 → AI/Owner 审查 → 发现真重复 → 反馈为什么引擎漏掉了 → 更新检测规则 | 每周 | `sampled_audit_findings.yaml`——循环驱动 Lean Six Sigma 改善 |

```yaml
# sensitivity_sweep_report.yaml —— Wave 2 health_monitor.py 产出
sensitivity_sweep:
  date: "2026-06-01"
  normal_threshold_findings: 5            # 正常阈值发现 5 组
  lowered_threshold_findings: 9           # 降低阈值后发现 9 组（多了 4 组潜在漏报）
  fnr_estimate: "≈ 44%"                   # 漏报率约 44%——高！
  new_findings:
    - dup_id: "SWEEP-20260601-001"
      similarity_at_normal: 0.62          # 正常阈值 0.65 下被漏掉
      similarity_at_lowered: 0.62         # 降低到 0.50 后被检出
      functions: ["_init_db", "init_database"]
      review_result: "TRUE_DUPLICATE"     # 人工审查确认是真重复
      root_cause: "不同文件不同函数名——无签名碰撞检测触发"
  recommendation: "建议在 Stage 0.5 中增加函数名相似度匹配（Levenshtein距离≤2→进行更深层比较）"
```

```yaml
# canary_report.yaml —— 每次全量扫描自动生成
canary:
  positives:
    total: 8
    detected: 7
    missed: 1                             # 灵敏度下降——漏掉了一个已知重复
    missed_case: "canary_002——函数被拆分为两个嵌套函数后引擎不再识别为重复"
    sensitivity: 87.5%                    # 上次98%→本次87.5%——恶化！
  negatives:
    total: 6
    correctly_exempted: 6
    incorrectly_flagged: 0
    specificity: 100%
```

### 3.16 Shadow Manifest 信任链——AI幻觉的ImportError防护回路（v0.7.0 终极审视 #5）

**发现**：影子清单（Shadow API Manifest）被注入 AI session context 来防止重复生成。但影子清单本身是引擎生成的，引擎本身是 AI 构建的。
**外部审计师的致命问题：如果影子清单中包含一个 AI 幻觉出来的、不存在的函数，AI session 会导入它 → ImportError → 整个模块加载失败**。

**信任链验证回路**：

```
引擎生成影子清单
  → shadow_validator.py（新增——Wave 2）：
      ① 对清单中的每个函数执行 `python -c "from zephyr.shared.xxx import func"` 
      ② import 成功 → 标记 verified
      ③ import 失败 → 标记 HALLUCINATED → 自动从清单移除 → 写入 Session Log
  → 清单消费端（Context Engine）：
      ④ 注入 AI context 前再次执行 spot-check（随机 10% 函数验证 import）
      ⑤ spot-check 失败率 > 10% → 拒绝注入本次影子清单——回退到"无清单模式"（AI 自由生成但不被影子约束）
  → 反馈回路：
      ⑥ HALLUCINATED 函数的指纹加入引擎黑名单——永远不再生成此函数
```

```yaml
# shadow_trust.yaml —— shadow_validator.py 产出
shadow_trust:
  last_validated: "2026-05-05T15:00:00Z"
  total_functions_in_manifest: 35
  verified: 33
  hallucinated: 2
  hallucinated_entries:
    - func: "zephyr.shared.data_utils.legacy_migrate"
      reason: "ImportError——data_utils.py 中不存在 legacy_migrate 函数"
      hallucination_source: "推断——v0.6.0 引擎升级时签名漂移导致生成了过期函数的幽灵条目"
  trust_score: 94.3%                      # 94.3% 的函数可信任——良好
  spot_check:
    sample_size: 4
    pass_rate: 100%
  recommendation: "清单可信——2个幻觉函数已自动清除。Trust Score ≥ 90%——可安全注入"
```

### 3.17 Temporal Signature Drift——渐进类型化打破指纹缓存（v0.7.0 终极审视 #6）

**发现**：Stage 0.5 签名指纹 `SHA256(param_types + return_type)` 假设函数的类型注解是静态的。但在 Python 中，类型注解在开发过程中持续演化——`str` → `Optional[str]` → `str | None` → `float | None`。每一次演化都会改变签名指纹，使 Stage 0.5 的有效性持续退化。
**外部审计师的致命问题：6 个月后，函数签名可能已经和缓存中的签名完全不同——引擎在比对的是"过去的影子"。**

**Temporal Drift 检测 + 自动重算**：

```
每次全量扫描时：
  ① 对 function_cache 中的每个函数条目执行 AST 重新解析
  ② 重新计算 signature_fingerprint
  ③ 对比新旧 fingerprint → 不同 = mark "SIGNATURE-DRIFT-DETECTED"
  ④ 更新缓存中的 fingerprint + 记录 drift_history
  ⑤ 检测到连续 3 次扫描 fingerpirnt 都不同 → "UNSTABLE-SIGNATURE" → 将该函数标记为 unstable
     → Stage 0.5 不再对此函数做签名碰撞检测 → 降级到 Stage 1-2
```

```yaml
# drift_registry.yaml —— cache_manager.py 自动维护
drift_entries:
  - func: "zephyr.shared.config_loader.load_config"
    fingerprint_history:
      - at: "2025-12-01"
        fingerprint: "sha256:a1b2c3..."
        params: "(str, Dict[str, Any])"
        return_type: "Config"
      - at: "2026-02-15"
        fingerprint: "sha256:d4e5f6..."
        params: "(str, Optional[Dict[str, Any]])"
        return_type: "Optional[Config]"             # ← 类型漂移！
      - at: "2026-05-01"  
        fingerprint: "sha256:g7h8i9..."
        params: "(str, dict[str, Any] | None)"
        return_type: "Config | None"                # ← 再次漂移！
    stability: "UNSTABLE"                            # 3 次扫描 3 个不同指纹
    stage_0_5_action: "SKIP"                         # 签名匹配对此函数关闭
    recommendation: "类型注解仍在重构中——待 API 稳定后手动标记为 STABLE 恢复 Stage 0.5"
```

### 3.18 引擎成本效益自审计——引擎自身是最重的技术债吗？（v0.8.0 终极审视 #7——外部取证审计师发现的最根本盲点）

**发现**：前六次审计都围绕"如何更好地检测/修复"展开。但外部取证审计师会问一个釜底抽薪的问题：
**"这个33模块的去重引擎，它的维护成本是否已经超过它消除的重复代码的成本？如果是——那么引擎本身就是项目中最重的技术债。"**

在 1人+AI 维护的语境下，这个问题的答案可能随时间变化——项目初期去重收益极高，但随着项目稳定和代码冻结，引擎继续运行的成本可能超过收益。

**引擎自审计公式（Self-Audit Score, SAS——0-100）**：

```
SAS = min(
  100,
  (total_dedup_benefit / (total_engine_cost + epsilon)) * 100
)

total_dedup_benefit = Σ(每组已修复重复的预估节省——开发时间 + bug修复时间 + 认知负荷)
total_engine_cost = engine_fix_hours + engine_scan_overhead_hours + engine_false_positive_triage_hours

epsilon = 0.01（防止除零）
```

| SAS | 等级 | 含义 | 引擎行为 |
|:---:|:---:|------|------|
| 80-100 | **EFFICIENT** | 引擎带来的收益远超维护成本 | 正常运行 |
| 50-79 | **BREAKEVEN** | 收益与成本大致持平 | 正常运行但标记"接近成本边界" |
| 25-49 | **QUESTIONABLE** | 维护成本开始接近收益 | ①Session Log 告警——"引擎成本效益比恶化" ②提取新功能建议冻结——不新增模块 ③自动修复降速——批次大小从 3→1 |
| 0-24 | **NET_NEGATIVE** | 引擎维护成本已超过收益 | ①停止所有自动修复——仅保留检测能力 ②健康报告中高亮"引擎自身为净债务" ③生成退役建议——"保留检测+关闭修复=月度节省 X 小时" |

```yaml
# simplicity_audit.yaml —— health_monitor.py 每月产出
simplicity_audit:
  date: "2026-07-01"
  self_audit_score: 62                     # BREAKEVEN——接近边界
  engine_cost:
    monthly_maintenance_hours: 3.5         # 引擎bug修复+Tree-sitter升级+依赖更新
    monthly_scan_overhead_hours: 0.5       # CI 中全量扫描耗时累计
    monthly_false_positive_triage_hours: 1.2  # Owner 审查误报耗时
    total_monthly_cost_hours: 5.2
  dedup_benefit:
    duplicates_prevented_past_month: 15    # 本月拦截的新重复组
    duplicates_auto_fixed_past_month: 4    # 本月自动修复的组
    estimated_hours_saved: 6.0             # 重复代码维护+bug修复预计节省
  verdict: "引擎仍为正收益，但边际递减——上月 SAS=78 → 本月 SAS=62"
  recommendation: "未来三个月若 SAS 持续 < 50 → 建议引擎进入 '只检测不修复' 轻量模式"
```

**Simplicity Audit 的核心原则**：引擎必须定期回答"我是否值得存在"。如果一个去重系统连自己的成本效益都不敢审计，它就失去了道德立足点。

### 3.19 死共享模块检测——僵尸坟场扩大到模块级（v0.8.0 #8）

**发现**：§3.10 的生命周期管理只追踪**单个共享函数**的状态。但一个 `shared/` 子模块（整个 `.py` 文件）可能所有函数都进入 Deprecated/Retired 状态——而文件本身仍存在于磁盘上，消耗认知负荷（"这个文件还要不要？"）和 lint 时间。

**死模块检测规则**：

```
dead_module判定条件（全部满足）：
  ① 模块内所有函数 lifecycle_status ∈ {deprecated, retired}
  ② 模块内无 Active 状态的函数
  ③ 项目中无任何 `from zephyr.shared.xxx import` 引用该模块中 Active 函数
  ④ 模块的最后修改日期 ≥ 90 天前
```

| 状态 | 条件 | 引擎行为 |
|------|------|------|
| **ZOMBIE_CANDIDATE** | 全部函数 deprecated 但仍有 ≥1 个 caller | Session Log 提示："模块 X 所有函数已弃用但有残留调用方——建议全部迁移后删除模块" |
| **DEAD** | 全部函数 retired + 零 caller + ≥90 天未修改 | ①生成 TaskCard DEAD-MODULE-{N}——"删除 dead shared 模块" ②报告中标记 `dead_modules` 计数 ③自动生成删除 PR（dry-run 可选） |
| **GRAVEYARD** | 已删除但 KB 保留记录 | `shared_graveyard.yaml` 中保留模块签名 + 删除日期——防止未来重新创建 |

```yaml
# dead_module_report.yaml —— shared_lifecycle_manager.py 产出
dead_modules:
  - module: "src/zephyr/shared/legacy_adapters.py"
    status: "DEAD"
    functions_all_deprecated_since: "2026-02-01"
    last_caller_migrated: "2026-04-15"
    days_since_last_modification: 95
    recommendation: "所有函数已退役且无调用方——建议删除此文件以减少认知负荷"
    dry_run_delete: "2026-07-15"      # 建议的安全删除日期（再等 15 天确认）
```

### 3.20 提取后稳定观察期——工业级安全部署实践（v0.8.0 #9）

**发现**：当前 auto_fixer 执行"提取→替换→验证→通过→下一个"。这忽略了工业界（Microsoft SDP、Netflix Staged Rollout）的核心实践：**任何影响多模块的变更都需要部署后的观察期**。提取到 shared 后立即进入下一轮提取——如果 shared 函数有隐藏 bug，可能在观察期才暴露（特定输入组合、边缘条件、竞态）。

**稳定观察期机制（Observation Window——14 天）**：

```
auto_fixer 执行完一批提取后：
  → 进入 OBSERVATION 模式（14 天）
  → 期间行为：
      ① 暂停所有新的自动提取——不做新修复
      ② 持续监控 Health Score（观察是否下降）
      ③ 收集行为采样数据——抽查新 shared 函数的输出稳定性
      ④ 监听 verifier.py 报告——是否有回归 bug 被报告
  → 观察期结束（14 天后）：
      ① 全部指标稳定 → resume 自动提取
      ② 任一指标恶化 → 延长观察期 7 天
      ③ 同一 shared 函数触发 ≥2 个回归报告 → 标记 FRAGILE → 回滚提取
```

| 观察期状态 | 条件 | 引擎行为 |
|:---:|------|------|
| **ACTIVE** | 正常执行自动修复 | 正常提取 |
| **OBSERVING** | 刚刚完成一批提取后的 14 天 | 只检测、不修复；Health Score 标注"观察中" |
| **EXTENDED** | 观察期满但有轻微异常 | 再观察 7 天；异常分析写入 Session Log |
| **ROLLBACK** | 观察期内发现提取引入 bug | 回滚最近一批提取的全部变更；标记 DUP group 为 FRAGILE；加入 `fragile_extractions.yaml` |

```yaml
# observation_window.yaml —— atomic_fixer.py 自动维护
observation:
  status: "OBSERVING"
  started_at: "2026-05-10T12:00:00Z"
  ends_at: "2026-05-24T12:00:00Z"
  batches_under_observation:
    - batch_id: "FIX-BATCH-20260510-001"
      dup_groups: ["DUP-20260510-001", "DUP-20260510-003"]
      newly_shared_functions:
        - "zephyr.shared.validation_utils.validate_input"
  health_snapshot_start: 85
  health_snapshot_current: 85         # 持平——良好
  stability: "STABLE"
  resume_auto_fix_at: "2026-05-24T12:00:00Z"
```

### 3.21 恢复失败的恢复——原子修复的递归安全网（v0.8.0 #10）

**发现**：§3.14 的原子修复假设"CHECKPOINT tar.gz 总是可恢复的"。外部审计师会立即追问：**如果 checkpoint tar.gz 本身已损坏（磁盘坏道/进程被kill在半写/文件系统满导致截断的 tar.gz），恢复机制本身失败了怎么办？**

这是一个递归信任问题——你信任恢复机制，但谁监督恢复机制？

**双层恢复安全网（Recovery-from-Recovery）**：

```
Layer 1（主恢复——CHECKPOINT tar.gz）：
  → 从 fix_checkpoint_{plan_hash}.tar.gz 恢复所有原始文件
  → 恢复后 SHA256 逐一验证 → 全部通过 → 成功

Layer 2（后备恢复——Human-Readable Recovery Manifest）：
  → 在生成 checkpoint tar.gz 的同时，也生成一个纯文本恢复清单：
    recovery_manifest_{plan_hash}.txt
  → 包含：每个被修改文件的原完整内容（base64）+ diff + 文件路径
  → 这是"最后的防线"——即使 tar.gz 完全损坏，Owner 可手动逐个文件恢复
  → 恢复清单永不依赖于压缩工具——纯文本可由任何编辑器打开
```

```yaml
# recovery_manifest_{plan_hash}.txt —— 与 checkpoint 同时生成
# 纯文本格式——不依赖任何工具即可阅读

RECOVERY MANIFEST for fix_plan FIX-20260505-012
=================================================
Plan Hash: sha256:abc123def456...
Created: 2026-05-05T16:00:00Z
Files affected: 3

--- FILE 1 ---
Path: src/zephyr/shared/time_utils.py
Action: CREATE
Original: (file does not exist)
---
--- FILE 2 ---
Path: src/zephyr/l02_alpha_factor/factor_registry.py
Action: MODIFY (line 45-48 replaced)
Original content (base64):
ZGVmIF9ub3dfaXNvKCk6CiAgICBmcm9tIGRhdGV0aW1lIGltc...
Diff:
-from .time_utils import _now_iso
+from zephyr.shared.time_utils import now_iso
---
```

| 恢复尝试层级 | 方法 | 失败时的回退 |
|:---:|------|------|
| **R0: 预检查** | 修复前SHA256验证所有目标文件与预期一致 | 文件已被外部修改 → ABORT → 不做任何改动 |
| **R1: tar.gz 恢复** | 解压 checkpoint → 覆盖文件 → SHA256验证 | 解压失败 or SHA256不匹配 → 进入 R2 |
| **R2: Manifest 恢复** | 从 recovery_manifest.txt 读取 base64 → 解码→ 逐文件写入→ SHA256验证 | 单个文件恢复失败 → 标记该文件 + 继续恢复其余文件 |
| **R3: 完全手动** | Session Log 写入："修复操作 DUP-xxx 未完成且自动恢复失败。受影响的文件列表：[...]。请从 git 恢复：`git checkout -- file1 file2...`" | — |

**R2 Manifest 的设计原则**：R2 必须是"技术上最基础、最不可能失败"的方案——纯文本文件、内容 base64 编码防止换行/编码问题、每个文件独立恢复。

### 3.22 噪声信号比·主题聚类摘要——当 50 组重复淹没 Owner（v0.8.0 #11）

**发现**：在大项目中，一次全量扫描可能产出 50+ 组重复。Owner 花 30 秒看 Health Score 是好的，但 50 组重复需要 30+ 分钟审查。工作组的研究（IEEE TSE 2024）表明：开发者在面对 >20 条告警时，注意力和判断准确率断崖式下降——前 5 条的审查准确率 ≈85%，第 20 条以后 ≈40%。

引擎必须把"50 组"压缩成"3 个主题"。

**主题聚类摘要（Thematic Clustering Executive Summary）**：

```
主题聚类算法（三层加权）：
  ① 函数名前缀聚类（30%）——"time_"、"validate_"、"parse_"、"format_"
  ② AST 结构模式聚类（50%）——相同的控制流骨架（if→for→return / try→except→raise）
  ③ 目录/模块共现（20%）——同一目录下反复出现的重复模式 → 该目录设计有问题
```

```yaml
# thematic_summary.yaml —— health_monitor.py + prioritizer.py 联合产出
thematic_summary:
  total_duplicate_groups: 47
  themes: 3
  themes_explain_pct: 68                    # 3 个主题解释了68%的重复
  
  themes:
    - theme: "时间/日期工具类"
      explanation: "7个文件各自实现时间戳/格式化/ISO字符串转换"
      duplicate_groups: 12
      affected_files: 18
      root_cause: "AI session 间无共享时间工具记忆"
      one_fix_solves_groups: 10             # 提取一个 shared time_utils 可消除 10 组
      # 重复了 10 个组的根本原因被提炼出来了
      
    - theme: "import 块重复"
      explanation: "23个文件开头有几乎相同的 import datetime/json/os/pathlib/logging 组合"
      duplicate_groups: 9
      affected_files: 23
      root_cause: "没有 shared import 预置模板"
      one_fix_solves_groups: 9              # 一个公共导入块解决所有
      
    - theme: "错误处理模板"
      explanation: "11 个模块各有自己的 try/log/raise 包装模式——结构相同但异常类型不同"
      duplicate_groups: 11
      affected_files: 11
      root_cause: "无统一错误处理装饰器/上下文管理器"
      one_fix_solves_groups: 8              # 共享错误装饰器可解决大部分
```

**主题摘要的使用方式**：
- Wave 1 的 Health Score 旁增加一行：`themes: "时间工具 (12组) + import块 (9组) + 错误处理 (11组)"`
- Owner 只需看这一行，不需要看 47 组

### 3.23 影子清单行为正确性验证——存在≠正确（v0.8.0 #12）

**发现**：§3.16 的 Shadow Manifest 信任链验证"函数是否可 import"（存在性验证）。但外部审计师会追问：**"如果函数存在但行为不正确——例如 shared 函数被后续修改改变了返回值格式——AI session 导入的将是一个'正确 import 但语义错误'的函数。"**

信任链必须从"存在性"升级到"行为正确性"。

**行为正确性验证（Behavioral Trust Check）**：

```
对影子清单中的 critical 函数（caller_count ≥ 5 或 on_critical_path = true）：
  ① 提取函数的"原始行为签名"——在提取时记录：
       behavior_signature = {
         inputs: 5 组代表性采样输入,
         expected_outputs: 对应的预期输出,
         timestamp: 提取时间
       }
  ② 每次全量扫描时重新执行 5 组采样输入
  ③ 对比当前输出 vs 原始预期输出
  ④ 全部匹配 → behavioral_trust = VERIFIED
  ⑤ 任一不匹配 → behavioral_trust = DIVERGED → 告警
```

```yaml
# behavioral_trust.yaml —— shadow_trust_validator.py + behavioral_sampler.py 联合产出
behavioral_trust:
  critical_functions: 8
  verified: 7
  diverged: 1
  diverged_entries:
    - func: "zephyr.shared.validation_utils.validate_input"
      original_behavior_snapshot:
        timestamp: "2026-03-15T10:00:00Z"
        test_case_1: {input: "hello", expected: True, current: True}      # OK
        test_case_2: {input: "", expected: False, current: True}          # ← DIVERGED! 空字符串现在返回 True
        test_case_3: {input: None, expected: False, current: False}       # OK
      divergence_cause: "2026-04-20 commit abc123 修改了空字符串处理逻辑——从'空字符串=无效'改为'空字符串=有效'"
      impact: "3 个 caller 可能受影响——它们依赖原始的空字符串拒绝行为"
      recommendation: "①审查 commit abc123 的变更意图 ②如果行为变更是有意的——更新 behavior_signature ③如果无意的——回滚 + 添加单元测试防止再次漂移"
```

### 3.24 并发源文件修改检测——修复窗口中的外部写入（v0.8.0 #13）

**发现**：§3.14 的原子修复在 PREFLIGHT 阶段对目标文件做了快照（SHA256），然后在 APPLY 阶段逐文件修改。但引擎没有在 APPLY 的**第一步之前**重新验证"所有目标文件是否从 PREFLIGHT 以来保持不变"。

在 Vibe Coding 环境中，以下场景完全可能：
- PREFLIGHT 完成（记录 file_a SHA256=abc）
- AI session 在另一个终端修改了 file_a（SHA256=def）
- APPLY 开始，以 abc 的认知去修改 def 的代码 → **损坏代码**

**并发修改检测窗口（Pre-Apply Integrity Gate）**：

```
APPLY 阶段的第一步（在任何文件被修改之前）：
  → Pre-Apply Integrity Gate：
      ① 重新计算所有目标文件的 SHA256
      ② 逐一与 fix_plan 中记录的 PREFLIGHT SHA256 对比
      ③ 全部一致 → 通过 → 开始 APPLY
      ④ 任一不一致 → ABORT → 不修改任何文件
  → ABORT 后的操作：
      ① Session Log 写入："检测到外部进程修改了目标文件 [file_x]——修复安全中止"
      ② 生成 "修改冲突报告"——PREFLIGHT SHA256 vs CURRENT SHA256 + git diff
      ③ 自动重新生成 fix_plan（基于最新的目标文件状态）——>放入 Session Log 等待下一个修复窗口
```

```yaml
# pre_apply_integrity_gate.yaml —— atomic_fixer.py 在 APPLY 前产出
pre_apply_integrity:
  check_time: "2026-05-05T16:01:00Z"
  preflight_time: "2026-05-05T16:00:30Z"
  target_files: 3
  consistent: 2
  modified_externally: 1
  conflicts:
    - file: "src/zephyr/l02_alpha_factor/factor_registry.py"
      preflight_sha256: "sha256:aaa..."
      current_sha256: "sha256:bbb..."
      diff_summary: "第 122-130 行被外部进程修改——新增了 3 个 import"
      recommendation: "修复计划已自动重新生成（基于最新文件）——等待下一个修复窗口"
  abort_reason: "PRE-APPLY-INTEGRITY-FAILED——1 个目标文件被外部修改"
```

### 3.25 微型克隆检测——高频短模式聚合（v0.9.0 外部审计 #14）

**发现**：当前蓝图在代码块级去重中设置了 `min_block_size=5` 行作为最小检测窗口。但专业机构（Google Tricorder/Meta Glean）的实践表明：
**最高频的复制粘贴往往不是 5+ 行的函数/代码块，而是 1-2 行的微型模式**——它们在单次扫描中 Agent 级别的聚合差异巨大，单个来看无足轻重，但聚合起来代表系统性的抽象缺失。

在 Vibe Coding 场景下，AI 生成代码时尤其容易引入大量微克隆：
- `logger.info(f"{self.__class__.__name__}: {msg}")` 在 50+ 文件中重复
- `result = await self._retry(lambda: api_call(**kwargs))` 重试模板在 15 个 service 中完全一致
- `self._validate_input(data, schema)` + `self._sanitize_output(result)` 模式对反复出现
- `try: ... except Exception as e: logger.error(f"Failed: {e}"); raise` 异常包装模板
- `timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")` 时间戳格式行

**Google/Meta 的做法**：
| 机构 | 工具 | 方法 | 我们能学什么 |
|------|------|------|------------|
| Google | Tricorder + Kythe | **模式频率计数**：对 tokenized 代码做 n-gram 频率统计（n=1,2,3 行），高频 n-gram 标记为"可提取模式候选"——即使单次只出现 2-3 次 | n-gram 频率计数完全不需要 AST/MinHash——纯 token 统计，零依赖、毫秒级 |
| Meta | Glean + Sapienz | **跨仓库模式挖掘**：即使在同一仓库中只出现 1 次，如果在跨多个仓库中出现频率高 → 标记为"组织级抽象候选" | 单仓库中低频但在全局中高频的模式值得关注（为未来跨仓库预留概念入口） |
| JetBrains | IntelliJ 2025.1 | **动态微模式检测**：IDE 实时分析最近粘贴的 1-3 行代码 → 如果相似片段在项目中已存在 ≥5 次 → inline hint "建议替换为 shared 调用" | 不依赖扫描周期——开发时即时反馈，阻止微克隆累积 |

**学术研究佐证**：
- MSR 2024 "Micro-Clones in AI-Generated Code"：AI 辅助编程项目中的微克隆密度是传统项目的 3.8 倍——AI 生成 1-2 行的"最佳实践代码片段"而不自知
- ICPC 2023 "The Cost of Tiny Duplications"：1 行微克隆的累积维护成本（修改一处→忘记改其余 43 处）占去重债务的 22%

**微型克隆检测机制（Wave 1 追加——折叠进 `scanner.py`）**：

```
微型克隆检测三级粒度：
  L0: 单行完全相同（Type-1 微克隆）
    → 逐行计算 SHA256 → 频率计数
    → 同一 SHA256 行在 ≥10 个不同文件中出现 → 标记为 MICRO-DUP-X
    → 加权：source 行权重 1.0 / comment 行权重 0.1 / blank 行权重 0

  L1: 单行归一化相同（Type-2 微克隆）
    → 归一化：变量名 → _VAR_，字符串字面量 → _STR_，数字 → _NUM_
    → 归一化后的 SHA256 频率计数
    → 阈值：≥8 个文件

  L2: 2-3 行连续块归一化相同（Type-2/3 微克隆）
    → 2 行和 3 行滑动窗口 → 归一化 → SHA256 → 频率计数
    → 阈值：≥5 个文件（2行）、≥3 个文件（3行）
```

```yaml
# micro_clone_report.yaml —— scanner.py + health_monitor.py 联合产出
micro_clones:
  single_line_exact:
    total_patterns_found: 7
    top_patterns:
      - pattern: "logger.info(f\"{self.__class__.__name__}: {msg}\")"
        file_count: 52
        files_affected: ["service_a.py", "service_b.py", ...]
        recommendation: "提取为 logging_utils.log_with_classname() —— 一次性消除 52 处重复"
        estimated_savings_lines: 51
      - pattern: "timestamp = datetime.now(timezone.utc).strftime(\"%Y-%m-%dT%H:%M:%SZ\")"
        file_count: 23
        recommendation: "提取为 time_utils.utc_now_iso()——已有 NOW_ISO 但函数名不统一导致 AI 未复用"
        
  two_line_blocks:
    top_patterns:
      - pattern: |
          self._validate_input(data, schema)
          self._sanitize_output(result)
        file_count: 14
        recommendation: "提取为 validation_utils.validate_and_sanitize()"
        
  three_line_blocks:
    top_patterns:
      - pattern: |
          try:
              result = await api_call(**kwargs)
          except Exception as e:
              logger.error(f"API call failed: {e}")
              raise ServiceError(str(e))
        file_count: 8
        recommendation: "提取为 error_utils.async_retry_wrapper()"
```

| 微克隆等级 | 条件 | 引擎行为 |
|:---:|------|------|
| **TRIVIAL** | file_count 3-5 | 报告中记录、不参与 Health Score |
| **NOTABLE** | file_count 6-15 | 报告中 WARN + Health Score 微克隆维度 -1~3 |
| **SIGNIFICANT** | file_count 16-30 | 报告中 HIGHLIGHT + 自动生成提取建议 TaskCard |
| **CRITICAL_MICRO** | file_count > 30 | 写入 Session Log Alert + Health Score -5~10——"X 处微克隆代表系统性抽象缺失" |

**关键设计决策**：微型克隆检测**决不自动修复**——微克隆的提取边界模糊（1 行函数体过于碎片化共享库），仅提供"检测+聚合+建议"。这避免了 shared 目录因微克隆提取而碎片化。

### 3.26 提取后自动测试生成——BRS 缓解的落地机制（v0.9.0 #15）

**发现**：§3.12 Monoculture 免疫指出 BRS ≥ 51 时"强烈建议为该 shared 函数增加独立单元测试"，但没有定义**"测试从哪来"**。在 100% AI 施工 + 低测试覆盖（< 20%）的现实下，手动编写测试不可行。

**Google Testing Culture 的对标**：
Google 的 "Test Certified" 标准要求每个被多个项目依赖的共享库函数必须有独立测试。Google 的做法不是要求开发者手写，而是通过 **Mozart（测试生成框架）** 自动生成参数化测试。

**提取后自动测试生成管道（Auto-Test-Gen Pipeline）**：

```
auto_fixer 完成提取后立即触发：
  ① 类型驱动测试生成：
      → 基于函数签名（参数类型+返回类型）生成边界测试
      → int: 0, 1, -1, MAX, MIN；str: "", "test", "中文", None（若Optional）
      → 每个参数组合 → 生成一个 test case
      → 格式：pytest 标准 parametrize

  ② 执行轨迹金丝雀录制：
      → 提取前的所有调用方执行行为采样
      → 录制成"金丝雀测试"——"函数被提取后，5 组已知输入→输出 必须保持不变"
      → 这是比随机采样更强的保证——来自真实生产调用

  ③ 调用方契约测试：
      → 对每个调用方生成一个"契约测试"——验证 shared 函数替换原重复函数后
        调用方行为不变化
      → contract_test_caller_a_{func_name}.py

  ④ AI 辅助语义测试生成（可选，Wave 3）：
      → 提供函数体 + docstring → LLM 生成"语义正确的复杂场景测试"
      → 当前可选——类型驱动 + 金丝雀已覆盖 80% 用例
```

```yaml
# auto_test_gen.yaml —— atomic_fixer.py 完成后产出
generated_tests:
  for_function: "zephyr.shared.validation_utils.validate_input"
  test_count: 12
  test_types:
    boundary_tests: 6        # 类型驱动——每个参数的边界值组合
    canary_tests: 5          # 执行轨迹金丝雀——提取前的真实输入→输出
    contract_tests: 1        # 调用方契约——每个调用方行为不退化
  test_file: "tests/unit/shared/test_validate_input.py"
  coverage_estimate: 85%     # 生成的测试预计覆盖的代码路径
  blast_radius_impact:
    before_test_gen: 78      # DANGEROUS
    after_test_gen: 48       # CAUTION  —— BRS 从 78→48
    test_gen_justified: true # 测试生成使去重从"危险"变为"可接受"
```

| 自动测试生成范围 | 条件 | 引擎行为 |
|------|------|------|
| **FULL** | BRS ≥ 51（CAUTION 及以上）or caller_count ≥ 8 | 全量生成上述三类测试，写入 test 目录，运行验证 → 通过 → 标记"TEST_GENERATED" |
| **LIGHT** | BRS 26-50（SAFE/CAUTION） | 仅类型驱动边界测试 + 1 组金丝雀 |
| **SKIP** | BRS < 26 + caller_count < 3 | 跳过测试生成——测试维护成本 > 收益 |

**关键设计决策**：生成的测试文件带有 `# @auto-generated-by-dedup` 文件头标记——引擎之后的扫描中识别并跳过这些测试文件内的重复（测试代码合理重复）。

### 3.27 API 契约一致性验证——存在性 + 行为正确性 + 契约一致性 三维信任（v0.9.0 #16）

**发现**：§3.16 影子清单信任链验证了"函数可 import"（存在性），§3.23 行为正确性验证了"函数行为未漂移"（行为正确性）。但外部审计师会发现一个中间维度：
**函数的 API 契约（docstring + 类型注解 + 影子清单描述）是否与函数的实际行为一致？**

这是专业机构极为重视的一个维度。Meta 的 Pyre 类型检查器会验证类型注解与函数体的兼容性；Google 的 Tricorder 在 code review 时会警告"docstring 中的参数列表与函数签名不匹配"。

在 100% AI 施工场景下，此问题尤为严重：
- AI 生成 shared 函数的 docstring 可能与实际实现不一致（AI 幻觉）
- 影子清单描述由引擎自动生成——如果提取的函数签名发生变化，清单描述可能过时
- 类型注解可能比实际行为更宽松（`-> Optional[str]` 但函数体永远返回 `str`）或更严格

**三维信任模型**：

```
Trust Dimension 1: 存在性（§3.16 shadow_trust_validator）
  → "函数可 import 吗？"  → validated / HALLUCINATED

Trust Dimension 2: 行为正确性（§3.23 behavioral_trust_checker）
  → "函数的输出与提取时一致吗？" → VERIFIED / DIVERGED

Trust Dimension 3: 契约一致性（§3.27 contract_consistency_checker——本新增）
  → "API契约（docstring+类型+描述）与实现一致吗？" → CONSISTENT / CONTRACT_MISMATCH
```

```
contract_consistency_checker 验证项：

  L1: Docstring 参数一致性
    → AST 提取 docstring 中 :param 列表
    → 与函数签名中的实际参数列表比对
    → 多出的 :param（已删除的参数）→ DOCSTRING_STALE
    → 缺少的 :param（新增参数无文档）→ DOCSTRING_INCOMPLETE

  L2: 类型注解精确度
    → 类型注解声称 `-> Optional[str]` 但函数体分析显示永远返回 `str`
      （无 `return None` 路径）→ TYPE_OVERAPPROXIMATED
    → 类型注解声称 `-> str` 但实际有 `return None` 路径
      → TYPE_UNDERAPPROXIMATED（更危险！）

  L3: 影子清单描述时效性
    → 影子清单中的 description 字段 vs 当前函数 docstring 的 summary 行
    → 不一致 → SHADOW_DESC_STALE
    → 自动更新清单描述为当前 docstring summary

  L4: 异常契约一致性
    → docstring :raises 列表 vs 函数体中实际 raise 语句
    → 不一致 → RAISES_MISMATCH
```

```yaml
# contract_consistency.yaml —— contract_consistency_checker.py 产出
contract_consistency:
  critical_functions_scanned: 12
  consistent: 9
  mismatches: 3
  mismatches_detail:
    - func: "zephyr.shared.validation_utils.validate_input"
      dimension: "DOCSTRING_INCOMPLETE"
      detail: "docstring 缺少参数 'strict_mode' 的说明（2026-04-20 新增）"
      fix: "自动补全 docstring——追加 :param strict_mode: ..."

    - func: "zephyr.shared.data_utils.parse_config"
      dimension: "TYPE_OVERAPPROXIMATED"
      detail: "类型注解声称 -> Optional[Config] 但函数体无 return None 路径——实际永远返回 Config"
      fix: "建议收紧类型为 -> Config"

    - func: "zephyr.shared.path_utils.resolve_path"
      dimension: "SHADOW_DESC_STALE"
      detail: "影子清单描述为'返回相对路径' 但 docstring 为'返回绝对路径'——函数行为已变更但清单未更新"
      fix: "自动更新影子清单描述匹配 docstring"
```

| 契约一致性状态 | 条件 | 引擎行为 |
|:---:|------|------|
| **CONSISTENT** | 全部 4 层验证通过 | Trust Score 中契约维度满分 |
| **MINOR_INCONSISTENCY** | L1-L3 有 ≤2 个低影响不一致 | 自动修复（补全 docstring、更新清单描述）+ Session Log 记录 |
| **MAJOR_INCONSISTENCY** | L2 类型近似问题 or L4 异常契约不匹配 | WARN + Session Log 高亮——可能影响 AI session 正确使用该函数 |
| **CRITICAL_CONTRACT_BREAK** | 类型低估（声称安全但实际危险）or 连续 3 次扫描契约都在恶化 | ALERT——"共享函数 API 契约正在退化——新 AI session 不应信任该函数" + 从影子清单降级为冷规则 |

### 3.28 跨边界克隆感知——不同代码区域差异化策略（v0.9.0 #17）

**发现**：当前蓝图的路径感知阈值（shared 0.3 / core 0.6 / * 0.7 / tests 0.9）假设克隆只在一个区域内发生。但专业机构的实践表明：
**最高价值的去重往往发生在跨边界场景**——src 和 tests 之间的代码重复、scripts 和 src 之间的逻辑复制、不同层之间解决相同问题的不同实现。

**工业界实践对标**：

| 边界对 | Google 的做法 | 我们的缺口 | 解决方案 |
|------|-------------|---------|---------|
| **src ↔ tests** | Test infrastructure 不应该 mirror production code 的结构——但有 shared test helpers | 当前 `tests/` 阈值 0.9 过于宽松——测试中复制源文件逻辑不会被检测 | 引入 `SRC_TEST_BRIDGE` 分类：src 函数 X 和 tests 中手工实现相同逻辑的测试辅助 → 标记为"测试可改用 shared" |
| **scripts ↔ src** | Build/release scripts 复制 runtime logic 是已知反模式——Google 的 Blaze/Bazel 强制 scripts 只能 import shared | scripts/ 中的独立工具脚本常常重新实现 src/ 中已有的核心逻辑（路径解析、配置加载、日志格式） | 跨 scripts↔src 边界单独计算一组相似度——类似"墙上的裂缝"检测 |
| **L01 ↔ L05** | 各层独立演化是理想——但实践中低层和高层常独立实现相同的横切关注点（时间格式、错误码映射、序列化） | 路径感知阈值只能处理"同区域内"重复，跨层重复需要专门编排 | 引入"跨层热点追踪"——发现 L01 和 L05 各自实现相同工具函数 → 立即升级为 CRITICAL |
| **src ↔ vendored** | Vendored 代码 vs 项目自有代码的"重复实现"（项目自己重写了 vendored 的功能）是非预期的 | 当前 vendored 代码被排除在扫描外 | 对标记为 vendored 目录的函数做"单向指纹索引"——不检测但记录指纹，当 src 中新函数与 vendored 中的匹配 → "你重写了依赖库的功能" |

```yaml
# cross_boundary_report.yaml —— scanner.py + cross_boundary_detector.py 联合产出
cross_boundary_clones:
  src_test_clones:
    - src_func: "zephyr.shared.validation_utils.validate_schema"
      test_func: "tests/unit/test_validation.py::_manual_schema_check"
      similarity: 0.97
      boundary: "SRC_TEST_BRIDGE"
      issue: "测试中手工实现了与 shared 函数 97% 相同的验证逻辑——测试应直接使用 shared 函数而非自己实现"
      recommendation: "替换 test 中的 _manual_schema_check → from zephyr.shared import validate_schema"

  src_scripts_clones:
    - src_func: "zephyr.shared.path_utils.get_repo_root"
      script_func: "scripts/build/generate_docs.py::_find_project_root"
      similarity: 0.92
      boundary: "SRC_SCRIPTS_DIVERGENCE"
      issue: "build script 重新实现了 src 中的路径解析——两者可能在不同环境下行为不一致"
      recommendation: "script 中 import get_repo_root 替换 _find_project_root"

  cross_layer_clones:
    - func_a: "L01 code_dedup_engine/signature_matcher.py::_compute_sha256"
      func_b: "L05 reports/report_generator.py::_hash_content"
      similarity: 0.89
      layers: ["L01", "L05"]
      boundary: "CROSS_LAYER_REDUNDANCY"
      issue: "两个不同层独立实现了 SHA256 计算+截断——应统一为 shared 函数"
      recommendation: "提取到 shared.crypto_utils.shorten_sha256()"
```

**跨边界检测的差异化策略**：

| 边界 | 阈值 | 特殊处理 | auto_fix |
|:---:|:---:|------|:---:|
| **SRC_TEST_BRIDGE** | 0.80 | 检测到 → WARN 不阻断——"测试可简化，但非阻塞" | ❌ 不自动修——测试代码改动需谨慎 |
| **SRC_SCRIPTS_DIVERGENCE** | 0.75 | 检测到 → Session Log 高亮——"scripts 与 src 正在走向 fork" | ❌ 不自动修——scripts 改 import 可能打破 CI |
| **CROSS_LAYER_REDUNDANCY** | 0.80 | 检测到 → **CRITICAL**——"架构分层放弃横切关注点共享"——这是去重的最高价值目标 | ✅ 可自动修（相似度 ≥ 0.95 + 纯函数） |
| **VENDORED_REIMPLEMENTATION** | 0.85 | 检测到 → WARN + 生成"为什么重写了三方库功能"分析 | ❌ |

**关键设计原则**：跨边界克隆的 auto_fix 比同区域内更保守——跨边界意味着不同的运行时上下文、不同的测试环境、不同的导入约定。宁可 WARN 等 Owner 决策也不盲修。

### 3.29 去重决策审计链——引擎行为的不可变追溯（v0.10.0 #18）

**发现**：蓝图当前通过 Session Log 记录了引擎活动的摘要，Health Monitor 提供了健康仪表盘。但缺少一个最关键的能力——**"引擎为什么做了这个决定？"**

对于 1人+AI 维护的场景，这个缺失是致命的：
- Owner 休假 2 周回来，发现 shared/ 多了 8 个新文件——谁加了什么？为什么？正确吗？
- 一个 shared 函数被标记为 ZOMBIE_CANDIDATE——是谁决定的？基于什么数据？
- 引擎漏报盲审发现了一个 Canary 漏了——是系统性退化还是偶发？
- AI session 收到某函数不再推荐的告警——但"为什么不再推荐"的历史原因丢失了

**Google/Meta 的做法**：

| 机构 | 系统 | 审计链实践 | 我们能学什么 |
|------|------|---------|------------|
| Google | Tricorder + Critique | 每个 code review comment 都带**决策指纹**——"rule-id + snapshot-hash + timestamp + 审查者"——任何决策都可以追溯到"哪个规则、哪个版本的代码、谁确认的" | 决策指纹 = 不可变决策 ID + 决策上下文快照 |
| Meta | Sapienz + Phabricator | 自动修复决策带**证据包**——"Detected by X, verified against Y, applied because Z"——回滚时可以看到完整证据链 | 决策附带证据链——不是"做了什么"而是"为什么做" |
| Netflix | Staged Rollout Decision Log | 每个金丝雀决策记录在不可变日志中——用于"如果在阶段 N 出了问题，回滚决定是有据可查的" | 决策不可变——日志追加模式，从不删除只标记 superseded |

**去重决策审计链设计（Decision Audit Trail——`decision_auditor.py`，Wave 2）**：

```
审计链记录等级：
  CRITICAL_DECISION: 代码修改类 + 不可逆（提取到shared / 从shared删除函数 / 自动修复APPLY）
  MAJOR_DECISION:   状态变更类（标记ACTIVE→DEPRECATED / 冻结Doom Loop / BRS ≥ 76→停止去重）
  MINOR_DECISION:   信息类（标记intentional-duplicate / 更新影子清单描述 / 漏报抽样审查结果）
  DEBUG_DECISION:   内部类（缓存刷新 / 签名重算 / Canary轮换）
```

```
决策指纹（DecisionFingerprint）结构：
  {
    "decision_id": "DED-20260506-A3F2B1C",
    "decision_type": "CRITICAL_DECISION",
    "category": "auto_extract_to_shared",
    "timestamp_utc": "2026-05-06T14:23:17Z",
    "session_id": "SESSION-20260506-001",
    "engine_version": "0.10.0",
    "codebase_snapshot_hash": "sha256:abc123...",  // 决策时的代码库指纹
    "evidence_pack": {
      "trigger": "scanner detected dup_group_042 with similarity 0.96",
      "suitability_score": 78,
      "brs_before": 34,
      "brs_after_estimated": 41,
      "blast_radius_check": "PASSED_BRS_41_SAFE",
      "fix_plan_id": "FIX-20260506-001",
      "affected_files": ["src/l05/api_handler.py", ...],
      "rollback_plan_id": "ROLLBACK-FIX-20260506-001"
    },
    "outcome": "APPLIED_SUCCESS",
    "verification": {
      "post_apply_health": 87,
      "post_apply_brs": 41,
      "no_regression": true
    },
    "reversible": true,
    "rollback_id": "ROLLBACK-FIX-20260506-001"
  }
```

```yaml
# decision_audit_log.yaml —— decision_auditor.py 不可变追加日志
decisions:
  - decision_id: "DED-20260506-A3F2B1C"
    type: "CRITICAL_DECISION"
    category: "auto_extract_to_shared"
    summary: "提取 validate_input → shared.validation_utils.validate_input（消除 8 处重复，BRS 34→41 SAFE）"
    timestamp: "2026-05-06T14:23:17Z"
    reversible: true
    rollback_id: "ROLLBACK-FIX-20260506-001"
    
  - decision_id: "DED-20260505-B7E4D2A"
    type: "MAJOR_DECISION"
    category: "lifecycle_deprecation"
    summary: "标记 shared.legacy_parser.parse_v1 → DEPRECATED（caller_count 0 for 60 days + 无测试覆盖）"
    timestamp: "2026-05-05T09:12:44Z"
    reversible: true
    
  - decision_id: "DED-20260504-C1A9F3E"
    type: "CRITICAL_DECISION"
    category: "micro_clone_critical"
    summary: "检测到 CRITICAL_MICRO——52 处 logger.info(f'{self.__class__.__name__}: {msg}')——建议提取为 logging_utils.log_with_classname()"
    timestamp: "2026-05-04T22:01:03Z"
    reversible: false  # 微克隆仅建议不自修——无回滚需求
```

**审计链查询接口（CLI + Session Log 注入）**：

```bash
# Owner 核心查询命令
python -m l01_infrastructure.code_dedup_engine audit --since 2w --type CRITICAL_DECISION
# → 过去 2 周内所有代码修改类决策——每个决策带决策指纹和回滚ID

python -m l01_infrastructure.code_dedup_engine audit --rollback DED-20260506-A3F2B1C
# → 回滚指定的提取决策——恢复被提取的文件 + 从 shared/ 删除函数 + 更新影子清单

python -m l01_infrastructure.code_dedup_engine audit --verify --since 1m
# → 验证过去 1 个月内所有决策是否仍然有效（shared 函数仍存在/行为正确性通过/契约一致性通过）
```

| 审计链属性 | 设计原则 |
|------|---------|
| **不可变** | 追加模式——决策一旦写入永不被修改。撤销/回滚 = 写入新决策 `superseded_by: ROLLBACK-xxx` |
| **证据携带** | 每个 CRITICAL/MAJOR 决策必须附带证据包——"基于什么数据、验证了什么、BRS 变化多少" |
| **可回滚** | 每个 CRITICAL 决策生成一个回滚计划——不能回滚的决策需要显式标记 `reversible: false` + 原因 |
| **跨 Session 可见** | 决策审计日志注入 Session Log——下一个 AI session 可以通过"历史决策摘要"快速理解引擎做了什么 |
| **轻量** | 追加 YAML 行——不建数据库，不引入结构化存储依赖——1人维护场景不需要 SQL |

**关键设计决策**：决策审计链是"最轻量的关键基础设施"——它本质上只是一个 `yaml.safe_dump(decision, f, allow_unicode=True)` 追加操作。复杂度 ≈ 0，价值极大——它解决了 1人+AI 维护场景下最核心的信任问题："我没看的时候，引擎做了什么？"

### 3.30 共享函数主动发现——从被动拦截到主动赋能（v0.10.0 #19）

**发现**：蓝图当前的防重复模型是**"被动拦截"**：Shadow Manifest 注入 AI context → AI 看到已有函数 → AI 不重复创建。GATE-DEDUP 在提交时拦截。这两者都是"等 AI 准备犯错时阻止它"。

但氛围编程社区和 Google 的最新实践揭示了一个更优的范式：**"主动发现——不等 AI 犯错，在 AI 需要写任何代码之前，主动告诉它'这个功能已经有人实现了'"**。

**氛围编程社区的做法**：

| 社区/工具 | 实践 | 本质 |
|------|------|------|
| **Cursor Community** | `.cursorrules` 中预定义 "Before creating any utility function, check if it already exists in `src/shared/`"——但这依赖 AI 自觉遵守 | 被动提醒——AI 可能忽略 |
| **Windsurf/Cascade** | Cascade 的 workspace 索引——自动索引函数名和 docstring——AI 可以"自然语言搜索已有函数" | 主动索引但仍需 AI 主动调用 |
| **Claude Code** | `CLAUDE.md` 指令 + 文件系统访问——Claude 可以 grep 代码库查找已有实现——但依赖 AI 在被要求"写一个 X"时主动搜索 | 依赖 AI 的搜索习惯——不一致 |
| **Sourcegraph Cody** | 上下文引擎——在 AI 生成代码前，"搜索并注入最相关的已有代码片段"——Cody 主动做发现 | **这才是对的**——引擎主动做发现，AI 被动接收 |

**Google 的对标**：
Google 的 Code Search（内部代号 "Kythe + Grok"）做的是同一件事：在你写任何代码之前，Code Search 返回"你要的功能很可能已经被 `//depot/core/util/foo.cc` 实现了"。

**主动发现机制设计（`function_discovery.py`——轻量模块，Wave 2）**：

```
主动发现双通道：

  Channel A: 签名驱动发现（精确）
    → AI session 即将生成函数 foo(x: str, y: int) -> Optional[dict]
    → 引擎对影子清单中所有函数做签名归一化匹配
    → 返回匹配度 > 80% 的 shared 函数列表（按匹配度降序）
    → "STOP——你要写的函数已经由这些实现覆盖：shared.validation_utils.validate_params(str, int) -> dict"
    
  Channel B: 语义驱动发现（模糊）
    → AI session 描述需求："需要一个函数来验证输入参数并记录日志"
    → 引擎对影子清单中所有函数的 docstring + description 做 TF-IDF/嵌入相似度
    → 返回语义最接近的 Top-5 shared 函数
    → "你可能需要的是这些：validate_input / log_with_context / sanitize_and_log"
```

```yaml
# function_discovery.yaml —— function_discovery.py 产出
discovery_index:
  last_indexed: "2026-05-06T14:00:00Z"
  total_indexed_functions: 47
  indices:
    signature_index:  # Channel A——精确签名匹配
      - signature: "validate(str, dict) -> bool"
        functions: ["shared.validation_utils.validate_input"]
      - signature: "resolve(str) -> Path"
        functions: ["shared.path_utils.resolve_path", "shared.path_utils.resolve_relative_path"]
      - signature: "log(str, str) -> None"
        functions: ["shared.logging_utils.log_with_context", "shared.logging_utils.log_error"]

    semantic_index:  # Channel B——TF-IDF + docstring 语义
      - keywords: ["validation", "input", "check", "schema"]
        functions: ["shared.validation_utils.validate_input", "shared.validation_utils.validate_schema"]
      - keywords: ["path", "resolve", "relative", "absolute", "file"]
        functions: ["shared.path_utils.resolve_path", "shared.path_utils.get_repo_root"]
      - keywords: ["log", "error", "context", "classname", "trace"]
        functions: ["shared.logging_utils.log_with_context", "shared.logging_utils.log_with_classname"]
```

**主动发现的触发时机（与现有防线的关系）**：

```
现有防线链（v0.9.0）：
  Stage 0.5 签名碰撞 → Stage 1 Token匹配 → Pre-commit GATE → Shadow Manifest 注入

v0.10.0 新增前置防线：
  ┌─────────────────────────────────────┐
  │ Channel A/B 主动发现 ← 新增！       │
  │ "在你写之前——这个已经有了"          │
  └──────────────┬──────────────────────┘
                 ↓ (如果AI忽略发现→继续创建重复)
  ┌─────────────────────────────────────┐
  │ Stage 0.5 签名碰撞（已有）          │
  │ "你写的签名与已有函数碰撞了"        │
  └──────────────┬──────────────────────┘
                 ↓
  ┌─────────────────────────────────────┐
  │ Pre-commit GATE-DEDUP（已有）        │
  │ "提交被拦截——这已经存在了"          │
  └─────────────────────────────────────┘
```

| 发现结果 | 条件 | 引擎行为 |
|:---:|------|------|
| **EXACT_MATCH_FOUND** | 签名完全匹配 shared 函数 | 主动植入 Context Engine——"STOP: 函数已存在——import 即可" |
| **CLOSE_MATCH_FOUND** | 签名/语义相似 > 80% | 建议列表植入 AI context——"考虑复用这些函数——可能只需微调" |
| **PARTIAL_COVERAGE** | 多个 shared 函数组合可达相同效果 | 组合建议——"validate_input() + sanitize_output() = 你需要的" |
| **NO_MATCH** | 无匹配 | 正常生成——引擎记录 "new_function_candidate: {signature}" 用于未来发现 |

**关键设计决策**：主动发现**不是替代**现有被动防线，而是**前置补充**——它让 AI session 从"我准备犯错→被拦截→被迫修正"变为"我被告知已有方案→直接复用→零摩擦"。对于一个理想中的 AI 编程工作流，前者消耗 2-3 轮对话修正，后者是 0 轮。

**轻量化实现路径**：`function_discovery.py` 不需要 LLM 调用——签名索引是纯字符串匹配（O(1)），语义索引是 TF-IDF + cosine similarity（Python 标准库 `collections.Counter` 即可）。整个模块 < 150 行。

```
src/zephyr/l01_infrastructure/code_dedup_engine/
├── __init__.py
├── scanner.py              # Stage 1: Token 级快速扫描（MinHash + LSH + 代码块级滑动窗口）
├── signature_matcher.py    # Stage 0.5: 签名指纹碰撞检测（O(1)精确匹配——Vibe Coding 性价比最高防线）
├── ast_comparator.py       # Stage 2: AST 级精确比对（子树哈希 + 部分重复 + 模板识别 + Python惯用法豁免）
├── semantic_verifier.py    # Stage 3: LLM 语义验证（可选）
├── cache_manager.py        # Stage 0: 缓存管理（加载/更新/失效 + _integrity自检 + 原子写入 + 自愈重建）
├── diff_detector.py        # Stage 0: git diff 变更检测（增量扫描入口）
├── auto_fixer.py           # Stage 4: 自动修复引擎（提取→替换→验证 + 分批安全机制）
├── ssot_registrar.py       # Stage 5: SSoT 注册（更新 b_shared.yaml + AGENTS.md 共享清单）
├── report.py               # 报告生成（YAML/JSON + 退出码判定 + Health Score + 降级标注）
├── health_monitor.py       # Stage 7: 代码健康仪表盘（Dedup Health Score 计算 + 趋势 + Session Log 写入）
├── prioritizer.py          # 优先级排序算法（重复次数×相似度×影响文件数×热路径权重×ROI因子）
├── hotspot_tracker.py      # AI健忘热点追踪（按函数名前缀聚类 + 重复趋势 + 影子清单强化建议）
├── shadow_verifier.py      # 影子清单消费验证回环（检测新重复→比对影子清单→反馈优化建议）
├── config.py               # 配置（阈值表、路径分区、排除目录、intentional-duplicate 标记正则、惯用法豁免模式、策略树YAML）
├── annotations.py          # @intentional-duplicate 标记解析器 + Owner决策模式学习
├── verifier.py             # 去重后验证（测试全绿 + import可解析 + 无循环依赖）
├── degradation.py          # 降级运行管理（各Stage独立try/except + degradation_level记录 + 降级日志）
├── symbol_index.py         # 轻量符号索引（SQLite——函数签名+调用关系+import图）——Wave 2
├── extraction_safety.py    # 安全提取评估（Suitability Score + 不安全模式目录 + 影响预分析）——Wave 2
├── stale_shared_detector.py # 过期共享函数检测（签名漂移 + 调用参数匹配 + 过期标记）——Wave 2
├── shared_lifecycle_manager.py # 共享函数生命周期管理（5阶段：Active→Deprecated→Grace→Sunset→Retired）——Wave 2
├── import_surface_tracker.py # Import表面积负债追踪（Shared Burden Score 0-100 + 跨层依赖分析）——Wave 2
├── debt_projector.py       # 去重债务预测——"以当前速率 N 周可还清"——Wave 2
├── doom_loop_guard.py      # Doom Loop 防护（修复升级阶梯L0-L4 + 冻结机制 + 失败分析）——Wave 2
├── behavioral_sampler.py   # Stage 0.25: 行为采样快速验证（类型推断采样输入→沙箱执行→输出diff）——Wave 1
├── self_scanner.py         # 引擎自保护（自扫描+Codegen覆盖防护+依赖自检）——Wave 1
├── monoculture_guard.py    # Monoculture免疫——Blast Radius Score计算+去重悖论检测+停止高风险去重——Wave 2
├── atomic_fixer.py         # 原子性修复引擎——WAL式fix_plan+CHECKPOINT+APPLY+RECOVER崩溃恢复——Wave 2
├── grandfather_manager.py  # Grandfather三定律——古老重复管理（永不自动修复+化石记录+考古豁免）——Wave 2
├── false_negative_auditor.py # 漏报盲审——Sensitivity Sweep+Canary注入+抽样审查+FNR趋势——Wave 2
├── shadow_trust_validator.py # Shadow Manifest信任链验证——import存活校验+幻觉清除+spot-check——Wave 2
├── temporal_drift_tracker.py # 签名时态漂移追踪——指纹演化检测+UNSTABLE标记+自动重算——Wave 2
├── simplicity_auditor.py   # 引擎成本效益自审计——SAS计算+净收益评估+退役建议——Wave 2
├── dead_module_detector.py # 死共享模块检测——僵尸文件识别+自动删除建议——Wave 2
├── observation_window_guard.py # 提取后稳定观察期——14天观察窗口+回滚触发——Wave 2
├── recovery_manifest_writer.py # 恢复失败的恢复——R2纯文本恢复清单+递归安全网——Wave 2
├── thematic_clusterer.py   # 噪声信号比·主题聚类——三层加权聚类+Executive Summary——Wave 2
├── behavioral_trust_checker.py # 影子清单行为正确性——原始行为签名+漂移检测+告警——Wave 2
├── pre_apply_integrity_gate.py # 并发修改检测——PREFLIGHT→APPLY间的文件完整性验证——Wave 2
├── micro_clone_detector.py   # 微型克隆检测——n-gram频率计数+L0/L1/L2三级粒度——对高频1-2行模式聚合——Wave 1
├── auto_test_generator.py    # 提取后自动测试生成——类型驱动+金丝雀录制+契约测试——对标Google Mozart——Wave 2
├── contract_consistency_checker.py # API契约一致性验证——docstring+类型+描述+异常四层——三维信任模型——Wave 2
├── cross_boundary_detector.py # 跨边界克隆感知——四大边界差异化策略——对标Google Blaze——Wave 2
├── decision_auditor.py       # 去重决策审计链——DecisionFingerprint不可变追加日志+证据包+可回滚——Wave 2
├── function_discovery.py     # 共享函数主动发现——签名+语义双通道——主动赋能AI——<150行——Wave 2
└── config/                  # 配置目录（含 policy_tree.yaml）——Wave 3

scripts/governance/d1_structure/
├── detect_code_duplicates.py    # CLI 入口（注册到 manifest）——支持 --file 单文件模式
└── fix_code_duplicates.py       # CLI 自动修复入口

tests/unit/
├── test_code_dedup_engine.py    # 单元测试：扫描器 + 比对器 + 签名匹配
├── test_cache_manager.py        # 单元测试：缓存读写 + _integrity自检 + 自愈重建
├── test_auto_fixer.py           # 单元测试：自动修复 + 回滚
├── test_verifier.py             # 单元测试：去重后验证
├── test_signature_matcher.py    # 单元测试：签名碰撞检测 + 误报/漏报边界
└── test_degradation.py          # 单元测试：各Stage降级场景 + degradation_level验证

data/cache/
└── function_cache.json          # 预计算函数指纹缓存（_integrity字段 + 原子写入 + .gitignore）
```

### 4.1 模块职责速查

| 模块 | 单一职责 | AI 自治权限 | 维护复杂度 |
|------|---------|:---:|:---:|
| `cache_manager.py` | 读写 `function_cache.json`——加载、增量更新、全量重建、`_integrity` 自检、原子写入、损坏自愈 | `supervised` | 中 |
| `diff_detector.py` | `git diff --name-only` → 变更文件列表 → 提取变更函数（函数粒度增量——不是文件粒度） | `supervised` | 低 |
| `signature_matcher.py` | Stage 0.5——签名指纹 SHA256[:12] O(1)精确匹配 + 签名碰撞分析（相同签名/近似签名） | `high` | 低 |
| `scanner.py` | Stage 1——Token 级 MinHash + LSH 快速扫描 + 代码块级滑动窗口（非函数级） | `high` | 中 |
| `ast_comparator.py` | Stage 2——AST 子树哈希 + 部分重复 + 模板聚类 + Python 惯用法自动豁免 | `supervised` | 高 |
| `semantic_verifier.py` | Stage 3——LLM 语义等价判断（可选，默认关闭） | `supervised` | 中 |
| `auto_fixer.py` | 自动修复——提取到 shared + 替换引用 + 分批执行 + 失败回滚 | `restricted`（涉及改写代码） | 高 |
| `ssot_registrar.py` | 更新 YAML SSoT + AGENTS.md 共享清单 | `restricted`（涉及改 frozen 资产） | 低 |
| `report.py` | YAML/JSON 报告生成 + 退出码 0/1/2/3/4 判定 + Health Score 聚合 + 降级标注 | `high` | 中 |
| `health_monitor.py` | 代码健康仪表盘——Dedup Health Score 计算 + 趋势对比 + Session Log 摘要写入 | `high` | 低 |
| `prioritizer.py` | 重复组排序——priority_score + ROI 因子 | `high` | 低 |
| `hotspot_tracker.py` | AI 健忘热点追踪——按函数名前缀聚类 + 重复趋势 + 影子清单强化建议 | `high` | 低 |
| `shadow_verifier.py` | 影子清单消费验证回环——新重复 vs 影子清单 → "为什么已有声明但 AI 没用？"→ 优化建议 | `supervised` | 中 |
| `extraction_safety.py` | 安全提取评估——Suitability Score 计算 + 不安全模式目录校验 + 提取影响预分析 | `supervised` | 中 |
| `stale_shared_detector.py` | 过期共享函数检测——签名漂移监控 + 调用参数匹配 + 过期标记 | `supervised` | 低 |
| `debt_projector.py` | 去重债务预测——"以当前引入速率 N 周可还清债务" | `high` | 低 |
| `verifier.py` | 修复后验证——`pytest` + `import` 检查 + 循环依赖检测 + 部分提取行为 diff 验证 | `supervised` | 中 |
| `annotations.py` | 解析 `# @intentional-duplicate: reason` 标记 + Owner 决策模式学习（同类重复自动 suppress） | `high` | 低 |
| `config.py` | 配置管理——阈值表、路径分区、排除目录、惯用法豁免模式库、策略树 YAML 加载 | `supervised` | 低 |
| `degradation.py` | 降级运行管理——各 Stage 独立 try/except + degradation_level 记录 + 降级日志 | `supervised` | 低 |
| `symbol_index.py` | 轻量符号索引——SQLite 存储函数签名 + 调用关系 + import 图（Wave 2） | `supervised` | 中 |
| `shared_lifecycle_manager.py` | 共享函数生命周期管理——5阶段状态机（Active→Deprecated→Grace→Sunset→Retired）+ 迁移diff生成 | `supervised` | 中 |
| `import_surface_tracker.py` | Import表面积负债——SBS (Shared Burden Score) 计算 + 跨层依赖热图 + shared分拆建议 | `high` | 低 |
| `doom_loop_guard.py` | Doom Loop 防护——修复升级阶梯（L0-L4）执行 + 冻结列表维护 + 失败分析报告生成 | `restricted`（涉及停止自动修复） | 中 |
| `behavioral_sampler.py` | Stage 0.25——类型推断采样输入生成 + 沙箱子进程执行 + 输出diff比对 + 副作用检测 | `supervised` | 中 |
| `self_scanner.py` | 引擎自保护——对自身源码去重 + Codegen fix manifest 维护 + 依赖版本自检 | `high` | 低 |
| `monoculture_guard.py` | Monoculture免疫——BRS计算 + 去重悖论检测（去重收益 vs 爆炸半径——找到最优边界）+ 停止高风险去重 | `restricted`（涉及停止自动修复） | 中 |
| `atomic_fixer.py` | 原子性修复引擎——WAL式（PREFLIGHT→CHECKPOINT→APPLY→RECOVER）+ 崩溃自动恢复 + fix_plan生命周期管理 | `restricted`（涉及代码库状态） | 高 |
| `grandfather_manager.py` | Grandfather三定律——古老重复识别（≥30天必有+≥60天化石）+ 考古测试 + 祖父豁免管理 | `supervised` | 中 |
| `false_negative_auditor.py` | 漏报盲审——Sensitivity Sweep执行 + Canary维护/验证 + 抽样审查工作流 + FNR趋势报告 | `high` | 中 |
| `shadow_trust_validator.py` | 影子清单信任链——import存活校验 + 幻觉函数自动清除 + spot-check + Trust Score | `restricted`（涉及AI session上下文完整性） | 低 |
| `temporal_drift_tracker.py` | 签名时态漂移追踪——指纹演化记录 + UNSTABLE标记 + 自动重算触发 | `high` | 低 |
| `simplicity_auditor.py` | 引擎成本效益自审计——SAS 0-100 计算 + 净收益评估 + 轻量/退役建议——Wave 2（**核心决策能力——引擎的自我审视**） | `high` | 低 |
| `dead_module_detector.py` | 死共享模块检测——ZOMBIE_CANDIDATE/DEAD/GRAVEYARD 判定 + 删除建议 TaskCard——Wave 2 | `high` | 低 |
| `observation_window_guard.py` | 提取后稳定观察期——OBSERVING/EXTENDED/ROLLBACK 状态机 + 回归监听——Wave 2（**对标 Microsoft SDP**） | `restricted`（涉及暂停自动修复） | 中 |
| `recovery_manifest_writer.py` | 恢复失败的恢复——R2纯文本Recovery Manifest生成 + tar.gz备份同步——Wave 2 | `supervised` | 低 |
| `thematic_clusterer.py` | 噪声信号比·主题聚类——三层加权聚类 + Executive Summary生成——Wave 2 | `high` | 中 |
| `behavioral_trust_checker.py` | 影子清单行为正确性验证——behavior_signature录制+漂移检测+告警——Wave 2（**将信任链从存在性提升到正确性**） | `restricted`（涉及函数行为的权威判断） | 中 |
| `pre_apply_integrity_gate.py` | 并发修改检测——Pre-Apply SHA256全量验证 + 冲突报告 + fix_plan自动重生成——Wave 2 | `restricted`（涉及修复执行的安全门禁） | 低 |
| `micro_clone_detector.py` | 微型克隆检测——n-gram频率计数 L0/L1/L2三级 + 高频模式聚合 + 提取建议——Wave 1（**折叠进scanner但逻辑独立**） | `high` | 低 |
| `auto_test_generator.py` | 提取后自动测试生成——类型驱动边界测试+执行轨迹金丝雀+调用方契约——pytest parametrize——对标Google Mozart——Wave 2 | `supervised` | 中 |
| `contract_consistency_checker.py` | API契约一致性验证——docstring参数+类型精确度+影子清单时效+异常契约四层——三维信任模型——对标Google Tricorder/Meta Pyre——Wave 2 | `high` | 低 |
| `cross_boundary_detector.py` | 跨边界克隆感知——SRC_TEST_BRIDGE/SRC_SCRIPTS_DIVERGENCE/CROSS_LAYER_REDUNDANCY/VENDORED 四边界——对标Google Blaze——Wave 2 | `high` | 中 |
| `decision_auditor.py` | 去重决策审计链——DecisionFingerprint 不可变追加日志 + 证据包 + 回滚计划 + CLI查询——Wave 2（最轻量的关键基础设施——≈0复杂度） | `restricted` | 极低 |
| `function_discovery.py` | 共享函数主动发现——签名驱动(Channel A) + 语义驱动(Channel B)——主动通知AI已有实现——<150行——Wave 2 | `high` | 低 |

---

## §5 退出码约定（对齐 MOD-INF-005 脚本系统）

本引擎的所有 CLI 入口 MUST 遵循 MOD-INF-005 §6 定义的五档退出码：

| 退出码 | 含义 | 触发条件 | Gate Engine 判定 |
|:---:|------|---------|:---:|
| **0** | ✅ PASS — 无重复 | 扫描范围内零重复组 | GATE-DEDUP PASS |
| **1** | ⚠️ WARN — 发现低/中严重度重复 | 所有重复组 severity ≤ medium | GATE-DEDUP WARN（不阻断）|
| **2** | ❌ ERROR — 发现高/严重重复 | 任意重复组 severity = high or critical | GATE-DEDUP FAIL（阻断 commit）|
| **3** | 🔧 TOOL-ERROR — 扫描器自身故障 | AST 解析失败 / cache 损坏且自愈失败 / git 不可用 | GATE-DEDUP SKIP（跳过门禁，记录审计）|
| **4** | ⚡ DEGRADED — 降级运行完成 | 某个 Stage 失败但降级到更低 Stage 完成了扫描（如 AST→Token） | GATE-DEDUP PASS with DEGRADED（通过但不阻断，产出完整报告 + degradation_level）|

### 5.1 severity 判定规则

| severity | 条件（满足任一） |
|---------|---------------|
| **critical** | `similarity ≥ 0.95` AND `affected_files ≥ 3` AND `category = accidental` |
| **high** | `similarity ≥ 0.85` AND `affected_files ≥ 2` |
| **medium** | `similarity ≥ 0.70` OR `category = needs_review` |
| **low** | `similarity < 0.70` OR `category = intentional` |

---

## §6 实施路线（三波递进 — v0.4.0 调整：核心阻断/交接/监控能力全部前移至 Wave 1）

### Wave 1：开工前补齐 — 决定引擎能否活下去（experimental，6 天）

| # | 任务 | 交付物 | 为什么是 Wave 1 |
|:---:|------|-------|---------------|
| W1-1 | `cache_manager.py` + `function_cache.json` 格式落地 | 缓存读写 + 增量更新 + `_integrity` 自检 + 原子写入（`.tmp` → `os.replace`）+ 自愈重建 | 没有缓存 = 每次全量扫描 = CI 不可用 |
| W1-2 | `diff_detector.py` 增量扫描入口 | git diff → 变更 Python 文件 → 提取变更函数（函数粒度——对标 Meta Glean） | Pre-commit 只能增量，不能全量 |
| W1-3 | `signature_matcher.py` Stage 0.5 签名碰撞检测 | SHA256[:12] O(1)精确匹配 → Collision/Near-Collision 判定 | Vibe Coding 性价比最高——零依赖，缓存中已有数据 |
| W1-4 | `scanner.py` Token 级扫描 + 路径感知阈值 + 代码块级滑动窗口 | 分区阈值 + MinHash + LSH + 代码块去重（min_block_size=5） | 函数 + 代码块双粒度覆盖 |
| W1-5 | `degradation.py` 降级运行管理 | 各 Stage 独立 try/except + degradation_level 记录 | 保证单模块故障不拖垮整个引擎 |
| W1-6 | `config.py` + Python 惯用法豁免模式 | `IDIOM_WHITELIST`：`__init__`/`__repr__`/`@property`/`@overload`/ABC 骨架 | 减少误报 = Owner 不会关掉引擎 |
| W1-7 | `report.py` 退出码标准化 + Health Score 初版 | exit code 0/1/2/3/4 + Dedup Health Score 0-100 + trend ↑↓→ | 退出码不标准化 = Gate Engine 无法接入；Health Score = Owner 30 秒看懂 |
| W1-8 | `prioritizer.py` 排序算法（含 ROI 因子） | `priority_score × roi_factor` | 扫描出 50 组重复时，先修 ROI 最高的 |
| W1-9 | `annotations.py` 标记解析 + Owner 决策模式学习 | `@intentional-duplicate` + 同类模式自动 suppress | 合理重复被误杀 = 开发者关掉 hook |
| W1-10 | `health_monitor.py` 健康仪表盘 + Session Log 写入 | Health Score 计算 + 去重摘要写入 Session Log | **v0.4.0 前移**——没有跨 session 交接 = 每个 AI session 从零发现 |
| W1-11 | `detect_code_duplicates.py` CLI 入口 | `--warn-only` / `--fail-on-duplicates` / `--incremental` / `--file` | 可用的 CLI + 单文件快速检查 |
| W1-12 | **GATE-DEDUP pre-commit 门禁落地** | `.pre-commit-config.yaml` 中加 `detect_code_duplicates.py --incremental` | **v0.4.0 前移**——Wave 1-2 没有阻断能力 = 引擎形同虚设 |
| W1-13 | 单元测试 ≥25 条 | `test_code_dedup_engine.py` + `test_signature_matcher.py` + `test_degradation.py` | 施工铁律 §4：源码-测试同步 |

**Wave 1 验收标准**：
- `detect_code_duplicates.py --incremental` 增量扫描 < 3 秒
- 已知 5 组重复（`_now_iso` / `_default_now` / `REPO_ROOT` / `_estimate_tokens` / import）全部可检出
- **GATE-DEDUP 发现 high/critical 重复 → 阻断 commit（exit code 2）**
- **Session Log 含去重摘要 + Health Score——下一个 AI session 零推理消费**
- Stage 0.5 签名碰撞检测对 `()->str` 签名重复正确标记
- Stage 0.25 行为采样对纯函数重复正确验证（行为一致 → 提升置信度；不一致 → 降级）
- `@intentional-duplicate` 标记的函数不被报告
- Python 惯用法（`__init__`/`@property` 等）不产生误报
- 设计模式（Strategy/Adapter/Factory/Template Method）不产生误报
- 缓存损坏 → 自动自愈重建 → exit code 0/1 正常（而非 exit 3）
- 引擎自扫描可运行——自身源码去重检测不崩溃
- Codegen fix manifest 初始化完成——所有层 __init__.py 进入监控
- `--quick-init` 模式 5s 内完成首轮扫描（仅签名匹配）

### Wave 2：beta 阶段 — 引擎从"能用"变"好用"（beta，9 天）

| # | 任务 | 交付物 | 依赖 |
|:---:|------|-------|------|
| W2-1 | `ast_comparator.py` 完整实现 | AST 子树哈希 + docstring/装饰器剥离 + 部分重复 LCS + 重排序容忍 | Wave 1 |
| W2-2 | `symbol_index.py` 轻量符号索引 | SQLite——函数签名+调用计数+import 图（对标 Google Kythe 但轻量 100 倍） | Wave 1 |
| W2-3 | `hotspot_tracker.py` AI 健忘热点 | 函数名前缀聚类 + 重复趋势 + 影子清单强化建议（"time_utils 类别 AI 总忘，请强化清单"） | Wave 1 |
| W2-4 | `shadow_verifier.py` 消费验证回环 | 新重复 vs 影子清单 → "已声明但 AI 还是重复→需优化清单格式/长度" | MOD-INF-008 + Wave 1 |
| W2-5 | `auto_fixer.py` 自动修复引擎 | 提取→替换→分批执行→失败回滚 + ROI 评估排序（优先修复 ROI 最高的组）+ **`--partial-extract` 模式**——只提取 LCS 公共核心 | Wave 1 + W2-1 |
| W2-6 | `extraction_safety.py` 安全提取评估 | Suitability Score 计算 + 不安全模式目录校验 + 提取影响预分析——**防止盲提取** | Wave 1 + W2-1 |
| W2-7 | `stale_shared_detector.py` 过期共享函数检测 | 签名漂移监控 + 调用参数匹配 + 过期标记——以防 shared 函数逐渐失配 | Wave 1 + W2-5 |
| W2-8 | `debt_projector.py` 去重债务预测 | "以当前引入 3 组/周 + 修复 2 组/周 → 12 周后重复率翻倍"；`--projection` CLI；债务还本付息计划 | Wave 1 |
| W2-9 | `verifier.py` 去重后验证 | pytest 全量 + import 可解析 + 无循环依赖 + Symbol Index 交叉验证 + **部分提取行为 diff 验证** | W2-2 + W2-5 + W2-6 |
| W2-10 | `fix_code_duplicates.py` CLI | `--fix` / `--dry-run` / `--batch-size` / `--auto-confirm` / `--partial-extract` / `--projection` | W2-5 + W2-9 |
| W2-11 | 非函数结构去重 + 代码块级深度检测 | 常量/import/类/枚举/类型别名 + 异常模板/配置读取块 | Wave 1 |
| W2-12 | 参数化模板识别 | 同名前缀聚类 + 结构相似度 > 0.7 → validate_* 模板建议 | W2-1 |
| W2-13 | 生成时预防 MVP | Context Engine 注入共享 API 影子清单（≤20 条函数签名）+ 渐进式三层记忆（热/领域/冷） | MOD-INF-008 |
| W2-14 | `ssot_registrar.py` | 修复后自动更新 `b_shared.yaml` + AGENTS.md 共享清单 + **KB 持久化（MOD-INF-012）** | W2-5 |
| W2-15 | `doom_loop_guard.py` Doom Loop 防护 | 修复升级阶梯（L0-L4）状态机 + 冻结列表维护 + 失败分析报告 + 3次尝试→停止→Owner告警 | W2-5 + W2-9 |
| W2-16 | `shared_lifecycle_manager.py` 生命周期 | 5阶段状态机（Active→Deprecated→Grace→Sunset→Retired）+ 迁移diff生成 + 影子清单同步降级 | W2-7 |
| W2-17 | `import_surface_tracker.py` Import负债 | SBS (Shared Burden Score) 计算 + 跨层依赖热图 + shared分拆建议 + 提取门槛联动 | Wave 1 + W2-6 |
| W2-18 | `monoculture_guard.py` Monoculture免疫 | BRS (Blast Radius Score) 计算 + 去重悖论检测（去重收益 vs 爆炸半径风险）+ 停止高风险去重（BRS ≥ 76） | W2-9 + W2-17 |
| W2-19 | `atomic_fixer.py` 原子性修复 | WAL 式 PREFLIGHT→CHECKPOINT→APPLY→RECOVER + 崩溃自动恢复 + fix_plan 完整性校验 | W2-9 + W2-11 |
| W2-20 | `grandfather_manager.py` 古老重复管理 | Grandfather 三定律实现——≥30 天永不自动修复 + ≥60 天化石化 + 第三定律考古测试 | Wave 1 + W2-7 |
| W2-21 | `false_negative_auditor.py` 漏报盲审 | Sensitivity Sweep（降低阈值+diff）+ Canary 注入/验证（5-10 组·FNR可量化）+ 抽样审查工作流 | Wave 1 + W2-10 |
| W2-22 | `shadow_trust_validator.py` 影子信任链 | import 存活校验 + 幻觉自动清除 + spot-check + Trust Score | Wave 1 + W2-8 |
| W2-23 | `temporal_drift_tracker.py` 签名时态漂移 | 指纹演化记录 + 连续3次不同→UNSTABLE→Stage 0.5 skip + unstable_ratio 全局监控 | Wave 1 + W2-7 |
| W2-24 | `simplicity_auditor.py` 引擎自审计 | SAS 计算 + 月度净收益评估 + NET_NEGATIVE 退役建议 + Session Log 成本报告——Wave 2 | Wave 1 + W2-18 |
| W2-25 | `dead_module_detector.py` 死模块检测 | ZOMBIE_CANDIDATE/DEAD/GRAVEYARD 判定 + TaskCard DEAD-MODULE 生成——Wave 2 | Wave 2 + W2-16 |
| W2-26 | `observation_window_guard.py` 观察期 | 提取后14天观察窗口 + OBSERVING→resume/ROLLBACK + 回归监听——Wave 2（**对标 Microsoft SDP/Netflix Staged Rollout**） | W2-19 + W2-9 |
| W2-27 | `recovery_manifest_writer.py` 恢复安全网 | R2纯文本Recovery Manifest生成 + tar.gz同步 + 递归恢复四层（R0-R3）——Wave 2 | W2-19 |
| W2-28 | `thematic_clusterer.py` 主题聚类 | 三层加权聚类（前缀30%+AST50%+共现20%）+ 50组→3主题压缩 + Executive Summary——Wave 2 | Wave 1 + W2-4 |
| W2-29 | `behavioral_trust_checker.py` 行为信任 | behavior_signature录制+全量扫描采样验证+行为漂移 DIVERGED 告警+根因分析——Wave 2 | W2-22 + W1-12 |
| W2-30 | `pre_apply_integrity_gate.py` 并发防护 | Pre-Apply全量SHA256验证 + ABORT冲突报告 + fix_plan自动重生成 + 文件锁——Wave 2 | W2-19 |
| W2-31 | `micro_clone_detector.py` 微克隆检测 | n-gram频率计数L0/L1/L2三级 + 高频1-2行模式聚合 + micro_clone_report.yaml——Wave 2（Wave 1预埋scanner基础能力） | Wave 1 |
| W2-32 | `auto_test_generator.py` 测试生成 | 类型驱动边界测试+执行轨迹金丝雀录制+调用方契约测试——pytest parametrize——BRS缓解——对标Google Mozart——Wave 2 | W2-19 + W2-18 |
| W2-33 | `contract_consistency_checker.py` 契约验证 | docstring参数+类型精确度+影子清单时效+异常契约四层——三维信任模型——对标Google Tricorder/Meta Pyre——Wave 2 | W2-22 + W2-29 |
| W2-34 | `cross_boundary_detector.py` 跨边界感知 | 四大边界差异化检测+独立策略——对标Google Blaze/JetBrains IntelliJ——Wave 2 | Wave 1 + W2-6 |
| W2-35 | `decision_auditor.py` 决策审计链 | DecisionFingerprint不可变追加日志 + 证据包 + 可回滚 + CLI查询——≈0复杂度——Wave 2 | W2-19 + W2-22 |
| W2-36 | `function_discovery.py` 主动发现 | 签名驱动(Channel A) + TF-IDF语义驱动(Channel B) + function_discovery.yaml——<150行——Wave 2 | W2-22 + W2-28 |

**Wave 2 验收标准**：
- `fix_code_duplicates.py --fix --batch-size 3` 自动修复 2+ 高置信度组
- **Suitability Score < 40 的重复组绝对不被自动修复**
- 修复后全量测试零失败
- 去重后验证检测到循环依赖 → 自动终止修复
- 过期共享函数被标记并报告（stale_shared_count > 0 时 Health Score 降低）
- 去重债务预测可产出——`--projection` 输出 N 周还本付息计划
- 共享 API 影子清单在 AI session 开始时自动注入（Context Engine 验证）
- 参数化模板识别 `validate_email` / `validate_phone` / `validate_url` 为同一模式
- 影子清单消费验证回环可运行：新重复 → 比对影子 → "%Y-%m-%d 发现 X 函数影子清单已声明但 AI 仍重复生成——需优化"
- KB 持久化验证——去重洞察可被 KB 查询 `dedup:hotspots:time_utils`
- 部分提取模式：LCS 公共核心提取到 shared + 差异化代码保留各调用方
- Doom Loop 防护可用——同一 DUP group 3 次修复失败 → L4 冻结 + Session Log 告警
- 共享函数生命周期状态机正常运转——Deprecated 函数从影子清单移除（降级为冷规则）
- SBS 计算正确——shared import 总数 + 跨层依赖比 + max dependents per func 三项全部纳入
- SBS ≥ 31 → 新提取 Suitability 门槛自动提升至 ≥ 70
- Monoculture免疫可用——BRS 计算正确 + BRS ≥ 76 → 自动停止去重 + 生成原因报告
- 原子性修复可用——中断修复后引擎自动恢复代码库到修复前状态
- Grandfather 三定律生效——≥30 天重复的 `auto_fix = false` + ≥60 天化石化不参与 Health Score 减值
- Canary 报告可用——FNR 量化 + 趋势 + canary_miss 触发告警
- 影子清单 Trust Score 可用——幻觉自动清除 + Trust Score < 90% 时拒绝注入
- 引擎自审计（Simplicity Audit）可用——SAS 月度计算 + SAS < 50 触发 Session Log 警告
- 死共享模块检测可用——DEAD 模块被标记 + TaskCard DEAD-MODULE 生成
- 稳定观察期可用——提取后自动进入14天 OBSERVING 模式 + 健康监控不下降
- 恢复安全网可用——R2 Recovery Manifest 与 checkpoint 同步生成 + base64内容可恢复
- 主题聚类可用——50组→3主题压缩 + Executive Summary 一行可读
- 行为正确性验证可用——behavior_signature 录制 + 全量扫描后采样验证 + 漂移告警
- Pre-Apply Integrity Gate 可用——修复 APPLY 前文件完整性验证 + 冲突 ABORT
- **微克隆检测可用**——n-gram频率计数正常 + micro_clone_report.yaml 产出 + 微克隆维度纳入 Health Score
- **自动测试生成可用**——提取后自动生成 3 类测试 + BRS 缓解效果可量化 + 生成的测试被引擎跳过去重
- **契约一致性验证可用**——四层校验+三维 Trust Score 聚合 + 契约腐烂自动修复
- **跨边界检测可用**——四大边界全部可检测 + 跨边界 auto_fix 保守策略生效
- **决策审计链可用**——不可变追加日志 + 决策指纹 + CLI `audit --since`/`audit --rollback` + 决策摘要注入 Session Log
- **主动发现可用**——签名+语义双通道索引 + `function_discovery.yaml` 产出 + 集成 Context Engine 主动推送

### Wave 3：stable 阶段 — 形成进化闭环 + 策略树落地（stable，6 天）

| # | 任务 | 交付物 | 依赖 |
|:---:|------|-------|------|
| W3-1 | `semantic_verifier.py` LLM 语义验证 | 置信度评分 0-100 + 修复方案生成（仅用于 0.70-0.85 不确定区间） | Wave 2 |
| W3-2 | Feedback Loop 深度集成 | 重复模式→FLE→`dedup_pattern_report` | MOD-INF-010 + Wave 2 |
| W3-3 | evolve() 进化信号 | 重复模式→EvolutionProposal（signal_type=LOW_KNOWLEDGE_HIT） | ADR-0034 + W3-2 |
| W3-4 | 频率/反模式追踪 | ChromaDB 记录：哪些重复反复出现；同一模式 3 次重现 → evolve() | MOD-INF-011 |
| W3-5 | **策略树 YAML 正式落地** | `config/policy_tree.yaml`：条件树替代硬编码阈值——Owner/AI 可改 YAML 调整去重行为 | Wave 2 |
| W3-6 | GATE-DEDUP 正式版 + Gate Engine 深度契约 | Gate Engine CT-SCRIPT-GATE-001 完整契约 + 双向验证 | MOD-INF-007 + Wave 1 |
| W3-7 | CI 集成 | `.github/workflows/governance.yml` 中新增 dedup step（全量扫描 + 趋势） | Wave 2 |
| W3-8 | Self-Benchmark（引擎自验证） | 5 组已知重复/非重复对 → 全量扫描后自动验证 → 引擎退化告警 | Wave 2 |
| W3-9 | 渐进式三层记忆注入落地 | 热规则 ≤400 tokens 始终注入 / 领域规则关键词触发 / 冷规则按需——对齐 AGENTS.md §8 | MOD-INF-008 + Wave 2 |
| W3-10 | 可视化/趋势面板（可选） | 重复趋势曲线 + TOP5 最多重复模块 + AI 健忘热点图 | W3-4 |

**Wave 3 验收标准**：
- Feedback Loop 正确消费 `dedup_pattern_report`
- 同一重复模式被删除 3 次后又出现 → evolve() 产出 EvolutionProposal
- Self-Benchmark 每全量扫描后验证 5 组已知对——退化 → 告警
- 策略树 YAML 配置可被 AI 直接修改调整去重行为，无需改 Python
- 渐进式三层记忆注入在 Context Engine build log 中可验证

### 工作量汇总

| Wave | 内容 | 预估工作量 | 累计 |
|:---:|------|:---:|:---:|
| **Wave 1** | 缓存+增量+Stage0.5签名+Stage0.25行为采样+降级+惯用法豁免+设计模式白名单+退出码5档+项目规模感知Tier配置+Health Score+引擎自观指标+Session Log+GATE阻断落地+模式学习+引擎自保护+Codegen覆盖防护+冷启动加速(`--quick-init`)+CLI+测试 | 8 天 | 8 天 |
| **Wave 2** | AST比对+符号索引+健忘热点+影子验证+安全提取评估+过期共享检测+Doom Loop防护+生命周期管理+Import负债追踪(SBS)+Monoculture免疫(BRS)+原子性修复(WAL)+Grandfather三定律+漏报盲审(Sweep+Canary+抽样)+影子信任链+时态漂移+债务预测+自动修复(含部分提取)+非函数去重+模板识别+生成预防+SSoT注册+KB持久化+引擎自审计+死模块检测+观察期+恢复安全网+主题聚类+行为信任+并发防护+微克隆检测+测试生成+契约验证+跨边界感知+**决策审计链+主动发现** | 25 天 | 35 天 |
| **Wave 3** | LLM验证+FLE集成+evolve+反模式追踪+策略树落地+Gate深度+CI+Self-Benchmark+三层记忆+退役路径文档化+跨AI工具适配+中文函数语义测试+可视化 | 7 天 | 42 天 |

---

## §7 与现有系统的深度集成

### 7.1 集成全景图

```
                          ┌──────────────────────────────┐
                          │     MOD-INF-017               │
                          │     代码去重引擎               │
                          └──────┬───────────┬───────────┘
                                 │           │
        ┌────────────────────────┼───────────┼────────────────────────┐
        │                        │           │                        │
   ┌────▼─────┐   ┌─────────┐  ┌▼────────┐ ┌▼─────────┐  ┌──────────┐
   │ Context  │   │  Gate   │  │ Shared+ │ │ Feedback │  │  Task    │
   │ Engine   │   │ Engine  │  │  Core   │ │  Loop    │  │ System   │
   │MOD-INF008│   │MOD-INF007│ │MOD-INF016│ │MOD-INF010│  │MOD-INF006│
   └──────────┘   └─────────┘  └─────────┘ └──────────┘  └──────────┘
   ①生成时预防     ②提交时拦截   ⑤SSoT注册    ⑥进化沉淀      TaskCard
```

### 7.2 各系统集成契约

| 集成目标 | 集成方式 | 数据流向 | 契约文件 | 验证方法 |
|---------|---------|---------|---------|---------|
| **Context Engine** (MOD-INF-008) | 每次 AI session 开始时，去重引擎提供"共享API影子清单"（≤20条函数签名+描述），Context Engine 注入到 system prompt | Dedup → CE | `shadow_api_manifest.yaml` | CE build log 中包含影子清单 |
| **Gate Engine** (MOD-INF-007) | Pre-commit GATE-DEDUP：`detect_code_duplicates.py --incremental` exit code → Gate 判定 | Script exit code → Gate PASS/FAIL/BLOCKED | CT-SCRIPT-GATE-001 | Gate 判定日志中 GATE-DEDUP 出现 |
| **Shared+Core** (MOD-INF-016) | 去重后自动修复提取的函数，通过 SSoT Guard 注册到 `b_shared.yaml` | Fixer → SSoT Guard → b_shared.yaml | `b_shared.yaml` | 提取的函数在 YAML SSoT 中可检索 |
| **Feedback Loop** (MOD-INF-010) | 重复模式写入 FLE，触发 evolve() 产出 EvolutionProposal | Scanner → FLE → evolve() → Proposal | `dedup_pattern_report` | Proposal 可追溯到具体 Dedup Report |
| **Task System** (MOD-INF-006) | 每组 high/critical 重复自动生成 TaskCard（`TASK-DEDUP-NNN`），由 AI pipeline 执行修复 | Report → TaskCard → Pipeline | TaskCard `source_blueprint: MOD-INF-017` | TaskCard 状态可追踪 |
| **Session Log** | 每次去重扫描的结果摘要写入 Session Log → 下一个 AI session 入职时知晓"最近有哪些重复被发现" | Scanner → Session Log → Next Session | Session Log §dedup | Next AI session 日志中提到去重发现 |

### 7.3 共享API影子清单格式

```yaml
# shadow_api_manifest.yaml — 生成时预防的核心数据
# 由 ssot_registrar.py 自动维护，被 Context Engine 消费
# 每次 AI session 开始时，Context Engine 将此清单注入 system prompt
shadow_apis:
  - signature: "now_iso() -> str"
    module: "zephyr.shared.time_utils"
    description: "返回 ISO 8601 格式的当前UTC时间戳"
  - signature: "estimate_tokens(text: str) -> int"
    module: "zephyr.shared.token_utils"
    description: "估算文本的 token 数量"
  - signature: "get_repo_root() -> Path"
    module: "zephyr.shared.path_utils"
    description: "获取项目根目录的绝对路径"
```

### 7.4 intentional-duplicate 标记规范

```python
# 用法1：函数级标记
# @intentional-duplicate: 这是API版本兼容层，v1和v2必须独立维护
def process_v1(data: dict) -> Result:
    ...

# 用法2：文件级标记
# @file-intentional-duplicate: tests/fixtures/ 下的fixture有合理重复

# 用法3：区块级标记
# @block-intentional-duplicate-start
# ... allowed duplicate block ...
# @block-intentional-duplicate-end
```

---

## §8 风险评估

| # | 风险 | 概率 | 影响 | 缓解措施 |
|:---:|------|:---:|:---:|------|
| 1 | **误报消耗 Owner 时间**（1人团队的致命风险） | 中 | **高** | ①路径感知阈值——shared低阈值/tests高阈值 ②默认偏向漏报（`--strict` 切换严格模式）③置信度评分让Owner优先看高置信度 ④`@intentional-duplicate` 标记白名单 ⑤ Python 惯用法自动豁免（`__init__`/`@property`/ABC骨架）⑥ Owner 决策模式学习——同类未来自动 suppress |
| 2 | 自动修复引入 bug（提取函数时改错调用方） | 中 | 高 | ①分批修复（每批≤3组）②每批后跑全量测试 ③修复前自动 `git stash` 备份 ④verifier.py 验证 import+测试+循环依赖+Symbol Index交叉验证 ⑤相似度<0.95不自动修复 ⑥ROI评估优先修高价值低风险组 |
| 3 | 增量扫描漏报（新重复因缓存过旧未被检测） | 中 | 中 | ①每周自动全量重建缓存 ②`--full` 标志强制全量扫描 ③缓存 `last_modified` 与实际文件 mtime 交叉验证 ④`_integrity` 字段校验缓存完整性 |
| 4 | LLM 语义判断不稳定 | 高 | 低 | LLM 是 Stage 3 可选——Stage 0.5-2 已完成 95% 检测。LLM 仅用于 0.70-0.85 的不确定区间 |
| 5 | 扫描速度随函数增长而退化 | 低 | 中 | MinHash LSH 是 O(n) 近似算法；增量模式下只扫描变更函数（通常 < 10 个）；缓存免除重复 AST 解析 |
| 6 | 与现有 D-D-07 checker 功能重叠 | 低 | 低 | D-D-07 是词法级精确匹配（Type-1），本引擎是语义级（Type-1~4），互补 |
| 7 | **`--fix` 模式下改动范围过大**（一次性修改 50+ 文件） | 低 | **高** | ①硬限制：单次 `--fix` 最多修改 3 组重复 ②超过限制 → 分批执行 + 中间跑测试 ③`--dry-run` 先预览 diff |
| 8 | 去重后循环依赖（A 提取到 shared，B 也依赖 A） | 中 | 中 | `verifier.py` 集成 `importlib` 依赖分析——检测到循环依赖 → 终止修复 + 报告 |
| **9** | **Tree-sitter Python grammar 版本漂移**导致 AST Stage 2 解析失败——CI 全红 | **中** | **高** | **①`config.py` 锁定 Tree-sitter grammar 版本（pyproject.toml 中固定）②扫描前 grammar 兼容性自检（用 10 个已知 Python 语法特征验证）③Stage 2 解析失败 → 降级到 Stage 0.5+1，exit code 4（DEGRADED），CI 不阻断 ④版本升级自动化——pyproject.toml grammar 版本与 CI Python 版本绑定** |
| **10** | **function_cache.json 损坏**——磁盘满/进程崩溃/并发写入导致 JSON 不完整 | **中** | **高** | **①`_integrity` 字段：SHA256(内容) 加载时校验 ②不一致 → 自动 full rebuild → Session Log 记录 ③原子写入：先写 `.tmp` → `os.replace(.tmp, cache.json)`（Windows 上 `os.replace` 是原子的）④损坏的旧缓存移动至 `.cache.json.corrupted` 供事后分析** |
| **11** | **Kill Switch 告警风暴**——正当代码批量操作触发 `config_file_blitz` 等自动阻断 | **低** | **高** | **①预声明机制：在 commit message 或临时配置文件声明"本次为合法批量操作"②自动阻断触发后保留 Owner 手动 bypass 通道（exit code 3 + 审计日志）③降级模式下 Allow Kills harsher 自动关闭——避免普通操作因 Kill Switch 全阻断** |
| **12** | **Vibe Coding "创造性漂移"**——AI 重新发明功能而非复制代码，相似度 0.3-0.5 但功能完全相同 | **高** | **中** | **①Stage 0.5 签名指纹匹配——签名相同 = 功能可能相同 ②AI 健忘热点追踪——"time_utils 类别本月已重复 4 次" ③影子清单消费验证回环——持续优化清单格式确保 AI 真读了** |
| **13** | **引擎自身维护成本被低估**——14+ 模块 + 多依赖 = 每个 Python/Tree-sitter/MinHash 升级都可能成为 breakage | **中** | **高** | **①模块维护复杂度分级（低/中/高）在 §4.1 中标注——AI session 进入时优先评估高风险模块 ②降级运行保障单模块故障不拖垮整体 ③Self-Benchmark（Wave 3）——每次全量扫描后用 5 组已知对验证引擎未退化** |
| **14** | **盲提取创建更重技术债**——行业实践证明"提取到共享库可能比保留重复更糟糕" | **中** | **高** | **①§3.6 安全提取适配性评估（Suitability Score）——< 40 分 → 绝不提取 ②§3.6 不安全提取模式目录——7 类模式 NEVER auto-extract ③部分共享提取——只提取公共核心(60%)+保留差异化部分 ④提取影响预分析——变更文件数×调用方测试覆盖率** |
| **15** | **"5000 行魔咒"**——项目增长超过临界点后 AI 系统性遗忘已有功能，代码克隆率指数级上升 | **高** | **高** | **①§3.7 项目规模感知四 Tier 自适应阈值——Tier 1 偏漏报 / Tier 4 激进拦截 ②重复引入速率追踪——新重复/周 指标暴露 Prevent 阶段是否失效 ③影子清单随规模增同步扩容——Tier 1 ≤20 条 / Tier 4 ≤100 条** |
| **16** | **过期共享函数**——提取到 shared 后各调用方持续定制，共享版本逐渐过时不匹配 | **中** | **中** | **①`stale_shared_detector.py`（Wave 2）——定期比对 shared 函数签名/调用参数 vs 各调用方实际使用 ②签名漂移告警——shared 函数新增参数但 40% 调用方未使用 → 标记"可能不需要此参数" ③Engine Health Report 中含 stale_shared_count** |
| **17** | **部分重复被全量处理**——检测到60%部分重复，但 auto-fix 无"只提取公共核心+保留差异"的能力 | **中** | **中** | **①§3.6 partial_extraction_plan——LCS 识别的公共核心 → shared，差异部分 → 各调用方保留 ②Wave 2 auto_fixer.py 支持 `--partial-extract` 模式 ③分阶段施工——先提取无争议核心 → 跑测试 → 再处理差异** |
| **18** | **情报丢失**——引擎发现的重复模式/健忘热点仅存于报告中，下一个 AI session 需要重新发现 | **中** | **中** | **①`depends_on` MOD-INF-012（Knowledge Base）——引擎发现 → KB 持久化 ②AI session 开始 → 影子清单外也检查 KB 中的去重洞察 ③`health_monitor.py` 在 Session Log 中同时写入 KB ID——"详见 KB://dedup/hotspots/2026-05"** |
| **19** | **去重债务不可预测**——不知道以当前速率何时会失控 | **低** | **中** | **①`debt_projector.py`（Wave 2）："以当前引入 3 组/周 + 修复 2 组/周 → 12 周后重复率翻倍" ②`--projection` CLI 标志——输出 4/8/12 周债务预测 ③Health Score 中的 `debt_paydown_eta` 字段——"预计 N 周可还清当前去重债务"** |
| **20** | **引擎自腐**——引擎本身是 Vibe Coding AI 生成的，内部可能有重复函数、硬编码、脆弱的 AST 处理 | **中** | **高** | **①§3.8 引擎自扫描（L1）——每次全量扫描后自我去重检测 ②不做自我修复（引擎改引擎 = 递归不可控）③引擎代码变更后自动触发 self-scan diff ④设计模式白名单防止引擎自身的 Strategy/Factory 被误报** |
| **21** | **Codegen覆盖修复**——codegen 重生成 `__init__.py` 时覆盖手动修复的共享导入和公共符号导出 | **高** | **高** | **①§3.8 L2 Codegen覆盖防护——SHA256 哈希白名单 + 自动检测覆盖 ②检测到覆盖 → Session Log 写入 + 生成修复 diff ③`.codegen-protect` 注释标记在文件头——codegen 识别后跳过生成 ④所有层 `__init__.py` 进入 `codegen_fix_manifest.json` 监控清单** |
| **22** | **Doom Loop 触发**——auto_fixer 修复A→B break→修复B→C break...→3次后仍失败→浪费大量 AI session 时间 | **中** | **高** | **①§3.9 修复升级阶梯（L0-L4）——3次尝试失败 → 冻结该 DUP group ②`doom_loop_freeze_list.json` 冻结机制——需 Owner 手动解除 ③24h 内同 DUP group 不重复尝试 ④行为采样验证（Stage 0.25）作为 L0 防线——先确认行为一致再提取** |
| **23** | **Shared 生命周期失控**——提取的函数越来越多但没有退役机制——shared 目录膨胀成"僵尸函数坟场" | **中** | **中** | **①§3.10 5阶段生命周期（Active→Deprecated→Grace→Sunset→Retired）②Deprecated 进入"冷规则"——新 AI session 不推荐 ③Sunset 阻断 pre-commit 引用 ④KB 保留退役记录——防止未来重新发明** |
| **24** | **Import表面积黑洞**——去重后 shared/ 成为全项目导入热点，耦合度超过去重前的分散重复 | **中** | **高** | **①§3.11 Shared Burden Score（0-100）实时追踪 ②SBS ≥ 31 → 提高提取门槛（Suitability≥70）③SBS ≥ 76 → 停止自动提取 + 建议分拆 shared/ ④Cross-layer 依赖热图——定位"耦合炸弹"** |
| **25** | **低测试覆盖下的验证失败**——Vibe Coding 项目测试覆盖率 < 20%——verifier.py 的 pytest 防线形同虚设 | **高** | **高** | **①Stage 0.25 行为采样验证——不依赖测试框架 ②对纯函数自动采样输入→沙箱执行→输出 diff ③有副作用函数跳过→标记 needs_review ④行为采样 pass→提升置信度；divergence→降低置信度** |
| **26** | **引擎冷启动 HIIT**——首次运行无缓存、无符号索引、无历史——全量 AST 解析 500+ 函数 → 耗时 > 60s → AI session 等待过长 | **中** | **中** | **①首次运行时输出进度条 + 预估时间（"首次扫描预计 45s，后续增量扫描 < 3s"）②首次运行可手动指定 `--quick-init`——仅做签名指纹扫描（Stage 0.5）+ 跳过 Stage 1-2 → 5s 完成 ③首次运行后的缓存写入 `< 2s`——后续扫描即享增量加速** |
| **27** | **Monoculture 灾难**——去重成功后一个 shared 函数 bug 影响 N 个 caller——比原来分散的重复更危险（爆炸半径悖论） | **高** | **高** | **①§3.12 Monoculture免疫——BRS (Blast Radius Score) 0-100 ②BRS ≥ 51 → 强烈建议增加独立单元测试 ③BRS ≥ 76 → 停止去重——"风险优先于简洁" ④分散重复本质上是一种blast radius隔离——不是所有重复都该消除** |
| **28** | **古老重复考古风险**——引擎安装前存在的重复代码可能是被测试了 6 个月的深度纠缠——提取 = 破坏稳定架构 | **中** | **高** | **①§3.13 Grandfather三定律——≥30天的重复永不自动修复 ②≥60天 → 化石记录（降级为 informational——退出 Health Score 减值）③第三定律考古测试——无 caller 独立测试 + 无 rollback plan → 拒绝提取** |
| **29** | **修复中断导致代码库损坏**——断电/OOM/crash 后 shared 中有新函数但 caller 没更新 or 反向——代码库处于不一致状态 | **中** | **极高** | **①§3.14 原子性修复——WAL 式 PREFLIGHT→CHECKPOINT→APPLY→RECOVER ②崩溃恢复：引擎下次启动自动扫描残留 checkpoint → 恢复所有原始文件 ③fix_plan SHA256 步进验证——每一步执行后立即校验 expected_sha256** |
| **30** | **系统性漏报不可见**——系统偏向漏报但不知道自己漏掉了什么、漏掉了多少——可能积累成"静默的技术债山" | **中** | **中** | **①§3.15 三层漏报盲审——L1 Monthly Sensitivity Sweep（降低阈值+diff）②L2 Canary注入（5-10组已知重复自动验证——FNR可量化）③L3 Sampled Human Audit（每周 10 组随机审查——反馈驱动改善）** |
| **31** | **影子清单幻觉导致 ImportError**——影子清单中有一个引擎/AI幻觉的不存在的函数 → AI session 导入它 → ImportError → 整个模块加载失败 | **中** | **高** | **①§3.16 Shadow Manifest信任链——import存活校验（`python -c "from shared.xxx import func"`）②幻觉函数自动清除 ③注入前 spot-check（随机 10%）→ 失败率 > 10% → 拒绝注入——降级到"无清单模式"** |
| **32** | **Temporal Drift 使 Stage 0.5 退化**——Python 类型注解持续演化（`str`→`Optional[str]`→`float\|None`）→ 签名指纹变化 → 缓存中的旧指纹无效 → Stage 0.5 命中率持续下降 | **中** | **中** | **①§3.17 每次全量扫描自动重算签名指纹 ②drift 检测 + 记录演化历史 ③连续 3 次 fingerprint 不同 → UNSTABLE → Stage 0.5 跳过此函数——降级到 Stage 1-2 ④Owner 手动标记 STABLE 恢复** |
| **33** | **引擎成本效益倒挂**——33模块去重引擎的月度维护时间可能超过它消除的重复代码的维护时间——引擎本身成为项目最重的技术债 | **中** | **极高** | **①§3.18 引擎成本效益自审计（Simplicity Audit）——SAS 0-100每月自动计算 ②SAS < 50 持续3月 → 自动触发轻量模式（只检测不修复）③SAS < 25 → 生成退役建议——"关闭修复功能可月度节省X小时"** |
| **34** | **死共享模块积累**——shared/ 中子模块所有函数退役后文件仍存在——消耗认知负荷、lint 时间、和索引开销 | **中** | **低** | **①§3.19 死共享模块检测——全函数退役+零caller+≥90天→DEAD ②自动标记删除建议 ③Graveyard记录防止重新创建** |
| **35** | **提取后静默退化**——提取到 shared 后立即进入下一轮提取，新 shared 函数的隐藏 bug 在未观察期暴露——可能带着 bug 运行数周 | **中** | **高** | **①§3.20 提取后14天稳定观察期——暂停新提取+监控Health Score+行为采样 ②观察期内触发≥2回归→FRAGILE→回滚 ③对标 Microsoft SDP 工业最佳实践** |
| **36** | **恢复机制自身故障**——原子修复的CHECKPOINT tar.gz损坏/不完整→恢复失败——系统无备选恢复方案 | **低** | **极高** | **①§3.21 双层恢复安全网——R1 tar.gz恢复 + R2纯文本Recovery Manifest（base64原始内容）②R2不依赖任何压缩工具——纯文本可由任何编辑器打开 ③R3 git恢复作为最终回退** |
| **37** | **告警疲劳导致审查质量断崖**——全量扫描产出 50+组重复 → Owner审查第20条后准确率从85%→40%（IEEE TSE 2024） | **高** | **高** | **①§3.22 噪声信号比·主题聚类摘要——三层加权聚类（函数名前缀30%+AST结构50%+目录共现20%）→50组→3个主题 ②Executive Summary一行可读——Owner不用审查全部** |
| **38** | **影子清单行为正确性缺失**——信任链验证函数存在但函数行为可能已漂移 → AI session导入"正确import但语义错误"的函数 | **中** | **高** | **①§3.23 行为正确性验证——提取时记录 behavior_signature（5组采样输入→预期输出）②每次全量扫描重新执行验证 ③行为漂移→DIVERGED→告警+根因分析** |
| **39** | **PREFLIGHT→APPLY窗口中的并发写入**——另一个AI session在修复窗口内修改了目标文件→引擎以旧认知改新代码→损坏 | **中** | **极高** | **①§3.24 Pre-Apply Integrity Gate——APPLY第一步重算所有目标文件SHA256→与PREFLIGHT对比 ②任一不一致→ABORT+冲突报告+自动重新生成fix_plan** |
| **40** | **微克隆泛滥被忽略**——Vibe Coding AI 生成了大量 1-2 行重复模式（logger调用、时间戳格式、重试模板）但 min_block_size=5 行门槛使其不可见——累积维护成本占去重债务 22%（ICPC 2023） | **高** | **中** | **①§3.25 微型克隆三级检测——L0逐行SHA256 + L1归一化SHA256 + L2 2-3行滑动窗口 ②i频率阈值自适应——≥10/8/5文件分别触发三个等级 ③微克隆决不自修——仅检测+建议 ④微克隆纳入 Health Score 微克隆维度** |
| **41** | **提取后无测试导致 BRS 高但无法缓解**——Monoculture 免疫建议"为该 shared 函数增加测试"但没有自动化测试生成——BRS 高悬但落地受阻 | **中** | **高** | **①§3.26 提取后自动测试生成管道——类型驱动边界测试+执行轨迹金丝雀录制+调用方契约测试 ②BRS ≥ 51 → 全量生成测试 → BRS 可降 30+ 分 ③生成的测试带 @auto-generated-by-dedup 标记——引擎后续跳过不对其做去重** |
| **42** | **API契约腐烂误导AI session**——影子清单中函数的 docstring/类型注解/描述与实现不一致 → AI session 使用该函数时基于错误契约生成代码 → 逻辑错误 | **中** | **高** | **①§3.27 API契约一致性验证——四层校验（docstring参数+类型精确度+影子清单描述+异常契约）②MINOR不一致→自动修复 ③TYPE_UNDERAPPROXIMATED → 告警不注入 ④连续恶化 → 从影子清单降级为冷规则** |
| **43** | **跨边界克隆不可见**——src vs tests / src vs scripts / L01 vs L05 / src vs vendored 之间的重复完全不在当前检测范围——4种边界各自需要独立策略 | **中** | **高** | **①§3.28 跨边界克隆感知——四大边界差异化检测+独立阈值+独立auto_fix规则 ②跨边界 auto_fix 比同区域内更保守——宁可 WARN 等 Owner 决策不盲修 ③CROSS_LAYER_REDUNDANCY 是最高价值目标——可 auto_fix** |
| **44** | **决策不可追溯导致信任危机**——Owner 休假后或维护模式下回来看 shared/ 多了文件/函数被标记废弃——无法追溯"谁决定的？为什么？可以撤销吗？"——对 1人+AI 维护信任的致命打击 | **高** | **中** | **①§3.29 决策审计链——DecisionFingerprint 不可变追加日志 + 证据包 ②每个 CRITICAL/MAJOR 决策附带完整证据链 ③所有可逆决策生成回滚计划 ④CLI `audit --since`/`audit --verify`/`audit --rollback` ⑤决策摘要注入 Session Log 供 AI session 快速理解历史** |
| **45** | **AI 被动等待拦截而非主动复用**——Shadow Manifest 被动注入依赖 AI 自觉读取——AI 可能在 "写一个新函数" 的惯性下忽略已有实现——导致先犯错再被 GATE-DEDUP 拦截——无谓消耗 2-3 轮对话 | **中** | **中** | **①§3.30 主动发现双通道——签名驱动(精确)+语义驱动(模糊)——不等 AI 犯错就主动告知已有实现 ②集成 Context Engine——在 AI 准备生成函数前推送匹配结果 ③EXACT_MATCH → STOP 信号 ④NO_MATCH → 记录 new_function_candidate 用于未来发现** |

---

## §9 成功标准

### 9.1 功能验收

| # | 标准 | 验证方法 | 达标条件 |
|:---:|------|---------|---------|
| 1 | 能检测出 `_now_iso()` / `now_iso()` / `_default_now()` 三者功能相同 | 手动构造测试用例 | 三者在同一 `duplicate_group` 中，`similarity ≥ 0.85` |
| 2 | 能检测出 `REPO_ROOT` 在 7 个文件中的独立计算 | 对现有项目运行全量扫描 | 7 个成员在同一 `duplicate_group` 中 |
| 3 | 能检测出 `_estimate_tokens()` 的 3 处重复（含微差版本） | 手动构造测试用例 | `similarity ≥ 0.80`，即使空字符串处理不一致 |
| 4 | 能识别 `validate_email` / `validate_phone` / `validate_url` 为同一参数化模板 | 手动构造测试用例 | 三者被聚类到同一 `template_group` |

### 9.2 性能验收

| # | 标准 | 验证方法 | 达标条件 |
|:---:|------|---------|---------|
| 5 | 全量扫描 `src/zephyr/`（342 函数）< 30 秒 | `time detect_code_duplicates.py` | wall time < 30s |
| 6 | 增量扫描（变更 5 个函数）< 3 秒 | 手动修改 2 个文件后 pre-commit | wall time < 3s（含缓存加载） |
| 7 | `--fix --batch-size 3` 修复 + 验证 < 60 秒 | 修复 3 组已知重复 | wall time < 60s（含 `pytest -q`） |

### 9.3 质量验收

| # | 标准 | 验证方法 | 达标条件 |
|:---:|------|---------|---------|
| 8 | 精准率（报告为重复的组中，确实是重复的）> 80% | 人工确认全量扫描结果 | `true_positives / (true_positives + false_positives) > 0.80` |
| 9 | 自动修复安全率（自动修复后测试全绿 + 无循环依赖）100% | `auto_fixer.py` 修复已知重复组 | 修复后全量测试零失败 |
| 10 | idempotency——连续两次扫描产生相同 group_id 和 member 列表 | 连续运行两次全量扫描 | 两次报告的 `duplicate_groups` 完全一致 |

### 9.4 集成验收

| # | 标准 | 验证方法 | 达标条件 |
|:---:|------|---------|---------|
| 11 | Pre-commit GATE-DEDUP 发现 high/critical 重复 → 阻断 commit | 手动引入重复函数后 git commit | commit 被阻断，exit code 2 |
| 12 | `@intentional-duplicate` 标记的函数不被拦截 | 标记一个已知重复 | commit 不被阻断，exit code 0 |

---

## §10 开放问题与决策记录

| # | 问题 | 当前决策 | 未来触发重审的条件 |
|:---:|------|---------|-----------------|
| 1 | **AST 相似度阈值如何精确确定？** 0.7 / 0.85 / 0.95 是否合理？ | Wave 1 用默认阈值 + **Python惯用法豁免**已大幅减少误报；Wave 2 用实际项目 342 函数调参——ROC 曲线找到最优 F1 点 | Wave 2 后误报率 > 20% 或漏报率 > 30% → 调参 |
| 2 | **是否需要 LLM？** | Wave 1-2 不需要。Stage 0.5 签名匹配 + Stage 1-2 已覆盖 95%。Wave 3 作为 optional Stage 3——仅用于 0.70-0.85 不确定区间 | Claude 5 / Opus 5 发布后（LLM 判断力质变）→ 可考虑升级 LLM 的角色 |
| 3 | **与 SonarQube 的关系？** | 当前不引入 SonarQube（1 人团队不需要）。本引擎独立运行 | 如果项目未来引入 SonarQube → 本引擎的 Stage 1-2 可能被替代，但 Stage 0.5签名+Stage 0 缓存+增量+自动修复+闭环+健康监控仍是独特价值 |
| 4 | **跨语言去重何时做？** | 当前只做 Python AST（Tree-sitter for Python）。不扩展到其他语言 | 项目引入 TypeScript/Go 代码 > 10 文件 → 添加 Tree-sitter 多语言支持 |
| 5 | **测试代码去重如何处理？** | 默认 `tests/` 阈值=0.9——只报告极高相似度（> 0.9）的重复。测试中合理重复较多 | 测试文件 > 50 且 Owner 发现维护负担 → 降低 tests 阈值 |
| 6 | **`--fix` 模式下多组修复的事务性？** | 分批执行——每批 1-3 组（按 ROI 排序），每批后跑测试。任一批失败 → 整体回滚 | Phase 3/4 施工频率翻倍 → 可考虑全量自动修复（但逐批跑测试的机制不变） |
| 7 | **配置文件语义重复检测？** | Wave 2 暂不做——当前项目配置规模尚小（YAML < 20 个） | 配置文件 > 50 个且 Owner 发现配置漂移 → 添加 YAML/TOML AST 比对 |
| **8** | **Python 惯用法豁免清单是否完整？** `__init__`/`__repr__`/`@property`/`@overload`/ABC骨架——还有哪些？ | Wave 1 以当前 5 类起步；Wave 2 收集运行数据——未被豁免的高置信度误报 → 追加到豁免清单 | 引擎误报 > 10% 且误报源 > 3 种新的惯用法 → 追加豁免 + 发布补丁 |
| **9** | **策略树 YAML 的复杂度边界**——声明式策略 vs 硬编码 Python 的分界在哪？ | Wave 1-2 用硬编码 + `config.py` YAML 参数。Wave 3 单独抽离 `policy_tree.yaml`——条件 → 动作映射 | 去重行为调整需求 > 3 次/月 → 正式迁移到策略树（Owner/AI 可改 YAML 不碰 Python） |
| **10** | **全局符号索引（Symbol Index）需要多完整？** Google Kythe 是全局图谱，但我们只需要轻量版 | Wave 2 落地 SQLite 轻量版——函数签名+调用计数+import 图；不追求跨仓库/跨语言 | 函数 > 2000 且 import 整理/循环依赖检测需求 > 2 次/周 → 升级为 Redis 缓存+实时更新 |
| **11** | **Session Log 交接的粒度**——写多少内容 AI 才能零推理消费？ | Wave 1 写入：Health Score(0-100)+Top3重复热点+本次发现数。不超过 3 行 Markdown | AI 零推理消费率 < 80%（AI 仍需额外搜索）→ 调整摘要粒度 |
| **12** | **影子清单的渐进式注入策略**——三层记忆（热/领域/冷）的各层 token 预算如何分配？ | Wave 2 MVP：热规则≤400 tokens 始终注入，领域规则≤200 tokens 关键词触发，冷规则按需。对齐 AGENTS.md §8 三层记忆模型 | 注入后 AI 重复率下降 < 30% → 调 token 预算分配 |
| **13** | **Suitability Score 的阈值如何标定？** < 40 不提取 / 40-69 needs_review / ≥70 safe——这些阈值合理吗？ | Wave 2 在真实 342 函数项目上测试——手动 review 每个提取决策 + 事后 2 周观察（提取是否还引入了回归）。对标 industrial 代码评审标准 | 误提取率 > 5%（提取后悔药超过 2 次）→ 提升阈值至 ≥75 |
| **14** | **项目规模 Tier 边界是否精确？** 5000 / 15000 / 50000 行的阈值来自社区经验——是否适合本项目？ | Wave 1 以当前规模（Tier 2）起步——`config.py` 中参数化阈值，并在所有 Tier 清单中记录"此为社区平均值，尚未对本项目校准" | 项目达到上一 Tier 边界时——触发 2 周观察期（使用上一个 Tier 的策略 → 评估是否真的需要切换） |
| **15** | **部分提取的正确性验证**——60% LCS 公共核心 + 40% 差异——谁保证这确实正确？ | 部分提取后 verifier.py 不仅跑测试，还生成 diff_comparison 报告——"提取后，各调用方的行为 diff 为零（无行为变化）"。对照 LCS 前后的 AST 行为分析 | 部分提取后测试覆盖 < 80% 的差异代码路径 → 禁止该组部分提取 |
| **16** | **多个 AI session 同时做 dent 扇入是否协调？** 两个 session 可能同时发现同一组重复——缓存竞争、Session Log 冲突 | Wave 1 基础设施：`function_cache.json` 带 PID 锁——`_lock_file: process_id`。同一时间只允许一个 writer。冲突检测：report.py 在写入前检查 Session Log 最新条目是否已有相同 DUP ID | 出现 2 次及以上缓存冲突 → 升级为独立锁服务（Redis/文件锁增强） |
| **17** | **退役/卸载路径**——如果引擎本身变成维护负担怎么办？ | Wave 3 文档化退役路径：①关闭 GATE-DEDUP hook（.pre-commit-config.yaml 注释一行）②保留 function_cache.json 供手动查阅 ③所有 shared 函数保持原样（不倒回）④AGENTS.md 中标记引擎为 deprecated，替换为"请手动检查共享清单" | 引擎月度维护时间 > 2 小时超过连续 3 个月 → 自动触发退役评估 |
| **18** | **行为采样的安全性边界**——Stage 0.25 沙箱执行用户代码——如何确保不执行恶意代码？ | ①仅执行纯函数（AST 静态判定——无 I/O/global/eval/exec/subprocess）②subprocess 隔离（独立进程+256MB 内存限制+500ms 超时）③白名单允许的模块（math/json/datetime 等标准库纯粹函数）④所有采样执行有完整日志——事后可审计 | 项目中未知模块需要在沙箱中执行 → 触发安全评审 + 扩大 AST 副作用检测规则 |
| **19** | **Shared Burden Score 阈值谁来标定？** max_safe_shared_imports=80 / max_safe_per_func=15 源自行业经验——对本项目是否合适？ | Wave 2 用真实项目数据标定——监控当前 shared import 数的增长曲线 + 耦合事件数（修改 shared 函数 → break caller > 3 次 = SBS 阈值过高） | shared 函数修改导致 caller break 超过连续 3 次 → 降低 max_safe_per_func |
| **20** | **Doom Loop 冻结后谁负责解冻？** Owner 不在时怎么办？ | 冻结 = 仅停止该 DUP group 的自动修复——不影响检测/报告/其他组修复。冻结的 DUP group 仍在报告中为 needs_review，AI session 可读取但不可执行修复。解冻 = Owner 手动 CLI `--unfreeze` | 冻结组 > 10 → 自动通知 Owner（Session Log Alert）——"有 10 组重复待您手动决策" |
| **21** | **跨 AI 工具（Claude/GPT-5/Gemini）的影子清单适配**——影子清单格式是否需要适配不同模型的上下文风格？ | Wave 2 MVP 统一 YAML 格式——Context Engine 负责转译为各模型的原生格式。额外维护 adapter（claude_adapter/gpt_adapter 等）→ 复杂度上升 | 影子清单在至少 2 种 AI 工具上消费成功率 < 50%（AI 仍重复生成清单中的函数）→ 触发 ad-hoc 格式优化 |
| **22** | **LLM Stage 3 对中文命名函数的判断可靠性**——学术研究显示 LLM 代码克隆检测在不同数据集上性能差异大（BigCloneBench F1 ↔ CodeNet F1 差距 > 20%） | Wave 3 启用 LLM 前——先对项目中已知的中文命名函数对测试（"获取当前时间" vs "_now_iso"），评估跨文化语义判断的可靠性 | LLM 判断 3 组及以上中文命名对出现前后不一致 → 该项目中文函数关闭 LLM Stage 3，仅依赖 Stage 0.5-2 |
| **23** | **去重的最优边界在哪里？** Monoculture 悖论提出了一个根本性问题——不是所有重复都该消除。但"最优爆炸半径"的阈值是多少？1个 shared 函数被 N 个 caller 依赖时，N 的安全上限是多少？ | Wave 2 使用历史故障数据分析——如果某个 shared 函数曾经 bug 并影响了 M 个 caller，则 N ≤ M×0.5 是安全上限。否则通过 A/B 风险模拟（blast_radius 评分）逐步逼近 | shared 函数历史故障影响 caller > 5 → 该函数的 BRS max_caller_threshold 自动降至 5 |
| **24** | **Grandfather 的化石记录何时可以被"重新激活"？** 60 天后进入化石的重复——如果项目发生重大架构重构，是否应该重新评估？ | ①Owner 可通过 `--reevaluate-grandfather` 手动触发重新评估 ②架构层重建后（如 shared 分拆为 shared-core/shared-utils）自动触发一次性重评 | 项目中任一层的模块数变化 > 30% → 自动触发祖父重评——"架构已变，重新判断古老重复是否已可安全修复" |
| **25** | **原子性修复的 CHECKPOINT tar.gz 文件积累**——频繁修复会产生大量 checkpoint 备份，磁盘占用如何管理？ | Wave 2 设计策略：①已完成修复的 checkpoint 保留 14 天后自动清理 ②未完成修复的 checkpoint（completion_marker = null）永不自动清理——它们是崩溃恢复的唯一依据 ③磁盘占用 > 200MB → Session Log 告警 | checkpoint 文件夹大小 > 200MB → 自动清理 14 天以上的已完成 checkpoint + 写入 Session Log 清理摘要 |
| **26** | **Canary 注入的重复对应该多久更新一次？** 静态的 canary 集合会随时间失去有效性——因为引擎在进化，旧 canary 逐渐变得不再有区分力 | 每月更新 1-2 对——从最近发现的真实重复/非重复中提取新的 canary，退役 1-2 对最老或最简单的（已被引擎完美识别不再有区分力）的 canary | canary sensitivity 稳定 ≥ 95% 连续 3 个月 → 解释为"canary 太简单"——触发更新 + 添加更难区分的新 canary |
| **27** | **Temporal Drift 是否会导致 Stage 0.5 的全局退化？** 如果大量函数同时进入 UNSTABLE 状态（如项目全面类型化），Stage 0.5 的有效性会骤降 | Wave 2 监控 unstable_ratio = unstable 函数/总函数数。unstable_ratio ≥ 50% → Session Log 告警——"Stage 0.5 签名匹配对半数函数失效——全量扫描退化为 Stage 1-2 only" | unstable_ratio > 60% → 引擎自动降低 Stage 0.5 权重——从 Stage 0 pipeline 中降低签名碰撞分数在 final similarity 中的权重（从 30%→10%） |
| **28** | **引擎的成本效益何时会倒挂？** SAS 评分依赖对"节省时间"和"成本"的估算——这些估算本身的主观性多大？ | Wave 2 月度运行 SAS 自审。初始用保守估算（节省 = 重复组数 × 0.5h/组，成本 = 实际维护时间记录）。3 个月后基于真实数据重新标定 | SAS 连续 2 个月 < 50 → 触发 Owner 手动审核——"引擎是否值得继续全功能运行" |
| **29** | **死模块删除的安全边界？** 引擎标记 DEAD 模块——自动删除 vs 等待 Owner 确认的边界在哪？ | 默认只标记、不自动删除——自动删除=不可恢复操作。生成 TaskCard DEAD-MODULE-{N}→Owner 手动确认删除 | 累积死模块 > 5 个 → Session Log 强调——"5 个死模块消耗 X KB 磁盘+每次全量扫描 Y ms" |
| **30** | **观察期的时长是否合理？** 14 天适用于本项目还是来自工业界的大团队节奏？1人团队中代码变更频率可能更高/更低 | Wave 2 起始用 14 天（保守）。记录 3 个月数据——实际有多少回归 bug 在 7 天内暴露 vs 14 天内暴露？基于真实数据调整 | 3 个月数据：80%+ 回归在 7 天内暴露 → 缩短观察期至 10 天 |
| **31** | **Recovery Manifest 的存储开销**——每个 fix_plan 都产出 tar.gz + 纯文本 manifest，修复频繁时磁盘占用如何管理？ | 与 checkpoint 同步管理——已完成修复的 manifest 保留 14 天后自动清理。未完成的 manifest 永不清理（它们是最后的恢复希望） | manifest 总大小 > 100MB → 清理已完成 manifest + Session Log 记录清理摘要 |
| **32** | **主题聚类的准确性由谁验证？** 三层加权聚类（前缀30%+AST50%+共现20%）的权重分配是否合理？ | Wave 2 起始用当前权重。每次主题聚类后由 Owner 或 AI 审查——"这 3 个主题是否准确反映了真实问题？"→反馈调整权重 | 主题审查 "不准确"率 > 20%（5 个主题中 1 个被判断为误导）→ 算法调整 |
| **33** | **行为正确性签名的代表性**——5 组采样输入能否足够覆盖 shared 函数的实际行为？ | Wave 2 起始用 5 组基础采样（边界值+典型值+特殊值）。每次行为漂移检测到后——分析是否采样输入覆盖不足→如果是，扩展采样 | 行为漂移检测到但实际行为未变化（假阳性漂移）> 3 次 → 扩展采样至 10 组 |
| **34** | **Pre-Apply Integrity Gate 的时机窗口**——从 Pre-Apply 检查到 APPLY 第一行写入之间仍有极小窗口 | Wave 2 实现为：检查所有目标文件 SHA256→获取文件系统锁（flock）→开始写入。锁机制需在 Windows 上验证（`msvcrt.locking` or `portalocker`） | 检测到 2 次及以上 "gate passed 但写入时文件已变" → 升级锁机制 + 报告 |
| **35** | **微型克隆检测的频率阈值如何标定？** ≥10/≥8/≥5 文件的三个等级来自业界经验还是需要本项目数据校准？ | Wave 1 起始用默认阈值。运行 2 周后基于实际检测数据调参——如果微克隆 TOP 列表中有大量"正常重复"（如 import 行）→ 提高阈值 | 微克隆 NOTABLE 及以上等级中 ≥30% 被 Owner 标记为 "非问题" → 提高触发阈值 2 个文件 |
| **36** | **自动测试生成的测试维护成本由谁承担？** 提取后自动生成 12 个测试 → 未来函数行为变更时这些测试会失败 → 需要更新测试 → 是否消耗了比去重更多的 Owner 时间？ | 生成的测试带有 @auto-generated-by-dedup 标记——引擎在后续扫描中发现该函数重新注册（行为变更）→ 自动触发"测试重生成"而非让 Owner 手动修复 | 测试重生成频率 > 1次/月/函数 → 该函数标记 UNSTABLE → 建议"shared 函数行为过于不稳定——撤回提取" |
| **37** | **三维信任模型的 Trust Score 如何聚合？** 存在性(§3.16)+行为正确性(§3.23)+契约一致性(§3.27) 三个维度的权重分配？ | 初始权重：存在性 30%（最基础）+ 行为正确性 40%（最重要）+ 契约一致性 30%。基于本项目的实际"信任break"事件分布调整 | 任一维度连续 3 次扫描出现 MAJOR 及以上问题 → 该维度权重自动+10% |
| **38** | **跨边界克隆的触发是否应该在 Wave 1 就提供基础支持？** 微型克隆可以 Wave 1 折叠进 scanner，但跨边界的检测逻辑是否需要独立的初次扫描？ | Wave 1 在 scanner 中预埋边界标签（is_test/is_script/is_l0x/is_vendored 标记）。W1 产出 cross_boundary_tagging 功能 → W2 在此基础上做跨边界检出 | W1 边界标签预埋完成后 → W2 跨边界检测可基于标签直接运行——减少了 W2 的前置工作量 |
| **39** | **决策审计日志会无限增长吗？** decision_audit_log.yaml 追加不可变模式 → 一年后可能有 500+ 决策 → 文件膨胀 | 按月归档——每月生成 `decision_audit_log_2026-05.yaml` → 压缩为 `.tar.gz` → 保留 12 个月 → 更早的归档到 `data/archive/`。查询接口自动跨文件检索 | 月度日志单文件 > 10MB → 触发归档 + 提醒 Owner "审计日志在膨胀——考虑合并决策摘要" |
| **40** | **主动发现的双通道优先级矛盾**——Channel A 签名匹配返回 validate_input(str) → bool，Channel B 语义匹配返回 validate_and_sanitize(str) → str——两个结果冲突时告诉 AI 哪个？ | 签名匹配结果（Channel A）优先级高于语义匹配（Channel B）——签名精确度更高。两个通道结果不一致时 → 合并展示：EXACT_MATCH for signature + CLOSE_MATCH for semantic → "精确匹配: X, 你可能也感兴趣: Y, Z" | 签名匹配和语义匹配结果的文件数交叉 > 30% → 调整签名归一化粒度（当前过于粗糙丢失了匹配） |

---

## §11 施工指引

### 11.1 Wave 1 第一步（v0.7.0 调整——核心阻断+交接+自保护+行为采样 全部落地）

1. 创建 `src/zephyr/l01_infrastructure/code_dedup_engine/` 包——所有 40 个模块文件
2. 实现 `cache_manager.py`：定义 `function_cache.json` Schema（Pydantic V2），实现 `load()`（含 `_integrity` 校验）/ `save()`（原子写入 `.tmp` → `os.replace`）/ `incremental_update()` / `full_rebuild()` / `self_heal()`（损坏检测 + 自愈重建）
3. 实现 `diff_detector.py`：`git diff --name-only --cached` → 变更 `.py` 文件列表 → `ast.parse()` 提取新增/修改的函数定义（**函数粒度增量**——非文件粒度）
4. 实现 `signature_matcher.py`：对每个缓存函数计算 `signature_fingerprint = SHA256(param_types + return_type) [:12]`；新增函数签名 O(1) 精确匹配缓存 → Collision/Near-Collision 判定
5. 实现 `scanner.py`：对变更函数计算 MinHash → LSH → 候选对；加入路径感知阈值 + **代码块级滑动窗口**（min_block_size=5 行）
6. 实现 `degradation.py`：各 Stage 独立 try/except + `degradation_level` 记录；Stage 2/3 失败 → 降级到更低 Stage
7. 实现 `config.py`：阈值表 + 路径分区 + **`IDIOM_WHITELIST`**（`__init__`/`__repr__`/`@property`/`@overload`/ABC骨架的 AST 模式匹配规则）+ **`DESIGN_PATTERN_WHITELIST`**（Strategy/Adapter/Factory/Template Method/Observer/Decorator 的 AST 模式匹配规则）
8. 实现 `report.py`：YAML 输出 + **五档退出码判定**（含 exit code 4 DEGRADED）+ Health Score 初版
9. 实现 `annotations.py`：解析 `@intentional-duplicate` 标记的正则匹配 + **Owner 决策模式学习**（同类未来自动 suppress）
10. 实现 `prioritizer.py`：`priority_score = occurrence_count × similarity × affected_files × hot_path_weight × roi_factor`
11. 实现 `health_monitor.py`：Health Score 计算 + 趋势（↑↓→）+ **Session Log 写入去重摘要**（不超过 3 行 Markdown——Health Score + Top3 热点 + 本次发现）+ Shared Burden Score 聚合
12. 实现 `behavioral_sampler.py`（**v0.6.0 新增——Stage 0.25**）：类型注解推断→采样输入生成→沙箱子进程执行→输出 diff 比对→副作用 AST 静态检测
13. 实现 `self_scanner.py`（**v0.6.0 新增——引擎自保护**）：引擎自身源码去重检测 + Codegen fix manifest 初始生成 + 依赖版本自检
14. 实现 CLI `detect_code_duplicates.py`：argparse 参数 `--warn-only` / `--fail-on-duplicates` / `--incremental` / `--full` / `--output` / `--file`（单文件快速检查）+ `--quick-init`（冷启动加速——仅 Stage 0.5）
15. **落地 GATE-DEDUP**：在 `.pre-commit-config.yaml` 中加 `detect_code_duplicates.py --incremental` as pre-commit hook——exit code 2 → 阻断 commit
16. 编写测试 ≥ 30 条：`test_code_dedup_engine.py` + `test_signature_matcher.py` + `test_degradation.py` + `test_behavioral_sampler.py`——含已知重复/非重复对 + 签名碰撞 + 降级场景 + 行为采样安全边界

### 11.2 Wave 1 CLI 参数设计

```
detect_code_duplicates.py [OPTIONS]

扫描模式:
  --incremental           增量扫描（仅扫描 git diff 变更文件）[默认]
  --full                  全量扫描（忽略缓存，重新解析所有函数）
  --file PATH             单文件快速检查——仅扫描指定文件的新函数签名（Session 内轻量拦截用）

输出控制:
  --warn-only             即使发现 high/critical 重复也 exit 1（而非 exit 2）
  --fail-on-duplicates    发现 high/critical 重复 → exit 2（阻断 CI）
  --output PATH           报告输出路径 [默认: stdout]
  --format FORMAT         报告格式 [yaml | json] [默认: yaml]
  --quiet                 只输出退出码，不输出报告内容

阈值覆盖:
  --threshold-global FLOAT        全局 AST 相似度阈值 [默认: 0.70]
  --threshold-shared FLOAT        shared/ 目录阈值 [默认: 0.30]
  --threshold-tests FLOAT         tests/ 目录阈值 [默认: 0.90]
  --min-lines INT                  最小函数行数（过短函数不检测）[默认: 3]
  --min-block-tokens INT          代码块级去重的最小 token 数 [默认: 15]

降级控制:
  --no-degrade             禁止降级运行——任何 Stage 失败 → exit 3（严格模式）
  --allow-degrade          允许降级——Stage N 失败 → 降级到 Stage N-1，exit 4 [默认]

其他:
  --skip-cache             跳过缓存——强制重新解析AST（即使增量模式）
  --ignore-patterns GLOB   额外忽略的文件 glob 模式
  --quick-init             冷启动加速模式——仅执行 Stage 0.5 签名指纹扫描，跳过 Stage 1-2（首次运行 5s 完成）

退出码:
  0 = 无重复，PASS
  1 = 发现低/中严重度重复，WARN（不阻断）
  2 = 发现高/严重重复，ERROR（阻断 commit）
  3 = 引擎自身故障，SKIP（跳过门禁）
  4 = 降级运行完成，DEGRADED（有结果但部分 Stage 未执行）

### 11.3 已知重复函数测试用例（供单元测试使用）

```python
# tests/unit/test_code_dedup_engine.py 中的测试 fixture

KNOWN_DUPLICATES = {
    "now_iso_group": {
        "functions": [
            {"name": "_now_iso", "body": "def _now_iso():\n    from datetime import datetime, timezone\n    return datetime.now(timezone.utc).isoformat()"},
            {"name": "now_iso", "body": "def now_iso():\n    from datetime import datetime, timezone\n    return datetime.now(timezone.utc).isoformat()"},
            {"name": "_default_now", "body": "def _default_now():\n    from datetime import datetime, timezone\n    return datetime.now(timezone.utc).isoformat()"},
        ],
        "expected_similarity_min": 0.95,
        "expected_clone_type": "Type-2",   # 重命名但结构相同
    },
    "repo_root_group": {
        "functions": [
            {"name": "REPO_ROOT", "body": "from pathlib import Path\nREPO_ROOT = Path(__file__).resolve().parent.parent.parent"},
            {"name": "_project_root", "body": "import os\n_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))"},
        ],
        "expected_similarity_min": 0.70,   # 语义相同但写法不同
        "expected_clone_type": "Type-3",
    },
}
```

### 11.4 验证流程（每次施工后必执行）

1. `python -m pytest tests/unit/ -q` —— 确认全部测试（≥25条）全绿
2. `detect_code_duplicates.py --full --warn-only` —— 确认扫描全量代码可正常输出含 Health Score
3. 检查退出码与 severity 的映射是否正确（0/1/2/3/4 五档）
4. 检查 `function_cache.json` 能与磁盘文件一致（运行 `--full` 后检查 cache 条目数 = 实际函数数 + `_integrity` 校验通过）
5. 模拟降级场景：故意移除 Tree-sitter grammar → `detect_code_duplicates.py --full` → 退出码应为 4（DEGRADED），而非 3（TOOL-ERROR）
6. 模拟缓存损坏：修改 `function_cache.json` 的 `_integrity` → 下次扫描 → 自动 full rebuild → exit 0/1 正常
7. 检查 Session Log 已追加去重摘要（Health Score + Top3 热点 + 本次发现）

---

## §12 施工——文件创建清单

以下列出 Wave 1 第一步需要创建的**全部文件**（完整绝对路径）：

### 12.1 源码文件（共40个模块——v0.8.0新增 simplicity_auditor / dead_module_detector / observation_window_guard / recovery_manifest_writer / thematic_clusterer / behavioral_trust_checker / pre_apply_integrity_gate）

| # | 文件 | 完整绝对路径 | 说明 |
|:---:|------|------------|------|
| 1 | `__init__.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\__init__.py` | 包初始化+模块职责声明（AI自描述） |
| 2 | `cache_manager.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\cache_manager.py` | 缓存管理（含_integrity自检+原子写入+自愈） |
| 3 | `diff_detector.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\diff_detector.py` | 变更检测（函数粒度增量） |
| 4 | `signature_matcher.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\signature_matcher.py` | Stage 0.5 签名碰撞检测 |
| 5 | `scanner.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\scanner.py` | Token扫描+代码块级去重 |
| 6 | `degradation.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\degradation.py` | 降级运行管理 |
| 7 | `health_monitor.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\health_monitor.py` | 健康仪表盘+Session Log写入 |
| 8 | `report.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\report.py` | 报告生成+五档退出码 |
| 9 | `prioritizer.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\prioritizer.py` | 优先级排序（含ROI因子） |
| 10 | `config.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\config.py` | 配置管理+惯用法豁免 |
| 11 | `annotations.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\annotations.py` | 标记解析+Owner决策学习 |
| 12 | `extraction_safety.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\extraction_safety.py` | Wave 2——安全提取评估（Suitability Score+不安全目录+影响预分析） |
| 13 | `stale_shared_detector.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\stale_shared_detector.py` | Wave 2——过期共享函数检测（签名漂移+调用参数匹配） |
| 14 | `debt_projector.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\debt_projector.py` | Wave 2——去重债务预测（引入速率→还本付息计划） |
| 15 | `behavioral_sampler.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\behavioral_sampler.py` | Stage 0.25：行为采样验证（类型推断→沙箱执行→输出diff）——Wave 1 |
| 16 | `self_scanner.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\self_scanner.py` | 引擎自保护（自扫描+Codegen防护+依赖自检）——Wave 1 |
| 17 | `shared_lifecycle_manager.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\shared_lifecycle_manager.py` | Wave 2——共享函数生命周期管理（5阶段状态机） |
| 18 | `import_surface_tracker.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\import_surface_tracker.py` | Wave 2——Import表面积负债（SBS评分+跨层依赖热图） |
| 19 | `doom_loop_guard.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\doom_loop_guard.py` | Wave 2——Doom Loop防护（修复升级阶梯+冻结机制） |
| 20 | `monoculture_guard.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\monoculture_guard.py` | Wave 2——Monoculture免疫（BRS+去重悖论+停止高风险去重） |
| 21 | `atomic_fixer.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\atomic_fixer.py` | Wave 2——原子性修复（WAL+CHECKPOINT+崩溃恢复） |
| 22 | `grandfather_manager.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\grandfather_manager.py` | Wave 2——Grandfather三定律（古老重复+化石+考古） |
| 23 | `false_negative_auditor.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\false_negative_auditor.py` | Wave 2——漏报盲审（Sweep+Canary+抽样审查） |
| 24 | `shadow_trust_validator.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\shadow_trust_validator.py` | Wave 2——影子清单信任链（import校验+幻觉清除） |
| 25 | `temporal_drift_tracker.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\temporal_drift_tracker.py` | Wave 2——签名时态漂移（指纹演化+UNSTABLE+自动重算） |
| 26 | `simplicity_auditor.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\simplicity_auditor.py` | Wave 2——引擎成本效益自审计（SAS计算+净收益评估+退役建议） |
| 27 | `dead_module_detector.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\dead_module_detector.py` | Wave 2——死共享模块检测（僵尸文件+自动删除建议） |
| 28 | `observation_window_guard.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\observation_window_guard.py` | Wave 2——提取后稳定观察期（14天观察+回滚触发） |
| 29 | `recovery_manifest_writer.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\recovery_manifest_writer.py` | Wave 2——恢复失败的恢复（R2纯文本Manifest+递归安全网） |
| 30 | `thematic_clusterer.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\thematic_clusterer.py` | Wave 2——噪声信号比·主题聚类（三层加权+Executive Summary） |
| 31 | `behavioral_trust_checker.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\behavioral_trust_checker.py` | Wave 2——影子清单行为正确性（行为签名+漂移检测+告警） |
| 32 | `pre_apply_integrity_gate.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\pre_apply_integrity_gate.py` | Wave 2——并发修改检测（Pre-Apply SHA256验证+冲突报告） |
| 33 | `micro_clone_detector.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\micro_clone_detector.py` | Wave 1——微型克隆检测（n-gram频率计数L0/L1/L2+高频模式聚合） |
| 34 | `auto_test_generator.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\auto_test_generator.py` | Wave 2——提取后自动测试生成（类型驱动+金丝雀+契约——对标Google Mozart） |
| 35 | `contract_consistency_checker.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\contract_consistency_checker.py` | Wave 2——API契约一致性验证（四层校验——三维信任模型） |
| 36 | `cross_boundary_detector.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\cross_boundary_detector.py` | Wave 2——跨边界克隆感知（四大边界差异化策略——对标Google Blaze） |
| 37 | `decision_auditor.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\decision_auditor.py` | Wave 2——去重决策审计链（DecisionFingerprint不可变追加日志+证据包+可回滚） |
| 38 | `function_discovery.py` | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\function_discovery.py` | Wave 2——共享函数主动发现（签名+语义双通道——主动赋能AI——<150行） |

### 12.2 CLI 脚本

| # | 文件 | 完整绝对路径 | 说明 |
|:---:|------|------------|------|
| 1 | `detect_code_duplicates.py` | `D:\ZephyrAlpha\scripts\governance\d1_structure\detect_code_duplicates.py` | CLI 入口 |

### 12.3 测试文件

| # | 文件 | 完整绝对路径 | 说明 |
|:---:|------|------------|------|
| 1 | `test_code_dedup.py` | `D:\ZephyrAlpha\tests\unit\test_code_dedup.py` | 单元测试 |

### 12.4 数据文件（运行时生成，不纳入版本控制）

| # | 文件 | 完整绝对路径 | 说明 |
|:---:|------|------------|------|
| 1 | `function_cache.json` | `D:\ZephyrAlpha\data\cache\function_cache.json` | 预计算缓存（`.gitignore`） |
| 2 | `codegen_fix_manifest.json` | `D:\ZephyrAlpha\data\cache\codegen_fix_manifest.json` | Codegen覆盖防护清单——所有 __init__.py SHA256 监控 |
| 3 | `doom_loop_freeze_list.json` | `D:\ZephyrAlpha\data\cache\doom_loop_freeze_list.json` | Doom Loop 冻结组 |
| 4 | `shared_lifecycle.yaml` | `D:\ZephyrAlpha\data\cache\shared_lifecycle.yaml` | 共享函数生命周期记录 |
| 5 | `shared_burden.yaml` | `D:\ZephyrAlpha\data\cache\shared_burden.yaml` | SBS评分+跨层依赖热图 |
| 6 | `monoculture_risk.yaml` | `D:\ZephyrAlpha\data\cache\monoculture_risk.yaml` | Monoculture BRS 评分 |
| 7 | `grandfather_registry.yaml` | `D:\ZephyrAlpha\data\cache\grandfather_registry.yaml` | 古老重复登记 |
| 8 | `fix_checkpoint_*` | `D:\ZephyrAlpha\data\cache\fix_checkpoint_*.tar.gz` | WAL 修复检查点 |
| 9 | `sensitivity_sweep_report.yaml` | `D:\ZephyrAlpha\data\cache\sensitivity_sweep_report.yaml` | 月度低阈值扫描报告 |
| 10 | `canary_report.yaml` | `D:\ZephyrAlpha\data\cache\canary_report.yaml` | Canary 灵敏度/特异度验证 |
| 11 | `shadow_trust.yaml` | `D:\ZephyrAlpha\data\cache\shadow_trust.yaml` | 影子清单信任链 |
| 12 | `drift_registry.yaml` | `D:\ZephyrAlpha\data\cache\drift_registry.yaml` | 签名时态漂移记录 |
| 13 | `simplicity_audit.yaml` | `D:\ZephyrAlpha\data\cache\simplicity_audit.yaml` | 引擎成本效益自审计报告（SAS+净收益） |
| 14 | `dead_module_report.yaml` | `D:\ZephyrAlpha\data\cache\dead_module_report.yaml` | 死共享模块检测结果 |
| 15 | `observation_window.yaml` | `D:\ZephyrAlpha\data\cache\observation_window.yaml` | 提取后稳定观察期状态 |
| 16 | `recovery_manifest_*.txt` | `D:\ZephyrAlpha\data\cache\recovery_manifest_*.txt` | R2纯文本恢复清单 |
| 17 | `thematic_summary.yaml` | `D:\ZephyrAlpha\data\cache\thematic_summary.yaml` | 主题聚类Executive Summary |
| 18 | `behavioral_trust.yaml` | `D:\ZephyrAlpha\data\cache\behavioral_trust.yaml` | 影子清单行为正确性验证 |
| 19 | `pre_apply_integrity_gate.yaml` | `D:\ZephyrAlpha\data\cache\pre_apply_integrity_gate.yaml` | Pre-Apply完整性验证报告 |
| 20 | `fragile_extractions.yaml` | `D:\ZephyrAlpha\data\cache\fragile_extractions.yaml` | 被标记为FRAGILE的提取记录（来自观察期回滚） |
| 21 | `micro_clone_report.yaml` | `D:\ZephyrAlpha\data\cache\micro_clone_report.yaml` | v0.9.0——微型克隆检测聚合报告（L0/L1/L2三级+高频模式列表） |
| 22 | `auto_test_gen.yaml` | `D:\ZephyrAlpha\data\cache\auto_test_gen.yaml` | v0.9.0——自动测试生成记录（生成测试数/BRS缓解效果/生成时间） |
| 23 | `contract_consistency.yaml` | `D:\ZephyrAlpha\data\cache\contract_consistency.yaml` | v0.9.0——API契约一致性验证报告（四层校验+Trust Score聚合） |
| 24 | `cross_boundary_report.yaml` | `D:\ZephyrAlpha\data\cache\cross_boundary_report.yaml` | v0.9.0——跨边界克隆检测报告（四大边界+独立策略+分类） |
| 25 | `decision_audit_log.yaml` | `D:\ZephyrAlpha\data\cache\decision_audit_log.yaml` | v0.10.0——去重决策审计日志（DecisionFingerprint不可变追加——按月归档） |
| 26 | `function_discovery.yaml` | `D:\ZephyrAlpha\data\cache\function_discovery.yaml` | v0.10.0——共享函数主动发现索引（签名+TF-IDF双通道） |

---

## 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\code-dedup-engine\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\` | Code Dedup Engine 源码（22 模块） |
| CLI 脚本 | `D:\ZephyrAlpha\scripts\governance\d1_structure\` | detect_code_duplicates.py + fix_code_duplicates.py |
| 测试代码 | `D:\ZephyrAlpha\tests\unit\` | test_code_dedup.py + test_signature_matcher.py + test_degradation.py 等 |
| 缓存数据 | `D:\ZephyrAlpha\data\cache\function_cache.json` | 运行时生成（.gitignore + _integrity校验） |
| 策略树配置 | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\config\policy_tree.yaml` | 策略树YAML——Wave 3落地（Owner/AI可改YAML调行为） |
| 符号索引 | `D:\ZephyrAlpha\data\cache\symbol_index.db` | 轻量符号索引 SQLite——Wave 2

---

## 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| Script System (MOD-INF-005) | 去重脚本注册到 manifest，遵循退出码约定 0/1/2/3/4 | `detect_code_duplicates.py` → `script_manifest.yaml` | G4 入库验收 + exit code 映射验证 |
| Gate Engine (MOD-INF-007) | **GATE-DEDUP Wave 1 即落地！** Pre-commit hook exit code → Gate PASS/FAIL/BLOCKED/SKIP/DEGRADED | CT-SCRIPT-GATE-001 | Gate 判定日志中 GATE-DEDUP 出现 + exit code 2 阻断验证 |
| Context Engine (MOD-INF-008) | 生成时预防：注入共享 API 影子清单到 system prompt + 渐进式三层记忆（热/领域/冷）+ 消费验证回环 | `shadow_api_manifest.yaml` → CE build → inject | CE build log 包含影子清单条目 + 回环验证可运行 |
| 降级运行 (本模块) | 引擎自身鲁棒性——各 Stage 独立 try/except → 降级而非崩溃 | degradation.py → Stage 0.5-3 各层包装 | degradation_level 字段 + exit code 4 验证 |
| Knowledge Base (MOD-INF-012) | 引擎发现的重复模式/健忘热点 → KB 持久化 → 未来 AI session 主动查阅 | health_monitor.py → KB API → kb://dedup/insights | KB 可查询 dedup 相关实体 |
| 安全提取评估 (本模块) | Suitability Score + 不安全模式目录——防止盲提取创建更重技术债 | extraction_safety.py → auto_fixer.py pre-check | 卡片中 Suitability ≥ 40 才执行修复 |
| 过期共享函数检测 (本模块) | 监控 shared 函数是否与调用方实际需求漂移 | stale_shared_detector.py → health_monitor.py → Health Score | stale_shared_count 纳入 Health Score 计算 |
| 去重债务预测 (本模块) | 引入速率驱动的债务还本付息规划 | debt_projector.py → health_monitor.py → `--projection` | 4/8/12 周债务预测 + ETA 还清日期 |
| Doom Loop 防护 (本模块) | 修复升级阶梯 + 3次失败冻结 + Owner告警 | doom_loop_guard.py → auto_fixer.py → Session Log | 冻结列表可查 + 失败分析报告可追溯 |
| 共享生命周期 (本模块) | 5阶段状态机——Active→Retired + 迁移diff | shared_lifecycle_manager.py → KB + shadow manifest | Retired 函数 KB 保留指纹 + 退役原因 |
| Import负债追踪 (本模块) | SBS 0-100 + 跨层依赖热图 + 提取门槛联动 | import_surface_tracker.py → health_monitor.py + superintelligent | SBS ≥ 31 → Suitability 门槛提升 |
| 行为采样验证 (本模块) | Stage 0.25——类型推断+沙箱执行+输出diff——低测试覆盖安全网 | behavioral_sampler.py → Stage 0 pipeline | 行为一致→提升置信度；不一致→降级 |
| 引擎自保护 (本模块) | 自扫描+Codegen覆盖防护+依赖版本自检——吃自己的狗粮 | self_scanner.py → codegen_fix_manifest.json + Session Log | 覆盖检测→修复diff可一键重新应用 |
| Shared+Core (MOD-INF-016) | 去重→提取→SSoT注册三合一原子操作 | Auto Fixer → SSoT Guard → `b_shared.yaml` | 提取的函数在 YAML SSoT 中可检索 |
| Feedback Loop (MOD-INF-010) | 重复模式→FLE→`dedup_pattern_report` | FLE detect → `dedup_pattern_report` | 重复模式可被 FLE 检测并触发 evolve() |
| Task System (MOD-INF-006) | high/critical 重复 → TaskCard → AI pipeline 修复 | TaskCard `source_blueprint: MOD-INF-017` | TaskCard 状态可追踪 |
| Session Log | **Wave 1 即落地**——扫描结果摘要写入 Session Log → next AI session | Scanner → health_monitor.py → Session Log | Next AI session 零推理读到去重发现 + Health Score |
| 微克隆检测 | n-gram频率计数结果 + micro_clone_report.yaml | Scanner → micro_clone_detector.py → Session Log | AI session 在生成前读取高频微克隆模式 → 避免继续产生 |
| 自动测试生成 | 提取后生成3类测试→test/目录 + auto_test_gen.yaml | Auto Fixer → auto_test_generator.py → AI pipeline | pytest 运行→通过则BRS下降/失败则标记UNSTABLE |
| 契约一致性 | 四层校验→contract_consistency.yaml→Trust Score聚合 | contract_consistency_checker.py → Shadow Manifest + Session Log | 契约腐烂→钱包告警/影子清单降级/描述自动修复 |
| 跨边界克隆 | 四大边界检测→cross_boundary_report.yaml→分类报告 | Scanner → cross_boundary_detector.py → Session Log | 跨边界红线→不自动修仅告警/跨层冗余→可auto_fix |
| 决策审计链 | DecisionFingerprint不可变追加日志 + 证据包 + 回滚计划 | decision_auditor.py → decision_audit_log.yaml + Session Log | CLI audit --since/--rollback/--verify——任何时候都能追溯+回滚 |
| 主动函数发现 | 签名+语义双通道索引→主动注入Context Engine | function_discovery.py → function_discovery.yaml → Context Engine | AI生成函数前自动被告知已有实现——零轮对话摩擦 |
| Self-Benchmark (内部) | Wave 3——全量扫描后用 5 组已知重复/非重复对自验证 | Scanner → benchmark → degradation check | 引擎退化 → 告警 |
| Monoculture免疫 (本模块) | Blast Radius Score——去重悖论显式评估 + 停止高风险去重 | monoculture_guard.py → auto_fixer.py + health_monitor.py | BRS ≥ 76 → 停止去重 + 生成 "为什么不修复" 报告 |
| 原子性修复 (本模块) | WAL 式 fix_plan + 崩溃自动恢复 | atomic_fixer.py → fix_checkpoint_*.tar.gz + Session Log | 引擎重启自动检测残留 checkpoint → 恢复代码库一致状态 |
| Grandfather三定律 (本模块) | 古老重复管理——≥30天永不自动修复 + ≥60天化石 | grandfather_manager.py → cache_manager.py + Health Score | 古老重复不参与 auto_fix + 化石不参与 Health Score |
| 漏报盲审 (本模块) | Sweep + Canary + 抽样——FNR 可量化 | false_negative_auditor.py → sensitivity_report.yaml + canary_report.yaml | FNR 趋势 + canary_miss 告警 |
| 影子信任链 (本模块) | import 存活校验 + 幻觉清除 + Trust Score | shadow_trust_validator.py → Context Engine + shadow_manifest.yaml | Trust Score < 90% → 拒绝注入 + 降级 "无清单模式" |
| 时态漂移追踪 (本模块) | 签名演化自动检测 + UNSTABLE标记 + 全局退化监控 | temporal_drift_tracker.py → cache_manager.py + Stage 0.5 | unstable_ratio > 60% → Stage 0.5 权重降级 |

---

## 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml` | MOD-INF-017 version→0.8.0, completeness→升级 | 蓝图升级到Monoculture免疫·原子修复·漏报可视·全生命周期·自审计闭环 |
| 2 | script_manifest.yaml | `D:\ZephyrAlpha\scripts\governance\script_manifest.yaml` | 注册 `detect_code_duplicates.py` + `fix_code_duplicates.py` + exit code 4 + `--quick-init` + `--unfreeze` + `--force-monoculture` + `--override-grandfather` 标志 | Wave 1 产出 CLI + 新增 4 个特殊覆盖标志 |
| 3 | AGENTS.md §5.1 共享清单 | `D:\ZephyrAlpha\AGENTS.md` | 新增"共享API影子清单"锚点——链接到 `shadow_api_manifest.yaml`；新增 §8 三层记忆模型注入说明；新增 Deprecated 函数标记说明 | 生成时预防的落地文件 + 渐进式披露 + 生命周期感知 |
| 4 | Gate Engine YAML 配置 | `D:\ZephyrAlpha\src\zephyr\gates\g6_blueprint_compliance.yaml` | 新增 GATE-DEDUP 门禁规则——exit code 0-4 判定（PASS/WARN/FAIL/SKIP/DEGRADED） | **Wave 1 即落地** pre-commit 门禁 |
| 5 | `.pre-commit-config.yaml` | `D:\ZephyrAlpha\.pre-commit-config.yaml` | 新增 `detect_code_duplicates.py --incremental` hook | **Wave 1 即落地** 阻断能力 |
| 6 | `codegen_fix_manifest.json` | `D:\ZephyrAlpha\data\cache\codegen_fix_manifest.json` | **新建**——记录所有层 `__init__.py` 的修复哈希 + 覆盖检测状态 | v0.6.0 引擎自保护——Codegen覆盖防护 |
| 7 | `doom_loop_freeze_list.json` | `D:\ZephyrAlpha\data\cache\doom_loop_freeze_list.json` | **新建**——记录被冻结的 DUP group + 失败分析 + 解冻指引 | v0.6.0 Doom Loop 防护——防止自动修复退化 |
| 8 | `shared_lifecycle.yaml` | `D:\ZephyrAlpha\data\cache\shared_lifecycle.yaml` | **新建**——共享函数生命周期记录（5阶段状态+迁移diff+时间线） | v0.6.0 共享生命周期管理——防止僵尸函数坟场 |
| 9 | `shared_burden.yaml` | `D:\ZephyrAlpha\data\cache\shared_burden.yaml` | **新建**——SBS评分+跨层依赖热图+shared分拆建议 | v0.6.0 Import负债追踪——防止耦合黑洞 |
| 10 | b_shared.yaml | `D:\ZephyrAlpha\architecture-model\layers\b_shared.yaml` | 去重后自动修复提取的函数——通过 SSoT Guard 注册 | SSOT 注册闭环 |
| 11 | evolve() 接口数据源配置 | `D:\ZephyrAlpha\src\zephyr\infra\evolve.py` | `failure_patterns` 中加入 `dedup_pattern_report` 作为 L2 Pattern 输入 | Wave 3 进化闭环 |
| 12 | pyproject.toml | `D:\ZephyrAlpha\pyproject.toml` | 锁定 Tree-sitter Python grammar 版本 | 风险 #9 缓解 |
| 13 | `monoculture_risk.yaml` | `D:\ZephyrAlpha\data\cache\monoculture_risk.yaml` | **新建**——BRS评分+Monoculture Top风险+去重 vs 爆炸半径评估 | v0.7.0 Monoculture免疫——去重成功的悖论显式评估 |
| 14 | `grandfather_registry.yaml` | `D:\ZephyrAlpha\data\cache\grandfather_registry.yaml` | **新建**——古老重复登记（首次日期+asterian+考古状态+化石记录） | v0.7.0 Grandfather三定律——古老重复的权威记录 |
| 15 | `fix_checkpoint_*` | `D:\ZephyrAlpha\data\cache\fix_checkpoint_*.tar.gz` | **新建**——WAL 式修复检查点（PREFLIGHT CHECKPOINT→APPLY标记→崩溃恢复依据） | v0.7.0 原子性修复——代码库崩溃恢复的唯一保证 |
| 16 | `sensitivity_sweep_report.yaml` | `D:\ZephyrAlpha\data\cache\sensitivity_sweep_report.yaml` | **新建**——月度低阈值扫描报告（正常 vs 降低阈值发现数 + FNR估算 + 根因分析） | v0.7.0 漏报盲审第一层——Sensitivity Sweep |
| 17 | `canary_report.yaml` | `D:\ZephyrAlpha\data\cache\canary_report.yaml` | **新建**——Canary 灵敏度/特异度验证（positive missed + negative flagged + 趋势） | v0.7.0 漏报盲审第二层——FNR 可量化 |
| 18 | `shadow_trust.yaml` | `D:\ZephyrAlpha\data\cache\shadow_trust.yaml` | **新建**——影子清单信任链（verified/hallucinated/Trust Score/spot-check结果） | v0.7.0 影子信任链——防止幻觉函数被注入 AI context |
| 19 | `drift_registry.yaml` | `D:\ZephyrAlpha\data\cache\drift_registry.yaml` | **新建**——签名指纹演化历史（每次扫描记录新旧fingerprint对比+稳定性判定） | v0.7.0 时态漂移——Stage 0.5 有效性的基础数据 |

---

## 后果（Consequences）

### 正面后果

- **消除代码重复**——从 9 个文件中的 `_now_iso()` 收敛到 shared 中的单一实现
- **阻止重复引入**——**Pre-commit GATE-DEDUP Wave 1 即落地**，提交时即拦截，而非事后清理
- **AI 不再重复造轮子**——生成时预防（共享 API 影子清单 + 签名碰撞检测 + 健忘热点强化 + KB 持久化洞察）从源头阻止 AI 重复发明
- **安全提取而非盲提取**——Suitability Score + 不安全模式目录——确保提取到 shared 不会创建比保留重复更重的技术债
- **提升代码一致性**——统一实现而非多重实现，降低 bug 风险（修一处 = 修全部）
- **自动修复减少人工负担**——1 人团队的核心瓶颈是 Owner 时间，安全自动修复 + ROI 排序 + 部分提取直接节省时间
- **进化闭环**——重复模式反馈给 Feedback Loop → evolve() → KB 持久化 → 持续优化 AGENTS.md 共享清单
- **跨 session 记忆传递**——**Wave 1 即落地**Session Log 去重摘要 + KB 持久化，下一个 AI session 零推理消费
- **代码健康可见**——Health Score 0-100 + 引入速率 + 债务预测 + 引擎自观指标——Owner 30 秒判断全貌
- **引擎鲁棒性**——降级运行 + 缓存自愈 + PID 锁——单模块故障不拖垮全局
- **退役友好**——文档化卸载路径，引擎本身不成负担
- **引擎吃自己的狗粮**——定期自扫描 + Codegen覆盖防护 + 依赖自检——引擎自身也不腐化
- **Doom Loop 不失控**——修复升级阶梯（L0-L4）+ 3次失败冻结 + Owner 告警——不会无限修复循环
- **共享函数有生老病死**——5阶段生命周期——不会形成"僵尸函数坟场"
- **Import表面积可控**——SBS 0-100 + 跨层依赖热图 + 提取门槛联动——不会因去重而创造耦合炸弹
- **低测试覆盖也能验证**——行为采样（Stage 0.25）——不依赖测试框架的纯函数验证
- **设计模式被尊重**——Strategy/Adapter/Factory/Template Method/Observer/Decorator 自动豁免
- **冷启动不卡顿**——`--quick-init` 5s 完成首轮扫描 + 进度条提示——首次体验不糟糕
- **Monoculture被看见**——Blast Radius Score 0-100 + 去重悖论显式评估——不会盲目追求"消除所有重复"
- **崩溃不丢状态**——WAL 式原子修复 + 自动崩溃恢复——断电/OOM 后代码库可自动回到一致状态
- **古老重复被尊重**——Grandfather 三定律——引擎安装前的深度纠缠不会被自动修复破坏稳定性
- **漏报不再是黑洞**——Sensitivity Sweep + Canary注入 + 抽样审查——FNR 从不可知变成可追踪、可改善
- **影子清单可信任**——import 存活校验 + 幻觉自动清除 + Trust Score——不会被幻觉函数误导 AI session
- **签名指纹不过期**——Temporal Drift 自动检测 + 重算——Stage 0.5 的有效性随时间不退化
- **引擎自知之明**——Simplicity Audit 月度自审计——SAS 0-100 + 成本效益量化——引擎自己判断是否该退役
- **死模块不堆积**——DEAD 共享模块自动检测 + 删除建议——不会因为 shared/ 膨胀而增加认知负荷
- **提取后不裸奔**——14天稳定观察期（对标 Microsoft SDP）——新 shared 函数的隐藏 bug 有时间暴露
- **恢复不是单点信任**——Recovery-from-Recovery 纯文本 Manifest——即使 tar.gz 损坏也能手动恢复
- **噪声不淹没信号**——主题聚类摘要（50组→3主题）——IEEE TSE 研究的告警疲劳问题被消解
- **信任链升级到行为级**——影子清单的行为正确性验证——从"函数存在"进化到"函数正确"——防止行为漂移
- **并发修改不搞破坏**——Pre-Apply Integrity Gate——修复前重新验证文件完整性——防止修复窗口中外部写入
- **微克隆不再隐身**——n-gram频率计数——AI生成的大量1-2行重复模式被显式聚合——不再因5行门槛而无视系统性碎片化
- **共享函数自带测试**——提取后自动测试生成——BRS从78→48——Monoculture免疫从"理论担忧"变为"可操作缓解"——对标Google Test Certified
- **API契约透明**——三维信任模型——存在性+行为正确性+契约一致性全维可见——影子清单从此不仅是"有哪些函数"而是"这些函数值得信任吗"
- **跨边界连接**——四大边界差异化策略——不同代码区域之间的重复不再是盲区——最高价值的去重被显式发现
- **决策可追溯可回滚**——DecisionFingerprint 不可变追加日志——任何时候都能回答"引擎做了什么、为什么、怎么撤销"——休假/维护模式下的核心信任基础设施
- **AI 从被动等待到主动串联**——主动发现双通道——不等 AI 犯错就告知已有实现——零轮对话摩擦——从"拦截→修正→重写"变成"被告知→直接复用"

### 负面后果 / 权衡

- **AST 分析性能开销**——全量扫描大型代码库耗时（缓解：增量扫描 + 缓存 + 降级运行 + Tier 自适应）
- **误报可能打乱开发节奏**——需要人工确认（缓解：路径感知阈值 + 偏向漏报 + `@intentional-duplicate` + 惯用法豁免 + Owner 决策模式学习）
- **自动修复风险**——自动改代码有引入 bug 的可能（缓解：分批修复 + 全量测试 + verifier.py 多道验证 + ROI 优先低风险组 + Suitability Score 门禁）
- **不是所有重复都该消除**——语义相同但场景不同的重复是合理的（缓解：`@intentional-duplicate` + 高阈值 + confidence scoring + 策略树可配豁免 + 不安全提取模式目录）
- **系统集成复杂度**——与 10+ 系统集成后，任一系统变更可能影响去重引擎（缓解：集成契约 CT-* 文档化 + 单元测试隔离各集成点）
- **22 个模块维护成本**——每个 Python/Tree-sitter/MinHash 升级都可能 break（缓解：维护复杂度分级 + 降级运行 + Self-Benchmark + 依赖版本锁定 + 退役路径）
- **27 个模块维护成本**（v0.6.0）——模块爆炸风险（缓解：分层维护 + 低层模块（sampler/scanner）> 高层模块（fixer/lifecycle）——低层出错影响更大的设计原则）
- **行为采样安全边界**——沙箱执行用户代码永远有风险（缓解：AST 静态副作用检测 + subprocess 隔离 + 白名单模块 + 500ms 超时 + 256MB 限制）
- **SBS 阈值主观性**——max_safe_shared_imports=80 等初始值是经验值，对本项目的适配需实际运行后标定（缓解：W2 用生产数据自适应 + 耦合事件触发自动下调）
- **设计模式白名单覆盖不足**——只覆盖了 6 种常见设计模式（缓解：AST 规则库可扩展 + 允许 Owner 手写自定义规则）
- **33 个模块维护成本**（v0.7.0）——WAL 原子修复 + Grandfather + Monoculture + 漏报盲审等增加 6 个模块——Wave 2 的复杂度进一步上升（缓解：原子性修复是自包含的——崩溃恢复逻辑独立于主流程；Monoculture/漏报盲审是只读的——不修改代码）
- **44 个模块维护成本**（v0.9.0）——新增微克隆检测/测试生成/契约验证/跨边界感知 4 个模块 + 之前积累（缓解：微克隆检测和契约验证是极简模块——纯统计/静态分析、零外部依赖；跨边界检测是配置扩展——主要工作量在边界标签标记；测试生成调用 AI pipeline——本身不实现复杂逻辑——这是给"100% AI 施工"的礼物——AI 做测试生成的工作，Owner 不需要懂测试生成内部实现）
- **46 个模块维护成本**（v0.10.0）——决策审计链+主动发现 2 个模块——共 46 模块（缓解：决策审计链是追加 logger——比任何一个现有 W2 模块都简单；主动发现 <150 行——签名索引 O(1)+语义索引 collections.Counter——零外部依赖 | 这个版本是"最轻增量，最大价值"的范例——两个模块的总智力负担 < 任何一个现有 W2 模块，但解决了 1人+AI 维护场景下 ONLY 2 个仍然悬而未决的核心问题）
- **Monoculture 的矛盾**——去重 vs 爆炸半径是客观矛盾，引擎只能显式报告而不能真正解决——最终仍需 Owner 做安全权衡（缓解：BRS 提供量化依据而非直觉——让 Owner 做 informed decision）
- **Grandfather 可能掩盖真实风险**——化石记录中的重复如果后续被证明是活跃的技术债，等 60 天太久（缓解：第三定律考古测试 = 独立恢复评估——不等时间，等"安全性"）
- **40 个模块维护成本**（v0.8.0）——新增自审计/死模块/观察期/恢复安全网/主题聚类/行为信任/并发防护 7 个模块 → Wave 2 总模块数达到 40（缓解：这 7 个模块多数是"只读型"或"被动触发型"——不像 auto_fixer 直接修改代码——维护风险相对可控）
- **Simplicity Audit 的自我否定悖论**——如果引擎自审计结果建议退役，但退役决策本身需要 Owner 执行——Owner 可能永远不看自审计报告（缓解：SAS < 25 时 Health Score 中直接显示为红色"引擎建议退役"——不可忽视）
- **观察期拖慢修复节奏**——14 天观察窗口意味着去重速度降至每 2 周一批，紧急去重需求被延迟（缓解：Owner 可 CLI `--skip-observation` 跳过观察期——风险自担）
- **44 个模块维护成本**（v0.9.0）——新增微克隆检测/测试生成/契约验证/跨边界感知 4 个模块 → Wave 2 总模块数达到 44（缓解：微克隆检测是极简模块——纯统计逻辑、零外部依赖；测试生成调用 AI pipeline——本身不实现复杂逻辑；契约验证和跨边界检测是只读型——不修改代码）
- **微克隆提取建议的碎片化风险**——建议"提取为 `logging_utils.log_with_classname()`"可能导致 shared/ 目录碎片化为大量极小函数（缓解：微克隆仅建议不自动提取——Owner 决定是否值得；提供聚合建议——"这 5 个微克隆可以合并为同一个 shared helper"）
- **测试生成的维护债务**——自动生成的测试如果函数行为持续变化 → 测试频繁失败 → 比手动测试更干扰（缓解：@auto-generated-by-dedup 标记 + 行为变更时触发测试重生成；连续 2 次测试失败 → 标记函数 UNSTABLE）
- **三维信任模型的复杂度成本**——维护三个维度的 Trust Score 计算器 → 出现信任分数矛盾的场景（存在性和行为正确性通过但契约腐烂 → 该信还是不信？）（缓解：三个维度用加权 Trust Score 归零为单一 0-100 值——Owner 只看最终分数；维度间矛盾 → 自动升级为 needs_review）
- **46 个模块维护成本**（v0.10.0）——新增决策审计链+主动发现 2 个模块（缓解：决策审计链 ≈ 0 复杂度——本质就是个追加 YAML 的 logger；主动发现 < 150 行——签名索引是纯字符串匹配，语义索引是 `collections.Counter` + cosine similarity——两个模块加起来的智力负担 < 任何一个现有 Wave 2 模块）

---

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-06 | 0.10.0 | **决策审计链·主动函数发现**——解决 1人+AI 维护场景下仅剩的 2 个核心运维信任问题：<br>①**§3.29 去重决策审计链**——DecisionFingerprint 不可变追加日志 + 证据包 + 可回滚 + CLI `audit --since`/`audit --rollback`/`audit --verify`——"休假2周回来，知道引擎做了什么、为什么做、怎么撤销"——对标 Google Tricorder/Meta Sapienz/Netflix Staged Rollout——≈0 复杂度（追加 YAML logger）<br>②**§3.30 共享函数主动发现**——签名驱动(Channel A)+语义驱动(Channel B)双通道——不等 AI 犯错、不等 GATE-DEDUP 拦截——AI 生成函数前主动被告知已有实现——从"被动拦截→主动赋能"——对标 Sourcegraph Cody/Google Code Search——<150 行<br>③**检测矩阵 16→18维**：新增决策审计链+主动发现<br>④**生命周期 23→25维**：新增决策审计链+主动发现<br>⑤**风险 43→45**：决策不可追溯/被动等待拦截<br>⑥**开放问题 38→40**：审计日志膨胀/双通道优先级矛盾<br>⑦**模块 44→46**：新增 decision_auditor/function_discovery<br>⑧**Wave 2 扩展**——33天→35天（+2天）+ W2-35~W2-36 两项新任务<br>⑨**数据文件 24→26**：新增 decision_audit_log/function_discovery<br>⑩**46 模块！**但这不是灾难——决策审计链 ≈ 0 复杂度，主动发现 < 150 行——两个模块总智力负担 < 任何现有 W2 模块——这是"最轻增量，最大价值"的范例——Blueprint 在此关闭盲点发现，进入施工阶段 |
| 2026-05-06 | 0.9.0 | **微克隆感知·测试生成·契约验证·跨边界感知**——与专业机构（Google/Meta/JetBrains）及学术界（MSR 2024/ICPC 2023/Google Testing Culture）最后差距弥合：<br>①**§3.25 微型克隆检测**——n-gram频率计数L0/L1/L2三级粒度 + 对标Google Tricorder/JetBrains IntelliJ 2025.1 + Vibe Coding微克隆密度3.8x（MSR 2024） + 微克隆仅检测不自修<br>②**§3.26 提取后自动测试生成**——类型驱动边界测试+执行轨迹金丝雀录制+调用方契约测试 + pytest parametrize + 对标Google Mozart/Test Certified + BRS缓解的落地机制（BRS 78→48）<br>③**§3.27 API契约一致性验证**——存在性+行为正确性+契约一致性三维信任模型 + docstring参数+类型精确度+影子清单描述+异常契约四层校验 + 对标Google Tricorder/Meta Pyre<br>④**§3.28 跨边界克隆感知**——SRC_TEST_BRIDGE/SRC_SCRIPTS_DIVERGENCE/CROSS_LAYER_REDUNDANCY/VENDORED_REIMPLEMENTATION 四大边界差异化策略 + 对标Google Blaze + 跨边界auto_fix比同区域内更保守<br>⑤**检测矩阵 12→16维**：新增微克隆/测试生成/契约一致性/跨边界四个维度<br>⑥**生命周期 19→23维**：新增微克隆检测+测试生成+契约验证+跨边界感知四个维度<br>⑦**风险 39→43**：微克隆泛滥/提取后无测试/契约腐烂/跨边界不可见<br>⑧**开放问题 34→38**：微克隆阈值标定/测试维护成本归属/三维Trust Score聚合/跨边界Wave 1预埋<br>⑨**模块 40→44**：新增micro_clone_detector/auto_test_generator/contract_consistency_checker/cross_boundary_detector<br>⑩**Wave 2 扩展**——29天→33天（+4天）+ W2-31~W2-34 四项新任务<br>⑪**数据文件 20→24**：新增micro_clone_report/auto_test_gen/contract_consistency/cross_boundary_report<br>⑫**标题从"三体最优边界"升级为"四体最优边界"** |
| 2026-05-06 | 0.8.0 | **自审计闭环·递归安全网·噪声信号消解**——终极外部取证审计发现 7 个递归悖论并全部补入：<br>①**§3.18 引擎成本效益自审计**——SAS 0-100 + Simplicity Audit 月度自审 + "33模块引擎自己是否已成为最重的技术债" + NET_NEGATIVE→自动退役建议<br>②**§3.19 死共享模块检测**——ZOMBIE_CANDIDATE/DEAD/GRAVEYARD 三级 + 全函数退役模块自动标记删除——生命周期从函数级扩展到模块级<br>③**§3.20 提取后稳定观察期**——14天观察窗口（对标 Microsoft SDP/Netflix Staged Rollout）+ OBSERVING→resume/ROLLBACK 状态机 + 回归监听<br>④**§3.21 恢复失败的恢复**——R0-R3 四层递归恢复 + R2纯文本Recovery Manifest（base64内容）作为 tar.gz 损坏的最终安全网<br>⑤**§3.22 噪声信号比·主题聚类摘要**——三层加权聚类（前缀30%+AST50%+共现20%）+ 50组→3主题压缩 + IEEE TSE 告警疲劳研究驱动<br>⑥**§3.23 影子清单行为正确性验证**——behavior_signature录制+全量扫描采样验证+行为漂移DIVERGED告警——信任链从"存在性"升级到"行为正确性"<br>⑦**§3.24 并发源文件修改检测**——Pre-Apply Integrity Gate + APPLY前全量SHA256重验证 + ABORT冲突报告 + fix_plan自动重生成<br>⑧**风险 33-39**：引擎成本倒挂 / 死模块积累 / 提取后静默退化 / 恢复故障 / 告警疲劳 / 行为正确性缺失 / 并发写入<br>⑨**开放问题 28-34**：SAS主观性 / 死模块安全边界 / 观察期时长 / Manifest存储 / 聚类准确性 / 采样代表性 / 锁窗口<br>⑩**模块 33→40**：新增 simplicity_auditor / dead_module_detector / observation_window_guard / recovery_manifest_writer / thematic_clusterer / behavioral_trust_checker / pre_apply_integrity_gate<br>⑪**Wave 2 扩展**——21天（+4天）+ W2-24~W2-30 七项新任务<br>⑫**生命周期多维模型更新**：目标从"去重收益 vs Monoculture风险"二体问题升级为"去重收益 vs Monoculture风险 vs 引擎维护成本"三体最优边界 |
| 2026-05-05 | 0.7.0 | **Monoculture免疫·原子修复·漏报可视·全生命周期治理**——终极外部取证审计发现 6 个根本性悖论并全部补入：<br>①**§3.12 Monoculture免疫**——Blast Radius Score 0-100 + 去重成功的悖论（消除重复=所有caller共享同一bug=爆炸半径增大N倍——分散重复是天然的blast radius隔离）<br>②**§3.13 Grandfather三定律**——≥30天古老重复永不自动修复 + ≥60天化石记录（降为informational不参与Health Score）+ 第三定律考古测试（caller独立测试+rollback plan → 否则拒绝提取）<br>③**§3.14 原子性修复**——WAL式PREFLIGHT→CHECKPOINT→APPLY→RECOVER + 崩溃自动恢复（引擎重启扫描fix_checkpoint_*.tar.gz→恢复原始文件）<br>④**§3.15 漏报盲审**——三层机制：L1 Sensitivity Sweep（降低阈值+diff）+ L2 Canary注入（5-10组·FNR可量化）+ L3 Sampled Human Audit（每周10组随机审查·反馈驱动改善）<br>⑤**§3.16 Shadow Manifest信任链**——import存活校验（`python -c "from shared.xxx import func"`）+ 幻觉自动清除 + spot-check + Trust Score（< 90%→拒绝注入+降级"无清单模式"）<br>⑥**§3.17 Temporal Signature Drift**——类型演化（`Optional[str]`→`str`→`float\|None`）自动检测 + 连续3次不同→UNSTABLE→Stage 0.5 skip + unstable_ratio全局退化监控<br>⑦**风险 27-32**：Monoculture灾难 / 古老考古 / 代码库损坏 / 系统性漏报 / 影子幻觉 / 时态退化<br>⑧**开放问题 23-27**：最优爆炸边界 / 化石重新激活 / checkpoint磁盘 / Canary更新频率 / Stage 0.5全局退化<br>⑨**模块 27→33**：新增 monoculture_guard / atomic_fixer / grandfather_manager / false_negative_auditor / shadow_trust_validator / temporal_drift_tracker<br>⑩**Wave 2 扩展**——17天（+4天）+ W2-18~W2-23 六项新任务<br>⑪**生命周期扩至 12 维**：新增 Monoculture免疫 + 原子修复保障 + 古老重复管理 + 漏报盲审 + 影子信任链 + 时态签名维护 |
| 2026-05-05 | 0.6.0 | **自保护·防Doom Loop·全生命周期治理**——第三轮深度审计发现 17 个新盲点并全部补入：<br>①**§3.8 引擎自保护与Dogfooding**——三层机制：L1引擎自扫描（Wave 1）、L2 Codegen覆盖防护（Wave 1）、L3引擎依赖自检<br>②**CodegenFix Manifest**（`codegen_fix_manifest.json`）——所有层`__init__.py` SHA256哈希白名单 + 覆盖自动检测 + 修复 diff 一键应用<br>③**§3.9 Doom Loop 防护**——修复升级阶梯（L0 Direct Fix→L1 Partial Fix→L2 Retry Once→L3 Escalate→L4 Stop+Alert）+ `doom_loop_freeze_list.json` 冻结机制<br>④**§3.10 共享函数生命周期管理**——5阶段状态机（Active→Deprecated→Grace Period→Sunset→Retired）+ 迁移 diff 自动生成 + 影子清单同步降级<br>⑤**Deprecated 冷规则**——进入 Deprecated 状态的函数不再推荐给新 AI session（影子清单降级）——防止AI继续生成废弃函数<br>⑥**§3.11 Import表面积负债追踪**——Shared Burden Score（SBS）0-100 + 跨层依赖热图 + shared 分拆建议 + 提取门槛联动（SBS≥31→Suitability≥70）<br>⑦**Stage 0.25 行为采样验证**（`behavioral_sampler.py`）——类型注解推断采样输入→沙箱子进程执行→输出 diff 比对→副作用 AST 静态检测——低测试覆盖项目的安全网<br>⑧**设计模式白名单**——6种模式AST规则（Strategy/Adapter/Factory/Template Method/Observer/Decorator/`@wraps`Wrapper）自动豁免<br>⑨**引擎冷启动体验**——`--quick-init` CLI标志（5s完成仅签名扫描）+ 进度条 + 预估时间提示<br>⑩**多Session去重状态机**设计路径（检测→修复→修复中断→恢复——状态一致性保障）<br>⑪**跨AI工具影子清单适配**架构路径（统一YAML → Claude/GPT-5/Gemini adapter）<br>⑫**LLM跨文化偏倚**识别——中文命名函数Stage 3可靠性需实际测试后验证<br>⑬**去重幂等性深度**——MinHash概率性→确定性哈希+缓存签名+版本锁定+Stage全链哈希保证<br>⑭**风险 20-26**：引擎自腐 / Codegen覆盖 / Doom Loop / 生命周期失控 / Import黑洞 / 低测试验证 / 冷启动延迟<br>⑮**开放问题 18-22**：行为采样安全边界 / SBS阈值标定 / 冻结解冻责任 / 跨AI适配 / LLM中文偏倚<br>⑯**模块 22→27**：新增 behavioral_sampler / self_scanner / shared_lifecycle_manager / import_surface_tracker / doom_loop_guard<br>⑰**测试用例 25→30条**：新增 test_behavioral_sampler + 行为采样安全边界用例
| 2026-05-05 | 0.5.0 | **安全提取+规模自适应+债务规划**——第二轮深度审计发现 12 个新盲点并全部补入：<br>①§3.6 **安全提取适配性评估**（Suitability Score 0-100 + 7维评估 + 4档verdict）——防止盲提取创建更重技术债<br>②§3.6 **不安全提取模式目录**——7类模式 NEVER auto-extract（高调用方/平台代码/公开API/性能热点/生成代码/Vendored/stub）<br>③§3.6 **部分共享提取**计划——LCS 公共核心60%→shared + 差异化40%保留各调用方<br>④§3.7 **项目规模感知**四 Tier 自适应阈值（Tier1<5000行偏漏报→Tier4>50000行激进拦截）——应对"5000行魔咒"<br>⑤§3.4 **引擎自观指标**（FPR/检测延迟/修复成功率/缓存命中率/扫描耗时）——调试引擎自身<br>⑥§3.4 **重复引入速率**追踪——新重复/周暴露 Prevent 阶段是否失效<br>⑦§3.4 **去重债务预测**——`debt_projector.py`："以当前速率 N 周可还清"<br>⑧**过期共享函数检测**（`stale_shared_detector.py`）——签名漂移+调用参数匹配告警<br>⑨**Knowledge Base 持久化**（`depends_on` MOD-INF-012）——引擎发现→KB存储→未来AI主动查阅<br>⑩**退役/卸载路径**文档化——引擎月度维护>2h持续3月→触发退役评估<br>⑪修复§5文本bug（"四档"→"五档"）<br>⑫二/三波容量扩容——Wave2 9→11天 / Wave3 6→7天 / 模块 19→22 / 风险 13→19 / 开放问题 12→17 |
| 2026-05-05 | 0.4.0 | **代码健康平台升级**——从"全生命周期去重系统"升级为"代码健康平台"：<br>①**盲点补全**——补入 v0.3.0 审计发现的 17 个盲点<br>②**致命盲点前移**——GATE-DEDUP 阻断 / Session Log 交接 / Health Score 仪表盘从 Wave 3 → Wave 1<br>③**Stage 0.5 签名指纹匹配**——新增签名碰撞检测流水线：O(1)精确匹配 SHA256[:12]——Vibe Coding 性价比最高的防线<br>④**降级运行模式**（degradation.py）——各 Stage 独立 try/except，AST 失败 → 降级到 Token 级，LLM 不可用 → 完全不阻塞<br>⑤**代码块级去重**——滑动窗口 MinHash（min_block_size=5 行）——import块/异常模板/配置逻辑去重<br>⑥**Python 惯用法自动豁免**（IDIOM_WHITELIST）——`__init__`/`__repr__`/`@property`/`@overload`/ABC 骨架<br>⑦**Owner 决策模式学习**——`@intentional-duplicate` 标记后，引擎学习模式并自动 suppress 同类<br>⑧**AI 健忘热点追踪**（hotspot_tracker.py）——按函数名前缀聚类 + 重复趋势 + 影子清单强化建议<br>⑨**影子清单消费验证回环**（shadow_verifier.py）——检测新重复 vs 影子清单 → 反馈"清单已声明但 AI 未读"→ 优化格式<br>⑩**缓存自愈机制**——`_integrity` SHA256 校验 + 原子写入（`.tmp`→`os.replace`）+ 损坏自动重建<br>⑪**代码健康仪表盘**（health_monitor.py）——Dedup Health Score 0-100 + 趋势 ↑↓→ + 健忘热点 Top3<br>⑫**去重 ROI 评估**（prioritizer.py 的 roi_factor）——修前评估"节省代码行数/(改动文件数×风险系数)"<br>⑬**单文件快速检查**（`--file PATH`）——Session 内轻量拦截，不依赖 commit<br>⑭**退出码五档化**（新增 exit code 4 DEGRADED）——降级运行完成但部分 Stage 未执行<br>⑮**专业对标升级**——Kythe 符号索引教训 + Glean 函数粒度增量 + SonarQube 最小克隆长度<br>⑯**风险评估扩充**（8→13 项）——Tree-sitter 漂移 / 缓存损坏 / Kill Switch 风暴 / Vibe Coding 创造性漂移 / 引擎自维护成本<br>⑰**开放问题扩充**（7→12 项）——惯用法豁免完整性 / 策略树复杂度边界 / Symbol Index 完整度 / Session Log 粒度 / 影子清单三层注入<br>⑱**策略树 YAML 设计**（Wave 3）——条件→动作映射，Owner/AI 可改 YAML 不碰 Python<br>⑲**Self-Benchmark**（Wave 3）——全量扫描后 5 组已知对自验证 → 引擎退化告警<br>⑳**渐进式三层记忆注入**（Wave 3）——热/领域/冷规则分 token 预算——对齐 AGENTS.md §8<br>㉑**模块数 14→19**：新增 signature_matcher / health_monitor / hotspot_tracker / shadow_verifier / degradation / symbol_index；测试文件 4→6 |
| 2026-05-05 | 0.3.0 | **重大升级**——从事后检测工具升级为全生命周期去重系统：<br>①新增六阶段全生命周期模型（Prevent→Block→Audit→Fix→Register→Evolve）<br>②新增 Stage 0 缓存预热 + 增量扫描设计（`function_cache.json` + `diff_detector.py`）<br>③新增 10 维检测矩阵（部分重复 + 重排序容忍 + 参数化模板 + 非函数结构 + 配置文件去重）<br>④新增自动修复引擎 + 去重后验证 + 分批安全机制<br>⑤新增 SSoT 注册闭环（去重→提取→注册 b_shared.yaml）<br>⑥新增退出码标准化（0/1/2/3 对齐 MOD-INF-005）<br>⑦新增优先排序算法 + 置信度评分<br>⑧新增与 6 大系统的深度集成契约（Context/Gate/Shared/FLE/Task/SessionLog）<br>⑨新增 @intentional-duplicate 标记机制<br>⑩新增共享 API 影子清单——生成时预防的核心数据<br>⑪模块数从 6→14，新增 `cache_manager` / `diff_detector` / `auto_fixer` / `ssot_registrar` / `prioritizer` / `annotations` / `verifier` / `config`<br>⑫实施路线从单轨→三波递进（Wave 1 5天 / Wave 2 7天 / Wave 3 5天）<br>⑬新增 evolve() 进化信号 + Session Log 跨 session 记忆传递<br>⑭新增路径感知阈值（shared 0.3 / core 0.6 / * 0.7 / tests 0.9）<br>⑮新增 idempotency 保证 + 性能降级策略 |
| 2026-05-05 | 0.2.0 | 补全标准模板四项：产出物存放目录 + 集成目标 + 需要更新的相关内容 + 后果 |
| 2026-05-02 | 0.1.0 | 初始创建——事后检测三阶段流水线（Token → AST → LLM）|

---

## 1. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。

### 1.1 源码文件（40 模块：Wave 1 14个 + Wave 2 24个 + Wave 3 2个）

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/l01_infrastructure/code_dedup_engine/__init__.py` | ⬜ 待施工 | 包初始化+模块职责声明（AI自描述） |
| `src/zephyr/l01_infrastructure/code_dedup_engine/cache_manager.py` | ⬜ 待施工 | Wave 1——缓存管理（_integrity+原子写入+自愈） |
| `src/zephyr/l01_infrastructure/code_dedup_engine/diff_detector.py` | ⬜ 待施工 | Wave 1——增量变更检测（函数粒度） |
| `src/zephyr/l01_infrastructure/code_dedup_engine/signature_matcher.py` | ⬜ 待施工 | Wave 1——Stage 0.5 签名碰撞检测 |
| `src/zephyr/l01_infrastructure/code_dedup_engine/scanner.py` | ⬜ 待施工 | Wave 1——Token扫描+代码块级去重 |
| `src/zephyr/l01_infrastructure/code_dedup_engine/degradation.py` | ⬜ 待施工 | Wave 1——降级运行管理 |
| `src/zephyr/l01_infrastructure/code_dedup_engine/config.py` | ⬜ 待施工 | Wave 1——配置+惯用法豁免 |
| `src/zephyr/l01_infrastructure/code_dedup_engine/report.py` | ⬜ 待施工 | Wave 1——报告+五档退出码 |
| `src/zephyr/l01_infrastructure/code_dedup_engine/prioritizer.py` | ⬜ 待施工 | Wave 1——优先级排序（含ROI） |
| `src/zephyr/l01_infrastructure/code_dedup_engine/annotations.py` | ⬜ 待施工 | Wave 1——标记解析+决策学习 |
| `src/zephyr/l01_infrastructure/code_dedup_engine/health_monitor.py` | ⬜ 待施工 | Wave 1——健康仪表盘+Session Log+SBS聚合 |
| `src/zephyr/l01_infrastructure/code_dedup_engine/behavioral_sampler.py` | ⬜ 待施工 | Wave 1——Stage 0.25 行为采样验证 |
| `src/zephyr/l01_infrastructure/code_dedup_engine/self_scanner.py` | ⬜ 待施工 | Wave 1——引擎自保护(自扫描+Codegen防护+依赖自检) |
| — | — | — |
| `src/zephyr/l01_infrastructure/code_dedup_engine/ast_comparator.py` | ⬜ 待施工 | Wave 2——AST比对 |
| `src/zephyr/l01_infrastructure/code_dedup_engine/symbol_index.py` | ⬜ 待施工 | Wave 2——轻量符号索引 |
| `src/zephyr/l01_infrastructure/code_dedup_engine/hotspot_tracker.py` | ⬜ 待施工 | Wave 2——AI健忘热点 |
| `src/zephyr/l01_infrastructure/code_dedup_engine/shadow_verifier.py` | ⬜ 待施工 | Wave 2——影子清单验证 |
| `src/zephyr/l01_infrastructure/code_dedup_engine/auto_fixer.py` | ⬜ 待施工 | Wave 2——自动修复引擎 |
| `src/zephyr/l01_infrastructure/code_dedup_engine/verifier.py` | ⬜ 待施工 | Wave 2——修复后验证 |
| `src/zephyr/l01_infrastructure/code_dedup_engine/ssot_registrar.py` | ⬜ 待施工 | Wave 2——SSoT注册+KB持久化 |
| `src/zephyr/l01_infrastructure/code_dedup_engine/extraction_safety.py` | ⬜ 待施工 | Wave 2——安全提取评估(Suitability Score) |
| `src/zephyr/l01_infrastructure/code_dedup_engine/stale_shared_detector.py` | ⬜ 待施工 | Wave 2——过期共享函数检测 |
| `src/zephyr/l01_infrastructure/code_dedup_engine/debt_projector.py` | ⬜ 待施工 | Wave 2——去重债务预测 |
| `src/zephyr/l01_infrastructure/code_dedup_engine/doom_loop_guard.py` | ⬜ 待施工 | Wave 2——Doom Loop防护(升级阶梯+冻结) |
| `src/zephyr/l01_infrastructure/code_dedup_engine/shared_lifecycle_manager.py` | ⬜ 待施工 | Wave 2——共享生命周期管理(5阶段) |
| `src/zephyr/l01_infrastructure/code_dedup_engine/import_surface_tracker.py` | ⬜ 待施工 | Wave 2——Import负债追踪(SBS+热图) |
| `src/zephyr/l01_infrastructure/code_dedup_engine/monoculture_guard.py` | ⬜ 待施工 | Wave 2——Monoculture免疫(BRS+去重悖论) |
| `src/zephyr/l01_infrastructure/code_dedup_engine/atomic_fixer.py` | ⬜ 待施工 | Wave 2——原子性修复(WAL+CHECKPOINT+崩溃恢复) |
| `src/zephyr/l01_infrastructure/code_dedup_engine/grandfather_manager.py` | ⬜ 待施工 | Wave 2——Grandfather三定律(古老重复+化石+考古) |
| `src/zephyr/l01_infrastructure/code_dedup_engine/false_negative_auditor.py` | ⬜ 待施工 | Wave 2——漏报盲审(Sweep+Canary+抽样审查) |
| `src/zephyr/l01_infrastructure/code_dedup_engine/shadow_trust_validator.py` | ⬜ 待施工 | Wave 2——影子清单信任链(import校验+幻觉清除) |
| `src/zephyr/l01_infrastructure/code_dedup_engine/temporal_drift_tracker.py` | ⬜ 待施工 | Wave 2——签名时态漂移(指纹演化+UNSTABLE+自动重算) |
| `src/zephyr/l01_infrastructure/code_dedup_engine/simplicity_auditor.py` | ⬜ 待施工 | Wave 2——引擎成本效益自审计(SAS+净收益+退役建议) |
| `src/zephyr/l01_infrastructure/code_dedup_engine/dead_module_detector.py` | ⬜ 待施工 | Wave 2——死共享模块检测(ZOMBIE/DEAD/GRAVEYARD) |
| `src/zephyr/l01_infrastructure/code_dedup_engine/observation_window_guard.py` | ⬜ 待施工 | Wave 2——提取后稳定观察期(14天OBSERVING+回滚) |
| `src/zephyr/l01_infrastructure/code_dedup_engine/recovery_manifest_writer.py` | ⬜ 待施工 | Wave 2——恢复失败的恢复(R2纯文本Manifest+R0-R3四层) |
| `src/zephyr/l01_infrastructure/code_dedup_engine/thematic_clusterer.py` | ⬜ 待施工 | Wave 2——噪声信号比·主题聚类(三层加权+Executive Summary) |
| `src/zephyr/l01_infrastructure/code_dedup_engine/behavioral_trust_checker.py` | ⬜ 待施工 | Wave 2——影子清单行为正确性(behavior_signature+漂移检测) |
| `src/zephyr/l01_infrastructure/code_dedup_engine/pre_apply_integrity_gate.py` | ⬜ 待施工 | Wave 2——并发修改检测(Pre-Apply SHA256+冲突报告) |
| `src/zephyr/l01_infrastructure/code_dedup_engine/semantic_verifier.py` | ⬜ 待施工 | Wave 3——LLM语义验证 |

### 1.2 CLI 脚本

| 脚本路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `scripts/governance/d1_structure/detect_code_duplicates.py` | ⬜ 待施工 | CLI 入口——Wave 1（含`--quick-init`冷启动加速） |
| `scripts/governance/d1_structure/fix_code_duplicates.py` | ⬜ 待施工 | CLI 自动修复入口——Wave 2 |

### 1.3 测试文件

| 测试路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/unit/test_code_dedup.py` | ⬜ 待施工 | 单元测试：扫描器+比对器——Wave 1 |
| `tests/unit/test_signature_matcher.py` | ⬜ 待施工 | 单元测试：签名碰撞检测——Wave 1 |
| `tests/unit/test_degradation.py` | ⬜ 待施工 | 单元测试：各Stage降级场景——Wave 1 |
| `tests/unit/test_cache_manager.py` | ⬜ 待施工 | 单元测试：缓存_integrity+自愈——Wave 1 |
| `tests/unit/test_behavioral_sampler.py` | ⬜ 待施工 | 单元测试：行为采样+安全边界——Wave 1 |
| `tests/unit/test_auto_fixer.py` | ⬜ 待施工 | 单元测试：自动修复+回滚——Wave 2 |
| `tests/unit/test_verifier.py` | ⬜ 待施工 | 单元测试：去重后验证——Wave 2 |

### 1.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §1 已实现代码索引 → 知道「哪些已实现、在哪里」
2. 读 §4 模块结构 → 知道「每个模块的职责和 AI 自治权限」
3. 读 §6 实施路线 → 知道「当前在哪个 Wave、下一步该做什么」
4. 读 §7 系统集成 → 知道「与哪些系统有集成契约、数据怎么流」
5. 读 §11 施工指引 → 知道「第一步该创建哪些文件」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\`
- 源码在 `src/zephyr/l01_infrastructure/code_dedup_engine/` 下
- CLI 脚本在 `scripts/governance/d1_structure/` 下
- 测试在 `tests/unit/` 下
- 缓存数据在 `data/cache/` 下（`.gitignore`）
- 配置在 `config/` 下
