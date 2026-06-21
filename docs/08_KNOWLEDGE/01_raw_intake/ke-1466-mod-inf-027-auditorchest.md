---
module_id: KE-1376----mod-inf-027-auditorchest-003
status: active
title: 11. 与 MOD-INF-027 AuditOrchestrator 的集成契约
category: module_blueprint
---

# 11. 与 MOD-INF-027 AuditOrchestrator 的集成契约

11. 与 MOD-INF-027 AuditOrchestrator 的集成契约

```yaml
integration_contract:
  contract_id: CT-SEM-001
  provider: MOD-INF-028
  consumer: MOD-INF-027
  
  interface:
    method: "audit"
    input:
      rule_documents: list[str]           # 规则文档路径列表
    output:
      report: SemanticAuditReport         # 结构化审计报告
    
  sla:
    per_document: "< 30s"
    max_concurrent: 4                     # ThreadPoolExecutor
    
  error_handling:
    timeout: "YELLOW — 记录超时，继续下一文档"
    llm_unavailable: "降级——跳过 Stage 6，仅报告触发条件"
```

---
