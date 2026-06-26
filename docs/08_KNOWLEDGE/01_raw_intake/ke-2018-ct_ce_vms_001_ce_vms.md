---
module_id: KE-1927---vms-003
status: active
title: 2.6 CT-CE-VMS-001：CE ↔ VMS
category: module_blueprint
ttl: permanent
---

# 2.6 CT-CE-VMS-001：CE ↔ VMS

2.6 CT-CE-VMS-001：CE ↔ VMS

```yaml
contract: CT-CE-VMS-001
title: "上下文构建 → 向量检索"
systems:
  - role: consumer
    name: context-engine
    path: "src/zephyr/context-engine/"
    blueprint: "MOD-CONTEXT_ENGINE"
  - role: provider
    name: vector-memory
    path: "src/zephyr/vector-memory/"
    blueprint: "MOD-INF-011"

interaction:
  query:
    method: "VMS.search(collection, query_embedding, top_k, filter)"
    collections:
      - name: "ke_entries"
        query: "task_type + target_layer → 语义相似KE"
        top_k: 5
      - name: "vibe_rules"
        query: "task_type → 相关治理规则"
        top_k: 3
      - name: "blueprints"
        query: "target_layer + related_files → 相关蓝图"
        top_k: 2
      - name: "failure_patterns"
        query: "task_type → 历史失败模式"
        top_k: 3

embedding:
  model: "BGE-M3 (ONNX本地推理)"
  dimension: 1024
  batch_size: 16

error_handling:
  VMS_unavailable: "CE降级——不注入向量检索结果 → AGENTS.md + 硬编码规则"
  embedding_failure: "CE跳过该collection → 记录 warning"

ai_prompt: >
  你是CT-CE-VMS-001的AI agent。当CE需要从VMS检索知识向量时：
  (1) 查询4个collection：ke_entries(top_k=5)、vibe_rules(top_k=3)、blueprints(top_k=2)、failure_patterns(top_k=3)；
  (2) query_embedding使用BGE-M3 1024d——不要混用其他模型；
  (3) VMS不可用时降级为仅注入AGENTS.md+硬编码规则——不要阻塞CE的build流程；
  (4) embedding_failure时跳过该collection但继续其他collection的检索——部分结果优于零结果；
  (5) 返回结果必须附带similarity_score——CE compress阶段用于优先级排序。

telemetry:
  metrics:
    - {name: "vms_search_latency_ms", type: histogram, buckets: [10,50,100,500,1000]}
    - {name: "vms_search_result_count", type: gauge, labels: [collection]}
    - {name: "vms_availability", type: rate}
  traces:
    required_spans: ["vms_search_ke", "vms_search_rules", "vms_search_blueprints", "vms_search_failures"]
```
