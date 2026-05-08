---
module_id: KE-module_blu-3_3_ke_kb_ce_vms_script_system-005
title: 3.3 KE（KB、CE、VMS、Script System 共用）
category: module_blueprint
---

# 3.3 KE（KB、CE、VMS、Script System 共用）

3.3 KE（KB、CE、VMS、Script System 共用）

```yaml
schema: SCHEMA-KE-001
canonical_source: "MOD-KB-001 §3.2"
schema_version: "1.0.0"
version_negotiation:
  ref: "CTR-VER-001（cross-layer-contracts.yaml §versioning_strategy）"
  rules:
    - "同MAJOR版本前后兼容；新增optional字段不影响消费者"
    - "废弃字段标记@deprecated，保留至少2个MAJOR版本后移除"
    - "MAJOR变更需Owner审批+30天通知所有签约方"
  ci_enforcement: "CI扫描SCHEMA-*与磁盘dataclass定义的一致性→不一致=CI FAIL"

fields:
  - name: ke_id
    type: str
    format: "KE-{NNN}"
  - name: status
    type: enum
    values: [DRAFT, INGESTED, TRIAGED, ANALYZED, ACTIVATED, EXTRACTED, DEPRECATED, ARCHIVED, CONFLICT, DUPLICATE]
  - name: kb_gate
    type: enum
    values: [G1, G2, G3, G4, G5]
    description: "当前KE所处的KMS门禁阶段"
  - name: source
    type: enum
    values: [manual, script_system_C4, FLE_dispatch, session_log, adr]
  - name: embedding_status
    type: enum
    values: [not_embedded, embedding, embedded, failed]
```

---
