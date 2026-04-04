---
module_id: RISK_DOC_INDEX_001
version: 1.0.0
status: Active
created_date: 2026-04-04
last_updated: 2026-04-04
owner: 文档审计员
standard_type: 专业量化机构文档索引
applicable_scope: 风险管理文档
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 活跃维护
---

# 风险管理文档索引

> **版本**: v1.0
> **创建日期**: 2026-04-04
> **目的**: 整合风险管理相关文档，识别职责重叠，建立清晰索引

---

## 📊 文档统计

| 分类 | 数量 | 说明 |
|------|------|------|
| 风险引擎核心 | 3 | Layer 6 风控引擎 |
| 风控规则 | 3 | 规则定义与执行 |
| 风险因子 | 1 | 风险因子库 |
| 风险预算 | 2 | 风险预算系统 |
| BARRA模型 | 2 | BARRA风险模型 |
| 实时监控 | 2 | 实时风险监控 |
| 风险归因 | 2 | 风险归因系统 |
| 尾部风险 | 2 | 尾部风险对冲 |
| 最佳实践 | 1 | 风险管理最佳实践 |
| **总计** | **18** | 核心风险管理文档 |

---

## 🔴 职责重叠分析

### 重叠组1: 风控规则引擎 (P0 - 高风险)

| 文档路径 | 职责 | 问题 |
|----------|------|------|
| `04_EXECUTION/05_RISK_ENGINE/README.md` | Layer 6风控规则引擎 | 与下方文档重复 |
| `03_TRADING_TACTICS/09_RISK_RULES/RISK_RULE_ENGINE.md` | 风控规则引擎蓝图 | 与上方文档重复 |
| `03_TRADING_TACTICS/09_RISK_RULES/BLUEPRINT.md` | 风控规则体系蓝图 | 框架层，应保留 |

**建议**:
- 保留 `03_TRADING_TACTICS/09_RISK_RULES/BLUEPRINT.md` 作为框架设计
- 合并两个"风控规则引擎"文档到 `04_EXECUTION/05_RISK_ENGINE/`
- 删除 `03_TRADING_TACTICS/09_RISK_RULES/RISK_RULE_ENGINE.md`

### 重叠组2: 实时风险监控 (P1 - 中风险)

| 文档路径 | 职责 | 问题 |
|----------|------|------|
| `01_FRAMEWORK/REALTIME_RISK_MONITORING_BLUEPRINT.md` | 实时风险监控仪表板 | 框架层定义 |
| `05_IMPLEMENTATION/.../REALTIME_RISK_HEDGE_ENGINE_BLUEPRINT.md` | 实时风险对冲引擎 | 实施层实现 |

**建议**:
- 两者职责不同（框架 vs 实施），应保留
- 需要在文档中明确引用关系

---

## 📁 分类索引

### 1. 风险引擎核心 (Layer 6)

| 文档 | 路径 | 职责 | 状态 |
|------|------|------|------|
| 风控规则引擎 | [04_EXECUTION/05_RISK_ENGINE/README.md](../../04_EXECUTION/05_RISK_ENGINE/README.md) | Layer 6执行 | ⚠️ 需整合 |
| 风控规则体系蓝图 | [03_TRADING_TACTICS/09_RISK_RULES/BLUEPRINT.md](../../03_TRADING_TACTICS/09_RISK_RULES/BLUEPRINT.md) | 规则框架 | ✅ 保留 |
| 风控规则引擎蓝图 | [03_TRADING_TACTICS/09_RISK_RULES/RISK_RULE_ENGINE.md](../../03_TRADING_TACTICS/09_RISK_RULES/RISK_RULE_ENGINE.md) | 引擎实现 | ⚠️ 需整合 |
| 风险报告生成器 | [03_TRADING_TACTICS/09_RISK_RULES/RISK_REPORT.md](../../03_TRADING_TACTICS/09_RISK_RULES/RISK_REPORT.md) | 报告生成 | ✅ 保留 |

### 2. 风险因子库

| 文档 | 路径 | 职责 | 状态 |
|------|------|------|------|
| 尾部风险因子 | [02_FACTOR_LIBRARY/03_RISK_FACTORS/T.03.RF003.tail_risk_factors.md](../../02_FACTOR_LIBRARY/03_RISK_FACTORS/T.03.RF003.tail_risk_factors.md) | 风险因子定义 | ✅ 保留 |

### 3. 风险预算系统

| 文档 | 路径 | 职责 | 状态 |
|------|------|------|------|
| 简化风险预算系统蓝图 | [05_IMPLEMENTATION/.../SIMPLIFIED_RISK_BUDGET_SYSTEM_BLUEPRINT.md](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/SIMPLIFIED_RISK_BUDGET_SYSTEM_BLUEPRINT.md) | 风险预算框架 | ✅ 保留 |
| 简化风险预算系统规格 | [05_IMPLEMENTATION/.../SIMPLIFIED_RISK_BUDGET_SYSTEM_TECHNICAL_SPECIFICATION.md](../../05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/SIMPLIFIED_RISK_BUDGET_SYSTEM_TECHNICAL_SPECIFICATION.md) | 技术规格 | ✅ 保留 |

### 4. BARRA风险模型

| 文档 | 路径 | 职责 | 状态 |
|------|------|------|------|
| BARRA风险模型蓝图 | [05_IMPLEMENTATION/.../BARRA_RISK_MODEL_BLUEPRINT.md](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/BARRA_RISK_MODEL_BLUEPRINT.md) | 模型框架 | ✅ 保留 |
| BARRA风险模型规格 | [05_IMPLEMENTATION/.../BARRA_RISK_MODEL_TECHNICAL_SPECIFICATION.md](../../05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/BARRA_RISK_MODEL_TECHNICAL_SPECIFICATION.md) | 技术规格 | ✅ 保留 |

### 5. 实时风险监控

| 文档 | 路径 | 职责 | 状态 |
|------|------|------|------|
| 实时风险监控仪表板 | [01_FRAMEWORK/REALTIME_RISK_MONITORING_BLUEPRINT.md](../../01_FRAMEWORK/REALTIME_RISK_MONITORING_BLUEPRINT.md) | 框架定义 | ✅ 保留 |
| 实时风险对冲引擎 | [05_IMPLEMENTATION/.../REALTIME_RISK_HEDGE_ENGINE_BLUEPRINT.md](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/REALTIME_RISK_HEDGE_ENGINE_BLUEPRINT.md) | 实施实现 | ✅ 保留 |

### 6. 风险归因系统

| 文档 | 路径 | 职责 | 状态 |
|------|------|------|------|
| 风险归因系统蓝图 | [05_IMPLEMENTATION/.../RISK_ATTRIBUTION_SYSTEM_BLUEPRINT.md](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/RISK_ATTRIBUTION_SYSTEM_BLUEPRINT.md) | 归因框架 | ✅ 保留 |
| 风险归因系统规格 | [05_IMPLEMENTATION/.../RISK_ATTRIBUTION_SYSTEM_TECHNICAL_SPECIFICATION.md](../../05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/RISK_ATTRIBUTION_SYSTEM_TECHNICAL_SPECIFICATION.md) | 技术规格 | ✅ 保留 |

### 7. 尾部风险对冲

| 文档 | 路径 | 职责 | 状态 |
|------|------|------|------|
| 尾部风险对冲蓝图 | [05_IMPLEMENTATION/.../TAIL_RISK_HEDGING_BLUEPRINT.md](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/TAIL_RISK_HEDGING_BLUEPRINT.md) | 对冲框架 | ✅ 保留 |

### 8. 最佳实践

| 文档 | 路径 | 职责 | 状态 |
|------|------|------|------|
| 风险管理最佳实践 | [08_KNOWLEDGE/BEST_PRACTICES/RISK_MANAGEMENT_BEST_PRACTICES.md](../../08_KNOWLEDGE/BEST_PRACTICES/RISK_MANAGEMENT_BEST_PRACTICES.md) | 最佳实践 | ✅ 保留 |

---

## 📋 整合建议

### 立即行动 (P0)

1. **合并风控规则引擎文档**
   - 将 `03_TRADING_TACTICS/09_RISK_RULES/RISK_RULE_ENGINE.md` 内容合并到 `04_EXECUTION/05_RISK_ENGINE/README.md`
   - 保留 `03_TRADING_TACTICS/09_RISK_RULES/BLUEPRINT.md` 作为框架层文档
   - 更新所有引用

### 短期改进 (P1)

1. **建立清晰的文档层级关系**
   - 框架层: `01_FRAMEWORK/` - 定义架构和原则
   - 战术层: `03_TRADING_TACTICS/` - 定义规则体系
   - 执行层: `04_EXECUTION/` - 实现风控引擎
   - 实施层: `05_IMPLEMENTATION/` - 具体技术规格

2. **更新索引引用**
   - 在各文档中添加明确的上下游引用
   - 建立风险管理文档导航图

---

## 🔗 相关索引

- [系统主索引](../INDEX.md)
- [执行层索引](../04_EXECUTION/INDEX.md)
- [交易战术索引](../03_TRADING_TACTICS/README.md)

---

**最后更新**: 2026-04-04
**维护者**: 文档审计员
