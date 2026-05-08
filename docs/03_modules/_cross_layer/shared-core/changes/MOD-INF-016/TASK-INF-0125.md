---
task_id: "TASK-INF-0125"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §17 Consumer Onboarding Guide"

title: "§17 Consumer Onboarding——3 步接入指南实施：install → import → consume 全链路验证"
description: |
  按蓝图 §17 的 Consumer Onboarding Guide，为新消费者模块提供接入 shared-core 的分步指南。
  三步流程：
  1. Step 1: 环境准备——确保 pyproject.toml 中 shared-core 依赖声明正确。
  2. Step 2: 导入体验——from zephyr.shared import ... 5 行完成接入。
  3. Step 3: 首次消费——生成一个 TaskCard（实例化 TaskCard + validate）。
  实现要求：
  - onboarding.py 脚本——自动化检测新消费者是否走完 3 步。
  - 接入检查清单——模块准入前 MUST 通过 onboarding 验证。
  - 集成到 contract_auto_tester——每次 CT 运行时检测新 consumer。
  - 文档示例代码——onboarding_guide.py 放置在 shared-core/changes/MOD-INF-016/。
  专业对标：Stripe API quickstart + ZephyrAlpha Directory Structure Standard。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\pyproject.toml"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\SHARED-QUICKREF.yml"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\scripts\\governance\\onboarding_check.py"
    description: "onboarding.py——自动化检测新消费者是否走完 3 步"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\changes\\MOD-INF-016\\onboarding_guide.py"
    description: "示例代码——展示 3 步接入流程的 Python 脚本"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_onboarding.py"
    description: "单元测试——验证 onboarding_check.py 检测逻辑"

allowed_touch:
  - "D:\\ZephyrAlpha\\scripts\\governance\\onboarding_check.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\changes\\MOD-INF-016\\onboarding_guide.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_onboarding.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\pyproject.toml"

applicable_rules:
  - module_id: "GOV-DOC-002"
    section: "§5.5"
    reason: "共享层禁直接修改——onboarding 验证脚本在 scripts/governance/"
  - module_id: "PS-STD-001"
    section: "§8"
    reason: "Checklist 结构——onboarding guide 必须符合检查清单格式"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    reason: "本蓝图 §17——Consumer Onboarding 三步指南"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\SHARED-QUICKREF.yml"
    reason: "SHARED-QUICKREF.yml——消费者查找公共 API 的入口"

assigned_model: "glm-5.1"
assigned_pipeline: "B"
pipeline_modules:
  - "M3"
estimated_tokens: 8000
timeout_minutes: 20

acceptance_criteria:
  - "onboarding_check.py: check_module_ready(module_name)——返回 PASS/FAIL + 缺失步骤"
  - "onboarding_guide.py 可执行——演示 3 步接入，验证 TaskCard 创建成功"
  - "pytest tests/unit/test_onboarding.py -v 全部通过"
  - "contract_auto_tester 运行时检测到新 consumer 并自动提示 onboarding 检查"
  - "接入检查清单包含：依赖 → import → 首次消费 三步强制门禁"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\scripts\governance\onboarding_check.py
  2. 删除 D:\ZephyrAlpha\docs\03_modules\_cross_layer\shared-core\changes\MOD-INF-016\onboarding_guide.py
  3. 删除 D:\ZephyrAlpha\tests\unit\test_onboarding.py

depends_on: ["TASK-INF-0115"]
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
