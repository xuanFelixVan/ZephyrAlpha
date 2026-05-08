---
task_id: "TASK-INF-0055"
title: "基线投毒防护 baseline_poisoning_guard.py（D-023-36）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P1"
status: "draft"
estimated_effort: "4h"
depends_on: ["TASK-INF-0002"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\baseline_poisoning_guard.py"]
acceptance_criteria:
  - cross_validation: 基线快照vs git对应commit原始代码diff 每DEEP scan抽样10%
  - multi_baseline_voting: 保留3版本>=2基线同意
  - git_as_ultimate_truth: baseline_hash_chain=SHA256(prev+current)写入commit message
  - integrity_manifest: 每DEEP scan签名存Git
rollback_instructions: "git checkout src/zephyr/drift_detector/baseline_poisoning_guard.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§6.25"]}]
tags: ["drift-detector","decision","§6.25"]
---
# TASK-INF-0055: 基线投毒防护 baseline_poisoning_guard.py（D-023-36）
对标 §6.25。cross_validation: 基线快照vs git对应commit原始代码diff 每DEEP scan抽样10%
