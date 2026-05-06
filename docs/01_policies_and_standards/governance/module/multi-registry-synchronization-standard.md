---
module_id: GOV-MOD-007
title: 多登记表同步标准
doc_type: standard
status: active
version: "2.1.1"
layer: L01
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-06"
valid_from: "2026-05-02"
ttl: permanent
summary: "定义所有项目操作（创建规则/模块/脚本/ADR/文档/目录/门禁/知识条目等）后必须同步更新的登记表清单和同步顺序。`catalogs/` 内自动收录数以 `registry-master-index.yaml` 的 `total_registries` 为准（勿写死常量）；MRS-001 矩阵仍按 15 类登记目标描述「写到哪里」。v2.1.1：更正历史文案中误用的「24 张」常数。对标 ITIL SACM + AGENTS.md §6.2。"
tags: [module, governance, registry, synchronization, multi-registry, ssot, artifact-lifecycle]
rule_form: declarative
scope: global
stability: evolving
verifiability: manual
depends_on:
  - {target: PS-STD-001, at: "§2", why: "frontmatter 字段合法性——本文档所有 frontmatter 字段格式遵循其约束"}
  - {target: PS-REG-002, at: "cross_registry_rules", why: "`registry-of-registries.yaml` 中的 CR 规则（跨表共享字段与 SSoT 归属）——本标准是其在登记表同步操作上的落地规范"}
  - {target: PS-REG-005, at: "§2", why: "登记表总索引——`total_registries` 动态收录；本标准 MRS-001 覆盖全部可登记目标分类"}
  - {target: GOV-MOD-001, at: "§8", why: "准入记录写入——创建模块时 MRS-001 引用其准入记录模板"}
  - {target: GOV-MOD-003, at: "§3", why: "status 受控枚举——module-registry.yaml 的 blueprint.status 值来源于此"}
ai_autonomy: ai_modifiable
---

# 多登记表同步标准

> module_id: GOV-MOD-007 | version: 2.1.1 | status: active | layer: L1

---

## 1. 目的与范围

### 1.1 目的

**`docs/01_policies_and_standards/_registry/catalogs/*.yaml` 的自动收录清单**以 [registry-master-index.yaml](../../_registry/catalogs/registry-master-index.yaml) 的 **`total_registries`** 为唯一真源（**勿手写常数**；以 `generate_registry_master_index.py` 最近一次输出为准）。下表描述 **MRS-001 登记目标分类**（15 类工件域；含域外路径如 `03_modules/*.yaml`），**不得**与 `total_registries` 混为一谈。

| 分类 | 登记表数 | 示例 |
|------|:---:|------|
| governance_rule | 2 | document-metadata-index.yaml |
| document | 1 | document-metadata-index.yaml（原 master-document-inventory.yaml 已废弃） |
| module | 4 | module-registry.yaml, blueprint-registry.yaml, module-id-registry.yaml, task-card-meta-registry.yaml |
| ai_asset | 4 | ai-autonomy-authority-registry.md, embedding_model_registry.yaml |
| risk | 1 | ai-risk-register.yaml |
| infrastructure | 1 | infrastructure-registry.yaml |
| dependency | 1 | cross-module-dependency-registry.yaml |
| operational | 1 | script-health-registry.yaml |
| knowledge | 1 | knowledge-article-registry.yaml |
| vocabulary | 3 | doc_type / rule_form / status 受控词表 |
| contract | 1 | architecture-contract.yaml |
| field_definition | 1 | frontmatter-field-registry.yaml |
| physical_structure | 1 | directory-registry.yaml |
| quality_gate | 1 | gate-registry.yaml |
| architecture_decision | 1 | adr-status-registry.yaml（冻结壳；ADR 物理树已废弃，决策见 KB/rationale） |

修改任何一个登记表的共享字段而不同步其他相关登记表，会导致数据不一致——这正是 4 轮审计抓住 25 个问题的共同根因（最初发生在模块登记表，但根本原因适用于所有分类）。

本标准定义：**创建/修改任何项目工件（artifact）后，必须同步更新哪些登记表、更新顺序、校验方式**。

### 1.2 责任范围（本标准管什么）

- **创建操作**：创建规则/模块/脚本/ADR/文档/目录/门禁/知识条目等工件后，必须写入哪些登记表
- **修改操作**：修改跨表共享字段后，必须同步哪些登记表
- 同步的原子性要求（所有关联更新在同一批次操作中完成）
- 同步后的校验步骤
- 违反同步规则的后果和补救流程

### 1.3 责任边界（本标准不管什么）

- 各登记表字段的具体定义 → 以各登记表自身的 `_schema` 为准
- 跨表共享字段的 SSoT 归属 → 以 [registry-of-registries.yaml](../../_registry/catalogs/registry-of-registries.yaml) `cross_registry_rules` 为准
- 登记表存量清单 → 以 [registry-master-index.yaml](../../_registry/catalogs/registry-master-index.yaml) 为准
- AI 操作工具的具体调用方式 → 以 AGENTS.md 为准
- 各类工件的准入审批 → 以对应的准入标准为准（模块=GOV-MOD-001，规则=PS-STD-004，ADR=ADR 治理流程）
- 登记表本身的物理迁移（如 module-registry.yaml → _registry/catalogs/）→ 以 registry-master-index.yaml migration_plan 为准

### 1.4 适用范围

- 项目 `` 下所有在 registry-master-index.yaml 中登记的登记表
- 后续新增的任何登记表在写入 registry-master-index.yaml 时即受本标准管辖
- 本标准**不适用于**：`_DO_NOT_USE_old_tree/` 下的任何文件（按 AGENTS.md §2 禁止操作）

---

## 2. SSoT 声明

本文档是 ZephyrAlpha 系统中**跨登记表同步操作规范**的唯一真源（SSoT）。

**本文档定义了**：
- 12 种工件操作 × 13 个登记目标分类的完整同步矩阵（MRS-001）
- 同步原子性约束（MRS-002）
- 同步后校验要求（MRS-003）
- 6 条禁止行为（MRS-004）

**本文档与以下文件互补**（非取代关系）：
- [registry-master-index.yaml](../../_registry/catalogs/registry-master-index.yaml)：列出 `total_registries` 条 catalogs 收录项——本标准是"创建 X 后怎么写"，它是"写到哪张表"
- [registry-of-registries.yaml](../../_registry/catalogs/registry-of-registries.yaml)：共享字段和 SSoT 归属——本标准是"怎么同步"，它是"同步什么共享字段"
- GOV-MOD-001 准入门控：创建模块时的审批流程——本标准是准入通过后登记数据的操作规范
- GOV-MOD-003 生命周期策略：status 枚举值定义——本标准是 status 变更后的同步操作

**若其他文件中出现与本标准冲突的多登记表同步规则，以本文档为准。**

---

## 3. 受控枚举定义

本文档不定义独立的受控枚举。以下枚举值的 SSoT 在其他文件中：
- 共享字段及其 SSoT 归属 → [registry-of-registries.yaml](../../_registry/catalogs/registry-of-registries.yaml) `cross_registry_rules`
- `status` 8 阶段枚举值 → GOV-MOD-003 §3
- `priority` 合法值（P0/P1/P2/P3） → module-registry.yaml `_schema.priority_values`
- `layer` 合法值（L00~L13） → module-registry.yaml `_schema.layer_values`
- `doc_type` 17 种合法值 → REG-VOC-001
- `rule_form` 6 种合法值 → REG-VOC-002

---

## 4. 消费者注册表

以下文件直接依赖本文档——本标准规则变更时必须同步更新：

| 消费者 | 文件 | Tier | 依赖内容 |
|--------|------|:---:|---------|
| check_registry_consistency.py | `scripts/governance/` | 1 | §7 校验步骤——校验脚本的执行流程引用 MRS-003 |
| run_all.py | `scripts/governance/` | 2 | 审计脚本编排——需将 check_registry_consistency.py 纳入 40 步编排 |
| document-metadata-index.yaml | `_registry/catalogs/` | 1 | MRS-001 规则行——创建/修改规则文档时的登记要求 |
| document-metadata-index.yaml（原 master-document-inventory.yaml 已废弃） | `_registry/catalogs/` | 1 | MRS-001 文档行——创建任何文档时必须登记 |
| module-registry.yaml | `03_modules/` | 1 | MRS-001 模块行——模块操作的登记要求 |
| blueprint-registry.yaml | `03_modules/` | 1 | MRS-001 模块行 |
| script-health-registry.yaml | `_registry/catalogs/` | 1 | MRS-001 脚本行 |
| adr-status-registry.yaml（冻结壳） | `_registry/catalogs/` | 1 | MRS-001 ADR 行（占位对账；活跃决策不在此表逐条维护） |
| directory-registry.yaml | `_registry/catalogs/` | 1 | MRS-001 目录行 |
| gate-registry.yaml | `_registry/catalogs/` | 2 | MRS-001 门禁行 |
| knowledge-article-registry.yaml | `_registry/catalogs/` | 2 | MRS-001 知识条目行 |

---

## 5. 主体内容 — 核心操作规则

### 5.1 MRS-001：操作-登记矩阵

**规则**：对项目执行以下操作时，MUST 同步更新矩阵中打 ✅ 的登记表。修改的字段值 MUST 与 SSoT 源一致。

**登记表列缩写对照**：

| 缩写 | 全称 | 路径 |
|------|------|------|
| GOV-RULES | document-metadata-index.yaml | `_registry/catalogs/` |
| DOC-INV | document-metadata-index.yaml（原 master-document-inventory.yaml 已废弃） | `_registry/catalogs/` |
| MOD-ID | module-id-registry.yaml | `02_enterprise_architecture/.../architecture-model/` |
| MODULE | module-registry.yaml | `03_modules/` |
| BPR | blueprint-registry.yaml | `03_modules/` |
| TASK-META | task-card-meta-registry.yaml | `_registry/catalogs/` |
| SCRIPT | script-health-registry.yaml | `_registry/catalogs/` |
| ADR | adr-status-registry.yaml（冻结壳） | `_registry/catalogs/` |
| KMS | knowledge-article-registry.yaml | `_registry/catalogs/` |
| DIR | directory-registry.yaml | `_registry/catalogs/` |
| GATE | gate-registry.yaml | `_registry/catalogs/` |
| FIELD | frontmatter-field-registry.yaml | `_registry/catalogs/` |
| AI-AUTH | ai-autonomy-authority-registry.md | `governance/ai/` |
| INFRA | infrastructure-registry.yaml | `_registry/catalogs/` |

**操作 × 登记表矩阵**：

| 操作 | GOV-RULES | DOC-INV | MOD-ID | MODULE | BPR | TASK-META | SCRIPT | ADR | KMS | DIR | GATE | FIELD | AI-AUTH | 其它 |
|------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|------|
| **创建治理规则** | ✅ | ✅ | ✅ | — | — | — | — | — | — | — | — | — | — | 目录 index.md |
| **创建模块** | — | ✅ | ✅ | ✅ | ✅ | — | — | — | — | ✅ | — | — | ✅ | 上级层 index.md |
| **创建脚本** | — | ✅ | — | — | — | — | ✅ | — | — | — | — | — | — | — |
| **创建 ADR** | — | ✅ | — | — | — | — | — | ✅ | — | — | — | — | — | — |
| **创建知识条目** | — | ✅ | — | — | — | — | — | — | ✅ | — | — | — | — | — |
| **创建新目录** | — | ✅ | — | — | — | — | — | — | — | ✅ | — | — | — | index.md |
| **创建门禁** | — | ✅ | — | — | — | — | — | — | — | — | ✅ | — | — | — |
| **创建任务卡系统** | — | ✅ | — | — | — | ✅ | — | — | — | — | — | — | — | — |
| **新增 frontmatter 字段** | — | — | — | — | — | — | — | — | — | — | — | ✅ | — | PS-STD-001 |
| **修改共享字段** | — | — | — | ✅ | ✅ | — | — | — | — | — | — | — | — | 物理蓝图.md |
| **模块改 version** | — | — | — | ✅ | ✅ | — | — | — | — | — | — | — | — | 物理蓝图.md |
| **模块改 status** | — | — | — | ✅ | ✅ | — | — | — | — | — | — | — | — | 物理蓝图.md |
| **模块归档/退役** | — | — | — | ✅ | ✅ | — | — | — | — | — | — | — | — | delivery/index.md |
| **创建基础设施组件** | — | ✅ | — | — | — | — | — | — | — | ✅ | — | — | — | INFRA |

> **不用同步的登记表分类**：vocabulary（受控词表——只定义枚举，不登记具体工件）、contract（验证契约——只定义验证规则）、dependency（模块间依赖——从 MODULE 字段推导，见 CR-004 注）、risk（风险登记——特殊用途，按 OPS-VC 风险流程登记，不在本标准自动同步范围）

### 5.2 创建各类型工件的通用步骤模板

无论创建什么类型的工件，遵循统一步骤：

1. **查 MRS-001 矩阵**：确定哪些登记表有 ✅
2. **创建物理文件**：写入实际内容 + 符合 PS-STD-001 的 frontmatter
3. **写入所有打 ✅ 的登记表**：在同一批操作中完成
4. **更新关联目录 index.md**：如果操作矩阵"其它"列标注
5. **运行相关校验脚本**：（见 MRS-003）

### 5.3 创建模块时的完整步骤（最复杂场景）

模块是横跨最多登记表的工作类型，作为参考模板：

1. **分配 module_id**：查 MOD-ID 登记表，取最后一个 ID 递增
2. **创建物理目录和文件**：`{layer_dir}/{module_name}/` + `index.md` + `blueprint.md` + `delivery/index.md`
3. **登记 MODULE**（module-registry.yaml）：新增 `modules[]` 条目
4. **登记 BPR**（blueprint-registry.yaml）：新增 `blueprints[]` 条目
5. **登记 DOC-INV**：新增文档条目
6. **登记 MOD-ID**：注册新 id
7. **登记 DIR**：注册新目录
8. **登记 AI-AUTH**：声明 AI 自治权限
9. **更新上级层 index.md**：添加模块行
10. **运行校验**：`check_registry_consistency.py` + `check_frontmatter_metadata.py`

### 5.4 MRS-002：同步原子性

**规则**：所有关联登记表的修改 MUST 在同一批次操作中完成。

- 禁止先改 A 再改 B（分开两个操作）。必须一个 SearchReplace/Write 批次覆盖所有目标文件
- 如果某个关联文件当前不在编辑上下文内，MUST 先 Read 该文件再加入同批次修改
- 原子性对标 AGENTS.md §6.2

**大白话**：创建规则文档时，document-metadata-index.yaml + module-id-registry.yaml 两个登记表必须一起更新（原 master-document-inventory.yaml 已废弃被 document-metadata-index.yaml 取代），不能今天写一个明天补一个。现在知道为什么 4 轮审计抓住了 25 个问题了——每次都是"做完主要事情就想不起来同步了"。

### 5.5 MRS-003：同步后校验

**规则**：任何触及 MRS-001 矩阵中 ✅ 标记的修改完成后，MUST 立即运行相关校验：

| 校验 | 覆盖 | 何时运行 |
|------|------|---------|
| `check_registry_consistency.py` | 跨登记表共享字段一致性（CR-001~006） | 任何触及 module-registry.yaml / blueprint-registry.yaml / 物理 blueprint.md 的操作后 |
| `check_frontmatter_metadata.py` | frontmatter 字段合法性 | 创建任何文档后 |
| `check_architecture_gates.py` | ADR/模块/架构一致性 | 创建/修改 ADR 或模块后 |
| `validate_directory_registry.py` | 物理目录 vs 登记表漂移 | 创建新目录后 |

- 如果校验脚本不可用（如 Python 环境问题），MUST 手动逐条对照 SSoT 定义验证
- 任何 FAIL 必须在 commit 前修复

---

## 6. 禁止行为

### MRS-004：禁止行为清单

以下行为被**明确禁止**，违反即视为同步违规：

| # | 禁止行为 | 示例 | 后果 |
|---|---------|------|------|
| 1 | **创建工件不登记**——创建了新文档/脚本/规则/ADR，但没有写入对应的登记表 | 创建了 GOV-MOD-007 但未写入 document-metadata-index.yaml | 新 AI session 遍历登记表时该工件不可见——违反 Zero-Memory Restart 标准 |
| 2 | **只改物理文件不该登记表**——改了 frontmatter 的共享字段，但未同步任何登记表 | 改了 blueprint.md 的 version，module-registry.yaml 和 BPR 仍是旧值 | CR-001 FAIL |
| 3 | **只改登记表不改物理文件**——改了登记表的共享字段，物理 frontmatter 不同步 | 改了 module-registry 的 status，blueprint.md frontmatter 未改 | 物理文件与登记表背离——物理文件是 SSoT，登记偏差会永久化 |
| 4 | **改了 A 登记表不改 B 登记表**——两个登记表有同一个共享字段，只动了一个 | 改了 module-registry 的 version，BPR 还是旧值 | CR-001 FAIL——AI 读到矛盾版本 |
| 5 | **SearchReplace 模板不唯一导致误匹配**——多条记录共享相同字段值，替换命中错了目标 | v1.0.0+AI-GLM-5.1 同时出现在 MOD-INF-001 和 MOD-INF-003——本标准的 root cause | SearchReplace 只替换第一个匹配——需要差异化或使用更唯一的上下文 |
| 6 | **创建登记表本身但不登记到 registry-master-index.yaml**——新增了一张 YAML 登记表，但主索引不知道 | 创建了 deploy-registry.yaml，未写在 registry-master-index | MRS-001 矩阵缺失该表——违反 §1.4"新增即受管辖" |

---

## 7. 变更同步规则

本标准 `stability: evolving`——操作矩阵和禁止行为会随 Phase 变化：

| 变更类型 | 影响范围 | 同步动作 | 时机 |
|---------|---------|---------|------|
| 新增登记表（写入 registry-master-index.yaml） | MRS-001 矩阵新增列 | 扩展矩阵列 + 新增对应操作行 | 同 commit |
| 新增工件类型（如 deploy-artifact） | MRS-001 矩阵新增行 | 新增操作行 + 更新 §15 AI 清单 | 同 commit |
| 修改 MRS-001 操作映射 | Tier 1 消费者 | 更新 check_registry_consistency.py 的字段匹配逻辑 | 同 commit |
| 新增禁止行为 | MRS-004 编号递增 | 更新消费者引用 | 同 commit |
| frontmatter 仅变更（summary/tags） | 无 | 不需同步 | — |

---

## 8. 修改条件

本标准 `ai_autonomy: ai_modifiable`——AI 可自主修改，但受以下分级约束：

| 级别 | 变更范围 | 审批方 | 要求 |
|:---:|---------|--------|------|
| L0 | 错别字、措辞优化、格式调整 | AI 自批 | Session Log 记录 |
| L1 | MRS-001 矩阵中新增/删除操作行 | AI 可建议，Owner 确认 | 需对照 registry-master-index.yaml 验证新增登记表已注册 |
| L2 | 修改 MRS-002~005 规则本体 | Owner 审批 | 涉及操作纪律——需 Owner 确认新规则可落地 |
| L3 | 新增登记表到 MRS-001 矩阵 / 新增工件类型 | Owner 审批 | 必须同时更新 registry-master-index.yaml + registry-of-registries.yaml |

---

## 9. 标准间引用规范

### 9.1 规范性引用（Normative）

| 引用文件 | 节 | 角色 |
|---------|---|------|
| AGENTS.md | §6.2 | 原子事务模式——所有同步操作必须在一批次中完成 |
| registry-of-registries.yaml | cross_registry_rules | 共享字段定义和 SSoT 归属——本标准是 CR 规则的施工操作落地方案 |
| registry-master-index.yaml | §2 | 登记表存量清单——MRS-001 矩阵列据此生成 |
| PS-STD-001 | §2 | frontmatter 字段合法性——本文件所有 frontmatter 格式遵循其约束 |

### 9.2 信息性引用（Informative）

| 引用文件 | 节 | 角色 |
|---------|---|------|
| GOV-MOD-001 | 全文 | 模块准入门控——创建模块的前置审批流程 |
| GOV-MOD-003 | §3 | status 枚举值——module-registry.yaml 的 blueprint.status 值来源 |
| check_registry_consistency.py | 全文 | 校验脚本——MRS-003 的执行目标 |
| PS-STD-004 | 全文 | 规则分类标准——创建治理规则的前置分类要求 |

---

## 10. 废弃流程

若本标准被更高层级的治理文件取代：

1. **搜索影响**：全项目搜索 `MRS-001|MRS-002|MRS-003|MRS-004`——确认所有引用都有迁移路径
2. **通知期**：30 天提前通知全部消费者（Session Log + ADR）
3. **废弃标记**：`status: deprecated`，`superseded_by` 指向替代文件
4. **过渡期**：至少 90 天保留本文件，期间消费者完成迁移
5. **延期**：90 天到期后有引用未迁移 → Owner 可批准延期（最长再延 90 天）——必须 Session Log 记录原因
6. **归档**：过渡期满、全部引用已迁移 → `status: archived`

---

## 11. 审查周期

对标 ISO 11179 §6.2 定期审查要求：

| 触发条件 | 审查内容 |
|---------|---------|
| 新增登记表（registry-master-index.yaml 增加条目） | MRS-001 矩阵是否需要新增列 |
| 新增工件类型（项目中出现新的可创建实体） | MRS-001 矩阵是否需要新增行 |
| Phase 边界（scaffold→1, 1→2...） | 操作矩阵是否仍覆盖当前操作类型 |
| check_registry_consistency.py 重大修改 | MRS-003 校验步骤描述是否准确 |
| 最低频率：每 6 个月 | 全量审查 |

---

## 12. 异常豁免机制

**默认**：MRS-001~004 对所有工件操作同等约束。

**例外通道**：

| 豁免场景 | 豁免内容 | 约束 |
|---------|---------|------|
| scaffold 原型快速迭代 | 临时跳过 MRS-003 校验步骤 | Owner 审批，仅限 scaffold，每次豁免不超过 3 天 |
| 登记表结构重构 | 允许登记表暂时不一致 | Session Log 记录不一致清单 + 修复时限（不超过 48h） |
| 纯内部文件（不上线的草稿） | 仅需 DOC-INV，可跳过规则登记 | 在 DOC-INV 备注字段标注 `internal_draft` |

---

## 13. 与 PS-STD-001 的字段不重复声明

本标准不定义新的 frontmatter 字段。所有 frontmatter 字段定义以 PS-STD-001 为准。

---

## 14. 跨标准字段交叉引用

本标准不定义跨标准共享字段。共享字段的 SSoT 归属以 registry-of-registries.yaml `cross_registry_rules[].ssoT` 为准。

---

## 15. AI 可消费性声明

> 对标 Anthropic CLAUDE.md——直接向 AI 说明如何解析和执行本文档。

### 15.1 AI 可直接执行的规则

- **MRS-001 操作矩阵**：12 行 × 14 列的真值表——查表确定创建 X 后必须写哪些登记表
- **MRS-002 原子性**：所有 ✅ 目标必须在同一批 SearchReplace/Write 中完成
- **MRS-003 校验**：修改完成后自动执行对应的校验脚本
- **MRS-004 禁止行为**：#1~#6 每条有触发条件和后果

### 15.2 需人类判断的规则

- 新登记表的引入（L3 级修改，需 Owner 审批）
- 豁免场景的审批（需 Owner 确认）

### 15.3 最小必读路径（全新 AI session）

1. §1.1 → 知道有 15 个分类的登记表系统
2. §5.1 MRS-001 矩阵 → 查表：创建 X → 必须写 Y、Z
3. §5.4 MRS-002 原子性 → 所有 ✅ 在同批完成
4. §5.5 MRS-003 校验 → 改完运行校验
5. §6 MRS-004 → 知道 6 种常见犯错模式

### 15.4 Token 预算

| 项目 | 值 |
|------|---|
| 全文 Token | ~3000 |
| 精简路径（目的 + 矩阵 + 校验 + 禁止行为） | ~1200 |

### 15.5 AI 执行清单

当 AI 完成任何创建/修改操作时：

- [ ] 确定工件类型（规则/模块/脚本/ADR/文档/目录/门禁/知识/字段…）
- [ ] 查 §5.1 MRS-001 矩阵 → 找出所有 ✅ 的登记表列
- [ ] 同一批操作覆盖所有 ✅ 目标
- [ ] 运行 MRS-003 指定的校验脚本
- [ ] 确认所有校验 PASS
- [ ] Session Log 记录同步操作

---

## 16. 完整性自检清单

- [ ] §1.1 目的：`total_registries` 与 MRS-001 15 类登记目标的口径已区分（勿写死张数）
- [ ] §2 SSoT 声明：互补关系覆盖 registry-master-index.yaml + registry-of-registries.yaml + GOV-MOD-001/003
- [ ] §5.1 MRS-001：操作矩阵覆盖 12 种操作 × 14 个登记目标，标注排除的分类
- [ ] §5.3 创建模块步骤：10 步完整流程（最复杂场景）
- [ ] §6 MRS-004：6 条禁止行为（新增 #5 SearchReplace 误匹配、#6 新登记表未注册）
- [ ] §15 AI 可消费性声明：最小路径 + Token + 执行清单

---

## 17. 变更记录

| 日期 | 版本 | 变更说明 |
|------|------|---------|
| 2026-05-06 | 2.1.1 | 对齐 `registry-master-index.yaml`：移除误用的「24 张」常数，改为 `total_registries` 真源 + MRS-001 分类说明；自检清单同步。 |
| 2026-05-02 | 2.0.0 | **重大扩展**：MRS-001 操作矩阵从 3 列（仅模块登记表）扩展到 14 列（覆盖 registry-master-index.yaml 的下全部可登记分类）。新增 8 种操作类型（创建规则/脚本/ADR/知识/目录/门禁/任务卡/字段）。MRS-004 禁止行为从 4 条扩展到 6 条（新增 SearchReplace 误匹配 + 新登记表不注册）。depends_on 新增 registry-master-index.yaml。Token 预算更新（2000→3000）。 |
| 2026-05-02 | 1.0.0 | 初始版本——定义 MRS-001~004 四条核心规则，仅覆盖模块登记表（module-registry.yaml + blueprint-registry.yaml + 物理 blueprint.md） |
