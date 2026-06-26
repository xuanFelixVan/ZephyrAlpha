---
module_id: KE-4064
title: 3.4 脚本前缀约定（看名知义）
category: module_blueprint
ttl: permanent
---

# 3.4 脚本前缀约定（看名知义）

3.4 脚本前缀约定（看名知义）

| 前缀 | 含义 | 示例 |
|------|------|------|
| `validate_*` | 校验脚本——产出PASS/FAIL | `validate_frontmatter.py` |
| `detect_*` | 检测脚本——产出Finding列表 | `detect_ruins_references.py` |
| `audit_*` | 审计脚本——产出结构化报告 | `audit_knowledge_gaps.py` |
| `check_*` | 门禁脚本——直接return exit code | `check_architecture_gates.py` |
| `register_*` | 登记脚本——添加新条目到登记表 | `register_module.py` |

> **Vibe Coding AI公约**：前缀 = 代码自文档化。AI 看文件名就知道它是校验还是检测还是审计——无需读源码。
