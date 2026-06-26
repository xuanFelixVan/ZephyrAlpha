---
module_id: KE-2273
status: active
title: 5. 验收标准
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 5. 验收标准

5. 验收标准

1. M-04 lazy_loader 延迟导入正确，首次访问时加载
2. M-07 背压机制：队列深度 > CAP-006 → 生产者减速
3. M-09 ContractBus Schema Enforcement：Pydantic v2 校验
4. M-10 ZephyrLogger：所有日志含 Trace ID
5. M-17 ai_audit_guard 规则引擎可拦截高风险 AI 操作
6. M-18 capacity_slo.yaml ≥ 8 SLI + Pydantic 校验通过
7. M-19 capacity_governance_loop EMA 评估 + 五级响应正确
8. M-20 TTL 清理：过期数据清理 + WAL checkpoint
9. ruff 零错误 + mypy strict 通过
10. pytest 覆盖率 > 80%
