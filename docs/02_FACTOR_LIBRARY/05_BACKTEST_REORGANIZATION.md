---
module_id: BACKTEST_STRUCTURE
version: 1.0
status: Active
last_updated: 2026-03-28
---

# 05_BACKTEST 目录重组方案

> 分离因子IC验证 vs 策略回测报告

---

## 新目录结构

```
05_BACKTEST/
├── README.md                          # 本文档
├── ic_reports/                        # 因子IC验证报告
│   ├── README.md
│   ├── ALPHA_001-014_趋势类_IC.md
│   ├── ALPHA_015-026_均值回归类_IC.md
│   ├── ALPHA_027-037_价值类_IC.md
│   ├── ALPHA_038-047_成长类_IC.md
│   ├── ALPHA_048-064_质量类_IC.md
│   ├── PE_TTM_IC_20260328.md          # 迁移自此处
│   └── 相关性矩阵_20260328.md         # 迁移自此处
│
└── strategy_reports/                  # 策略回测报告
    ├── README.md
    ├── S001_TREND_FOLLOW/
    │   ├── backtest_20260328.md
    │   ├── performance_metrics.md
    │   └── equity_curve.png
    ├── S002_MEAN_REVERSION/
    │   ├── backtest_20260328.md
    │   └── performance_metrics.md
    └── ...
```

---

## 迁移计划

### 第一步：创建新目录结构

```bash
# 创建IC报告目录
mkdir ic_reports/
mkdir strategy_reports/

# 创建README文件
touch ic_reports/README.md
touch strategy_reports/README.md
```

### 第二步：迁移因子IC报告

**源文件**:
- `05_BACKTEST/价值类/PE_TTM_IC_20260328.md` → `ic_reports/PE_TTM_IC_20260328.md`
- `05_BACKTEST/相关性矩阵_20260328.md` → `ic_reports/相关性矩阵_20260328.md`

**新增文件**:
- `ic_reports/ALPHA_001-014_趋势类_IC.md`
- `ic_reports/ALPHA_015-026_均值回归类_IC.md`
- `ic_reports/ALPHA_027-037_价值类_IC.md`
- `ic_reports/ALPHA_038-047_成长类_IC.md`
- `ic_reports/ALPHA_048-064_质量类_IC.md`

### 第三步：创建策略回测报告目录

**新增目录**:
- `strategy_reports/S001_TREND_FOLLOW/`
- `strategy_reports/S002_MEAN_REVERSION/`
- `strategy_reports/S003_VALUE_INVESTING/`
- ...

---

## 文件说明

### ic_reports/ - 因子IC验证报告

**用途**: 验证单个因子的预测能力

**文件命名**: `{因子ID范围}_{因子类型}_IC.md`

**内容**:
- 因子列表
- IC值统计
- IC分布图
- 相关性分析
- 结论

**示例**: `ALPHA_001-014_趋势类_IC.md`

### strategy_reports/ - 策略回测报告

**用途**: 验证完整策略的交易表现

**文件命名**: `S{策略ID}_{策略名称}/backtest_{日期}.md`

**内容**:
- 策略说明
- 回测参数
- 性能指标（夏普比、最大回撤等）
- 权益曲线
- 交易统计

**示例**: `S001_TREND_FOLLOW/backtest_20260328.md`

---

## 关键区别

| 维度 | IC报告 | 策略回测 |
|------|--------|---------|
| **对象** | 单个因子 | 完整策略 |
| **目的** | 验证因子预测能力 | 验证策略交易表现 |
| **指标** | IC值、相关性 | 夏普比、最大回撤、胜率 |
| **频率** | 因子更新时验证 | 策略运行后验证 |
| **位置** | `ic_reports/` | `strategy_reports/` |

---

## 迁移检查清单

- [ ] 创建 `ic_reports/` 目录
- [ ] 创建 `strategy_reports/` 目录
- [ ] 迁移 `PE_TTM_IC_20260328.md` 到 `ic_reports/`
- [ ] 迁移 `相关性矩阵_20260328.md` 到 `ic_reports/`
- [ ] 创建 `ic_reports/README.md`
- [ ] 创建 `strategy_reports/README.md`
- [ ] 更新 `02_FACTOR_LIBRARY/00_INDEX/README.md`
- [ ] 更新 `System_Manifest.md`
- [ ] 更新 `CHANGELOG.md`

---

**版本**: 1.0 | **更新**: 2026-03-28
