---
module_id: INDEX_EXECUTION_001
version: 1.0.1
status: Active
created_date: 2026-04-03
last_updated: 2026-04-04
owner: 执行层架构师
responsibility:
  - 索引文档、导航目录
  - 交易执行
  - 机器学习
standard_type: 专业量化机构目录索引
applicable_scope: 04_EXECUTION目录
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 活跃维护---


# 执行层目录索引

> **版本**: v5.3  
> **架构**: 三级时间框架融合架构  
> **最后更新**: 2026-04-07  
> **维护者**: 执行层架构师

---

## 📋 文档职责说明

### 核心职责

本文档是**执行层的导航索引文档**，负责：
- 提供执行层的快速导航
- 说明执行层的目录结构
- 推荐执行层文档的阅读路径
- 为执行层文档查找提供导航服务

### 职责边界

**负责**：
- ✅ 提供执行层的快速导航入口
- ✅ 提供执行层文档的分类和层级说明
- ✅ 推荐执行层文档的阅读路径
- ✅ 说明执行层的文档体系架构

**不负责**：
- ❌ 完整的模块清单（由System_Manifest.md负责）
- ❌ 详细的实施状态跟踪（由System_Manifest.md负责）
- ❌ 版本管理和变更历史（由System_Manifest.md负责）

### 对接文档

**相关文档**：
- [../INDEX.md](../INDEX.md) - 系统导航入口（快速导航和文档分类）
- [../System_Manifest.md](../System_Manifest.md) - 系统清单账本（完整模块清单和实施状态）

---

## 🎯 目录职责

本目录存放执行层相关文档，包括事件引擎、交易执行、监控、风险引擎、模拟和实盘等。

> **版本**: v5.3  
> **架构**: 三级时间框架融合架构  
> **最后更�?*: 2026-04-03  
> **维护�?*: 执行层架构师

---

## 🎯 目录职责

本目录存放执行层相关文档，包括事件引擎、交易执行、监控、风险引擎、模拟和实盘等�?
---

## 📚 核心文档

### 系统概述

| 文档名称 | 说明 | 重要�?|
|---------|------|--------|
| [README](API_README.md) | 执行层概�?| ⭐⭐⭐⭐�?|
| [信号生成](./signal_generation.md) | 信号生成机制 | ⭐⭐⭐⭐ |

### 事件引擎

| 文档名称 | 说明 | 重要�?|
|---------|------|--------|
| [事件总线](./01_EVENT_ENGINE/EVENT_BUS.md) | 事件总线设计 | ⭐⭐⭐⭐�?|
| [事件引擎概述](API_README.md) | 事件引擎概述 | ⭐⭐⭐⭐ |

### 订单执行

| 文档名称 | 说明 | 重要�?|
|---------|------|--------|
| [订单执行蓝图](./01_ORDER_EXECUTION/ORDER_EXECUTION_BLUEPRINT.md) | 订单执行蓝图 | ⭐⭐⭐⭐�?|
| [QMT执行器蓝图](./01_ORDER_EXECUTION/QMT_EXECUTOR_BLUEPRINT.md) | QMT执行器蓝�?| ⭐⭐⭐⭐�?|
| [订单生成算法](./01_ORDER_EXECUTION/ORDER_GENERATION_ALGORITHMS.md) | TWAP/VWAP/冲击成本模型 | ⭐⭐⭐⭐�?|

### 交易执行�?
| 文档名称 | 说明 | 重要�?|
|---------|------|--------|


### 监控系统

| 文档名称 | 说明 | 重要�?|
|---------|------|--------|
| [监控蓝图](01_FRAMEWORK/ACCEPTANCE_CRITERIA_BLUEPRINT.md) | 监控系统蓝图 | ⭐⭐⭐⭐�?|
| [健康监控](./03_MONITORING/HEALTH_MONITORING.md) | 健康监控 | ⭐⭐⭐⭐ |
| [实时监控](./03_MONITORING/REAL_TIME_MONITORING.md) | 实时监控 | ⭐⭐⭐⭐ |
| [绩效归因](./03_MONITORING/PERFORMANCE_ATTRIBUTION.md) | 绩效归因 | ⭐⭐⭐⭐ |

### AI委员�?
| 文档名称 | 说明 | 重要�?|
|---------|------|--------|


### 风险引擎

| 文档名称 | 说明 | 重要�?|
|---------|------|--------|


### 模拟系统

| 文档名称 | 说明 | 重要�?|
|---------|------|--------|
| [模拟蓝图](01_FRAMEWORK/ACCEPTANCE_CRITERIA_BLUEPRINT.md) | 模拟系统蓝图 | ⭐⭐⭐⭐�?|
| [多引擎蓝图](./06_SIMULATION/MULTI_ENGINE_BLUEPRINT.md) | 多引擎蓝�?| ⭐⭐⭐⭐ |

### 实盘系统

| 文档名称 | 说明 | 重要�?|
|---------|------|--------|
| [实盘流概述](./07_LIVE_STREAM/README_RTX3090.md) | 实盘流概�?| ⭐⭐⭐⭐ |
| [实盘财务分析蓝图](./07_LIVE_STREAM/LIVE_STREAM_FINANCIAL_ANALYSIS_BLUEPRINT.md) | 实盘财务分析蓝图 | ⭐⭐⭐⭐ |

---

## 🗂�?子目�?
| 目录名称 | 说明 | 文档数量 |
|---------|------|---------|
| [01_EVENT_ENGINE/](./01_EVENT_ENGINE/) | 事件引擎 | 2 |
| [01_ORDER_EXECUTION/](./01_ORDER_EXECUTION/) | 订单执行 | 3 |
| [02_TRADE_EXECUTOR/](./02_TRADE_EXECUTOR/) | 交易执行�?| 1 |
| [03_MONITORING/](./03_MONITORING/) | 监控系统 | 6 |


| [06_SIMULATION/](./06_SIMULATION/) | 模拟系统 | 3 |
| [07_LIVE_STREAM/](./07_LIVE_STREAM/) | 实盘系统 | 10+ |

---

## 📖 快速导�?
### 新手入门

1. 阅读 [README.md](API_README.md) - 执行层概�?2. 阅读 [01_EVENT_ENGINE/EVENT_BUS.md](./01_EVENT_ENGINE/EVENT_BUS.md) - 事件总线
3. 阅读 [03_MONITORING/BLUEPRINT.md](01_FRAMEWORK/ACCEPTANCE_CRITERIA_BLUEPRINT.md) - 监控系统

### 开发者
1. 阅读 [01_ORDER_EXECUTION/ORDER_EXECUTION_BLUEPRINT.md](./01_ORDER_EXECUTION/ORDER_EXECUTION_BLUEPRINT.md) - 订单执行
2. 阅读 [06_SIMULATION/BLUEPRINT.md](01_FRAMEWORK/ACCEPTANCE_CRITERIA_BLUEPRINT.md) - 模拟系统

---

## 🔗 相关链接

- [系统主索引](../INDEX.md)
- [框架设计索引](../01_FRAMEWORK/INDEX.md)
- [交易战术索引](../03_TRADING_TACTICS/INDEX.md)

- [交易成本分析 (TCA)](./tca.md) - 系统文档
