---
task_id: "TASK-INF-0216"
source_blueprint: "MOD-INF-014"
source_section: "§16 集成目标（9个集成目标）"
title: "LSG与ZephyrAlpha 9个模块集成实现——介入点+调用时机+fallback策略"
description: |
  实现 LSG 与 ZephyrAlpha 现有模块的全量集成：
  1. shared/llm_client.py——system prompt入口集成 L2 PromptProtectionLayer
  2. shared/llm_client.py——LLM输出出口集成 L3 OutputSecurityLayer
  3. Agent系统tool_call入口集成 L4 AgentSecurityLayer
  4. Agent系统tool_result入口集成 ToolResultTransform+L1间接注入检测
  5. TaskSystem——AI生成task解析前集成 L3 Schema验证+AI代码信任边界
  6. TaskSystem/SpecSystem——蓝图/Spec生成后集成 L1+L3+L4 AST/Grammar/能力/安全/结构审计
  7. RAG pipeline——文档块入口集成 L1+L3 PII脱敏+注入扫描
  8. CI/CD pipeline——L6异常检测+L0 产出物SHA256基线+L0 pipeline门禁
  9. ModuleRegistry——模块生命周期安全门禁集成 (L0+L1+L3+L7+SecurityFence)
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\llm_client.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-infrastructure\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\llm_client.py"
    description: "集成 LSG L2 (prompt entry) + L3 (output exit)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\llm_client_adapter.py"
    description: "LSG 注入器——llm_client.py 的 Prompt+Output wrapper"
  - path: "D:\\ZephyrAlpha\\tests\\integration\\test_lsg_integration.py"
    description: "9个集成目标的端到端集成测试"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\llm_client.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\llm_client_adapter.py"
  - "D:\\ZephyrAlpha\\tests\\integration\\test_lsg_integration.py"
forbidden_touch: []
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
    reason: "§16 完整集成目标定义"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1","M2","M3"]
estimated_tokens: 12000
timeout_minutes: 60
acceptance_criteria:
  - "llm_client.py 在 build_prompt() 中嵌入 L2 PromptProtectionLayer"
  - "llm_client.py 在 parse_response() 中嵌入 L3 OutputSecurityLayer"
  - "Agent 在 tool_call 前嵌入 L4 AgentSecurityLayer"
  - "Agent 在 tool_result 回注前嵌入 L1 ToolResultTransformGuard+indirect scan"
  - "TaskSystem 在 parse_ai_task() 时嵌入 L3 validate_schema+AIGeneratedCodeTrustBoundary"
  - "SpecSystem/BlueprintReview 在 analyze() 返回后嵌入 L1+L3+L4 六维审计+安全Plugin"
  - "RAG pipeline 在 document_chunk_entry 嵌入 L1+L3 脱敏+扫描"
  - "CI/CD pipeline 门禁: CodeIntegrityGuard+L6 anomaly+L0 AI-BOM"
  - "ModuleRegistry lifecycle hook: before_register/before_enable/before_disable 嵌入 L0+L1+L3+L7+SecurityFence"
  - "Feedback Loop (MOD-INF-010): L6异常事件(ANOMALY_DETECTED) → FLE.ingest() → 模式学习"
  - "Audit Trail (MOD-INF-020): L6全部安全事件 → behavior_audit_logger.log_security_event() → 审计链写入"
  - "MCP Servers (MOD-INF-013): L0 verify_mcp_server() + L4 tool_descriptor_audit() → MCP工具名/描述完整性审计"
  - "Telemetry (MOD-INF-015): L6 dashboard_metrics → Telemetry.collect(security_metrics) → 系统可观测面板"
  - "9条集成端到端测试全部通过"
rollback_instructions: |
  1. 将 llm_client.py 回退至集成前版本
  2. 删除 llm_client_adapter.py
  3. 删除 test_lsg_integration.py
depends_on: ["TASK-INF-0201","TASK-INF-0203","TASK-INF-0204","TASK-INF-0205","TASK-INF-0206","TASK-INF-0207","TASK-INF-0208","TASK-INF-0209","TASK-INF-0210"]
blocked_by: []
status: "created"
tags_fn: ["integration","security"]
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo: ["MOD-INF-014"]
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---

# 目标

实现 LSG 与 ZephyrAlpha 9 个下游模块的介入点集成。每个集成点确保安全层在数据流入/流出 LLM 时正确介入。

## 执行步骤

### 读
- `D:\ZephyrAlpha\docs\03_modules\_cross_layer\llm-security\blueprint.md` §16
- 9 个集成目标的各自蓝图

### 做
1. llm_client.py → L2 prompt build + L3 output parse wrapper (Context Engine MOD-INF-008)
2. Agent tool_call/tool_result → L4 Agent + L1 indirect injection hooks (Agent RBAC MOD-INF-018)
3. TaskSystem/SpecSystem → L3 Schema + AI code trust audit hooks (Gate Engine MOD-INF-007)
4. RAG pipeline → L1+L3 document chunk guards (Vector Memory MOD-INF-011)
5. CI/CD pipeline → L0+L6+L7 pipeline gates (Pipeline MOD-INF-009)
6. ModuleRegistry → L0+L1+L3+L7 lifecycle hooks
7. Feedback Loop (MOD-INF-010) → L6 ANOMALY_DETECTED→FLE.ingest()
8. Audit Trail (MOD-INF-020) → L6 security events→audit logger
9. MCP Servers (MOD-INF-013) → L0 verify_mcp_server + L4 tool descriptor audit
10. Telemetry (MOD-INF-015) → L6 dashboard metrics→Telemetry.collect()
11. 编写 9 条端到端集成测试
