---
module_id: KE-MODULE-BLU-FIX-PLAN-YAML-AUTO-FIXER-PY-000
status: active
title: fix_plan.yaml —— auto_fixer.py 生成，引擎崩溃后恢复的依据
category: module_blueprint
---

# fix_plan.yaml —— auto_fixer.py 生成，引擎崩溃后恢复的依据

fix_plan.yaml —— auto_fixer.py 生成，引擎崩溃后恢复的依据
plan:
  plan_hash: "sha256:abc123def456..."
  dup_id: "DUP-20260505-012"
  status: "in_progress"                    # preflight | in_progress | completed | recovered
  created_at: "2026-05-05T16:00:00Z"
  steps:
    - step: 1
      action: "CREATE_FILE"
      file: "src/zephyr/shared/time_utils.py"
      expected_sha256: "sha256:111..."
      depends_on: []
      completed: true
    - step: 2
      action: "MODIFY_FILE"
      file: "src/zephyr/factor/factor_registry.py"
      expected_sha256: "sha256:222..."
      depends_on: [1]
      completed: false                     # ← 崩溃发生在这里——step 1 已执行，step 2 未执行
      diff: |
        -from .time_utils import _now_iso
        +from zephyr.shared.time_utils import now_iso
  crash_marker: "checkpoint saved at fix_checkpoint_abc123def456.tar.gz"
  completion_marker: null                  # ← null = 未完成——引擎下次启动自动 recover
```
