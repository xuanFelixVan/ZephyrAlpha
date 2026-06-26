---
module_id: KE-2361
status: active
title: 6.10 知识图谱实体化
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 6.10 知识图谱实体化

6.10 知识图谱实体化

```yaml
knowledge_graph_integration:
  description: "将漂移事件、检测器、模块、根因作为知识图谱实体——支持图谱查询和推理"

  entities:
    - type: "DriftEvent"
      relations:
        - "DETECTED_BY → Detector"
        - "AFFECTS → Module"
        - "INTRODUCED_BY → Commit"
        - "CORRELATED_WITH → DriftEvent"
        - "RESOLVED_BY → Session/AI"

    - type: "Detector"
      relations:
        - "COVERS → DriftDimension"
        - "PRODUCES → DriftEvent"

    - type: "Module"
      relations:
        - "DEPENDS_ON → Module"
        - "HAS_BUDGET → DriftBudget"
        - "AFFECTED_BY → DriftEvent"

  queries:
    - "哪些检测器从未产生过漂移？（可能太宽松）"
    - "哪些模块的漂移总是成对出现？（因果关系）"
    - "最近的漂移热点区域在哪？（最多漂移的子图）"

  implementation: "通过 mcp_Knowledge_Graph_Memory MCP server 读写"
```
