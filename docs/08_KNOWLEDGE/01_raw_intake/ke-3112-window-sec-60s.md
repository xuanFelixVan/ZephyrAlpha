---
module_id: KE-3011-------------60s-004
status: active
title: 时间窗口 window_sec 定义条件聚合窗口，默认 60s（单次操作）
category: module_blueprint
---

# 时间窗口 window_sec 定义条件聚合窗口，默认 60s（单次操作）

时间窗口 window_sec 定义条件聚合窗口，默认 60s（单次操作）

rules:
  # ===== blocked 级规则（优先级 0-99） =====
  - id: "ESC-003"
    priority: 0
    condition: "删除 ttl:permanent 文件"
    escalate_to: "blocked"
    reason: "不可逆操作"

  - id: "ESC-004"
    priority: 1
    condition: "熔断器状态 == OPEN"
    escalate_to: "blocked"
    reason: "系统熔断状态"

  - id: "ESC-006"
    priority: 2
    condition: "修改 escalation_rules.yaml 或 rbac_roles.yaml"
    escalate_to: "blocked"
    reason: "升级/权限规则不可由AI自修改——§2.5"

  - id: "ESC-007"
    priority: 3
    condition: "尝试修改自身 Skill Pack 的 system_prompt / 安全约束"
    escalate_to: "blocked"
    reason: "AI不能修改自身行为边界——对标 GitHub Copilot .github/agents"

  - id: "ESC-008"
    priority: 4
    condition: "操作涉及 API Key / Secret / Token 文件"
    escalate_to: "blocked"
    reason: "安全敏感内容——防止凭证泄露"

  # ===== auto_guard 级规则（优先级 100-199） =====
  - id: "ESC-001"
    priority: 100
    condition: "修改文件数 >= 5"
    window_sec: 60
    escalate_to: "auto_guard"
    guard_checks: ["drift-detector", "schema_validation"]

  - id: "ESC-002"
    priority: 101
    condition: "修改 architecture_model/ 下 YAML"
    escalate_to: "auto_guard"
    guard_checks: ["yaml_syntax", "cross_layer_contract"]

  - id: "ESC-009"
    priority: 102
    condition: "修改接口契约文件（API schemas / MCP tool definitions）"
    escalate_to: "auto_guard"
    guard_checks: ["contract_compatibility", "breaking_change_detector"]

  - id: "ESC-010"
    priority: 103
    condition: "AI 决策置信度 < 0.7"
    escalate_to: "auto_guard"
    guard_checks: ["second_opinion", "human_preview"]

  - id: "ESC-011"
    priority: 104
    condition: "当前任务 token 消耗 > 预算的 80%"
    escalate_to: "auto_guard"
    guard_checks: ["budget_remaining_check"]
    action: "提示Owner + 降级模型使用"

  # ===== 降级触发规则（优先级 200+） =====
  - id: "ESC-DE-001"
    priority: 200
    condition: "auto_guard 后验连续通过 >= 3次"
    deescalate_to: "autonomous"
    reason: "信任恢复——同一Agent+同类操作连续通过"

  - id: "ESC-DE-002"
    priority: 201
    condition: "熔断器状态 CLOSED + Owner手动确认"
    deescalate_to: "autonomous"

  # ===== 重复失败 → blocked（ESC-005 保留） =====
  - id: "ESC-005"
    priority: 50
    condition: "auto_guard 后验失败 >= 3次（同一任务内累计）"
    escalate_to: "blocked"
    reason: "持续失败需人工介入"
```

---
