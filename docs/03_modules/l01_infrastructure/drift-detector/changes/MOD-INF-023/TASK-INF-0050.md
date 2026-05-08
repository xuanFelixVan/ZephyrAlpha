---
task_id: "TASK-INF-0050"
title: "测试夹具漂移检测 test_fixture_checker.py（D-023-28）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P1"
status: "draft"
estimated_effort: "4h"
depends_on: ["TASK-INF-0002"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\test_fixture_checker.py"]
acceptance_criteria:
  - fixture_schema_drift: 夹具硬编码数据结构vs ORM/pydantic schema
  - mock_target_drift: mock.patch路径vs实际模块路径
  - expected_output_drift: assert expected_value来源
  - auto_fixable=false 测试漂移最隐蔽测试通过不代表系统正确
rollback_instructions: "git checkout src/zephyr/drift_detector/test_fixture_checker.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§6.20"]}]
tags: ["drift-detector","decision","§6.20"]
---
# TASK-INF-0050: 测试夹具漂移检测 test_fixture_checker.py（D-023-28）
对标 §6.20。fixture_schema_drift: 夹具硬编码数据结构vs ORM/pydantic schema
