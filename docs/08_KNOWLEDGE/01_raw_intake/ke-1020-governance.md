---
module_id: KE-941
title: 5.1 受控词表
category: governance_rule
ttl: permanent
---

# 5.1 受控词表

5.1 受控词表

| 值 | 含义 | 影响范围 | 示例 |
|---|------|---------|------|
| `global` | 全局——影响项目中所有文件、所有 session | 整个项目 | PS-STD-001, PS-STD-002, PS-STD-003 |
| `domain` | 领域——影响某个领域下的所有文件 | 一个领域 | trae_028_doc_structure_naming.yaml（影响所有文档的命名） |
| `module` | 模块——影响特定模块 | 一个或几个模块 | module-injection-rules-policy.md |
| `session` | 会话——仅影响当前 AI session | 单个 session | vibe-coding-session-state-runbook.md |
