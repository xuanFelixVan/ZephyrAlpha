---
module_id: META-IDX-001
title: 元规则目录索引
doc_type: index
status: active
version: "1.3.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-02"
ttl: permanent
summary: "meta/ 目录的导航入口。列出所有元规则文件的 module_id、文件名、状态和一句话说明。新 AI session 从此文件开始了解元规则体系全貌。"
tags: [index, meta, navigation]
rule_form: declarative
scope: global
stability: stable
verifiability: manual
---

# 元规则目录索引

> **module_id**: META-IDX-001 | **version**: 1.3.0 | **status**: active

本文件是 `meta/` 目录的导航入口。**新 AI session 的第一站**——读完此文件即了解整个元规则体系的全貌。

> **对标**：ISO/IEC Directives Part 2 要求标准目录提供索引文件。IETF RFC 目录有 `index.txt`。IEEE 标准库有目录级 README。
> Zero-Memory Restart Standard §5.1：AI 每次都是"新员工"，必须有一个文件让它 3 分钟内理解目录结构。

---

## 一、文件清单

| module_id | 文件名 | status | 一句话说明 |
|-----------|--------|:------:|----------|
| PS-STD-000 | meta-standard-constitution.md | active | 最高层级元规则——"什么规则进宪法"的二元分类标准（后果不可逆性） |
| PS-STD-001 | metadata-registry.md | active | 全项目元数据唯一真源——字段定义、doc_type 受控词表、三域架构 |
| PS-STD-002 | document-structure-standard.md | active | 标准文档模板——L1/L2/L3 三层模板，L1 含 4 种标准子类型（v3.1.0） |
| PS-STD-003 | behavior-boundaries-standard.md | active | 行为边界标准——绝对禁止（ABS）、条件禁止（COND）、推荐做法（REC） |
| PS-STD-004 | rule-classification-and-arbitration-standard.md | active | 规则分类与冲突裁决标准——五维分类体系 + stability→layer→scope 推导链 |
| PS-STD-006 | governance-metrics-standard.md | active | 治理度量标准——6 项 KPI 定义规则体系健康度 |
| PS-STD-009 | rule-lifecycle-and-change-standard.md | active | 规则治理标准——生命周期状态机 + P0~P3 变更门控审批流程 |
| PS-STD-011 | governance-methodology-standard.md | active | 治理方法论——MTH-001~011 十一条决策原则 + 决策流程总图 |
| PS-STD-012 | rule-verification-standard.md | active | 规则验证标准——自动化/手动验证的分级体系 |
| META-GLS-001 | glossary.md | active | 规则体系术语表——21 个核心术语的统一定义（仲裁源） |
| META-TERM-001 | terminology-mapping.md | active | 术语大白话映射表——专业术语↔通俗解释双轨对照（glossary.md 的下游衍生文件） |

> **已迁移**：PS-REG-001 rule-registry.md 和 PS-REG-002 registry-of-registries.yaml 已迁移至 `_registry/catalogs/`（2026-05-03）。

---

## 二、本目录责任声明

### 2.1 责任范围（本目录管什么）

本目录是 ZephyrAlpha **元规则的唯一存放处**，负责管理：

- **规则标准**（`*-standard.md`）：定义"规则怎么写"、"规则怎么分类"、"规则怎么变更"、"规则怎么验证"——规则本身的元规则
- **术语表**（`glossary.md`）：核心术语的统一定义和仲裁源
- **规则登记表**（`_registry/catalogs/rule-registry.md`）：全部规则的集中发现入口（已从 meta/ 迁移）

### 2.2 责任边界（本目录不管什么）

以下类型文件 **不在** 本目录管辖范围内：

| 文件类型 | 不在此目录的原因 | 正确位置 |
|---------|---------------|---------|
| 具体领域的治理规则（编码、文档、任务等） | 这些是"规则实例"不是"元规则" | `governance/` 各子目录 |
| 操作流程/施工手册 | 操作层面内容 | `operational/` |
| 模板文件 | 模板是工具不是规则 | `templates/` |
| 架构决策记录（ADR） | 架构决策不是规则标准 | **`KB:decisions`**（旧 `docs/02_enterprise_architecture/adr/` 已移除） |
| Session Log | 临时会话记录 | 已迁至项目外部独立目录（2026-05-02）。 |

### 2.3 目录命名逻辑

`meta/` 目录名遵循以下命名逻辑：

- **`meta`** = 元（metadata/meta-rules 的 meta）——对标 ITIL meta-data management、ISO 11179 元数据管理
- 全小写，单级目录名，不使用 kebab-case 或下划线
- **不**使用 `meta-rules/` 或 `_meta/`——因为 meta 本身已经是完整语义单元

## 三、文件总数

META 目录共有 **13 个文件**（9 个 PS-STD 标准 + 1 个 META-GLS 术语表 + 1 个 META-IDX 索引入口 + 1 个 META-TERM 术语映射表 + 1 个 PS-STD 元数据注册表），注册在 [metadata-registry.md](metadata-registry.md)。PS-REG-001 和 PS-REG-002 已迁移至 [_registry/catalogs/](../_registry/catalogs/)。

## 四、推荐阅读顺序

新 AI session 接手 meta/ 目录时，按以下顺序阅读：

```
1. index.md（本文件）          ← 3 分钟了解全貌
2. META-GLS-001 术语表        ← 统一核心概念定义
3. PS-STD-000 元标准宪法      ← 理解"规则怎么分类"
4. PS-STD-011 治理方法论      ← 理解"决策怎么执行"
5. PS-STD-001 元数据注册表    ← 理解"字段怎么填"
6. PS-STD-003 行为边界标准    ← 理解"什么不能做"
```

---

## 五、编号池状态

| 编号 | 状态 | 说明 |
|------|:----:|------|
| PS-STD-000 ~ PS-STD-004 | ✅ 已分配 | 核心元标准 |
| PS-STD-005 | 📋 可用 | 待分配 |
| PS-STD-006 | ✅ 已分配 | 治理度量标准（draft） |
| PS-STD-007 ~ PS-STD-008 | 📋 可用 | 待分配（PS-STD-007 保留给持续改进标准，PS-STD-008 合并释放） |
| PS-STD-009 ~ PS-STD-012 | ✅ 已分配 | 扩展元标准（PS-STD-010 已合并至 PS-STD-009，编号释放） |
| PS-STD-013+ | 📋 可用 | 扩展空间 |
| META-GLS-001 | ✅ 已分配 | 术语表 |
| META-IDX-001 | ✅ 已分配 | 索引入口 |
| PS-REG-001 | ✅ 已分配 | 规则登记表 |

---

## 六、未来待办标准（Backlog）

以下标准当前**暂不创建**，待触发条件满足时启动。每项均列明对标框架和触发条件，确保不会遗忘。

| # | module_id | 标准名称 | 对标框架 | 触发条件 | 计划阶段 |
|:--:|-----------|---------|---------|---------|:---:|
| G3 | PS-STD-007 | 持续改进标准 | ISO 42001 §10, ITIL CSI | 累计 50 次 AI session 后，出现可识别的重复问题模式（同类问题 ≥ 3 次） | beta+ |
| G4 | GOV-CMP-003 | 风险登记册 | NIST AI RMF | 识别出 ≥ 5 项独立的 AI 操作风险时。注意：放入 `governance/compliance/` 而非 meta/ | beta+ |
| G5 | PS-STD-013 | 知识管理标准 | ITIL Knowledge Mgmt | Session Log 体积 > 50 条，需自动抽取经验时 | stable+ |

> **大白话**：这三个是"现在不该补、但以后可能需要补"的标准。每一次 AI session 读到 index.md 都会看到这张表——确保不会被遗忘。触发条件是客观可量化的，不是"感觉需要了再加"。

---

## 七、变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 1.3.0 | 2026-05-02 | 审计修复。(1) §三 文件总数 12→13——补齐遗漏的 META-TERM-001（terminology-mapping.md），分解更新为 9 PS-STD + 1 PS-REG + 1 META-GLS + 1 META-IDX + 1 META-TERM = 13。(2) Context Tax 余量从 3 更新为 2（13/15）。版本号 minor +1。 |
| 1.2.3 | 2026-05-01 | meta/ 最终审查。(1) 3 个文件正文版本号对账：META-GLS-001 body 1.1.0→1.2.0、PS-STD-006 body 1.1.0→1.1.1、PS-STD-003 body 1.5.2→1.5.3。(2) 文件总数确认：12 个（Context Tax 余量 3），无幽灵条目。版本号 patch +1。 |
| 1.2.2 | 2026-05-01 | 状态同步修复。(1) §一 PS-STD-006/011/012 状态从 draft→active（对齐实际 frontmatter）。(2) PS-STD-011 说明从"九条/MTH-001~009"→"十条/MTH-001~010"，META-GLS-001 从"19个"→"21个"（对齐实际术语表）。版本号 patch +1。 |
| 1.2.1 | 2026-05-01 | 交叉引用同步——PS-STD-002 v3.1.0 引入标准子类型，§一 PS-STD-002 说明从"必须包含 19 个章节"改为"L1/L2/L3 三层模板，L1 含 4 种标准子类型"。版本号 patch +1。 |
| 1.2.0 | 2026-05-01 | 决策卡三合一。(1) §一 文件清单更新：PS-STD-002/004/009 文件名修正（`document-structure-standard.md`/`rule-classification-and-arbitration-standard.md`/`rule-lifecycle-and-change-standard.md`）。(2) 新增 §二 本目录责任声明——正向：管规则标准+术语表+登记表；负向：不管领域治理规则/操作流程/模板/ADR/Session Log；命名逻辑：`meta` = 元。(3) section 重新编号（§三~§七）。(4) PS-STD-009+010 合并收尾：文件清单更新 PS-STD-009 文件名 + 编号池标注 PS-STD-010 已合并释放。(5) 新增 §三 文件总数（12 个，Context Tax 余量 3）。 |
| 1.1.0 | 2026-05-01 | (1) PS-STD-008 合并至 PS-STD-004：文件清单删除 PS-STD-008 行，PS-STD-004 说明更新为"规则分类与冲突裁决标准——五维分类体系 + stability→layer→scope 推导链"。(2) 编号池 PS-STD-005~008 标记为可用（PS-STD-008 从合并释放）。(3) 新增 §四 未来待办标准（Backlog）：登记 G3/G4/G5 三个待创建标准的触发条件和计划阶段。 |
| 1.0.0 | 2026-05-01 | 初始创建——meta/ 目录系统审查后补齐 |
