---
task_id: "TASK-INF-0026"
title: "关联引擎 correlation_engine.py（D-023-09）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P1"
status: "draft"
estimated_effort: "4h"
depends_on: ["TASK-INF-0025"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\correlation_engine.py"]
acceptance_criteria:
  - "co_occurrence: Jaccard(模块A scan_id集合, 模块B scan_id集合) → 漂移共现矩阵"
  - "causal_chain: 按时间排序+Granger因果检验(简化版) → A先漂B后漂"
  - "dimension_cluster: 对detector_id做模块聚类 → 同一维度集中出现"
  - "output: 漂移关联热力图(模块×模块)、系统性风险告警(N模块同时同维度漂移→根因在基础设施)"
rollback_instructions: "git checkout src/zephyr/drift_detector/correlation_engine.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§5.2"]}]
tags: ["drift-detector","correlation","D-023-09"]
---
# TASK-INF-0026: 关联引擎（D-023-09）
对标 §5.2。实现co_occurrence(Jaccard)、causal_chain(Granger简化)、dimension_cluster(聚类)+漂移关联热力图+系统性风险告警。
