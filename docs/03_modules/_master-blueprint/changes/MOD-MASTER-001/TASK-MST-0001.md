---
task_id: "TASK-MST-0001"
source_blueprint: "MOD-MASTER-001"
source_section: "蓝图 §零之零 真源优先级宪章"

title: "实现真源优先级宪章的冲突检测与裁决机制"
description: |
  将 §零之零 Truth Source Precedence 的 5 级优先级链实现为可执行代码：
  Tier 0(本蓝图) → Tier 1(architecture-model YAML) → Tier 2(模块蓝图) → Tier 3(策略标准文档) → Tier 4(实际代码)。
  核心功能：(1) AI agent 发现文档不一致时自动按优先级表确定权威源；
  (2) 自动创建 Finding(severity=LOW, type=DOC_INCONSISTENCY) 记录不一致；
  (3) 阻止 AI agent 自行修改权威源来修复不一致。
  违反此优先级链的任何 AI agent 行为均构成架构违规(AP1)。

priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_core.yaml"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\gates\\truth_source_validator.py"
    description: "真源优先级裁决器——读取5级优先级链，检测文档不一致并按优先级裁决"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_truth_source_validator.py"
    description: "单元测试——验证5级优先级链裁决正确性"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\gates\\truth_source_validator.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_truth_source_validator.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\**\\*.md"
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\*.yaml"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号格式 TASK-MST-NNNN"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2——禁止 dataclass"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径架构合规创建"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
    reason: "§零之零——True Source Precedence 5级优先级链定义"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
    reason: "Finding schema——生成 DOC_INCONSISTENCY 类型的 Finding"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 8000
timeout_minutes: 30

acceptance_criteria:
  - "truth_source_validator.py 读取 5 级优先级链配置并正确裁决 Tier 0 覆盖 Tier 1-4"
  - "检测到 Tier 0 与 Tier 4 矛盾时返回 Tier 0 为准，并自动生成 DOC_INCONSISTENCY Finding"
  - "阻止 AI agent 自行修改权威源——修改操作被拦截并记录 audit_log"
  - "Pydantic V2 BaseModel 实现——导入路径 from pydantic import BaseModel"
  - "单元测试覆盖全部 5 级优先级链的排列组合(至少 10 个测试用例)"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\gates\truth_source_validator.py
  2. 删除 D:\ZephyrAlpha\tests\unit\test_truth_source_validator.py
  3. 如有自动生成的 Finding 记录——运行 sqlite3 data/zephyr.db "DELETE FROM findings WHERE type='DOC_INCONSISTENCY'"

depends_on: []
blocked_by: []

status: "done"

tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-MASTER-001"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
