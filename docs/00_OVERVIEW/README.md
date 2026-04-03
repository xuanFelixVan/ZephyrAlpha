---
module_id: OVERVIEW_README_001
version: 5.1.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构师
standard_type: 专业量化机构文档
applicable_scope: 全系统
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 进行中
---

# 清风量化交易系统 v5.1 - 系统总览

> **版本**：v5.1
> **更新日期**：2026-03-31
> **状态**：已完成

---

## 1. 系统简介

清风量化交易系统是一套面向A股市场的专业级多策略量化交易平台，采用**Layer 0-8分层架构**，支持30-50种策略的动态管理和市场状态自适应。

### 1.1 系统特点

| 特点 | 说明 |
|------|------|
| 专业架构 | 采用专业量化机构标准分层设计 |
| 个人适配 | 适配单人开发、维护、使用场景 |
| 模块化设计 | 15个核心模块，可独立测试和替换 |
| AI辅助 | 支持AI因子挖掘、参数优化、自我迭代 |

---

## 2. 快速导航（Quick Access）

### 2.1 核心文档

| 类型 | 文档 | 说明 |
|------|------|------|
| **主入口** | [INDEX.md](../03_TRADING_TACTICS/INDEX.md) | 文档索引入口 |
| **架构** | [BLUEPRINT.md](../02_FACTOR_LIBRARY/04_DATA_SOURCE/02_SCHEDULER/BLUEPRINT.md) | 系统蓝图 |
| **版本** | [CHANGELOG.md](../06_ARCHIVE/CHANGELOG.md) | 版本变更日志 |

### 2.2 主要模块

| 目录 | 说明 |
|------|------|
| [01_FRAMEWORK/](../01_FRAMEWORK/) | 核心框架（Layer 0-8战术实现） |
| [02_FACTOR_LIBRARY/](../02_FACTOR_LIBRARY/) | 因子库（87 Alpha + 46 Risk） |
| [03_TRADING_TACTICS/](../03_TRADING_TACTICS/) | 交易策略池（S001-S120） |
| [04_EXECUTION/](../04_EXECUTION/) | 执行引擎 |
| [05_IMPLEMENTATION/](../05_IMPLEMENTATION/) | 实施指南 |

---

## 3. Layer 0-8 分层架构（概览）

| Layer | 名称 | 功能 |
|-------|------|------|
| Layer 0 | 数据层 | 数据采集、清洗、存储 |
| Layer 1 | 数据预处理层 | 市场状态识别、信号预处理 |
| Layer 2 | Alpha因子层 | Alpha因子生成、预测 |
| Layer 3 | 舆情分析层 | 新闻/情感/事件分析 |
| Layer 4 | 机器学习层 | ML Pipeline |
| Layer 5 | 策略执行层 | 订单生成、路由、执行 |
| Layer 6 | 组合优化层 | 组合优化、权重分配 |
| Layer 7 | AI报告层 | 绩效归因、分析 |
| Layer 8 | 人机交互层 | 授权、监控、报告 |

> 详见：[01_FRAMEWORK/](../01_FRAMEWORK/) 中的战术实现文档

---

## 4. 开发阶段

| 阶段 | 目标 | 状态 |
|------|------|------|
| **阶段1** | 基础框架搭建 | ✅ 完成 |
| **阶段2** | 核心模块实现 | 🔴 进行中 |
| **阶段3** | 支撑系统实现 | 🔴 未开始 |
| **阶段4** | 集成测试 | 🔴 未开始 |
| **阶段5** | 生产部署 | 🔴 未开始 |

---

## 5. 相关文档索引

| 文档 | 说明 |
|------|------|
| [INDEX.md](../03_TRADING_TACTICS/INDEX.md) | 文档索引入口 |
| [SITEMAP.md](../02_FACTOR_LIBRARY/SITEMAP.md) | 完整文档地图 |
| [BLUEPRINT.md](../02_FACTOR_LIBRARY/04_DATA_SOURCE/02_SCHEDULER/BLUEPRINT.md) | 系统蓝图 |
| [CHANGELOG.md](../06_ARCHIVE/CHANGELOG.md) | 变更日志 |

---

## 6. 代码项目

| 目录 | 说明 |
|------|------|
|  | 源代码 |
|  | 测试 |
|  | 配置 |

---

*最后更新：2026-03-31*
