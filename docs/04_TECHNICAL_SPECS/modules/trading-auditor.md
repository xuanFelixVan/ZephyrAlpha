# 交易日志审计

> 合规审计体系
>
> **配套文档**：
> - 主文档：[SPEC.md](../SPEC.md)
> - 容灾备份：[architecture/disaster-recovery.md](./architecture/disaster-recovery.md)

***

## 1. 审计日志内容

| 日志类型 | 记录内容 | 保留周期 |
|----------|----------|----------|
| 订单日志 | 订单创建/修改/撤销/成交 | 5年 |
| 成交日志 | 成交确认/回报 | 5年 |
| 持仓日志 | 持仓变化/成本记录 | 5年 |
| 资金日志 | 资金变化/冻结/释放 | 5年 |
| 风控日志 | 风控触发/处理记录 | 3年 |

***

## 2. Python审计实现

```python
class TradingAuditor:
    """交易审计系统"""

    def __init__(self):
        self.db = AuditDatabase()
        self.log_path = '/data/audit'

    def log_order(self, order: dict, action: str):
        """记录订单日志"""
        audit_record = {
            'timestamp': datetime.now().isoformat(),
            'type': 'ORDER',
            'action': action,
            'order_id': order.get('order_id'),
            'code': order.get('code'),
            'side': order.get('side'),
            'volume': order.get('volume'),
            'price': order.get('price'),
            'user': order.get('user', 'SYSTEM')
        }

        self.db.insert(audit_record)
        self.write_to_file(audit_record)

    def log_trade(self, trade: dict):
        """记录成交日志"""
        audit_record = {
            'timestamp': datetime.now().isoformat(),
            'type': 'TRADE',
            'trade_id': trade.get('trade_id'),
            'order_id': trade.get('order_id'),
            'code': trade.get('code'),
            'side': trade.get('side'),
            'volume': trade.get('volume'),
            'price': trade.get('price'),
            'commission': trade.get('commission')
        }

        self.db.insert(audit_record)
        self.write_to_file(audit_record)

    def log_position(self, position: dict, change: dict):
        """记录持仓日志"""
        audit_record = {
            'timestamp': datetime.now().isoformat(),
            'type': 'POSITION',
            'code': position.get('code'),
            'volume_before': change.get('volume_before'),
            'volume_after': change.get('volume_after'),
            'cost_before': change.get('cost_before'),
            'cost_after': change.get('cost_after')
        }

        self.db.insert(audit_record)
        self.write_to_file(audit_record)

    def log_risk_event(self, event: dict):
        """记录风控事件"""
        audit_record = {
            'timestamp': datetime.now().isoformat(),
            'type': 'RISK',
            'event_type': event.get('type'),
            'description': event.get('description'),
            'action': event.get('action'),
            'result': event.get('result')
        }

        self.db.insert(audit_record)
        self.write_to_file(audit_record)

    def write_to_file(self, record: dict):
        """写入日志文件"""
        import json
        from datetime import datetime

        date = datetime.now().strftime('%Y%m%d')
        log_file = f"{self.log_path}/audit_{date}.jsonl"

        with open(log_file, 'a') as f:
            f.write(json.dumps(record) + '\n')

    def query_audit(self, start_time: str, end_time: str, audit_type: str = None) -> list:
        """查询审计记录"""
        return self.db.query(start_time, end_time, audit_type)

    def generate_report(self, start_date: str, end_date: str) -> dict:
        """生成审计报告"""
        records = self.query_audit(start_date, end_date)

        return {
            'total_orders': len([r for r in records if r['type'] == 'ORDER']),
            'total_trades': len([r for r in records if r['type'] == 'TRADE']),
            'total_positions': len([r for r in records if r['type'] == 'POSITION']),
            'risk_events': len([r for r in records if r['type'] == 'RISK']),
            'period': f"{start_date} to {end_date}"
        }
```

***

## 3. 审计合规要求

| 要求 | 说明 | 实现 |
|------|------|------|
| 完整性 | 日志不被篡改 | 哈希校验 |
| 可追溯性 | 每笔交易可追踪 | 全链路ID |
| 时效性 | 日志实时记录 | 异步写入 |
| 保密性 | 敏感信息脱敏 | 权限控制 |

***

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-27 | 新增交易日志审计文档 |
