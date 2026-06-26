---
module_id: KE-3589---------g4-activate-yaml-000
title: 4.4.2 检查项（对应 `g4-activate.yaml`）
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 4.4.2 检查项（对应 `g4-activate.yaml`）

4.4.2 检查项（对应 `g4-activate.yaml`）

| ID | 检查名 | 级别 | 说明 | on_failure |
|----|-------|:---:|------|-----------|
| G4-C01 | `dependencies_ready` | **P0** | 所有依赖 KE/module/config `status == 'active'` | **`defer`**（进入 `deferred_queue`）|
| G4-C02 | `no_conflict_with_existing` | **P0** | 与现有 active KE 无矛盾 | `flag`（人工仲裁）|
| G4-C03 | `target_path_compliant` | **P0** | 符合 `docs/08_knowledge/{subdir}/ke-*.md`（Stage G 后小写） | `reject` |
| G4-C04 | `frontmatter_schema_valid` | **P0** | 符合 `kms-entry-schema` | `reject` |
| G4-C05 | `module_id_registered` | P1 | `module_id ∈ MODULE_ID_REGISTRY` | `auto_register` |
| G4-C06 | `no_orphan_references` | P1 | 所有 `references` 均存在 | `flag` |
