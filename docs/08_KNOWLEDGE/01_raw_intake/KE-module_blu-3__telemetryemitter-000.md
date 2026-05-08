---
module_id: KE-module_blu-3__telemetryemitter-000
title: 3. TelemetryEmitter
category: module_blueprint
---

# 3. TelemetryEmitter

3. TelemetryEmitter

```python
class TelemetryEmitter:
    metrics: MetricsRegistry
    tracer: TracerProvider
    
    def record_dispatch(self, result: PipelineResult):
        """记录一次dispatch的所有metrics+traces"""
    def record_module_execution(self, module_result: ModuleResult):
        """记录单个模块执行"""
    def emit_pipeline_complete(self, result: PipelineResult):
        """CT-PIPE-ORC-001：PIPELINE_COMPLETE事件→EventBus"""
```
