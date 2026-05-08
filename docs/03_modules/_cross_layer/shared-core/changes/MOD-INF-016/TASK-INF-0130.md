---
task_id: "TASK-INF-0130"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §14.3 Shared 层准入边界规则"

title: "§14.3 Shared 层准入规则实施——4 条硬边界落地到 pre-commit + CI gate"
description: |
  按蓝图 §14.3 的 Shared 层准入边界规则，在 shared/ 层面落地 4 条硬门禁：
  1. 规则一：新 shared/ 子模块 MUST 被 ≥2 个蓝图层（或 L01/L02 模块）所消费。
  2. 规则二：新公共 API MUST 在 API_INDEX.py 中注册并在 SHARED-QUICKREF.yml 中引用。
  3. 规则三：shared/ 文件 MUST 保持 <200 行——超长触发同时拆分建议。
  4. 规则四：shared/ 文件中禁止包含 L01-L04 模块专有逻辑——发现即剔除。
  实现要求：
  - shared_entry_gate.py——pre-commit + CI gate 实施 4 条准入规则。
  - commit message MUST 解释 consumer 数量（<2 → block）。
  - 行数检查——shared/ 任何文件 >200 行 → warning >500 行 → block。
  专业对标：Google BUILD visibility + Garbage Collection Policy + ZephyrAlpha governance。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\API_INDEX.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\SHARED-QUICKREF.yml"
  - "D:\\ZephyrAlpha\\.pre-commit-config.yaml"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\scripts\\governance\\shared_entry_gate.py"
    description: "shared_entry_gate——实施 4 条准入规则的 pre-commit + CI gate"

allowed_touch:
  - "D:\\ZephyrAlpha\\scripts\\governance\\shared_entry_gate.py"
  - "D:\\ZephyrAlpha\\.pre-commit-config.yaml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "GOV-DOC-002"
    section: "§5.5"
    reason: "shared/ 准入规则——shared_entry_gate 是这四条规则的自动化执行者"
  - module_id: "PS-STD-001"
    section: "§5.1"
    reason: "API_INDEX.py——规则二的验证依据"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    reason: "本蓝图 §14.3——4 条准入边界规则定义"

assigned_model: "glm-5.1"
assigned_pipeline: "B"
pipeline_modules:
  - "M3"
estimated_tokens: 10000
timeout_minutes: 25

acceptance_criteria:
  - "规则一: check_consumer_count(module) → <2 consumers = block（已有 consumer 豁免）"
  - "规则二: check_api_registry(module) → 公共 API 缺 API_INDEX 注册 = block"
  - "规则三: check_file_size(path) → >200 行 warning / >500 行 block"
  - "规则四: check_domain_leakage(module) → 检测到 L01-L04 特有逻辑 import = block"
  - "shared_entry_gate.py 注册为 pre-commit hook——shared-entry-gate"
  - "commit message 强制填写 consumer 数量——consumer_count: N"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\scripts\governance\shared_entry_gate.py
  2. 还原 .pre-commit-config.yaml shared-entry-gate

depends_on: ["TASK-INF-0101"]
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
