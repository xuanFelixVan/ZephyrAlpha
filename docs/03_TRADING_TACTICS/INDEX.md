---
module_id: DOC_DOC_001
version: 5.1.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构师
standard_type: 专业量化机构文档
applicable_scope: 全系统
compliance_level: 专业标准
parent_document: INDEX.md
implementation_status: 进行中
---


# 文档主索引

> 清风量化系统 v5.1 精简文档导航（个人开发版）
>
> **文档职责说明**:
> - **INDEX.md**: 快速入口（5分钟导航），聚焦核心文档和常用路径
> - **SITEMAP.md**: 完整地图（深度参考），提供全面目录结构和按用途路线
>
> ⭐ 完整文档地图请查看 [SITEMAP.md](../02_FACTOR_LIBRARY/SITEMAP.md)
>
> **快速入口**: ⭐ 推荐阅读 [BLUEPRINT.md](../02_FACTOR_LIBRARY/04_DATA_SOURCE/02_SCHEDULER/BLUEPRINT.md) 了解完整系统蓝图


## 🎯 快速入口

### 我是新手
→ [00_OVERVIEW/README.md](../../README.md) - 系统总览（5分钟）

### 我要理解架构
→ [BLUEPRINT.md](../02_FACTOR_LIBRARY/04_DATA_SOURCE/02_SCHEDULER/BLUEPRINT.md) - 清风量化系统蓝图（推荐）
→ [01_FRAMEWORK/ARCHITECTURE.md](../01_FRAMEWORK/ARCHITECTURE.md) - Layer 0-8统一架构

### 我要开发策略
→ [Strategy_Spec_S001.md](Strategy_Spec_S001.md) - 策略模板（30分钟）

### 我要查因子
→ [02_FACTOR_LIBRARY/02_ALPHA_FACTORS_INDEX.md](../02_FACTOR_LIBRARY/02_ALPHA_FACTORS_INDEX.md) - 因子索引（10分钟）

### 我要部署系统
→  - 部署指南（20分钟）

### 我遇到问题
→ [FAQ.md](../02_FACTOR_LIBRARY/FAQ.md) - 常见问题（5分钟）

### 我要审计系统
→ [09_AUDIT/INDEX_AUDIT.md](../09_AUDIT/INDEX_AUDIT.md) - 审计门户（5分钟）


## ⭐ 核心文档（必读）

| 文档 | 用途 | 阅读时间 |
|------|------|----------|
| [BLUEPRINT.md](../02_FACTOR_LIBRARY/04_DATA_SOURCE/02_SCHEDULER/BLUEPRINT.md) | ⭐ 清风量化系统蓝图（合并版） | 30分钟 |
| [01_FRAMEWORK/ARCHITECTURE.md](../01_FRAMEWORK/ARCHITECTURE.md) | Layer 0-8统一架构 | 30分钟 |
| [AI_Permissions.md](../08_AI_GOVERNANCE/AI_Permissions.md) | AI权限清单 | 10分钟 |
| [API_Contract.md](API_Contract.md) | 模块接口契约 | 15分钟 |
| [Strategy_Spec_S001.md](Strategy_Spec_S001.md) | 策略逻辑白皮书 | 30分钟 |
| [BLUEPRINT_CHECKLIST.md](../09_AUDIT/BLUEPRINT_CHECKLIST.md) | 蓝图完整性检查清单 | 20分钟 |

> **说明**: 7个蓝图文档已合并为 ，原始文档归档于 


## 🤖 AI自主量化系统（终极目标）

> 核心: AI判断市场 → AI选择策略 → AI调整风控 → 人仅授权

### 开发规划

| 文档 | 用途 | 索引 |
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
| [CHANGELOG.md](../06_ARCHIVE/CHANGELOG.md) | 版本历史（已合并） |

### 01_FRAMEWORK - 框架定义

| 文档 | 说明 |
|------|------|
| [README.md](../../README.md) | 框架文档索引 |
| [ARCHITECTURE.md](../01_FRAMEWORK/ARCHITECTURE.md) | Layer 0-8统一架构 |
| [MODULE_DESIGN_TEMPLATE.md](../05_IMPLEMENTATION/MODULE_DESIGN_TEMPLATE.md) | 模块设计模板 |
| [MODULE_DESIGN_PLAN.md](../02_FACTOR_LIBRARY/MODULE_DESIGN_PLAN.md) | 模块设计计划 |
| [MARKET_REGIME.md](../01_FRAMEWORK/MARKET_REGIME.md) | 市场状态识别 |
| [HUMAN_AI_FLOW.md](../01_FRAMEWORK/HUMAN_AI_FLOW.md) | 人机协作流程 |
| [TECH_STACK.md](../01_FRAMEWORK/TECH_STACK.md) | 技术栈选择 |

### 02_FACTOR_LIBRARY - 因子库 (v5.0架构)

| 目录/文档 | 说明 |
|------|------|
| [README.md](../../README.md) | 因子库总览 |
|  | 因子分类导航 |
|  | 因子研究方法论 |
| [02_ALPHA_FACTORS_INDEX.md](../02_FACTOR_LIBRARY/02_ALPHA_FACTORS_INDEX.md) | 87个Alpha因子索引 |
|  | 46个风险因子 |
|  | 数据源说明 |
|  | 回测报告 |
|  | 因子注册 |
|  | 监控中心 |

### 03_TRADING_TACTICS - 交易策略

| 目录/文档 | 说明 |
|------|------|
| [README.md](../../README.md) | 策略池总览 |
| [INDEX.md](INDEX.md) | 策略索引 |
|  | 策略框架 |
| [STRATEGY_ENGINE_BLUEPRINT.md](01_STRATEGY_FRAMEWORK/STRATEGY_ENGINE_BLUEPRINT.md) | 策略引擎开发蓝图 |
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
|  | 快速开始（5分钟） |
|  | 开发规范 |
|  | 部署指南 |
|  | 运维手册 |

### 06_ARCHIVE - 归档

| 目录/文档 | 说明 |
|------|------|
| [README.md](../../README.md) | 归档说明 |
|  | v4.0开发文档（精简后2个） |
|  | 过度工程化文档 |

### 07_RESEARCH - AI研究

| 目录/文档 | 说明 |
|------|------|
| [README.md](../../README.md) | 研究总览 |
|  | 研究环境 |
|  | 探索性分析 |
|  | 模式识别 |
|  | 实验追踪 |

### 09_AUDIT - 系统治理审计

| 目录/文档 | 说明 |
|------|------|
| [README.md](../../README.md) | 审计体系总览 |
| [INDEX_AUDIT.md](../09_AUDIT/INDEX_AUDIT.md) | 审计门户首页 |
|  | 审计标准 |
|  | 审计程序 |


## 🔍 按用途查找

### 策略开发者
1. [Strategy_Spec_S001.md](Strategy_Spec_S001.md) - 策略模板
2. [02_FACTOR_LIBRARY/02_ALPHA_FACTORS_INDEX.md](../02_FACTOR_LIBRARY/02_ALPHA_FACTORS_INDEX.md) - 因子库
3. [03_TRADING_TACTICS/](./) - 策略参考
4.  - 开发规范

### 系统构建
1. [BLUEPRINT.md](../02_FACTOR_LIBRARY/04_DATA_SOURCE/02_SCHEDULER/BLUEPRINT.md) - 清风量化系统蓝图
2. [01_FRAMEWORK/ARCHITECTURE.md](../01_FRAMEWORK/ARCHITECTURE.md) - 统一架构
3.  - 快速开始

### 运维
1.  - 部署指南
2.  - 运维手册
3. [FAQ.md](../02_FACTOR_LIBRARY/FAQ.md) - 常见问题

### AI研究
1. [BLUEPRINT.md](../02_FACTOR_LIBRARY/04_DATA_SOURCE/02_SCHEDULER/BLUEPRINT.md) - AI研究框架（见第六章）
2.  - 实验追踪
3. [KNOWLEDGE_MANAGEMENT.md](../02_FACTOR_LIBRARY/KNOWLEDGE_MANAGEMENT.md) - 知识管理

### 系统审计员
1. [09_AUDIT/INDEX_AUDIT.md](../09_AUDIT/INDEX_AUDIT.md) - 审计门户首页
2. [09_AUDIT/STANDARDS/AUDIT_STANDARDS.md](../09_AUDIT/STANDARDS/AUDIT_STANDARDS.md) - 审计标准
3. [09_AUDIT/PROCEDURES/AI_AUDIT_GUIDELINES.md](../09_AUDIT/PROCEDURES/AI_AUDIT_GUIDELINES.md) - AI审计指南


## 📊 文档统计

- **总文档数**: ~80+（精简后）
- **核心文档**: 5个（必读）
- **一级目录**: 8个
- **因子数**: 133个（87 Alpha + 46 Risk）
- **策略数**: 120个（S001-S120）


## 📋 其他重要文档

| 文档 | 说明 | 用途 |
|------|------|------|
| [BLUEPRINT.md](../02_FACTOR_LIBRARY/04_DATA_SOURCE/02_SCHEDULER/BLUEPRINT.md) | 清风量化系统蓝图（合并版） | 完整蓝图参考 |
| [CHANGELOG.md](../06_ARCHIVE/CHANGELOG.md) | 版本变更日志 | 版本控制参考 |
| [VERSIONING.md](../05_IMPLEMENTATION/VERSIONING.md) | 版本管理规范 | 版本控制参考 |
| [CODE_EXAMPLES.md](../05_IMPLEMENTATION/CODE_EXAMPLES.md) | 代码示例 | 开发参考 |
| [HANDOVER.md](../02_FACTOR_LIBRARY/HANDOVER.md) | 交接文档 | 项目交接参考 |
| [EXPERIMENT_TRACKING.md](../07_RESEARCH/EXPERIMENT_TRACKING.md) | 实验追踪 | AI研究参考 |
| [DOCUMENT_AUDIT_v5.1.md](../../DOCUMENT_AUDIT_v5.1.md) | 文档审查报告 | 文档治理参考 |

### 因子库补充文档

| 文档 | 说明 |
|------|------|
| [02_FACTOR_LIBRARY/99_AUDIT_REPORT.md](../02_FACTOR_LIBRARY/99_AUDIT_REPORT.md) | 因子库审计报告 |
| [02_FACTOR_LIBRARY/OPTIMIZATION_SUMMARY.md](../02_FACTOR_LIBRARY/OPTIMIZATION_SUMMARY.md) | 因子优化总结 |

### 交易策略补充文档

| 文档 | 说明 |
|------|------|
| [03_TRADING_TACTICS/OPTIMIZATION_REPORT.md](OPTIMIZATION_REPORT.md) | 策略优化报告 |
| [03_TRADING_TACTICS/REFACTOR_COMPLETE.md](REFACTOR_COMPLETE.md) | 重构完成报告 |


## 📖 完整地图

如需完整文档结构，请查看 [SITEMAP.md](../02_FACTOR_LIBRARY/SITEMAP.md)


**最后更新**: 2026-03-31
**维护者**: 清风量化系统
**版本**: v5.1 个人开发精简版
