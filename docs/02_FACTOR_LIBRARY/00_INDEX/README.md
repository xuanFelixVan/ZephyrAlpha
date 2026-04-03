---
module_id: FACTOR_README_001
version: 5.1.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构师
standard_type: 专业量化机构因子标准
applicable_scope: 因子研究与管理
compliance_level: 研究标准
parent_document: ../INDEX.md
implementation_status: 进行中
---

# 因子库索引

> 清风量化因子库导航入口
>
> **版本**：v5.1
> **更新日期**：2026-03-28

---

## 快速导航

| 目录 | 内容 | 说明 |
|------|------|------|
| [00_INDEX](../../../README.md) | 本文档 | 索引入口 |
| [01_METHODOLOGY](../../../README.md) | 研究方法论 | 因子研究标准 |
|  | Alpha因子 | 87+个Alpha因子 |
|  | 风险因子 | 46+个风险因子 |
|  | 数据源 | THS_BD指标清单 |
|  | 回测报告 | IC验证/回测报告 |
|  | 归档文件 | 历史文件归档 |
|  | 手册文档 | 因子库手册 |

---

## 目录结构

```
factor-library/
├── 00_INDEX/                 # 索引导航
│   ├── README.md             # 本文档
│   └── factor_classification_summary.md        # 因子分类总览
├── 01_METHODOLOGY/           # 研究方法论
│   ├── README.md            # 方法论索引
│   ├── T.02.FE001.factor_definition.md # 因子定义标准
│   ├── ic_analysis.md       # IC分析体系
│   ├── factor_preprocessing.md    # 预处理方法
│   ├── factor_synthesis.md  # 因子合成
│   └── backtest_standards.md # 回测标准
├── 02_ALPHA_FACTORS/        # Alpha因子（87+）
│   ├── 1_趋势跟踪因子.md
│   ├── 2_均值回归因子.md
│   ├── 3_价值因子.md
│   ├── 4_成长因子.md
│   ├── 5_质量因子.md
│   ├── 6_动量因子.md
│   └── 7_情绪因子.md
├── 03_RISK_FACTORS/         # 风险因子（46+）
│   ├── T.03.RF001.barra_style_factors.md
│   ├── T.03.RF002.industry_factors.md
│   └── T.03.RF003.tail_risk_factors.md
├── 04_DATA_SOURCE/           # 数据源
│   ├── iFind/               # iFind数据
│   │   ├── factor_master_index.csv
│   │   ├── factor_master_index.md
│   │   ├── factor_list.csv
│   │   └── financial_statements/
│   └── README.md
├── 05_BACKTEST/             # 回测报告（新增）
│   ├── README.md
│   ├── correlation_matrix.md
│   ├── 趋势类/
│   ├── 均值回归类/
│   ├── value_factors/
│   │   ├── PE_TTM_IC.md
│   │   └── PE_TTM_BACKTEST.md
│   ├── 成长类/
│   ├── 质量类/
│   ├── 动量类/
│   ├── 情绪类/
│   └── 风险类/
├── 06_ARCHIVE/              # 归档
├── 10_MANUAL/               # 手册
└── SPEC.md                  # 规格文档
```

---

## 因子统计

| 类别 | 数量 | 说明 |
|------|------|------|
| Alpha因子 | 87+ | 趋势、均值回归、价值、成长、质量、动量、情绪 |
| 风险因子 | 46+ | Barra风格、行业、尾部风险 |
| 数据源因子 | 5700+ | THS_BD指标 |
| **合计** | **5900+** | - |

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v4.0 | 2026-03-28 | 完善01_METHODOLOGY，新增05_BACKTEST，扁平化目录结构 |
| v3.2 | 2026-03-26 | 因子库手册v3.2 |
| v3.1 | 2026-03-01 | 因子分类体系建立 |
