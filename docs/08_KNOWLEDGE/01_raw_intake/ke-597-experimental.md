---
module_id: KE-537
status: active
title: 8A.2 健康检查合约（所有服务必须实现）
category: documentation
ttl: permanent
---

# 8A.2 健康检查合约（所有服务必须实现）

8A.2 健康检查合约（所有服务必须实现）

每个服务必须暴露标准化 health check 接口（详见各自 interface 规范 §8）：

```python
class ServiceHealthProtocol(Protocol):
    def health(self) -> dict:
        return {
            "status": "healthy" | "degraded" | "unhealthy",
            "version": "x.y.z",
            "uptime_seconds": int,
            "last_error": str | None,
            "dependencies": {...},  # 上游服务状态
        }
```

**巡检频率**：experimental 由 FLE 每 60 秒轮询一次，异常立即进入 detect_anomaly 流程。
