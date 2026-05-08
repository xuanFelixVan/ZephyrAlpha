---
module_id: KE-module_blu-3_11_kb_knowledge_base_rule-007
title: 3.11 KB（Knowledge Base Rule）存储格式
category: module_blueprint
---

# 3.11 KB（Knowledge Base Rule）存储格式

3.11 KB（Knowledge Base Rule）存储格式

**定位**：KB 是"系统级规则"——从多条 KE 聚合提炼出的硬约束/自动化检查项。对标 ITIL DIKW 的 Knowledge→Wisdom 层：KB = 可执行的 Wisdom（不是"建议"，是"规则"）。

**KB 与 KE 的核心差异**：

| 维度 | KB | KE |
|------|:---:|:---:|
| 消费者 | pre-commit hooks / CI 门禁 / APScheduler cron | AI context assembler / `recall()` |
| 格式 | YAML rule 定义（可机器执行） | Markdown 知识卡片（可人类阅读） |
| 来源 | 多条 KE 聚合 + MINOR 自动合并 | 单条知识提取 |
| 状态 | ACTIVE / SUPERSEDED / RETIRED（3 状态） | 10 状态机 |
| 向量化 | ❌ 不入 ChromaDB（规则精确匹配，不需语义检索） | ✅ |
| 文件命名 | `KB-{NNN}-{rule_name}.yaml` | `KE-{NNN}-{slug}.md` |

**KB 3 状态机**：

```
ACTIVE → SUPERSEDED（被新版规则取代）
  │
  └──→ RETIRED（规则不再适用）
```

**KB 文件模板**（`docs/08_knowledge/kb/KB-001-python-linter-must-be-ruff.yaml`）：

```yaml
---
kb_id: "KB-001"
title: "Python Linter 必须是 ruff"

category: "tool_configuration"
domain: "infra"
layer: "L01"

status: "ACTIVE"
priority: "P0"

derived_from:
  - "KE-041"     # pre-commit hooks 选型
  - "KE-042"     # ruff 选 pylint
  - "ADR-0020"   # 编码工具链标准化

rule:
  check: "file_exists"
  path: "pyproject.toml"
  required_section: "tool.ruff.lint"
  on_violation: "BLOCK"           # BLOCK / WARN / AUTO_FIX

merged_at: "2026-05-03T10:00:00+08:00"
created_at: "2026-05-02T14:30:00+08:00"
updated_at: "2026-05-03T10:00:00+08:00"

supersedes: []
superseded_by: []
---
```

**KB 的自动聚合策略（MINOR 自动合并）**：

| 条件 | 操作 | 触发 |
|------|------|------|
| 2+ 条 ACTIVE KB 字段完全相同（仅 derived_from 不同） | MINOR 自动合并 derived_from 列表，保留一条 | CI weekly cron |
| 2+ 条 ACTIVE KB 规则有交叉但不完全相同 | 推送 Owner："2 条规则有冲突，建议合并？" | L3 哨兵 |
| 1 条 ACTIVE KB 90d 未被触发 | 自动 RETIRED（冷却机制） | APScheduler monthly cron |

> **对标**：K8s Admission Controller（KB = 准入规则——不符合规则的操作被硬件阻断）+ OPA/Rego（声明式策略语言——"期望状态"而非"执行步骤"，对应 §6.4 声明式优于命令式）
> **大白话**：KB 不是"建议"——是"规则"。KE-042 说"ruff 比 pylint 好"（知识），KB-001 说"pyproject.toml 里必须有 `[tool.ruff.lint]` 否则提交直接挡住"（规则）。KB 从多条 KE 自动聚合，同类型规则自动合并，90 天不用自动废弃——这样规则体系永远不会膨胀到没人管。

---
