---
module_id: SITEMAP
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
---

﻿---
module_id: DOC_SYSTEM_SITEMAP_001
version: 1.0.0
status: Active
created_date: 2026-04-03
last_updated: 2026-04-03
owner: 系统架构?standard_type: 专业量化机构文档地图
responsibility:
  - 扩展功能、辅助模块、支撑文档
applicable_scope: 全系?compliance_level: 专业标准
parent_document: INDEX.md
implementation_status: 活跃维护
---
---
---


# 系统文档地图 (SITEMAP)

> 清风量化系统 v5.3 的完整文档导航地?>
> **职责区分**:
> - [INDEX.md](./INDEX.md) = 快速入口（5分钟导航?> - **本文?* = 完整地图（深度参考）

---

## 📍 文档位置导航 (v5.3)

### 一级导?
```
docs/
├── 核心文档 (6?
?  ├── INDEX.md                   # 快速入??  ├── SITEMAP.md                 # 完整地图 ←────────────??  └── ...
?├── 00_OVERVIEW/                   # 系统总览
├── 00_RESOURCES/                  # 资源文档
├── 01_FRAMEWORK/                  # 框架设计 (三级时间框架)
├── 02_FACTOR_LIBRARY/             # 因子?(5700+因子)
├── 03_TRADING_TACTICS/            # 交易策略?├── 04_EXECUTION/                  # 执行引擎
├── 05_IMPLEMENTATION/             # 实施指南
├── 06_ARCHIVE/                    # 归档文档
├── 08_AI_GOVERNANCE/              # AI治理
├── 09_AUDIT/                      # 系统治理审计
└── 10_AI_WORKFLOW/                # AI工作?```

---

## 🗺?按用途查?
### 我是新手

**快速上手路?* (30分钟):
1. 阅读 [INDEX.md](./INDEX.md) - 快速入?(5分钟)
2. 阅读 [01_FRAMEWORK/README.md](./01_FRAMEWORK/README.md) - 框架概述 (10分钟)
3. 阅读 [05_IMPLEMENTATION/01_QUICKSTART/README.md](./05_IMPLEMENTATION/01_QUICKSTART/README.md) - 快速开?(15分钟)

### 我要理解架构

**架构学习路线** (2小时):
1. 阅读 [01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md](./01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md) - 三级时间框架融合架构 (30分钟)
2. 阅读 [01_FRAMEWORK/ARCHITECTURE.md](./01_FRAMEWORK/ARCHITECTURE.md) - 系统架构 (30分钟)
3. 阅读 [01_FRAMEWORK/ARCHITECTURE_MIGRATION_PLAN.md](./01_FRAMEWORK/ARCHITECTURE_MIGRATION_PLAN.md) - 架构迁移计划 (20分钟)
4. 阅读 [01_FRAMEWORK/MODULE_RESPONSIBILITY_BOUNDARIES.md](./01_FRAMEWORK/MODULE_RESPONSIBILITY_BOUNDARIES.md) - 模块边界 (20分钟)

### 我要开发策?
**策略开发路?* (4小时):
1. 阅读 [03_TRADING_TACTICS/INDEX.md](./03_TRADING_TACTICS/INDEX.md) - 交易战术索引 (30分钟)
2. 阅读 [02_FACTOR_LIBRARY/System_Manifest.md](System_Manifest.md) - 因子库系统清?(30分钟)
3. 阅读 [02_FACTOR_LIBRARY/01_STANDARDS/FACTOR_REGISTRY.md](02_FACTOR_LIBRARY/01_STANDARDS/FACTOR_REGISTRY.md) - 因子注册?(30分钟)
4. 阅读 [05_IMPLEMENTATION/02_DEVELOPMENT/DEVELOPMENT_STANDARDS.md](./05_IMPLEMENTATION/02_DEVELOPMENT/DEVELOPMENT_STANDARDS.md) - 开发规?(1小时)
5. 实践编写策略代码 (1.5小时)

### 我要执行审计

**审计工作路线** (2小时):
1. 阅读 [09_AUDIT/README.md](./09_AUDIT/README.md) - 审计系统概述 (20分钟)
2. 阅读 [09_AUDIT/TEMPLATES/PROFESSIONAL_DOCUMENT_GOVERNANCE_AUDIT_GUIDE.md](./09_AUDIT/TEMPLATES/PROFESSIONAL_DOCUMENT_GOVERNANCE_AUDIT_GUIDE.md) - 审计指南 (30分钟)
3. 阅读 [09_AUDIT/TEMPLATES/DOCUMENT_GOVERNANCE_AUDIT_CHECKLIST.md](./09_AUDIT/TEMPLATES/DOCUMENT_GOVERNANCE_AUDIT_CHECKLIST.md) - 审计检查清?(20分钟)
4. 执行审计工作 (50分钟)

---

## 📊 按目录查?
### 01_FRAMEWORK - 框架设计

**核心职责**: 系统架构定义、技术决策、模块边?
**关键文档**:
- [专业多时间框架架构](./01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md)
- [架构文档](./01_FRAMEWORK/ARCHITECTURE.md)
- [模块职责边界](./01_FRAMEWORK/MODULE_RESPONSIBILITY_BOUNDARIES.md)
- [技术栈](./01_FRAMEWORK/TECH_STACK.md)

**子目?*:
- [ARCHITECTURE_DECISIONS/](01_FRAMEWORK/ARCHITECTURE_DECISIONS/) - 架构决策记录

**索引文件**: [INDEX.md](./01_FRAMEWORK/INDEX.md) | [SITEMAP.md](./01_FRAMEWORK/SITEMAP.md)

### 02_FACTOR_LIBRARY - 因子?
**核心职责**: 因子方法论、因子计算、因子回测、数据源接口

**关键文档**:
- [系统清单](System_Manifest.md)
- [因子注册表](02_FACTOR_LIBRARY/01_STANDARDS/FACTOR_REGISTRY.md)
- [因子计算框架](./02_FACTOR_LIBRARY/01_STANDARDS/FACTOR_CALCULATION_FRAMEWORK.md)
- [数据源概述](01_FRAMEWORK\README.md)

**子目?*:
- [00_GOVERNANCE/](02_FACTOR_LIBRARY/00_GOVERNANCE/) - 治理文档
- [01_STANDARDS/](02_FACTOR_LIBRARY\01_STANDARDS) - 方法?- [03_RISK_FACTORS/](02_FACTOR_LIBRARY\03_RISK_FACTORS) - 风险因子
- [04_DATA_SOURCE/](02_FACTOR_LIBRARY\04_DATA_SOURCE) - 数据?- [05_BACKTEST/](02_FACTOR_LIBRARY\05_BACKTEST) - 回测

**索引文件**: [INDEX.md](./02_FACTOR_LIBRARY/INDEX.md) | [SITEMAP.md](./02_FACTOR_LIBRARY/SITEMAP.md)

### 03_TRADING_TACTICS - 交易战术

**核心职责**: 交易策略设计、战术执?
**关键文档**:
- [交易战术索引](./03_TRADING_TACTICS/INDEX.md)

**索引文件**: [INDEX.md](./03_TRADING_TACTICS/INDEX.md)

### 04_EXECUTION - 执行?
**核心职责**: 事件引擎、交易执行、监控、风险引?
**关键文档**:
- [执行层概述](./04_EXECUTION/README.md)
- [事件总线](./04_EXECUTION/01_EVENT_ENGINE/EVENT_BUS.md)
- [监控蓝图](./04_EXECUTION/03_MONITORING/BLUEPRINT.md)

**子目?*:
- [01_EVENT_ENGINE/](04_EXECUTION\01_EVENT_ENGINE) - 事件引擎
- [03_MONITORING/](04_EXECUTION\03_MONITORING) - 监控系统
- [06_SIMULATION/](04_EXECUTION\06_SIMULATION) - 模拟系统

**索引文件**: [INDEX.md](./04_EXECUTION/INDEX.md)

### 05_IMPLEMENTATION - 实施?
**核心职责**: 快速开始、开发标准、部署、运?
**关键文档**:
- [快速开始](./05_IMPLEMENTATION/01_QUICKSTART/README.md)
- [开发标准](./05_IMPLEMENTATION/02_DEVELOPMENT/DEVELOPMENT_STANDARDS.md)
- [运维概述](./05_IMPLEMENTATION/07_OPERATIONS/README.md)

**子目?*:
- [01_QUICKSTART/](05_IMPLEMENTATION\01_QUICKSTART) - 快速开?- [02_DEVELOPMENT/](05_IMPLEMENTATION\02_DEVELOPMENT) - 开发标?- [07_OPERATIONS/](05_IMPLEMENTATION\07_OPERATIONS) - 运维
- [05_TECHNICAL_SPECIFICATIONS/](05_IMPLEMENTATION\05_TECHNICAL_SPECIFICATIONS) - 技术规?
**索引文件**: [INDEX.md](./05_IMPLEMENTATION/INDEX.md) | [SITEMAP.md](./05_IMPLEMENTATION/SITEMAP.md)

### 09_AUDIT - 审计系统

**核心职责**: 审计标准、模板、最佳实践、培?
**关键文档**:
- [审计系统概述](./09_AUDIT/README.md)
- [专业文档治理审计指南](./09_AUDIT/TEMPLATES/PROFESSIONAL_DOCUMENT_GOVERNANCE_AUDIT_GUIDE.md)
- [文档治理审计检查清单](./09_AUDIT/TEMPLATES/DOCUMENT_GOVERNANCE_AUDIT_CHECKLIST.md)

**子目?*:
- [STANDARDS/](09_AUDIT\STANDARDS) - 标准
- [TEMPLATES/](09_AUDIT\TEMPLATES) - 模板
- [BEST_PRACTICES/](08_KNOWLEDGE\BEST_PRACTICES) - 最佳实?- [TRAINING/](09_AUDIT\TRAINING) - 培训

**索引文件**: [INDEX.md](./09_AUDIT/INDEX.md)

### 10_AI_WORKFLOW - AI工作?
**核心职责**: AI工作流程、智能体协作

**关键文档**:
- [AI工作流索引](./10_AI_WORKFLOW/INDEX.md)

**索引文件**: [INDEX.md](./10_AI_WORKFLOW/INDEX.md)

---

## 🔍 按关键词查找

### 架构相关

- **三级时间框架**: [专业多时间框架架构](./01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md)
- **Layer 0-11**: [架构迁移计划](./01_FRAMEWORK/ARCHITECTURE_MIGRATION_PLAN.md)
- **模块边界**: [模块职责边界](./01_FRAMEWORK/MODULE_RESPONSIBILITY_BOUNDARIES.md)

### 因子相关

- **因子注册**: [因子注册表](02_FACTOR_LIBRARY/01_STANDARDS/FACTOR_REGISTRY.md)
- **因子计算**: [因子计算框架](./02_FACTOR_LIBRARY/01_STANDARDS/FACTOR_CALCULATION_FRAMEWORK.md)
- **因子回测**: [回测概述](./02_FACTOR_LIBRARY/05_BACKTEST/README.md)

### 数据相关

- **数据?*: [数据源概述](01_FRAMEWORK\README.md)
- **QMT接口**: [QMT接口](./02_FACTOR_LIBRARY/04_DATA_SOURCE/QMT_INTERFACE.md)
- **iFind连接?*: [iFind连接器](./02_FACTOR_LIBRARY/04_DATA_SOURCE/IFIND_CONNECTOR.md)

### 审计相关

- **审计指南**: [专业文档治理审计指南](./09_AUDIT/TEMPLATES/PROFESSIONAL_DOCUMENT_GOVERNANCE_AUDIT_GUIDE.md)
- **审计检查清?*: [文档治理审计检查清单](./09_AUDIT/TEMPLATES/DOCUMENT_GOVERNANCE_AUDIT_CHECKLIST.md)
- **最佳实?*: [文档治理最佳实践](./09_AUDIT/BEST_PRACTICES/DOCUMENT_GOVERNANCE_BEST_PRACTICES.md)

---

## 🔗 相关链接

- [系统主索引](./INDEX.md)
- [框架设计索引](./01_FRAMEWORK/INDEX.md)
- [因子库索引](./02_FACTOR_LIBRARY/INDEX.md)
- [实施层索引](./05_IMPLEMENTATION/INDEX.md)
