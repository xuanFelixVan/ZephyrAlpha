---
module_id: INDEX
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
---

﻿---
module_id: VALUE_FACTORS_INDEX_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 因子工程团队
responsibility:
  - 目录导航与文档索引管理与优化维护
standard_type: 索引文档
applicable_scope: 全系统
compliance_level: 专业标准---



# value_factors - 价值因子回测报告
> **核心职责**: value_factors - 价值因子回测报告的定义和实现
> **职责边界**: 
> - ✅ 本文档负责：目录结构导航、文档索引、快速定位
> - ❌ 本文档不负责：具体内容实现、详细设计


> 价值类因子的IC验证和回测报告集中管理

---

## 📂 目录说明

本目录存放价值类因子的回测报告，包括：
- IC验证记录
- 单因子回测报告
- 多因子组合回测报告

---

## 📄 文档列表

### PE_TTM因子

| 文档 | 说明 | 状态 |
|------|------|------|
| [PE_TTM_IC.md](./PE_TTM_IC.md) | PE_TTM因子IC验证记录 | ✅ 已通过 |
| [PE_TTM_BACKTEST.md](./PE_TTM_BACKTEST.md) | PE_TTM单因子回测报告 | ✅ 已通过 |

---

## 📊 因子概览

### PE_TTM (市盈率TTM)

| 项目 | 内容 |
|------|------|
| **因子名称** | PE_TTM |
| **THS代码** | ths_pe_ttm_stock |
| **数据频率** | 日频 |
| **因子类型** | 价值因子 |
| **验证状态** | ✅ 已通过 |
| **回测状态** | ✅ 已通过 |

---

## 🔍 使用指南

### 查看因子验证结果

1. 阅读 [PE_TTM_IC.md](./PE_TTM_IC.md) - 了解因子的IC表现
2. 阅读 [PE_TTM_BACKTEST.md](./PE_TTM_BACKTEST.md) - 了解因子的回测表现

### 添加新的价值因子报告

1. 创建 `{因子名}_IC.md` 文件，记录IC验证结果
2. 创建 `{因子名}_BACKTEST.md` 文件，记录回测结果
3. 更新本INDEX.md文件，添加新因子的索引

---

## 📈 统计信息

| 指标 | 数值 |
|------|------|
| **因子数量** | 1个 |
| **IC验证报告** | 1个 |
| **回测报告** | 1个 |
| **通过率** | 100% |

---

## 🔗 相关链接

- [回测报告总目录](../INDEX.md)
- [因子库总览](API_README.md)
- [因子分类体系](02_FACTOR_LIBRARY/01_STANDARDS/FACTOR_TAXONOMY.md)

---

> **最后更新**: 2026-04-04  
> **维护者**: 首席文档架构师

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
