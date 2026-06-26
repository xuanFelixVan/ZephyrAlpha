---
module_id: KE-567
title: 一、三层权限模型（来自 ADR-0010）
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 一、三层权限模型（来自 ADR-0010）

一、三层权限模型（来自 ADR-0010）

| 层级 | 语义 | AI 自主修改权限 | 修改流程 |
|------|------|----------------|---------|
| **Immutable Core** | 系统宪法层 / 风控核心 / 审计基础设施 | 禁止 AI 自主修改 | Owner 直接审批 + ADR/rationale-log 记录 |
| **Human-Gated** | 业务规则 / 阈值 / 评估标准 / 治理参数 | 修改前必须 Owner 审批 | request_change() + approve_change() + Provenance Chain |
| **AI-Modifiable** | 算法实现 / 性能优化 / 日志级别 | AI 可自主修改 | 每次修改写入 Provenance Chain，可被回溯 |

---
