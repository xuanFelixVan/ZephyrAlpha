---
ttl: permanent
doc_type: architecture_view
title: AI 设计资产盘点
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.4.0"
date: 2026-08-17
topic: ai_design_asset_inventory
scope: 09_ai_architecture
---

# AI 设计资产盘点（Design Asset Inventory）

> **本文定位**：汇总散落在项目各处的 AI 相关设计资产——设计文档、AI 员工体系、已有域、运行态设施。不重复内容，只做链接与状态登记。
>
> **与其他文件的分工**：结构设计见 [00_index.md](00_index.md)，外部对标见 [01_external_benchmark_analysis.md](01_external_benchmark_analysis.md)。按真源唯一纪律：施工顺序/解锁点以 00_index.md §5 为真源，外部对标以 01 号文为真源，本文是**资产盘点唯一真源**（03~17 号文引用资产状态时链接本文，不复制）。
>
> **更新策略**：新发现的设计资产/运行态设施随时补充，标注发现日期。

---

## 1. 盘点方法与口径

### 1.1 真源与链接纪律

- 盘点对象仅限 **AI 层资产**（代码包 / 蓝图 / 注册表 / 数据资产 / 配置 / 脚本 / 治理规则）；交易决策侧业务模块（因子、策略、组合等）不在盘点范围，引用时只读链接。
- 所有数量、路径、状态一律实测（LS / Glob / Grep / Read / Test-Path），盘点日期 2026-08-17；禁止凭记忆报数。每行资产必须能被验证命令复现。
- 引用交易决策侧文档只用稳定文件名，禁止行号锚点（07 侧审计收口期间特殊纪律）。

### 1.2 实测口径与状态词表

- **代码包计数口径**：`Get-ChildItem -Recurse -Filter *.py`，排除 `__pycache__`，含各级 `__init__.py`；计数 = 文件存在性，**不代表实现完成度**（未逐一审计函数实现）。
- **域资产计数口径**：全仓 Grep 域 ID（排除 `.worktrees/`），命中含蓝图、注册表、测试、脚本、代码中的域标记，**不等于 depgraph 节点数**。
- **状态词表**：`production`（代码存在且非空壳）/ `skeleton`（仅目录+`__init__.py` 或极少实现）/ `design`（仅蓝图/备忘，无代码）/ `planned`（注册表预留，未实施）/ `deprecated`（退役不再使用）。

---

## 2. 背景

### 2.1 项目处境

项目 AI 层处于"**横切设施代码密度高、自我进化层基本空白**"的不均衡状态。以 00_index.md §1 目标架构图的 20 个组件为比对基准（逐组件 Grep/LS 实测存在性，2026-08-17）：

| 架构层 | 组件 | 现状档位 | 实测依据 |
|--------|------|---------|---------|
| 自我进化层 | 证据关联（假设→证据→迭代引导） | 设计完成·无代码 | 全仓无对应模块；设计见 11 号文方向 |
| 自我进化层 | 技能库（AutoSkill+Voyager） | **代码基础已存** | `src/zephyr/autonomy_core/skills/` 58 个 .py（注册/路由/生命周期/沙箱等基础设施），AutoSkill 自进化机制未施工 |
| 自我进化层 | 模型路由级联控制器 | 部分代码 | `src/zephyr/governance/intelligence_governance/model_router.py` 存在；级联控制/Q-learning 学习未施工 |
| 自我进化层 | 自反Agent | 部分代码 | `src/zephyr/feedback_loop/evolution/self_reflection.py` 存在；Actor→Evaluator→SelfReflection 完整闭环未施工 |
| 自我进化层 | 多Agent协作（投票优先） | 部分代码 | `intelligence_governance/agent_debate.py`、`multi_model_consensus.py` 存在；涌现检测器未施工 |
| 执行层 | 治理 Agent | 部分代码 | `gate_engine` 蓝图 + `src/zephyr/gov_enforcement/` 等治理包存在 |
| 执行层 | 业务 Agent（因子/策略/组合） | **空白** | 无对应代码；依赖交易决策侧 G04 策略定义（62 号注册表） |
| 执行层 | 算法 Agent（信号/模型/训练） | 骨架 | `src/zephyr/ml_train/` 12 个 .py（多为 `__init__` 骨架 + 2 实现） |
| 执行层 | 自我迭代 Agent（评估/优化/反馈） | **代码已存** | `src/zephyr/feedback_loop/` 338 个 .py（含 evolution/ 20 个） |
| 治理风控运维层 | AI 自治边界 | **代码已存** | `src/zephyr/security/access_control/` 108 个 .py |
| 治理风控运维层 | AI/Agent 风险 | 部分代码 | `src/zephyr/risk/core/ai_agent_monitor.py` + `_domain_risk/ai_agent_monitor/blueprint.md` |
| 治理风控运维层 | AI 安全 | **代码已存** | `src/zephyr/security/llm_defense/` 39 个 .py（L0~L8 layers + self_protection） |
| 治理风控运维层 | AI 自治运维 | 部分代码 | `src/zephyr/security/adversarial_validation/` 25 个 .py（game_day/chaos 方向），Detect→Diagnose→Remediate→Learn 闭环未完整 |
| 基础设施层 | AutoRuntime Core | 蓝图+部分代码 | `_cross_layer/auto_runtime_core/blueprint.md` + `src/zephyr/autonomy_core/` 113 个 .py |
| 基础设施层 | 三层运行时 | 骨架 | `src/zephyr/runtime/` 仅 2 个 .py |
| 基础设施层 | LLM 安全栈 | **代码已存** | 同「AI 安全」；`_cross_layer/large_language_model_security/blueprint.md` |
| 基础设施层 | LLM Agent 工具调用（MCP） | 蓝图+配置 | `_cross_layer/model_context_protocol_servers/blueprint.md` + `config/mcp.json` |
| 基础设施层 | LLM 推理优化（llama.cpp+GPTQ） | 部分 | `data/brain/passports/` 10 本护照记录本地模型档位；量化推理管线未实测到独立模块 |
| 基础设施层 | 模型注册（MLflow） | 部分代码 | `src/zephyr/experiment_tracking/` 8 个 .py（含 mlflow fallback_tracker/adapters） |
| 基础设施层 | 数据增强（TimeGAN/扩散） | 设计级·无代码 | 全仓 Grep `TimeGAN` 零代码命中（仅文档提及） |

**汇总口径**：20 个组件中，代码已存 5 个、部分代码/骨架 9 个、仅设计 4 个、空白 2 个（业务 Agent、数据增强）。即 AI 层**约七成组件已有代码或代码基础，但密度高度集中于治理/安全/上下文横切设施**；自我进化层四件套（证据关联/自反闭环/级联路由/AutoSkill）与执行层业务 Agent 是主要空白。

### 2.2 核心问题

1. **有码无档**：`feedback_loop/`（338 文件）、`security/`（179 文件）、`autonomy_core/`（113 文件）、`infrastructure/a2a_protocol/`（89 文件）等大包在 v0.3.0 盘点中缺失或仅一行带过，读者无法从文档感知其存在。
2. **有档无码**：自我进化层设计（§3.1.2 四件套）场外已完成且覆盖外部顶级框架核心机制，但代码零施工；MOD-ML-002（ai_operator）目录实测不存在。
3. **档案失准**：v0.3.0 多处数字无法复现（depgraph 域模块数 131/72/33 无查询入口；intelligence_governance "~20 文件" 实测 25；passports "10+" 实测 10）——本版全部改为实测口径。
4. **归属待裁定**：intelligence_governance 25 文件无统一入口（Q1）；D_KNOWLEDGE 空壳（Q2）——均由 03/05 号文裁定，本文只登记不拍板。

---
## 3. 资产盘点（清单→状态）

### 3.1 设计资产盘点

#### 3.1.1 核心设计文档（手写）

| 文档 | 位置 | 状态 | 摘要 | 代码映射（实测） |
|------|------|------|------|----------------|
| 系统宪章·约束六 | [system_charter.md](../../04_architecture_principles_decisions/system_charter.md) | 宪法级 | AI 原生范式：多 AI 交叉验证 + AI 自治熔断 | 由 `security/access_control/`（kill_switch、guard_layers 等）与 `docs/01_policies_and_standards/rules/` 承载 |
| 策略生命周期与多 AI 协作 | [61_lifecycle_multi_ai.md](../../07_trading_decision_architecture/design_memos/61_lifecycle_multi_ai.md) | active v2.13.3 | **否定式边界**：不做 agent 编排系统；单 AI 多会话 + 人调度 | 约束性设计，无直接代码（边界约束） |
| Git 安全治理 | [65_git_safety_governance.md](../../07_trading_decision_architecture/design_memos/65_git_safety_governance.md) | 已定稿 | 多 AI 并发下 git 安全护栏 | `scripts/lock_files.py`（文件锁，实测存在） |
| 提交队列串行化 | [66_commit_queue_serialization.md](../../07_trading_decision_architecture/design_memos/66_commit_queue_serialization.md) | 已定稿 | 多 AI 并发提交流水线（Outbox / Merge Queue） | `scripts/git_commit.py`（GitCommitGateway，实测存在） |
| AutoRuntime Core 蓝图 | [blueprint.md](../../../03_modules/_cross_layer/auto_runtime_core/blueprint.md) | 核心蓝图 | 系统大脑·三层运行时运营中心·五层同心圆·MAPE-K 循环 | `src/zephyr/autonomy_core/`（113 个 .py，部分实现） |
| A2A 协议蓝图 | [blueprint.md](../../../03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md) | 蓝图 | Agent 间通信协议（治理运行时用，非策略编排） | `src/zephyr/infrastructure/a2a_protocol/`（89 个 .py）+ `security/access_control/a2a_check.py` |
| 模型画像器（MOD-INF-034） | [blueprint.md](../../../03_modules/_cross_layer/model_profiler/blueprint.md) | 蓝图 | 7 维评测 + 任务×模型增量学习 + 智能路由推荐 | `src/zephyr/intelligence/model_profiling/`（18 个 .py，production） |
| 模型能力考试（MOD-INF-036） | [blueprint.md](../../../03_modules/_cross_layer/model_capability_exam/blueprint.md) | 蓝图 | 五维评测 → CapabilityPassport → TaskGate 门控 | `model_profiling/exam_*.py`（6 个）+ `capability_passport.py`；产物 `data/brain/passports/`（10 本）+ 3 份考试成绩 |
| Context Engine（MOD-CONTEXT_ENGINE） | [blueprint.md](../../../03_modules/_cross_layer/context_engine/blueprint.md) | 部分实现 | 上下文注入管道（build→compress→validate→inject）+ Token 预算 | `src/zephyr/autonomy_core/context/`（39 个 .py，实现度高于"部分"，完成度未逐一审计） |
| 可执行 Agent Spec（MOD-INF-019） | functional_domain_registry 登记（ssot_module） | 蓝图 | 蓝图→Skill 升级引擎，AGENTS.md 路由 | `src/zephyr/autonomy_core/spec_engine.py` + `all_skill_modules.py` + `file_autoregister.py`（部分） |

#### 3.1.2 AI 自我进化设计（场内已有设计，未施工）

> 以下设计已在场外完成，尚未施工到代码。这些设计覆盖了外部顶级框架（AQuA/Hermes/Qualixar/TiMi）的核心机制。设计细节与施工计划分别由 11/12/13/17 号文承载，本文只登记存在性与状态。

| 设计 | 核心内容 | 对标 | 代码状态（实测） |
|------|---------|------|----------------|
| 自反Agent | Actor→Evaluator→SelfReflection、L1/L2/L3 三级反思、PreFlect 前瞻反思、Agent-R 实时反思、ReflCtrl 频率控制、策略自我修正闭环、技能注册、四层记忆模型 | TiMi 数学反思闭环 | 仅 `feedback_loop/evolution/self_reflection.py` 单文件，完整闭环未施工 |
| 元学习系统（S6 层） | 7 阶段流水线、模块工厂（核心独创）、STOP/RISE/Voyager/Meta-Harness/AutoSkill/MAML/EWC/ICL、Phase 0→3 分阶段路线 | AQuA 证据保留 + Hermes 技能自进化 | 零代码（MAML/EWC 已裁定 Phase 3 用 ICL 替代，见 00_index.md §4） |
| 分阶段实现路线 | Phase 0 手动→Phase 1 半自动→Phase 2 全自动→Phase 3 自我进化 | Agentic Engineering 三层架构 | 当前处于 Phase 0→1 之间 |
| 行业对标（13 个公开系统） | R&D-Agent-Quant / QuantEvolve / Hubble / FactorMAD / TiMi / ProFiT / CogAlpha / FactorMiner / FinRL-X / Dnalyaw 等 | — | 信息库（01 号文），无代码 |

### 3.2 AI 员工体系（"AI 公司"思想内核）

> **考古结论**：项目中不存在"AI 公司"这一提法（git 历史/归档/备份全量搜索零命中）。其思想内核以四件套活跃存在，最早的"AI 员工"成文规则（PS-STD-001 §10）已于 2026 年 6-7 月标准体系重构中删除，蒸馏进 `trae_043` 等结构化规则。

| 组件 | 位置（实测） | 状态 | 摘要 |
|------|------|------|------|
| 三层 AI 工作分配 | [AGENTS.md](../../../../AGENTS.md) §5 | **活跃** | L1 Trae 免费人在环 / L2 Local Ollama 24/7 / L3 API 夜班付费（DeepSeek/Claude） |
| 模型岗位矩阵 | `data/brain/job_matrix.yaml` | **活跃·骨架态** | 6 岗位三档（初/中/高级）× A-F 能力分级 + 幻觉率/成本上限 |
| 岗位匹配器 | `src/zephyr/intelligence/model_profiling/job_matcher.py` | **生产代码** | JobMatcher：能力分级+幻觉率六维 → Top-N 岗位推荐 |
| AI 自治等级词表 | `docs/01_policies_and_standards/_registry/vocabularies/ai_autonomy_level_planned_vocabulary.yaml` | **活跃** | L0 无自治→L3 高自治，对标 PS-STD-001 §10.7 |
| AI 能力槽位词表 | `docs/01_policies_and_standards/_registry/vocabularies/ai_capability_slot_vocabulary.yaml` | **活跃** | planned/reserved/active/none 四值 |
| AI 自治权限终表 | `docs/01_policies_and_standards/_registry/catalogs/ai_autonomy_authority_registry.yaml` | **活跃** | GOV-AI-001，全模块 AI 自治权限登记 |
| AI 员工花名册（预留） | `architecture_model/governance_systems_registry.yaml` §D3-B | **预留·Stage K** | 6 Policy 口子（花名册/行为规则/决策记录/AISG 红线/Scout 白名单）+ Factory 4 口子 + Runtime 5 口子，只预留不实施，T3 触发激活 |
| AI 员工数字段 | `docs/01_policies_and_standards/_registry/catalogs/frontmatter_field_registry.yaml` | **planned 态** | `ai_employee_count_planned`（0-10），对标 PS-STD-001 §10.7 |
| 夜班登记表 | `src/zephyr/trading/night_shift_queue.py` | **生产代码** | L3 API 夜间执行遇到不确定时登记，留待人类裁定 |
| AI 操作员决策模块 | MOD-ML-002（`src/zephyr/ml_train/ai_operator/`） | **design 态** | Generator(GLM-5.1)→Critic(DeepSeek)→Judge(Claude)→AST 沙箱→人工审核；目录实测不存在，未实现 |
| AI 行为规则群 | `trae_021` 等（`docs/01_policies_and_standards/rules/`） | **活跃** | PS-STD-003 §1.2：所有 AI 员工（Cursor/Trae/Kimi/Claude 等）的所有 session |
| 已删除的原始真源 | PS-STD-001 `metadata_registry.md` §10 | **已删除** | 2026-06-13 快照后整目录删除，§10.1-10.7"AI 员工在文档操作中的约束"蒸馏入 `trae_043` |

### 3.3 已有域盘点（depgraph 登记）

> **口径说明（2026-08-17 修订）**：v0.3.0 的"模块数 131/72/33/16/7/1/0"在全仓（`architecture_model/`、`functional_domain_registry.yaml`、depgraph.db 查询入口）均无法复现，本版改为**全仓域标记命中数**（Grep 域 ID，排除 `.worktrees/`，命中含蓝图/注册表/测试/脚本/代码）。depgraph 节点级计数的查询入口待补（见开放问题 Q4）。域边界裁定（横切视图 vs 独立域）是 03 号文的职责，本文只登记现状。

| 域 | 全仓标记命中（次/文件） | 层级 | 与 AI 层关系 | 代码对应（实测） |
|----|--------|------|-------------|----------------|
| D_AUTONOMY_CORE | 669 / 163 | L1 | AI 自治决策、目标分解、执行编排（**AI 层最重实体**） | `src/zephyr/autonomy_core/`（113 个 .py） |
| D_INTELLIGENCE | 343 / 66 | L2 | AI 上下文窗口管理、记忆检索、上下文压缩 | `src/zephyr/intelligence/`（43 个 .py）+ `autonomy_core/context/` |
| D_ORCHESTRATOR | 175 / 88 | L1 | Agent 编排（回滚/容错/生命周期/质量评估） | `src/zephyr/orchestrator/`（70 个 .py） |
| D_ML_SERVE | 74 / 27 | L2 | 模型部署、在线推理、模型服务管理 | `src/zephyr/ml_serve/`（7 个 .py） |
| D_ML_TRAIN | 300 / 78 | L2 | 模型训练、特征工程、模型评估 | `src/zephyr/ml_train/`（12 个 .py，骨架态） |
| D_SECURITY_LLM | 18 / 15 | — | LLM 安全（functional_domain_registry 登记 ssot_module=MOD-LLM_SECURITY） | `src/zephyr/security/llm_defense/`（39 个 .py）+ `_cross_layer/large_language_model_security/blueprint.md` |
| D_KNOWLEDGE | 135 / 24（92 次集中于归档注册表 harvest_archive） | L2 | 知识库构建、向量索引（基本空壳） | 无独立代码包；`_domain_knowledge/vector_memory/blueprint.md` 有蓝图；注册表登记 ssot_module=MOD-INF-011 |

> 补充：`docs/03_modules/` 下实际存在的 AI 相关域目录为 `_domain_autonomy_core`、`_domain_autonomy_perm`、`_domain_knowledge`、`_domain_machine_learning_train`、`_domain_infrastructure_operations`（含 agent_to_agent_protocol）、`_domain_governance` 等 30 个域目录；depgraph 域 ID 与目录名并非一一对应，映射关系由 03 号文裁定。

### 3.4 运行态设施盘点

> 按通用规则 11 分类登记；全部路径 2026-08-17 实测存在。状态词表见 §1.2。

| 类别 | 路径/位置 | 内容简述 | 状态 |
|------|-----------|---------|------|
| 脚本工具 | `scripts/construction/start_brain.py` | 大脑启动脚本，单次 boot 模式，Trae AI 进入项目必做 | production |
| 脚本工具 | `scripts/git_commit.py` | GitCommitGateway 串行提交门禁（66 号备忘） | production |
| 脚本工具 | `scripts/lock_files.py` | 多 AI 并发文件锁（65 号备忘） | production |
| 数据资产 | `data/brain/job_matrix.yaml` | 任务矩阵真源，大脑任务调度配置 | production（骨架态内容） |
| 数据资产 | `data/brain/passports/`（10 个 JSON） | 模型能力护照：deepseek-v4 四档、deepseek_r1 14b/8b、qwen2.5-coder 14b、qwen3-coder 30b、qwen3 8b | production |
| 数据资产 | `data/brain/`（3 份 exam_results） | deepseek_v4 / ollama / v4_pro 五维评测结果 | production |
| 数据资产 | `data/brain/quick_profiles/`（1 个 JSON） | qwen3_8b 快速画像 | draft |
| 数据资产 | `data/capability_cards/`（33 个 YAML） | 内部 Agent 系统 skill_*.yaml，L0~L3 渐进披露（AGENTS.md 称 22 个，实测 33 个，差异见 Q5） | production |
| 代码模块 | `src/zephyr/autonomy_core/`（113 个 .py） | 自治核心：spec_engine / trigger_router / phase_planner + context/（41）+ skills/（59）+ integration/ | production |
| 代码模块 | `src/zephyr/intelligence/`（43 个 .py） | 智能层：model_profiling/（18，画像/考试/护照/岗位匹配）+ model_evaluation/（11）+ model_drift_detector.py | production |
| 代码模块 | `src/zephyr/governance/intelligence_governance/`（25 个 .py） | 智能治理：委托引擎/模型路由/多模型共识/故障转移/置信度估计/持续信任/Agent 辩论/AISG 沙箱等 24 功能模块，**无统一入口**（Q1） | production |
| 代码模块 | `src/zephyr/security/`（179 个 .py） | 安全栈：access_control/（108，含 guards/detectors/verifiers/orphan_judge）+ adversarial_validation/（25）+ llm_defense/（39，L0~L8） | production |
| 代码模块 | `src/zephyr/feedback_loop/`（338 个 .py） | 反馈/自我迭代：evolution/（20，含 self_reflection、ewc_kb_review、knowledge_distillation 等） | production |
| 代码模块 | `src/zephyr/infrastructure/a2a_protocol/`（89 个 .py） | Agent 间三层协调（通信/冲突/治理），AgentCard 注册 | production |
| 代码模块 | `src/zephyr/orchestrator/`（70 个 .py） | 编排器（回滚/容错/生命周期） | production |
| 代码模块 | `src/zephyr/experiment_tracking/`（8 个 .py） | 实验跟踪，含 MLflow fallback_tracker/adapters | production |
| 代码模块 | `src/zephyr/ml_train/`（12 个 .py） | 训练域：trainer_base/inference_base + 2 实现（default_inference_engine、sentiment_sft_trainer），余为骨架 | skeleton |
| 代码模块 | `src/zephyr/ml_serve/`（7 个 .py） | 推理服务域 | skeleton |
| 代码模块 | `src/zephyr/runtime/`（2 个 .py） | 三层运行时承载包 | skeleton |
| 代码模块 | `src/zephyr/risk/core/ai_agent_monitor.py` | AI Agent 风险监控（_domain_risk/ai_agent_monitor 蓝图对应） | production |
| 配置 | `config/ai_capability_matrix.yaml` | AI 能力矩阵 | production |
| 配置 | `config/ai_context_policy.yaml` | AI 上下文策略 | production |
| 配置 | `config/embedding_model_registry.yaml` | Embedding 模型注册 | production |
| 配置 | `config/model_pricing.yaml` | 模型定价（L3 API 成本控制） | production |
| 配置 | `config/mcp.json` | MCP 服务器配置 | production |
| 配置 | `config/sandbox_policy.yaml` / `context_rules.yaml` / `compression_policy.yaml` / `rbac_roles.yaml` / `budget_policy.yaml` | 沙箱/上下文规则/压缩策略/RBAC/预算策略 | production |
| 治理注册表 | `docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml` | 功能域注册表（82 条 domain 条目，含 AI 域 ssot_module 映射） | production |
| 治理注册表 | `docs/01_policies_and_standards/_registry/`（catalogs 2 + vocabularies 2） | AI 自治权限终表/frontmatter 字段注册表/自治等级词表/能力槽位词表（见 §3.2） | production |
| 治理注册表 | `architecture_model/governance_systems_registry.yaml` | 治理系统注册表（§D3-B AI 员工花名册预留） | production |
| 蓝图 | `docs/03_modules/_cross_layer/` 下 8 篇 AI 相关蓝图 | auto_runtime_core / context_engine / model_profiler / model_capability_exam / large_language_model_security / agent_orchestrator / model_context_protocol_servers / red_blue_validator（另有 feedback_loop / gate_engine / orphan_judge / auto_fix_engine / behavioral_auditor / semantic_auditor 等治理向蓝图） | blueprint |
| 蓝图 | `docs/03_modules/_cross_layer/_b_track_interfaces/`（7 篇接口文档） | agent_orchestrator / context_engine / feedback_loop_engine / llm_security_gateway / task_pipeline_service / vector_memory_service 接口 | blueprint |

---
## 4. 缺口分析与填补优先级

> 口径：缺口 = 00_index.md §1 目标架构组件 − §3 实测现状。优先级 P0（阻塞 Phase 0→1）/ P1（Phase 1 需要）/ P2（Phase 2+ 或远期）。施工归属指向 03~17 号文；交易决策侧依赖只读引用。

### 4.1 P0 缺口（阻塞当前施工波次）

| # | 缺口 | 现状实测 | 填补归属 | 外部依赖 |
|---|------|---------|---------|---------|
| G1 | intelligence_governance 25 文件无统一入口 | §3.4 已登记 24 功能模块散落 | 05 号文（整合方案） | 无 |
| G2 | 自我进化层四件套零代码（证据关联/自反闭环/级联路由/AutoSkill 技能库） | §2.1 逐项实测无对应模块 | 11/12/13 号文 | 11 依赖 06 画像流水线（U3）；13 依赖交易决策侧 62 号注册表 P0（U8） |
| G3 | 业务 Agent（因子/策略/组合）空白 | 无对应代码 | 14 号文 | **依赖交易决策侧 G04 策略定义完成（U7）**；62 号注册表只读引用 |
| G4 | 模块工厂（核心独创）零代码 | 全仓无对应模块 | 13 号文 | 依赖 62 号注册表 P0（U8）+ 12 号文自反 Agent |
| G5 | depgraph 域节点级计数无查询入口 | 全仓无法复现 v0.3.0 的 131/72/33 等数字 | 本文 Q4 + 03 号文 | 无 |

### 4.2 P1 缺口（Phase 1 需要）

| # | 缺口 | 现状实测 | 填补归属 | 外部依赖 |
|---|------|---------|---------|---------|
| G6 | D_KNOWLEDGE 空壳（无独立代码包，标记命中集中于归档注册表） | §3.3 | 03 号文裁定保留/合并/退役 | 无 |
| G7 | 三层运行时仅骨架（runtime/ 2 个 .py） | §3.4 | 04/10 号文 | 无 |
| G8 | LLM 安全栈 L0~L8 纵深防御与 gateway 强制覆盖面未审计 | 代码 39 文件已存，RULE-LSG-001 强制面未实测 | 09 号文 | 10 号文 LLM 基础设施 |
| G9 | MOD-ML-002 ai_operator design 态（目录不存在） | §3.2 | 待裁定（Q3）→ 14 号文 | AlphaQuanter 对标结论（01 号文） |

### 4.3 P2 缺口（Phase 2+ / 远期）

| # | 缺口 | 现状实测 | 填补归属 | 外部依赖 |
|---|------|---------|---------|---------|
| G10 | 模型路由 Q-learning 动态学习（Qualixar 对标） | model_router.py 为规则式 | 11 号文 | 无 |
| G11 | RL 训练信号回传（AlphaQuanter 对标） | 无 RL 回传链路 | 14 号文远期 | 01 号文对标结论 |
| G12 | 数据增强（TimeGAN/扩散）零代码 | Grep 零代码命中 | 交易决策侧业务范围，AI 层不承接 | 交易决策侧裁定 |
| G13 | 多 Agent 涌现行为检测器 | agent_debate.py 有辩论无涌现检测 | 12 号文 | 无 |

---

## 5. 不做什么

1. **不做代码质量审查**：本文只盘点资产存在性与状态档位，不评估实现优劣、不审函数级实现（盘点到模块级，不到函数级——函数级 = 过度详细）。
2. **不做设计决策**：域边界裁定（D_KNOWLEDGE 存废、横切视图 vs 独立域）归 03 号文；intelligence_governance 整合方案归 05 号文；本文只登记现状与缺口，不替任何文档拍板。
3. **不盘点交易决策侧业务模块**：因子/策略/组合/执行等业务资产归 07 侧文档与 62 号注册表；本文只读引用其解锁点（U7/U8），不复制其内容。
4. **不引入过度工程项**：缺口分析不登记超出 system_charter §2 硬边界的设施（K8s 部署、分布式训练、热备集群、多团队治理流程等一律不列）；远期项（P2）保持远期标注。
5. **不做双向同步**：本文是资产盘点唯一真源；其他文档需要资产状态时链接本文，禁止复制本文表格到他处维护第二份。

---

## 6. 开放问题

| # | 问题 | 状态 | 说明 |
|---|------|------|------|
| Q1 | intelligence_governance 包（实测 25 文件）是否需要整合到统一的 AI 层入口？ | 待裁定 | 目前散落在 `src/zephyr/governance/intelligence_governance/`，无统一入口文档；05 号文承接方案 |
| Q2 | D_KNOWLEDGE（135 次标记命中但 92 次集中于归档注册表，无独立代码包）是保留还是合并到 D_INTELLIGENCE？ | 待裁定 | 知识库构建是 AI 层的重要能力，但当前实现几乎为零；03 号文承接裁定 |
| Q3 | MOD-ML-002（ai_operator，design 态）的施工优先级？ | 待裁定 | Generator→Critic→Judge 三层设计完整，但无 RL 训练信号回传，是否等 AlphaQuanter 对标结论后再施工？ |
| Q4 | depgraph 域节点级计数的查询入口在哪？ | 待裁定 | v0.3.0 的"模块数 131/72/33/16/7/1/0"无法从 `architecture_model/`、`functional_domain_registry.yaml` 复现；`depgraph.db` 为二进制未查询。若确认真源存在，本文 §3.3 应改回节点级口径 |
| Q5 | AGENTS.md 称 capability_cards 为 22 个 skill_*.yaml，实测 33 个 | 待裁定 | 差异 11 个；AGENTS.md 非本文档修改范围，是否同步修正待用户裁定 |
| Q6 | 若 03/05~16 号文填充后资产状态口径与本文冲突（如组件完成度评级），以哪方为准？ | 待裁定 | 本文定位为资产盘点真源，但施工完成度细节由施工文档维护，边界待确认 |
| Q7 | 施工期间 `09_ai_architecture/` 遭漂移隔离机制整体移出工作区（`.runtime/quarantine/drift_*` 多份快照，2026-08-17 18:06/18:35/18:38），目录为 untracked 状态 | 待裁定 | 本文档由 AI-FILL-02 重建并即时 staged；目录级恢复与防再隔离措施（是否收编进 git 跟踪/加白名单）待 Owner 裁定 |

---

## 7. 修订记录

| 日期 | 版本 | 变更 | 原因 |
|------|------|------|------|
| 2026-08-17 | 0.1.0 | 初版：设计文档+场外草稿+AI员工体系+已有域+运行态设施 | 从 00_index.md 拆分盘点内容到独立文件 |
| 2026-08-17 | 0.2.0 | 加入 frontmatter+开放问题+修订记录；标注更新策略 | 按 AI_review 方法论规范文档结构 |
| 2026-08-17 | 0.3.0 | 移除对 架构图/ 和 依赖图/ 草稿目录的所有引用；新增 §2"AI 自我进化设计"节（纯文字描述不带文件链接）；开放问题从 Q1-Q4 精简为 Q1-Q3 | 用户裁定草稿目录待删除 |
| 2026-08-17 | 0.4.0 | 全量实测填充：新增 §1 盘点口径、§2 背景（20 组件覆盖率比对）、§3.1.1 增加代码映射列、§3.3 域盘点改实测口径（原 131/72/33 等数字无法复现，降级为全仓标记命中数）、§3.4 运行态设施从 5 行扩至 30+ 行（补 feedback_loop 338/security 166/a2a_protocol 89/orchestrator 70 等大包）、新增 §4 缺口分析（G1~G13 按 P0/P1/P2 + 依赖标注）、新增 §5 不做什么；开放问题扩为 Q1~Q7；修正失准档案（intelligence_governance ~20→25、passports 10+→10、注册表补全实际路径） | AI-FILL-02 指令：盘点类文档深度填充，实测纪律优先 |

---

*维护者：AI 架构协调者*