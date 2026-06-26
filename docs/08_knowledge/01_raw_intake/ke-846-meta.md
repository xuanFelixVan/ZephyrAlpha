---
module_id: KE-768
title: 2. META 域（元规则）
category: governance_rule
ttl: permanent
doc_type: knowledge_entry
---

# 2. META 域（元规则）

2. META 域（元规则）

> 来源：`01_policies_and_standards/meta/`

| 登记号 | 规则内容 | 对应 ABS/COND/REC | 强制方式 | 来源路径 |
|--------|---------|------------------|---------|---------|
| META-001 | AI 禁止自主修改 immutable_core 文件 | ABS-01 | doc | `meta/behavior_boundaries_standard.yaml` |
| META-002 | AI 禁止自主删除任何文档 | ABS-02 | doc | `meta/behavior_boundaries_standard.yaml` |
| META-003 | AI 禁止自行裁决规则冲突 | ABS-03 | doc | `meta/behavior_boundaries_standard.yaml` |
| META-004 | AI 禁止忽略高优先级规则 | ABS-04 | doc | `meta/behavior_boundaries_standard.yaml` |
| META-005 | AI 禁止执行 P0 变更 | ABS-05 | doc | `meta/rule_lifecycle_and_change_standard.yaml` |
| META-006 | AI 禁止未经批准修改 P0 条款 | ABS-06 | doc | `meta/rule_lifecycle_and_change_standard.yaml` |
| META-007 | AI 禁止自行判断"紧急"并绕过审批 | ABS-07 | doc | `meta/rule_lifecycle_and_change_standard.yaml` |
| META-008 | AI 禁止修改 .cursor/rules/ | ABS-08 | doc | `meta/rule_lifecycle_and_change_standard.yaml` |
| META-009 | AI 禁止修改 AGENTS.md | ABS-09 | doc | `meta/rule_lifecycle_and_change_standard.yaml` |
| META-010 | AI 禁止修改 .roomodes | ABS-10 | doc | `meta/rule_lifecycle_and_change_standard.yaml` |
| META-011 | AI 禁止在不知道当前 Phase 的情况下开始工作 | ABS-11 | doc | `governance/ai/ai-onboarding-guide.md` |
| META-012 | AI 禁止在不知道能力边界的情况下操作文件 | ABS-12 | doc | `governance/ai/ai-onboarding-guide.md` |
| META-013 | AI 禁止跳过幻觉自检直接开始工作 | ABS-13 | doc | `governance/ai/ai-onboarding-guide.md` |
| META-014 | 禁止删除锚点文件 | ABS-14 | hook | `governance/document/trae_029_doc_operation_security.yaml` |
| META-015 | 禁止先删文件后清引用 | ABS-15 | hook | `governance/document/trae_029_doc_operation_security.yaml` |
| META-016 | 禁止使用 --no-verify 跳过 pre-commit | ABS-16 | hook | `governance/document/trae_029_doc_operation_security.yaml` |
| META-017 | 禁止不查搬迁历史直接移动文件 | ABS-17 | doc | `governance/document/trae_029_doc_operation_security.yaml` |
| META-018 | 禁止在废弃路径下写入新文件 | ABS-18 | doc | `governance/document/trae_028_doc_structure_naming.yaml` |
| META-019 | 禁止在非权威文件中修改权威字段 | ABS-19 | ci | `meta/document_structure_standard.yaml` |
| META-020 | 禁止重复定义 PS-STD-001 已定义的字段 | ABS-20 | ci | `meta/document_structure_standard.yaml` |
| META-021 | 禁止口头指令覆盖书面规则 | ABS-21 | doc | `meta/rule_classification_and_arbitration_standard.yaml` |
| META-022 | 禁止跨级降格文档状态 | ABS-22 | doc | `meta/metadata_registry.yaml` |
| META-023 | 禁止 PowerShell echo/Out-File 默认参数写 .md | ABS-23 | doc | `AGENTS.md` |
| META-024 | 禁止 Python 写文件不指定 encoding='utf-8' | ABS-24 | doc | `AGENTS.md` |
| META-025 | 禁止两个编辑器同时打开同一文件编辑 | ABS-25 | doc | `AGENTS.md` |
| META-026 | 禁止 git add . 或 git add -A | ABS-26 | hook | `governance/ai/ai-onboarding-guide.md` |
| META-027 | 禁止 git commit --no-verify | ABS-27 | hook | `governance/ai/ai-onboarding-guide.md` |
| META-028 | 禁止 git push --force | ABS-28 | hook | `governance/ai/ai-onboarding-guide.md` |
| META-029 | 禁止将密钥/API Key/Token 提交到版本控制 | ABS-29 | hook | `meta/behavior_boundaries_standard.yaml` |
| META-030 | 禁止 AI 读取并输出密钥内容到响应/日志 | ABS-30 | doc | `meta/behavior_boundaries_standard.yaml` |
| META-031 | 禁止在日志中记录密钥 | ABS-31 | ci | `meta/behavior-boundaries-standard.
