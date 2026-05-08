---
module_id: KE-module_blu-orchestrator-003
title: Orchestrator 侧的维度声明（调度契约）
category: module_blueprint
---

# Orchestrator 侧的维度声明（调度契约）

Orchestrator 侧的维度声明（调度契约）
dimension:
  dim_id: DIM-SEMANTIC-001
  name: "规则文档语义审计"
  axis: semantic
  provider: MOD-INF-028.SemanticAuditor       # 由独立子系统执行
  input:
    rule_documents: ["project_rules.md", ...]  # 所有规则文档路径
  convergence_passes: 1                        # 语义审计 1 次即可
  max_total_passes: 3
```

**Orchestrator 不关心语义审计内部如何判定**——它只关心两件事：
1. 调度：`SemanticAuditor.audit(doc)` → 阻塞等待完成
2. 接收报告：解析 `SemanticAuditReport` → RED 问题路由到 Phase 3 FixDispatcher → YELLOW 问题上报

详细的语义审计管道（6 个 Stage：引用提取→触发检测→安全过滤→双向对齐→聚合→LLM桥接）见 [MOD-INF-028 蓝图 §2-§8](./semantic-auditor/blueprint.md)。

---
