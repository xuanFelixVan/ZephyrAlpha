---
task_id: "TASK-INF-0120"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §16 AD-001"

title: "AD-001 实现——Pydantic V2 作为全项目唯一契约基座：强制校验 + Runtime保证"
description: |
  按 AD-001 决策——所有 Task/Contract/Schema 只用 Pydantic V2，禁用 dataclass/attrs。
  实现要求：
  1. 所有 shared/ 和 core/ 中的新模型（Phase 11-20 总计 30+ 新 Pydantic 模型）
     都必须继承 pydantic.BaseModel。
  2. 使用 Field(..., frozen=True) 标记不可变模型。
  3. model_validate() 替代 dict(**model) + TypeAdapter API。
  4. CI pre-commit hook——check_pydantic_compliance.py——扫描所有 shared/core 文件，
     检测是否有裸 dataclass 或 attrs 模型并阻止 commit。
  5. 集成到 blueprint_pre.py——每次蓝图变更 MUST 验证所有新模型为纯 Pydantic V2。
  专业对标：Pydantic V2 performance guide + Ruff UP rules。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
  - "D:\\ZephyrAlpha\\.pre-commit-config.yaml"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\scripts\\governance\\check_pydantic_compliance.py"
    description: "pre-commit hook——扫描 shared/ + core/ 的所有 .py 文件，阻止 dataclass/attrs"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_pydantic_compliance.py"
    description: "单元测试——验证 check_pydantic_compliance 检测逻辑"

allowed_touch:
  - "D:\\ZephyrAlpha\\scripts\\governance\\check_pydantic_compliance.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_pydantic_compliance.py"
  - "D:\\ZephyrAlpha\\.pre-commit-config.yaml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§7.1"
    reason: "Task 31字段定义——31 字段 MUST 为 Pydantic V2 Field() 定义"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2——禁止 dataclass。AD-001 是 ADR-0040 的蓝图级子决策"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    reason: "本蓝图 §16——AD-001 决策上下文与专业对标"

assigned_model: "glm-5.1"
assigned_pipeline: "B"
pipeline_modules:
  - "M3"
estimated_tokens: 10000
timeout_minutes: 25

acceptance_criteria:
  - "check_pydantic_compliance.py 可扫描 src/zephyr/shared/ 所有 46 文件——检测 dataclass"
  - "check_pydantic_compliance.py 可扫描 src/zephyr/core/ 所有 2 文件——检测 attrs"
  - "pre-commit hook 阻止含 @dataclass 装饰的 shared/ 新文件"
  - "pytest tests/unit/test_pydantic_compliance.py -v 全部通过"
  - "Phase 11-20 新增 30+ 模型 100% 使用 Pydantic V2 BaseModel"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\scripts\governance\check_pydantic_compliance.py
  2. 删除 D:\ZephyrAlpha\tests\unit\test_pydantic_compliance.py
  3. 还原 .pre-commit-config.yaml 中 check-pydantic 条目

depends_on: ["TASK-INF-0102"]
blocked_by: []

status: "created"

tags_fn:
  - "infra"
tags_ly: "cross_layer"
tags_md: "glm-5.1"
tags_st: "active"
tags_mo:
  - "MOD-INF-016"

completed_gates: []
blocked_gates: {}

artifact_paths: []

audit_findings: []

ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
