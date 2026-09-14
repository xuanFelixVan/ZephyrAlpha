---
ttl: task_bound
completes_when: P0 三项工程（队列转正/own-scope 第三批/死信详情回写）已 commit 且 ARCH-310 登记 in_progress；P1/P2 项由后续班次按本报告 §五施工方案接续
---

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：阴性/审查结论类（C-3 保留至季度末）。处置=**保留**。**
>
> **✅ 已完成（1 条，摘录）**
> - L61: **P0（本次已施工）**：
>
> **⚠️ 未完成**：无待办信号
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 0 个，其中判废弃 0、路径漂移 0）+ commit 提及 0 处。
>
> **处置建议**：保留。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）






# AI 原生治理体系战略评审（100% AI 开发场景）

日期：2026-09-12 ｜ 会话：st-govreform-20260912
触发：并发提交抢锁事故（4 会话 35 分钟零落地）+ Owner 要求从第一性原理做长远期战略评审并全面开工
议题：#ARCH-310 ｜ 本文档=该议题的报告真源

---

## 一、治理资产负债表（实测 2026-09-12）

| 资产 | 数量 | 备注 |
|------|------|------|
| 业务代码 | 3,509 个 .py 模块 | 被治理对象 |
| commit gate | 112 文件 / 446 priority 标记 + 68 pre-commit hooks | |
| 规则文件 | 86 个 yaml / 33,380 行 | trae_001~086 |
| 注册表 | 76 个（ROOR 确认） | 含 49 个对齐注册表 |
| reconciler | 154 处注册 | |
| 架构议题 | 751 个 #ARCH-XXX（本议题=310） | |
| SOP | 16 份（主 SOP 1,037 行 / 15 强制步骤） | |
| 宪法 AGENTS.md | 1,639 行 | 每会话冷启动必读 |

运行时实测：单次提交占全局锁 ≥221s 上限 14min；git_commit.py 20 flag 中 8 个逃生通道默认可用（allow_overlap 曾 62 次超阈）；commit_queue 建成但 commit_queue_interactive 原 OFF（本次转 ON）；session_worktree 被普遍绕过（--allow-non-worktree 成事实惯例）。治理文档自身失治实证：主 SOP 13vs15 内部矛盾 / perf plan §3 与总账冲突 / alignment_checklist 11 天 5 版 3 次计数改名。**结论：元治理成本已与业务开发同量级。**

## 二、第一性原理：100% AI 开发五约束

1. **会话无记忆** → 记忆必须外化（depgraph/registry 体系是正确答案，已做）。
2. **注意力有限** → context 填满性能退化（Anthropic 官方）；规范总量与单条执行率负相关，规范注入有硬预算。
3. **并发无社交协调** → 协调必须机制化；依赖"自觉"的条款在并发压力下必然失守（昨晚 4 家绕过队列硬冲实证）。
4. **产出并行∞/集成串行有限** → 集成吞吐量是系统真瓶颈（"PR volume stops tracking headcount, but merge throughput still does"）。
5. **治理本身是 AI 写的代码** → 无预算与退役机制则无限膨胀，直至元治理追平业务。

## 三、业界三方对照

- **Agentic 社区（2026 共识）**：one agent=one worktree=one branch；非 git 共享态（DB/端口/env）才是最常见碰撞点；批量 merge queue 验证 rebase 后组合状态、最终合入 human-gated；merge 吞吐是新瓶颈，扩队列容量而非 agent 数。
- **量化机构**：Jane Street=类型系统做治理（编译器是最强 gate，研究生产同语言统一）；Two Sigma=VATS monorepo+global incrementality（验证成本随变更集而非仓库规模缩放）。
- **SDD/vibe coding 社区**：无 guardrails 时 AI 债务加速（Info-Tech）；耐久性=状态外部化到文件+自动质量防线+CLAUDE.md 上下文预算。项目外部化领先，**上下文预算是最大欠账**。

## 四、六个结构性诊断

- **D1** 共享工作区模型与并发本质矛盾（worktree 激励不相容：成本即时、收益仅在并发时兑现 → 每次被理性绕过）。
- **D2** 门禁作用域错配：全暂存区扫描使外来违规文件阻断所有提交人（事故实证）。
- **D3** 集成层未队列化：--wait 语义是"原地空转抢锁"而非"排队"。
- **D4** 宪法膨胀：1,639 行+33,380 行规则远超会话可靠吸收能力；"再加一条规则"的条件反射本身已成违规之源。
- **D5** 逃生通道通胀：8 个 flag 默认可用，阻断强度实际取决于 AI 自觉；fail-open/fail-closed 语义不统一。
- **D6** 验证非增量：106 gate 全量跑，gate_cache 刚转正覆盖低。

## 五、五裁定与施工方案

**裁定**（详见 #ARCH-310 adjudication 字段）：
- **R1** 队列是正门，锁降级为队列内部实现（AI 接口只有 enqueue）。
- **R2** 门禁默认 own-diff 作用域，全仓扫描是须登记的例外。
- **R3** 宪法分层：L0 ≤300 行硬规则+索引卡，全文下沉渐进披露（复用 capability_cards L0-L3）。
- **R4** 治理元预算：gate 注册表化+触发率退役审计+新增规则须声明替代（净零增长）。
- **R5** 人机门位模型化：高风险域（交易核心/数据写入/门禁自身/注册表）human-gate，低风险全自动。

**P0（本次已施工）**：
1. `commit_queue_interactive` flag 转 ON + git_commit.py LOCK_TIMEOUT 自动改道入队（--no-auto-enqueue 逃生保留）。
2. DATETIME-NOW-FORBIDDEN gate own-scope 第三批（#ARCH-GATE-OWN-SCOPE-001 模式，+3 测试 44/44 绿）；ERRCODE 经评估豁免（触发已按 own files 收窄，本体=注册表↔全库结构对账，属 §2.6 结构校验型 own-scope 不适用，记录在案）。
3. landing 死信阻断详情 400→2000 字符（AI requeue 可读全量病灶）。
4. watchdog 活跃 claim 豁免：核实已有（verdict=claimed 只审计不告警），残余误报=写入方未 claim 的纪律缺口，不改码，记入议题。

**P1（待排后续班次）**：gate 注册表单一真源 / AGENTS.md 瘦身 L0≤300 行+索引卡 / 风险分级注册表 / ERRCODE 进 gate_result_cache 白名单（输入面分析后）。
**P2（季度）**：worktree 零摩擦化（WorktreePool 常备+merge 自动处置）/ 增量验证全覆盖 / 文档纪律类型化前移。

**全局验收指标**：并发 6 会话全落地 <30min（事故基线 35min 零落地）；foreign_staged 连坐审计趋零；冷启动必读 ≤300 行；规则/gate 净增长 ≤0。
