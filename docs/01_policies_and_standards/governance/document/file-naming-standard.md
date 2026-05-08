---
module_id: GOV-DOC-003
title: 文件命名规范
doc_type: standard
status: active
version: 2.5.0
date: "2026-05-06"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
valid_from: "2026-04-25"
ttl: permanent
summary: "ZephyrAlpha 2.0 宪法层命名铁律的唯一真源，所有目录、文件、module_id、编号空间的命名规则均以本文为准。"
tags: [file-naming, governance, naming-convention]
rule_form: declarative
scope: global
stability: stable
verifiability: automated
---

# 文件命名规范 v2.5.0

> **定位**：本文档是 ZephyrAlpha 2.0 **宪法层命名铁律**的唯一真源，所有目录、文件、module_id、编号空间的命名规则均以本文为准。
> **门禁**：Stage G 通过 `GATE-11 命名规范门禁` pre-commit hook 强制校验本文档定义的规则（续号于既有 Architecture-as-Code `GATE-01 ~ GATE-10`）。
> **历史**：
> - v1.0.0 (2026-04-22) 首次建立基础命名规则
> - v2.0.0 (2026-04-25) 经 Stage F 归一化批次升级，纳入扁平编号、module_id 与文件名分离、专业对标等铁律
> - v2.0.1 (2026-04-25) **编号纠偏**：Stage G 开工阶段发现 Stage F 预占的 `GATE-06` 与 `check_architecture_gates.py v2.0.0` 已有的 `GATE-06 事件 publisher 层检查` 冲突；本门禁续号为 `GATE-11`，保留既有 GATE 编号空间 append-only（符合 ADR-0006 跳号治理精神）

---

## §〇 核心原则：名字 = 责任

### 〇.1 目的

**文件和文件夹的命名共享同一核心原则：看见名字就知道它管什么。** 名字是职责的声明，不是装饰性的标签。

| 对象 | 原则 | 自检问题 |
|------|------|---------|
| **文件** | 读到文件名后，一眼就知道该文件定义什么标准/什么流程 | "如果不读内容，只看名字，我能说出这个文件干什么吗？" |
| **文件夹** | 读到文件夹名后，一眼就知道该文件夹管辖什么职责域 | "如果不打开文件夹，只看名字，我能说出什么类型的文件可以放进去吗？" |

**反例警示**：
- `rule-document-format-standard.md` → 读到的是"格式标准"（format），实际管的是"文档结构模板"（structure）——名字偏离责任 → 已修正为 `document-structure-standard.md`
- `rule-change-gate-protocol.md` → 读到的是"变更门禁"+ 后缀 `protocol`（同目录全是 `standard`），实际管的是"生命周期状态机 + 变更审批"——名字不完整 + 后缀不一致 → 已修正为 `rule-lifecycle-and-change-standard.md`

> **大白话**：别让人读完文件名还要琢磨"它到底是干什么的"。名字就是简历——招聘方（AI session）只有 2 秒决定要不要点进去。

### 〇.2 本标准管理以下内容

| # | 内容 | 说明 |
|---|------|------|
| 1 | 通用文件命名规则 | 全小写 kebab-case、禁止大写、禁止空格、`_` 仅允许 3 个场景 |
| 2 | 文件夹命名风格选择规则 | 三种命名风格（单词/snake_case/L{XX}_snake_case）+ 决策树（§一.1） |
| 3 | ADR 特殊命名规则 | 扁平编号 / 跳号 governance / 关联关系靠字段 / append-only（§2.2） |
| 4 | Session Log 命名规则 | 日期+序号格式（§2.1） |
| 5 | KE 文件命名规则 | 小写三位序号（§2.5） |
| 6 | module_id 命名空间定义 | 前缀→目录的映射表（§四） |
| 7 | 违规检测规则 | GATE-11 引擎 7 条规则（§五） |
| 8 | 技术栈专有名词版本白名单 | TECH_VERSION_TOKENS 豁免表（§2.8） |

### 〇.3 本标准**不**覆盖以下内容

| # | 排除项 | 以哪个文件为准 |
|---|--------|-------------|
| 1 | 全系统统一编号体系（module_id 前缀） | unified-numbering-standard.md（GOV-DOC-001） |
| 2 | 文件的强制写入路径 | file-path-standard.md（GOV-DOC-004） |
| 3 | 目录结构的具体定义 | directory-structure-standard.md（GOV-DOC-002） |
| 4 | 文档的生命周期管理 | document-lifecycle-standard.md（GOV-DOC-006） |
| 5 | 文件删除/移动的安全门禁 | file-operation-safety-policy.md（GOV-DOC-007） |
| 6 | 编码安全要求 | encoding-safety-standard.md（GOV-DOC-005） |

### 〇.4 专业对标

详见 §一.1.1（完整 5 家机构对标表）。此处仅列方向性来源：

| 来源 | 方向性对标 |
|------|---------|
| PEP 8 | Python 代码文件命名：`snake_case` |
| K8s 社区 | 文件名全小写 + kebab-case；目录名全小写无连字符（如 `controllers/`、`scheduler/`） |
| Linux FHS | 顶级目录用单词（如 `/etc/`、`/var/`），禁止空格和特殊字符 |
| ISO 文档管理 | 编号 + 语义名称（如 `04.02_quality/`），对应本标准的编号前缀+命名 |
| Go 社区 | 全项目统一一种风格，不可混用——对应本标准的"全小写铁律" |

---

## 一、通用命名规则（适用于所有目录和文件）

| 规则 | 示例（✅ 正确） | 示例（❌ 错误） |
|------|------------|------------|
| 全小写 kebab-case | `rule-classification-and-arbitration-standard.md` | `Rule-Classification-Standard.md` |
| 禁止大写字母（新建文件） | `ai-onboarding-guide.md` | `AI-Onboarding-Guide.md` |
| 禁止版本号后缀 | `module-schema.yaml` | `module-schema-v2.yaml` |
| 禁止 round/iteration 后缀 | `ssot-map.md` | `ssot-map-round2.md` |
| 禁止带日期后缀（LATEST 文件除外） | `scan-LATEST.json` | `scan-20260422.json` |
| 单词间用连字符 `-` | `cross-layer-contracts.yaml` | `cross_layer_contracts.yaml` |

**下划线 `_` 的唯一合法用法**：

1. **Python 源文件** `snake_case.py`（遵循 PEP 8）
2. **YAML 内部字段名** `module_id: value`（非文件名）
3. **模板文件前缀** `_template.md`（表示"非编号项"）

**其他位置一律禁止下划线。**

### 一.0 文件名后缀必须匹配 doc_type（v2.4.0 新增）

> **对标**：K8s well-known labels（label=value 强制匹配）+ OpenAPI discriminator（discriminator 字段决定 schema 类型，不允许模糊）。

在 `01_policies_and_standards/` 目录下，**文件名后缀必须反映 doc_type**。不允许文件名使用与 doc_type 矛盾的后缀——做到"看名字就知道这个文件是什么类型的规则"。

**doc_type → 文件名后缀强制映射表**：

| doc_type | 文件名格式 | 示例 | 说明 |
|----------|-----------|------|------|
| `policy` | `{subject}-policy.md` | `secret-management-policy.md` | 声明式"必须/禁止"规则 |
| `standard` | `{subject}-standard.md` | `file-naming-standard.md` | 技术标准/度量规范 |
| `protocol` | `{subject}-protocol.md` | `architecture-review-policy.md` | 多方交互规则 |
| `operational_rule` | `{subject}-runbook.md` / `-playbook.md` / `-procedure.md` / `-checklist.md` | `architecture-change-playbook.md` | 过程式操作步骤——以上四个后缀均可，均属操作范畴 |
| `register` | `{subject}-registry.md` / `-register.md` | `rule-registry.md` | 结构化数据清单 |
| `index` | `index.md`（固定） | `index.md` | 目录导航入口，不可改名 |
| `terminology` | 术语特定命名 | `glossary.md`、`terminology-mapping.md` | 术语定义文件 |
| `template` | `{target_doc_type}-template.md` | `policy-template.md`、`blueprint-template.md` | templates/ 下模板文件，doc_type 取目标类型 |

**禁止的行为**：

| 禁止 | 例子（违规 → 合规） | 原因 |
|------|------|------|
| 声明式规则用过程式后缀 | `governance-runbook.md` → `governance-protocol.md` | protocol 不能叫 runbook |
| 策略文件用操作后缀 | `security-incident-playbook.md` → `security-incident-response-policy.md` | policy 不能叫 playbook |
| 策略文件用手册后缀 | `document-discovery-runbook.md` → `document-discovery-policy.md` | policy 不能叫 runbook |

**历史修正（2026-05-02）**：上述 3 个违规文件名已于同日修正。此前 `doc_type-vocabulary.yaml` v1.1.0 允许"文件名描述业务场景、doc_type 定义文档结构，两者不需要一致"——该条款已废除，被本条强制映射替代。

**验证方式（GATE-11 新检测规则 N-08）**：pre-commit hook 逐文件检查"文件名后缀 vs frontmatter doc_type"，不一致则 V1 阻断。

### 一.1 文件夹命名风格选择规则

> §一定义了文件命名规则（全小写 kebab-case），但未定义文件夹命名风格的选择规则。
> 实际项目中存在三种文件夹命名风格混用（单词 / snake_case / L{XX}_snake_case），
> 没有规则说明哪种情况用哪种，AI 新建目录时会猜错风格。

#### 一.1.1 专业机构做法

| 机构/框架 | 文件夹命名规则 | 跟我们的对应 |
|----------|-------------|------------|
| **Python PEP 8** | 包目录用 `snake_case` | 对应 `src/zephyr/` 下 |
| **K8s 社区** | `kebab-case`（如 `cmd/kube-apiserver/`） | 对应 docs/ 下 |
| **Go 社区** | `snake_case` 或 `kebab-case`（项目自选，但必须统一） | 关键：**选一种，全项目统一** |
| **Linux FHS** | 单词（如 `/etc/`、`/var/`、`/usr/`） | 对应顶级目录 |
| **ISO 文档管理** | 编号+名称（如 `04.02_quality/`） | 对应 `L00_data_source/` |

**专业机构的共识**：不是"只能用一种风格"，而是**每种场景有明确的风格选择规则，全项目统一执行**。

#### 一.1.2 三种风格定义

| 风格 | 格式 | 例子 | 适用场景 |
|------|------|------|---------|
| **单词** | `{word}` | `ai/`, `document/`, `task/` | 语义单一的目录 |
| **snake_case** | `{word}_{word}` | `vibe_coding/`, `data_source/` | 语义需要两个以上单词才能表达 |
| **L{XX}_snake_case** | `L{XX}_{snake_case}` | `L00_data_source/`, `L04_risk_management/` | 对应架构层的目录 |

#### 一.1.3 选择决策树

```
Q1: 这个目录是否对应某个架构层（L00~L13）？
    → 是: 用 L{XX}_snake_case（如 L00_data_source/）
    → 否: Q2

Q2: 目录名是否用一个单词就能准确表达？
    → 是: 用单词（如 ai/, document/, task/）
    → 否: 用 snake_case（如 vibe_coding/, post_trade_analytics/）
```

#### 一.1.4 防幻觉完整路径映射表

> AI 新建目录时，查这张表确定命名风格。

| 目录层级 | 命名风格 | 完整路径示例 | 理由 |
|---------|---------|------------|------|
| `docs/` 顶级目录 | 数字编号+单词 | `01_policies_and_standards/` | 已有规范（directory-structure-standard.md §二） |
| `governance/` 子目录 | 单词 | `governance/security/` | 语义单一，一个词就够了 |
| `operational/` 子目录 | 单词 或 snake_case | `operational/devops/` 或 `operational/vibe_coding/` | 一个词够就用单词；不够就用 snake_case |
| `domains/` 子目录 | L{XX}_snake_case | `domains/L00_data_source/` | 对应架构层，必须带层编号 |
| `domains/L{XX}_*/` 子目录 | 单词 | `domains/L00_data_source/governance/` | governance/operational 是固定词 |
| `_registry/` 子目录 | 单词 | `_registry/contracts/` | 语义单一 |
| `meta/` | 无子目录 | — | 固定不增长 |
| `templates/` | 无子目录 | — | 固定不增长 |

#### 一.1.5 禁止的命名风格

| 禁止 | 例子 | 原因 |
|------|------|------|
| kebab-case 文件夹名 | `vibe-coding/` | 与 Python 包目录的 snake_case 冲突；§一的 kebab-case 规则只适用于文件名 |
| 大写字母文件夹名 | `AI/`, `VibeCoding/` | §一禁止大写 |
| 驼峰文件夹名 | `vibeCoding/` | 与全小写规则冲突 |
| 数字前缀（非层编号） | `01_security/` | 数字编号只用于 docs/ 顶级目录 |
| 空格或特殊字符 | `vibe coding/` | 跨平台兼容性问题 |

---

## 二、特殊文件命名规则

### 2.1 Session Log

- 格式：`session-YYYYMMDD-NNN.md`
- 示例：`session-20260422-001.md`
- NNN 为当日序号，从 001 开始

### 2.2 Architecture Decision Record (ADR) — v2.0.0 铁律

本节规则遵循 **Michael Nygard ADR 原规范 / adr-tools / AWS Prescriptive Guidance / Google Engineering Practices** 业界扁平惯例。

#### 2.2.1 文件名

- **格式**：`adr-nnnn-<kebab-case-title>.md`（**全小写**，无例外）
- **示例**：
  - `adr-0014-module-admission-principles.md`
  - `adr-0030-sqlite-task-metadata-store.md`
  - `adr-0041-session-handoff-protocol.md`

#### 2.2.2 frontmatter `module_id`

- **格式**：`ADR-NNNN`（**大写** 4 位数字，无 `EA-` / `PROD-` 等 scope 前缀）
- **作用域与存放**：权威条目收录于 **`KB:decisions`**（Git-backed）；`ADR-NNNN` 仍用作条目编号前缀。**禁止**在文档或脚本中引用已移除的旧路径 `docs/02_enterprise_architecture/adr/` 作为主存放声明。
- **示例**：`module_id: ADR-0011`

#### 2.2.3 文件名 vs module_id 的正交性

| 维度 | 文件名 | module_id |
|---|---|---|
| 大小写 | 小写 `adr-nnnn-*` | 大写 `ADR-NNNN` |
| 编号位数 | 4 位，零填充 | 4 位，零填充 |
| 语义 | 人类友好路径 | 机器可检索 ID |
| 作用域前缀 | 无 | 无 |
| 标题 | 必须带 kebab-case 尾缀 | 不带 |

#### 2.2.4 编号空间铁律（扁平 + append-only）

1. **扁平编号**：所有 ADR 共享同一个 4 位数字序列（`0001~9999`）
2. **禁止嵌套编号**：不得创建 `ADR-NNN-MMM` 子编号空间（原 `ADR-011-*` 12 个子决策已于 Stage F 合并至扁平序列 `0030~0041`）
3. **关联关系靠字段**：用 frontmatter `refines: [ADR-NNNN]` / `supersedes: ADR-NNNN` / `superseded_by: ADR-NNNN` 表达，**不**用编号承载语义
4. **append-only**：编号**永不回收、不回填、不重编**
5. **跳号**：`status: skipped`（意外产生的空号，如 ADR-0006）
6. **保留号**：`status: reserved`（有意识留空，如 ADR-0023~0029）
7. **新决策编号选取**：取**当前最大编号 + 1**，不得回填 skipped/reserved

#### 2.2.5 状态字段（ADR 工作流语义）

| 状态 | 含义 |
|---|---|
| `proposed` | 讨论稿；Markdown 草稿仅存放于 Owner 批准的草稿区或外部工作区；文件名可加 `-draft`；**禁止**写入已移除的 `docs/02_enterprise_architecture/adr/` |
| `accepted` | 已纳入 **`KB:decisions`** namespace；条目内容为 immutable |
| `superseded` | 被新 KB 决策记录取代；原文快照保留，`superseded_by` 指向继任条目 |
| `deprecated` | 已废弃但暂无继任映射（极少使用） |
| `skipped` | 跳号 |
| `reserved` | 保留号 |

**与全局 DocStatus 的关系**：上表描述 KB 决策记录**工作流语义**。若同一 Markdown 另纳入全局文档治理，则 YAML frontmatter 中的 **`status`（draft/active/deprecated）** 必须以 **PS-STD-001 §4.1** 为准；与本节枚举并用时不得自相矛盾，冲突按 **PS-STD-004** 裁定。

KB/decisions 条目的展示用状态标签大小写以 KB schema 为准；全局 DocStatus 仍为小写三值。

### 2.3 架构模型 YAML（层文件）

- 格式：`l{XX}-{layer-name}.yaml`（XX 为两位数字）
- 示例：`l00-data-source.yaml`、`l13-experiment-pipeline.yaml`

### 2.4 状态快照（LATEST 模式）

- 格式：`{name}-LATEST.{ext}`
- 示例：`architecture-snapshot-LATEST.yaml`
- **禁止**：`architecture-snapshot-20260422.yaml`

### 2.5 知识库条目

- 格式：`ke-{三位数序号}-{kebab-case-title}.md`（v2.0.0 起改小写）
- 示例：`ke-025-encoding-corruption-postmortem.md`

### 2.6 Python 源文件

- 格式：`{snake_case}.py`（PEP 8）
- 示例：`intent_parser.py`、`task_repo.py`

### 2.7 模板文件

- 格式：`_template.md`（下划线前缀表示非编号项）
- 位置：各类文档目录（`adr/_template.md`、`working-designs/_template.md`）

---

## 三、历史遗留大写文件（白名单，新建文件一律禁止）

以下大写文件名是历史遗留，**不得新建**，但现有文件暂时保留：

- `AGENTS.md`（根目录，Owner 专属配置文件，类比 `CLAUDE.md` 业界惯例）
- `README.md`（各目录的说明文件，业界通用约定）

**新建文件一律使用全小写 kebab-case / snake_case，无例外。**

---

## 四、module_id 命名空间

### 4.1 通用规则

- **大写字母 + 连字符**：`{TYPE}-{ID}` 格式
- **无 scope 前缀**（作用域由目录承载）
- **唯一性**：全库内 `module_id` 唯一

### 4.2 分类表

| 文档类型 | module_id 格式 | 示例 |
|---|---|---|
| ADR | `ADR-NNNN` | `ADR-0011` |
| Knowledge Entry | `KE-NNN` | `KE-025` |
| Open Question | `OQ-NNN` | `OQ-083` |
| Task | `T-PHASE-NNN` | `T-1-09` |
| Rationale | `R-YY` | `R69` |
| Error Code | `ZA-{SERVER}-{NNNN}` | `ZA-TSK-1001` |

---

## 五、违规检测规则（Stage G GATE-11 实施范围）

pre-commit hook 将检测以下违规：

| 违规类型 | 检测规则 | 豁免白名单 |
|---|---|---|
| 新建文件名包含大写字母 | 正则 `[A-Z]` 命中文件名主体 | `AGENTS.md` / `README.md` |
| 新建文件名包含版本号后缀 | 正则 `-v\d+` / `-round\d+` / `-iteration\d+` | **技术栈专有名词词组**（见 §2.8） |
| 新建状态快照文件带日期后缀 | 正则 `-\d{8}` | LATEST 白名单 |
| ADR 使用嵌套编号 | 正则 `adr-\d+-\d+` | — |
| ADR 缺失 kebab 尾缀 | 正则 `adr-\d{4}\.md` (无中间连字符) | `_template.md` |
| module_id 含 `EA-` / `PROD-` 等 scope 前缀 | frontmatter 字段正则 | 历史 archive/ 目录 |
| ADR module_id 与文件名编号不一致 | 对比 frontmatter 与文件名 | — |

---

## 2.8 技术栈专有名词版本白名单（N-02 豁免）

业界存在大量"技术产品真实版本号"的文件名需求（如 `pydantic-v2` 结构化契约对比 `pydantic-v1`，`python-v3` 迁移指南等）。这类命名语义核心是**产品版本差异**而非作者迭代，应豁免。

**豁免机制**：文件名（小写后）**包含**以下任一 token 时，N-02 不触发：

| Token | 示例 |
|---|---|
| `pydantic-v` | `adr-0040-pydantic-v2-structured-contracts.md` |
| `python-v` / `node-v` / `go-v` / `rust-v` | 语言版本迁移文档 |
| `numpy-v` / `pandas-v` | 数据栈版本对比 |
| `postgres-v` / `mysql-v` / `sqlite-v` / `redis-v` | 数据库版本 |
| `django-v` / `flask-v` / `fastapi-v` | Python Web 框架版本 |
| `typescript-v` / `react-v` / `vue-v` / `next-v` | 前端栈版本 |
| `kubernetes-v` / `docker-v` / `terraform-v` / `ansible-v` | 基础设施版本 |
| `http-v` / `tls-v` / `oauth-v` | 协议版本 |

完整清单维护在 `scripts/governance/check_naming_convention.py::TECH_VERSION_TOKENS`，新增产品需同步更新两处（本文件 + 脚本常量）。

**非豁免判定**（必须整改）：`round1` / `iteration2` / `-v1-draft` / `-v2-final` 等作者草稿迭代式版本后缀**一律不豁免**，必须改用 frontmatter `version` 字段。

---

## 六、历史大改的归档说明

### 6.1 Stage F 归一化批次（2026-04-25）

- **34 个 ADR 文件名**：`ADR-NNNN-*.md` → `adr-nnnn-*.md` 全体小写化
- **12 个嵌套编号**：`ADR-011-001~020` → `ADR-0030~0041` 扁平化
- **19 个 module_id**：`EA-ADR-NNNN` → `ADR-NNNN` 去前缀
- **9 个 frontmatter schema**：`doc_id:` → `module_id:` 统一
- **全库引用更新**：200+ 处
- **snapshot 保留**：`_reorg_snapshots/snapshot-stage-F-pre`（可回滚）

### 6.2 Stage G 漏网清理 + GATE-11 引擎落地（2026-04-25）

**GATE-06 → GATE-11 编号纠偏**：Stage F 预占的 `GATE-06` 与 Architecture-as-Code 已有 `GATE-06 事件 publisher 层检查`（`check_architecture_gates.py v2.0.0`）冲突，本门禁续号为 `GATE-11`，AaC 编号空间 append-only 不动（对标 ADR-0006 跳号治理精神）。

**Stage F 漏网扫尾**：
- **8 个 KE 文件**：`KE-NNN-*.md` → `ke-NNN-*.md` 全体小写化（`docs/08_knowledge/best-practices/`）
- **1 个索引**：`docs/08_knowledge/INDEX.md` → `index.md`
- **29 处视图 module_id**：`target-architecture/` 系列 `EA-ARCH-*` / `EA-VIBE-*` / `EA-AUDIT-*` / `EA-SESSION-*` / `EA-PHASE-*` → `VIEW-*` / `STD-*` / `POL-*` 三族合法命名空间
- **2 个文件名真违规**：
  - `memory-system-landing-v1-task-draft.md` → 去 `-v1`（作者版本后缀，不属于技术产品版本）
  - `architecture-audit-final-verdict-20260421.md` → `-2026-04-21.md`（ISO 日期格式）
- **pydantic-v2 等技术产品版本**：加入 `TECH_VERSION_TOKENS` 豁免白名单（§2.8）

**GATE-11 引擎上线**：`scripts/governance/check_naming_convention.py` + `.pre-commit-config.yaml` 注册，7 条违规规则（N-01 ~ N-07）+ 技术栈豁免机制；全库扫描收敛到 **0 violation**。

**snapshot 保留**：`_reorg_snapshots/snapshot-stage-G-pre`（可回滚）

---

## 六.1 历史遗留目录命名不一致处理

| 目录 | 当前风格 | 是否需要改 | 处理方案 |
|------|---------|:---------:|---------|
| `governance/ai/` | 单词 | ❌ | 符合规则 |
| `governance/document/` | 单词 | ❌ | 符合规则 |
| `governance/task/` | 单词 | ❌ | 符合规则 |
| `operational/vibe_coding/` | snake_case | ❌ | 符合规则（"vibe coding"需要两个词） |
| `operational/devops/` | 单词 | ❌ | 符合规则 |
| `operational/migration/` | 单词 | ❌ | 符合规则 |
| `domains/L00_data_source/`（新建） | L{XX}_snake_case | — | 符合规则 |

**结论：现有目录全部符合规则，不需要改名。** 之前看起来不一致是因为没有选择规则，现在有了选择规则，三种风格各自有明确的适用场景。

## 六.2 新建目录命名检查清单

AI 新建目录时，必须逐项检查：

- [ ] 目录是否对应架构层？→ 是：用 `L{XX}_snake_case`
- [ ] 目录名一个词能表达吗？→ 是：用单词；否：用 `snake_case`
- [ ] 目录名全小写？→ 必须全小写
- [ ] 目录名不含 kebab-case？→ 文件夹名禁止 kebab-case
- [ ] 目录名不含大写字母？→ 必须全小写
- [ ] 目录名不含数字前缀（非层编号）？→ 数字编号只用于 docs/ 顶级目录

---

## 七、与其他规则的关系

| 规则 | 与本标准的关系 |
|------|-------------|
| unified-numbering-standard.md（GOV-DOC-001） | 编号前缀体系是 module_id 命名空间（§四）的权威来源——本标准消费其前缀表来构造 module_id 映射 |
| directory-structure-standard.md（GOV-DOC-002） | 目录结构定义确定了每个子目录的职责边界——本标准的文件夹命名规则服务于该结构 |
| encoding-safety-standard.md（GOV-DOC-005） | 文件名中的字符必须符合 UTF-8 编码约束——编码安全规范确保文件名本身不出现编码损坏 |
| document-lifecycle-standard.md（GOV-DOC-006） | 生命周期决定了文件状态快照的 LATEST 后缀和 session log 的日期前缀用法 |
| document-control-policy.md（GOV-DOC-009） | 本标准的 P4（"名字即地址，禁止改文件名以求匹配内容"）→ DOC-002（名字=责任声明） |
| templates/policy-template.md | 本文件是 policy-template 的实质性例子——结构对齐 template 要求的 §〇 + 与其他规则的关系 + 变更记录 |

## 八、变更记录

| 日期 | 版本 | 修改内容 |
|------|------|---------|
| 2026-04-22 | 1.0.0 | 首次建立基础命名规则（通用 kebab-case + 特殊文件类型 + 历史大写遗留白名单 + 违规检测 3 条）|
| 2026-04-25 | 2.0.0 | **Stage F 归一化升级（major）**：(1) §2.2 ADR 章节全面重写；(2) 新增 §4 module_id 命名空间；(3) §5 违规检测规则扩展至 7 条；(4) 新增 §6 历史大改归档说明 |
| 2026-04-25 | 2.0.1 | **Stage G 开工纠偏（patch）**：编号冲突纠偏 `GATE-06` → `GATE-11`；新增 §2.8 技术栈专有名词版本白名单 |
| 2026-04-30 | 2.1.0 | **文件夹命名规则补全（minor）**：新增 §一.1 文件夹命名风格选择规则（三种风格定义 + 决策树 + 防幻觉路径映射表 + 禁止风格）；新增 §六.1/§六.2 |
| 2026-04-30 | 2.2.0 | 历史修订，见 header comment block |
| 2026-05-02 | 2.4.0 | **文件名-doc_type 强制映射（minor）**。新增 §一.0：文件名后缀必须匹配 doc_type 字段——废除旧 doc_type-vocabulary.yaml v1.1.0 中"文件名不需要与 doc_type 一致"的约定。新增 GATE-11 N-08 检测规则（V1 阻断）。修正 3 个历史违规文件：governance-runbook.md → governance-protocol.md，security-incident-playbook.md → security-incident-response-policy.md，document-discovery-runbook.md → document-discovery-policy.md。 |
| 2026-05-06 | 2.5.0 | **ADR 真源对齐（minor）**。§2.2 等处明确 ADR 权威存放为 **KB:decisions**，禁止将已移除的 `docs/02_enterprise_architecture/adr/` 作为主路径声明；补充 ADR 工作流状态表与 PS-STD-001 DocStatus / PS-STD-004 仲裁关系；正文标题版本号与 frontmatter `version` 对齐。 |
| 2026-05-01 | 2.3.1 | **元规对齐 (patch)**。新增 frontmatter `date` 字段——PS-STD-001 §2.2 规定 Draft+ 必填 7 字段含 `date`，此前仅有 `valid_from` 缺少 `date` 违反了元规必填要求。 |
| 2026-05-01 | 2.3.0 | **结构对齐 + 矛盾消除（minor）**。（1）删除 §1.1"文件夹命名逻辑与原则"——该节与 §一.1 互相矛盾（snake_case vs kebab-case），§一.1 为 v2.1.0 新建的权威版本（有决策树 + 5 家机构对标 + 匹配磁盘真实状态）；（2）新增 §〇.2 管理内容 + §〇.3 不覆盖内容 + §〇.4 专业对标；（3）新增 §七 与其他规则的关系；（4）§七 → §八 更名"变更记录"；（5）版本 2.2.0 → 2.3.0。对齐 templates/policy-template.md 强制结构。全量修改符合 Vibe Coding 零记忆重启标准——每个文件现在 self-describing。 |
