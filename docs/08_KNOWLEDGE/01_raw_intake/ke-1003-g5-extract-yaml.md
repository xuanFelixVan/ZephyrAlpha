---
module_id: KE-925---------g5-extract-yaml-000
title: 4.5.2 检查项（对应 `g5-extract.yaml`）
category: governance
---

# 4.5.2 检查项（对应 `g5-extract.yaml`）

4.5.2 检查项（对应 `g5-extract.yaml`）

| ID | 检查名 | 级别 | 说明 | on_failure |
|----|-------|:---:|------|-----------|
| G5-C01 | `extraction_template_ready` | **P0** | `doc_type ∈ EXTRACTION_TEMPLATES`（blueprint / strategy / factor / best_practice / lesson_learned）| `reject` |
| G5-C02 | `target_path_available` | **P0** | 路径不存在 **或** `overwrite_approved=true` | `flag`（等待批准）|
| G5-C03 | `target_path_compliant` | **P0** | 符合 `docs/08_knowledge/{category}/ke-{NNN}-{name}.md`（Stage G 后小写） | `reject` |
| G5-C04 | `ke_number_assigned` | **P0** | KE 编号 > `current_max_KE` 且唯一 | `auto_assign`（递增）|
| G5-C05 | `source_document_complete` | **P0** | 源文档 `gate_status ∈ {'passed_g4', 'active'}` | `reject` |
| G5-C06 | `extraction_scope_defined` | P1 | `extraction_scope` 非空 | `auto_scope`（全文）|
