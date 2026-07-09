---
doc_type: architecture_view
title: D_INTELLIGENCE 上下文管理架构文档
version: "1.0"
status: active
date: 2026-07-09
owner: auto-generator
ttl: permanent
---

# 39_d_intelligence / context_management / 上下文管理 / Context Management

> **功能简介 / Overview**: 上下文管理，负责 AI 上下文窗口管理、记忆检索和上下文压缩

> **文档作用 / Purpose**: 展示 上下文管理（D_INTELLIGENCE）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新: 2026-07-09 19:26:42
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 39 | Number | 39 |
| 域ID | D_INTELLIGENCE | Domain ID | D_INTELLIGENCE |
| 域名称 | 上下文管理 | Domain Name | Context Management |
| 层级 | L2 业务域层 | Layer | L2 Domain |
| 模块数 | 43 | Module Count | 43 |
| 域内依赖 | 33 | Internal Dependencies | 33 |
| 跨域入边 | 60 | Cross-domain Incoming | 60 |
| 跨域出边 | 33 | Cross-domain Outgoing | 33 |
| 设计态模块 | 0 | Design Modules | 0 |
| 原型态模块 | 22 | Prototype Modules | 22 |
| 生产态模块 | 21 | Production Modules | 21 |
| 容量 | 21/150 (正常) | Capacity | 21/150 (正常) |
| 描述 | 上下文预算管理(context_budget/token_budget) | Description | 上下文预算管理(context_budget/token_budget) |

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 43 个模块 / 43 modules）。

### L2 领域层 / Domain Layer (43 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name (功能简介 / Description) | 成熟度 / Maturity | 蓝图 / Blueprint |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/intelligence/__init__.py | Intelligence Domain | 原型态 / prototype | [MOD-INF-036](../../03_modules/_cross_layer/model_capability_exam/blueprint.md) |
| 2 | src/zephyr/intelligence/_extensions/__init__.py | __init__.py | 原型态 / prototype |  |
| 3 | src/zephyr/intelligence/api/__init__.py | __init__.py | 原型态 / prototype |  |
| 4 | src/zephyr/intelligence/core/__init__.py | __init__.py | 原型态 / prototype |  |
| 5 | src/zephyr/intelligence/infrastructure/__init__.py | __init__.py | 原型态 / prototype |  |
| 6 | src/zephyr/intelligence/model_drift_detector.py | ModelDriftDetector — LLM 模型行为漂移检测。 | 生产态 / production | [MOD-INF-021](../../03_modules/_domain_autonomy_core/rollback_system/blueprint.md) |
| 7 | src/zephyr/intelligence/model_evaluation/__init__.py | Intelligence — Model Evaluation Domain | 原型态 / prototype | [MOD-INF-036](../../03_modules/_cross_layer/model_capability_exam/blueprint.md) |
| 8 | src/zephyr/intelligence/model_evaluation/activate.py | G4 Activate 门禁 — 人工激活（T-2-13-D） | 生产态 / production | [MOD-INF-036](../../03_modules/_cross_layer/model_capability_exam/blueprint.md) |
| 9 | src/zephyr/intelligence/model_evaluation/experiment_track... | D_RESEARCH — Research & Innovation Concrete Im... | 原型态 / prototype | [MOD-INF-036](../../03_modules/_cross_layer/model_capability_exam/blueprint.md) |
| 10 | src/zephyr/intelligence/model_evaluation/implementations/... | Intelligence — Model Evaluation Concrete Imple... | 原型态 / prototype | [MOD-INF-036](../../03_modules/_cross_layer/model_capability_exam/blueprint.md) |
| 11 | src/zephyr/intelligence/model_evaluation/implementations/... | D_ML_TRAIN — Default Inference Engine | 生产态 / production | [MOD-INF-036](../../03_modules/_cross_layer/model_capability_exam/blueprint.md) |
| 12 | src/zephyr/intelligence/model_evaluation/inference_base.py | inference_base.py | 生产态 / production | [MOD-INF-036](../../03_modules/_cross_layer/model_capability_exam/blueprint.md) |
| 13 | src/zephyr/intelligence/model_evaluation/notebook_integra... | D_RESEARCH Research & Innovation | 原型态 / prototype | [MOD-INF-036](../../03_modules/_cross_layer/model_capability_exam/blueprint.md) |
| 14 | src/zephyr/intelligence/model_evaluation/reranker.py | Cross-Encoder 重排序层 — BGE-reranker-v2-m3（T... | 生产态 / production | [MOD-INF-036](../../03_modules/_cross_layer/model_capability_exam/blueprint.md) |
| 15 | src/zephyr/intelligence/model_evaluation/sync_engine.py | KB->VMS 同步引擎 — sync_to_vms() 生产者 | 原型态 / prototype | [MOD-INF-036](../../03_modules/_cross_layer/model_capability_exam/blueprint.md) |
| 16 | src/zephyr/intelligence/model_evaluation/target_lib/__ini... | __init__.py | 原型态 / prototype |  |
| 17 | src/zephyr/intelligence/model_evaluation/unified_memory_a... | UnifiedMemoryAPI — RI-02 统一记忆 API（M2 跨模... | 生产态 / production | [MOD-INF-036](../../03_modules/_cross_layer/model_capability_exam/blueprint.md) |
| 18 | src/zephyr/intelligence/model_profiling/__init__.py | Model Profiling — 本地 + 远程模型性能基准测试 | 原型态 / prototype | [MOD-INF-034](../../03_modules/_cross_layer/model_profiler/blueprint.md) |
| 19 | src/zephyr/intelligence/model_profiling/benchmark_suite.py | BenchmarkSuite — 多维度模型性能测试用例集 | 原型态 / prototype | [MOD-INF-034](../../03_modules/_cross_layer/model_profiler/blueprint.md) |
| 20 | src/zephyr/intelligence/model_profiling/capability_passpo... | CapabilityPassport --- AI 模型能力护照 | 生产态 / production | [MOD-INF-034](../../03_modules/_cross_layer/model_profiler/blueprint.md) |
| 21 | src/zephyr/intelligence/model_profiling/case_assembler.py | 真实多文件注入装配器（Phase 3 极限深度）。 | 原型态 / prototype | [MOD-INF-034](../../03_modules/_cross_layer/model_profiler/blueprint.md) |
| 22 | src/zephyr/intelligence/model_profiling/cli.py | model-profiler.cli — 模型性能检测命令行入口 | 生产态 / production | [MOD-INF-034](../../03_modules/_cross_layer/model_profiler/blueprint.md) |
| 23 | src/zephyr/intelligence/model_profiling/deepseek_v4_chat.py | DeepSeekV4Chat --- DeepSeek V4 系列模型 API 客户端 | 生产态 / production | [MOD-INF-034](../../03_modules/_cross_layer/model_profiler/blueprint.md) |
| 24 | src/zephyr/intelligence/model_profiling/exam_executor.py | ExamExecutor --- 执行式代码评测（HumanEval pass... | 原型态 / prototype | [MOD-INF-034](../../03_modules/_cross_layer/model_profiler/blueprint.md) |
| 25 | src/zephyr/intelligence/model_profiling/exam_judge.py | ExamJudge --- LLM-as-judge 评分器 | 生产态 / production | [MOD-INF-034](../../03_modules/_cross_layer/model_profiler/blueprint.md) |
| 26 | src/zephyr/intelligence/model_profiling/exam_orchestrator.py | ExamOrchestrator --- 五轴入职考试主控 | 生产态 / production | [MOD-INF-034](../../03_modules/_cross_layer/model_profiler/blueprint.md) |
| 27 | src/zephyr/intelligence/model_profiling/exam_rubric.py | ExamRubric --- 奥赛题结构化多维清单评分（v3.0.5... | 原型态 / prototype | [MOD-INF-034](../../03_modules/_cross_layer/model_profiler/blueprint.md) |
| 28 | src/zephyr/intelligence/model_profiling/exam_test_cases.py | ExamTestCases --- v3.0.5 扩展考试题库（96 题 / ... | 生产态 / production | [MOD-INF-034](../../03_modules/_cross_layer/model_profiler/blueprint.md) |
| 29 | src/zephyr/intelligence/model_profiling/job_matcher.py | JobMatcher --- 模型岗位匹配器 | 生产态 / production | [MOD-INF-034](../../03_modules/_cross_layer/model_profiler/blueprint.md) |
| 30 | src/zephyr/intelligence/model_profiling/model_discovery.py | ModelDiscovery — 枚举所有本地 Ollama 模型 + 远... | 生产态 / production | [MOD-INF-034](../../03_modules/_cross_layer/model_profiler/blueprint.md) |
| 31 | src/zephyr/intelligence/model_profiling/pipeline_routing/... | Model Profiler — Pipeline Routing variant | 原型态 / prototype | [MOD-INF-034](../../03_modules/_cross_layer/model_profiler/blueprint.md) |
| 32 | src/zephyr/intelligence/model_profiling/pipeline_routing/... | BenchmarkSuite — 多维度模型性能测试用例集 | 生产态 / production | [MOD-INF-034](../../03_modules/_cross_layer/model_profiler/blueprint.md) |
| 33 | src/zephyr/intelligence/model_profiling/pipeline_routing/... | model-profiler.cli — 模型性能检测命令行入口 | 原型态 / prototype | [MOD-INF-034](../../03_modules/_cross_layer/model_profiler/blueprint.md) |
| 34 | src/zephyr/intelligence/model_profiling/pipeline_routing/... | ModelProfiler — 核心性能分析引擎 | 生产态 / production | [MOD-INF-034](../../03_modules/_cross_layer/model_profiler/blueprint.md) |
| 35 | src/zephyr/intelligence/model_profiling/pipeline_routing/... | Results Writer — 持久化 benchmark 结果，支持历... | 生产态 / production | [MOD-INF-034](../../03_modules/_cross_layer/model_profiler/blueprint.md) |
| 36 | src/zephyr/intelligence/model_profiling/pipeline_routing/... | ModelTaskMatrix — 任务×模型性能学习引擎 | 生产态 / production | [MOD-INF-034](../../03_modules/_cross_layer/model_profiler/blueprint.md) |
| 37 | src/zephyr/intelligence/model_profiling/profiler.py | ModelProfiler — 核心性能分析引擎 | 原型态 / prototype | [MOD-INF-034](../../03_modules/_cross_layer/model_profiler/blueprint.md) |
| 38 | src/zephyr/intelligence/model_profiling/provider_data.py | provider_data.py | 生产态 / production | [MOD-INF-034](../../03_modules/_cross_layer/model_profiler/blueprint.md) |
| 39 | src/zephyr/intelligence/model_profiling/results_writer.py | Results Writer — 持久化 benchmark 结果，支持历... | 生产态 / production | [MOD-INF-034](../../03_modules/_cross_layer/model_profiler/blueprint.md) |
| 40 | src/zephyr/intelligence/model_profiling/task_model_learne... | ModelTaskMatrix — 任务×模型性能学习引擎 | 原型态 / prototype | [MOD-INF-034](../../03_modules/_cross_layer/model_profiler/blueprint.md) |
| 41 | src/zephyr/intelligence/models/__init__.py | __init__.py | 原型态 / prototype |  |
| 42 | src/zephyr/intelligence/services/__init__.py | __init__.py | 原型态 / prototype |  |
| 43 | src/zephyr/research/__init__.py | MOD-L09-001 Research Innovation Core. | 生产态 / production |  |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。参考 decision_index.md 设计，分四个视图：合并全景图、运营态子图、设计态子图、原型态子图（按 design_maturity 实际值拆分）。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，蓝图阶段，代码未写）
> - **虚线边框 = 原型态模块**（prototype，代码已写，验证中未稳定上线）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 合并全景图（全部模块，标签标注成熟度）

> 展示全部 43 个模块（生产态 21 + 设计态 0 + 原型态 22），标签标注成熟度。

#### 第 1 页 / 共 2 页

```mermaid
graph TD
    subgraph D_INTELLIGENCE["D_INTELLIGENCE 上下文管理"]
        src_zephyr_intelligence_init_py["(原型态 / prototype) Intelligence Domain<br/>文件: __init__.py"]
        src_zephyr_intelligence_extensions_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_intelligence_api_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_intelligence_core_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_intelligence_infrastructure_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_intelligence_model_drift_detector_py["(生产态 / production) ModelDriftDetector — LLM 模型行为漂移检测。<br/>文件: model_drift_detector.py"]
        src_zephyr_intelligence_model_evaluation_init_py["(原型态 / prototype) Intelligence — Model Evaluation Domain<br/>文件: __init__.py"]
        src_zephyr_intelligence_model_evaluation_activate_py["(生产态 / production) G4 Activate 门禁 — 人工激活（T-2-13-D）<br/>文件: activate.py"]
        src_zephyr_intelligence_model_evaluation_experiment_tracker_init_py["(原型态 / prototype) D_RESEARCH — Research & Innovation Concrete Im...<br/>文件: __init__.py"]
        src_zephyr_intelligence_model_evaluation_implementations_init_py["(原型态 / prototype) Intelligence — Model Evaluation Concrete Imple...<br/>文件: __init__.py"]
        src_zephyr_intelligence_model_evaluation_implementations_default_inference_engine_py["(生产态 / production) D_ML_TRAIN — Default Inference Engine<br/>文件: default_inference_engine.py"]
        src_zephyr_intelligence_model_evaluation_inference_base_py["(生产态 / production) inference_base.py"]
        src_zephyr_intelligence_model_evaluation_notebook_integration_init_py["(原型态 / prototype) D_RESEARCH Research & Innovation<br/>文件: __init__.py"]
        src_zephyr_intelligence_model_evaluation_reranker_py["(生产态 / production) Cross-Encoder 重排序层 — BGE-reranker-v2-m3（T...<br/>文件: reranker.py"]
        src_zephyr_intelligence_model_evaluation_sync_engine_py["(原型态 / prototype) KB->VMS 同步引擎 — sync_to_vms() 生产者<br/>文件: sync_engine.py"]
        src_zephyr_intelligence_model_evaluation_target_lib_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_intelligence_model_evaluation_unified_memory_api_py["(生产态 / production) UnifiedMemoryAPI — RI-02 统一记忆 API（M2 跨模...<br/>文件: unified_memory_api.py"]
        src_zephyr_intelligence_model_profiling_init_py["(原型态 / prototype) Model Profiling — 本地 + 远程模型性能基准测试<br/>文件: __init__.py"]
        src_zephyr_intelligence_model_profiling_benchmark_suite_py["(原型态 / prototype) BenchmarkSuite — 多维度模型性能测试用例集<br/>文件: benchmark_suite.py"]
        src_zephyr_intelligence_model_profiling_capability_passport_py["(生产态 / production) CapabilityPassport --- AI 模型能力护照<br/>文件: capability_passport.py"]
        src_zephyr_intelligence_model_profiling_case_assembler_py["(原型态 / prototype) 真实多文件注入装配器（Phase 3 极限深度）。<br/>文件: case_assembler.py"]
        src_zephyr_intelligence_model_profiling_cli_py["(生产态 / production) model-profiler.cli — 模型性能检测命令行入口<br/>文件: cli.py"]
        src_zephyr_intelligence_model_profiling_deepseek_v4_chat_py["(生产态 / production) DeepSeekV4Chat --- DeepSeek V4 系列模型 API 客户端<br/>文件: deepseek_v4_chat.py"]
        src_zephyr_intelligence_model_profiling_exam_executor_py["(原型态 / prototype) ExamExecutor --- 执行式代码评测（HumanEval pass...<br/>文件: exam_executor.py"]
        src_zephyr_intelligence_model_profiling_exam_judge_py["(生产态 / production) ExamJudge --- LLM-as-judge 评分器<br/>文件: exam_judge.py"]
        src_zephyr_intelligence_model_profiling_exam_orchestrator_py["(生产态 / production) ExamOrchestrator --- 五轴入职考试主控<br/>文件: exam_orchestrator.py"]
        src_zephyr_intelligence_model_profiling_exam_rubric_py["(原型态 / prototype) ExamRubric --- 奥赛题结构化多维清单评分（v3.0.5...<br/>文件: exam_rubric.py"]
        src_zephyr_intelligence_model_profiling_exam_test_cases_py["(生产态 / production) ExamTestCases --- v3.0.5 扩展考试题库（96 题 / ...<br/>文件: exam_test_cases.py"]
        src_zephyr_intelligence_model_profiling_job_matcher_py["(生产态 / production) JobMatcher --- 模型岗位匹配器<br/>文件: job_matcher.py"]
        src_zephyr_intelligence_model_profiling_model_discovery_py["(生产态 / production) ModelDiscovery — 枚举所有本地 Ollama 模型 + 远...<br/>文件: model_discovery.py"]
    end
    src_zephyr_intelligence_init_py -.->|config_depends / config_depends| src_zephyr_intelligence_model_drift_detector_py
    src_zephyr_intelligence_model_evaluation_init_py -.->|config_depends / config_depends| src_zephyr_intelligence_model_evaluation_activate_py
    src_zephyr_intelligence_model_evaluation_implementations_init_py -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_evaluation_implementations_default_inference_engine_py
    src_zephyr_intelligence_model_profiling_cli_py -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_init_py
    src_zephyr_intelligence_model_profiling_exam_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_capability_passport_py
    src_zephyr_intelligence_model_profiling_exam_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_exam_judge_py
    src_zephyr_intelligence_model_profiling_exam_orchestrator_py -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_exam_executor_py
    src_zephyr_intelligence_model_profiling_exam_orchestrator_py -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_exam_rubric_py
    src_zephyr_intelligence_model_profiling_exam_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_exam_test_cases_py
    src_zephyr_intelligence_model_profiling_exam_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_job_matcher_py
    src_zephyr_intelligence_model_profiling_exam_test_cases_py -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_case_assembler_py
    src_zephyr_intelligence_model_profiling_job_matcher_py -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_capability_passport_py
    src_zephyr_intelligence_model_profiling_init_py -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_benchmark_suite_py
    src_zephyr_intelligence_model_profiling_init_py -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_model_discovery_py
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_intelligence_model_drift_detector_py -->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    src_zephyr_intelligence_model_evaluation_activate_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_GOV_ENFORCEMENT["(生产态 / production) D_GOV_ENFORCEMENT"]
    src_zephyr_intelligence_model_evaluation_activate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_intelligence_model_evaluation_activate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    D_ML_TRAIN["(原型态 / prototype) D_ML_TRAIN"]
    src_zephyr_intelligence_model_evaluation_inference_base_py -.->|导入依赖 / import_depends| D_ML_TRAIN
    src_zephyr_intelligence_model_evaluation_inference_base_py -.->|导入依赖 / import_depends| D_ML_TRAIN
    D_AUTONOMY_CORE["(生产态 / production) D_AUTONOMY_CORE"]
    src_zephyr_intelligence_model_evaluation_sync_engine_py -.->|导入依赖 / import_depends| D_AUTONOMY_CORE
    src_zephyr_intelligence_model_evaluation_sync_engine_py -.->|导入依赖 / import_depends| D_GOVERNANCE
    D_INTEGRATION["(生产态 / production) D_INTEGRATION"]
    src_zephyr_intelligence_model_evaluation_sync_engine_py -.->|导入依赖 / import_depends| D_INTEGRATION
    src_zephyr_intelligence_model_evaluation_unified_memory_api_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_intelligence_model_evaluation_unified_memory_api_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_intelligence_model_evaluation_unified_memory_api_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_intelligence_model_evaluation_implementations_default_inference_engine_py -.->|导入依赖 / import_depends| D_ML_TRAIN
    src_zephyr_intelligence_model_evaluation_implementations_default_inference_engine_py -.->|导入依赖 / import_depends| D_ML_TRAIN
    src_zephyr_intelligence_model_evaluation_implementations_default_inference_engine_py -.->|导入依赖 / import_depends| D_SHARED
    D_AUTONOMY_CORE -->|导入依赖 / import_depends| src_zephyr_intelligence_model_evaluation_unified_memory_api_py
    D_AUTONOMY_CORE -->|导入依赖 / import_depends| src_zephyr_intelligence_model_evaluation_reranker_py
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_intelligence_model_evaluation_reranker_py
    D_SECURITY["(原型态 / prototype) D_SECURITY"]
    D_SECURITY -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_evaluation_unified_memory_api_py
    D_TRADING["(生产态 / production) D_TRADING"]
    D_TRADING -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_init_py
    D_TRADING -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_evaluation_sync_engine_py
    D_TRADING -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_capability_passport_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_capability_passport_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_deepseek_v4_chat_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_exam_orchestrator_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_exam_test_cases_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_deepseek_v4_chat_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_exam_orchestrator_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_capability_passport_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_job_matcher_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_intelligence_model_drift_detector_py,src_zephyr_intelligence_model_evaluation_activate_py,src_zephyr_intelligence_model_evaluation_implementations_default_inference_engine_py,src_zephyr_intelligence_model_evaluation_inference_base_py,src_zephyr_intelligence_model_evaluation_reranker_py,src_zephyr_intelligence_model_evaluation_unified_memory_api_py,src_zephyr_intelligence_model_profiling_capability_passport_py,src_zephyr_intelligence_model_profiling_cli_py,src_zephyr_intelligence_model_profiling_deepseek_v4_chat_py,src_zephyr_intelligence_model_profiling_exam_judge_py,src_zephyr_intelligence_model_profiling_exam_orchestrator_py,src_zephyr_intelligence_model_profiling_exam_test_cases_py,src_zephyr_intelligence_model_profiling_job_matcher_py,src_zephyr_intelligence_model_profiling_model_discovery_py production
    class src_zephyr_intelligence_init_py,src_zephyr_intelligence_extensions_init_py,src_zephyr_intelligence_api_init_py,src_zephyr_intelligence_core_init_py,src_zephyr_intelligence_infrastructure_init_py,src_zephyr_intelligence_model_evaluation_init_py,src_zephyr_intelligence_model_evaluation_experiment_tracker_init_py,src_zephyr_intelligence_model_evaluation_implementations_init_py,src_zephyr_intelligence_model_evaluation_notebook_integration_init_py,src_zephyr_intelligence_model_evaluation_sync_engine_py,src_zephyr_intelligence_model_evaluation_target_lib_init_py,src_zephyr_intelligence_model_profiling_init_py,src_zephyr_intelligence_model_profiling_benchmark_suite_py,src_zephyr_intelligence_model_profiling_case_assembler_py,src_zephyr_intelligence_model_profiling_exam_executor_py,src_zephyr_intelligence_model_profiling_exam_rubric_py design
    class D_SHARED,D_GOVERNANCE,D_GOV_ENFORCEMENT,D_AUTONOMY_CORE,D_INTEGRATION,D_TRADING external_prod
    class D_ML_TRAIN,D_SECURITY external_design
```

#### 第 2 页 / 共 2 页

```mermaid
graph TD
    subgraph D_INTELLIGENCE["D_INTELLIGENCE 上下文管理"]
        src_zephyr_intelligence_model_profiling_pipeline_routing_init_py["(原型态 / prototype) Model Profiler — Pipeline Routing variant<br/>文件: __init__.py"]
        src_zephyr_intelligence_model_profiling_pipeline_routing_benchmark_suite_py["(生产态 / production) BenchmarkSuite — 多维度模型性能测试用例集<br/>文件: benchmark_suite.py"]
        src_zephyr_intelligence_model_profiling_pipeline_routing_cli_py["(原型态 / prototype) model-profiler.cli — 模型性能检测命令行入口<br/>文件: cli.py"]
        src_zephyr_intelligence_model_profiling_pipeline_routing_profiler_py["(生产态 / production) ModelProfiler — 核心性能分析引擎<br/>文件: profiler.py"]
        src_zephyr_intelligence_model_profiling_pipeline_routing_results_writer_py["(生产态 / production) Results Writer — 持久化 benchmark 结果，支持历...<br/>文件: results_writer.py"]
        src_zephyr_intelligence_model_profiling_pipeline_routing_task_model_learner_py["(生产态 / production) ModelTaskMatrix — 任务×模型性能学习引擎<br/>文件: task_model_learner.py"]
        src_zephyr_intelligence_model_profiling_profiler_py["(原型态 / prototype) ModelProfiler — 核心性能分析引擎<br/>文件: profiler.py"]
        src_zephyr_intelligence_model_profiling_provider_data_py["(生产态 / production) provider_data.py"]
        src_zephyr_intelligence_model_profiling_results_writer_py["(生产态 / production) Results Writer — 持久化 benchmark 结果，支持历...<br/>文件: results_writer.py"]
        src_zephyr_intelligence_model_profiling_task_model_learner_py["(原型态 / prototype) ModelTaskMatrix — 任务×模型性能学习引擎<br/>文件: task_model_learner.py"]
        src_zephyr_intelligence_models_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_intelligence_services_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_research_init_py["(生产态 / production) MOD-L09-001 Research Innovation Core.<br/>文件: __init__.py"]
    end
    src_zephyr_intelligence_model_profiling_results_writer_py -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_profiler_py
    src_zephyr_intelligence_model_profiling_pipeline_routing_results_writer_py -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_pipeline_routing_profiler_py
    src_zephyr_intelligence_model_profiling_pipeline_routing_init_py -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_pipeline_routing_benchmark_suite_py
    src_zephyr_intelligence_model_profiling_pipeline_routing_init_py -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_pipeline_routing_profiler_py
    src_zephyr_intelligence_model_profiling_pipeline_routing_init_py -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_pipeline_routing_cli_py
    src_zephyr_intelligence_model_profiling_pipeline_routing_init_py -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_pipeline_routing_task_model_learner_py
    src_zephyr_intelligence_model_profiling_pipeline_routing_profiler_py -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_pipeline_routing_benchmark_suite_py
    src_zephyr_intelligence_model_profiling_pipeline_routing_cli_py -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_pipeline_routing_results_writer_py
    src_zephyr_intelligence_model_profiling_pipeline_routing_cli_py -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_pipeline_routing_profiler_py
    D_SHARED["(原型态 / prototype) D_SHARED"]
    src_zephyr_intelligence_model_profiling_profiler_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_intelligence_model_profiling_profiler_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_intelligence_model_profiling_results_writer_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_intelligence_model_profiling_pipeline_routing_results_writer_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_intelligence_model_profiling_pipeline_routing_profiler_py -->|导入依赖 / import_depends| D_SHARED
    D_INFRA_RUNTIME["(生产态 / production) D_INFRA_RUNTIME"]
    src_zephyr_intelligence_model_profiling_pipeline_routing_task_model_learner_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    D_TRADING["(生产态 / production) D_TRADING"]
    D_TRADING -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_task_model_learner_py
    D_AUDITTEST["(原型态 / prototype) D_AUDITTEST"]
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_intelligence_model_profiling_provider_data_py
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_provider_data_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_intelligence_model_profiling_results_writer_py
    D_TRADING -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_results_writer_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_results_writer_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_intelligence_model_profiling_pipeline_routing_benchmark_suite_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_intelligence_model_profiling_pipeline_routing_benchmark_suite_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_intelligence_model_profiling_pipeline_routing_results_writer_py
    D_INTEGRATION["(生产态 / production) D_INTEGRATION"]
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_pipeline_routing_results_writer_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_intelligence_model_profiling_pipeline_routing_profiler_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_intelligence_model_profiling_pipeline_routing_profiler_py
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_pipeline_routing_profiler_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_intelligence_model_profiling_pipeline_routing_task_model_learner_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_intelligence_model_profiling_pipeline_routing_benchmark_suite_py,src_zephyr_intelligence_model_profiling_pipeline_routing_profiler_py,src_zephyr_intelligence_model_profiling_pipeline_routing_results_writer_py,src_zephyr_intelligence_model_profiling_pipeline_routing_task_model_learner_py,src_zephyr_intelligence_model_profiling_provider_data_py,src_zephyr_intelligence_model_profiling_results_writer_py,src_zephyr_research_init_py production
    class src_zephyr_intelligence_model_profiling_pipeline_routing_init_py,src_zephyr_intelligence_model_profiling_pipeline_routing_cli_py,src_zephyr_intelligence_model_profiling_profiler_py,src_zephyr_intelligence_model_profiling_task_model_learner_py,src_zephyr_intelligence_models_init_py,src_zephyr_intelligence_services_init_py design
    class D_INFRA_RUNTIME,D_TRADING,D_GOVERNANCE,D_INTEGRATION external_prod
    class D_SHARED,D_AUDITTEST external_design
```

### 运营态子图（仅 design_maturity=production 的模块和依赖）

> 仅展示已上线运行的模块（共 21 个，11 条域内依赖）。

```mermaid
graph TD
    subgraph D_INTELLIGENCE["D_INTELLIGENCE 上下文管理"]
        src_zephyr_intelligence_model_drift_detector_py["(生产态 / production) ModelDriftDetector — LLM 模型行为漂移检测。<br/>文件: model_drift_detector.py"]
        src_zephyr_intelligence_model_evaluation_activate_py["(生产态 / production) G4 Activate 门禁 — 人工激活（T-2-13-D）<br/>文件: activate.py"]
        src_zephyr_intelligence_model_evaluation_implementations_default_inference_engine_py["(生产态 / production) D_ML_TRAIN — Default Inference Engine<br/>文件: default_inference_engine.py"]
        src_zephyr_intelligence_model_evaluation_inference_base_py["(生产态 / production) inference_base.py"]
        src_zephyr_intelligence_model_evaluation_reranker_py["(生产态 / production) Cross-Encoder 重排序层 — BGE-reranker-v2-m3（T...<br/>文件: reranker.py"]
        src_zephyr_intelligence_model_evaluation_unified_memory_api_py["(生产态 / production) UnifiedMemoryAPI — RI-02 统一记忆 API（M2 跨模...<br/>文件: unified_memory_api.py"]
        src_zephyr_intelligence_model_profiling_capability_passport_py["(生产态 / production) CapabilityPassport --- AI 模型能力护照<br/>文件: capability_passport.py"]
        src_zephyr_intelligence_model_profiling_cli_py["(生产态 / production) model-profiler.cli — 模型性能检测命令行入口<br/>文件: cli.py"]
        src_zephyr_intelligence_model_profiling_deepseek_v4_chat_py["(生产态 / production) DeepSeekV4Chat --- DeepSeek V4 系列模型 API 客户端<br/>文件: deepseek_v4_chat.py"]
        src_zephyr_intelligence_model_profiling_exam_judge_py["(生产态 / production) ExamJudge --- LLM-as-judge 评分器<br/>文件: exam_judge.py"]
        src_zephyr_intelligence_model_profiling_exam_orchestrator_py["(生产态 / production) ExamOrchestrator --- 五轴入职考试主控<br/>文件: exam_orchestrator.py"]
        src_zephyr_intelligence_model_profiling_exam_test_cases_py["(生产态 / production) ExamTestCases --- v3.0.5 扩展考试题库（96 题 / ...<br/>文件: exam_test_cases.py"]
        src_zephyr_intelligence_model_profiling_job_matcher_py["(生产态 / production) JobMatcher --- 模型岗位匹配器<br/>文件: job_matcher.py"]
        src_zephyr_intelligence_model_profiling_model_discovery_py["(生产态 / production) ModelDiscovery — 枚举所有本地 Ollama 模型 + 远...<br/>文件: model_discovery.py"]
        src_zephyr_intelligence_model_profiling_pipeline_routing_benchmark_suite_py["(生产态 / production) BenchmarkSuite — 多维度模型性能测试用例集<br/>文件: benchmark_suite.py"]
        src_zephyr_intelligence_model_profiling_pipeline_routing_profiler_py["(生产态 / production) ModelProfiler — 核心性能分析引擎<br/>文件: profiler.py"]
        src_zephyr_intelligence_model_profiling_pipeline_routing_results_writer_py["(生产态 / production) Results Writer — 持久化 benchmark 结果，支持历...<br/>文件: results_writer.py"]
        src_zephyr_intelligence_model_profiling_pipeline_routing_task_model_learner_py["(生产态 / production) ModelTaskMatrix — 任务×模型性能学习引擎<br/>文件: task_model_learner.py"]
        src_zephyr_intelligence_model_profiling_provider_data_py["(生产态 / production) provider_data.py"]
        src_zephyr_intelligence_model_profiling_results_writer_py["(生产态 / production) Results Writer — 持久化 benchmark 结果，支持历...<br/>文件: results_writer.py"]
        src_zephyr_research_init_py["(生产态 / production) MOD-L09-001 Research Innovation Core.<br/>文件: __init__.py"]
    end
    src_zephyr_intelligence_model_profiling_cli_py -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_results_writer_py
    src_zephyr_intelligence_model_profiling_exam_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_capability_passport_py
    src_zephyr_intelligence_model_profiling_exam_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_exam_judge_py
    src_zephyr_intelligence_model_profiling_exam_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_provider_data_py
    src_zephyr_intelligence_model_profiling_exam_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_exam_test_cases_py
    src_zephyr_intelligence_model_profiling_exam_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_job_matcher_py
    src_zephyr_intelligence_model_profiling_model_discovery_py -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_provider_data_py
    src_zephyr_intelligence_model_profiling_job_matcher_py -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_capability_passport_py
    src_zephyr_intelligence_model_profiling_pipeline_routing_results_writer_py -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_pipeline_routing_profiler_py
    src_zephyr_intelligence_model_profiling_pipeline_routing_profiler_py -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_model_discovery_py
    src_zephyr_intelligence_model_profiling_pipeline_routing_profiler_py -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_pipeline_routing_benchmark_suite_py
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_intelligence_model_drift_detector_py -->|导入依赖 / import_depends| D_SHARED
    D_GOV_ENFORCEMENT["(生产态 / production) D_GOV_ENFORCEMENT"]
    src_zephyr_intelligence_model_evaluation_activate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_intelligence_model_evaluation_activate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    src_zephyr_intelligence_model_evaluation_activate_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_ML_TRAIN["(原型态 / prototype) D_ML_TRAIN"]
    src_zephyr_intelligence_model_evaluation_inference_base_py -.->|导入依赖 / import_depends| D_ML_TRAIN
    src_zephyr_intelligence_model_evaluation_inference_base_py -.->|导入依赖 / import_depends| D_ML_TRAIN
    src_zephyr_intelligence_model_evaluation_unified_memory_api_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_intelligence_model_evaluation_unified_memory_api_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_intelligence_model_evaluation_unified_memory_api_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_TRADING["(生产态 / production) D_TRADING"]
    src_zephyr_intelligence_model_evaluation_implementations_default_inference_engine_py -->|导入依赖 / import_depends| D_TRADING
    src_zephyr_intelligence_model_evaluation_implementations_default_inference_engine_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_intelligence_model_evaluation_implementations_default_inference_engine_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_intelligence_model_evaluation_implementations_default_inference_engine_py -.->|导入依赖 / import_depends| D_ML_TRAIN
    src_zephyr_intelligence_model_evaluation_implementations_default_inference_engine_py -.->|导入依赖 / import_depends| D_ML_TRAIN
    src_zephyr_intelligence_model_profiling_capability_passport_py -->|导入依赖 / import_depends| D_SHARED
    D_AUTONOMY_CORE["(生产态 / production) D_AUTONOMY_CORE"]
    D_AUTONOMY_CORE -->|导入依赖 / import_depends| src_zephyr_intelligence_model_evaluation_unified_memory_api_py
    D_AUTONOMY_CORE -->|导入依赖 / import_depends| src_zephyr_intelligence_model_evaluation_reranker_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_provider_data_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_results_writer_py
    D_INTEGRATION["(生产态 / production) D_INTEGRATION"]
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_pipeline_routing_profiler_py
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_pipeline_routing_results_writer_py
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_intelligence_model_evaluation_reranker_py
    D_SECURITY["(原型态 / prototype) D_SECURITY"]
    D_SECURITY -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_evaluation_unified_memory_api_py
    D_TRADING -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_results_writer_py
    D_TRADING -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_capability_passport_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_capability_passport_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_deepseek_v4_chat_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_exam_orchestrator_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_exam_test_cases_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_deepseek_v4_chat_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_intelligence_model_drift_detector_py,src_zephyr_intelligence_model_evaluation_activate_py,src_zephyr_intelligence_model_evaluation_implementations_default_inference_engine_py,src_zephyr_intelligence_model_evaluation_inference_base_py,src_zephyr_intelligence_model_evaluation_reranker_py,src_zephyr_intelligence_model_evaluation_unified_memory_api_py,src_zephyr_intelligence_model_profiling_capability_passport_py,src_zephyr_intelligence_model_profiling_cli_py,src_zephyr_intelligence_model_profiling_deepseek_v4_chat_py,src_zephyr_intelligence_model_profiling_exam_judge_py,src_zephyr_intelligence_model_profiling_exam_orchestrator_py,src_zephyr_intelligence_model_profiling_exam_test_cases_py,src_zephyr_intelligence_model_profiling_job_matcher_py,src_zephyr_intelligence_model_profiling_model_discovery_py,src_zephyr_intelligence_model_profiling_pipeline_routing_benchmark_suite_py,src_zephyr_intelligence_model_profiling_pipeline_routing_profiler_py,src_zephyr_intelligence_model_profiling_pipeline_routing_results_writer_py,src_zephyr_intelligence_model_profiling_pipeline_routing_task_model_learner_py,src_zephyr_intelligence_model_profiling_provider_data_py,src_zephyr_intelligence_model_profiling_results_writer_py,src_zephyr_research_init_py production
    class D_SHARED,D_GOV_ENFORCEMENT,D_GOVERNANCE,D_TRADING,D_AUTONOMY_CORE,D_INTEGRATION external_prod
    class D_ML_TRAIN,D_SECURITY external_design
```

### 设计态子图（仅 design_maturity=design 的模块和依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 0 个，0 条域内依赖）。

> （无设计态模块 / No design modules）

### 原型态子图（仅 design_maturity=prototype 的模块和依赖）

> 仅展示代码已写、验证中未稳定上线的原型态模块（共 22 个，5 条域内依赖）。

```mermaid
graph TD
    subgraph D_INTELLIGENCE["D_INTELLIGENCE 上下文管理"]
        src_zephyr_intelligence_init_py["(原型态 / prototype) Intelligence Domain<br/>文件: __init__.py"]
        src_zephyr_intelligence_extensions_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_intelligence_api_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_intelligence_core_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_intelligence_infrastructure_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_intelligence_model_evaluation_init_py["(原型态 / prototype) Intelligence — Model Evaluation Domain<br/>文件: __init__.py"]
        src_zephyr_intelligence_model_evaluation_experiment_tracker_init_py["(原型态 / prototype) D_RESEARCH — Research & Innovation Concrete Im...<br/>文件: __init__.py"]
        src_zephyr_intelligence_model_evaluation_implementations_init_py["(原型态 / prototype) Intelligence — Model Evaluation Concrete Imple...<br/>文件: __init__.py"]
        src_zephyr_intelligence_model_evaluation_notebook_integration_init_py["(原型态 / prototype) D_RESEARCH Research & Innovation<br/>文件: __init__.py"]
        src_zephyr_intelligence_model_evaluation_sync_engine_py["(原型态 / prototype) KB->VMS 同步引擎 — sync_to_vms() 生产者<br/>文件: sync_engine.py"]
        src_zephyr_intelligence_model_evaluation_target_lib_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_intelligence_model_profiling_init_py["(原型态 / prototype) Model Profiling — 本地 + 远程模型性能基准测试<br/>文件: __init__.py"]
        src_zephyr_intelligence_model_profiling_benchmark_suite_py["(原型态 / prototype) BenchmarkSuite — 多维度模型性能测试用例集<br/>文件: benchmark_suite.py"]
        src_zephyr_intelligence_model_profiling_case_assembler_py["(原型态 / prototype) 真实多文件注入装配器（Phase 3 极限深度）。<br/>文件: case_assembler.py"]
        src_zephyr_intelligence_model_profiling_exam_executor_py["(原型态 / prototype) ExamExecutor --- 执行式代码评测（HumanEval pass...<br/>文件: exam_executor.py"]
        src_zephyr_intelligence_model_profiling_exam_rubric_py["(原型态 / prototype) ExamRubric --- 奥赛题结构化多维清单评分（v3.0.5...<br/>文件: exam_rubric.py"]
        src_zephyr_intelligence_model_profiling_pipeline_routing_init_py["(原型态 / prototype) Model Profiler — Pipeline Routing variant<br/>文件: __init__.py"]
        src_zephyr_intelligence_model_profiling_pipeline_routing_cli_py["(原型态 / prototype) model-profiler.cli — 模型性能检测命令行入口<br/>文件: cli.py"]
        src_zephyr_intelligence_model_profiling_profiler_py["(原型态 / prototype) ModelProfiler — 核心性能分析引擎<br/>文件: profiler.py"]
        src_zephyr_intelligence_model_profiling_task_model_learner_py["(原型态 / prototype) ModelTaskMatrix — 任务×模型性能学习引擎<br/>文件: task_model_learner.py"]
        src_zephyr_intelligence_models_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_intelligence_services_init_py["(原型态 / prototype) __init__.py"]
    end
    src_zephyr_intelligence_model_profiling_profiler_py -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_benchmark_suite_py
    src_zephyr_intelligence_model_profiling_init_py -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_benchmark_suite_py
    src_zephyr_intelligence_model_profiling_init_py -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_task_model_learner_py
    src_zephyr_intelligence_model_profiling_init_py -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_profiler_py
    src_zephyr_intelligence_model_profiling_pipeline_routing_init_py -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_pipeline_routing_cli_py
    D_INTEGRATION["(生产态 / production) D_INTEGRATION"]
    src_zephyr_intelligence_model_evaluation_sync_engine_py -.->|导入依赖 / import_depends| D_INTEGRATION
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    src_zephyr_intelligence_model_evaluation_sync_engine_py -.->|导入依赖 / import_depends| D_GOVERNANCE
    D_AUTONOMY_CORE["(生产态 / production) D_AUTONOMY_CORE"]
    src_zephyr_intelligence_model_evaluation_sync_engine_py -.->|导入依赖 / import_depends| D_AUTONOMY_CORE
    D_BACKTEST["(生产态 / production) D_BACKTEST"]
    src_zephyr_intelligence_model_evaluation_implementations_init_py -.->|导入依赖 / import_depends| D_BACKTEST
    src_zephyr_intelligence_model_evaluation_experiment_tracker_init_py -.->|导入依赖 / import_depends| D_BACKTEST
    src_zephyr_intelligence_model_evaluation_notebook_integration_init_py -.->|导入依赖 / import_depends| D_BACKTEST
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_intelligence_model_profiling_case_assembler_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_intelligence_model_profiling_profiler_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_intelligence_model_profiling_profiler_py -.->|导入依赖 / import_depends| D_SHARED
    D_TRADING["(生产态 / production) D_TRADING"]
    D_TRADING -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_evaluation_sync_engine_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_exam_rubric_py
    D_TRADING -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_task_model_learner_py
    D_TRADING -.->|导入依赖 / import_depends| src_zephyr_intelligence_model_profiling_init_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_intelligence_init_py,src_zephyr_intelligence_extensions_init_py,src_zephyr_intelligence_api_init_py,src_zephyr_intelligence_core_init_py,src_zephyr_intelligence_infrastructure_init_py,src_zephyr_intelligence_model_evaluation_init_py,src_zephyr_intelligence_model_evaluation_experiment_tracker_init_py,src_zephyr_intelligence_model_evaluation_implementations_init_py,src_zephyr_intelligence_model_evaluation_notebook_integration_init_py,src_zephyr_intelligence_model_evaluation_sync_engine_py,src_zephyr_intelligence_model_evaluation_target_lib_init_py,src_zephyr_intelligence_model_profiling_init_py,src_zephyr_intelligence_model_profiling_benchmark_suite_py,src_zephyr_intelligence_model_profiling_case_assembler_py,src_zephyr_intelligence_model_profiling_exam_executor_py,src_zephyr_intelligence_model_profiling_exam_rubric_py,src_zephyr_intelligence_model_profiling_pipeline_routing_init_py,src_zephyr_intelligence_model_profiling_pipeline_routing_cli_py,src_zephyr_intelligence_model_profiling_profiler_py,src_zephyr_intelligence_model_profiling_task_model_learner_py,src_zephyr_intelligence_models_init_py,src_zephyr_intelligence_services_init_py design
    class D_INTEGRATION,D_GOVERNANCE,D_AUTONOMY_CORE,D_BACKTEST,D_SHARED,D_TRADING external_prod
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | KB->VMS 同步引擎 — sync_to_vms() 生产者 (sync_... | → | D_AUTONOMY_CORE 自治核心: VectorBridge — CE↔VMS 检索桥接 (Connect CT-CE... | 导入依赖 / import_depends |
| 2 | D_RESEARCH — Research & Innovation Concrete Im... | → | D_BACKTEST 回测: L_BACKTEST — Vectorized Backtest Engine (vecto... | 导入依赖 / import_depends |
| 3 | Intelligence — Model Evaluation Concrete Imple... | → | D_BACKTEST 回测: L_BACKTEST — Vectorized Backtest Engine (vecto... | 导入依赖 / import_depends |
| 4 | D_RESEARCH Research & Innovation (__init__.py) | → | D_BACKTEST 回测: L_BACKTEST — Backtest Engine Layer (engine_bas... | 导入依赖 / import_depends |
| 5 | G4 Activate 门禁 — 人工激活（T-2-13-D） (activ... | → | D_GOVERNANCE 生命周期管理: KB 五阶段门禁 evaluate 用的最小合法 Task（对齐 ... | 导入依赖 / import_depends |
| 6 | KB->VMS 同步引擎 — sync_to_vms() 生产者 (sync_... | → | D_GOVERNANCE 生命周期管理: SQLite 元数据层 Schema DDL + 版本化迁移框架（T-... | 导入依赖 / import_depends |
| 7 | UnifiedMemoryAPI — RI-02 统一记忆 API（M2 跨模... | → | D_GOVERNANCE 生命周期管理: Re-export shim — 真源在 zephyr.governance.kb.s... | 导入依赖 / import_depends |
| 8 | UnifiedMemoryAPI — RI-02 统一记忆 API（M2 跨模... | → | D_GOVERNANCE 生命周期管理: VMSMemoryBackend — UnifiedMemoryAPI 的 VMS 后.... | 导入依赖 / import_depends |
| 9 | G4 Activate 门禁 — 人工激活（T-2-13-D） (activ... | → | D_GOV_ENFORCEMENT 规则执行: GateEngine — KMS G1-G6 + Orc G0/G7 + 交易 G10-... | 导入依赖 / import_depends |
| 10 | G4 Activate 门禁 — 人工激活（T-2-13-D） (activ... | → | D_GOV_ENFORCEMENT 规则执行: gate_types.py | 导入依赖 / import_depends |
| 11 | ModelTaskMatrix — 任务×模型性能学习引擎 (task... | → | D_INFRA_RUNTIME 运行时集成: Pipeline 数据模型 (models.py) | 导入依赖 / import_depends |
| 12 | KB->VMS 同步引擎 — sync_to_vms() 生产者 (sync_... | → | D_INTEGRATION 管线路由: InMemoryFakeVMS — MOD-INF-011 · 零依赖测试双... | 导入依赖 / import_depends |
| 13 | D_ML_TRAIN — Default Inference Engine (default... | → | D_ML_TRAIN 训练: D_ML_TRAIN — ML Inference Base (inference_base.py) | 导入依赖 / import_depends |
| 14 | D_ML_TRAIN — Default Inference Engine (default... | → | D_ML_TRAIN 训练: D_ML_TRAIN — ML Training Base (trainer_base.py) | 导入依赖 / import_depends |
| 15 | inference_base.py | → | D_ML_TRAIN 训练: D_ML_TRAIN — ML Inference Base (inference_base.py) | 导入依赖 / import_depends |
| 16 | inference_base.py | → | D_ML_TRAIN 训练: D_ML_TRAIN — ML Training Base (trainer_base.py) | 导入依赖 / import_depends |
| 17 | ModelDriftDetector — LLM 模型行为漂移检测。 (m... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 18 | D_ML_TRAIN — Default Inference Engine (default... | → | D_SHARED 共享服务: model_serving_response.py | 导入依赖 / import_depends |
| 19 | D_ML_TRAIN — Default Inference Engine (default... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 20 | UnifiedMemoryAPI — RI-02 统一记忆 API（M2 跨模... | → | D_SHARED 共享服务: CBAC 能力检查器 (Capability-Based Access Contro... | 导入依赖 / import_depends |
| 21 | CapabilityPassport --- AI 模型能力护照 (capabil... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 22 | CapabilityPassport --- AI 模型能力护照 (capabil... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设... | 导入依赖 / import_depends |
| 23 | CapabilityPassport --- AI 模型能力护照 (capabil... | → | D_SHARED 共享服务: secrets.py —— Secrets 管理抽象（Phase 7 新增 ... | 导入依赖 / import_depends |
| 24 | 真实多文件注入装配器（Phase 3 极限深度）。 (cas... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 25 | DeepSeekV4Chat --- DeepSeek V4 系列模型 API 客... | → | D_SHARED 共享服务: secrets.py —— Secrets 管理抽象（Phase 7 新增 ... | 导入依赖 / import_depends |
| 26 | JobMatcher --- 模型岗位匹配器 (job_matcher.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 27 | ModelDiscovery — 枚举所有本地 Ollama 模型 + 远... | → | D_SHARED 共享服务: constants.py —— 共享枚举 & 常量集中 re-export... | 导入依赖 / import_depends |
| 28 | ModelProfiler — 核心性能分析引擎 (profiler.py) | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 ... | 导入依赖 / import_depends |
| 29 | Results Writer — 持久化 benchmark 结果，支持历... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 ... | 导入依赖 / import_depends |
| 30 | ModelProfiler — 核心性能分析引擎 (profiler.py) | → | D_SHARED 共享服务: constants.py —— 共享枚举 & 常量集中 re-export... | 导入依赖 / import_depends |
| 31 | ModelProfiler — 核心性能分析引擎 (profiler.py) | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 ... | 导入依赖 / import_depends |
| 32 | Results Writer — 持久化 benchmark 结果，支持历... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 ... | 导入依赖 / import_depends |
| 33 | D_ML_TRAIN — Default Inference Engine (default... | → | D_TRADING 交易运营: model_serving_request.py | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_AUDITTEST 审计测试套件: test_capability_passport.py | → | CapabilityPassport --- AI 模型能力护照 (capabil... | 测试依赖 / test_depends |
| 2 | D_AUDITTEST 审计测试套件: test_cross_layer.py | → | inference_base.py | 测试依赖 / test_depends |
| 3 | D_AUDITTEST 审计测试套件: DM-202009: F10 红蓝对抗测试套件。 (test_f10_red... | → | CapabilityPassport --- AI 模型能力护照 (capabil... | 测试依赖 / test_depends |
| 4 | D_AUDITTEST 审计测试套件: DM-202009: F10 红蓝对抗测试套件。 (test_f10_red... | → | ExamOrchestrator --- 五轴入职考试主控 (exam_orc... | 测试依赖 / test_depends |
| 5 | D_AUDITTEST 审计测试套件: DM-202009: F10 红蓝对抗测试套件。 (test_f10_red... | → | ExamTestCases --- v3.0.5 扩展考试题库（96 题 / ... | 测试依赖 / test_depends |
| 6 | D_AUDITTEST 审计测试套件: DM-202009: F10 红蓝对抗测试套件。 (test_f10_red... | → | Results Writer — 持久化 benchmark 结果，支持历... | 测试依赖 / test_depends |
| 7 | D_AUDITTEST 审计测试套件: test_kb_activate.py | → | G4 Activate 门禁 — 人工激活（T-2-13-D） (activ... | 测试依赖 / test_depends |
| 8 | D_AUDITTEST 审计测试套件: test_kb_pipeline_activate.py | → | G4 Activate 门禁 — 人工激活（T-2-13-D） (activ... | 测试依赖 / test_depends |
| 9 | D_AUDITTEST 审计测试套件: test_kb_reranker.py | → | Cross-Encoder 重排序层 — BGE-reranker-v2-m3（T... | 测试依赖 / test_depends |
| 10 | D_AUDITTEST 审计测试套件: test_kb_unified_memory_api.py | → | UnifiedMemoryAPI — RI-02 统一记忆 API（M2 跨模... | 测试依赖 / test_depends |
| 11 | D_AUDITTEST 审计测试套件: test_benchmark_suite.py | → | BenchmarkSuite — 多维度模型性能测试用例集 (ben... | 测试依赖 / test_depends |
| 12 | D_AUDITTEST 审计测试套件: calibrate_model_diff.py 单元测试（P1-3 配套, 零... | → | CapabilityPassport --- AI 模型能力护照 (capabil... | 测试依赖 / test_depends |
| 13 | D_AUDITTEST 审计测试套件: test_cli.py | → | model-profiler.cli — 模型性能检测命令行入口 (c... | 测试依赖 / test_depends |
| 14 | D_AUDITTEST 审计测试套件: test_deepseek_v4_chat.py | → | DeepSeekV4Chat --- DeepSeek V4 系列模型 API 客... | 测试依赖 / test_depends |
| 15 | D_AUDITTEST 审计测试套件: test_exam_orchestrator.py | → | CapabilityPassport --- AI 模型能力护照 (capabil... | 测试依赖 / test_depends |
| 16 | D_AUDITTEST 审计测试套件: test_exam_orchestrator.py | → | ExamJudge --- LLM-as-judge 评分器 (exam_judge.py) | 测试依赖 / test_depends |
| 17 | D_AUDITTEST 审计测试套件: test_exam_orchestrator.py | → | ExamOrchestrator --- 五轴入职考试主控 (exam_orc... | 测试依赖 / test_depends |
| 18 | D_AUDITTEST 审计测试套件: test_exam_orchestrator.py | → | ExamTestCases --- v3.0.5 扩展考试题库（96 题 / ... | 测试依赖 / test_depends |
| 19 | D_AUDITTEST 审计测试套件: test_exam_test_cases.py | → | ExamTestCases --- v3.0.5 扩展考试题库（96 题 / ... | 测试依赖 / test_depends |
| 20 | D_AUDITTEST 审计测试套件: test_job_matcher.py | → | CapabilityPassport --- AI 模型能力护照 (capabil... | 测试依赖 / test_depends |
| 21 | D_AUDITTEST 审计测试套件: test_job_matcher.py | → | JobMatcher --- 模型岗位匹配器 (job_matcher.py) | 测试依赖 / test_depends |
| 22 | D_AUDITTEST 审计测试套件: test_model_discovery.py | → | ModelDiscovery — 枚举所有本地 Ollama 模型 + 远... | 测试依赖 / test_depends |
| 23 | D_AUDITTEST 审计测试套件: test_model_drift_detector.py | → | ModelDriftDetector — LLM 模型行为漂移检测。 (m... | 测试依赖 / test_depends |
| 24 | D_AUDITTEST 审计测试套件: test_profiler.py | → | BenchmarkSuite — 多维度模型性能测试用例集 (ben... | 测试依赖 / test_depends |
| 25 | D_AUDITTEST 审计测试套件: test_profiler.py | → | ModelProfiler — 核心性能分析引擎 (profiler.py) | 测试依赖 / test_depends |
| 26 | D_AUDITTEST 审计测试套件: test_provider_data.py | → | provider_data.py | 测试依赖 / test_depends |
| 27 | D_AUDITTEST 审计测试套件: test_results_writer.py | → | ModelProfiler — 核心性能分析引擎 (profiler.py) | 测试依赖 / test_depends |
| 28 | D_AUDITTEST 审计测试套件: test_results_writer.py | → | Results Writer — 持久化 benchmark 结果，支持历... | 测试依赖 / test_depends |
| 29 | D_AUDITTEST 审计测试套件: test_task_gate.py | → | CapabilityPassport --- AI 模型能力护照 (capabil... | 测试依赖 / test_depends |
| 30 | D_AUDITTEST 审计测试套件: test_task_model_learner.py | → | ModelTaskMatrix — 任务×模型性能学习引擎 (task... | 测试依赖 / test_depends |
| 31 | D_AUTONOMY_CORE 自治核心: ContextAssembler — 上下文装配、校验、影子留档 ... | → | Cross-Encoder 重排序层 — BGE-reranker-v2-m3（T... | 导入依赖 / import_depends |
| 32 | D_AUTONOMY_CORE 自治核心: ContextAssembler — 上下文装配、校验、影子留档 ... | → | UnifiedMemoryAPI — RI-02 统一记忆 API（M2 跨模... | 导入依赖 / import_depends |
| 33 | D_GOVERNANCE 生命周期管理: 模型能力差异校准脚本（P1-3 治本）。 (calibrate_... | → | CapabilityPassport --- AI 模型能力护照 (capabil... | 导入依赖 / import_depends |
| 34 | D_GOVERNANCE 生命周期管理: C-track 端到端演示 —— 全流水线一次性运行 (dem... | → | D_ML_TRAIN — Default Inference Engine (default... | 导入依赖 / import_depends |
| 35 | D_GOVERNANCE 生命周期管理: 诊断 breadth_failed 能力的根因。 (diagnose_brea... | → | DeepSeekV4Chat --- DeepSeek V4 系列模型 API 客... | 导入依赖 / import_depends |
| 36 | D_GOVERNANCE 生命周期管理: 诊断 breadth_failed 能力的根因。 (diagnose_brea... | → | ExamOrchestrator --- 五轴入职考试主控 (exam_orc... | 导入依赖 / import_depends |
| 37 | D_GOVERNANCE 生命周期管理: 诊断 breadth_failed 能力的根因。 (diagnose_brea... | → | ExamTestCases --- v3.0.5 扩展考试题库（96 题 / ... | 导入依赖 / import_depends |
| 38 | D_GOVERNANCE 生命周期管理: 模型快速能力画像脚本 (P2 三级模式 Quick 入口)。... | → | CapabilityPassport --- AI 模型能力护照 (capabil... | 导入依赖 / import_depends |
| 39 | D_GOVERNANCE 生命周期管理: 模型快速能力画像脚本 (P2 三级模式 Quick 入口)。... | → | ExamOrchestrator --- 五轴入职考试主控 (exam_orc... | 导入依赖 / import_depends |
| 40 | D_GOVERNANCE 生命周期管理: 模型快速能力画像脚本 (P2 三级模式 Quick 入口)。... | → | JobMatcher --- 模型岗位匹配器 (job_matcher.py) | 导入依赖 / import_depends |
| 41 | D_GOVERNANCE 生命周期管理: DeepSeek V4 入职考试运行脚本 (run_deepseek_v4_e... | → | DeepSeekV4Chat --- DeepSeek V4 系列模型 API 客... | 导入依赖 / import_depends |
| 42 | D_GOVERNANCE 生命周期管理: DeepSeek V4 入职考试运行脚本 (run_deepseek_v4_e... | → | ExamOrchestrator --- 五轴入职考试主控 (exam_orc... | 导入依赖 / import_depends |
| 43 | D_GOVERNANCE 生命周期管理: Ollama 入职考试运行脚本 (run_ollama_exam.py) | → | ExamOrchestrator --- 五轴入职考试主控 (exam_orc... | 导入依赖 / import_depends |
| 44 | D_GOVERNANCE 生命周期管理: 考试系统评分逻辑单元测试（合成数据，零成本，不.... | → | CapabilityPassport --- AI 模型能力护照 (capabil... | 导入依赖 / import_depends |
| 45 | D_GOVERNANCE 生命周期管理: 考试系统评分逻辑单元测试（合成数据，零成本，不.... | → | ExamOrchestrator --- 五轴入职考试主控 (exam_orc... | 导入依赖 / import_depends |
| 46 | D_GOVERNANCE 生命周期管理: 考试系统评分逻辑单元测试（合成数据，零成本，不.... | → | ExamRubric --- 奥赛题结构化多维清单评分（v3.0.5... | 导入依赖 / import_depends |
| 47 | D_GOVERNANCE 生命周期管理: 考试系统评分逻辑单元测试（合成数据，零成本，不.... | → | ExamTestCases --- v3.0.5 扩展考试题库（96 题 / ... | 导入依赖 / import_depends |
| 48 | D_GOVERNANCE 生命周期管理: model_router.py | → | provider_data.py | 导入依赖 / import_depends |
| 49 | D_GOVERNANCE 生命周期管理: model_router.py | → | Results Writer — 持久化 benchmark 结果，支持历... | 导入依赖 / import_depends |
| 50 | D_GOV_SCRIPTS 脚本治理: 考试题库一致性检查——根因治本，防止"定义-注册.... | → | ExamTestCases --- v3.0.5 扩展考试题库（96 题 / ... | 导入依赖 / import_depends |
| 51 | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | Cross-Encoder 重排序层 — BGE-reranker-v2-m3（T... | 导入依赖 / import_depends |
| 52 | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | ModelProfiler — 核心性能分析引擎 (profiler.py) | 导入依赖 / import_depends |
| 53 | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | Results Writer — 持久化 benchmark 结果，支持历... | 导入依赖 / import_depends |
| 54 | D_SECURITY 对抗验证: kb_bridge.py | → | UnifiedMemoryAPI — RI-02 统一记忆 API（M2 跨模... | 导入依赖 / import_depends |
| 55 | D_TRADING 交易运营: AutoRuntimeCore — 三层运行时运营中心（系统大脑... | → | Model Profiling — 本地 + 远程模型性能基准测试 ... | 导入依赖 / import_depends |
| 56 | D_TRADING 交易运营: AutoRuntimeCore — 三层运行时运营中心（系统大脑... | → | Results Writer — 持久化 benchmark 结果，支持历... | 导入依赖 / import_depends |
| 57 | D_TRADING 交易运营: AutoRuntimeCore — 三层运行时运营中心（系统大脑... | → | ModelTaskMatrix — 任务×模型性能学习引擎 (task... | 导入依赖 / import_depends |
| 58 | D_TRADING 交易运营: boot_hooks.py | → | KB->VMS 同步引擎 — sync_to_vms() 生产者 (sync_... | 导入依赖 / import_depends |
| 59 | D_TRADING 交易运营: TaskGate --- 任务门控 (task_gate.py) | → | CapabilityPassport --- AI 模型能力护照 (capabil... | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 12 个外部域直接连接（出边 33 条 + 入边 60 条 = 93 条）。只显示直接连接的域，不展开具体节点。

```mermaid
graph LR
    D_INTELLIGENCE["D_INTELLIGENCE<br/>上下文管理"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_ML_TRAIN["D_ML_TRAIN<br/>训练"]
    D_BACKTEST["D_BACKTEST<br/>回测"]
    D_GOV_ENFORCEMENT["D_GOV_ENFORCEMENT<br/>规则执行"]
    D_TRADING["D_TRADING<br/>交易运营"]
    D_INFRA_RUNTIME["D_INFRA_RUNTIME<br/>运行时集成"]
    D_INTEGRATION["D_INTEGRATION<br/>管线路由"]
    D_AUTONOMY_CORE["D_AUTONOMY_CORE<br/>自治核心"]
    D_AUDITTEST["D_AUDITTEST<br/>审计测试套件"]
    D_GOV_SCRIPTS["D_GOV_SCRIPTS<br/>脚本治理"]
    D_SECURITY["D_SECURITY<br/>对抗验证"]
    D_INTELLIGENCE -->|16条 导入依赖 / import_depends| D_SHARED
    D_INTELLIGENCE -->|4条 导入依赖 / import_depends| D_GOVERNANCE
    D_INTELLIGENCE -->|4条 导入依赖 / import_depends| D_ML_TRAIN
    D_INTELLIGENCE -->|3条 导入依赖 / import_depends| D_BACKTEST
    D_INTELLIGENCE -->|2条 导入依赖 / import_depends| D_GOV_ENFORCEMENT
    D_INTELLIGENCE -->|1条 导入依赖 / import_depends| D_TRADING
    D_INTELLIGENCE -->|1条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_INTELLIGENCE -->|1条 导入依赖 / import_depends| D_INTEGRATION
    D_INTELLIGENCE -->|1条 导入依赖 / import_depends| D_AUTONOMY_CORE
    D_AUDITTEST -->|31条 测试依赖 / test_depends| D_INTELLIGENCE
    D_GOVERNANCE -->|17条 导入依赖 / import_depends| D_INTELLIGENCE
    D_TRADING -->|5条 导入依赖 / import_depends| D_INTELLIGENCE
    D_INTEGRATION -->|3条 导入依赖 / import_depends| D_INTELLIGENCE
    D_AUTONOMY_CORE -->|2条 导入依赖 / import_depends| D_INTELLIGENCE
    D_GOV_SCRIPTS -->|1条 导入依赖 / import_depends| D_INTELLIGENCE
    D_SECURITY -->|1条 导入依赖 / import_depends| D_INTELLIGENCE
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
