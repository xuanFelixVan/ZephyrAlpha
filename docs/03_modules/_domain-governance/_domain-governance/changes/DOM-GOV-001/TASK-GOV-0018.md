---
task_id: "TASK-GOV-0018"
source_blueprint: "DOM-GOV-001"
source_section: "蓝图 §6 风险 R3——A2A Protocol 与 Agent Spec 矛盾（G-CT-007 获取 Agent Spec 值的同时 Phase 4 才施工）"

# ===== 内容 =====
title: "风险 R3 缓解：A2A Protocol Phase 4 Hold 标记——确保 G-CT-007 先行、A2A 不提前"
description: |
  缓解 DOM-GOV-001 §6 风险 R3："G-CT-007 需要 Agent Spec 注册为前提，但 Agent Spec 在 Phase 4 才启动施工；A2A 与 Phase 3 模块可能并发"。
  缓解策略：
  1. G-CT-007（Agent Spec→RBAC/Audit）Phase 4 施工——Agent Spec 在 Phase 4 启动
  2. G-CT-008（A2A→RBAC/Escalation）Phase 4 施工——A2A 不提前到 Phase 1-3
  3. Phase 3→Phase 4 门禁时验证 Agent Spec Registry 就绪——否则拒绝 Phase 4 启动
  4. A2A Phase 4 Hold 锁定标记写入 a2a/__init__.py——任何 AI 会话读取控标代码前先检查标记
priority: "P2"

# ===== 上游：执行前必须读取的文件 =====
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\a2a\\__init__.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_spec\\registry.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

# ===== 下游：执行后必须产出的文件 =====
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\a2a\\phase_hold.py"
    description: "A2A Phase 4 Hold 锁定标记模块——含 is_phase4_started() 门禁函数"
  - path: "D:\\ZephyrAlpha\\tests\\governance\\test_a2a_phase4_hold.py"
    description: "A2A Phase 4 Hold 验证测试——Phase 4 启动后才允许 A2A 接口调用"

# ===== 范围：允许和禁止触碰的文件 =====
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\a2a\\phase_hold.py"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_a2a_phase4_hold.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\a2a\\__init__.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_spec\\*"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"

# ===== 规则：必须遵守的治理规则 =====
applicable_rules:
  - module_id: "DOM-GOV-001"
    section: "§6 R3"
    reason: "风险 R3——A2A Phase 4 Only"
  - module_id: "DOM-GOV-001"
    section: "§4 Phase 4"
    reason: "Phase 4 施工——A2A+Agent Spec 同期"

# ===== 上下文：执行前必须装配进上下文的所有文件 =====
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
    reason: "§6 R3——风险定义与缓解策略"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\a2a\\__init__.py"
    reason: "TASK-GOV-0001 的产出——A2A 模块骨架（Phase Hold 标记注入点）"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_spec\\registry.py"
    reason: "TASK-GOV-0008 的产出——Agent Spec Registry"

# ===== 执行 =====
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M3"
  - "M5"
estimated_tokens: 7000
timeout_minutes: 20

# ===== 验收标准 =====
acceptance_criteria:
  - "a2a/phase_hold.py 定义 is_phase4_started()——返回 bool，Phase 4 未启动时返回 False"
  - "A2A 任何公共接口（send/receive/route）必须在调用前检查 phase_hold——未启动抛出 A2APhase4HoldException"
  - "Phase 4 门禁通过（TASK-GOV-0013）后手动触发 A2A Phase 4 Start——is_phase4_started() → True"
  - "test_a2a_phase4_hold.py 验证：Phase 4 未启动→A2A.send() 拒绝；Phase 4 已启动→正常运行"
  - "a2a/__init__.py docstring 声明 'Phase 4 Only——不得在 Phase 1-3 施工'"
  - "回滚方案：删除新创建的 2 个文件 + 还原 __init__.py"

# ===== 回滚 =====
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\governance\a2a\phase_hold.py
  2. 删除 D:\ZephyrAlpha\tests\governance\test_a2a_phase4_hold.py
  3. 用 git checkout 还原 D:\ZephyrAlpha\src\zephyr\governance\a2a\__init__.py

# ===== 依赖 =====
depends_on:
  - "TASK-GOV-0001"
  - "TASK-GOV-0008"
blocked_by: []

# ===== 状态 =====
status: "done"

# ===== 五轴标签 =====
tags_fn:
  - "security"
tags_ly: "cross_layer"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "DOM-GOV-001"
  - "risk:R3"

# ===== 门禁 =====
completed_gates: []
blocked_gates: {}

# ===== 产物 =====
artifact_paths: []

# ===== 审计 =====
audit_findings: []

# ===== 知识 =====
ke_entries: []

# ===== AI 自治 =====
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
