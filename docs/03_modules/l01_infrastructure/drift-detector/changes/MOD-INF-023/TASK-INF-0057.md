---
task_id: "TASK-INF-0057"
title: "命名约定与魔数字符串漂移 naming_magic_checker.py（D-023-38）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P1"
status: "draft"
estimated_effort: "4h"
depends_on: ["TASK-INF-0002"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\naming_magic_checker.py"]
acceptance_criteria:
  - naming: verb_synonym_drift get/fetch/retrieve归一化
  - case_style_drift snake vs camel混用>10% auto_fixable
  - prefix_suffix_inconsistency
  - magic_string: duplicated_string_literal >10字符>=3文件 EXTRACT_CONSTANT
  - near_duplicate_constant 语义相同值不同 MERGE_CONSTANT
rollback_instructions: "git checkout src/zephyr/drift_detector/naming_magic_checker.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§6.27"]}]
tags: ["drift-detector","decision","§6.27"]
---
# TASK-INF-0057: 命名约定与魔数字符串漂移 naming_magic_checker.py（D-023-38）
对标 §6.27。naming: verb_synonym_drift get/fetch/retrieve归一化
