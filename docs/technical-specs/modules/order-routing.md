# 订单路由系统

> 量化订单路由架构
>
> **配套文档**：
> - 主文档：[SPEC.md](../SPEC.md)
> - 低延迟架构：[architecture/low-latency.md](./architecture/low-latency.md)

***

## 1. 订单路由架构

| 组件 | 功能 | 技术要点 |
|------|------|----------|
| 订单管理器 | 订单创建/修改/撤销 | 订单状态跟踪 |
| 路由引擎 | 订单分发到交易所 | 智能路由选择 |
| 柜台接口 | 连接券商柜台系统 | 统一API |
| 交易所接口 | 连接交易所系统 | 高速通道 |

***

## 2. 订单路由Python实现

```python
class OrderRouter:
    """订单路由系统"""

    def __init__(self):
        self.exchanges = {
            'SSE': ExchangeConnection('SSE', 'tcp://sse.example.com:8001'),
            'SZSE': ExchangeConnection('SZSE', 'tcp://szse.example.com:8002')
        }
        self.brokers = {
            'ZT': BrokerConnection('ZT', 'tcp://zt.example.com:9001')
        }
        self.order_cache = {}

    def route_order(self, order: dict) -> dict:
        """路由订单到交易所"""
        exchange = self.get_exchange(order['exchange'])
        if not exchange:
            return {'status': 'failed', 'reason': 'invalid_exchange'}

        routed_order = {
            'order_id': self.generate_order_id(),
            'exchange': order['exchange'],
            'code': order['code'],
            'side': order['side'],
            'price': order['price'],
            'volume': order['volume'],
            'type': order.get('type', 'LIMIT')
        }

        self.order_cache[routed_order['order_id']] = routed_order

        return {'status': 'routed', 'order': routed_order}

    def cancel_order(self, order_id: str) -> dict:
        """撤销订单"""
        if order_id not in self.order_cache:
            return {'status': 'failed', 'reason': 'order_not_found'}

        order = self.order_cache[order_id]
        exchange = self.get_exchange(order['exchange'])

        success = exchange.send_cancel(order_id)

        if success:
            order['status'] = 'cancelled'
            return {'status': 'success', 'order_id': order_id}

        return {'status': 'failed', 'reason': 'cancel_failed'}

    def query_order_status(self, order_id: str) -> dict:
        """查询订单状态"""
        if order_id not in self.order_cache:
            return {'status': 'unknown'}

        order = self.order_cache[order_id]
        exchange = self.get_exchange(order['exchange'])

        status = exchange.query_order(order_id)

        order['status'] = status
        return {'status': 'success', 'order': order}

    def generate_order_id(self) -> str:
        """生成订单ID"""
        import uuid
        return f"ORD-{uuid.uuid4().hex[:12].upper()}"
```

***

## 3. 订单状态机

| 状态 | 说明 | 转换条件 |
|------|------|----------|
| PENDING | 等待提交 | 订单创建 |
| SUBMITTED | 已提交 | 发送到交易所 |
| PARTIAL | 部分成交 | 部分成交 |
| FILLED | 全部成交 | 成交完成 |
| CANCELLED | 已撤销 | 用户撤单 |
| REJECTED | 已拒绝 | 交易所拒绝 |

***

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-27 | 新增订单路由系统文档 |
