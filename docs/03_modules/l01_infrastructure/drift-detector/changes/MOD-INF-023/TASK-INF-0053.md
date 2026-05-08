---
task_id: "TASK-INF-0053"
title: "向后兼容策略漂移检测 backcompat_checker.py（D-023-31）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P1"
status: "draft"
estimated_effort: "4h"
depends_on: ["TASK-INF-0002"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\backcompat_checker.py"]
acceptance_criteria:
  - removed_parameter: 基线(a,b,c)vs当前(a,b) c被移除
  - changed_return_type: Optional[X]X
  - renamed_function: Jaccard搜索相似签名
  - changed_exception: ValueErrorCustomError
  - impact_analysis: 扫描调用方BREAKING_CHANGE_REPORT
  - INTENTIONAL_BREAK标记
rollback_instructions: "git checkout src/zephyr/drift_detector/backcompat_checker.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§6.23"]}]
tags: ["drift-detector","decision","§6.23"]
---
# TASK-INF-0053: 向后兼容策略漂移检测 backcompat_checker.py（D-023-31）
对标 §6.23。removed_parameter: 基线(a,b,c)vs当前(a,b) c被移除
