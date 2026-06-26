---
module_id: KE-219--------ri-01-07---wave-1-r-003
title: 2.9 运行时集成层（RI-01~07，**Wave 1 R83/R84 增补**）
category: documentation
ttl: permanent
---

# 2.9 运行时集成层（RI-01~07，**Wave 1 R83/R84 增补**）

2.9 运行时集成层（RI-01~07，**Wave 1 R83/R84 增补**）

> 来源：B6 施工图 `construction-plan-runtime-integration-and-cl-gaps.md`。**Wave 1 修正**项以加粗标注。

| 模块 | 路径 | 权限 | 判定理由 | 审批要求 |
|------|------|------|---------|---------|
| RI-01 ContextEngineRuntime | `src/zephyr/context-engine/runtime_integration.py` | Human-Gated | 上下文预算影响所有 AI 调用 | Owner 审批 |
| **RI-02 UnifiedMemoryAPI** | `src/zephyr/kb/unified_memory_api.py` | **Human-Gated**（**Wave 1 修正**：原草稿 AI-Modifiable 偏松）| 检索阈值影响 Agent 决策质量 | Owner 审批 |
| **RI-03 FileWatchRouter** | `src/zephyr/orchestrator/trigger_router.py` | **Human-Gated**（**Wave 1 修正**：原草稿 AI-Modifiable 偏松）| 路由策略影响 Agent 行为 | Owner 审批 |
| RI-04 FeedbackEngine M4-A decide | `src/zephyr/feedback-loop/decision_engine.py` | Human-Gated | 评估标准影响所有质量门禁 | Owner 审批 |
| **RI-04 FeedbackEngine M4-B auto_repair** | `src/zephyr/feedback-loop/auto_repair.py` | **Immutable Core**（Wave 0 R76 已锁，Wave 1 维持）| Self-Modification 递归风险 | Owner + R-XXX |
| RI-05 ProcessSandbox（L2a）| `src/zephyr/llm-security/process_sandbox.py` | Immutable Core | 安全核心 | Owner + R-XXX |
| RI-05 OutputValidator（L3 schema）| `src/zephyr/llm-security/output_validator.py` | Human-Gated | schema 可演进 | Owner 审批 |
| RI-05 EditorConfigGate（CL-021）| `src/zephyr/llm-security/editor_config_gate.py` | Immutable Core | 编码规则核心 | Owner + R-XXX |
| RI-06 HandoffAutoLoader | `src/zephyr/mcp/handoff_auto_loader.py` | Human-Gated | Session 状态管理 | Owner 审批 |
| **RI-07 DriftDetector 算法** | `src/zephyr/gates/drift-detector.py` | AI-Modifiable（**Wave 1 修正**：原整体 Human-Gated 偏紧，需拆分） | 算法可优化 | 写 Provenance |
| **RI-07 DriftDetector 阈值** | `config/drift_thresholds.yaml` | Human-Gated（**Wave 1 修正**） | 阈值影响审计 | Owner 审批 |
