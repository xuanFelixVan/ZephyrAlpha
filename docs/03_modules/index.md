---
classification: internal
date: '2026-05-02'
doc_type: index
generated: '2026-05-02'
merged_from: README.md + index.md
module_id: DIR-03-README
status: active
title: 03_modules 目录说明 — 模块生命周期唯一真源
---

# 03_modules — 模块生命周期文档（唯一真源）

## 责任声明（Single Responsibility）

本目录只存放：**全量模块生命周期文档——C 轨 14 层 + B 轨横切基础设施。蓝图（含施工指引）、接口规范、交付记录统一在此目录树下**。

> **2026-05-02 更新**：蓝图和施工指引已合并为一份 `blueprint.md`（§1-§11 架构设计 + §12 施工指引）。不再需要独立的 `construction-plan.md`。对于 100% AI 开发，一份文档覆盖全流程。

## 文件清单

| 文件 | 说明 |
|------|------|
| module-registry.yaml | 模块生命周期登记表（YAML） |
| blueprint-registry.yaml | 蓝图深度评估登记表（YAML） |
| README.md | 跳转至 index.md |

## 一、抽屉责任（Single Responsibility）

> **一句话**：这个目录是 ZephyrAlpha **所有业务模块**的文档之家。一个模块从生到死的所有文档都在这里。

| 放什么 | 不放什么（→ 去哪） |
|--------|-------------------|
| 模块蓝图（`blueprint.md`）| 企业级架构视图（→ `02_enterprise_architecture/target-architecture/`） |
| 模块施工图（整合在 `blueprint.md` 中）| — |
| 模块交付记录（`delivery/`）| 架构决策记录 ADR（→ `02_enterprise_architecture/adr/`） |
| — | AI 服务接口合同（→ `_b_track_interfaces/`）|
| — | 合规规范（→ `10_compliance/`） |
| — | 治理规则（→ `01_policies_and_standards/`） |

**对标**：Google Monorepo 的"一个项目 = 一个目录，所有文档和代码在一起"原则。Linux FHS 的"按主体分目录，不按文件类型分目录"原则。

## 二、内部结构

```
03_modules/
├── module-registry.yaml          ← ★ 模块登记表（AI 的第一入口，YAML 结构化数据）
├── blueprint-registry.yaml       ← ★ 蓝图登记表（施工进度/完整度/代际评估）
├── index.md                      ← 本文件（唯一真源）
├── README.md                     ← 跳转至 index.md
│
├── _b_track_interfaces/          ← B 轨接口规范（原 07_ai_engineering/，v2.0.0 迁移至此）
│   ├── index.md
│   ├── agent-orchestrator-interface.md
│   ├── context-engine-interface.md
│   ├── feedback-loop-engine-interface.md
│   ├── llm-security-gateway-interface.md
│   └── vector-memory-service-interface.md
│
├── l01_infrastructure/           ← L01 基础设施层
│   ├── README.md                 ← 本层职责声明
│   ├── index.md                  ← 层级索引
│   ├── <module-name>/            ← 每个模块一个子目录（全小写 kebab-case）
│   │   ├── blueprint.md          ← ★ 蓝图：架构设计（§1-§11）+ 施工指引（§12）
│   │   └── delivery/             ← 交付记录（按版本）
│   │       └── index.md
│   └── ...
│
├── l02-l13/                      ← 预留给未来各层（Phase 1+ 随模块创建逐步建立）
```

## 三、模块生命周期（从蓝图到交付）

> **2026-05-02 更新**：蓝图与施工图已合并。`blueprint.md` §1-§11 为架构设计，§12 为施工指引。不再独立维护 `construction-plan.md`。

```
阶段 1: 蓝图（Blueprint）
  │ 产出: blueprint.md（§1-§11 架构设计 + §12 施工指引）
  │ 内容: 架构设计、模块边界、依赖关系、接口契约、实施步骤
  │ 状态: drafting → review → approved
  │
阶段 2: 交付（Delivery）
  │ 产出: delivery/vX.Y.Z.md
  │ 内容: 实际做了什么、偏差说明、经验教训
  │ 状态: pending → delivered → verified
```

**状态机完整定义**见 `module-registry.yaml` → `_schema.status_values`。

## 四、AI 使用指南（Zero-Memory 友好）

### 入口流程

```
Step 1: 读 module-registry.yaml → 了解全部模块概况
        ├── 按 layer 过滤: 这个层有哪些模块？
        ├── 按 domain 过滤: 这个功能域涉及哪些模块？
        └── 按 status 过滤: 哪些蓝图通过了？哪些施工中？

Step 2: 定位到目标模块目录 → 读具体文件
        ├── 读 blueprint.md → 了解模块设计（§1-§11）与施工指引（§12）
        └── 读 delivery/ → 了解历史交付

Step 3: 修改后 → 更新 module-registry.yaml 对应条目的状态
```

### 创建新模块时

```
0. ★【强制查重】先在 module-registry.yaml 中搜索同名/同责模块——
      ├── 是否有 status=retired 但责任范围重叠的蓝图？
      │     → 有 → 走"蓝图升级流程"（见 §八），禁止新建
      │     → 无 → 继续下一步
1. 在 module-registry.yaml 的 modules 列表中添加一条记录
2. 在对应层级目录下创建模块子目录（全小写 kebab-case）
3. 创建 blueprint.md（可参考 templates/blueprint-template.md，§1-§11 架构 + §12 施工指引）
4. 施工完成后，在 delivery/ 下创建版本记录文件
```

### 登记表校验

```
pre-commit 脚本会自动:
  ├── 扫描 03_modules/ 下实际存在的模块目录
  ├── 与 module-registry.yaml 比对
  ├── 物理存在但未登记 → 告警
  └── 已登记但目录不存在 → 告警
```

## 五、与其他目录的关系

```
01_policies_and_standards/  ← 怎么管（治理规则、模板）
    ├── templates/blueprint-template.md        ← 蓝图模板
    ├── governance/module/                     ← 模块准入/生命周期/注入规则
    │                                             bootstrap-plans/ 已于 2026-05-02 废除，
    │                                             施工内容迁入各模块 blueprint.md 中

02_enterprise_architecture/  ← 为什么这样设计（企业架构 + ADR）
    └── target-architecture/                   ← TOGAF 架构视图

03_modules/                  ← ★ 本目录：每个模块的完整文档
    └── module-registry.yaml                  ← 登记表

src/zephyr/                  ← 代码（与 03_modules 按层对齐）
    └── l{NN}_*/                              ← 代码目录，与文档目录一一对应
```

## 六、规模验证（1500 个模块）

```
1500 个模块 ÷ 14 层 ≈ 107 个模块/层
每层 107 个子目录 × 每目录 2-4 个文件 = 文件系统无压力

AI 定位流程:
  module-registry.yaml（1 次读取，了解全部 1500 个）→
  定位到模块目录（1 次读取，了解该模块完整生命周期）
  无需遍历、无需猜测
```

## 七、规则

| # | 规则 | 说明 |
|:--:|------|------|
| 1 | 模块目录名**全小写 kebab-case** | 如 `market-data-ingestor`，不用 `MarketDataIngestor` 或 `market_data_ingestor` |
| 2 | 同模块所有文件放同一目录 | blueprint.md（含施工指引）+ delivery/ 不分散 |
| 3 | 在登记表登记后再创建目录 | module-registry.yaml 先有一条记录，再创建物理目录 |
| 4 | 蓝图必须含 §12 施工指引 | 不允许蓝图缺失具体实施步骤 |
| 5 | 每个层级目录必须含 README.md | 声明本层职责和包含的模块概述 |
| 6 | **一个 module_id 只有一个 blueprint.md** | 同一系统的文档不可拆分为多个蓝图。如需扩展→升级现有蓝图，不新建。违反即重复造轮子 |
| 7 | **创建新蓝图前必须查重** | 必须在 module-registry.yaml 中搜索相同/重叠职责。发现已退役的完成蓝图→走升级流程（§八） |
| 8 | **已完成蓝图必含实现状态节** | `construction_progress = phase_N_complete` 的蓝图正文必须列出实际代码文件映射（§八·铁律五） |
| 9 | **construction_progress 必须 LS 磁盘验证** | AI 设定 construction_progress 前必须先用 `LS` 扫描目标源码目录，凭磁盘事实而非记忆/设计意图填写（§八·铁律六） |

## 八、蓝图查重与复用升级铁律

> **对标**：K8s Admission Controller——不允许重复 CRD 进入集群。ITIL Change Enablement——变更优先升级现有 CI，禁止新建重复配置项。

### 铁律一：蓝图唯一真源

**一个 module_id 只对应一份蓝图。** 同一系统/同一职责领域必须只有一个蓝图。如果发现两份蓝图描述同一系统——那是漏洞，不是特色。

- ✅ 正确：`task-card-kms/` 蓝图 → 内容升级为 `task-system/` 蓝图 → 旧蓝图标记完成
- ❌ 错误：`task-card-kms/` 和 `task-system/` 两套蓝图同时 active —— 责任重叠

### 铁律二：创建前强制查重

AI 在创建任何新蓝图前，**必须先执行以下查重流程**：

```
Step 1: 在 module-registry.yaml 中搜索
        ├── 按 name 搜索：是否有同名/相似名模块？
        ├── 按 tags 搜索：是否有相同标签组合的模块？
        └── 按 purpose/summary 搜索：是否有覆盖相同责任领域的模块？

Step 2: 如果发现已存在的模块
        ├── status=retired 且有 superseded_by → 这是已完成工作
        │     → 需要此领域的更新？
        │       ├── 是 → 走"蓝图升级流程"（见下）
        │       └── 否 → 你为什么要建新蓝图？
        └── status=active/draft → 责任冲突
              → 停止创建。向 Owner 说明冲突情况，等待裁定。

Step 3: 确认无重叠后 → 正常创建新蓝图
```

### 铁律三：复用升级流程（替换"新建"）

当已退役的完成蓝图的责任领域出现新需求时，**禁止新建蓝图——必须升级现有蓝图**：

```
蓝图升级流程:
  1. 锁定目标蓝图：确认 status=retired 的蓝图内容与当前需求高度重叠
  2. 状态重开：将该蓝图 status 从 retired 改为 draft（加 frontmatter 备注"reopened for Phase N upgrade"）
  3. 升级规则：
     ├── 原内容必须保留在 §1-§11 中，新增内容追加/插入，不可删除
     ├── Version bump：如 v2.0.0 → v3.0.0
     ├── ADR 创建：重大升级必须创建 ADR（如 adr-nnnn-reopen-<module>.md）
     └── superseded 链更新：如果该蓝图曾被 superseded_by，需评估是否仍指向正确目标
  4. 恢复施工：按 §12 施工指引重新施工
  5. 完成后：status → retired（或 approved），construction_progress → phase_N_complete

  禁止:
    ├── ❌ 直接创建新 module_id 覆盖相同职责
    ├── ❌ 删除旧蓝图内容
    └── ❌ 无视查重流程直接开工
```

### 铁律四：已完成蓝图永久保留

`construction_progress = phase_0_completed` 或 `phase_1_complete` 的蓝图：
- **标记 "构建完成"**：不是失败、不是废弃——是完成了该做的事
- **物理文件永久保留**：作为系统演进的历史记录
- **可被重开升级**：有新需求时按铁律三升级

### 铁律五：蓝图必须记载实际实现状态

任何 `construction_progress = phase_N_complete` 或 `merged_into_blueprint` 的蓝图，**必须在蓝图正文中记录实际代码实现情况**——蓝图的真源职责不仅包括"设计了什么"，还包括"实现了什么"。

**要求**：
- 蓝图必须含 `## 实际代码实现情况（Code Implementation Status）` 节（或等效节号）
- 该节必须列出现有磁盘代码文件及其对应蓝图节的映射
- 无代码的纯设计蓝图 → `construction_progress` 必须为 `not_started` 或 `skeleton`

**禁止**：
- ❌ 蓝图说"已完成"但无代码文件清单 → 虚假声明
- ❌ 蓝图 frontmatter 有 `construction_progress: phase_1_complete` 但正文无实现节 → 状态不一致
- ❌ 只更新注册表 YAML 但不更新蓝图 .md 正文 → 蓝图真源原则被违反（YAML 注册表是索引，不是真源）

> **大白话**：K8s 不允许两个同名的 Deployment。我们也不允许两套蓝图管同一件事。查重是 AI 的第一责任——不查就建等于闭着眼睛造桥。发现旧的完成了的蓝图？打开它、升级它、记录它——不要在隔壁再盖一栋。"

## 排除规则（不应放入本目录的内容）

- ❌ 5 大 AI 服务的接口文档 → `_b_track_interfaces/`（本目录内）
- ❌ 项目级元计划/DevOps 流程 → `01_policies_and_standards/operational/devops/`
- ❌ 治理规范/标准 → `01_policies_and_standards/governance/`
- ❌ 企业架构视图/ADR → `02_enterprise_architecture/`

## 父级目录

- 父级：[docs 根目录](file:///D:/ZephyrAlpha/docs/index.md)
