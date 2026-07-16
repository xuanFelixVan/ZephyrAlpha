---
ttl: task_bound
completes_when: _working 目录被清空或重构
---

# _working 工作区索引

> **语义**：本目录只保留**进行中**的任务文档。已完成（task_bound + completes_when 满足）的文档必须归档到 `docs/_archive/`。
>
> **命名规则**：根目录文件统一使用 `YYYY-MM-DD-<topic>.md` 前缀；子目录按任务类别组织。

## 进行中文档（根目录）

| 文件 | 创建日期 | 状态 | completes_when |
|------|----------|------|----------------|
| `2026-07-10-panorama_remaining_7_issues_remediation.md` | 2026-07-10 | spec | ARCH-056 剩余7问题治本方案落地 |
| `2026-07-10-panorama_remaining_7_plan.md` | 2026-07-10 | plan | ARCH-056 计划落地 |
| `2026-07-13-tick-subscriber-plan.md` | 2026-07-13 | plan | tick-subscriber 施工完成 |
| `domain_split_proposal_d_governance_d_trading.md` | 2026-07-12 | 待审批 | 域拆分方案审批并落地 |
| `handoff_llm_security_15fail.md` | 2026-06-xx | 进行中 | llm_security 15 个失败测试修复任务结案 |
| `hyperv_clickhouse_migration_2026_07_15.md` | 2026-07-15 | 待授权 | Hyper-V 迁移施工授权 |
| `phase1_baseline.md` | 2026-07-12 | baseline | Phase 1 完成归档 |
| `trae_060_s5_evidence_audit.md` | 2026-06-26 | 审计报告 | Owner 审阅并决定是否修订 trae_060.yaml |

## 子目录

| 子目录 | 用途 | 文件数 |
|--------|------|--------|
| `module_migration/` | 模块迁移任务卡 | 6 |
| `p2_review_reports/` | P2 评审报告 | 1 |
| `research_notes/` | 研究笔记 | 4 |

## 已归档文档（2026-07-16 退役）

> 注：以下文档已完成退役，原路径不再存在。列此仅作历史记录，不可作为活跃引用。

| 原名称 | 归档原因 | 归档位置 |
|--------|----------|----------|
| ghost_commit_automation_assessment | 评估完成（completes_when 满足） | _archive |
| 2026-07-15-panorama_orphan_governance_spec | ARCH-057 spec 已落地 | _archive |
| TASK-OPS-2026062501（原 module_migration 子目录） | status=COMPLETED | _archive |
| 2026-07-15-panorama_orphan_governance_plan | ARCH-057 四图孤儿治理已完成 | _archive |
| hyperv_migration_impact_inventory | 迁移完成并归档 | _archive |
| 03_governance_reports 目录索引 | 引用断裂（9个文档不存在），目录已删除 | 已删除 |

## AI 使用方式

1. 新 AI 进入 `_working/` 时先读本 `index.md` 了解进行中任务
2. 创建新文档时使用 `YYYY-MM-DD-<topic>.md` 命名前缀
3. 文档完成（completes_when 满足）后移动到 `docs/_archive/` 并更新本索引
