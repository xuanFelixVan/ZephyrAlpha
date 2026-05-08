---
module_id: KE-module_blu-deliverysemantics-003
title: DeliverySemantics（消息传递语义）
category: module_blueprint
---

# DeliverySemantics（消息传递语义）

DeliverySemantics（消息传递语义）

```python
from enum import Enum

class DeliverySemantics(Enum):
    """RI-01 EventBus 的消息传递语义"""
    AT_MOST_ONCE = "at_most_once"    # 可能丢失，不重复——遥测日志等低价值事件
    AT_LEAST_ONCE = "at_least_once"  # 可能重复，不丢失——默认；配合IdempotencyGuard
    EXACTLY_ONCE = "exactly_once"    # 不丢不重——金融交易等关键事件，走ES expected_version

class EventPriority(Enum):
    """RI-01 EventBus 事件优先级——高优先级不排低优先级后面"""
    CRITICAL = 0   # 风控告警/熔断触发——立即消费
    HIGH = 1       # 交易执行/仓位变更——优先
    NORMAL = 2     # 模块状态变更/配置变更——正常
    LOW = 3        # Telemetry聚合/日志——积压时可丢弃
```
