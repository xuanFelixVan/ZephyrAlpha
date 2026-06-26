---
module_id: KE-4113
title: 2. 关键关联清单（蓝图 §15）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2. 关键关联清单（蓝图 §15）

2. 关键关联清单（蓝图 §15）

| # | 关联对象 | 关系 | 路径 |
|---|---------|------|------|
| 1 | `metadata-registry.yaml` | MOD-INF-001 元数据注册 | `docs/01_policies_and_standards/meta/metadata-registry.yaml` |
| 2 | `task-system/blueprint.md` | 施工框架：G0-G5 门禁体系 + ContractBus 模式来源 | `docs/03_modules/_domain-infra_ops/task-system/blueprint.md` |
| 3 | `context-engine/blueprint.md` | 上下文引擎为 Token Budget 提供基础设施 | `docs/03_modules/_domain-infra_ops/context-engine/blueprint.md` |
| 4 | `llm-security/blueprint.md` | AI 审计守卫治理模型来源（合规审计、输入消毒、行为审计） | `docs/03_modules/_domain-infra_ops/llm-security/blueprint.md` |
| 5 | `gate-engine/blueprint.md` | 阻断门门禁引擎——执行层预检 | `docs/03_modules/_domain-infra_ops/gate-engine/blueprint.md` |
| 6 | `predict-router/blueprint.md` | 跨层容量联动的引航（批量执行、预算感知调度） | `docs/03_modules/_domain-infra_ops/predict-router/blueprint.md` |
| 7 | `orchestrator/blueprint.md` | Agent 健康（SLO+三态）的监控目标 | `docs/03_modules/_domain-infra_ops/orchestrator/blueprint.md` |
| 8 | SQLite best practices | DB schema、PRAGMA、TTL 清理等技术依据 | Supabase/Postgres best practices standard |
| 9 | `.trae/rules/project_rules.md` | Env + Agent 行为约束（R-001~R-008） | `.trae/rules/project_rules.md` |
