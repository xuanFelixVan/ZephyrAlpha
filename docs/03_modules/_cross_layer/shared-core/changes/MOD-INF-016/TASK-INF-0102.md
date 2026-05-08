---
task_id: "TASK-INF-0102"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §3 Core 模块（1 子模块, 2 文件）"

title: "§3 Core 模块验证——models.py v0.3.0 + BlueprintDecomposer 全链路贯通审计"
description: |
  验证 Core 模块（src/zephyr/core/）的 2 个文件：
  1. blueprint_decomposer.py——蓝图分解器：蓝图.md → 多个 TaskCard
  2. models.py v0.3.0——核心数据模型：继承 schemas.py Task（31字段：28业务+3 DB追踪），全链路贯通。
  确认 TaskCard 继承结构无破坏——所有现有模块 import 不受影响（17/17 测试通过已确认）。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\blueprint_decomposer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_schemas.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\changes\\MOD-INF-016\\TASK-INF-0102.md"
    description: "本任务卡——Core 模块验证执行记录"

allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\changes\\MOD-INF-016\\TASK-INF-0102.md"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\blueprint_decomposer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2——禁止 dataclass。models.py 必须使用 Pydantic V2 BaseModel"
  - module_id: "PS-STD-001"
    section: "§7.1"
    reason: "Task 31字段定义——28语义+3追踪=31字段，models.py 继承 schemas.py 的 Task"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    reason: "本蓝图 §3——Core 模块职权与接口定义"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
    reason: "验证 TaskCard 继承 Task 31字段全链路贯通"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
    reason: "Task 基座——31字段 Pydantic V2 模型"

assigned_model: "claude-sonnet-4.6"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 5000
timeout_minutes: 20

acceptance_criteria:
  - "blueprint_decomposer.py 文件磁盘存在且内容非空"
  - "models.py 文件磁盘存在且内容非空"
  - "models.py 中 TaskCard 类继承自 schemas.py 的 Task"
  - "TaskCard 包含全部 31 字段（28 语义 + 3 追踪：is_deleted / deleted_at / schema_version）"
  - "pytest tests/unit/test_schemas.py -v 全部通过（17/17）"
  - "from zephyr.core.models import TaskCard 可成功执行"

rollback_instructions: |
  本任务为只读审计。发现 model 漂移时记录审计发现，创建修复任务卡。
  不修改 models.py 或 schemas.py——所有 L01 模块依赖这些文件。

depends_on: ["TASK-INF-0101"]
blocked_by: []

status: "done"

tags_fn:
  - "infra"
tags_ly: "cross_layer"
tags_md: "claude-sonnet-4.6"
tags_st: "active"
tags_mo:
  - "MOD-INF-016"

completed_gates: []
blocked_gates: {}

artifact_paths: []

audit_findings:
  - id: "F-TASK-INF-0102-001"
    severity: "info"
    finding: "pytest tests/unit/test_schemas.py 实际 44/44 通过（非任务卡预期的 17/17），测试套件已扩展。全部通过。"
    evidence: "pytest -v passed 44, 0 failed"
  - id: "F-TASK-INF-0102-002"
    severity: "info"
    finding: "TaskCard 继承 Task (31字段基座) + 追加 27 个 Vibe Coding 字段 = 58 字段。全链路贯通验证通过。"
    evidence: "models.py:L74 class TaskCard(Task)"

ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
