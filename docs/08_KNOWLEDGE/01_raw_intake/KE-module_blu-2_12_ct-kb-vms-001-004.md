---
module_id: KE-module_blu-2_12_ct-kb-vms-001-004
title: 2.12 CT-KB-VMS-001：知识库 → 向量记忆 — 知识条目向量化存储
category: module_blueprint
---

# 2.12 CT-KB-VMS-001：知识库 → 向量记忆 — 知识条目向量化存储

2.12 CT-KB-VMS-001：知识库 → 向量记忆 — 知识条目向量化存储

```yaml
contract: CT-KB-VMS-001
title: "结构化知识→非结构化向量记忆的双向映射"
systems:
  - role: producer
    name: knowledge_base
    path: "src/zephyr/knowledge_base/"
    blueprint: "MOD-KB-001"
  - role: consumer
    name: vector_memory_system
    path: "src/zephyr/vector_memory/"
    blueprint: "MOD-INF-011"

data_flow:
  direction: bidirectional

  kb_to_vms:
    trigger: "KE.status → ACTIVE 且 ke_type ∈ {ARCHITECTURE_RULE, CODE_CONVENTION, DECISION_RECORD}"
    payload:
      ke_id: "string"
      ke_title: "string"
      ke_content_plaintext: "string — 去Markdown格式化的纯文本"
      ke_type: "string"
      priority: "P0..P3"
      embedding_model: "text-embedding-3-large"
    action: "VMS生成embedding → 存储为 vector_entry → 返回 vector_id"

  vms_to_kb:
    trigger: "CE查询向量记忆 → 检索到KE相关向量"
    query: "{ vector_id, similarity_score, source_ke_id }"
    action: "KB根据 ke_id 返回KE完整内容 → CE注入上下文"

consistency_rule: >
  KE更新时 → KB通知VMS重新生成embedding（而非覆写旧向量）。
  旧向量标记为 superseded_by={new_vector_id}，保留用于审计追溯。

ai_prompt: >
  你是CT-KB-VMS-001的AI agent。当KB需要将KE向量化存储到VMS时：
  (1) 仅当KE.status=ACTIVE且ke_type∈{ARCHITECTURE_RULE,CODE_CONVENTION,DECISION_RECORD}时触发向量化；
  (2) embedding使用text-embedding-3-large——不要用BGE-M3（那是VMS查询用的）；
  (3) KE更新时生成新embedding + 旧向量标记superseded_by——不要覆写旧向量（DD6）；
  (4) KE被DEPRECATED/ARCHIVED时，VMS中对应向量标记deprecated=true但保留——用于审计追溯；
  (5) VMS→KB方向：CE查询到向量后，KB根据ke_id返回完整KE内容——不要只返回vector_id。

telemetry:
  metrics:
    - {name: "kb_vms_embed_count", type: counter, labels: [ke_type]}
    - {name: "kb_vms_embed_latency_ms", type: histogram, buckets: [50,100,500,1000,5000]}
    - {name: "kb_vms_superseded_count", type: counter}
    - {name: "kb_vms_consistency_check_pass", type: gauge}
  traces:
    required_spans: ["kb_ke_activate", "vms_generate_embedding", "vms_store_vector"]
```
