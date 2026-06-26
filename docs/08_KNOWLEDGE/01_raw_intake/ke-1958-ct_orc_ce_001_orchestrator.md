---
module_id: KE-1867
status: active
title: 2.3 CT-ORC-CE-001：Orchestrator ↔ Context Engine
category: module_blueprint
ttl: permanent
---

# 2.3 CT-ORC-CE-001：Orchestrator ↔ Context Engine

2.3 CT-ORC-CE-001：Orchestrator ↔ Context Engine

```yaml
contract: CT-ORC-CE-001
title: "任务启动时上下文构建请求"
systems:
  - role: consumer
    name: context-engine
    path: "src/zephyr/context-engine/"
    blueprint: "MOD-CONTEXT_ENGINE"
  - role: producer
    name: orchestrator
    path: "src/zephyr/orchestrator/"
    blueprint: "MOD-TASK_SYSTEM"

interaction:
  trigger: "Orc.create_session(task_id)"
  sequence:
    step_1:
      actor: Orc
      action: "发送 session_context_request → CE"
      payload:
        task_id: "string"
        task_type: "enum[MODEL_BUILD, AUDIT, DOC_WRITE, REFACTOR]"
        target_layer: "string"
        related_files: "list[Path]"
    step_2:
      actor: CE
      action: "build: 从VMS拉取相关KE + 规则 + 蓝图"
      input: "session_context_request"
      output: "raw_context { ke_list[], rules[], blueprints[] }"
    step_3:
      actor: CE
      action: "compress: Token预算内压缩 → priority排序"
      input: "raw_context + token_budget"
      output: "compressed_context"
    step_4:
      actor: CE
      action: "validate: 通过LSG安全校验"
      input: "compressed_context"
      output: "validated_context or REJECTED"
    step_5:
      actor: CE
      action: "inject: 返回最终上下文给Orc"
      output: "injection_result { context_str, token_count, sources[] }"

token_budget:
  total_per_session: 8000
  breakdown:
    ke_entries: "0-3000 (动态)"
    rules_policies: "0-2000"
    blueprints: "0-2000"
    runtime_logs: "0-1000"

error_handling:
  VMS_unavailable: "CE → 降级为仅注入AGENTS.md + 当前模块蓝图 → 标记 session.degraded=true"
  LSG_reject: "CE → 移除被拒绝块 → 重新compress → 再送LSG → 3次仍失败 → 注入失败标记"
  timeout: "CE 10s 超时 → 降级注入 → 记录CE_timeout metric"

ai_prompt: >
  你是CT-ORC-CE-001的AI agent。当Orc请求为任务构建上下文时：
  (1) build阶段从VMS拉取KE+规则+蓝图——如果VMS不可用，降级为仅注入AGENTS.md+硬编码规则，不要抛异常；
  (2) compress阶段必须在8000 token预算内完成，优先级：KE > 规则 > 蓝图 > 日志；
  (3) compress后必须保留raw_text——LSG需要它做注入检测（AP4）；
  (4) validate阶段必须通过LSG——LSG不可用时fail-closed（AP5），不要尝试跳过；
  (5) 10s超时立即降级，不要阻塞Orc的任务启动；
  (6) 返回的injection_result必须包含source_files字段——明确告诉Orc"上下文来自哪里"。

telemetry:
  metrics:
    - {name: "ce_context_build_duration_ms", type: histogram, buckets: [100,500,1000,5000,10000]}
    - {name: "ce_context_token_count", type: gauge}
    - {name: "ce_context_build_errors", type: counter, labels: [error_type]}
    - {name: "ce_degradation_rate", type: rate}
  traces:
    required_spans: ["ce_build", "ce_vector_search", "ce_compress", "ce_lsg_validate", "ce_inject"]
```
