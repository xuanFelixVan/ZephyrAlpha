---
module_id: CONSTRUCTION_MASTER_PLAN_001
version: 1.0.0
status: Active
created_date: '2026-04-16'
last_updated: '2026-04-16'
owner: 仓库 Owner
standard_type: 施工主计划
applicable_scope: Phase 2 施工图设计（L00-L07 + Shared）
compliance_level: P0-CRITICAL
priority: P0
layer: cross_layer
parent_document: ./INDEX.md
related_documents:
  - '../../02_FACTOR_LIBRARY/04_DATA_SOURCE/INDEX.md'
  - './CONSTRUCTION_PLAN_L00_DATA_SOURCE.md'
responsibility:
  - Phase 2 施工图设计进度唯一真源
  - 架构冲突裁决（L04 独立性、L06 蓝图真源）
---

# ZephyrAlpha 施工主计划（Phase 2 施工图设计）

> **注意**：本文档是 Phase 2 施工图阶段的 **唯一真源**。施工图覆盖范围、层优先级或 ADR 变更须先更新本文档，再同步下游。

## 1. 阶段状态

| 阶段 | 状态 |
|------|------|
| Phase 1 蓝图 | 已冻结 |
| Phase 2 施工图 | **进行中** |
| Phase 3 代码实现 | 锁定（待 Phase 2 验收） |

## 2. Phase 2 任务清单（验收：每层 1 张施工图 + Owner 复核）

| 任务 ID | 层 | 状态 | 施工图文件 |
|---------|-----|------|------------|
| P2.1 | L00 数据基础设施 | [x] 初稿已建 | [CONSTRUCTION_PLAN_L00_DATA_SOURCE.md](CONSTRUCTION_PLAN_L00_DATA_SOURCE.md) |
| P2.2 | L01 数据处理 | [ ] | CONSTRUCTION_PLAN_L01_DATA_PROCESSING.md |
| P2.3 | L02 特征工程 | [ ] | CONSTRUCTION_PLAN_L02_FEATURE_ENGINEERING.md |
| P2.4 | L03 信号生成 | [ ] | CONSTRUCTION_PLAN_L03_SIGNAL_GENERATION.md |
| P2.5 | L04 风险管理 | [ ] | CONSTRUCTION_PLAN_L04_RISK_MANAGEMENT.md |
| P2.6 | L05 组合构建 | [ ] | CONSTRUCTION_PLAN_L05_PORTFOLIO_CONSTRUCTION.md |
| P2.7 | L06 交易执行 | [ ] | CONSTRUCTION_PLAN_L06_TRADE_EXECUTION.md |
| P2.8 | L07 交易后分析 | [ ] | CONSTRUCTION_PLAN_L07_POST_TRADE_ANALYTICS.md |
| P2.9 | Cross-Layer | [ ] | CONSTRUCTION_PLAN_SHARED.md |

**建议施工顺序**（与 ADR-D1-003 一致）：L00 → L03 → L04 → L06 → L01 → L02 → L05 → L07 → Shared。

## 3. ADR（节选，全文以施工图与 ARCHITECTURE 为准）

### ADR-D1-001：L04 风险管理层独立

- L04 须独立施工图；L05 不得包含 VaR/CVaR 核心计算与止损引擎（仅消费 L04 限额）。

### ADR-D1-002：L06 蓝图真源

- 执行层施工图覆盖 QMT/OMS/SOR；真源蓝图以 `docs/03_BLUEPRINTS/L06_TRADE_EXECUTION/` 中裁决文件为准。

## 4. 施工图格式（每张必含）

1. 前置条件（依赖蓝图、输入数据契约）
2. 模块分解（3–8 个可独立施工单元）
3. 公共 API：函数签名、类型、异常（Python type hints）
4. 数据流（可 mermaid）
5. 测试：每模块至少 3 条 P0 用例思路
6. 技术选型与 TDR 引用
7. 已知风险与缓解

## 5. 变更历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-04-16 | 初版；P2.1 L00 施工图落盘 |
