---
task_id: "TASK-INF-0030"
title: "Git Bisect 溯源集成 git_bisector.py（D-023-15）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P1"
status: "draft"
estimated_effort: "5h"
depends_on: ["TASK-INF-0004"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\git_bisector.py"]
acceptance_criteria:
  - "trigger: DETECTED事件(非周期性漂移)→自动bisect"
  - "scope_narrowing: last_known_good(上次DEEP PASS commit) → first_known_bad(HEAD); >50 commits提示Owner"
  - "automation: git bisect start→每step跑触发detector→PASS=good/FAIL=bad→定位commit"
  - "output: root_cause_commit+author+message+changed_files+ai_session_hint"
  - "bisect_cache: detector×commit结果永久缓存"
rollback_instructions: "git checkout src/zephyr/drift_detector/git_bisector.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§5.6"]}]
tags: ["drift-detector","git-bisect","root-cause","D-023-15"]
---
# TASK-INF-0030: Git Bisect 溯源（D-023-15）
对标 §5.6。实现bisect自动定位+scope缩小(last_good→bad)+结果输出(root_cause+author+session_hint)+永久缓存。
