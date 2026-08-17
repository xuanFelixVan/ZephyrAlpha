---
ttl: permanent
doc_type: architecture_view
title: AI 设计资产盘点
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.5.1"
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
- **域资产口径**：域清单以 `docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml`（v0.4.0，2026-07-19，自述为全 63 域统一真源；实测 82 条 entry / 63 个唯一 domain 值）为真源；全仓标记命中数（Grep 域 ID）仅作热度参考，**不等于 depgraph 节点数**。
- **状态词表**：`production`（代码存在且非空壳）/ `skeleton`（仅目录+`__init__.py` 或极少实现）/ `design`（仅蓝图/备忘，无代码）/ `planned`（注册表预留，未实施）/ `deprecated`（退役不再使用）。

### 1.3 场外参考快照的核实结论（只读引用，不作真源）

任务提供的两份场外参考位于 `.runtime/aidrafts/09_drafts_audit/依赖图/`，经抽样核实**不作盘点真源**，仅作历史快照：

| 快照 | 规模（实测） | 核实结论 |
|------|-------------|---------|
| `场内模块清单.csv` | 2434 行（路径/类型/blueprint_id 三列） | AI 相关行抽样 200 行，**134 行路径当前不存在**（如 `src/zephyr/model_profiler/`、`src/zephyr/vector_memory/`、`src/zephyr/agent_rbac/` 等顶层路径当前不存在，对应实体现址为 `intelligence/model_profiling/`、`integration/vector_memory/`、`security/access_control/`）——快照生成时点早于多轮包迁移，blueprint_id 映射思路可借鉴，路径清单不可直接采用 |
| `project-entity-depgraph.yaml` | 28 域 / 138 边（metadata 自述 2026-05-22 生成） | 域 ID 为连字符格式（`D-AUTONOMY-CORE`），与注册表下划线格式（`D_AUTONOMY_CORE`）不一致；28 域口径与注册表 63 域口径差异大——以注册表为域真源，该快照仅反映 2026-05 时点的域划分草案 |

> 处置：本文所有数字以 2026-08-17 当日实测为准；场外快照是否按当前代码树重生成，见开放问题 Q10。

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
| 执行层 | 治理 Agent | **代码基础已存** | `gate_engine` 蓝图 + `src/zephyr/gov_enforcement/` 185 个 .py（commit_gates 102 / rule_enforcement 57 / rule_bridge 13 / behavioral_admission 12） |
| 执行层 | 业务 Agent（因子/策略/组合） | **空白** | 无对应代码；依赖交易决策侧 G04 策略定义（62 号注册表） |
| 执行层 | 算法 Agent（信号/模型/训练） | 骨架 | `src/zephyr/ml_train/` 12 个 .py（多为 `__init__` 骨架 + 2 实现） |
| 执行层 | 自我迭代 Agent（评估/优化/反馈） | **代码已存** | `src/zephyr/feedback_loop/` 338 个 .py（含 evolution/ 20 个） |
| 治理风控运维层 | AI 自治边界 | **代码已存** | `src/zephyr/security/access_control/` 108 个 .py |
| 治理风控运维层 | AI/Agent 风险 | 部分代码 | `src/zephyr/risk/core/ai_agent_monitor.py` + `_domain_risk/ai_agent_monitor/blueprint.md` |
| 治理风控运维层 | AI 安全 | **代码已存** | `src/zephyr/security/llm_defense/` 39 个 .py（L0~L8 layers + self_protection） |
| 治理风控运维层 | AI 自治运维 | 部分代码 | `src/zephyr/security/adversarial_validation/` 25 个 .py（game_day/chaos 方向），Detect→Diagnose→Remediate→Learn 闭环未完整 |
| 基础设施层 | AutoRuntime Core | 蓝图+部分代码 | `_cross_layer/auto_runtime_core/blueprint.md` + `src/zephyr/autonomy_core/` 113 个 .py |
| 基础设施层 | 三层运行时 | 骨架+部分代码 | `src/zephyr/runtime/` 2 个 .py（骨架）；L2 本地模型调用已在 `src/zephyr/integration/local_model/` 落地 6 个实现模块（ollama_chat / deepseek_chat / embedding_router / local_model_scheduler 等） |
| 基础设施层 | LLM 安全栈 | **代码已存** | 同「AI 安全」；`_cross_layer/large_language_model_security/blueprint.md` |
| 基础设施层 | LLM Agent 工具调用（MCP） | 蓝图+配置+**部分代码** | `_cross_layer/model_context_protocol_servers/blueprint.md` + `config/mcp.json` + `src/zephyr/integration/mcp/` 20 个 .py（11 个 *_server 实现 + gateway/base/rate_limiter 等基础设施） |
| 基础设施层 | LLM 推理优化（llama.cpp+GPTQ） | 部分 | `data/brain/passports/` 7 本护照记录本地模型档位；`integration/local_model/` 含 cache_layer/embedding_router；量化推理管线未实测到独立模块 |
| 基础设施层 | 模型注册（MLflow） | 部分代码 | `src/zephyr/experiment_tracking/` 8 个 .py（含 mlflow fallback_tracker/adapters） |
| 基础设施层 | 数据增强（TimeGAN/扩散） | 设计级·无代码 | 全仓 Grep `TimeGAN` 零代码命中（仅文档提及） |

**汇总口径**：20 个组件中，代码已存/代码基础已存 6 个、部分代码/骨架 11 个、仅设计 2 个（证据关联、数据增强）、空白 1 个（业务 Agent）。即 AI 层**约八成半组件已有代码或代码基础，但密度高度集中于治理/安全/上下文横切设施**；自我进化层四件套（证据关联/自反闭环/级联路由/AutoSkill）与执行层业务 Agent 是主要空白。

### 2.2 核心问题

1. **有码无档**：`feedback_loop/`（338 文件）、`security/`（179 文件）、`autonomy_core/`（113 文件）、`infrastructure/a2a_protocol/`（89 文件）、`gov_enforcement/`（185 文件）等大包需要逐包、逐子包级登记，读者才能从文档感知其内部构成。
2. **有档无码**：自我进化层设计（§3.1.2 四件套）场外已完成且覆盖外部顶级框架核心机制，但代码零施工；MOD-ML-002（ai_operator）目录实测不存在；D_AUTONOMY_PERM 注册表登记 2 条目（MOD-INF-022/024）但其 ssot_path `src/zephyr/autonomy_perm/` 实测不存在。
3. **档案随代码漂移失准**：资产数量随包迁移/模型清单变动持续变化（如 passports 当日实测 7 本、model_profiling 当日实测 24 文件、03_modules 域目录当日实测 29 个），盘点文档必须每轮重测，禁止沿用旧数。
4. **归属待裁定**：intelligence_governance 25 文件无统一入口（Q1）；D_KNOWLEDGE 与 D_INTELLIGENCE 的边界（Q2）——均由 03/05 号文裁定，本文只登记不拍板。
5. **监控类设施分散**：无 `src/zephyr/monitoring/` 顶层包；可观测/监控能力散在 `infrastructure/system_telemetry/`（25）、`infrastructure/health_monitor/`（2）、`infrastructure/observability/`（3）、`governance/observability_governance/`（6）四处（G15）。
6. **场外快照失效**：`.runtime/aidrafts/09_drafts_audit/依赖图/` 两份快照经抽样核实不可作真源（§1.3），依赖图类资产缺乏当前有效的查询入口（Q4/Q10）。

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
| 模型画像器（MOD-INF-034） | [blueprint.md](../../../03_modules/_cross_layer/model_profiler/blueprint.md) | 蓝图 | 7 维评测 + 任务×模型增量学习 + 智能路由推荐 | `src/zephyr/intelligence/model_profiling/`（24 个 .py，production，含 pipeline_routing/ 6 个） |
| 模型能力考试（MOD-INF-036） | [blueprint.md](../../../03_modules/_cross_layer/model_capability_exam/blueprint.md) | 蓝图 | 五维评测 → CapabilityPassport → TaskGate 门控 | `model_profiling/exam_*.py`（6 个：exam_orchestrator/exam_test_cases/exam_judge/exam_rubric/exam_checks/exam_executor）+ `capability_passport.py`；产物 `data/brain/passports/`（7 本）+ 3 份考试成绩 |
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

### 3.3 已有域盘点（注册表登记）

> **口径说明（2026-08-17 第二轮修订）**：域清单真源 = `functional_domain_registry.yaml`（v0.4.0，82 条 entry / 63 个唯一域）。下表覆盖注册表中与 AI 层直接相关的 13 个域（含 GOV 族归并行）；全仓标记命中数（Grep 域 ID，排除 `.worktrees/`）仅作热度参考。域边界裁定（横切视图 vs 独立域）是 03 号文的职责，本文只登记现状。

| 域 | ssot_module（注册表） | 代码路径（注册表 ssot_path） | 代码实测（.py） | 全仓标记命中（次/文件） | 与 AI 层关系 |
|----|----------------------|------------------------------|----------------|------------------------|-------------|
| D_AUTONOMY_CORE | MOD-INF-019 / MOD-INF-025 | `src/zephyr/autonomy_core/` | 113 ✔ 存在 | 669 / 163 | AI 自治决策、目标分解、执行编排（**AI 层最重实体**） |
| D_AUTONOMY_PERM | MOD-INF-022 / MOD-INF-024 | `src/zephyr/autonomy_perm/` | **✘ 目录不存在** | 137 / 17 | 自治保护（注册表有条目、无代码，Q9） |
| D_INTELLIGENCE | MOD-CONTEXT_ENGINE | `src/zephyr/intelligence/` | 43 ✔ 存在（另 `autonomy_core/context/` 39） | 343 / 66 | AI 上下文窗口管理、记忆检索、上下文压缩 |
| D_KNOWLEDGE | MOD-INF-011 | `src/zephyr/integration/vector_memory/` | 28 ✔ 存在 | 135 / 24 | 知识库构建、向量索引（代码在 vector_memory，归属裁定见 Q2） |
| D_ML_TRAIN | MOD-INF-034 / MOD-INF-036 | `src/zephyr/intelligence/model_profiling/` 等 | model_profiling 24 + model_evaluation 11 ✔；`ml_train/` 12 骨架 | 300 / 78 | 模型画像/考试/训练 |
| D_ML_SERVE | MOD-ML_SERVE | `src/zephyr/ml_serve/` | 7 ✔ 骨架 | 74 / 27 | 模型部署、在线推理 |
| D_ORCHESTRATOR | MOD-INF-039 | `src/zephyr/orchestrator/` | 70 ✔ 存在 | 175 / 88 | Agent 编排（回滚/容错/生命周期/质量评估） |
| D_SECURITY | MOD-INF-018 / MOD-INF-029 / MOD-INF-030 | `src/zephyr/security/access_control/` 等 | access_control 108 + adversarial_validation 25 ✔ | 796 / 204 | 访问控制/对抗验证（AI 自治边界承载域） |
| D_SECURITY_LLM | MOD-LLM_SECURITY | `src/zephyr/security/llm_defense/` | 39 ✔ 存在 | 18 / 15 | LLM 安全 L0~L8 |
| D_INFRA_A2A | MOD-INF-025 | `src/zephyr/infrastructure/a2a_protocol/` | 89 ✔ 存在 | 165 / 88 | Agent 间通信协议 |
| D_INFRA_TELEMETRY | MOD-INF-015 | `src/zephyr/infrastructure/system_telemetry/` | 25 ✔ 存在 | 29 / 22 | 可观测性/遥测 |
| D_FEEDBACK_LOOP | MOD-FEEDBACK_LOOP | `src/zephyr/feedback_loop/` | 338 ✔ 存在 | 279 / 144 | 反馈/自我迭代引擎（自我迭代 Agent 承载域） |
| D_BEHAVIORAL_AUDIT | MOD-INF-023 | `src/zephyr/gov_drift/detector_core/` | 8 ✔ 存在（gov_drift 全包 74） | 51 / 12 | 行为审计/漂移检测 |

> 补充一：`docs/03_modules/` 下实测 29 个 `_domain_*` 域目录，其中 AI 相关为 `_domain_autonomy_core`、`_domain_autonomy_perm`、`_domain_knowledge`、`_domain_machine_learning_train`、`_domain_infrastructure_operations`（含 agent_to_agent_protocol）、`_domain_governance`、`_domain_infrastructure_runtime`、`_domain_integration` 等；depgraph 域 ID 与目录名并非一一对应，映射关系由 03 号文裁定。
>
> 补充二：GOV 族代码治理域（注册表条目 D_GOV_ENFORCEMENT / D_GOV_DRIFT / D_GOV_AUDIT / D_GOV_CODE_QUALITY / D_GOV_RULE 等）对应 `src/zephyr/gov_enforcement/`（185）、`gov_drift/`（74）、`gov_audit/`（70）、`gov_code_quality/`（66）、`gov_rule/`（3）——AI 生成代码的治理执行设施，归入 §3.4 运行态设施。
>
> 补充三：场外快照 `project-entity-depgraph.yaml` 的 28 域口径（2026-05-22）与注册表 63 域口径不一致，不作真源（§1.3）。

### 3.4 运行态设施盘点

> 按通用规则 11 分类登记；全部路径 2026-08-17 实测存在。状态词表见 §1.2。计数口径见 §1.2（文件存在性，非完成度审计）。

#### 3.4.1 代码包逐包实测（AI 核心包）

**`src/zephyr/intelligence/`（43 个 .py，production）**——D_INTELLIGENCE 承载包：

| 子包/位置 | .py 数 | 内容（实测文件名） |
|-----------|-------|---------------------|
| `model_profiling/` | 24 | profiler / benchmark_suite / capability_passport / case_assembler / cli / deepseek_v4_chat / exam_checks / exam_executor / exam_judge / exam_orchestrator / exam_rubric / exam_test_cases / job_matcher / model_discovery / provider_data / results_writer / task_model_learner + `pipeline_routing/`（6） |
| `model_evaluation/` | 11 | unified_memory_api / reranker / inference_base / activate / _memory_backend 等 |
| 包根 | 2 | model_drift_detector.py（模型漂移检测）+ `__init__.py` |
| 脚手架子包 | 各 1 | api / core / infrastructure / models / services / _extensions |

**`src/zephyr/autonomy_core/`（113 个 .py，production）**——D_AUTONOMY_CORE 承载包：

| 子包/位置 | .py 数 | 内容（实测文件名） |
|-----------|-------|---------------------|
| 包根 | 14 | spec_engine / trigger_router / phase_planner / prompt_registry / progressive_disclosure_injector / self_evolution_fidelity_gate / skill_rbac_registry / vibe_coding_quality_gate / agent_observability / all_skill_modules / file_autoregister / ide_watcher + `__init__` / `__main__` |
| `context/` | 39 | context_assembler / context_injector / context_pipeline(+auto) / context_budget(+tracker) / memory_bank / vector_bridge / curation_loop / shadow_canary / checkpoint_manager / cold_start_booster / complexity_budget / atomic_injector / diff_injector / integrity_check / staleness_manager / ce_bootstrap 等 |
| `skills/` | 58 | skill_registry / skill_factory / skill_constructor / skill_discovery / skill_router / skill_executor / skill_evaluator / skill_lifecycle / skill_sandbox / skill_gitops / skill_learning / skill_loader / skill_model(+evolution) / skill_postmortem / skill_freshness(+ext) / skill_kill_switch / skill_guardrails / skill_security / skill_compliance / skill_canary / skill_shadow / skill_observability / skill_telemetry / skill_lineage / skill_ontology / skill_contract / skill_schema_registry / skill_economics / skill_tokenomics / skill_kya 等 |
| `integration/` | 2 | 集成适配 |

**`src/zephyr/governance/`（295 个 .py，27 个子包，production）**——治理横切大包，AI 相关子包：

| 子包 | .py 数 | 内容简述 |
|------|-------|---------|
| `intelligence_governance/` | 25 | 智能治理 24 功能模块（**无统一入口**，Q1）：delegation_engine / delegation_manager / model_router / multi_model_consensus / provider_failover / provider_base / confidence_estimator / confidence_quantifier / meta_confidence / continuous_trust / agent_debate / aisg_sandbox / ai_self_diagnosis / autonomy_dashboard / cross_agent_conflict_detector / cross_assistant_adapter / memory_provider / model_provider_data / model_version_detector / mvep_orchestrator / self_benchmark / self_test / self_validator / subagent_hook_propagator |
| `ops_governance/` | 38 | 运维治理 |
| `audit/` | 24 | 审计 |
| `security_governance/` | 22 | 安全治理 |
| `resilience_governance/` | 21 | 韧性治理 |
| `escalation/` | 20 | 升级/上抛 |
| `semantic_audit/` | 19 | 语义审计 |
| `persistence/` | 16 | 持久化 |
| `architecture_governance/` | 15 | 架构治理 |
| `context_governance/` | 14 | 上下文治理 |
| `data_governance/` | 13 | 数据治理 |
| `financial_governance/` | 13 | 财务治理 |
| `lifecycle_governance/` | 8 | 生命周期治理 |
| `observability_governance/` | 6 | 可观测治理 |
| 其余子包 | 各 1~4 | a2a / adapters / agent-rbac / agent-spec / agent_spec / audit-trail / bridges / budget-enforcer / compliance_gate_a6 / drift-detector / engine / implementations / rollback / services / strategies + 包根 6 |

**`src/zephyr/security/`（179 个 .py，production）**——D_SECURITY / D_SECURITY_LLM 承载包：

| 子包 | .py 数 | 内容（实测） |
|------|-------|-------------|
| `access_control/` | 108 | 顶层 51（kill_switch / guard_layers / immutable_core / genesis_bootstrap / bootstrap_superadmin / capability_check / decision_registry / identity / intent_binder / key_hierarchy / emergency_override / session_lifecycle / secrets_lifecycle / legal_audit_chain 等）+ `guards/` 19（abac / rbac / input / output / path / permission / memory / memory_provenance / replay_attack / rule_injection / sequence / toctou / vibe_coding / anti_pattern / audit_log / cybersec_2026 / native_api / novel_attack 等）+ `orphan_judge/` 25 + `detectors/` 7（anomaly / context_drift / cross_session / false_completion / multi_agent_collusion / shell_dialect）+ `verifiers/` 6（bootstrap / continuous / contract / micro / post_action） |
| `llm_defense/` | 39 | `llm_security/`：gateway / protocol / input_sanitizer / alignment_scorer / adversarial_robustness / behavior_audit_logger / poisoning_monitor / process_sandbox / runtime_interceptor / sensitivity_classifier / solo_dev_safety_net / lsg_pattern_tracker + `layers/`（l0_supply_chain / l1_input / l2_prompt_protection / l2a_process_sandbox / l3_output / l4_agent / l5_resource_protection / l6_data_flow / l6_observability / l8_compliance / l8_multi_agent）+ `self_protection/`（l7_validation / adversarial_mutator / code_integrity / isolation / red_team_scanner）+ `patterns/` + `dashboard/` —— **L0~L8 各层均有对应文件** |
| `adversarial_validation/` | 25 | game_day_runner / game_day_scheduler / chaos 方向：ai_attack_generator / attack_registry / blast_radius / bypass_recorder / circuit_breaker / cold_start / commit_trigger / constitution_engine / constitution_guard / convergence_checker / defense_runner / injection_engine / mcp_endpoints / scenario_loader / steady_state / validator(+event_bridge) 等 |
| 脚手架子包 | 各 1 | api / core / infrastructure / models / services / _extensions + 包根 1 |

**`src/zephyr/feedback_loop/`（338 个 .py，production）**——D_FEEDBACK_LOOP 承载包（自我迭代 Agent 主场）：

| 子包 | .py 数 | 内容简述 |
|------|-------|---------|
| `diagnosers/` | 76 | 诊断器群 |
| `detectors/` | 65 | 检测器群 |
| `gates/` | 49 | 门控群 |
| 包根 | 29 | scheduler(+_act/_collect_detect/_health/_safety) / decision_engine / evolution_engine / eval_harness / auto_evolution / self_diagnosis / session_learner / slo_manager / error_budget / fitness_functions / alert_dispatcher / backpressure_bridge 等 |
| `verifiers/` | 24 | 验证器群 |
| `collectors/` | 21 | 收集器（token_finops / llm_cost_accounting / knowledge_capture / knowledge_injection / knowledge_freshness / kb_provenance / temporal_event_store 等） |
| `evolution/` | 20 | self_reflection / auto_reward / conformal_prediction / cross_gen_validation / dynamic_threshold / ewc_kb_review / failure_replay / graduated_activation_protocol / hypernetwork / knowledge_distillation / online_feature_importance / prompt_factory_governance / prompt_optimization_regression_detector / prompt_self_optimization_loop / self_modification_rate_limiter / self_upgrade_canary / semantic_intent_preservation_guard / teacher_transfer / training_data_gov |
| `forensic/` | 19 | 取证（deterministic_replay / boot_integrity_attestation / self_modification_audit / automated_rca_postmortem_generator / sub_agent_collusion / toctou_guard / worm_write_integrity 等） |
| `actors/` | 13 | 执行器（agent_lifecycle / action_selector / alert_router / intent_driven_ops / multi_agent_orchestrator / owner_absence_escalation / saga_compensator 等） |
| `resilience/` | 10 | 韧性（deadman_switch / dr_automation / graceful_degradation_planner / multi_instance_coord / oscillation_damping / split_brain_quorum 等） |
| `security/` | 7 | wireheading_prevention / secret_rotation / remote_attestation / metric_prompt_scanner / dep_cve_correlator / agent_skill_guard |
| 其他 | 5 | docs 2 / subdir 1 / tests 2 |

**`src/zephyr/infrastructure/` 内 AI 相关子包（infrastructure 全包 321 个 .py）**：

| 子包 | .py 数 | 内容简述 |
|------|-------|---------|
| `a2a_protocol/` | 89 | D_INFRA_A2A：`layer1_discovery/` 4（agent_card / a2a_registry / identity_verifier）+ `layer2_communication/` 9（message_router / handoff_manager / streaming / context_package 等）+ `layer3_coordination/` 54（arbitrator / supervisor / a2a_voting / a2a_debate / conflict_detector / deadlock_guard / livelock_detector / cascade_guard / a2a_security / a2a_collusion_detector / a2a_consent / a2a_checkpoint 等）+ `governance/` 11 + 包根 11 |
| `rollback/` | 54 | 回滚 |
| `auto_fix_engine/` | 30 | 自动修复引擎 |
| `system_telemetry/` | 25 | D_INFRA_TELEMETRY：系统遥测 |
| `asset_inventory/` | 15 | 资产清单 |
| `capacity_assurance/` | 15 | 容量保障 |
| `pipeline/` | 15 | 管线 |
| `h1_redis_hot/` | 6 | Redis 热层 |
| `runtime/` | 5 | 运行时支撑 |
| `observability/` | 3 | 可观测 |
| `health_monitor/` | 2 | 健康监控 |
| `model_profiler/` | 1 | 占位（实体在 intelligence/model_profiling） |
| `model_capability_exam/` | 1 | 占位（实体在 intelligence/model_profiling） |

**`src/zephyr/integration/` 内 AI 相关子包（integration 全包 76 个 .py）**：

| 子包 | .py 数 | 内容简述 |
|------|-------|---------|
| `vector_memory/` | 28 | D_KNOWLEDGE 代码实体：bm25_index / faiss_collection_manager / hybrid_retriever / cross_collection_retriever / chunk_strategy_router / collection_manager(+schemas) / context_ingest / provenance_enforcer / retrieval_feedback / sqlite_metadata_store / ollama_embedding / vector_bridge / vector_writer / migrate_chroma_to_faiss / bridge_layer / cache_layer / index_health_monitor / interface / delegated_vector_memory / in_process_vector_memory / vms_* 等 |
| `mcp/` | 20 | MCP 工具调用实体：gateway_server / sentinel_server / sandbox_server / blueprint_search_server / doc_guard_server / gate_engine_server / governance_server / rule_discovery_server / task_manager_server / telemetry_server / vector_memory_server + base_server / _base_server / audit_logger / error_codes / handoff_auto_loader / prompt_provider / rate_limiter / resource_provider |
| `local_model/` | 7 | L2 本地模型运行时：ollama_chat / ollama_embedding / deepseek_chat / embedding_router / local_model_scheduler / cache_layer |
| `shared/` | 12 | 共享 |
| `behavioral_admission/` | 2 | 行为准入 |
| `budget_enforcer/` | 2 | 预算执行 |

**其余 AI 相关顶层包**：

| 包 | .py 数 | 内容简述 | 状态 |
|----|-------|---------|------|
| `gov_enforcement/` | 185 | 治理执行：commit_gates/ 102 + rule_enforcement/ 57 + rule_bridge/ 13 + behavioral_admission/ 12（65/66 号备忘的代码侧承载） | production |
| `gov_drift/` | 74 | 漂移治理：detector_core/ 8（D_BEHAVIORAL_AUDIT）+ state_machine / reconciler / alert_router / runbook_generator / events / cold_start 等 | production |
| `gov_audit/` | 70 | 审计：bridges/ 8 等 | production |
| `gov_code_quality/` | 66 | AI 生成代码质量门禁 | production |
| `orchestrator/` | 70 | D_ORCHESTRATOR：execution/ 13 + lifecycle/ 10 + fault_tolerance/ 9 + governance/ 9 + quality/ 9 + contracts/ 8 + core/ 2 + resilience/ 2 + 包根 8 | production |
| `experiment_tracking/` | 8 | 实验跟踪：experiment_tracker / fallback_tracker / query / models / config + adapters/（c1_adapter）——MLflow 轻量替代 | production |
| `ml_train/` | 12 | D_ML_TRAIN：trainer_base / inference_base + implementations/（default_inference_engine / sentiment_sft_trainer 等 3） | skeleton |
| `ml_serve/` | 7 | D_ML_SERVE：推理服务 | skeleton |
| `runtime/` | 2 | 三层运行时承载包：intraday_main.py | skeleton |
| `risk/core/ai_agent_monitor.py` | 1 | AI Agent 风险监控（`_domain_risk/ai_agent_monitor/blueprint.md` 对应） | production |
| `red_blue_validator/` | 1 | 红蓝验证器（`_cross_layer/red_blue_validator/` 蓝图对应） | skeleton |
| `gov_rule/` | 3 | D_GOV_RULE | production |

#### 3.4.2 数据资产

| 路径/位置 | 内容简述 | 状态 |
|-----------|---------|------|
| `data/brain/passports/`（7 个 JSON） | 模型能力护照：deepseek-v4-flash-thinking / deepseek-v4-flash-non-thinking / deepseek-v4-pro-thinking / deepseek-v4-pro-non-thinking / qwen2.5-coder_14b / qwen3-coder_30b / qwen3_8b（deepseek_r1 无护照，见 Q8） | production |
| `data/brain/`（3 份 exam_results） | deepseek_v4 / ollama / v4_pro 五维评测结果 | production |
| `data/brain/quick_profiles/`（1 个 JSON） | qwen3_8b 快速画像 | draft |
| `data/brain/job_matrix.yaml` | 任务矩阵真源，大脑任务调度配置 | production（骨架态内容） |
| `data/capability_cards/`（33 个 YAML） | 内部 Agent 系统 skill_*.yaml，L0~L3 渐进披露（AGENTS.md 称 22 个，实测 33 个，差异见 Q5） | production |

#### 3.4.3 配置 / 脚本 / 治理注册表 / 蓝图

| 类别 | 路径/位置 | 内容简述 | 状态 |
|------|-----------|---------|------|
| 脚本工具 | `scripts/construction/start_brain.py` | 大脑启动脚本，单次 boot 模式，Trae AI 进入项目必做 | production |
| 脚本工具 | `scripts/git_commit.py` | GitCommitGateway 串行提交门禁（66 号备忘） | production |
| 脚本工具 | `scripts/lock_files.py` | 多 AI 并发文件锁（65 号备忘） | production |
| 脚本工具 | `scripts/git_guard.py` | git 操作护栏 | production |
| 脚本工具 | `scripts/governance/apply_depgraph.py` | depgraph 设计态登记脚本（status planned→production 流转） | production |
| 配置 | `config/ai_capability_matrix.yaml` | AI 能力矩阵 | production |
| 配置 | `config/ai_context_policy.yaml` | AI 上下文策略 | production |
| 配置 | `config/embedding_model_registry.yaml` | Embedding 模型注册 | production |
| 配置 | `config/model_pricing.yaml` | 模型定价（L3 API 成本控制） | production |
| 配置 | `config/mcp.json` | MCP 服务器配置 | production |
| 配置 | `config/sandbox_policy.yaml` / `context_rules.yaml` / `compression_policy.yaml` / `rbac_roles.yaml` / `budget_policy.yaml` / `error_budget_config.yaml` | 沙箱/上下文规则/压缩策略/RBAC/预算/错误预算策略 | production |
| 治理注册表 | `docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml` | 功能域注册表（82 条 entry / 63 唯一域，含 AI 域 ssot_module 映射，域真源） | production |
| 治理注册表 | `docs/01_policies_and_standards/_registry/`（catalogs 2 + vocabularies 2） | AI 自治权限终表/frontmatter 字段注册表/自治等级词表/能力槽位词表（见 §3.2） | production |
| 治理注册表 | `architecture_model/governance_systems_registry.yaml` | 治理系统注册表（§D3-B AI 员工花名册预留） | production |
| 蓝图 | `docs/03_modules/_cross_layer/` 下 17 篇 AI 相关蓝图 | auto_runtime_core / context_engine / model_profiler / model_capability_exam / large_language_model_security / model_context_protocol_servers / agent_orchestrator / audit_orchestrator / feedback_loop / gate_engine / orphan_judge / auto_fix_engine / behavioral_auditor / semantic_auditor / red_blue_validator / clone_guard / resource_optimization_engine | blueprint |
| 蓝图 | `docs/03_modules/_cross_layer/_b_track_interfaces/`（7 篇接口文档） | agent_orchestrator / context_engine / feedback_loop_engine / llm_security_gateway / task_pipeline_service / vector_memory_service 接口 + index | blueprint |

### 3.5 升级门禁与负向裁定登记（防重复评估）

> 登记目的：以下"暂缓+触发条件"门禁项与"❌ 不可建"负向裁定均为场外草稿（`.runtime/aidrafts/09_drafts_audit/架构图/`）中**已拍板的结论**，触发条件满足前不再重新评估，防止未来 AI 会话重复立项论证。源文件为历史快照（非真源），本节仅登记其裁定结论与触发条件；裁定细节以源文件条目为准。
>
> 口径：触发条件按源文件原文浓缩；约束编号对应 system_charter §2 硬边界（一=单人力 / 二=单机硬件 / 三=资金与用途）。

#### 3.5.1 升级门禁条件集（源：`架构图/Agent架构.md` §17 LP-001~021，AI 层相关 11 项）

| 门禁编号 | 暂缓设施 | 触发条件（全部满足方可重估） |
|---------|---------|------------------------------|
| LP-001 | OPA Rego 策略引擎 | ① Agent 数量 ≥8 且规则 ≥20 条；② 有第二位开发人员加入（MVP 替代：YAML 配置 + if-else 硬编码） |
| LP-002 | Agent 记忆向量检索（RAG 独立嵌入模型） | ① GPU 显存 ≥48GB；② 需要非结构化数据语义检索；③ AUM ≥500 万（MVP 替代：FAISS 轻量索引 + SQLite FTS5） |
| LP-004 | 影子模式测试 | ① GPU 显存 ≥48GB；② 多 GPU 架构；③ 或战略 Agent 影子测试走 API 推理 |
| LP-005 | EU AI Act 正式合规文档 | ① 面向欧洲客户/市场；② AUM ≥5000 万需机构级合规；③ 中国出台类似法规 |
| LP-007 | 11 个 Agent 全部 MVP 实现 | MVP 建 5 个核心 → V2 增 4 个（稳定 ≥1 月）→ V3 增 2 个（稳定 ≥2 月 + AUM ≥80 万） |
| LP-010 | Agent 密码学身份（DID + Ed25519） | ① Agent 数量 ≥15 个；② 多机部署需要跨节点身份验证；③ 安全审计要求密码学级别身份 |
| LP-011 | 内部竞赛机制（ContestTrade） | ① Agent 数量 ≥8 个（同类 Agent ≥2 才能竞赛）；② GPU 显存 ≥48GB（并行推理）；③ AUM ≥200 万 |
| LP-012 | 记忆图数据库（Neo4j / Graphiti） | ① GPU 显存 ≥48GB；② AUM ≥500 万需深度知识管理；③ 非结构化数据占比 >30% |
| LP-014 | MCP×A2A 集成框架 | ① 外部工具 ≥10 个需 MCP 统一管理；② 多 Agent 框架互操作需求；③ 有第二位开发人员加入（MVP 替代：Python SDK 直接调用，无 MCP 中间层） |
| LP-015 | Agent 365 OTel 企业级管道 | ① 多机部署需要统一遥测管道；② 企业级监控需求；③ 有第二位开发人员加入 |
| LP-016 | NeMo Guardrails IORails 并行护栏 | ① GPU ≥48GB（IORails 需并行推理）；② Agent ≥15 个；③ 有第二位开发人员加入（MVP 替代：同 LP-001 串行检查） |

> 注一：LP-003 / LP-006 / LP-008 / LP-009 / LP-013 源文件裁定为 🟢 能建，不在负向登记范围。
> 注二：LP-017~021（D-ALT-DATA / D-CROSS-ASSET / D-COMPLIANCE / D-TRADING / D-FRONTEND 五域暂缓）属交易决策侧域级门禁，本文不展开，触发条件以源文件为准。

#### 3.5.2 ❌ 负向裁定登记（源：`架构图/学习系统架构.md` §14.0 裁定总表，R-31~42 / R-64~67 / R-103~112 共 26 条）

| 裁定编号 | 裁定对象 | 负向理由（硬边界） | 重估门禁 |
|---------|---------|--------------------|---------|
| R-31 | Rust/Go 延迟分层 | 约束二（单机 Windows + Python） | GPU 集群 + Linux + 多语言编译链就绪 |
| R-32 | Agent 集群（MARL） | 约束一（单人）+ 约束二（单机） | 多机集群 + MARL 训练框架就绪 |
| R-33 | 平台化基础设施 | 约束一（单人）+ 约束三（50 万 AUM） | 多团队 + 多账户 + AUM >1000 万 |
| R-34 | EU AI Act 字面合规 | 约束三（个人使用不对外服务） | 对外提供服务或管理他人资金 |
| R-35 | TEE 可信执行环境 | 约束二（单机 Windows，无 TEE 硬件） | SGX/TDX 硬件 + Linux 就绪 |
| R-36 | 多管线并行架构（独立资金池） | 约束三（50 万 AUM 单一账户） | 多账户 + AUM >500 万 + 独立资金池 |
| R-37 | DeepSCM 深度因果模型 | 约束二（深度因果模型需 GPU 集群训练） | GPU 集群 + Linux + PyTorch 分布式训练就绪 |
| R-38 | ODL-Net 在线深度学习 | 约束二（在线深度学习需 GPU 集群） | GPU 集群 + 在线训练框架就绪 |
| R-39 | Formal Verification 形式化验证 | 约束二（SMT 求解器需专业工具链） | Z3/PySMT 集成 + 形式化验证专家就绪 |
| R-40 | Micro-Agent 微 Agent 架构 | 约束一（单人）+ 约束二（单机） | 多机集群 + 微 Agent 编排框架就绪 |
| R-41 | Synthetic Backtesting 合成回测 | 约束二（生成模型需 GPU 集群） | GPU 集群 + 扩散模型/GAN 训练框架就绪 |
| R-42 | SEC AI Trading Advisor 注册 | 约束三（个人使用不对外服务） | 对外提供服务或管理他人资金 |
| R-64 | AlphaFin 统一多模态框架 | 约束二（统一多模态模型需 GPU 集群） | 统一多模态模型量化部署方案就绪 + RTX 3090 24GB 验证通过 |
| R-65 | FinVision 端到端图表→策略 | 约束三（端到端生成绕过 DSL + AST 沙箱安全约束） | 端到端生成不绕过 DSL + AST 沙箱的安全方案设计完成 |
| R-66 | AlphaEvolve 元级基础设施进化 | 约束三（DSL 语法进化可能破坏 AST 沙箱安全约束） | DSL 语法进化不破坏 AST 沙箱安全约束的验证方案就绪 |
| R-67 | 可微因果发现（NOTEARS+） | 约束二（连续优化需 GPU 长时间训练） | RTX 3090 上 <100 变量训练时间 <4h 验证通过 |
| R-103 | Monte Carlo Engine（GPU 加速） | 约束二（GPU 加速蒙特卡洛需 GPU 集群 + CUDA 并行） | GPU 集群 + CUDA 并行计算框架就绪 |
| R-104 | VaR Calculator（蒙特卡洛 GPU） | 约束二（同 R-103） | GPU 集群 + CUDA 并行计算框架就绪 |
| R-105 | Market Digital Twin（代理人引擎 + 订单簿仿真） | 约束一（单人）+ 约束二（需多机集群 + 高频数据源） | 多机集群 + 高频数据源接入就绪 |
| R-106 | 数字孪生系列（依赖图/实时同步/混沌实验） | 约束一（单人）+ 约束二（实时同步 + 混沌实验需多机集群） | 多机集群 + 实时数据同步框架就绪 |
| R-107 | Data Mesh（域所有权/数据产品/联邦治理） | 约束一（单人）+ 约束三（需多团队 + 数据产品目录平台） | 多团队 + 数据产品目录平台就绪 |
| R-108 | CQRS/Event Sourcing 模型 | 约束二（需分布式事件存储 + 消息队列） | 分布式事件存储 + 消息队列就绪 |
| R-109 | LLM 模型分级路由（M1/M3/M7/M9 四级） | 约束二（多 GPU 推理服务器 + 模型服务化框架需集群） | 多 GPU 推理服务器 + 模型服务化框架就绪 |
| R-110 | PDF 预测引擎 | 约束二（PDF 结构化解析精度 ≥95% 需专用模型训练） | PDF 结构化解析精度 ≥95% 验证通过 |
| R-111 | A 股特色数据（五类资金追踪/政策预期） | 约束五（Level-2 数据源 + 政策事件数据库需付费数据源） | Level-2 数据源 + 政策事件数据库就绪 |
| R-112 | AI 治理框架（EU AI Act 合规） | 约束三（个人使用不对外服务） | 对外提供服务或管理他人资金 |

#### 3.5.3 场外快照一行登记（历史快照，不作真源，不重复核实）

- `依赖图/场内模块清单.csv`（2434 行）：早于多轮包迁移的历史快照，AI 相关抽样 200 行中 134 行路径当前不存在（67% 失效），blueprint_id 映射思路可借鉴、路径清单不可采用——不作真源，重生成与否待 Owner 裁定（Q10）。
- `依赖图/project-entity-depgraph.yaml`（28 域 / 138 边，自述 2026-05-22 生成）：域 ID 连字符格式与注册表下划线格式不一致，28 域口径与注册表 63 域口径差异大——域真源 = functional_domain_registry，该快照仅反映 2026-05 时点域划分草案，不作真源，重生成与否待 Owner 裁定（Q10）。

---

## 4. 缺口分析与填补优先级

> 口径：缺口 = 00_index.md §1 目标架构组件 − §3 实测现状。优先级 P0（阻塞 Phase 0→1）/ P1（Phase 1 需要）/ P2（Phase 2+ 或远期）。施工归属指向 03~17 号文；交易决策侧依赖只读引用。

### 4.1 P0 缺口（阻塞当前施工波次）

| # | 缺口 | 现状实测 | 填补归属 | 外部依赖 |
|---|------|---------|---------|---------|
| G1 | intelligence_governance 25 文件无统一入口 | §3.4.1 已登记 24 功能模块散落 | 05 号文（整合方案） | 无 |
| G2 | 自我进化层四件套零代码（证据关联/自反闭环/级联路由/AutoSkill 技能库） | §2.1 逐项实测无对应模块 | 11/12/13 号文 | 11 依赖 06 画像流水线（U3）；13 依赖交易决策侧 62 号注册表 P0（U8） |
| G3 | 业务 Agent（因子/策略/组合）空白 | 无对应代码 | 14 号文 | **依赖交易决策侧 G04 策略定义完成（U7）**；62 号注册表只读引用 |
| G4 | 模块工厂（核心独创）零代码 | 全仓无对应模块 | 13 号文 | 依赖 62 号注册表 P0（U8）+ 12 号文自反 Agent |
| G5 | depgraph 域节点级计数无查询入口 | 全仓无法复现旧档的 131/72/33 等数字；域清单真源已锚定注册表（§1.2），节点级入口仍缺 | 本文 Q4 + 03 号文 | 无 |

### 4.2 P1 缺口（Phase 1 需要）

| # | 缺口 | 现状实测 | 填补归属 | 外部依赖 |
|---|------|---------|---------|---------|
| G6 | D_KNOWLEDGE 归属不清（代码实体在 `integration/vector_memory/` 28 个 .py，域内独立知识包不存在） | §3.3 | 03 号文裁定保留/合并/退役 | 无 |
| G7 | 三层运行时仅骨架（runtime/ 2 个 .py；L2 调用在 integration/local_model/ 但未收编进统一运行时） | §3.4.1 | 04/10 号文 | 无 |
| G8 | LLM 安全栈 L0~L8 纵深防御与 gateway 强制覆盖面未审计 | 代码 39 文件已存且 L0~L8 层文件齐全，RULE-LSG-001 强制面未实测 | 09 号文 | 10 号文 LLM 基础设施 |
| G9 | MOD-ML-002 ai_operator design 态（目录不存在） | §3.2 | 待裁定（Q3）→ 14 号文 | AlphaQuanter 对标结论（01 号文） |
| G14 | D_AUTONOMY_PERM 注册表 2 条目（MOD-INF-022/024）ssot_path `src/zephyr/autonomy_perm/` 无码 | §3.3 | 03 号文域裁定 → 注册表维护方 | 无 |

### 4.3 P2 缺口（Phase 2+ / 远期）

| # | 缺口 | 现状实测 | 填补归属 | 外部依赖 |
|---|------|---------|---------|---------|
| G10 | 模型路由 Q-learning 动态学习（Qualixar 对标） | model_router.py 为规则式 | 11 号文 | 无 |
| G11 | RL 训练信号回传（AlphaQuanter 对标） | 无 RL 回传链路 | 14 号文远期 | 01 号文对标结论 |
| G12 | 数据增强（TimeGAN/扩散）零代码 | Grep 零代码命中 | 交易决策侧业务范围，AI 层不承接 | 交易决策侧裁定 |
| G13 | 多 Agent 涌现行为检测器 | agent_debate.py 有辩论无涌现检测；a2a_protocol 有 collusion/anomaly 检测可作邻近能力 | 12 号文 | 无 |
| G15 | 监控/可观测设施分散于 4 处（system_telemetry 25 / health_monitor 2 / observability 3 / observability_governance 6），无统一盘点入口 | §2.2.5 | 16 号文（运维闭环） | 无 |
| G16 | 场外依赖图快照（CSV/depgraph.yaml）内容失效，依赖图类资产无当前有效快照 | §1.3 | 待裁定（Q10） | 无 |

### 4.4 外部对标逐项对照（与 01 号文一致性核查）

> 口径：以 [01_external_benchmark_analysis.md](01_external_benchmark_analysis.md) 的 14 个框架/实践 + 模块工厂评估为清单，逐项标注场内覆盖状态：**已有**（代码已存且方向一致）/ **部分**（有邻近代码或基础设施，核心机制未施工）/ **空白**（无代码）/ **不适用**（超出 system_charter §2 硬边界或已被裁定不做）。对标细节真源在 01 号文，本表只做覆盖状态登记。

| 外部框架/机制（01 号文出处） | 关键机制 | 场内对应资产（实测） | 覆盖状态 |
|------------------------------|---------|---------------------|---------|
| AQuA（§2.1） | 证据保留→迭代引导闭环；双系统隔离沙箱；固定评估器 | 证据关联无代码；通用沙箱有 `skills/skill_sandbox.py`、`intelligence_governance/aisg_sandbox.py` | **空白**（证据闭环）/ 部分（沙箱机制） |
| NVIDIA NeMo（§2.2） | 信号→代码→评估三 Agent 闭环 | 模块工厂未施工；评估侧有 `experiment_tracking/` 8 文件 | **空白** |
| TiMi（§2.3） | 数学反思闭环 | `feedback_loop/evolution/self_reflection.py` 单文件 | **部分** |
| AlphaQuanter（§2.4） | RL 端到端训练信号回传 | 无；设计裁定 Phase 3 用 ICL 替代 MAML/EWC（00_index.md §4） | **空白** |
| AI Agent Swarm（§2.5） | 机构级 Agent 集群 | 超出单人单机约束 | **不适用** |
| Man Group AlphaGPT（§2.6） | 中心化研究助手 | `autonomy_core/` 包根（spec_engine / trigger_router / phase_planner） | **部分** |
| Balyasny / Millennium（§2.7） | 中心化平台复用 | `intelligence_governance/` 25 + `governance/` 横切 295 | **部分** |
| Agentic Engineering 三层架构（§3.2） | 上下文工程/工程保障层/协作生成层 | `autonomy_core/context/` 39 + `progressive_disclosure_injector.py` + `vibe_coding_quality_gate.py` + AGENTS.md L1/L2/L3 工作分配 | **已有** |
| VibeDev（§3.3） | Vibe 开发质量门 | `vibe_coding_quality_gate.py` + `gov_code_quality/` 66 + `access_control/guards/vibe_coding_guard.py` | **部分** |
| 受约束 Vibe Coding·Zenera（§3.4） | 约束先行/门禁强制 | `gov_enforcement/` 185（commit_gates 102）+ system_charter §2 | **已有** |
| Hermes（§4.2） | 可写运行时/技能自进化/渐进披露/五层记忆 | `skills/` 58（注册/路由/生命周期/沙箱/复盘/保鲜/熔断等基础设施）+ `model_evaluation/unified_memory_api.py` + `vector_memory/` 28；AutoSkill 自动发现未施工 | **部分** |
| Qualixar OS（§4.3） | 三层模型路由/Q-learning/Goodhart 检测/JSD 漂移 | `intelligence_governance/model_router.py`（规则式）+ `intelligence/model_drift_detector.py` + `gov_drift/` 74；Q-learning 空白 | **部分** |
| claude-flow（§4.4） | Agent 编排/hive-mind | 61 号备忘已裁定不做 agent 编排；多 AI 并发治理由 `lock_files.py` / `git_commit.py` 承载 | **不适用**（治理需求已有等价设施） |
| CrewAI（§4.5） | role-based crew 编排 | 同上裁定 | **不适用** |
| 模块工厂（§5，核心独创无对标） | 知识→模块六环节流水线 | 零代码 | **空白** |

**对照汇总**：已有 2、部分 7（AQuA 沙箱计入部分）、空白 4、不适用 3。空白项与 §4.1 P0 缺口（G2/G4）完全重合——外部演进方向与场内缺口指向同一施工波次（11/12/13 号文）。

---

## 5. 不做什么

1. **不做代码质量审查**：本文只盘点资产存在性与状态档位，不评估实现优劣、不审函数级实现（盘点到模块级，不到函数级——函数级 = 过度详细）。
2. **不做设计决策**：域边界裁定（D_KNOWLEDGE 存废、D_AUTONOMY_PERM 处置、横切视图 vs 独立域）归 03 号文；intelligence_governance 整合方案归 05 号文；本文只登记现状与缺口，不替任何文档拍板。
3. **不盘点交易决策侧业务模块**：因子/策略/组合/执行等业务资产归 07 侧文档与 62 号注册表；本文只读引用其解锁点（U7/U8），不复制其内容。
4. **不引入过度工程项**：缺口分析不登记超出 system_charter §2 硬边界的设施（K8s 部署、分布式训练、热备集群、多团队治理流程等一律不列）；远期项（P2）保持远期标注。
5. **不做双向同步**：本文是资产盘点唯一真源；其他文档需要资产状态时链接本文，禁止复制本文表格到他处维护第二份。
6. **不把场外快照回流为真源**：`.runtime/aidrafts/` 下快照经核实失效的只登记核实结论（§1.3），不将其数字并入本文盘点口径。

---

## 6. 开放问题

| # | 问题 | 状态 | 说明 |
|---|------|------|------|
| Q1 | intelligence_governance 包（实测 25 文件）是否需要整合到统一的 AI 层入口？ | 待裁定 | 目前散落在 `src/zephyr/governance/intelligence_governance/`，无统一入口文档；05 号文承接方案 |
| Q2 | D_KNOWLEDGE（注册表 ssot_path 指向 `integration/vector_memory/` 28 个 .py，无独立知识包）是保留还是合并到 D_INTELLIGENCE？ | 待裁定 | 知识库能力是 AI 层的重要组成，代码实体存在但归属跨 integration/ 与 intelligence/；03 号文承接裁定 |
| Q3 | MOD-ML-002（ai_operator，design 态）的施工优先级？ | 待裁定 | Generator→Critic→Judge 三层设计完整，但无 RL 训练信号回传，是否等 AlphaQuanter 对标结论后再施工？ |
| Q4 | depgraph 域节点级计数的查询入口在哪？ | 待裁定 | 旧档"模块数 131/72/33/16/7/1/0"无法从 `architecture_model/`、`functional_domain_registry.yaml` 复现；`depgraph.db` 为二进制未查询。域清单真源已锚定注册表（82 条/63 域）；`scripts/governance/apply_depgraph.py` 存在，节点级计数入口仍待确认 |
| Q5 | AGENTS.md 称 capability_cards 为 22 个 skill_*.yaml，实测 33 个 | 待裁定 | 差异 11 个；AGENTS.md 非本文档修改范围，是否同步修正待用户裁定 |
| Q6 | 若 03/05~16 号文填充后资产状态口径与本文冲突（如组件完成度评级），以哪方为准？ | 待裁定 | 本文定位为资产盘点真源，但施工完成度细节由施工文档维护，边界待确认 |
| Q7 | 施工期间 `09_ai_architecture/` 遭漂移隔离机制整体移出工作区（`.runtime/quarantine/drift_*` 多份快照，2026-08-17 18:06/18:35/18:38），目录为 untracked 状态 | 待裁定 | 本文档由 AI-FILL-02 重建并即时 staged；目录级恢复与防再隔离措施（是否收编进 git 跟踪/加白名单）待 Owner 裁定 |
| Q8 | passports 当日实测 7 本（deepseek-v4 四档 + qwen2.5-coder_14b + qwen3-coder_30b + qwen3_8b），deepseek_r1 14b/8b 无护照 | 待裁定 | 是为 deepseek_r1 补考发证，还是接受当前护照集以在役模型为准？06 号文承接执行 |
| Q9 | D_AUTONOMY_PERM（注册表 MOD-INF-022/024）ssot_path `src/zephyr/autonomy_perm/` 目录不存在 | 待裁定 | 补施工代码还是修正注册表条目？03 号文域裁定时一并处理 |
| Q10 | `.runtime/aidrafts/09_drafts_audit/依赖图/` 两份快照（CSV 2434 行 / depgraph.yaml 28 域）抽样 67% 路径失效 | 已核实降级历史快照，重生成与否待 Owner 裁定 | 核实结论已登记 §1.3 与 §3.5.3（一行登记，不重复核实）；是否按当前代码树重生成依赖图快照、还是随草稿区清理一并处置，待 Owner 裁定 |

---

## 7. 修订记录

| 日期 | 版本 | 变更 | 原因 |
|------|------|------|------|
| 2026-08-17 | 0.1.0 | 初版：设计文档+场外草稿+AI员工体系+已有域+运行态设施 | 从 00_index.md 拆分盘点内容到独立文件 |
| 2026-08-17 | 0.2.0 | 加入 frontmatter+开放问题+修订记录；标注更新策略 | 按 AI_review 方法论规范文档结构 |
| 2026-08-17 | 0.3.0 | 移除对 架构图/ 和 依赖图/ 草稿目录的所有引用；新增 §2"AI 自我进化设计"节（纯文字描述不带文件链接）；开放问题从 Q1-Q4 精简为 Q1-Q3 | 用户裁定草稿目录待删除 |
| 2026-08-17 | 0.4.0 | 全量实测填充：新增 §1 盘点口径、§2 背景（20 组件覆盖率比对）、§3.1.1 增加代码映射列、§3.3 域盘点改实测口径（原 131/72/33 等数字无法复现，降级为全仓标记命中数）、§3.4 运行态设施从 5 行扩至 30+ 行（补 feedback_loop 338/security 166/a2a_protocol 89/orchestrator 70 等大包）、新增 §4 缺口分析（G1~G13 按 P0/P1/P2 + 依赖标注）、新增 §5 不做什么；开放问题扩为 Q1~Q7；修正失准档案（intelligence_governance ~20→25、passports 10+→10、注册表补全实际路径） | AI-FILL-02 指令：盘点类文档深度填充，实测纪律优先 |
| 2026-08-17 | 0.5.0 | 第二轮深挖扩写：①§1.3 新增场外快照核实结论（CSV 抽样 67% 路径失效、depgraph.yaml 28 域与注册表 63 域口径不一致，均不作真源）；②§2.1 二十组件表重测（治理 Agent 升代码基础已存·gov_enforcement 185，三层运行时补 integration/local_model 6 实现，MCP 补 integration/mcp 20，汇总口径改 6/11/2/1）；③§3.3 域盘点锚定 functional_domain_registry（82 条/63 域），扩至 13 个 AI 相关域含 ssot_module/ssot_path/代码实测/标记命中，新登记 D_AUTONOMY_PERM（无码）、D_INFRA_A2A、D_INFRA_TELEMETRY、D_FEEDBACK_LOOP、D_BEHAVIORAL_AUDIT、D_SECURITY；④§3.4 重构为 3.4.1 代码包逐包实测（intelligence 43/autonomy_core 113/governance 295/security 179/feedback_loop 338/a2a 89/mcp 20/local_model 7/vector_memory 28/gov_enforcement 185 等，含子包分解与实测文件名）+ 3.4.2 数据资产 + 3.4.3 配置/脚本/注册表/蓝图；⑤§4.4 新增外部对标逐项对照表（14 框架+模块工厂：已有 2/部分 7/空白 4/不适用 3）；⑥实测修正：passports 7 本、model_profiling 24、03_modules 域目录 29 个、D_KNOWLEDGE 代码实体 vector_memory 28；⑦新增缺口 G14（autonomy_perm 无码）/G15（监控设施分散）/G16（场外快照失效），开放问题扩为 Q1~Q10 | AI-FILL-02 第二轮指令：逐域/逐包实测扩大盘点颗粒度，与 01 号文对标逐项对照 |
| 2026-08-17 | 0.5.1 | 新增 §3.5 升级门禁与负向裁定登记：①§3.5.1 登记 Agent架构.md §17 LP-001~021 中 AI 层相关 11 项"暂缓+触发条件"门禁（OPA Rego/记忆 RAG/影子模式/EU AI Act/11 Agent 分期/DID 密码学身份/内部竞赛/Neo4j 记忆图谱/MCP×A2A/Agent 365 OTel/NeMo IORails）；②§3.5.2 登记学习系统架构.md §14.0 ❌ 负向裁定 26 条（R-31~42 / R-64~67 / R-103~112，含 FinVision 绕过 DSL+AST 沙箱 / AlphaEvolve DSL 语法进化 / LLM 四级路由 M1/M3/M7/M9 / Level-2 数据源门禁 / 可微因果发现等）；③§3.5.3 场外快照一行登记（CSV 抽样 67% 路径失效、depgraph.yaml 28 域 vs 注册表 63 域，均降级历史快照不作真源、不重复核实）；④Q10 状态改为"已核实降级历史快照，重生成与否待 Owner 裁定" | AI-FILL-02-R3 指令：登记负向裁定+触发条件，防未来重复评估 |

---

*维护者：AI 架构协调者*
