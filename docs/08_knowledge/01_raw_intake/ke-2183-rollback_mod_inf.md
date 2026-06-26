---
module_id: KE-2090-------mod-inf-021-003
status: active
title: 3.2 Rollback 集成（对接 MOD-INF-021）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 3.2 Rollback 集成（对接 MOD-INF-021）

3.2 Rollback 集成（对接 MOD-INF-021）

一个 Skill 执行 = 一个 Checkpoint 单位：

```yaml
skill_checkpoint:
  rule: "Skill 加载前自动创建 Checkpoint，Skill 卸载时如果门禁 FAIL 则自动回滚"
  checkpoint_name_format: "skill_{skill_id}_{timestamp}"
  rollback_trigger:
    - "Skill 执行后门禁 FAIL（G0-G7 任一）"
    - "Skill 执行产出的代码导致下游测试 FAIL"
    - "Skill 执行中 AI 主动请求回滚"
  post_rollback_action: "降级 Skill 的 freshness_score → 触发人工审查"
```
