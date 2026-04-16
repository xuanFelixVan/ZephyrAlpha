---
module_id: 09_AUDIT_STANDARDS_INDEX_9137
version: 2.0.0
status: Active
created_date: 2026-04-07
last_updated: '2026-04-16'
owner: 首席文档架构师
responsibility:
- STANDARDS目录索引
layer: layer_09
standard_type: 索引文档
applicable_scope: 标准规范管理
compliance_level: 专业标准
---

## 导航

- [09_AUDIT 上级索引](../INDEX.md)

## 说明

本目录经 **2026-04-16 合并** 后固定为 **20 份**正式标准（原 34 份：主题合并与 v1 废止）。
新增 `.md` 须在本文件登记（见 pre-commit：`check_standards_index_registration.py`）。

## 标准清单（20）

| # | 文件 | 说明 |
|---|------|------|
| 1 | [adr-standard.md](adr-standard.md) | ADR 技术决策记录 |
| 2 | [audit-and-compliance-master-standard.md](audit-and-compliance-master-standard.md) | 审计 + 合规（合并原 audit-standards、compliance-audit-system） |
| 3 | [continuous-improvement-process.md](continuous-improvement-process.md) | 持续改进（已并入持续质量改进） |
| 4 | [decision-record-standard.md](decision-record-standard.md) | 决策记录 |
| 5 | [doc-governance-mechanism.md](doc-governance-mechanism.md) | 文档治理机制（合并优化提案、系统计划、流程标准） |
| 6 | [doc-naming-standard.md](doc-naming-standard.md) | 文档命名 + 文件命名附录 |
| 7 | [document-classification-standard.md](document-classification-standard.md) | 文档分类 + 例外清单 |
| 8 | [document-metadata-and-versioning-standard.md](document-metadata-and-versioning-standard.md) | 元数据模板 + 版本命名 |
| 9 | [document-repository-layout-standard.md](document-repository-layout-standard.md) | 仓库目录布局 |
| 10 | [document-responsibility-boundary-standard.md](document-responsibility-boundary-standard.md) | 职责边界 |
| 11 | [module-interface-specification.md](module-interface-specification.md) | 模块接口规格 |
| 12 | [orphan-duplicate-and-overlap-governance-standard.md](orphan-duplicate-and-overlap-governance-standard.md) | 孤儿/重复/重叠治理 |
| 13 | [path-and-reference-standard.md](path-and-reference-standard.md) | 路径 + 文档引用 |
| 14 | [periodic-audit-mechanism.md](periodic-audit-mechanism.md) | 周期性审计 + 检查计划 |
| 15 | [quality-standard.md](quality-standard.md) | 质量标准 + 质量文化 |
| 16 | [research-memo-standard.md](research-memo-standard.md) | 研究备忘录 |
| 17 | [responsibility-description-standard-v2.md](responsibility-description-standard-v2.md) | 职责描述规范（v2 为真源；v1 已废止） |
| 18 | [responsibility-template-library.md](responsibility-template-library.md) | 职责模板库 |
| 19 | [risk-management-framework.md](risk-management-framework.md) | 风险管理框架 |
| 20 | [testing-and-defect-prevention-standard.md](testing-and-defect-prevention-standard.md) | 测试驱动治理 + 缺陷预防 |

## 合并记录（供追溯）

| 废止/合并前文件名 | 并入目标 |
|-------------------|----------|
| responsibility-description-standard.md | responsibility-description-standard-v2.md |
| continuous-quality-improvement-process.md | continuous-improvement-process.md |
| doc-governance-optimization-proposal.md 等 3 份 | doc-governance-mechanism.md |
| periodic-check-plan.md | periodic-audit-mechanism.md |
| doc-quality-culture-plan.md | quality-standard.md |
| test_driven_governance_standard.md, document-defect-prevention-standard.md | testing-and-defect-prevention-standard.md |
| duplicate-document-handling-standard.md, doc-orphan-and-duplicate-governance-playbook.md | orphan-duplicate-and-overlap-governance-standard.md |
| audit-standards.md, compliance-audit-system.md | audit-and-compliance-master-standard.md |
| file-naming-standard.md | doc-naming-standard.md |
| document-metadata-template.md, document-version-naming-standard.md | document-metadata-and-versioning-standard.md |
| path-reference-standard.md, doc-reference-standard.md | path-and-reference-standard.md |
| document-classification-exception-list.md | document-classification-standard.md |

<!-- orphan-link -->
- [doc-governance-system-plan](doc-governance-system-plan.md)

<!-- orphan-link -->
- [document-governance-process-standard](document-governance-process-standard.md)
