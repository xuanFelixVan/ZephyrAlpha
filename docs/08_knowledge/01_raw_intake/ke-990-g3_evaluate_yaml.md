---
module_id: KE-912---------g3-evaluate-yaml-003
title: 4.3.2 检查项（对应 `g3-evaluate.yaml`）
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 4.3.2 检查项（对应 `g3-evaluate.yaml`）

4.3.2 检查项（对应 `g3-evaluate.yaml`）

| ID | 检查名 | 级别 | 阈值 | on_failure |
|----|-------|:---:|------|-----------|
| G3-C01 | `knowledge_value_score_threshold` | **P0** | `score ≥ 0.4` | `reject` |
| G3-C02 | `uniqueness_check` | P1 | `similarity < 0.95` | `flag` |
| G3-C03 | `content_integrity_verified` | **P0** | `encoding_status == 'clean'` + 无混合编码 | `reject` |
| G3-C04 | `metadata_complete` | P1 | 须含 `module_id, layer, classification` | `auto_fill`（按命名规则推导）|
| G3-C05 | `no_expired_ttl` | **P0** | `ttl == 'permanent' or ttl_expiry > now()` | `reject` |
