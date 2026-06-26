---
module_id: KE-2435
status: active
title: 7.2 Session Resume 协议模板
category: module_blueprint
ttl: permanent
---

# 7.2 Session Resume 协议模板

7.2 Session Resume 协议模板

```yaml
session_resume_protocol:
  description: "Skill 卸载时必须在 Session Log 中留下结构化交接信息"
  required_fields:
    skill_id: "最后执行的 Skill ID"
    completion_stage: "执行到了 Phase N / N 个阶段"
    last_action: "最后一步具体做了什么"
    next_action: "下一个 session 应该从哪一步继续"
    known_issues: "执行过程中发现的未解决问题"
    gate_results: "门禁结果总结（G0-G7 PASS/FAIL）"
    suggested_domain_skill: "推荐下一个 session 加载的 Domain Skill"

  session_log_location: "docs/06_logs/session_logs/session_{timestamp}.yaml"
```
