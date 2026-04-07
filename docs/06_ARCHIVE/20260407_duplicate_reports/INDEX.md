---
module_id: 06_ARCHIVE_20260407_DUPLICATE_REPORTS_INDEX
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - 20260407_duplicate_reports目录索引
---

﻿# 重复报告归档索引

**归档时间**: 2026-04-07
**归档原因**: 版本隔离原则 - 保留最新版本，归档旧版本

---

## 归档文件清单

| 文件名 | 原路径 | 归档原因 | 保留版本位置 |
|--------|--------|----------|--------------|
| STRATEGY_EXECUTION_DEEP_AUDIT_REPORT_v4_20260407.md | 05_IMPLEMENTATION/07_OPERATIONS/audit_state/ | 旧版本审计报告 | LAYER5_DEEP_AUDIT_REPORT_v4_20260407.md |

---

## 版本对比

### STRATEGY_EXECUTION_DEEP_AUDIT_REPORT_v4 (旧版本)
- 审计时间: 2026-04-07 15:06:59
- 审计文档数: 114个
- 发现问题数: 179个
- 重复内容对: 17对

### LAYER5_DEEP_AUDIT_REPORT_v4 (新版本 - 保留)
- 审计时间: 2026-04-07 15:44:22
- 审计文档数: 115个
- 发现问题数: 175个
- 重复内容对: 3对

---

## 恢复方法

如需恢复归档文件，请使用以下命令：

```bash
git checkout HEAD~1 -- docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state/STRATEGY_EXECUTION_DEEP_AUDIT_REPORT_v4_20260407.md
```

或从归档目录复制：

```bash
cp docs/06_ARCHIVE/20260407_duplicate_reports/STRATEGY_EXECUTION_DEEP_AUDIT_REPORT_v4_20260407.md docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state/
```
