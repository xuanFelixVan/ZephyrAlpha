---
ttl: task_bound
completes_when: 孤儿分诊战役终裁落地（chief 终审+处置执行）后本册随 30/31 号转归档
title: 孤儿分诊证据包：小簇合并册 misc_ai_report（6 簇 35 台）
owner: st-orphtriage-20261004
---

# 41 号·小簇合并册：misc_ai_report（6 簇 35 台）

> 宇宙口径=裁定#481；数据真源=30_attribution_table.yaml；处置=建议非终裁。
>
> 合并初判汇总：mount=35

### 簇 scripts.ai_layer（1 台；初判 mount=1）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `scripts/ai_layer/run_ai_l1_scan_tick.py` | run_ai_l1_scan_tick — L1 外扫节拍宿主 tick（施工项 7，AI2 车道 2026-09-26）。 | 2026-10-02（2天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |

### 簇 src.zephyr.digital_twin（8 台；初判 mount=8）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/digital_twin/__init__.py` | [DORMANT] 未启用占位模板，勿当实现引用；2026-08-22 STR-01 标注，架构审查报告 §3.2 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 digital_twin 无预设映射）（活线在身未挂线） |
| `src/zephyr/digital_twin/_extensions/__init__.py` | [DORMANT] 未启用占位模板，勿当实现引用；2026-08-22 STR-01 标注，架构审查报告 §3.2 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 digital_twin 无预设映射）（活线在身未挂线） |
| `src/zephyr/digital_twin/api/__init__.py` | [DORMANT] 未启用占位模板，勿当实现引用；2026-08-22 STR-01 标注，架构审查报告 §3.2 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 digital_twin 无预设映射）（活线在身未挂线） |
| `src/zephyr/digital_twin/core/__init__.py` | [DORMANT] 未启用占位模板，勿当实现引用；2026-08-22 STR-01 标注，架构审查报告 §3.2 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 digital_twin 无预设映射）（活线在身未挂线） |
| `src/zephyr/digital_twin/infrastructure/__init__.py` | [DORMANT] 未启用占位模板，勿当实现引用；2026-08-22 STR-01 标注，架构审查报告 §3.2 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 digital_twin 无预设映射）（活线在身未挂线） |
| `src/zephyr/digital_twin/market_twin_simulator.py` | MarketTwinSimulator — 数字孪生市场仿真（MOD-DT-001，Phase1 规则 ABM 纯 CPU）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 digital_twin 无预设映射）（活线在身未挂线） |
| `src/zephyr/digital_twin/models/__init__.py` | [DORMANT] 未启用占位模板，勿当实现引用；2026-08-22 STR-01 标注，架构审查报告 §3.2 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 digital_twin 无预设映射）（活线在身未挂线） |
| `src/zephyr/digital_twin/services/__init__.py` | [DORMANT] 未启用占位模板，勿当实现引用；2026-08-22 STR-01 标注，架构审查报告 §3.2 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 digital_twin 无预设映射）（活线在身未挂线） |

### 簇 src.zephyr.experiment_tracking（9 台；初判 mount=9）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/experiment_tracking/__init__.py` | L_INFRA_TELEMETRY — 实验跟踪包（单一 JSON FallbackBackend，MLflow 已退役）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/experiment_tracking/adapters/__init__.py` | L_INFRA_TELEMETRY — 各零件领域对象 → 实验跟踪语义适配器包（单一 JSON 后端，MLflow 已退役）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/experiment_tracking/adapters/c2c3_adapter.py` | L_INFRA_TELEMETRY — C2/C3 验证器结果 → 实验跟踪语义适配器（50 号 §3 ⑥，M4）。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/experiment_tracking/adapters/feature_adapter.py` | L_INFRA_TELEMETRY — regime_feature_builder 特征矩阵 → 实验跟踪语义适配器（50 号 §3 ⑥，M4）。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/experiment_tracking/config.py` | L_INFRA_TELEMETRY — 实验跟踪配置（fallback 目录 / 全局开关）。 | 2026-09-16（18天） | in=5/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/experiment_tracking/experiment_tracker.py` | L_INFRA_TELEMETRY — 实验跟踪器主类（单一 JSON FallbackBackend，MLflow 已退役）。 | 2026-09-16（18天） | in=7/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/experiment_tracking/fallback_tracker.py` | L_INFRA_TELEMETRY — JSON 实验跟踪器（单一后端实现）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/experiment_tracking/models.py` | L_INFRA_TELEMETRY — 实验跟踪数据模型（RunSummary / RunDetail）。 | 2026-09-16（18天） | in=3/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/experiment_tracking/query.py` | L_INFRA_TELEMETRY — 实验跟踪查询接口（统一本地 JSON 源，MLflow 已退役）。 | 2026-09-16（18天） | in=3/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |

### 簇 src.zephyr.knowledge（5 台；初判 mount=5）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/knowledge/ai_knowledge_extractor.py` | AiKnowledgeExtractor — AI 自动知识提取器（MOD-KNW-007）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/knowledge/collection_schema_manager.py` | CollectionSchemaManager — Collection 模式管理器（MOD-KNW-010）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/knowledge/financial_knowledge_graph.py` | FinancialKnowledgeGraph — 金融知识图谱（MOD-KNW-003）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/knowledge/knowledge_quality_assessor.py` | KnowledgeQualityAssessor — 知识质量评估器（MOD-KNW-002）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/knowledge/research_workflow_engine.py` | ResearchWorkflowEngine — 研究工作流引擎轻量版（MOD-KNW-014）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |

### 簇 src.zephyr.ml_serve（7 台；初判 mount=7）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/ml_serve/__init__.py` | [DORMANT] 未启用占位模板，勿当实现引用；2026-08-22 STR-01 标注，架构审查报告 §3.2 | 2026-09-29（5天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_serve/_extensions/__init__.py` | ml_serve/_extensions | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_serve/api/__init__.py` | ml_serve/api | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_serve/core/__init__.py` | ml_serve/core | 2026-09-30（4天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_serve/infrastructure/__init__.py` | ml_serve/infrastructure | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_serve/models/__init__.py` | ml_serve/models | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_serve/services/__init__.py` | ml_serve/services | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |

### 簇 src.zephyr.nlp（5 台；初判 mount=5）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/nlp/news_impact_grader.py` | MOD-NLP-IMPACT-001 — 新闻影响评估分级 + 热点聚类（GAP-F-22，新闻页后端）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/nlp/nlp_inference.py` | MOD-NLP-INFERENCE-001 NLPImply — 新闻情感推理（零样本基线）。 | 2026-09-16（18天） | in=7/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/nlp/research_rating.py` | research_rating — 研报结构化评级提取（CAND-NLP-006）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/nlp/sentiment_aggregator.py` | MOD-NLP-AGGREGATOR-001 SentimentAggregator — 跨源情绪一致性投票聚合（NLP Phase 7）。 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/nlp/sentiment_pipeline.py` | MOD-NLP-SENT-PIPE SentimentPipeline — 离线批量端到端接线件（NLP Phase 7）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
