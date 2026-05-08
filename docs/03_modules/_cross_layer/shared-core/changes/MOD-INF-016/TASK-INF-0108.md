---
task_id: "TASK-INF-0108"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §4 Phase 16 + §13 盲点 B41-B42"

title: "Phase 16 施工——AI 溯源可控：AIBOM物料清单(B41) + Memory Bank跨会话持久记忆(B42)"
description: |
  实现 AI 产物的可追溯性与跨会话记忆持久化。
  B41：AIBOM——AI 物料清单与代码溯源。当前无 AI 生成物料的 provenance 追踪。
  需实现：AIBOMGenerator——自动捕获 AI 生成物的 model_id/prompt_hash/timestamp/tool_calls lineage。
  对标 Cisco AIBOM v0.5.2 / Trusera ai-bom v3.6.0 / SPDX 3.0 AI 扩展。
  B42：Memory Bank——Agent 跨会话持久记忆。Claude Code auto-memory 模式：AI 在会话结束时自动
  将关键发现写入 memory bank，下次 session 冷启动时自动加载。
  需实现：MemoryBank——write_memory() / query_memory() / decay_score() + Mem0/Memori 风格嵌入索引。
  对标 Claude Code auto-memory / Mem0 / Memori。
  专业对标：Cisco AIBOM v0.5.2 / Trusera ai-bom v3.6.0 / SPDX 3.0 AI Profile / Claude Code auto-memory / Mem0 / Memori。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\content_fingerprint.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\aibom.py"
    description: "AIBOMGenerator——捕获 model_id/prompt_hash/timestamp/tool_calls lineage"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\memory_bank.py"
    description: "MemoryBank——write/query/decay + 嵌入索引"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_aibom.py"
    description: "单元测试——验证 AIBOM 生成、SPDX 格式兼容"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_memory_bank.py"
    description: "单元测试——验证 write/query/decay"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\aibom.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\memory_bank.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\__init__.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_aibom.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_memory_bank.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\SHARED-QUICKREF.yml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\content_fingerprint.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "GOV-DOC-002"
    section: "§5.5"
    reason: "shared/ 准入规则——被 ≥2 个 L01 模块消费"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    reason: "本蓝图 §4/§13——Phase 16 + B41-B42 盲点详情"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\content_fingerprint.py"
    reason: "content_fingerprint.py——AIBOM 需基于内容指纹做 provenance"

assigned_model: "claude-sonnet-4.6"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 20000
timeout_minutes: 50

acceptance_criteria:
  - "aibom.py: AIBOMEntry 模型——model_id / prompt_hash / timestamp / tool_calls[] / output_hash"
  - "aibom.py: AIBOMGenerator.record()——每次 AI 操作后自动写入 provenance"
  - "aibom.py: export_spdx()——输出 SPDX 3.0 JSON 格式"
  - "memory_bank.py: MemoryEntry 模型——session_id / key_finding / confidence / decay_score / timestamp"
  - "memory_bank.py: MemoryBank.write_memory(entry)——追加到持久化存储"
  - "memory_bank.py: MemoryBank.query_memory(query, top_k=5)——语义检索相关记忆"
  - "memory_bank.py: decay_score 随时间衰减——30 天无引用 decay→0"
  - "pytest tests/unit/test_aibom.py -v 全部通过"
  - "pytest tests/unit/test_memory_bank.py -v 全部通过"
  - "SHARED-QUICKREF.yml 更新——新增 aibom + memory_bank 入口"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\shared\aibom.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\shared\memory_bank.py
  3. 删除 D:\ZephyrAlpha\tests\unit\test_aibom.py
  4. 删除 D:\ZephyrAlpha\tests\unit\test_memory_bank.py
  5. 还原 __init__.py 对应导出
  6. 还原 SHARED-QUICKREF.yml 对应条目

depends_on: ["TASK-INF-0104"]
blocked_by: []

status: "created"

tags_fn:
  - "infra"
tags_ly: "cross_layer"
tags_md: "claude-sonnet-4.6"
tags_st: "active"
tags_mo:
  - "MOD-INF-016"

completed_gates: []
blocked_gates: {}

artifact_paths: []

audit_findings: []

ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
