---
module_id: ADR-0005
title: 以六层 KMS 架构作为 AI 驱动自主迭代的知识基础设施
doc_type: adr
status: partially_superseded
version: 1.1.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: 2026-04-18
superseded_by: ADR-0016
supersedes: null
related_rationale: R29, R30
related_open_questions:
- KMS-OQ-001
- KMS-OQ-002
- KMS-OQ-003
- KMS-OQ-004
tags:
- kms
- knowledge-management
- six-layer
- decision-gates
- adr
- e6
- sprint3
- sprint6
summary: 将知识管理系统（KMS）设计为六层流水线架构（Input Sources → Collection → Triage → Knowledge Base
  → Analysis → Integration），配合五决策门质量控制，使用 28 字段 Schema 规范化存储，通过 OCP 扩展点机制激活为系统能力。核心理由：分层职责隔离使
  AI 可在无人干预下完成 G1/G2 分拣，五决策门防止低质知识污染系统，六层架构使 KMS 与 OCP 扩展点机制形成闭环自我进化链路。
date: '2026-04-22'
ttl: permanent
---

# ADR-0005: 以六层 KMS 架构作为 AI 驱动自主迭代的知识基础设施

## 1. 状态（Status）

- **当前状态**：`partially_superseded`
- **提议日期**：2026-04-18
- **拍板日期**：2026-04-18
- **被谁取代**：ADR-0016（增量取代——保留 KMS 六层概念框架，实施技术栈从原方案切换至 ChromaDB/BGE-M3）
- **取代了谁**：无（新能力，无前代 ADR）

---

## 2. 背景与问题（Context）

### 2.1 核心问题

ZephyrAlpha 2.0 的战略目标是**AI 驱动的自主迭代量化系统**。为此需要解决一个根本问题：

> **AI 如何持续吸收外部知识（论文、开源、行业报告），并将其中有价值的部分自动转化为系统新能力（新因子、新策略、架构优化）？**

若无结构化的知识管理机制，会出现以下问题：
1. **知识熵增**：无筛选地堆积文档，低质内容淹没高价值洞察，AI 协作者找不到可操作的知识
2. **知识孤岛**：知识散落在会话记录/临时文件中，无法跨会话积累和传承
3. **激活断链**：知识与系统能力之间没有明确的落地路径，洞察停留在"我知道"而无法变成"系统能做"
4. **质量无保证**：AI 直接引用未验证的论文结论作为实施依据，存在"垃圾进、垃圾出"风险

### 2.2 触发来源

- `architecture-rationale-log.md` Stage 3（2026-04-17）：AI 自主迭代链路设计讨论
- `archive/reorg-2026-04-24/draft-abandoned/working-designs/knowledge-management-system-design.md`（Sprint 2 E1-E3，ARC-20260424-011）：六层架构设计稿
- 工作流 E（KMS 架构）：E4 + E5 完成物理落地后，升格为正式 ADR

### 2.3 约束条件

- **单人操作约束**：不能引入需要专职知识管理员的重型流程
- **AI 可执行性约束**：G1/G2 必须可以在无人干预下由 AI 自动执行
- **渐进演进约束**：KMS 骨架必须支持"先手工、后自动化"的渐进成熟路径
- **与 OCP 集成约束**：知识激活路径必须通过 ADR-0004 定义的 OCP 扩展点机制落地

---

## 3. 考虑过的方案（Options Considered）

### 方案 A：平铺文档目录（简单知识库）

将外部知识直接放入一个平铺目录（如 `docs/references/`），按来源类型分子目录存放，不做结构化流程。

- **优点**：
  - 极简，零运维成本
  - 适合知识量少（< 50 条）时快速起步
- **缺点**：
  - **无质量控制**：不做筛选，低质内容与高价值洞察混存，随知识量增长快速退化
  - **无激活路径**：文档放进去后，AI 协作者无法知道哪些值得实施，知识无法转化为能力
  - **无索引体系**：知识量 > 100 条后，AI 检索成本指数增长
  - **无生命周期**：不知道哪些知识已激活、哪些已过时
- **机构案例**：小型研究团队的临时知识库，无法支撑持续运营

### 方案 B：Wiki/Notion 风格的主题笔记库

按主题建立 Wiki 页面，每个主题汇聚相关知识，人工编辑整合。

- **优点**：
  - 人类可读性强
  - 结构灵活
- **缺点**：
  - **强依赖人工维护**：需要专职人员整理，单人操作不可持续
  - **AI 不友好**：非结构化 frontmatter，AI 无法机械处理
  - **无自动分拣**：采集-分拣-分析全靠人工，处理 387 个老树蓝图不现实
  - **激活路径不清晰**：知识如何转化为代码实现，没有定义明确的路径

### 方案 C：六层流水线架构 + 五决策门（本方案）

设计结构化的六层知识流水线（Input → Collection → Triage → Knowledge Base → Analysis → Integration），配合五决策门（G1-G5）质量控制，使用 28 字段标准化 Schema。

- **优点**：
  - **可 AI 自动化**：G1/G2 两个门可完全由 AI 执行，无需人工干预
  - **质量分层**：只有通过 G2/G3 的高价值知识才进入深度分析队列，防止知识熵增
  - **激活路径清晰**：G4 激活门明确定义"知识 → 系统能力"的转化步骤，通过 OCP 扩展点落地
  - **渐进演进**：骨架先建好，可从手工触发开始，逐步演进为全自动
  - **KMS 与 OCP 闭环**：六层架构的第六层（Integration）直接对接 ADR-0004 的扩展点机制，形成完整的"知识 → 能力"闭环
- **缺点**：
  - 设计复杂度高于方案 A/B，初期有一定搭建成本
  - 28 字段 Schema 对每条条目有较高的元数据要求
  - G2/G3 的 AI Prompt 模板（KMS-OQ-001）需要精心设计才能保证质量
- **机构案例**：Two Sigma Alpha Research Pipeline（多层因子评估流水线）、ThoughtWorks Technology Radar（Hold/Assess/Trial/Adopt 分级体系）

### 方案 D：图数据库知识图谱

使用 Neo4j 等图数据库构建知识图谱，知识以节点/边存储，支持复杂关系查询。

- **优点**：
  - 关系表达能力极强
  - 支持跨知识推理
- **缺点**：
  - **过度工程**：当前阶段知识量不足以发挥图数据库优势
  - **高运维成本**：需要维护额外的数据库服务
  - **与 docs/ 体系不兼容**：ZephyrAlpha 以 Markdown + Git 为核心存储，引入独立数据库打破单一真源原则
  - **AI 访问障碍**：AI 协作者通过文件系统读取知识，图数据库访问需要额外工具层

---

## 4. 决策（Decision）

**最终选择：方案 C — 六层流水线架构 + 五决策门**

选择方案 C 的核心理由：

1. **AI 自动化可行性**：G1/G2 的判断逻辑可以完全编码为规则（G1：格式/去重/长度检查）或 AI 标准化任务（G2：domain 分类 + 评分），无需人工逐条判断，支撑"处理 387 个老树蓝图"这类批量任务。

2. **激活路径闭环**：方案 C 的 Layer 6 Integration 直接通过 OCP 扩展点（ADR-0004 的 `FactorBase` / `StrategyBase` / `BrokerInterface`）将知识转化为代码，形成"论文 → KMS 分拣 → ADR 提案 → OCP 实现"的完整自主迭代闭环。方案 A/B 都缺少这个明确的激活路径。

3. **渐进成熟可行性**：六层架构可以"骨架先行"——先建目录结构（E4）和 Schema（E3），手工执行 G2/G3，再逐步引入自动化脚本。方案 D 需要数据库服务从一开始就运行。

4. **防熵增设计**：`rejected/` 目录记录拒绝原因，`04_future_capabilities/` 储存未成熟的高价值知识，`06_lessons_learned/` 记录失败激活经验。这三个"负样本库"是方案 A/B 都没有的熵减机制。

---

## 5. 六层架构决策细节（Key Design Decisions）

### 5.1 为什么选择"六层"而非更少层次

| 层数选择 | 分析 |
|---------|------|
| 三层（Input/Store/Output）| 分拣（Triage）和分析（Analysis）合并后，AI 无法区分"快速过滤"和"深度评估"的不同算力消耗，导致每条知识都做深度分析，成本失控 |
| 四层（+Triage）| 缺少独立的 Analysis 层，高价值知识无法与普通归档条目区分，`03_analyzed/` 的深度分析报告无法独立存储 |
| **六层（最终选择）**| Input/Collection/Triage/Knowledge Base/Analysis/Integration 六层职责清晰，每层有明确的输入/输出和 Gate 控制，可独立演进 |
| 八层以上 | 过度设计，增加系统复杂性 |

### 5.2 五决策门的设计依据

| 门 | 设计考量 |
|----|---------|
| G1 Ingest | 规则引擎执行，无需 LLM，保证采集层成本可控 |
| G2 Classification | LLM 批量执行（Kimi 长上下文），`ai_triage_score` 阈值 0.7 平衡精度与召回 |
| G3 Evaluation | LLM 深度分析，手动触发，每周处理，控制 API 成本 |
| G4 Activation | 强制人工最终拍板（`ai_value_score >= 7.0` 是必要条件，非充分条件），防止 AI 自主激活产生资金风险 |
| G5 Graduation | 实证验证驱动，确保"最佳实践"有真实数据支撑，不是 AI 主观判断 |

**G4 强制人工的设计理由**：激活涉及资金运用和架构改造，必须有人类最终确认，这是系统安全边界。AI 可以评分、建议、准备，但不能自主激活。

### 5.3 28 字段 Schema 的分组逻辑

Schema 的 8 个分组（标识/来源/分类/AI 分拣/深度评估/激活/升格/生命周期）对应 KMS 六层的数据流：

```
G1 填写：标识 + 来源（原始事实，AI 无需判断）
G2 填写：分类 + AI 分拣（AI 标准化判断）
G3 填写：深度评估（AI 深度分析）
G4 填写：激活（人工+AI 共同填写）
G5 填写：升格（实证结果）
全程：生命周期（状态机追踪）
```

这种"按门填字段"的设计使 AI 在任意阶段都只需关注当前门的字段，减少认知负担。

---

## 6. KMS 与 OCP 扩展点的协同关系

```
外部知识（学术论文 / 开源项目）
        ↓ G1 Ingest → G2 Classification → G3 Evaluation
        ↓
docs/08_knowledge/03_analyzed/
  ai_value_score >= 7.0 + activation_conditions 满足
        ↓ G4 Activation（人工拍板）
        ↓
激活路径（按知识类型）：
  因子类 → FactorBase 实现 + @FactorRegistry.register（ADR-0004）
  策略类 → StrategyBase 实现 + @StrategyRegistry.register（ADR-0004）
  架构类 → 新 ADR 提案 + 任务书更新
        ↓ G5 Graduation（实证验证）
        ↓
docs/08_knowledge/07_best_practices/ 或 06_lessons_learned/
  FactorRegistry / StrategyRegistry 标记 validated
```

**关键设计约束**：KMS 激活（G4）不绕过 OCP 扩展点。所有通过 G4 的知识落地，必须走 `FactorBase` / `StrategyBase` / `BrokerInterface` 协议实现，而不是直接修改现有代码。这保证了 OCP 原则（开闭原则）的完整性。

---

## 7. 后果（Consequences）

### 正面后果

- **AI 自主迭代链路完整**：从外部知识采集到系统能力激活的全流程有明确的架构支撑
- **知识累积可持续**：G1/G2 自动化 + 结构化 Schema 使知识库可以持续增长而不退化
- **质量可追溯**：每条知识的评分理由、激活决策、验证结果均有记录，支持事后审计
- **与 OCP 形成闭环**：ADR-0004（OCP）+ ADR-0005（KMS）共同构成 ZephyrAlpha 自我进化的两大架构锚点
- **老树蓝图吸收路径清晰**：387 个老树蓝图通过 C 工作流进入 `01_raw_intake/blueprints/`，走完 G1-G4 后按 P0-P4 分级落地

### 负面后果 / 权衡

- **初期搭建成本**：28 字段 Schema + 五决策门需要时间建立 Prompt 模板和自动化脚本（KMS-OQ-001 待解决）
- **G2/G3 LLM 成本**：批量处理 387 个蓝图时有显著 API 成本，需要配额管理
- **手工阶段的摩擦**：在 `scripts/governance/memory_pipeline/` 脚本未实现前，G1/G2 需要半手工执行

### 未来需要重新审视的触发条件

满足以下条件时，本 ADR 应被重新评估：

- KMS 条目超过 2000 条，Markdown 文件索引性能不足 → 考虑引入轻量级向量数据库（SQLite + embeddings）
- G2/G3 AI 误判率 > 20% → 重新设计 Prompt 模板（KMS-OQ-001）或引入人工标注辅助训练
- OCP 扩展点机制（ADR-0004）发生重大变更 → 同步更新 Layer 6 Integration 的激活路径

---

## 8. 落地动作（Implementation）

本决策的落地动作已在 Sprint 3 执行完成（E4 + E5）：

- [x] **E4**：创建 `docs/08_knowledge/` 完整目录体系（10 个子目录 + README + Schema）
- [x] **E5**：升级 `02-information-architecture.md §2` 中 `08_knowledge` 展开为 10 层
- [x] **E6**：本 ADR 草稿升格（当前文件）
- [x] **G1（Sprint 6）**：草稿升格为正式 ADR，移入 `adr/` 目录（Sprint 6 G1 完成）

待后续执行的落地动作（纳入后续 Sprint 跟踪）：

- [ ] **KMS-OQ-001**：设计 G2 分类 AI Prompt 模板
- [ ] **KMS-OQ-004**：确定 `indexes/` 文件的维护方式（手工 vs CI 自动）
- [ ] **C7（Sprint 6）**：P3 蓝图写入 `04_future_capabilities/`，P4 蓝图写入 `99_archive/retired-blueprints/`

---

## 9. 参考

- 相关 ADR：
  - ADR-0004：`adr/adr-0004-ocp-extension-points.md`（KMS 激活的执行机制）
- 相关文档：
  - `archive/reorg-2026-04-24/draft-abandoned/working-designs/knowledge-management-system-design.md`（本 ADR 的完整设计稿，ARC-20260424-011）
  - `08_knowledge/kms-entry-schema.md`（28 字段 Schema 规范）
  - `19_development_workspace/structure-and-mapping/blueprint-classification-taxonomy.md`（蓝图分级体系，C1 产出）
- 外部参考：
  - Two Sigma Alpha Research Pipeline：多层因子评估流水线的设计范式
  - ThoughtWorks Technology Radar 2024：Hold/Assess/Trial/Adopt 四象限分级模型

---

## 10. 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-04-18 | 1.0.0 | Sprint 3 E6 产出：从 knowledge-management-system-design.md 升格为正式 ADR 草稿。包含四方案对比（平铺目录/Wiki/六层流水线/图数据库）、六层决策细节（为何选六层、五决策门设计依据、28 字段分组逻辑）、KMS 与 OCP 协同关系图、G4 强制人工的安全设计理由。 |
| 2026-04-18 | 1.1.0 | Sprint 6 G1 升格：草稿状态 proposed → accepted，正式移入 adr/ 目录，待落地动作（KMS-OQ-001、KMS-OQ-004、C7）纳入后续 Sprint 跟踪。 |
