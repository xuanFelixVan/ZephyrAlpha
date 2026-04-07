---
module_id: DATA_IFIND_MAIN_INDEX_001
version: 1.0.0
status: Active
created_date: 2026-04-04
last_updated: 2026-04-04
owner: 首席文档架构师
standard_type: 目录索引文档
applicable_scope: iFind数据源
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 已完成
responsibility: iFind数据源模块导航
---
---

# iFind数据源

> **核心职责**: iFind数据源的定义和实现
> **职责边界**: 
> - ✅ 本文档负责：目录导航和文档索引相关内容
> - ❌ 本文档不负责：其他模块内容


## 文档职责说明

**本文档职责**: iFind数据源模块索引
- 提供iFind数据源的目录导航
- 说明因子数据和财务数据结构
- 管理因子主索引和财务报表文档

**相关文档引用**:
| 文档 | 路径 | 关系 | 说明 |
|------|------|------|------|

| 数据源索引 | [../INDEX.md](../INDEX.md) | 上级索引 | 数据源模块总索引 |

**职责边界**:
- ✅ 本文档负责: iFind数据源模块索引和导航
- ❌ 本文档不负责: 因子验证细节（由 FACTOR_MASTER_INDEX.md 负责）

> 清风量化系统 - 同花顺iFind数据源集成
> **核心定位**: 提供专业的金融数据接口，支持行情、财务、因子等多维度数据

---

## 📁 目录结构

| 文件/目录 | 职责 | 状态 |
|-----------|------|------|

| [financial_statements/](financial_statements/) | 财务数据 | Active |
| factor_list.csv | 因子列表数据 | Active |
| factor_master_index.csv | 因子主索引数据 | Active |

---

## 📖 核心功能

### 1. 因子数据

- **因子主索引**: 追踪每个因子的IC验证、回测报告、版本历史
- **因子列表**: 提供完整的因子清单和分类
- **因子数据**: 支持多维度因子数据获取

### 2. 财务数据

- **财务报表**: 季频和年频财务指标
- **指标清单**: 完整的财务指标列表（943个指标）
- **数据质量**: 自动化数据质量检查

### 3. 行情数据

- **实时行情**: 支持实时行情数据获取
- **历史数据**: 完整的历史行情数据
- **复权处理**: 自动复权计算

---

## 🔗 快速导航

### 数据源连接器

- [IFIND_CONNECTOR.md](../IFIND_CONNECTOR.md) - iFind数据源接口文档

### 财务数据

- [financial_statements/INDEX.md](financial_statements/INDEX.md) - 财务数据索引
- [financial_statements/THS_BD_COMPLETE_INDICATOR_LIST.md](financial_statements/THS_BD_COMPLETE_INDICATOR_LIST.md) - 完整指标清单

### 因子数据



---

## 📊 数据统计

| 数据类型 | 数量 | 说明 |
|----------|------|------|
| **季频指标** | 183 | ths_sq_开头，季度财务报表 |
| **年频指标** | 760 | 非ths_sq_开头 |
| **合计** | **943** | 完整财务指标体系 |

---

## 🚀 使用指南

### 1. 连接iFind

```python
from zephyr.data.sources.ifind import IFindConnector

# 创建连接器
connector = IFindConnector()

# 测试连接
if connector.test_connection():
    print("✅ iFind连接成功")
```

### 2. 获取行情数据

```python
# 获取日线数据
df = connector.get_daily_data(
    symbols=['000001.SZ', '000002.SZ'],
    start_date='2024-01-01',
    end_date='2024-12-31'
)
```

### 3. 获取财务数据

```python
# 获取财务指标
df = connector.get_financial_data(
    symbols=['000001.SZ'],
    indicators=['ths_roe_stock', 'ths_net_profit_margin'],
    start_date='2024-01-01'
)
```

---

## 📅 扩展计划

### Phase 1（当前）

- ✅ 因子主索引
- ✅ 财务数据索引
- ✅ 完整指标清单

### Phase 2（计划中）

- 🟡 IFIND_API.md - API详细文档
- 🟡 IFIND_DATA_MODELS.md - 数据模型文档

---

## ⚠️ 注意事项

1. **权限要求**: 需要有效的iFind账号和API权限
2. **速率限制**: 遵守iFind API的速率限制
3. **数据更新**: 定期检查数据更新和指标变更
4. **成本控制**: 监控API调用次数，控制成本

---

**索引版本**: v1.0.0 | **创建日期**: 2026-04-04 | **维护者**: 首席文档架构师

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
