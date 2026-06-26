---
module_id: KE-2044
status: active
title: 3.1 Slot 概念（上下文槽位）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 3.1 Slot 概念（上下文槽位）

3.1 Slot 概念（上下文槽位）

`ContextBundle` 不是一个扁平 prompt 串，而是**按语义分槽**的结构化容器。MCP 注入时按通道能力分发到不同槽位。

| Slot | 含义 | 典型内容来源 | 默认 token 预算占比 |
|------|------|-------------|---------------------|
| `task_spec` | 任务本身规格 | task card yaml 渲染 | 10% |
| `architecture` | 架构决策 / ADR / 接口契约 | VMS `decisions` collection | 25% |
| `code_refs` | 相关代码片段 / blueprints | VMS `code_context` + 文件系统兜底 | 30% |
| `task_history` | 历史相似任务执行记录 | VMS `task_history` | 15% |
| `lessons` | 经验教训 / 反模式 | VMS `lessons` | 10% |
| `runtime_state` | 运行时上下文（分支名、失败的 CI、最近 commit） | git + 运行时状态 | 5% |
| `guardrails` | 规则与约束 | `.cursor/rules/*` + `AGENTS.md` 片段 | 5% |

预算占比可被 `FeedbackSignal` 动态调整（例如 `lessons` 长期低命中 → 降至 5%，腾给 `code_refs`）。
