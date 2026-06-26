---
module_id: KE-2120-------mod-inf-018-----000
status: active
title: 3.4 RBAC 集成（对接 MOD-INF-018）——每 Skill 级权限
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 3.4 RBAC 集成（对接 MOD-INF-018）——每 Skill 级权限

3.4 RBAC 集成（对接 MOD-INF-018）——每 Skill 级权限

```yaml
skill_rbac:
  description: "每个 Skill 有自己的 allowed-tools，遵循 agentskills.io 标准"
  permission_levels:
    read_only:
      tools: [Read, Grep, Glob, Bash(readonly), mcp__context_retrieval]
      example: "drift-detector, coordinate-wizard"
    code_modify:
      tools: [Read, Grep, Glob, Edit, Write, Bash]
      example: "database-specialist, mcp-specialist"
    admin:
      tools: [Read, Grep, Glob, Edit, Write, Bash, Execute]
      example: "governor(role), implementer(role)"
  enforcement: "SkillLoader 在加载 Skill 时检查 allowed-tools → 将限制注入 AGENTS.md 上下文"
```
