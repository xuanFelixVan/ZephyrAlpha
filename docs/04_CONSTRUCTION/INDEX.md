---
module_id: CONSTRUCTION_INDEX
version: 1.2.0
status: Active
created_date: 2026-04-13
last_updated: 2026-04-16
owner: 仓库 Owner
standard_type: 施工阶段目录索引
applicable_scope: Phase 2 施工图设计（docs/04_CONSTRUCTION/）
compliance_level: 强制标准
priority: P0-CRITICAL
layer: cross_layer
responsibility:
  - 施工阶段所有文档的导航入口
  - 新 AI 模型了解施工进度的首要入口
---

# 施工阶段目录索引（`docs/04_CONSTRUCTION/`）

> **当前阶段**：Phase 2 施工图设计，进行中（1/9 完成）。
> **P0 必读**：每次 session 开始必须读取 [MASTER_DEVELOPMENT_PLAN.md](PLANS/MASTER_DEVELOPMENT_PLAN.md)。

## 子目录

| 目录 | 说明 |
|------|------|
| [PLANS/](PLANS/INDEX.md) | 施工主计划 + 各层施工图 + Trae Prompt 模板 |

## 关键文档直达链接

| 文档 | 重要性 | 说明 |
|------|--------|------|
| [PLANS/MASTER_DEVELOPMENT_PLAN.md](PLANS/MASTER_DEVELOPMENT_PLAN.md) | **P0 必读** | Phase 2 施工进度唯一真源，列出全部 9 个施工任务状态 |
| [PLANS/INDEX.md](PLANS/INDEX.md) | P0 | 施工图全部条目索引（含待创建文件清单） |
| [PLANS/CONSTRUCTION_PLAN_L00_DATA_SOURCE.md](PLANS/CONSTRUCTION_PLAN_L00_DATA_SOURCE.md) | P0 | L00 数据基础设施施工图（当前唯一已建初稿） |

## Phase 2 整体进度快照

| 层 | 状态 | 施工图 |
|----|------|--------|
| L00 数据基础设施 | ✅ 初稿 | `CONSTRUCTION_PLAN_L00_DATA_SOURCE.md` |
| L01 数据处理 | ⬜ 待建 | — |
| L02 特征工程 | ⬜ 待建 | — |
| L03 信号生成 | ⬜ 待建 | — |
| L04 风险管理 | ⬜ 待建 | — |
| L05 组合构建 | ⬜ 待建 | — |
| L06 交易执行 | ⬜ 待建 | — |
| L07 交易后分析 | ⬜ 待建 | — |
| Cross-Layer Shared | ⬜ 待建 | — |

> **提示**：Phase 3 代码实现已锁定，待 Phase 2 全部 9 张施工图通过 Owner 复核后解锁。
