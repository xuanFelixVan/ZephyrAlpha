---
module_id: KE-module_blu-10_3____c_____api-000
title: 10.3 模式 C：全自主 API 循环
category: module_blueprint
---

# 10.3 模式 C：全自主 API 循环

10.3 模式 C：全自主 API 循环

```python
class AutonomousAuditLoop:
    def run_full_audit(self) -> GlobalAuditReport:
        orchestrator = AuditOrchestrator()
        return orchestrator.run_full_audit()  # 全自主运行
```

---
