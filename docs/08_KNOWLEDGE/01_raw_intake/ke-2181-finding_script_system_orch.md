---
module_id: KE-2181
status: active
title: 3.2 Finding（Script System、Orchestrator、Gates、KB 共用）
category: module_blueprint
ttl: permanent
---

# 3.2 Finding（Script System、Orchestrator、Gates、KB 共用）

3.2 Finding（Script System、Orchestrator、Gates、KB 共用）

```yaml
schema: SCHEMA-FINDING-001
canonical_source: "MOD-INF-005 §4.3 + src/zephyr/infra_ops/script_system/finding.py"
schema_version: "1.0.0"
version_negotiation:
  ref: "CTR-VER-001（cross_layer_contracts.yaml §versioning_strategy）"
  rules:
    - "同MAJOR版本前后兼容；新增optional字段不影响消费者"
    - "废弃字段标记@deprecated，保留至少2个MAJOR版本后移除"
    - "MAJOR变更需Owner审批+30天通知所有签约方"
  ci_enforcement: "CI扫描SCHEMA-*与磁盘dataclass定义的一致性→不一致=CI FAIL"

fields:
  - name: finding_id
    type: str
    format: "FND-{DIMENSION}-{SEQ}"
  - name: severity
    type: enum
    values: [CRITICAL, HIGH, MEDIUM, LOW, INFO]
    routing:
      CRITICAL: "→ GATE FAIL + Orc BLOCK + OPS任务卡 + Owner通知"
      HIGH: "→ GATE FAIL + Orc BLOCK + OPS任务卡"
      MEDIUM: "→ GATE WARN + KB入库(G1→G2 Triage)"
      LOW: "→ GATE WARN + 审计日志"
      INFO: "→ 审计日志"
  - name: dimension
    type: enum
    values: [D1, D2, D3, D4, D5, D6, D7, D8, D9, D10, D11, D12]
  - name: recommendation
    type: str
    description: "修复建议——人类可读"
  - name: recommendation_type
    type: enum
    values: [auto_fixable, manual_only, needs_review]
```
