---
module_id: README
---

﻿---
module_id: 03_TRADING_TACTICS_README
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - 03_TRADING_TACTICS说明文档
---

﻿---
module_id: TACTICS_MAIN_README_001
version: 5.3.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构?standard_type: 专业量化机构文档
responsibility:
  - 交易策略设计与实施管理与优化维护
applicable_scope: 全系?compliance_level: 专业标准
parent_document: INDEX.md
implementation_status: 进行?---

# 03_TRADING_TACTICS - 交易战术?
> **核心职责**: 模块说明和快速入门指南
> **职责边界**: 
> - ✅ 本文档负责：模块说明和快速入门指南相关内容
> - ❌ 本文档不负责：其他模块内容

> 清风量化交易系统 v5.3 核心交易策略与战术文?>
> **版本**: v5.3
> **更新日期**: 2026-03-31
> **维护?*: 策略研发团队
> **Layer**: Layer 5 (策略执行?
---


## 快速导?
### 核心模块

| 目录 | 说明 | 关键文档 |
|------|------|----------|
| 01_STRATEGY_FRAMEWORK/ | 策略框架 | overview.md, lifecycle.md, classification.md, STRATEGY_ENGINE_BLUEPRINT.md |
| 02_TACTICS_MERGED/ | 战术融合 | README.md |
| 03_ADVANCED_TACTICS/ | 高级战术 | 波段交易, 涨停分析, 市场周期 |
| 04_YOUZI_STRATEGIES/ | 游资策略 | 龙头战法, 短线技?|
| 05_STRATEGY_POOL/ | 策略?| index.md (S001-S120) |
| 06_POSITION_MANAGEMENT/ | 仓位管理 | README.md |
| 09_RISK_RULES/ | 风险规则 | BLUEPRINT.md, RISK_RULE_ENGINE.md |

> **注意**: `07_ORDER_GENERATION/` 已移动至 [../04_EXECUTION/01_ORDER_EXECUTION/](../04_EXECUTION/01_ORDER_EXECUTION/) (属于执行层内?

### 支持模块

| 目录 | 说明 |
|------|------|
| 99_ARCHIVE/ | 已归档文?|

---

## 核心文档

| 文档 | 说明 |
|------|------|
| [INDEX.md](INDEX.md) | 策略索引 |
| STRATEGY_ENGINE_BLUEPRINT.md | 策略引擎开发蓝图|
| Strategy_Spec_S001.md | S001策略规格 |
| parameter_management.md | 参数管理 |
| OPTIMIZATION_REPORT.md | 优化报告 |
| REFACTOR_COMPLETE.md | 重构完成记录 |

---

## 策略池概述
| 策略ID | 策略类型 | 状态|
|--------|----------|------|
| S001-S030 | 短线策略 | 活跃 |
| S031-S060 | 中线策略 | 活跃 |
| S061-S090 | 长线策略 | 活跃 |
| S091-S120 | 组合策略 | 开发中 |

---

## Layer 5 战术实现

```
Layer 5: 策略执行?├── 信号生成 ?订单路由 ?执行监控
└── 详见: 01_STRATEGY_FRAMEWORK/
```

---

## 相关文档

| 文档 | 说明 |
|------|------|
| [../01_FRAMEWORK/README.md](../01_FRAMEWORK/README.md) | Layer 0-11 框架说明 |
| [../02_FACTOR_LIBRARY/](../02_FACTOR_LIBRARY/) | 因子?(87 Alpha + 46 Risk) |
| [../04_EXECUTION/README.md](../04_EXECUTION/README.md) | 执行引擎 |
| [../05_IMPLEMENTATION/](../05_IMPLEMENTATION/) | 实施指南 |

---

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v5.3 | 2026-03-31 | 版本同步至v5.3 |
| v2.0 | 2026-03-28 | 专业机构版重?|
| v1.0 | 2026-03-01 | 初始版本 |

---

**最后更?*: 2026-03-31
