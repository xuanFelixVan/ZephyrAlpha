---
ttl: permanent
doc_type: architecture_view
title: 自我进化核心组件施工图
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.2.0"
date: 2026-08-17
topic: evidence_skill_router
scope: 09_ai_architecture
---

# 自我进化核心组件施工图

> 本文定位：AI 自我进化层的三个核心组件——证据关联（假设→证据→迭代引导）、技能库（AutoSkill+Voyager）、模型路由。
> 与其他文件的分工：结构设计见 [00_index.md](00_index.md)，对标见 [01_external_benchmark_analysis.md](01_external_benchmark_analysis.md)，全局资产盘点真源见 [02_design_asset_inventory.md](02_design_asset_inventory.md)（本文 §2.4 只列本主题设施）。

---

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | 自我进化核心组件 |
| 所属 | [00_index.md](00_index.md) §1 目标架构·AI 自我进化层 |
| 依赖 | 元学习系统设计（S6 层）；[06_model_profiling_pipeline.md](06_model_profiling_pipeline.md)（护照驱动路由） |
| 对标 | AQuA（证据保留→迭代引导）/ Hermes（技能自进化）/ Qualixar OS（模型路由） |
| 优先级 | P1——自我进化是 AI 层的核心竞争力 |
| 状态 | draft（已填充 v0.2.0） |

---

## 2. 背景

### 2.1 项目处境

自我进化层是 [00_index.md](00_index.md) §1 目标架构中"AI 自我进化层（设计已有，待施工）"的组成部分，含证据关联、技能库、模型路由三组件；[01_external_benchmark_analysis.md](01_external_benchmark_analysis.md) §1 对照表将三者均标注为"设计完成，未施工"。经 §2.4 实测盘点后，真实处境比"未施工"更细：

- **模型路由：基座已 production，缺统一级联编排**。画像→考试→护照链路已生产可用（MOD-INF-034：五轴 CapabilityPassport 落盘 `data/brain/passports/` 实测 10 份；JobMatcher 按岗位矩阵 `data/brain/job_matrix.yaml` 输出 Top-N 岗位推荐）；`task_model_learner.py` 已按任务×模型增量学习 composite_score；`governance/intelligence_governance/model_router.py`（MOD-INF-024）已有层级/成本感知的 ModelRouter（ECONOMY/STANDARD/PREMIUM × SIMPLE/MODERATE/COMPLEX）。但三套设施**各自独立消费、互不调用**：JobMatcher 不消费 ModelRouter，ModelRouter 不消费护照——"能力门（能不能做）→岗位匹配（谁适合）→成本路由（预算内选谁）"没有串成一次路由决策，级联控制器（对标 Qualixar，分时分任务本地/API）正是这层缺失的编排。
- **技能库：工程基座重、量化技能零**。`autonomy_core/skills/` 已有 58 个 production 工程模块（注册/路由/生命周期/沙箱/KYA 等，蓝图 MOD-INF-019），`skill_constructor.py` 已能"蓝图→SKILL.md"自动生成**开发协作类**技能。但 `skill-registry.yaml` 实测仅 2 条 domain 技能（database-specialist、master-blueprint），**量化交易技能为零**；Voyager 式"研究轨迹→技能→验证→入库"自进化闭环完全没有。
- **证据关联：全新建设，且须与既有"证据"概念划界**。`governance/evidence_pack.py` 与 `gov_audit/evidence_pack.py` 是**审计证据包**（audit findings 打包+SHA256 不可变），属治理域，与本文"假设→证据链→迭代引导"的**研究证据**是不同事物；研究侧实测不存在任何假设管理/证据关联设施（全 src 扫描无 hypothesis/evidence 命名模块命中，审计证据包除外）。

### 2.2 核心问题

三组件不是"三选一先后施工"，而是**一个迭代闭环的三段**：证据关联回答"哪个假设值得继续投入"（迭代引导），技能库回答"已验证的做法如何沉淀复用"（能力沉淀），模型路由回答"每个任务用哪个模型最划算"（执行效率）。核心问题拆解为：

1. **证据如何引导迭代？** 假设（如"因子 X 在 regime Y 下有效"）需要结构化存储，支持/反驳/中性证据逐条挂链，置信度随证据显式更新，输出"继续/转向/放弃"的迭代建议——这正是 AQuA"证据保留→迭代引导"机制（对标分析见 [01_external_benchmark_analysis.md](01_external_benchmark_analysis.md) §2.1，本文不重复其内容）。
2. **技能如何入库？** 两条路径并存：人工编写（现状唯一路径）+ AutoSkill 式自动生成（研究轨迹→抽象技能→沙箱测试→回测验证→人工门→注册入库）。金融场景比 Hermes 通用场景多一道**回测验证门**（差异分析见 [01_external_benchmark_analysis.md](01_external_benchmark_analysis.md) §4.2）——未验证技能不得进生产库。
3. **三组件如何协同？** 证据链验证过的假设 → 其验证过程/代码模式抽象为技能入库；技能执行按任务类型经模型路由分派；路由执行结果（成功率/置信度/成本）又回流为证据条目与技能疗效数据。闭环不追求一步建成，按 §4 分 Phase。
4. **施工顺序**（§6 Q1 之分析）：证据关联最轻（纯结构化存储+显式规则，零模型依赖）；模型路由基座最全（三处 production 设施只差编排）；技能库自动生成最重（依赖回测验证链路与证据输入）。建议顺序：**证据关联 → 模型路由编排 → 技能库自动生成 → 闭环**，最终裁定权留在 §6 Q1。

### 2.3 约束条件

- **硬件**：单机 RTX 3090 24GB（显存 <90%）+ 64GB RAM，无集群/K8s——模型路由只能在"本地 Ollama 模型 + 云端 API"之间做轻量级联；禁止引入需独立训练的 RL 路由模型；Q-learning 仅限表格型轻量实现（且不默认启用，见 §6 Q6）。
- **一人+AI 施工**：组件必须规则化、可交叉验证；证据置信度更新用显式规则（可审计），不用黑盒学习模型。
- **金融安全**：技能自动入库必须过沙箱测试 + 回测验证门 + 人工门，并复用现有 skill 治理链（guardrails/KYA/kill switch 已 production），不重造治理。
- **频率约束**：Tick=3 秒、日频及以上根频率——证据关联不做实时盘中更新，按日频/周频批量处理；模型路由不进下单热路径。
- **依赖锁定**：模型路由消费能力护照接口，护照 Schema 以 `capability_passport.py`（production，STABILITY=stable，HMAC 签名）为准，路由侧不得反向修改护照结构。
- **元学习范式约束**：按 system_charter §2 与既有决策，快速适应以 ICL 替代 MAML/EWC 类重训练方案——本文三组件均为"检索+规则+轻量增量学习"，不涉及梯度级元学习。
- **不破坏在跑治理**：`model_router.py`（MOD-INF-024）MODIFY-GUARD 为"no structural changes without owner approval"——级联编排只做消费与包裹，不改其结构。

### 2.4 已施工设施盘点

以下全部经实际读取/扫描验证（扫描日期 2026-08-17）。全局资产盘点真源是 [02_design_asset_inventory.md](02_design_asset_inventory.md)，本节只列本主题相关设施。

**模型路由相关**

| 类别 | 路径/位置 | 内容简述 | 状态 |
|---|---|---|---|
| 代码模块 | `src/zephyr/intelligence/model_profiling/capability_passport.py` | CapabilityPassport 五轴（横/纵/速/幻/稳）数据模型，HMAC-SHA256 签名，落盘 data/brain/passports/；QuickProfile + compute_grade_simple A/B/C/D/F 分级 | production |
| 代码模块 | `src/zephyr/intelligence/model_profiling/job_matcher.py` | JobMatcher 岗位匹配器：四维加权 match_score（required 0.45/bonus 0.25/幻觉 0.20/成本 0.10），幻觉率正常评分非硬门，输出 Top-N 岗位推荐 | production |
| 代码模块 | `src/zephyr/intelligence/model_profiling/task_model_learner.py` | 任务×模型增量学习引擎：composite_score=速度0.40+质量0.35+一致性0.25；样本≥3 用实测、<3 用 benchmark 兜底、=0 用静态映射 | production |
| 代码模块 | `src/zephyr/intelligence/model_profiling/pipeline_routing/`（6 个文件） | task_model_learner/benchmark_suite/profiler/results_writer/cli 的并行变体副本，与上级目录版本并存且内容有差异（实测 fc 比对），MODIFY-GUARD=none | production（归属待裁定，见 §6 Q5） |
| 代码模块 | `src/zephyr/governance/intelligence_governance/model_router.py` | ModelRouter（MOD-INF-024）：ModelTier×TaskComplexity 映射 + performance-aware 权重（成本0.50/速度0.35/质量0.15）+ RoutingDecision（reason/估成本/requires_owner）+ 黑名单 + benchmark profiles；MODIFY-GUARD 禁结构变更 | production |
| 代码模块 | `src/zephyr/governance/intelligence_governance/` 其余 24 个文件 | delegation_engine / multi_model_consensus / provider_failover / confidence_estimator / meta_confidence / mvep_orchestrator 等（整合归属 [05_intelligence_governance_consolidation.md](05_intelligence_governance_consolidation.md)） | production |
| 代码模块 | `src/zephyr/intelligence/model_drift_detector.py` | 模型漂移检测，可支撑路由的模型健康信号 | production |
| 代码模块 | `src/zephyr/integration/local_model/embedding_router.py` | EmbeddingRouter（MOD-INF-042）双嵌入维度路由（BGE-M3 1024d/bge-small 按 collection 分派+降级链）——**向量路由，非 LLM 任务路由**，注意区分防混淆 | production |
| 配置/数据 | `data/brain/passports/` | 实测 10 份能力护照 JSON（deepseek-v4 系列 4 份、deepseek_r1 8b/14b、qwen2.5-coder 14b、qwen3-coder 30b、qwen3 8b） | production |
| 配置/数据 | `data/brain/job_matrix.yaml` | 岗位匹配矩阵真源（v1.0.0，幻觉率九维权重+成本维度；文件自标"骨架 6 示例岗位"） | production（骨架规模） |
| 配置/数据 | `data/brain/quick_profiles/`、`*_exam_results.json`（3 份） | 快画像结果与各模型五维评测结果 | production |
| 测试 | `tests/model/`（实测 23 个文件） | test_profiler.py / test_model_capability_exam.py / test_benchmark_suite.py / test_job_matcher.py / test_model_router.py / test_model_drift_detector.py 等，覆盖画像/考试/护照/岗位匹配/路由/漂移 | production |

**技能库相关**

| 类别 | 路径/位置 | 内容简述 | 状态 |
|---|---|---|---|
| 代码模块 | `src/zephyr/autonomy_core/skills/`（实测 58 个 skill_*.py） | 技能工程基座全集：registry/router/loader/executor/lifecycle/discovery/evaluator/learning/factory/sandbox/guardrails/kill_switch/KYA/telemetry/tokenomics/lineage/ontology 等，蓝图 MOD-INF-019 | production |
| 代码模块 | `src/zephyr/autonomy_core/skills/skill_router.py` | SkillRouter：按施工阶段（想法/审计前/蓝图/施工/验证/审计后六阶段）+语义相似度（阈值 0.7，经 EmbeddingRouter）把任务路由到技能——**技能路由，非模型路由** | production |
| 代码模块 | `src/zephyr/autonomy_core/skills/skill_constructor.py` | 蓝图→SKILL.md 全自动构造器（解析蓝图 frontmatter→生成技能模板→写 skills/domain/{module}/SKILL.md→更新 skill-registry.yaml），面向开发模块 | production |
| 代码模块 | `src/zephyr/autonomy_core/skills/skill_registry.py` | SkillDefinition/PromptTemplate Pydantic 契约（semver+stability 词表校验），跨层数据契约 | production |
| 代码模块 | `src/zephyr/shared/contracts/skill_protocol.py` | SkillLoaderProtocol/SkillRouterProtocol 结构子类型协议（MOD-INF-016），解耦 D-INFRA/D-GOV 对 D-ORCH 依赖 | production |
| 代码模块 | `src/zephyr/autonomy_core/all_skill_modules.py`、`skill_rbac_registry.py`、`src/zephyr/feedback_loop/security/agent_skill_guard.py` | 技能模块总清单、RBAC 注册、反馈环侧 Agent 技能守卫 | production |
| 注册表 | `src/zephyr/autonomy_core/skills/skill-registry.yaml` | 技能注册表真源，实测仅 2 条 domain 技能（SKILL-DOM-DS0-001 database-specialist、SKILL-DOM-MB0-002 master-blueprint），量化技能为零 | production（内容骨架） |
| 文档 | `docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md`（MOD-INF-019） | 技能系统蓝图（§12 盲点 B34 等） | production |

**证据关联相关**

| 类别 | 路径/位置 | 内容简述 | 状态 |
|---|---|---|---|
| 代码模块 | `src/zephyr/governance/evidence_pack.py` | 审计证据包（MOD-INF-020：findings 打包+SHA256 不可变+签名后禁改），治理域审计用途，**非**研究假设证据链 | production（域不同，仅借鉴不可变性设计） |
| 代码模块 | `src/zephyr/gov_audit/evidence_pack.py` | 治理审计侧证据包（与上者并存） | production |
| 代码模块 | 研究侧假设/证据关联设施 | 实测不存在——全 src 按 evidence/skill/hypothesis 文件名扫描，研究向证据模块零命中（审计证据包除外） | 未施工 |
| 代码模块 | `src/zephyr/research/` | 实测仅 `__init__.py`，是证据关联新模块的天然落点 | 空目录域 |

---

## 3. 设计决策

> 本节只写 why（为什么选这个方案、考虑过哪些替代），实现细节由蓝图/代码维护。

### 3.1 证据关联设计（假设→证据→迭代引导）

**决策**：在 `src/zephyr/research/evidence/`（空目录域，见 §2.4）新建证据关联组件，三件套：假设注册表（Hypothesis Registry，含状态机 proposed→testing→supported/refuted→archived）、证据链（Evidence Chain，每条证据=支持/反驳/中性三态之一+来源+日期+完整性 hash）、迭代引导器（Iteration Guide，按显式规则从证据链输出"继续/转向/放弃"建议）。日频/周频批量更新，不进盘中。

**Why 结构化存储而非纯文档/纯向量库**：研究迭代最大的浪费是"重复验证已否定的假设"和"忘记为什么放弃某条线"。假设与证据必须可机读（状态机驱动迭代建议），纯文档无法规则化处理；纯向量语义关联做证据三态判定不可靠（支持/反驳是极性判断，embedding 相似度不区分极性），向量检索只作为"找相关证据"的辅助手段，降级为可选。

**Why 显式规则更新置信度而非学习模型**：个人项目假设量级（数十至数百条）不足以训练置信度更新模型；显式规则（如"独立反驳证据≥2 条且近 4 周无新支持 → 建议放弃"）可审计、可交叉验证，符合"AI 生成代码需交叉验证"的自治约束。

**Why 借鉴但不复用 governance EvidencePack**：审计证据包的"不可变+签名"思想适用于证据条目防篡改（每条证据落盘后 hash 固化），但审计包是"打包封存"语义，研究证据链是"持续生长"语义，域不同不复用其类（见 §2.1 划界），只借鉴 hash 完整性模式。

**考虑过的替代方案**：AQuA 双系统完全隔离沙箱（因子发现与模型开发隔离防污染）——未采纳为本文施工项，其取舍真源在 [01_external_benchmark_analysis.md](01_external_benchmark_analysis.md) §6 Q1（待裁定），本文不重复登记。

### 3.2 技能库设计（AutoSkill + Voyager）

**决策**：技能入库双路径——①人工路径（现状唯一）：手写 SKILL.md→registry，保留不变；②自动生成路径（新建）：研究轨迹/已验证假设的验证过程 → 轨迹挖掘器生成技能草稿 → 复用 `skill_sandbox` 沙箱测试 → **回测验证门**（量化技能必须过回测，调 backtest 域设施）→ 人工门 → 复用 `skill_constructor` 式写盘与 registry 更新入库。不新造技能运行时/注册表/治理链——58 个 production 工程模块直接复用（§2.4）。

**Why 自动生成而非纯人工**：一人力约束下"代码 100% AI 生成"已是定论，技能沉淀同理——纯人工路径的现实结果就是 registry 只有 2 条（实测现状）。Voyager/Hermes 证明了"执行轨迹→技能"自进化的可行性（对标细节见 [01_external_benchmark_analysis.md](01_external_benchmark_analysis.md) §4.2，其"技能三元组"设计真源在 01 号文 §1 对照表，本文不复制）。

**Why 比 Hermes 多一道回测验证门**：Hermes 面向通用场景，技能错了代价是重试；量化技能错了代价是亏钱——金融场景必须"未验证不入库"。验证门复用 backtest 域现有设施，不新造回测引擎。

**Why 自动生成排在 Phase 2 而非 Phase 0**：技能草稿的优质输入源是"已验证假设的验证过程"，即证据关联的输出——证据组件先建（Phase 0），自动生成才有真源输入；且回测验证门依赖交易侧链路就绪，故人工路径先行、自动生成后置（过度工程审查结论见 §4.4 注）。

### 3.3 模型路由设计（级联控制器）

**决策**：新建级联控制器编排层（`src/zephyr/intelligence/model_routing/`），把一次路由决策串成三段级联——**L1 能力门**（消费 CapabilityPassport：岗位 required 硬门+幻觉率正常评分，"能不能做"）→ **L2 任务适配排序**（融合 JobMatcher match_score 与 task_model_learner composite_score，"谁适合+历史上谁做得好"）→ **L3 成本/层级路由**（复用 MOD-INF-024 ModelRouter 的 tier×complexity×performance-aware 决策，"预算内最终选谁"，本地优先、API 兜底，分时分任务）。编排层只做消费与串联，不改三个基座的内部结构。

**Why 级联编排而非新造路由算法**：三处基座全部 production 且各有 MODIFY-GUARD/蓝图归属，新造统一算法=推翻既有资产+违反不破坏交叉引用约束；级联模式（每段独立可降级）天然匹配单机约束——任一段故障可降级为静态映射兜底（task_model_learner 已有"样本=0 用静态映射"先例）。

**Why 护照驱动**：`data/brain/passports/` 已有 10 份签名护照，能力评测是真源资产；路由若绕过护照自行评测=重复建设+双真源。护照消费接口（加载/校验签名/读五轴与 recommendations）以 `capability_passport.py` 为准（§2.3 依赖锁定）；与 [06_model_profiling_pipeline.md](06_model_profiling_pipeline.md) 的接口对齐见 §4.6 与 §6 Q3。

**Why 规则为主、Q-learning 轻量可选**：Qualixar 的全量 Q-learning+POMDP 三层路由（L1 ε-greedy 赌博机/L2 路由策略/L3 贝叶斯信念）在单机个人项目上属过度工程（无集群、路由决策频率低、训练数据稀薄）。本文设计：静态规则（成本+时段+能力门）为硬门保证安全可控；表格型 Q-learning 仅作为规则放行集内的排序优化实验项，默认关闭（是否启用见 §6 Q6；"是否替换静态路由"的取舍真源在 [01_external_benchmark_analysis.md](01_external_benchmark_analysis.md) §6 Q3，本文不重复登记）。

**考虑过的替代方案**：纯静态路由（现状）——长期次优但简单可控，保留为 L3 兜底与 Q-learning 未启用时的默认；POMDP 信念状态路由——过度工程，列入 §5。

### 3.4 三组件协同设计（证据→技能→路由闭环）

**决策**：闭环数据流单向三段——证据链验证过的假设（supported 状态）触发"是否可沉淀为技能"评估 → 可沉淀者走 §3.2 自动生成路径入库；技能执行与路由决策共用任务类型词表，技能每次执行经级联路由分派模型；路由执行结果（成功率/置信度/成本/延迟）批量回流：作为证据条目挂到相关假设链上，同时写入技能疗效数据（复用 `skill_evaluator`/`skill_efficacy_calibrator` 既有设施）。

**Why 单向三段而非全互连**：全互连（证据↔技能↔路由两两直连）在单机单人维护下是 N² 接口复杂度；单向闭环每段只有一个上游一个下游，接口数=3，可独立验收、独立降级。闭环回流按日频批量（§2.3 频率约束），不做实时反馈环。

**Why 协同放 Phase 3**：三段各自未验收前做闭环=把三个未验证组件绑在一起调试，违反"每个文档聚焦一个主题，可独立施工"的分治原则；闭环是"三组件都 production 后的接线工程"，不是新组件。

---

## 4. 施工计划

> depgraph L1 铁律：凡新建模块，第一步用 `apply_depgraph`（`scripts/governance/apply_depgraph.py`）登记设计态（status=planned），验证通过后最后一步翻转 production。禁止先施工后补登记。

### 4.1 第 0 步：depgraph 登记（L1 铁律，先于一切施工）

1. 用 `apply_depgraph --add-design-node` 将以下依赖登记到 depgraph 设计态（status=planned）：
   - `MOD-EVIDENCE_CHAIN`（新，证据关联，落点 `src/zephyr/research/evidence/`）→ 消费：无新建依赖；产出消费方：技能自动生成、路由回流（后两者登记时挂接）
   - `MOD-MODEL_ROUTER_ORCH`（新，级联路由编排，落点 `src/zephyr/intelligence/model_routing/`）→ `MOD-INF-034`（护照/JobMatcher/task_model_learner）+ `MOD-INF-024`（ModelRouter，只消费不改结构）
   - `MOD-SKILL_TRAJECTORY_MINER`（新，轨迹挖掘→技能草稿，挂在 MOD-INF-019 蓝图下）→ `MOD-INF-019`（沙箱/注册表/治理链复用）+ backtest 域验证门接口 + `MOD-EVIDENCE_CHAIN`（假设输入）
2. 全部施工验证通过后，最后一步统一 `--transition-design-maturity` 将上述登记项 status planned → production（见 §4.7）。

### 4.2 Phase 0（P0）：证据关联组件

| # | 任务 | 内容 | 验收标准 |
|---|------|------|---------|
| P0-1 | 假设注册表 | `research/evidence/` 假设 CRUD + 状态机（proposed→testing→supported/refuted→archived），JSON 落盘 | 状态机全路径单测通过；非法迁移（如 archived→testing）被拒 |
| P0-2 | 证据链 | 证据条目（三态+来源+日期+假设外键）落盘，条目 hash 固化防篡改 | 篡改任一条目内容→完整性校验失败；三态之外取值被拒 |
| P0-3 | 迭代引导器 | 显式规则集从证据链输出"继续/转向/放弃"建议，规则可配置可审计 | 人工构造证据序列→引导输出与规则推演一致；每条建议可追溯到触发规则与证据 |
| P0-4 | 批量入口 | 日频/周频批量处理入口（手动触发+计划任务挂点），不做盘中实时 | 批量跑一次全量假设：输出迭代建议清单落盘；盘中路径零调用（静态扫描佐证） |

### 4.3 Phase 1（P1）：模型路由级联编排

| # | 任务 | 内容 | 验收标准 |
|---|------|------|---------|
| P1-1 | L1 能力门 | 消费 `capability_passport.py` 加载/验签护照，按岗位 required 硬门过滤候选模型 | 伪造/篡改护照→验签失败被拒；不满足 required 的模型不进入 L2 |
| P1-2 | L2 任务适配排序 | 融合 JobMatcher match_score 与 task_model_learner composite_score（权重可配置），样本不足按既有兜底链降级 | 已知 benchmark 数据下排序结果与两源分数的手工复算一致；样本=0 时静态映射兜底生效 |
| P1-3 | L3 成本路由接线 | 编排层调用 MOD-INF-024 ModelRouter 做最终 tier/成本决策，本地优先、API 兜底 | 路由决策含 reason+估成本（RoutingDecision 字段完整）；MOD-INF-024 源文件零改动（git diff 佐证） |
| P1-4 | 级联降级链 | L1 无护照→L2 样本不足→L3 ModelRouter 异常，逐段降级到静态映射 | 逐段故障注入：每次故障均有降级产物+告警，不中断路由返回 |
| P1-5 | 时段/任务分派策略 | 分时分任务规则（如盘中时段禁重型 API 调用、夜间批量任务走本地）规则化落配置 | 规则命中单测通过；配置变更不改代码 |

### 4.4 Phase 2（P2）：技能库自动生成

> 过度工程审查结论（指令第 6 轮）：三组件不裁——证据关联是纯结构化存储（轻）、路由是编排既有基座（轻）；但 **AutoSkill 自动生成降级为"人工路径先行、自动生成 P2 可选"**——若 P2 启动时证据输入稀薄（supported 假设 <5 条），自动生成暂缓，只保人工路径。Q-learning 路由默认关闭（§6 Q6）。

| # | 任务 | 内容 | 验收标准 |
|---|------|------|---------|
| P2-1 | 轨迹挖掘器 | 从 supported 假设的验证过程/研究轨迹抽象技能草稿（技能三元组结构，真源见 01 号文 §1） | 输入已验证假设→产出草稿 SKILL.md；草稿标注"未验证"态，不可被生产加载 |
| P2-2 | 沙箱测试接线 | 草稿复用 `skill_sandbox` 既有设施跑隔离测试 | 恶意/越权草稿探针在沙箱被隔离；测试报告落盘 |
| P2-3 | 回测验证门 | 量化技能草稿调 backtest 域设施验证，未过门不得入生产 registry | 构造负收益探针技能→被验证门拦截；过门记录含回测摘要 |
| P2-4 | 人工门+入库 | 人工批准后复用 `skill_constructor` 式写盘与 registry 更新，走既有治理链（guardrails/KYA） | registry 新增条目含来源追溯（假设 ID+回测记录+批准人）；kill switch 对新条目生效 |
| P2-5 | 人工路径补量 | 手工编写首批量化技能（≥3 条，从已验证策略经验提取） | registry 量化技能从 0→≥3 条，全部走人工路径验收 |

### 4.5 Phase 3（P3）：三组件闭环接线

| # | 任务 | 内容 | 验收标准 |
|---|------|------|---------|
| P3-1 | 证据→技能触发 | supported 假设触发"可沉淀技能"评估（规则化） | supported 假设入库后评估清单自动产出；评估留痕 |
| P3-2 | 路由结果回流证据 | 路由执行结果批量挂链到相关假设（日频） | 抽样验证：路由记录与证据条目外键一致；盘中零实时写入 |
| P3-3 | 路由结果回流技能疗效 | 执行结果写入既有 `skill_evaluator`/`skill_efficacy_calibrator` | 技能疗效数据随执行累积可查；疗效下降技能进入人工复核清单 |

### 4.6 与其他文档的接口

**与 [06_model_profiling_pipeline.md](06_model_profiling_pipeline.md) 的接口（护照如何驱动路由）**：
- 接口假设（06 号文当前为骨架 v0.1.0，见 §6 Q3）：级联路由 L1/L2 消费 `capability_passport.py`（production，代码接口稳定）的护照加载/验签/五轴读取能力与 `job_matcher.py` 的 `match_top()` 输出；护照更新频率、TaskGate 门控语义以 06 号文填充后为真源，若其定义与本文假设冲突，修订本文并升版本。
- 职责边界：06 号文管"护照怎么生产/更新"，本文管"护照怎么被路由消费"；本文不改护照 Schema（§2.3 依赖锁定）。

**与 [13_module_factory.md](13_module_factory.md) 的接口（技能库如何支撑模块工厂）**：
- 接口假设（13 号文当前为骨架 v0.1.0，见 §6 Q2）：技能库存"怎么做"（可复用的做法/流程/代码模式），模块工厂管"创建什么"（新模块的生成与试运行）；模块工厂施工新模块时检索技能库匹配可复用技能，技能命中即注入施工上下文（ICL 范式，§2.3）；技能库不为模块工厂单独建索引，复用 `skill_discovery`/语义检索既有设施。
- 职责边界：技能库不做模块创建决策，模块工厂不做技能疗效评估（疗效归本文 §4.5 P3-3）。

**与 [05_intelligence_governance_consolidation.md](05_intelligence_governance_consolidation.md) 的关系**：`intelligence_governance/model_router.py`（MOD-INF-024）等 24 个模块的整合归属由 05 号文裁定（其当前为骨架 v0.1.0，见 §6 Q4）；本文级联编排对 MOD-INF-024 只消费不改结构，若 05 号文裁定其迁移/改名，本文同步修订引用。

**与交易决策侧的关系**：只读不改。回测验证门（P2-3）消费 backtest 域设施，发现需同步改的记 §6 待用户裁定；三组件均不进下单热路径。

### 4.7 收尾验证与 depgraph 状态翻转

1. Phase 0/1 全部验收项通过，Phase 2 按 §4.4 启动条件滚动推进，Phase 3 在三组件均 production 后启动；
2. 新增组件专项测试全绿，既有 `tests/model/`（test_profiler/test_model_capability_exam/test_job_matcher/test_model_router 等）回归全绿（证明编排未破坏基座）；
3. MOD-INF-024 / MOD-INF-034 源文件零改动复核（git diff 佐证"只消费不改结构"）；
4. skill-registry.yaml 量化技能 ≥3 条（人工路径）且全部可追溯；
5. 上述全部满足后，`apply_depgraph --transition-design-maturity` 将 §4.1 登记项 status planned → production。

---

## 5. 不做什么

| # | 不做项 | 理由 |
|---|------|------|
| 1 | 不做通用技能库 | 只做量化交易相关技能；通用技能需求由 Hermes 类外部框架满足，个人项目无维护面 |
| 2 | 不做强化学习路由大模型/POMDP 信念路由 | 单 GPU 单机约束+路由决策频率低+训练数据稀薄；Q-learning 仅限表格型轻量实验且默认关闭（§6 Q6）；Qualixar L3 层不引入 |
| 3 | 不做实时盘中证据关联 | 日频/周频批量处理（§2.3 频率约束）；盘中无迭代引导需求 |
| 4 | 不新造技能运行时/注册表/治理链 | 58 个 production 工程模块（§2.4）已覆盖，新造=双真源 |
| 5 | 不改造 governance/gov_audit 审计证据包 | 域不同（§2.1 划界），本文只借鉴其 hash 完整性模式 |
| 6 | 不做 AQuA 双系统完全隔离沙箱 | 取舍待裁定，真源在 [01_external_benchmark_analysis.md](01_external_benchmark_analysis.md) §6 Q1 |
| 7 | 不改 MOD-INF-024 ModelRouter 内部结构 | MODIFY-GUARD 禁结构变更；级联编排只消费包裹（§3.3） |
| 8 | 不做模型能力自行评测 | 护照是唯一能力真源，路由绕过护照评测=双真源（§3.3） |
| 9 | 不做技能自动生成的无条件入库 | 沙箱+回测验证门+人工门三段缺一不可（§3.2 金融安全） |

---

## 6. 开放问题

| # | 问题 | 状态 | 说明 |
|---|------|------|------|
| Q1 | 证据关联、技能库、模型路由的施工顺序？ | 待裁定 | §2.2 分析建议"证据关联→模型路由编排→技能库自动生成→闭环"（证据最轻零依赖、路由基座最全、技能自动生成最重且依赖证据输入）；§4 已按此排 Phase，若裁定不同则重排 |
| Q2 | 技能库与模块工厂的关系？ | 待裁定 | 技能库存"怎么做"，模块工厂管"创建什么"；§4.6 已写接口假设（工厂检索技能库复用技能、技能库不做创建决策），[13_module_factory.md](13_module_factory.md) 当前为骨架 v0.1.0，其填充后若为冲突定义以 13 号文为真源修订本文 |
| Q3 | 与 06 号文的护照→路由接口对齐？ | 待裁定 | [06_model_profiling_pipeline.md](06_model_profiling_pipeline.md) 当前为骨架 v0.1.0；§4.6 接口假设基于 production 代码（capability_passport.py/job_matcher.py），06 号文填充后若定义不同（如 TaskGate 语义、护照更新频率），以 06 为真源修订本文 |
| Q4 | 与 05 号文 intelligence_governance 整合的组件边界？ | 待裁定 | model_router.py（MOD-INF-024）归属/演进由 [05_intelligence_governance_consolidation.md](05_intelligence_governance_consolidation.md)（当前骨架 v0.1.0）裁定；本文只消费不改结构，若 05 裁定迁移/改名，本文同步修订引用 |
| Q5 | `model_profiling/pipeline_routing/` 并行副本如何处置？ | 待裁定 | 实测与上级目录 6 个同名文件并存且内容有差异（fc 比对非逐字节相同），MODIFY-GUARD=none；去重合并还是保留为独立流水线变体，需用户裁定 |
| Q6 | 表格型 Q-learning 路由排序实验是否启用？ | 待裁定 | 本文设计默认静态规则为硬门、Q-learning 默认关闭（§3.3）；"Q-learning 是否替换静态路由"的上层取舍真源在 [01_external_benchmark_analysis.md](01_external_benchmark_analysis.md) §6 Q3（同为待裁定），两处联动裁定 |

---

## 修订记录

| 日期 | 版本 | 变更 | 原因 |
|------|------|------|------|
| 2026-08-17 | 0.1.0 | 骨架建立 | 新建 |
| 2026-08-17 | 0.2.0 | 骨架填充完成：§2 背景（含实测设施盘点：模型路由 3 处基座+技能库 58 模块+证据关联零设施）、§3 设计决策（证据关联/技能库/模型路由/三组件协同四节 why+替代方案）、§4 施工计划（depgraph 登记先行+Phase 0~3+06/13/05 接口假设）、§5 不做什么 9 项、§6 开放问题扩至 Q1~Q6 | AI-FILL-11 按指令块执行首轮完整填充 |

---

*维护者：AI 架构协调者*