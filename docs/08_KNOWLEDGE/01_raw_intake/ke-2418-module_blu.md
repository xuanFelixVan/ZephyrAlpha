---
module_id: KE-2323
status: active
title: 5.6 产出物命名规范
category: module_blueprint
---

# 5.6 产出物命名规范

5.6 产出物命名规范

run_all.py 和独立脚本的产出物按以下格式命名，保证任何人看到文件名即知内容：

| 阶段 | 文件名模式 | 示例 |
|------|-----------|------|
| C1 扫描原始输出 | `scan-{dimension}-{YYYYMMDD}.json` | `scan-d2-20260425.json` |
| C2 分类后 Finding | `findings-{dimension}-{YYYYMMDD}.jsonl` | `findings-d2-20260425.jsonl` |
| C3 单维度报告 | `RPT-AUDIT-{dimension}-{YYYYMMDD}.md` | `RPT-AUDIT-D2-20260425.md` |
| C3 全维度报告 | `RPT-AUDIT-FULL-{YYYYMMDD}.md` | `RPT-AUDIT-FULL-20260425.md` |
| C3 周度周期报告 | `RPT-AUDIT-PERIODIC-WEEKLY-{YYYYMMDD}.md` | `RPT-AUDIT-PERIODIC-WEEKLY-20260502.md` |
| C3 增量差异报告 | `RPT-AUDIT-DELTA-{YYYYMMDD}.md` | `RPT-AUDIT-DELTA-20260502.md` |
| C4 修复日志 | `remediation-log-{YYYYMMDD}.md` | `remediation-log-20260502.md` |
| C5 知识条目 | `KE-{NNN}-{topic}.md` | `KE-035-encoding-lesson.md` |

> **唯一定位公式**：`{文件类型前缀}-{维度|编号}-{日期}`（维度不适用时用编号）。AI 看文件名即知内容——无需读文件。

---
