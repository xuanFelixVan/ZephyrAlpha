---
module_id: KE-module_blu-6_3_cold_start-000
title: 6.3 Cold Start——历史操作回溯
category: module_blueprint
---

# 6.3 Cold Start——历史操作回溯

6.3 Cold Start——历史操作回溯

> **决策 D-020-13**（新增）：审计系统首次启动时（Cold Start），扫描现有 git log + session-logs/ 目录，生成历史审计基线 `bootstrap_audit_baseline.jsonl`。基线条目标记 `entry_type=cold_start_bootstrap` + `confidence_level=low`（历史数据不可完全验证）。

```python
class ColdStartBootstrapper:
    def scan_git_log(self, since: datetime | None = None) -> int:
        """扫描 git log → 生成历史审计基线条目"""

    def scan_session_logs(self) -> int:
        """扫描 session-logs/ 目录 → 标准化为审计条目"""

    def merge_to_baseline(self) -> Path:
        """合并 → 写入 bootstrap_audit_baseline.jsonl → 返回路径"""
```
