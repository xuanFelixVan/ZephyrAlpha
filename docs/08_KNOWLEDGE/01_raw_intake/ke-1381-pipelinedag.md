---
module_id: KE-1292
status: active
title: 1. PipelineDAG 数据模型
category: module_blueprint
---

# 1. PipelineDAG 数据模型

1. PipelineDAG 数据模型

```python
class PipelineDAG(BaseModel):
    nodes: list[str]              # ["M1","M2",...,"M11"]
    edges: list[tuple[str,str]]   # [("M1","M2"), ("M2","M3"), ...]

    def topological_sort(self) -> list[str]:
        """Kahn's BFS algorithm"""
    def detect_cycle(self) -> bool:
        """DFS cycle detection"""
    def resolve_execution_order(self) -> list[list[str]]:
        """返回拓扑层次——同层可并行"""
```
