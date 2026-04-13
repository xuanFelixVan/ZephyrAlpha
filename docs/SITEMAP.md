---
module_id: DOC_SYSTEM_SITEMAP_001
version: 1.1.0
status: Active
created_date: 2026-04-03
last_updated: '2026-04-12'
owner: 首席文档架构师
standard_type: 专业量化机构文档地图
applicable_scope: 全系统文档导航
compliance_level: 专业标准
parent_document: INDEX.md
implementation_status: 活跃维护
responsibility:
  - 系统文档导航与站点地图维护
layer: layer_00
---

# 系统文档地图 (SITEMAP)

> 清风量化系统 v5.3 的完整文档导航地图

> **职责区分**:
> - [INDEX.md](./INDEX.md) = 快速入口（5分钟导航）
> - **本文档** = 完整地图（深度参考）

```
```---
```

## 📍 文档位置导航 (v5.3)

### 一级目录

```
docs/
├── 核心文档 (6个)
│   ├── INDEX.md                   # 快速入口
│   ├── SITEMAP.md                 # 完整地图 ←────────────── 你在这里
│   └── ...
│
├── 00_OVERVIEW/                   # Layer 0: 系统总览
├── 00_RESOURCES/                  # Layer 0: 资源文档
├── 01_FRAMEWORK/                  # Layer 1: 框架设计 (三级时间框架)
├── 02_FACTOR_LIBRARY/             # Layer 2: 因子库 (5700+因子)
├── 03_TRADING_TACTICS/            # Layer 3: 交易战术
├── 04_EXECUTION/                  # Layer 4-6: 执行引擎
├── 05_IMPLEMENTATION/             # 实施指南
├── 06_ARCHIVE/                    # 归档文档
├── 06_CONSTRUCTION_DOCS/          # 施工文档 (蓝图图纸柜)
├── 07_AI_REPORTING/               # Layer 7: AI报告与分析
├── 08_KNOWLEDGE/                  # 知识库
├── 09_AUDIT/                      # 系统治理审计
├── 11_STRATEGIC_DECISION/         # Layer 11: 战略决策层
└── 12_MODULE_DESIGNS/                # 模块设计草图
```

```
```---
```

## 🗺️ 按用途查找

### 我是新手

**快速上手路线** (30分钟):

1. 阅读 [INDEX.md](./INDEX.md) - 快速入口 (5分钟)
2. 阅读 [01_FRAMEWORK/README.md](./01_FRAMEWORK/README.md) - 框架概述 (10分钟)
3. 阅读 `05_IMPLEMENTATION/01_QUICKSTART/README.md` - 快速开始 (15分钟)

### 我要理解架构

**架构学习路线** (2小时):

1. 阅读 01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md - 三级时间框架融合架构 (30分钟)
2. 阅读 [01_FRAMEWORK/ARCHITECTURE.md](./01_FRAMEWORK/ARCHITECTURE.md) - 系统架构 (30分钟)
3. 阅读 `01_FRAMEWORK/ARCHITECTURE_MIGRATION_PLAN.md` - 架构迁移计划 (20分钟)
4. 阅读 01_FRAMEWORK/MODULE_RESPONSIBILITY_BOUNDARIES.md - 模块边界 (20分钟)

### 我要开发策略

**策略开发路线** (4小时):

1. 阅读 [03_TRADING_TACTICS/INDEX.md](./03_TRADING_TACTICS/INDEX.md) - 交易战术索引 (30分钟)
2. 阅读 [02_FACTOR_LIBRARY/README.md](./02_FACTOR_LIBRARY/README.md) - 因子库系统清单 (30分钟)
3. 阅读 [02_FACTOR_LIBRARY/INDEX.md](./02_FACTOR_LIBRARY/INDEX.md) - 因子注册表 (30分钟)
4. 阅读 05_IMPLEMENTATION/02_DEVELOPMENT/DEVELOPMENT_STANDARDS.md - 开发规范 (1小时)
5. 实践编写策略代码 (1.5小时)

### 我要执行审计

**审计工作路线** (2小时):

1. 阅读 [09_AUDIT/README.md](./09_AUDIT/README.md) - 审计系统概述 (20分钟)
2. 阅读 09_AUDIT/TEMPLATES/PROFESSIONAL_DOCUMENT_GOVERNANCE_AUDIT_GUIDE.md - 审计指南 (30分钟)
3. 阅读 09_AUDIT/TEMPLATES/DOCUMENT_GOVERNANCE_AUDIT_CHECKLIST.md - 审计检查清单 (20分钟)
4. 执行审计工作 (50分钟)

```
```---
```

## 📊 按目录查找

### 01_FRAMEWORK - 框架设计

**核心职责**: 系统架构定义、技术决策、模块边界

**关键文档**:

- 专业多时间框架架构
- [架构文档](./01_FRAMEWORK/ARCHITECTURE.md)
- 模块职责边界
- 技术栈

**子目录**:

- [ARCHITECTURE_DECISIONS/](./01_FRAMEWORK/ARCHITECTURE_DECISIONS/) - 架构决策记录

**索引文件**: [INDEX.md](./01_FRAMEWORK/INDEX.md) | [SITEMAP.md](./01_FRAMEWORK/SITEMAP.md)

### 02_FACTOR_LIBRARY - 因子库

**核心职责**: 因子方法论、因子计算、因子回测、数据源接口

**关键文档**:

- [因子库 README](./02_FACTOR_LIBRARY/README.md)
- [因子库索引](./02_FACTOR_LIBRARY/INDEX.md)
- [因子注册表](./02_FACTOR_LIBRARY/INDEX.md)
- `因子计算框架`

**子目录**:

- [00_GOVERNANCE/](./02_FACTOR_LIBRARY/00_GOVERNANCE/) - 治理文档
- [01_STANDARDS/](./02_FACTOR_LIBRARY/01_STANDARDS/) - 方法论标准
- [03_RISK_FACTORS/](./02_FACTOR_LIBRARY/03_RISK_FACTORS/) - 风险因子
- [04_DATA_SOURCE/](./02_FACTOR_LIBRARY/04_DATA_SOURCE/) - 数据源
- [05_BACKTEST/](./02_FACTOR_LIBRARY/05_BACKTEST/) - 回测

**索引文件**: [INDEX.md](./02_FACTOR_LIBRARY/INDEX.md) | [SITEMAP.md](./02_FACTOR_LIBRARY/SITEMAP.md)

### 03_TRADING_TACTICS - 交易战术

**核心职责**: 交易策略设计、战术执行

**关键文档**:

- [交易战术索引](./03_TRADING_TACTICS/INDEX.md)

**索引文件**: [INDEX.md](./03_TRADING_TACTICS/INDEX.md)

### 04_EXECUTION - 执行引擎

**核心职责**: 事件引擎、交易执行、监控、风险引擎

**关键文档**:

- [执行层概述](./04_EXECUTION/README.md)
- 事件总线
- `监控蓝图`

**子目录**:

- [01_EVENT_ENGINE/](./04_EXECUTION/01_EVENT_ENGINE/) - 事件引擎
- [03_MONITORING/](./04_EXECUTION/03_MONITORING/) - 监控系统
- [06_SIMULATION/](./04_EXECUTION/06_SIMULATION/) - 模拟系统

**索引文件**: [INDEX.md](./04_EXECUTION/INDEX.md)

### 05_IMPLEMENTATION - 实施指南

**核心职责**: 快速开始、开发标准、部署、运维

**关键文档**:

- `快速开始`
- 开发标准
- [运维概述](./05_IMPLEMENTATION/07_OPERATIONS/README.md)

**子目录**:

- [01_QUICKSTART/](./05_IMPLEMENTATION/01_QUICKSTART/) - 快速开始
- [02_DEVELOPMENT/](./05_IMPLEMENTATION/02_DEVELOPMENT/) - 开发标准
- [07_OPERATIONS/](./05_IMPLEMENTATION/07_OPERATIONS/) - 运维
- [05_TECHNICAL_SPECIFICATIONS/](./05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/) - 技术规范

**索引文件**: [INDEX.md](./05_IMPLEMENTATION/INDEX.md) | [SITEMAP.md](./05_IMPLEMENTATION/SITEMAP.md)

### 06_CONSTRUCTION_DOCS - 施工文档

**核心职责**: 蓝图图纸柜、施工文档索引

**关键文档**:

- [施工文档索引](./06_CONSTRUCTION_DOCS/INDEX.md)
- [蓝图图纸柜 README](./06_CONSTRUCTION_DOCS/01_BLUEPRINTS/README.md)

**索引文件**: [INDEX.md](./06_CONSTRUCTION_DOCS/INDEX.md)

### 07_AI_REPORTING - AI报告与分析

**核心职责**: AI报告生成、绩效归因、自动报告

**关键文档**:

- [AI报告层索引](./07_AI_REPORTING/INDEX.md)
- [AI报告层 README](./07_AI_REPORTING/README.md)

**索引文件**: [INDEX.md](./07_AI_REPORTING/INDEX.md)

### 08_KNOWLEDGE - 知识库

**核心职责**: 最佳实践、因子案例库、策略案例库

**关键文档**:

- [知识库索引](./08_KNOWLEDGE/INDEX.md)
- [最佳实践索引](./08_KNOWLEDGE/BEST_PRACTICES/INDEX.md)
- [因子案例库索引](./08_KNOWLEDGE/FACTOR_LIBRARY/INDEX.md)
- [策略案例库索引](./08_KNOWLEDGE/STRATEGY_LIBRARY/INDEX.md)

**索引文件**: [INDEX.md](./08_KNOWLEDGE/INDEX.md)

### 09_AUDIT - 审计系统

**核心职责**: 审计标准、模板、最佳实践、培训

**关键文档**:

- [审计系统概述](./09_AUDIT/README.md)
- 专业文档治理审计指南
- 文档治理审计检查清单

**子目录**:

- [STANDARDS/](./09_AUDIT/STANDARDS/) - 标准
- [TEMPLATES/](./09_AUDIT/TEMPLATES/) - 模板
- [BEST_PRACTICES/](./08_KNOWLEDGE/BEST_PRACTICES/) - 最佳实践
- [TRAINING/](./09_AUDIT/TRAINING/) - 培训

**索引文件**: [INDEX.md](./09_AUDIT/INDEX.md)

### 11_STRATEGIC_DECISION - 战略决策层

**核心职责**: Layer 11 战略决策、蓝图清单、职责边界

**关键文档**:

- [完整蓝图总览](./11_STRATEGIC_DECISION/complete-blueprint-overview.md) (权威源)
- [蓝图索引](./11_STRATEGIC_DECISION/blueprint-index.md)
- [职责边界矩阵](./11_STRATEGIC_DECISION/responsibility-boundary-matrix.md)

**索引文件**: 参见蓝图索引

### 12_MODULE_DESIGNS - 模块设计草图

**核心职责**: 模块设计文档索引

**关键文档**:

- [模块设计索引](./12_MODULE_DESIGNS/INDEX.md)
- [Layer 0 模块设计索引](./12_MODULE_DESIGNS/layer_0/INDEX.md)

```
```---
```

## 🔍 按关键词查找

### 架构相关

- **三级时间框架**: 专业多时间框架架构
- **Layer 0-11**: [统一架构](./01_FRAMEWORK/ARCHITECTURE.md)
- **模块边界**: 模块职责边界

### 因子相关

- **因子注册**: [因子库索引](./02_FACTOR_LIBRARY/INDEX.md)
- **因子计算**: `因子计算框架`
- **因子回测**: `回测概述`

### 数据相关

- **数据源**: [框架 README](./01_FRAMEWORK/README.md)
- **QMT接口**: `QMT接口`
- **iFind连接器**: `iFind连接器`

### 审计相关

- **审计指南**: 专业文档治理审计指南
- **审计检查清单**: 文档治理审计检查清单
- **最佳实践**: 文档治理最佳实践

```
```---
```

## 🔗 相关链接

- [系统主索引](./INDEX.md)
- [框架设计索引](./01_FRAMEWORK/INDEX.md)
- [因子库索引](./02_FACTOR_LIBRARY/INDEX.md)
- [实施层索引](./05_IMPLEMENTATION/INDEX.md)
