---
module_id: BLUEPRINT_ARCHITECTURE_MAPPING_001
version: 1.1.0
status: Active
created_date: 2026-04-02
last_updated: '2026-04-08'
owner: 首席文档架构师
standard_type: 架构映射文档
applicable_scope: 业务时间框架与 Layer 0-11 技术流水线对照
compliance_level: 专业标准
parent_document: ./ARCHITECTURE.md
responsibility:
  - 维护业务视角与技术 Layer 映射，并与 ARCHITECTURE.md 一致
---

# 蓝图与架构映射（BLUEPRINT_ARCHITECTURE_MAPPING）

> **核心职责**：说明 **三级时间框架（业务决策）** 与 **Layer 0～11（技术流水线）** 的对应关系。  
> **权威顺序**：与 [ARCHITECTURE.md](./ARCHITECTURE.md) 冲突时，**以 ARCHITECTURE.md 为准**。  
> **职责边界**：回测链上因子 / 策略 / 引擎分工见 [MODULE_RESPONSIBILITY_BOUNDARIES.md](./MODULE_RESPONSIBILITY_BOUNDARIES.md)。

---

## 1. 双重架构体系

| 类型 | 文档 | 用途 |
|------|------|------|
| 业务架构 | [PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md](./PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md) | 宏观 / 中观 / 微观决策与策略划分 |
| 技术架构 | [ARCHITECTURE.md](./ARCHITECTURE.md) | Layer 0～11、数据流、模块分层 |

### 1.1 场景选型

| 场景 | 优先阅读 |
|------|----------|
| 策略与时间框架划分 | 三级时间框架架构 |
| Layer 编号、数据流、顶层模块 | ARCHITECTURE.md |
| 因子库 / 策略引擎 / 回测引擎谁做什么 | MODULE_RESPONSIBILITY_BOUNDARIES.md |

---

## 2. 时间框架 ↔ Layer 对照摘要

| 业务视角（示意） | 主要 Layer | 说明 |
|------------------|------------|------|
| 数据与预处理 | Layer 0～1 | 数据源、清洗、对齐 |
| Alpha 与特征 | Layer 2 | 因子计算与因子库 |
| 舆情与事件 | Layer 3 | 情感 / 事件信号（通常由 Layer 5 策略消费） |
| 机器学习 | Layer 4 | ML / AI 因子与预测 |
| 策略与执行 | Layer 5 | 策略逻辑、信号、下单路径 |
| 组合优化 | Layer 6 | 权重、约束、优化 |
| 报告与交互 | Layer 7～8 | AI 报告、人机协同 |
| 研究 / 治理 / 战略 | Layer 9～11 | 见 ARCHITECTURE 与各层主蓝图 |

---

## 3. 技术规格书入口（示例）

| 主题 | 文档 |
|------|------|
| 智能执行 | [SMART_EXECUTION_ENGINE_TECHNICAL_SPECIFICATION.md](../05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/SMART_EXECUTION_ENGINE_TECHNICAL_SPECIFICATION.md) |
| 市场冲击 | [MARKET_IMPACT_MODEL_TECHNICAL_SPECIFICATION.md](../05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/MARKET_IMPACT_MODEL_TECHNICAL_SPECIFICATION.md) |
| QMT 数据接口 | [QMT_DATA_INTERFACE_TECHNICAL_SPECIFICATION.md](../05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/QMT_DATA_INTERFACE_TECHNICAL_SPECIFICATION.md) |

---

## 4. 治理与同步

- 新增或重命名蓝图 / 规格书后，应在本文件或 [ARCHITECTURE.md](./ARCHITECTURE.md) 「相关文档」中 **至少一处** 可点击到达。  
- 架构级缺口与矛盾登记：[ARCH_MODULE_GAP_REGISTER_20260408.md](../09_AUDIT/STATE/ARCH_MODULE_GAP_REGISTER_20260408.md)。  
- 执行方案：[ARCHITECTURE_MODULE_AUDIT_AND_GAP_PLAN_20260408.md](../09_AUDIT/PROCEDURES/ARCHITECTURE_MODULE_AUDIT_AND_GAP_PLAN_20260408.md)。

---

**版本**: v1.1 | **更新**: 2026-04-08 | **状态**: Active
