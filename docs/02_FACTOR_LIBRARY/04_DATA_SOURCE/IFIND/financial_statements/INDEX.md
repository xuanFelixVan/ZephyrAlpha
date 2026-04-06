---
module_id: FACTOR_IFIND财务数据_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 因子工程团队
standard_type: 索引文档
applicable_scope: 全系统
compliance_level: 专业标准
---

﻿---
module_id: DATA_IFIND_FINSTMT_INDEX_001
version: 1.0.0
status: Active
created_date: 2026-04-04
last_updated: 2026-04-04
owner: 首席文档架构师
standard_type: 目录索引文档
applicable_scope: iFind财务数据
compliance_level: 专业标准
parent_document: ../../INDEX.md
---

# iFind财务数据

## 文档职责说明

**本文档职责**: iFind财务数据模块索引
- 提供财务数据模块的目录导航
- 说明财务数据指标体系
- 管理财务数据API和指标清单文档

**相关文档引用**:
| 文档 | 路径 | 关系 | 说明 |
|------|------|------|------|
| iFind索引 | [../INDEX.md](../INDEX.md) | 上级索引 | iFind数据源总索引 |
| 财务API | [FINANCIAL_STATEMENTS_API.md](./FINANCIAL_STATEMENTS_API.md) | 详细文档 | 财务数据API参考 |

**职责边界**:
- ✅ 本文档负责: 财务数据模块索引和导航
- ❌ 本文档不负责: API详细说明（由 FINANCIAL_STATEMENTS_API.md 负责）

> 清风量化系统 - 同花顺iFind财务数据集成
> **核心定位**: 提供完整的财务数据指标体系，支持基本面因子研究

---

## 📁 目录结构

| 文件 | 职责 | 状态 |
|------|------|------|
| [THS_BD_COMPLETE_INDICATOR_LIST.md](THS_BD_COMPLETE_INDICATOR_LIST.md) | iFind THS_BD完整指标清单 | Active |
| [FINANCIAL_STATEMENTS_API.md](FINANCIAL_STATEMENTS_API.md) | 财务数据API参考文档 | Active |

---

## 📖 核心功能

### 1. 财务数据指标体系
- **季频指标**: 183个，季度财务报表数据
- **年频指标**: 760个，年度财务数据
- **合计**: 943个财务指标

### 2. 指标分类管理
- 利润表相关（59个）
- 资产负债表相关（126个）
- 现金流量表相关（50个）
- 股东权益相关（31个）
- 高管信息相关（55个）
- 股份变动相关（78个）
- 行业分类相关（26个）
- 上市发行相关（21个）
- 员工信息相关（66个）
- 处罚诉讼相关（9个）

### 3. 数据获取接口
- THS_BD函数调用
- 支持批量数据获取
- 自动数据格式转换

### 4. 数据质量控制
- 数据完整性检查
- 数据有效性验证
- 异常数据处理

---

## 🔗 相关文档

### 上层文档
- [iFind数据源](../INDEX.md) - iFind数据源总览
- [数据源层索引](../../INDEX.md) - 数据源层总览

### 相关模块
- [iFind连接器](../../IFIND_CONNECTOR.md) - iFind数据源接入
- [宏观数据](../../MACRO_DATA.md) - 宏观经济数据
- [数据源适配器](../../DATA_SOURCE_ADAPTERS.md) - 数据源管理

---

## 📊 指标统计总览

| 类别 | 数量 | 说明 |
|------|------|------|
| **季频指标** | 183 | ths_sq_开头，季度财务报表 |
| **年频指标** | 760 | 非ths_sq_开头 |
| 利润表相关 | 59 | 营收/成本/利润/所得税 |
| 资产负债表相关 | 126 | 资产/负债/所有者权益 |
| 现金流量表相关 | 50 | 经营/投资/筹资现金流 |
| 股东权益相关 | 31 | 股东/股权 |
| 高管信息相关 | 55 | 董监高薪酬/持股 |
| 股份变动相关 | 78 | 限售/质押/浮动 |
| 行业分类相关 | 26 | 申万/证监会/同花顺行业 |
| 上市发行相关 | 21 | IPO/配股/增发 |
| 员工信息相关 | 66 | 员工数量/教育程度 |
| 处罚诉讼相关 | 9 | 违规/诉讼 |
| 其他指标 | 239 | 未分类 |
| **合计** | **943** | |

---

## 🎯 数据特点

| 特点 | 说明 |
|------|------|
| **全面性** | 覆盖943个财务指标 |
| **标准化** | 统一的指标命名规范 |
| **时效性** | 支持季频和年频数据 |
| **可靠性** | 同花顺官方数据源 |

---

## 📅 扩展计划

### Phase 1（当前）
- ✅ iFind THS_BD完整指标清单

### Phase 2（计划中）
- 🟡 FINANCIAL_STATEMENTS_API.md - 财务数据API文档
- 🟡 FINANCIAL_STATEMENTS_MODELS.md - 财务数据模型

### Phase 3（未来）
- 🟢 FINANCIAL_STATEMENTS_EXAMPLES.md - 财务数据使用示例
- 🟢 FINANCIAL_STATEMENTS_BEST_PRACTICES.md - 财务数据最佳实践

---

**索引版本**: v1.0.0 | **创建日期**: 2026-04-04 | **维护者**: 首席文档架构师

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
