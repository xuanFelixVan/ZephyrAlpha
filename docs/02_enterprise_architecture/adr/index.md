---
classification: confidential
created_by: agent
date: '2026-05-02'
doc_type: index
language: zh
layer: cross_layer
merged_from: README.md + index.md
module_id: ADR-INDEX
owner: ZephyrAlpha-Owner
status: active
summary: 本目录下所有 ADR 的登记表，按编号排序。每条给出主题、当前状态与对应的 rationale-log 推导来源。
title: ADR 登记表
ttl: permanent
valid_from: 2026-04-17
version: 2.0.0
---

# ADR 登记表

> ## 🛑 ADR 体系冻结公告（2026-04-27 Wave 0 终审 · R72；2026-05-02 补充）
>
> **本 ADR 体系已进入冻结模式（Frozen）**：
>
> - **不再新增 ADR**：自 2026-04-27 起，新的架构决策记录通过 rationale-log + 双管线机制生产，不再以 ADR 格式写入本目录。
> - **现存 33 份 ADR 仍有效**：所有 `status: accepted`（含等价的 `active`）的 ADR 继续作为当前决策依据，可被任何文件引用。冻结 ≠ 作废。
> - **ADR-0003 已即时 superseded**：被 Wave 0/Wave 1 终审全面升级——详见 rationale-log R71/R72/R76/R80（双管线 + 单一草稿区 + V-12 门禁）。
> - **替代机制**：rationale-log（决策真源）+ 双管线（决策生产）+ 单一草稿区（drafts-and-audits/，frontmatter audit_status 状态机驱动）+ V-12 门禁（蓝图准入）+ M2/M9 共享 collection（决策检索）= 接管新增决策的生产职责。
> - **远期迁移计划**：M2 知识库（Vector Memory Service）建成后，现存 ADR 将批量迁入 `decisions` namespace（metadata.type=adr），届时本目录物理删除。详见 [B4 蓝图](../../03_modules/l01_infrastructure/vibe-coding-pipelines/blueprint.md)。
>
> **大白话**：ADR 不再新增，但已有的 33 份继续有效——就像一家老店不再接新订单，但之前的订单照样履约。

## 1. 本目录是什么

本目录是 ZephyrAlpha 2.0 **所有正式架构决策的永久凭证真源**。

每一份 ADR 回答**一个**架构级决策：为什么选 A 方案、不选 B/C 方案、选后的后果是什么。

## 2. ADR 属于哪类文档

| 问题 | 答案 |
|------|------|
| 回答什么？ | **WHY**（为什么做这个决策） |
| 什么时候写？ | **决策被接受（accepted）时**，不是讨论中 |
| 可变吗？ | **不可变**（accepted 后只能被 superseded） |
| 生命周期 | `proposed → accepted → (superseded by ADR-XXXX)` |
| 和 rationale-log 的区别 | rationale-log 是**推导链时间轴**，ADR 是**单个决策的快照凭证** |
| 和 Decision Memory Index 的区别 | Decision Memory Index 是**路由索引**，指向本目录的 ADR |

## 3. 命名与编号（Stage F 归一化后的铁律）

### 3.1 文件名

- **格式**：`adr-nnnn-<kebab-case-title>.md`（**全小写**，无例外）
- **编号**：4 位数字，从 `0001` 开始，**扁平空间 + append-only**
- **title 尾缀**：小写 kebab-case 英文短语（3~8 词）
- **示例**：
  - `adr-0001-canonical-source-of-truth.md`
  - `adr-0030-sqlite-task-metadata-store.md`
  - `adr-0041-session-handoff-protocol.md`

### 3.2 frontmatter 内部 `module_id`

- **格式**：`ADR-NNNN`（**大写**，无 `EA-` / `PROD-` 等 scope 前缀）
- **作用域**通过**目录**承载（本目录 = Enterprise Architecture ADR），不用前缀重复
- **示例**：`module_id: ADR-0011`

### 3.3 编号空间规则（扁平 + append-only）

- **扁平编号**：所有 ADR 使用同一个 4 位数字序列，**严禁**嵌套编号（如 `ADR-NNN-MMM` 子系列）
- **关联关系靠 `refines` / `supersedes` / `related_to` 字段**表达，不靠编号承载语义
- **append-only**：编号**永不回收、不回填、不重编**；跳号用 `status: skipped` 登记，留空用 `status: reserved` 登记
- **决策不可变**：`accepted` 后只能被 `superseded`，不能编辑历史内容

### 3.4 专业实践对标

- Michael Nygard ADR 原规范（2011）
- adr-tools（Nat Pryce，业界事实工具链）
- Joel Parker Henderson ADR GitHub Organization（1.5 万 star 汇编）
- AWS Prescriptive Guidance / Google Engineering Practices / ThoughtWorks Technology Radar

### 3.5 特殊情况

| 情况 | 处理 |
|---|---|
| 历史嵌套编号 | `ADR-011-*` 已合并至扁平序列 `ADR-0030~0041`（Stage F, 2026-04-25）|
| 编号跳空 | `ADR-0006` 登记为 `status: skipped`（见 §10.1）|
| 编号保留 | `ADR-0023~0029` 登记为 `status: reserved`（见 §10.2）|
| 新决策编号选取 | 取当前最大编号 + 1（**不得**回填 skipped/reserved 编号）|

## 4. 写作流程（生命周期）

```
┌──────────────────────────────────────────────────────────┐
│  Stage 1: 讨论中                                          │
│     rationale-log 追加 Stage N → 产生结论 R-YY           │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│  Stage 2: 草稿                                            │
│     新建 adr-drafts/adr-nnnn-xxx.md  (status: proposed)  │
│     路径：外部开发工作区（已移出项目）                  │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│  Stage 3: 拍板                                            │
│     status: proposed → accepted                           │
│     搬到：docs/02_enterprise_architecture/adr/           │
│     rationale-log 里的 R-YY 标注"→ ADR-NNNN"             │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│  Stage 4: 推翻（可选）                                    │
│     新建 ADR-MMMM 取而代之                                │
│     原 ADR-NNNN 标注 status: superseded + superseded_by  │
│     原文**不删改**                                        │
└──────────────────────────────────────────────────────────┘
```

## 5. 模板

新 ADR 复制 [`_template.md`](./_template.md) 即可。

## 6. 本目录不是什么

- ❌ **不是讨论区**（讨论放 `02_enterprise_architecture/architecture-rationale-log.md`）
- ❌ **不是任务清单**（动作放 `19_development_workspace/taskbooks/taskbook.md`）
- ❌ **不是未决登记簿**（未决放 `19_development_workspace/open-questions/open-questions-register.md`）
- ❌ **不是设计稿**（设计放 `19_development_workspace/working-designs/`）

## 7. 修订记录

| 日期 | 说明 |
|------|------|
| 2026-04-17 | 初版：建立 ADR canonical 目录、命名规则、生命周期与模板位置。 |
| 2026-04-25 | **Stage F 归一化 v2.0.0**：§3 命名与编号章节全面重写，纳入 Stage F 批次新增的 5 条铁律：(1) 文件名全小写；(2) module_id 无 scope 前缀；(3) 扁平编号 + append-only；(4) 关联关系通过 `refines` 字段；(5) 对标 Michael Nygard / adr-tools / AWS / Google 五家专业实践。新增 §3.5 特殊情况表（历史嵌套编号合并、skipped/reserved 说明）。README 版本 v1.0.0 → v2.0.0（major 版本跳跃因命名铁律重构）。|


## 8. 登记规则

新增 ADR 时，在第 9 节"登记表"追加一行。**按编号升序排列**，不要插行。

> ⚠️ **ADRs are frozen as of 2026-05-02**（Wave 0 终审后 ADR 系统进入冻结模式）：现存 33 份 ADR，不再新增。新增 ADR 时撕开此封条。

## 9. 登记表

| # | 主题 | 状态 | 拍板日期 | 推导来源 | 取代关系 |
|---|------|------|---------|---------|---------|
| [ADR-0001](./adr-0001-canonical-source-of-truth.md) | 确立 `docs/` 为唯一真源 | accepted | 2026-04-17 | rationale-log R1/R4-R6 | — |
| [ADR-0002](./adr-0002-single-schema-with-phased-required-fields.md) | 采用单一 frontmatter schema + 分阶段必填闸门 | accepted | 2026-04-17 | rationale-log R8/R12 | — |
| [ADR-0003](./adr-0003-dual-ai-collaboration-workflow.md) | 采用 Kimi 发散 + Opus 收口的双 AI 协作工作流 | **superseded** | 2026-04-17 | rationale-log Stage 13-14 + R71/R72/R76/R80 | 被 Wave 0/Wave 1 终审全面升级取代（2026-04-27 Wave 0）|
| [ADR-0004](./adr-0004-ocp-extension-points.md) | OCP 扩展点机制作为架构终局锚点（因子/策略/券商三层注册机制）| accepted | 2026-04-18 | rationale-log R29/R30 | — |
| [ADR-0005](./adr-0005-kms-architecture.md) | 以六层 KMS 架构作为 AI 驱动自主迭代的知识基础设施 | **partially_superseded** | 2026-04-18 | rationale-log R29/R30 | — |
| ADR-0006 | **— 空号（跳号，永久保留）** | `skipped` | — | 见 §10.1 跳号说明 | — |
| [ADR-0007](./adr-0007-frontend-platform.md) | 前端层不进 src/ 15 层，作为独立 frontend/ 平台层 | accepted | 2026-04-18 | rationale-log R29/R30/R64 + OQ-043 | — |
| [ADR-0008](./adr-0008-federated-architecture.md) | 四架构联邦制（Federated-Light）与 Metamodel 桥梁 | accepted | 2026-04-18 | rationale-log R29/R30/R64 + OQ-045/OQ-046 | — |
| [ADR-0009](./adr-0009-src-14-layer-upgrade.md) | `src/zephyr/` 从 11 业务层升级至 14 业务层（+ shared = 15 物理目录）+ 17 项工程基础设施盲点补齐 | accepted | 2026-04-19 | rationale-log R29/R30/R31/R32/R67 + OQ-021/022/047/068/073 | — |
| [ADR-0010](./adr-0010-governance-three-layer-boundary.md) | 治理架构采用 Policy/Factory/Runtime 三层边界 + 三角闭环反馈 + 预留三层 AI 员工口子 + Scheme B 分阶段激活 | accepted | 2026-04-19 | rationale-log R65/R66 + OQ-026/062/063 | — |
| [ADR-0011](./adr-0011-runtime-planes-orthogonal-view.md) | **正交视图第一张** Runtime Planes（Hot/Warm/Cold）+ 正交视图方法论 5 条铁律 OV-P1~P5 | accepted | 2026-04-19 | rationale-log R69 + OQ-083 | — |
| [ADR-0012](./adr-0012-capability-maturity-heatmap-view.md) | **正交视图第二张** Capability Maturity Heatmap（L0-L5 × 14 层 × 7 能力域）| accepted | 2026-04-19 | rationale-log R70 + OQ-084 + 外部评审 P1 短板 | — |
| [ADR-0013](./adr-0013-governance-system-admission-criteria.md) | 治理系统准入铁律（Governance System Admission Criteria）| accepted | 2026-04-21 | Architecture-as-Code v2.0 Phase D 批次 | — |
| [ADR-0014](./adr-0014-module-admission-principles.md) | 模块准入铁律（MOD-P1~P4 四级筛选 + INJ-001~006 六条铁律）| accepted | 2026-04-22 | architecture-model 候选池注入需求 | — |
| [ADR-0015](./adr-0015-context-engine-architecture.md) | **Vibe Coding 2.0 核心服务** Context Engine 架构（NetworkX + Qwen2.5-3B ONNX + MCP 能力协商）| accepted | 2026-04-24 | vibe-coding-audit-merged.md §Kimi 9.7 + §Qwen 选型 #1-3 | — |
| [ADR-0016](./adr-0016-vector-memory-chromadb-bge-m3.md) | **Vibe Coding 2.0 核心服务** Vector Memory Service（ChromaDB 0.6 + BGE-M3 ONNX + 递归分块 + 5 Collection + 级联 4 场景）| accepted | 2026-04-24 | §Kimi 7.5.2 + §Qwen #4-6 | 增量取代 ADR-0005 KMS 实施路径 |
| [ADR-0017](./adr-0017-agent-orchestrator-sqlite-asyncio.md) | **Vibe Coding 2.0 核心服务** Agent Orchestrator（SQLite + asyncio.Queue + enum 状态机 + 规则基幻觉检测）| accepted | 2026-04-24 | §Kimi 10.6.2 + §Qwen #7-11 | 替代已归档 workflow-interface-contract.md |
| [ADR-0018](./adr-0018-agent-sandbox-windows-acl.md) | **Vibe Coding 2.0 安全基石** Agent Sandbox（Windows ACL + Firewall + Job Object 三件套）| accepted | 2026-04-24 | §Kimi 11.6.1 + §Qwen #12 | — |
| [ADR-0019](./adr-0019-feedback-loop-engine.md) | **Vibe Coding 2.0 核心服务** Feedback Loop Engine（SQLite 时序 + EMA + Protocol 单向依赖，修复 VG-07）| accepted | 2026-04-24 | §Kimi 13.5.2 + §Qwen #13-14 | — |
| [ADR-0020](./adr-0020-llm-security-gateway.md) | **Vibe Coding 2.0 安全基石** LLM Security Gateway（四层防御 + fail-closed + OWASP LLM Top 10 映射，D6 红线 2.2→5.5）| accepted | 2026-04-24 | §Kimi 11.6.1 + §Qwen #15-17 + §GLM D11 | 替代已归档 tool-interface-contract.md |
| [ADR-0021](./adr-0021-ssot-validator-phase0-gate.md) | **Phase 0 唯一强制门禁** SSoT Validator（三级违规分级 + pre-commit 阻塞 + 4-6 人日升级）| accepted | 2026-04-24 | §Kimi 根因 #7 + §Qwen Phase 0 升级 + §Opus 4.7 §四 | — |
| [ADR-0022](./adr-0022-dual-track-directory-governance.md) | **双轨目录治理** Spine-and-Wings (LPC) 架构范式（C 轨业务分层 + B 轨平台能力）| accepted | 2026-04-25 | Stage D 批次归一化（决策树 + 5 个案 + LPC 缩写说明）| — |
| ADR-0023 ~ ADR-0029 | **— 保留编号（Stage F 归一化未使用）** | `reserved` | — | 见 §10.2 编号保留说明 | — |
| [ADR-0030](./adr-0030-sqlite-task-metadata-store.md) | **细化决策** SQLite 作为本地元数据存储层（refines ADR-0011）| accepted | 2026-04-24 | R-PHASE1-META + R-ZERO-DEP | — |
| [ADR-0031](./adr-0031-chromadb-vector-retrieval.md) | **细化决策** ChromaDB 向量检索层（驳回 FAISS/Qdrant/Whoosh/pgvector，refines ADR-0011）| accepted | 2026-04-24 | R-PHASE2-VECTOR + R-ZERO-DEP + R-EMBEDDING-LOCAL | — |
| [ADR-0032](./adr-0032-agent-orchestration-architecture.md) | **细化决策** Agent 编排架构（Router + Orchestrator + Health Monitor + 幻觉检测，refines ADR-0011）| accepted | 2026-04-24 | R-AGENT-ORCHESTRATION + R-HEALTH-MONITOR | — |
| [ADR-0033](./adr-0033-mcp-protocol-integration.md) | **细化决策** MCP 协议在 ZephyrAlpha 的规范与集成边界（refines ADR-0011）| accepted | 2026-04-24 | R-MCP-ADOPTION + R-TOOL-CONTRACT | — |
| [ADR-0034](./adr-0034-semi-auto-evolution-architecture.md) | **细化决策** 半自动进化架构（evolve() + 三层反馈闭环 + 五类进化信号，refines ADR-0011）| accepted | 2026-04-24 | R-SEMI-AUTO-EVOLUTION + R-FEEDBACK-LOOP + R-HUMAN-IN-LOOP | — |
| [ADR-0035](./adr-0035-intent-parsing-three-stage.md) | **细化决策** 意图解析三阶段演进（keyword → embedding → LLM，refines ADR-0011）| accepted | 2026-04-24 | R-INTENT-EVOLUTION + R-PHASE-GRADUAL + R-COST-CTRL | — |
| [ADR-0036](./adr-0036-deferred-queue-async-workflow.md) | **细化决策** Deferred Queue 异步工作流调度层（refines ADR-0011）| accepted | 2026-04-24 | R-PHASE1-ASYNC + R-ZERO-DEP | — |
| [ADR-0037](./adr-0037-observer-event-bus.md) | **细化决策** Observer 发布订阅模式（零依赖事件总线，refines ADR-0011）| accepted | 2026-04-24 | R-PHASE1-ASYNC + R-ZERO-DEP | — |
| [ADR-0038](./adr-0038-file-as-task-paradigm.md) | **细化决策** File-as-Task 范式（文件即任务最小单元，refines ADR-0011）| accepted | 2026-04-24 | R-PHASE2-FILE-AS-TASK + R-SSOT-FILE | — |
| [ADR-0039](./adr-0039-cove-hallucination-detection.md) | **细化决策** Chain-of-Verification 幻觉检测策略（驳回 SelfCheckGPT/Reflexion，refines ADR-0011）| accepted | 2026-04-24 | R-COVE-ADOPTION + R-DUAL-MODEL-CROSS + R-INTENT-DEGRADE | — |
| [ADR-0040](./adr-0040-pydantic-v2-structured-contracts.md) | **细化决策** AI 结构化输出契约采用 Pydantic v2（refines ADR-0011）| accepted | 2026-04-24 | R-OUTPUT-CONTRACT + R-TYPE-SAFETY | — |
| [ADR-0041](./adr-0041-session-handoff-protocol.md) | **细化决策** Session Handoff Protocol 跨会话交接协议（refines ADR-0011）| accepted | 2026-04-24 | R-PHASE1-HANDOFF + R-SESSION-GOV | — |

## 10. 状态说明

| 状态 | 含义 |
|-----|------|
| `proposed` | 草稿中，放在外部开发工作区，尚未拍板 |
| `accepted` | 已拍板，放在本目录，生效 |
| `active` | **等价于 accepted**（历史遗留：33 份 ADR frontmatter 统一使用 `active`，语义与 `accepted` 完全等价，无需批量迁移） |
| `superseded` | 被新 ADR 取代，原文保留；`superseded_by` 字段指向新 ADR |
| `partially_superseded` | **部分取代**：概念框架保留，但实施路径被新 ADR 替代（如 ADR-0005 被 ADR-0016 增量取代——KMS 六层框架仍有效，技术栈切换至 ChromaDB）。`superseded_by` 指向新 ADR，但原文中未取代的部分仍为当前决策依据 |
| `deprecated` | 已废弃但未被取代（极少使用） |
| `skipped` | **跳号（空号）**：该编号被分配出去但最终未被使用，编号不可复用（append-only 编号空间原则） |
| `reserved` | **保留号（Stage F 归一化副产物）**：编号段留空以预备未来使用，本质与 skipped 不同（skipped 是"意外"，reserved 是"预期"），编号同样不可回填已拍板内容 |

## 10.1 ADR-0006 跳号说明

> ADR-0006 从未建立草稿，是真正的空号。跳号原因（OQ-025 未决 + OQ-026 延后）、治理决策（允许跳号，对标 Linux Kernel / Rust RFC / Google / Amazon / Microsoft append-only 编号空间）、永久不可复用铁律详见修订记录 2026-04-19 批次 H。

## 10.2 ADR-0023 ~ ADR-0029 保留号说明

> 编号 ADR-0023~0029 共 7 个编号为有意识保留（`reserved`），Stage F 归一化（2026-04-25）时原嵌套编号 ADR-011-xxx 合并续号至 ADR-0030+，刻意为中间段留空以形成语义断层。reserved 编号可供未来主线决策使用，但不得回填或追溯升格。与 ADR-0006（skipped）的区别：前者是有意留空，后者是意外跳号。详见修订记录 2026-04-25 Stage F 归一化批次。

## 11. 修订记录

| 日期 | 说明 |
|------|------|
| 2026-04-17 | 初版：登记 ADR-0001 / ADR-0002 / ADR-0003。 |
| 2026-04-18 | Sprint 6 G1：登记 ADR-0004（OCP 扩展点）+ ADR-0005（KMS 六层架构），均于 2026-04-18 正式 accepted。 |
| 2026-04-19 | **S14-Phase2 批次 H**：(1) ADR-0007（前端平台层）+ ADR-0008（四架构联邦制）从 `adr-drafts/` 追溯性升格为 accepted（retroactive backfill，拍板日期保留 2026-04-18 OQ-043/OQ-045 关闭日，升格日期为 2026-04-19）；(2) ADR-0006 显式登记为 `skipped` 空号，新增 §3bis 跳号说明 + 状态说明新增 `skipped` 状态；(3) 僵尸草稿清理：`adr-drafts/` 下 ADR-DRAFT-0004 / DRAFT-0005 / DRAFT-0007 / DRAFT-0008 物理删除（前两者是正式版升格后遗留的僵尸，后两者本次已搬到本目录）；(4) ADR-DRAFT-0009（src 15 层升级）保留在草稿目录待后续批次拍板。index 版本 v1.1.0 → v1.2.0。|
| 2026-04-19 | **S14-Phase2 批次 I-Reopen**：新增 **ADR-0010**（治理架构三层边界 Policy/Factory/Runtime + 三角闭环 + AI 员工三层预留口子 + Scheme B 分阶段激活）v1.0.0 accepted，承载 R66 五议题（D1-D4 + OQ-026）一次性拍板结果。ADR-0009 编号**保留**（未使用，非 skipped——后续批次可用）。index 版本 v1.2.0 → v1.3.0。同步相关新建/更新：`target-architecture/09-governance-architecture.md` v1.0.0 active（TOGAF 视图 9/10 → 10/10）+ `working-designs/governance-three-layer-boundary-design.md` v1.0.0 accepted + OQ-026 由 deferred 关闭（采纳 Scheme B）。 |
| 2026-04-19 | **S15-Phase1 J1**：新增 **ADR-0011**（Runtime Planes 正交视图 Hot/Warm/Cold，TOGAF 之外第一张正交视图 + 正交视图方法论 5 条铁律 OV-P1~P5 落地，对标 Citadel/Jane Street/Two Sigma/Jump/Renaissance 五家顶级量化机构控制面执行面物理切分共识）v1.0.0 accepted + **ADR-0012**（Capability Maturity Heatmap 正交视图 L0-L5 × 14 层 × 7 能力域 = 98 格热力图，对标 ArchiMate/Gartner/Goldman 三家方法论，回应 tests/外部评审.md 四家 AI 评审 P1 短板）v1.0.0 accepted。承载 R69 + R70 rationale + OQ-083 + OQ-084 即时 closed。同批次联动 6 份文件：新建 `target-architecture/04bis-runtime-planes.md` v1.0.0 active + `target-architecture/04ter-capability-heatmap.md` v1.0.0 active + `src/zephyr/shared/contracts/runtime_plane_tag.py` v1.0.0 契约预留；更新 `03-application-architecture.md` v1.10.0（§4.0 Runtime Plane Attribution Index 索引节）+ `09-governance-architecture.md` v1.2.0（§1.2bis Runtime 层 ≠ Runtime Plane 铁律澄清 + §4.5.1 D 家族详表新增 Runtime Plane 列）+ `10-frontend-architecture.md` v1.1.0（§7.5 前端三平面归属：Warm 主 + Hot-adjacent + Cold 报表 + 浏览器栈天然不满足 Hot Path 硬门槛澄清）+ `target-architecture/README.md` v1.7.0（§1ter 正交视图体系方法论整节 + §2 清单新增 04bis/04ter 🔷 标记 + §4 Mermaid 依赖图新增 RTP + CHM 黄色高亮节点 + 9 条虚线正交标注关系）。零业务决策变动，零代码影响。TOGAF 10 视图完整度维持 10/10，正交视图数量从 0 升 2。index 版本 v1.4.0 → v1.5.0。|
| 2026-04-19 | **S15-Phase1 J0-b**：**ADR-0009** 编号启用。`19_development_workspace/adr-drafts/ADR-DRAFT-0009-src-15-layer-upgrade.md v1.0.0 proposed` 采用 **IETF RFC "Retitle + Errata"** 升格做法，移动到 `adr/adr-0009-src-14-layer-upgrade.md v1.1.0 accepted`——标题由"11→15 层升级"改为"11→14 业务层升级 + shared 深化"澄清口径歧义（14 业务层 L00-L13 + shared 横切目录 = 15 个物理顶级目录，两种计数并存业界通用），L11 命名校准 `strategic_decision → ml_platform`（OQ-073 R31），L10 命名校准 `governance_compliance → compliance`（OQ-073 R32），§8 新增 Errata 4 条勘误记录 + §9 业界对标 5 家机构（Goldman/JPM/Two Sigma/Citadel/BlackRock）对应 OQ-068 closed 结论。原 DRAFT 物理删除（git 历史保留）。index 版本 v1.3.0 → v1.4.0。本次升格零决策变更，仅口径澄清。|
| 2026-04-24 | **B-e 批次（7 条一次性 accepted）**：登记 **ADR-0014**（模块准入铁律，漏登补上）+ **ADR-0015 ~ ADR-0021**（Vibe Coding 2.0 核心决策 7 条：6 大核心服务 5 条 + SSoT Phase 0 门禁 1 条 + Agent Sandbox 1 条）。7 条全部以 vibe-coding-audit-merged.md 三源共识（Kimi 根因 + Qwen 选型 + GLM/Opus 裁定）为真源；关键创新：（1）ADR-0021 作为 Phase 0 唯一强制门禁，阻塞下游一切建设；（2）ADR-0020 LSG 引入 fail-closed 语义，是 6 大核心服务中唯一故障时拒绝继续的服务；（3）ADR-0019 FLE 通过 Protocol 单向依赖修复 VG-07，零循环依赖；（4）ADR-0016 增量取代 ADR-0005 KMS 实施路径（不废弃 ADR-0005，只切换实施栈）；（5）ADR-0017/0020 替代已归档 workflow/tool-interface-contract.md。D6 审计红线修复路径（2.2 → Phase 1 末 5.5）通过 ADR-0018 + ADR-0020 双保险达成。index 版本 v1.5.0 → v1.6.0。|
| 2026-04-25 | **Stage F 归一化批次（命名空间 + 编号空间大收敛）**：本批次完成 6 项命名治理：(1) **文件名全体小写化**：34 个 ADR 文件 `ADR-NNNN-*.md` → `adr-nnnn-*.md`，对标 Michael Nygard / adr-tools / AWS / Google 业界扁平小写惯例；(2) **嵌套编号合并续号**：原 `ADR-011-001 ~ ADR-011-020` 共 12 个跳号子决策合并续号至主序列 `ADR-0030 ~ ADR-0041`，嵌套编号空间**永久废除**，关联关系改为通过 `refines: [ADR-0011]` frontmatter 字段表达；(3) **module_id 前缀统一**：全部去除 `EA-ADR-` 前缀（作用域已由目录承载，前缀冗余），改为 `ADR-NNNN`；(4) **doc_id → module_id schema 统一**：ADR-0014~0022 的 `doc_id:` 字段与其它 ADR 的 `module_id:` 字段分裂统一，全部改为 `module_id:`，同时去除冗余的 `type: adr`；(5) **status 大小写统一**：index.md / README.md 的 `active` → `Active`，与 frontmatter schema 一致；(6) **_template.md 清理**：module_id 去 EA-, 补 refines 占位字段，valid_from 占位符修正；(7) **ADR-0022 追登**：本次同步补登漏登的 ADR-0022（双轨目录治理）；(8) **ADR-0023~0029 保留号登记**：有意识保留 7 个编号，新增 §3ter 保留号说明 + 状态说明新增 `reserved` 状态。全库引用更新 200+ 处；修订决策零变动，仅命名/编号空间规整化。ADR-0011 升级至 v1.1.0 加 §6bis 细化决策族整节。index 版本 v1.6.0 → v2.0.0（major 版本跳跃因编号空间重构）。|
