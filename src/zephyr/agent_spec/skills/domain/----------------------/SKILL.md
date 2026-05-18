---

skill_id: SKILL-DOM-{{MODULE_ABBR}}-{{NUMBER}}
name: "红白对抗验证器蓝图 — 治理规则混沌工程引擎"
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


# Domain Skill: 红白对抗验证器蓝图 — 治理规则混沌工程引擎

## CRITICAL Rules

### Core Operations
# 攻击注入操作需要权限校验
identity = AgentIdentity(
    session_id=current_session_id,
    maturity=MaturityLevel.L2_REGULAR,
    role=AgentRole.EXECUTOR,
    ide_source=IDESource.TRAE,
)
guard = PermissionGuard()
result = guard.check(identity, "red_blue:inject:create_file", target_path)
if result.decision == GuardDecision.BLOCKED:
    raise PermissionError(f"RBAC blocked: {result.reason}")
```

### Unique Constraints
## 19. 运行场景约束

> **对标 Agent RBAC §1.3 / Escalation §1.3 / Drift Detector §1.3**——明确运行上下文的约束条件。

| 约束 | 值 | 影响 |
|------|-----|------|
| 开发者人数 | 1 | 无团队 Code Review，AI 是唯一审查者 |
| AI 维护者 | 1~3 个并发 session | 多 session 可能同时触发对抗 |
| 用户人数 | 1 | Owner 即 Operator，无分级审批链 |
| 开发模式 | 100% 氛围编程 | AI 生成代码的信任问题——对抗验证是必要防线 |
| 运行环境 | Windows (NTFS) | RULE-ONE 并发写入约束 |
| 人工值守 | 零 | Game Day 全自动，人工仅做月度 SYSTEM 级确认 |
| CI/CD | GitHub Actions | push/PR 自动触发 FILE 级对抗 |
| 外部依赖 | MOD-INF-007/013/014/017/018/020/022/023/024/027/028/029/031 | 13 个模块依赖 |

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