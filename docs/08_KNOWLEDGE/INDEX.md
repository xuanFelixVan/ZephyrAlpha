---
module_id: INDEX_08_KNOWLEDGE
version: "2.0.0"
status: Active
layer: L00
owner: ZephyrAlpha-Owner
created_date: "2026-04-03"
last_updated: "2026-04-16"
description: "知识库总索引（v2.0 — 编码修复重建版）"
---

# 知识库总索引

> **重建说明**：v1.0 版本因 Cursor+Trae 双编辑器交替使用导致严重编码损坏，已于 2026-04-16 重建为标准 UTF-8 版本。

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
├── FACTOR_LIBRARY/        # 因子案例库
│   ├── INDEX.md
│   ├── factor-case-library.md
│   └── momentum-factor-library.md
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

## 知识条目（KE-XXX 格式，由流水线提取入库）

> 流水线执行后，在此处追加新条目索引。

| KE-ID | 标题 | 类别 | 来源蓝图 | 层级 |
|-------|------|------|---------|------|
| *(待流水线提取)* | — | — | — | — |

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
| 知识库使用指南 | `knowledge-base-platform-guide.md` | 如何使用本知识库 |

---

*本文件是知识库总入口。流水线提取的新条目请追加到上方 KE 表格中。*

<!-- orphan-link -->
- [knowledge-base-case-studies](knowledge-base-case-studies.md)

<!-- orphan-link -->
- [knowledge-transfer-system](knowledge-transfer-system.md)

<!-- orphan-link -->
- [knowledge-enrichment-sprint-plan](knowledge-enrichment-sprint-plan.md)
