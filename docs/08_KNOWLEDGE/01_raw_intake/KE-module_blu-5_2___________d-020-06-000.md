---
module_id: KE-module_blu-5_2___________d-020-06-000
title: 5.2 蓝图漂移检测（决策 D-020-06）
category: module_blueprint
---

# 5.2 蓝图漂移检测（决策 D-020-06）

5.2 蓝图漂移检测（决策 D-020-06）

> **决策 D-020-06**（新增）：每条 `FILE_DETAIL` 审计条目对比"蓝图规定的操作"与"AI 实际操作"。漂移来源：(a) AI 跳过了蓝图规定的检查项，(b) AI 执行了蓝图未授权的操作，(c) AI 修改了 immutable 文件。

```python
class DriftDetector:
    """蓝图 vs 实际操作漂移检测器"""

    def compare(self, entry: AuditEntryV1, blueprint_constraints: BlueprintConstraints) -> DriftResult:
        """单条目漂移检测"""

    def batch_compare(self, entries: list[AuditEntryV1]) -> DriftReport:
        """批量漂移检测——生成报告"""

class DriftResult(BaseModel):
    entry_id: str
    drift_detected: bool
    drift_type: str | None = None  # unauthorized_op / skipped_check / immutable_violation
    expected: str | None = None
    actual: str | None = None
    severity: str | None = None
    blueprint_ref: str | None = None
```
