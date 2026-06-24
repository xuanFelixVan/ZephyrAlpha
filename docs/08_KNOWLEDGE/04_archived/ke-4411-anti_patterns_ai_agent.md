---
module_id: KE-4247---ai-agent-003
title: 七、Anti-Patterns — AI agent 绝对禁止的集成行为
category: module_blueprint
---

# 七、Anti-Patterns — AI agent 绝对禁止的集成行为

七、Anti-Patterns — AI agent 绝对禁止的集成行为

> 门控引擎是"AI被约束的地方"——Anti-Patterns比普通模块更重要。

| # | Anti-Pattern | 违反后果 | 正确做法 |
|---|-------------|---------|---------|
| AP1 | **绕过门禁直接修改TaskCard.status** — AI用 `task.status=COMPLETED` 而非通过 `task_repo.transition()` | G0-G7全部门禁被跳过——相当于安全员被支开 | 状态变更必须通过 task_repo.transition() → 自动触发对应门禁 |
| AP2 | **跳过G1-G5 KMS门禁直接写入知识库** — AI直接写 `docs/08_knowledge/ke-*.md` 而不通过activate→extract管道 | 未审查的知识进入AI上下文——可能包含错误/过时/冲突内容 | KE入库必须经过 G1→G2→G3→G4→G5 完整管道 |
| AP3 | **门禁规则留问句** — 写 `check: "TaskCard必填字段完整？"` | AI无法直接执行——需要"猜测"什么算完整 | check必须是布尔表达式：`check: "task_id IS NOT NULL AND priority IS NOT NULL"` |
| AP4 | **熔断器触发后手动override** — AI在circuit_breaker=OPEN时强行reset | 连续故障的系统性问题被掩盖——可能积累成灾难性故障 | OPEN期间只能等待cooldown到期——HALF_OPEN自动试探恢复 |
| AP5 | **创建门禁但不注册** — AI新建YAML但不写入 _registry.yaml | 门禁成为孤儿——引擎无法发现——形式上存在但实际不执行 | 新建门禁 = copy _template.yaml + 写入 _registry.yaml |
| AP6 | **废弃门禁直接删除** — AI `rm g5-extract.yaml` | 历史session回溯时找不到"当时为什么这个门禁存在" | 废弃= `status: deprecated` + 移到 `_deprecated/` ——铁律四 |
| AP7 | **门禁的on_failure只有reject没有fix_hint** | AI被拒绝后不知道"怎么才能通过"——反复重试→无限循环 | 每条reject的entry_condition必须配 fix_hint |

---
