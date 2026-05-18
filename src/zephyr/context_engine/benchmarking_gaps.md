---
blueprint_id: MOD-INF-008
---

# Benchmarking Gaps — 工业对标差距分析 (TASK-013)

> Generated: 2026-05-07 | Module: MOD-INF-008 | Blueprint §13

## §13.1 Anthropic Context Engineering

| 实践 | 我们有？ | 差距 | 对应任务 |
|------|:---:|------|---------|
| Context Rot 模型 | ❌ | 有预算追踪，无 n² attention 衰减 | TASK-014 (beta a) |
| XML Tag 强制分区 | 部分 | 四层结构化注入已实现，未 XML 化 | TASK-005 (Inject) |
| Multi-Turn Curation Loop | ❌ | 单次 build→inject | TASK-014 (beta b: curation_loop.py) |
| System Prompt 版本化 | ❌ | 未追踪 prompt version | TASK-013 (本审计标记) |
| Hybrid Approach | 部分 | context_rules_v1.yaml + policy.yaml 存在但未全链路集成 | TASK-010 (集成契约) |

## §13.2 Google Context Caching

| 层级 | 特征 | 我们有？ | 对应任务 |
|------|------|:---:|---------|
| Hot | 同 session 高频复用 | ❌ | AP4 @lru_cache (TASK-002/TASK-009) |
| Warm | 跨 session 共享 60min | ❌ | TASK-014 (beta a eviction: context_evictor.py) |
| Cold | 长期存储 permanent | ✅ | VMS 全量 KE |

## §13.3 Vibe Coding Community Patterns

| 模式 | 我们有？ | 差距 | 对应任务 |
|------|:---:|------|---------|
| Memory Bank | ❌ | 蓝图 ≠ AI 工作记忆 | TASK-014 (beta c: memory_bank.py) |
| Cursor Rules | 部分 | depends_on 静态 — 需动态依赖解析 | TASK-014 |
| Windsurf Freshness Decay | ❌ | 有 freshness 字段，无 per-domain halflife | TASK-019 (DD105: domain_decay_config.py) |
| Spec Coding | 部分 | execution_plan→task_cards 规约驱动 | — |
| Skill 展开 | ❌ | 无渐进式上下文展开 | TASK-016 (vibe shortcuts) |

## §13.4 对标总结 (8 项差距)

| # | 差距 | 严重度 | 对应 task_id | 状态 |
|---|------|:---:|------|:---:|
| 1 | Context Rot 数学模型 | P0 | MOD-INF-008-TASK-014 | backlog |
| 2 | XML Tag 方法 | P1 | MOD-INF-008-TASK-014 (beta c) | backlog |
| 3 | System Prompt 版本化 | P2 | MOD-INF-008-TASK-013 (标记) | documented |
| 4 | Hot/Warm 缓存分级 | P1 | MOD-INF-008-TASK-014 (evictor) | backlog |
| 5 | Multi-Turn Curation | P0 | MOD-INF-008-TASK-014 (beta b) | backlog |
| 6 | Memory Bank | P1 | MOD-INF-008-TASK-014 (beta c) | backlog |
| 7 | Per-domain halflife | P1 | MOD-INF-008-TASK-019 (DD105) | backlog |
| 8 | Skill/渐进式展开 | P2 | MOD-INF-008-TASK-016 | backlog |
