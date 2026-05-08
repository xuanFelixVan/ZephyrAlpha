---
task_id: "DB-025-0092"
namespace: "OPS"
seq: 92
title: "蓝图编写铁律自检——10条铁律逐条复核验证任务卡"
status: "PENDING"
priority: "P1"
phase: 0
execution_model: "deepseek-v4-pro"
fallback_model: "glm-4.7"
safety_level: "medium"
directive: "verify_self_check"
idempotent: true
classification: "confidential"
evolution_policy: "immutable"
estimate_hours: 0.5
actual_hours: 0
tags: ["fn:governance", "ly:cross_layer", "st:active", "mo:manual"]
depends_on: ["DB-025-0001"]
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md"
acceptance_criteria:
  - "铁律1 所有路径必须是绝对路径：§6完整路径索引已验证为D:\\绝对路径"
  - "铁律2 必备链接不可省略：§0必备链接8/8由DB-025-0012验证"
  - "铁律3 蓝图是最终设计结果：蓝图不记录决策过程，由变更记录跟踪历史"
  - "铁律4 产出物路径与GOV-DOC-002一致：已对齐"
  - "铁律5 涉及文件范围必须明确列出：§6完整文件清单由DB-025-0014/0020-0022验证"
  - "铁律6 容量估算必须写：§13容量估算由DB-025-0061-0063验证"
  - "铁律7 迁移/废弃方案必须写：§11迁移指南由DB-025-0059-0060验证"
  - "铁律8 禁止模糊词：全文无\"待定\"\"建议\"等模糊词"
  - "铁律9 蓝图必须自包含：CT-DB-*合同内嵌于§12"
  - "铁律10 安全删除协议：无删除型变更"
  - "10/10铁律全部✅"
rollback_instructions: "若任一铁律不满足→登记到§20风险矩阵追加条目不修改蓝图正文"
context_assembly_manifest:
  - {file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md", reason: "蓝图铁律自检表所在位置"}
upstream_files_content_hash: null
allowed_touch: []
forbidden_touch: []
applicable_rules: []
completed_gates: []
blocked_gates: {}
assigned_pipeline: "B"
pipeline_modules: ["M7"]
ai_autonomy_level: "supervised"
construction_status: "pending"
verification_status: "unverified"
parent_task_id: null
epic: "MOD-INF-012-database-v2.2-decomposition"
effective_priority: "P1"
diff_plan_required: false
estimated_context_tokens: 3000
context_window_limit: 128000
---

# DB-025-0092：蓝图编写铁律自检——10条铁律逐条复核验证

本任务对应blueprint.md第52−66行的蓝图编写铁律自检表，对10条铁律逐条复核确认。

| # | 铁律 | 蓝图声明 | 任务卡验证 |
|---|------|:---:|---------|
| 1 | 所有路径必须是绝对路径 | ✅ | §6完整路径索引→DB-025-0020~0022 |
| 2 | 必备链接不可省略 | ✅ | §0必备链接→DB-025-0012 |
| 3 | 蓝图是最终设计结果 | ✅ | 不记录决策过程 |
| 4 | 产出物路径与GOV-DOC-002一致 | ✅ | 已对齐 |
| 5 | 涉及文件范围必须明确列出 | ✅ | §6文件清单→DB-025-0014 |
| 6 | 容量估算必须写 | ✅ | §13→DB-025-0061~0063 |
| 7 | 迁移/废弃方案必须写 | ✅ | §11→DB-025-0059~0060 |
| 8 | 禁止模糊词 | ✅ | 无"待定""建议"等 |
| 9 | 蓝图必须自包含 | ✅ | CT-DB-*内嵌§12 |
| 10 | 安全删除协议 | ✅ | 无删除型变更 |

## 验收标准

- [ ] 10/10铁律全部验证通过
- [ ] 任一失败→§20追加R*风险条目

## 回滚方案

铁律不满足→不修改蓝图正文，登记到§20风险矩阵追加条目。
