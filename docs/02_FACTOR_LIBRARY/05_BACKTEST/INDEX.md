---
module_id: INDEX_BACKTEST_001
version: 1.0.1
status: Active
created_date: 2026-04-04
last_updated: 2026-04-04
owner: 首席文档架构师
standard_type: 目录索引
applicable_scope: 因子回测
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 已完成
---

# 因子回测目录索引

> 因子回测的核心索引文件，提供回测方法论、验证流程和过拟合测试

---

## 📂 目录结构

### 核心文档

| 文档名称 | 说明 | 重要度 |
|---------|------|--------|
| [因子验证蓝图](./FACTOR_VALIDATION_BLUEPRINT.md) | 因子验证的完整蓝图 | ⭐⭐⭐⭐⭐ |
| [因子衰减测试](./06_FACTOR_DECAY.md) | 因子IC衰减分析 | ⭐⭐⭐⭐⭐ |
| [分层回测](./07_LAYERED_BACKTEST.md) | 因子分层回测方法 | ⭐⭐⭐⭐⭐ |
| [过拟合测试](./09_OVERFITTING_TEST.md) | 过拟合检测和防范 | ⭐⭐⭐⭐ |
| [相关性矩阵](./CORRELATION_MATRIX.md) | 因子相关性分析 | ⭐⭐⭐⭐ |
| [回测概览](./README.md) | 回测系统概述 | ⭐⭐⭐ |

---

## 🔍 快速导航

### 回测流程

```
因子计算 → IC测试 → 分层回测 → 相关性分析 → 过拟合测试 → 入库决策
```

### 关键指标

- **IC (Information Coefficient)**: 因子预测能力
- **ICIR (IC Information Ratio)**: IC稳定性
- **分层收益**: Top-Bottom收益差
- **换手率**: 因子信号换手成本
- **最大回撤**: 策略风险控制

---

## 📊 回测标准

| 指标 | 标准 | 说明 |
|------|------|------|
| IC均值 | > 0.03 | 因子有效性 |
| ICIR | > 0.5 | IC稳定性 |
| IC t值 | > 2.0 | 统计显著性 |
| Top-Bottom收益 | > 10% | 分层效果 |
| 换手率 | < 50% | 交易成本控制 |

---

## 📚 相关文档

- [因子筛选策略](../01_STANDARDS/FACTOR_SCREENING_STRATEGY.md)
- [因子验证指南](../01_STANDARDS/FACTOR_VALIDATION_GUIDE.md)
- [因子监控](../07_FACTOR_MONITORING/FACTOR_MONITORING.md)

---

> **最后更新**: 2026-04-04  
> **维护者**: 首席文档架构师
