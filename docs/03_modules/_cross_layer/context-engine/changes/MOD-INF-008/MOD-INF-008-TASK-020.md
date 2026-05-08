---
task_id: "MOD-INF-008-TASK-020"
task_title: "第十六轮擦边取证审计落地 — B39-B48 + AP40-AP47 + DD113-DD120 + beta ac-af"
module_id: "MOD-INF-008"
blueprint_section: "§23 第十六轮擦边取证 B39-B48 + §23.4 AP40-AP47 + §23.5 DD113-DD120 + §23.6 beta ac-af"
status: "backlog"
priority: "P0"
layer: "cross_layer"
assigned_agent: "DeepSeek-V4-Pro"
review_agent: "GLM-4.7"
execution_model: ["DeepSeek-V4-Pro", "GLM-4.7"]
task_type: "CODE_GEN"
estimated_effort_hours: 30
actual_effort_hours: null
deadline: null
depends_on:
  - task_id: "MOD-INF-008-TASK-019"
    why: "第十六轮在第十五轮基础上叠加交互与认知维度"
parent_task_id: "MOD-INF-008-TASK-001"
child_task_ids:
  - "MOD-INF-008-TASK-020A"
  - "MOD-INF-008-TASK-020B"
  - "MOD-INF-008-TASK-020C"
  - "MOD-INF-008-TASK-020D"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_assembler.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_injector.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_budget_tracker.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\ce_fetch_api.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\cache_invalidation_bus.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\retrieval_diversity_constraint.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\ce_self_diagnosis.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\session_pattern_learner.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\external_dep_tracker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\citation_graph_walker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\model_aware_strategy.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_budget_forecaster.py"
  - "D:\\ZephyrAlpha\\tests\\test_ce_integration_goldens.py"
  - "D:\\ZephyrAlpha\\tests\\test_ce_quality_regression.py"
  - "D:\\ZephyrAlpha\\tests\\test_ce_lsg_integration.py"
  - "D:\\ZephyrAlpha\\tests\\test_ce_pull_integration.py"
tags: ["context-engine", "round-16", "pull-model", "cognitive-bias", "diversity", "integration-tests", "beta-ac-af"]
acceptance_criteria:
  - "AC-001: B39 (Push-Only 无 Pull): ce_fetch_api.py — /ce:fetch MCP tool→按 domain/keyword/KE_ID/file 四种模式拉取，~350 行 (DD113)"
  - "AC-002: B40 (测试保真度断层): 4 个集成测试文件创建: test_ce_integration_goldens.py (Jaccard≥0.85), test_ce_quality_regression.py (<5% drift), test_ce_lsg_integration.py, test_ce_pull_integration.py (DD114)"
  - "AC-003: B41 (跨Session模式学习): session_pattern_learner.py — 离线 job→聚类 closed sessions→task_type→top KE combinations→prebuilt_clusters，~400 行 (DD115)"
  - "AC-004: B42 (外部依赖版本过期): external_dep_tracker.py — KE 创建时 snapshot poetry.lock→检索时 compare→stale flag，~300 行 (DD116)"
  - "AC-005: B43 (平面检索无引用图): citation_graph_walker.py — LLM extract internal references→1-2 hop retrieve→build KE DAG→topological sort inject，~350 行 (DD117)"
  - "AC-006: B44 (缓存无事件驱动): cache_invalidation_bus.py — event-driven→subscribe VMS delta events→semantic_overlap calc→invalidate，~250 行 (DD118)"
  - "AC-007: B45 (模型无感知): model_aware_strategy.py — per-consumer-model config→{budget, top_k, threshold, compression_level, position}→全局策略路由，~200 行 (DD119)"
  - "AC-008: B46 (检索同质化): retrieval_diversity_constraint.py — MMR-based diversity→max 2/3 per source/domain→second-pass fallback，~250 行 (DD120)"
  - "AC-009: B47 (自我诊断 API): ce_self_diagnosis.py — /ce:diagnose→health_score/sessions/cache_hit/degraded/poisoned→结构化 JSON，~200 行"
  - "AC-010: B48 (预算预测): context_budget_forecaster.py — rate_estimator→预测剩余时间到 hard stop，~150 行"
  - "AC-011: AP40-AP47 全部在对应文件中实现防护"
  - "AC-012: DD113-DD120 在代码中可验证"
rollback_instructions: "删除 beta ac-af 所有新增文件和升级代码，恢复被修改文件至第十六轮审计前版本"
context_assembly_manifest:
  required_blueprints:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md §23"
  required_standards: []
  required_templates: []
  required_references:
    - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_context_engine.yaml"
---
# MOD-INF-008-TASK-020: 第十六轮擦边取证审计落地

## 1. Purpose

将第十六轮擦边取证（交互模型+认知偏见+运维缺口审计）发现的 10 个盲点落地，补齐 CE 在交互模型、认知维度和运维维度上的最后缺口。

## 2. Blindspots B39-B48

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

## 3. beta ac (4 Files + upgrades) — 交互双模

ce_fetch_api + cache_invalidation_bus + retrieval_diversity_constraint + ce_self_diagnosis

## 4. beta ad (3 Files) — 跨Session学习

session_pattern_learner + external_dep_tracker + citation_graph_walker

## 5. beta ae (2 Files) — 模型感知

model_aware_strategy + context_budget_forecaster

## 6. beta af (4 Test Files) — 测试保真度修复

test_ce_integration_goldens + test_ce_quality_regression + test_ce_lsg_integration + test_ce_pull_integration

## 7. Key Design Decisions

| ID | 决策 | 为什么是范式级突破 |
|----|------|------|
| DD113 | AgenticPull API | 行业 2026 标杆 (Claude Code/Cursor) 已切换 pull 模型 |
| DD114 | IntegrationTestGoldens | 打破 B40 测试保真度断层 |
| DD115 | SessionPatternLearner | 从 session-aware 到 system-learning |
| DD117 | CitationGraphWalker | 平面检索→引用图检索 |
| DD120 | DiversityConstraint | 防止 source/domain echo chamber |

## 8. Acceptance Criteria

- 9 个新源文件 + 4 个新测试文件全部创建
- /ce:fetch 按 keyword "安全漏洞" 返回相关 KE 列表
- test_ce_integration_goldens 验证 Jaccard≥0.85
- session_pattern_learner 可聚类同类 session
- retrieval_diversity_constraint 限制 max 2 from same source
- /ce:diagnose 返回 JSON 格式健康报告
- budget_forecaster 返回 estimated_time_to_hard_stop
