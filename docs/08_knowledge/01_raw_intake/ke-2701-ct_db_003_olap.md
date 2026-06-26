---
module_id: KE-2604
status: active
title: CT-DB-003：OLAP 查询契约
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# CT-DB-003：OLAP 查询契约

CT-DB-003：OLAP 查询契约

```yaml
contract_id: CT-DB-003
provider: MOD-DATABASE (OLAPEngine)
consumers:
  - MOD-FEEDBACK_LOOP (feedback-loop)
  - MOD-INF-015 (system-telemetry)

operations:
  task_progress_trend:
    input: "period: day|week|month, limit: 1-10000, phase?: int"
    output: "list[TrendRow]"
    sql_injection_protection: "参数化查询 + period白名单 + limit范围校验"

  compliance_rate_trend:
    input: "period, limit, gate_id?: str"
    output: "list[TrendRow]"

  knowledge_activation_trend:
    input: "period, limit, category?: str"
    output: "list[TrendRow]"

  archive_events:
    input: "days: int (默认30), archive_dir?: Path"
    output: "{archived_count, archive_files, deleted_count}"
    guarantee: "DuckDB 读取 → Parquet 写入 → SQLite DELETE 三步"

  query_unified_events:
    input: "limit: int"
    output: "list[TrendRow]"
    semantics: "UNION ALL (SQLite热数据 + Parquet冷数据)"
```
