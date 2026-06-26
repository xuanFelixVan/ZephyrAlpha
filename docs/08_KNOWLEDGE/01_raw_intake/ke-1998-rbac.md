---
module_id: KE-1907
status: active
title: 2.4 RBAC 集成
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.4 RBAC 集成

2.4 RBAC 集成

```yaml
permission_levels:
  read_only: {tools: [Read, Grep, Glob, Bash(readonly), mcp__context_retrieval], example: "drift-detector"}
  code_modify: {tools: [Read, Grep, Glob, Edit, Write, Bash], example: "database-specialist"}
  admin: {tools: [Read, Grep, Glob, Edit, Write, Bash, Execute], example: "governor, implementer"}
enforcement: "SkillLoader 加载时检查 allowed-tools → 注入 AGENTS.md 上下文"
```
