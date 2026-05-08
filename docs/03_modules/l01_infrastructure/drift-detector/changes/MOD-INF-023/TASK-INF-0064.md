---
task_id: "TASK-INF-0064"
title: "depends_on 依赖验证与集成对账——MOD-INF-007/021/020及Evolution Engine"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "verification"
priority: "P0"
status: "draft"
estimated_effort: "4h"
depends_on: ["TASK-INF-0063","TASK-INF-0031"]
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\gates\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\feedback_loop\\evolution_engine.py"
downstream_outputs: []
acceptance_criteria:
  - "MOD-INF-007 Gate Engine: G1门禁evaluate(task)集成漂移预算检查通过"
  - "MOD-INF-021 Rollback: 漂移修复失败自动回滚链路验证通过"
  - "MOD-INF-020 Audit Trail: 审计写入仅存references集成验证通过"
  - "feedback_loop/evolution_engine.py: 漂移数据→蓝图进化反馈闭环验证通过"
  - "所有depends_on target的at字段指向的章节在目标文件中确实存在"
rollback_instructions: "无产出物回滚。若验证发现问题→修正对应模块接口而非本模块代码。"
context_assembly_manifest: [
  {file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["depends_on","references"]},
  {file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\gates\\blueprint.md", sections: ["§5"]},
  {file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback\\blueprint.md", sections: ["§2"]},
  {file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md", sections: ["§2"]}
]
tags: ["drift-detector","dependency","verification"]
---
# TASK-INF-0064: depends_on依赖验证与集成对账
验证blueprint.md frontmatter中4个depends_on项和1个references项的集成状态：MOD-INF-007(Gate Engine G1→预算检查)、MOD-INF-021(Rollback→修复失败自动回滚)、MOD-INF-020(Audit Trail仅存references)、feedback_loop(Evolution Engine→漂移数据反馈)。
