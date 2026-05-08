---
task_id: "TASK-INF-0022"
title: "告警可信度评分 credibility_engine.py（D-023-35）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P1"
status: "draft"
estimated_effort: "3h"
depends_on: ["TASK-INF-0005","TASK-INF-0028"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\credibility_engine.py"]
acceptance_criteria:
  - "formula: credibility = base_score × (1 - fp_rate) × precision × recency_factor"
  - "new_detector base_score=0.5 / proven=1.0; fp_rate>0.3→×0.5 / >0.5→×0.2; recency>90天→×0.8"
  - "alert_modulation: >0.8正常推送、0.4-0.8聚合批次、<0.4 shadow观测仅仪表板"
  - "owner_override: 手动设置特定detector credibility_weight"
rollback_instructions: "git checkout src/zephyr/drift_detector/credibility_engine.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§2.21"]}]
tags: ["drift-detector","credibility","alert","D-023-35"]
---
# TASK-INF-0022: 告警可信度评分（D-023-35）
对标 §2.21。实现 credibility = base × (1-fp_rate) × precision × recency 公式 + alert_modulation三级推送 + Owner override。
