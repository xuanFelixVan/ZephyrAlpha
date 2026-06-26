---
module_id: KE-979--------v2-0-0------sonnet-000
title: 6.2 完整集成映射（v2.0.0 规范，供 Sonnet 后续扩展实现）
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 6.2 完整集成映射（v2.0.0 规范，供 Sonnet 后续扩展实现）

6.2 完整集成映射（v2.0.0 规范，供 Sonnet 后续扩展实现）

| 状态转换 | 触发门禁 | 失败行为 | 成功副作用 |
|---------|---------|---------|-----------|
| `PENDING → IN_PROGRESS` | **G1** | `raise GateViolationError`，保持 `PENDING` | `events.insert(gate_passed, gate_id=G1)` |
| `IN_PROGRESS → COMPLETED` | **G2** | `raise GateViolationError`，保持 `IN_PROGRESS` | `task.gate_status = 'passed_g2'` |
| `COMPLETED → VERIFIED` | **G3** | `raise GateViolationError`，保持 `COMPLETED`；可通过 `COMPLETED→CANCELLED` 终止 | `task.gate_status = 'passed_g3'` |
| `VERIFIED`（终态）后的激活动作 | **G4** | 依赖未就绪 → `transition(WAITING, waiting_for=deps)`；其他 P0 → `transition(FAILED)` | `task.gate_status = 'passed_g4'` |
| 激活后写入知识库前 | **G5** | 后验失败 → `git checkout` 回滚 + `transition(FAILED)` | 新 KE 落盘 + `task.gate_status = 'extracted'` |
