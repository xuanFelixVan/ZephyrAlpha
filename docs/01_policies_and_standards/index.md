---
module_id: PS-IDX-001
title: 规则体系总索引
doc_type: index
status: active
version: "1.4.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-04"
ttl: permanent
summary: "01_policies_and_standards/ 的顶层导航入口。列出全部 6 个子目录的结构、职责和关键文件。所有目录项和文件项均附带中文说明。新 AI session 的第一站——读完此文件即理解整个规则体系的全貌。"
tags: [index, root, navigation, policies-and-standards]
rule_form: declarative
scope: global
stability: stable
verifiability: manual
---

# 规则体系总索引

> **module_id**: PS-IDX-001 | **version**: 1.4.0 | **status**: active

本文件是 `01_policies_and_standards/` 的顶层导航入口。**新 AI session 的第一站**——读完此文件即理解整个规则体系的全貌，无需遍历 6 个子目录。

> **对标**：ISO/IEC Directives Part 2 要求标准目录提供索引文件。meta/index.md 定义了 index 文件的六模块模板。AGENTS.md §5.1 零记忆重启标准：AI 每次都是"新员工"，必须有一个文件让它 3 分钟内理解目录结构。

---

## 一、目录结构速览

```
01_policies_and_standards/
├── meta/                        ← 元规则（关于规则体系的规则）
│   ├── index.md                 ← 元规则索引入口（新 AI 优先读）
│   ├── meta-standard-constitution.md      ← 最高层级元宪法
│   ├── metadata-registry.md               ← frontmatter 字段规范真源（字段数据真源见 frontmatter-field-registry.yaml）
│   ├── document-structure-standard.md     ← 标准文档模板
│   ├── behavior-boundaries-standard.md    ← 行为边界（绝对禁止/条件禁止）
│   ├── rule-classification-and-arbitration-standard.md ← 规则分类与冲突仲裁
│   ├── governance-metrics-standard.md     ← 治理度量 KPI
│   ├── rule-lifecycle-and-change-standard.md ← 规则生命周期+变更门控
│   ├── governance-methodology-standard.md ← 治理方法论 MTH-001~010
│   ├── rule-verification-standard.md      ← 规则验证分级体系
│   ├── glossary.md                        ← 术语表（仲裁源）
│   ├── terminology-mapping.md             ← 术语大白话双向映射表
│   └── blueprint-architecture-standard.md ← 蓝图架构标准
│
├── governance/                  ← 声明式全局规则（"应该是什么"）
│   ├── ai/                      ← AI 治理（自主权、幻觉自检、onboarding）
│   ├── architecture/            ← 架构治理（评审门、版本策略、ADR 协议）
│   ├── compliance/              ← 合规治理（审计追踪、监管分类）
│   ├── data/                    ← 数据治理（血缘、质量、留存）
│   ├── document/                ← 文档治理（命名、路径、目录结构、生命周期）
│   ├── module/                  ← 模块治理（准入、注入规则、接口契约）
│   ├── security/                ← 安全治理（访问控制、密钥管理、应急）
│   └── task/                    ← 任务治理（卡片标准、生命周期、handoff）
│
├── operational/                 ← 过程式操作手册（"怎么做"）
│   ├── devops/                  ← DevOps 操作（pre-commit、CI、架构变更 playbook）
│   ├── migration/               ← 迁移操作（老树→当前项目审计）
│   └── vibe_coding/             ← Vibe Coding 操作（上下文规则、状态机、应急手册）
│
├── domains/                     ← 层/域特定规则
│   ├── L00_data_source/         ← L00 数据源层
│   │   ├── governance/          ← 声明式规则
│   │   └── operational/         ← 过程式手册
│   ├── L02_alpha_factor/        ← L02 Alpha 因子层
│   │   ├── governance/          ← 声明式规则
│   │   └── operational/         ← 过程式手册
│   ├── L04_risk_management/     ← L04 风险管理层
│   │   ├── governance/          ← 声明式规则
│   │   └── operational/         ← 过程式手册
│   └── L07_post_trade_analytics/ ← L07 盘后分析层
│       ├── governance/          ← 声明式规则
│       └── operational/         ← 过程式手册
│
├── _registry/                   ← 注册表 + 验证契约（机器可读）
│   ├── catalogs/                ← 集中注册表（20 个 YAML/MD——详见 catalogs/index.md）
│   │   ├── registry-master-index.yaml            ← 登记表总索引
│   │   ├── document-metadata-index.yaml         ← 文件元数据索引（auto-generated）
│   │   ├── frontmatter-field-registry.yaml       ← frontmatter 字段数据 SSoT（字段规范见 metadata-registry.md）
│   │   └── ...（其余 16 个 catalog 文件见 catalogs/index.md）
│   ├── contracts/               ← 架构合规契约
│   │   └── architecture-contract.yaml             ← 架构合规自动验证契约
│   ├── schemas/                 ← JSON Schema 定义
│   │   └── frontmatter-schema.json                ← frontmatter 字段校验 Schema
│   └── vocabularies/            ← 受控词表（11 个——详见 vocabularies/index.md）
│       ├── doc_type-vocabulary.yaml               ← 文档类型受控枚举（27 值）
│       ├── rule_form-vocabulary.yaml              ← 规则形式受控枚举
│       ├── status-vocabulary.yaml                 ← 文档状态受控枚举
│       └── ttl-vocabulary.yaml                    ← TTL 周期受控枚举
│
└── templates/                   ← 文档模板（11 个标准模板）
    ├── adr-template.md           ← 架构决策记录模板
    ├── blueprint-template.md     ← 蓝图 + 施工指引统一模板
    ├── playbook-template.md      ← 操作手册模板
    ├── policy-template.md        ← 策略模板
    ├── protocol-template.md      ← 协议模板
    ├── register-template.md      ← 注册表模板
    ├── risk-register-template.md ← 风险登记表模板
    ├── roadmap-template.md       ← 路线图模板
    ├── runbook-template.md       ← 执行手册模板
    ├── standard-template.md      ← 标准模板
    └── task-card-template.md     ← 任务卡模板
```

---

## 二、各子目录关键信息

<!-- TABLE-AUTO-START -->
| 子目录 | 职责 | 管辖文件数 | 索引入口 | 注册表 |
|--------|------|:---------:|---------|--------|
| `meta/` | 元规则——定义"规则怎么写、怎么管" | 12 | [meta/index.md](meta/index.md) | [_registry/catalogs/rule-registry.md](_registry/catalogs/rule-registry.md) |
| `governance/` | 声明式全局规则——8 个治理域 | 43 | [governance/index.md](governance/index.md) | [document-metadata-index.yaml](_registry/catalogs/document-metadata-index.yaml) |
| `operational/` | 过程式操作手册——3 个操作域 | 4 | [operational/index.md](operational/index.md) | 同上 |
| `domains/` | 层域特定规则——4 个架构层 | 8 | [domains/index.md](domains/index.md) | 同上 |
| `_registry/` | 注册表+契约——4 个子目录 | 35 | [不需要（机器可读）](不需要（机器可读）) | 自身即注册表 |
| `templates/` | 文档模板 | 11 | [不需要（文件名自描述）](不需要（文件名自描述）) | [document-metadata-index.yaml](_registry/catalogs/document-metadata-index.yaml) |

> **合计**：6 个子目录，113 个文件，全部注册在 [document-metadata-index.yaml](_registry/catalogs/document-metadata-index.yaml)（auto-generated，取代旧的 governance-rules-master-registry.yaml 和 master-document-inventory.yaml）。
<!-- TABLE-AUTO-END -->

---

## 三、本目录责任声明

### 3.1 责任范围（本目录管什么）

本目录是 ZephyrAlpha **规则体系**的唯一存放处，负责管理：

| 类别 | 存放位置 | 说明 |
|------|---------|------|
| **元规则** | `meta/` | 关于规则体系的规则——格式、分类、生命周期、方法论 |
| **声明式治理规则** | `governance/` | 全局策略、标准、协议——"应该是什么状态" |
| **过程式操作手册** | `operational/` | 施工步骤、应急流程、上下文规则——"怎么达到那个状态" |
| **层域规则** | `domains/` | 各架构层的专属规则和操作手册 |
| **机器注册表** | `_registry/` | 自动索引、受控词表、验证契约 |
| **文档模板** | `templates/` | 新建文件的起点 |

### 3.2 责任边界（本目录不管什么）

以下类型文件 **不在** 本目录管辖范围内：

| 文件类型 | 不在此目录的原因 | 正确位置 |
|---------|---------------|---------|
| 企业架构视图（TOGAF） | 架构模型不是规则 | `docs/02_enterprise_architecture/` |
| 架构决策记录（ADR，已冻结 2026-04-27） | 架构决策不是规则标准，替代方案见 MOD-KB-001 §3.9.5 三层决策记录模型 | `docs/02_enterprise_architecture/adr/`（归档） |
| 模块生命周期文档 | 蓝图+施工图+交付 | `docs/03_modules/` |
| 知识库条目 | 经验积累不是规则 | `docs/08_knowledge/` |
| 审计报告 | 事后评估不是规则 | `docs/09_audit/` |
| Session Log | 临时会话记录 | 已迁至项目外部独立目录（2026-05-02）。`docs/19_development_workspace/` 目录已删除。 |
| 业务代码 | 可执行代码 | `src/zephyr/` |
| 治理/审计脚本 | 工具不是规则 | `scripts/governance/` / `scripts/audit/` |

### 3.3 `governance/` vs `operational/` 边界判据

这是本目录最重要的架构边界。判据如下：

| 我要放一个文件…… | 对照问题 | 放 governance/ 如果…… | 放 operational/ 如果…… |
|:----------------|:--------|:---------------------|:----------------------|
| | "这个文件描述什么？" | 描述 **期望状态**（声明式） | 描述 **执行步骤**（过程式） |
| | "怎么判断？" | 能用 `policy`/`standard`/`protocol` 做 doc_type | 能用 `operational_rule` 做 doc_type |
| | 对标 | K8s Declarative Config / ITIL Policy | K8s Imperative Command / ITIL Procedure |

**正例（放对了）**：
- `governance/architecture/architecture-review-policy.md` ← 声明式：定义了"什么变更必须评审"（期望状态）
- `operational/vibe_coding/vibe-coding-session-state-runbook.md` ← 过程式：定义了"AI 加载上下文的步骤"（执行步骤）
- `operational/devops/architecture-change-playbook.md`（OPS-DEV-002）← 过程式：定义了"架构变更 L1~L4 四级操作步骤+回滚方案"（执行步骤）。该文件曾错放在 `operational/architecture/`，已于 2026-05-01 审查后迁至 `operational/devops/`——`architecture` 既是 governance 域名又是 operational 路径名违反 AGENTS.md §5.1 原则 2（责任唯一）。

---

## 四、推荐阅读顺序

### 4.1 新 AI session 冷启动（所有任务通用）

```
1. 本文件（index.md）                     ← 3 分钟了解全貌
2. meta/index.md                          ← 元规则全貌
3. meta/glossary.md                       ← 术语对齐
4. meta/rule-classification-and-arbitration-standard.md ← 规则怎么分类
```

### 4.2 按任务类型定向阅读

| 你的任务 | 读完通用 4 步后，继续读 | Token 成本 |
|---------|----------------------|:---:|
| **修改/优化规则文件** | `meta/rule-lifecycle-and-change-standard.md` | ~1500 |
| **创建新标准文档** | `meta/document-structure-standard.md` + `meta/metadata-registry.md` §1~§4 | ~2500 |
| **审查规则体系** | `meta/rule-verification-standard.md` + `_registry/catalogs/rule-registry.md` | ~2000 |
| **操作具体文件夹** | 对应规则文件 | ~1000 |

> 以上路径对齐 AGENTS.md §8.2 三层记忆模型。

---

## 五、关键注册表速查

| 注册表 | 路径 | 用途 |
|--------|------|------|
| **文件注册表** | [_registry/catalogs/document-metadata-index.yaml](_registry/catalogs/document-metadata-index.yaml) | 全部文件的 machine-readable 元数据索引（auto-generated） |
| **文档清单** | [_registry/catalogs/document-metadata-index.yaml](_registry/catalogs/document-metadata-index.yaml) | 全部文档的完整列表（auto-generated，取代已废弃的 master-document-inventory.yaml） |
| **任务卡注册表** | [_registry/catalogs/task-card-meta-registry.yaml](_registry/catalogs/task-card-meta-registry.yaml) | 任务卡元数据定义 |
| **架构契约** | [_registry/contracts/architecture-contract.yaml](_registry/contracts/architecture-contract.yaml) | 架构合规自动验证契约 |
| **doc_type 词表** | [_registry/vocabularies/doc_type-vocabulary.yaml](_registry/vocabularies/doc_type-vocabulary.yaml) | 文档类型受控枚举 |
| **rule_form 词表** | [_registry/vocabularies/rule_form-vocabulary.yaml](_registry/vocabularies/rule_form-vocabulary.yaml) | 规则形式受控枚举 |
| **status 词表** | [_registry/vocabularies/status-vocabulary.yaml](_registry/vocabularies/status-vocabulary.yaml) | 文档状态受控枚举 |

---

## 六、变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 1.4.0 | 2026-05-04 | 审计修复。(1) §一 删除 meta/ 下已迁移文件的注释行（rule-registry.md、registry-of-registries.yaml 已物理删除）。(2) §二 文件数全面更新（非 index 文件口径）：meta/ 11→12、governance/ 38→42、operational/ 4→4、domains/ 8→8、_registry/ 32→35、templates/ 11→11。全局合计 104→112（非 index 文件）。(3) §三.3 断链修复：architecture-review-gate.md → architecture-review-policy.md。(4) §三.1 Session Log 路径：标记为已迁至外部独立目录。(5) 配套修复 15 个文件中的 56 处 `19_development_workspace/` 引用、6 个子索引文件数对账。版本号 minor +1。 |
| 1.2.0 | 2026-05-02 | 审计修复——全量文件数对账。(1) §一 目录树：_registry/catalogs/ 从 3 个文件更新为 10+1，templates/ 从 9 个模板更新为 11 个。(2) §二 文件数：meta/ 12→13、operational/ 9→7、domains/ 12→20、_registry/ 8→20、templates/ 9→12；索引入口 operational/ 和 domains/ 从"（待建）"更新为实际路径。全局合计 96→122。版本号 minor +1。 |
| 1.1.0 | 2026-05-01 | 目录树全中文化 + 索引策略明确。(1) §一 目录结构速览——所有子目录行（governance/ 8 个子域、operational/ 3 个子域、_registry/ 4 个子目录+其下 8 个文件、domains/ L02/L04/L07 下的 governance/operational、templates/ 9 个模板文件）全部补上中文说明。(2) §二 表格——_registry/ 和 templates/ 的"索引入口"从"（待建）"改为"不需要"（原因：机器可读/文件名自描述）。operational/ 和 domains/ 保留"（待建）"（需建但非紧急）。 |
| 1.0.0 | 2026-05-01 | 初始创建。(1) §一 目录结构速览——6 子目录树形图含中文标注。(2) §二 各子目录关键信息——职责、文件数、入口、注册表。(3) §三 责任声明——正向 6 类、负向 8 类、governance/operational 边界判据。(4) §四 推荐阅读顺序——冷启动 4 步 + 按任务定向。(5) §五 关键注册表速查——7 个注册表入口。对标 meta/index.md 六模块模板。 |
