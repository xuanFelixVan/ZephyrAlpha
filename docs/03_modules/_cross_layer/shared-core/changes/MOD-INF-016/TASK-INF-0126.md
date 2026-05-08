---
task_id: "TASK-INF-0126"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §17.3 Anti-Patterns（5条）"

title: "§17.3 Anti-Patterns 防护——5 条反模式门禁落地：AP1 到 AP5"
description: |
  按蓝图 §17.3 的 5 条 Anti-Patterns，在 shared/ 层面落地预防性门禁。
  AP1: 在 shared/ 中导入产品模块——禁止 shared/ 的任何文件 import 任何 L01-L04 模块。
  AP2: 创建"万能日志"类——禁止跨越 Protocol/Props/Dict 包装器的中间抽象类。
  AP3: 绕过 API_INDEX 使用内部模块——所有 consumer MUST 通过 API_INDEX 导入。
  AP4: 假"国际化"——禁止在 shared/ 中创建 i18n 字符串包装类。
  AP5: 修改 shared/ 但不更新契约——shared/ 中任何 .py 变更 MUST 更新同 PR 内 test_import_chain.py / SHARED-QUICKREF.yml / auto_contract_tester。
  实现要求：
  1. anti_pattern_guard.py——pre-commit hook 检查 AP1-AP5。
  2. 每个 AP 对应一条 pytest 测试用例。
  3. AP 违反 gate 的 commit 自动标记 CI 为 FAILED。
  专业对标：Google BUILD visibility rules + meta/ FawltyDeps + Ruff rules。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\API_INDEX.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\SHARED-QUICKREF.yml"
  - "D:\\ZephyrAlpha\\.pre-commit-config.yaml"

downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\gates\anti_pattern_guard.py"
    description: "anti_pattern_guard——pre-commit hook 检查 AP1-AP5"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_anti_patterns.py"
    description: "单元测试——每条 AP 一个 pytest 用例"

allowed_touch:
  - "D:\\ZephyrAlpha\\scripts\\governance\\anti_pattern_guard.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_anti_patterns.py"
  - "D:\\ZephyrAlpha\\.pre-commit-config.yaml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\API_INDEX.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5.1"
    reason: "API_INDEX.py——AP3 的检测依据，consumer 入口清单"
  - module_id: "GOV-DOC-002"
    section: "§5.5"
    reason: "shared/ 准入——AP Anti-Pattern 门禁对 shared/ 修改普通"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    reason: "本蓝图 §17.3——5 条 Anti-Patterns 定义与示例"

assigned_model: "glm-5.1"
assigned_pipeline: "B"
pipeline_modules:
  - "M3"
estimated_tokens: 12000
timeout_minutes: 30

acceptance_criteria:
  - "AP1 guard: any 'from zephyr.l01..' in shared/ → block commit"
  - "AP2 guard: def万能/通用/super_util patterns → block commit"
  - "AP3 guard: import bypass API_INDEX → warning→block commit"
  - "AP4 guard: i18n/l10n/国际化 class → block commit"
  - "AP5 guard: any .py change without test_import_chain/SHARED-QUICKREF → block commit"
  - "pytest tests/unit/test_anti_patterns.py -v 全部通过（5 个 AP 各 1 个用例）"
  - "anti_pattern_guard 作为 pre-commit hook 已注册且正常运作"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\scripts\governance\anti_pattern_guard.py
  2. 删除 D:\ZephyrAlpha\tests\unit\test_anti_patterns.py
  3. 还原 .pre-commit-config.yaml anti-pattern-guard

depends_on: ["TASK-INF-0101"]
blocked_by: []

status: "done"

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
