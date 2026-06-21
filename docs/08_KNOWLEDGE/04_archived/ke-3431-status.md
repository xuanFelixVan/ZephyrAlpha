---
module_id: KE-3303----status-000
title: 4.4 三域 status 对照表
category: documentation
---

# 4.4 三域 status 对照表

4.4 三域 status 对照表

| 维度 | DocStatus | TaskStatus | KeStatus |
|------|-----------|------------|----------|
| 域 | A（文档） | B（任务） | C（知识） |
| 值数量 | 3 | 10 | 10 |
| 大小写 | 枚举值小写 / 标识符大写 | 全大写 | 全大写 |
| 终态 | deprecated / superseded | VERIFIED / CANCELLED | ARCHIVED |
| 代码真源 | 本文件 §4.1 | `src/zephyr/shared/schemas.py` | kb_repo.py |
| 对标专业机构 | MLflow: status | IETF: task_status | OpenLineage: lifecycleState |
