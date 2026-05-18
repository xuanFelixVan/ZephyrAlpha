---

skill_id: SKILL-DOM-{{MODULE_ABBR}}-{{NUMBER}}
name: "===== I"
description: ""
allowed-tools: [Read, Grep, Glob, Edit, Write, Bash]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-06
version: "0.1.0"
token_budget_l1: 50
token_budget_l2: 500
author: factory-agent
blueprint_id: MOD-INF-019
---


# Domain Skill: ===== I

## CRITICAL Rules

### Core Operations
# 时间窗口 window_sec 定义条件聚合窗口，默认 60s（单次操作）

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
    guard_checks: ["drift_detector", "schema_validation"]

  - id: "ESC-002"
    priority: 101
    condition: "修改 architecture-model/ 下 YAML"
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

### Unique Constraints
### 1.3 运行场景约束

| 约束 | 影响 |
|------|------|
| 1 人 + AI，99% AI 维护 | 升级不能依赖人工审批——规则驱动自动升级；Owner需反偏见强制审查 |
| 10+ 并发对话 | 升级判定必须实时且无阻塞；死锁防护必须内建 |
| 多 IDE 并发（TRAE/Cursor/RooCode） | 升级状态跨IDE一致；跨Agent配置隔离；Agent身份加密验证 |
| 个人经济预算有限 | Token消耗必须有硬顶；模型降级策略必选 |
| AI 可修改项目所有文件 | 升级规则自身必须对AI只读——不可变护栏 |
| 100% AI 施工 | 升级引擎由AI开发→必须独立验证核心判定逻辑 |
| 升级引擎自身也满足 Lethal Trifecta | 引擎必须运行在OS级Sandbox中——§2.14 |

---

### Common Error Patterns
待填写

## Checklist

- [ ] Verify blueprint before implementation
- [ ] Check upstream dependencies
- [ ] Validate against acceptance criteria
- [ ] Run gate engine checks (G0-G9)

## Key Constants

| Constant | Value | Description |
|----------|-------|-------------|
| DEFAULT_TIMEOUT | 30 | Default operation timeout (seconds) |

## References (L3, on-demand)

- module_blueprint.md
- integration_guide.md
- troubleshooting.md