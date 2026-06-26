---
module_id: KE-1914---------ide----------d-020-003
status: active
title: 2.5 逻辑时钟——多 IDE 时序一致性（决策 D-020-09）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.5 逻辑时钟——多 IDE 时序一致性（决策 D-020-09）

2.5 逻辑时钟——多 IDE 时序一致性（决策 D-020-09）

> **决策 D-020-09**（新增）：多 IDE 并发场景下，每个 IDE 维护独立 Lamport 逻辑时钟 `(ide_source: str, counter: int)`。写入 JSONL 时递增 counter；读取排序时以 `(max(local, received) + 1)` 规则合并。不对操作系统时钟做任何假设——`utc_timestamp` 仅用于人类阅读。

> **短术语**：`(trae, 42)` < `(cursor, 15)` 无法直接比较大小——Lamport 只保证因果顺序（happens-before），不保证全序。全序由 `(counter, ide_source)` 字典序打破——对标 Dynamo Vector Clock 简化版。

```python
class LamportClock:
    """单 IDE 逻辑时钟——Happens-Before 关系追踪"""
    def __init__(self, ide_source: str) -> None:
        self._ide = ide_source
        self._counter = 0

    def tick(self) -> tuple[str, int]:
        """操作前递增——返回当前时钟"""
        self._counter += 1
        return (self._ide, self._counter)

    def merge(self, received: tuple[str, int]) -> None:
        """接收外部事件时合并——Lamport merge 规则"""
        self._counter = max(self._counter, received[1]) + 1

    def now(self) -> tuple[str, int]:
        """返回当前时钟（不递增）"""
        return (self._ide, self._counter)

def audit_entry_sort_key(entry: AuditEntryV1) -> tuple[int, str]:
    """审计条目全序排序键：(counter, ide_source) 字典序"""
    return (entry.lamport_clock[1], entry.lamport_clock[0])
```
