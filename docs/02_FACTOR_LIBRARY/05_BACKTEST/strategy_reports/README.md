---
module_id: FACTOR_STRATEGY_REPORTS_001_L02_README
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 因子工程团队
responsibility:
  - 因子计算
  - 交易执行
  - 回测系统
standard_type: 说明文档
applicable_scope: 全系统
compliance_level: 专业标准---




# strategy_reports/ - 策略回测报告

> 完整策略交易表现验证报告集中管理


## 目录说明

本目录存�?*策略回测报告**，用于评估完整策略的交易表现�?


## 目录结构

```
strategy_reports/
├── README.md                    # 本文�?
├── S001_TREND_FOLLOW/          # 均线趋势跟踪策略
�?  ├── backtest_20260328.md
�?  ├── performance_metrics.md
�?  └── equity_curve.png
├── S002_MEAN_REVERSION/        # 均值回归策�?
�?  ├── backtest_20260328.md
�?  └── performance_metrics.md
└── ...
```


## 报告模板

### backtest_{日期}.md

```markdown
# {策略名称} 回测报告

## 策略说明
[策略逻辑]

## 回测参数
- 回测周期: 2023-01-01 ~ 2026-03-28
- 初始资金: 100�?
- 手续�? 0.001

## 性能指标
| 指标 | �?|
| 年化收益 | 15% |
| 夏普�?| 1.8 |
| 最大回�?| 12% |

## 权益曲线
[图表]

## 交易统计
[统计数据]
```


## 相关文档

| 文档 | 说明 |
|------|------|
| [../../Strategy_Spec_S001.md](../../../03_TRADING_TACTICS/Strategy_Spec_S001.md) | 策略逻辑定义 |
| [../01_STANDARDS/BACKTEST_STANDARDS.md](../../01_STANDARDS/BACKTEST_STANDARDS.md) | 回测标准 |


**版本**: 1.0 | **更新**: 2026-03-28

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
