---
task_id: "TASK-INF-0123"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §16 AD-004"

title: "AD-004 实现——Prompt/Skill 注册表职责边界：context_engine 负责实例化，shared/ 负责基座定义"
description: |
  按 AD-004 决策——PromptRegistry 和 SkillRegistry 的实际实例化归 context_engine 模块，
  shared/ 仅负责抽象的基座定义（PromptTemplate / SkillDefinition Pydantic 模型 + AbstractRegistryBase）。
  实现要求：
  1. shared/skill_registry.py（B34）只定义 PromptTemplate + SkillDefinition Pydantic 模型。
  2. shared/skill_registry.py 中 AbstractRegistryBase Protocol——register() / get() / list()。
  3. 禁止 shared/ 内引入任何 context_engine 的 import（前后端倒置）。
  4. context_engine/prompt_registry.py 和 context_engine/skill_registry.py 从 shared/ 导入基座并实例化。
  5. 增加依赖测试——验证 shared/ 不 import context_engine（B34 检查）。
  专业对标：Dependency Inversion Principle (DIP) + Abstract Registry Pattern。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\skill_registry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\prompt_registry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\skill_registry.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\abstract_registry.py"
    description: "AbstractRegistryBase Protocol——register() / get() / list()"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_abstract_registry.py"
    description: "单元测试——验证 Protocol 签名 + shared/ 不 import context_engine"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\abstract_registry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\skill_registry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\__init__.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_abstract_registry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\SHARED-QUICKREF.yml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\prompt_registry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\skill_registry.py"

applicable_rules:
  - module_id: "GOV-DOC-002"
    section: "§5.5"
    reason: "shared/ 准入规则——基座被 ≥2 个 L01 模块消费"
  - module_id: "PS-STD-001"
    section: "§7.1"
    reason: "抽象基座不能有外部模块引用"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    reason: "本蓝图 §16——AD-004 决策上下文与职责边界"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\prompt_registry.py"
    reason: "context_engine/prompt_registry——验证从 shared/ 正确导入基座"

assigned_model: "glm-5.1"
assigned_pipeline: "B"
pipeline_modules:
  - "M3"
estimated_tokens: 8000
timeout_minutes: 20

acceptance_criteria:
  - "abstract_registry.py: AbstractRegistryBase Protocol——含 register/get/list 抽象方法"
  - "shared/skill_registry.py 不 import context_engine 的任何模块"
  - "context_engine/prompt_registry.py 必须 from zephyr.shared.abstract_registry import AbstractRegistryBase"
  - "shared/ 入口 __init__.py 不导出 context_engine 符号"
  - "pytest tests/unit/test_abstract_registry.py -v 全部通过"
  - "SHARED-QUICKREF.yml 更新——新增 abstract_registry 入口"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\shared\abstract_registry.py
  2. 删除 D:\ZephyrAlpha\tests\unit\test_abstract_registry.py
  3. 还原 __init__.py + skill_registry.py 变更
  4. 还原 SHARED-QUICKREF.yml 对应条目

depends_on: ["TASK-INF-0106"]
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
