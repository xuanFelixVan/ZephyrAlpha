# 因子库 (Factor Library) - v4.0 专业机构版

> 清风量化交易系统的核心因子库，采用专业量化机构标准构建
>
> **版本**: v4.0
> **更新日期**: 2026-03-28
> **状态**: 已实施

---

## 快速导航

| 模块 | 说明 | 链接 |
|------|------|------|
| ** 治理框架** | 因子治理、生命周期管理、质量标准 | [00_GOVERNANCE](00_GOVERNANCE/README.md) |
| ** 方法论** | IC 分析、回测标准、因子定义 | [01_METHODOLOGY](01_METHODOLOGY/README.md) |
| ** Alpha 工厂** | Alpha 因子详细说明 | [02_ALPHA_FACTORY](02_ALPHA_FACTORY/README.md) |
| ** 风险模型** | 风险因子、Barra 模型 | [03_RISK_MODELS](03_RISK_MODELS/README.md) |
| ** 数据宇宙** | 数据源、数据质量 | [04_DATA_UNIVERSE](04_DATA_UNIVERSE/README.md) |
| ** 回测结果** | IC 报告、回测报告 | [05_BACKTEST_RESULTS](05_BACKTEST_RESULTS/README.md) |
| ** 因子注册** | 因子注册表、元数据 | [06_FACTOR_REGISTRY](06_FACTOR_REGISTRY/README.md) |
| ** 监控中心** | 实时监控、月度报告 | [07_MONITORING](07_MONITORING/README.md) |

---

## 架构升级说明

### v4.0 重大变更

#### 1. 架构重构

**旧架构 (v3.x)**:
`
00_INDEX/           # 索引
01_METHODOLOGY/     # 方法论
02_ALPHA_FACTORS/   # Alpha 因子
03_RISK_FACTORS/    # 风险因子
04_DATA_SOURCE/     # 数据源
05_BACKTEST/        # 回测
10_MANUAL/          # 手册
`

**新架构 (v4.0)**:
`
00_GOVERNANCE/      # 治理框架  新增
01_METHODOLOGY/     # 方法论 (优化)
02_ALPHA_FACTORY/   # Alpha 工厂  重构
03_RISK_MODELS/     # 风险模型  升级
04_DATA_UNIVERSE/   # 数据宇宙  重新定义
05_BACKTEST_RESULTS/# 回测结果  充实
06_FACTOR_REGISTRY/ # 因子注册  新增
07_MONITORING/      # 监控中心  新增
`

#### 2. 核心改进

| 改进点 | 说明 | 收益 |
|--------|------|------|
| **治理框架** | 引入因子治理委员会、全生命周期管理 | 提升决策质量、降低风险 |
| **质量标准** | 明确入库标准 (IC_IR>0.5, 夏普>1.0) | 保证因子质量 |
| **命名规范** | 统一命名规则 (ALPHA_TREND_001_v1.0) | 提高可维护性 |
| **版本控制** | 主版本。次版本。修订版 | 变更可追溯 |
| **监控体系** | 日常监控 + 告警响应机制 | 及时发现问题 |
| **合规审计** | 审计追踪 + 合规要求 | 符合监管要求 |

#### 3. 文档迁移

| 原文档 | 新位置 | 状态 |
|--------|--------|------|
| 因子分类总表.md | 06_FACTOR_REGISTRY/factor_catalog.md |  已迁移 |
| 因子库手册_v3.2.md | 00_GOVERNANCE/ + 01_METHODOLOGY/ |  拆分迁移 |
| 趋势跟踪因子.md | 02_ALPHA_FACTORY/01_trend_factors.md |  已迁移 |
| Barra 风格因子.md | 03_RISK_MODELS/01_barra_factors.md |  已迁移 |

---

## 因子库概览

### 因子统计

| 类别 | 数量 | A 级 | B 级 | C 级 | 状态 |
|------|------|-----|-----|-----|------|
| **Alpha 因子** | 45 | 12 | 20 | 13 | 活跃 |
| **风险因子** | 28 | 8 | 15 | 5 | 活跃 |
| **风格因子** | 10 | 5 | 4 | 1 | 活跃 |
| **行业因子** | 30 | 10 | 15 | 5 | 活跃 |
| **另类因子** | 15 | 3 | 7 | 5 | 观察 |
| **总计** | **128** | **38** | **61** | **29** | - |

### 因子表现 (近 30 日)

| 指标 | 均值 | 中位数 | 标准差 |
|------|------|--------|--------|
| **IC** | 0.035 | 0.032 | 0.015 |
| **IR** | 0.78 | 0.72 | 0.35 |
| **夏普比率** | 1.25 | 1.18 | 0.45 |
| **最大回撤** | 15.2% | 13.5% | 6.8% |
| **换手率** | 35%/年 | 30%/年 | 18%/年 |

---

## 使用指南

### 1. 因子开发流程

`mermaid
graph LR
    A[创意提出] --> B[初步研究]
    B --> C[IC 验证]
    C --> D[回测验证]
    D --> E[入库审批]
    E --> F[正式入库]
    F --> G[持续监控]
`

**详细流程**: [00_GOVERNANCE/README.md](00_GOVERNANCE/README.md#二因子全生命周期管理)

### 2. 因子查询

`ash
# 按分类查询
因子注册表 > Alpha 因子 > 趋势跟踪

# 按名称查询
因子注册表 > 搜索 "MA5"

# 按表现查询
因子注册表 > 筛选 "IC_IR > 1.0"
`

**因子注册表**: [06_FACTOR_REGISTRY/factor_catalog.md](06_FACTOR_REGISTRY/factor_catalog.md)

### 3. 因子使用

`python
# 示例：使用因子
from factor_library import FactorLibrary

fl = FactorLibrary()

# 获取因子数据
factor_data = fl.get_factor(
    factor_id="ALPHA_TREND_001",
    start_date="2026-01-01",
    end_date="2026-03-28"
)

# 获取因子元数据
factor_info = fl.get_factor_info("ALPHA_TREND_001")
`

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

**详细标准**: [00_GOVERNANCE/README.md](00_GOVERNANCE/README.md#三因子质量标准)

---

## 监控与告警

### 监控指标

| 指标 | 告警阈值 | 响应时限 |
|------|----------|----------|
| IC 衰减率 | > 30% | 3 天 |
| 数据缺失率 | > 10% | 4 小时 |
| IC 连续为负 | 10 日 | 24 小时 |

**监控体系**: [00_GOVERNANCE/README.md](00_GOVERNANCE/README.md#七因子监控体系)

### 最新告警

| 日期 | 因子 | 告警类型 | 状态 |
|------|------|----------|------|
| 2026-03-25 | ALPHA_MRV_003 | IC 衰减>30% | 观察中 |
| 2026-03-20 | ALPHA_SENT_002 | 数据缺失>5% | 已解决 |

**监控报告**: [07_MONITORING/monthly/2026-03.md](07_MONITORING/monthly/2026-03.md)

---

## 更新记录

| 版本 | 日期 | 变更内容 | 审批人 |
|------|------|----------|--------|
| v4.0 | 2026-03-28 | 专业机构化重构 | 首席量化官 |
| v3.2 | 2026-03-20 | 补充 THS_BD 指标 | 因子管理员 |
| v3.1 | 2026-03-15 | 优化因子分类 | 因子验证员 |
| v3.0 | 2026-03-01 | 初始版本 | 首席量化官 |

---

## 相关文档

- [治理框架](00_GOVERNANCE/README.md) - 因子治理、生命周期管理
- [方法论](01_METHODOLOGY/README.md) - IC 分析、回测标准
- [因子注册表](06_FACTOR_REGISTRY/factor_catalog.md) - 完整因子列表
- [监控报告](07_MONITORING/README.md) - 日常监控、月度报告

---

**维护部门**: 清风量化因子治理委员会  
**最后更新**: 2026-03-28  
**下次审查日期**: 2026-06-28

**联系方式**: factor-committee@qingfeng-quant.com
