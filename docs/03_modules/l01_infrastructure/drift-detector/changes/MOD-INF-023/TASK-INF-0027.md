---
task_id: "TASK-INF-0027"
title: "覆盖率仪表板 dashboard.py（§5.3）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P1"
status: "draft"
estimated_effort: "4h"
depends_on: ["TASK-INF-0023","TASK-INF-0025"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\dashboard.py"]
acceptance_criteria:
  - "detector_coverage_matrix: 漂移维度×检测器矩阵——盲区可视化"
  - "module_health_index: velocity × severity × resolution_rate——综合评分"
  - "drift_heatmap: 时间轴漂移事件热力图——时段/模块稳定性"
  - "export: MCP Tool call返回JSON摘要(<500 token)、CLI报告文本表格"
rollback_instructions: "git checkout src/zephyr/drift_detector/dashboard.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§5.3"]}]
tags: ["drift-detector","dashboard","coverage"]
---
# TASK-INF-0027: 覆盖率仪表板
对标 §5.3。实现三视图(coverage_matrix/module_health/drift_heatmap)+MCP JSON导出+CLI文本表格。
