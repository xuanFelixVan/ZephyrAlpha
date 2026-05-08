---


task_id: TASK-MOD-INF-001-0007
module_id: MOD-INF-001
title: "M-25~M-27 运行时增强模块 + 蓝图外已有实现引用"
doc_type: task_card
status: done
priority: P0
layer: L01
layer_name: infrastructure
functional_domain: observability
owner: ZephyrAlpha-Owner
assignee: AI-GLM-5.1
created_by: AI-GLM-5.1
created_at: 2026-05-07T02:59:00+08:00
valid_from: 2026-05-07
ttl: permanent
belongs_to: MOD-INF-001
dependencies:
  - TASK-MOD-INF-001-0005
  - TASK-MOD-INF-001-0006
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\reasoning_spans.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\cost_estimator.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\semantic_cache.py"
acceptance_criteria:
  - "M-25 reasoning_spans.py: OTel GenAI Semantic Conventions对齐，agent.reasoning span+steps events"
  - "M-26 cost_estimator.py: Pre-flight Estimation, 预算超限→拒绝或降级建议"
  - "M-27 semantic_cache.py: ChromaDB语义缓存，相似度>0.95命中，TTL 24h"
  - "蓝图外6个已有实现（context_budget_tracker/doc_compressor/circuit_breaker/agent_health_monitor等）引用路径正确"
rollback_instructions:
  - "M-25~M-27可独立禁用"
  - "蓝图外引用不受影响"
context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
    sections: ["§6.2 M-25~M-27", "§6.3 蓝图外已有实现", "§9 多级 Token Budget", "§11.2 语义缓存", "§12 OTel语义规范", "§19.2 蓝图外已有实现"]
    purpose: "提取运行时增强模块+蓝图外引用映射"
tags:
  - capacity-assurance
  - runtime-modules
  - M-25-to-M-27
  - otel-semantic
  - cost-estimator
  - semantic-cache
phase: phase_0_foundation
estimated_effort_minutes: 180
ai_autonomy: AI-Modifiable
governance_layer: GOV-P1
runtime_plane: RP-3
source_blueprint: "MOD-INF-001"
source_section: "蓝图 §6.2+§6.3 M-25~M-27 + 蓝图外已有实现"
description: "M-25~M-27 运行时增强模块 + 蓝图外已有实现引用"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\reasoning_spans.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\cost_estimator.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\semantic_cache.py"
forbidden_touch:
  - "D:\ZephyrAlpha\docs\01_policies_and_standards\**\*.md"
  - "D:\ZephyrAlpha\src\zephyr\shared\schemas.py"
applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号格式 TASK-{DOMAIN}-{NNNN}"
  - module_id: "PS-STD-011"
  - module_id: "ADR-0040"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 54000
timeout_minutes: 180
depends_on:
  - TASK-MOD-INF-001-0005
  - TASK-MOD-INF-001-0006
blocked_by: []
tags_fn: ["infra"]
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo: ["MOD-INF-001"]
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []


---



# M-25~M-27 运行时增强模块 + 蓝图外已有实现引用

## 1. 模块清单

### 1.1 M-25~M-27（蓝图 §6.2 v2.0.0 新增）

| 模块ID | 模块名称 | 预期路径 | 对标来源 | AI自治权限 |
|--------|---------|---------|---------|-----------|
| M-25 | reasoning_spans.py | `src/zephyr/shared/reasoning_spans.py` | OpenTelemetry GenAI Semantic Conventions | AI-Modifiable |
| M-26 | cost_estimator.py | `src/zephyr/shared/cost_estimator.py` | AI Agent Rate Limiting | AI-Modifiable |
| M-27 | semantic_cache.py | `src/zephyr/shared/semantic_cache.py` | Agent 成本控制实战 | AI-Modifiable |

### 1.2 蓝图外已有实现（蓝图 §6.3）

| 已有实现 | 实际路径 | 归属蓝图 |
|---------|---------|---------|
| Token 预算管理器 (L1/L2/L3) | `src/zephyr/context_engine/context_budget_tracker.py` | context-engine |
| 上下文压缩器 (DocCompressor) | `src/zephyr/context_engine/doc_compressor.py` | context-engine |
| 熔断器 (CBGManager + L08) | `src/zephyr/gates/circuit_breaker.py` | gate-engine |
| Agent SLO 监控 (5 项 SLO) | `src/zephyr/orchestrator/agent_health_monitor.py` | orchestrator |
| AI 行为审计日志 | `src/zephyr/llm_security/behavior_audit_logger.py` | llm-security |
| 输入消毒器 (InputSanitizer) | `src/zephyr/llm_security/input_sanitizer.py` | llm-security |
| 原子事务管理器 (ATM) | `src/zephyr/db/atomic_transaction_manager.py` | database |
| SQLite Schema DDL + init_db | `src/zephyr/db/sqlite_schema.py` | database |
| MCP 工具限流 (rate_limit_qps) | `src/zephyr/mcp/tool_contracts.yaml` | mcp-servers |
| L12 Metrics 骨架 | `src/zephyr/l12_system_telemetry/metrics/__init__.py` | system-telemetry |
| 任务反馈收集器 | `src/zephyr/feedback_loop/feedback_collector.py` | feedback-loop |

## 2. 施工内容

### 2.1 M-25: reasoning_spans.py

OTel GenAI Semantic Conventions 对齐：

```python
tracer = trace.get_tracer("zephyr.capacity-assurance")

async def trace_reasoning(agent_name: str, task: str, steps: list[str]):
    with tracer.start_as_current_span("agent.reasoning") as span:
        span.set_attribute("gen_ai.system", "zephyr")
        span.set_attribute("gen_ai.request.model", agent_name)
        span.set_attribute("agent.task", task)
        span.set_attribute("agent.steps.count", len(steps))
```

W3C TraceContext 传播：
- 所有 ContractBus 调用自动注入 `traceparent` + `tracestate`
- 所有事件总线消息携带 `trace_context` 字段
- 与 `behavior_audit_logger.py` 集成：审计日志关联 Trace ID

### 2.2 M-26: cost_estimator.py

Pre-flight Estimation（执行前成本预估）：

```python
class CostEstimator:
    async def estimate(self, prompt_tokens: int, model: str) -> CostEstimate:
        estimated_cost = prompt_tokens * MODEL_COST[model].input_per_1k / 1000
        if estimated_cost > self.session_budget_remaining:
            return CostEstimate(affordable=False, suggestion="downgrade_model")
        return CostEstimate(affordable=True, estimated_cost=estimated_cost)
```

与 Token Budget 四级体系的关系（蓝图 §9.3）：
- Level 2: session级 → `context_budget_tracker.py`（已有，由 context-engine 管理）
- Level 1: MCP工具级 → `tool_contracts.yaml`（已有，由 mcp-servers 管理）
- Level 3/4: org/global级 → 本蓝图 M-21 + M-26 新增

### 2.3 M-27: semantic_cache.py

ChromaDB 语义缓存：
- 缓存键：prompt 语义向量（BGE-M3 embedding）
- 命中阈值：余弦相似度 > 0.95
- TTL：24 小时
- 失效策略：源数据变更时自动失效
- 复用已有 ChromaDB 基础设施

## 3. 蓝图外已有实现集成验证

本任务需验证以下已实现模块的路径正确性并确保集成：

1. `context_budget_tracker.py` → Level 2 session级Token预算 ✓（已有测试）
2. `circuit_breaker.py` → M-13 fault_isolator子集，与 M-22 kill_switch.py 联动
3. `agent_health_monitor.py` → 5项SLO + 三态健康
4. `behavior_audit_logger.py` → 4种事件 + JSONL审计日志
5. `atomic_transaction_manager.py` → DB操作原子性保证

## 4. 验收标准

1. M-25 reasoning_spans 正确生成 agent.reasoning span
2. M-25 TraceContext 通过 ContractBus 正确传播
3. M-26 cost_estimator Pre-flight估算正确，超限→拒绝
4. M-27 semantic_cache 相似度>0.95命中 + TTL 24h失效
5. 蓝图外7个引用路径正确 + 实现状态与实际一致
6. ruff 零错误 + mypy strict 通过 + pytest > 80%