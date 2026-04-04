---
module_id: INDEX_TACTICS_001
version: 5.3.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-04
owner: 首席文档架构�?standard_type: 专业量化机构文档
applicable_scope: 全系�?compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 进行�?---

# 交易战术目录索引

> 清风量化系统 v5.3 战术层文档导�?>
> **文档职责说明**:
> - **INDEX.md**: 快速入口（5分钟导航），聚焦核心文档和常用路�?> - **SITEMAP.md**: 完整地图（深度参考），提供全面目录结构和按用途路�?>
> �?完整文档地图请查�?[SITEMAP.md](../02_FACTOR_LIBRARY/SITEMAP.md)
>
> **快速入�?*: �?推荐阅读 [BLUEPRINT.md](../02_FACTOR_LIBRARY/04_DATA_SOURCE/02_SCHEDULER/BLUEPRINT.md) 了解完整系统蓝图


## 🎯 快速入�?
### 我是新手
�?[00_OVERVIEW/README.md](../../README.md) - 系统总览�?分钟�?
### 我要理解架构
�?[BLUEPRINT.md](../02_FACTOR_LIBRARY/04_DATA_SOURCE/02_SCHEDULER/BLUEPRINT.md) - 清风量化系统蓝图（推荐）
�?[01_FRAMEWORK/ARCHITECTURE.md](../01_FRAMEWORK/ARCHITECTURE.md) - Layer 0-11统一架构

### 我要开发策�?�?[Strategy_Spec_S001.md](Strategy_Spec_S001.md) - 策略模板�?0分钟�?
### 我要查因�?�?[02_FACTOR_LIBRARY/02_ALPHA_FACTORS_INDEX.md](../02_FACTOR_LIBRARY/02_ALPHA_FACTORS_INDEX.md) - 因子索引�?0分钟�?
### 我要部署系统
�? - 部署指南�?0分钟�?
### 我遇到问�?�?[FAQ.md](../02_FACTOR_LIBRARY/FAQ.md) - 常见问题�?分钟�?
### 我要审计系统
�?[09_AUDIT/INDEX_AUDIT.md](../09_AUDIT/INDEX_AUDIT.md) - 审计门户�?分钟�?

## �?核心文档（必读）

| 文档 | 用�?| 阅读时间 |
|------|------|----------|
| [BLUEPRINT.md](../02_FACTOR_LIBRARY/04_DATA_SOURCE/02_SCHEDULER/BLUEPRINT.md) | �?清风量化系统蓝图（合并版�?| 30分钟 |
| [01_FRAMEWORK/ARCHITECTURE.md](../01_FRAMEWORK/ARCHITECTURE.md) | Layer 0-11统一架构 | 30分钟 |
| [AI_Permissions.md](../08_AI_GOVERNANCE/AI_Permissions.md) | AI权限清单 | 10分钟 |
| [API_Contract.md](API_Contract.md) | 模块接口契约 | 15分钟 |
| [Strategy_Spec_S001.md](Strategy_Spec_S001.md) | 策略逻辑白皮�?| 30分钟 |
| [BLUEPRINT_CHECKLIST.md](../09_AUDIT/BLUEPRINT_CHECKLIST.md) | 蓝图完整性检查清�?| 20分钟 |

> **说明**: 7个蓝图文档已合并�?，原始文档归档于 


## 🤖 AI自主量化系统（终极目标）

> 核心: AI判断市场 �?AI选择策略 �?AI调整风控 �?人仅授权

### 开发规�?
| 文档 | 用�?| 索引 |
|------|------|------|
| [BLUEPRINT.md](../02_FACTOR_LIBRARY/04_DATA_SOURCE/02_SCHEDULER/BLUEPRINT.md) | 清风量化系统蓝图 | - |
| [06_ARCHIVE/main/BLUEPRINTS/06_DEVELOPMENT_ROADMAP.md](../06_ARCHIVE/main/BLUEPRINTS/06_DEVELOPMENT_ROADMAP.md) | 阶段性开发路线图 (Phase 0-6) | DEV.001 |
| [06_ARCHIVE/main/BLUEPRINTS/05_AI_RESEARCH_FRAMEWORK.md](../06_ARCHIVE/main/BLUEPRINTS/05_AI_RESEARCH_FRAMEWORK.md) | AI研究Agent核心架构 | AI.AGENT.001 |




## 📁 文档地图

### 00_OVERVIEW - 系统总览

| 文档 | 说明 |
|------|------|
| [README.md](../../README.md) | 系统总览 |
| [DATA_FLOW.md](../00_OVERVIEW/DATA_FLOW.md) | 数据流图 |
| [CHANGELOG.md](../06_ARCHIVE/CHANGELOG.md) | 版本历史（已合并�?|

### 01_FRAMEWORK - 框架定义

| 文档 | 说明 |
|------|------|
| [README.md](../../README.md) | 框架文档索引 |
| [ARCHITECTURE.md](../01_FRAMEWORK/ARCHITECTURE.md) | Layer 0-11统一架构 |
| [MODULE_DESIGN_TEMPLATE.md](../05_IMPLEMENTATION/MODULE_DESIGN_TEMPLATE.md) | 模块设计模板 |
| [MODULE_DESIGN_PLAN.md](../02_FACTOR_LIBRARY/MODULE_DESIGN_PLAN.md) | 模块设计计划 |
| [MARKET_REGIME.md](../01_FRAMEWORK/MARKET_REGIME.md) | 市场状态识�?|
| [HUMAN_AI_FLOW.md](../01_FRAMEWORK/HUMAN_AI_FLOW.md) | 人机协作流程 |
| [TECH_STACK.md](../01_FRAMEWORK/TECH_STACK.md) | 技术栈选择 |

### 02_FACTOR_LIBRARY - 因子�?(v5.0架构)

| 目录/文档 | 说明 |
|------|------|
| [README.md](../../README.md) | 因子库总览 |
|  | 因子分类导航 |
|  | 因子研究方法�?|
| [02_ALPHA_FACTORS_INDEX.md](../02_FACTOR_LIBRARY/02_ALPHA_FACTORS_INDEX.md) | 87个Alpha因子索引 |
|  | 46个风险因�?|
|  | 数据源说�?|
|  | 回测报告 |
|  | 因子注册 |
|  | 监控中心 |

### 03_TRADING_TACTICS - 交易策略

| 目录/文档 | 说明 |
|------|------|
| [README.md](../../README.md) | 策略池总览 |
| [INDEX.md](INDEX.md) | 策略索引 |
|  | 策略框架 |
| [STRATEGY_ENGINE_BLUEPRINT.md](01_STRATEGY_FRAMEWORK/STRATEGY_ENGINE_BLUEPRINT.md) | 策略引擎开发蓝�?|
|  | 高级战术 |
|  | 游资策略 |

### 04_EXECUTION - 执行引擎

| 目录/文档 | 说明 |
|------|------|
| [README.md](../../README.md) | 执行总览 |
|  | 事件驱动引擎 |
|  | 交易执行 |
|  | 监控模块 |

### 05_IMPLEMENTATION - 实施指南

| 目录/文档 | 说明 |
|------|------|
| [README.md](../../README.md) | 实施指南总览 |
|  | 快速开始（5分钟�?|
|  | 开发规�?|
|  | 部署指南 |
|  | 运维手册 |

### 06_ARCHIVE - 归档

| 目录/文档 | 说明 |
|------|------|
| [README.md](../../README.md) | 归档说明 |
|  | v4.0开发文档（精简�?个） |
|  | 过度工程化文�?|

### 07_RESEARCH - AI研究

| 目录/文档 | 说明 |
|------|------|
| [README.md](../../README.md) | 研究总览 |
|  | 研究环境 |
|  | 探索性分�?|
|  | 模式识别 |
|  | 实验追踪 |

### 09_AUDIT - 系统治理审计

| 目录/文档 | 说明 |
|------|------|
| [README.md](../../README.md) | 审计体系总览 |
| [INDEX_AUDIT.md](../09_AUDIT/INDEX_AUDIT.md) | 审计门户首页 |
|  | 审计标准 |
|  | 审计程序 |


## 🔍 按用途查�?
### 策略开发�?1. [Strategy_Spec_S001.md](Strategy_Spec_S001.md) - 策略模板
2. [02_FACTOR_LIBRARY/02_ALPHA_FACTORS_INDEX.md](../02_FACTOR_LIBRARY/02_ALPHA_FACTORS_INDEX.md) - 因子�?3. [03_TRADING_TACTICS/](./) - 策略参�?4.  - 开发规�?
### 系统构建
1. [BLUEPRINT.md](../02_FACTOR_LIBRARY/04_DATA_SOURCE/02_SCHEDULER/BLUEPRINT.md) - 清风量化系统蓝图
2. [01_FRAMEWORK/ARCHITECTURE.md](../01_FRAMEWORK/ARCHITECTURE.md) - 统一架构
3.  - 快速开�?
### 运维
1.  - 部署指南
2.  - 运维手册
3. [FAQ.md](../02_FACTOR_LIBRARY/FAQ.md) - 常见问题

### AI研究
1. [BLUEPRINT.md](../02_FACTOR_LIBRARY/04_DATA_SOURCE/02_SCHEDULER/BLUEPRINT.md) - AI研究框架（见第六章）
2.  - 实验追踪
3. [KNOWLEDGE_MANAGEMENT.md](../02_FACTOR_LIBRARY/KNOWLEDGE_MANAGEMENT.md) - 知识管理

### 系统审计�?1. [09_AUDIT/INDEX_AUDIT.md](../09_AUDIT/INDEX_AUDIT.md) - 审计门户首页
2. [09_AUDIT/STANDARDS/AUDIT_STANDARDS.md](../09_AUDIT/STANDARDS/AUDIT_STANDARDS.md) - 审计标准
3. [09_AUDIT/PROCEDURES/AI_AUDIT_GUIDELINES.md](../09_AUDIT/PROCEDURES/AI_AUDIT_GUIDELINES.md) - AI审计指南


## 📊 文档统计

- **总文档数**: ~80+（精简后）
- **核心文档**: 5个（必读�?- **一级目�?*: 8�?- **因子�?*: 133个（87 Alpha + 46 Risk�?- **策略�?*: 120个（S001-S120�?

## 📋 其他重要文档

| 文档 | 说明 | 用�?|
|------|------|------|
| [BLUEPRINT.md](../02_FACTOR_LIBRARY/04_DATA_SOURCE/02_SCHEDULER/BLUEPRINT.md) | 清风量化系统蓝图（合并版�?| 完整蓝图参�?|
| [CHANGELOG.md](../06_ARCHIVE/CHANGELOG.md) | 版本变更日志 | 版本控制参�?|
| [VERSIONING.md](../05_IMPLEMENTATION/VERSIONING.md) | 版本管理规范 | 版本控制参�?|
| [CODE_EXAMPLES.md](../05_IMPLEMENTATION/CODE_EXAMPLES.md) | 代码示例 | 开发参�?|
| [HANDOVER.md](../02_FACTOR_LIBRARY/HANDOVER.md) | 交接文档 | 项目交接参�?|
| [EXPERIMENT_TRACKING.md](../07_RESEARCH/EXPERIMENT_TRACKING.md) | 实验追踪 | AI研究参�?|
| [DOCUMENT_AUDIT_v5.3.md](../../DOCUMENT_AUDIT_v5.3.md) | 文档审查报告 | 文档治理参�?|

### 因子库补充文�?
| 文档 | 说明 |
|------|------|
| [02_FACTOR_LIBRARY/99_AUDIT_REPORT.md](../02_FACTOR_LIBRARY/99_AUDIT_REPORT.md) | 因子库审计报�?|
| [02_FACTOR_LIBRARY/OPTIMIZATION_SUMMARY.md](../02_FACTOR_LIBRARY/OPTIMIZATION_SUMMARY.md) | 因子优化总结 |

### 交易策略补充文档

| 文档 | 说明 |
|------|------|
| [03_TRADING_TACTICS/OPTIMIZATION_REPORT.md](OPTIMIZATION_REPORT.md) | 策略优化报告 |
| [03_TRADING_TACTICS/REFACTOR_COMPLETE.md](REFACTOR_COMPLETE.md) | 重构完成报告 |


## 📖 完整地图

如需完整文档结构，请查看 [SITEMAP.md](../02_FACTOR_LIBRARY/SITEMAP.md)


**最后更�?*: 2026-03-31
**维护�?*: 清风量化系统
**版本**: v5.3 个人开发精简�?