---
task_id: "TASK-INF-0017"
title: "孤儿资源检测 orphan_scanner.py（D-023-25）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P1"
status: "draft"
estimated_effort: "4h"
depends_on: ["TASK-INF-0001"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\orphan_scanner.py"]
acceptance_criteria:
  - "scope: docs/03_modules/ + scripts/governance/ + src/zephyr/(排除.git+data+__pycache__+*.pyc)"
  - "true_orphan: 文件不在YAML注册表+不被import引用+不在.gitignore豁免 → 清理建议(>7天未修改)"
  - "undocumented_asset: 被import引用但不在YAML注册表 → YAML补全建议"
  - "stale_artifact: 最后修改>90天+不在注册表 → 归档或删除建议"
  - "safeguards: 清理建议仅建议不自动删、Owner显式确认、删除前备份到data/orphan_archive/"
rollback_instructions: "git checkout src/zephyr/drift_detector/orphan_scanner.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§2.16"]}]
tags: ["drift-detector","orphan","D-023-25"]
---
# TASK-INF-0017: 孤儿资源检测（D-023-25）
对标 §2.16。实现磁盘-vs-注册表-vs-import三方对比，三级分类(true_orphan/undocumented_asset/stale_artifact)，安全保护(仅建议不自动删，Owner确认+备份)。
