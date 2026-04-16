---
module_id: INDEX_08_KNOWLEDGE
version: "2.1.0"
status: Active
layer: L00
owner: ZephyrAlpha-Owner
created_date: "2026-04-03"
last_updated: "2026-04-16"
description: "知识库总索引（v2.1 — GH Wave 3 完成后更新）"
---

# 知识库总索引

> **更新说明**：v2.1 版本在 GH Wave 3 完成后更新，新增 395 个 KE 条目（KE-031~KE-425），知识库总量达到 425 条。

---

## 知识库结构

```
docs/08_KNOWLEDGE/
├── BEST_PRACTICES/        # 最佳实践 + 蓝图设计决策 + 教训记录
│   ├── INDEX.md
│   ├── backtest-best-practices.md
│   ├── risk-management-best-practices.md
│   └── factor-research-best-practices.md
├── STRATEGY_LIBRARY/      # 策略案例库
│   ├── INDEX.md
│   ├── strategy-case-library.md
│   └── multi-factor-strategy-library.md
├── FACTOR_LIBRARY/        # 因子案例库 + KE 条目（395个）
│   ├── INDEX.md
│   ├── factor-case-library.md
│   ├── momentum-factor-library.md
│   └── KE-031~KE-425.md   # GH Wave 3 提取的知识条目
├── DESIGN_PRINCIPLES/     # 设计原则
│   └── L02-factor-design-principle-alpha-generation.md
├── PITFALLS/              # 陷阱与反模式
│   └── L02-pitfall-factor-overfitting-backtest.md
├── 01_TECHNICAL_KNOWLEDGE/ # 技术知识
│   ├── INDEX.md
│   └── ai-code-editors-complete-guide.md
└── INDEX.md               # 本文件
```

---

## 知识条目统计（KE-XXX 格式）

| 批次 | 范围 | 数量 | 来源 | 状态 |
|------|------|------|------|------|
| GH Wave 2 | KE-001~KE-030 | 30 | 01_FRAMEWORK 历史版本 | ✅ 已完成 |
| GH Wave 3 | KE-031~KE-425 | 395 | 因子库/策略/蓝图被删文件 | ✅ 已完成 |
| **总计** | **KE-001~KE-425** | **425** | Git 历史挖掘 | ✅ **完成** |

### 分类统计

| 类别 | 数量 | 占比 |
|------|------|------|
| blueprint_decision | 357 | 84.0% |
| factor | 56 | 13.2% |
| best_practice | 12 | 2.8% |
| **总计** | **425** | **100%** |

---

## 技术领域覆盖

### L01 数据层 (Data Layer)
数据获取、存储、治理、质量、实时处理相关 KE 条目

### L02 特征层 (Feature Layer)
因子计算、挖掘、验证、合成、风险相关 KE 条目

### L03 模型层 (Model Layer)
优化器、风险模型、回测框架、ML 集成相关 KE 条目

### L04 执行层 (Execution Layer)
交易执行、成本控制、策略执行、实时监控相关 KE 条目

### L05 组合层 (Portfolio Layer)
组合构建、管理、风险管理、绩效评估相关 KE 条目

### L06 监控层 (Monitoring Layer)
监控系统、质量监控、风险监控相关 KE 条目

### L07 治理层 (Governance Layer)
蓝图管理、开发流程、架构设计相关 KE 条目

---

## 现有内容导航

| 文档 | 路径 | 核心内容 |
|------|------|---------|
| 最佳实践（回测） | `BEST_PRACTICES/backtest-best-practices.md` | 前瞻偏差、生存偏差、过拟合防护 |
| 最佳实践（风险管理） | `BEST_PRACTICES/risk-management-best-practices.md` | VaR、最大回撤、压力测试 |
| 最佳实践（因子研究） | `BEST_PRACTICES/factor-research-best-practices.md` | 因子挖掘流程、IC 评估 |
| 策略案例库 | `STRATEGY_LIBRARY/strategy-case-library.md` | 动量、价值、机器学习策略案例 |
| 多因子策略库 | `STRATEGY_LIBRARY/multi-factor-strategy-library.md` | 多因子组合方法 |
| 因子案例库 | `FACTOR_LIBRARY/factor-case-library.md` | EP、ROE、动量、低波动率因子 |
| 动量因子库 | `FACTOR_LIBRARY/momentum-factor-library.md` | 12 月价格动量因子 |
| 因子设计原则 | `DESIGN_PRINCIPLES/L02-factor-design-principle-alpha-generation.md` | Alpha 生成设计原则 |
| 陷阱（因子过拟合） | `PITFALLS/L02-pitfall-factor-overfitting-backtest.md` | 回测过拟合的识别与规避 |
| AI 编辑器指南 | `01_TECHNICAL_KNOWLEDGE/ai-code-editors-complete-guide.md` | Cursor+Trae 使用最佳实践 |

---

## 快速检索

### 按 KE 编号范围

| 范围 | 内容主题 | 文件命名模式 |
|------|---------|-------------|
| KE-001~KE-030 | AI 架构、蓝图管理、数据质量 | 混合命名 |
| KE-031~KE-100 | 因子管理、数据质量、另类数据 | 混合命名 |
| KE-101~KE-200 | 因子库手册、蓝图规则、数据架构 | 混合命名 |
| KE-201~KE-300 | L1-L7 架构蓝图、组合优化 | 混合命名 |
| KE-301~KE-400 | 风险系统、策略引擎、数据库设计 | 混合命名 |
| KE-401~KE-425 | UI 设计、Web 界面、开发流程 | 混合命名 |

---

*本文件是知识库总入口。GH Wave 3 清仓提交后更新于 2026-04-16。*

<!-- orphan-link -->
- [knowledge-base-case-studies](knowledge-base-case-studies.md)

<!-- orphan-link -->
- [knowledge-transfer-system](knowledge-transfer-system.md)

<!-- orphan-link -->
- [knowledge-enrichment-sprint-plan](knowledge-enrichment-sprint-plan.md)
