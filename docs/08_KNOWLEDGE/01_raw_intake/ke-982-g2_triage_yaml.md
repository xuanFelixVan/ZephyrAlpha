---
module_id: KE-904---------g2-triage-yaml-003
title: 4.2.2 检查项（对应 `g2-triage.yaml`）
category: governance
ttl: permanent
---

# 4.2.2 检查项（对应 `g2-triage.yaml`）

4.2.2 检查项（对应 `g2-triage.yaml`）

| ID | 检查名 | 级别 | 说明 | on_failure |
|----|-------|:---:|------|-----------|
| G2-C00 | `content_not_empty_shell` | **P0** | 空壳文件/占位符比例 > 50% 时阻断 | `reject` |
| G2-C01 | `classification_label_valid` | **P0** | 必须 ∈ `{BLUEPRINT, MODULE_SPEC, STRATEGY, AUDIT_REPORT, STATE_SNAPSHOT, GOVERNANCE_STD, KNOWLEDGE_ENTRY, TEMP_ARTIFACT, ORPHAN_SHELL, ENCODING_BROKEN}` | `reject` |
| G2-C02 | `doc_type_valid` | **P0** | 必须 ∈ frontmatter-standard 的合法 `doc_type` 枚举 | `reject` |
| G2-C03 | `priority_score_assigned` | **P0** | `P0/P1/P2/P3` 任一 | `auto_assign`（默认 P2）|
| G2-C04 | `layer_assignment_valid` | P1 | 必须 ∈ `l00_data_source ~ l13_experiment_pipeline` ∪ `{shared, cross_layer}` | `flag` |
| G2-C05 | `no_duplicate_ingest` | **P0** | `content_hash` 未在 `INGESTED_HASHES` 中 | `reject` |
| G2-C06 | `source_path_compliant` | P1 | 路径符合 directory-structure-standard | `flag` |
