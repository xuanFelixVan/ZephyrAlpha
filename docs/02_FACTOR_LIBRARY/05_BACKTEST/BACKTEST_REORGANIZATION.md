---
module_id: 02_FACTOR_LIBRARY_05_BACKTEST_001


---
module_id: BACKTEST_REORGANIZATION_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 因子工程团队
responsibility:
  - 因子研究与管理框架设计与优化维护
standard_type: 通用文档
applicable_scope: 全系统
compliance_level: 专业标准
---

# 05_BACKTEST 目录重组方案
> **核心职责**: 回测目录重组方案和规划，涉及目录重组方案
> **职责边界**: 
> - ✅ 本文档负责：回测目录重组方案和规划相关内容
> - ❌ 本文档不负责：具体实现细节、其他模块内容

> 分离因子IC验证 vs 策略回测报告

## 新目录结?

```
05_BACKTEST/
├── README.md                          # 本文?
├── ic_reports/                        # 因子IC验证报告
?  ├── README.md
?  ├── ALPHA_001-014_趋势类_IC.md
?  ├── ALPHA_015-026_均值回归类_IC.md
?  ├── ALPHA_027-037_value_factors_IC.md
?  ├── ALPHA_038-047_成长类_IC.md
?  ├── ALPHA_048-064_质量类_IC.md
?  ├── PE_TTM_IC.md          # 迁移自此?
?  └── CORRELATION_MATRIX.md         # 迁移自此?
?
└── strategy_reports/                  # 策略回测报告
    ├── README.md
    ├── S001_TREND_FOLLOW/
    ?  ├── backtest_20260328.md
    ?  ├── performance_metrics.md
    ?  └── equity_curve.png
    ├── S002_MEAN_REVERSION/
    ?  ├── backtest_20260328.md
    ?  └── performance_metrics.md
    └── ...
```

## 迁移计划

### 第一步：创建新目录结?

```bash
# 创建IC报告目录
mkdir ic_reports/
mkdir strategy_reports/

# 创建README文件
touch ic_reports/README.md
touch strategy_reports/README.md
```

### 第二步：迁移因子IC报告

**源文?*:
- `05_BACKTEST/value_factors/PE_TTM_IC.md` ?`ic_reports/PE_TTM_IC.md`
- `05_BACKTEST/CORRELATION_MATRIX.md` ?`ic_reports/CORRELATION_MATRIX.md`

**新增文件**:
- `ic_reports/ALPHA_001-014_趋势类_IC.md`
- `ic_reports/ALPHA_015-026_均值回归类_IC.md`
- `ic_reports/ALPHA_027-037_value_factors_IC.md`
- `ic_reports/ALPHA_038-047_成长类_IC.md`
- `ic_reports/ALPHA_048-064_质量类_IC.md`

### 第三步：创建策略回测报告目录

**新增目录**:
- `strategy_reports/S001_TREND_FOLLOW/`
- `strategy_reports/S002_MEAN_REVERSION/`
- `strategy_reports/S003_VALUE_INVESTING/`
- ...

## 文件说明

### ic_reports/ - 因子IC验证报告

**用?*: 验证单个因子的预测能?

**文件命名**: `{因子ID范围}_{因子类型}_IC.md`

**内容**:
- 因子列表
- IC值统?
- IC分布?
- 相关性分?
- 结论

**示例**: `ALPHA_001-014_趋势类_IC.md`

### strategy_reports/ - 策略回测报告

**用?*: 验证完整策略的交易表?

**文件命名**: `S{策略ID}_{策略名称}/backtest_{日期}.md`

**内容**:
- 策略说明
- 回测参数
- 性能指标（夏普比、最大回撤等?
- 权益曲线
- 交易统计

**示例**: `S001_TREND_FOLLOW/backtest_20260328.md`

## 关键区别

| 维度 | IC报告 | 策略回测 |
|------|--------|---------|
| **对象** | 单个因子 | 完整策略 |
| **目的** | 验证因子预测能力 | 验证策略交易表现 |
| **指标** | IC值、相关?| 夏普比、最大回撤、胜?|
| **频率** | 因子更新时验?| 策略运行后验?|
| **位置** | `ic_reports/` | `strategy_reports/` |

## 迁移检查清?

- [ ] 创建 `ic_reports/` 目录
- [ ] 创建 `strategy_reports/` 目录
- [ ] 迁移 `PE_TTM_IC.md` ?`ic_reports/`
- [ ] 迁移 `CORRELATION_MATRIX.md` ?`ic_reports/`
- [ ] 创建 `ic_reports/README.md`
- [ ] 创建 `strategy_reports/README.md`
- [ ] 更新 `02_FACTOR_LIBRARY/00_INDEX/README.md`
- [ ] 更新 `System_Manifest.md`
- [ ] 更新 `CHANGELOG.md`

**版本**: 1.0 | **更新**: 2026-03-28
