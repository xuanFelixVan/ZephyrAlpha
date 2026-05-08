---
task_id: "TASK-INF-0035"
title: "安全策略漂移检测（§6.5）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P1"
status: "draft"
estimated_effort: "4h"
depends_on: ["TASK-INF-0002"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\drift_engine.py"]
acceptance_criteria:
  - input_sanitization_coverage: 扫描HTTP/CLI入口检查input_sanitizer调用
  - auth_middleware_coverage: 检查API路由认证中间件
  - secrets_in_code: 复用Gate Engine运行时检测
rollback_instructions: "git checkout src/zephyr/drift_detector/drift_engine.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§6.5"]}]
tags: ["drift-detector","integration","§6.5"]
---
# TASK-INF-0035: 安全策略漂移检测（§6.5）
对标 §6.5。input_sanitization_coverage: 扫描HTTP/CLI入口检查input_sanitizer调用
