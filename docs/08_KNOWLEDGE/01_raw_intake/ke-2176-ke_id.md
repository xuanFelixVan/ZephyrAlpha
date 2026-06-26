---
module_id: KE-2084
status: active
title: 3.2.1 KE ID 格式裁决
category: module_blueprint
ttl: permanent
---

# 3.2.1 KE ID 格式裁决

3.2.1 KE ID 格式裁决

> **历史冲突**：代码 `kb_repo.py` 使用 `KE-{NNN}`（3位数字），早期 schema 草案用 `KMS-{YYYYMMDD}-{SEQ}`。经 `知识库专题讨论文档.md` §KB-024 裁定：

- **最终格式**：`KE-{NNN}`（NNN = 3位递增编号，如 KE-001、KE-042）
- **裁决理由**：简短+机器可消费+与 `KMS-` 前缀冲突时已代码实现的事实为准（代码 = 最终仲裁者）
- **与 task_id 格式的关系**：KE ID ≠ task_id。KE 有独立的 `KE-{NNN}` 格式；KB 施工任务用 MOD-TASK_SYSTEM 的 `{NAMESPACE}-{SEQ}` 格式（如 `KB-INF-0001`）。
