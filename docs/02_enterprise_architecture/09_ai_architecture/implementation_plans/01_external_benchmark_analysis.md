---
ttl: permanent
doc_type: architecture_view
title: AI 架构外部对标分析
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.5.1"
date: 2026-08-17
topic: ai_external_benchmark
scope: 09_ai_architecture
---

# AI 架构外部对标分析（External Benchmark Analysis）

> **本文定位**：信息库——汇总外部顶级框架的详细分析、与场内设计资产的对照、模块工厂落地性评估。本文是**外部对标的唯一真源**（00_index.md §2 只保留一句话速览表）。
>
> **与其他文件的分工**：结构设计见 [00_index.md](00_index.md)，盘点见 [02_design_asset_inventory.md](02_design_asset_inventory.md)。
>
> **更新策略**：外部框架持续涌现，本文需定期更新（建议每季度搜索一次最新进展）。新框架加入「前沿演进方向」（§7.2）或各框架「考虑过的替代方案」节，不直接替换已定决策；已定决策修订需升版本+记理由。
>
> **核验纪律**：文中标注「2026-08-17 复核」的事实均经当日 WebSearch 核实（来源见 §9 参考来源）；标注「实测」的代码事实均经当日 LS/Glob 验证（验证命令随文给出）。

---

## 一、结论先行

**当前 AI 员工体系（四件套）解决的是"AI 怎么管"（组织架构）。** 但项目并非缺少"AI 怎么进化"的设计——自反Agent（Actor-Evaluator-SelfReflection）和元学习系统（S6 层）已设计了完整的自我进化体系，只是尚未施工到代码。

四件套清单：

| 组件 | 状态 | 解决什么问题 |
|------|------|-------------|
| 三层 AI 工作分配（L1/L2/L3） | 活跃 | AI 算力成本优化排班 |
| 模型岗位矩阵（6岗位×A-F） | 活跃·骨架 | AI 能力分级与岗位匹配 |
| AI 自治等级（L0-L3） | 活跃 | AI 权限边界 |
| AI 员工花名册（预留） | Stage K 未激活 | AI 组织化运营 |

**自我进化设计已有，缺的是施工**：

| 外部对标发现的"缺失" | 场内已有等价设计 | 施工状态 |
|---------------------|-----------------|---------|
| 证据保留→迭代引导闭环 (AQuA) | 元学习层 + 证据关联（假设→证据链：支持/反驳/中性） | 设计完成，未施工 |
| 技能自进化/可写运行时 (Hermes) | AutoSkill 自动技能发现 + Voyager 技能库 + 技能三元组 | 设计完成，已有大量代码（见 §1.2 盘点） |
| 动态模型路由 Q-learning (Qualixar) | LLM Agent 路由（级联控制器 3 阶段：本地/API 分时分任务） | 设计完成，静态路由+画像链路已有代码（见 §1.2） |
| 意图→任务自动分解 (Agentic Engineering) | Phase 0→3 分阶段路线（手动→半自动→全自动→自我进化） | 设计完成，未施工 |
| 数学反思闭环 (TiMi) | 自反Agent：Actor→Evaluator→SelfReflection + L1/L2/L3 三级反思 + PreFlect 前瞻反思 + Agent-R 实时反思 + ReflCtrl 频率控制 | 设计完成，未施工 |
| 信号→代码→评估闭环 (NeMo) | 模块创建（代码生成+AST沙箱）→试运行（回测+模拟）→元学习反馈 | 设计完成，未施工 |
| Goodhart 检测 (Qualixar) | 可解释性门控 + Agent漂移检测 + 群集行为风险防护 | 设计完成，漂移检测已有代码（见 §1.2） |
| RL 端到端策略训练 (AlphaQuanter) | MAML 快速适应 + 在线EWC防遗忘 + ICL元学习 | 设计完成，未施工 |

> 施工状态真源是 [02_design_asset_inventory.md](02_design_asset_inventory.md)；本表只做对标映射，2026-08-17 代码扫描显示技能库/画像链路/漂移检测已有实质代码（§1.2），上表相应行已据此修正。

**核心发现**：模块工厂（Module Factory）被评为"⭐⭐ 核心独创"——没有任何已公开系统有此概念。模块工厂是因子工厂/信号工厂/策略工厂/模型工厂的"上游供应商"，管理"从知识到模块的创建过程"，这是 ZephyrAlpha 的独特创新。

### 1.1 项目处境（2026-08-17 快照）

- **已有分析框架**：12 个外部框架/范式（量化社区 5 + Vibe Coding 3 + GitHub 开源 4，其中 Swarm 兼列机构实践）+ 2 个机构实践（Man Group / Balyasny·Millennium），本次填充前均为"速览+简表"深度。
- **代码侧**：AI 自我进化相关代码集中在 `src/zephyr/autonomy_core/`（113 个 .py，递归实测）与 `src/zephyr/intelligence/`（43 个 .py，递归实测）两大包——**技能库与模型画像两条链路已有大量代码，但证据关联、自反Agent、模块工厂仍无对应实现**。
- **外部侧**：2026 年 Q2~Q3 量化研究 Agent 进入"闭环商品化"阶段（AQuA 论文 2026-08-13 挂网、NeMo 蓝图 2026-05-21 发布、Hermes 突破 228k stars），外部演进速度验证了本项目自我进化层方向的正确性，也抬高了"不施工就落后"的机会成本。

### 1.2 对标相关已施工设施盘点（2026-08-17 实测）

> 仅登记与外部对标直接相关的设施存在性（验证命令：`Get-ChildItem <path> -Filter *.py -File [-Recurse] | Measure-Object`）；功能成熟度与完整资产清单以 [02_design_asset_inventory.md](02_design_asset_inventory.md) 为真源。

| 类别 | 路径/位置 | 内容简述 | 状态 | 对应外部框架 |
|------|-----------|---------|------|-------------|
| 技能库 | `src/zephyr/autonomy_core/skills/` | 58 个 .py（skill_factory / skill_constructor / skill_discovery / skill_registry / skill_evaluator / skill_executor / skill_router / skill_sandbox / skill_gitops / skill_learning / skill_model_evolution / skill_postmortem / skill_freshness / skill_kill_switch 等）+ 2 个子目录 | 存在性已实测 | Hermes 可写运行时/技能系统（§4.2） |
| 上下文引擎 | `src/zephyr/autonomy_core/context/` | 39 个 .py（context_assembler / context_injector / memory_bank / vector_bridge / curation_loop / shadow_canary 等；渐进披露注入器在包根） | 存在性已实测 | Agentic Engineering 协作生成层·上下文（§3.2）；Hermes 渐进披露加载（§4.2） |
| 自我进化门控 | `src/zephyr/autonomy_core/` 包根 | self_evolution_fidelity_gate.py / phase_planner.py / spec_engine.py / prompt_registry.py / trigger_router.py 等 | 存在性已实测 | Agentic Engineering 工程保障层（§3.2） |
| 模型画像/考试/护照 | `src/zephyr/intelligence/model_profiling/` | 24 个 .py（profiler / exam_orchestrator(68KB) / exam_test_cases(126KB) / exam_judge / exam_rubric / capability_passport / job_matcher / task_model_learner / model_discovery / benchmark_suite 等） | 存在性已实测 | Qualixar 路由的"静态画像前置"（§4.3）；NeMo 评估 Agent 门控思想（§2.2） |
| 模型评估/记忆 | `src/zephyr/intelligence/model_evaluation/` | 11 个 .py（unified_memory_api / reranker / default_inference_engine / activate / _memory_backend 等） | 存在性已实测 | Hermes 五层记忆的场内对应（§4.2） |
| 漂移检测 | `src/zephyr/intelligence/model_drift_detector.py` | 模型漂移检测单文件 | 存在性已实测 | Qualixar JSD 漂移监控的邻近能力（§4.3） |

### 1.3 核心问题与对标深度分级

**核心问题**：14 个外部框架/实践，哪些值得逐段深度对标，哪些只需一句话？判定基准是对本项目硬约束（1 人全栈 + 单机 RTX 3090 + miniQMT T+1 + 无集群，见 [system_charter.md](../../04_architecture_principles_decisions/system_charter.md) §2）的**可迁移性**：

| 深度 | 框架 | 分级理由 |
|------|------|---------|
| **深度对标**（逐段分析+映射+替代方案） | AQuA / NeMo / TiMi / Hermes / Qualixar / Agentic Engineering | 与 AI 自我进化层四大组件（证据关联/技能库/模型路由/自反Agent）及 Phase 路线直接映射，单机个人可借鉴 |
| **中度对标**（一段分析+映射） | AlphaQuanter / VibeDev / 受约束 Vibe Coding(Zenera) / claude-flow / CrewAI / Man Group / Balyasny·Millennium | 有单点启示（RL 奖励/治理/Meta Agent/目标分解/中心化复用），但整体不可直接迁移 |
| **浅度对标**（速览+边界标注） | AI Agent Swarm | 机构级终局形态，超出个人约束，仅作"不做什么"的校准参照 |

---

## 二、量化社区与机构实践顶级框架

### 2.1 AQuA（Princeton，2026-08）

> 递归自我改进量化交易研究 Agent——**目前最接近"AI 自我迭代"的学术实现**。

| 维度 | 内容 |
|------|------|
| 架构 | **双系统完全隔离**：符号因子发现系统 + 可训练模型开发系统，不共享 agent/记忆/状态 |
| 核心机制 | 各自闭环：保留已验证证据 → 引导后续提案 → 沙箱验证 → 再迭代 |
| 沙箱设计 | 固定数据划分 + 固定特征/标签定义 + 固定评估器，LLM 只能输出受限表达（因子公式/config diff） |
| 成果 | 因子系统 IC=0.190（加密资产）；模型系统单股 IC=+0.0843，Sharpe=+2.50（美股 2021-2025 每年正收益） |
| 关键约束 | 无代码开源，但方法论透明（manager-mediated 多智能体 + hybrid 时序架构） |

**与场内设计对照**：元学习层已包含证据关联（假设→证据链）和迭代引导设计，但未实现 AQuA 的"双系统完全隔离"沙箱。AQuA 的双系统隔离是防止因子发现和模型开发互相污染的关键机制，值得参考。

**为什么深入对标它**：AQuA 是目前唯一把"递归自我改进"在量化研究流程层面做到学术级严谨的公开实现。它回答的正是本项目 Phase 3 自我进化的核心风险问题——**无约束 Agent 会污染自己赖以为据的证据**：一个引入未来函数的代码生成 Agent 可能产出虚高分数，该"成功先例"被存入记忆后又引导后续迭代，递归改进因此放大错误而非放大发现。AQuA 的解法不是靠更强的评审 prompt（作者明言 prompt 级指令和模型评审不构成可靠的完整性边界），而是让泄漏类动作在 DSL 层面**不可表达**。这为本项目"证据关联+迭代引导"设计提供了最直接的学术背书，也划定了一条硬标准：自我进化的前提不是更强的模型，而是不可绕过的实验契约。

**对本项目的映射**：
- 证据关联（假设→证据链→迭代引导）↔ AQuA 每系统内"保留已验证证据→引导后续提案"的研究状态机（施工见 11 号文）。
- 模块工厂 DSL 约束代码生成 + AST 沙箱（§5.1 评"可行"）↔ AQuA 的受限 DSL——本项目设计与之同构，AQuA 论文证明该路线可产出 IC=0.190 级别的成果。
- 固定数据划分+固定评估器 ↔ 现有 C-003 回测复用（§5.1）——模块工厂试运行环节必须冻结评估器，不允许 Agent 自选回测口径。
- 双系统完全隔离 ↔ 因子工厂与模型工厂的隔离（开放问题 Q1，待裁定）。

**考虑过的替代方案**：
- *AlphaZero 式自我对弈*：适用于规则封闭的对弈场景，量化研究是开放假设空间，无对局可自弈——不适用。
- *AutoML/HPO（Optuna 等）*：只调参不产生研究假设，无证据语义——是工具不是研究闭环。
- *R&D-Agent-Quant*：开源且经 NeurIPS 2025 收录，但无密封沙箱与双系统隔离，实测暴露"IC 目标与实盘脱钩"问题（见 §2.8）——列为补充对标而非主对标。

**2026-08-17 复核**：论文 arXiv:2608.12841v1（2026-08-13 挂网，Princeton + Ant Group + Stanford，Mengdi Wang 团队）核实——双系统不共享 agents/memories/candidate spaces/research state；因子系统组合 IC≈0.190（加密资产）；模型系统单股 IC=+0.0843，两腿成本下 held-out Sharpe 最高 +2.50，2021-2025 每年正收益；agent 只能发射受限 DSL 程序，无法触碰数据通路与评估器。与本文既有记录一致，另补充作者核心立场："改进的是研究过程，而非成功的定义"。
### 2.2 NVIDIA NeMo Agent Toolkit（2026-05）

> 信号发现 Agent 三件套——**自进化自主循环的工程实现**。

| 维度 | 内容 |
|------|------|
| 架构 | 三 Agent 循环：**信号 Agent**（提假设）→ **代码 Agent**（写代码）→ **评估 Agent**（回测+逻辑评估）→ 结果反馈优化假设 |
| 模型 | Nemotron-3-Nano-30B-A3B 通过 NIM 推理 |
| 关键特性 | 结构化数学计算器作为 building blocks，防止 LLM "幻觉数学" |
| 工程层 | NeMo Agent Toolkit 管理 Agent 间 handoff，保留上下文（信号定义/回测结果） |

**与场内设计对照**：模块创建→试运行→元学习反馈流水线与 NeMo 的信号→代码→评估闭环高度对齐。差异在于 NeMo 是"全自动零人工"，Phase 2 保留人工审批（符合 system_charter §2 约束六：AI 生成代码不可完全信任）。

**为什么深入对标它**：NeMo 信号发现蓝图是工业界把"研究闭环"做成可复制商品的标志——NVIDIA 官方 developer example 意味着三 Agent 分工闭环已越过"论文原型"阶段，成为有运维、有观测、有配置化入口的工程范式。对本项目的价值不在复刻（本地 NIM 部署需 48GB+ 显存，超出 RTX 3090 24GB 硬约束），而在三点工程细节的互证：①结构化算子库（66 类数学计算器）防"幻觉数学"——与本项目 DSL 约束思路独立同构；②评估 Agent 的 IC/RankIC 阈值门控——与本项目画像→考试→护照链路的门控思想一致；③全流程 YAML 配置化——研究参数（阈值/轮数/前瞻期）与代码分离，本项目 config 驱动设计同此方向。

**对本项目的映射**：
- 模块创建（代码生成+AST 沙箱）→试运行（回测+模拟）→元学习反馈 ↔ Signal/Code/Evaluation 三 Agent 闭环（施工见 13 号文）。
- 评估 Agent 的指标门控 ↔ 模型画像→考试→护照链路的准入门槛（06 号文；`src/zephyr/intelligence/model_profiling/` 已有 exam_orchestrator / capability_passport 等 24 个 .py，2026-08-17 实测）。
- NeMo Agent Toolkit 的 handoff 上下文保留 ↔ 本项目多 AI 会话"落盘交接"机制（08 号文）——前者进程内自动，后者跨会话手动，目标同为防止上下文在环节间丢失。

**考虑过的替代方案**：
- *自研 LangChain 编排*：重复造轮子，且无 NeMo 的观测/trace 生态。
- *Temporal/Prefect 工作流引擎*：偏数据管道语义，不含研究闭环的假设-证据状态。
- *直接部署 NeMo 蓝图*：本地需 48GB+ 显存（A100/H100 级），违反硬件约束；托管 NIM API 则引入外网依赖与数据出站风险——故只取架构思想，不作依赖。

**2026-08-17 复核**：NVIDIA 开发者博客原文（2026-05-21，Peihan Huo 等）核实——三 Agent 角色、handoff 上下文保留、结构化计算器防幻觉数学、Nemotron-3-Nano-30B-A3B 经 NIM 推理均与本文记录一致。补充两个值得注意的事实：①蓝图演示中最优信号 Rank IC=-0.0134（3,504 个交易日统计显著）——效应量 modest，印证"AI 发现信号可行但非圣杯"，门控与成本意识不可少；②蓝图已商品化（build.nvidia.com launchable，支持托管 API 免本地 GPU）。

### 2.3 TiMi（Microsoft Research，2026-02）

> 理性驱动多 Agent 系统——**策略开发与部署解耦**。

| 维度 | 内容 |
|------|------|
| 架构 | 策略开发（离线）与分钟级部署（在线）解耦 |
| 核心机制 | **数学反思闭环**：策略→执行→数学反思→参数优化→再执行 |
| 两层分析范式 | 宏观模式→微观定制 |
| 编程设计 | 分层编程实现交易机器人 |

**与场内设计对照**：自反Agent的三级反思（L1/L2/L3）+ PreFlect 前瞻反思 + Agent-R 实时反思覆盖了 TiMi 的数学反思功能，且增加了频率控制（ReflCtrl）。

**为什么深入对标它**：TiMi 的价值在两条独立的架构判断上给了本项目外部印证。①**开发/部署解耦**：离线深度研究与在线轻量执行分离，恰好匹配本项目 T+1、日频及以上根频率的交易约束——盘中不需要也不能做重型推理，反思与优化全部发生在盘后离线窗口。②**数学反思闭环**：用可计算的数学对象（而非自由文本感想）作为反思载体，是"理性驱动 Agent"区别于一般 ReAct 循环的关键；本项目自反Agent设计的反思分级（L1 执行/L2 策略/L3 目标）与之同构且更细。此外本项目 ReflCtrl 频率控制是 TiMi 没有的补充——反思不是越多越好，无频率约束的反思循环等于算力成本失控，单机约束下这是生存性问题。

**对本项目的映射**：
- 数学反思闭环 ↔ 自反Agent（Actor→Evaluator→SelfReflection，12 号文施工）。
- 开发/部署解耦 ↔ Phase 路线的离线施工/在线执行分离（17 号文），以及"架构手动来"原则下人工审核天然位于离线侧。
- 宏观模式→微观定制两层分析 ↔ 策略组合层与单策略层的分工（交易决策侧设计，只读引用）。

**考虑过的替代方案**：
- *Reflexion 原始范式（Shinn et al.）*：通用领域文本反思，无金融数学对象，无部署解耦——TiMi 是其金融特化增强版，选 TiMi。
- *CRITIC 等工具校验框架*：侧重工具输出校验，不含参数优化闭环。

### 2.4 AlphaQuanter（HKUST，2025-10）

> 单 Agent + RL 端到端训练——**可验证奖励强化学习**。

| 维度 | 内容 |
|------|------|
| 架构 | 单 Agent ReAct 循环：规划→工具调用→信息获取→深度分析→交易决策 |
| 核心机制 | **RL 端到端训练**：可验证奖励（outcome-based + process-based）直接优化决策过程 |
| 关键特性 | 透明推理链，决策可解释；无需 prompt engineering |
| 开源 | GitHub: AlphaQuanter/AlphaQuanter |

**与场内设计对照**：MAML + 在线EWC 提供了元学习能力，但无 RL 端到端训练信号回传。MOD-ML-002（ai_operator）有 Generator→Critic→Judge 三层但无 RL。

**为什么中度对标它**：AlphaQuanter 证明了两件对本项目有方向性意义的事：①**可验证奖励可以替代 prompt 调优地狱**——outcome-based（盈亏结果）+ process-based（推理链质量）双奖励直接优化决策过程，免去手工 prompt engineering 的无尽试错；②**单 Agent 足矣**——不需要多 Agent 编排也能完成端到端交易决策，这与 61 号备忘"不做 agent 编排系统"的裁定方向一致。但对本项目而言 RL 训练信号回传需要持续的 GPU 训练预算，单 RTX 3090 既要跑本地推理又要跑训练，时段冲突难以调和——故列为方向参考+开放问题（Q2），不进主线施工计划。

**对本项目的映射**：
- process-based 奖励设计 ↔ MOD-ML-002（ai_operator）Generator→Critic→Judge 的 Critic/Judge 层可参考其奖励分解思路。
- 透明推理链 ↔ 可解释性门控设计（00_index.md §3 横切层）——决策可解释是本项目门控的前置条件。

**考虑过的替代方案**：
- *纯 prompt 工程（现状）*：零训练成本但天花板低、回归不可测。
- *SFT 微调*：本项目无足够标注轨迹数据。
- *RLHF*：人工标注成本超出 1 人约束。
- 结论：主线维持"无训练"路线（ICL/prompt），RL 端到端留 Q2 待裁定。

### 2.5 AI Agent Swarm（行业报告，2026-01）

> 多 Agent 强化学习群体——**机构级部署规模**。

| 维度 | 内容 |
|------|------|
| 规模 | 42.5% 美股量化交易量，$1.2T AUM |
| 角色分工 | 情绪分析器 / 风险守护 / 执行机器人 / 协调 Agent |
| 协调机制 | MARL（多 Agent 强化学习）+ 共识构建 |
| 监管响应 | EU AI Act + SEC Agent Identity Protocol（实时追踪非人类市场参与者） |

**与项目关系**：机构级终局形态，但 61 号备忘已明确"不做 agent 编排系统"。Swarm 架构是远期参考，非当前方向。按 system_charter §2 约束一（1 人全栈+AI），Swarm 级多 Agent 编排超出个人能力边界，属过度工程。

**为什么只需浅度对标**：Swarm 报告的价值是提供"终局形态"参照系，用于校准本项目**不做什么**——机构级群智依赖集群算力、专属数据团队、合规部门和毫秒级执行通道，每一项都超出本项目硬约束。它的角色分工（情绪/风控/执行/协调）与本项目执行层四类 Agent（治理/业务/算法/自我迭代）在概念上呼应，但本项目以"人调度多 AI 会话"替代 MARL 协调层，是约束下的有意识降级而非能力不足。

**中国市场对照（2026-07 补充）**：A 股语境下"量化群智"另有一层监管维度——2026 年 Q1 国内量化私募规模超 1.8 万亿元、贡献约 30%~40% 日成交额；2026-06 上交所清理量化专属高速通道，监管明确"降频、透明、限空、收费"导向。本项目 miniQMT 通道、T+1、日频、不做空、10 笔/秒 的参数恰好落在监管鼓励的非高频区间——Swarm 式高频群智与本项目既无能力相关性也无合规相关性。

**2026-08-17 复核**：原始报告《The Rise of Autonomous AI Agent Swarms in Quantitative Trading》（Rick Spair / DX Today，2026-01）核实——42.5% 美股量化交易量、55% 加密衍生品交易量、$1.2T AUM、MARL+共识构建、EU AI Act + SEC Agent Identity Protocol 均与本文记录一致。注意：该数据源自行业研究报告而非监管统计，口径宜作趋势参考。

### 2.6 Man Group AlphaGPT（机构实践）

> 全自动投研流水线——**机构级"AI 研究员"的最完整公开描述**。

| 维度 | 内容 |
|------|------|
| 流程 | AI 独立提出假设 → 编写代码 → 验证策略 → 解释经济原理 |
| 关键特征 | 端到端无人工干预的研究循环；强调可解释产出（经济原理解释） |
| 规模前提 | 机构数据平台 + 合规框架 + 专职 AI 团队 |

**对本项目的映射**：本项目元学习系统（知识采集→模块工厂→证据关联）是最接近 AlphaGPT 路径的个人级实现，且多了"知识采集→模块工厂"这一上游环节——AlphaGPT 从假设开始，本项目从外部知识开始，假设由知识驱动而非凭空生成。其"解释经济原理"环节对应本项目可解释性门控：策略必须附带可陈述的经济逻辑才允许进入人工审批。

**考虑过的替代方案/边界**：机构模式依赖专属数据授权与合规团队，个人项目不可复制；只取"假设→验证→解释"闭环的可解释性要求，不取"全自动无人工"（违反 system_charter 约束六）。

### 2.7 Balyasny / Millennium（机构实践）

> 中心化 AI 基础设施 + 多团队赋能——**"平台型 AI"路径代表**。

| 维度 | 内容 |
|------|------|
| 模式 | 中心化 AI 团队建设通用基础设施，赋能多个独立投资团队（pod）复用 |
| 关键特征 | 能力复用 > 单点策略；平台沉淀数据/工具/模型，团队专注 alpha |

**对本项目的映射**：模块工厂的"上游供应商"定位与此同构——一套"知识→模块"生产线服务因子/信号/策略/模型四个下游工厂，正是"中心化能力复用"的个人版。Balyasny 模式证明平台化路线的杠杆来自**复用次数**而非单次质量，这支持模块工厂 Phase 0→1 优先做"映射与入库"（提高复用率）而非先做"全自动生成"。

**考虑过的替代方案/边界**：多团队编排与预算结算机制超出 1 人约束，不取；只取"中心化能力复用"思想。

### 2.8 其他量化 Agent 公开系统速览

> 场内元学习系统设计时已做过 13 个公开系统对标（R&D-Agent-Quant / QuantEvolve / Hubble / FactorMAD / TiMi / ProFiT / CogAlpha / FactorMiner / FinRL-X / Dnalyaw 等），对标明细真源在场内设计资产（12/13 号文引用），本文不重复展开，仅登记与 AI 层施工直接相关的两条新证据。

**R&D-Agent-Quant（微软亚洲研究院）第三方 A 股实测（2026-05-20，国联民生金工）**：
- 实测设置：Wind A 股 5,792 只股票、165 字段、财务数据 PIT 对齐；fin_factor 场景 36 个有效 Loop，组合双周频 IC 提升至 0.07，触发 11 次 SOTA 更新；运行成本约 $10/轮。
- 对本项目的三条直接启示：①**模型的代码工程能力比单纯推理能力更关键**（实测 GLM-V5.1 显著优于 DeepSeek-V3.2，后者频繁无限重复/编码失败）——直接影响本项目模型画像与岗位匹配的维度权重；②**IC 优化目标与实盘收益脱钩**（ICIR/换手率/容量/成本/回撤缺乏系统评估）——本项目模块工厂试运行必须内嵌成本与容量评估，不能只看 IC；③环境约束（Linux + Qlib + Conda 隔离，Windows 需 WSL）——本项目不回测框架外迁，继续复用 C-003。
- 原文另确认 R&D-Agent 量化分支（RD-Agent-Quant）已被 NeurIPS 2025 收录，迭代至 v0.8.0。

**FactorMAD（因子挖掘多 Agent 辩论）**：多 Agent 以辩论机制做因子挖掘，是 00_index.md §1 多Agent协作组件的对标来源之一（12 号文施工引用）。与 R&D-Agent 的"R/D 两角色"相比，FactorMAD 强调对抗性互评，对本项目多Agent投票（3-5 Agent 投票→选最优）的评审环节有参考价值。本次未做独立深挖，维持 12 号文施工时按既有场内对标口径引用。
---

## 三、Vibe Coding 社区演进

### 3.1 范式跃迁时间线

```
2025-02  Karpathy 提出 Vibe Coding
         "忘记代码存在，专注想法实现"
         → 项目当前所处阶段

2026-02  Karpathy 提出 Agentic Engineering
         终结 Vibe Coding，三层架构：
         意图层(PRD/ADR) → 协作生成层(Agent编排) → 工程保障层(代码/测试/监控)
         → 项目 Phase 0→3 分阶段路线已覆盖此演进路径

2026-03  Zenera 提出受约束 Vibe Coding
         Meta Agent 接收高级意图 → 自动生成部署工件
         → 语义验证 → 持续优化
         → 项目无 Meta Agent 概念，可作为远期参考
```

### 3.2 Agentic Engineering 三层架构

| 层 | 核心资产 | 项目对应 | 差距 |
|----|---------|---------|------|
| **意图与决策层** | PRD / BizContext / ADR | design_memos/（66 份备忘）| 有意图文档，但无自动转化为 AI 可执行任务的机制 |
| **协作与生成层** | Agent 编排 / 上下文 / Prompt 库 | AutoRuntime Core + D_ORCHESTRATOR + 自反Agent设计 | 有编排基础设施+设计，但无"意图→任务"自动分解 |
| **工程保障层** | 代码仓库 / 测试 / 监控 | pre-commit 门禁 + reconciler + 测试体系 | 有工程保障，但无"AI 生成→自动验证→自动修复"闭环 |

**为什么深入对标它**：Agentic Engineering 是 Karpathy 本人对 Vibe Coding 的正式终结宣言，其三层划分给本项目 Phase 0→3 路线提供了元框架级的合法性：Phase 0（手动）= 只有意图层；Phase 1（半自动）= 协作生成层人工触发；Phase 2（全自动+人工审核）= 三层贯通但意图层保留人工；Phase 3（自我进化）= 协作生成层获得自我改进能力。对本项目最关键的判断是——**三层的成熟度必须自下而上**：工程保障层（门禁/测试/监控）不稳固就上协作生成层自动化，等于把错误放大器装上流水线。本项目当前工程保障层已有实质设施（pre-commit 门禁、GitCommitGateway、reconciler），这正是 Phase 0→1 以基础设施先行的外部依据。

**对本项目的映射**：见上表"项目对应"列；差距列三项即 17 号文分阶段路线需闭环的三件事。

**考虑过的替代方案**：
- *继续纯 Vibe Coding 不升级*：意图与生成混在一起，技术债以对话速度累积——Karpathy 本人已宣告此路终结。
- *跳过保障层直接上全自治编排*：违反 system_charter 约束六（AI 生成代码需交叉验证+依赖锁定+自治熔断）。
- 结论：三层渐进是唯一与本项目约束兼容的路径，Phase 划分（17 号文）即其落地。

### 3.3 VibeDev（GitHub，2026-07）

> AI 驱动软件开发治理框架——**Vibe Coding 的治理侧**。

| 维度 | 内容 |
|------|------|
| 组件 | VibeDev（开发周期编排）+ VibeShield（安全审计） |
| 触发 | 每个项目 session 自动运行 |
| 特性 | 阶段/计划/门禁/事后复盘 + Layman Mode |

**与项目关系**：65 号备忘（git 安全治理）+ 66 号备忘（提交队列串行化）已覆盖 VibeDev 的核心功能，但更偏"防护"而非"编排"。

**为什么中度对标它**：VibeDev 补上了 Agentic Engineering 三层架构里"工程保障层"的一个具体实现样本——把治理动作（阶段/计划/门禁/复盘）做成每个 session 自动运行的默认项，而非靠开发者自觉。这印证本项目 65/66 号备忘的方向正确（提交走 Gateway 串行、git 安全护栏），差异在本项目治理是"防护优先"（防 AI 改坏仓库），VibeDev 是"编排优先"（管 AI 开发节奏）——在 1 人多 AI 会话模式下，防护是刚需、编排可由人承担，故本项目无需引入 VibeDev 本体。

**考虑过的替代方案**：直接采用 VibeDev 框架（引入外部 session 钩子依赖，与 TRAE 多对话施工方式不兼容，放弃）；OpenHands 等自治开发 Agent（越过"架构手动来"红线，放弃）。

### 3.4 受约束 Vibe Coding（Zenera，2026-03）

> Meta Agent 范式——**在意图层之上再加一层"理解意图的 Agent"**。

| 维度 | 内容 |
|------|------|
| 架构 | Meta Agent 接收高级意图 → 自动生成部署工件 → 语义验证 → 持续优化 |
| 关键特征 | 意图层本身被 Agent 化；人只下高级意图 |
| 提出者 | Zenera / Stephane Maes（2026-03） |

**为什么中度对标它**：受约束 Vibe Coding 是"架构自动来"路线的代表——Meta Agent 接管意图层，与本案"架构手动来"原则恰好构成对照实验。关注它的理由不是要引入，而是监控：若 Meta Agent 范式在未来证明能可靠地把 PRD/ADR 转为可执行任务且不漂移，本项目意图层（当前 66 份备忘人工维护）才有自动化的候选路径。当前判定为**远期参考**：意图理解错误的代价是架构级错误，个人项目无冗余承受此类实验。

**对本项目的映射**：无直接映射（有意为之的空白）。00_index.md §1 顶层"人（架构师）：架构设计·意图定义·红线裁定（手动，不可自动化）"即对本范式的显式拒绝。

**考虑过的替代方案**：无同类公开实现（该范式 2026-03 才提出）——本身即"替代方案库"中的唯一条目，留 §7.2 持续跟踪。

---

## 四、GitHub 顶级 Agent 框架

### 4.1 框架对比

| 框架 | Stars | 核心能力 | 项目适配度 |
|------|-------|---------|-----------|
| **claude-flow** | 61k | 自主 Agent 协调 + 目标分解 + 跨网络联邦 + MCP 工具 | 中——D_ORCHESTRATOR 可参考其目标分解引擎 |
| **CrewAI** | 54k | 角色化多 Agent + 人在环 + 协作工作流 | 低——61 号备忘已暂缓 agent 编排 |
| **Hermes** | 2026 最火 | **可写运行时** + 五层记忆 + 原生多 Agent + MCP 原生 | **高——AutoSkill 技能库已有等价设计，Hermes 的工程实现可参考** |
| **Qualixar OS** | 新 | 12 种拓扑 + **三层模型路由**（Q-learning+POMDP）+ **Goodhart 检测** + 行为契约 | **高——LLM 路由已有设计，Qualixar 的 Q-learning 动态学习可参考** |

### 4.2 Hermes 可写运行时 vs AutoSkill

```
Hermes（外部）                          场内设计（AutoSkill）
─────────────────                      ─────────────────────────
任务执行 → 识别短板/错误                研究轨迹分析 → 轨迹→抽象技能
    ↓                                      ↓
自动生成技能代码/补丁                   新技能经回测验证
    ↓                                      ↓
自主测试校验                            注册到技能库（Voyager模式）
    ↓                                      ↓
永久存入技能库                          新任务优先检索复用
    ↓                                      ↓
下次同类任务直接调用                    技能三元组匹配→引导生成方向
```

**差异**：Hermes 是"执行中发现短板→自动生成"，场内设计是"研究轨迹分析→抽象技能→回测验证→注册"。场内设计增加了回测验证环节（金融场景必要），Hermes 更轻量（通用场景）。

**为什么深入对标它**：Hermes 是"Agent 能力随时间复利"这一命题在 2026 年最成功的工程实证——发布后约半年即成为当年增长最快的开源 Agent（2026-08-11 达 228,662 stars，见 §7.1）。它的核心赌注与本案 AutoSkill 完全一致：**智能不在模型权重里，在模型外面那层可持续积累的技能与记忆里**（Harness Engineering）。对本项目更有价值的是 Hermes 暴露的两个本项目尚未覆盖的工程答案：①技能的**渐进披露三级加载**（索引常载/详情按需/参考文件单点取）解决技能库膨胀后的 token 成本问题；②**Curator 后台自治体**（2026-04-30 v0.12.0）按周期自动评分/合并/剪枝技能库——技能库不是建好就完，无人维护会腐烂。这两点都可直接映射到已存在的代码设施上（见下）。

**对本项目的映射**：
- AutoSkill 技能库 ↔ `src/zephyr/autonomy_core/skills/`（58 个 .py 实测）：skill_factory / skill_constructor / skill_discovery / skill_registry / skill_evaluator / skill_executor / skill_router / skill_sandbox 等文件名级对应。
- 渐进披露加载 ↔ `src/zephyr/autonomy_core/progressive_disclosure_injector.py` + context/ 包注入管线（实测存在）。
- Curator ↔ skill_postmortem.py / skill_freshness.py / skill_freshness_ext.py（实测存在，功能覆盖度待 02 号文评估）——场内有死后复盘与新鲜度概念，尚无"周期自治评分/合并/剪枝"闭环，列为 11 号文施工参考。
- /learn（2026-06 新增，从任意材料蒸馏 SKILL.md）↔ 模块工厂"知识采集→模块映射"（13 号文）——Hermes 证明"从材料到技能"的蒸馏环节可以极轻量（一个标准 prompt 回合），支持 §5.1"知识采集可行"的判断。

**考虑过的替代方案**：
- *LangChain/LangGraph 插件机制*：技能静态注册，无运行时自创建——不满足自进化。
- *AutoGPT 插件生态*：2025 后已式微，维护风险高。
- *Voyager 原版（Minecraft）*：技能库概念源头但域绑定游戏。
- 结论：AutoSkill 自研路线正确（金融需回测验证环节），Hermes 作工程实现参照库，不作依赖引入。

**2026-08-17 复核更新**：①Hermes Agent 为 Nous Research 2026-02 发布的开源自主 Agent（MIT），支持 Linux/macOS/WSL2，一条 curl 安装；技能遵循 SKILL.md + agentskills.io 开放标准。②v0.12.0 "Curator"（2026-04-30）：后台自治体按 cron 周期（默认 7 天）评分/合并/剪枝技能库并出报告，内置防御门保护内置/社区技能不被误改。③2026-06 新增 `/learn`：指向文档页/本地 SDK/对话/笔记即自动撰写合规 SKILL.md。④自我进化独立管线 hermes-agent-self-evolution（Phase 1 验证报告 2026-03-09）：DSPy + GEPA（ICLR 2026 Oral）纯 API 进化技能文本，无需 GPU，单次 $2~10，arxiv 技能 held-out 质量 +39.5%——**这是"无 GPU 技能自进化"的直接工程先例，印证本文 §5.3 用 ICL 替代 MAML/EWC 的裁剪方向**（详见 §7.1）。

### 4.3 Qualixar OS 三层模型路由 vs LLM Agent 路由

| 层 | Qualixar OS | LLM Agent 路由 |
|----|------------|---------------|
| L1 | ε-greedy 上下文赌博机选择路由策略 | 级联控制器 3 阶段（本地/API 分时分任务） |
| L2 | 5 种策略（成本优化/质量优先/速度优先/认知任务感知等） | 成本控制 + 降级策略 |
| L3 | 贝叶斯信念状态更新（POMDP） | 无 |

**差异**：LLM 路由是静态规则（成本+时段），Qualixar 是动态学习（Q-learning）。Goodhart 检测（跨模型熵监控防刷分）是 Qualixar 独有，可解释性门控+Agent漂移检测提供了类似但不等价的功能。

**为什么深入对标它**：Qualixar OS 是目前唯一把"模型路由"当作一等公民做成学习系统的公开实现，且作者本人是独立研究者——单兵做出 12 拓扑编排 OS 的事实本身就证明该量级设计在个人项目可达范围内。对本项目最直接的三点启示：①**路由可以先静态后学习**——其 L1 ε-greedy bandit 的前提是已有可观的路由结果数据，本项目画像→考试→护照链路（`model_profiling/` 24 个 .py 实测）正是该数据的生产者，task_model_learner.py（实测存在）已是任务×模型表现的学习雏形，静态路由不是落后而是学习路由的必要前置；②**Goodhart 检测是 LLM-as-judge 的必需品**——本项目考试链路用 LLM 评审（exam_judge.py 实测存在），一旦把评审分数用于路由/晋升决策，"刷分"动机即产生，跨模型熵监控是低成本的完整性信号；③**行为契约（design-by-contract）**为 Agent 团队划不变量，与本项目"自治边界三分类"（15 号文）思想同构。

**对本项目的映射**：
- 三层路由 ↔ LLM Agent 路由级联控制器（11 号文施工）；Q-learning 动态化留 Q3 待裁定。
- Goodhart 检测 ↔ 可解释性门控 + Agent 漂移检测（`src/zephyr/intelligence/model_drift_detector.py` 实测存在）；Qualixar 的 JSD 漂移阈值 Θ=0.877 可作参数参考。
- 行为契约 ↔ 自治边界 ai_modifiable/human_gated/immutable 三分类（00_index.md §3.1，15 号文施工）。

**考虑过的替代方案**：
- *RouteLLM（静态成本路由）*：与本项目级联控制器同级，无学习能力——现状已覆盖。
- *FrugalGPT 级联*：Qualixar L2 策略层已内含该思想。
- *OpenRouter 等托管自动路由*：黑盒、数据出站、不可审计——违反本项目治理约束。
- 结论：静态级联先行，Q-learning 升级留 Q3；许可证注意：Elastic License 2.0（源码可用但非 OSI 开源），只可借鉴思想不可搬代码。

**2026-08-17 复核**：论文 arXiv:2604.06392v1（2026-04-07，独立研究员 Varun Pratap Bhardwaj）核实——三层路由（ε-greedy contextual bandit + 5 策略 + Bayesian POMDP）、Goodhart 检测器（goodhart-detector.ts，290 行，监控跨模型熵等 4 信号）、JSD 漂移阈值 Θ=0.877、行为契约、2,821 测试用例、20 任务评测 100% 准确率/均成本 $0.000039 均与本文记录一致；产品侧已 npm 化（`npx qualixar-os`），拓扑数从论文 12 种增至 13 种。

### 4.4 claude-flow

| 维度 | 内容 |
|------|------|
| 规模 | 61k stars（2026-06 口径） |
| 核心能力 | 自主 Agent 协调 + 目标分解 + 跨网络联邦 + MCP 工具 |

**为什么中度对标它**：claude-flow 的目标分解引擎（把高层目标拆成可并行执行的子任务图）是 D_ORCHESTRATOR 可参考的单点能力；但其"跨网络联邦"假设多机多节点，超出单机约束，整体不可引入。适配度评"中"仅指目标分解一个子模块。

**对本项目的映射**：D_ORCHESTRATOR 目标分解（05 号文域边界、14 号文执行层引用）；**边界**：61 号备忘已裁定不做 agent 编排系统，故只读其任务图数据结构思想，不接其运行时。

**考虑过的替代方案**：LangGraph（图编排强但同样假设进程内自治编排）；CrewAI（见 §4.5）。均因 61 号备忘裁定不引入运行时。

### 4.5 CrewAI

| 维度 | 内容 |
|------|------|
| 规模 | 54k stars（2026-06 口径） |
| 核心能力 | 角色化多 Agent + 人在环 + 协作工作流 |

**为什么中度对标它**：CrewAI 的"角色+人在环"范式与本项目"人调度多 AI 会话"神似——差异在 CrewAI 把人在环编码进框架，本项目由人在 TRAE 多对话间手动调度。它的角色卡（role/goal/backstory 三要素）定义方式对本项目 AI 员工花名册（Stage K 未激活）的岗位描述格式有参考价值。适配度"低"是因为 61 号备忘已暂缓 agent 编排，只取其角色定义 schema 思想。

**考虑过的替代方案**：AutoGen（微软，对话式编排，同样编排越界）；MetaGPT（SOP 编码，与本项目 design_memos 流程重复）。

---

## 五、模块工厂落地性评估

> 模块工厂（Module Factory）在 §一 被评为"⭐⭐ 核心独创"——没有任何已公开系统有此概念。本节回答的问题是：它会不会是纸上谈兵？评估基准是 [system_charter.md](../../04_architecture_principles_decisions/system_charter.md) §2 硬约束（1 人全栈 + 单机 RTX 3090 + 无集群 + AI 生成代码需交叉验证）。施工细节真源是 [13_module_factory.md](13_module_factory.md)，本节只做落地性判断。

### 5.1 逐项可行性评估

| 环节 | 可行性 | 判断 |
|------|--------|------|
| 知识采集（手动/爬虫） | **可行** | 无技术门槛；Hermes `/learn`（2026-06）证明"从材料到技能"的蒸馏可轻至一个标准 prompt 回合（§4.2） |
| LLM 知识分类 | **可行** | LLM 文本分类准确率已足够支撑因子/策略/风控/执行的粗粒度分桶 |
| 语义匹配→模块映射 | **可行** | embedding + SQLite FTS5 轻量实现；Hermes 跨会话召回同为 SQLite FTS5 方案，单机验证过的栈 |
| DSL 约束代码生成 | **可行** | DSL 限制搜索空间，AST 沙箱防注入；AQuA 证明受限 DSL 路线可产出组合 IC≈0.190 级成果（§2.1） |
| 回测验证 | **可行** | 现有 C-003 回测直接复用；评估器必须冻结，不允许 Agent 自选回测口径（AQuA 密封沙箱原则，§2.1） |
| **Phase 2 全自动零审核** | **不可行** | LLM 生成交易策略代码，零审核=自杀（system_charter §2 约束六） |
| **Phase 3 MAML/EWC** | **不现实** | RTX 3090 单 GPU 跑不动显式元训练，ICL 替代更实际 |
| **Phase 3 自我进化** | **远期愿景** | RSI 学术界无可靠实现，只能渐进逼近；hermes-agent-self-evolution 证明"无 GPU 技能自进化"（DSPy+GEPA 纯 API，单次 $2~10）是这条渐进路径上已验证的第一级台阶（§7.1） |

### 5.2 结论

**模块工厂不是纸上谈兵，但 Phase 2→3 需要大幅裁剪。**

- **Phase 0→1（知识→模块映射）**：核心独特点，值得优先落地。技术栈成熟（LLM 分类 + embedding 检索 + DSL 代码生成 + 现有回测），无不可逾越的障碍。
- **Phase 2（全自动）**：保留人工审核。LLM 生成 → 人工审核 → 自动回测，不追求零人工。
- **Phase 3（自我进化）**：用 ICL（上下文学习）替代 MAML/EWC——只需精心设计 prompt 含历史案例，无需显式元训练，与单 GPU 兼容。
- **成本与容量必须内嵌**：R&D-Agent-Quant A 股第三方实测暴露"IC 优化目标与实盘收益脱钩"（§2.8）——模块工厂试运行环节必须内嵌成本/容量/回撤评估，不能只看 IC。

### 5.3 裁剪后的现实路径

```
Phase 0（手动）     → 知识→模块映射验证，全程人工
Phase 1（半自动）   → LLM 分类+匹配自动化，代码生成人工审核
Phase 2（全自动）   → 采集→分类→匹配→生成→回测 全自动，上线人工审批
Phase 3（自我进化） → ICL 元学习 + AutoSkill 技能库 + 证据关联迭代引导
                     （裁剪掉 MAML/EWC，用 ICL + prompt 工程替代）
```

### 5.4 实施约束（不可违反）

| 约束 | 来源 | 说明 |
|------|------|------|
| 不做 agent 编排系统 | 61 号备忘 §2.3 | 多 AI 协作 = 人调度多会话，非 agent 自治 |
| 架构手动来 | 用户明确裁定 | 架构设计决策始终由人做出，AI 不自动修改架构 |
| 多 AI 交叉验证 | system_charter §2 约束六 | AI 生成代码不可完全信任 |
| AI 自治熔断 | system_charter §2 约束六 | 亏损超限/置信度低 → 降级"仅建议"模式 |
| Phase 2 保留人工审核 | 本文 §5.2 | LLM 生成交易策略代码，零审核=自杀 |
| Phase 3 用 ICL 替代 MAML/EWC | 本文 §5.3 | 单 GPU 不支撑 MAML/EWC，ICL 更实际 |

---

## 六、不做什么（本文边界）

1. **不做代码实现细节**：本文只做框架分析、映射与落地性判断，不施工；施工真源是 03~17 号施工文档，设施存在性真源是 [02_design_asset_inventory.md](02_design_asset_inventory.md)。
2. **不做框架完整复现**：只取启示与单点机制（如 Goodhart 检测、渐进披露加载、密封沙箱），不引入外部框架本体作依赖——NeMo 本地部署需 48GB+ 显存（§2.2）、OpenRouter 类托管路由数据出站不可审计（§4.3）、claude-flow 跨网络联邦超出单机约束（§4.4），均已逐个否决。
3. **不做远期框架的深度评估**：AI Agent Swarm、受约束 Vibe Coding（Meta Agent）等机构级/范式级条目仅作边界校准与跟踪（远期属性见 §1.3 分级与 §7.2），不展开施工级分析。
4. **不做双真源维护**：00_index.md §2 只保留一句话速览表，深度分析唯一真源在本文；场内设计资产细节唯一真源在 02 号文与 12/13 号文，本文引用不复制。

---

## 七、前沿演进方向

### 7.1 2026-08 已核实动态（2026-08-17 WebSearch 复核）

| 动向 | 事实 | 对本项目的意义 |
|------|------|---------------|
| Hermes 持续爆发 | 2026-08-11 达 228,662 stars，为 2026 年增长最快的开源 Agent；官方文档确认 Curator 后台进程归档低分技能、FTS5 跨会话召回、技能经 `/<skill-name>` 加载 | "技能库建好会腐烂、需周期自治维护"的判断获官方实现背书 → 11 号文施工参考 |
| hermes-agent-self-evolution Phase 1 验证报告（2026-03-09） | DSPy + GEPA（ICLR 2026 Oral）纯 API 进化技能文本，无需 GPU，单次 $2~10；arxiv 技能 held-out 质量 0.408→0.569（+39.5%）；GEPA 较 GRPO +6% 且 rollouts 少 35 倍；防护门 = 测试 100% 通过 + 技能 ≤15KB + 语义保留 + 人工评审 | **无 GPU 技能自进化的直接工程先例**，印证 §5.3 用 ICL/文本进化替代 MAML/EWC 的裁剪方向；其防护门设计可作 13 号文模块工厂验证环节参照 |
| AQuA 挂网（2026-08-13，arXiv:2608.12841v1） | 双系统不共享 agents/memories/candidate spaces/research state；作者立场："改进的是研究过程，而非成功的定义" | 已并入 §2.1；自我进化的证据完整性有了学术标杆 |
| NeMo 信号发现蓝图商品化 | build.nvidia.com launchable，托管 API 免本地 GPU；蓝图演示最优信号 Rank IC=-0.0134（3,504 个交易日统计显著，效应量 modest） | "AI 发现信号可行但非圣杯"，门控与成本意识不可少（§2.2） |
| Qualixar OS 产品化 | npm 化（`npx qualixar-os`）；拓扑从论文 12 种增至 13 种；测试通过数 2,821（论文）→ 2,936（产品页）；产品页许可证标注 FSL-1.1（两年后转 Apache 2.0），论文标注 Elastic License 2.0——两者均为源码可用非 OSI，§4.3"借鉴思想不搬代码"结论不变 | 独立研究员可持续运营该量级系统，佐证本项目自我进化层的个人可达性 |
| R&D-Agent-Quant 获学术认可 | NeurIPS 2025 收录，迭代至 v0.8.0；A 股第三方实测（2026-05-20，国联民生金工） | 三条启示已并入 §2.8（代码工程能力 > 推理能力、IC 与实盘脱钩、环境约束） |
| RSI 成为独立研究领域 | ICLR 2026 首设 Recursive Self-Improvement Workshop；OpenAI 随 GPT-5.6 发布 RSI Index；Anthropic 披露 Claude 产出公司 80%+ 合入代码；Sakana AI 设 RSI Lab（2026-06） | Phase 3 方向的外部合法性增强，同时印证"渐进逼近、不赌单点"的裁剪策略 |
| 自进化三层分类共识 | 社区分类法（2026-07 流传）：Models（权重）/ Harness（prompt·记忆·技能·路由）/ Artifacts（产出物）三层自进化 | 本项目 Phase 3 与 Hermes/AutoSkill 同属 **Harness 层**——不动权重、只进化脚手架，正是单 GPU 约束下唯一可行层 |

> 中国市场监管维度（"降频、透明、限空、收费"导向，2026-06 上交所清理量化专属高速通道）已并入 §2.5 正文，不重复登记。

### 7.2 持续跟踪清单

| 条目 | 跟踪理由 | 触发动作 |
|------|---------|---------|
| 受约束 Vibe Coding / Meta Agent（Zenera，2026-03） | 若"意图层 Agent 化"被证明可靠且不漂移，本项目意图层（design_memos 人工维护）才有自动化候选路径 | 出现可复现的意图→任务分解实证时再评估 |
| FactorMAD 深挖 | 12 号文多 Agent 投票评审环节的对标来源，本轮未独立深挖 | 12 号文施工时按场内既有对标口径引用，必要时补深度 |
| hermes-agent-self-evolution Phase 2~5 | Phase 1 仅覆盖技能文本；后续阶段覆盖工具描述/系统 prompt/代码进化/连续循环 | 每季度复查其报告，验证"无 GPU 进化"的边界扩展情况 |
| 新涌现框架（2026 Q3/Q4 及以后） | 外部演进速度快（本轮复核的框架均有新事实） | 按 Q4 开放问题待裁定的机制登记；登记前只做跟踪，不替换已定决策 |

---

## 八、开放问题

| # | 问题 | 状态 | 说明 |
|---|------|------|------|
| Q1 | AQuA 双系统完全隔离沙箱是否值得引入？ | 待裁定 | 目前场内无此机制，因子发现和模型开发可能互相污染；AQuA 论文证明隔离是防证据污染的关键机制（§2.1） |
| Q2 | AlphaQuanter 的 RL 端到端训练是否值得引入 MOD-ML-002？ | 待裁定 | 场内目前无 RL 训练信号回传；可验证奖励机制对策略优化有价值，但单 RTX 3090 训练/推理时段冲突难以调和（§2.4） |
| Q3 | Qualixar OS 的 Q-learning 动态路由是否值得替换静态路由？ | 待裁定 | 静态路由简单可控且是学习路由的数据前置；task_model_learner.py 已具任务×模型表现学习雏形，Q-learning 需积累路由结果数据（§4.3） |
| Q4 | 新涌现框架如何纳入本文更新机制？ | 待裁定 | 建议每季度搜索一次（§7.2 已列跟踪清单），但由谁触发、如何登记未定 |

---

## 九、参考来源

### 外部来源

| 框架 | 来源 | 日期 |
|------|------|------|
| AQuA | arXiv:2608.12841v1（Princeton + Ant Group + Stanford，Mengdi Wang 团队） | 2026-08-13 |
| TiMi | arXiv:2510.04787（Microsoft Research Asia + 同济大学；v1 2025-10-06，v2 2026-02-09） | 2026-02-09（v2） |
| AlphaQuanter | HKUST，GitHub: AlphaQuanter/AlphaQuanter | 2025-10-16 |
| NVIDIA NeMo Signal Discovery | NVIDIA Developer Blog（Peihan Huo 等） | 2026-05-21 |
| AI Agent Swarm | DX Today / Rick Spair（行业研究报告，数据口径宜作趋势参考） | 2026-01 |
| R&D-Agent-Quant A 股实测 | 国联民生金工第三方实测报告 | 2026-05-20 |
| Vibe Coding → Agentic Engineering | Karpathy / 张昕东 | 2025-02 → 2026-02 |
| 受约束 Vibe Coding | Zenera / Stephane Maes | 2026-03 |
| Hermes Agent | Nous Research（MIT；228,662 stars @2026-08-11）；hermes-agent-self-evolution Phase 1 验证报告 | 2026-02 发布；报告 2026-03-09 |
| Qualixar OS | arXiv:2604.06392v1（独立研究员 Varun Pratap Bhardwaj；DOI: 10.5281/zenodo.19454219） | 2026-04-07 |
| claude-flow | ruvnet | 2026-06 |
| CrewAI | joaomdmoura | 2026-06 |
| Man Group AlphaGPT / Balyasny·Millennium | 机构公开实践报道 | 2026 年口径 |

### 场内设计资产

| 设计 | 核心内容 |
|------|---------|
| 自反Agent | Actor→Evaluator→SelfReflection、L1/L2/L3 三级反思、PreFlect 前瞻反思、Agent-R 实时反思、ReflCtrl 频率控制、策略自我修正闭环、技能注册、四层记忆 |
| 元学习系统（S6 层） | 7 阶段流水线、模块工厂（核心独创）、STOP/RISE/Voyager/Meta-Harness/AutoSkill/MAML/EWC/ICL、Phase 0→3、13 个公开系统对标 |
| 分阶段实现路线 | Phase 0 手动→Phase 1 半自动→Phase 2 全自动→Phase 3 自我进化（真源：17 号文） |
| 行业对标（13 个公开系统） | R&D-Agent-Quant / QuantEvolve / Hubble / FactorMAD / TiMi / ProFiT / CogAlpha / FactorMiner / FinRL-X / Dnalyaw 等（明细真源在 12/13 号文引用的场内设计资产） |

---

## 十、修订记录

| 日期 | 版本 | 变更 | 原因 |
|------|------|------|------|
| 2026-08-17 | 0.1.0 | 初版：外部对标分析 + 差距矩阵 | 新建 09_ai_architecture |
| 2026-08-17 | 0.2.0 | 修正结论："项目缺失"→"设计已有，缺施工"；新增模块工厂落地性分析；删除不可二元判定的成功标准表格 | 发现场内设计资产已包含大量自我进化设计 |
| 2026-08-17 | 0.3.0 | 加入 frontmatter+开放问题+修订记录；增加过度工程标注（Swarm 属远期/个人项目不适用）；增加更新策略说明 | 按 AI_review 方法论规范文档结构 |
| 2026-08-17 | 0.4.0 | 移除对场外草稿目录的引用，相关编号改纯文字描述 | 用户裁定草稿目录待删除 |
| 2026-08-17 | 0.5.0 | 深度填充：14 个框架/实践按深度分级逐段展开（为什么对标/对本项目的映射/考虑过的替代方案）；新增 §1.1~1.3 现状快照+已施工设施盘点+深度分级；新增 §2.6~2.8 机构实践与量化系统速览；全部关键事实经 2026-08-17 WebSearch 复核 | AI-FILL-01 第一轮：信息库深度填充 |
| 2026-08-17 | 0.5.1 | 补完第一轮中断处：续写 §5 模块工厂落地性评估（含成本/容量内嵌新约束）、§6 不做什么、§7 前沿演进方向（7.1 已核实动态+7.2 跟踪清单）、§8 开放问题（Q1~Q4 按现状核实更新）、§9 参考来源（补 arXiv 编号与版本口径）、§10 修订记录 | AI-FILL-01 第二轮补完 |

---

*维护者：AI 架构协调者*
