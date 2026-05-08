---
module_id: KE-module_blu-1_3___auditorchestrator-003
title: 1.3 与 AuditOrchestrator 的关系
category: module_blueprint
---

# 1.3 与 AuditOrchestrator 的关系

1.3 与 AuditOrchestrator 的关系

```
MOD-INF-027 AuditOrchestrator         MOD-INF-028 SemanticAuditor
┌────────────────────────┐            ┌──────────────────────────┐
│ Phase 2 审计           │            │ TriggerEngine             │
│   ├─ 结构审计维度们    │  调度      │   ├─ 触发A: 文件失联      │
│   └─ DIM-SEMANTIC-001 ─┼───────────▶│   ├─ 触发B: 系统超越      │
│                        │  报告      │   └─ 触发C: 结构缺失      │
│                        │◀───────────│ AlignmentEngine           │
│   └─ 问题→修复→验证    │            │   ├─ 正向: 注册表→磁盘    │
└────────────────────────┘            │   └─ 反向: 磁盘→注册表    │
                                      │ SafetyBoundary            │
                                      │   ├─ 禁碰规则（白名单）    │
                                      │   └─ 置信度阈值            │
                                      │ LLMBridge                 │
                                      │   ├─ 安全校验（MOD-INF-014)│
                                      │   ├─ 修复文本生成          │
                                      │   └─ 幻觉检测              │
                                      └──────────────────────────┘
```

---
