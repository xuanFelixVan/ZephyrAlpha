---
module_id: KE-3010
status: active
title: W3C TraceContext
category: module_blueprint
ttl: permanent
---

# W3C TraceContext

W3C TraceContext

```python
class W3CTraceContext:
    """对齐 W3C Trace Context Level 2——跨模块/跨进程 trace_id 传播"""
    trace_id: str    # 32 hex chars
    span_id: str     # 16 hex chars
    trace_flags: int  # 01 = sampled

    def to_traceparent(self) -> str:
        """生成 traceparent header: 00-{trace_id}-{span_id}-{trace_flags:02x}"""
        return f"00-{self.trace_id}-{self.span_id}-{self.trace_flags:02x}"

    @classmethod
    def from_traceparent(cls, header: str) -> "W3CTraceContext": ...
```
