---
module_id: KE-3972
title: 2. Blindspots B39-B48
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2. Blindspots B39-B48

2. Blindspots B39-B48

| # | 盲点 | 严重度 | 维度 | 实现文件 | DD |
|---|------|:---:|------|------|:---:|
| B39 | Push-Only | P0 | 交互 | ce_fetch_api.py | DD113 |
| B40 | 测试保真度 | P0 | 运维 | test_ce_integration_goldens.py 等 | DD114 |
| B41 | 跨Session学习 | P0 | 认知 | session_pattern_learner.py | DD115 |
| B42 | 外部依赖过期 | P1 | 认知 | external_dep_tracker.py | DD116 |
| B43 | 引用图未遍历 | P1 | 交互 | citation_graph_walker.py | DD117 |
| B44 | 缓存无事件驱动 | P1 | 交互 | cache_invalidation_bus.py | DD118 |
| B45 | 模型无感知 | P1 | 交互 | model_aware_strategy.py | DD119 |
| B46 | 检索同质化 | P1 | 认知 | retrieval_diversity_constraint.py | DD120 |
| B47 | 自我诊断 API | P2 | 运维 | ce_self_diagnosis.py | — |
| B48 | 预算预测 | P2 | 运维 | context_budget_forecaster.py | — |
