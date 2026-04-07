---
module_id: BACKTEST_INDEX_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 因子工程团队
responsibility:
  - 因子计算、因子库管理
  - 因子计算
  - 交易执行
standard_type: 索引文档
applicable_scope: 全系统
compliance_level: 专业标准---



> **核心职责**: 回测目录导航、文档索引和系统管理
> **职责边界**: 
> - ✅ 本文档负责：回测目录导航、文档索引、快速定位
> - ❌ 本文档不负责：具体回测实现、详细设计

## 📂 目录结构

### 子目录

| 目录 | 说明 | 文件数 |
|------|------|--------|
| [value_factors/](01_FRAMEWORK/DATA_LAYER_INDEX.md) | 价值因子回测报告 | 2个 |



### 核心文档

| 文档名称 | 说明 | 重要度 |
|---------|------|--------|
| [因子验证蓝图](./FACTOR_VALIDATION_BLUEPRINT.md) | 因子验证的完整蓝图 | ⭐⭐⭐⭐⭐ |
| [因子衰减测试](./FACTOR_DECAY.md) | 因子IC衰减分析 | ⭐⭐⭐⭐⭐ |
| [分层回测](./LAYERED_BACKTEST.md) | 因子分层回测方法 | ⭐⭐⭐⭐⭐ |
| [过拟合测试](./OVERFITTING_TEST.md) | 过拟合检测和防范 | ⭐⭐⭐⭐ |
| [相关性矩阵](./correlation_matrix.md) | 因子相关性分析 | ⭐⭐⭐⭐ |
| [回测概览](API_README.md) | 回测系统概述 | ⭐⭐⭐ | ⭐⭐�?|

---

## 🔍 快速导�?
### 回测流程

```
因子计算 �?IC测试 �?分层回测 �?相关性分�?�?过拟合测�?�?入库决策
```

### 关键指标

- **IC (Information Coefficient)**: 因子预测能力
- **ICIR (IC Information Ratio)**: IC稳定�?- **分层收益**: Top-Bottom收益�?- **换手�?*: 因子信号换手成本
- **最大回�?*: 策略风险控制

---

## 📊 回测标准

| 指标 | 标准 | 说明 |
|------|------|------|
| IC均�?| > 0.03 | 因子有效�?|
| ICIR | > 0.5 | IC稳定�?|
| IC t�?| > 2.0 | 统计显著�?|
| Top-Bottom收益 | > 10% | 分层效果 |
| 换手�?| < 50% | 交易成本控制 |

---

## 📚 相关文档

- [因子筛选策略](02_FACTOR_LIBRARY/01_STANDARDS/FACTOR_SCREENING_STRATEGY.md)
- [因子验证指南](02_FACTOR_LIBRARY/01_STANDARDS/FACTOR_VALIDATION_GUIDE.md)
- [因子监控](02_FACTOR_LIBRARY/07_FACTOR_MONITORING/factor_monitoring.md)

---

> **最后更�?*: 2026-04-04  
> **维护�?*: 首席文档架构�?
---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
