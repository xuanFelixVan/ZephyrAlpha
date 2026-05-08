---
module_id: KE-module_blu-2_2_rollback-003
title: 2.2 Rollback 集成
category: module_blueprint
---

# 2.2 Rollback 集成

2.2 Rollback 集成

```yaml
skill_checkpoint:
  rule: "Skill 加载前自动创建 Checkpoint, Skill 卸载时门禁 FAIL 自动 rollback"
  checkpoint_name_format: "skill_{skill_id}_{timestamp}"
  rollback_trigger:
    - "Skill 执行后门禁 FAIL (G0-G7 任一)"
    - "Skill 产出代码导致下游测试 FAIL"
    - "Skill 执行中 AI 主动请求回滚"
  post_rollback_action: "降级 Skill freshness_score → 触发人工审查"
```
