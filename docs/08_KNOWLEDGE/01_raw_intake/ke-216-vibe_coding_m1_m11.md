---
module_id: KE-196--------m1-m11-003
title: 2.3 Vibe Coding 基础设施模块（M1-M11，本次终审产出）
category: documentation
ttl: permanent
---

# 2.3 Vibe Coding 基础设施模块（M1-M11，本次终审产出）

2.3 Vibe Coding 基础设施模块（M1-M11，本次终审产出）

| 模块 | 组件 | 权限 | 判定理由 |
|------|------|------|---------|
| **M1 上下文引擎** | context_budget_tracker / prompt_registry | Human-Gated | 预算变更影响所有 AI 调用 |
| **M2 记忆系统** | vector-memory / decisions store | Human-Gated | 检索影响 Agent 决策质量 |
| **M2 kb 基础设施** | kb/kb_repo.py / kb/chromadb_init.py | Human-Gated | 存储层与 Schema 影响记忆完整性 |
| **M2 kb 加工链** | kb/（ingest / extract / analyze / triage / activate / batch_ingest / graph_validator / embedding_migrate） | AI-Modifiable | 数据加工流水线可 AI 优化 |
| **M2 Provenance Chain** | provenance_logger.py | **Immutable Core** | 审计记录不可被 AI 修改 |
| **M3 Agent 编排** | orchestrator / AgentRouter | Human-Gated | 路由策略 |
| **M4-A 反馈闭环 决策引擎** | evolution_engine.py | Human-Gated | 评估标准影响所有质量门禁 |
| **M4-B 自动修复执行器** | auto_fixer.py | **Immutable Core**（**修正**：原 Human-Gated 偏低） | 执行器直接改代码，核心逻辑不可 AI 自主决策 |
| **M5 LLM 安全网关** | llm-security / input_sanitizer | Immutable Core | 安全网关 |
| **M5 Provenance Chain** | （集成 M2）| Immutable Core | 审计记录 |
| **M6 Session 接力** | session_carryover.py | Human-Gated | 必须含 agent_role + task_id |
| **M7 漂移检测算法** | drift-detector.py | AI-Modifiable | 算法可优化 |
| **M7 漂移检测阈值** | drift_thresholds.yaml | Human-Gated（**修正**） | 阈值影响审计 |
| **M8 代码健康度验证器** | code_health_validator.py | AI-Modifiable | 评分算法可 AI 优化 |
| **M8 代码健康度阈值** | health_thresholds.yaml | Human-Gated | 阈值变更需审批 |
| **M9 审计链** | provenance_chain.py | Immutable Core | 审计记录不可 AI 改 |
| **M10 Kill Switch** | kill_switch.py | Immutable Core | 触发/恢复需 Owner 确认 |
| **M11 不变量守卫** | invariant_rules.py | Immutable Core | 修改需 Owner + rationale-log |
