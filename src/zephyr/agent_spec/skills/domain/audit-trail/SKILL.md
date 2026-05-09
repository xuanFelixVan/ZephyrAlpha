---
skill_id: SKILL-DOM-AUD-001
name: "audit-trail"
description: "不可变审计写入器 — 每次AI操作自动记录不可篡改审计日志"
allowed-tools: [Read, Grep, Glob, Edit, Write, Bash]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-09
version: "1.4.0"
token_budget_l1: 50
token_budget_l2: 400
author: factory-agent
---

# Domain Skill: audit-trail — 不可变审计写入

## CRITICAL Rules

### Core Operations

**每次 AI 执行操作后，MUST 写入一条不可变审计事件。**

一行式写入：
```python
from zephyr.audit_trail.bridge import write_to_core
write_to_core(event_type="file_edit", agent_id="...", target_path="...", status="success")
```

支持的 event_type（50+ 种）:
`file_edit` `file_delete` `file_create` `gate_pass` `gate_fail` `permission_violation`
`agent_impersonation` `delegation_chain_issue` `collusion_pattern` `indirect_operation`
`dry_run_mismatch` `drift_detected` `drift_reconciled` `rollback_executed`
`feedback_loop_evolution` `heartbeat` `genesis` `compliance_check` ...

### Unique Constraints

1. **不可变** — 写入后不可修改/删除，违反即视为安全事件
2. **密码学链** — SHA-256 哈希链 + HMAC-SHA256，每行不可孤立篡改
3. **Lamport 时钟** — 分布式有序，防止时钟回拨
4. **Ed25519 签名** — Agent 操作前签名，事后可验证
5. **线程安全** — 多 Agent 并发写入不损坏日志

### Common Error Patterns

- **操作完成但忘记审计** — 这是最危险的模式，会导致审计盲区
- **审计日志路径错误** — 默认路径 `data/audit_trail/events.jsonl`
- **写锁冲突** — 系统自动处理线程安全，不要手动加锁

## Checklist

- [ ] 每次操作后调用 write_to_core()
- [ ] event_type 使用标准枚举值
- [ ] agent_id 保持唯一且可追溯
- [ ] target_path 完整记录操作目标

## Key Constants

| Constant | Value | Description |
|----------|-------|-------------|
| DATA_DIR | data/audit_trail/ | 审计日志目录 |
| EVENTS_FILE | events.jsonl | 审计事件文件 |

## References (L3, on-demand)

- 蓝图: docs/03_modules/l01_infrastructure/audit-trail/blueprint.md
- 审计策略: docs/01_policies_and_standards/governance/compliance/audit-trail-policy.md