---
module_id: KE-module_blu-2_13___ide____________d-020-19-000
title: 2.13 跨 IDE 一致性交叉验证（决策 D-020-19）
category: module_blueprint
---

# 2.13 跨 IDE 一致性交叉验证（决策 D-020-19）

2.13 跨 IDE 一致性交叉验证（决策 D-020-19）

> **决策 D-020-19**（新增）：对标 Goldman SecSync 不一致检测。多 IDE 并发场景下，两个 IDE 可能对同一操作记录了相互矛盾的信息（TRAE 记录"成功"，Cursor 记录"失败"）。新增 `CrossIDEConsistencyChecker`：定期扫描所有 IDE 的 JSONL，通过 `(task_id, action_type, file_path, lamport_clock 时间窗口)` 匹配同一操作，检测内容矛盾并标记。

```python
class CrossIDEConsistencyChecker:
    """跨 IDE 审计一致性验证器——对标 Goldman SecSync"""

    def find_conflicts(self, window: timedelta = timedelta(seconds=10)) -> list[ConsistencyConflict]:
        """扫描所有 IDE JSONL，检测同一操作的多版本矛盾"""

    def merge_consensus(self, task_id: str) -> ConsensusView:
        """合并多 IDE 对同一操作的视角——多数一致 → 可信"""

class ConsistencyConflict(BaseModel):
    entry_a_id: str
    entry_b_id: str
    field: str  # 冲突字段名
    value_a: str
    value_b: str
    ide_a: str
    ide_b: str
    severity: str  # low/high/critical
```
