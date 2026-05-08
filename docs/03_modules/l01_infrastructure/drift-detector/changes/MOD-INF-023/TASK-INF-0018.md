---
task_id: "TASK-INF-0018"
title: "符号链接与子模块完整性检查 symlink_checker.py（D-023-26）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P1"
status: "draft"
estimated_effort: "3h"
depends_on: ["TASK-INF-0001"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\symlink_checker.py"]
acceptance_criteria:
  - "symlink: broken_symlink(os.path.islink+os.path.exists)、symlink_target_change(baseline SHA256对比)、circular_symlink(链跟踪防A→B→C→A)"
  - "submodule: dirty_submodule(git submodule status '+'前缀)、out_of_sync(.gitmodules commit hash vs 实际HEAD)、uninitialized('-'前缀)"
  - "policy: 项目符号链接应声明在YAML注册表symlinks字段"
rollback_instructions: "git checkout src/zephyr/drift_detector/symlink_checker.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§2.17"]}]
tags: ["drift-detector","symlink","submodule","D-023-26"]
---
# TASK-INF-0018: 符号链接与子模块完整性（D-023-26）
对标 §2.17。实现 symlink 三检查(断裂/目标变更/循环) + submodule 三检查(dirty/out-of-sync/uninitialized)。
