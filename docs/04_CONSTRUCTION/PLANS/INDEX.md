---
module_id: CONSTRUCTION_PLANS_INDEX_001
version: 1.1.0
status: Active
created_date: '2026-04-16'
last_updated: '2026-04-16'
owner: 仓库 Owner
standard_type: 施工计划目录索引
applicable_scope: Phase 2 施工图设计
parent_document: ../INDEX.md
related_documents:
  - './MASTER_DEVELOPMENT_PLAN.md'
  - '../../02_FACTOR_LIBRARY/04_DATA_SOURCE/INDEX.md'
layer: cross_layer
priority: P0
---

# 施工计划索引（`docs/04_CONSTRUCTION/PLANS/`）

> **Phase 2 状态**：1/9 施工图已完成初稿（P2.1 L00）。建议施工顺序：L00 → L03 → L04 → L06 → L01 → L02 → L05 → L07 → Shared（见 ADR-D1-003）。

## 主计划

| 文档 | 说明 |
|------|------|
| [MASTER_DEVELOPMENT_PLAN.md](MASTER_DEVELOPMENT_PLAN.md) | Phase 2 施工主计划（**唯一真源**，每次 session 必读） |

## 各层施工图（P2.1 ~ P2.9）

| 任务 ID | 状态 | 施工图文件 | 说明 |
|---------|------|------------|------|
| P2.1 | ✅ 初稿已建 | [CONSTRUCTION_PLAN_L00_DATA_SOURCE.md](CONSTRUCTION_PLAN_L00_DATA_SOURCE.md) | L00 数据基础设施（采集/存储/缓存/质量门禁） |
| P2.2 | ⬜ 待创建 | `construction-plan-l01-data-processing.md` | L01 数据处理（清洗/复权/对齐/特征预处理） |
| P2.3 | ⬜ 待创建 | `construction-plan-l02-feature-engineering.md` | L02 特征工程（因子计算/标准化/选择） |
| P2.4 | ⬜ 待创建 | `construction-plan-l03-signal-generation.md` | L03 信号生成（策略逻辑/信号组合/回测接口） |
| P2.5 | ⬜ 待创建 | `construction-plan-l04-risk-management.md` | L04 风险管理（VaR/CVaR/止损/限额，**独立层**） |
| P2.6 | ⬜ 待创建 | `construction-plan-l05-portfolio-construction.md` | L05 组合构建（优化器/权重分配/再平衡） |
| P2.7 | ⬜ 待创建 | `construction-plan-l06-trade-execution.md` | L06 交易执行（QMT/OMS/SOR，见 ADR-D1-002） |
| P2.8 | ⬜ 待创建 | `construction-plan-l07-post-trade-analytics.md` | L07 交易后分析（归因/绩效/报告） |
| P2.9 | ⬜ 待创建 | `construction-plan-shared.md` | Cross-Layer 共享（公共契约/类型/异常/日志） |

## Trae Prompt 模板

| 文件 | 用途 |
|------|------|
| [trae-prompt-file-elimination-pipeline.md](trae-prompt-file-elimination-pipeline.md) | Pipeline A 文件消除流水线 Trae 提示词 |
| [trae-prompt-blueprint-safety-pipeline.md](trae-prompt-blueprint-safety-pipeline.md) | Pipeline B 蓝图安全流水线 Trae 提示词 |
| [trae-prompt-git-history-pipeline.md](trae-prompt-git-history-pipeline.md) | Pipeline C Git 历史知识挖掘 Trae 提示词 |

<!-- orphan-link -->
- [trae-session-wave1-openclaw](trae-session-wave1-openclaw.md)
