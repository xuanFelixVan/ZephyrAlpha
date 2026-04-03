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

# 02_FACTOR_LIBRARY - 因子库 (v5.1)

> 清风量化交易系统的核心因子库，采用专业量化机构标准构建
>
> **版本**: v5.2
> **更新日期**: 2026-04-01
> **状态**: 活跃

---

## 快速导航

| 模块 | 说明 | 链接 |
|------|------|------|
| **治理框架** | 因子治理、生命周期管理、质量标准 | [00_GOVERNANCE](00_GOVERNANCE/README.md) |
| **方法论** | IC 分析、回测标准、因子定义 | [01_METHODOLOGY](01_METHODOLOGY/README.md) |
| **Alpha因子** | Alpha 因子详细说明 | [02_ALPHA_FACTORS](02_ALPHA_FACTORS/) |
| **风险因子** | 风险因子、Barra 模型 | [03_RISK_FACTORS](03_RISK_FACTORS/) |
| **数据宇宙** | 数据源、数据质量 | [04_DATA_SOURCE](./04_DATA_SOURCE/) |
| **回测结果** | IC 报告、回测报告 | [05_BACKTEST](./05_BACKTEST/) |
| **集成架构** | 因子库与回测集成蓝图 | [FACTOR_BACKTEST_INTEGRATION_BLUEPRINT.md](./FACTOR_BACKTEST_INTEGRATION_BLUEPRINT.md) |
| **因子注册** | 因子注册表、元数据 | [06_FACTOR_REGISTRY](./06_FACTOR_REGISTRY/) |
| **监控中心** | 实时监控、月度报告、AI因子管家 | [07_FACTOR_MONITORING](./07_FACTOR_MONITORING/) |

---

## 新增内容 (2026-04-01)

| 文档 | 说明 | 链接 |
|------|------|------|
| **因子库与回测集成蓝图** | 专业架构设计、开源模块集成、实施路径 | [FACTOR_BACKTEST_INTEGRATION_BLUEPRINT.md](./FACTOR_BACKTEST_INTEGRATION_BLUEPRINT.md) |
| **因子管理标准** | 专业机构做法（分层/IC阈值/生命周期） | [01_METHODOLOGY](01_METHODOLOGY/FACTOR_MANAGEMENT_STANDARD.md) |
| **因子筛选策略** | 5900因子筛选到20-30个有效因子 | [01_METHODOLOGY](01_METHODOLOGY/FACTOR_SCREENING_STRATEGY.md) |
| **AI因子管家** | 全自动因子管理（发现/淘汰/报告） | [07_FACTOR_MONITORING](07_FACTOR_MONITORING/AI_FACTOR_AGENT.md) |

---

## 架构说明

### v5.1 目录结构

```
02_FACTOR_LIBRARY/
├── FACTOR_BACKTEST_INTEGRATION_BLUEPRINT.md  # 因子库与回测集成蓝图 (新增)
├── 00_GOVERNANCE/           # 因子治理框架 (新增)
│   └── README.md
├── 00_INDEX/               # 因子分类总表
│   ├── README.md
│   └── factor_classification_summary.md
├── 01_METHODOLOGY/          # 研究方法论
│   ├── README.md
│   ├── FACTOR_MANAGEMENT_STANDARD.md  # ⭐ 专业机构做法 (v1.0)
│   ├── FACTOR_SCREENING_STRATEGY.md  # ⭐ 5900因子筛选 (v1.0)
│   ├── ic_analysis.md
│   ├── T.02.FE001.factor_definition.md
│   ├── factor_preprocessing.md
│   ├── factor_neutralization.md
│   ├── factor_return_analysis.md
│   ├── factor_synthesis.md
│   ├── backtest_standards.md
│   ├── research_management.md
│   └── TECHNICAL_INDICATORS.md
├── 02_ALPHA_FACTORS/        # Alpha因子 (87个)
│   └── (因子定义文件)
├── 03_RISK_FACTORS/         # 风险因子 (46 个)
│   ├── T.03.RF001.barra_style_factors.md
│   ├── T.03.RF002.industry_factors.md
│   └── T.03.RF003.tail_risk_factors.md
├── 04_DATA_SOURCE/          # 数据源
│   ├── README.md
│   ├── iFind/
│   └── ...
├── 05_BACKTEST/             # 回测报告
│   ├── ic_reports/
│   ├── strategy_reports/
│   └── ...
├── 06_FACTOR_REGISTRY/      # 因子注册 (新增)
│   └── factor_catalog.md
└── 07_FACTOR_MONITORING/           # 监控中心
    ├── factor_monitoring.md
    └── AI_FACTOR_AGENT.md          # ⭐ AI因子管家 (v1.0)
```

---

## 因子库概览

### 因子统计

| 类别 | 数量 | 说明 |
|------|------|------|
| **Alpha 因子** | 87 | 趋势、均值回归、价值、成长、质量、技术、情绪 |
| **风险因子** | 46 | Barra风格(10)、行业(30)、尾部风险(6) |
| **总计** | **133** | - |

---

## 核心文档

| 文档 | 说明 |
|------|------|
| [因子分类总表.md](00_INDEX/factor_classification_summary.md) | 所有因子分类索引 |
| [因子注册表](./06_FACTOR_REGISTRY/factor_catalog.md) | 完整因子列表 |
| [Alpha因子索引](02_ALPHA_FACTORS_INDEX.md) | 87个Alpha因子详细说明 |

---

## 使用指南

### 1. 因子开发流程

```
创意提出 → 初步研究 → IC验证 → 回测验证 → 入库审批 → 正式入库 → 持续监控
```

详细流程: [00_GOVERNANCE/README.md](00_GOVERNANCE/README.md)

### 2. 因子查询

按分类查询：因子注册表 → Alpha因子 → 趋势跟踪
按名称查询：因子注册表 → 搜索 "MA5"
按表现查询：因子注册表 → 筛选 "IC_IR > 1.0"

因子注册表: [06_FACTOR_REGISTRY/factor_catalog.md](./06_FACTOR_REGISTRY/factor_catalog.md)

### 3. 因子使用

```python
from factor_library import FactorLibrary

fl = FactorLibrary()

factor_data = fl.get_factor(
    factor_id="ALPHA_001",
    start_date="2026-01-01",
    end_date="2026-03-28"
)

factor_info = fl.get_factor_info("ALPHA_001")
```

---

## 质量标准

### 入库标准

| 指标 | 最低要求 | 优秀标准 |
|------|----------|----------|
| IC 均值 | > 0.02 | > 0.05 |
| IC_IR | > 0.5 | > 1.0 |
| 夏普比率 | > 1.0 | > 1.5 |
| 最大回撤 | < 20% | < 10% |
| 换手率 | < 50%/年 | < 20%/年 |

详细标准: [00_GOVERNANCE/README.md](00_GOVERNANCE/README.md)

---

## 监控与告警

### 监控指标

| 指标 | 告警阈值 | 响应时限 |
|------|----------|----------|
| IC 衰减率 | > 30% | 3 天 |
| 数据缺失率 | > 10% | 4 小时 |
| IC 连续为负 | 10 日 | 24 小时 |

监控报告: [07_FACTOR_MONITORING/factor_monitoring.md](./07_FACTOR_MONITORING/factor_monitoring.md)

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v5.2 | 2026-04-01 | 添加因子库与回测集成蓝图 |
| v5.1 | 2026-03-31 | 版本同步至v5.1 |
| v5.0 | 2026-03-29 | 同步 v5.0 目录结构 |
| v4.0 | 2026-03-28 | 专业机构化重构 |
| v3.2 | 2026-03-20 | 补充 THS_BD 指标 |
| v3.0 | 2026-03-01 | 初始版本 |

---

## 相关文档

- [治理框架](00_GOVERNANCE/README.md) - 因子治理、生命周期管理
- [方法论](01_METHODOLOGY/README.md) - IC 分析、回测标准
- [因子注册表](./06_FACTOR_REGISTRY/factor_catalog.md) - 完整因子列表
- [监控报告](../../README.md) - 日常监控、月度报告

---

**维护部门**: 清风量化因子治理委员会
**最后更新**: 2026-04-01
**版本**: v5.2
