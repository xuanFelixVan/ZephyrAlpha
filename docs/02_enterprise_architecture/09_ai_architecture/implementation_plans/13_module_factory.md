---
ttl: permanent
doc_type: blueprint
title: 模块工厂施工图
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.3.0"
date: 2026-08-17
valid_from: 2026-08-17
last_verified: 2026-08-17
topic: module_factory
scope: 09_ai_architecture
---

# 模块工厂施工图

> 本文定位：模块工厂（Module Factory）的施工——知识采集→分类→映射→代码生成→验证→入库的完整流水线。
> 与其他文件的分工：结构设计见 [00_index.md](00_index.md)，落地性分析见 [01_external_benchmark_analysis.md](01_external_benchmark_analysis.md) §5。
> 本文只写 why（决策推理）与 how（施工步骤）；实现细节（代码级）由 blueprint/代码维护。入库 schema 的真源在交易决策侧 [62_business_registry_construction.md](../../07_trading_decision_architecture/design_memos/62_business_registry_construction.md)，本文只引用不复制。

---

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | 模块工厂 |
| 所属 | [00_index.md](00_index.md) §1 目标架构·AI 自我进化层 |
| 依赖 | factor_registry / strategy_registry / 现有回测框架（C-003） |
| 对标 | 无（核心独创，没有任何已公开系统有此概念） |
| 优先级 | P1——核心独特点，但依赖 P1 注册表先就位 |
| 状态 | draft（已填充） |

---

## 2. 背景

### 2.1 项目处境

模块工厂是"知识资产 → 可执行交易模块"的流水线，共六个环节：**知识采集 → 知识分类 → 知识→模块映射 → 代码生成 → 验证 → 入库**。以下现状全部实测（验证方式见各行）：

| 环节 | 当前实现状态 | 实测证据 |
|------|------------|---------|
| 知识采集 | **手动模式已有完整先例**：潘潘课程 546 条因子/策略条目经 29 号文抽取流程入库（人工喂料 + LLM 辅助抽取）；自动化采集（论文/开源/社区爬虫）未建 | [29_factor_strategy_extraction.md](../../07_trading_decision_architecture/design_memos/29_factor_strategy_extraction.md)（371KB，落盘存在）；factor_registry.yaml 头部注释载明"潘潘课程 546 条因子/策略条目入库前，库结构先支持多维适用性标注" |
| 知识分类 | **分类词表已定稿**（factor 10 类 / strategy 6 类，62 号裁定 S2/S3），注册表 schema v2.0 已内建多维适用性标注字段（timeframe/regime/direction/entry_role/tags）；独立自动分类器未建 | 62 号 §6.1.1/§6.1.2；catalogs/factor_registry.yaml 头部 schema v2.0 注释 |
| 知识→模块映射 | **核心独创环节，未建**。但锚点已预留：factor_registry schema v1.19.0 的 `schema_plan` 字段（{event, context, qualities, direction, output} 语义抽象层，对标 AlphaSchema），LLM 挖掘因子 MUST 填 | 62 号 §6.1.1 schema `schema_plan` 字段注释 |
| 代码生成 | **通用层面已是项目范式**（约束六：代码 100% AI 生成 + 交叉验证 + 依赖锁定）；但"从知识条目定向生成因子/策略模块"的受控生成通道未建。schema 已预留 `llm_safety_stack` 五字段（ast_validation/dsl_constrained/complexity_control/dual_channel_rag/family_aware_selection），discovery_agent≠human 时 MUST 声明 | 62 号 §6.1.1 schema `llm_safety_stack`/`discovery_agent` 字段 |
| 验证 | **C-003 回测管道 production**：三引擎（event_driven/vectorized/shrinkage）+ 过拟合检测 + walk-forward + PIT 管理 + 衰减监控；入库晋升 9 门禁算法（PROMOTE_ENTRY）已定稿 | `src/zephyr/backtest/`（core/ 10 文件、implementations/ 3、services/ 9、regime_validation/ 3，实测 LS）；62 号 §4.13 |
| 入库 | **注册表已落盘 active**：factor_registry.yaml（REG-FCT-001，schema v2.1，实测 140 条目）/ strategy_registry.yaml（REG-STR-001，schema v2.1，实测 146 条目）；另有候选模块晋升管道 candidate_module_registry（REG-CAND-001，active） | `docs/01_policies_and_standards/_registry/catalogs/` 实测（Select-String 计数 `- factor_id:`=140、`- strategy_id:`=146） |

**处境判断**：六个环节中，验证与入库两端的设施已 production/active（超出骨架预期）；中间四环节（采集自动化、分类器、映射引擎、受控生成）是真正的施工缺口。模块工厂不是从零造轮子，而是**把已存在的两端用一条受控流水线连起来**。

### 2.2 核心问题

**Q-A：知识→模块映射的核心独特点是什么？**

外部已公开系统（R&D-Agent-Quant / QuantEvolve / Hubble / AlphaGPT 类）的路径都是"想法 → 直接生成代码 → 回测"，知识本身不作为一等资产管理，也没有注册表治理。本项目的独特点在于：

1. **知识是一等资产**：知识条目先进知识/业务注册表（knowledge_article_registry、factor/strategy registry 的 candidate 态），带 owner/TTL/消费者/多维适用性标注，可检索、可追溯、可晋升——而不是一次性 prompt 耗材。
2. **映射经过语义抽象层**：知识 → `schema_plan` {event, context, qualities, direction, output} → 模块，语义与实现解耦（62 号 v1.19.0 已预留该字段，对标 AlphaSchema）。同一语义可换实现，同一实现可回溯语义。
3. **生成受三重约束**：受控词表（10 类/6 类 + v2.1 标签词表防同义词漂移）+ entry_schema（MUST 字段）+ 既有库重复检测（286 条目 + code_symbol/code_fingerprint 代码锚点）。幻觉和重复造轮子在入库前被结构性拦截。
4. **入库即治理**：产出物落库时自动进入 62 号的全生命周期（candidate→PROMOTE_ENTRY 9 门禁→active→DECAY_SCAN→RETIRE），模块工厂不需要自建治理。

一句话：**外部系统做"代码生成器"，本项目做"知识资产到受治理模块的转化流水线"**。这就是"没有任何已公开系统有此概念"的具体含义。

**Q-B：Phase 0→1（知识→模块映射）的施工路径？**

关键洞察：**Phase 0 事实上已经部分发生**——29 号文（潘潘课程 546 条抽取→注册表入库）就是一次人工执行的知识→模块映射。所以 Phase 0 的施工不是"做新事"，而是**把 29 号文的隐性流程显性化为 SOP**（六环节检查单 + 每环节验收标准），并跑通 1 个完整手动实例验证 SOP 可复用。Phase 1 再把 SOP 中纯机械的两环（分类、重复检索）自动化。详细步骤见 §4。

### 2.3 约束条件

硬边界统一引用 [system_charter.md §2 硬边界约束](../../04_architecture_principles_decisions/system_charter.md)（约束一~七，不复制）。本文特化约束：

| 约束 | 内容 | 出处 |
|------|------|------|
| C1 单 GPU | RTX 3090 24GB 跑不动 MAML/EWC 元训练，Phase 3 用 ICL（上下文学习）替代 | 01 号文 §5.2/§5.3 已裁定（引用，不重述推理） |
| C2 人工审核不可裁 | Phase 2 全自动保留人工审核，零审核=自杀；入库晋升 G8 人工签批门不可降级 | 01 号文 §5.2；62 号 §4.13 G8 |
| C3 批量非实时 | 模块工厂是日频/周频批量流水线，不在 tick=3s 实时交易路径上 | 系统宪章约束四 |
| C4 生成代码不信任 | AI 生成代码必须交叉验证 + 依赖锁定 + 自治熔断 | 系统宪章约束六 |
| C5 A 股合规 | 生成模块必须遵守 T+1、涨跌停、融券受限；验证环节内建 A 股规则模拟 | 系统宪章约束五（规则） |
| C6 单机轻量 | 无集群/K8s；检索用 embedding + SQLite FTS5，不上图数据库/向量数据库集群 | 系统宪章约束三（硬件）；01 号文 §5.1 |
| C7 一人力 | 所有自动化必须降低人的负担而非增加运维面；人审台必须极简（批量批准/驳回） | 系统宪章约束一/二 |

### 2.4 已施工设施盘点

以下每行均实测验证存在（2026-08-17，LS/Grep/Select-String 实测）：

| 类别 | 路径/位置 | 内容简述 | 状态 |
|------|----------|---------|------|
| 知识条目登记 | `docs/01_policies_and_standards/_registry/catalogs/knowledge_article_registry.yaml` | KMS 知识条目登记表（KE 编号，KMS 三层漏斗 50 KO→30 KE→10 KB 设计；对标 ITIL 知识管理 + ISO 30401） | draft（planned，空表，beta KMS 落地前仅 Schema 骨架） |
| 知识抽取先例 | `docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/29_factor_strategy_extraction.md` | 潘潘课程 546 条因子/策略抽取设计（v1.2.2）——人工知识→模块映射的 Phase 0 事实先例 | active（条目入库进行中） |
| 入库目标注册表（业务） | `docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml`（REG-FCT-001，schema v2.1，实测 140 条目）/ `strategy_registry.yaml`（REG-STR-001，schema v2.1，实测 146 条目） | 因子/策略唯一真源；v2.1 含 code_symbol/code_fingerprint 库↔代码双向锚定（#ARCH-BREG-002） | active |
| 入库目标注册表（P0 输入） | 同目录 `universe_registry.yaml` / `benchmark_registry.yaml` / `cost_model_registry.yaml` | 回测必需输入三件套（62 号 §5 P0 已完成） | active |
| 入库目标注册表（其余） | 同目录 `technical_indicator_registry.yaml` / `risk_limit_registry.yaml` / `execution_algo_registry.yaml` / `data_asset_registry.yaml` / `chart_pattern_registry.yaml` / `experiment_registry.yaml` 等 | 62 号 18 表体系的其余注册表落盘 | active |
| 候选模块晋升管道 | `docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml`（REG-CAND-001，v1.1.0） | 通用代码模块点子库：deferred → 一问标准（q1 已实现/重复）→ apply_depgraph --add-design-node → depgraph 设计态晋升 | active |
| 回测验证管道（C-003） | `src/zephyr/backtest/`：core/（engine_base、matching_engine、metrics、overfitting_detector、pit_manager、walk_forward 等 10 文件）、implementations/（event_driven / vectorized / shrinkage 3 引擎）、services/（decay_monitor、param_analyzer、report_generator 等 9 文件）、regime_validation/（3 文件）、io/（3 文件） | 因子/策略验证算力管道：过拟合检测（PBO/DSR 类）、walk-forward、PIT 防前视、衰减监控 | production |
| 技能生命周期设施 | `src/zephyr/autonomy_core/skills/`（skill_factory.py / skill_constructor.py / skill_registry.py / skill_sandbox.py / skill_evaluator.py / skill_discovery.py 等，实测 58 个 .py = 57 个 skill_* 模块 + __init__.py，与 17 号文口径一致） | "怎么做"层设施；其沙箱/评估/注册模式供模块工厂受控生成环节复用 | production |
| 模块治理设施 | `src/zephyr/shared/protocols/module_birth_registry.py`（MOD-INF-016）、`src/zephyr/trading/module_onboarding_scanner.py`（MOD-INF-035，AST 扫描发现未注册模块） | 模块出生登记 + 接入扫描 | production |
| 代码落地门禁 | `src/zephyr/gov_enforcement/commit_gates/`（module_id_consistency_gate.py / orphan_module_gate.py / registry_code_anchor_gate.py 等） | 生成代码入库前必须通过的 commit 门禁（模块 ID 一致性/孤儿模块/注册表锚点） | production |
| 实验追踪 | `src/zephyr/experiment_tracking/` + `catalogs/experiment_registry.yaml` | 验证结果/回测实验登记 | production / active |
| 依赖登记工具 | `scripts/governance/apply_depgraph.py`（实测 255KB 落盘）+ `catalogs/generator_registry.yaml`（TRAE-062） | depgraph 设计态/生产态登记与生成器触发编排——模块工厂新节点登记的指定工具 | production / active |
| 因子/策略代码落点 | `src/zephyr/factor/`（analysis/api/core/governance/infrastructure/services/technical_indicators/_extensions 子目录 + factor_base.py 等 6 因子模块文件）、`src/zephyr/governance/strategies/strategy_registry.py` | 生成模块的代码落地位置（62 号 §6.1.1 已勘正实际结构） | production |
| 语义检索底座 | `config/embedding_model_registry.yaml` | embedding 模型登记——映射环节语义检索的模型真源 | active |
| 反馈循环设施 | `src/zephyr/feedback_loop/`（template.py、collectors/known_unknown_registry.py 等） | 失效模式/已知未知收集——内部经验知识源的承载设施 | production |

> 盘点结论：模块工厂需要的**验证端、入库端、治理端设施已全部存在**；缺失的是中间的采集器、分类器、映射引擎、受控生成器四个新模块（见 §4 施工计划）。`src/zephyr/research/` 目录实测仅含 `__init__.py`（空壳），`src/zephyr/red_blue_validator/` 实测仅含 `__init__.py`——研究/红蓝验证能力的施工不在本文范围（分属其他专题）。

---

## 3. 设计决策

> 按 01 号规范 §4.4 流水线类组织：输入（§3.1）→ 处理（§3.2/§3.3/§3.4）→ 输出（§3.6）→ 验证（§3.5）→ 不做（§5）。每节写 why 与考虑过的替代方案，不写实现细节。

### 3.0 流水线总览

```
┌─────────┐   ┌─────────┐   ┌─────────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│ 知识采集 │ → │ 知识分类 │ → │ 知识→模块映射 │ → │ 代码生成 │ → │  验证   │ → │  入库   │
│ (输入)   │   │ (处理1)  │   │ (处理2·核心) │   │ (处理3) │   │ (验证)  │   │ (输出)  │
│ §3.1    │   │ §3.2    │   │ §3.3        │   │ §3.4    │   │ §3.5    │   │ §3.6    │
└─────────┘   └─────────┘   └─────────────┘   └─────────┘   └─────────┘   └─────────┘
   四源         受控词表       schema_plan         DSL约束       四级验证      双通道
   手动先行     LLM分类       +语义检索          +AST沙箱      L1~L4       业务/通用
```

**总决策：六环节不合并**（对"是否可简化为三环节"的审查见 §5 不做什么·审查记录）。理由：分类与映射是两种不同性质的操作（分类=打标签，映射=判新建/变体/重复/组合），合并会失去重复检出这个核心拦截点；验证与入库分离是 62 号生命周期的既定结构（candidate→门禁→active），不可逾越。

### 3.1 知识采集设计（输入）

**决策**：四类知识源，手动触发先行，半自动辅助。

| 知识源 | 内容 | 采集方式 | Phase |
|--------|------|---------|-------|
| 课程/书籍 | 体系化因子/策略知识（潘潘课程模式） | 人工喂料 + LLM 辅助抽取（29 号文已验证的路径） | Phase 0 起 |
| 论文 | arXiv q-fin/cs.AI、SSRN 量化栏目新论文 | 人筛选论文 → LLM 抽取结构化知识条目；不做全自动爬虫 | Phase 1 起 |
| 开源 | GitHub 量化因子库/策略实现（stars 过滤） | 人筛选仓库 → LLM 抽取；许可证合规人工确认 | Phase 1 起 |
| 内部经验 | 失效因子墓园（衰减退役条目）、回测失败报告、交易复盘、known_unknown 登记 | 从 feedback_loop 设施 + 62 号 RETIRE/DECAY 记录半自动汇聚 | Phase 2 起 |

知识条目的承载：通用知识进 knowledge_article_registry（KMS 三层漏斗已有设计，beta 落地前以 29 号文式设计备忘录为载体）；业务知识（因子/策略类）直接按 29 号文模式抽取为 factor/strategy registry 的 candidate 条目。

**why**：
- 采集本身无技术门槛（01 号文 §5.1 判定"可行"），真正的风险是**质量控制与版权**——所以人保持在筛选回路上（人选论文/仓库，LLM 做抽取苦力），全自动爬虫在 30Mbps 家用网络 + 版权风险下得不偿失（见 §5）。
- **内部经验源是独家 alpha**：失效因子墓园让映射环节能拦截"重新发明已失效因子"（外部系统没有这个东西）；这也是自我进化层"证据关联"的输入（与 11 号联动，见 §4.6）。

**考虑过的替代方案**：
- 全自动 RSS/爬虫采集 → 放弃：信噪比低、版权风险、30Mbps 网络约束（C6）。
- 知识只进 KMS 不进业务注册表 → 放弃：因子/策略知识必须带 code_path、回测 evidence 才有战斗力，KMS 条目不具备这些字段。
- 采集频率实时化 → 放弃：C3，日频/周频批量足够（知识半衰期远长于交易信号）。

**采集侧质量控制与创意拓宽（草稿吸收，源：学习系统架构 §4.1 Step6 / §10.2.4 / §5.2 Step11 + 12-D-ML-TRAIN §9.2 R-84）**：

| 机制 | 内容 | Phase |
|------|------|-------|
| 信息价值四维评分 | LLM 对每条知识片段评四维——相关性（与持仓/关注标的相关程度）/时效性（有效时间窗口）/信息量（相对已有知识的新增量）/可靠性（来源可信度+逻辑自洽性）；综合评分（加权平均）<0.3 → quality_gate=REJECT，不进入分类环节 | Phase 1（随分类器同期引入，同为 LLM 受控输出） |
| 知识质量门禁四规则 | ①低质量知识（REJECT）自动拦截不进分类；②矛盾知识标记后降权，**不自动覆盖**已有条目；③NO_MATCH（映射无匹配）必须人工审核后才进生成环节；④试运行失败的模块不可重试超过 3 次 | Phase 1 起逐条落地（①②随分类器，③随映射引擎，④随验证编排） |
| Factor Mining Agent 创意拓宽 | LLM 一次并发生成 10+ 因子假设 → 快速预评估 → 仅高潜力假设进深度提取——瓶颈从"需要更多想法"变为"更快评估想法"（Two Sigma 2025-2026）；挖掘侧完整分工见 §3.3 | Phase 2 候选 |

门禁与评分的分工：评分是"值不值得学"（采集→分类之间的筛子），门禁是"学得对不对/能不能建"（分类→映射→生成之间的闸口），两者串联不合并。

### 3.2 知识分类设计（处理 1）

**决策**：LLM 分类器 + 受控词表约束输出。分类目标不是发明新体系，而是把知识条目映射到**已定稿的注册表词表**：

1. **主分类**：factor 10 类（value/quality/momentum/volatility/size/liquidity/event/intraday/technical/sentiment）/ strategy 6 类（daban/multifactor/event_driven/value_reversal/momentum_trend/sector_rotation）/ 其他（风控规则、执行算法、数据资产、技术指标、工具——分流到对应注册表或候选模块库）。
2. **多维适用性标注**：复用 schema v2.0 十字段（primary_timeframe/applicable_timeframes/regime_valid/regime_invalid/direction/entry_role/applies_to/tags/algorithm_status/evidence）。
3. **标签词表纪律**：tags 必须先归并到 v2.0 既有标签词表（防同义词漂移机制，如"翻转→反转"归并），新词先登记再使用。

**why**：
- 词表与标注字段已由 62 号裁定（S2/S3）且落盘 active，分类器是"对齐"而非"设计"——这保证分类结果可直接入库，无需二次翻译。
- LLM 文本分类准确率足以胜任受控词表分类（01 号文 §5.1 判定"可行"）；Phase 1 用 50 条样本人评一致率 ≥85% 作为验收门槛（§4.2）。

**考虑过的替代方案**：
- 训练专用分类模型（fine-tune 小模型）→ 放弃：单 GPU（C1）+ 标注样本不足百条，且词表会演进，维护成本远超 LLM prompt。
- 纯人工分类 → Phase 0 默认做法，保留为 fallback；但 286+ 条目规模下人分类是瓶颈，Phase 1 必须自动化。
- 多级层次分类树（TEJ Factor Library 式）→ 部分采纳：62 号 v2.0 已对标 TEJ 做了条目级多维标注，不再另建树（真源唯一）。

**知识 11 类参照系 + 矛盾三态 + 语义去重（草稿吸收，源：学习系统架构 §5.1 / §5.2 Step6）**：

1. **采集侧 11 类与入库侧词表的两级关系**：学习系统架构的知识分类体系为 11 类（strategy/factor/market_state/sector_rotation/risk/event/methodology/liquidity/game_theory/regime/lesson_learned）。入库真源仍是 62 号 factor 10 类/strategy 6 类词表（不双真源）；11 类作为**采集侧粗分流标签**使用——factor/strategy 直通入库通道，liquidity/game_theory/regime 归入市场状态类知识（分流到市场状态相关注册表或候选模块库），lesson_learned 归入内部经验源（§3.1 第四源），methodology 归入 KMS 知识条目。两级不冲突：采集侧回答"这条知识是什么"，入库侧回答"这条知识落到哪张表"。
2. **矛盾三态处理**（新提取知识与库内已有知识比对）：一致 → 增强（提高置信度）；矛盾 → 标记矛盾 + 保留两者 + 降低置信度（不自动覆盖）；无匹配 → 新增。
3. **因子语义去重**（补数值去重的盲区）：既有 IC 相关性 ≥0.7 的数值判冗之外，LLM 判定两因子经济学逻辑是否等价（即使数值不同）；语义等价 → 保留 IC 更高者 + 另一因子标"语义冗余"；语义不等价但数值相关 → 保留两者 + 标"数值相关但逻辑独立"。去重发生在映射环节检索阶段（§3.3），分类器只负责产出可比对的结构化描述。

### 3.3 知识→模块映射设计（处理 2，核心独创）

**决策**：三段映射——语义抽象 → 语义检索匹配 → 映射裁决。

```
知识条目（已分类）
   │
   ▼ ① 语义抽象：生成 schema_plan
{event, context, qualities, direction, output}
   │
   ▼ ② 语义检索：embedding + SQLite FTS5 双通道
检索范围：factor_registry 140 条 + strategy_registry 146 条
        + code_symbol/code_fingerprint 代码锚点 + 失效墓园
   │
   ▼ ③ 映射裁决（四选一）
┌──────────┬──────────┬──────────┬──────────┐
│  新建     │  变体     │  重复     │  组合     │
│ new      │ variant_of│ reject/  │ 多条目    │
│ entry    │ 指向 parent│ 归并     │ 组合生成  │
└──────────┴──────────┴──────────┴──────────┘
   │
   ▼ 输出 ModuleSpec
{目标 registry + 条目草稿（schema MUST 字段预填）+ 代码骨架规格 + 验证计划}
```

**why（这是核心独创环节的推理）**：
- **语义抽象先行**（schema_plan）：62 号 v1.19.0 已把该字段设为 LLM 挖掘因子的 MUST——"先语义后公式"使同一语义可换实现公式、同一公式可回溯经济含义，这正是 AlphaSchema（2026-07）验证有效的解耦设计，而本项目已把它内建进注册表 schema。映射引擎只是激活这个已预留的字段。
- **检索前置拦截重复**：外部系统（Hubble 用 formula-similarity penalty 事后罚）在生成后处理重复；本设计在**生成前**用既有库 286 条目 + 代码指纹 + 失效墓园做检索，重复/变体在写代码前就被裁决——省 GPU、省人审、防库膨胀。registry 的 correlation_group/redundancy_status 治理字段使变体登记天然合规。
- **四选一裁决而非二选一**：新建/变体/重复之外保留"组合"（多条既有条目组合成新策略），对应 62 号 combination_strategy 字段（regime_detector + allocation_weights），避免把"旧因子新组合"误判为新建。
- **轻量技术栈**：embedding + SQLite FTS5（01 号文 §5.1 判定可行的轻量实现），单机 64GB RAM 足够；不上向量数据库集群（C6）。

**考虑过的替代方案**：
- 跳过语义抽象直接 LLM 生成代码 → 拒绝：等于退化为外部系统的"想法→代码"，丢失独特点，幻觉无结构性拦截。
- 知识图谱（Neo4j 类）承载映射 → 拒绝：C6 单机约束，SQLite 足够；图谱的边际收益不抵运维面扩张（C7）。
- 纯人工映射 → Phase 0 默认；不扩展到 Phase 1+。
- surrogate 模型预测语义空间收益（AlphaSchema 的 reward surrogate + adaptive quota selection）→ 登记为 Phase 3 前沿演进方向（§3.7），Phase 1/2 样本量不足以训练 surrogate。

**Factor Mining Agent 与因果增强（草稿吸收，Phase 2 候选；源：学习系统架构 §7.2 R-84 / §5.2 Step4 + 12-D-ML-TRAIN §9.2 + 20-D-RESEARCH §12.0）**：

1. **Factor Mining Agent（R-84，Phase 2 候选）**：LLM 并发生成 10+ 因子假设 → 去重（与既有因子库 IC 相关性 <0.7 + §3.2 语义去重）→ 验证（IC 测试 + Walk-Forward + 过拟合检测）→ 辩论精炼（Generator 生成 / Critic 批判迭代，连续 2 轮无新批评或 ≤5 轮收敛）→ 产出走本文三段映射的四选一裁决入库。**与遗传编程变异的分工**：Factor Mining Agent 从零生成新因子假设（**创造**，扩展因子空间边界）；LLM 遗传编程变异对既有策略池做语义引导的变异进化（**改良**，在邻域内搜索更优解）。流水线顺序：Mining Agent 生成 → 辩论精炼 → 验证 → 注册 → 池中继续进化。两者互补不合并。
2. **因果发现引擎 + 验证层（Phase 2 候选）**：62 号 schema 已 MUST `causal_graph`（注册时声明，防事后合理化），当前靠人工填写；因果发现引擎是该字段的自动填充工具链——PC 算法（causal-learn，α=0.01 严格阈值防伪因果，<50 变量本地可跑）→ LiNGAM 确定因果方向 → TimePC 时序约束（金融时序专用）→ Neural Granger 非线性检测 → **LLM 语义校验**（形式化发现的因果边须有经济学解释，无解释→标"疑似伪因果"降权）→ **验证层**（有自然实验/工具变量支持→高置信度；无支持→降权标"待验证"）。扩展：DoWhy 三阶段（工具变量 → do-calculus 干预推理 → 反事实推理），反事实输出辅助 §3.5 验证环节评估。causal-learn/DoWhy 均纯 Python，C6 兼容；该引擎只产出 schema 字段值与置信度标注，不改变映射裁决结构。

### 3.4 代码生成设计（处理 3）

**决策**：DSL 约束 + AST 沙箱 + 模板骨架三件套的**受控生成**，不生成自由 Python。

1. **生成目标白名单**（只生成这些形态）：
   - 因子：qlib 表达式 / 继承 factor_base 的模板化类（优先表达式，可解释性最强）
   - 策略：entry_logic/exit_logic/position_sizing 的结构化填充（模板骨架 + 参数）
   - 技术指标：OHLCV 计算函数（technical_indicator 模板）
   - 风控规则：risk_limit_registry 条目 + 限额检查函数模板
2. **llm_safety_stack 五声明强制**：生成时 MUST 产出 {ast_validation, dsl_constrained, complexity_control, dual_channel_rag, family_aware_selection} 五字段值——这是 62 号 schema 对 discovery_agent≠human 条目的既定 MUST，模块工厂的生成器输出天然满足。
3. **AST 沙箱**：生成代码先过 AST 静态检查（禁 import 白名单外模块、禁文件/网络 IO、禁 eval/exec、圈复杂度上限），再进沙箱执行冒烟。沙箱实现复用 `skill_sandbox.py`（production），不自建。
4. **代码落地纪律**：落地文件必须带 blueprint 锚定头 + code_symbol，过现有 commit 门禁（module_id_consistency_gate / orphan_module_gate / registry_code_anchor_gate）；code_commit 绑定（62 号 G5 代码冻结门的前置）。
5. **交叉验证**：生成代码由第二个 AI 会话独立评审（系统宪章约束六 C4），评审记录附在 evidence。

**why**：
- 01 号文 §5.1 逐项判定"DSL 约束代码生成可行——DSL 限制搜索空间，AST 沙箱防注入"；Hubble（2026-04）实证了 DSL+AST 沙箱+dual-channel RAG+family-aware selection 在因子挖掘上零运行时崩溃跑完 104 候选——与本设计五件套一一对应，说明路线被外部独立验证。
- 表达式优先于自由代码：ALPHAQT-BENCH（ACL 2026）揭示自由代码范式存在"静默语义错误"（lookahead、状态性 bug 可运行但不正确），表达式/模板形态把这类错误的搜索空间压到最小（§3.7 登记）。
- 复用 skill_sandbox 与 commit 门禁：不建新安全设施（C7），生成代码与项目内一切 AI 代码走同一治理管道。

**考虑过的替代方案**：
- 自由 Python 生成（R&D-Agent 式）→ 拒绝：静默语义错误风险 + 零审核约束（C2/C4）。
- 人工写全部代码 → Phase 0/1 默认；Phase 2 起人写不过来（采集自动化后知识条目增速 > 人写速度）。
- 自建 AST 沙箱 → 拒绝：skill_sandbox.py 已 production，重复建设。

**受控生成的四项增强（草稿吸收，Phase 2/3 登记；源：学习系统架构 §7.2 + 12-D-ML-TRAIN §9.2 + 20-D-RESEARCH §12.11.2 + 23-D-AUT-PERM §17.3）**：

1. **三重语义一致性约束（Phase 2，QuantaAlpha）**：假设（Hypothesis）⇄ 表达式（Expression）⇄ 代码（Code）三者语义一致——假设的经济逻辑 = 表达式的数学逻辑 = 代码的程序逻辑；LLM 交叉验证三者一致性，不一致 → 拒绝生成、要求重新对齐。与既有设计的关系：schema_plan 是"假设"的结构化载体，三重一致性把 §3.3 语义抽象与 §3.4 代码生成焊死，防止"语义说一套、代码做一套"的漂移；生成器输出该验证结果，§3.5 L1 将其列为检查项。
2. **进化式代码生成 + 分析师 Agent 反馈循环（Phase 2 登记增强，Phase 3 完善）**：单次生成 → 多轮进化迭代——Generator（GLM-5.1）生成 → Critic（DeepSeek V4 Pro）批判（逻辑漏洞/过拟合风险/代码缺陷）→ Generator 按反馈修正 → 收敛（Critic 无新批评或 ≤3 轮）→ Judge（Claude）综合评估 → AST 沙箱 → L4 人审。进化收敛条件：连续 2 轮 Sharpe 无提升或达最大 5 轮；进化全程不违反 AST 沙箱约束；每轮代码 + 回测结果存技能库（走 §4.6 沉淀接口）供后续任务检索复用。**轨迹级进化**（QuantaAlpha，与 §3.7 登记呼应）：每次知识→模块映射视为一条研究轨迹（假设→构建→回测→优化），进化时定位轨迹中的次优步骤定向修正、交叉复用互补高奖励片段，而非整段重写。实证依据：Man Group AlphaGPT 反馈循环使 IC 从 0.58% → 2.23%。**边界声明**：30 号文已裁定"R&D-Agent 自进化策略搜索"为作战地图之外的研究议题（暂缓）——本增强与该裁定的兼容方式 = L4 人审不可降级（C2）+ 第 4 条限速，多轮进化的每一步都在沙箱与人审回路内，全自动无人审闭环留 Phase 3 远期。
3. **可解释设计约束（Phase 2，R-51 Explainable By Design）**：生成阶段即嵌入可解释性，而非事后补挂 SHAP/LIME——生成模块 MUST 含 `self.explain()` 自然语言解释方法；因子表达式 MUST 附经济学假设文本（与三重一致性的"假设"对齐）；模块输出 MUST 含 top-3 特征贡献度（特征 + 贡献百分比）。验证侧门控见 §3.5 可解释性门控行。
4. **自进化限速（23-D-AUT-PERM §17.3 吸收）**：每轮最多创建 1 个新模块（防失控）；元反思频率 ≤1 次/周；AutoSkill 发现的技能自动组合需人工审核。配套五禁见 §5 #11。

### 3.5 验证设计（验证）

**决策**：四级验证 L1→L4，门槛与 62 号 PROMOTE_ENTRY 对齐，保证"验证通过即可走晋升"。

| 级 | 内容 | 工具/依据 | 自动化 |
|----|------|----------|--------|
| L1 静态验证 | AST 安全扫描 + 复杂度上限 + 词表合规 + **因果安全截断测试**（截断输入时序，检测 lookahead——ALPHAQT-BENCH 2026 方法，§3.7）+ **三重语义一致性交叉验证**（假设⇄表达式⇄代码，不一致拒绝，§3.4 增强 1） | skill_sandbox + AST 检查器 | 全自动 |
| L2 回测验证 | C-003 全量回测：OOS Sharpe≥0.5、OOS max DD≤15%、OOS≥3 月；过拟合检查：PBO≤0.2、DSR≥1.0、CPCV 门禁（worst_dd≤15%、OOS 均值>0、std/mean≤0.5）、PF ratio≤2.0 | `src/zephyr/backtest/`（overfitting_detector/walk_forward）；门槛=62 号 §4.13 G1/G2（引用，阈值以其为准） | 全自动 |
| L3 合规验证 | A 股规则模拟：T+1、涨跌停不可成交、融券受限、PIT available_at 防前视 | C-003 matching_engine/pit_manager（production 内建 A 股规则） | 全自动 |
| L3+ 可解释性门控 | 生成物 MUST 附 SHAP/LIME 解释 + 经济学原理解释（§3.4 增强 3 的验证侧）；解释标注置信度三级（高/中/低），低置信度标"需人工验证"并转 L4 重点复核；**无法提供经济学原理解释的模块 → 拒绝部署**（Man Group AlphaGPT 门控原则）；承认 XAI 局限性（BIS FSI No.24：SHAP/LIME 存在不精确性与不稳定性），LLM 自然语言解释与数值解释不一致时以数值为准 | §3.4 可解释设计产物 + C-003 归因报告 | 全自动拦截 + L4 复核 |
| L4 人工审核 | 人审台批量批准/驳回：展示 schema_plan、生成代码 diff、L1~L3 报告、经济含义一句话 | 极简人审台（C7）；对应 62 号 G8 人工签批（不可降级） | **人工，不可自动化** |

验证结果沉淀：回测证据写条目 `evidence` 字段（v2.0 已预留，空=未回测），实验登记进 experiment_registry；失败案例进内部经验知识源（§3.1 第四源）——验证环节同时是知识再生产环节。

**L2 增强：三阶段决策门控 + 高级回测（草稿吸收，源：学习系统架构 §8.1 + 20-D-RESEARCH §12.0 R-48；Phase 2 登记，叠加在 62 号 G1/G2 既有门槛之上，阈值真源不动）**：

1. **三阶段决策门控**（AlgoXpert arXiv 2026）：
   - **IS 阶段 → 稳定性门控**：参数扫描识别"稳定高原"，选高原中心点参数；避免悬崖型参数（参数微调即性能骤降的区域）。
   - **WFA 阶段 → 多数通过门控 + 灾难否决门控**：多数通过 = WFA 各窗口中 >50% 盈利才通过；灾难否决 = 任一窗口最大回撤 >10% 直接 FAIL；**Purge Gap ≥5 个交易日**（训练集末尾 → Gap 期 → 测试集开头，防信息泄漏）。
   - **OOS 阶段 → 参数锁定门控**：OOS 期间参数不可调整（防 OOS 过拟合）。
2. **高级回测方法库（R-48，纯 Python scipy/statsmodels，C6 兼容）**：DSR 扩展（多策略同测时按策略间相关性调整多重检验阈值）/ CPCV v2（支持非 IID 金融时序的组合式净化交叉验证）/ White's Reality Check 增强（改进 bootstrap 适配金融厚尾，过拟合检测功效 +30%）/ Adaptive Walk-Forward（按市场波动率自适应训练/测试窗口，高波缩短、低波延长）。**与 62 号去重**：62 号 §4.13 G1/G2 门槛值（PBO≤0.2 / DSR≥1.0 / CPCV 门禁三条件 / PF ratio≤2.0）为既定真源，本条只扩充检测方法库与门控流程，不重复定义阈值。

**why**：
- 验证设施 100% 复用现有 C-003 + 62 号门禁算法，模块工厂只做**编排**（批量跑、汇总报告、拦截分流），不重写验证逻辑（C7）。
- 门槛与 PROMOTE_ENTRY 对齐：candidate 条目在入库前已过 G1/G2 同门槛验证，后续晋升无重复验证——这是"入库即治理"的另一半。
- L4 保留人审是 C2 硬约束；人审台设计为批量操作（一次审一批带完整报告的候选），把人的瓶颈从"写代码"降到"点批准"。

**考虑过的替代方案**：
- 只看回测收益不过拟合检测 → 拒绝：G2 是生存底线（62 号裁定）。
- 实时 paper 验证纳入模块工厂 → 拒绝：Shadow/Canary 属于 62 号 §4.13 渐进部署阶段，是注册表生命周期职责，非模块工厂职责（边界划分）。
- L4 也自动化（LLM 审 LLM）→ 拒绝：C2 零审核=自杀；LLM 复审可作为人审的预筛助手，不替代人。

### 3.6 入库设计（输出）

**决策**：双通道路径，复用现有全部注册表，不建任何新库。

| 通道 | 产出物类型 | 目标 | 流程 |
|------|-----------|------|------|
| 业务通道 | 因子/策略/技术指标/风控规则条目 | factor_registry / strategy_registry / technical_indicator_registry / risk_limit_registry（catalogs 落盘 YAML） | ModuleSpec 条目草稿 → schema 校验（MUST 字段）→ candidate 状态入库（algorithm_status=pending_backtest）→ L2/L3 验证后回填 evidence → 晋升走 62 号 §4.13 PROMOTE_ENTRY 9 门禁（非本文职责） |
| 通用通道 | 流水线自身需要的通用代码模块（如新的采集器、解析器） | candidate_module_registry（REG-CAND-001） | 登记候选 → 一问标准（q1 已实现/重复）→ apply_depgraph --add-design-node 晋升 depgraph 设计态（status=planned）→ 施工后转 production |

入库 MUST 满足（从 62 号 schema 摘录的硬要求，以 62 号为真源）：
- factor：formula 或 schema_plan（LLM 来源 MUST schema_plan）、pit_policy、inputs/outputs、module_id、code_path、discovery_agent + llm_safety_stack（非 human 时）、causal_graph（注册时 MUST 声明，防事后合理化）。
- strategy：entry/exit/position_sizing 三段、risk_rules 非空、benchmark_id、lifecycle_status、origin（human/llm_generated/hybrid）+ distilled_to_code（llm_generated 未蒸馏阻断上线，62 号 G5 关联）。
- 共同：code_commit 绑定（G5）；v2.1 code_symbol/code_fingerprint 双向锚定（#ARCH-BREG-002）。

**入库注记（草稿吸收）**：

1. **权重中心接口原则**（源：学习系统架构 §11.3）：模块工厂产出的策略/信号类模块在交易侧消费时输出**目标组合权重而非订单**——Python 代码即使有 bug 最多产生错误目标权重，物理上无法绕过风控引擎。约束：所有权重 ≥0 且权重之和 =1；单只股票权重 ≤20%（B-002 集中度约束）；权重变更频率 ≤1 次/交易日（防过度交易）。
2. **知识条目 append-only + Git-like 版本**（源：学习系统架构 §10.1 / §6.1 R-116）：知识与条目更新 = 新增一条 + 旧版标 superseded_by，历史不可删不可改；版本管理在 append-only 之上构建版本链，**回滚 = 当前生效指针回退到历史版本，不删除版本链**；每条知识可血缘追溯至原始来源。与本文既定写纪律一致：模块工厂对 62 侧注册表仅 candidate 追加（§4.5），不直接改既有条目。
3. **Non-AI Module Boundary Guard：AI 权重 ≤30%**（源：学习系统架构 §11.1 R-101，与 15 号文同口径互参）：入库的 AI 生成信号类模块在组合中的权重 ≤30%（B-007 人类监督对齐），超限自动降权至 30% 以下；入库时标记模块 AI/non-AI 属性，供组合层守卫执行。

**why**：
- 真源唯一铁律：因子/策略真源已在 catalogs YAML（active，286 条目），模块工厂另建库=双真源漂移，结构性禁止。
- 候选态入库 + 人审晋升的分离：模块工厂负责"到 candidate + evidence 齐"，是否上线由 62 号生命周期决定——职责边界清晰，模块工厂永不触碰"上线"按钮（C2）。
- 通用通道复用 candidate_module_registry 既有晋升管道（deferred→一问→apply_depgraph），与项目模块治理完全一致。

**考虑过的替代方案**：
- 模块工厂自建"生成模块库" → 拒绝：违反真源唯一。
- 直接写 active 状态 → 拒绝：跳过门禁=自杀（C2）。
- 入库走 PostgreSQL → 62 号已定 YAML 真源先行、DB 阶段演进（MIGRATE_REGISTRY §4.16），模块工厂不超前。

### 3.7 前沿演进方向（2026-08 检索登记）

> 以下为 2026 年最新研究/开源实证，**仅登记不替换已定决策**；若未来采纳需升版本+记理由。

| 来源 | 内容 | 与本文关系 |
|------|------|-----------|
| AlphaSchema（[arXiv:2607.26642](https://arxiv.org/html/2607.26642v1)，2026-07） | schema plan={Event, Context, Qualities, Direction, Output} 语义空间 + surrogate 收益模型 + adaptive quota 选择（探索/利用/变异三平衡）；A 股实证 | 62 号 schema_plan 字段的原始对标，§3.3 已对齐；surrogate+quota 选择登记为 Phase 3 候选增强（需样本量积累） |
| Hubble（[arXiv:2604.09601v2](https://arxiv.org/html/2604.09601v2)，2026-04） | DSL+AST 沙箱+dual-channel RAG+family-aware selection，104 候选零崩溃；正/负 RAG、公式相似度罚、持久诊断 artifacts | 实证 §3.4 五件套路线；正负 RAG（成功+失败案例双通道检索）登记为 Phase 2 增强候选 |
| ALPHAQT-BENCH（[ACL 2026 Findings](https://aclanthology.org/2026.findings-acl.138.pdf)） | 多层评估协议：可执行性/因果安全（动态截断测 lookahead）/功能正确性/结构合规；揭示自由代码"静默语义错误" | §3.5 L1 已吸收"因果安全截断测试"；同时强化 §3.4 "表达式/模板优先"决策 |
| QuantaAlpha（[arXiv:2602.07085v3](https://arxiv.org/html/2602.07085v3)，2026-05） | 轨迹级进化：每轮挖掘全程为 trajectory，做 mutation/crossover + 经验复用 | 轨迹级进化登记为 Phase 3 演进方向（与 ICL 案例库互补）；三重语义一致性已由 §3.4 增强 1 吸收 |
| QuantGPT（[GitHub](https://github.com/Miasyster/QuantGPT)，2026-05） | LLM Agent 经 MCP 全自动发现→评估→迭代→验证因子 + 云端独立复核 + OOS 跟踪；零人工研究循环 | 零人工循环与 C2 冲突，不采纳其"无人"部分；其云端独立 OOS 复核思路可用 Shadow/Canary 替代（已有，62 号 §4.13） |

---

## 4. 施工计划

> depgraph L1 铁律（规则 19）：凡新建模块，**第一步=用 apply_depgraph 将依赖关系登记到 depgraph 设计态（status=planned），最后一步=验证通过后 status planned→production**。禁止先施工后补登记。
> 前置解锁：U8（62 号注册表 P0）实测已就绪——P0 三件套（universe/benchmark/cost_model）active，且 P1 factor/strategy registry 亦已落盘 active（§2.4）。U4（11+12+13 完成）是执行层（14 号）的前置，不阻塞本计划 Phase 0/1。

### 4.0 总览

| Phase | 名称 | 六环节自动化程度 | 新模块 | 预估 |
|-------|------|----------------|--------|------|
| Phase 0 | 手动 SOP 化 | 全人工（人采集/分类/写模块/验证/入库） | 无新代码模块（SOP + depgraph 占位节点） | 1~2 周 |
| Phase 1 | 半自动 | AI 采集辅助 + AI 分类 + AI 映射检索；人写模块；AI 辅助验证；人入库 | knowledge_classifier、module_mapper | 3~4 周 |
| Phase 2 | 全自动+人审 | AI 采集/分类/映射/生成/L1~L3 验证；人审（L4）；自动入库 candidate | module_generator、verification_orchestrator、人审台 | 6~8 周 |
| Phase 3 | 自我进化（**远期 P4**） | ICL 案例库驱动生成质量自提升 | icl_case_base（远期） | 不承诺时间表 |

### 4.1 Phase 0（手动）：把人正在做的事流程化

| 步骤 | 内容 | 产出/验收 |
|------|------|----------|
| P0-S1（depgraph 登记，铁律第一步） | 用 `scripts/governance/apply_depgraph.py` 登记"模块工厂"设计态节点（status=planned，编号与域归属见开放问题 Q6，先以占位节点登记） | depgraph 设计态存在模块工厂节点 |
| P0-S2 | 编制《模块工厂手动 SOP》：把 29 号文抽取流程抽象为六环节检查单（每环节：输入/操作/输出/验收标准/常见坑） | SOP 成文，挂到 29 号文同目录或本文附录链接 |
| P0-S3 | 跑通 1 个完整手动实例：从 29 号文剩余未入库条目（或 1 篇新论文）→ 分类 → schema_plan → 人工写代码 → C-003 回测 → candidate 入库 + evidence 回填 | 1 实例全链路闭环；条目过 schema 校验；evidence 非空 |
| P0-S4（铁律最后一步） | SOP 走查 + 实例复盘 → depgraph 节点 status planned→production（SOP 治理范围） | 复盘记录；status 翻转 |

**验收标准**：SOP 可被"另一个 AI 会话"独立执行不重问（交叉验证 C4）；实例条目在 factor/strategy registry 可查。

### 4.2 Phase 1（半自动）：分类与检索自动化

| 步骤 | 内容 | 产出/验收 |
|------|------|----------|
| P1-S1（depgraph 登记） | apply_depgraph 登记 knowledge_classifier + module_mapper 两节点（planned），依赖边：→factor/strategy registry（读）、→embedding_model_registry（读） | 设计态节点+边就位 |
| P1-S2 | LLM 分类器：受控词表约束 prompt（10 类/6 类/其他分流）+ v2.0 多维标注输出 + 标签归并纪律（§3.2） | 50 条样本人评一致率 ≥85% |
| P1-S3 | 映射引擎：schema_plan 生成 + embedding/FTS5 双通道检索（286 条目+代码锚点+失效墓园）+ 四选一裁决输出 ModuleSpec（§3.3） | 对既有库自检：已知重复条目检出率统计；变体判定抽样人核 |
| P1-S4 | 人写模块 + AI 辅助验证编排：C-003 批量回测脚本化（输入=条目批次，输出=evidence 草稿） | 一批（≥5 条）半自动链路入库 |
| P1-S5（铁律最后一步） | 验收通过 → planned→production | status 翻转 |

**验收标准**：分类一致率达标；映射引擎重复检出有效（不误杀变体）；≥5 知识条目走"AI 采集辅助→AI 分类→AI 映射→人写→AI 辅助验证→人入库"全链路。

### 4.3 Phase 2（全自动，保留人工审核）

| 步骤 | 内容 | 产出/验收 |
|------|------|----------|
| P2-S1（depgraph 登记） | apply_depgraph 登记 module_generator + verification_orchestrator + 人审台节点（planned），依赖边：→skill_sandbox（复用）、→backtest 服务、→commit gates | 设计态节点+边就位 |
| P2-S2 | 受控生成器：DSL/表达式优先生成 + 模板骨架 + llm_safety_stack 五声明输出（§3.4）；AST 沙箱复用 skill_sandbox | 生成物 100% 过 L1 静态门 |
| P2-S3 | 四级验证编排：L1（含因果截断测试）→L2（G1/G2 同门槛）→L3（A 股合规）全自动；L4 人审台（批量批准/驳回，报告含 schema_plan+diff+L1~L3 结果+经济含义一句话） | 编排管道跑通；人审台可用 |
| P2-S4 | 自动入库：验证通过 → candidate 入库 + evidence 回填 + code_commit 绑定；晋升走 62 号 §4.13（非本 Phase 职责） | 入库条目 100% 过 schema + commit 门禁 |
| P2-S5 | 20 例全自动生成压力测试：统计人审拦截率与拦截原因分布（幻觉/重复/过拟合/合规），反哺 prompt 与 DSL | 拦截原因分布报告；零审核绕过记录 |
| P2-S6（铁律最后一步） | 验收通过 → planned→production | status 翻转 |

**验收标准**：20 例全自动链路完成；人审拦截率有统计（不预设数值目标，首轮先摸清基线）；任何条目未经 L4 不得入 candidate（门禁强制，非自觉）。

### 4.4 Phase 3（自我进化，**远期愿景 P4，不承诺时间表**）

> 本 Phase 整体为远期工程（规则 5：远期不算过度工程，但远期属性必须明确可见——此处显式标注）。MAML/EWC 已裁剪（01 号文 §5.3 裁定），自我进化用 ICL 渐进逼近。

- **ICL 案例库**：成功/失败模块案例（含人审拦截原因、回测 evidence、失效墓园记录）结构化沉淀，生成 prompt 自动注入同类案例——无需元训练，单 GPU 兼容（C1）。
- **语义空间选择增强**：AlphaSchema 式 surrogate + quota 选择的候选引入（§3.7，样本量足够后评估）。
- **技能沉淀**：高频生成模式 → 候选技能，走 11 号技能库登记流程（接口见 §4.6）。
- **反思驱动再生成**：验证失败案例 → 12 号自反 Agent 反思 → 再生成（接口见 §4.7）。
- **轨迹级进化**：QuantaAlpha 式 trajectory mutation/crossover 的评估（§3.7）。
- **S6 元学习机制细节（草稿 12-D-ML-TRAIN §10 吸收，Phase 3 候选增强登记）**：①Prompt 自优化 STOP 模式——LLM 分析 prompt 效果 → 自动生成改进 prompt → **人工审核** → 部署（prompt 变更必须人工审核，防 LLM 自我优化到不可控）；②代码自纠正 RISE 模式——模块代码运行异常 → LLM 自动定位 + 修正 → 人工审核 → 部署；③技能三元组——技能以（条件， 动作， 效果）结构化存储，按条件检索、按效果排序，新任务优先从技能库检索复用以加速收敛；④元反思四步闭环——经验回放 → 反思提炼 → 技能注册 → 元反思（反思"反思过程本身"的质量），频率 ≤1 次/周；⑤轻量 Agent 化四角色——PromptOptimizer / ArchitectureOptimizer / CodeGenerator / MethodologyLearner 四个逻辑 Agent 各管一个元学习维度，共享同一进程与 GPU 内存、消息队列协调，非物理分布式、不做 MARL（裁定 6❌硬边界门禁）。与 12 号分工：12 号自反 Agent 管"个案失败的反思"，本条 S6 管"学习策略自身的元优化"；个案语料接口见 §4.7。

### 4.5 与 62 号注册表的接口（入库 schema 与流程）

- **schema 真源**：factor/strategy entry_schema 以 62 号 §6.1.1/§6.1.2 与 catalogs 落盘 YAML（v2.1）为准，本文不复制字段全集；模块工厂产出的 MUST 字段清单见 §3.6。
- **状态机对齐**：条目入库 lifecycle_status=candidate、algorithm_status=pending_backtest；L2/L3 通过后回填 evidence；晋升（candidate→active）走 62 号 §4.13 PROMOTE_ENTRY 9 门禁，G8 人工签批不可降级——模块工厂永不自动晋升。
- **代码锚定**：code_commit（G5）+ code_symbol/code_fingerprint（v2.1，#ARCH-BREG-002）在入库时绑定；后续指纹对账门禁（62 侧立项）自动覆盖模块工厂产出物。
- **discovery_agent 取值**：62 号枚举为 human/rd_agent/efs/hubble/quantevolver/other——模块工厂不在枚举内，暂定登记 `other` + llm_safety_stack 全声明；是否扩展枚举加 `module_factory` 值属 62 侧 schema 变更，记开放问题 Q5（只读不改，待用户裁定）。
- **读取侧**：映射引擎只读检索 62 侧注册表（140+146 条目），写操作仅 candidate 追加；既有条目的修改/退役走 62 号 EVOLVE/RETIRE 算法，模块工厂不直接改。

### 4.6 与 11 号技能库的接口

> 11 号文档（AI-FILL-11）填充中，以下为**接口假设**（依据：11 号骨架主题组信息 + `src/zephyr/autonomy_core/skills/` 已 production 的设施）；最终以 11 号定稿为准，差异记开放问题 Q2。

- **复用方向（技能库 → 模块工厂）**：代码生成环节按任务描述检索技能库，复用已有技能作为模块组件（如"因子计算骨架""回测调用"类技能）。假设存在按描述检索技能的入口（skill_discovery/skill_registry 已 production，11 号将定义其对外接口）。
- **沉淀方向（模块工厂 → 技能库）**：Phase 3 将高频生成模式沉淀为候选技能，走技能库自己的登记/验证流程（模块工厂不直接写技能库，只提交候选）；进化式生成的每轮代码 + 回测结果（§3.4 增强 2）同走本接口沉淀。
- **分工边界**：技能库存"怎么做"（可复用过程性知识），模块工厂管"创建什么"（知识→业务模块的转化）——与 11 号骨架开放问题 Q2 的表述一致，两边对齐后关闭。

### 4.7 与 12 号自反 Agent 的接口

> 12 号文档（AI-FILL-12）填充中，以下为**接口假设**（依据：12 号骨架 Actor→Evaluator→SelfReflection 结构）；最终以 12 号定稿为准，差异记开放问题 Q3。

- **输入方向（自反 Agent → 模块工厂）**：L1/L2 反思输出（生成模块为何验证失败/人审驳回的结构化原因）作为再生成 prompt 的负案例——形成"生成→验证→反思→再生成"闭环（Phase 3）。
- **输出方向（模块工厂 → 自反 Agent）**：验证失败案例 + 人审拦截记录作为反思语料；Evaluator 的评估报告格式假设与本文 §3.5 四级报告兼容。
- **频率纪律**：反思调用受 ReflCtrl 类频率控制（12 号骨架约束"节省 20-80% token"），模块工厂侧按批量（日频/周频）触发反思，不逐条实时触发（C3）。

### 4.8 验收标准汇总

| Phase | 硬性验收 |
|-------|---------|
| Phase 0 | SOP 成文且可被独立 AI 会话执行；1 手动实例全链路闭环；depgraph 节点 production |
| Phase 1 | 分类一致率 ≥85%（50 条样本）；映射重复检出有效；≥5 条目半自动链路入库；两新模块 production |
| Phase 2 | 20 例全自动完成；入库 100% 过 schema+门禁；L4 无绕过；人审拦截基线报告；三新模块 production |
| Phase 3 | （远期，不设硬性验收；以 ICL 案例库运转 + 生成通过率环比提升为观察指标） |

---

## 5. 不做什么

| # | 不做 | 理由/出处 |
|---|------|----------|
| 1 | **不做 MAML/EWC 元训练** | 单 GPU RTX 3090 跑不动（C1）；01 号文 §5.3 已裁定 Phase 3 用 ICL 替代（草稿"小参数可行"反证已记开放问题 Q9，裁定前本条维持） |
| 2 | **不做零审核全自动** | LLM 生成交易策略代码零审核=自杀（01 号文 §5.2）；L4 人审 + 62 号 G8 人工签批不可降级（C2） |
| 3 | **不做通用代码生成** | 只生成白名单形态（因子表达式/策略三段/技术指标/风控规则，§3.4）；通用代码生成是静默语义错误温床（ALPHAQT-BENCH 2026，§3.7） |
| 4 | **不做实时模块工厂** | 日频/周频批量处理（C3）；不在 tick=3s 实时交易路径上 |
| 5 | **不建新注册表/知识库** | 真源唯一：业务条目进 catalogs 既有注册表，通用模块进 candidate_module_registry，知识进 knowledge_article_registry（§3.6） |
| 6 | **不做论文级 RSI（递归自我改进）** | 01 号文 §5.1 判定"RSI 学术界无可靠实现，只能渐进逼近"；Phase 3 只是 ICL+案例库，不承诺自我递归 |
| 7 | **不做多语言代码生成** | Python only；项目技术栈单一 |
| 8 | **Phase 0/1 不做全自动采集爬虫** | 30Mbps 网络 + 版权风险 + 信噪比（§3.1）；人保持在筛选回路上 |
| 9 | **不做全自动晋升/上线** | candidate→active 是 62 号 PROMOTE_ENTRY 职责；模块工厂止步于 candidate+evidence（§3.6 边界） |
| 10 | **不做 agent 编排系统** | 61 号备忘 §2.3 已裁定：多 AI 协作=人调度多会话，非 agent 自治；模块工厂各环节由人调度触发，不自治串联 |
| 11 | **不做自进化五禁项** | 草稿 23-D-AUT-PERM §17.1/§17.3 吸收：①不可自动修改 B-001~B-020 硬边界；②不可自动上线策略（B-007 人审）；③不可自动删除已有模块（只能标记退役）；④代码不可自动部署（需人工验证）；⑤禁止 MARL 训练/分布式协调（裁定 6❌硬边界门禁）。配套限速（每轮≤1 新模块/元反思≤1 次每周/技能组合人审）见 §3.4 增强 4 |

**过度工程审查记录**（指令第 6 轮三问）：

1. **"模块工厂整体是否过度？个人项目可否用简单知识库+手动开发替代？"** → 审查结论：不过度，但分期就是这个问题的答案。Phase 0 = 手动开发 SOP 化（几乎零新建设施）；Phase 1 只自动化两个纯机械环节（分类、重复检索）；Phase 2 的受控生成是在"采集自动化后知识增速 > 人写速度"时才必要的。若 Phase 1 运行后知识增速仍低，Phase 2 可无限期推迟——流水线设计允许停在任何 Phase 运行。验证/入库两端设施已存在，非新建负担。
2. **"六环节是否过多？可否简化三环节（采集→生成→入库）？"** → 审查结论：不可简化。分类与映射合并会失去重复检出拦截点（§3.0/§3.3）；验证与入库分离是 62 号生命周期既定结构。六环节中四个（采集/验证/入库/分类的词表）复用既有设施，实际新建的只有分类器、映射引擎、生成器、编排器四个模块。
3. **"Phase 3 自我进化是否过度？Phase 2 是否已是终点？"** → 审查结论：Phase 3 已显式标注远期 P4（规则 5 豁免），且已裁剪 MAML/EWC 到 ICL。Phase 2 在工程上确实是"可长期停留的终点"；Phase 3 保留为演进方向而非承诺。

---

## 6. 开放问题

| # | 问题 | 状态 | 说明 |
|---|------|------|------|
| Q1 | 模块工厂 Phase 0→1 的施工优先级？ | 待裁定 | 知识→模块映射是核心独特点。新信息：U8 前置实测已就绪（P0 三件套 + P1 factor/strategy registry 均 active，§2.4），解锁条件比骨架预期更充分；优先级排序仍待人裁定 |
| Q2 | 11 号技能库接口假设待确认 | 待 11 号定稿 | §4.6 的技能检索/沉淀接口为假设（11 号填充中）：检索入口签名、候选技能提交流程待 11 号定稿后对齐；若不一致，修订本文 §4.6 |
| Q3 | 12 号自反 Agent 接口假设待确认 | 待 12 号定稿 | §4.7 的反思输出→再生成输入 schema、评估报告格式为假设（12 号填充中），待 12 号定稿后对齐；若不一致，修订本文 §4.7 |
| Q4 | 62 号文档 §6 标题"P1 待施工七注册表"与落盘状态不一致 | 待用户裁定（只读不改） | 实测 catalogs 下 factor/strategy 等注册表 YAML 已 active（schema v2.1，2026-08-10/15 #ARCH-BREG-001/002 系列工作），而 62 号文档 §6 章节标题仍写"待施工"。本文以落盘实测为准；62 侧文档是否需同步修订，按规则 13 只读不改，待用户裁定并转交易决策侧 |
| Q5 | discovery_agent 枚举是否扩展 `module_factory` 值 | 待用户裁定（62 侧只读不改） | 62 号 factor schema 枚举为 human/rd_agent/efs/hubble/quantevolver/other，模块工厂产出暂登记 `other`；枚举扩展属 62 侧 schema 变更，待裁定 |
| Q6 | 模块工厂自身的 depgraph 节点编号与域归属 | 待 03 号域边界裁定 | Phase 0 S1 需先以占位节点登记；正式编号（MOD-xxx）与归属域（D_AI / D_INFRA / 其他）待 03 号文档（AI-FILL-03）域边界裁定后确定 |
| Q7 | 潘潘课程剩余约 260 条是否作为 Phase 0 首批手动实例 | 待裁定 | 29 号文规划 546 条，实测已入库 286 条（factor 140 + strategy 146）；剩余条目天然是 Phase 0 SOP 的最佳练兵素材，但是否排入近期计划待人裁定 |
| Q8 | S0 采集增强候选与本文"文本优先"裁定的口径差异 | 待 Owner 裁定（不进施工计划） | 草稿（学习系统架构 §3.2/§3.3）登记三项采集增强：①漂移感知调度（ADWIN/DDM 检测数据分布漂移 → 自动调整采集频率/数据增强策略）；②VLM 图表理解（本地 VLM 解析 K 线图/技术图表 → {chart_type, trend, support, resistance, pattern, signal} 结构化描述，RTX 3090 可推理）；③PIT 门控（采集数据全量时间戳标注 + 财务数据强制延迟 60-90 天报告期 + 特征存储防前视验证）。三项属自动化采集范畴，与本文 §3.1"人筛选 + 文本优先、不做全自动爬虫"裁定存在口径差异——按指令登记为开放问题，是否吸收为 Phase 2+ 采集增强候选待裁定 |
| Q9 | MAML/EWC/LoRA"小参数可行"反证 vs 01 号文"用 ICL 替代"裁定 | 待 Owner 裁定（请求重新裁定，不改既定决策） | 草稿（12-D-ML-TRAIN §10.1 维度 5/7 + 20-D-RESEARCH §12.0 R-10/R-30/R-44）给出反证：①<1M 参数小模型 MAML 元训练在 RTX 3090 可行（新市场 5-10 episode 快速适应）；②在线 EWC 防遗忘为纯 Python Fisher 信息矩阵正则，无集群需求；③LoRA 适配器轻量微调（基础模型冻结）3090 可运行。与本文 C1/§5 #1"单 GPU 跑不动 MAML/EWC，Phase 3 用 ICL 替代"（01 号文 §5.3 裁定）冲突。草稿自身亦给出折中口径：小样本用 ICL、大样本用 MAML（R-62），MAML 管前向迁移、EWC 管后向保持。是否将"<1M 参数级 MAML/EWC + LoRA 适配器"从"不做"降级为"Phase 3 远期候选"待裁定；裁定前 §5 #1 维持不变 |

---

## 修订记录

| 日期 | 版本 | 变更 | 原因 |
|------|------|------|------|
| 2026-08-17 | 0.1.0 | 骨架建立 | 新建 |
| 2026-08-17 | 0.2.0 | 骨架填充完成：§2 六环节现状实测+核心独特点论证+约束表+15 类设施盘点；§3 按流水线"输入→处理→输出→验证"填充六个设计决策（含替代方案）+前沿演进方向登记（AlphaSchema/Hubble/ALPHAQT-BENCH/QuantaAlpha/QuantGPT）；§4 Phase 0→3 施工计划（depgraph L1 铁律）+62/11/12 号接口；§5 不做什么 10 条+过度工程三问审查；§6 开放问题扩至 7 项 | 按 AI-FILL-13 指令填充；11/12 号依赖文档未填充，接口按规则降级为假设并登记 Q2/Q3 |
| 2026-08-17 | 0.3.0 | 草稿缺口 15 项吸收：§3.1 信息价值四维评分+知识质量门禁四规则+Factor Mining 创意拓宽；§3.2 知识 11 类参照系+矛盾三态+语义去重；§3.3 Factor Mining Agent 分工+因果发现引擎/验证层候选；§3.4 三重语义一致性+进化式生成/分析师 Agent 反馈循环+可解释设计约束+自进化限速；§3.5 L1 三重一致性检查+L2 三阶段决策门控/高级回测+新增 L3+ 可解释性门控；§3.6 权重中心接口/append-only+Git-like 版本/AI 权重≤30% 注记；§4.4 S6 元学习机制细节登记（STOP/RISE/技能三元组/元反思四步/轻量 Agent 化四角色）；§5 新增 #11 自进化五禁；§6 新增 Q8（S0 采集增强口径差异）/Q9（MAML/EWC/LoRA 复核请求）；顺手修正 skills 设施数 57→58 个 .py（17 号文实测口径） | 按 AI-FILL-13-R2 指令回填；草稿源（学习系统架构 v8.1/12-D-ML-TRAIN/20-D-RESEARCH/23-D-AUT-PERM）实测核实后写入；与现行裁定冲突项（30 号文自进化搜索暂缓、01 号文 ICL 替代）不改既定决策，记 Q8/Q9 待 Owner 裁定 |

---

*维护者：AI 架构协调者*