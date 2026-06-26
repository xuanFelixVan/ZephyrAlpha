---
module_id: KE-2849
title: 施工文件对照（Phase scaffold）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 施工文件对照（Phase scaffold）

施工文件对照（Phase scaffold）

| 文件 | 类型 | 职责 |
|------|------|------|
| `src/zephyr/audit-trail/__init__.py` | Package | 模块入口 + `__all__` |
| `src/zephyr/audit-trail/models.py` | Pydantic V2 | 全量审计事件模型 + AuditEventType 枚举（29 种）+ DID 模型 |
| `src/zephyr/audit-trail/writer.py` | Runtime | 不可变写入器（JSONL + 哈希链 + HMAC + Ed25519 + Lamport） |
| `src/zephyr/audit-trail/query.py` | Query | 审计查询接口（SQLite + JSONL + 元审计 + trail_for_ai_context） |
| `src/zephyr/audit-trail/integrity.py` | Crypto | 密码学完整性验证器（哈希链 + HMAC + Ed25519 + Merkle） |
| `src/zephyr/audit-trail/anomaly.py` | Detection | 异常检测引擎（experimental 阶段——13 签名） |
| `src/zephyr/audit-trail/drift.py` | Detection | 蓝图漂移对账（experimental 阶段） |
| `src/zephyr/audit-trail/agent_signer.py` | Crypto | Ed25519 Agent 签名器 + DID 注册（scaffold） |
| `src/zephyr/audit-trail/supply_chain.py` | Detection | 供应链审计——包安装检测（experimental 阶段） |
| `src/zephyr/audit-trail/delegation.py` | Governance | 委托链审计器（experimental 阶段） |
| `src/zephyr/audit-trail/trust-score.py` | Governance | 渐进信任引擎（experimental 阶段） |
| `src/zephyr/audit-trail/cross_ide.py` | Integrity | 跨 IDE 一致性交叉验证（experimental 阶段） |
| `src/zephyr/audit-trail/evidence_pack.py` | Governance | 监管证据包导出（beta 阶段） |
| `src/zephyr/audit-trail/lifecycle.py` | Lifecycle | 三层存储迁移 + 保留期执行（beta 阶段） |
| `src/zephyr/audit-trail/self_monitor.py` | Monitor | 自监控 heartbeat + 信任分数趋势 + 健康采集 |
| `src/zephyr/audit-trail/cli.py` | CLI | 审计命令行面板——query/trail/integrity/health/evidence |
| `scripts/governance/rebuild_audit_index.py` | Script | JSONL → SQLite 索引重建 |
| `scripts/governance/verify_audit_integrity.py` | Script | 外部独立验证——零依赖 audit-trail/，CI 门禁用 |
| `scripts/governance/enforce_audit_retention.py` | Script | 保留期强制执行 + CoT 文件生命周期（beta 阶段） |

---
