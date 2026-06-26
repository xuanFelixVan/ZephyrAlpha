---
module_id: KE-2442
status: active
title: 7.3 Skill Diff 基线
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 7.3 Skill Diff 基线

7.3 Skill Diff 基线

```yaml
skill_diff_baseline:
  description: "每次 Skill 被修改后，自动生成 diff summary"
  format: |
    - Skill: {skill_id}
    - 变更步骤: 步骤3 从 "跑 pytest" 改为 "跑 pytest + ruff"
    - 变更原因: ruff 检查 2026-05-05 才进入 CI 管线
    - 变更者: human/AI（标注）
    - 关联蓝图变更: MOD-INF-XXX version X.Y.Z → A.B.C
  storage: "skills/domain/{module}/changelog.yaml"
  purpose: "1 人维护时快速理解 Skill 变更历史——不需要回溯 git log"
```
