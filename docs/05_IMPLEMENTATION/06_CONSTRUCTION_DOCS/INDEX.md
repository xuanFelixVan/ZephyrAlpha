---
module_id: 05_IMPLEMENTATION_06_CONSTRUCTION_DOCS_INDEX_2
version: 1.1.0
status: Active
created_date: 2026-04-07
last_updated: '2026-04-17'
owner: 首席文档架构师
responsibility:
  - 06_CONSTRUCTION_DOCS目录索引
layer: layer_05
---




# 建设文档索引

## 核心定位

提供建设文档的总入口导航，包含各子目录链接、快速开始指南、文档阅读路径等，支持快速定位所需文档，帮助读者快速了解文档体系结构。




## 设计目标

### 主要目标

1. **功能完整性**: 确保文档内容完整，满足使用需求
2. **易用性**: 提高文档可读性，便于快速理解
3. **可维护性**: 文档结构清晰，便于后续维护
4. **一致性**: 确保文档格式和风格统一

### 质量目标

- 文档完整性: 100%
- 格式规范性: 100%
- 内容准确性: 100%


## 📋 目录概要

**Canonical 路径（全库建设文档真源）**：`docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/`。新建与默认修改均落于此树；与 `docs/06_CONSTRUCTION_DOCS/` 的关系见下「遗留路径」。

**目录职责**：建设文档总入口——项目办公室、正式图纸柜、施工计划、实施指南、运维手册、配置模板、设计文档与检查清单等。

**顶层子目录数**：**8**（与磁盘一致，2026-04-10 核对）。存在并列前缀 `03_CONSTRUCTION_PLANS` 与 `03_OPERATION_MANUALS`，后续如需统一编号可单独立项迁移。

**文档篇数**：不在本页缓存；请以各子目录 `INDEX.md` 及 ~~[01_BLUEPRINTS/INDEX.md]~~（脚本生成）为准。

### 遗留路径（`docs/06_CONSTRUCTION_DOCS`）

历史上与上述 canonical **平行**的 `docs/06_CONSTRUCTION_DOCS/` 树（**非权威**；当前仅余少量蓝图副本）。权威模块列表以 canonical 侧 ~~[01_BLUEPRINTS 机器生成索引]~~ 为准。以下链接用于消除严格孤儿入度并避免误删遗留副本：

- [遗留 01_BLUEPRINTS 索引](../../06_CONSTRUCTION_DOCS/01_BLUEPRINTS/INDEX.md)
- A_STOCK_DATA_PROCESSING_BLUEPRINT（遗留副本）

```
```---
```

## 📁 子目录清单

| 子目录 | 职责 | 导航入口 |
|--------|------|----------|
| **00_MANAGEMENT** | 项目办公室：规章、CANON 门禁、任务清单、登记表 | ~~[README]~~ |
| **01_BLUEPRINTS** | 正式图纸柜：模块 `*BLUEPRINT.md` | ~~[INDEX]~~ |
| **02_IMPLEMENTATION_GUIDES** | 实施指南（回测、策略工厂等） | ~~[INDEX]~~ |
| **03_CONSTRUCTION_PLANS** | 施工计划与 MVP 方案 | ~~[INDEX]~~ |
| **03_OPERATION_MANUALS** | 部署、监控、维护、风控等运维手册 | ~~[INDEX]~~ |
| **04_CONFIG_TEMPLATES** | 配置、变更、测试与评审模板 | ~~[INDEX]~~ |
| **05_DESIGN_DOCS** | 库表、界面、交易成本、一致性等设计 | ~~[INDEX]~~ |
| **06_CHECKLISTS** | 评审与发布前后检查、文档质量门 | ~~[INDEX]~~ |

```
```---
```

## 🔍 目录说明（与子目录表一致）

### 00_MANAGEMENT

规章、蓝图终稿定义、~~[CANON]~~ 施工门禁与卫生总案、全库蓝图终稿任务清单、全库治理导航等。

### 01_BLUEPRINTS

系统模块蓝图；根目录仅 `*BLUEPRINT.md` 与 `INDEX.md`；过程报告见 `REPORTS/`（见 图纸柜规则）。

### 02_IMPLEMENTATION_GUIDES

面向编码与联调落地的实施指南。

### 03_CONSTRUCTION_PLANS

施工层计划与索引；与门禁 §0.3 施工文档交付衔接。

### 03_OPERATION_MANUALS

运维向手册（部署、监控、维护等）。

### 04_CONFIG_TEMPLATES

各类模板（API、变更、部署、测试计划等）。

### 05_DESIGN_DOCS

专题设计正文与子域 INDEX。

### 06_CHECKLISTS

质量与发布检查清单。

```
```---
```

## 📊 统计信息

| 指标 | 数值 |
|------|------|
| **顶层子目录数** | 8 |
| **活跃子目录** | 8（见上表） |

> 各目录文档计数易变，**不以本页固定数字为真**；请以子目录 INDEX / `generate_01_blueprints_index.py` 产出为准。

```
```---
```

## 🔗 相关文档

- ~~[项目办公室总入口（00_MANAGEMENT）]~~
- 项目办公室 AI 交接说明
- 图纸柜执行协议（防幻觉）
- ~~[蓝图终稿 / 施工门禁真源（CANON）]~~
- 全库治理文档导航
- 文档治理架构（机构式 L0～L5）
- 蓝图交付标准（机构精华版）
- 蓝图终稿定义与认可
- 受控文档登记表
- 01_BLUEPRINTS 图纸柜文件治理规则
- 全库蓝图终稿任务清单（勾选进度）
- [实施层索引](../INDEX.md)
- 全库蓝图阶段总结（总清单主入口之一）

### 索引健全性与目录体量（P5 §7）

- **零入链扫描（最新）**：../../09_AUDIT/STATE/INDEX_HEALTH_ORPHAN_20260417.md（`docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS`；**zero_inbound=0**）  
- **rollup（深度 3 条数）**：../../09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260414.md（检索本前缀 **272** 条）  
- **尽治任务清单 §7**：./00_MANAGEMENT/REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md

```
```---
```

## 📝 维护记录

| 日期 | 操作 | 操作人 | 备注 |
|------|------|--------|------|
| 2026-04-17 | P5 §7 门面：`INDEX_HEALTH_20260417`；补 `REPORTS/README` 与 `05_DESIGN_DOCS/INDEX` 入链使零入链归零 | 文档治理 | 见 `09_AUDIT/STATE/INDEX_HEALTH_ORPHAN_20260417.*` |
| 2026-04-10 | 子目录表与磁盘对齐 | 文档治理 | 8 顶层目录；删除冗长逐文件枚举（旧版见 `git log -p --` 本路径） |
| 2026-04-07 | 创建索引 | Audit Sentinel | 初始创建索引 |

```
```---
```

## 📑 子目录索引入口（维护说明）

本页**不**逐项枚举全树 Markdown（避免与下列 INDEX 重复、易过期）。请直接打开：

- ~~[01_BLUEPRINTS/INDEX.md]~~
- ~~[02_IMPLEMENTATION_GUIDES/INDEX.md]~~
- ~~[03_CONSTRUCTION_PLANS/INDEX.md]~~
- ~~[03_OPERATION_MANUALS/INDEX.md]~~
- ~~[04_CONFIG_TEMPLATES/INDEX.md]~~
- ~~[05_DESIGN_DOCS/INDEX.md]~~
- ~~[06_CHECKLISTS/INDEX.md]~~

**本目录根下常用单文件**：~~[README]~~、BLUEPRINT_TEMPLATE.md、CONSTRUCTION_SPECIFICATION.md、IMPLEMENTATION_PROGRESS.md、VERSION_MANAGEMENT_GUIDE.md、AI_CONSTRUCTION_QUICK_REFERENCE.md、NEW_EMPLOYEE_ONBOARDING_GUIDE.md。

```
```---
```

**目录状态**：与子目录磁盘布局对齐（2026-04-10）  
**索引策略**：大门 + 子目录表；篇级枚举交给各 `INDEX.md` 与蓝图生成脚本

<!-- orphan-link -->
- [ai-construction-quick-reference](ai-construction-quick-reference.md)

<!-- orphan-link -->
- [blueprint-template](blueprint-template.md)

<!-- orphan-link -->
- [construction-specification](construction-specification.md)

<!-- orphan-link -->
- [implementation-progress](implementation-progress.md)

<!-- orphan-link -->
- [new-employee-onboarding-guide](new-employee-onboarding-guide.md)

<!-- orphan-link -->
- [version-management-guide](version-management-guide.md)
