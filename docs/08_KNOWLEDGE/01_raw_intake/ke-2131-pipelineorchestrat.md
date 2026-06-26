---
module_id: KE-2039-------pipelineorchestrat-000
status: active
title: 3.1.3 管线调度器（PipelineOrchestrator）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 3.1.3 管线调度器（PipelineOrchestrator）

3.1.3 管线调度器（PipelineOrchestrator）

```python
class PipelineOrchestrator:
    """调度 A区/B区/C区管线 + 模型分配"""

    def dispatch(self, task_id: str, pipeline: str = "auto") -> "DispatchResult":
        """按 GOV-AI-002 决策树分配管线+模型"""
        ...

    def execute_pipeline(self, dispatch_id: str, modules: list[str],
                         model: str) -> "PipelineExecutionResult":
        """串行执行 M 模块链"""
        ...
```
