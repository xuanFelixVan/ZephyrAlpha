---
module_id: KE-2416
status: active
title: 7. Stage 5：问题聚合与去重
category: module_blueprint
---

# 7. Stage 5：问题聚合与去重

7. Stage 5：问题聚合与去重

多个触发条件可能指向同一个根问题——聚合去重避免修复冲突：

```python
class IssueAggregator:
    def aggregate(self, triggers: TriggerResults, alignment: AlignmentReport) -> AggregatedIssues:
        """
        去重策略：
          - 同文件 + 同类型触发 → 合并为一个 issue
          - 孤儿文件已出现在对齐报告 → 优先对齐报告的分类
          - 系统超越(YELLOW)不与 RED 合并——YELLOW 单独上报
        """
        all_issues = triggers.disconnections + triggers.gaps + alignment.zombies + alignment.orphans
        merged = self._merge_by_file(all_issues)
        return AggregatedIssues(
            red_issues=merged.red,
            yellow_issues=merged.yellow,
            total_before_dedup=len(all_issues),
            total_after_dedup=len(merged),
            dedup_ratio=len(merged) / max(len(all_issues), 1)
        )
```

---
