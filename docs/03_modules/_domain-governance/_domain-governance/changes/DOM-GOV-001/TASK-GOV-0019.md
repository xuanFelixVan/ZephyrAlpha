---
task_id: "TASK-GOV-0019"
source_blueprint: "DOM-GOV-001"
source_section: "蓝图 §8——测试用例 P0（P0-U1, P0-U2, P0-I1, P0-I2）"

# ===== 内容 =====
title: "实现 §8 P0 测试用例：P0-U1 冒烟测试 + P0-U2 输入校验 + P0-I1 集成测试 + P0-I2 施工顺序验证"
description: |
  实现 DOM-GOV-001 §8 定义的 4 个 P0 级测试用例：
  1. P0-U1（模块核心功能冒烟测试）：
     - G-CT-001~008 每条契约的端到端数据流通断言
     - RBAC→Audit 写入验证：RBAC.check() 后 Audit 记录正确写入
     - Audit→Rollback 回滚触发验证：异常操作签名→anomaly_detector 产出 AnomalyEvent→Rollback 消费
  2. P0-U2（输入校验）：
     - 非法 module_id 引用拒绝：传入不存在的 module_id→系统拒绝并返回明确错误
     - 循环依赖检测：验证 G-CT-004 Escalation→RBAC 反向引用不会被误判为循环依赖
  3. P0-I1（与 depends_on 模块集成）：
     - SYS-MASTER-001 金字塔层级约束验证：治理域 8 模块的 module_id 符合 Level 1 层级映射
     - MOD-MASTER-001 CT-* 契约与 G-CT-* 契约不冲突验证：双方契约编号/方向/字段无不兼容差异
  4. P0-I2（域内施工顺序验证）：
     - §4 施工顺序的拓扑排序正确性：Phase 1→2→3→4 拓扑无环
     - 前置模块 not_started 时后续模块禁止开工：Phase 2 启动时若 Phase 1 门禁未通过→拒绝
priority: "P0"

# ===== 上游：执行前必须读取的文件 =====
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\audit_trail\\contracts.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_rbac\\contracts.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\rollback\\contracts.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\escalation\\contracts.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\drift_detector\\events.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\budget_enforcer\\alerts.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_spec\\registry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\a2a\\protocol.py"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_gct_001_rbac_to_audit.py"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_gct_002_audit_to_rollback.py"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_gct_003_rollback_to_escalation.py"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_gct_004_escalation_to_rbac.py"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_gct_005_drift_to_rollback.py"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_gct_006_budget_to_escalation.py"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_gct_007_spec_to_rbac_audit.py"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_gct_008_a2a_to_rbac_escalation.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

# ===== 下游：执行后必须产出的文件 =====
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\tests\\governance\\test_p0_u1_contract_smoke.py"
    description: "P0-U1——G-CT-001~008 每条契约端到端数据流通断言 + RBAC→Audit + Audit→Rollback 验证"
  - path: "D:\\ZephyrAlpha\\tests\\governance\\test_p0_u2_input_validation.py"
    description: "P0-U2——非法 module_id 拒绝 + 循环依赖检测"
  - path: "D:\\ZephyrAlpha\\tests\\governance\\test_p0_i1_depends_on_integration.py"
    description: "P0-I1——SYS-MASTER-001 层级验证 + MOD-MASTER-001 CT-* 契约冲突检测"
  - path: "D:\\ZephyrAlpha\\tests\\governance\\test_p0_i2_construction_order.py"
    description: "P0-I2——§4 拓扑排序正确性 + 前置模块未开工禁止后续"

# ===== 范围：允许和禁止触碰的文件 =====
allowed_touch:
  - "D:\\ZephyrAlpha\\tests\\governance\\test_p0_u1_contract_smoke.py"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_p0_u2_input_validation.py"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_p0_i1_depends_on_integration.py"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_p0_i2_construction_order.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\**\\*.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_gct_*.py"

# ===== 规则：必须遵守的治理规则 =====
applicable_rules:
  - module_id: "DOM-GOV-001"
    section: "§8"
    reason: "P0 测试用例定义——P0-U1 (冒烟) / P0-U2 (输入校验) / P0-I1 (depends_on集成) / P0-I2 (施工顺序)"
  - module_id: "DOM-GOV-001"
    section: "frontmatter depends_on"
    reason: "P0-I1——SYS-MASTER-001 / MOD-MASTER-001 集成验证"

# ===== 上下文：执行前必须装配进上下文的所有文件 =====
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
    reason: "§8——测试用例定义与验收标准，逐条对照"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\audit_trail\\contracts.py"
    reason: "P0-U1——G-CT-001 Audit.write() + G-CT-002 AnomalyEvent"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_rbac\\contracts.py"
    reason: "P0-U1——G-CT-001 RBAC.check() → Audit.write()"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\rollback\\contracts.py"
    reason: "P0-U1——G-CT-002 Rollback.on_audit_anomaly()"
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "P0-I1——SYS-MASTER-001 金字塔层级约束"
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
    reason: "P0-I1——MOD-MASTER-001 CT-* 契约交叉验证"
  - file_path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
    reason: "P0-I1——module_id 映射真源"
  - file_path: "D:\\ZephyrAlpha\\tests\\governance\\test_phase1_gate_check.py"
    reason: "P0-I2——Phase 门禁测试参考"

# ===== 执行 =====
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M5"
estimated_tokens: 18000
timeout_minutes: 45

# ===== 验收标准 =====
acceptance_criteria:
  - "P0-U1: G-CT-001~008 全部 8 条契约的 e2e 数据流通断言 PASS——RBAC→Audit 写入成功 + Audit→Rollback anomaly 触发成功"
  - "P0-U2: 传入非法 module_id（如 MOD-INF-999）→系统拒绝并返回明确错误码；G-CT-004 反向引用不触发循环依赖误报"
  - "P0-I1: SYS-MASTER-001 域间拓扑中包含 DOM-GOV-001 节点→层级验证通过；MOD-MASTER-001 B轨模块表的 MOD-INF-018~025 8 行与 G-CT-001~008 契约编号/方向无冲突"
  - "P0-I2: §4 Phase 1→2→3→4 拓扑排序无环→验证通过；Phase 1 门禁未过时 Phase 2 启动被拒绝→验证通过"
  - "4 个 P0 测试全部通过——ALL PASS——方可判定治理域 §8 P0 测试就绪"
  - "回滚方案：删除 4 个测试文件"

# ===== 回滚 =====
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\tests\governance\test_p0_u1_contract_smoke.py
  2. 删除 D:\ZephyrAlpha\tests\governance\test_p0_u2_input_validation.py
  3. 删除 D:\ZephyrAlpha\tests\governance\test_p0_i1_depends_on_integration.py
  4. 删除 D:\ZephyrAlpha\tests\governance\test_p0_i2_construction_order.py

# ===== 依赖 =====
depends_on:
  - "TASK-GOV-0002"
  - "TASK-GOV-0003"
  - "TASK-GOV-0004"
  - "TASK-GOV-0005"
  - "TASK-GOV-0006"
  - "TASK-GOV-0007"
  - "TASK-GOV-0008"
  - "TASK-GOV-0009"
  - "TASK-GOV-0010"
  - "TASK-GOV-0011"
blocked_by: []

# ===== 状态 =====
status: "done"

# ===== 五轴标签 =====
tags_fn:
  - "observability"
  - "security"
tags_ly: "cross_layer"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "DOM-GOV-001"

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
