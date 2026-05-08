---
module_id: KE-module_blu-5_5___________d-020-21-000
title: 5.5 间接操作检测（决策 D-020-21）
category: module_blueprint
---

# 5.5 间接操作检测（决策 D-020-21）

5.5 间接操作检测（决策 D-020-21）

> **决策 D-020-21**（新增）：Agent 可能不直接修改目标文件，而是通过 symlink、hardlink、生成脚本、cron job、MCP 委托等方式间接操作。检测方法：(a) Agent 写入的任何内容扫描潜在执行路径（脚本/shebang/shell），(b) 写入文件后短时间内被执行→关联审计，(c) MCP 操作记录携带 `indirect_operation=True`。

```python
class IndirectOperationDetector:
    """间接操作检测器——对标 ANM-011"""

    def scan_generated_scripts(self, entry: AuditEntryV1) -> bool:
        """检测 Agent 是否生成了可执行脚本——潜在间接操作"""

    def correlate_write_execute(self, write_entry: AuditEntryV1, exec_entry: AuditEntryV1) -> float:
        """关联写入→执行——返回关联度 0.0~1.0"""

    def trace_indirect_path(self, entry: AuditEntryV1) -> list[str]:
        """追踪间接操作路径——symlink→target, script→cron→target"""
```
