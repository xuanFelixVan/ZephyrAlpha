---
module_id: PS-STD-004
title: ZephyrAlpha 规则分类与冲突裁决标准
doc_type: standard
status: active
version: "2.0.2"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-01"
valid_from: "2026-04-30"
summary: "ZephyrAlpha 项目规则分类体系与冲突裁决机制的唯一真源。上半卷定义五维分类（Domain/Layer/Scope/Stability/Executor），下半卷定义基于五维分类的冲突裁决推导链（stability→layer→scope→Owner）。原 PS-STD-008（rule-priority-hierarchy.md）已合并入本文件。"
ttl: permanent
tags: [rule-classification, taxonomy, conflict-resolution, priority, derivation-engine, ssot, meta-standard, frontmatter]
rule_form: declarative
scope: global
stability: stable
verifiability: manual
depends_on:
  - {target: PS-STD-001, at: "§2~§3", why: "字段定义+受控词表——元数据SSoT"}
ai_autonomy: human_gated
---

# ZephyrAlpha 规则分类与冲突裁决标准

> **module_id**: PS-STD-004 | **version**: 2.0.2 | **status**: active
>
> 本标准是 ZephyrAlpha 项目**规则分类体系**和**规则冲突裁决机制**的唯一真源。
>
> **上半卷（§2-§8）**：五维分类体系——所有规则文档按五个维度（Domain/Layer/Scope/Stability/Executor）分类。
> **下半卷（§9-§11）**：冲突裁决推导链——当两条规则冲突时，按 stability → layer → scope → Owner 链式推导优先级。
>
> > **合并声明**：v2.0.0 合并原 PS-STD-008（rule-priority-hierarchy.md）。理由：PS-STD-008 自述"本文不存数据，只存推导规则……PS-STD-004 的五维分类是数据源"——分类与裁决是供需关系，分开存储增加 AI 的上下文翻页成本。合并后 12 个 meta 文件减为 11 个。
>
> **根因**：当前规则分类仅依赖 `doc_type` 一个维度，无法表达：
> - 这条规则的作用范围是全局还是模块级？
> - 这条规则能不能被 AI 自主修改？
> - 这条规则是稳定的还是可能频繁变更？
> - 这条规则属于哪个领域？
> - 两条规则冲突时，按什么顺序裁决？
>
> 对标：ISO 11179（元数据分类）、Library of Congress Classification（多维分类）、
> Kubernetes SIG（领域分组）、Google Canonical Sources（权威层级）、
> ITIL Problem Management（冲突优先）。

---

## 1. 目的与范围

### 1.1 目的

为 ZephyrAlpha 项目建立多维规则分类体系与冲突裁决机制，确保：

- **AI 员工**可以按领域、范围、稳定性精确检索规则，而非全量扫描
- **规则冲突仲裁**可以基于分类维度快速定位冲突源并链式推导优先级
- **规则生命周期管理**可以按稳定性分级控制变更频率
- **规则权限管理**可以按执行者维度控制谁能修改什么

### 1.2 责任范围（本标准管什么）

本标准管理以下内容：
- 规则文档的**五维分类体系**——domain/layer/scope/stability/ai_autonomy 五个维度的受控词表和分类规则
- **scope 和 stability 字段**的 frontmatter 定义
- 规则之间的**冲突裁决推导链**——stability→layer→scope→Owner

### 1.3 责任边界（本标准不管什么）

本标准**不**覆盖以下内容：
- 规则文件的**生命周期状态机**（draft→active→deprecated）→ 以 PS-STD-009（rule-lifecycle-and-change-standard.md）为准
- 规则文件的**变更审批门控**（P0-P3 流程）→ 以 PS-STD-009 为准
- frontmatter 字段的完整定义（类型、校验规则）→ 以 PS-STD-001（metadata-registry.md）为准
- 标准文档的章节结构 → 以 PS-STD-002（document-structure-standard.md）为准

### 1.4 适用范围

本标准适用于 `01_policies_and_standards/` 下的所有规则文档。

### 1.5 术语

| 术语 | 含义 |
|------|------|
| **分类维度** | 规则的一个分类角度，每个维度有独立的受控词表 |
| **受控词表** | 维度值的合法集合，不允许自由扩展 |
| **规则画像** | 一条规则在五个维度上的取值组合，如 `{domain: document, layer: L1, scope: global, stability: stable, executor: ai_gated}` |
| **推导链** | 冲突发生时，按 stability → layer → scope 顺序链式推导优先级，三步后仍冲突则上报 Owner |
| **终极仲裁** | 推导链失效时，由 Owner 按 MTH-003 目标优先原则手动裁决 |

---

## 上半卷：五维分类体系

---

## 2. 五维分类体系

### 2.1 维度总览

| # | 维度 | 英文 | frontmatter 字段 | 受控词表大小 | 用途 |
|---|------|------|-----------------|:----------:|------|
| 1 | 领域 | Domain | `domain` | 9 | 按业务/技术领域分组规则 |
| 2 | 层级 | Layer | `layer` | 3 | 按规范性语言强度分层 |
| 3 | 作用范围 | Scope | `scope` | 4 | 按影响范围分级 |
| 4 | 稳定性 | Stability | `stability` | 3 | 按变更频率分级 |
| 5 | 执行者 | Executor | `ai_autonomy` | 3 | 按谁有权执行/修改分级 |

> **注意**：维度 2（Layer）和维度 5（Executor）已有对应的 frontmatter 字段（`layer` 和 `ai_autonomy`）。
> 本标准不新增这两个字段，而是明确其受控词表和分类规则。
> 维度 3（Scope）和维度 4（Stability）引入两个新字段：`scope`、`stability`。

---

### 2.2 Vibe Coding AI 检索策略映射

五维分类定义了"AI 怎么理解规则"，但 Vibe Coding AI 实际施工时需要"怎么找到规则"。以下是 Vibe Coding AI 从查询意图到分类维度的检索路径：

| AI 查询意图 | 检索路径 | 解释 |
|-----------|---------|------|
| "文件操作的禁止行为有哪些" | ① domain=document → ② stability=frozen→stable→evolving → ③ 优先读 PS-STD-003（SSoT） | 先定位领域 → 按稳定性排序（冻结文件权威性最高）→ 先读 SSoT |
| "某个模块的编码规则变更要走什么审批" | ① scope=module→domain → ② stability 维度 → ③ 查看 PS-STD-009 变更门控 | 自底向上：模块→领域→全局 |
| "AI 可以自主修改哪些文件" | ① executor=ai_modifiable → ② stability 不为 frozen → ③ layer 可写 | AI 自治权限的"可修改范围"由 Executor 维度直接筛选 |
| "当前项目所有规则文件有哪些" | ① layer=cross_layer → L1 → L2 → L3 → ② domain 分组 | 层级影响范围大头优先：全局规则 → 领域规则 → 会话规则 → 模块规则 |
| "这条规则和哪条有冲突" | ① scope 相同 → ② stability 是否矛盾 → ③ 见 §9 冲突裁决推导链 | 作用范围相同的规则最可能冲突，不同 scope 互不干扰 |

**检索原则**（按优先级排序）：
1. **SSoT 优先**：如果有 SSoT 文件声明了该领域（如 PS-STD-003 声明行为边界），先读 SSoT 再查领域规则
2. **稳定性过滤**：`frozen` 文件优先于 `stable` 优先于 `evolving`——冻结内容的权威性最高
3. **层级收敛**：`cross_layer` → `L1` → `L2` → `L3`——范围大的先读，在理解全局约束后再看局部
4. **领域隔离**：不同 `domain` 的规则互不冲突（如 `document` 领域的规则不会和 `vibe_coding` 领域的规则打架），冲突仅在同 domain 或 scope 重叠时发生

> **大白话**：AI 每次找规则时，先看"哪个领域的文件管这事"（domain），再看"文件稳不稳定、能不能改"（stability），然后按"全局→领域→模块"的顺序（layer）依次读。如果有 SSoT 文件，先读它——它是该领域所有规则的源头。

---

## 3. 维度 1：领域（Domain）

### 3.1 受控词表

| 值 | 含义 | 对应目录 | 示例文件 |
|---|------|---------|---------|
| `meta` | 元规则——定义规则怎么写、怎么分类、怎么变更 | `meta/` | PS-STD-002, PS-STD-003, PS-STD-004 |
| `document` | 文档治理——命名、路径、编码、生命周期 | `governance/document/` | file-naming-standard.md |
| `ai` | AI 治理——自治权限、入职、幻觉自检 | `governance/ai/` | ai-onboarding-guide.md |
| `task` | 任务治理——任务卡、交接、裁定 | `governance/task/` | task-card-standard.md |
| `vibe_coding` | Vibe Coding 操作——上下文规则、状态机、可验证性 | `operational/vibe_coding/` | vibe-coding-session-state-runbook.md |
| `architecture` | 架构治理——模块注入、入职规则 | `governance/module/` | module-injection-rules.yaml |
| `migration` | 迁移——旧树迁移审计（该文件从未创建，2026-05-02 已标记 deprecated） | `operational/migration/` | — |
| `devops` | DevOps——pre-commit、CI、部署 | `operational/devops/` | pre-commit-simplification-plan.md |
| `coding` | 编码——代码风格、安全编码 | 待建立 | encoding-safety-standard.md |

### 3.2 分类规则

1. 每条规则必须且只能属于一个领域
2. 领域与目录结构对应：`domain` 值决定文件存放位置
3. 新增领域需 Owner 批准 + ADR 记录

### 3.3 新增领域流程

1. 在本标准 §3.1 中新增受控词表条目
2. 在 `01_policies_and_standards/` 下创建对应子目录
3. 更新 PS-STD-001 的 `doc_type` 路径映射表
4. 更新 `document-metadata-index.yaml`

---

## 4. 维度 2：层级（Layer）

### 4.1 受控词表

| 值 | 含义 | 规范性语言 | 对应 doc_type | 章节 |
|---|------|----------|-------------|------|
| `L1` | 治理层——最高权威，可使用 MUST | MUST/SHOULD/MAY | policy, standard, ai_governance | 6~15 章（按子类型，见 PS-STD-002 §3.2） |
| `L2` | 设计层——中等权威，禁止 MUST | SHOULD/MAY | blueprint, construction_plan, adr, design, service_spec | 10 章 |
| `L3` | 基础层——信息性，禁止规范性语言 | 禁止 MUST/SHOULD | 其他所有 doc_type | 5 章 |
| `cross_layer` | 跨层——适用于所有层级 | 按引用上下文决定 | meta 类文档 | 6~15 章（按子类型，见 PS-STD-002 §3.2） |

### 4.2 分类规则

1. `layer` 字段由 `doc_type` 决定，不需要手动指定（但 frontmatter 中必须显式声明）
2. `cross_layer` 仅用于 meta/ 下的元规则
3. Layer 与规范性语言的对应关系由 PS-STD-002 定义，本标准引用

---

## 5. 维度 3：作用范围（Scope）

### 5.1 受控词表

| 值 | 含义 | 影响范围 | 示例 |
|---|------|---------|------|
| `global` | 全局——影响项目中所有文件、所有 session | 整个项目 | PS-STD-001, PS-STD-002, PS-STD-003 |
| `domain` | 领域——影响某个领域下的所有文件 | 一个领域 | file-naming-standard.md（影响所有文档的命名） |
| `module` | 模块——影响特定模块 | 一个或几个模块 | module-injection-rules.yaml |
| `session` | 会话——仅影响当前 AI session | 单个 session | vibe-coding-session-state-runbook.md |

### 5.2 分类规则

1. 每条规则必须且只能有一个 scope
2. scope 决定了规则变更时的通知范围：
   - `global` 变更：通知所有 Tier 1 消费者
   - `domain` 变更：通知该领域内的 Tier 1 消费者
   - `module` 变更：通知引用该模块的 Tier 1 消费者
   - `session` 变更：无需通知，下次 session 自动生效

### 5.3 新 frontmatter 字段：`scope`

```yaml
scope: global | domain | module | session
```

- **必填**：是（新增规则文档时）
- **默认值**：`domain`（如果未指定）
- **校验**：值必须在受控词表中

---

## 6. 维度 4：稳定性（Stability）

### 6.1 受控词表

| 值 | 含义 | 变更频率 | 修改条件 | 示例 |
|---|------|---------|---------|------|
| `frozen` | 冻结——除非 Owner 批准 + ADR 方可解冻 | 极低（年级别） | Owner 批准 + ADR + 90 天过渡期 | PS-STD-001, PS-STD-003 |
| `stable` | 稳定——变更需充分理由和审批 | 低（季度级别） | 领域负责人批准 + 消费者同步 | file-naming-standard.md |
| `evolving` | 演进中——可能频繁变更 | 中（月级别） | 正常变更流程即可 | vibe-coding-session-state-runbook.md |

### 6.2 分类规则

1. 每条规则必须且只能有一个 stability
2. stability 决定了变更的审批门槛：
   - `frozen`：Owner 批准 + ADR
   - `stable`：领域负责人批准
   - `evolving`：正常变更流程
3. stability 与 `ai_autonomy` 的关系（正交维度，非硬绑定）：
   - `frozen` → `ai_autonomy: immutable_core`（冻结文件 AI 不可修改）
   - `stable` → `ai_autonomy: human_gated` 或 `immutable_core`（均合法，取决于内容敏感度）
   - `evolving` → `ai_autonomy: ai_modifiable` 或 `human_gated`（均合法）

### 6.3 新 frontmatter 字段：`stability`

```yaml
stability: frozen | stable | evolving
```

- **必填**：是（新增规则文档时）
- **默认值**：`stable`（如果未指定）
- **校验**：值必须在受控词表中
- **与 `ai_autonomy` 的一致性约束**：`frozen` 必须对应 `immutable_core`（单向强制）。其余组合无硬性约束，遵循 PS-STD-001 §2.6 架构公民原则——`stability` 描述变更频率，`ai_autonomy` 描述修改权限，两者正交。

---

## 7. 维度 5：执行者（Executor）

### 7.1 受控词表

| 值 | 含义 | AI 权限 | 示例 |
|---|------|--------|------|
| `immutable_core` | 不可变核心 | AI 禁止修改，需 Owner 直接审批 + ADR | PS-STD-001, PS-STD-002 |
| `human_gated` | 人类门控 | AI 可提议修改，需 Owner 批准后执行 | rule-lifecycle-and-change-standard.md |
| `ai_modifiable` | AI 可编辑 | AI 可自主修改，需在 Session Log 记录 | vibe-coding-session-state-runbook.md |

### 7.2 分类规则

1. 本维度已由 `ai_autonomy` 字段覆盖，不新增字段
2. `ai_autonomy` 的受控词表由 PS-STD-001 定义，本标准引用
3. `ai_autonomy` 与 `stability` 必须保持一致性（见 §6.3）

---

## 8. 规则画像示例

### 8.1 meta/ 文件夹

| 文件 | domain | layer | scope | stability | executor |
|------|--------|-------|-------|-----------|----------|
| PS-STD-001 metadata-registry.md | meta | cross_layer | global | frozen | immutable_core |
| PS-STD-002 document-structure-standard.md | meta | cross_layer | global | frozen | immutable_core |
| PS-STD-003 behavior-boundaries-standard.md | meta | cross_layer | global | frozen | immutable_core |
| PS-STD-004 rule-classification-and-arbitration-standard.md | meta | cross_layer | global | stable | human_gated |
| PS-STD-009 rule-lifecycle-and-change-standard.md | meta | cross_layer | global | stable | human_gated |
| PS-STD-012 rule-verification-standard.md | meta | cross_layer | global | evolving | human_gated |

### 8.2 governance/document/ 文件夹

| 文件 | domain | layer | scope | stability | executor |
|------|--------|-------|-------|-----------|----------|
| file-naming-standard.md | document | L1 | domain | stable | human_gated |
| file-path-standard.md | document | L1 | domain | stable | human_gated |
| encoding-safety-standard.md | document | L1 | global | stable | human_gated |
| file-operation-safety-policy.md | document | L1 | domain | stable | human_gated |
| document-lifecycle-standard.md | document | L1 | domain | stable | human_gated |
| directory-structure-standard.md | document | L1 | global | frozen | immutable_core |
| unified-numbering-standard.md | document | L1 | domain | stable | human_gated |

### 8.3 governance/ai/ 文件夹

| 文件 | domain | layer | scope | stability | executor |
|------|--------|-------|-------|-----------|----------|
| ai-autonomy-authority-registry.md | ai | L1 | global | frozen | immutable_core |
| ai-onboarding-guide.md | ai | L1 | global | stable | human_gated |
| ai-hallucination-self-check-policy.md | ai | L1 | global | stable | human_gated |
| dual-editor-collaboration-policy.md | ai | L1 | domain | stable | human_gated |
| model-capability-contract.yaml | ai | L1 | global | stable | human_gated |
| session-log-schema.yaml | ai | L1 | domain | stable | human_gated |

### 8.4 governance/task/ 文件夹

| 文件 | domain | layer | scope | stability | executor |
|------|--------|-------|-------|-----------|----------|
| task-card-standard.md | task | L1 | domain | stable | human_gated |
| handoff-protocol.md | ai | L0 | domain | stable | immutable_core |

### 8.5 operational/ 文件夹

| 文件 | domain | layer | scope | stability | executor |
|------|--------|-------|-------|-----------|----------|
| vibe-coding-session-state-runbook.md | vibe_coding | L2 | session | evolving | ai_modifiable |
| vibe-coding-session-state-runbook.md | vibe_coding | L2 | session | stable | human_gated |
| vibe-coding-gate-checklist.md | vibe_coding | L2 | domain | stable | human_gated |
| old-tree-migration-audit.md | migration | L3 | module | — | —（deprecated: 文件从未创建） |
| pre-commit-simplification-plan.md | devops | L3 | domain | evolving | ai_modifiable |

---

## 下半卷：规则冲突裁决

---

## 9. 推导链

```
冲突发生时，按以下链路裁决：

  stability → layer → scope → Owner
```

| 步骤 | 维度 | 规则 | 来源 |
|:----:|------|------|------|
| 1 | stability | `frozen` > `stable` > `evolving` | §6 |
| 2 | layer | `cross_layer` > `L1` > `L2` > `L3` | §4 |
| 3 | scope | `global` > `domain` > `module` | §5 |
| 4 | Owner | 三步推导后仍冲突 → **停止操作，上报 Owner**（MTH-003 目标优先裁决） | PS-STD-011 MTH-003 |

**大白话**：两条规则打架时，先看谁更"硬"（stability——冻结的比稳定的牛逼），再比谁管得宽（layer——全局规则比领域规则优先），最后看谁范围大（scope——全局 > 领域 > 模块）。如果这三步比完还分不出高低，就停手问 Owner。AI 自己不做裁判。

---

## 10. 推导示例

### 10.1 不同 stability

| 规则 A | 规则 B | 裁决 |
|--------|--------|:--:|
| `PS-STD-003 §3`: "禁止删除审计日志"（stability=frozen） | 某 domain 规则："日志可压缩"（stability=evolving） | **A 胜**。frozen > evolving |

### 10.2 同 stability，不同 layer

| 规则 A | 规则 B | 裁决 |
|--------|--------|:--:|
| `GOV-DOC-009`: "引用必须用绝对路径"（cross_layer, stable） | 某模块规则："模块内可用相对路径"（L3, stable） | **A 胜**。cross_layer > L3 |

### 10.3 无法推导

| 规则 A | 规则 B | 裁决 |
|--------|--------|:--:|
| `PS-STD-003 ABS-14`: "不知道文件位置就不操作"（cross_layer, frozen） | `PS-STD-003 ABS-52`: "先读当前版本再改"（cross_layer, frozen） | **无法推导**（同 stability, 同 layer） → 上报 Owner |

---

## 11. 禁止行为

- **禁止**：AI 自行裁决无法推导的冲突（必须上报 Owner）
- **禁止**：AI 选择对自己"更方便"的规则
- **禁止**：AI 忽略高 stability 或高 layer 的规则
- **禁止**：AI 绕过推导链直接声称"这条规则优先"

---

## 12. SSoT 声明

| 声明项 | 值 |
|--------|-----|
| 本标准是什么的唯一真源 | ZephyrAlpha 项目规则分类体系的五个维度及其受控词表 + 规则冲突裁决推导链 |
| 下位法 | 领域规则可以定义领域内的子分类，但不得与本标准维度冲突 |
| 新增字段 | `scope` 和 `stability` 两个 frontmatter 字段由本标准定义 |
| 冲突仲裁 | 本标准与 PS-STD-001 冲突时，以 PS-STD-001 为准（字段定义权属于 PS-STD-001） |

---

## 13. 消费者注册表

| 消费者 | 消费方式 | Tier |
|--------|---------|:----:|
| PS-STD-001 | 新增 `scope`、`stability` 字段定义 | 1 |
| PS-STD-002 | 引用 Layer 维度定义 | 1 |
| behavior-boundaries-standard.md | 引用 Executor 维度定义 + 冲突裁决推导链 | 1 |
| document-metadata-index.yaml | 新增 `domain`、`scope`、`stability` 列 | 1 |
| frontmatter-schema.json | 新增 `scope`、`stability` 字段 Schema | 1 |
| check_frontmatter_metadata.py | 新增 `scope`、`stability` 校验规则 | 2 |
| PS-STD-009 rule-lifecycle-and-change-standard.md | 消费推导链决定 P0-P3 分级 | 1 |

---

## 14. 标准间引用规范

### 14.1 Normative 引用

| 引用标准 | 引用内容 | 与本标准的关系 |
|---------|---------|--------------|
| PS-STD-001 | `layer`、`ai_autonomy` 字段定义 | 本标准引用其字段定义，不重复定义 |
| PS-STD-002 | L1/L2/L3 层级定义 | 本标准 Layer 维度引用其层级定义 |
| PS-STD-011 MTH-003 | 目标优先裁决原则 | 推导链失效时的终极仲裁者 |

### 14.2 Informative 引用

| 引用文档 | 引用内容 |
|---------|---------|
| rule-lifecycle-and-change-standard.md (PS-STD-009) | 变更分级与本标准 Stability 维度及推导链的关系 |

---

## 15. 新字段注册声明

本标准向 PS-STD-001 注册以下新字段：

### 15.1 `scope` 字段

| 属性 | 值 |
|------|-----|
| 字段名 | `scope` |
| 域 | A（文档 frontmatter） |
| 必填 | 是（新增规则文档时） |
| 类型 | enum |
| 受控词表 | `global`, `domain`, `module`, `session` |
| 默认值 | `domain` |
| 说明 | 规则的作用范围，决定变更通知范围 |
| 归属标准 | PS-STD-004 |

### 15.2 `stability` 字段

| 属性 | 值 |
|------|-----|
| 字段名 | `stability` |
| 域 | A（文档 frontmatter） |
| 必填 | 是（新增规则文档时） |
| 类型 | enum |
| 受控词表 | `frozen`, `stable`, `evolving` |
| 默认值 | `stable` |
| 说明 | 规则的变更稳定性，决定变更审批门槛 |
| 归属标准 | PS-STD-004 |
| 一致性约束 | `frozen` ↔ `immutable_core`（单向强制）；其余组合无硬性约束，遵循 PS-STD-001 §2.6 架构公民原则 |

---

## 16. 废弃流程

本标准的 `stability` 为 `stable`，废弃流程需：

1. Owner 明确批准
2. 创建 ADR 记录废弃原因和替代方案
3. 从 PS-STD-001 中移除 `scope`、`stability` 字段定义
4. 所有规则文档移除 `scope`、`stability` 字段
5. 本标准状态改为 `deprecated`，保留 90 天后可删除

---

## 17. 审查周期

| 审查项 | 周期 | 负责人 |
|--------|------|--------|
| 领域受控词表是否需要扩展 | 每 90 天 | Owner |
| Scope 受控词表是否足够 | 每 180 天 | Owner |
| Stability 与 ai_autonomy 一致性 | 每 90 天 | Owner |
| 规则画像是否与实际一致 | 每 30 天 | 领域负责人 |
| 推导链是否覆盖所有实际冲突场景 | 每 90 天 | Owner |

---

## 18. 修改条件

| 修改类型 | 审批要求 | 同步要求 |
|---------|---------|---------|
| 新增领域受控词表条目 | Owner 批准 | 同步 PS-STD-001 路径映射 + 创建目录 |
| 新增 Scope/Stability 值 | Owner 批准 + ADR | 同步 PS-STD-001 + frontmatter-schema.json |
| 修改规则画像 | 领域负责人批准 | 同步 document-metadata-index.yaml |
| 修改维度定义 | Owner 批准 + ADR | 同步所有 Tier 1 消费者 |
| 修改推导链步骤 | Owner 批准 + ADR | 同步 PS-STD-009（变更门控依赖推导链） |

---

## 19. 与 PS-STD-001 字段不重复声明

本标准新增的 `scope` 和 `stability` 字段已在 §15 中向 PS-STD-001 注册。
字段定义权归属 PS-STD-001，本标准仅定义受控词表和分类规则。
`layer` 和 `ai_autonomy` 字段完全由 PS-STD-001 定义，本标准引用。

---

## 20. 可验证性标注

| 条目 | 可验证性 | 验证方式 |
|------|:-------:|---------|
| 领域受控词表合规 | A | check_frontmatter_metadata.py 校验 |
| Layer 与 doc_type 一致性 | A | check_frontmatter_metadata.py 校验 |
| Scope 受控词表合规 | A | check_frontmatter_metadata.py 校验 |
| Stability 受控词表合规 | A | check_frontmatter_metadata.py 校验 |
| Stability 与 ai_autonomy 一致性 | A | check_frontmatter_metadata.py 校验 |
| 规则画像与实际一致 | M | 人工审查 |
| 推导链一致性（stability→layer→scope→Owner） | A | check_frontmatter_metadata.py 校验 |

---

## 21. 完整性自检清单

- [x] §1 目的与范围：目的 + 责任范围 + 责任边界 + 适用范围 + 术语
- [x] §2 五维分类体系总览 + Vibe Coding 检索策略
- [x] §3 领域维度：受控词表 + 分类规则 + 新增流程
- [x] §4 层级维度：受控词表 + 分类规则
- [x] §5 作用范围维度：受控词表 + 分类规则 + 新字段定义
- [x] §6 稳定性维度：受控词表 + 分类规则 + 新字段定义
- [x] §7 执行者维度：受控词表 + 分类规则
- [x] §8 规则画像示例：所有现有文件的五维分类
- [x] §9 冲突裁决推导链
- [x] §10 推导示例
- [x] §11 禁止行为
- [x] §12 SSoT 声明
- [x] §13 消费者注册表
- [x] §14 标准间引用规范
- [x] §15 新字段注册声明
- [x] §16 废弃流程
- [x] §17 审查周期
- [x] §18 修改条件
- [x] §19 字段不重复声明
- [x] §20 可验证性标注
- [x] §21 完整性自检清单

---

## 22. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 2.0.2 | 2026-05-01 | 交叉引用同步——PS-STD-002 v3.1.0 引入标准子类型，§4.1 layer 画像表中 L1/cross_layer 的章节数从"19 章"改为"6~15 章（按子类型，见 PS-STD-002 §3.2）"。版本号 patch +1。 |
| 2.0.1 | 2026-05-01 | 编辑性变更——frontmatter 字段排序对齐 PS-STD-001 §2.3（date 移至 created_by 之后，ai_autonomy 移至 verifiability 之后）。版本号 patch +1。 |
| 2.0.0 | 2026-05-01 | **合并 PS-STD-008**。原 PS-STD-008（rule-priority-hierarchy.md）的冲突裁决推导链（§1-§5）内容整合为本标准 §9-§11（推导链 + 示例 + 禁止行为）。更新 §1.3 术语（新增强推导链/终极仲裁）、§8.1 画像表（删除 PS-STD-008 行，新增 PS-STD-012 行）、§13 消费者注册表（新增 PS-STD-009 消费推导链）、§14 Normative 引用（新增 PS-STD-011 MTH-003）、§17 审查周期（新增推导链审查项）、§18 修改条件（新增推导链修改条件）、§20 可验证性（新增推导链一致性校验）。精简 title（"规则分类标准"→"规则分类与冲突裁决标准"）。原 PS-STD-008 编号释放回编号池。 |
| 1.2.0 | 2026-05-01 | Vibe Coding 社区对标补遗。新增 §2.2 Vibe Coding AI 检索策略映射——五维分类从"定义分类"到"AI 怎么用"的检索路径：五类查询意图→检索策略映射表（domain→stability→SSoT 路径）+ 四条检索原则（SSoT优先/稳定性过滤/层级收敛/领域隔离）。 |
| 1.1.0 | 2026-05-01 | B6 审查修复。(1) frontmatter 补 `date` 字段。(2) 全文 `stability: immutable` → `frozen`（13 处）。(3) 全文 `ai_editable` → `ai_modifiable`（2 处）。(4) §6.3 约束从全硬绑定改为单向。(5) PS-STD-004 自身定位从 `frozen+immutable_core` 改为 `stable+human_gated`。(6) §8 画像表清废：删除 4 个已废弃/已迁移文件。(7) PS-STD-008/009 `layer` 从 `L1` 改为 `cross_layer`。 |
| 1.0.0 | 2026-04-29 | 初始版本。定义五维分类体系（Domain/Layer/Scope/Stability/Executor），引入 `scope`、`stability` 两个新 frontmatter 字段，完成所有现有文件的规则画像。 |
