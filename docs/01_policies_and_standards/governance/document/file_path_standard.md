---
module_id: GOV-DOC-004
title: 文件路径规范
doc_type: standard
status: active
version: "1.2.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-06"
ttl: permanent
summary: "定义 ZephyrAlpha 2.0 中所有文件的强制写入路径、废弃路径和根目录白名单，防止文件放错位置导致路径漂移。"
tags: [file-path, governance, path-standard]
rule_form: declarative
scope: global
stability: stable
verifiability: automated
---

# 文件路径规范

> **目的**：定义 ZephyrAlpha 2.0 中所有文件的强制写入路径、废弃路径和根目录白名单，防止文件放错位置导致路径漂移。
>
> **铁律**：MUST 按本标准路径映射存放文件——散落存放 = 路径引用断裂。

## 〇、目的与范围

### 〇.1 目的

为 ZephyrAlpha 2.0 项目中的所有文件类型指定唯一的、强制性的写入路径。消除"同类文件可能出现在多个位置"的歧义——每种文件有且只有一个正确的存放目录。

### 〇.2 本标准管理以下内容

| # | 内容 | 说明 |
|---|------|------|
| 1 | 21 种文件类型的强制写入路径 | 从治理规范到 AI 生成产物的完整路径映射 |
| 2 | 废弃路径清单 | 旧体系中已被替代的路径，禁止写入 |
| 3 | 根目录白名单 | 项目根目录允许存在的文件类型 |
| 4 | 违规检测规则 | 5 种路径违规判定 |

### 〇.3 本标准**不**覆盖以下内容

| # | 排除项 | 以哪个文件为准 |
|---|--------|-------------|
| 1 | 目录结构的具体定义（每个目录装什么） | directory-structure-standard.md（GOV-DOC-002） |
| 2 | 文件的命名规范 | file-naming-standard.md（GOV-DOC-003） |
| 3 | 文件的生命周期管理 | document-lifecycle-standard.md（GOV-DOC-006） |
| 4 | 文件的删除/移动安全门禁 | file-operation-safety-gate.md（GOV-DOC-007） |
| 5 | 新增目录的审批流程 | directory-structure-standard.md §七 |

### 〇.4 专业对标

| 来源 | 对标内容 |
|------|---------|
| ITIL SACM → Location | 每个配置项（CI）必须有唯一的物理/逻辑位置记录——本文的"一种文件类型 = 一个目标目录"基于此 |
| Linux FHS (Filesystem Hierarchy Standard) | 标准化的目录结构——`/etc/` 放配置、`/usr/bin/` 放可执行文件——本文以同样的确定性思维定义项目路径 |
| K8s API Group Organization | `apps/v1/deployments`——通过前缀确定资源的存放位置，不靠约定——本文的路径映射表对等 |

---

## 一、强制写入路径

| 操作类型 | 强制路径 |
|---------|---------|
| 治理规范、标准、协议 | `docs/01_policies_and_standards/` |
| AI 治理规则 | `docs/01_policies_and_standards/governance/ai/` |
| 架构治理规则 | `docs/01_policies_and_standards/governance/architecture/` |
| 文档治理规则 | `docs/01_policies_and_standards/governance/document/` |
| 企业架构视图（TOGAF） | `docs/02_enterprise_architecture/target-architecture/` |
| ADR | **`KB:decisions`**（Git-backed；旧 `docs/02_enterprise_architecture/adr/` 物理树已移除） |
| 架构模型 YAML | `docs/02_enterprise_architecture/target-architecture/architecture-model/` |
| 架构快照 | `docs/02_enterprise_architecture/snapshots/` |
| 模块生命周期文档 | `docs/03_modules/l{xx}_{layer}/{module}/` |
| 知识库条目 | `docs/08_knowledge/` |
| 审计报告/状态 | `docs/09_audit/` |
| Session Log | 已迁至项目外部独立目录（2026-05-02）。`docs/19_development_workspace/` 目录已删除。 |
| 任务书 | 已迁至项目外部独立目录（2026-05-02）。`docs/19_development_workspace/` 目录已删除。 |
| 业务代码 | `src/zephyr/{layer_id}/` |
| 治理/审计脚本 | `scripts/governance/` |
| pre-commit hooks | `scripts/hooks/` |
| AI 生成产物（临时） | `.audit_cache/`（已 gitignored） |

## 二、废弃路径（禁止写入）

| 废弃路径 | 替代路径 |
|---------|---------|
| `docs/`（旧体系根目录下所有子目录） | `docs/` 对应子目录 |
| `docs/01_FRAMEWORK/` | `docs/02_enterprise_architecture/` |
| `docs/09_audit/` | `docs/09_audit/` |
| `docs/10_GOVERNANCE_COMPLIANCE/` | `docs/01_policies_and_standards/` |
| `docs/08_KNOWLEDGE/` | `docs/08_knowledge/` |
| `docs/04_CONSTRUCTION/` | `docs/03_modules/` |
| `docs/02_enterprise_architecture/adr/` | **`KB:decisions`**（ADR 权威 namespace） |

## 三、根目录白名单

项目根目录（`d:/ZephyrAlpha/`）只允许以下文件存在：

```
AGENTS.md
README.md
LICENSE
CONTRIBUTING.md
SECURITY.md
pyproject.toml
requirements*.txt
.pre-commit-config.yaml
.env*
.gitignore
.editorconfig
.roomodes
```

**禁止**在根目录创建任何 `.py`、`.txt`、`.json`、`.md`（白名单外）文件。

## 四、违规检测规则

以下情况视为路径违规：

- 在 `docs/`（旧体系）下新建文件
- 在根目录创建白名单外的文件
- 将治理规范放入 `02_enterprise_architecture/`
- 将架构视图放入 `01_policies_and_standards/`
- 将 AI 生成产物直接写入受版本控制目录

## 四-A、物理路径树规则

| # | 规则 | 检测方式 |
|---|------|---------|
| 1 | `project-path-tree.yaml` 由脚本自动生成，禁止手写 | `python scripts/governance/generate_project_path_tree.py --check` |
| 2 | `path-ownership-map.yaml` 中同一路径只能被一个蓝图声明 | `python scripts/governance/generate_path_ownership_map.py --conflicts` |
| 3 | 路径冲突时，`ssot_claims` 声明优先于 §0.1 清单声明 | `--conflicts` 输出 resolution 字段 |
| 4 | 路径变更（移动/重命名）必须同步更新 `path-ownership-map.yaml` | `python scripts/governance/generate_path_ownership_map.py --check` |

| 产出物 | 路径 | 生成脚本 |
|--------|------|---------|
| 物理路径树快照 | `docs/01_policies_and_standards/_registry/catalogs/project-path-tree.yaml` | `scripts/governance/generate_project_path_tree.py` |
| 路径归属声明 | `docs/03_modules/path-ownership-map.yaml` | `scripts/governance/generate_path_ownership_map.py` |

## 五、禁止操作

| 禁止操作 | 原因 |
|---------|------|
| 在 `docs/` 下新建文件 | 只读遗留体系 |
| 在根目录创建白名单外文件 | 根目录只允许配置文件 |
| 新建未在 `directory-structure-standard.md` 中定义的顶级目录 | 必须先更新规范并获得 Owner 批准 |

## 六、与其他规则的关系

| 规则 | 与本标准的关系 |
|------|-------------|
| directory-structure-standard.md（GOV-DOC-002） | 本标准 §一 的路径条目与 GOV-DOC-002 §5.1.2 的完整路径映射表一一对应。目录结构定义了"什么目录装什么"，本标准定义了"什么文件只能装哪个目录" |
| file-naming-standard.md（GOV-DOC-003） | 文件命名规范确保文件名可被 glob 模式发现，路径规范确保文件位置可预测 |
| document-lifecycle-standard.md（GOV-DOC-006） | 生命周期管理决定了文件在哪个阶段可能发生路径变更（如归档移动到 archive/） |

## 七、变更记录

| 日期 | 版本 | 修改内容 |
|------|------|---------|
| 2026-05-16 | 1.2.0 | 新增 §四-A 物理路径树规则：4 条路径树/归属声明规则 + 2 个自动生成产出物路径。minor 版本升级。 |
| 2026-04-22 | 1.0.0 | 初始创建。定义 21 种文件类型的强制写入路径、废弃路径、根目录白名单、违规检测规则。 |
| 2026-05-06 | 1.1.3 | ADR 路径：`§一` / `§二` 与 **KB:decisions** 对齐；与 **META-TERM-001**、**directory-registry.yaml**（adr 键 deprecated）交叉引用一致。版本号 patch +1。 |
| 2026-05-04 | 1.1.2 | 审计修复。Session Log 和任务书 路径更新：`docs/19_development_workspace/` 已删除（迁至外部独立目录），行内容替换为迁移说明。版本号 patch +1。 |
| 2026-05-01 | 1.1.1 | **元规对齐 + 描述修正 (patch)**。（1）`date` 更新为 2026-05-01——上次修改日与实际不一致；（2）§一 路径表中 `governance/document/` 描述从"文档格式标准"修正为"文档治理规则"——该目录覆盖 7 维度（Identity/Location/Encoding/Lifecycle/Safety/Discovery/Quality），不止"格式"。 |
| 2026-05-01 | 1.1.0 | 结构对齐。（1）新增 §〇 目的与范围（§〇.2 管理内容 + §〇.3 不覆盖内容 + §〇.4 专业对标）；（2）新增 §六 与其他规则的关系 + §七 变更记录；（3）蓝图路径格式修正：`L{XX}_{LAYER}` → `l{xx}_{snake_case}`。对齐 templates/policy-template.md 强制结构。 |
