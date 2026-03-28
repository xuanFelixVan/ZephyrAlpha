# 交易API与接口

> 交易API接口文档
>
> **配套文档**：
> - 主文档：[SPEC.md](../SPEC.md)
> - 订单路由：[modules/order-routing.md](./modules/order-routing.md)

***

## 1. 主流API对比

| API | 特点 | 适用场景 |
|-----|------|----------|
| 东方财富 | 免费/功能全 | 零售用户 |
| 同花顺 | 稳定性好 | 机构用户 |
| 掘金量化 | 策略回测 | 量化私募 |
| vn.py | 开源/Python | 开发者 |
| CTP | 期货/穿透式 | 期货量化 |

***

## 2. Python交易API封装

```python
class TradingAPI:
    """统一交易API接口"""

    def __init__(self, broker: str = 'ZT'):
        self.broker = broker
        self.api = self._init_api(broker)
        self.connected = False

    def _init_api(self, broker: str):
        """初始化API"""
        if broker == 'ZT':
            return ZTAPI()
        elif broker == 'THS':
            return THSAPI()
        elif broker == 'JM':
            return JMAPI()
        else:
            raise ValueError(f"Unknown broker: {broker}")

    def connect(self, account: dict) -> bool:
        """连接交易账户"""
        result = self.api.login(
            username=account['username'],
            password=account['password'],
            server=account['server']
        )
        self.connected = result['success']
        return self.connected

    def disconnect(self):
        """断开连接"""
        if self.connected:
            self.api.logout()
            self.connected = False

    def send_order(self, order: dict) -> dict:
        """发送订单"""
        if not self.connected:
            return {'success': False, 'reason': 'not_connected'}

        return self.api.send_order(order)

    def cancel_order(self, order_id: str) -> dict:
        """撤单"""
        return self.api.cancel_order(order_id)

    def get_positions(self) -> list:
        """获取持仓"""
        return self.api.query_positions()

    def get_account(self) -> dict:
        """获取账户信息"""
        return self.api.query_account()

    def get_orders(self, status: str = None) -> list:
        """查询订单"""
        return self.api.query_orders(status)
```

***

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-27 | 新增交易API文档 |
