---
module_id: KE-1956-----cot-------d-020-15-000
status: active
title: 2.9 LLM 推理链（CoT）审计（决策 D-020-15）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.9 LLM 推理链（CoT）审计（决策 D-020-15）

2.9 LLM 推理链（CoT）审计（决策 D-020-15）

> **决策 D-020-15**（新增）：对标 OWASP ASI-10 "完整可观测性" + FCA 监管文件审查 "推理"维度。每条审计条目记录 LLM 推理链摘要（`reasoning_trace` <500 chars）+ 完整 CoT 的 SHA-256 引用（`cot_hash`）。完整 CoT 文本存储在 `reasoning/` 目录（独立于审计日志，按 session 组织）。Phase scaffold 记录摘要，Phase experimental 起记录完整 CoT。

```yaml
cot_audit:
  summary_level:
    field: "reasoning_trace"
    max_length: 500  # chars
    format: "Markdown 摘要——关键推理步骤 + 最终决策"

  full_trace:
    field: "cot_hash"
    storage_path: "data/reasoning/{session_id}/{entry_id}.cot.json"
    format: "JSON —— [{'step': 1, 'thought': '...', 'action': '...', 'observation': '...'}, ...]"
    retention: "随审计日志分层存储——hot 7d / warm 90d / cold archive"

  retrieval:
    description: "通过 cot_hash 查找完整 CoT —— SHA-256(完整 CoT 文件) == cot_hash → 可信"
    query: "AuditQuery.by_task(task_id) → 获取 cot_hash → reasoning_store.fetch(cot_hash)"
```
