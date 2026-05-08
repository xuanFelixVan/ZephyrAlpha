---
task_id: "TASK-INF-0117"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §9 R1 风险 + §11.3 步骤2"

title: "§9 R1 缓解——models.py 按域拆分：将 200+ 行 TaskCard 垂直拆分到 4 个子模块"
description: |
  缓解蓝图 §9 R1 风险——models.py 超过 200 行，突破 shared/ 最大 200 行规则。
  按蓝图 §11.3 步骤2 的要求，将 models.py 按业务域垂直拆分：
  1. task_models.py——Task 核心字段（31 字段）
  2. pipeline_models.py——Stage/Step/Pipeline 定义
  3. review_models.py——Review/Approval/Rejection 定义
  4. pdf_models.py——PDF 相关模型
  5. 仅在 models.py 中保留 re-export 外观（Facade pattern）。
  拆分后每个文件 ≤200 行，保留 schemas.py Task 继承链不变。
  专业对标：DDD Vertical Slice Architecture + Python namespace packages。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\task_models.py"
    description: "Task 核心 31 字段 Pydantic 模型"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\pipeline_models.py"
    description: "Stage/Step/Pipeline Pydantic 模型"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\review_models.py"
    description: "Review/Approval/Rejection Pydantic 模型"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\pdf_models.py"
    description: "PDF 相关 Pydantic 模型"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
    description: "Facade——re-export 4 个子模块"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_task_models.py"
    description: "单元测试——验证拆分后 Task 继承链不变"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_pipeline_models.py"
    description: "单元测试——验证 Stage/Step/Pipeline"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_review_models.py"
    description: "单元测试——验证 Review/Approval"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_pdf_models.py"
    description: "单元测试——验证 PDF 模型"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\task_models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\pipeline_models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\review_models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\pdf_models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\__init__.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_task_models.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_pipeline_models.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_review_models.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_pdf_models.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§7.1"
    reason: "Task 31字段定义——拆分 MUST 保持 31 字段完整，不能丢失字段"
  - module_id: "GOV-DOC-002"
    section: "§3"
    reason: "Core 代码包结构——B 轨子模块存放 src/zephyr/core/"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    reason: "本蓝图 §9/§11.3——R1 风险缓解 + 施工步骤 2"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
    reason: "需要拆分的源文件——200+ 行 TaskCard proxy Pydantic model"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
    reason: "Task 继承基——拆分后所有子模型继续继承 Task"

assigned_model: "claude-sonnet-4.6"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 20000
timeout_minutes: 50

acceptance_criteria:
  - "models.py 拆分后，task_models.py / pipeline_models.py / review_models.py / pdf_models.py 都 ≤200 行"
  - "models.py 变成 Facade——仅 re-export，≤30 行"
  - "所有现有 from zephyr.core.models import TaskCard 仍然工作（Facade re-export）"
  - "Task 31 字段继承链——父 Task 不变，子模型不丢字段"
  - "pytest tests/unit/test_task_models.py -v 全部通过"
  - "pytest tests/unit/test_pipeline_models.py -v 全部通过"
  - "pytest tests/unit/test_review_models.py -v 全部通过"
  - "pytest tests/unit/test_pdf_models.py -v 全部通过"
  - "所有下游 import 不受影响——test_import_chain.py 全部通过"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\core\task_models.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\core\pipeline_models.py
  3. 删除 D:\ZephyrAlpha\src\zephyr\core\review_models.py
  4. 删除 D:\ZephyrAlpha\src\zephyr\core\pdf_models.py
  5. 删除 4 个对应 test 文件
  6. git checkout -- src/zephyr/core/models.py
  7. git checkout -- src/zephyr/core/__init__.py

depends_on: ["TASK-INF-0102"]
blocked_by: []

status: "created"

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

audit_findings: []

ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
