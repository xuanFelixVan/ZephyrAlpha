---
module_id: DOC_FACTOR_LIBRARY_INDEX_001
version: 1.0.0
status: Active
created_date: 2026-04-03
last_updated: 2026-04-03
owner: 因子库架构师
standard_type: 专业量化机构目录索引
applicable_scope: 02_FACTOR_LIBRARY目录
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 活跃维护
---

# 因子库目录索引

> **版本**: v5.1  
> **架构**: 三级时间框架融合架构  
> **最后更新**: 2026-04-03  
> **维护者**: 因子库架构师

---

## 🎯 目录职责

本目录存放因子库相关文档，包括因子方法论、因子计算、因子回测、数据源接口等。

---

## 📚 核心文档

### 系统清单

| 文档名称 | 说明 | 重要性 |
|---------|------|--------|
| [系统清单](../System_Manifest.md) | 系统清单（全局） | ⭐⭐⭐⭐⭐ |
| [README](./README.md) | 因子库概述 | ⭐⭐⭐⭐⭐ |
| [SITEMAP](./SITEMAP.md) | 因子库文档地图 | ⭐⭐⭐⭐ |

### 因子方法论

| 文档名称 | 说明 | 重要性 |
|---------|------|--------|
| [因子注册表](./01_METHODOLOGY/FACTOR_REGISTRY.md) | 因子注册表 | ⭐⭐⭐⭐⭐ |
| [因子计算框架](./01_METHODOLOGY/FACTOR_CALCULATION_FRAMEWORK.md) | 因子计算框架 | ⭐⭐⭐⭐⭐ |
| [因子管理标准](./01_METHODOLOGY/FACTOR_MANAGEMENT_STANDARD.md) | 因子管理标准（含筛选策略） | ⭐⭐⭐⭐ |

### Alpha因子

| 文档名称 | 说明 | 重要性 |
|---------|------|--------|
| [Alpha因子索引](./02_ALPHA_FACTORS_INDEX.md) | Alpha因子索引 | ⭐⭐⭐⭐⭐ |
| [技术指标](./01_METHODOLOGY/TECHNICAL_INDICATORS.md) | 技术指标因子 | ⭐⭐⭐⭐ |

### 风险因子

| 文档名称 | 说明 | 重要性 |
|---------|------|--------|
| [Barra风格因子](./03_RISK_FACTORS/T.03.RF001.barra_style_factors.md) | Barra风格因子 | ⭐⭐⭐⭐ |
| [行业因子](./03_RISK_FACTORS/T.03.RF002.industry_factors.md) | 行业因子 | ⭐⭐⭐⭐ |
| [尾部风险因子](./03_RISK_FACTORS/T.03.RF003.tail_risk_factors.md) | 尾部风险因子 | ⭐⭐⭐⭐ |

### 数据源

| 文档名称 | 说明 | 重要性 |
|---------|------|--------|
| [数据源概述](./04_DATA_SOURCE/README.md) | 数据源概述 | ⭐⭐⭐⭐⭐ |
| [QMT接口](./04_DATA_SOURCE/QMT_INTERFACE.md) | QMT数据接口 | ⭐⭐⭐⭐ |
| [iFind连接器](./04_DATA_SOURCE/IFIND_CONNECTOR.md) | iFind数据接口 | ⭐⭐⭐⭐ |
| [Baostock连接器](./04_DATA_SOURCE/BAOSTOCK_CONNECTOR.md) | Baostock数据接口 | ⭐⭐⭐⭐ |

### 因子回测

| 文档名称 | 说明 | 重要性 |
|---------|------|--------|
| [回测概述](./05_BACKTEST/README.md) | 回测概述 | ⭐⭐⭐⭐⭐ |
| [因子验证蓝图](./05_BACKTEST/FACTOR_VALIDATION_BLUEPRINT.md) | 因子验证蓝图 | ⭐⭐⭐⭐ |
| [IC分析](./01_METHODOLOGY/ic_analysis.md) | IC分析方法 | ⭐⭐⭐⭐ |

---

## 🗂️ 子目录

| 目录名称 | 说明 | 文档数量 |
|---------|------|---------|
| [00_GOVERNANCE/](./00_GOVERNANCE/) | 治理文档 | 1 |
| [00_INDEX/](./00_INDEX/) | 索引文档 | 3 |
| [01_METHODOLOGY/](./01_METHODOLOGY/) | 方法论文档 | 13 |
| [03_RISK_FACTORS/](./03_RISK_FACTORS/) | 风险因子 | 5 |
| [04_DATA_SOURCE/](./04_DATA_SOURCE/) | 数据源 | 15+ |
| [05_BACKTEST/](./05_BACKTEST/) | 回测文档 | 10+ |
| [06_FACTOR_REGISTRY/](./06_FACTOR_REGISTRY/) | 因子注册 | 1 |
| [07_FACTOR_MONITORING/](./07_FACTOR_MONITORING/) | 因子监控 | 2 |
| [10_MANUAL/](./10_MANUAL/) | 手册文档 | 1 |

---

## 📖 快速导航

### 新手入门

1. 阅读 [README.md](./README.md) - 因子库概述
2. 阅读 [系统清单](../System_Manifest.md) - 系统清单（全局）
3. 阅读 [因子分类学](./01_METHODOLOGY/FACTOR_REGISTRY.md) - 因子分类体系

### 因子开发

1. 阅读 [01_METHODOLOGY/FACTOR_CALCULATION_FRAMEWORK.md](./01_METHODOLOGY/FACTOR_CALCULATION_FRAMEWORK.md) - 因子计算框架
2. 阅读 [05_BACKTEST/FACTOR_VALIDATION_BLUEPRINT.md](./05_BACKTEST/FACTOR_VALIDATION_BLUEPRINT.md) - 因子验证
3. 阅读 [01_METHODOLOGY/ic_analysis.md](./01_METHODOLOGY/ic_analysis.md) - IC分析

---

## 🔗 相关链接

- [系统主索引](../INDEX.md)
- [框架设计索引](../01_FRAMEWORK/INDEX.md)
- [实施层索引](../05_IMPLEMENTATION/README.md)
