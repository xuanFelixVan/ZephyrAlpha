---
task_id: "TASK-KB-0023"
source_blueprint: "MOD-KB-001"
source_section: "§8 容量预估(KE阶段:增长/流量/延迟/5场景)"

title: "KB 容量预估监控实现——增长曲线监控 + 5场景延迟预算 + 存储阈值报警"
description: |
  实现蓝图 §8 定义的容量预估体系：(1)KE阶段容量预估——experimental当前~32 KE + beta末~500 KE(54 MB) + beta末~2000 KE(452 MB) + stable+~10000 KE(1.46 GB)，年增长率控制≤10%（参见 §8.1 数量表+§8.2 存储表）；(2)流量预估——16x context_assembler的AI-Pipeline session/d + 8x Tool Valet Tools→~2400次召回/d s0.5-0.5s→1.1 MB Tokens/d；(3)五场景延迟预算——纯向量语义召回(no cache)<100ms、检索无缓存全链路<500ms、带重排全链路<1000ms、门禁全链路含LLM抽取<2500ms、哈希碰撞概率<1%;(4)chroma存储上限2GB→接近75%自动报警+自动compact；(5)实现 capacity_monitor.py 周期性扫描+更新容量曲线+email预警。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\chromadb_init.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\capacity_monitor.py"
    description: "新建——check_chroma_size() + check_sqlite_size() + estimate_daily_growth() + alert_over_threshold()"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\capacity_monitor.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ingest.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\triage.py"
  - "D:\\ZephyrAlpha\\data\\chroma\\**"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "CapacityStatus MetricRecord Pydantic V2"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§8 完整容量预估——包含 KE阶段增长/日流量/五场景延迟预算/存储阈值"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 6000
timeout_minutes: 25

acceptance_criteria:
  - "capacity_monitor.py check_chroma_size()→返回 (path, size_bytes, percent_of_2GB)"
  - "capacity_monitor.py check_sqlite_size()→返回 (path, size_bytes, table_counts)"
  - "ChromaDB 2GB阈值←>75%(1.5GB)→WARNING + >90%(1.8GB)→CRITICAL + >95%(1.85GB)→立即推Owner"
  - "SQLite 增长>100MB/月→WARNING"
  - "年增长<10%曲线在每日扫描时更新——偏差>5%→ALERT"

rollback_instructions: |
  1. 删除 src/zephyr/kb/capacity_monitor.py

depends_on: ["TASK-KB-0021"]
blocked_by: []
status: "created"
tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-KB-001"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
