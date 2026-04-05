---
module_id: INDEX_BACKTEST_001
version: 1.0.1
status: Active
created_date: 2026-04-04
last_updated: 2026-04-04
owner: 首席文档架构�?standard_type: 目录索引
applicable_scope: 因子回测
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 已完�?---

# 因子回测目录索引

> 因子回测的核心索引文件，提供回测方法论、验证流程和过拟合测�?
---

## 📂 目录结构

### 子目录

| 目录 | 说明 | 文件数 |
|------|------|--------|
| [value_factors/](./value_factors/INDEX.md) | 价值因子回测报告 | 2个 |
| [ic_reports/](./ic_reports/README.md) | 因子IC验证报告 | 1个 |
| [strategy_reports/](./strategy_reports/README.md) | 策略回测报告 | 1个 |

### 核心文档

| 文档名称 | 说明 | 重要度 |
|---------|------|--------|
| [因子验证蓝图](./FACTOR_VALIDATION_BLUEPRINT.md) | 因子验证的完整蓝图 | ⭐⭐⭐⭐⭐ |
| [因子衰减测试](./06_FACTOR_DECAY.md) | 因子IC衰减分析 | ⭐⭐⭐⭐⭐ |
| [分层回测](./07_LAYERED_BACKTEST.md) | 因子分层回测方法 | ⭐⭐⭐⭐⭐ |
| [过拟合测试](./09_OVERFITTING_TEST.md) | 过拟合检测和防范 | ⭐⭐⭐⭐ |
| [相关性矩阵](./CORRELATION_MATRIX.md) | 因子相关性分析 | ⭐⭐⭐⭐ |
| [回测概览](./README.md) | 回测系统概述 | ⭐⭐⭐ | ⭐⭐�?|

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

- [因子筛选策略](../01_STANDARDS/FACTOR_SCREENING_STRATEGY.md)
- [因子验证指南](../01_STANDARDS/FACTOR_VALIDATION_GUIDE.md)
- [因子监控](../07_FACTOR_MONITORING/FACTOR_MONITORING.md)

---

> **最后更�?*: 2026-04-04  
> **维护�?*: 首席文档架构�?