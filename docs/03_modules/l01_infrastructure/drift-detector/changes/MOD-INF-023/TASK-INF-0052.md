---
task_id: "TASK-INF-0052"
title: "Python版本兼容性漂移检测 python_compat.py（D-023-30）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P1"
status: "draft"
estimated_effort: "4h"
depends_on: ["TASK-INF-0002"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\python_compat.py"]
acceptance_criteria:
  - syntax_incompatibility: pyright/mypy目标Python版本类型检查
  - stdlib_import_incompatibility: 扫描import vs目标版本标准库
  - type_hint_incompatibility: X|Y vs Union[X,Y]
  - auto_fixable自动降级语法
rollback_instructions: "git checkout src/zephyr/drift_detector/python_compat.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§6.22"]}]
tags: ["drift-detector","decision","§6.22"]
---
# TASK-INF-0052: Python版本兼容性漂移检测 python_compat.py（D-023-30）
对标 §6.22。syntax_incompatibility: pyright/mypy目标Python版本类型检查
